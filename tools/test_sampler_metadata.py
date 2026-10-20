#!/usr/bin/env python3
"""Regression tests for guest sampler identities, independent of GL bindings."""
import unittest
from build_lamentum_catalogue import samplers_of, rewrite_cbuf_blocks, component_masks

class SamplerMetadata(unittest.TestCase):
    def test_bare(self):
        s = samplers_of('uniform sampler2D fs_tex0_20;')[0]
        self.assertEqual((s['stage'], s['binding'], s['offset']), (1, 14, 0))
    def test_gl_binding_is_not_guest_bank(self):
        s = samplers_of('layout(set = 0, binding = 9) uniform sampler2D vs_tex2_a8;')[0]
        self.assertEqual((s['stage'], s['binding'], s['offset']), (0, 2, 168))
    def test_cross_collision_suffix(self):
        s = samplers_of('uniform sampler2D fs_tex0_20_1;')[0]
        self.assertEqual((s['binding'], s['offset']), (14, 0))
    def test_unknown_identity_rejected(self):
        with self.assertRaises(ValueError):
            samplers_of('uniform sampler2D unknown;')

    def test_rgba_scalar_rewrite(self):
        source = 'uniform B { float data[16384]; } c3; float a = c3.data[5u];'
        result = rewrite_cbuf_blocks(source, [{'block': 'B', 'instance': 'c3'}])
        self.assertIn('ivec2((int(5u) >> 2) & 1023, int(5u) >> 12)', result)
        self.assertIn('[int(5u) & 3]', result)
        for index in range(16384):
            x, y, lane = (index >> 2) & 1023, index >> 12, index & 3
            self.assertEqual((y * 1024 + x) * 4 + lane, index)
    def test_test_fragment_interface(self):
        self.assertEqual(component_masks('in vec4 varying_1;', 'in'), {1: 15})

if __name__ == '__main__':
    unittest.main()
