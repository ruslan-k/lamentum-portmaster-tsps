"""Owner §48.2 N4-A/B regression gates; no device input."""
import unittest
from navigator import Navigation, observe, MAIN_MENU, NEWGAME_CONFIG


class ConfirmUniqueFrameTests(unittest.TestCase):
    def test_owner_duplicate_serial_regression(self):
        nav = Navigation()
        self.assertEqual(observe(nav, MAIN_MENU, 492, 10)['action'], 'wait')
        self.assertEqual(observe(nav, MAIN_MENU, 492, 10)['action'], 'wait')
        self.assertFalse(any(e.get('button') == 'confirm' for e in nav.events))
        self.assertEqual(observe(nav, MAIN_MENU, 492, 11).get('button'), 'confirm')

    def test_older_than_target_observation_is_refused(self):
        nav = Navigation()
        observe(nav, MAIN_MENU, 492, 10)
        self.assertEqual(observe(nav, MAIN_MENU, 492, 9)['action'], 'refuse')

    def test_conflicting_cursor_on_same_serial_is_refused(self):
        nav = Navigation()
        observe(nav, MAIN_MENU, 492, 10)
        self.assertEqual(observe(nav, MAIN_MENU, 442, 10)['action'], 'refuse')

    def test_unknown_cursor_breaks_confirmation_streak(self):
        nav = Navigation()
        observe(nav, MAIN_MENU, 492, 10)
        observe(nav, MAIN_MENU, 100, 11)
        self.assertEqual(observe(nav, MAIN_MENU, 492, 12)['action'], 'wait')
        self.assertEqual(observe(nav, MAIN_MENU, 492, 13).get('button'), 'confirm')

    def test_leaving_target_breaks_confirmation_streak(self):
        nav = Navigation()
        observe(nav, MAIN_MENU, 492, 10)
        self.assertEqual(observe(nav, MAIN_MENU, 442, 11).get('button'), 'down')
        self.assertEqual(observe(nav, MAIN_MENU, 492, 12)['action'], 'wait')
        self.assertEqual(observe(nav, MAIN_MENU, 492, 13).get('button'), 'confirm')


class DeadlineTests(unittest.TestCase):
    def nav(self):
        self.now = 100.0
        return Navigation(clock=lambda: self.now, response_timeout_s=5.0)

    def test_hundred_fast_polls_wait_without_confirm_or_refusal(self):
        nav = self.nav()
        observe(nav, MAIN_MENU, 492, 10)
        for _ in range(100):
            self.assertEqual(observe(nav, MAIN_MENU, 492, 10)['action'], 'wait')
        self.now += 1
        self.assertEqual(observe(nav, MAIN_MENU, 492, 11).get('button'), 'confirm')

    def test_expired_action_cannot_accept_even_fresh_page(self):
        nav = self.nav()
        observe(nav, MAIN_MENU, 492, 10)
        observe(nav, MAIN_MENU, 492, 11)
        self.now += 5.001
        event = observe(nav, NEWGAME_CONFIG, 0, 12)
        self.assertEqual(event['action'], 'refuse')
        self.assertGreaterEqual(event['elapsed_ms'], 5000)
        self.assertEqual(event['last_serial'], 11)
        self.assertEqual(event['issued_serial'], 11)
        self.assertFalse(nav.finished)

    def test_repeated_fresh_menu_does_not_extend_confirm_deadline(self):
        nav = self.nav()
        observe(nav, MAIN_MENU, 492, 10)
        observe(nav, MAIN_MENU, 492, 11)
        self.now += 4
        self.assertEqual(observe(nav, MAIN_MENU, 492, 12)['action'], 'wait')
        self.now += 2
        self.assertEqual(observe(nav, MAIN_MENU, 492, 13)['action'], 'refuse')

    def test_timeout_is_terminal(self):
        nav = self.nav()
        observe(nav, MAIN_MENU, 442, 10)
        self.now += 6
        self.assertEqual(observe(nav, MAIN_MENU, 492, 11)['action'], 'refuse')
        self.now += 1
        self.assertEqual(observe(nav, MAIN_MENU, 492, 12)['action'], 'refuse')
