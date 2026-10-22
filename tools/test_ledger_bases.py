import unittest, json
from ledger_bases import reconcile, replay_texture_budget

LEDGER = ('LC2_MENU_LEDGER why=interval t-ms=8622 frames=11 line=2 available-kib=111664 '
          'budget-live-bytes=115278848 textures-live=93 textures-charged-bytes=115278848 '
          'depth-renderbuffers=2 depth-estimate-bytes=11980800 color-targets=19 '
          'color-target-estimate-bytes=45465460\n')
LIFE = ('LC2_LIFE_SUMMARY share-group=unverified bytes=declared-payload completion=unobserved '
        'texture-calls=1 deletes=24 retained=253465904 peak=253465904 live=92 '
        'tex-bytes=241485104 tex-live=90 rb-bytes=11980800 rb-live=2 buf-bytes=0 buf-live=0\n')
RUN = dict(run_uuid='u-1', pid=7, starttime='9', boot_id='b-1')
BUDGET_RUN = dict(run_uuid='u-1', boot_id='b-1', pid=7, starttime=9, elf_sha256='a'*64)


def budget_log():
    header = {'run_uuid': 'u-1', 'boot_id': 'b-1', 'pid': 7, 'starttime': 9, 'elf_sha256': 'a'*64}
    return chr(10).join((
        'LAMENTUM_RUN_HEADER ' + json.dumps(header),
        'LC2_TEXTURE_PAIR run-id=u-1 t-ns=100 phase=initialize id=42 object-generation=42 storage-owner=42 guest-bytes=100 charge-bytes=100 storage-status=recorded',
        'LC2_TEXTURE_PAIR run-id=u-1 t-ns=105 phase=initialize id=43 object-generation=43 storage-owner=43 guest-bytes=30 charge-bytes=30 storage-status=no-live-gl-storage',
        'LC2_TEXTURE_BUDGET_EVENT run-id=u-1 t-ns=110 action=add texture-id=42 delta-bytes=100 live-bytes=100 charge-count=1 caller=1 status=recorded',
        'LC2_GL_STORAGE_EVENT run-id=u-1 t-ns=120 event=allocate owner=42 gl-name=9 kind=1 storage-generation=1 bytes=400 total-bytes=400 status=recorded',
        'LC2_TEXTURE_BUDGET_EVENT run-id=u-1 t-ns=130 action=add texture-id=43 delta-bytes=30 live-bytes=130 charge-count=2 caller=1 status=recorded',
        'LC2_GL_STORAGE_DELETE run-id=u-1 t-ns=140 owner=42 gl-name=9 kind=1 storage-generation=1 bytes=400 matched=1',
        'LC2_TEXTURE_BUDGET_EVENT run-id=u-1 t-ns=150 action=sub texture-id=42 delta-bytes=100 live-bytes=30 charge-count=2 caller=1 status=recorded',
        'LC2_TEXTURE_BUDGET_FLOOR run-id=u-1 floor-check-t-ns=160 budget-sample-t-ns=160 floor-available-kib=97580 floor-swap-free-kib=1988100 live-bytes=30 peak-bytes=130 charge-count=2 event-lines=3 event-overflow=0 status=sampled lock-rc=0',
        'LC2_TEXTURE_BUDGET_EVENT run-id=u-1 t-ns=170 action=add texture-id=99 delta-bytes=1 live-bytes=31 charge-count=3 caller=1 status=recorded',
        'LC2_LIFE_SUMMARY share-group=unverified storage-calls=1 extends=0 deletes=1 delete-with-views=0 name-reuse=0 retained=0 peak=400 live=0 overflow=0 tex-bytes=0 tex-live=0 rb-bytes=0 rb-live=0 storage-event-lines=1 storage-event-overflow=0 delete-event-lines=1 delete-event-overflow=0',
    )) + chr(10)


def samples(rows):
    return [dict(run_uuid='u-1', pid=7, starttime='9', boot_id='b-1', **r) for r in rows]


