import pathlib
import re
import unittest
from analyze_ui_cbuf import analyze

ROOT = pathlib.Path(__file__).resolve().parents[1]


class UiCbufRegression(unittest.TestCase):
    def test_catalogue_ui_reads_nvn_slot_one(self):
        text = (ROOT / 'runtime/lamentum-shaders-draft.h').read_text()
        start = text.rindex('/* 12 dump-6a930d0e vertex */')
        end = text.index('/* 13 ', start)
        block = text[start:end]
        self.assertIn('.name="c4",.stage=0,.binding=1,', block)
        self.assertNotIn('.name="c4",.stage=0,.binding=0,', block)
        # No shader source substitution or identity replacement.
        self.assertIn('.sha256="6a930d0edea444e0a29d3db880fe7620"', block)
        self.assertIn('.code_size=1024', block)

    def test_real_capture_wrong_bank_clips_and_zeroes_alpha(self):
        result = analyze(ROOT / 'evidence/ui-pass-01/latest.log')
        self.assertEqual(len(result['draws']), 6)
        for draw in result['draws']:
            old = draw['replay']['0']
            corrected = draw['replay']['1']
            self.assertEqual(old['vertex_color_multiplier'][-1], 0)
            self.assertEqual(corrected['vertex_color_multiplier'], [1, 1, 1, 1])
            self.assertTrue(all(not v['inside_xy'] for v in old['vertices']))
            self.assertTrue(all(v['inside_xy'] for v in corrected['vertices']))


if __name__ == '__main__':
    unittest.main()
