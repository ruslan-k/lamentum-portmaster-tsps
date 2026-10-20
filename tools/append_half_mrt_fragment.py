#!/usr/bin/env python3
"""Append the pinned bb10c5c3 MRT fragment with half-accurate products."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import tempfile

from append_program import append
from build_lamentum_catalogue import samplers_of
from half_mrt_lowering import lower_half_mrt

CODE_SHA = 'bb10c5c308ac2a145198a848f7a13ac9c2d510c02d208695c0dc5511adcf1c07'
CONTROL_SHA = 'c28023ec007cc676bf9f5ad08db0a67053e04109679222c16f703f235fdaf540'
SOURCE_SHA = '330094f224f266efe3fdf19a06c560b2da36e7ebcbe22161175d13049a87c945'
FRAGMENT = 4


def verify_ir(data):
    if len(data) < 20 or len(data) % 4:
        raise ValueError('truncated or unaligned IR')
    words = struct.unpack('<%dI' % (len(data) // 4), data)
    if words[0] != 0x07230203:
        raise ValueError('not SPIR-V')
    models, i = [], 5
    while i < len(words):
        n, op = words[i] >> 16, words[i] & 65535
        if not n or i + n > len(words):
            raise ValueError('invalid IR instruction')
        if op == 15:
            models.append(words[i + 1])
        i += n
    if models != [FRAGMENT]:
        raise ValueError('not the pinned fragment execution model')


def prepare(source, code, control, ir):
    if hashlib.sha256(code).hexdigest() != CODE_SHA or hashlib.sha256(control).hexdigest() != CONTROL_SHA:
        raise ValueError('wrong shader code/control')
    verify_ir(ir)
    samplers = samplers_of(source)
    if [(s['name'], s['binding'], s['offset']) for s in samplers] != [('fs_tex0_20', 14, 0)]:
        raise ValueError('sampler provenance changed')
    return lower_half_mrt(source, SOURCE_SHA), samplers


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('workspace', type=Path)
    ap.add_argument('catalogue', type=Path)
    ap.add_argument('output', type=Path)
    ap.add_argument('--report', type=Path, required=True)
    a = ap.parse_args()
    code = (a.workspace / 'missing.code.bin').read_bytes()
    control = (a.workspace / 'missing.control.bin').read_bytes()
    source, samplers = prepare((a.workspace / 'original-vulkan.glsl').read_text(), code, control,
                               (a.workspace / 'original.spv').read_bytes())
    with tempfile.TemporaryDirectory() as td:
        w = Path(td)
        (w / 'half-mrt.code.bin').write_bytes(code)
        (w / 'half-mrt.control.bin').write_bytes(control)
        (w / 'half-mrt.glsl').write_text(source)
        text, index, literals = append(a.catalogue.read_text(), 'half-mrt', w)
    if literals:
        raise ValueError('unexpected literal specialization')
    a.output.write_text(text)
    a.report.write_text(json.dumps({'index': index, 'code_sha256': CODE_SHA, 'control_sha256': CONTROL_SHA,
                                    'source_sha256_before': SOURCE_SHA,
                                    'source_sha256_after': hashlib.sha256(source.encode()).hexdigest(),
                                    'samplers': samplers, 'cbufs': [], 'outputs': 4,
                                    'half_rounding': 'every original f16 product is wrapped in lc2_half',
                                    'execution_model': 'fragment'}, indent=2) + '\n')
    print('appended fragment', index)


if __name__ == '__main__':
    main()
