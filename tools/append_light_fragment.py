#!/usr/bin/env python3
"""Append the captured e1d6ede5 fragment's guarded, probe-disabled translation.

Not a general 3D/SSBO backend. EVERY draw needs the native flag/range guard.
Vulkan scalar-layout GLSL is lowered directly; no SPIR-V stride is changed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import tempfile
from append_program import append
from float_cbuf_contract import inspect, without_scalar_extension
from specialize_probe_disabled import specialize

CODE_SHA = 'e1d6ede5c901f5d441954877f35e624b591f81762ca0d962343206a1e9d396ce'
CONTROL_SHA = '687431312e0b2413baa9419a5d8a7dc62c024569bf4791868cac8249d01ccad8'


def prepare(source):
    # Retain the original false-branch expressions, not a constant TEST result.
    s = specialize(source, flag='_125', sampler='fs_tex0_30')
    report = inspect(s)
    s = without_scalar_extension(s)
    # Emulate explicit scalar f16 conversion with core GLES half pack/unpack,
    # rather than silently promoting all f16 casts to float32.
    s = re.sub(r'\bfloat16_t\s*\(', 'lc2_half(', s)
    s = re.sub(r'\bfloat16_t\b', 'float', s)
    s = re.sub(r'\bf16vec2\b', 'vec2', s)
    s = re.sub(r'#if defined\(GL_AMD_gpu_shader_half_float\).*?#endif\s*', '', s, flags=re.S)
    s = re.sub(r'^#extension GL_EXT_shader_16bit_storage[^\n]*\n', '', s, flags=re.M)
    s = s.replace('#version 450', '#version 450\n#define lc2_half(a) unpackHalf2x16(packHalf2x16(vec2(float(a), 0.0))).x\n/* GUARDED: c3[8] != 1.0 at every draw; enabled volume requires real backend. */', 1)
    if 'sampler3D' in s or re.search(r'\bf(?:loat16_t|16vec\d)\b', s):
        raise ValueError('unsupported dependency remains')
    return s, report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('workspace', type=Path)
    ap.add_argument('catalogue', type=Path)
    ap.add_argument('output', type=Path)
    ap.add_argument('--report', type=Path, required=True)
    a = ap.parse_args()
    code = (a.workspace / 'missing.code.bin').read_bytes()
    control = (a.workspace / 'missing.control.bin').read_bytes()
    if hashlib.sha256(code).hexdigest() != CODE_SHA or hashlib.sha256(control).hexdigest() != CONTROL_SHA:
        raise ValueError('not the pinned code/control pair')
    glsl, report = prepare((a.workspace / 'original-vulkan.glsl').read_text())
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)
        (p / 'lighting.glsl').write_text(glsl)
        (p / 'lighting.code.bin').write_bytes(code)
        (p / 'lighting.control.bin').write_bytes(control)
        text, index, literals = append(a.catalogue.read_text(), 'lighting', p)
    if literals or len(report) != 1 or report[0]['required_bytes'] != 220:
        raise ValueError('unexpected cbuf contract')
    text = '#define LC2_LIGHTPROBE_SPECIALIZED_INDEX %d\n' % index + text
    a.output.write_text(text)
    a.report.write_text(json.dumps({'index': index, 'code_sha256': CODE_SHA,
       'control_sha256': CONTROL_SHA, 'blocks': report, 'guard': 'fragment UBO0, bytes>=220, word8 != 0x3f800000',
       'half_conversion': 'explicit scalar casts round via packHalf2x16/unpackHalf2x16'}, indent=2) + '\n')
    print('appended guarded fragment', index)


if __name__ == '__main__':
    main()