class BudgetReplayTests(unittest.TestCase):
    def test_replays_per_id_charge_and_storage_to_the_floor_sample(self):
        result = replay_texture_budget(budget_log(), BUDGET_RUN)
        self.assertEqual(result['status'], 'reconciled')
        self.assertEqual(result['budget']['floor_available_kib'], 97580)
        self.assertEqual(result['budget']['live_bytes'], 30)
        self.assertEqual(result['budget']['replay_bytes'], 30)
        self.assertEqual(result['budget']['peak_bytes'], 130)
        self.assertEqual(result['budget']['event_count'], 3)
        self.assertEqual(result['budget']['events_after_sample'], 1)
        self.assertEqual(result['budget']['live_ids'], ['43'])
        self.assertEqual(result['budget']['pair_charge_mismatches'], [])
        self.assertEqual(result['budget']['pair_guest_charge_mismatches'], [])
        self.assertEqual(result['budget']['budget_without_gl_storage_ids'], ['43'])
        self.assertEqual(result['gl_storage']['live_records'], 0)
        self.assertTrue(result['gl_storage']['summary_matches'])

    def test_replays_same_subresource_redefinition_and_mip_extension(self):
        lines=[]
        for line in budget_log().splitlines():
            if line.startswith('LC2_GL_STORAGE_EVENT '):
                line=line.replace('bytes=400 total-bytes=400 status=recorded',
                                  'bytes=100 total-bytes=100 subresource=0 status=recorded')
                lines.append(line)
                lines.append('LC2_GL_STORAGE_EVENT run-id=u-1 t-ns=125 event=extend owner=42 gl-name=9 kind=1 storage-generation=1 bytes=50 total-bytes=150 subresource=1 status=recorded')
                lines.append('LC2_GL_STORAGE_EVENT run-id=u-1 t-ns=128 event=respec owner=42 gl-name=9 kind=1 storage-generation=1 bytes=80 total-bytes=130 subresource=0 status=recorded')
            elif line.startswith('LC2_GL_STORAGE_DELETE '):
                continue
            elif line.startswith('LC2_LIFE_SUMMARY '):
                lines.append('LC2_LIFE_SUMMARY share-group=unverified storage-calls=3 extends=1 deletes=0 delete-with-views=0 name-reuse=0 respecs=1 retained=130 peak=150 live=1 overflow=0 tex-bytes=130 tex-live=1 rb-bytes=0 rb-live=0 storage-event-lines=3 storage-event-overflow=0 delete-event-lines=0 delete-event-overflow=0')
            else:
                lines.append(line)
        result=replay_texture_budget(chr(10).join(lines)+chr(10), BUDGET_RUN)
        self.assertTrue(result['gl_storage']['summary_matches'])
        self.assertEqual(result['gl_storage']['bytes_by_kind'], {'1':130})
        self.assertEqual(result['gl_storage']['live_records'], 1)

    def test_replays_share_group_and_cube_face_keys_without_cross_delete(self):
        events = [
            'LC2_GL_STORAGE_EVENT run-id=u-1 t-ns=120 event=allocate owner=42 gl-name=9 kind=1 storage-generation=1 bytes=100 total-bytes=100 subresource=0 subresource-count=1 status=recorded share-group=verified share-group-id=1 target=0x8515 face=0 level=0 layer=0',
            'LC2_GL_STORAGE_EVENT run-id=u-1 t-ns=125 event=extend owner=42 gl-name=9 kind=1 storage-generation=1 bytes=50 total-bytes=150 subresource=0 subresource-count=2 status=recorded share-group=verified share-group-id=1 target=0x8515 face=1 level=0 layer=0',
            'LC2_GL_STORAGE_EVENT run-id=u-1 t-ns=128 event=allocate owner=42 gl-name=9 kind=1 storage-generation=1 bytes=20 total-bytes=20 subresource=0 subresource-count=1 status=recorded share-group=verified share-group-id=2 target=0x8515 face=0 level=0 layer=0',
        ]
        lines=[]
        inserted=False
        for line in budget_log().splitlines():
            if line.startswith('LC2_GL_STORAGE_EVENT '):
                lines.extend(events);inserted=True
            elif line.startswith('LC2_GL_STORAGE_DELETE '):
                lines.append('LC2_GL_STORAGE_DELETE run-id=u-1 t-ns=140 owner=42 gl-name=9 kind=1 storage-generation=1 bytes=150 subresource-count=2 views=0 matched=1 share-group=verified share-group-id=1')
            elif line.startswith('LC2_LIFE_SUMMARY '):
                lines.append('LC2_LIFE_SUMMARY share-group=per-record storage-calls=3 extends=1 deletes=1 delete-with-views=0 name-reuse=0 retained=20 peak=170 live=1 overflow=0 tex-bytes=20 tex-live=1 rb-bytes=0 rb-live=0 storage-event-lines=3 storage-event-overflow=0 delete-event-lines=1 delete-event-overflow=0')
            else:
                lines.append(line)
        self.assertTrue(inserted)
        result=replay_texture_budget(chr(10).join(lines)+chr(10), BUDGET_RUN)
        self.assertTrue(result['gl_storage']['summary_matches'])
        self.assertEqual(result['gl_storage']['bytes_by_kind'], {'1':20})
        self.assertEqual(result['gl_storage']['live_records'], 1)

    def test_refuses_foreign_run_and_underflow(self):
        with self.assertRaisesRegex(ValueError, 'identity'):
            replay_texture_budget(budget_log(), dict(BUDGET_RUN, run_uuid='foreign'))
        broken = budget_log().replace('delta-bytes=100 live-bytes=30 charge-count=2',
                                      'delta-bytes=101 live-bytes=29 charge-count=2')
        with self.assertRaisesRegex(ValueError, 'underflow|transition|snapshot'):
            replay_texture_budget(broken, BUDGET_RUN)

    def test_refuses_busy_or_overflowed_floor_sample(self):
        busy = budget_log().replace('status=sampled lock-rc=0', 'status=mutex-busy lock-rc=16')
        with self.assertRaisesRegex(ValueError, 'snapshot'):
            replay_texture_budget(busy, BUDGET_RUN)
        overflow = budget_log().replace('event-overflow=0 status=sampled', 'event-overflow=1 status=sampled')
        with self.assertRaisesRegex(ValueError, 'overflow'):
            replay_texture_budget(overflow, BUDGET_RUN)


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
