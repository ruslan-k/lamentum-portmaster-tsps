import struct
import unittest
from append_literal_vertex import verify_ir, prepare
from float_cbuf_contract import inspect


def inst(op, *args):
    return [((len(args) + 1) << 16) | op, *args]


def name(i, value):
    b = value.encode() + b'\0'; b += bytes((-len(b)) % 4)
    return inst(5, i, *struct.unpack('<%dI' % (len(b) // 4), b))


class LiteralVertexTests(unittest.TestCase):
    def test_ir_provenance_and_stage(self):
        words = [0x07230203, 0x10000, 0, 100, 0]
        words += inst(15, 0, 90, 0) + name(43, 'c1') + name(44, 'c3')
        words += inst(59, 42, 43, 2) + inst(59, 42, 44, 2)
        data = struct.pack('<%dI' % len(words), *words)
        self.assertEqual(verify_ir(data), {'c1': 43, 'c3': 44})
        words[6] = 4
        with self.assertRaises(ValueError):
            verify_ir(struct.pack('<%dI' % len(words), *words))
        with self.assertRaises(ValueError):
            verify_ir(data[:-1])

    def test_no_implicit_suffix_mapping(self):
        s = 'layout(binding=1, scalar) uniform c3 {float data[16384];} c3_1;\nvoid main(){gl_Position=vec4(c3_1.data[95u]);}'
        with self.assertRaises(ValueError):
            inspect(s)
        self.assertEqual(inspect(s, {'c3_1': 3})[0]['nvn_slot'], 0)
        self.assertEqual(inspect(s, {'c3_1': 3})[0]['required_bytes'], 384)

    def test_wrong_capture_refuses(self):
        with self.assertRaisesRegex(ValueError, 'wrong shader code/control'):
            prepare('', b'wrong', b'wrong', b'')


if __name__ == '__main__':
    unittest.main()
