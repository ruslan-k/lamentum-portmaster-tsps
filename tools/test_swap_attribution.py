import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import swap_attribution

SMAPS = textwrap.dedent('''\
7f0000000000-7f0000400000 rw-p 00000000 00:00 0                          [heap]
Size:             409600 kB
Rss:               12000 kB
Pss:               12000 kB
Referenced:         4000 kB
Dirty:              9000 kB
Swap:             380000 kB
VmFlags: rd wr mr mw me ac
7f0000400000-7f0000800000 r--p 00000000 b3:05 12345                      /usr/lib/libvulkan.so.1
Size:             409600 kB
Rss:               20000 kB
Pss:               20000 kB
Referenced:        20000 kB
Dirty:                 0 kB
Swap:              20000 kB
VmFlags: rd mr mw me
7f0000800000-7f0000c00000 rw-p 00000000 00:00 0
Size:             409600 kB
Rss:              300000 kB
Pss:              300000 kB
Referenced:       300000 kB
Dirty:            100000 kB
Swap:                  0 kB
VmFlags: rd wr mr mw me ac
''')
ROLLUP = 'Rss: 332000 kB\nPss: 332000 kB\nSwap: 400000 kB\nSwapPss: 395000 kB\n'
STATUS = 'Name:\tterminator2d-ne\nVmSwap:\t  415000 kB\n'


def build_tree(root: Path, runtime: Path) -> None:
    pid = root / '4242'
    pid.mkdir(parents=True, exist_ok=True)
    (pid / 'stat').write_text('4242 (terminator2d-ne) S 1 4242 4242 0 -1 0 0 0 0 0 100 50 0 0 20 0 34 0 6503852 0 0\n')
    (pid / 'smaps').write_text(SMAPS)
    (pid / 'smaps_rollup').write_text(ROLLUP)
    (pid / 'status').write_text(STATUS)
    (pid / 'exe').symlink_to(runtime)
    (root.parent / 'sys/kernel/random').mkdir(parents=True, exist_ok=True)
    (root.parent / 'sys/kernel/random/boot_id').write_text('boot-a\n')


def run(root: Path, runtime: Path, expected):
    source = 'import sys\nsys.argv=%r\n%s' % (['probe', json.dumps(expected), str(root), str(runtime)],
                                             swap_attribution.PAYLOAD)
    out = subprocess.run([sys.executable, '-'], input=source, text=True, capture_output=True, check=True)
    return json.loads(out.stdout.strip().splitlines()[-1])


class SwapAttributionTests(unittest.TestCase):
    def test_attributes_swap_per_mapping_and_reports_the_gap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'proc'
            runtime = Path(tmp) / 'runtime-elf'
            runtime.write_bytes(b'elf')
            build_tree(root, runtime)
            result = run(root, runtime, {'boot_id': 'boot-a', 'pid': 4242, 'starttime': 6503852})
            self.assertEqual(result['status'], 'ok')
            self.assertEqual(result['rollup_swap_kb'], 400000)
            self.assertEqual(result['process_swap_kb'], 415000)
            self.assertEqual(result['mapped_swap_kb'], 400000)
            self.assertEqual(result['unattributed_swap_kb'], 15000)
            self.assertEqual(result['coverage_percent'], 96.39)
            self.assertEqual(result['mapping_count'], 2)          # the zero-swap mapping is skipped
            self.assertEqual(result['top'][0]['swap_kb'], 380000)
            self.assertEqual(result['anonymous_swap_kb'], 380000)
            self.assertEqual(result['file_backed_swap_kb'], 20000)
            self.assertEqual(result['largest_anonymous_swap_kb'], 380000)
            self.assertIn('[heap]', result['top'][0]['header'])
            self.assertEqual(result['top'][0]['vmflags'], 'rd wr mr mw me ac')

    def test_rollup_mapping_headers_never_become_counters(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'proc'
            runtime = Path(tmp) / 'runtime-elf'
            runtime.write_bytes(b'elf')
            build_tree(root, runtime)
            (root / '4242/smaps_rollup').write_text(
                '08000000-7ffbed6000 ---p 00000000 00:00 0 \n' + ROLLUP)
            result = run(root, runtime, None)
            self.assertEqual(result['rollup_swap_kb'], 400000)
            self.assertNotIn('08000000-7ffbed6000 ---p 00000000 00', result['rollup'])

    def test_rejects_a_stale_generation_instead_of_attributing_another_process(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'proc'
            runtime = Path(tmp) / 'runtime-elf'
            runtime.write_bytes(b'elf')
            build_tree(root, runtime)
            stale = run(root, runtime, {'boot_id': 'boot-a', 'pid': 4242, 'starttime': 6503000})
            self.assertEqual(stale['status'], 'identity_changed')
            other_boot = run(root, runtime, {'boot_id': 'boot-b', 'pid': 4242, 'starttime': 6503852})
            self.assertEqual(other_boot['status'], 'boot_changed')

    def test_absent_runtime_is_reported_as_no_unique_process(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'proc'
            runtime = Path(tmp) / 'runtime-elf'
            runtime.write_bytes(b'elf')
            build_tree(root, runtime)
            missing = Path(tmp) / 'other-elf'
            missing.write_bytes(b'elf')
            (root / '4242/exe').unlink()
            (root / '4242/exe').symlink_to(missing)
            result = run(root, runtime, None)
            self.assertEqual(result['status'], 'no_unique_process')


if __name__ == '__main__':
    unittest.main()
