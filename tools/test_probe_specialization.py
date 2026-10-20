import unittest
from specialize_probe_disabled import specialize, select_branch


class ProbeSpecializationTests(unittest.TestCase):
    def test_nested_false_branch_and_true_negation(self):
        source = ('uniform sampler3D fs_tex0_28;\n'
                  'bool _98 = c3.data[8u] == 1.0;\n'
                  'vec4 color=texture(fs_tex0_20, uv);\n'
                  'if (_98) { if (x) { bad(); } else { also_bad(); } } else { keep(); }\n'
                  'if (!_98) { light=1.0; } else { light=volume; }\n'
                  'result=color*light;')
        out = specialize(source)
        self.assertIn('texture(fs_tex0_20, uv)', out)
        self.assertIn('{ keep(); }', out)
        self.assertIn('{ light=1.0; }', out)
        self.assertIn('result=color*light;', out)
        for token in ['_98','sampler3D','bad','volume']:
            self.assertNotIn(token, out)

    def test_changed_flag_or_unhandled_dependency_refused(self):
        with self.assertRaises(ValueError):
            specialize('bool _98 = c3.data[9u] == 1.0;')
        with self.assertRaises(ValueError):
            select_branch('if (_98) { a(); }', '_98', False)
        with self.assertRaises(ValueError):
            select_branch('if (_98) { a(); ', '_98', False)


if __name__ == '__main__':
    unittest.main()
