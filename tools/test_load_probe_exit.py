import contextlib
import io
import tempfile
import unittest
from unittest.mock import Mock, patch

import load_probe


class LoadProbeExitTests(unittest.TestCase):
    def test_unverified_navigation_is_disabled_before_launch_by_default(self):
        harness = Mock(); harness.poll.return_value = 4; harness.wait.return_value = 4
        with tempfile.TemporaryDirectory() as temporary, \
             patch.object(load_probe.sys, 'argv', ['load_probe.py', '--evidence', temporary]), \
             patch.object(load_probe.subprocess, 'Popen', return_value=harness) as start, \
             contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as caught:
                load_probe.main()
            self.assertEqual(caught.exception.code, 2)
            start.assert_not_called()

    def test_observer_attaches_only_after_header_and_executable_match(self):
        import json
        from pathlib import Path
        from load_metrics import parse_chunk
        self.assertTrue(hasattr(load_probe, 'wait_owned_start'), 'owned observation barrier is missing')
        expected = {'run_uuid': 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'}
        header = dict(expected, boot_id='fixture-boot', pid=77, starttime=42, elf_dev=1, elf_ino=2)
        sample = dict(parse_chunk('NVN_PRESENT_PIXELS frame=1 x\n'), strict=True, status='ok',
                      log_identity_qualified=True, run_header=header, expected_run=expected,
                      header_sha256='a'*64, identity=[1, 3], rotated=False, size=100, offset=100,
                      mem={}, anchor=None)
        harness = Mock(); harness.poll.return_value = None
        with tempfile.TemporaryDirectory() as temporary:
            Path(temporary, 'expected-run.json').write_text(json.dumps(expected))
            with patch.object(load_probe, 'remote', side_effect=[sample, {'running': True, 'sample_status': 'ok'}]), \
                 patch.object(load_probe, 'set_expected_owner') as set_owner:
                state = load_probe.wait_owned_start(Path(temporary), harness)
                self.assertEqual(state['run_header'], header)
                set_owner.assert_called_once_with({key: header[key] for key in ('boot_id', 'pid', 'starttime', 'elf_dev', 'elf_ino')})

    def test_completed_probe_propagates_harness_failure(self):
        # Synthetic supervisor/navigation boundaries; this test does not launch or control a game.
        harness = Mock()
        harness.poll.return_value = 4
        harness.wait.return_value = 4
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(load_probe.sys, 'argv', ['load_probe.py', '--evidence', directory, '--allow-unverified-navigation']), \
             patch.object(load_probe.subprocess, 'Popen', return_value=harness), \
             patch.object(load_probe, 'navigate', return_value={'fixture': 'no real navigation'}), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(load_probe.main(), 4)


if __name__ == '__main__':
    unittest.main()
