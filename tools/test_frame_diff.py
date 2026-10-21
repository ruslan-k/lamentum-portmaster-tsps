"""Behaviour of the frame comparison used for storage A/Bs."""
import unittest

import frame_diff

W, H = 4, 4


def uniform(value, channels=3):
    return bytes([value]) * (W * H * channels)


class FrameDiffTests(unittest.TestCase):
    def test_identical_frames_pass_both_gates(self):
        verdict = frame_diff.compare(uniform(10), uniform(10), W, H)
        self.assertTrue(verdict['comparable'])
        self.assertTrue(verdict['exact'])
        self.assertTrue(verdict['within_tolerance'])
        self.assertEqual(verdict['differing'], 0)
        self.assertTrue(frame_diff.identical(verdict))
        self.assertTrue(frame_diff.equivalent(verdict))

    def test_a_delta_inside_tolerance_is_equivalent_but_not_identical(self):
        verdict = frame_diff.compare(uniform(10), uniform(12), W, H, tolerance=2)
        self.assertEqual(verdict['differing'], 0)
        self.assertEqual(verdict['max_delta'], 2)
        self.assertTrue(frame_diff.equivalent(verdict))
        self.assertFalse(frame_diff.identical(verdict),
                         'a tolerance match must never be reported as identical')

    def test_a_delta_above_tolerance_is_a_difference(self):
        verdict = frame_diff.compare(uniform(10), uniform(13), W, H, tolerance=2)
        self.assertFalse(frame_diff.equivalent(verdict))
        self.assertFalse(frame_diff.identical(verdict))
        self.assertEqual(verdict['differing'], W * H)
        self.assertEqual(verdict['ratio'], 1.0)

    def test_a_local_change_is_located_in_bands(self):
        first = bytearray(uniform(10))
        second = bytearray(uniform(10))
        second[(H - 1) * W * 3:(H - 1) * W * 3 + 3] = b'\xff\xff\xff'   # one pixel, bottom row
        verdict = frame_diff.compare(bytes(first), bytes(second), W, H, bands=4)
        self.assertEqual(verdict['differing'], 1)
        self.assertEqual(verdict['bands'][0], 0.0)
        self.assertGreater(verdict['bands'][-1], 0.0)

    def test_geometry_and_size_mismatches_are_refused(self):
        self.assertFalse(frame_diff.compare(b'', uniform(1), W, H)['comparable'])
        wrong = frame_diff.compare(uniform(1), uniform(1)[:-1], W, H)
        self.assertFalse(wrong['comparable'])
        self.assertIn('frame size mismatch', wrong['reason'])
        self.assertFalse(frame_diff.compare(uniform(1), uniform(1), 0, H)['comparable'])
        self.assertFalse(frame_diff.identical({'comparable': False}))

    def test_channel_count_is_honoured(self):
        verdict = frame_diff.compare(bytes(W * H), bytes(W * H), W, H, channels=1)
        self.assertTrue(verdict['comparable'])
        self.assertEqual(verdict['pixels'], W * H)


if __name__ == '__main__':
    unittest.main()
