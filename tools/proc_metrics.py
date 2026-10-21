#!/usr/bin/env python3
"""Target-side proc snapshots and identity-safe CPU deltas (roadmap §26.2.5)."""
import inspect
from typing import Any


def parse_stat(text):
    """Linux proc_pid_stat: comm may contain spaces and parentheses; fields follow last ')'."""
    end = text.rindex(')')
    begin = text.index('(')
    fields = text[end + 1:].split()
    return {'pid': int(text[:begin].strip()), 'name': text[begin + 1:end],
            'state': fields[0], 'cpu': int(fields[11]) + int(fields[12]),
            'minflt': int(fields[7]), 'majflt': int(fields[9]), 'starttime': int(fields[19])}


def collect_proc(pid=None, expected=None, proc_root='/proc',
                 runtime_path='/mnt/SDCARD/Roms/PORTS/lamentum-switch/lamentum-nextos'):
    """Read one unique runtime or an explicitly pinned PID; never combine process generations."""
    import os
    import time
    from pathlib import Path

    root = Path(proc_root)
    started = time.monotonic()
    cpu_started = time.process_time_ns()
    boot = (root / 'sys/kernel/random/boot_id').read_text().strip()
    hz = os.sysconf('SC_CLK_TCK')

    def optional(path):
        try:
            return path.read_text().strip()
        except OSError:
            return None

    if expected is not None:
        pid = expected['pid']
    if pid is None:
        candidates = []
        runtime = Path(runtime_path).resolve()
        for directory in root.iterdir():
            if directory.name.isdigit() and optional(directory / 'comm') in ('lamentum-nextos', 'terminator2d-ne'):
                try:
                    # Resolve by filesystem identity: VFAT paths can differ in spelling/case
                    # while naming the exact same executable. Do not lowercase or trust comm.
                    if os.path.samefile(directory / 'exe', runtime):
                        candidates.append(int(directory.name))
                except OSError:
                    continue
        if len(candidates) != 1:
            return {'running': False, 'sample_status': 'absent' if not candidates else 'ambiguous',
                    'candidates': candidates, 'boot_id': boot, 'target_hz': hz}
        pid = candidates[0]
    base = root / str(pid)
    try:
        first = parse_stat((base / 'stat').read_text())
        sample_time = time.monotonic()
        identity = {'boot_id': boot, 'pid': int(pid), 'starttime': first['starttime']}
        if expected is not None and any(expected[k] != identity[k] for k in identity):
            return dict(identity, running=False, sample_status='identity_mismatch', target_hz=hz)
        if first['state'] in ('Z', 'X', 'x'):
            return dict(identity, running=False, sample_status='exited', target_hz=hz)
        if expected is not None and any(key in expected for key in ('elf_dev', 'elf_ino')):
            executable = os.stat(base / 'exe')
            identity.update(elf_dev=executable.st_dev, elf_ino=executable.st_ino)
            if any(expected.get(key) != identity[key] for key in ('elf_dev', 'elf_ino')):
                return dict(identity, running=False, sample_status='identity_mismatch', target_hz=hz)
        threads = {}
        for thread in (base / 'task').iterdir():
            try:
                row = parse_stat((thread / 'stat').read_text())
                sched = optional(thread / 'schedstat')
                row['schedstat'] = [int(x) for x in sched.split()[:3]] if sched else None
                if row['schedstat'] is not None and len(row['schedstat']) != 3:
                    row['schedstat'] = None
                row['wchan'] = optional(thread / 'wchan')
                # TID reuse during the individual read invalidates that thread's fields.
                last = parse_stat((thread / 'stat').read_text())
                if row['starttime'] == last['starttime']:
                    threads[thread.name] = row
            except (OSError, ValueError, IndexError):
                continue
        memory = {}
        for line in (base / 'status').read_text().splitlines():
            key = line.split(':')[0]
            if key in ('VmRSS', 'VmSwap'):
                memory[key] = int(line.split()[1])
        wchan = optional(base / 'wchan')
        last = parse_stat((base / 'stat').read_text())
        final_boot = (root / 'sys/kernel/random/boot_id').read_text().strip()
        if 'elf_ino' in identity:
            executable = os.stat(base / 'exe')
            if (executable.st_dev, executable.st_ino) != (identity['elf_dev'], identity['elf_ino']):
                return dict(identity, running=False, sample_status='changed_during_read', target_hz=hz)
        if last['starttime'] != first['starttime'] or final_boot != boot:
            return dict(identity, running=False, sample_status='changed_during_read', target_hz=hz)
        if last['state'] in ('Z', 'X', 'x'):
            return dict(identity, running=False, sample_status='exited', target_hz=hz)
        return dict(identity, running=True, sample_status='ok', target_hz=hz,
                    monotonic_s=sample_time, sample_duration_s=time.monotonic() - started,
                    collector_cpu_ns=time.process_time_ns() - cpu_started,
                    total_cpu_ticks=first['cpu'], minflt=first['minflt'], majflt=first['majflt'],
                    state=first['state'], wchan=wchan, threads=threads,
                    rss_kb=memory.get('VmRSS'), swap_kb=memory.get('VmSwap'))
    except (OSError, ValueError, IndexError) as exc:
        return {'running': False, 'sample_status': 'unavailable', 'error': type(exc).__name__,
                'pid': int(pid), 'boot_id': boot, 'target_hz': hz}


