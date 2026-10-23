"""Compile the self-authored BC-layout fixture against the pinned adapter source."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
ADAPTER_NATIVE = Path(os.environ.get(
    'LAMENTUM_ADAPTER_NATIVE', str(REPO.parent / 'adapter-src' / 'native')))


class BcLayoutTests(unittest.TestCase):
    def test_medium_width_policy_and_1920x1080_decode_equivalence(self):
        vendor = ADAPTER_NATIVE / 'vendor' / 'bcdec' / 'bcdec.h'
        fixture = REPO / 'tools' / 'test_bc_layout.c'
        if not vendor.is_file():
            self.skipTest('pinned adapter source/bcdec fixture is not installed')
        self.assertTrue(fixture.is_file(), 'self-authored BC fixture is missing')

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            include = root / 'native'
            (include / 'vendor' / 'bcdec').mkdir(parents=True)
            for header in ('zero_bc.h', 'zero_bc_layout.h'):
                source = ADAPTER_NATIVE / header
                self.assertTrue(source.is_file(), f'pinned overlay header missing: {source}')
                shutil.copyfile(source, include / header)
            shutil.copyfile(vendor, include / 'vendor' / 'bcdec' / 'bcdec.h')
            binary = root / 'bc-layout-test'
            built = subprocess.run(
                ['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-I', str(include),
                 str(fixture), '-o', str(binary)], text=True, capture_output=True)
            self.assertEqual(built.returncode, 0, built.stderr)
            ran = subprocess.run([str(binary)], text=True, capture_output=True, timeout=90)
            self.assertEqual(ran.returncode, 0, ran.stderr)
            self.assertIn('stripe equivalence OK', ran.stdout)
            self.assertIn('in-place equivalence OK', ran.stdout)


if __name__ == '__main__':
    unittest.main()
