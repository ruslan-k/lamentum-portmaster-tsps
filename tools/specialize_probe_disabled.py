#!/usr/bin/env python3
"""Guarded specialization of the captured fragment's disabled probe-volume path.

This is not 3D sampler support: the runtime MUST validate the material flag at
EVERY draw and refuse enabled probes before issuing it.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
from build_lamentum_catalogue import rewrite_essl100, component_masks


def closing_brace(source, opening):
    depth = 0
    for i in range(opening, len(source)):
        depth += (source[i] == '{') - (source[i] == '}')
        if depth == 0:
            return i
    raise ValueError('unbalanced captured branch')


def select_branch(source, condition, take_true):
    matches = list(re.finditer(r'\bif\s*\(\s*' + re.escape(condition) + r'\s*\)\s*\{', source))
    if len(matches) != 1:
        raise ValueError('expected one captured branch: ' + condition)
    m = matches[0]
    a = source.index('{', m.start())
    b = closing_brace(source, a)
    other = re.match(r'\s*else\s*\{', source[b+1:])
    if not other:
        raise ValueError('expected explicit else')
    c = b + 1 + other.end() - 1
    d = closing_brace(source, c)
    selected = source[a:b+1] if take_true else source[c:d+1]
    return source[:m.start()] + selected + source[d+1:]


def specialize(source):
    source, n = re.subn(r'\bbool\s+_98\s*=\s*c3\.data\[8u\]\s*==\s*1\.0\s*;', '', source)
    if n != 1:
        raise ValueError('captured flag expression changed')
    source = select_branch(source, '_98', False)
    source = select_branch(source, '!_98', True)
    source, n = re.subn(r'\buniform\s+sampler3D\s+fs_tex0_28\s*;', '', source)
    if n != 1 or re.search(r'\b(?:_98|fs_tex0_28|sampler3D)\b', source):
        raise ValueError('probe dependency survived specialization')
    return source


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('workspace', type=Path)
    ap.add_argument('catalogue', type=Path)
    ap.add_argument('output', type=Path)
    a = ap.parse_args()
    name = 'dump-c523448a'
    text = a.catalogue.read_text()
    marker = 'static const struct mm_shader_binding nvn_megaman_shader_bindings[]='
    sources, metadata = text.split(marker, 1)
    pat = r'(/\* (\d+) ' + name + r' fragment \*/)(.*?)(?=/\* \d+ |\Z)'
    m = re.search(pat, metadata, re.S)
    if not m:
        raise ValueError('captured catalogue entry missing')
    index = int(m[2])
    for kind in ['code', 'control']:
        blob = (a.workspace / (name + '.' + kind + '.bin')).read_bytes()
        expected = bytes(int(v,16) for v in re.search(r'\.'+kind+r'_hash=\{([^}]+)\}', m[3])[1].split(','))
        if hashlib.sha256(blob).digest() != expected:
            raise ValueError('capture/catalogue identity mismatch: '+kind)
    raw = specialize((a.workspace/(name+'.glsl')).read_text())
    glsl, _ = rewrite_essl100(raw, 'fragment')
    glsl = glsl.replace('#version 310 es\n', '#version 310 es\n/* GUARDED translation: runtime requires probe flag != 1.0 before every draw. */\n', 1)
    entry = re.compile(r'(^\t/\* '+str(index)+' '+name+r' fragment \*/\n)(\t\{"",.*?\t "", 1\},\n)', re.M|re.S)
    body = '\t{"", "\\n"\n' + ''.join('\t '+json.dumps(line+'\n')+'\n' for line in glsl.splitlines()) + '\t "", 1},\n'
    sources, n = entry.subn(lambda x:x[1]+body, sources)
    if n != 1:
        raise ValueError('source entry mismatch')
    reads = component_masks(raw, 'in')
    block = re.sub(r'\.varying_read_masks=\{[^}]+\}', '.varying_read_masks={'+','.join(str(reads.get(i,0)) for i in range(8))+'}', m[3])
    metadata = metadata[:m.start(3)]+block+metadata[m.end(3):]
    macro = '#define LC2_PROBE_SPECIALIZED_INDEX %d\n' % index
    sources = re.sub(r'^#define LC2_PROBE_SPECIALIZED_INDEX \d+\n', '', sources, flags=re.M)
    a.output.write_text(macro + sources + marker + metadata)
    print('Guarded fragment',index,'probe disabled; shader identities preserved; runtime guard REQUIRED')


if __name__ == '__main__':
    main()
