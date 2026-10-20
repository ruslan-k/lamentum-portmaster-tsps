"""Faithful lowering of the pinned bb10c5c3 half-arithmetic MRT fragment.

The captured shader multiplies half lanes: every product in the original rounds to
float16 before it is widened back to float32. Replacing the types with `float` and
keeping the products would change those rounding points, so each product is wrapped
in `lc2_half()` (pack/unpack round-trip) and the statements are matched EXACTLY:
any drift in the pinned capture or in the GLSL text raises instead of silently
producing a different shader.
"""
import hashlib
import re

from half_float_lowering import HALF_ROUND_MACRO, lower_scalar_half_casts

# Exact statements from the pinned SPIRV-Cross output, and their faithful ESSL form.
REWRITES = [
    ('    mediump vec4 _54 = texture(fs_tex0_20, vec2(in_attr0.x, in_attr0.y));',
     '    mediump vec4 _54 = texture(fs_tex0_20, vec2(in_attr0.x, in_attr0.y));'),
    ('    float16_t _90 = float16_t(float(unpackFloat2x16(_61).x) * in_attr3.x);',
     '    float _90 = lc2_half(float(unpackHalf2x16(_61).x) * in_attr3.x);'),
    ('    f16vec2 _92 = unpackFloat2x16(_61);',
     '    vec2 _92 = unpackHalf2x16(_61);'),
    ('    float16_t _97 = float16_t(float(unpackFloat2x16(_63).y) * in_attr3.w);',
     '    float _97 = lc2_half(float(unpackHalf2x16(_63).y) * in_attr3.w);'),
    ('    float _108 = float(_97 * _90);',
     '    float _108 = float(lc2_half(_97 * _90));'),
    ('    float _110 = float(_97 * float16_t(float(_92.y) * in_attr3.y));',
     '    float _110 = float(lc2_half(_97 * lc2_half(float(_92.y) * in_attr3.y)));'),
    ('    float _112 = float(_97 * float16_t(float(unpackFloat2x16(_63).x) * in_attr3.z));',
     '    float _112 = float(lc2_half(_97 * lc2_half(float(unpackHalf2x16(_63).x) * in_attr3.z)));'),
]

REQUIRED_BEFORE = ['packHalf2x16(vec2(_54.xy))', 'packHalf2x16(vec2(_54.zw))',
                   'frag_color3.x = exp2(-(_108 * in_attr5.x));']


def lower_half_mrt(source, expected_source_sha256):
    actual = hashlib.sha256(source.encode()).hexdigest()
    if actual != expected_source_sha256:
        raise ValueError('GLSL text does not match the pinned capture: ' + actual)
    for old, new in REWRITES:
        if source.count(old) != 1:
            raise ValueError('pinned statement not found exactly once: ' + old.strip())
    for token in REQUIRED_BEFORE:
        if token not in source:
            raise ValueError('unexpected capture shape, missing ' + token)
    for old, new in REWRITES:
        source = source.replace(old, new)
    # Remaining f16 casts/types are handled by the shared narrow lowering (none expected here).
    source = lower_scalar_half_casts(source)
    source = source.replace('#version 450', '#version 450\n' + HALF_ROUND_MACRO, 1)
    if re.search(r'float16_t|f16vec|unpackFloat2x16', source):
        raise ValueError('half construct survived lowering')
    return source
