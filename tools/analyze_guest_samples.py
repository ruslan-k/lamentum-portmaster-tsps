#!/usr/bin/env python3
"""Bucket MOMO_SAMPLE guest-frame samples into PCs and caller frames.

Reads the runtime log and reports, for the sampled window only, how often each
interrupted guest PC appears and which guest frames appear in the reported
chains. It never attributes a cost to a symbol it did not observe: an
unresolved location stays as its raw `<seg>+0x<off>` string.
"""
import argparse
import collections
import json
import re
from pathlib import Path

LOC = re.compile(r'\b([a-z0-9_.]+\.seg(?:\+0x[0-9a-f]+)?|0x[0-9a-f]+)\b')


def analyze(text):
    samples = [l for l in text.splitlines() if l.startswith('MOMO_SAMPLE')]
    pcs = collections.Counter()
    chains = collections.Counter()
    in_kernel = 0
    threads = collections.Counter()
    for line in samples:
        m = re.search(r'pc=(\S+)', line)
        if m:
            pcs[m[1]] += 1
        m = re.search(r'thread=(\S+)', line)
        if m:
            threads[m[1]] += 1
        m = re.search(r'in-kernel=(\S+)', line)
        if m and m[1] not in ('0x0', '0'):
            in_kernel += 1
        for loc in LOC.findall(line.split('pc=', 1)[-1]):
            chains[loc] += 1
    total = len(samples)
    return {'samples': total, 'in_kernel': in_kernel,
            'threads': dict(threads.most_common()),
            'top_pc': [{'pc': k, 'n': v, 'share': round(v / total, 4)} for k, v in pcs.most_common(15)] if total else [],
            'top_frames': [{'location': k, 'n': v} for k, v in chains.most_common(20)]}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('log', type=Path)
    ap.add_argument('--json', type=Path)
    a = ap.parse_args()
    result = analyze(a.log.read_text(errors='replace'))
    if a.json:
        a.json.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
