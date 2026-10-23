"""Compile the self-authored BC-layout fixture against the pinned adapter source."""
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
ADAPTER_NATIVE = Path(os.environ.get(
    'LAMENTUM_ADAPTER_NATIVE', str(REPO.parent / 'adapter-src' / 'native')))


class BcLayoutTests(unittest.TestCase):
    def test_native_bc_layout_fixture(self):
        vendor = ADAPTER_NATIVE / 'vendor' / 'bcdec' / 'bcdec.h'
        fixture = REPO / 'tools' / 'test_bc_layout.c'
        required_inputs = [fixture, vendor, ADAPTER_NATIVE / 'zero_bc.h',
                           ADAPTER_NATIVE / 'zero_bc_layout.h']
        missing = [str(path) for path in required_inputs if not path.is_file()]
        if missing:
            message = 'native BC fixture inputs missing: ' + ', '.join(missing)
            if os.environ.get('LAMENTUM_REQUIRE_BC_TEST') == '1':
                self.fail('required-build profile: ' + message)
            self.skipTest(message)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            include = root / 'native'
            (include / 'vendor' / 'bcdec').mkdir(parents=True)
            for header in ('zero_bc.h', 'zero_bc_layout.h'):
                shutil.copyfile(ADAPTER_NATIVE / header, include / header)
            shutil.copyfile(vendor, include / 'vendor' / 'bcdec' / 'bcdec.h')
            binary = root / 'bc-layout-test'
            image = os.environ.get('LAMENTUM_BC_TEST_IMAGE')
            if image:
                base = ['docker', 'run', '--rm', '--network=none', '--security-opt', 'label=disable',
                        '-v', f'{root}:/fixture:rw', '-v', f'{REPO}:/repo:ro', '-w', '/fixture',
                        '--entrypoint', '/bin/bash', image]
                include_path, source_path, binary_path = '/fixture/native', '/repo/tools/test_bc_layout.c', '/fixture/bc-layout-test'
            else:
                base = []
                include_path, source_path, binary_path = str(include), str(fixture), str(binary)
            compile_args = ['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-I', include_path]
            if os.environ.get('LAMENTUM_BC_SANITIZERS') == '1':
                compile_args.extend(['-O1', '-g', '-fsanitize=address,undefined',
                                     '-fno-omit-frame-pointer'])
            compile_args.extend([source_path, '-o', binary_path])
            command = base + ['-lc', shlex.join(compile_args)] if image else compile_args
            built = subprocess.run(command, text=True, capture_output=True, timeout=180)
            self.assertEqual(built.returncode, 0, built.stderr)
            run_command = base + ['-lc', shlex.quote(binary_path)] if image else [binary_path]
            ran = subprocess.run(run_command, text=True, capture_output=True, timeout=180)
            self.assertEqual(ran.returncode, 0, ran.stderr)
            self.assertIn('stripe geometry, full-decode parity and mip metadata OK', ran.stdout)
            self.assertIn('in-place equivalence OK', ran.stdout)
            self.assertIn('BC layout address uniqueness OK', ran.stdout)
            self.assertRegex(ran.stdout, r'M4A_BC_FIXTURE_COUNTS stripe_parity=[0-9]+ source_preserved=[0-9]+ guarded_buffers=[0-9]+ upload_regions=[0-9]+ metadata_mips=[0-9]+ inplace=[0-9]+ rejects=[0-9]+ selections=[0-9]+')
            print(f"BC_PROFILE required={os.environ.get('LAMENTUM_REQUIRE_BC_TEST') == '1'} skipped=0 sanitizer={os.environ.get('LAMENTUM_BC_SANITIZERS') == '1'} image={image or 'host'}")
            print(ran.stdout, end='')


if __name__ == '__main__':
    unittest.main()
