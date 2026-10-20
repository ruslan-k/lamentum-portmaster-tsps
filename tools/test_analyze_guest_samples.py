import unittest
from analyze_guest_samples import analyze


LOG = '''MOMO_SAMPLE thread=0x1 in-kernel=0x0 pc=main.text.seg+0x1177010 main.text.seg+0x1177010 main.text.seg+0x11a0234 sdk.text.seg+0x208a40
MOMO_SAMPLE thread=0x1 in-kernel=0x0 pc=main.text.seg+0x1177010 main.text.seg+0x1177010
MOMO_SAMPLE thread=0x4 in-kernel=0x1 pc=sdk.text.seg+0x393dc8
MOMO_SAMPLE thread=0x1 in-kernel=0x0 pc=main.text.seg+0x2dec648 main.text.seg+0x2dec648
'''


class GuestSampleTests(unittest.TestCase):
    def test_buckets_and_share(self):
        r = analyze(LOG)
        self.assertEqual(r['samples'], 4)
        self.assertEqual(r['in_kernel'], 1)
        self.assertEqual(r['top_pc'][0], {'pc': 'main.text.seg+0x1177010', 'n': 2, 'share': 0.5})
        self.assertEqual(r['threads'], {'0x1': 3, '0x4': 1})

    def test_no_silent_symbol_guessing(self):
        r = analyze('MOMO_SAMPLE thread=0x1 in-kernel=0x0 pc=main.text.seg+0xdead\n')
        self.assertEqual(r['top_pc'][0]['pc'], 'main.text.seg+0xdead')
        self.assertTrue(all(f['location'].startswith(('main.', 'sdk.')) for f in r['top_frames']))

    def test_empty_log_is_zero_not_error(self):
        r = analyze('nothing here\n')
        self.assertEqual((r['samples'], r['top_pc'], r['top_frames']), (0, [], []))


if __name__ == '__main__':
    unittest.main()
