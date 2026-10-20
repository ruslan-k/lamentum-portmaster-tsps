#!/usr/bin/env python3
"""Append ONE captured program to the existing catalogue without regenerating it.

A full regeneration re-derives every entry from the workspace and silently reverts
hand-validated refinements (real translations that replaced TEST substitutes,
literal specialization, guarded branch selection). Appending keeps the existing
entries byte-identical and only adds a new identity at the end.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_lamentum_catalogue import (attributes_of, cbuf_blocks_of, component_masks,
                                      rewrite_essl100, samplers_of, varying_locations)
from shader_literals import inline_literal_cbuf


SRC_MARK = 'static const struct {const char *original,*gles;unsigned stage;} nvn_shader_sources[]='
META_MARK = 'static const struct mm_shader_binding nvn_megaman_shader_bindings[]='


def split_catalogue(text):
    head, rest = text.split(SRC_MARK, 1)
    src_body, meta_body = rest.split(META_MARK, 1)
    end = src_body.find('\n};\n')
    if end < 0 or not meta_body.rstrip().endswith('};'):
        raise ValueError('unexpected catalogue array tail')
    return head, src_body[:end + 1], src_body[end + 4:], meta_body.rstrip()[:-2]


def append(text, name, workspace):
    glsl = (workspace / (name + '.glsl')).read_text()
    code = (workspace / (name + '.code.bin')).read_bytes()
    control = (workspace / (name + '.control.bin')).read_bytes()
    stage = 'fragment' if ('frag_color' in glsl or 'gl_FragColor' in glsl) else 'vertex'
    translated, _ = rewrite_essl100(glsl, stage)
    cbufs = cbuf_blocks_of(glsl)
    translated, literals = inline_literal_cbuf(translated, {b['instance'] for b in cbufs}, code, control)
    cbufs = [b for b in cbufs if b['instance'] not in literals]
    # Hades names cN from desc.index (the hardware bank), not the declaration
    # binding ordinal. SDK 10.9 BindUniformBuffers encodes bank = NVN slot + 3.
    # Literal banks were specialized above; unknown non-literal names fail closed.
    for b in cbufs:
        match = re.fullmatch(r'c(\d+)', b['instance'])
        if not match or not 3 <= int(match[1]) <= 18:
            raise ValueError('unproven application cbuf bank: ' + b['instance'])
        b['binding'] = int(match[1]) - 3
    samplers = samplers_of(glsl)
    head, src_body, between, meta_body = split_catalogue(text)
    index = len(re.findall(r'^\t/\* \d+ ', src_body, re.M))
    if index != len(re.findall(r'^ /\* \d+ ', meta_body, re.M)):
        raise ValueError('catalogue arrays disagree on program count')
    code_sha, control_sha = hashlib.sha256(code).digest(), hashlib.sha256(control).digest()
    for digest in re.findall(r'\.code_hash=\{([^}]+)\}', meta_body):
        if bytes(int(v, 16) for v in digest.split(',')) == code_sha:
            raise ValueError('program already catalogued: ' + name)
    src = '\t/* %d %s %s */\n\t{"", "\\n"\n' % (index, name, stage)
    src += ''.join('\t ' + json.dumps(line + '\n') + '\n' for line in translated.splitlines())
    src += '\t "", %d},\n' % (1 if stage == 'fragment' else 0)
    writes = [0] * 8
    for loc, mask in component_masks(glsl, 'out').items():
        if loc < 8:
            writes[loc] = mask
    reads = [0] * 8
    for loc, mask in component_masks(translated if stage == 'fragment' else glsl, 'in').items():
        if loc < 8:
            reads[loc] = mask
    def kind(t):
        return 2 if t.startswith('u') else 1 if t.startswith('i') else 0
    meta = ' /* %d %s %s */\n' % (index, name, stage)
    meta += (' {.sha256="%s",.error=NULL,.control_size=%d,.code_size=%d,.sampler_count=%d,.attribute_count=%d,'
             '.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,\n'
             % (code_sha.hex()[:32], len(control), len(code), len(samplers), len(attributes_of(glsl))))
    meta += '  .uniform_count=%d,.uniforms={%s},\n' % (len(cbufs), ','.join(
        '{.name="%s",.stage=%d,.binding=%d,.offset=0,.size=%d,.components=4,.word_boolean=0,.word_int=0,.word_array=%d}'
        % (b['instance'], 0 if stage == 'vertex' else 1, b['binding'], b['count'] * 4, b['count'] // 4) for b in cbufs))
    meta += '  .varying_read_masks={%s},.varying_write_masks={%s},\n' % (
        ','.join(map(str, reads)), ','.join(map(str, writes)))
    meta += '  .code_hash={%s},.control_hash={%s},\n' % (
        ','.join('0x%02x' % b for b in code_sha), ','.join('0x%02x' % b for b in control_sha))
    meta += '  .samplers={%s},\n' % ','.join(
        '{.name="%s",.stage=%d,.binding=%d,.offset=%d,.size_query=1,.texel_fetch_bits=0,.cpu_view=0}'
        % (s['name'], s['stage'], s['binding'], s['offset']) for s in samplers)
    meta += '  .attributes={%s}},\n' % ','.join(
        '{.name="%s",.location=%d,.kind=%d}' % (a['name'], a['location'], kind(a['type'])) for a in attributes_of(glsl))
    head = re.sub(r'#define ZERO_ZX_SHADER_PACKAGES (\d+)',
                  lambda m: '#define ZERO_ZX_SHADER_PACKAGES %d' % (int(m[1]) + 1), head)
    return (head + SRC_MARK + src_body + src + '};\n' + between + META_MARK + meta_body + meta + '};\n'), index, literals


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('workspace', type=Path)
    ap.add_argument('catalogue', type=Path)
    ap.add_argument('output', type=Path)
    ap.add_argument('name')
    a = ap.parse_args()
    text, index, literals = append(a.catalogue.read_text(), a.name, a.workspace)
    a.output.write_text(text)
    print(json.dumps({'name': a.name, 'index': index, 'literal_banks_inlined': sorted(literals)}))


if __name__ == '__main__':
    main()
