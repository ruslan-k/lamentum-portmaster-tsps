"""Narrow scalar f16 conversion lowering used by pinned captured programs.

Vector f16 arithmetic is NOT emulated here. Callers pin the code/control pair and
prove f16vec2 variables only hold half-unpacked lanes or already-rounded scalars.
"""
import re

HALF_ROUND_MACRO = '#define lc2_half(a) unpackHalf2x16(packHalf2x16(vec2(float(a), 0.0))).x'


def lower_scalar_half_casts(source):
    source = re.sub(r'\bfloat16_t\s*\(', 'lc2_half(', source)
    source = re.sub(r'\bfloat16_t\b', 'float', source)
    source = re.sub(r'\bf16vec2\b', 'vec2', source)
    source = re.sub(r'#if defined\(GL_AMD_gpu_shader_half_float\).*?#endif\s*', '', source, flags=re.S)
    source = re.sub(r'^#extension GL_EXT_shader_16bit_storage[^\n]*\n', '', source, flags=re.M)
    if re.search(r'\b(?:f16\w*|float16_t|u?int16_t)\b', source):
        raise ValueError('unsupported half or narrow integer operation remains')
    return source
