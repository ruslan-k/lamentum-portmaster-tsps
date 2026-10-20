import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import load_metrics

SYNTH = """NATIVE_PROBE_TIME_BUDGET seconds=900
NVN_TEXTURE_REAL object=0x1 format=0x44 size=8192x8192 levels=1 bytes=67108864 texture=1 depth=0 gpu-storage=allocated no-draw
LC2_BC_DEFERRED id=295 size=8192x8192 rgba-bytes=268435456 source=retained-guest-pool diagnostic=1
T2_TEXTURE_BUDGET add-bytes=268435456 live-MiB=411 count=151 budget-MiB=300
ROMFS_READ offset=0x0 size=0x50
NVN_PRESENT_PIXELS frame=806 nonblack=1656 max=154 white=0 texture-draws=2672 status=PIXELS
STOP status=T2_TEXTURE_BUDGET pc=main.text.seg+0x52d294 detail=0x19b
"""


class PayloadExecutionTests(unittest.TestCase):
    """The payload is a source string, so it can be compiled and checked without a device."""

    def test_payload_compiles(self):
        compile(load_metrics.PAYLOAD, '<payload>', 'exec')

    def test_payload_executes_against_a_synthetic_log(self):
        """Run the real payload locally with a rewritten log path: this is T0's missing test."""
        source = load_metrics.PAYLOAD.replace(
            "Path('/mnt/SDCARD/Roms/PORTS/lamentum-switch/logs/latest.log')", "Path(sys.argv[2])")
        source = source.replace("Path('/proc/meminfo').read_text().splitlines()", "[]")
        with tempfile.TemporaryDirectory() as td:
            log = Path(td) / 'latest.log'
            log.write_text(SYNTH)
            run = subprocess.run([sys.executable, '-c', source, '0', str(log)],
                                 capture_output=True, text=True, timeout=60)
            self.assertEqual(run.returncode, 0, run.stderr)
            out = json.loads(run.stdout)
        self.assertEqual(out['frame'], 806)
        self.assertEqual(out['stops'], ['T2_TEXTURE_BUDGET'])
        self.assertEqual(out['counters']['presents'], 1)
        self.assertEqual(out['counters']['textures'], 1)
        self.assertEqual(out['counters']['bc_deferred'], 1)
        self.assertEqual(out['counters']['budget_adds'], 1)
        self.assertIn('live-MiB=411', out['budget_last'])
        self.assertEqual(out['offset'], len(SYNTH))

    def test_payload_reports_rotation_instead_of_double_counting(self):
        source = load_metrics.PAYLOAD.replace(
            "Path('/mnt/SDCARD/Roms/PORTS/lamentum-switch/logs/latest.log')", "Path(sys.argv[2])")
        source = source.replace("Path('/proc/meminfo').read_text().splitlines()", "[]")
        with tempfile.TemporaryDirectory() as td:
            log = Path(td) / 'latest.log'
            log.write_text('short\n')
            run = subprocess.run([sys.executable, '-c', source, '999999', str(log)],
                                 capture_output=True, text=True, timeout=60)
            out = json.loads(run.stdout)
        self.assertTrue(out['rotated'])
        self.assertEqual(out['offset'], len('short\n'))


class FoldTests(unittest.TestCase):
    def test_counters_accumulate_and_frames_take_the_latest(self):
        first = load_metrics.parse_chunk('NVN_PRESENT_PIXELS frame=10 x\nROMFS_READ a\n')
        first.update(offset=10, size=10, rotated=False, mem={'MemAvailable': 100})
        running = load_metrics.fold(None, first)
        second = load_metrics.parse_chunk('NVN_PRESENT_PIXELS frame=12 x\nROMFS_READ b\nSTOP status=T2_TEXTURE_BUDGET\n')
        second.update(offset=20, size=20, rotated=False, mem={'MemAvailable': 50})
        running = load_metrics.fold(running, second)
        self.assertEqual(running['presents'], 2)
        self.assertEqual(running['romfs'], 2)
        self.assertEqual(running['frame'], 12)
        self.assertEqual(running['stops'], ['T2_TEXTURE_BUDGET'])
        self.assertEqual(running['mem']['MemAvailable'], 50)

    def test_rotation_resets_running_totals(self):
        first = load_metrics.parse_chunk('NVN_PRESENT_PIXELS frame=99 x\n')
        first.update(offset=5, size=5, rotated=False, mem={})
        running = load_metrics.fold(None, first)
        fresh = load_metrics.parse_chunk('NVN_PRESENT_PIXELS frame=3 x\n')
        fresh.update(offset=4, size=4, rotated=True, mem={})
        running = load_metrics.fold(running, fresh)
        self.assertEqual(running['presents'], 1)
        self.assertEqual(running['frame'], 3)

    def test_killed_flag_is_sticky(self):
        first = load_metrics.parse_chunk('Killed  ./lamentum-nextos\n')
        first.update(offset=1, size=1, rotated=False, mem={})
        running = load_metrics.fold(None, first)
        calm = load_metrics.parse_chunk('NVN_PRESENT_PIXELS frame=1 x\n')
        calm.update(offset=2, size=2, rotated=False, mem={})
        self.assertTrue(load_metrics.fold(running, calm)['killed'])


if __name__ == '__main__':
    unittest.main()
