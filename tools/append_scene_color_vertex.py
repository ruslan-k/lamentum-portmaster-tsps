#!/usr/bin/env python3
"""Append only pinned 801b91ae vertex; captured c1 + read-only c3_1 -> UBO0."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
from append_literal_vertex import verify_ir
from append_program import append
from build_lamentum_catalogue import cbuf_blocks_of, rewrite_cbuf_blocks, samplers_of
from shader_literals import inline_literal_cbuf
from float_cbuf_contract import inspect, without_scalar_extension

CODE_SHA = '801b91aed1fb1660a5c1ae9413994c0113547d596e4be5ef5143582addc325d0'
CONTROL_SHA = 'ada676aaf675d0510aa7fea908d1473518596087a1a9dadf5a0cc43235eee820'


def prepare(source, code, control, ir):
    if hashlib.sha256(code).hexdigest() != CODE_SHA or hashlib.sha256(control).hexdigest() != CONTROL_SHA:
        raise ValueError('wrong shader code/control')
    banks = verify_ir(ir)
    blocks = cbuf_blocks_of(source)
    if len(blocks) != 2 or {b['instance'] for b in blocks} != {'c1', 'c3_1'} or samplers_of(source):
        raise ValueError('unexpected vertex resources')
    source = rewrite_cbuf_blocks(source, [b for b in blocks if b['instance'] == 'c1'])
    source, removed = inline_literal_cbuf(source, {'c1'}, code, control)
    if removed != {'c1'}:
        raise ValueError('literal bank not completely specialized')
    report = inspect(source, {'c3_1': 3})
    if len(report) != 1 or report[0]['required_bytes'] != 368 or report[0]['loads'] != 82:
        raise ValueError('access contract changed')
    source = without_scalar_extension(source, {'c3_1': 3})
    aliases = {'c3_1': {'hardware_bank': 3, 'code_sha256': CODE_SHA, 'control_sha256': CONTROL_SHA}}
    return source, aliases, {'banks': banks, 'blocks': report, 'literal_banks_inlined': ['c1'],
                             'source_sha256': hashlib.sha256(source.encode()).hexdigest()}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('workspace', type=Path)
    ap.add_argument('catalogue', type=Path)
    ap.add_argument('output', type=Path)
    ap.add_argument('--report', type=Path, required=True)
    a = ap.parse_args()
    code = (a.workspace / 'missing.code.bin').read_bytes()
    control = (a.workspace / 'missing.control.bin').read_bytes()
    source, aliases, report = prepare((a.workspace / 'original-vulkan.glsl').read_text(), code, control,
                                     (a.workspace / 'original.spv').read_bytes())
    with tempfile.TemporaryDirectory() as td:
        w = Path(td)
        for suffix, data in [('code.bin', code), ('control.bin', control)]:
            (w / ('scene-color-vertex.' + suffix)).write_bytes(data)
        (w / 'scene-color-vertex.glsl').write_text(source)
        text, index, literals = append(a.catalogue.read_text(), 'scene-color-vertex', w, aliases)
    if literals:
        raise ValueError('unexpected second literal specialization')
    a.output.write_text('#define LC2_SCENE_COLOR_VERTEX_INDEX %d\n' % index + text)
    report.update(index=index, code_sha256=CODE_SHA, control_sha256=CONTROL_SHA, aliases=aliases)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
