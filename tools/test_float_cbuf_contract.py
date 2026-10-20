import struct
import unittest
from float_cbuf_contract import inspect, without_scalar_extension
from build_lamentum_catalogue import rewrite_essl100

SOURCE = '''#version 450
#extension GL_EXT_scalar_block_layout : require
layout(set = 0, binding = 0, scalar) uniform Block { float data[16384]; } c4;
void main() { gl_Position = vec4(c4.data[0u], c4.data[3u], c4.data[4u], c4.data[4097u]); }
'''


class FloatCbufTests(unittest.TestCase):
    def test_offsets_and_texture_lane_math(self):
        report = inspect(SOURCE)[0]
        self.assertEqual(report['byte_offsets'], [0, 12, 16, 16388])
        self.assertEqual(report['nvn_slot'], 1)
        # Self-authored host memory fixture: boundary lanes and second row.
        words = [float(i) * -0.125 for i in range(16384)]
        raw = struct.pack('<16384f', *words)
        for word in range(16384):
            x, y, lane = (word >> 2) & 1023, word >> 12, word & 3
            byte_offset = ((y * 1024 + x) * 4 + lane) * 4
            self.assertEqual(byte_offset, word * 4)
            self.assertEqual(struct.unpack_from('<f', raw, byte_offset)[0], words[word])

    def test_no_stride_mutation_and_no_unsupported_extension_in_final(self):
        s = without_scalar_extension(SOURCE)
        self.assertIn('scalar) uniform', s)
        out, _ = rewrite_essl100(s, 'vertex')
        self.assertNotIn('scalar', out)
        self.assertNotIn('data[', out)
        self.assertIn('uniform highp sampler2D c4;', out)
        self.assertIn('int(4097u) >> 12', out)

    def test_fail_closed(self):
        for replacement in ['c4.data[16384u]', 'c4.data[i]', 'c4.data[0u] = 1.0']:
            with self.assertRaises(ValueError):
                inspect(SOURCE.replace('c4.data[0u]', replacement, 1))
        for extra in ['\nbuffer Writable {float a;};', '\nvoid x(){atomicAdd(a,1);}', '\nvoid x(){foo(c4);}']:
            with self.assertRaises(ValueError):
                inspect(SOURCE + extra)


if __name__ == '__main__':
    unittest.main()
