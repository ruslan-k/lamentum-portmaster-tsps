#!/usr/bin/env python3
"""Validate a finite read-only scalar float cbuf before texture lowering.

Input is SPIRV-Cross Vulkan GLSL (scalar layout accepted), NOT a stride-mutated
SPIR-V module. Only statically indexed scalar float loads are admitted here.
This deliberately does not purport to lower writable/atomic/SSBO buffers.
"""
import argparse
import json
from pathlib import Path
import re


def inspect(source, bank_aliases=None):
    if re.search(r'\b(buffer|atomic\w*|image\w*)\b', source):
        raise ValueError('writable/storage/atomic resource not supported')
    pattern = r'layout\([^)]*\bscalar\b[^)]*\)\s*uniform\s+(\w+)\s*\{\s*float\s+data\[(\d+)\];\s*\}\s*(\w+)\s*;'
    matches = list(re.finditer(pattern, source))
    if not matches:
        raise ValueError('no scalar finite float block')
    report = []
    for m in matches:
        count = int(m[2]); instance = m[3]
        if not 1 <= count <= 16384:
            raise ValueError('unsupported extent')
        uses = list(re.finditer(r'\b' + instance + r'\.data\[([^\]]+)\]', source))
        accesses = []
        for u in uses:
            index = u[1].strip()
            if not re.fullmatch(r'\d+u?', index):
                raise ValueError('dynamic/unknown index requires a separate range proof')
            n = int(index.rstrip('u'))
            if not 0 <= n < count:
                raise ValueError('out-of-bounds cbuf access')
            tail = source[u.end():].lstrip()
            head = source[:u.start()].rstrip()
            if re.match(r'(?:[+*/%&|^\-]?=(?!=)|\+\+|--)', tail) or head.endswith(('++','--')):
                raise ValueError('cbuf write is not a texture load')
            accesses.append(n)
        if not accesses:
            raise ValueError('unused block')
        remainder = source[:m.start()] + source[m.end():]
        remainder = re.sub(r'\b' + instance + r'\.data\[\d+u?\]', '', remainder)
        if re.search(r'\b' + instance + r'\b', remainder):
            raise ValueError('unhandled block use')
        match = re.fullmatch(r'c(\d+)', instance)
        bank = int(match[1]) if match else (bank_aliases or {}).get(instance)
        if bank is None or not 3 <= bank <= 18:
            raise ValueError('not an application cbuf bank')
        report.append({'instance': instance, 'block': m[1], 'count': count,
                       'original_stride_bytes': 4, 'nvn_slot': bank - 3,
                       'loads': len(accesses), 'word_indices': sorted(set(accesses)),
                       'byte_offsets': sorted({4 * n for n in accesses}),
                       'required_bytes': 4 * (max(accesses) + 1),
                       'texture_width': 1024, 'texture_format': 'RGBA32F',
                       'address_rule': '(word>>2)&1023, word>>12, lane=word&3'})
    # Strip the directive only when all scalar blocks were identified for removal.
    rest = re.sub(pattern, '', source)
    if re.search(r'\bscalar\b|\buniform\s+\w+\s*\{', rest):
        raise ValueError('unhandled scalar/block declaration')
    return report


def without_scalar_extension(source, bank_aliases=None):
    inspect(source, bank_aliases)
    return re.sub(r'^\s*#extension GL_EXT_scalar_block_layout\s*:\s*require\s*$', '', source, flags=re.M)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    p.add_argument('output', type=Path)
    p.add_argument('--report', type=Path, required=True)
    a = p.parse_args()
    s = a.source.read_text()
    report = inspect(s)
    a.output.write_text(without_scalar_extension(s))
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
