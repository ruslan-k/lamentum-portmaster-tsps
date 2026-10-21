#!/usr/bin/env python3
"""Read-only attribution of a live process's swapped pages, by mapping (roadmap G1).

The G1 arm measured 913 MB of VmSwap inside the game process without naming the owner.
This reads /proc/PID/smaps for every mapping that reports Swap: > 0, adds VmSwap to the
process-wide parse from smaps_rollup, and reports the gap, so an unattributed remainder is
visible instead of being silently dropped.

  python3 tools/swap_attribution.py --evidence evidence/swap-01 [--samples 6 --interval 10]
"""
import argparse
import json
import os
import pathlib
import subprocess
import sys
import time

from proc_metrics import sample_request

REPO = pathlib.Path(__file__).resolve().parents[1]
HOST = os.environ.get('LAMENTUM_DEVICE')

# One process only: the request carries the expected boot/PID/starttime generation.
PAYLOAD = r'''
import json, sys
from pathlib import Path
expected = json.loads(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1] else None
root = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('/proc')
runtime = Path(sys.argv[3]) if len(sys.argv) > 3 else Path('/mnt/SDCARD/Roms/PORTS/lamentum-switch/lamentum-nextos')
found = []
for entry in root.iterdir():
    if not entry.name.isdigit():
        continue
    try:
        if not __import__('os').path.samefile(entry / 'exe', runtime):
            continue
    except OSError:
        continue
    stat = (entry / 'stat').read_text()
    fields = stat[stat.rindex(')') + 2:].split()
    found.append({'pid': int(entry.name), 'starttime': int(fields[19])})
if len(found) != 1:
    print(json.dumps({'status': 'no_unique_process', 'found': found}))
    raise SystemExit(0)
pid = found[0]['pid']
if expected and (expected['pid'] != pid or expected['starttime'] != found[0]['starttime']):
    print(json.dumps({'status': 'identity_changed', 'found': found}))
    raise SystemExit(0)
boot_file = root.parent / 'sys/kernel/random/boot_id' if str(root) != '/proc' else Path('/proc/sys/kernel/random/boot_id')
boot = boot_file.read_text().strip()
if expected and expected.get('boot_id') and expected['boot_id'] != boot:
    print(json.dumps({'status': 'boot_changed', 'boot_id': boot}))
    raise SystemExit(0)
base = root / str(pid)
rollup = {}
for line in (base / 'smaps_rollup').read_text().splitlines():
    key, sep, rest = line.partition(':')
    # Only real counters: a stray mapping header must not masquerade as a rollup key.
    if sep and key and key.replace('_', '').isalnum() and rest.split():
        rollup[key] = rest.split()[0]
status = {}
for line in (base / 'status').read_text().splitlines():
    key, sep, rest = line.partition(':')
    if sep and key.replace('_', '').isalnum() and rest.split():
        status[key] = rest.split()[0]
mappings = []
header = None
record = None
def flush():
    if record is None:
        return
    swap = int(record.get('Swap', '0 kB').split()[0])
    if swap <= 0:
        return
    mappings.append({
        'header': header,
        'size_kb': int(record.get('Size', '0 kB').split()[0]),
        'swap_kb': swap,
        'rss_kb': int(record.get('Rss', '0 kB').split()[0]),
        'pss_kb': int(record.get('Pss', '0 kB').split()[0]),
        'referenced_kb': int(record.get('Referenced', '0 kB').split()[0]),
        'dirty_kb': int(record.get('Dirty', '0 kB').split()[0]),
        'vmflags': record.get('VmFlags', ''),
    })
for line in (base / 'smaps').read_text(errors='replace').splitlines():
    if line and line[0].isalnum() and ':' not in line.split()[0]:
        flush()
        header = line.strip()
        record = {}
        continue
    if ':' in line and record is not None:
        key, _, rest = line.partition(':')
        record[key.strip()] = rest.strip()
flush()
mappings.sort(key=lambda m: -m['swap_kb'])
total_swap = sum(m['swap_kb'] for m in mappings)
# VmSwap lives in status; smaps_rollup carries the same total under Swap.
process_swap = int(status.get('VmSwap', '0').split()[0])
rollup_swap = int(rollup.get('Swap', '0').split()[0])
gap = process_swap - total_swap
print(json.dumps({
    'status': 'ok', 'pid': pid, 'starttime': found[0]['starttime'], 'boot_id': boot,
    'rollup': rollup, 'rollup_swap_kb': rollup_swap,
    'process_swap_kb': process_swap, 'mapped_swap_kb': total_swap,
    'unattributed_swap_kb': gap,
    'rollup_minus_status_kb': rollup_swap - process_swap,
    'coverage_percent': round(100.0 * total_swap / process_swap, 2) if process_swap else None,
    'mapping_count': len(mappings), 'top': mappings[:12],
    'anonymous_swap_kb': sum(m['swap_kb'] for m in mappings if ' /' not in m['header']),
    'file_backed_swap_kb': sum(m['swap_kb'] for m in mappings if ' /' in m['header']),
    'largest_anonymous_swap_kb': max([m['swap_kb'] for m in mappings if ' /' not in m['header']] or [0]),
}))
'''


def ssh(command, timeout=90, data=None):
    if not HOST:
        raise RuntimeError('Set LAMENTUM_DEVICE to the SSH target before using the remote collector')
    result = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', HOST, command],
                            input=data, capture_output=True, timeout=timeout)
    result.check_returncode()
    return result


def remote(source):
    return json.loads(ssh('python3 -', data=source.encode()).stdout.decode().strip().splitlines()[-1])


def attribute(expected=None):
    args = ['probe', json.dumps(expected), '/proc',
            '/mnt/SDCARD/Roms/PORTS/lamentum-switch/lamentum-nextos']
    return remote('import sys\nsys.argv=%r\n' % (args,) + PAYLOAD)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=pathlib.Path, required=True)
    parser.add_argument('--samples', type=int, default=6)
    parser.add_argument('--interval', type=float, default=10.0)
    args = parser.parse_args(argv)
    if args.samples < 1 or args.interval <= 0:
        parser.error('samples must be >= 1 and interval > 0')
    out = args.evidence if args.evidence.is_absolute() else REPO / 'evidence' / args.evidence
    out.mkdir(parents=True, exist_ok=True)
    output = out / 'swap.jsonl'
    count = 0
    with output.open('w') as handle:
        for index in range(args.samples):
            record = {'n': index, 't': time.time()}
            try:
                record['attribution'] = attribute()
            except Exception as exc:                      # transport failure is not "no swap"
                record['error'] = repr(exc)
            handle.write(json.dumps(record) + '\n')
            handle.flush()
            count += 1
            if index + 1 < args.samples:
                time.sleep(args.interval)
    print(json.dumps({'samples': count, 'path': str(output), 'scope': 'read-only smaps attribution; not FPS'}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
