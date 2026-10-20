import unittest
from half_float_lowering import lower_scalar_half_casts
from append_half_color import prepare


class HalfColorTests(unittest.TestCase):
    def test_scalar_casts_not_silently_promoted(self):
        source = 'float16_t h=float16_t(a*b); f16vec2 v=unpackFloat2x16(w); v.x=h;'
        out = lower_scalar_half_casts(source)
        self.assertIn('float h=lc2_half(a*b);', out)
        self.assertIn('vec2 v=unpackFloat2x16(w);', out)

    def test_unsupported_vector_half_refuses(self):
        with self.assertRaises(ValueError):
            lower_scalar_half_casts('f16vec3 v;')

    def test_wrong_capture_refuses(self):
        with self.assertRaisesRegex(ValueError, 'not the pinned'):
            prepare('', b'wrong', b'wrong')


if __name__ == '__main__':
    unittest.main()
