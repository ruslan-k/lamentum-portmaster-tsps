import struct
import hashlib
from pathlib import Path
import tempfile
import unittest
from shader_literals import inline_literal_cbuf, specialize_catalogue


def fetch(name, index):
    return f'texelFetch({name}, ivec2((int({index}) >> 2) & 1023, int({index}) >> 12), 0)[int({index}) & 3]'


class LiteralBankTests(unittest.TestCase):
    def fixture(self):
        # Synthetic format fixture, not captured game output.
        code = bytearray(0x200)
        struct.pack_into('<III', code, 0x100, 0x3f870a3d, 0x80000000, 0x7fc01234)
        control = bytearray(0x880)
        struct.pack_into('<II', control, 0x700, 0x100, len(code))
        return bytes(code), bytes(control)

    def test_exact_bits_and_collision_suffix(self):
        code, control = self.fixture()
        source = 'uniform highp sampler2D c1_1;\nfloat x=' + fetch('c1_1', '0u') + ';'
        out, removed = inline_literal_cbuf(source, {'c1_1'}, code, control)
        self.assertEqual(removed, {'c1_1'})
        self.assertNotIn('sampler2D', out)
        self.assertIn('uintBitsToFloat(0x3f870a3du)', out)

    def test_negative_zero_and_nan_payload(self):
        code, control = self.fixture()
        source = 'uniform highp sampler2D c1;\nfloat x=' + fetch('c1', '1u') + '+' + fetch('c1', '2u') + ';'
        out, _ = inline_literal_cbuf(source, {'c1'}, code, control)
        self.assertIn('0x80000000u', out)
        self.assertIn('0x7fc01234u', out)

    def test_application_bank_untouched(self):
        code, control = self.fixture()
        source = 'uniform highp sampler2D c3;\nfloat x=' + fetch('c3', '0u') + ';'
        self.assertEqual(inline_literal_cbuf(source, {'c3'}, code, control), (source, set()))

    def test_catalogue_identity_metadata_and_idempotence(self):
        import json
        code, control = self.fixture()
        glsl = ('uniform highp sampler2D c1;\nuniform highp sampler2D c4_1;\nfloat x=' +
                fetch('c1', '0u') + '+' + fetch('c4_1', '0u') + ';\n')
        digest = lambda data: ','.join('0x%02x' % b for b in hashlib.sha256(data).digest())
        text = ('static const struct {int unused;} nvn_shader_sources[]={\n'
                '\t/* 0 fixture vertex */\n\t{"", "\\n"\n' +
                '\t ' + json.dumps(glsl) + '\n\t "", 0},\n};\n' +
                'static const struct mm_shader_binding nvn_megaman_shader_bindings[]={\n'
                ' /* 0 fixture vertex */\n' +
                ' {.code_hash={' + digest(code) + '},.control_hash={' + digest(control) + '},\n' +
                '  .uniform_count=2,.uniforms={{.name="c1",.binding=0},{.name="c4_1",.binding=1}},\n},\n};\n')
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace/'fixture.code.bin').write_bytes(code)
            (workspace/'fixture.control.bin').write_bytes(control)
            out, changes = specialize_catalogue(text, workspace)
            self.assertEqual(changes, {'fixture': ['c1']})
            self.assertIn('.uniform_count=1,.uniforms={{.name="c4_1",.binding=1}}', out)
            self.assertIn('.code_hash={' + digest(code) + '}', out)
            self.assertEqual(specialize_catalogue(out, workspace), (out, {}))
            (workspace/'fixture.code.bin').write_bytes(bytes([code[0] ^ 1])+code[1:])
            with self.assertRaisesRegex(ValueError, 'identity mismatch'):
                specialize_catalogue(text, workspace)

    def test_reject_dynamic_index_and_bad_capture(self):
        code, control = self.fixture()
        for index in ['i', '64u']:
            with self.assertRaises(ValueError):
                inline_literal_cbuf('uniform highp sampler2D c1;\nx=' + fetch('c1', index) + ';', {'c1'}, code, control)
        for bad_code, bad_control in [(code[:-1], control), (code, control[:0x704])]:
            with self.assertRaises(ValueError):
                inline_literal_cbuf('uniform highp sampler2D c1;\nx=' + fetch('c1', '0u') + ';', {'c1'}, bad_code, bad_control)


if __name__ == '__main__':
    unittest.main()
