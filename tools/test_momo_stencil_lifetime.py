"""Exercise the default-off MOMO stencil storage path against mocked GL errors."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
ADAPTER_NATIVE = Path(os.environ.get(
    'LAMENTUM_ADAPTER_NATIVE', str(ROOT.parent / 'adapter-src' / 'native')))
FIXTURE = ROOT / 'tools' / 'fixtures' / 'momo-stencil-lifetime.c'
REQUIRED = os.environ.get('LAMENTUM_REQUIRE_MOMO_STENCIL_TEST') == '1'


class MomoStencilLifetimeTests(unittest.TestCase):
    def test_storage_transactions_isolate_errors_and_stay_default_off(self):
        inputs = [FIXTURE, ADAPTER_NATIVE / 'momo_stencil_bench.h', ADAPTER_NATIVE / 'lc2_lifetime.h']
        missing = [str(path) for path in inputs if not path.is_file()]
        if missing:
            message = 'MOMO stencil fixture inputs missing: ' + ', '.join(missing)
            if REQUIRED:
                self.fail('required-build profile: ' + message)
            self.skipTest(message)

        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / 'momo-stencil-lifetime'
            built = subprocess.run(
                ['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-Wno-unused-function',
                 '-Wno-unused-variable', '-Wno-unused-but-set-variable', '-I', str(ADAPTER_NATIVE), str(FIXTURE), '-o', str(binary)],
                text=True, capture_output=True)
            self.assertEqual(built.returncode, 0, built.stderr)

            def run(**overrides):
                env = os.environ.copy()
                for key in ('MOMO_STENCIL_SELFTEST', 'MOCK_TEXTURE_SETUP_ERROR',
                            'MOCK_TEXTURE_STORAGE_ERROR', 'MOCK_RENDERBUFFER_SETUP_ERROR',
                            'MOCK_RENDERBUFFER_STORAGE_ERROR'):
                    env.pop(key, None)
                env.update(overrides)
                return subprocess.run([str(binary)], env=env, text=True,
                                      capture_output=True, timeout=10)

            disabled = run()
            self.assertEqual(disabled.returncode, 0, disabled.stderr)
            self.assertIn('MOCK_STORAGE_CALLS texture=0 renderbuffer=0', disabled.stdout)
            self.assertNotIn('MOMO_STENCIL_STORAGE ', disabled.stdout)

            success = run(MOMO_STENCIL_SELFTEST='1')
            self.assertEqual(success.returncode, 0, success.stderr)
            self.assertIn('MOMO_STENCIL_STORAGE scope=one-shot group=42 texture=committed texture-error=0x0 renderbuffer=committed renderbuffer-error=0x0 retained-bytes=32768 reserved-bytes=0 completion=unproven', success.stdout)
            self.assertIn('MOCK_STORAGE_CALLS texture=1 renderbuffer=1', success.stdout)

            operation_error = run(MOMO_STENCIL_SELFTEST='1', MOCK_TEXTURE_STORAGE_ERROR='0x505')
            self.assertEqual(operation_error.returncode, 0, operation_error.stderr)
            self.assertIn('MOMO_STENCIL_STORAGE scope=one-shot group=42 texture=outcome-unknown texture-error=0x505 renderbuffer=committed renderbuffer-error=0x0 retained-bytes=16384 reserved-bytes=16384 completion=unproven', operation_error.stdout)
            self.assertIn('MOCK_STORAGE_CALLS texture=1 renderbuffer=1', operation_error.stdout)

            setup_error = run(MOMO_STENCIL_SELFTEST='1', MOCK_TEXTURE_SETUP_ERROR='0x502')
            self.assertEqual(setup_error.returncode, 0, setup_error.stderr)
            self.assertIn('MOMO_STENCIL_STORAGE scope=one-shot group=42 texture=preexisting-error texture-error=0x502 renderbuffer=committed renderbuffer-error=0x0 retained-bytes=16384 reserved-bytes=0 completion=unproven', setup_error.stdout)
            self.assertIn('MOCK_STORAGE_CALLS texture=0 renderbuffer=1', setup_error.stdout)


if __name__ == '__main__':
    unittest.main()
