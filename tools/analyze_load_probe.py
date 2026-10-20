#!/usr/bin/env python3
"""Summarize a load_probe sample series: memory trend vs asset counters and frame progress.

Only reported numbers are derived here; a metric the probe did not sample stays None.
"""
import argparse
import json
from pathlib import Path

from analyze_guest_samples import analyze

KEYS = ('romfs', 'textures', 'bc_deferred', 'bc_fileback', 'presents')


def summarize(rows):
    good = [r for r in rows if 'mem' in r]
    out = {'samples': len(rows), 'usable': len(good), 'errors': len(rows) - len(good)}
    if not good:
        return out
    first, last = good[0], good[-1]
    out['first'] = {k: first['mem'].get(k) for k in ('MemTotal', 'MemAvailable', 'SwapFree', 'CmaFree')}
    out['last'] = {k: last['mem'].get(k) for k in ('MemTotal', 'MemAvailable', 'SwapFree', 'CmaFree')}
    out['span_s'] = round(last['t'] - first['t'], 1)
    out['min_available_kb'] = min(r['mem'].get('MemAvailable', 1 << 40) for r in good)
    out['counter_delta'] = {}
    for key in KEYS:
        values = [r[key] for r in good if isinstance(r.get(key), int)]
        out['counter_delta'][key] = (values[-1] - values[0]) if values else None
    out['frames'] = {'first': first.get('frame'), 'last': last.get('frame')}
    timeline = [(r['t'], r['mem'].get('MemAvailable')) for r in good]
    out['timeline_minutes'] = [{'t': t, 'available_mb': round(v / 1024)} for t, v in timeline[::max(1, len(timeline) // 12)]]
    out['stops'] = sorted({s for r in good for s in r.get('stops', [])})
    out['killed'] = any(r.get('killed') for r in good)
    out['entry45_links'] = max((r.get('entry45') or 0) for r in good)
    out['unknown_shader_requests'] = max((r.get('unknown') or 0) for r in good)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('evidence', type=Path)
    ap.add_argument('--json', type=Path)
    a = ap.parse_args()
    rows = [json.loads(l) for l in (a.evidence / 'samples.jsonl').read_text().splitlines() if l.strip()]
    result = summarize(rows)
    log = a.evidence / 'latest.log'
    if log.exists():
        result['guest_samples'] = analyze(log.read_text(errors='replace'))
    if a.json:
        a.json.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
