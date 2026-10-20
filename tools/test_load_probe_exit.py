import contextlib
import io
import tempfile
import unittest
from unittest.mock import Mock, patch

import load_probe


class LoadProbeExitTests(unittest.TestCase):
    def test_completed_probe_propagates_harness_failure(self):
        # Synthetic supervisor/navigation boundaries; this test does not launch or control a game.
        harness = Mock()
        harness.poll.return_value = 4
        harness.wait.return_value = 4
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(load_probe.sys, 'argv', ['load_probe.py', '--evidence', directory]), \
             patch.object(load_probe.subprocess, 'Popen', return_value=harness), \
             patch.object(load_probe, 'navigate', return_value={'fixture': 'no real navigation'}), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(load_probe.main(), 4)


if __name__ == '__main__':
    unittest.main()
