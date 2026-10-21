"""What one press+frame pair proves, and what it must refuse to claim."""
import unittest

import nav_chain


class SummariseTests(unittest.TestCase):
    def test_one_row_on_a_newer_frame_is_a_qualified_chain(self):
        verdict = nav_chain.summarise(10, 'load', 11, 'newgame')
        self.assertTrue(verdict['qualified'])
        self.assertEqual(verdict['step'], 1)
        self.assertEqual(verdict['serial_delta'], 1)
        self.assertIn('exactly one row', verdict['reason'])

    def test_two_rows_is_reported_as_a_hold_length_overshoot(self):
        verdict = nav_chain.summarise(10, 'load', 12, 'options', tap_ms=900)
        self.assertTrue(verdict['qualified'])
        self.assertEqual(verdict['step'], 2)
        self.assertIn('overshoot', verdict['reason'])
        self.assertIn('900', verdict['reason'])

    def test_an_unchanged_serial_never_qualifies_the_press(self):
        verdict = nav_chain.summarise(10, 'load', 10, 'newgame')
        self.assertFalse(verdict['qualified'])
        self.assertIn('no newer presented frame', verdict['reason'])

    def test_a_missing_serial_is_refused_rather_than_guessed(self):
        for before, after in ((0, 12), (10, 0), (0, 0)):
            verdict = nav_chain.summarise(before, 'load', after, 'newgame')
            self.assertFalse(verdict['qualified'], (before, after))
            self.assertIn('serial unavailable', verdict['reason'])

    def test_an_unmeasurable_row_is_refused(self):
        verdict = nav_chain.summarise(10, 'load', 11, None)
        self.assertFalse(verdict['qualified'])
        self.assertIn('row was not measurable', verdict['reason'])

    def test_no_movement_is_qualified_but_names_the_next_lever(self):
        short = nav_chain.summarise(10, 'load', 11, 'load', tap_ms=350)
        long = nav_chain.summarise(10, 'load', 11, 'load', tap_ms=900)
        self.assertEqual(short['step'], 0)
        self.assertIn('check the button role', short['hint'])
        self.assertIn('longer tap', long['hint'])

    def test_tap_default_stays_short(self):
        self.assertLessEqual(nav_chain.TAP_MS, 400, 'a long tap moves two rows on this device')


if __name__ == '__main__':
    unittest.main()
