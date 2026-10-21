"""Real incremental collector requests against temporary owned logs; no SSH/input."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from load_metrics import OwnedSerial
from owned_navigation import OwnedNavigationDriver


class RealCollectorIntegrationTests(unittest.TestCase):
    def test_rotation_after_capture_cannot_rebind_or_press(self):
        with tempfile.TemporaryDirectory() as folder:
            log = Path(folder) / 'latest.log'
            header = dict(schema=1, run_uuid='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
                          launch_nonce='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',
                          boot_id='cccccccc-cccc-4ccc-8ccc-cccccccccccc',
                          pid=17, starttime=42, elf_dev=8, elf_ino=9,
                          elf_sha256='a'*64, launcher_sha256='b'*64, helper_sha256='c'*64)
            def write(h):
                log.write_text('LAMENTUM_RUN_HEADER ' + json.dumps(h) + '\n'
                               'NVN_PRESENT_PIXELS frame=10 nonblack=1\n')
            write(header)
            requests = []
            def remote(source):
                requests.append(source)
                source = source.replace("Path('/mnt/SDCARD/Roms/PORTS/lamentum-switch/logs/latest.log')",
                                        'Path(%r)' % str(log))
                result = subprocess.run([sys.executable, '-c', source], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                return json.loads(result.stdout)
            presses = []
            def capture():
                foreign = dict(header, run_uuid='dddddddd-dddd-4ddd-8ddd-dddddddddddd')
                write(foreign)
                return dict(page='MAIN_MENU', cursor_y=442)
            reader = OwnedSerial(expected_run={'run_uuid': header['run_uuid']})
            driver = OwnedNavigationDriver(reader=reader, remote=remote, capture=capture,
                                            press=lambda *args: presses.append(args),
                                            verify_owner=lambda owner: owner['pid'] == 17,
                                            response_timeout_s=5, clock=lambda: 0.0)
            self.assertEqual(driver.tick()['action'], 'refuse')
            self.assertEqual(driver.tick()['action'], 'refuse')
            self.assertEqual(presses, [])
            self.assertEqual(len(requests), 2)
            self.assertGreater(reader.state['offset'], 0)


class CliGuardTests(unittest.TestCase):
    def test_legacy_entry_requires_expected_run_and_explicit_input_opt_in(self):
        script = Path(__file__).with_name('nav_chain.py')
        r = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertIn('--expected-run', r.stderr)

    def test_missing_opt_in_refuses_before_reading_receipt_or_connecting(self):
        script = Path(__file__).with_name('owned_nav_chain.py')
        r = subprocess.run([sys.executable, str(script), '--expected-run', '/does/not/exist',
                            '--evidence', '/does/not/exist', '--response-timeout-s', '5'],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertIn('diagnostic input opt-in required', r.stderr)
