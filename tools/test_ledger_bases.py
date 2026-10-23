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
        'LC2_GL_STORAGE_EVENT run-id=u-1 t-ns=120 event=allocate owner=42 gl-name=9 kind=1 storage-generation=1 bytes=400 total-bytes=400 status=recorded call-result=unobserved',
        'LC2_TEXTURE_BUDGET_EVENT run-id=u-1 t-ns=130 action=add texture-id=43 delta-bytes=30 live-bytes=130 charge-count=2 caller=1 status=recorded',
        'LC2_GL_STORAGE_DELETE run-id=u-1 t-ns=140 owner=42 gl-name=9 kind=1 storage-generation=1 bytes=400 matched=1',
        'LC2_TEXTURE_BUDGET_EVENT run-id=u-1 t-ns=150 action=sub texture-id=42 delta-bytes=100 live-bytes=30 charge-count=2 caller=1 status=recorded',
        'LC2_TEXTURE_BUDGET_FLOOR run-id=u-1 floor-check-t-ns=160 budget-sample-t-ns=160 floor-available-kib=97580 floor-swap-free-kib=1988100 live-bytes=30 peak-bytes=130 charge-count=2 event-lines=3 event-overflow=0 status=sampled lock-rc=0',
        'LC2_TEXTURE_BUDGET_EVENT run-id=u-1 t-ns=170 action=add texture-id=99 delta-bytes=1 live-bytes=31 charge-count=3 caller=1 status=recorded',
        'LC2_LIFE_SUMMARY share-group=unverified storage-calls=1 extends=0 deletes=1 delete-with-views=0 name-reuse=0 retained=0 peak=400 live=0 overflow=0 tex-bytes=0 tex-live=0 rb-bytes=0 rb-live=0 storage-event-lines=1 storage-event-overflow=0 delete-event-lines=1 delete-event-overflow=0',
    )) + chr(10)


