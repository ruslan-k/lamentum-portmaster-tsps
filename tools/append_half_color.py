#!/usr/bin/env python3
"""Append pinned 5ff482d4 fragment: two 2D samplers and explicit scalar f16 casts."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import tempfile
from append_program import append
from build_lamentum_catalogue import cbuf_blocks_of, samplers_of
from half_float_lowering import lower_scalar_half_casts, HALF_ROUND_MACRO

CODE_SHA = '5ff482d48c9426db3f69965a3a6f96a3fe2e994f309135ddf71cda1a5f184c8a'
CONTROL_SHA = 'ccd3fcacba180042a8fe9c991e7044157958aa0b54fa582d4f8bc2eb1200ab00'


def prepare(source, code, control):
    if hashlib.sha256(code).hexdigest() != CODE_SHA or hashlib.sha256(control).hexdigest() != CONTROL_SHA:
        raise ValueError('not the pinned fragment')
    if cbuf_blocks_of(source):
        raise ValueError('unexpected cbuf')
    samplers = samplers_of(source)
    if [(s['name'], s['binding'], s['offset']) for s in samplers] != [('fs_tex0_20', 14, 0), ('fs_tex0_28', 14, 8)]:
        raise ValueError('sampler provenance changed')
    s = lower_scalar_half_casts(source)
    s = s.replace('#version 450', '#version 450\n' + HALF_ROUND_MACRO, 1)
    return s, samplers


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('workspace', type=Path)
    ap.add_argument('catalogue', type=Path)
    ap.add_argument('output', type=Path)
    ap.add_argument('--report', type=Path, required=True)
    a = ap.parse_args()
    code = (a.workspace / 'missing.code.bin').read_bytes()
    control = (a.workspace / 'missing.control.bin').read_bytes()
    source, samplers = prepare((a.workspace / 'original-vulkan.glsl').read_text(), code, control)
    ir = (a.workspace / 'original.spv').read_bytes()
    words = struct.unpack('<%dI' % (len(ir) // 4), ir); i = 5; stages = []
    while i < len(words):
        n, op = words[i] >> 16, words[i] & 65535
        if not n or i + n > len(words):
            raise ValueError('bad IR')
        if op == 15: stages.append(words[i + 1])
        i += n
    if stages != [4]: raise ValueError('not fragment execution model')
    old = a.catalogue.read_text()
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)
        (p / 'half-color.glsl').write_text(source)
        (p / 'half-color.code.bin').write_bytes(code)
        (p / 'half-color.control.bin').write_bytes(control)
        text, index, literals = append(old, 'half-color', p)
    if literals: raise ValueError('unexpected literal specialization')
    # Only this new source uses highp outside its explicit f16 conversion points.
    marker = '/* %d half-color fragment */' % index
    start = text.index(marker); end = text.index('};\n', start)
    part = text[start:end].replace('precision mediump float;', 'precision highp float;')
    text = text[:start] + part + text[end:]
    start = text.rindex(marker)
    text = text[:start] + text[start:].replace('.requires_fragment_highp=0,.requires_fragment_mediump=1',
                                              '.requires_fragment_highp=1,.requires_fragment_mediump=0', 1)
    a.output.write_text(text)
    a.report.write_text(json.dumps({'index': index, 'code_sha256': CODE_SHA, 'control_sha256': CONTROL_SHA,
                                    'samplers': samplers, 'cbufs': [], 'half_rounding': HALF_ROUND_MACRO,
                                    'execution_model': 'fragment', 'non_half_arithmetic': 'highp float'}, indent=2) + '\n')
    print('appended fragment', index)


if __name__ == '__main__':
    main()
