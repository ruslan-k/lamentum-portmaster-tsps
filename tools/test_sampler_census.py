import unittest
from sampler_census import census

ROW = 'T2_DRAW_TEXTURE frame=1 draw=0 pair=1/2 program=3 sampler=tex unit=0 id=81 size=3600x2160 format=0x44 target=2\n'

class CensusTests(unittest.TestCase):
    def test_roles_separate(self):
        r = census(ROW.encode(), [81, 92])
        self.assertEqual(r['observed']['81']['bindings'], 1)
        self.assertEqual(r['target_ids'], [2])
        self.assertEqual(r['watched']['92']['bindings'], 0)
        self.assertFalse(r['absence_proves_unused'])
        self.assertIsNone(r['physical_refund_bytes'])
    def test_split_line_is_not_record(self):
        r = census(ROW.rstrip().encode(), [81])
        self.assertEqual(r['events'], 0)
        self.assertTrue(r['incomplete_tail'])
    def test_order_refuses(self):
        with self.assertRaises(ValueError):
            census((ROW.replace('frame=1', 'frame=2') + ROW).encode())
    def test_bad_record_refuses(self):
        for row in [ROW.replace('id=81', 'id=x'), ROW.replace('target=2', ''), ROW.replace('id=81', 'id=81 id=92')]:
            with self.subTest(row=row), self.assertRaises(ValueError):
                census(row.encode())
    def test_repeated_binding_is_legal(self):
        r = census((ROW + ROW).encode())
        self.assertEqual(r['events'], 2)
        self.assertEqual(r['observed']['81']['frames'], [1])
    def test_empty_is_unknown(self):
        r = census(b'irrelevant\n', [81])
        self.assertIsNone(r['first_frame'])
        self.assertEqual(r['watched']['81']['bindings'], 0)
        self.assertFalse(r['absence_proves_unused'])

if __name__ == '__main__':
    unittest.main()
