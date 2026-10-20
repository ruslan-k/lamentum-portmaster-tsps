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

    def test_kill_of_different_log_pid_is_not_owned_oom(self):
        self.assertEqual(classify_exit(KILL.replace('26250', '123'), kernel_before=kernel(100),
                                     kernel_after=kernel(130, OOM), owner=OWNER)['kind'], 'sigkill_unknown')


class HarnessEvidenceIntegrationTests(unittest.TestCase):
    def test_kernel_receipts_and_owner_control_exit_code(self):
        # All SSH/process boundaries below are synthetic; no game or kernel OOM is induced.
        state = {'game': [], 'processes': {k: [{'pid': n, 'starttime': 1}]
                 for k, n in (('MainUI', 100), ('principal.sh', 101), ('runtime.sh', 102))},
                 'online': '0-7'}
        log = 'STOP status=TIME_LIMIT\n' + KILL + 'exit status 137\n'

        def fake_ssh(cmd, timeout=60):
            text = ('1' if cmd.startswith('ps | grep -cE') else
                    '100' if cmd.startswith("ps | grep '[M]ainUI'") else
                    log if cmd.startswith(('tail -c', 'cat ')) else '')
            return subprocess.CompletedProcess(cmd, 0, stdout=text, stderr='')

        for receipt, expected_code, expected_kind in ((kernel(130, OOM), 8, 'kernel_oom_sigkill'),
                                                       (kernel(130, '', ok=False), 7, 'sigkill_unknown')):
            with self.subTest(kind=expected_kind), tempfile.TemporaryDirectory() as directory:
                argv = ['device_principal_test.py', '--evidence', directory]
                owner = dict(OWNER, running=True, sample_status='ok')
                with patch.object(harness.sys, 'argv', argv), \
                     patch.object(harness, 'ssh', side_effect=fake_ssh), \
                     patch.object(harness, 'snapshot', return_value=state), \
                     patch.object(harness, 'remote', side_effect=[kernel(100), owner, receipt]), \
                     patch.object(harness.time, 'sleep'), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(harness.main(), expected_code)
                result = json.loads((Path(directory) / 'cleanup.json').read_text())
                self.assertEqual(result['termination']['kind'], expected_kind)
                self.assertEqual(result['process_identity'], OWNER)
                self.assertEqual(result['cleanup_errors'], [])
                self.assertTrue((Path(directory) / 'kernel-before.json').exists())
                self.assertTrue((Path(directory) / 'kernel-after.json').exists())

    def test_busy_preflight_does_not_truncate_old_log(self):
        with patch.object(harness.sys, 'argv', ['device_principal_test.py']), \
             patch.object(harness, 'ssh', return_value=subprocess.CompletedProcess('ssh', 0, stdout='1')) as ssh, \
             patch.object(harness, 'snapshot', return_value={'game': [{'pid': 1}], 'processes': {}}), \
             contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(harness.main(), 2)
            self.assertFalse(any('truncate' in call.args[0] for call in ssh.call_args_list))


if __name__ == '__main__':
    unittest.main()
