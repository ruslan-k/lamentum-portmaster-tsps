import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from proc_metrics import collect_proc, cpu_delta, parse_stat, sample_request
import proc_metrics


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
    def test_same_inode_path_alias_is_accepted_but_different_file_is_not(self):
        # Hard links reproduce same dev/inode with unequal resolved strings on ordinary host FS.
        # On TSPS the observed equivalent paths came from case-insensitive Roms/ports vs PORTS.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'sys/kernel/random').mkdir(parents=True)
            (root / 'sys/kernel/random/boot_id').write_text('fixture-boot')
            process = root / '77'
            process.mkdir()
            (process / 'comm').write_text('terminator2d-ne')
            (process / 'stat').write_text('77 (terminator2d-ne) Z 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21')
            actual = root / 'actual-binary'
            alias = root / 'expected-alias'
            actual.write_bytes(b'self-authored fixture, not game code')
            os.link(actual, alias)
            (process / 'exe').symlink_to(actual)
            accepted = collect_proc(proc_root=str(root), runtime_path=str(alias))
            self.assertEqual(accepted['sample_status'], 'exited')
            self.assertEqual(accepted['pid'], 77)
            alias.unlink()
            alias.write_bytes(actual.read_bytes())
            rejected = collect_proc(proc_root=str(root), runtime_path=str(alias))
            self.assertEqual(rejected['sample_status'], 'absent')

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

    def test_unpinned_runtime_discovery_returns_executable_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'proc'
            (root / 'sys/kernel/random').mkdir(parents=True)
            (root / 'sys/kernel/random/boot_id').write_text('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa')
            process = root / '77'
            (process / 'task').mkdir(parents=True)
            (process / 'comm').write_text('terminator2d-ne')
            stat = '77 (terminator2d-ne) R 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21'
            (process / 'stat').write_text(stat)
            (process / 'status').write_text('VmRSS: 10 kB\nVmSwap: 0 kB\n')
            executable = Path(directory) / 'runtime'
            executable.write_bytes(b'self-authored runtime identity fixture')
            (process / 'exe').symlink_to(executable)
            row = collect_proc(proc_root=str(root), runtime_path=str(executable))
            self.assertTrue(row['running'])
            self.assertEqual(row['elf_dev'], os.stat(executable).st_dev)
            self.assertEqual(row['elf_ino'], os.stat(executable).st_ino)

    def test_expected_exec_inode_is_checked_even_when_pid_generation_matches(self):
        actual = collect_proc(pid=os.getpid())
        metadata = os.stat('/proc/self/exe')
        expected = {k: actual[k] for k in ('boot_id', 'pid', 'starttime')}
        expected.update(elf_dev=metadata.st_dev, elf_ino=metadata.st_ino)
        accepted = collect_proc(expected=expected)
        self.assertEqual(accepted.get('elf_ino'), metadata.st_ino)
        expected['elf_ino'] += 1
        self.assertEqual(collect_proc(expected=expected)['sample_status'], 'identity_mismatch')

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


