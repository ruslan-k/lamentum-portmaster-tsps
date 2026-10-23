import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from device_principal_test import should_hard_stop, is_killed_without_stop


import device_principal_test as principal


class OwnedLaunchTests(unittest.TestCase):
    def test_memory_timeline_requires_local_evidence_directory(self):
        with self.assertRaises(SystemExit):
            principal.parse_args(['--memory-timeline'])
        args = principal.parse_args(['--memory-timeline', '--evidence', 'evidence/m3b-test'])
        self.assertTrue(args.memory_timeline)
        self.assertEqual(args.evidence, Path('evidence/m3b-test'))

    def test_uuid_is_explicit_and_reserved_env_cannot_replace_it(self):
        self.assertTrue(hasattr(principal, 'launch_command'), 'owned principal launch contract is missing')
        uuid = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
        command = principal.launch_command(uuid, 90, ['T2_TEXTURE_BUDGET_MIB=300'])
        self.assertIn('LAMENTUM_RUN_UUID=' + uuid, command)
        self.assertIn('LAMENTUM_PROBE_SECONDS=90', command)
        self.assertIn('/mnt/SDCARD/Emu/PORTS/../../', command)
        for value in ('LAMENTUM_RUN_UUID=wrong', 'LAMENTUM_PROBE_SECONDS=0', 'bad=value'):
            with self.assertRaises(ValueError):
                principal.launch_command(uuid, 90, [value])
        with self.assertRaises(ValueError):
            principal.launch_command('123', 90, [])
        with self.assertRaises(ValueError):
            principal.launch_command(uuid, 0, [])


class HardStopTests(unittest.TestCase):
    def test_rejected_or_racing_stop_is_not_claimed_as_a_delivered_host_term(self):
        self.assertTrue(hasattr(principal, 'confirmed_host_termination'), 'pidfd receipt qualification is missing')
        for result in ({'outcome': 'already_exited'}, {'outcome': 'identity_mismatch'},
                       {'outcome': 'pidfd_unavailable'}, {'outcome': 'pidfd_error'}):
            self.assertIsNone(principal.confirmed_host_termination(result))
        delivered = {'outcome': 'pidfd_TERM'}
        self.assertIs(principal.confirmed_host_termination(delivered), delivered)

    def test_stops_only_past_deadline_with_a_live_game(self):
        self.assertTrue(should_hard_stop(100, 90, [4321]))
        self.assertFalse(should_hard_stop(100, 120, [4321]))
        self.assertFalse(should_hard_stop(100, 90, []))

    def test_disabled_bound_never_kills(self):
        self.assertFalse(should_hard_stop(10 ** 9, None, [4321]))
        self.assertFalse(should_hard_stop(10 ** 9, 0, [4321]))


class KillClassificationTests(unittest.TestCase):
    def test_sigkill_without_stop_is_only_a_cause_unknown_hint(self):
        log = 'AUDOUT_HOST_PROFILE ...\n... Lamentum.sh: line 56: 26250 Killed                  ./lamentum-nextos\n'
        self.assertTrue(is_killed_without_stop(log, []))

    def test_a_real_stop_is_not_reclassified(self):
        self.assertFalse(is_killed_without_stop('Killed\nSTOP status=TIME_LIMIT', ['TIME_LIMIT']))

    def test_normal_exit_is_not_a_kill(self):
        self.assertFalse(is_killed_without_stop('NATIVE_PROBE_TIME_BUDGET seconds=900\n', []))


