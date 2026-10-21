"""Self-authored native exec/UUID fixtures; never launch the game or touch a device."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / 'tools/run_identity.py'


class RunIdentityTests(unittest.TestCase):
    def module(self):
        self.assertTrue(TOOL.is_file(), 'T1 owned-run exec helper is missing')
        spec = importlib.util.spec_from_file_location('identity_fixture_module', TOOL)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_kernel_uuid_is_not_a_wall_clock_token(self):
        module = self.module()
        first, second = module.new_run_uuid(), module.new_run_uuid()
        self.assertNotEqual(first, second)
        generated = subprocess.run([sys.executable, '-c', module.uuid_request()], text=True,
                                   capture_output=True, timeout=10)
        self.assertEqual(generated.returncode, 0, generated.stderr)
        self.assertNotEqual(json.loads(generated.stdout)['run_uuid'], first)
        for value in (first, second):
            self.assertRegex(value, r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')
        for bad in ('', '0caf515', first.upper(), first + '\n', '../' + first):
            with self.assertRaises(ValueError):
                module.validate_uuid(bad)

    def test_header_precedes_exec_records_and_binds_actual_exec_inode(self):
        module = self.module()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'fixture.c'
            source.write_text(r'''
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/stat.h>
int main(void) {struct stat s;if(stat("/proc/self/exe",&s))return 9;
 printf("EXEC_FIXTURE {\"pid\":%ld,\"dev\":%llu,\"ino\":%llu,\"run_uuid\":\"%s\",\"legacy\":\"%s\"}\n",
 (long)getpid(),(unsigned long long)s.st_dev,(unsigned long long)s.st_ino,
 getenv("LAMENTUM_RUN_UUID"),getenv("COTM_RUN_ID"));return 7;}
''')
            runtime = root / 'same-basename'
            subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', str(source), '-o', str(runtime)], check=True)
            launcher = root / 'launcher.sh'
            launcher.write_text('# self-authored launcher identity fixture\n')
            uuid = module.new_run_uuid()
            preflight = subprocess.run([sys.executable, '-c', module.preflight_request(runtime, launcher, TOOL)],
                                       text=True, capture_output=True, timeout=10)
            self.assertEqual(preflight.returncode, 0, preflight.stderr)
            self.assertEqual(json.loads(preflight.stdout)['runtime']['sha256'], hashlib.sha256(runtime.read_bytes()).hexdigest())
            process = subprocess.run([sys.executable, str(TOOL), 'exec', '--runtime', str(runtime),
                                      '--launcher', str(launcher), '--run-uuid', uuid],
                                     capture_output=True, text=True, timeout=10)
            self.assertEqual(process.returncode, 7, process.stderr)
            lines = process.stdout.splitlines()
            self.assertTrue(lines[0].startswith('LAMENTUM_RUN_HEADER '), lines)
            header = json.loads(lines[0].split(' ', 1)[1])
            record = json.loads(next(line for line in lines if line.startswith('EXEC_FIXTURE ')).split(' ', 1)[1])
            self.assertEqual(header['run_uuid'], uuid)
            self.assertEqual(record['run_uuid'], uuid)
            self.assertEqual(header['pid'], record['pid'])
            self.assertEqual(header['elf_dev'], record['dev'])
            self.assertEqual(header['elf_ino'], record['ino'])
            self.assertEqual(header['elf_sha256'], hashlib.sha256(runtime.read_bytes()).hexdigest())
            self.assertEqual(header['launcher_sha256'], hashlib.sha256(launcher.read_bytes()).hexdigest())
            self.assertGreater(header['starttime'], 0)
            self.assertRegex(record['legacy'], r'^\d{1,12}$')
            self.assertIsNone(header['image_sha256'])
            self.assertIsNone(header['catalogue_sha256'])
            self.assertFalse(header['content_bindings_complete'])
            # Equal bytes at another inode must not be reported as the same executable.
            old_inode = header['elf_ino']
            renamed = root / 'old'
            runtime.rename(renamed)
            runtime.write_bytes(renamed.read_bytes())
            runtime.chmod(0o755)
            self.assertNotEqual(runtime.stat().st_ino, old_inode)

    def test_pidfd_termination_rejects_reuse_then_stops_only_owned_child(self):
        module = self.module()
        self.assertTrue(hasattr(module, 'terminate_owned'), 'owned pidfd termination is missing')
        child = subprocess.Popen([sys.executable, '-c', 'import time;time.sleep(30)'])
        try:
            text = Path('/proc/%d/stat' % child.pid).read_text()
            info = os.stat('/proc/%d/exe' % child.pid)
            owner = {'pid': child.pid, 'starttime': int(text[text.rindex(')')+1:].split()[19]),
                     'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                     'elf_dev': info.st_dev, 'elf_ino': info.st_ino}
            def rpc(value):
                result = subprocess.run([sys.executable, '-c', module.terminate_request(value)],
                                        text=True, capture_output=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                return json.loads(result.stdout)
            rejected = rpc(dict(owner, starttime=owner['starttime'] + 1))
            self.assertEqual(rejected['outcome'], 'identity_mismatch')
            self.assertIsNone(child.poll())
            stopped = rpc(owner)
            self.assertEqual(stopped['outcome'], 'pidfd_TERM')
            self.assertEqual(child.wait(timeout=10), -15)
        finally:
            if child.poll() is None:
                child.terminate()
                child.wait(timeout=10)

    def test_bad_uuid_stops_before_runtime_or_header(self):
        self.module()
        process = subprocess.run([sys.executable, str(TOOL), 'exec', '--runtime', '/does/not/exist',
                                  '--launcher', '/does/not/exist', '--run-uuid', '123'],
                                 capture_output=True, text=True, timeout=10)
        self.assertNotEqual(process.returncode, 0)
        self.assertNotIn('LAMENTUM_RUN_HEADER ', process.stdout)


if __name__ == '__main__':
    unittest.main()
