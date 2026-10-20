#!/usr/bin/env python3
"""Regression tests for guest sampler identities, independent of GL bindings."""
import unittest
from build_lamentum_catalogue import samplers_of

class SamplerMetadata(unittest.TestCase):
    def test_bare(self):
        s = samplers_of('uniform sampler2D fs_tex0_20;')[0]
        self.assertEqual((s['stage'], s['binding'], s['offset']), (1, 0, 32))
    def test_gl_binding_is_not_guest_bank(self):
        s = samplers_of('layout(set = 0, binding = 9) uniform sampler2D vs_tex2_a8;')[0]
        self.assertEqual((s['stage'], s['binding'], s['offset']), (0, 2, 168))
    def test_cross_collision_suffix(self):
        s = samplers_of('uniform sampler2D fs_tex0_20_1;')[0]
        self.assertEqual((s['binding'], s['offset']), (0, 32))
    def test_unknown_identity_rejected(self):
        with self.assertRaises(ValueError):
            samplers_of('uniform sampler2D unknown;')

if __name__ == '__main__':
    unittest.main()
