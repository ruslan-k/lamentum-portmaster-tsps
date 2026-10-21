"""Behaviour of the single navigation core (no device, synthetic observations)."""
import unittest

import navigator
from navigator import MAIN_MENU, NEWGAME_CONFIG, CONTROLS, LOADING, Navigation, observe


class NavigatorTests(unittest.TestCase):
    def test_presses_down_once_per_new_frame_until_the_target_row(self):
        nav = Navigation()
        first = observe(nav, MAIN_MENU, 425, 10)
        self.assertEqual((first['action'], first['button'], first['row']), ('press', 'down', 'load'))
        second = observe(nav, MAIN_MENU, 475, 11)
        self.assertEqual((second['action'], second['button']), ('press', 'confirm'))
        done = observe(nav, NEWGAME_CONFIG, 0, 12)
        self.assertEqual(done['action'], 'done')
        self.assertTrue(nav.finished)

    def test_a_press_is_not_reissued_without_a_new_presented_frame(self):
        nav = Navigation()
        observe(nav, MAIN_MENU, 425, 10)
        stale = observe(nav, MAIN_MENU, 425, 10)
        self.assertEqual(stale['action'], 'wait')
        self.assertIn('no new presented frame', stale['reason'])

    def test_a_stale_serial_refuses_instead_of_pressing_forever(self):
        nav = Navigation()
        observe(nav, MAIN_MENU, 425, 10)
        events = [observe(nav, MAIN_MENU, 425, 10) for _ in range(5)]
        self.assertEqual(events[-1]['action'], 'refuse')
        self.assertIn('not advancing', nav.refused)

    def test_two_rows_from_one_press_is_reported_as_overshoot(self):
        nav = Navigation()
        observe(nav, MAIN_MENU, 425, 10)
        moved = observe(nav, MAIN_MENU, 525, 11)
        self.assertEqual(moved['button'], 'down')
        overshoot = [e for e in nav.events if e['action'] == 'overshoot']
        self.assertEqual(len(overshoot), 1)
        self.assertEqual((overshoot[0]['from_row'], overshoot[0]['to_row'], overshoot[0]['steps']),
                         ('load', 'options', 2))

    def test_an_animated_picture_without_cursor_movement_does_not_press(self):
        nav = Navigation()
        observe(nav, MAIN_MENU, 425, 10)
        still = observe(nav, MAIN_MENU, 425, 11)
        self.assertEqual(still['action'], 'press')
        self.assertEqual(still['row'], 'load')

    def test_a_page_change_is_not_inferred_from_a_moved_cursor(self):
        nav = Navigation()
        observe(nav, MAIN_MENU, 425, 10)          # pressed down from 'load'
        confirm = observe(nav, MAIN_MENU, 475, 11)  # cursor moved to 'newgame'
        self.assertEqual(confirm['button'], 'confirm')
        again = observe(nav, MAIN_MENU, 475, 12)
        self.assertEqual(again['action'], 'wait')
        self.assertFalse(nav.finished)

    def test_unknown_page_and_unbanded_cursor_refuse_or_wait(self):
        nav = Navigation()
        self.assertEqual(observe(nav, 'SPLASH', 400, 5)['action'], 'refuse')
        other = Navigation()
        waiting = observe(other, MAIN_MENU, 100, 5)
        self.assertEqual(waiting['action'], 'wait')
        self.assertIn('not inside a known band', waiting['reason'])

    def test_zero_serial_is_refused_not_treated_as_a_frame(self):
        nav = Navigation()
        event = observe(nav, MAIN_MENU, 425, 0)
        self.assertEqual(event['action'], 'refuse')
        self.assertIn('present serial not established', nav.refused)

    def test_world_is_never_claimed_by_this_component(self):
        nav = Navigation()
        event = observe(nav, 'WORLD_VISIBLE', 0, 7)
        self.assertEqual(event['action'], 'done')
        self.assertEqual(event['page'], 'WORLD_VISIBLE')
        self.assertNotIn('world_verified', event)

    def test_rows_come_from_the_measured_menu_band(self):
        nav = Navigation()
        self.assertEqual(nav.row_at(427), 'load')
        self.assertEqual(nav.row_at(474), 'newgame')
        self.assertEqual(nav.row_at(573), 'credits')
        self.assertIsNone(nav.row_at(500))


if __name__ == '__main__':
    unittest.main()
