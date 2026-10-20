import hashlib
import json
import os
import re
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from append_program import append


GLSL = '''#version 450
#extension GL_EXT_demote_to_helper_invocation : require
layout(set = 0, binding = 0, scalar) uniform fs_cbuf_block_4f { float data[16384]; } c3;
layout(set = 0, binding = 1) uniform sampler2D fs_tex0_20;
layout(location = 0) in vec4 in_attr0;
layout(location = 0) out vec4 frag_color0;
void main() {
    if (texture(fs_tex0_20, in_attr0.xy).w < c3.data[4u]) { demote; }
    frag_color0 = vec4(c3.data[0u], c3.data[1u], c3.data[2u], c3.data[3u]);
}'''


def fixture_catalogue():
    text = ('#define ZERO_ZX_SHADER_PACKAGES 2\n'
            'static const struct {const char *original,*gles;unsigned stage;} nvn_shader_sources[]={\n'
            '\t/* 0 alpha vertex */\n\t{"", "\\n"\n\t "void main();\\n"\n\t "", 0},\n'
            '\t/* 1 beta fragment */\n\t{"", "\\n"\n\t "void main();\\n"\n\t "", 1},\n};\n'
            'struct mm_shader_binding {int x;};\n'
            'static const struct mm_shader_binding nvn_megaman_shader_bindings[]={\n'
            ' /* 0 alpha vertex */\n {.sha256="aa",.control_size=1,.code_size=1},\n'
            ' /* 1 beta fragment */\n {.sha256="bb",.control_size=1,.code_size=1},\n};\n')
    return text


class AppendProgramTests(unittest.TestCase):
    def workspace(self, directory):
        workspace = Path(directory)
        (workspace / 'gamma.glsl').write_text(GLSL)
        code = bytes(range(64))
        control = bytearray(0x880)
        struct.pack_into('<II', control, 0x700, 0x40, len(code) + 0x40)
        (workspace / 'gamma.code.bin').write_bytes(code + bytes(0x40))
        (workspace / 'gamma.control.bin').write_bytes(bytes(control))
        return workspace

    def test_append_keeps_existing_entries_and_bumps_count(self):
        original = fixture_catalogue()
        with tempfile.TemporaryDirectory() as directory:
            out, index, literals = append(original, 'gamma', self.workspace(directory))
        self.assertEqual(index, 2)
        self.assertIn('#define ZERO_ZX_SHADER_PACKAGES 3', out)
        for keep in ['/* 0 alpha vertex */', '/* 1 beta fragment */',
                     '{.sha256="aa",.control_size=1,.code_size=1}', '{.sha256="bb",.control_size=1,.code_size=1}']:
            self.assertIn(keep, out)
        self.assertEqual(out.count('/* 2 gamma fragment */'), 2)
        self.assertLess(out.index('/* 2 gamma fragment */'), out.index('struct mm_shader_binding'))
        self.assertIn('{ discard; }', out)
        self.assertIn('uniform sampler2D fs_tex0_20;', out)
        self.assertIn('uniform highp sampler2D c3;', out)
        self.assertNotIn('demote', out)

    def test_duplicate_identity_refused(self):
        original = fixture_catalogue()
        with tempfile.TemporaryDirectory() as directory:
            workspace = self.workspace(directory)
            once, _, _ = append(original, 'gamma', workspace)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, 'already catalogued'):
                append(once, 'gamma', self.workspace(directory))

    def test_array_count_mismatch_refused(self):
        broken = fixture_catalogue().replace(' /* 1 beta fragment */\n', '', 1)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, 'disagree'):
                append(broken, 'gamma', self.workspace(directory))


if __name__ == '__main__':
    unittest.main()
