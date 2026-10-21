import unittest, json
from ledger_bases import reconcile

LEDGER = ('LC2_MENU_LEDGER why=interval t-ms=8622 frames=11 line=2 available-kib=111664 '
          'budget-live-bytes=115278848 textures-live=93 textures-charged-bytes=115278848 '
          'depth-renderbuffers=2 depth-estimate-bytes=11980800 color-targets=19 '
          'color-target-estimate-bytes=45465460\n')
LIFE = ('LC2_LIFE_SUMMARY share-group=unverified bytes=declared-payload completion=unobserved '
        'texture-calls=1 deletes=24 retained=253465904 peak=253465904 live=92 '
        'tex-bytes=241485104 tex-live=90 rb-bytes=11980800 rb-live=2 buf-bytes=0 buf-live=0\n')
RUN = dict(run_uuid='u-1', pid=7, starttime='9', boot_id='b-1')


def samples(rows):
    return [dict(run_uuid='u-1', pid=7, starttime='9', boot_id='b-1', **r) for r in rows]


class ReconcileTests(unittest.TestCase):
    def test_three_bases_and_depth_agreement(self):
        r = reconcile(LEDGER, LIFE, samples([{'game': True, 'gpu_memory': 80000, 'log_bytes': 10},
                                             {'game': True, 'gpu_memory': 84222, 'log_bytes': 12}]), RUN)
        self.assertEqual(r['declared']['texture_bytes'], 241485104)
        self.assertEqual(r['charged']['texture_bytes'], 115278848)
        self.assertEqual(r['declared']['depth_bytes'], r['charged']['depth_bytes'])
        self.assertTrue(r['depth_agrees_exactly'])
        self.assertEqual(r['declared']['texture_over_charge'], round(241485104 / 115278848, 4))
        self.assertEqual(r['gpu_memory']['max'], 84222)
        self.assertFalse(r['gpu_memory']['units_verified'])
        self.assertFalse(r['physical_attribution'])
    def test_foreign_run_refused(self):
        bad = samples([{'game': True, 'gpu_memory': 1, 'log_bytes': 1}])
        bad[0]['run_uuid'] = 'other'
        with self.assertRaises(ValueError):
            reconcile(LEDGER, LIFE, bad, RUN)
    def test_mixed_identity_refused(self):
        rows = samples([{'game': True, 'gpu_memory': 1, 'log_bytes': 1},
                        {'game': True, 'gpu_memory': 1, 'log_bytes': 2}])
        rows[1]['pid'] = 8
        with self.assertRaises(ValueError):
            reconcile(LEDGER, LIFE, rows, RUN)
    def test_no_game_window_refused(self):
        with self.assertRaises(ValueError):
            reconcile(LEDGER, LIFE, samples([{'game': False, 'gpu_memory': 3175, 'log_bytes': 1}]), RUN)
    def test_missing_ledger_line_refused(self):
        with self.assertRaises(ValueError):
            reconcile('nothing here\n', LIFE, samples([{'game': True, 'gpu_memory': 1, 'log_bytes': 1}]), RUN)
    def test_missing_summary_refused(self):
        with self.assertRaises(ValueError):
            reconcile(LEDGER, 'nothing\n', samples([{'game': True, 'gpu_memory': 1, 'log_bytes': 1}]), RUN)
    def test_uses_last_interval_only(self):
        two = LEDGER.replace('textures-charged-bytes=115278848', 'textures-charged-bytes=1') + LEDGER
        r = reconcile(two, LIFE, samples([{'game': True, 'gpu_memory': 5, 'log_bytes': 3}]), RUN)
        self.assertEqual(r['charged']['texture_bytes'], 115278848)


if __name__ == '__main__':
    unittest.main()
