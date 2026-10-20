import unittest
from append_light_fragment import prepare
from build_lamentum_catalogue import rewrite_essl100

SOURCE = '''#version 450
#extension GL_EXT_shader_16bit_storage : require
#extension GL_EXT_scalar_block_layout : require
layout(set = 0, binding = 0, scalar) uniform Block { float data[16384]; } c3;
layout(set = 0, binding = 3) uniform sampler3D fs_tex0_30;
void main(){
 bool _125 = c3.data[8u] == 1.0;
 if (_125) { volume = texture(fs_tex0_30, uv); } else { color = 1.0; }
 if (!_125) { light = c3.data[54u]; } else { light = volume; }
 float16_t h = float16_t(light * color);
 frag_color0 = vec4(float(h));
}
'''


class LightFragmentTests(unittest.TestCase):
    def test_false_branch_and_half_rounding_preserved(self):
        s, report = prepare(SOURCE)
        self.assertNotIn('sampler3D', s)
        self.assertNotIn('texture(fs_tex0_30', s)
        self.assertNotIn('float16_t', s)
        self.assertIn('lc2_half(light * color)', s)
        self.assertIn('packHalf2x16', s)
        self.assertEqual(report[0]['required_bytes'], 220)
        self.assertEqual(report[0]['nvn_slot'], 0)
        out, _ = rewrite_essl100(s, 'fragment')
        self.assertNotIn('scalar', out)
        self.assertNotIn('data[', out)
        self.assertIn('texelFetch(c3', out)

    def test_unknown_probe_condition_refuses(self):
        with self.assertRaises(ValueError):
            prepare(SOURCE.replace('c3.data[8u] == 1.0', 'c3.data[9u] == 1.0'))


if __name__ == '__main__':
    unittest.main()