def missing_pair_log(extra_records=(), pair_overflow=None, final_newline=True):
    lines=[]
    for line in budget_log().splitlines():
        if line.startswith('LC2_TEXTURE_PAIR ') and ' id=43 ' in line:
            continue
        if line.startswith('LC2_LIFE_SUMMARY ') and pair_overflow is not None:
            line += ' tex-pair-overflow=' + str(pair_overflow)
        lines.append(line)
    lines[-1:-1] = list(extra_records)
    return chr(10).join(lines) + (chr(10) if final_newline else '')


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
        self.assertEqual(result['gl_storage']['call_results_by_status'], {'unobserved': 1})
        legacy = replay_texture_budget(budget_log().replace(' call-result=unobserved', ''), BUDGET_RUN)
        self.assertEqual(legacy['gl_storage']['call_results_by_status'], {'unknown': 1})
        self.assertTrue(result['gl_storage']['summary_matches'])

    def test_call_id_requires_ordered_begin_result_and_storage_records(self):
        begin = ('LC2_TEXTURE_OWNER_EVENT run-id=u-1 event-seq=1 call-id=1 t-ns=115 phase=cpu-view-glTexImage2D '
                 'nvn-id=42 object-generation=42 generation-basis=nvn-object-id storage-owner=42 '
                 'storage-owner-status=resolved charge-bytes=0 pool-id=99 pool-generation=1 pool-status=recorded '
                 'cpu-write-generation=1 storage-bytes=400 source-write-generation=untracked status=attempt-recorded')
        result = ('LC2_TEXTURE_OWNER_EVENT run-id=u-1 event-seq=2 call-id=1 t-ns=120 phase=cpu-view-glTexImage2D '
                  'nvn-id=42 object-generation=42 generation-basis=nvn-object-id storage-owner=42 '
                  'storage-owner-status=resolved charge-bytes=0 pool-id=99 pool-generation=1 pool-status=recorded '
                  'cpu-write-generation=1 storage-bytes=400 source-write-generation=untracked status=call-result-unobserved')

        def make_log(include_result):
            lines=[]
            for line in budget_log().splitlines():
                if line.startswith('LC2_GL_STORAGE_EVENT '):
                    line += ' call-id=1'
                if line.startswith('LC2_LIFE_SUMMARY '):
                    events=[begin]+([result] if include_result else [])
                    lines.extend(events)
                    count=len(events)
                    lines.append(f'LC2_TEXTURE_OWNER_EVENTS_SUMMARY run-id=u-1 configured=512 claimed={count} final-claimed={count} emitted={count} incomplete=0 active=0 dropped=0 format-errors=0 complete=1')
                lines.append(line)
            return chr(10).join(lines)+chr(10)

        complete = replay_texture_budget(make_log(True), BUDGET_RUN)
        self.assertEqual(complete['gl_storage']['call_attempts_correlated'],1)
        with self.assertRaisesRegex(ValueError,'storage_call_id_incomplete:1'):
            replay_texture_budget(make_log(False), BUDGET_RUN)
        mismatched = make_log(True).replace(
            'storage-bytes=400 source-write-generation=untracked status=call-result-unobserved',
            'storage-bytes=399 source-write-generation=untracked status=call-result-unobserved')
        with self.assertRaisesRegex(ValueError,'storage_call_id_mismatch:1'):
            replay_texture_budget(mismatched, BUDGET_RUN)
        incomplete_ring = make_log(True).replace(
            'dropped=0 format-errors=0 complete=1',
            'dropped=1 format-errors=0 complete=0')
        with self.assertRaisesRegex(ValueError,'storage_call_id_owner_ring_incomplete'):
            replay_texture_budget(incomplete_ring, BUDGET_RUN)

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

    def test_missing_pair_after_completed_initialize_is_missing_owner_path(self):
        records = [
            'LC2_TEXTURE_OWNER_EVENT run-id=u-1 event-seq=1 t-ns=140 phase=initialize nvn-id=43 object-generation=43 generation-basis=nvn-object-id storage-owner=43 storage-owner-status=resolved charge-bytes=30 pool-id=99 pool-generation=1 pool-status=recorded cpu-write-generation=0 source-write-generation=untracked status=pair-emitted',
            'LC2_TEXTURE_OWNER_EVENTS_SUMMARY run-id=u-1 configured=512 claimed=1 final-claimed=1 emitted=1 incomplete=0 active=0 dropped=0 format-errors=0 complete=1',
        ]
        with self.assertRaisesRegex(ValueError, '43=missing_owner_path'):
            replay_texture_budget(missing_pair_log(records), BUDGET_RUN)

    def test_missing_pair_with_incomplete_owner_ring_is_log_truncated(self):
        event = 'LC2_TEXTURE_OWNER_EVENT run-id=u-1 event-seq=1 t-ns=140 phase=initialize-start nvn-id=43 object-generation=43 generation-basis=nvn-object-id storage-owner=0 storage-owner-status=unresolved charge-bytes=0 pool-id=99 pool-generation=1 pool-status=recorded cpu-write-generation=0 source-write-generation=untracked status=started'
        with self.assertRaisesRegex(ValueError, '43=log_truncated'):
            replay_texture_budget(missing_pair_log([event]), BUDGET_RUN)

    def test_pair_event_overflow_is_over_capacity(self):
        with self.assertRaisesRegex(ValueError, '43=over_capacity'):
            replay_texture_budget(missing_pair_log(pair_overflow=1), BUDGET_RUN)

    def test_alias_owner_requires_an_explicit_alias_resolution(self):
        text = budget_log().replace('id=43 object-generation=43 storage-owner=43',
                                    'id=43 object-generation=43 storage-owner=99')
        with self.assertRaisesRegex(ValueError, '43=alias_scope_mismatch'):
            replay_texture_budget(text, BUDGET_RUN)
        rows = text.splitlines()
        rows.insert(2, 'LC2_TEXTURE_OWNER_EVENT run-id=u-1 event-seq=1 t-ns=106 phase=alias-resolve nvn-id=43 object-generation=43 generation-basis=nvn-object-id storage-owner=99 storage-owner-status=resolved charge-bytes=30 pool-id=30 pool-generation=1 pool-status=recorded cpu-write-generation=0 source-write-generation=untracked status=alias-owner-resolved')
        rows.insert(-1, 'LC2_TEXTURE_OWNER_EVENTS_SUMMARY run-id=u-1 configured=512 claimed=1 final-claimed=1 emitted=1 incomplete=0 active=0 dropped=0 format-errors=0 complete=1')
        result = replay_texture_budget(chr(10).join(rows)+chr(10), BUDGET_RUN)
        self.assertEqual(result['budget']['pair_coverage']['43'], 'joined')

    def test_final_unterminated_record_is_log_truncated(self):
        with self.assertRaisesRegex(ValueError, 'log_truncated'):
            replay_texture_budget(missing_pair_log(final_newline=False), BUDGET_RUN)

    def test_future_generation_does_not_change_floor_owner_join(self):
        late = 'LC2_TEXTURE_PAIR run-id=u-1 t-ns=170 phase=initialize id=43 object-generation=99 storage-owner=43 guest-bytes=30 charge-bytes=30 storage-status=recorded'
        text = budget_log().replace('LC2_LIFE_SUMMARY ', late + chr(10) + 'LC2_LIFE_SUMMARY ')
        result = replay_texture_budget(text, BUDGET_RUN)
        self.assertEqual(result['budget']['pair_coverage']['43'], 'joined')

    def test_conflicting_pair_generations_are_generation_mismatch(self):
        pair = 'LC2_TEXTURE_PAIR run-id=u-1 t-ns=106 phase=initialize id=43 object-generation=99 storage-owner=43 guest-bytes=30 charge-bytes=30 storage-status=no-live-gl-storage'
        text = budget_log().replace('LC2_LIFE_SUMMARY ', pair + chr(10) + 'LC2_LIFE_SUMMARY ')
        with self.assertRaisesRegex(ValueError, '43=generation_mismatch'):
            replay_texture_budget(text, BUDGET_RUN)

    def test_refuses_foreign_run_and_underflow(self):
        with self.assertRaisesRegex(ValueError, 'identity'):
            replay_texture_budget(budget_log(), dict(BUDGET_RUN, run_uuid='foreign'))
        broken = budget_log().replace('delta-bytes=100 live-bytes=30 charge-count=2',
                                      'delta-bytes=101 live-bytes=29 charge-count=2')
        with self.assertRaisesRegex(ValueError, 'underflow|transition|snapshot'):
            replay_texture_budget(broken, BUDGET_RUN)

    def test_incomplete_owner_ring_blocks_an_otherwise_joined_live_owner(self):
        event = 'LC2_TEXTURE_OWNER_EVENT run-id=u-1 event-seq=1 t-ns=175 phase=initialize-start nvn-id=43 object-generation=43 generation-basis=nvn-object-id storage-owner=0 storage-owner-status=unresolved charge-bytes=0 pool-id=99 pool-generation=1 pool-status=recorded cpu-write-generation=0 source-write-generation=untracked status=started'
        summary = 'LC2_TEXTURE_OWNER_EVENTS_SUMMARY run-id=u-1 configured=512 claimed=1 final-claimed=1 emitted=1 incomplete=1 active=0 dropped=0 format-errors=0 complete=0'
        lines = budget_log().splitlines()
        lines[-1:-1] = [event, summary]
        with self.assertRaisesRegex(ValueError, '43=log_truncated'):
            replay_texture_budget(chr(10).join(lines)+chr(10), BUDGET_RUN)

    def test_owner_event_schema_is_explicit_for_legacy_logs(self):
        replay_texture_budget(budget_log(), BUDGET_RUN)
        with self.assertRaisesRegex(ValueError, '43=log_truncated'):
            replay_texture_budget(budget_log(), BUDGET_RUN, owner_events_expected=True)

    def test_expected_owner_ring_summary_is_required_even_with_no_active_owners(self):
        text = budget_log().replace(
            'LC2_TEXTURE_BUDGET_EVENT run-id=u-1 t-ns=150 action=sub texture-id=42 delta-bytes=100 live-bytes=30 charge-count=2 caller=1 status=recorded',
            'LC2_TEXTURE_BUDGET_EVENT run-id=u-1 t-ns=150 action=sub texture-id=42 delta-bytes=100 live-bytes=30 charge-count=2 caller=1 status=recorded' + chr(10) + 'LC2_TEXTURE_BUDGET_EVENT run-id=u-1 t-ns=155 action=sub texture-id=43 delta-bytes=30 live-bytes=0 charge-count=2 caller=1 status=recorded')
        text = text.replace('live-bytes=30 peak-bytes=130 charge-count=2 event-lines=3',
                            'live-bytes=0 peak-bytes=130 charge-count=2 event-lines=4')
        text = text.replace('t-ns=170 action=add texture-id=99 delta-bytes=1 live-bytes=31',
                            't-ns=170 action=add texture-id=99 delta-bytes=1 live-bytes=1')
        with self.assertRaisesRegex(ValueError, 'log_truncated'):
            replay_texture_budget(text, BUDGET_RUN, owner_events_expected=True)

    def test_refuses_nonmonotonic_budget_event_timestamps(self):
        text = budget_log().replace('t-ns=130 action=add texture-id=43',
                                    't-ns=109 action=add texture-id=43')
        with self.assertRaisesRegex(ValueError, 'not monotonic'):
            replay_texture_budget(text, BUDGET_RUN)

    def test_refuses_busy_or_overflowed_floor_sample(self):
        busy = budget_log().replace('status=sampled lock-rc=0', 'status=mutex-busy lock-rc=16')
        with self.assertRaisesRegex(ValueError, 'snapshot'):
            replay_texture_budget(busy, BUDGET_RUN)
        overflow = budget_log().replace('event-overflow=0 status=sampled', 'event-overflow=1 status=sampled')
        with self.assertRaisesRegex(ValueError, 'overflow'):
            replay_texture_budget(overflow, BUDGET_RUN)
    def test_replay_classifies_pair_emitted_after_floor_but_still_fails_closed(self):
        for missing_id in ('280', '288'):
            text = budget_log().replace(
                'LC2_TEXTURE_PAIR run-id=u-1 t-ns=105 phase=initialize id=43 object-generation=43 storage-owner=43 guest-bytes=30 charge-bytes=30 storage-status=no-live-gl-storage',
                f'LC2_TEXTURE_PAIR run-id=u-1 t-ns=170 phase=initialize id={missing_id} object-generation={missing_id} storage-owner={missing_id} guest-bytes=30 charge-bytes=30 storage-status=no-live-gl-storage')
            text = text.replace('texture-id=43', 'texture-id='+missing_id)
            with self.assertRaisesRegex(ValueError, rf'{missing_id}=pair_not_yet_emitted'):
                replay_texture_budget(text, BUDGET_RUN)

    def test_duplicate_bc_materialize_pairs_do_not_double_charge(self):
        pair = 'LC2_TEXTURE_PAIR run-id=u-1 t-ns=145 phase=bc-materialize id=43 object-generation=43 storage-owner=43 guest-bytes=30 charge-bytes=30 storage-status=recorded'
        text = budget_log().replace('phase=initialize id=43', 'phase=bc-materialize id=43')
        text = text.replace('LC2_LIFE_SUMMARY ', pair + chr(10) + 'LC2_LIFE_SUMMARY ')
        result = replay_texture_budget(text, BUDGET_RUN)
        self.assertEqual(result['budget']['live_ids'], ['43'])
        self.assertEqual(result['budget']['replay_bytes'], 30)

    def test_zero_charge_id_does_not_require_a_texture_pair(self):
        text = budget_log().replace(
            'LC2_TEXTURE_BUDGET_EVENT run-id=u-1 t-ns=150 action=sub texture-id=42 delta-bytes=100 live-bytes=30 charge-count=2',
            'LC2_TEXTURE_BUDGET_EVENT run-id=u-1 t-ns=135 action=add texture-id=99 delta-bytes=0 live-bytes=130 charge-count=3 caller=9 status=recorded' + chr(10) + 'LC2_TEXTURE_BUDGET_EVENT run-id=u-1 t-ns=150 action=sub texture-id=42 delta-bytes=100 live-bytes=30 charge-count=3')
        text = text.replace('peak-bytes=130 charge-count=2 event-lines=3',
                            'peak-bytes=130 charge-count=3 event-lines=4')
        text = text.replace('t-ns=170 action=add texture-id=99 delta-bytes=1 live-bytes=31 charge-count=3',
                            't-ns=170 action=add texture-id=99 delta-bytes=1 live-bytes=31 charge-count=4')
        result = replay_texture_budget(text, BUDGET_RUN)
        self.assertEqual(result['budget']['live_ids'], ['43'])
        self.assertEqual(result['budget']['charge_count'], 3)


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
