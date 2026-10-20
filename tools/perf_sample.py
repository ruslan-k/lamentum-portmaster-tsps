#!/usr/bin/env python3
"""Start a principal-flow Lamentum run and sample its process (sampling is read-only).

  python3 tools/perf_sample.py <env.json> <evidence-name-or-absolute-dir>

CPU uses target HZ and monotonic time, process boot/PID/starttime, and TID/starttime.
Log counters are incremental diagnostics only: they are NOT a world/presentation identity or FPS.
"""
import argparse
import json
import os
import pathlib
import subprocess
import sys
import time
from typing import Any

from load_metrics import collector_request, fold
from proc_metrics import cpu_delta, sample_request

REPO = pathlib.Path(__file__).resolve().parents[1]
HOST = 'root@192.168.50.135'


def ssh(cmd, timeout=60, data=None):
    result = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', HOST, cmd],
                            input=data, capture_output=True, timeout=timeout)
    result.check_returncode()
    return result


def remote_json(source):
    result = ssh('python3 -', data=source.encode())
    # SSH/MOTD output may precede the one JSON result; a failed transport is never "not running".
    return json.loads(result.stdout.decode().strip().splitlines()[-1])


def sample(expected=None):
    return remote_json(sample_request(expected=expected))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('env', type=pathlib.Path)
    ap.add_argument('evidence', type=pathlib.Path)
    args = ap.parse_args(argv)
    out_dir = args.evidence if args.evidence.is_absolute() else REPO / 'evidence' / args.evidence
    env = json.loads(args.env.read_text())
    budget = int(os.environ.get('LAMENTUM_PERF_BUDGET', '420'))
    interval = float(os.environ.get('LAMENTUM_PERF_INTERVAL', '5'))
    if budget <= 0 or interval <= 0:
        ap.error('budget and interval must be positive')
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'env.json').write_text(json.dumps(env, indent=2) + '\n')
    cmd = [sys.executable, str(REPO / 'tools/device_principal_test.py'),
           '--budget', str(budget), '--wait', str(budget + 120), '--evidence', str(out_dir)]
    for entry in env:
        cmd += ['--env', entry]
    previous = None
    expected = None
    log_state = {}
    count = 0
    with (out_dir / 'harness.log').open('w') as harness_log, (out_dir / 'perf.jsonl').open('w') as output:
        harness = subprocess.Popen(cmd, cwd=str(REPO), stdout=harness_log, stderr=subprocess.STDOUT)
        deadline = time.monotonic() + budget + 150
        while time.monotonic() < deadline and harness.poll() is None:
            record: dict[str, Any] = {'t': time.time()}
            try:
                current = sample(expected)
                if current.get('running') and expected is None:
                    expected = {k: current[k] for k in ('boot_id', 'pid', 'starttime')}
                record['sample'] = current
                record.update(cpu_delta(previous, current))
                # A missed/dead sample breaks the delta pair; never bridge an unknown gap.
                previous = current if current.get('running') else None
                if current.get('running'):
                    try:
                        log_state = fold(log_state, remote_json(collector_request(log_state)))
                        record['log_metrics'] = log_state
                        record['frame'] = log_state.get('frame')
                        record['frame_scope'] = 'unverified log frame; not a scene or FPS measurement'
                    except Exception as exc:
                        record['log_error'] = str(exc)
            except Exception as exc:
                record['sample_error'] = str(exc)
                previous = None
            output.write(json.dumps(record) + '\n')
            output.flush()
            count += 1
            time.sleep(interval)
        # The principal harness owns exact-PID hard stopping and cleanup; do not kill its supervisor.
        harness.wait(timeout=90)
    result = {'harness_rc': harness.returncode, 'samples': count,
              'process_identity': expected, 'scope': 'CPU diagnostics, not gameplay FPS'}
    print(json.dumps(result))
    return harness.returncode


if __name__ == '__main__':
    sys.exit(main())
