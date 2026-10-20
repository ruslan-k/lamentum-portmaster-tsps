#!/usr/bin/env python3
"""Compare VS12's exact matrix sequence against captured UBO0/UBO1.

Read-only numerical replay of real MOMO diagnostics. First four captured
positions only; no claim about the complete indexed draw or visible pixels.
"""
import argparse
import json
import re
import struct
from pathlib import Path


def f32(x):
    return struct.unpack('<f', struct.pack('<f', x))[0]


def madd(a, b, c):
    # The Mali catalogue lowers fma(a,b,c) to ((a)*(b)+(c)).
    return f32(f32(a*b)+c)


def transform(position, bank):
    c = [f32(x) for x in bank] + [0.0] * max(0, 40-len(bank))
    x, y, z = map(f32, position[:3])
    world = [f32(madd(z,c[8+i],madd(x,c[i],f32(y*c[4+i])))+c[12+i]) for i in range(4)]
    a, b, d, w = world
    clip = [madd(w,c[28+i],madd(d,c[24+i],madd(a,c[16+i],f32(b*c[20+i])))) for i in range(4)]
    return {'clip': clip, 'ndc': [v/clip[3] for v in clip[:3]] if clip[3] else None,
            'inside_xy': clip[3] > 0 and abs(clip[0]) <= clip[3] and abs(clip[1]) <= clip[3]}


def analyze(log):
    lines = log.read_text().splitlines()
    starts = [i for i,l in enumerate(lines) if 'NVN_DRAW_DIAGNOSTIC_FRAME frame=300' in l]
    out = []
    for start in starts:
        if 'sources=12/14' not in lines[start]:
            continue
        stop = next((i for i in range(start+1,len(lines)) if 'NVN_DRAW_DIAGNOSTIC_FRAME' in lines[i]),len(lines))
        block = lines[start:stop]
        banks = {}
        for line in block:
            match = re.search(r'MOMO_UNIFORM_RANGE .*stage=0 binding=(\d+).*size=(\d+) \|',line)
            if match:
                values = line.split(' |',1)[1].split(' ||',1)[0].replace('|',' ').split()
                banks[int(match[1])] = [float(x) for x in values][:int(match[2])//4]
        attr = next((l for l in block if l.startswith('NVN_DRAW_ATTR index=0 ')),None)
        if not attr or 0 not in banks or 1 not in banks:
            continue
        vertices = [[float(x) for x in s.split()] for s in re.findall(r'\[([^]]+)\]',attr)]
        draw_match = re.search(r'draw=(\d+)',lines[start])
        if draw_match is None:
            raise ValueError('missing draw identity')
        row = {'draw': int(draw_match[1]), 'positions': vertices,
               'banks': {str(k):v for k,v in banks.items()}, 'replay': {}}
        for bank in [0,1]:
            row['replay'][str(bank)] = {'vertices':[transform(v,banks[bank]) for v in vertices],
                                     'vertex_color_multiplier': banks[bank][32:36]}
        out.append(row)
    if len(out)!=6:
        raise ValueError('expected six real UI draw diagnostics at frame300')
    return {'source_log':str(log), 'source':'captured values, not generated game state',
            'limitations':'First four captured vertices per draw, float32 non-fused lowering; no pixel proof.', 'draws':out}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log',type=Path)
    print(json.dumps(analyze(parser.parse_args().log),indent=2))
