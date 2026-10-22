#!/usr/bin/env python3
"""Evidence-gated termination taxonomy. A shell 'Killed' token is not an OOM receipt."""
import re


KERNEL_PAYLOAD = r'''
import json, os, subprocess, time
from pathlib import Path
try:
    result = subprocess.run(['dmesg'], capture_output=True, text=True, errors='replace', timeout=10)
    data = {'available': result.returncode == 0, 'text': result.stdout,
            'error': result.stderr, 'returncode': result.returncode}
except (OSError, subprocess.TimeoutExpired) as exc:
    data = {'available': False, 'text': '', 'error': type(exc).__name__}
data.update(boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
            monotonic_s=time.monotonic(), target_hz=os.sysconf('SC_CLK_TCK'))
print(json.dumps(data))
'''


def classify_exit(log, *, host_terminated=None, kernel_before=None, kernel_after=None, owner=None):
    stops = [line[len('STOP status='):].split(' ',1)[0] for line in log.splitlines()
             if line.startswith('STOP status=') and line[len('STOP status='):]]
    result = {'kind': 'exit_unknown', 'stops': stops, 'oom_evidence': []}
    if host_terminated:
        result['kind'] = 'host_timeout'
        return result
    if stops:
        result['kind'] = ('invalid_configuration' if any(s.startswith('INVALID_') for s in stops)
                          else 'runtime_timeout' if all(s == 'TIME_LIMIT' for s in stops)
                          else 'runtime_stop')
    if not re.search(r'\bKilled\b|exit status 137', log):
        return result
    result['kind'] = 'sigkill_unknown'
    before, after = kernel_before or {}, kernel_after or {}
    if not owner or not before.get('available') or not after.get('available'):
        return result
    if not owner.get('boot_id') or not (owner['boot_id'] == before.get('boot_id') == after.get('boot_id')):
        return result
    if before.get('target_hz', 0) <= 0 or before.get('target_hz') != after.get('target_hz'):
        return result
    lower, upper = before.get('monotonic_s'), after.get('monotonic_s')
    if lower is None or upper is None or upper < lower:
        return result
    pid = owner['pid']
    shell_pids = {int(x) for x in re.findall(r'\b(\d+)\s+Killed\b', log)}
    if shell_pids and shell_pids != {pid}:
        return result
    earliest = max(lower, owner['starttime'] / before['target_hz'])
    # Only a timestamped kernel victim line proves OOM; a Mali notifier alone does not.
    # Unknown kernel formats or clock disagreements remain unknown, not heuristic positives.
    pattern = r'^\s*\[\s*(\d+(?:\.\d+)?)\]\s+.*?Out of memory: Killed process (\d+) \(([^)]*)\)'
    for match in re.finditer(pattern, after.get('text', ''), re.MULTILINE | re.IGNORECASE):
        timestamp, victim = float(match[1]), int(match[2])
        if victim == pid and earliest <= timestamp <= upper:
            result['oom_evidence'].append({'pid': victim, 'kernel_timestamp_s': timestamp,
                                           'comm': match[3], 'line': match[0]})
    if result['oom_evidence']:
        result['kind'] = 'kernel_oom_sigkill'
    return result
