import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from proc_metrics import collect_proc, cpu_delta, parse_stat, sample_request


def sample(t, ticks, *, hz=250, start=42, tid_start=43):
    return {'running': True, 'boot_id': 'boot-a', 'pid': 17, 'starttime': start,
            'target_hz': hz, 'monotonic_s': t, 'total_cpu_ticks': ticks,
            'minflt': 100, 'majflt': 3,
            'threads': {'18': {'name': 'worker (one)', 'starttime': tid_start,
                               'cpu': ticks, 'state': 'R', 'minflt': 10, 'majflt': 1,
                               'schedstat': [1000, 2000, 3], 'wchan': '0'}}}


class CpuDeltaTests(unittest.TestCase):
    def test_target_hz_and_target_elapsed_not_host_clock(self):
        old = sample(10.0, 100)
        new = sample(12.0, 350)
        new['threads']['18']['schedstat'] = [500001000, 250002000, 8]
        out = cpu_delta(old, new)
        self.assertEqual(out['cpu_percent'], 50.0)
        self.assertEqual(out['thread_deltas'][0]['cpu_ms_per_s'], 500.0)
        self.assertEqual(out['thread_deltas'][0]['run_ns'], 500000000)
        self.assertEqual(out['thread_deltas'][0]['wait_ns'], 250000000)
        self.assertEqual(out['thread_deltas'][0]['timeslices'], 5)


class CollectorExecutionTests(unittest.TestCase):
    def test_zombie_is_not_live_and_comm_alone_does_not_own_a_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'sys/kernel/random').mkdir(parents=True)
            (root / 'sys/kernel/random/boot_id').write_text('fixture-boot')
            process = root / '77'
            process.mkdir()
            (process / 'comm').write_text('terminator2d-ne')
            (process / 'stat').write_text('77 (terminator2d-ne) Z 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21')
            zombie = collect_proc(pid=77, proc_root=str(root))
            self.assertFalse(zombie['running'])
            self.assertEqual(zombie['sample_status'], 'exited')
            discovered = collect_proc(proc_root=str(root))
            self.assertFalse(discovered['running'])
            self.assertEqual(discovered['sample_status'], 'absent')

    def test_exact_generated_remote_payload_reads_a_live_process(self):
        source = sample_request(pid=os.getpid())
        run = subprocess.run([sys.executable, '-c', source], capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 0, run.stderr)
        out = json.loads(run.stdout)
        self.assertTrue(out['running'])
        self.assertEqual(out['pid'], os.getpid())
        self.assertGreater(out['target_hz'], 0)
        self.assertGreater(out['starttime'], 0)
        self.assertIn(str(os.getpid()), out['threads'])
        self.assertIn('schedstat', out['threads'][str(os.getpid())])

    def test_expected_process_identity_is_enforced(self):
        first = collect_proc(pid=os.getpid())
        expected = {k: first[k] for k in ('boot_id', 'pid', 'starttime')}
        self.assertTrue(collect_proc(expected=expected)['running'])
        expected['starttime'] += 1
        stale = collect_proc(expected=expected)
        self.assertFalse(stale['running'])
        self.assertEqual(stale['sample_status'], 'identity_mismatch')


class IdentityAndStatTests(unittest.TestCase):
    def test_stat_name_with_spaces_and_parentheses(self):
        row = parse_stat('17 (a name ) with (paren)) R 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21')
        self.assertEqual(row['name'], 'a name ) with (paren)')
        self.assertEqual(row['cpu'], 23)
        self.assertEqual(row['starttime'], 19)
        self.assertEqual(row['minflt'], 7)
        self.assertEqual(row['majflt'], 9)

    def test_process_reuse_or_reboot_never_yields_cpu_delta(self):
        old = sample(10, 100)
        for key, value in (('starttime', 900), ('boot_id', 'boot-b'), ('pid', 99), ('target_hz', 100)):
            new = sample(12, 350)
            new[key] = value
            with self.subTest(key=key):
                self.assertEqual(cpu_delta(old, new), {'delta_status': 'identity_changed'})

    def test_reused_tid_is_not_the_old_thread(self):
        out = cpu_delta(sample(10, 100), sample(12, 350, tid_start=999))
        self.assertEqual(out['delta_status'], 'ok')
        self.assertEqual(out['thread_deltas'], [])

    def test_gap_or_bad_clock_does_not_create_negative_cpu(self):
        for old, new in ((None, sample(12, 350)),
                         ({'running': False}, sample(12, 350)),
                         (sample(10, 100), {'running': False})):
            self.assertEqual(cpu_delta(old, new)['delta_status'], 'no_live_pair')
        for t, ticks in ((9, 350), (10, 350), (12, 50)):
            self.assertEqual(cpu_delta(sample(10, 100), sample(t, ticks))['delta_status'],
                             'invalid_clock_or_counter')

    def test_all_thread_deltas_kept_and_process_cpu_not_sum_of_live_threads(self):
        old, new = sample(10, 100), sample(12, 350)
        new['threads']['18']['cpu'] = 150
        for n in range(19, 26):
            old['threads'][str(n)] = dict(old['threads']['18'])
            new['threads'][str(n)] = dict(new['threads']['18'])
        out = cpu_delta(old, new)
        self.assertEqual(len(out['thread_deltas']), 8)
        self.assertEqual(len(out['top_threads']), 6)
        self.assertEqual(out['cpu_percent'], 50.0)
        self.assertEqual(out['thread_deltas'][0]['cpu_ms_per_s'], 100.0)


if __name__ == '__main__':
    unittest.main()
