"""Behaviour of the navigation core under the owner's P0-N2 contract (no device)."""
import unittest

import navigator
from navigator import (CONTROLS, MAIN_MENU, NEWGAME_CONFIG, REFUSED, Navigation,
                       observe)


class DirectionAndStepTests(unittest.TestCase):
    def test_load_steps_down_to_newgame_one_row_at_a_time(self):
        nav = Navigation()
        first = observe(nav, MAIN_MENU, 442, 10)
        self.assertEqual((first['action'], first['button'], first['row']), ('press', 'down', 'load'))
        second = observe(nav, MAIN_MENU, 492, 11)
        self.assertEqual((second['action'], second['state']), ('wait', 'AWAIT_NEW_PRESENT'))
        third = observe(nav, MAIN_MENU, 492, 12)
        self.assertEqual((third['action'], third['button']), ('press', 'confirm'))

    def test_a_row_below_the_target_presses_up(self):
        nav = Navigation()
        event = observe(nav, MAIN_MENU, 592, 10)
        self.assertEqual((event['action'], event['button'], event['row']), ('press', 'up', 'credits'))
        self.assertEqual(nav.direction_to('options'), 'up')
        self.assertEqual(nav.direction_to('load'), 'down')

    def test_one_press_that_moves_two_rows_is_refused_without_another_press(self):
        nav = Navigation()
        observe(nav, MAIN_MENU, 442, 10)             # press down from 'load'
        event = observe(nav, MAIN_MENU, 542, 11)     # landed on 'options'
        self.assertEqual(event['action'], 'refuse')
        self.assertIn('overshoot', event['reason'])
        self.assertEqual(nav.state, REFUSED)
        again = observe(nav, MAIN_MENU, 492, 12)
        self.assertEqual(again['action'], 'refuse')
        self.assertEqual(len([e for e in nav.events if e['action'] == 'press']), 1)

    def test_recovery_is_explicit_and_never_auto_confirms(self):
        nav = Navigation(recovery=True)
        observe(nav, MAIN_MENU, 442, 10)
        event = observe(nav, MAIN_MENU, 542, 11)
        self.assertEqual(event['action'], 'press')
        self.assertEqual(event['button'], 'up')      # next stop is back towards newgame
        self.assertTrue([e for e in nav.events if e['action'] == 'overshoot'])
        self.assertNotEqual(nav.state, 'DONE')


class SerialAndStateTests(unittest.TestCase):
    def test_repeated_same_frame_polls_never_press_twice(self):
        nav = Navigation()
        observe(nav, MAIN_MENU, 442, 10)
        events = [observe(nav, MAIN_MENU, 442, 10) for _ in range(4)]
        self.assertTrue(all(e['action'] == 'wait' for e in events[:3]))
        self.assertEqual(events[-1]['action'], 'refuse')
        self.assertIn('not advancing', nav.refused)

    def test_a_backwards_serial_is_refused_as_a_lagged_frame(self):
        nav = Navigation()
        observe(nav, MAIN_MENU, 442, 20)
        event = observe(nav, MAIN_MENU, 442, 19)
        self.assertEqual(event['action'], 'refuse')
        self.assertIn('went backwards', event['reason'])

    def test_zero_serial_is_refused_not_treated_as_a_frame(self):
        nav = Navigation()
        self.assertEqual(observe(nav, MAIN_MENU, 442, 0)['action'], 'refuse')
        self.assertIn('present serial not established', nav.refused)

    def test_an_unknown_page_is_refused(self):
        nav = Navigation()
        self.assertEqual(observe(nav, 'SPLASH', 400, 5)['action'], 'refuse')

    def test_an_unbanded_cursor_waits_instead_of_guessing_a_row(self):
        nav = Navigation()
        event = observe(nav, MAIN_MENU, 100, 5)
        self.assertEqual(event['action'], 'wait')
        self.assertIn('not inside a known band', event['reason'])


class ConfirmTests(unittest.TestCase):
    def _to_target(self, nav, start=442, serial=10):
        observe(nav, MAIN_MENU, start, serial)
        observe(nav, MAIN_MENU, 492, serial + 1)
        return observe(nav, MAIN_MENU, 492, serial + 2)

    def test_confirm_requires_two_agreeing_observations(self):
        nav = Navigation()
        confirm = self._to_target(nav)
        self.assertEqual(confirm['button'], 'confirm')
        same_frame = observe(nav, MAIN_MENU, 492, 12)
        self.assertEqual(same_frame['action'], 'wait')

    def test_the_expected_config_page_finishes_navigation(self):
        nav = Navigation()
        self._to_target(nav)
        done = observe(nav, NEWGAME_CONFIG, 0, 13)
        self.assertEqual(done['action'], 'done')
        self.assertTrue(nav.finished)

    def test_a_wrong_page_after_confirm_is_refused(self):
        nav = Navigation()
        self._to_target(nav)
        event = observe(nav, CONTROLS, 0, 13)
        self.assertEqual(event['action'], 'refuse')
        self.assertIn('unexpected page', event['reason'])
        self.assertFalse(nav.finished)

    def test_the_menu_still_shown_after_confirm_is_not_a_page_change(self):
        nav = Navigation()
        self._to_target(nav)
        event = observe(nav, MAIN_MENU, 492, 13)
        self.assertEqual(event['action'], 'wait')
        self.assertIn('confirm not acknowledged', event['reason'])

    def test_starting_already_on_newgame_still_needs_two_frames(self):
        nav = Navigation()
        first = observe(nav, MAIN_MENU, 492, 10)
        self.assertEqual((first['action'], first['state']), ('wait', 'AWAIT_NEW_PRESENT'))
        second = observe(nav, MAIN_MENU, 492, 11)
        self.assertEqual(second['button'], 'confirm')


class GeometryTests(unittest.TestCase):
    def test_rows_come_from_the_measured_menu_band(self):
        nav = Navigation()
        self.assertEqual(nav.row_at(444), 'load')
        self.assertEqual(nav.row_at(491), 'newgame')
        self.assertEqual(nav.row_at(590), 'credits')
        self.assertIsNone(nav.row_at(520))

    def test_world_visible_is_reported_but_not_verified(self):
        nav = Navigation()
        event = observe(nav, 'WORLD_VISIBLE', 0, 7)
        self.assertEqual(event['action'], 'refuse')     # no confirm preceded it
        self.assertNotIn('world_verified', event)


if __name__ == '__main__':
    unittest.main()
