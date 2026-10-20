#!/usr/bin/env python3
"""Append pinned 301af8ce vertex with captured literal c1 and proven c3_1 alias.

The SPIR-V variable is named c3; SPIRV-Cross adds _1 because the GLSL block
itself is also called c3. Never interpret that suffix as an NVN slot.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import tempfile
from append_program import append
from build_lamentum_catalogue import cbuf_blocks_of, rewrite_cbuf_blocks
from shader_literals import inline_literal_cbuf
from float_cbuf_contract import inspect, without_scalar_extension

CODE_SHA = '301af8ced90e7e506eb4d5ace0dfabd65453557bac79a74dfebacef7396b3098'
CONTROL_SHA = '1307789791808c82c0b5c7a141f34ef4780a3ec430630b1588b0803e4ffba4fe'


def verify_ir(data):
    if len(data) < 20 or len(data) % 4:
        raise ValueError('truncated or unaligned IR')
    words = struct.unpack('<%dI' % (len(data) // 4), data)
    if words[0] != 0x07230203:
        raise ValueError('not SPIR-V')
    names, variables, models = {}, {}, []
    i = 5
    while i < len(words):
        n, op = words[i] >> 16, words[i] & 65535
        if not n or i + n > len(words):
            raise ValueError('invalid IR instruction')
        a = words[i + 1:i + n]
        if op == 5:
            names[a[0]] = struct.pack('<%dI' % len(a[1:]), *a[1:]).split(b'\0')[0].decode()
        elif op == 59:
            variables[a[1]] = a[2]
        elif op == 15:
            models.append(a[0])
        i += n
    banks = {names[k]: k for k, storage in variables.items() if storage == 2 and names.get(k) in ('c1', 'c3')}
    if models != [0] or set(banks) != {'c1', 'c3'}:
        raise ValueError('unexpected entry model or bank provenance')
    return banks


def prepare(source, code, control, ir):
    if hashlib.sha256(code).hexdigest() != CODE_SHA or hashlib.sha256(control).hexdigest() != CONTROL_SHA:
        raise ValueError('wrong shader code/control')
    banks = verify_ir(ir)
    blocks = cbuf_blocks_of(source)
    if {b['instance'] for b in blocks} != {'c1', 'c3_1'}:
        raise ValueError('unexpected GLSL block identities')
    # Convert ONLY c1 to the existing texelFetch form, then specialize static
    # literal loads with their exact IEEE-754 word from the captured code range.
    source = rewrite_cbuf_blocks(source, [b for b in blocks if b['instance'] == 'c1'])
    source, removed = inline_literal_cbuf(source, {'c1'}, code, control)
    if removed != {'c1'}:
        raise ValueError('literal bank not completely specialized')
    report = inspect(source, {'c3_1': 3})
    source = without_scalar_extension(source, {'c3_1': 3})
    if len(report) != 1 or report[0]['required_bytes'] != 384:
        raise ValueError('access contract changed')
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
            (w / ('literal-vertex.' + suffix)).write_bytes(data)
        (w / 'literal-vertex.glsl').write_text(source)
        text, index, literals = append(a.catalogue.read_text(), 'literal-vertex', w, aliases)
    if literals:
        raise ValueError('unexpected second literal specialization')
    a.output.write_text('#define LC2_LIT_VERTEX_INDEX %d\n' % index + text)
    report.update(index=index, code_sha256=CODE_SHA, control_sha256=CONTROL_SHA, aliases=aliases)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