class MemoryTimelineTests(unittest.TestCase):
    def test_prelaunch_system_sample_keeps_missing_values_unknown(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'proc'
            (root / 'sys/kernel/random').mkdir(parents=True)
            boot = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
            (root / 'sys/kernel/random/boot_id').write_text(boot)
            (root / 'meminfo').write_text('MemTotal: 1000 kB\nMemAvailable: 500 kB\nSwapTotal: 2000 kB\nSwapFree: 1500 kB\n')
            (root / 'vmstat').write_text('pgfault 20\n')
            expected = {'boot_id': boot, 'elf_sha256': 'a' * 64, 'elf_dev': 9, 'elf_ino': 10}
            sample = proc_metrics.collect_memory_system_sample(expected,
                'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb', expected['elf_sha256'], proc_root=str(root))
            self.assertEqual(sample['sample_status'], 'ok')
            self.assertEqual(sample['pid'], None)
            self.assertEqual(sample['phase'], 'prelaunch')
            self.assertEqual((sample['elf_dev'],sample['elf_ino']),(9,10))
            self.assertEqual(sample['system']['MemAvailable_kib'], 500)
            self.assertIsNone(sample['system']['CmaFree_kib'])
            self.assertIsNone(sample['vmstat']['pswpin'])
            self.assertIsNone(sample['pressure_memory'])

    def test_system_memory_request_serializes_tested_function(self):
        run_uuid = 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'
        expected = {'boot_id': 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'}
        source = proc_metrics.system_memory_request(expected, run_uuid, 'a' * 64)
        compile(source, '<remote-system-memory>', 'exec')
        self.assertIn(run_uuid, source)
        self.assertIn(expected['boot_id'], source)
        self.assertIn('collect_memory_system_sample', source)

    def test_attach_discovery_uses_executable_inode_and_boot_id(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'proc'
            (root / 'sys/kernel/random').mkdir(parents=True)
            boot = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
            (root / 'sys/kernel/random/boot_id').write_text(boot)
            executable = Path(directory) / 'runtime'
            executable.write_bytes(b'self-authored runtime identity fixture')
            process = root / '77'
            (process / 'task').mkdir(parents=True)
            (process / 'comm').write_text('terminator2d-ne')
            (process / 'stat').write_text('77 (terminator2d-ne) R 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21')
            (process / 'exe').symlink_to(executable)
            expected = {'boot_id': boot, 'elf_dev': os.stat(executable).st_dev,
                        'elf_ino': os.stat(executable).st_ino}
            owner = proc_metrics.discover_memory_owner(expected, proc_root=str(root))
            self.assertEqual(owner['status'], 'ok')
            self.assertEqual((owner['pid'], owner['starttime']), (77, 19))
            self.assertEqual((owner['elf_dev'], owner['elf_ino']),
                             (expected['elf_dev'], expected['elf_ino']))

    def test_sparse_smaps_sample_records_read_duration(self):
        owner = collect_proc(pid=os.getpid())
        expected = {key: owner[key] for key in ('boot_id','pid','starttime','elf_dev','elf_ino')}
        sample = proc_metrics.collect_memory_sample(expected,
            'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa','a'*64,sample_seq=39)
        self.assertEqual(sample['sample_status'],'ok')
        self.assertIn(sample['smaps_rollup']['status'],('ok','unavailable'))
        self.assertGreaterEqual(sample['smaps_rollup']['read_duration_ns'],0)

    def test_bounded_target_timeline_carries_run_and_process_identity(self):
        live = collect_proc(pid=os.getpid())
        exe = os.stat('/proc/self/exe')
        expected = {key: live[key] for key in ('boot_id', 'pid', 'starttime')}
        expected.update(elf_dev=exe.st_dev, elf_ino=exe.st_ino)
        run_uuid = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
        elf_sha256 = 'a' * 64
        source = proc_metrics.memory_timeline_request(
            expected, run_uuid, elf_sha256, max_samples=2, interval_ms=10)
        compile(source, '<memory-timeline-payload>', 'exec')
        run = subprocess.run([sys.executable, '-c', source], capture_output=True,
                             text=True, timeout=10)
        self.assertEqual(run.returncode, 0, run.stderr)
        timeline = json.loads(run.stdout)
        self.assertEqual(timeline['run_uuid'], run_uuid)
        self.assertEqual(timeline['elf_sha256'], elf_sha256)
        self.assertEqual(timeline['identity'], expected)
        self.assertEqual(timeline['sample_count'], 2)
        self.assertFalse(timeline['complete'])
        self.assertEqual(timeline['stop_reason'], 'sample-limit')
        self.assertEqual(timeline['dropped_samples'], 0)
        first, second = timeline['samples']
        self.assertEqual(first['phase'], 'process-attach')
        self.assertEqual(first['sample_status'], 'ok')
        self.assertEqual(second['phase'], 'sampling')
        self.assertGreater(second['t_monotonic_ns'], first['t_monotonic_ns'])
        self.assertGreater(first['process']['VmRSS_kib'], 0)
        self.assertIsNotNone(first['process']['VmHWM_kib'])
        self.assertIn('CmaFree_kib', first['system'])
        self.assertIn('pswpin', first['vmstat'])
        self.assertIn('pressure_memory', first)
        self.assertIn(first['smaps_rollup']['status'], ('not-scheduled', 'ok', 'unavailable'))


if __name__ == '__main__':
    unittest.main()
