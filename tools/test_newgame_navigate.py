import unittest
from newgame_navigate import changed


class NavigationGateTests(unittest.TestCase):
    def test_cursor_move_is_below_screen_transition(self):
        a = [0] * 100
        b = list(a)
        for i in range(6):
            b[i] = 200
        self.assertEqual(changed(a, b), 6)
        self.assertLess(changed(a, b), 50)

    def test_small_noise_does_not_count(self):
        a = [0] * 100
        b = [5] * 100      # below the 10-level threshold
        self.assertEqual(changed(a, b), 0)

    def test_identical_captures_are_zero(self):
        a = [10, 200, 30, 255]
        self.assertEqual(changed(a, list(a)), 0)


if __name__ == '__main__':
    unittest.main()
