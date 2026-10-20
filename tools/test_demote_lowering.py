import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_lamentum_catalogue import rewrite_essl100


CAPTURED = '''#version 450
#extension GL_EXT_scalar_block_layout : require
#extension GL_EXT_demote_to_helper_invocation : require

layout(set = 0, binding = 0, scalar) uniform fs_cbuf_block_4f
{
    float data[16384];
} c3;

layout(set = 0, binding = 1) uniform sampler2D fs_tex0_20;

layout(location = 0) in vec4 in_attr0;
layout(location = 0) out vec4 frag_color0;

void main()
{
    float _62 = 1.0 / gl_FragCoord.w;
    if (texture(fs_tex0_20, vec2(_62 * (in_attr0.x * gl_FragCoord.w), _62 * (in_attr0.y * gl_FragCoord.w))).w < c3.data[4u])
    {
        demote;
    }
    frag_color0.x = c3.data[0u];
    frag_color0.y = c3.data[1u];
    frag_color0.z = c3.data[2u];
    frag_color0.w = c3.data[3u];
}'''


class DemoteLoweringTests(unittest.TestCase):
    def test_demote_becomes_discard_and_extension_goes(self):
        out, _ = rewrite_essl100(CAPTURED, 'fragment')
        self.assertIn('discard;', out)
        self.assertNotIn('demote', out)
        self.assertNotIn('#extension GL_EXT_demote_to_helper_invocation', out)
        self.assertTrue(out.startswith('#version 310 es\n'))

    def test_cbuf_and_sampler_paths_preserved(self):
        out, _ = rewrite_essl100(CAPTURED, 'fragment')
        self.assertIn('uniform highp sampler2D c3;', out)
        self.assertIn('uniform sampler2D fs_tex0_20;', out)
        self.assertIn('texelFetch(c3', out)
        self.assertIn('texture(fs_tex0_20', out)
        self.assertIn('in vec4 varying_0;', out)

    def test_inline_demote_inside_braces(self):
        out, _ = rewrite_essl100('void main() { if (x) { demote; } }', 'fragment')
        self.assertIn('{ discard; }', out)

    def test_no_demote_leaves_source_alone(self):
        out, _ = rewrite_essl100('void main() { }', 'fragment')
        self.assertNotIn('discard', out)


if __name__ == '__main__':
    unittest.main()
