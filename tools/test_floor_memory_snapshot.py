"""Compile/run the M3-B floor snapshot parser extracted from the public overlay."""
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MARKER = 'diff --git a/native/lc2_proc_memory_snapshot.h b/native/lc2_proc_memory_snapshot.h'
FIXTURE = r'''
#include "lc2_proc_memory_snapshot.h"
#include <assert.h>
#include <stdio.h>
int main(int argc, char **argv) {
    assert(argc == 3);
    struct lc2_proc_memory_snapshot sample;
    lc2_proc_memory_snapshot_capture(argv[1], argv[2], &sample);
    assert(sample.time_known && sample.start_ns > 0 && sample.end_ns >= sample.start_ns);
    printf("meminfo-read=%d status-read=%d cma-known=%d cma=%ld rss-known=%d rss=%ld swap-known=%d swap=%ld\n",
        sample.meminfo_read, sample.status_read, sample.cmafree_known, sample.cmafree_kib,
        sample.vmrss_known, sample.vmrss_kib, sample.vmswap_known, sample.vmswap_kib);
    char line[512];
    int written=lc2_proc_memory_snapshot_format_line(line,sizeof(line),"test-run",123456,84000,2000000,
        argv[1],argv[2]);
    assert(written>0);
    printf("%s",line);
    return 0;
}
'''


class FloorMemorySnapshotTests(unittest.TestCase):
    def _compile_fixture(self, directory):
        patch = (ROOT / 'runtime/lamentum-adapter.patch').read_text()
        self.assertIn(MARKER, patch)
        block = patch.split(MARKER, 1)[1].split('diff --git ', 1)[0]
        header = '\n'.join(line[1:] for line in block.splitlines()
                            if line.startswith('+') and not line.startswith('+++')) + '\n'
        root = pathlib.Path(directory)
        (root / 'lc2_proc_memory_snapshot.h').write_text(header)
        (root / 'fixture.c').write_text(FIXTURE)
        result = subprocess.run(
            ['cc', '-std=c11', '-D_POSIX_C_SOURCE=200809L', '-Wall', '-Wextra', '-Werror',
             '-I', str(root), str(root / 'fixture.c'), '-o', str(root / 'fixture')],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return root / 'fixture'

    def test_snapshot_parses_present_fields_in_kib_and_bounds_capture_time(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            fixture = self._compile_fixture(root)
            meminfo = root / 'meminfo'
            status = root / 'status'
            meminfo.write_text('MemAvailable: 1000 kB\nCmaFree: 12345 kB\nSwapFree: 9000 kB\n')
            status.write_text('Name:\tfixture\nVmRSS:\t5432 kB\nVmSwap:\t0 kB\n')
            result = subprocess.run([str(fixture), str(meminfo), str(status)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            lines = result.stdout.splitlines()
            self.assertEqual(lines[0],
                             'meminfo-read=1 status-read=1 cma-known=1 cma=12345 '
                             'rss-known=1 rss=5432 swap-known=1 swap=0')
            self.assertIn('run-id=test-run floor-check-t-ns=123456', lines[1])
            self.assertIn('floor-available-kib=84000 floor-swap-free-kib=2000000 '
                          'cmafree-kib=12345 vmrss-kib=5432 vmswap-kib=0', lines[1])
            self.assertRegex(lines[1], r'snapshot-start-ns=[0-9]+ snapshot-end-ns=[0-9]+ snapshot-read-ns=[0-9]+')

    def test_missing_fields_or_proc_files_remain_unknown_not_zero(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            fixture = self._compile_fixture(root)
            meminfo = root / 'meminfo'
            status = root / 'status'
            meminfo.write_text('MemAvailable: 1000 kB\n')
            status.write_text('Name:\tfixture\n')
            result = subprocess.run([str(fixture), str(meminfo), str(status)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            lines = result.stdout.splitlines()
            self.assertEqual(lines[0],
                             'meminfo-read=1 status-read=1 cma-known=0 cma=-1 '
                             'rss-known=0 rss=-1 swap-known=0 swap=-1')
            self.assertIn('cmafree-kib=unknown vmrss-kib=unknown vmswap-kib=unknown', lines[1])
            result = subprocess.run([str(fixture), str(root / 'missing-meminfo'),
                                     str(root / 'missing-status')], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            lines = result.stdout.splitlines()
            self.assertEqual(lines[0],
                             'meminfo-read=0 status-read=0 cma-known=0 cma=-1 '
                             'rss-known=0 rss=-1 swap-known=0 swap=-1')
            self.assertIn('meminfo-read=0 status-read=0', lines[1])
            self.assertIn('cmafree-kib=unknown vmrss-kib=unknown vmswap-kib=unknown', lines[1])


if __name__ == '__main__':
    unittest.main()
