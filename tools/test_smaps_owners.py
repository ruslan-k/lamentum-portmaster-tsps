import unittest
from smaps_owners import summarise


def vma(path, rss, anon=0, swap=0):
    return ('1000-2000 rw-p 00000000 00:01 7 ' + path + '\n'
            'Rss: %d kB\nAnonymous: %d kB\nSwap: %d kB\n' % (rss, anon, swap))


class SmapsOwnersTests(unittest.TestCase):
    def test_device_mapping_not_labelled_image(self):
        r = summarise(vma('/dev/mali0', 500000) + vma('/game/romfs.bin', 100))
        self.assertEqual(r['owners'][0]['path'], '/dev/mali0')
        self.assertEqual(r['totals']['Rss'], 500100)

    def test_file_backed_cow_is_preserved(self):
        r = summarise(vma('/snapshot (deleted)', 80, 70, 12))
        self.assertEqual(r['owners'][0]['Anonymous'], 70)
        self.assertEqual(r['owners'][0]['Swap'], 12)

    def test_aggregate_same_path_and_anonymous(self):
        r = summarise(vma('/a path', 10) + vma('/a path', 20) + vma('', 7, 7))
        self.assertEqual(r['owners'][0]['mappings'], 2)
        self.assertEqual(r['owners'][0]['Rss'], 30)
        self.assertEqual(r['owners'][1]['path'], '[anonymous]')

    def test_empty_is_not_measurement_of_no_live_process(self):
        r = summarise('')
        self.assertEqual(r['owners'], [])
        self.assertIn('one smaps read', r['scope'])
