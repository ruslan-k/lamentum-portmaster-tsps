"""GLES upload-triple contract for decoded BC/CPU textures (roadmap 32.3).

The runtime used one value as BOTH the sized internal format and the client
`format` argument (0x8C42), which is not a legal external format in GLES2 or
GLES3. These tests exercise a self-authored pure mapper extracted from the
public overlay; they do not touch game data, a driver or a device.
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
HEADER = 'lc2_gl_format.h'
RGBA, UBYTE, FLOAT, HALF = 0x1908, 0x1401, 0x1406, 0x8D61
RGBA8, SRGB8_A8, SRGBA_EXT, RGBA32F = 0x8058, 0x8C43, 0x8C42, 0x8814
UNSUPPORTED, SRGB_UNAVAILABLE, CONTEXT_INVALID = 1, 2, 3


def overlay_header():
    text = (REPO / 'runtime/lamentum-adapter.patch').read_text()
    marker = f'diff --git a/native/{HEADER} b/native/{HEADER}\n'
    if marker not in text:
        return None
    section = text.split(marker, 1)[1].split('\ndiff --git ', 1)[0]
    return '\n'.join(line[1:] for line in section.splitlines()
                     if line.startswith('+') and not line.startswith('+++')) + '\n'


def overlay_added():
    text = (REPO / 'runtime/lamentum-adapter.patch').read_text()
    return '\n'.join(line[1:] for line in text.splitlines()
                     if line.startswith('+') and not line.startswith('+++'))


class GlUploadFormatTests(unittest.TestCase):
    def map_formats(self, cases):
        header = overlay_header()
        self.assertIsNotNone(header, 'GLES upload-format mapper missing from overlay')
        assert header is not None
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / HEADER).write_text(header)
            source = REPO / 'tools/fixtures/lc2-gl-format-fixture.c'
            self.assertTrue(source.is_file(), 'self-authored mapper fixture is missing')
            binary = root / 'format'
            flags = os.environ.get('LC2_FORMAT_TEST_CFLAGS', '').split()
            built = subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                                    *flags, '-I', str(root), str(source), '-o', str(binary)],
                                   text=True, capture_output=True)
            self.assertEqual(built.returncode, 0, built.stderr)
            ran = subprocess.run([str(binary)], text=True, capture_output=True, timeout=20,
                                 input=''.join(' '.join(map(str, c)) + '\n' for c in cases))
            self.assertEqual(ran.returncode, 0, ran.stderr)
            rows = [json.loads(line) for line in ran.stdout.splitlines()]
            self.assertEqual(len(rows), len(cases))
            return rows

    def test_srgb_rgba_uses_a_sized_internal_and_unsized_rgba_external(self):
        es3, es2 = self.map_formats([[3, 1, 1, UBYTE], [2, 1, 1, UBYTE]])
        self.assertEqual((es3['status'], es3['internal'], es3['external'], es3['type']),
                         (0, SRGB8_A8, RGBA, UBYTE))
        self.assertEqual((es2['status'], es2['internal'], es2['external'], es2['type']),
                         (0, SRGBA_EXT, RGBA, UBYTE))

    def test_never_reuses_the_storage_value_as_the_client_format(self):
        rows = self.map_formats([[3, 1, 1, UBYTE], [2, 1, 1, UBYTE], [3, 0, 0, UBYTE],
                                 [3, 0, 0, FLOAT]])
        for row in rows:
            self.assertEqual(row['status'], 0, row)
            self.assertEqual(row['external'], RGBA, row)
            self.assertNotEqual(row['internal'], row['external'], row)
        # ES2 has no sized colour formats: unsized RGBA storage plus an RGBA
        # client array is the one legal linear pair and is not the defect.
        es2, = self.map_formats([[2, 0, 0, UBYTE]])
        self.assertEqual((es2['status'], es2['internal'], es2['external'], es2['type']),
                         (0, RGBA, RGBA, UBYTE))

    def test_linear_rgba8_and_float_follow_the_context_generation(self):
        es3_8, es2_8, es3_f, es2_f = self.map_formats([
            [3, 0, 0, UBYTE], [2, 0, 0, UBYTE], [3, 0, 0, FLOAT], [2, 1, 0, FLOAT]])
        self.assertEqual((es3_8['internal'], es3_8['external'], es3_8['type']), (RGBA8, RGBA, UBYTE))
        self.assertEqual((es2_8['internal'], es2_8['external'], es2_8['type']), (RGBA, RGBA, UBYTE))
        self.assertEqual((es3_f['internal'], es3_f['external'], es3_f['type']), (RGBA32F, RGBA, FLOAT))
        self.assertEqual((es2_f['internal'], es2_f['external'], es2_f['type']), (RGBA, RGBA, FLOAT))

    def test_srgb_without_a_sized_or_EXT_storage_refuses_instead_of_faking_it(self):
        rows = self.map_formats([[2, 0, 1, UBYTE], [3, 0, 1, FLOAT], [2, 1, 1, FLOAT],
                                 [2, 1, 1, HALF], [3, 0, 0, 0xDEAD]])
        self.assertEqual(rows[0]['status'], SRGB_UNAVAILABLE)      # ES2 without GL_EXT_sRGB
        self.assertEqual(rows[1]['status'], UNSUPPORTED)           # no sRGB float upload
        self.assertEqual(rows[2]['status'], UNSUPPORTED)           # sRGB half
        self.assertEqual(rows[3]['status'], UNSUPPORTED)
        self.assertEqual(rows[4]['status'], UNSUPPORTED)
        self.assertTrue(all('internal' not in row for row in rows), rows)

    def test_packed_and_half_types_are_not_silently_coerced_to_rgba8(self):
        rows = self.map_formats([[2, 0, 0, HALF], [2, 0, 0, 0x8363], [3, 0, 0, 0x8D61]])
        self.assertTrue(all(row['status'] == UNSUPPORTED for row in rows), rows)
        self.assertTrue(all('type' not in row for row in rows), rows)

    def test_an_unknown_context_generation_is_refused(self):
        rows = self.map_formats([[1, 1, 1, UBYTE], [0, 1, 1, UBYTE], [1, 0, 0, UBYTE]])
        self.assertTrue(all(row['status'] == CONTEXT_INVALID for row in rows), rows)

    def test_overlay_runtime_call_sites_use_the_mapper(self):
        added = overlay_added()
        self.assertIn('lc2_gl_upload_format(', added)
        self.assertIn('static struct lc2_gl_upload lc2_gl_upload_for(', added)
        # The defect signature: one call passes the sRGB value as internal AND client format.
        doubled = [line for line in added.splitlines()
                   if ('glTexImage2D(' in line or 'glTexSubImage2D(' in line)
                   and line.count('0x8c42U') > 1]
        self.assertEqual(doubled, [], doubled)
        self.assertGreaterEqual(added.count('lc2_gl_upload_for(t,'), 3,
                                'decoded upload paths must resolve their triple through the mapper')
        self.assertIn('glTexImage2D(GL_TEXTURE_2D,level,spec.internal,width,height,0,spec.external,spec.type,NULL)', added)
        self.assertIn('glTexSubImage2D(GL_TEXTURE_2D,level,0,y,width,rows,spec.external,spec.type,pixels)', added)
        # Partial-mip completion takes a resolved spec, not one value for both arguments.
        self.assertIn('zero_mip_complete_storage(struct nvn_texture *t,struct lc2_gl_upload spec)', added)
        self.assertIn('glTexImage2D(GL_TEXTURE_2D,level,spec.internal,width,height,0,GL_RGBA,spec.type,zero)', added)


if __name__ == '__main__':
    unittest.main()
