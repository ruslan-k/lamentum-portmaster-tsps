import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import device_principal_test as harness
from exit_outcome import classify_exit


def kernel(t, text='', boot='boot-a', ok=True):
    return {'boot_id': boot, 'monotonic_s': t, 'target_hz': 100,
            'available': ok, 'text': text}


OWNER = {'boot_id': 'boot-a', 'pid': 26250, 'starttime': 10500}
KILL = 'Lamentum.sh: line 56: 26250 Killed ./lamentum-nextos\n'
OOM = '[ 120.500] Out of memory: Killed process 26250 (terminator2d-ne) total-vm:999kB\n'


class ExitEvidenceTests(unittest.TestCase):
    def test_killed_without_kernel_victim_is_unknown_not_oom(self):
        self.assertEqual(classify_exit(KILL)['kind'], 'sigkill_unknown')

    def test_oom_requires_matching_boot_pid_and_run_time(self):
        result = classify_exit(KILL, kernel_before=kernel(100), kernel_after=kernel(130, OOM), owner=OWNER)
        self.assertEqual(result['kind'], 'kernel_oom_sigkill')
        self.assertEqual(result['oom_evidence'][0]['pid'], 26250)

    def test_stale_foreign_and_unavailable_evidence_cannot_prove_oom(self):
        variants = [
            (kernel(121), kernel(130, OOM), OWNER),
            (kernel(100), kernel(120, OOM), OWNER),
            (kernel(100), kernel(130, OOM, boot='new-boot'), OWNER),
            (kernel(100), kernel(130, OOM.replace('26250', '123')), OWNER),
            (kernel(100), kernel(130, OOM, ok=False), OWNER),
            (kernel(100), kernel(130, OOM), None),
            (kernel(100), kernel(130, OOM), dict(OWNER, starttime=12500)),
        ]
        for before, after, owner in variants:
            with self.subTest(before=before, after=after, owner=owner):
                self.assertEqual(classify_exit(KILL, kernel_before=before, kernel_after=after,
                                               owner=owner)['kind'], 'sigkill_unknown')

    def test_kill_during_stop_teardown_is_not_hidden_by_time_limit(self):
        log = 'STOP status=TIME_LIMIT\n' + KILL
        result = classify_exit(log, kernel_before=kernel(100), kernel_after=kernel(130, OOM), owner=OWNER)
        self.assertEqual(result['kind'], 'kernel_oom_sigkill')
        self.assertEqual(result['stops'], ['TIME_LIMIT'])
        self.assertEqual(classify_exit(log)['kind'], 'sigkill_unknown')

    def test_mali_notifier_alone_is_not_an_oom_victim_receipt(self):
        text = '[ 120.500] mali: OOM notifier for terminator2d-ne GPU memory 725992 kB\n'
        self.assertEqual(classify_exit(KILL, kernel_before=kernel(100),
                                     kernel_after=kernel(130, text), owner=OWNER)['kind'], 'sigkill_unknown')

    def test_host_stop_and_runtime_stops_keep_their_own_taxonomy(self):
        self.assertEqual(classify_exit(KILL, host_terminated={'pids': [26250]})['kind'], 'host_timeout')
        self.assertEqual(classify_exit('STOP status=T2_TEXTURE_BUDGET\n')['kind'], 'runtime_stop')
        self.assertEqual(classify_exit('STOP status=TIME_LIMIT\n')['kind'], 'runtime_timeout')
        self.assertEqual(classify_exit('STOP status=INVALID_PROBE_TIME_BUDGET\n')['kind'], 'invalid_configuration')
        self.assertEqual(classify_exit('no stop receipt')['kind'], 'exit_unknown')

    def test_diagnostic_marker_containing_stop_word_is_not_a_runtime_stop(self):
        log = 'LC2_MENU_LEDGER_PRESTOP status=gl-lock-unavailable\\n'
        result = classify_exit(log)
        self.assertEqual(result['kind'], 'exit_unknown')
        self.assertEqual(result['stops'], [])

    def test_kill_of_different_log_pid_is_not_owned_oom(self):
        self.assertEqual(classify_exit(KILL.replace('26250', '123'), kernel_before=kernel(100),
                                     kernel_after=kernel(130, OOM), owner=OWNER)['kind'], 'sigkill_unknown')


