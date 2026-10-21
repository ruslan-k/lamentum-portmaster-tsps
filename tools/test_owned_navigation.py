"""Transport fixtures only: not device or gameplay evidence."""
import unittest
from owned_navigation import OwnedNavigationDriver

OWNER = dict(boot_id='boot', pid=17, starttime=42, elf_dev=8, elf_ino=9)


class Reader:
    def __init__(self):
        self.serial = 10
        self.status = 'ok'
        self.state = dict(log_identity_qualified=True, header_sha256='generation-A', run_header=dict(OWNER))
    def poll(self, remote):
        return dict(status=self.status, serial=self.serial, fresh=True)


class DriverTests(unittest.TestCase):
    def setup_driver(self, row=442):
        self.now = 0.0
        self.reader = Reader()
        self.live = True
        self.presses = []
        self.capture_hook = None
        self.press_hook = None
        self.row = row
        def capture():
            if self.capture_hook:
                self.capture_hook()
            return dict(page='MAIN_MENU', cursor_y=self.row)
        def press(button, hold_ms):
            self.presses.append(button)
            if self.press_hook:
                return self.press_hook(button)
            return dict(action=button, released=True)
        return OwnedNavigationDriver(reader=self.reader, remote=lambda x: None,
                                     capture=capture, press=press,
                                     verify_owner=lambda owner: self.live,
                                     clock=lambda: self.now, response_timeout_s=5.0)

    def test_slow_capture_cannot_issue_action_after_overall_deadline(self):
        d = self.setup_driver()
        self.capture_hook = lambda: setattr(self, 'now', 6.0)
        self.assertEqual(d.tick()['action'], 'refuse')
        self.assertEqual(self.presses, [])

    def test_one_instance_retains_overshoot_and_never_corrects(self):
        d = self.setup_driver()
        self.assertEqual(d.tick()['action'], 'press')
        self.reader.serial = 11
        self.row = 542
        self.assertEqual(d.tick()['action'], 'refuse')
        self.reader.serial = 12
        self.assertEqual(d.tick()['action'], 'refuse')
        self.assertEqual(self.presses, ['down'])

    def test_generation_change_is_terminal_and_never_rebinds(self):
        d = self.setup_driver()
        d.tick()
        self.reader.state['header_sha256'] = 'generation-B'
        self.reader.serial = 1
        self.assertEqual(d.tick()['action'], 'refuse')
        self.reader.serial = 50
        self.assertEqual(d.tick()['action'], 'refuse')
        self.assertEqual(self.presses, ['down'])

    def test_foreign_capture_is_refused_without_press(self):
        d = self.setup_driver()
        self.capture_hook = lambda: setattr(self, 'live', False)
        self.assertEqual(d.tick()['action'], 'refuse')
        self.assertEqual(self.presses, [])

    def test_capture_crossing_a_present_is_not_used_for_input(self):
        d = self.setup_driver()
        self.capture_hook = lambda: setattr(self.reader, 'serial', 11)
        self.assertEqual(d.tick()['action'], 'wait')
        self.assertEqual(self.presses, [])

    def test_absent_release_receipt_is_a_terminal_refusal(self):
        d = self.setup_driver()
        self.press_hook = lambda button: None
        self.assertEqual(d.tick()['action'], 'refuse')
        self.assertEqual(d.tick()['action'], 'refuse')
        self.assertEqual(self.presses, ['down'])

    def test_release_receipt_is_mandatory(self):
        d = self.setup_driver()
        self.press_hook = lambda button: dict(action=button, released=False)
        self.assertEqual(d.tick()['action'], 'refuse')
        self.reader.serial = 11
        self.assertEqual(d.tick()['action'], 'refuse')
        self.assertEqual(self.presses, ['down'])

    def test_rotation_during_press_preserves_release_but_refuses(self):
        d = self.setup_driver()
        def press(button):
            self.reader.status = 'LOG_GENERATION_CHANGED'
            return dict(action=button, released=True)
        self.press_hook = press
        self.assertEqual(d.tick()['action'], 'refuse')
        self.assertTrue(d.events[-1]['release_receipt']['released'])

    def test_duplicate_frame_does_not_confirm_and_timeout_is_terminal(self):
        d = self.setup_driver(row=492)
        self.assertEqual(d.tick()['action'], 'wait')
        for _ in range(100):
            self.assertEqual(d.tick()['action'], 'wait')
        self.now = 6.0
        self.assertEqual(d.tick()['action'], 'refuse')
        self.reader.serial = 11
        self.assertEqual(d.tick()['action'], 'refuse')
        self.assertEqual(self.presses, [])

    def test_unqualified_log_never_sends_input(self):
        d = self.setup_driver()
        self.reader.state['log_identity_qualified'] = False
        self.assertEqual(d.tick()['action'], 'refuse')
        self.assertEqual(self.presses, [])

    def test_confirm_disabled_until_page_oracle_and_memory_gate(self):
        d = self.setup_driver(row=492)
        d.tick()
        self.reader.serial = 11
        self.assertEqual(d.tick()['action'], 'refuse')
        self.assertEqual(self.presses, [])
