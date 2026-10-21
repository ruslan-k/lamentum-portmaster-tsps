"""Page/cursor oracle geometry, checked on self-authored frames.

The oracle turns one presented frame into (page, cursor row) for the navigation
core. These tests use synthetic frames drawn to the measured menu geometry - no
game capture is embedded, and a real frame is still required to calibrate the
thresholds (that calibration is a separate, recorded measurement).
"""
import unittest

import page_oracle
from page_oracle import MAIN_MENU, UNKNOWN, analyse, frame_from_rows

W, H = 1280, 720
ROWS = {442: 'load', 492: 'newgame', 542: 'options', 592: 'credits'}


def menu_frame(cursor_y=None, rows=(442, 492, 542, 592), text_level=70, cursor_level=235):
    return frame_from_rows(W, H, rows=rows, cursor_y=cursor_y, text_level=text_level,
                           cursor_level=cursor_level)


class PageOracleTests(unittest.TestCase):
    def test_finds_the_measured_cursor_band_and_the_menu_page(self):
        result = analyse(menu_frame(cursor_y=492), W, H)
        self.assertEqual(result['page'], MAIN_MENU)
        self.assertEqual(result['row'], 'newgame')
        self.assertEqual(result['cursor_y'], 492)
        self.assertTrue(result['confident'])

    def test_each_row_maps_to_its_own_entry(self):
        for y, name in ROWS.items():
            result = analyse(menu_frame(cursor_y=y), W, H)
            self.assertEqual((result['page'], result['row']), (MAIN_MENU, name), y)

    def test_a_blank_frame_is_refused_not_classified(self):
        blank = analyse(frame_from_rows(W, H, rows=(), cursor_y=None, text_level=0), W, H)
        self.assertEqual(blank['page'], UNKNOWN)
        self.assertFalse(blank['confident'])
        self.assertIn('no bright rows', blank['reason'])

    def test_a_menu_without_a_cursor_band_still_reports_the_page_but_no_row(self):
        result = analyse(menu_frame(cursor_y=None), W, H)
        self.assertEqual(result['page'], MAIN_MENU)
        self.assertIsNone(result['row'])
        self.assertFalse(result['confident'])

    def test_a_different_row_pitch_is_not_this_menu(self):
        far = analyse(frame_from_rows(W, H, rows=(382, 432, 482, 532), cursor_y=432), W, H)
        self.assertEqual(far['page'], UNKNOWN)
        self.assertIn('row pitch', far['reason'])

    def test_a_single_bright_row_is_loading_or_unknown_not_the_menu(self):
        result = analyse(frame_from_rows(W, H, rows=(500,), cursor_y=None, text_level=90), W, H)
        self.assertEqual(result['page'], UNKNOWN)
        self.assertFalse(result['confident'])

    def test_uniform_noise_is_refused(self):
        frame = bytes((x * 7 + y * 13) & 0x3F for y in range(0, H, 4) for x in range(W))
        result = analyse(frame, W, H, stride=4)
        self.assertEqual(result['page'], UNKNOWN)
        self.assertFalse(result['confident'])

    def test_wrong_buffer_size_is_refused(self):
        result = analyse(b'\x00' * 100, W, H)
        self.assertEqual(result['page'], UNKNOWN)
        self.assertIn('buffer', result['reason'])


if __name__ == '__main__':
    unittest.main()