def sample_request(expected=None, pid=None):
    """Serialize the tested functions, not a separate hand-maintained parser mirror."""
    return ('import json\n' + inspect.getsource(parse_stat) + '\n' + inspect.getsource(collect_proc)
            + '\nprint(json.dumps(collect_proc(pid=%r, expected=%r)))\n' % (pid, expected))


def cpu_delta(previous, current) -> dict[str, Any]:
    """Use process total ticks (including exited threads), target HZ and target monotonic time."""
    if not previous or not previous.get('running') or not current.get('running'):
        return {'delta_status': 'no_live_pair'}
    if any(previous.get(k) != current.get(k) for k in ('boot_id', 'pid', 'starttime', 'target_hz', 'elf_dev', 'elf_ino')):
        return {'delta_status': 'identity_changed'}
    dt = current['monotonic_s'] - previous['monotonic_s']
    hz = current['target_hz']
    ticks = current['total_cpu_ticks'] - previous['total_cpu_ticks']
    if dt <= 0 or hz <= 0 or ticks < 0:
        return {'delta_status': 'invalid_clock_or_counter'}
    threads = []
    for tid, row in current['threads'].items():
        old = previous['threads'].get(tid)
        if not old or old['starttime'] != row['starttime'] or row['cpu'] < old['cpu']:
            continue
        item = {'tid': tid, 'name': row['name'], 'starttime': row['starttime'],
                'state': row['state'], 'wchan': row.get('wchan'),
                'cpu_ms_per_s': round(1000.0 * (row['cpu'] - old['cpu']) / (hz * dt), 3),
                'minflt_delta': row['minflt'] - old['minflt'],
                'majflt_delta': row['majflt'] - old['majflt']}
        if row.get('schedstat') is not None and old.get('schedstat') is not None:
            for index, key in enumerate(('run_ns', 'wait_ns', 'timeslices')):
                item[key] = row['schedstat'][index] - old['schedstat'][index]
        threads.append(item)
    threads.sort(key=lambda item: -item['cpu_ms_per_s'])
    return {'delta_status': 'ok', 'elapsed_s': dt,
            'cpu_percent': round(100.0 * ticks / (hz * dt), 3),
            'minflt_per_s': (current['minflt'] - previous['minflt']) / dt,
            'majflt_per_s': (current['majflt'] - previous['majflt']) / dt,
            'thread_deltas': threads, 'top_threads': threads[:6]}
