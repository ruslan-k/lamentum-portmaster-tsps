import unittest
from half_mrt_lowering import lower_half_mrt, REWRITES


class HalfMrtTests(unittest.TestCase):
    def test_wrong_source_hash_refuses(self):
        with self.assertRaisesRegex(ValueError, 'does not match the pinned capture'):
            lower_half_mrt('void main(){}', '0' * 64)

    def test_the_three_half_products_are_rounded(self):
        by_target = {new.split('=')[0].split()[-1]: new for _, new in REWRITES}
        for name in ('_108', '_110', '_112', '_90', '_97'):
            self.assertIn('lc2_half(', by_target[name], name)

    def test_half_types_do_not_survive(self):
        self.assertFalse(any('float16_t' in new or 'f16vec' in new for _, new in REWRITES))


if __name__ == '__main__':
    unittest.main()
