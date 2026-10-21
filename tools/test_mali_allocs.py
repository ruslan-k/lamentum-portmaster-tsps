import unittest
from mali_allocs import summarise


class MaliAllocsTests(unittest.TestCase):
    def test_hex_commit_not_virtual_size(self):
        r = summarise('Zone name: SAME_VA:\n 1000, 8000, 2000, c07e, Native\n')
        self.assertEqual(r['commit_descriptor_bytes_by_type'], {'Native': 8192})
        self.assertIsNone(r['deduplicated_physical_residency'])

    def test_imports_kept_separate(self):
        r = summarise(' 1000, 8000, 2000, c07e, Native\n 9000, 3000, 1000, c23e, Imported UMM\n')
        self.assertEqual(r['commit_descriptor_bytes_by_type'], {'Native': 8192, 'Imported UMM': 4096})
        self.assertEqual(r['rows'], 2)

    def test_zero_commit_and_invalid_rows(self):
        r = summarise(' VA, VA size, Commit size, Flags, Mem type\n 1000, f000, 0, c07e, Native\ninvalid\n')
        self.assertEqual(r['commit_descriptor_bytes_by_type'], {'Native': 0})
        self.assertEqual(r['rows'], 1)
