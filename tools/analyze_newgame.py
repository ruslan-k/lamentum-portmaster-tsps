#!/usr/bin/env python3
"""Numeric summary of a New-game probe run: frame progression, stop reason,
memory trend and whether consecutive physical captures actually change.

No text is inferred from pixels; a capture counts as "live" only when the
measured difference between it and the previous capture exceeds the noise
floor that the same rig shows on two captures of one static menu.
"""
import json
import pathlib
import sys

import numpy as np
from PIL import Image

NOISE_FLOOR = 8  # grayscale levels; above this a pixel counts as changed


def load(path):
    return np.asarray(Image.open(path).convert('L'), dtype=np.int16)


def compare(a, b):
    d = np.abs(a - b)
    return {'changed_pixels_gt%d' % NOISE_FLOOR: int((d > NOISE_FLOOR).sum()),
            'max_delta': int(d.max()),
            'mean_luminance': round(float(a.mean()), 3)}


def main(run_dir):
    run = pathlib.Path(run_dir)
    shots = sorted(run.glob('*.png'))
    rows = []
    prev = None
    for p in shots:
        img = load(p)
        row = {'capture': p.name, 'shape': list(img.shape),
               'mean_luminance': round(float(img.mean()), 3),
               'pixels_gt128': int((img > 128).sum())}
        if prev is not None and prev[0] == img.shape:
            row['vs_previous'] = compare(prev[1], img)
        rows.append(row)
        prev = (img.shape, img)
    memory = []
    if (run / 'memory.jsonl').exists():
        for line in (run / 'memory.jsonl').read_text().splitlines():
            memory.append(json.loads(line))
    stops = []
    log = run / 'latest.log'
    if log.exists():
        for line in log.read_text().splitlines():
            if 'STOP status=' in line:
                stops.append(line)
    flat = [m['sample'] for m in memory if 'MemAvailable' in m.get('sample', {})]
    summary = {'run': run.name, 'captures': rows, 'stop_lines': stops,
               'memory_samples': len(memory),
               'mem_available_mib': [round(s['MemAvailable'] / 1024) for s in flat],
               'runtime_rss_mib': [round(s.get('runtime_rss_kB', 0) / 1024) for s in flat]}
    print(json.dumps(summary, indent=2))
    (run / 'analysis.json').write_text(json.dumps(summary, indent=2) + '\n')


if __name__ == '__main__':
    main(sys.argv[1])
