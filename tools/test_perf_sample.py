import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import perf_sample
from load_metrics import parse_chunk


class PerfSamplingBoundaryTests(unittest.TestCase):
    def test_transport_failure_is_not_reported_as_absent_game(self):
        with patch.object(perf_sample.subprocess, 'run', side_effect=subprocess.CalledProcessError(255, 'ssh')):
            with self.assertRaises(subprocess.CalledProcessError):
                perf_sample.sample()

    def test_principal_harness_status_is_propagated_and_log_frame_is_not_fps(self):
        # Synthetic external boundaries only; this test never contacts or launches on a device.
        fixture = {'running': True, 'boot_id': 'fixture-boot', 'pid': 17, 'starttime': 42,
                   'target_hz': 250, 'monotonic_s': 10, 'total_cpu_ticks': 100,
                   'minflt': 0, 'majflt': 0, 'threads': {}}
        log = parse_chunk('NVN_PRESENT_PIXELS frame=3 x\n')
        log.update(offset=30, size=30, identity=[1, 2], rotated=False, mem={})
        harness = Mock(returncode=4)
        harness.poll.side_effect = [None, 4]
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / 'output'
            env = Path(directory) / 'env.json'
            env.write_text('[]')
            with patch.object(perf_sample.subprocess, 'Popen', return_value=harness), \
                 patch.object(perf_sample, 'remote_json', side_effect=[fixture, log]), \
                 patch.object(perf_sample.time, 'sleep'):
                self.assertEqual(perf_sample.main([str(env), str(out)]), 4)
            record = json.loads((out / 'perf.jsonl').read_text())
            self.assertEqual(record['sample']['pid'], 17)
            self.assertEqual(record['delta_status'], 'no_live_pair')
            self.assertEqual(record['log_metrics']['presents'], 1)
            self.assertIn('not a scene or FPS', record['frame_scope'])
            self.assertNotIn('guest_frame_ms', record)


if __name__ == '__main__':
    unittest.main()
