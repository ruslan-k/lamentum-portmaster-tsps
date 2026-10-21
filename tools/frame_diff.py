"""Pixel comparison for a storage A/B (no game data, no device).

A resolution change is only acceptable with identical output, so the A/B needs a
measurable "identical": this compares two decoded frames and reports how many
pixels differ beyond a tolerance, plus the worst channel delta and a coarse
per-band summary that catches "only the text moved" versus "the whole picture
shifted".
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def compare(first, second, width, height, channels=3, tolerance=2, bands=8):
    """Compare two raw frames of the same geometry.

    Returns a dict with the differing-pixel ratio, the maximum channel delta, the
    mean absolute delta and a per-horizontal-band ratio. Refuses geometry or size
    mismatches instead of comparing a prefix of two different images.
    """
    if width <= 0 or height <= 0:
        return {'comparable': False, 'reason': 'invalid geometry'}
    expected = width * height * channels
    if len(first) != expected or len(second) != expected:
        return {'comparable': False,
                'reason': 'frame size mismatch: %d and %d against %d expected'
                          % (len(first), len(second), expected)}
    differing, total, worst, sum_delta = 0, 0, 0, 0
    band_pixels = [0] * bands
    band_differing = [0] * bands
    limit = height // bands or 1
    for pixel in range(width * height):
        base = pixel * channels
        delta = 0
        for channel in range(channels):
            value = abs(first[base + channel] - second[base + channel])
            if value > delta:
                delta = value
        y = pixel // width
        band = min(bands - 1, y // limit)
        band_pixels[band] += 1
        total += 1
        sum_delta += delta
        if delta > worst:
            worst = delta
        if delta > tolerance:
            differing += 1
            band_differing[band] += 1
    return {'comparable': True, 'pixels': total, 'differing': differing,
            'ratio': round(differing / total, 6), 'max_delta': worst,
            'mean_delta': round(sum_delta / total, 4), 'tolerance': tolerance,
            'bands': [round(band_differing[i] / band_pixels[i], 6) if band_pixels[i] else 0.0
                      for i in range(bands)],
            'identical': differing == 0}


def identical(verdict):
    """An A/B passes only when the comparison ran and nothing differed."""
    return bool(verdict.get('comparable')) and verdict.get('identical') is True
