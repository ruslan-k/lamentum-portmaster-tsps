"""Offline census of the existing generic sampler-bind diagnostic.

This is NOT a complete reader/lifetime ledger or an FPS benchmark. Binding is not
proof of issued draw, fence completion or exclusive GL storage ownership.
"""
import argparse
import json
from pathlib import Path


def census(data, watched=()):
    records = data.split(b'\n')
    incomplete = bool(records[-1])
    records = records[:-1]  # Only newline-complete records qualify.
    observed, targets, frames = {}, set(), []
    count = 0
    for offset, raw in enumerate(records, 1):
        if not raw.startswith(b'T2_DRAW_TEXTURE '):
            continue
        try:
            pairs = [token.split('=', 1) for token in raw.decode('ascii').split()[1:]]
            row = dict(pairs)
            if len(row) != len(pairs):
                raise ValueError('duplicate key')
            values = {k: int(row[k]) for k in ('frame', 'draw', 'unit', 'id', 'target')}
            if any(v < 0 for v in values.values()):
                raise ValueError('negative field')
            frame, owner = values['frame'], str(values['id'])
            if frames and frame < frames[-1]:
                raise ValueError('frame regression')
            dims = row['size'].split('x')
            if len(dims) != 2 or any(int(v) <= 0 for v in dims):
                raise ValueError('invalid dimensions')
            pair = row['pair'].split('/')
            if len(pair) != 2 or any(int(v) < 0 for v in pair):
                raise ValueError('invalid pair')
            int(row['format'], 16)
        except (KeyError, ValueError, UnicodeError) as exc:
            raise ValueError('invalid sampler event at line %d: %s' % (offset, exc)) from exc
        entry = observed.setdefault(owner, dict(bindings=0, frames=set(), pairs=set(), sizes=set(), targets=set()))
        entry['bindings'] += 1
        for key, value in [('frames', frame), ('pairs', row['pair']), ('sizes', row['size']), ('targets', values['target'])]:
            entry[key].add(value)
        targets.add(values['target'])
        frames.append(frame)
        count += 1
    for entry in observed.values():
        for key in ('frames', 'pairs', 'sizes', 'targets'):
            entry[key] = sorted(entry[key])
    return dict(events=count, first_frame=frames[0] if frames else None,
                last_frame=frames[-1] if frames else None,
                observed=observed, target_ids=sorted(targets),
                watched={str(k): observed.get(str(k), dict(bindings=0, frames=[])) for k in watched},
                incomplete_tail=incomplete, absence_proves_unused=False,
                physical_refund_bytes=None, fence_completion='unobserved',
                scope='generic sampler preparation; alternate paths, aliases, issued draw and finalization not covered')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('log', type=Path)
    p.add_argument('--watch', type=int, nargs='*', default=[81, 92])
    a = p.parse_args()
    print(json.dumps(census(a.log.read_bytes(), a.watch), indent=2))


if __name__ == '__main__':
    main()
