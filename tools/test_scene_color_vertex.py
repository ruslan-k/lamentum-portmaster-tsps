import re
import subprocess
import tempfile
import unittest
from pathlib import Path
from append_scene_color_vertex import prepare
from float_cbuf_contract import inspect


class SceneColorVertexTests(unittest.TestCase):
    def test_wrong_capture_refuses(self):
        with self.assertRaisesRegex(ValueError, 'wrong shader code/control'):
            prepare('', b'wrong', b'wrong', b'')

    def test_static_last_word_extent(self):
        source = 'layout(binding=1,scalar) uniform c3 {float data[16384];} c3_1;\nvoid main(){gl_Position=vec4(c3_1.data[91u]);}'
        self.assertEqual(inspect(source, {'c3_1': 3})[0]['required_bytes'], 368)
        with self.assertRaises(ValueError):
            inspect(source.replace('[91u]', '[index]'), {'c3_1': 3})

    def test_compiled_native_range_predicate(self):
        patch = (Path(__file__).resolve().parents[1] / 'runtime/lamentum-adapter.patch').read_text()
        match = re.search(r'\+        if\(([^\n]+)\)\n\+            stop\("LC2_SCENE_COLOR_VERTEX_CBUF_REQUIRED"', patch)
        assert match is not None
        source = '#include <stdint.h>\n#include <assert.h>\n'
        source += 'static int accept(uint64_t address,uint64_t size){struct {uint64_t address,size;} range={address,size};return !(' + match[1] + ');}\n'
        source += 'int main(void){assert(!accept(0,368));assert(!accept(4096,367));assert(accept(4096,368));assert(accept(4096,512));assert(!accept(UINT64_MAX-367,368));return 0;}\n'
        with tempfile.TemporaryDirectory() as td:
            p = Path(td); (p/'guard.c').write_text(source)
            subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(p/'guard.c'),'-o',str(p/'guard')],check=True)
            subprocess.run([str(p/'guard')],check=True)


if __name__ == '__main__':
    unittest.main()
