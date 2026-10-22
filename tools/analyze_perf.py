#!/usr/bin/env python3
"""Distributions of the runtime's own T2P_SLOW_FRAME records.

Implements the parser the 30 FPS roadmap asks for (docs/performance-roadmap-30fps.md §3):
P50/P90/P95/P99/max per field, unattributed time, early vs steady-state phases, and gaps.
No FPS claim is made from a run that still includes loading; every window is reported
with its frame range so two runs can be compared like-for-like.

  python3 tools/analyze_perf.py <latest.log> [--from-frame N] [--to-frame M] [--json out.json]
"""
import argparse
import json
import pathlib
import re
import statistics
import sys

FIELD_RE = re.compile(r'([a-z-]+)=([0-9.]+)')
STOP_RE = re.compile(r'^STOP status=([A-Z_0-9]+)', re.MULTILINE)


def parse(path):
    frames = []
    for line in pathlib.Path(path).read_text(errors='replace').splitlines():
        if not line.startswith('T2P_SLOW_FRAME'):
            continue
        row = {k: float(v) for k, v in FIELD_RE.findall(line)}
        if 'frame' in row:
            row['frame'] = int(row['frame'])
            frames.append(row)
    frames.sort(key=lambda r: r['frame'])
    stops = STOP_RE.findall(pathlib.Path(path).read_text(errors='replace'))
    return frames, stops


def dist(values):
    if not values:
        return None
    values = sorted(values)
    def pct(p):
        k = min(len(values) - 1, max(0, int(round(p / 100.0 * (len(values) - 1)))))
        return round(values[k], 2)
    return {'n': len(values), 'p50': pct(50), 'p90': pct(90), 'p95': pct(95),
            'p99': pct(99), 'max': round(values[-1], 2),
            'mean': round(statistics.fmean(values), 2)}


def window(frames, lo=None, hi=None):
    sel = [f for f in frames
           if (lo is None or f['frame'] >= lo) and (hi is None or f['frame'] <= hi)]
    if not sel:
        return None
    out = {'frames': [sel[0]['frame'], sel[-1]['frame']], 'records': len(sel)}
    for field in ('period-ms', 'replay-ms', 'finish-ms', 'present-ms', 'swap-ms', 'readback-ms'):
        out[field] = dist([r[field] for r in sel if field in r])
    # Unattributed = period - the measured stages. Reported per frame, never summed medians.
    unattributed = []
    for r in sel:
        if 'period-ms' not in r:
            continue
        spent = sum(r.get(k, 0.0) for k in ('replay-ms', 'finish-ms', 'present-ms', 'swap-ms', 'readback-ms'))
        unattributed.append(max(0.0, r['period-ms'] - spent))
    out['unattributed-ms'] = dist(unattributed)
    gaps = [b['period-ms'] for b in sel if b['period-ms'] > 250]
    out['period_over_250ms'] = {'count': len(gaps),
                               'share_of_window': round(len(gaps) / len(sel), 3)}
    # Steady-state view: exclude the warm-up by starting where period first drops under 1 s.
    warm = next((i for i, r in enumerate(sel) if r.get('period-ms', 1e9) < 1000), None)
    out['warmup_records'] = warm if warm is not None else None
    if warm is not None and len(sel) - warm >= 30:
        tail = sel[warm:]
        out['after_warmup'] = {'frames': [tail[0]['frame'], tail[-1]['frame']],
                               'period-ms': dist([r['period-ms'] for r in tail]),
                               'replay-ms': dist([r['replay-ms'] for r in tail
                                                  if 'replay-ms' in r])}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('log', type=pathlib.Path)
    ap.add_argument('--from-frame', type=int, default=None)
    ap.add_argument('--to-frame', type=int, default=None)
    ap.add_argument('--json', type=pathlib.Path, default=None)
    a = ap.parse_args()
    frames, stops = parse(a.log)
    result = {'log': str(a.log), 'records': len(frames), 'stop_status': stops[-1] if stops else None,
              'whole_run': window(frames),
              'requested_window': window(frames, a.from_frame, a.to_frame)}
    if frames:
        result['frame_range'] = [frames[0]['frame'], frames[-1]['frame']]
        late = [r for r in frames if r['frame'] >= 500]
        if late:
            result['frames_500_plus'] = window(frames, 500, None)
    text = json.dumps(result, indent=2)
    print(text)
    if a.json:
        a.json.write_text(text + '\n')


if __name__ == '__main__':
    main()