class MemoryTimelineReceiptTests(unittest.TestCase):
    def test_raw_timeline_is_saved_with_a_compact_hash_receipt(self):
        timeline = {'run_uuid': 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
                    'sample_count': 1, 'complete': True, 'dropped_samples': 0,
                    'stop_reason': 'process-exited', 'samples': [{'seq': 0, 'sample_status': 'ok', 'running': True}]}
        with tempfile.TemporaryDirectory() as directory:
            summary = principal.store_memory_timeline(timeline, Path(directory))
            raw = Path(directory) / 'memory-timeline.raw.json'
            self.assertEqual(json.loads(raw.read_text()), timeline)
            self.assertEqual(summary['sha256'], hashlib.sha256(raw.read_bytes()).hexdigest())
            self.assertEqual(summary['sample_count'], 1)
            self.assertEqual(summary['live_samples'], 1)
            self.assertTrue(summary['complete'])
            self.assertNotIn('samples', summary)

    def test_memory_timeline_call_binds_preflight_and_run_before_saving(self):
        run_uuid = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
        expected = {'run_uuid': run_uuid, 'elf_sha256': 'a' * 64, 'boot_id': run_uuid,
                    'elf_dev': 9, 'elf_ino': 10}
        actual = {'boot_id': run_uuid, 'pid': 77, 'starttime': 88, 'elf_dev': 9, 'elf_ino': 10}
        timeline = {'run_uuid': run_uuid, 'elf_sha256': expected['elf_sha256'],
                    'identity': actual, 'sample_count': 0, 'complete': False,
                    'dropped_samples': 0, 'stop_reason': 'attach-timeout', 'samples': []}
        seen = {}
        def remote_fn(source):
            compile(source, '<remote-memory-timeline>', 'exec')
            seen['source'] = source
            return timeline
        with tempfile.TemporaryDirectory() as directory:
            summary = principal.run_memory_timeline(remote_fn, expected, Path(directory))
            self.assertEqual(summary['run_uuid'], run_uuid)
            self.assertTrue(summary['identity_matches_preflight'])
            self.assertEqual(summary['identity']['pid'], 77)
            self.assertIn('9', seen['source'])
            self.assertIn(run_uuid, seen['source'])
            self.assertIn(expected['elf_sha256'], seen['source'])
            self.assertIn('256,100', seen['source'])
            self.assertTrue((Path(directory) / 'memory-timeline.raw.json').exists())
    def test_prelaunch_sample_is_merged_and_not_counted_as_live_runtime(self):
        run_uuid = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
        expected = {'run_uuid': run_uuid, 'elf_sha256': 'a' * 64, 'boot_id': run_uuid,
                    'elf_dev': 9, 'elf_ino': 10}
        identity = {'boot_id': run_uuid, 'pid': 77, 'starttime': 88, 'elf_dev': 9, 'elf_ino': 10}
        runtime_sample = {'run_uuid': run_uuid, 'boot_id': run_uuid, 'pid': 77, 'starttime': 88,
                          'elf_sha256': 'a' * 64, 'seq': 0, 'phase': 'process-attach',
                          'sample_status': 'ok', 'running': True}
        timeline = {'run_uuid': run_uuid, 'elf_sha256': 'a' * 64, 'identity': identity,
                    'sample_count': 1, 'complete': True, 'dropped_samples': 0,
                    'stop_reason': 'exited', 'samples': [runtime_sample]}
        prelaunch = {'run_uuid': run_uuid, 'boot_id': run_uuid, 'pid': None, 'starttime': None,
                     'elf_sha256': 'a' * 64, 'elf_dev': 9, 'elf_ino': 10,
                     'seq': 0, 'phase': 'prelaunch', 'sample_status': 'ok', 'running': False}
        with tempfile.TemporaryDirectory() as directory:
            summary = principal.run_memory_timeline(lambda source: timeline, expected, Path(directory),
                                                    prelaunch_sample=prelaunch,
                                                    mainui_exit={'outcome': 'pidfd_TERM'})
            raw = json.loads((Path(directory) / 'memory-timeline.raw.json').read_text())
        self.assertEqual(raw['sample_count'], 2)
        self.assertEqual(raw['samples'][0]['phase'], 'prelaunch')
        self.assertEqual(raw['samples'][0]['seq'], -1)
        self.assertEqual(raw['samples'][1]['phase'], 'process-attach')
        self.assertEqual(raw['external_landmarks']['mainui_exit']['outcome'], 'pidfd_TERM')
        self.assertEqual(summary['live_samples'], 1)
        self.assertEqual(summary['prelaunch_sample_status'], 'ok')
        bad_prelaunch = dict(prelaunch,elf_ino=11)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(RuntimeError):
                principal.run_memory_timeline(lambda source: timeline, expected, Path(directory),
                                              prelaunch_sample=bad_prelaunch)

    def test_timeline_execution_requires_matching_owner_and_live_sample(self):
        self.assertTrue(principal.memory_timeline_proves_execution(
            {'identity_matches_preflight': True, 'live_samples': 1}))
        self.assertFalse(principal.memory_timeline_proves_execution(
            {'identity_matches_preflight': False, 'live_samples': 1}))
        self.assertFalse(principal.memory_timeline_proves_execution(
            {'identity_matches_preflight': True, 'live_samples': 0}))
        self.assertFalse(principal.memory_timeline_proves_execution(None))


if __name__ == '__main__':
    unittest.main()
