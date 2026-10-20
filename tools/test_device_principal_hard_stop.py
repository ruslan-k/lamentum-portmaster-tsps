import unittest
from device_principal_test import should_hard_stop


class HardStopTests(unittest.TestCase):
    def test_stops_only_past_deadline_with_a_live_game(self):
        self.assertTrue(should_hard_stop(100, 90, [4321]))
        self.assertFalse(should_hard_stop(100, 120, [4321]))
        self.assertFalse(should_hard_stop(100, 90, []))

    def test_disabled_bound_never_kills(self):
        self.assertFalse(should_hard_stop(10 ** 9, None, [4321]))
        self.assertFalse(should_hard_stop(10 ** 9, 0, [4321]))


if __name__ == '__main__':
    unittest.main()
