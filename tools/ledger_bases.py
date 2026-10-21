"""Pair three storage bases from ONE owned run: declared payload, budget charge,
and the driver's gpu_memory counter.

Deliberate limits: declared/charged bytes are accounting figures, not measured
driver residency; gpu_memory's units are not verified against the driver source,
so no physical attribution is produced. A zero-argument reconciliation is not
evidence of memory being free.
"""
import argparse
import json
import re
from pathlib import Path


def _fields(line):
    return dict(re.findall(r'([A-Za-z0-9_-]+)=(\S+)', line))


def _owned(rows, run):
    """Keep only rows of the declared run and refuse a mixed or foreign series.

    An idle row (no pid) asserts nothing about ownership: it is outside the game
    window and must not be counted as either evidence or a mismatch.
    """
    key = ('run_uuid', 'pid', 'starttime', 'boot_id')
    seen = set()
    for row in rows:
        if row.get('pid') is None:
            continue
        if any(str(row.get(k)) != str(run[k]) for k in key):
            raise ValueError('foreign or mixed process identity in samples')
        seen.add(tuple(str(row.get(k)) for k in key))
    if not seen:
        raise ValueError('no samples')
    return rows


def reconcile(ledger_text, life_text, rows, run):
    rows = _owned(rows, run)
    game = [r for r in rows if r.get('game')]
    if not game:
        raise ValueError('no sample observed the game process')
    charge = [_fields(l) for l in ledger_text.splitlines() if l.startswith('LC2_MENU_LEDGER')]
    if not charge:
        raise ValueError('no menu-ledger line in this log')
    charge = charge[-1]
    life = [l for l in life_text.splitlines() if l.startswith('LC2_LIFE_SUMMARY')]
    if not life:
        raise ValueError('no life summary in this log')
    life = _fields(life[-1])
    declared_tex = int(life['tex-bytes'])
    declared_depth = int(life['rb-bytes'])
    charged_tex = int(charge['textures-charged-bytes'])
    charged_depth = int(charge['depth-estimate-bytes'])
    gpu = [r['gpu_memory'] for r in game if r.get('gpu_memory') is not None]
    if not gpu:
        raise ValueError('no gpu_memory reading during the game window')
    return {
        'declared': {'texture_bytes': declared_tex, 'depth_bytes': declared_depth,
                     'texture_mib': round(declared_tex / 2**20, 4),
                     'depth_mib': round(declared_depth / 2**20, 4),
                     'live_textures': int(life['tex-live']), 'live_depth': int(life['rb-live']),
                     'texture_over_charge': round(declared_tex / charged_tex, 4) if charged_tex else None},
        'charged': {'texture_bytes': charged_tex, 'depth_bytes': charged_depth,
                    'texture_mib': round(charged_tex / 2**20, 4),
                    'depth_mib': round(charged_depth / 2**20, 4),
                    'live_textures': int(charge['textures-live'])},
        'depth_agrees_exactly': declared_depth == charged_depth,
        'gpu_memory': {'min': min(gpu), 'max': max(gpu), 'samples': len(gpu),
                       'units_verified': False, 'scope': 'driver counter, unit not derived from source'},
        'physical_attribution': False,
        'notes': ['declared payload counts every requested texture level',
                  'budget charge is an accounting policy figure',
                  'gpu_memory may include alignment, tiling, aliases and non-texture storage'],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--log', type=Path, required=True)
    p.add_argument('--samples', type=Path, required=True)
    p.add_argument('--harness', type=Path, required=True, help='harness.json of the same arm')
    a = p.parse_args()
    harness = json.loads(a.harness.read_text())
    expected = harness['expected_run']
    identity = harness['process_identity']
    run = {'run_uuid': expected['run_uuid'], 'boot_id': expected['boot_id'],
           'pid': identity['pid'], 'starttime': identity['starttime']}
    text = a.log.read_text(errors='replace')
    print(json.dumps(reconcile(text, text, json.loads(a.samples.read_text()), run), indent=2))


if __name__ == '__main__':
    main()
