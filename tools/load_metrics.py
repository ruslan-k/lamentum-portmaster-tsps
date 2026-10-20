#!/usr/bin/env python3
"""Run-scoped, incremental log metrics for the device probes (roadmap §25.4 T0).

The previous collector pasted a regex-heavy Python payload into an f-string, so escaping was
unverifiable until it ran on the device, and it re-read a multi-MiB log every five seconds.
This module keeps the payload as a plain source string, parses a log LOCALLY in tests, and
supports offset-based incremental reads so the device only sends new bytes plus running totals.
"""
import json
import re

PAYLOAD = r'''
import json, os, re, sys
from pathlib import Path
offset = int(sys.argv[1]) if len(sys.argv) > 1 else 0
if offset < 0:
    raise ValueError('negative log offset')
expected_identity = json.loads(sys.argv[2]) if len(sys.argv) > 2 else None
path = Path('/mnt/SDCARD/Roms/PORTS/lamentum-switch/logs/latest.log')
# fstat the opened file, not the pathname: rename during a poll must not mix identities.
with path.open('rb') as handle:
    stat = os.fstat(handle.fileno())
    identity = [stat.st_dev, stat.st_ino]
    size = stat.st_size
    rotated = offset > size or (expected_identity is not None and expected_identity != identity)
    if rotated:
        offset = 0
    handle.seek(offset)
    raw = handle.read(max(0, size - offset))
# Consume complete records in BYTES. Replacement decoding changes encoded lengths and a
# partial event must not be counted until its newline arrives on a subsequent poll.
complete_bytes = raw.rfind(b'\n') + 1
chunk = raw[:complete_bytes].decode('utf-8', 'replace')
consumed = offset + complete_bytes
mem = {}
for line in Path('/proc/meminfo').read_text().splitlines():
    key = line.split(':')[0]
    if key in ('MemTotal', 'MemFree', 'MemAvailable', 'SwapFree', 'CmaFree'):
        mem[key] = int(line.split()[1])
counters = {
    'presents': len(re.findall(r'NVN_PRESENT_PIXELS frame=\d+', chunk)),
    'romfs': chunk.count('ROMFS_READ'),
    'textures': chunk.count('NVN_TEXTURE_REAL'),
    'bc_deferred': chunk.count('LC2_BC_DEFERRED'),
    'bc_fileback': chunk.count('LC2_BC_FILEBACK'),
    'budget_adds': len(re.findall(r'T2_TEXTURE_BUDGET add-bytes=\d+', chunk)),
}
frames = re.findall(r'NVN_PRESENT_PIXELS frame=(\d+)', chunk)
stops = re.findall(r'STOP status=(\S+)', chunk)
budget = re.findall(r'T2_TEXTURE_BUDGET add-bytes=\d+ live-MiB=\d+ count=\d+ budget-MiB=\d+', chunk)
killed = 'Killed' in chunk
print(json.dumps({'offset': consumed, 'size': size, 'identity': identity, 'rotated': rotated, 'mem': mem,
                  'counters': counters, 'frame': int(frames[-1]) if frames else None,
                  'stops': stops[-3:], 'budget_last': budget[-1] if budget else None,
                  'killed': killed}))
'''

CUMULATIVE = ('presents', 'romfs', 'textures', 'bc_deferred', 'bc_fileback', 'budget_adds')


def fold(previous, sample):
    """Add a new chunk's counters to the previous running totals (rotation resets them)."""
    identity_changed = (previous and previous.get('identity') is not None
                        and sample.get('identity') is not None
                        and previous['identity'] != sample['identity'])
    base = {} if sample['rotated'] or identity_changed else dict(previous or {})
    for key in CUMULATIVE:
        base[key] = base.get(key, 0) + sample['counters'].get(key, 0)
    base['frame'] = sample['frame'] if sample['frame'] is not None else base.get('frame')
    base['stops'] = (base.get('stops', []) + sample['stops'])[-3:]
    if sample.get('budget_last'):
        base['budget_last'] = sample['budget_last']
    base['killed'] = base.get('killed', False) or sample['killed']
    base['mem'] = sample['mem']
    base['offset'] = sample['offset']
    base['size'] = sample['size']
    base['identity'] = sample.get('identity')
    return base


def collector_request(previous):
    """Pass the byte cursor and opened-file identity together to the real remote payload."""
    previous = previous or {}
    args = ['probe', str(previous.get('offset', 0)), json.dumps(previous.get('identity'))]
    return 'import sys\nsys.argv=%r\n' % args + PAYLOAD


def parse_chunk(chunk):
    """Local mirror of the payload's parsing, used by tests against synthetic logs."""
    counters = {
        'presents': len(re.findall(r'NVN_PRESENT_PIXELS frame=\d+', chunk)),
        'romfs': chunk.count('ROMFS_READ'),
        'textures': chunk.count('NVN_TEXTURE_REAL'),
        'bc_deferred': chunk.count('LC2_BC_DEFERRED'),
        'bc_fileback': chunk.count('LC2_BC_FILEBACK'),
        'budget_adds': len(re.findall(r'T2_TEXTURE_BUDGET add-bytes=\d+', chunk)),
    }
    frames = re.findall(r'NVN_PRESENT_PIXELS frame=(\d+)', chunk)
    stops = re.findall(r'STOP status=(\S+)', chunk)
    budget = re.findall(r'T2_TEXTURE_BUDGET add-bytes=\d+ live-MiB=\d+ count=\d+ budget-MiB=\d+', chunk)
    return {'counters': counters, 'frame': int(frames[-1]) if frames else None,
            'stops': stops[-3:], 'budget_last': budget[-1] if budget else None,
            'killed': 'Killed' in chunk}


if __name__ == '__main__':
    import sys
    print(json.dumps(parse_chunk(open(sys.argv[1], errors='replace').read()), indent=2))
