#!/usr/bin/env python3
"""Numerical comparison of real DRM input-probe captures; no menu inference."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image


def analyze(directory):
    reference = np.asarray(Image.open(directory / 'at-title.png').convert('L'), dtype=np.int16)
    rows = []
    for path in [directory / 'at-title.png', *sorted(directory.glob('after-*.png'))]:
        current = np.asarray(Image.open(path).convert('L'), dtype=np.int16)
        if current.shape != reference.shape:
            raise ValueError('capture dimensions differ')
        delta = np.abs(current - reference)
        ys, xs = np.where(delta > 10)
        rows.append({'capture': path.name, 'mean_luminance': float(current.mean()),
                     'band_300_600_mean': float(current[300:600].mean()),
                     'changed_pixels_gt10': int((delta > 10).sum()),
                     'max_delta': int(delta.max()),
                     'changed_bbox_xyxy': [int(xs.min()), int(ys.min()), int(xs.max()) + 1,
                                           int(ys.max()) + 1] if xs.size else None})
    return {'reference': 'at-title.png', 'comparison': 'PIL grayscale, absolute luminance delta',
            'note': 'Metrics do not identify text, menu ownership, or gameplay.', 'captures': rows}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('directory', type=Path)
    print(json.dumps(analyze(ap.parse_args().directory), indent=2))