class HarnessEvidenceIntegrationTests(unittest.TestCase):
    def test_kernel_receipts_and_owner_control_exit_code(self):
        # Synthetic RPC/supervisor boundaries ONLY. No game, OOM or MainUI signal.
        import hashlib
        from load_metrics import parse_chunk
        state = {'game': [], 'processes': {key: [{'pid': value, 'starttime': 1}]
                 for key, value in (('MainUI', 100), ('principal.sh', 101), ('runtime.sh', 102))},
                 'online': '0-7'}
        run_uuid = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
        repo = Path(__file__).resolve().parents[1]
        preflight = {'boot_id': OWNER['boot_id'], 'runtime': {'dev': 1, 'ino': 2, 'sha256': 'a'*64},
                     'launcher': {'sha256': hashlib.sha256((repo/'port/Lamentum.sh').read_bytes()).hexdigest()},
                     'helper': {'sha256': hashlib.sha256((repo/'tools/run_identity.py').read_bytes()).hexdigest()}}
        for receipt, expected_code, expected_kind, killed, changed_generation in (
                (kernel(130, OOM), 8, 'kernel_oom_sigkill', True, False),
                (kernel(130, '', ok=False), 7, 'sigkill_unknown', True, False),
                (kernel(130), 0, 'runtime_timeout', False, False),
                (kernel(130), 9, 'exit_unknown', False, True)):
            with self.subTest(kind=expected_kind), tempfile.TemporaryDirectory() as directory:
                log = chr(10).join(('LC2_MENU_LEDGER_PRESTOP status=gl-lock-unavailable',
                                    'STOP status=TIME_LIMIT')) + chr(10) + (KILL + 'exit status 137' + chr(10) if killed else '')
                owned = dict(OWNER, elf_dev=1, elf_ino=2)
                kernel_polls = []
                def fake_remote(source):
                    if source == harness.KERNEL_PAYLOAD:
                        kernel_polls.append(1)
                        return kernel(100) if len(kernel_polls) == 1 else receipt
                    if source.startswith('import os,stat,hashlib,json'):
                        return preflight
                    if 'print(json.dumps({"run_uuid":new_run_uuid()}))' in source:
                        return {'run_uuid': run_uuid}
                    if 'p.write_text(text)' in source:
                        return {'command': harness.launch_command(run_uuid, 90, [])}
                    if 'assert (p/"comm").read_text().strip()=="MainUI"' in source:
                        return {'pid': 100, 'starttime': 1, 'boot_id': OWNER['boot_id'], 'elf_dev': 1, 'elf_ino': 3}
                    if 'print(json.dumps(terminate_owned(' in source:
                        return {'outcome': 'pidfd_TERM'}
                    if source.startswith('import sys\nsys.argv='):
                        expected = json.loads((Path(directory)/'expected-run.json').read_text())
                        if changed_generation and '_include_text=True' in source:
                            return dict(parse_chunk(''), strict=True, status='LOG_GENERATION_CHANGED',
                                        expected_run=expected, reason='synthetic final-log replacement')
                        header = dict(expected, **{key: value for key, value in owned.items() if key not in expected},
                                      launch_nonce='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb')
                        return dict(parse_chunk(log), strict=True, status='ok', rotated=False,
                                    offset=len(log), size=len(log), identity=[1, 4], mem={},
                                    log_identity_qualified=True, run_header=header, expected_run=expected,
                                    header_sha256='c'*64, anchor=None, chunk_text=log, partial_bytes=0)
                    if 'collect_proc(pid=' in source:
                        return dict(owned, running=True, sample_status='ok')
                    raise RuntimeError('unexpected synthetic RPC boundary')
                with patch.object(harness.sys, 'argv', ['device_principal_test.py', '--evidence', directory]), \
                     patch.object(harness, 'snapshot', return_value=state), \
                     patch.object(harness, 'remote', side_effect=fake_remote), \
                     patch.object(harness.time, 'sleep'), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(harness.main(), expected_code)
                result = json.loads((Path(directory)/'cleanup.json').read_text())
                self.assertEqual(result['termination']['kind'], expected_kind)
                self.assertEqual(result['process_identity'], owned)
                self.assertEqual(result['cleanup_errors'], [])
                expected_stops = [] if changed_generation else ['TIME_LIMIT']
                self.assertEqual(result['stops'], expected_stops)
                self.assertEqual(result['termination']['stops'], expected_stops)
                self.assertTrue(result['execution_verified'])
                self.assertFalse(result['content_bindings_complete'])
                self.assertTrue((Path(directory)/'kernel-before.json').exists())
                self.assertTrue((Path(directory)/'kernel-after.json').exists())

    def test_busy_preflight_does_not_touch_old_log_or_device(self):
        with patch.object(harness.sys, 'argv', ['device_principal_test.py']), \
             patch.object(harness, 'remote') as remote, \
             patch.object(harness, 'snapshot', return_value={'game': [{'pid': 1}], 'processes': {}}), \
             contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(harness.main(), 2)
            remote.assert_not_called()



if __name__ == '__main__':
    unittest.main()
