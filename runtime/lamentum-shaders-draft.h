#define LC2_LIT_VERTEX_INDEX 42
#define LC2_SCENE_VERTEX_INDEX 40
#define LC2_LIGHTPROBE_SPECIALIZED_INDEX 39
#define LC2_PROBE_SPECIALIZED_INDEX 19
/* GENERATED DRAFT catalogue for Lamentum - our own translations, not game data.
 * Source: tools/build_lamentum_catalogue.py over the translate_lamentum_shaders.py workspace.
 * Every entry is a translation of the title's program; entries with an error string are
 * NOT translated and the runtime stops on them by design. */
#include <stddef.h>
#include <stdint.h>
#define ZERO_ZX_SHADER_PACKAGES 44
#define ZERO_SHADER_VARYING_SLOTS 8
#ifndef MOMO_SHADERS
#define MOMO_SHADERS 1
#endif
static const struct {const char *original,*gles;unsigned stage;} nvn_shader_sources[]={
	/* 0 dump-128077a9 fragment */
	{"", "\n"
	 "#version 310 es\n"
	 "precision mediump float;\n"
	 "#if defined(GL_AMD_gpu_shader_half_float)\n"
	 "#elif defined(GL_EXT_shader_explicit_arithmetic_types_float16)\n"
	 "#else\n"
	 "\n"
	 "#endif\n"
	 "\n"
	 " uniform highp sampler2D c3;\n"
	 "\n"
	 " uniform sampler2D fs_tex0_20;\n"
	 "\n"
	 "in vec4 varying_0;\n"
	 "in vec4 varying_1;\n"
	 "in vec4 varying_2;\n"
	 "layout(location = 0) out vec4 frag_color0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    vec4 _56 = texture(fs_tex0_20, vec2(varying_0.x, varying_0.y));\n"
	 "    float _57 = _56.w;\n"
	 "    float _93 = float((_57 * texelFetch(c3, ivec2((int(3u) >> 2) & 1023, int(3u) >> 12), 0)[int(3u) & 3]) * varying_2.w);\n"
	 "    frag_color0.x = float(_93 * float(((varying_2.w * varying_2.x) * texelFetch(c3, ivec2((int(0u) >> 2) & 1023, int(0u) >> 12), 0)[int(0u) & 3]) * varying_2.x)) * varying_1.x;\n"
	 "    frag_color0.y = float(_93 * float(((varying_2.w * varying_2.y) * texelFetch(c3, ivec2((int(1u) >> 2) & 1023, int(1u) >> 12), 0)[int(1u) & 3]) * varying_2.y)) * varying_1.x;\n"
	 "    frag_color0.z = float(_93 * float(((varying_2.w * varying_2.z) * texelFetch(c3, ivec2((int(2u) >> 2) & 1023, int(2u) >> 12), 0)[int(2u) & 3]) * varying_2.z)) * varying_1.x;\n"
	 "    frag_color0.w = _57 * varying_1.x;\n"
	 "}\n"
	 "", 1},
	/* 1 dump-12e9d131 fragment */
	{"", "\n"
	 "#version 310 es\n"
	 "precision mediump float;\n"
	 "uniform highp sampler2D c3;\n"
	 "\n"
	 " uniform sampler2D fs_tex0_20;\n"
	 "\n"
	 "in vec4 varying_0;\n"
	 "in vec4 varying_1;\n"
	 "layout(location = 0) out vec4 frag_color0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    vec4 _51 = texture(fs_tex0_20, vec2(varying_1.x, varying_1.y));\n"
	 "    frag_color0.x = (_51.x * texelFetch(c3, ivec2((int(0u) >> 2) & 1023, int(0u) >> 12), 0)[int(0u) & 3]) * varying_0.x;\n"
	 "    frag_color0.y = (_51.y * texelFetch(c3, ivec2((int(1u) >> 2) & 1023, int(1u) >> 12), 0)[int(1u) & 3]) * varying_0.y;\n"
	 "    frag_color0.z = (_51.z * texelFetch(c3, ivec2((int(2u) >> 2) & 1023, int(2u) >> 12), 0)[int(2u) & 3]) * varying_0.z;\n"
	 "    frag_color0.w = (_51.w * texelFetch(c3, ivec2((int(3u) >> 2) & 1023, int(3u) >> 12), 0)[int(3u) & 3]) * varying_0.w;\n"
	 "}\n"
	 "", 1},
	/* 2 dump-14196b8e vertex */
	{"", "\n"
	 "#version 310 es\n"
	 "precision highp float;\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "uniform highp sampler2D c3;\n"
	 "\n"
	 "layout(location = 0) in vec4 in_attr0;\n"
	 "layout(location = 1) in vec4 in_attr1;\n"
	 "layout(location = 2) in vec4 in_attr2;\n"
	 "out vec4 varying_0;\n"
	 "out vec4 varying_1;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_0 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_1 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_0.x = in_attr1.x;\n"
	 "    varying_0.y = in_attr1.y;\n"
	 "    varying_0.z = in_attr1.z;\n"
	 "    float _110 = fma(in_attr0.z, texelFetch(c3, ivec2((int(9u) >> 2) & 1023, int(9u) >> 12), 0)[int(9u) & 3], fma(in_attr0.x, texelFetch(c3, ivec2((int(1u) >> 2) & 1023, int(1u) >> 12), 0)[int(1u) & 3], in_attr0.y * texelFetch(c3, ivec2((int(5u) >> 2) & 1023, int(5u) >> 12), 0)[int(5u) & 3])) + texelFetch(c3, ivec2((int(13u) >> 2) & 1023, int(13u) >> 12), 0)[int(13u) & 3];\n"
	 "    varying_0.w = in_attr1.w;\n"
	 "    varying_1.x = fma(in_attr2.x, texelFetch(c3, ivec2((int(32u) >> 2) & 1023, int(32u) >> 12), 0)[int(32u) & 3], texelFetch(c3, ivec2((int(34u) >> 2) & 1023, int(34u) >> 12), 0)[int(34u) & 3]);\n"
	 "    float _122 = fma(in_attr0.z, texelFetch(c3, ivec2((int(8u) >> 2) & 1023, int(8u) >> 12), 0)[int(8u) & 3], fma(in_attr0.x, texelFetch(c3, ivec2((int(0u) >> 2) & 1023, int(0u) >> 12), 0)[int(0u) & 3], in_attr0.y * texelFetch(c3, ivec2((int(4u) >> 2) & 1023, int(4u) >> 12), 0)[int(4u) & 3])) + texelFetch(c3, ivec2((int(12u) >> 2) & 1023, int(12u) >> 12), 0)[int(12u) & 3];\n"
	 "    float _154 = fma(in_attr0.z, texelFetch(c3, ivec2((int(10u) >> 2) & 1023, int(10u) >> 12), 0)[int(10u) & 3], fma(in_attr0.x, texelFetch(c3, ivec2((int(2u) >> 2) & 1023, int(2u) >> 12), 0)[int(2u) & 3], in_attr0.y * texelFetch(c3, ivec2((int(6u) >> 2) & 1023, int(6u) >> 12), 0)[int(6u) & 3])) + texelFetch(c3, ivec2((int(14u) >> 2) & 1023, int(14u) >> 12), 0)[int(14u) & 3];\n"
	 "    float _158 = fma(in_attr0.z, texelFetch(c3, ivec2((int(11u) >> 2) & 1023, int(11u) >> 12), 0)[int(11u) & 3], fma(in_attr0.x, texelFetch(c3, ivec2((int(3u) >> 2) & 1023, int(3u) >> 12), 0)[int(3u) & 3], in_attr0.y * texelFetch(c3, ivec2((int(7u) >> 2) & 1023, int(7u) >> 12), 0)[int(7u) & 3])) + texelFetch(c3, ivec2((int(15u) >> 2) & 1023, int(15u) >> 12), 0)[int(15u) & 3];\n"
	 "    varying_1.y = fma(in_attr2.y, texelFetch(c3, ivec2((int(33u) >> 2) & 1023, int(33u) >> 12), 0)[int(33u) & 3], texelFetch(c3, ivec2((int(35u) >> 2) & 1023, int(35u) >> 12), 0)[int(35u) & 3]);\n"
	 "    gl_Position.x = fma(_158, texelFetch(c3, ivec2((int(28u) >> 2) & 1023, int(28u) >> 12), 0)[int(28u) & 3], fma(_154, texelFetch(c3, ivec2((int(24u) >> 2) & 1023, int(24u) >> 12), 0)[int(24u) & 3], fma(_122, texelFetch(c3, ivec2((int(16u) >> 2) & 1023, int(16u) >> 12), 0)[int(16u) & 3], _110 * texelFetch(c3, ivec2((int(20u) >> 2) & 1023, int(20u) >> 12), 0)[int(20u) & 3])));\n"
	 "    gl_Position.y = fma(_158, texelFetch(c3, ivec2((int(29u) >> 2) & 1023, int(29u) >> 12), 0)[int(29u) & 3], fma(_154, texelFetch(c3, ivec2((int(25u) >> 2) & 1023, int(25u) >> 12), 0)[int(25u) & 3], fma(_122, texelFetch(c3, ivec2((int(17u) >> 2) & 1023, int(17u) >> 12), 0)[int(17u) & 3], _110 * texelFetch(c3, ivec2((int(21u) >> 2) & 1023, int(21u) >> 12), 0)[int(21u) & 3])));\n"
	 "    gl_Position.z = fma(_158, texelFetch(c3, ivec2((int(30u) >> 2) & 1023, int(30u) >> 12), 0)[int(30u) & 3], fma(_154, texelFetch(c3, ivec2((int(26u) >> 2) & 1023, int(26u) >> 12), 0)[int(26u) & 3], fma(_122, texelFetch(c3, ivec2((int(18u) >> 2) & 1023, int(18u) >> 12), 0)[int(18u) & 3], _110 * texelFetch(c3, ivec2((int(22u) >> 2) & 1023, int(22u) >> 12), 0)[int(22u) & 3])));\n"
	 "    gl_Position.w = fma(_158, texelFetch(c3, ivec2((int(31u) >> 2) & 1023, int(31u) >> 12), 0)[int(31u) & 3], fma(_154, texelFetch(c3, ivec2((int(27u) >> 2) & 1023, int(27u) >> 12), 0)[int(27u) & 3], fma(_122, texelFetch(c3, ivec2((int(19u) >> 2) & 1023, int(19u) >> 12), 0)[int(19u) & 3], _110 * texelFetch(c3, ivec2((int(23u) >> 2) & 1023, int(23u) >> 12), 0)[int(23u) & 3])));\n"
	 "}\n"
	 "", 0},
	/* 3 dump-1792425422-0 fragment */
	{"", "\n"
	 "#version 310 es\n"
	 "precision mediump float;\n"
	 "#define unpackFloat2x16(a) unpackHalf2x16(a)\n"
	 "#define packFloat2x16(a) packHalf2x16(a)\n"
	 "#if defined(GL_AMD_gpu_shader_half_float)\n"
	 "#elif defined(GL_EXT_shader_explicit_arithmetic_types_float16)\n"
	 "#else\n"
	 "\n"
	 "#endif\n"
	 "\n"
	 " \n"
	 "\n"
	 " uniform sampler2D fs_tex0_20;\n"
	 " uniform sampler3D fs_tex0_28;\n"
	 "\n"
	 "in vec4 varying_1;\n"
	 "in vec4 varying_3;\n"
	 "layout(location = 0) out vec4 frag_color0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    if (float(unpackFloat2x16(packHalf2x16(vec2(texture(fs_tex0_28, vec3(gl_FragCoord.x * 0.25, gl_FragCoord.y * 0.25, float(float(float(unpackFloat2x16(packHalf2x16(vec2(texture(fs_tex0_20, vec2(varying_1.x, varying_1.y)).w, 0.0))).x) * varying_3.w) * unpackFloat2x16(998259584u).x))).w, 0.0))).x) < uintBitsToFloat(0x3c23e000u))\n"
	 "    {\n"
	 "        demote;\n"
	 "    }\n"
	 "    frag_color0.x = 0.0;\n"
	 "    frag_color0.y = 0.0;\n"
	 "    frag_color0.z = 0.0;\n"
	 "    frag_color0.w = 0.0;\n"
	 "}\n"
	 "", 1},
	/* 4 dump-2991ad4b fragment */
	{"", "\n"
	 "#version 310 es\n"
	 "precision mediump float;\n"
	 "uniform sampler2D fs_tex0_20;\n"
	 "\n"
	 "in vec4 varying_0;\n"
	 "in vec4 varying_1;\n"
	 "in vec4 varying_2;\n"
	 "in vec4 varying_3;\n"
	 "layout(location = 0) out vec4 frag_color0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    vec4 _59 = texture(fs_tex0_20, vec2(varying_1.x, varying_1.y));\n"
	 "    vec4 _64 = texture(fs_tex0_20, vec2(varying_2.x, varying_2.y));\n"
	 "    vec4 _69 = texture(fs_tex0_20, vec2(varying_3.x, varying_3.y));\n"
	 "    vec4 _74 = texture(fs_tex0_20, vec2(varying_0.x, varying_0.y));\n"
	 "    frag_color0.x = max(max(_74.x, _59.x), max(_64.x, _69.x));\n"
	 "    frag_color0.y = min(min(_74.y, _59.y), min(_64.y, _69.y));\n"
	 "    frag_color0.z = _74.z;\n"
	 "    frag_color0.w = _74.w;\n"
	 "}\n"
	 "", 1},
	/* 5 dump-29d0db82 vertex */
	{"", "\n"
	 "#version 310 es\n"
	 "precision highp float;\n"
	 "/* TEST-ONLY substitute: NOT a translation of the title's program. Written so the\n"
	 " * replay can exercise draws/present while the real program is untranslated; the\n"
	 " * log marks it TEST and no picture claim may rest on it. */\n"
	 "in vec4 in_attr0;\n"
	 "in vec4 in_attr1;\n"
	 "layout(location = 1) out vec4 varying_1;\n"
	 "layout(location = 2) out vec4 varying_2;\n"
	 "layout(location = 3) out vec4 varying_3;\n"
	 "void main() { gl_Position = vec4(in_attr0.xy, in_attr0.z, 1.0); varying_1 = in_attr1; varying_2 = in_attr1; varying_3 = in_attr1; }\n"
	 "", 0},
	/* 6 dump-33650b4b fragment */
	{"", "\n"
	 "#version 310 es\n"
	 "precision highp int;\n"
	 "precision mediump float;\n"
	 "#define unpackFloat2x16(a) unpackHalf2x16(a)\n"
	 "#define packFloat2x16(a) packHalf2x16(a)\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "#if defined(GL_AMD_gpu_shader_half_float)\n"
	 "#elif defined(GL_EXT_shader_explicit_arithmetic_types_float16)\n"
	 "#else\n"
	 "\n"
	 "#endif\n"
	 "\n"
	 " \n"
	 "\n"
	 " uniform highp sampler2D c3_1;\n"
	 "\n"
	 " uniform sampler2D fs_tex0_20;\n"
	 " uniform sampler2D fs_tex0_28;\n"
	 "\n"
	 "in vec4 varying_0;\n"
	 "layout(location = 0) out vec4 frag_color0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    float _61 = fma(varying_0.x, texelFetch(c3_1, ivec2((int(4u) >> 2) & 1023, int(4u) >> 12), 0)[int(4u) & 3], texelFetch(c3_1, ivec2((int(6u) >> 2) & 1023, int(6u) >> 12), 0)[int(6u) & 3]);\n"
	 "    float _68 = fma(varying_0.y, texelFetch(c3_1, ivec2((int(5u) >> 2) & 1023, int(5u) >> 12), 0)[int(5u) & 3], texelFetch(c3_1, ivec2((int(7u) >> 2) & 1023, int(7u) >> 12), 0)[int(7u) & 3]);\n"
	 "    uint _75 = packHalf2x16(vec2(texture(fs_tex0_28, vec2(_61, _68)).xy));\n"
	 "    vec4 _78 = texture(fs_tex0_20, vec2(_61, _68));\n"
	 "    float _79 = _78.x;\n"
	 "    float _80 = _78.y;\n"
	 "    float _97 = float(float((-_79) + float(unpackFloat2x16(_75).x))) * texelFetch(c3_1, ivec2((int(0u) >> 2) & 1023, int(0u) >> 12), 0)[int(0u) & 3];\n"
	 "    float _100 = float(float((-_80) + float(unpackFloat2x16(_75).y))) * texelFetch(c3_1, ivec2((int(0u) >> 2) & 1023, int(0u) >> 12), 0)[int(0u) & 3];\n"
	 "    float _142 = max(fma(max(abs(_97), uintBitsToFloat(0x3b808081u)), float(int(bitfieldExtract(uint(abs(int(uint(bitfieldExtract(int((_97 > 0.0) ? 4294967295u : 0u), int(0u), int(32u)))))), int(0u), int(32u)) + (-bitfieldExtract(uint(abs(int(uint(bitfieldExtract(int((_97 < 0.0) ? 4294967295u : 0u), int(0u), int(32u)))))), int(0u), int(32u))))), _79), texelFetch(c3_1, ivec2((int(2u) >> 2) & 1023, int(2u) >> 12), 0)[int(2u) & 3]);\n"
	 "    float _145 = min(fma(max(abs(_100), uintBitsToFloat(0x3b808081u)), float(int(bitfieldExtract(uint(abs(int(uint(bitfieldExtract(int((_100 > 0.0) ? 4294967295u : 0u), int(0u), int(32u)))))), int(0u), int(32u)) + (-bitfieldExtract(uint(abs(int(uint(bitfieldExtract(int((_100 < 0.0) ? 4294967295u : 0u), int(0u), int(32u)))))), int(0u), int(32u))))), _80), texelFetch(c3_1, ivec2((int(1u) >> 2) & 1023, int(1u) >> 12), 0)[int(1u) & 3]);\n"
	 "    float _149 = (_142 + (-_145)) + 0.00999999977648258209228515625;\n"
	 "    frag_color0.x = _142;\n"
	 "    frag_color0.y = _145;\n"
	 "    frag_color0.z = _149;\n"
	 "    frag_color0.w = _145 * (1.0 / _149);\n"
	 "}\n"
	 "", 1},
	/* 7 dump-3a41323d vertex */
	{"", "\n"
	 "#version 310 es\n"
	 "precision highp float;\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "uniform highp sampler2D c4;\n"
	 "\n"
	 "layout(location = 0) in vec4 in_attr0;\n"
	 "layout(location = 1) in vec4 in_attr1;\n"
	 "layout(location = 2) in vec4 in_attr2;\n"
	 "out vec4 varying_0;\n"
	 "out vec4 varying_1;\n"
	 "out vec4 varying_2;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_0 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_1 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_2 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_0.x = in_attr2.x;\n"
	 "    varying_2.y = in_attr1.y;\n"
	 "    float _121 = fma(in_attr0.z, texelFetch(c4, ivec2((int(17u) >> 2) & 1023, int(17u) >> 12), 0)[int(17u) & 3], fma(in_attr0.x, texelFetch(c4, ivec2((int(9u) >> 2) & 1023, int(9u) >> 12), 0)[int(9u) & 3], in_attr0.y * texelFetch(c4, ivec2((int(13u) >> 2) & 1023, int(13u) >> 12), 0)[int(13u) & 3])) + texelFetch(c4, ivec2((int(21u) >> 2) & 1023, int(21u) >> 12), 0)[int(21u) & 3];\n"
	 "    varying_2.x = in_attr1.x;\n"
	 "    varying_2.z = in_attr1.z;\n"
	 "    varying_0.y = in_attr2.y;\n"
	 "    float _144 = fma(in_attr0.z, texelFetch(c4, ivec2((int(16u) >> 2) & 1023, int(16u) >> 12), 0)[int(16u) & 3], fma(in_attr0.x, texelFetch(c4, ivec2((int(8u) >> 2) & 1023, int(8u) >> 12), 0)[int(8u) & 3], in_attr0.y * texelFetch(c4, ivec2((int(12u) >> 2) & 1023, int(12u) >> 12), 0)[int(12u) & 3])) + texelFetch(c4, ivec2((int(20u) >> 2) & 1023, int(20u) >> 12), 0)[int(20u) & 3];\n"
	 "    varying_0.z = in_attr2.z;\n"
	 "    varying_0.w = in_attr2.w;\n"
	 "    varying_2.w = in_attr1.w;\n"
	 "    float _180 = fma(in_attr0.z, texelFetch(c4, ivec2((int(18u) >> 2) & 1023, int(18u) >> 12), 0)[int(18u) & 3], fma(in_attr0.x, texelFetch(c4, ivec2((int(10u) >> 2) & 1023, int(10u) >> 12), 0)[int(10u) & 3], in_attr0.y * texelFetch(c4, ivec2((int(14u) >> 2) & 1023, int(14u) >> 12), 0)[int(14u) & 3])) + texelFetch(c4, ivec2((int(22u) >> 2) & 1023, int(22u) >> 12), 0)[int(22u) & 3];\n"
	 "    float _185 = fma(in_attr0.z, texelFetch(c4, ivec2((int(19u) >> 2) & 1023, int(19u) >> 12), 0)[int(19u) & 3], fma(in_attr0.x, texelFetch(c4, ivec2((int(11u) >> 2) & 1023, int(11u) >> 12), 0)[int(11u) & 3], in_attr0.y * texelFetch(c4, ivec2((int(15u) >> 2) & 1023, int(15u) >> 12), 0)[int(15u) & 3])) + texelFetch(c4, ivec2((int(23u) >> 2) & 1023, int(23u) >> 12), 0)[int(23u) & 3];\n"
	 "    varying_1.x = fma(sin(texelFetch(c4, ivec2((int(42u) >> 2) & 1023, int(42u) >> 12), 0)[int(42u) & 3] * texelFetch(c4, ivec2((int(3u) >> 2) & 1023, int(3u) >> 12), 0)[int(3u) & 3]) * ((texelFetch(c4, ivec2((int(40u) >> 2) & 1023, int(40u) >> 12), 0)[int(40u) & 3] * texelFetch(c4, ivec2((int(41u) >> 2) & 1023, int(41u) >> 12), 0)[int(41u) & 3]) * cos(texelFetch(c4, ivec2((int(42u) >> 2) & 1023, int(42u) >> 12), 0)[int(42u) & 3] * texelFetch(c4, ivec2((int(2u) >> 2) & 1023, int(2u) >> 12), 0)[int(2u) & 3])), texelFetch(c4, ivec2((int(7u) >> 2) & 1023, int(7u) >> 12), 0)[int(7u) & 3], texelFetch(c4, ivec2((int(40u) >> 2) & 1023, int(40u) >> 12), 0)[int(40u) & 3]);\n"
	 "    gl_Position.x = fma(_185, texelFetch(c4, ivec2((int(36u) >> 2) & 1023, int(36u) >> 12), 0)[int(36u) & 3], fma(_180, texelFetch(c4, ivec2((int(32u) >> 2) & 1023, int(32u) >> 12), 0)[int(32u) & 3], fma(_144, texelFetch(c4, ivec2((int(24u) >> 2) & 1023, int(24u) >> 12), 0)[int(24u) & 3], _121 * texelFetch(c4, ivec2((int(28u) >> 2) & 1023, int(28u) >> 12), 0)[int(28u) & 3])));\n"
	 "    gl_Position.y = fma(_185, texelFetch(c4, ivec2((int(37u) >> 2) & 1023, int(37u) >> 12), 0)[int(37u) & 3], fma(_180, texelFetch(c4, ivec2((int(33u) >> 2) & 1023, int(33u) >> 12), 0)[int(33u) & 3], fma(_144, texelFetch(c4, ivec2((int(25u) >> 2) & 1023, int(25u) >> 12), 0)[int(25u) & 3], _121 * texelFetch(c4, ivec2((int(29u) >> 2) & 1023, int(29u) >> 12), 0)[int(29u) & 3])));\n"
	 "    gl_Position.z = fma(_185, texelFetch(c4, ivec2((int(38u) >> 2) & 1023, int(38u) >> 12), 0)[int(38u) & 3], fma(_180, texelFetch(c4, ivec2((int(34u) >> 2) & 1023, int(34u) >> 12), 0)[int(34u) & 3], fma(_144, texelFetch(c4, ivec2((int(26u) >> 2) & 1023, int(26u) >> 12), 0)[int(26u) & 3], _121 * texelFetch(c4, ivec2((int(30u) >> 2) & 1023, int(30u) >> 12), 0)[int(30u) & 3])));\n"
	 "    gl_Position.w = fma(_185, texelFetch(c4, ivec2((int(39u) >> 2) & 1023, int(39u) >> 12), 0)[int(39u) & 3], fma(_180, texelFetch(c4, ivec2((int(35u) >> 2) & 1023, int(35u) >> 12), 0)[int(35u) & 3], fma(_144, texelFetch(c4, ivec2((int(27u) >> 2) & 1023, int(27u) >> 12), 0)[int(27u) & 3], _121 * texelFetch(c4, ivec2((int(31u) >> 2) & 1023, int(31u) >> 12), 0)[int(31u) & 3])));\n"
	 "}\n"
	 "", 0},
	/* 8 dump-3a75a7d0 vertex */
	{"", "\n"
	 "#version 310 es\n"
	 "precision highp float;\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "uniform highp sampler2D c3;\n"
	 "\n"
	 "layout(location = 0) in vec4 in_attr0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    float _90 = fma(in_attr0.z, texelFetch(c3, ivec2((int(9u) >> 2) & 1023, int(9u) >> 12), 0)[int(9u) & 3], fma(in_attr0.x, texelFetch(c3, ivec2((int(1u) >> 2) & 1023, int(1u) >> 12), 0)[int(1u) & 3], in_attr0.y * texelFetch(c3, ivec2((int(5u) >> 2) & 1023, int(5u) >> 12), 0)[int(5u) & 3])) + texelFetch(c3, ivec2((int(13u) >> 2) & 1023, int(13u) >> 12), 0)[int(13u) & 3];\n"
	 "    float _94 = fma(in_attr0.z, texelFetch(c3, ivec2((int(8u) >> 2) & 1023, int(8u) >> 12), 0)[int(8u) & 3], fma(in_attr0.x, texelFetch(c3, ivec2((int(0u) >> 2) & 1023, int(0u) >> 12), 0)[int(0u) & 3], in_attr0.y * texelFetch(c3, ivec2((int(4u) >> 2) & 1023, int(4u) >> 12), 0)[int(4u) & 3])) + texelFetch(c3, ivec2((int(12u) >> 2) & 1023, int(12u) >> 12), 0)[int(12u) & 3];\n"
	 "    float _114 = fma(in_attr0.z, texelFetch(c3, ivec2((int(10u) >> 2) & 1023, int(10u) >> 12), 0)[int(10u) & 3], fma(in_attr0.x, texelFetch(c3, ivec2((int(2u) >> 2) & 1023, int(2u) >> 12), 0)[int(2u) & 3], in_attr0.y * texelFetch(c3, ivec2((int(6u) >> 2) & 1023, int(6u) >> 12), 0)[int(6u) & 3])) + texelFetch(c3, ivec2((int(14u) >> 2) & 1023, int(14u) >> 12), 0)[int(14u) & 3];\n"
	 "    float _118 = fma(in_attr0.z, texelFetch(c3, ivec2((int(11u) >> 2) & 1023, int(11u) >> 12), 0)[int(11u) & 3], fma(in_attr0.x, texelFetch(c3, ivec2((int(3u) >> 2) & 1023, int(3u) >> 12), 0)[int(3u) & 3], in_attr0.y * texelFetch(c3, ivec2((int(7u) >> 2) & 1023, int(7u) >> 12), 0)[int(7u) & 3])) + texelFetch(c3, ivec2((int(15u) >> 2) & 1023, int(15u) >> 12), 0)[int(15u) & 3];\n"
	 "    gl_Position.x = fma(_118, texelFetch(c3, ivec2((int(28u) >> 2) & 1023, int(28u) >> 12), 0)[int(28u) & 3], fma(_114, texelFetch(c3, ivec2((int(24u) >> 2) & 1023, int(24u) >> 12), 0)[int(24u) & 3], fma(_94, texelFetch(c3, ivec2((int(16u) >> 2) & 1023, int(16u) >> 12), 0)[int(16u) & 3], _90 * texelFetch(c3, ivec2((int(20u) >> 2) & 1023, int(20u) >> 12), 0)[int(20u) & 3])));\n"
	 "    gl_Position.y = fma(_118, texelFetch(c3, ivec2((int(29u) >> 2) & 1023, int(29u) >> 12), 0)[int(29u) & 3], fma(_114, texelFetch(c3, ivec2((int(25u) >> 2) & 1023, int(25u) >> 12), 0)[int(25u) & 3], fma(_94, texelFetch(c3, ivec2((int(17u) >> 2) & 1023, int(17u) >> 12), 0)[int(17u) & 3], _90 * texelFetch(c3, ivec2((int(21u) >> 2) & 1023, int(21u) >> 12), 0)[int(21u) & 3])));\n"
	 "    gl_Position.z = fma(_118, texelFetch(c3, ivec2((int(30u) >> 2) & 1023, int(30u) >> 12), 0)[int(30u) & 3], fma(_114, texelFetch(c3, ivec2((int(26u) >> 2) & 1023, int(26u) >> 12), 0)[int(26u) & 3], fma(_94, texelFetch(c3, ivec2((int(18u) >> 2) & 1023, int(18u) >> 12), 0)[int(18u) & 3], _90 * texelFetch(c3, ivec2((int(22u) >> 2) & 1023, int(22u) >> 12), 0)[int(22u) & 3])));\n"
	 "    gl_Position.w = fma(_118, texelFetch(c3, ivec2((int(31u) >> 2) & 1023, int(31u) >> 12), 0)[int(31u) & 3], fma(_114, texelFetch(c3, ivec2((int(27u) >> 2) & 1023, int(27u) >> 12), 0)[int(27u) & 3], fma(_94, texelFetch(c3, ivec2((int(19u) >> 2) & 1023, int(19u) >> 12), 0)[int(19u) & 3], _90 * texelFetch(c3, ivec2((int(23u) >> 2) & 1023, int(23u) >> 12), 0)[int(23u) & 3])));\n"
	 "}\n"
	 "", 0},
	/* 9 dump-4b551bd7 fragment */
	{"", "\n"
	 "#version 310 es\n"
	 "precision mediump float;\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "uniform sampler2D fs_tex0_20;\n"
	 " uniform sampler2D fs_tex0_28;\n"
	 "\n"
	 "in vec4 varying_0;\n"
	 "in vec4 varying_1;\n"
	 "layout(location = 0) out vec4 frag_color0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    vec4 _50 = texture(fs_tex0_28, vec2(varying_1.x, varying_1.y));\n"
	 "    float _52 = _50.w;\n"
	 "    vec4 _55 = texture(fs_tex0_20, vec2(varying_0.x, varying_0.y));\n"
	 "    float _61 = 1.0 / _50.z;\n"
	 "    frag_color0.x = fma(_55.x, _61, -_52);\n"
	 "    frag_color0.y = fma(_55.y, _61, -_52);\n"
	 "    frag_color0.z = fma(_55.z, _61, -_52);\n"
	 "    frag_color0.w = _55.w;\n"
	 "}\n"
	 "", 1},
	/* 10 dump-56844c6b vertex */
	{"", "\n"
	 "#version 310 es\n"
	 "precision highp float;\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "uniform highp sampler2D c3;\n"
	 "\n"
	 "layout(location = 0) in vec4 in_attr0;\n"
	 "layout(location = 1) in vec4 in_attr1;\n"
	 "layout(location = 2) in vec4 in_attr2;\n"
	 "out vec4 varying_0;\n"
	 "out vec4 varying_1;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_0 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_1 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    float _62 = in_attr0.y * texelFetch(c3, ivec2((int(37u) >> 2) & 1023, int(37u) >> 12), 0)[int(37u) & 3];\n"
	 "    float _69 = in_attr0.x * texelFetch(c3, ivec2((int(36u) >> 2) & 1023, int(36u) >> 12), 0)[int(36u) & 3];\n"
	 "    varying_1.x = in_attr2.x;\n"
	 "    varying_1.y = in_attr2.y;\n"
	 "    float _120 = fma(in_attr0.z, texelFetch(c3, ivec2((int(9u) >> 2) & 1023, int(9u) >> 12), 0)[int(9u) & 3], fma(_69, texelFetch(c3, ivec2((int(1u) >> 2) & 1023, int(1u) >> 12), 0)[int(1u) & 3], _62 * texelFetch(c3, ivec2((int(5u) >> 2) & 1023, int(5u) >> 12), 0)[int(5u) & 3])) + texelFetch(c3, ivec2((int(13u) >> 2) & 1023, int(13u) >> 12), 0)[int(13u) & 3];\n"
	 "    float _136 = fma(in_attr0.z, texelFetch(c3, ivec2((int(8u) >> 2) & 1023, int(8u) >> 12), 0)[int(8u) & 3], fma(_69, texelFetch(c3, ivec2((int(0u) >> 2) & 1023, int(0u) >> 12), 0)[int(0u) & 3], _62 * texelFetch(c3, ivec2((int(4u) >> 2) & 1023, int(4u) >> 12), 0)[int(4u) & 3])) + texelFetch(c3, ivec2((int(12u) >> 2) & 1023, int(12u) >> 12), 0)[int(12u) & 3];\n"
	 "    varying_0.x = (in_attr1.x * texelFetch(c3, ivec2((int(40u) >> 2) & 1023, int(40u) >> 12), 0)[int(40u) & 3]) * texelFetch(c3, ivec2((int(32u) >> 2) & 1023, int(32u) >> 12), 0)[int(32u) & 3];\n"
	 "    varying_0.y = (in_attr1.y * texelFetch(c3, ivec2((int(41u) >> 2) & 1023, int(41u) >> 12), 0)[int(41u) & 3]) * texelFetch(c3, ivec2((int(33u) >> 2) & 1023, int(33u) >> 12), 0)[int(33u) & 3];\n"
	 "    float _178 = fma(in_attr0.z, texelFetch(c3, ivec2((int(10u) >> 2) & 1023, int(10u) >> 12), 0)[int(10u) & 3], fma(_69, texelFetch(c3, ivec2((int(2u) >> 2) & 1023, int(2u) >> 12), 0)[int(2u) & 3], _62 * texelFetch(c3, ivec2((int(6u) >> 2) & 1023, int(6u) >> 12), 0)[int(6u) & 3])) + texelFetch(c3, ivec2((int(14u) >> 2) & 1023, int(14u) >> 12), 0)[int(14u) & 3];\n"
	 "    float _182 = fma(in_attr0.z, texelFetch(c3, ivec2((int(11u) >> 2) & 1023, int(11u) >> 12), 0)[int(11u) & 3], fma(_69, texelFetch(c3, ivec2((int(3u) >> 2) & 1023, int(3u) >> 12), 0)[int(3u) & 3], _62 * texelFetch(c3, ivec2((int(7u) >> 2) & 1023, int(7u) >> 12), 0)[int(7u) & 3])) + texelFetch(c3, ivec2((int(15u) >> 2) & 1023, int(15u) >> 12), 0)[int(15u) & 3];\n"
	 "    varying_0.z = (in_attr1.z * texelFetch(c3, ivec2((int(42u) >> 2) & 1023, int(42u) >> 12), 0)[int(42u) & 3]) * texelFetch(c3, ivec2((int(34u) >> 2) & 1023, int(34u) >> 12), 0)[int(34u) & 3];\n"
	 "    varying_0.w = (in_attr1.w * texelFetch(c3, ivec2((int(43u) >> 2) & 1023, int(43u) >> 12), 0)[int(43u) & 3]) * texelFetch(c3, ivec2((int(35u) >> 2) & 1023, int(35u) >> 12), 0)[int(35u) & 3];\n"
	 "    gl_Position.x = fma(_182, texelFetch(c3, ivec2((int(28u) >> 2) & 1023, int(28u) >> 12), 0)[int(28u) & 3], fma(_178, texelFetch(c3, ivec2((int(24u) >> 2) & 1023, int(24u) >> 12), 0)[int(24u) & 3], fma(_136, texelFetch(c3, ivec2((int(16u) >> 2) & 1023, int(16u) >> 12), 0)[int(16u) & 3], _120 * texelFetch(c3, ivec2((int(20u) >> 2) & 1023, int(20u) >> 12), 0)[int(20u) & 3])));\n"
	 "    gl_Position.y = fma(_182, texelFetch(c3, ivec2((int(29u) >> 2) & 1023, int(29u) >> 12), 0)[int(29u) & 3], fma(_178, texelFetch(c3, ivec2((int(25u) >> 2) & 1023, int(25u) >> 12), 0)[int(25u) & 3], fma(_136, texelFetch(c3, ivec2((int(17u) >> 2) & 1023, int(17u) >> 12), 0)[int(17u) & 3], _120 * texelFetch(c3, ivec2((int(21u) >> 2) & 1023, int(21u) >> 12), 0)[int(21u) & 3])));\n"
	 "    gl_Position.z = fma(_182, texelFetch(c3, ivec2((int(30u) >> 2) & 1023, int(30u) >> 12), 0)[int(30u) & 3], fma(_178, texelFetch(c3, ivec2((int(26u) >> 2) & 1023, int(26u) >> 12), 0)[int(26u) & 3], fma(_136, texelFetch(c3, ivec2((int(18u) >> 2) & 1023, int(18u) >> 12), 0)[int(18u) & 3], _120 * texelFetch(c3, ivec2((int(22u) >> 2) & 1023, int(22u) >> 12), 0)[int(22u) & 3])));\n"
	 "    gl_Position.w = fma(_182, texelFetch(c3, ivec2((int(31u) >> 2) & 1023, int(31u) >> 12), 0)[int(31u) & 3], fma(_178, texelFetch(c3, ivec2((int(27u) >> 2) & 1023, int(27u) >> 12), 0)[int(27u) & 3], fma(_136, texelFetch(c3, ivec2((int(19u) >> 2) & 1023, int(19u) >> 12), 0)[int(19u) & 3], _120 * texelFetch(c3, ivec2((int(23u) >> 2) & 1023, int(23u) >> 12), 0)[int(23u) & 3])));\n"
	 "}\n"
	 "", 0},
	/* 11 dump-6054acba vertex */
	{"", "\n"
	 "#version 310 es\n"
	 "precision highp float;\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "uniform highp sampler2D c4;\n"
	 "\n"
	 "layout(location = 0) in vec4 in_attr0;\n"
	 "layout(location = 1) in vec4 in_attr1;\n"
	 "out vec4 varying_0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_0 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_0.x = in_attr1.x;\n"
	 "    varying_0.y = in_attr1.y;\n"
	 "    float _94 = fma(in_attr0.z, texelFetch(c4, ivec2((int(9u) >> 2) & 1023, int(9u) >> 12), 0)[int(9u) & 3], fma(in_attr0.x, texelFetch(c4, ivec2((int(1u) >> 2) & 1023, int(1u) >> 12), 0)[int(1u) & 3], in_attr0.y * texelFetch(c4, ivec2((int(5u) >> 2) & 1023, int(5u) >> 12), 0)[int(5u) & 3])) + texelFetch(c4, ivec2((int(13u) >> 2) & 1023, int(13u) >> 12), 0)[int(13u) & 3];\n"
	 "    float _102 = fma(in_attr0.z, texelFetch(c4, ivec2((int(8u) >> 2) & 1023, int(8u) >> 12), 0)[int(8u) & 3], fma(in_attr0.x, texelFetch(c4, ivec2((int(0u) >> 2) & 1023, int(0u) >> 12), 0)[int(0u) & 3], in_attr0.y * texelFetch(c4, ivec2((int(4u) >> 2) & 1023, int(4u) >> 12), 0)[int(4u) & 3])) + texelFetch(c4, ivec2((int(12u) >> 2) & 1023, int(12u) >> 12), 0)[int(12u) & 3];\n"
	 "    float _122 = fma(in_attr0.z, texelFetch(c4, ivec2((int(10u) >> 2) & 1023, int(10u) >> 12), 0)[int(10u) & 3], fma(in_attr0.x, texelFetch(c4, ivec2((int(2u) >> 2) & 1023, int(2u) >> 12), 0)[int(2u) & 3], in_attr0.y * texelFetch(c4, ivec2((int(6u) >> 2) & 1023, int(6u) >> 12), 0)[int(6u) & 3])) + texelFetch(c4, ivec2((int(14u) >> 2) & 1023, int(14u) >> 12), 0)[int(14u) & 3];\n"
	 "    float _142 = fma(in_attr0.z, texelFetch(c4, ivec2((int(11u) >> 2) & 1023, int(11u) >> 12), 0)[int(11u) & 3], fma(in_attr0.x, texelFetch(c4, ivec2((int(3u) >> 2) & 1023, int(3u) >> 12), 0)[int(3u) & 3], in_attr0.y * texelFetch(c4, ivec2((int(7u) >> 2) & 1023, int(7u) >> 12), 0)[int(7u) & 3])) + texelFetch(c4, ivec2((int(15u) >> 2) & 1023, int(15u) >> 12), 0)[int(15u) & 3];\n"
	 "    gl_Position.x = fma(_142, texelFetch(c4, ivec2((int(28u) >> 2) & 1023, int(28u) >> 12), 0)[int(28u) & 3], fma(_122, texelFetch(c4, ivec2((int(24u) >> 2) & 1023, int(24u) >> 12), 0)[int(24u) & 3], fma(_102, texelFetch(c4, ivec2((int(16u) >> 2) & 1023, int(16u) >> 12), 0)[int(16u) & 3], _94 * texelFetch(c4, ivec2((int(20u) >> 2) & 1023, int(20u) >> 12), 0)[int(20u) & 3])));\n"
	 "    gl_Position.y = fma(_142, texelFetch(c4, ivec2((int(29u) >> 2) & 1023, int(29u) >> 12), 0)[int(29u) & 3], fma(_122, texelFetch(c4, ivec2((int(25u) >> 2) & 1023, int(25u) >> 12), 0)[int(25u) & 3], fma(_102, texelFetch(c4, ivec2((int(17u) >> 2) & 1023, int(17u) >> 12), 0)[int(17u) & 3], _94 * texelFetch(c4, ivec2((int(21u) >> 2) & 1023, int(21u) >> 12), 0)[int(21u) & 3])));\n"
	 "    gl_Position.z = fma(_142, texelFetch(c4, ivec2((int(30u) >> 2) & 1023, int(30u) >> 12), 0)[int(30u) & 3], fma(_122, texelFetch(c4, ivec2((int(26u) >> 2) & 1023, int(26u) >> 12), 0)[int(26u) & 3], fma(_102, texelFetch(c4, ivec2((int(18u) >> 2) & 1023, int(18u) >> 12), 0)[int(18u) & 3], _94 * texelFetch(c4, ivec2((int(22u) >> 2) & 1023, int(22u) >> 12), 0)[int(22u) & 3])));\n"
	 "    gl_Position.w = fma(_142, texelFetch(c4, ivec2((int(31u) >> 2) & 1023, int(31u) >> 12), 0)[int(31u) & 3], fma(_122, texelFetch(c4, ivec2((int(27u) >> 2) & 1023, int(27u) >> 12), 0)[int(27u) & 3], fma(_102, texelFetch(c4, ivec2((int(19u) >> 2) & 1023, int(19u) >> 12), 0)[int(19u) & 3], _94 * texelFetch(c4, ivec2((int(23u) >> 2) & 1023, int(23u) >> 12), 0)[int(23u) & 3])));\n"
	 "}\n"
	 "", 0},
	/* 12 dump-6a930d0e vertex */
	{"", "\n"
	 "#version 310 es\n"
	 "precision highp float;\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "uniform highp sampler2D c4;\n"
	 "\n"
	 "layout(location = 0) in vec4 in_attr0;\n"
	 "layout(location = 1) in vec4 in_attr1;\n"
	 "layout(location = 2) in vec4 in_attr2;\n"
	 "out vec4 varying_0;\n"
	 "out vec4 varying_1;\n"
	 "out vec4 varying_2;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_0 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_1 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_2 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_1.z = in_attr0.z;\n"
	 "    varying_1.y = in_attr0.y;\n"
	 "    varying_2.x = fma(in_attr2.x, texelFetch(c4, ivec2((int(36u) >> 2) & 1023, int(36u) >> 12), 0)[int(36u) & 3], texelFetch(c4, ivec2((int(38u) >> 2) & 1023, int(38u) >> 12), 0)[int(38u) & 3]);\n"
	 "    varying_1.x = in_attr0.x;\n"
	 "    varying_1.w = in_attr0.w;\n"
	 "    float _117 = fma(in_attr0.z, texelFetch(c4, ivec2((int(9u) >> 2) & 1023, int(9u) >> 12), 0)[int(9u) & 3], fma(in_attr0.x, texelFetch(c4, ivec2((int(1u) >> 2) & 1023, int(1u) >> 12), 0)[int(1u) & 3], in_attr0.y * texelFetch(c4, ivec2((int(5u) >> 2) & 1023, int(5u) >> 12), 0)[int(5u) & 3])) + texelFetch(c4, ivec2((int(13u) >> 2) & 1023, int(13u) >> 12), 0)[int(13u) & 3];\n"
	 "    varying_2.y = fma(in_attr2.y, texelFetch(c4, ivec2((int(37u) >> 2) & 1023, int(37u) >> 12), 0)[int(37u) & 3], texelFetch(c4, ivec2((int(39u) >> 2) & 1023, int(39u) >> 12), 0)[int(39u) & 3]);\n"
	 "    varying_0.x = in_attr1.x * texelFetch(c4, ivec2((int(32u) >> 2) & 1023, int(32u) >> 12), 0)[int(32u) & 3];\n"
	 "    varying_0.z = in_attr1.z * texelFetch(c4, ivec2((int(34u) >> 2) & 1023, int(34u) >> 12), 0)[int(34u) & 3];\n"
	 "    float _163 = fma(in_attr0.z, texelFetch(c4, ivec2((int(8u) >> 2) & 1023, int(8u) >> 12), 0)[int(8u) & 3], fma(in_attr0.x, texelFetch(c4, ivec2((int(0u) >> 2) & 1023, int(0u) >> 12), 0)[int(0u) & 3], in_attr0.y * texelFetch(c4, ivec2((int(4u) >> 2) & 1023, int(4u) >> 12), 0)[int(4u) & 3])) + texelFetch(c4, ivec2((int(12u) >> 2) & 1023, int(12u) >> 12), 0)[int(12u) & 3];\n"
	 "    float _171 = fma(in_attr0.z, texelFetch(c4, ivec2((int(10u) >> 2) & 1023, int(10u) >> 12), 0)[int(10u) & 3], fma(in_attr0.x, texelFetch(c4, ivec2((int(2u) >> 2) & 1023, int(2u) >> 12), 0)[int(2u) & 3], in_attr0.y * texelFetch(c4, ivec2((int(6u) >> 2) & 1023, int(6u) >> 12), 0)[int(6u) & 3])) + texelFetch(c4, ivec2((int(14u) >> 2) & 1023, int(14u) >> 12), 0)[int(14u) & 3];\n"
	 "    float _175 = fma(in_attr0.z, texelFetch(c4, ivec2((int(11u) >> 2) & 1023, int(11u) >> 12), 0)[int(11u) & 3], fma(in_attr0.x, texelFetch(c4, ivec2((int(3u) >> 2) & 1023, int(3u) >> 12), 0)[int(3u) & 3], in_attr0.y * texelFetch(c4, ivec2((int(7u) >> 2) & 1023, int(7u) >> 12), 0)[int(7u) & 3])) + texelFetch(c4, ivec2((int(15u) >> 2) & 1023, int(15u) >> 12), 0)[int(15u) & 3];\n"
	 "    varying_0.y = in_attr1.y * texelFetch(c4, ivec2((int(33u) >> 2) & 1023, int(33u) >> 12), 0)[int(33u) & 3];\n"
	 "    varying_0.w = in_attr1.w * texelFetch(c4, ivec2((int(35u) >> 2) & 1023, int(35u) >> 12), 0)[int(35u) & 3];\n"
	 "    gl_Position.x = fma(_175, texelFetch(c4, ivec2((int(28u) >> 2) & 1023, int(28u) >> 12), 0)[int(28u) & 3], fma(_171, texelFetch(c4, ivec2((int(24u) >> 2) & 1023, int(24u) >> 12), 0)[int(24u) & 3], fma(_163, texelFetch(c4, ivec2((int(16u) >> 2) & 1023, int(16u) >> 12), 0)[int(16u) & 3], _117 * texelFetch(c4, ivec2((int(20u) >> 2) & 1023, int(20u) >> 12), 0)[int(20u) & 3])));\n"
	 "    gl_Position.y = fma(_175, texelFetch(c4, ivec2((int(29u) >> 2) & 1023, int(29u) >> 12), 0)[int(29u) & 3], fma(_171, texelFetch(c4, ivec2((int(25u) >> 2) & 1023, int(25u) >> 12), 0)[int(25u) & 3], fma(_163, texelFetch(c4, ivec2((int(17u) >> 2) & 1023, int(17u) >> 12), 0)[int(17u) & 3], _117 * texelFetch(c4, ivec2((int(21u) >> 2) & 1023, int(21u) >> 12), 0)[int(21u) & 3])));\n"
	 "    gl_Position.z = fma(_175, texelFetch(c4, ivec2((int(30u) >> 2) & 1023, int(30u) >> 12), 0)[int(30u) & 3], fma(_171, texelFetch(c4, ivec2((int(26u) >> 2) & 1023, int(26u) >> 12), 0)[int(26u) & 3], fma(_163, texelFetch(c4, ivec2((int(18u) >> 2) & 1023, int(18u) >> 12), 0)[int(18u) & 3], _117 * texelFetch(c4, ivec2((int(22u) >> 2) & 1023, int(22u) >> 12), 0)[int(22u) & 3])));\n"
	 "    gl_Position.w = fma(_175, texelFetch(c4, ivec2((int(31u) >> 2) & 1023, int(31u) >> 12), 0)[int(31u) & 3], fma(_171, texelFetch(c4, ivec2((int(27u) >> 2) & 1023, int(27u) >> 12), 0)[int(27u) & 3], fma(_163, texelFetch(c4, ivec2((int(19u) >> 2) & 1023, int(19u) >> 12), 0)[int(19u) & 3], _117 * texelFetch(c4, ivec2((int(23u) >> 2) & 1023, int(23u) >> 12), 0)[int(23u) & 3])));\n"
	 "}\n"
	 "", 0},
	/* 13 dump-7227c812 fragment */
	{"", "\n"
	 "#version 310 es\n"
	 "precision highp int;\n"
	 "precision mediump float;\n"
	 "#define unpackFloat2x16(a) unpackHalf2x16(a)\n"
	 "#define packFloat2x16(a) packHalf2x16(a)\n"
	 "#if defined(GL_AMD_gpu_shader_half_float)\n"
	 "#elif defined(GL_EXT_shader_explicit_arithmetic_types_float16)\n"
	 "#else\n"
	 "\n"
	 "#endif\n"
	 "\n"
	 " uniform sampler2D fs_tex0_20;\n"
	 "\n"
	 "in vec4 varying_0;\n"
	 "in vec4 varying_1;\n"
	 "layout(location = 0) out vec4 frag_color0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    mediump vec4 _49 = texture(fs_tex0_20, vec2(varying_1.x, varying_1.y));\n"
	 "    uint _56 = packHalf2x16(vec2(_49.xy));\n"
	 "    uint _58 = packHalf2x16(vec2(_49.zw));\n"
	 "    float _73 = float(float(unpackFloat2x16(_56).x) * varying_0.x);\n"
	 "    vec2 _75 = unpackFloat2x16(_56);\n"
	 "    _75.x = _73;\n"
	 "    float _81 = float(float(float(unpackFloat2x16(_58).y) * varying_0.w));\n"
	 "    frag_color0.x = float(float(_81 * float(_73)));\n"
	 "    frag_color0.y = float(float(_81 * float(float(float(_75.y) * varying_0.y))));\n"
	 "    frag_color0.z = float(float(_81 * float(float(float(unpackFloat2x16(_58).x) * varying_0.z))));\n"
	 "    frag_color0.w = _81;\n"
	 "}\n"
	 "", 1},
	/* 14 dump-800121db fragment */
	{"", "\n"
	 "#version 310 es\n"
	 "precision mediump float;\n"
	 "uniform highp sampler2D c3;\n"
	 "\n"
	 " uniform sampler2D fs_tex0_20;\n"
	 "\n"
	 "in vec4 varying_0;\n"
	 "in vec4 varying_2;\n"
	 "layout(location = 0) out vec4 frag_color0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    vec4 _51 = texture(fs_tex0_20, vec2(varying_2.x, varying_2.y));\n"
	 "    frag_color0.x = (_51.x + texelFetch(c3, ivec2((int(0u) >> 2) & 1023, int(0u) >> 12), 0)[int(0u) & 3]) * varying_0.x;\n"
	 "    frag_color0.y = (_51.y + texelFetch(c3, ivec2((int(1u) >> 2) & 1023, int(1u) >> 12), 0)[int(1u) & 3]) * varying_0.y;\n"
	 "    frag_color0.z = (_51.z + texelFetch(c3, ivec2((int(2u) >> 2) & 1023, int(2u) >> 12), 0)[int(2u) & 3]) * varying_0.z;\n"
	 "    frag_color0.w = (_51.w + texelFetch(c3, ivec2((int(3u) >> 2) & 1023, int(3u) >> 12), 0)[int(3u) & 3]) * varying_0.w;\n"
	 "}\n"
	 "", 1},
	/* 15 dump-815bc387 fragment */
	{"", "\n"
	 "#version 310 es\n"
	 "precision mediump float;\n"
	 "layout(location = 0) out vec4 frag_color0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    frag_color0.x = 1.0;\n"
	 "    frag_color0.y = 0.0;\n"
	 "    frag_color0.z = 1.0;\n"
	 "    frag_color0.w = 1.0;\n"
	 "}\n"
	 "", 1},
	/* 16 dump-8af77a17 vertex */
	{"", "\n"
	 "#version 310 es\n"
	 "precision highp float;\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "\n"
	 "\n"
	 " uniform highp sampler2D c4_1;\n"
	 "\n"
	 "layout(location = 0) in vec4 in_attr0;\n"
	 "layout(location = 1) in vec4 in_attr1;\n"
	 "layout(location = 2) in vec4 in_attr2;\n"
	 "layout(location = 3) in vec4 in_attr3;\n"
	 "out vec4 varying_0;\n"
	 "out vec4 varying_1;\n"
	 "out vec4 varying_2;\n"
	 "out vec4 varying_3;\n"
	 "out vec4 varying_4;\n"
	 "out vec4 varying_5;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_0 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_1 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_2 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_3 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_4 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_5 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    float _93 = fma(in_attr1.z, texelFetch(c4_1, ivec2((int(46u) >> 2) & 1023, int(46u) >> 12), 0)[int(46u) & 3], fma(in_attr1.y, texelFetch(c4_1, ivec2((int(45u) >> 2) & 1023, int(45u) >> 12), 0)[int(45u) & 3], in_attr1.x * texelFetch(c4_1, ivec2((int(44u) >> 2) & 1023, int(44u) >> 12), 0)[int(44u) & 3]));\n"
	 "    float _101 = fma(in_attr1.z, texelFetch(c4_1, ivec2((int(50u) >> 2) & 1023, int(50u) >> 12), 0)[int(50u) & 3], fma(in_attr1.y, texelFetch(c4_1, ivec2((int(49u) >> 2) & 1023, int(49u) >> 12), 0)[int(49u) & 3], in_attr1.x * texelFetch(c4_1, ivec2((int(48u) >> 2) & 1023, int(48u) >> 12), 0)[int(48u) & 3]));\n"
	 "    float _106 = fma(in_attr1.z, texelFetch(c4_1, ivec2((int(54u) >> 2) & 1023, int(54u) >> 12), 0)[int(54u) & 3], fma(in_attr1.y, texelFetch(c4_1, ivec2((int(53u) >> 2) & 1023, int(53u) >> 12), 0)[int(53u) & 3], in_attr1.x * texelFetch(c4_1, ivec2((int(52u) >> 2) & 1023, int(52u) >> 12), 0)[int(52u) & 3]));\n"
	 "    float _110 = in_attr0.y * texelFetch(c4_1, ivec2((int(81u) >> 2) & 1023, int(81u) >> 12), 0)[int(81u) & 3];\n"
	 "    float _114 = in_attr0.x * texelFetch(c4_1, ivec2((int(80u) >> 2) & 1023, int(80u) >> 12), 0)[int(80u) & 3];\n"
	 "    float _125 = inversesqrt(fma(_106, _106, fma(_101, _101, _93 * _93)));\n"
	 "    float _145 = _93 * _125;\n"
	 "    float _146 = _101 * _125;\n"
	 "    float _147 = _106 * _125;\n"
	 "    float _169 = _145 * _146;\n"
	 "    float _170 = _146 * _147;\n"
	 "    float _171 = _145 * _147;\n"
	 "    float _178 = _147 * _147;\n"
	 "    float _248 = fma(_145, _145, -(_146 * _146));\n"
	 "    varying_0.y = fma(in_attr3.y, texelFetch(c4_1, ivec2((int(89u) >> 2) & 1023, int(89u) >> 12), 0)[int(89u) & 3], texelFetch(c4_1, ivec2((int(91u) >> 2) & 1023, int(91u) >> 12), 0)[int(91u) & 3]);\n"
	 "    varying_0.x = fma(in_attr3.x, texelFetch(c4_1, ivec2((int(88u) >> 2) & 1023, int(88u) >> 12), 0)[int(88u) & 3], texelFetch(c4_1, ivec2((int(90u) >> 2) & 1023, int(90u) >> 12), 0)[int(90u) & 3]);\n"
	 "    varying_1.x = _145;\n"
	 "    varying_1.y = _146;\n"
	 "    varying_1.z = _147;\n"
	 "    varying_5.w = 0.0;\n"
	 "    float _317 = fma(in_attr0.z, texelFetch(c4_1, ivec2((int(37u) >> 2) & 1023, int(37u) >> 12), 0)[int(37u) & 3], fma(_114, texelFetch(c4_1, ivec2((int(29u) >> 2) & 1023, int(29u) >> 12), 0)[int(29u) & 3], _110 * texelFetch(c4_1, ivec2((int(33u) >> 2) & 1023, int(33u) >> 12), 0)[int(33u) & 3])) + texelFetch(c4_1, ivec2((int(41u) >> 2) & 1023, int(41u) >> 12), 0)[int(41u) & 3];\n"
	 "    varying_2.y = _317;\n"
	 "    float _330 = fma(in_attr0.z, texelFetch(c4_1, ivec2((int(36u) >> 2) & 1023, int(36u) >> 12), 0)[int(36u) & 3], fma(_114, texelFetch(c4_1, ivec2((int(28u) >> 2) & 1023, int(28u) >> 12), 0)[int(28u) & 3], _110 * texelFetch(c4_1, ivec2((int(32u) >> 2) & 1023, int(32u) >> 12), 0)[int(32u) & 3])) + texelFetch(c4_1, ivec2((int(40u) >> 2) & 1023, int(40u) >> 12), 0)[int(40u) & 3];\n"
	 "    varying_2.x = _330;\n"
	 "    varying_3.z = (in_attr2.z * texelFetch(c4_1, ivec2((int(86u) >> 2) & 1023, int(86u) >> 12), 0)[int(86u) & 3]) * texelFetch(c4_1, ivec2((int(78u) >> 2) & 1023, int(78u) >> 12), 0)[int(78u) & 3];\n"
	 "    varying_3.y = (in_attr2.y * texelFetch(c4_1, ivec2((int(85u) >> 2) & 1023, int(85u) >> 12), 0)[int(85u) & 3]) * texelFetch(c4_1, ivec2((int(77u) >> 2) & 1023, int(77u) >> 12), 0)[int(77u) & 3];\n"
	 "    varying_3.w = (in_attr2.w * texelFetch(c4_1, ivec2((int(87u) >> 2) & 1023, int(87u) >> 12), 0)[int(87u) & 3]) * texelFetch(c4_1, ivec2((int(79u) >> 2) & 1023, int(79u) >> 12), 0)[int(79u) & 3];\n"
	 "    float _380 = fma(in_attr0.z, texelFetch(c4_1, ivec2((int(38u) >> 2) & 1023, int(38u) >> 12), 0)[int(38u) & 3], fma(_114, texelFetch(c4_1, ivec2((int(30u) >> 2) & 1023, int(30u) >> 12), 0)[int(30u) & 3], _110 * texelFetch(c4_1, ivec2((int(34u) >> 2) & 1023, int(34u) >> 12), 0)[int(34u) & 3])) + texelFetch(c4_1, ivec2((int(42u) >> 2) & 1023, int(42u) >> 12), 0)[int(42u) & 3];\n"
	 "    varying_2.z = _380;\n"
	 "    float _405 = fma(in_attr0.z, texelFetch(c4_1, ivec2((int(39u) >> 2) & 1023, int(39u) >> 12), 0)[int(39u) & 3], fma(_114, texelFetch(c4_1, ivec2((int(31u) >> 2) & 1023, int(31u) >> 12), 0)[int(31u) & 3], _110 * texelFetch(c4_1, ivec2((int(35u) >> 2) & 1023, int(35u) >> 12), 0)[int(35u) & 3])) + texelFetch(c4_1, ivec2((int(43u) >> 2) & 1023, int(43u) >> 12), 0)[int(43u) & 3];\n"
	 "    varying_3.x = (in_attr2.x * texelFetch(c4_1, ivec2((int(84u) >> 2) & 1023, int(84u) >> 12), 0)[int(84u) & 3]) * texelFetch(c4_1, ivec2((int(76u) >> 2) & 1023, int(76u) >> 12), 0)[int(76u) & 3];\n"
	 "    gl_Position.x = fma(_405, texelFetch(c4_1, ivec2((int(72u) >> 2) & 1023, int(72u) >> 12), 0)[int(72u) & 3], fma(_380, texelFetch(c4_1, ivec2((int(68u) >> 2) & 1023, int(68u) >> 12), 0)[int(68u) & 3], fma(_330, texelFetch(c4_1, ivec2((int(60u) >> 2) & 1023, int(60u) >> 12), 0)[int(60u) & 3], _317 * texelFetch(c4_1, ivec2((int(64u) >> 2) & 1023, int(64u) >> 12), 0)[int(64u) & 3])));\n"
	 "    gl_Position.y = fma(_405, texelFetch(c4_1, ivec2((int(73u) >> 2) & 1023, int(73u) >> 12), 0)[int(73u) & 3], fma(_380, texelFetch(c4_1, ivec2((int(69u) >> 2) & 1023, int(69u) >> 12), 0)[int(69u) & 3], fma(_330, texelFetch(c4_1, ivec2((int(61u) >> 2) & 1023, int(61u) >> 12), 0)[int(61u) & 3], _317 * texelFetch(c4_1, ivec2((int(65u) >> 2) & 1023, int(65u) >> 12), 0)[int(65u) & 3])));\n"
	 "    gl_Position.z = fma(_405, texelFetch(c4_1, ivec2((int(74u) >> 2) & 1023, int(74u) >> 12), 0)[int(74u) & 3], fma(_380, texelFetch(c4_1, ivec2((int(70u) >> 2) & 1023, int(70u) >> 12), 0)[int(70u) & 3], fma(_330, texelFetch(c4_1, ivec2((int(62u) >> 2) & 1023, int(62u) >> 12), 0)[int(62u) & 3], _317 * texelFetch(c4_1, ivec2((int(66u) >> 2) & 1023, int(66u) >> 12), 0)[int(66u) & 3])));\n"
	 "    gl_Position.w = fma(_405, texelFetch(c4_1, ivec2((int(75u) >> 2) & 1023, int(75u) >> 12), 0)[int(75u) & 3], fma(_380, texelFetch(c4_1, ivec2((int(71u) >> 2) & 1023, int(71u) >> 12), 0)[int(71u) & 3], fma(_330, texelFetch(c4_1, ivec2((int(63u) >> 2) & 1023, int(63u) >> 12), 0)[int(63u) & 3], _317 * texelFetch(c4_1, ivec2((int(67u) >> 2) & 1023, int(67u) >> 12), 0)[int(67u) & 3])));\n"
	 "    varying_4.x = max(0.0, fma(exp2(log2(max(0.0, fma(_248, texelFetch(c4_1, ivec2((int(24u) >> 2) & 1023, int(24u) >> 12), 0)[int(24u) & 3], fma(_171, texelFetch(c4_1, ivec2((int(15u) >> 2) & 1023, int(15u) >> 12), 0)[int(15u) & 3], fma(_178, texelFetch(c4_1, ivec2((int(14u) >> 2) & 1023, int(14u) >> 12), 0)[int(14u) & 3], fma(_170, texelFetch(c4_1, ivec2((int(13u) >> 2) & 1023, int(13u) >> 12), 0)[int(13u) & 3], _169 * texelFetch(c4_1, ivec2((int(12u) >> 2) & 1023, int(12u) >> 12), 0)[int(12u) & 3])))) + (fma(_147, texelFetch(c4_1, ivec2((int(2u) >> 2) & 1023, int(2u) >> 12), 0)[int(2u) & 3], fma(_146, texelFetch(c4_1, ivec2((int(1u) >> 2) & 1023, int(1u) >> 12), 0)[int(1u) & 3], _145 * texelFetch(c4_1, ivec2((int(0u) >> 2) & 1023, int(0u) >> 12), 0)[int(0u) & 3])) + texelFetch(c4_1, ivec2((int(3u) >> 2) & 1023, int(3u) >> 12), 0)[int(3u) & 3]))) * 0.4166666567325592041015625), uintBitsToFloat(0x3f870a3du), -0.054999999701976776123046875));\n"
	 "    varying_4.y = max(0.0, fma(exp2(log2(max(0.0, fma(_248, texelFetch(c4_1, ivec2((int(25u) >> 2) & 1023, int(25u) >> 12), 0)[int(25u) & 3], fma(_171, texelFetch(c4_1, ivec2((int(19u) >> 2) & 1023, int(19u) >> 12), 0)[int(19u) & 3], fma(_178, texelFetch(c4_1, ivec2((int(18u) >> 2) & 1023, int(18u) >> 12), 0)[int(18u) & 3], fma(_170, texelFetch(c4_1, ivec2((int(17u) >> 2) & 1023, int(17u) >> 12), 0)[int(17u) & 3], _169 * texelFetch(c4_1, ivec2((int(16u) >> 2) & 1023, int(16u) >> 12), 0)[int(16u) & 3])))) + (fma(_147, texelFetch(c4_1, ivec2((int(6u) >> 2) & 1023, int(6u) >> 12), 0)[int(6u) & 3], fma(_146, texelFetch(c4_1, ivec2((int(5u) >> 2) & 1023, int(5u) >> 12), 0)[int(5u) & 3], _145 * texelFetch(c4_1, ivec2((int(4u) >> 2) & 1023, int(4u) >> 12), 0)[int(4u) & 3])) + texelFetch(c4_1, ivec2((int(7u) >> 2) & 1023, int(7u) >> 12), 0)[int(7u) & 3]))) * 0.4166666567325592041015625), uintBitsToFloat(0x3f870a3du), -0.054999999701976776123046875));\n"
	 "    varying_4.z = max(0.0, fma(exp2(log2(max(0.0, fma(_248, texelFetch(c4_1, ivec2((int(26u) >> 2) & 1023, int(26u) >> 12), 0)[int(26u) & 3], fma(_171, texelFetch(c4_1, ivec2((int(23u) >> 2) & 1023, int(23u) >> 12), 0)[int(23u) & 3], fma(_178, texelFetch(c4_1, ivec2((int(22u) >> 2) & 1023, int(22u) >> 12), 0)[int(22u) & 3], fma(_170, texelFetch(c4_1, ivec2((int(21u) >> 2) & 1023, int(21u) >> 12), 0)[int(21u) & 3], _169 * texelFetch(c4_1, ivec2((int(20u) >> 2) & 1023, int(20u) >> 12), 0)[int(20u) & 3])))) + (fma(_147, texelFetch(c4_1, ivec2((int(10u) >> 2) & 1023, int(10u) >> 12), 0)[int(10u) & 3], fma(_146, texelFetch(c4_1, ivec2((int(9u) >> 2) & 1023, int(9u) >> 12), 0)[int(9u) & 3], _145 * texelFetch(c4_1, ivec2((int(8u) >> 2) & 1023, int(8u) >> 12), 0)[int(8u) & 3])) + texelFetch(c4_1, ivec2((int(11u) >> 2) & 1023, int(11u) >> 12), 0)[int(11u) & 3]))) * 0.4166666567325592041015625), uintBitsToFloat(0x3f870a3du), -0.054999999701976776123046875));\n"
	 "}\n"
	 "", 0},
	/* 17 dump-b5d846ce vertex */
	{"", "\n"
	 "#version 310 es\n"
	 "precision highp float;\n"
	 "#define unpackFloat2x16(a) unpackHalf2x16(a)\n"
	 "#define packFloat2x16(a) packHalf2x16(a)\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "#if defined(GL_AMD_gpu_shader_half_float)\n"
	 "#elif defined(GL_EXT_shader_explicit_arithmetic_types_float16)\n"
	 "#else\n"
	 "\n"
	 "#endif\n"
	 "\n"
	 " uniform highp sampler2D c3;\n"
	 "\n"
	 "layout(location = 0) in vec4 in_attr0;\n"
	 "layout(location = 1) in vec4 in_attr1;\n"
	 "out vec4 varying_0;\n"
	 "out vec4 varying_1;\n"
	 "out vec4 varying_2;\n"
	 "out vec4 varying_3;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_0 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_1 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_2 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_3 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_0.x = fma(in_attr1.x, texelFetch(c3, ivec2((int(32u) >> 2) & 1023, int(32u) >> 12), 0)[int(32u) & 3], texelFetch(c3, ivec2((int(34u) >> 2) & 1023, int(34u) >> 12), 0)[int(34u) & 3]);\n"
	 "    varying_1.x = fma(float(float(in_attr1.x + float(unpackFloat2x16(0u).x))), texelFetch(c3, ivec2((int(32u) >> 2) & 1023, int(32u) >> 12), 0)[int(32u) & 3], texelFetch(c3, ivec2((int(34u) >> 2) & 1023, int(34u) >> 12), 0)[int(34u) & 3]);\n"
	 "    float _138 = fma(in_attr0.z, texelFetch(c3, ivec2((int(9u) >> 2) & 1023, int(9u) >> 12), 0)[int(9u) & 3], fma(in_attr0.x, texelFetch(c3, ivec2((int(1u) >> 2) & 1023, int(1u) >> 12), 0)[int(1u) & 3], in_attr0.y * texelFetch(c3, ivec2((int(5u) >> 2) & 1023, int(5u) >> 12), 0)[int(5u) & 3])) + texelFetch(c3, ivec2((int(13u) >> 2) & 1023, int(13u) >> 12), 0)[int(13u) & 3];\n"
	 "    varying_0.y = fma(in_attr1.y, texelFetch(c3, ivec2((int(33u) >> 2) & 1023, int(33u) >> 12), 0)[int(33u) & 3], texelFetch(c3, ivec2((int(35u) >> 2) & 1023, int(35u) >> 12), 0)[int(35u) & 3]);\n"
	 "    float _151 = fma(float(float(in_attr1.x + float(unpackFloat2x16(1006648320u).x))), texelFetch(c3, ivec2((int(32u) >> 2) & 1023, int(32u) >> 12), 0)[int(32u) & 3], texelFetch(c3, ivec2((int(34u) >> 2) & 1023, int(34u) >> 12), 0)[int(34u) & 3]);\n"
	 "    float _156 = fma(float(float(in_attr1.y + float(unpackFloat2x16(1006648320u).x))), texelFetch(c3, ivec2((int(33u) >> 2) & 1023, int(33u) >> 12), 0)[int(33u) & 3], texelFetch(c3, ivec2((int(35u) >> 2) & 1023, int(35u) >> 12), 0)[int(35u) & 3]);\n"
	 "    varying_2.x = _151;\n"
	 "    varying_3.x = _151;\n"
	 "    varying_2.y = fma(float(float(in_attr1.y + float(unpackFloat2x16(0u).x))), texelFetch(c3, ivec2((int(33u) >> 2) & 1023, int(33u) >> 12), 0)[int(33u) & 3], texelFetch(c3, ivec2((int(35u) >> 2) & 1023, int(35u) >> 12), 0)[int(35u) & 3]);\n"
	 "    varying_1.y = _156;\n"
	 "    varying_3.y = _156;\n"
	 "    float _190 = fma(in_attr0.z, texelFetch(c3, ivec2((int(8u) >> 2) & 1023, int(8u) >> 12), 0)[int(8u) & 3], fma(in_attr0.x, texelFetch(c3, ivec2((int(0u) >> 2) & 1023, int(0u) >> 12), 0)[int(0u) & 3], in_attr0.y * texelFetch(c3, ivec2((int(4u) >> 2) & 1023, int(4u) >> 12), 0)[int(4u) & 3])) + texelFetch(c3, ivec2((int(12u) >> 2) & 1023, int(12u) >> 12), 0)[int(12u) & 3];\n"
	 "    float _202 = fma(in_attr0.z, texelFetch(c3, ivec2((int(10u) >> 2) & 1023, int(10u) >> 12), 0)[int(10u) & 3], fma(in_attr0.x, texelFetch(c3, ivec2((int(2u) >> 2) & 1023, int(2u) >> 12), 0)[int(2u) & 3], in_attr0.y * texelFetch(c3, ivec2((int(6u) >> 2) & 1023, int(6u) >> 12), 0)[int(6u) & 3])) + texelFetch(c3, ivec2((int(14u) >> 2) & 1023, int(14u) >> 12), 0)[int(14u) & 3];\n"
	 "    float _222 = fma(in_attr0.z, texelFetch(c3, ivec2((int(11u) >> 2) & 1023, int(11u) >> 12), 0)[int(11u) & 3], fma(in_attr0.x, texelFetch(c3, ivec2((int(3u) >> 2) & 1023, int(3u) >> 12), 0)[int(3u) & 3], in_attr0.y * texelFetch(c3, ivec2((int(7u) >> 2) & 1023, int(7u) >> 12), 0)[int(7u) & 3])) + texelFetch(c3, ivec2((int(15u) >> 2) & 1023, int(15u) >> 12), 0)[int(15u) & 3];\n"
	 "    gl_Position.x = fma(_222, texelFetch(c3, ivec2((int(28u) >> 2) & 1023, int(28u) >> 12), 0)[int(28u) & 3], fma(_202, texelFetch(c3, ivec2((int(24u) >> 2) & 1023, int(24u) >> 12), 0)[int(24u) & 3], fma(_190, texelFetch(c3, ivec2((int(16u) >> 2) & 1023, int(16u) >> 12), 0)[int(16u) & 3], _138 * texelFetch(c3, ivec2((int(20u) >> 2) & 1023, int(20u) >> 12), 0)[int(20u) & 3])));\n"
	 "    gl_Position.y = fma(_222, texelFetch(c3, ivec2((int(29u) >> 2) & 1023, int(29u) >> 12), 0)[int(29u) & 3], fma(_202, texelFetch(c3, ivec2((int(25u) >> 2) & 1023, int(25u) >> 12), 0)[int(25u) & 3], fma(_190, texelFetch(c3, ivec2((int(17u) >> 2) & 1023, int(17u) >> 12), 0)[int(17u) & 3], _138 * texelFetch(c3, ivec2((int(21u) >> 2) & 1023, int(21u) >> 12), 0)[int(21u) & 3])));\n"
	 "    gl_Position.z = fma(_222, texelFetch(c3, ivec2((int(30u) >> 2) & 1023, int(30u) >> 12), 0)[int(30u) & 3], fma(_202, texelFetch(c3, ivec2((int(26u) >> 2) & 1023, int(26u) >> 12), 0)[int(26u) & 3], fma(_190, texelFetch(c3, ivec2((int(18u) >> 2) & 1023, int(18u) >> 12), 0)[int(18u) & 3], _138 * texelFetch(c3, ivec2((int(22u) >> 2) & 1023, int(22u) >> 12), 0)[int(22u) & 3])));\n"
	 "    gl_Position.w = fma(_222, texelFetch(c3, ivec2((int(31u) >> 2) & 1023, int(31u) >> 12), 0)[int(31u) & 3], fma(_202, texelFetch(c3, ivec2((int(27u) >> 2) & 1023, int(27u) >> 12), 0)[int(27u) & 3], fma(_190, texelFetch(c3, ivec2((int(19u) >> 2) & 1023, int(19u) >> 12), 0)[int(19u) & 3], _138 * texelFetch(c3, ivec2((int(23u) >> 2) & 1023, int(23u) >> 12), 0)[int(23u) & 3])));\n"
	 "}\n"
	 "", 0},
	/* 18 dump-b894e79b vertex */
	{"", "\n"
	 "#version 310 es\n"
	 "precision highp float;\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "uniform highp sampler2D c4;\n"
	 "\n"
	 "layout(location = 0) in vec4 in_attr0;\n"
	 "layout(location = 1) in vec4 in_attr1;\n"
	 "layout(location = 2) in vec4 in_attr2;\n"
	 "out vec4 varying_0;\n"
	 "out vec4 varying_1;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_0 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_1 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_0.x = in_attr1.x;\n"
	 "    varying_0.y = in_attr1.y;\n"
	 "    varying_0.z = in_attr1.z;\n"
	 "    float _110 = fma(in_attr0.z, texelFetch(c4, ivec2((int(9u) >> 2) & 1023, int(9u) >> 12), 0)[int(9u) & 3], fma(in_attr0.x, texelFetch(c4, ivec2((int(1u) >> 2) & 1023, int(1u) >> 12), 0)[int(1u) & 3], in_attr0.y * texelFetch(c4, ivec2((int(5u) >> 2) & 1023, int(5u) >> 12), 0)[int(5u) & 3])) + texelFetch(c4, ivec2((int(13u) >> 2) & 1023, int(13u) >> 12), 0)[int(13u) & 3];\n"
	 "    varying_0.w = in_attr1.w;\n"
	 "    varying_1.x = fma(in_attr2.x, texelFetch(c4, ivec2((int(32u) >> 2) & 1023, int(32u) >> 12), 0)[int(32u) & 3], texelFetch(c4, ivec2((int(34u) >> 2) & 1023, int(34u) >> 12), 0)[int(34u) & 3]);\n"
	 "    float _122 = fma(in_attr0.z, texelFetch(c4, ivec2((int(8u) >> 2) & 1023, int(8u) >> 12), 0)[int(8u) & 3], fma(in_attr0.x, texelFetch(c4, ivec2((int(0u) >> 2) & 1023, int(0u) >> 12), 0)[int(0u) & 3], in_attr0.y * texelFetch(c4, ivec2((int(4u) >> 2) & 1023, int(4u) >> 12), 0)[int(4u) & 3])) + texelFetch(c4, ivec2((int(12u) >> 2) & 1023, int(12u) >> 12), 0)[int(12u) & 3];\n"
	 "    float _154 = fma(in_attr0.z, texelFetch(c4, ivec2((int(10u) >> 2) & 1023, int(10u) >> 12), 0)[int(10u) & 3], fma(in_attr0.x, texelFetch(c4, ivec2((int(2u) >> 2) & 1023, int(2u) >> 12), 0)[int(2u) & 3], in_attr0.y * texelFetch(c4, ivec2((int(6u) >> 2) & 1023, int(6u) >> 12), 0)[int(6u) & 3])) + texelFetch(c4, ivec2((int(14u) >> 2) & 1023, int(14u) >> 12), 0)[int(14u) & 3];\n"
	 "    float _158 = fma(in_attr0.z, texelFetch(c4, ivec2((int(11u) >> 2) & 1023, int(11u) >> 12), 0)[int(11u) & 3], fma(in_attr0.x, texelFetch(c4, ivec2((int(3u) >> 2) & 1023, int(3u) >> 12), 0)[int(3u) & 3], in_attr0.y * texelFetch(c4, ivec2((int(7u) >> 2) & 1023, int(7u) >> 12), 0)[int(7u) & 3])) + texelFetch(c4, ivec2((int(15u) >> 2) & 1023, int(15u) >> 12), 0)[int(15u) & 3];\n"
	 "    varying_1.y = fma(in_attr2.y, texelFetch(c4, ivec2((int(33u) >> 2) & 1023, int(33u) >> 12), 0)[int(33u) & 3], texelFetch(c4, ivec2((int(35u) >> 2) & 1023, int(35u) >> 12), 0)[int(35u) & 3]);\n"
	 "    gl_Position.x = fma(_158, texelFetch(c4, ivec2((int(28u) >> 2) & 1023, int(28u) >> 12), 0)[int(28u) & 3], fma(_154, texelFetch(c4, ivec2((int(24u) >> 2) & 1023, int(24u) >> 12), 0)[int(24u) & 3], fma(_122, texelFetch(c4, ivec2((int(16u) >> 2) & 1023, int(16u) >> 12), 0)[int(16u) & 3], _110 * texelFetch(c4, ivec2((int(20u) >> 2) & 1023, int(20u) >> 12), 0)[int(20u) & 3])));\n"
	 "    gl_Position.y = fma(_158, texelFetch(c4, ivec2((int(29u) >> 2) & 1023, int(29u) >> 12), 0)[int(29u) & 3], fma(_154, texelFetch(c4, ivec2((int(25u) >> 2) & 1023, int(25u) >> 12), 0)[int(25u) & 3], fma(_122, texelFetch(c4, ivec2((int(17u) >> 2) & 1023, int(17u) >> 12), 0)[int(17u) & 3], _110 * texelFetch(c4, ivec2((int(21u) >> 2) & 1023, int(21u) >> 12), 0)[int(21u) & 3])));\n"
	 "    gl_Position.z = fma(_158, texelFetch(c4, ivec2((int(30u) >> 2) & 1023, int(30u) >> 12), 0)[int(30u) & 3], fma(_154, texelFetch(c4, ivec2((int(26u) >> 2) & 1023, int(26u) >> 12), 0)[int(26u) & 3], fma(_122, texelFetch(c4, ivec2((int(18u) >> 2) & 1023, int(18u) >> 12), 0)[int(18u) & 3], _110 * texelFetch(c4, ivec2((int(22u) >> 2) & 1023, int(22u) >> 12), 0)[int(22u) & 3])));\n"
	 "    gl_Position.w = fma(_158, texelFetch(c4, ivec2((int(31u) >> 2) & 1023, int(31u) >> 12), 0)[int(31u) & 3], fma(_154, texelFetch(c4, ivec2((int(27u) >> 2) & 1023, int(27u) >> 12), 0)[int(27u) & 3], fma(_122, texelFetch(c4, ivec2((int(19u) >> 2) & 1023, int(19u) >> 12), 0)[int(19u) & 3], _110 * texelFetch(c4, ivec2((int(23u) >> 2) & 1023, int(23u) >> 12), 0)[int(23u) & 3])));\n"
	 "}\n"
	 "", 0},
	/* 19 dump-c523448a fragment */
	{"", "\n"
	 "#version 310 es\n"
	 "/* GUARDED translation: runtime requires probe flag != 1.0 before every draw. */\n"
	 "precision highp int;\n"
	 "precision mediump float;\n"
	 "#define unpackFloat2x16(a) unpackHalf2x16(a)\n"
	 "#define packFloat2x16(a) packHalf2x16(a)\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "#if defined(GL_AMD_gpu_shader_half_float)\n"
	 "#elif defined(GL_EXT_shader_explicit_arithmetic_types_float16)\n"
	 "#else\n"
	 "\n"
	 "#endif\n"
	 "\n"
	 " uniform highp sampler2D c3;\n"
	 "\n"
	 " uniform sampler2D fs_tex0_20;\n"
	 " \n"
	 "\n"
	 "in vec4 varying_0;\n"
	 "in vec4 varying_1;\n"
	 "in vec4 varying_2;\n"
	 "in vec4 varying_3;\n"
	 "in vec4 varying_4;\n"
	 "layout(location = 0) out vec4 frag_color0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    mediump vec4 _72 = texture(fs_tex0_20, vec2(varying_0.x, varying_0.y));\n"
	 "    uint _79 = packHalf2x16(vec2(_72.xy));\n"
	 "    uint _81 = packHalf2x16(vec2(_72.zw));\n"
	 "    \n"
	 "    float _103 = float(float(unpackFloat2x16(_79).x) * varying_3.x);\n"
	 "    vec2 _105 = unpackFloat2x16(_79);\n"
	 "    _105.x = _103;\n"
	 "    float _109 = float(float(_105.y) * varying_3.y);\n"
	 "    vec2 _110 = _105;\n"
	 "    _110.y = _109;\n"
	 "    float _117 = float(float(float(unpackFloat2x16(_81).y) * varying_3.w));\n"
	 "    float _122 = float(float(unpackFloat2x16(_81).x) * varying_3.z);\n"
	 "    vec2 _124 = unpackFloat2x16(floatBitsToUint(varying_3.z));\n"
	 "    _124.x = _122;\n"
	 "    uint _257;\n"
	 "    uint _258;\n"
	 "    uint _259;\n"
	 "    uint _260;\n"
	 "    {\n"
	 "        _257 = packFloat2x16(_124);\n"
	 "        _258 = floatBitsToUint(varying_3.y);\n"
	 "        _259 = packFloat2x16(_110);\n"
	 "        _260 = _81;\n"
	 "    }\n"
	 "    uint _270;\n"
	 "    uint _271;\n"
	 "    uint _272;\n"
	 "    uint _273;\n"
	 "    {\n"
	 "        uint _269 = floatBitsToUint(float((-unpackFloat2x16(0u).x) + unpackFloat2x16(1006648320u).x));\n"
	 "        _270 = _269;\n"
	 "        _271 = _269;\n"
	 "        _272 = _269;\n"
	 "        _273 = _269;\n"
	 "    }\n"
	 "    float _300 = clamp(fma(uintBitsToFloat(_270), texelFetch(c3, ivec2((int(7u) >> 2) & 1023, int(7u) >> 12), 0)[int(7u) & 3], fma(uintBitsToFloat(_271), texelFetch(c3, ivec2((int(6u) >> 2) & 1023, int(6u) >> 12), 0)[int(6u) & 3], fma(uintBitsToFloat(_272), texelFetch(c3, ivec2((int(5u) >> 2) & 1023, int(5u) >> 12), 0)[int(5u) & 3], uintBitsToFloat(_273) * texelFetch(c3, ivec2((int(4u) >> 2) & 1023, int(4u) >> 12), 0)[int(4u) & 3]))), 0.0, 1.0);\n"
	 "    float _324 = max(0.0, fma(varying_1.z, texelFetch(c3, ivec2((int(2u) >> 2) & 1023, int(2u) >> 12), 0)[int(2u) & 3], fma(varying_1.y, texelFetch(c3, ivec2((int(1u) >> 2) & 1023, int(1u) >> 12), 0)[int(1u) & 3], varying_1.x * texelFetch(c3, ivec2((int(0u) >> 2) & 1023, int(0u) >> 12), 0)[int(0u) & 3])));\n"
	 "    frag_color0.x = float(float(fma(_300 * texelFetch(c3, ivec2((int(36u) >> 2) & 1023, int(36u) >> 12), 0)[int(36u) & 3], _324, varying_4.x)) * float(_117 * float(_103)));\n"
	 "    frag_color0.y = float(float(fma(_300 * texelFetch(c3, ivec2((int(37u) >> 2) & 1023, int(37u) >> 12), 0)[int(37u) & 3], _324, varying_4.y)) * float(_117 * float(_109)));\n"
	 "    frag_color0.z = float(float(fma(_300 * texelFetch(c3, ivec2((int(38u) >> 2) & 1023, int(38u) >> 12), 0)[int(38u) & 3], _324, varying_4.z)) * float(_117 * float(_122)));\n"
	 "    frag_color0.w = _117;\n"
	 "}\n"
	 "", 1},
	/* 20 dump-d032944a fragment */
	{"", "\n"
	 "#version 310 es\n"
	 "precision mediump float;\n"
	 "#define unpackFloat2x16(a) unpackHalf2x16(a)\n"
	 "#define packFloat2x16(a) packHalf2x16(a)\n"
	 "#if defined(GL_AMD_gpu_shader_half_float)\n"
	 "#elif defined(GL_EXT_shader_explicit_arithmetic_types_float16)\n"
	 "#else\n"
	 "\n"
	 "#endif\n"
	 "\n"
	 " \n"
	 "\n"
	 " uniform sampler2D fs_tex0_20;\n"
	 " uniform sampler3D fs_tex0_28;\n"
	 "\n"
	 "in vec4 varying_1;\n"
	 "in vec4 varying_3;\n"
	 "layout(location = 0) out vec4 frag_color0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    if (float(unpackFloat2x16(packHalf2x16(vec2(texture(fs_tex0_28, vec3(gl_FragCoord.x * 0.25, gl_FragCoord.y * 0.25, float(float(float(unpackFloat2x16(packHalf2x16(vec2(texture(fs_tex0_20, vec2(varying_1.x, varying_1.y)).w, 0.0))).x) * varying_3.w) * unpackFloat2x16(998259584u).x))).w, 0.0))).x) < uintBitsToFloat(0x3c23e000u))\n"
	 "    {\n"
	 "        demote;\n"
	 "    }\n"
	 "    frag_color0.x = 0.0;\n"
	 "    frag_color0.y = 0.0;\n"
	 "    frag_color0.z = 0.0;\n"
	 "    frag_color0.w = 0.0;\n"
	 "}\n"
	 "", 1},
	/* 21 dump-e4fb4243 fragment */
	{"", "\n"
	 "#version 310 es\n"
	 "precision highp int;\n"
	 "precision mediump float;\n"
	 "#define unpackFloat2x16(a) unpackHalf2x16(a)\n"
	 "#define packFloat2x16(a) packHalf2x16(a)\n"
	 "#if defined(GL_AMD_gpu_shader_half_float)\n"
	 "#elif defined(GL_EXT_shader_explicit_arithmetic_types_float16)\n"
	 "#else\n"
	 "\n"
	 "#endif\n"
	 "\n"
	 " uniform highp sampler2D c3;\n"
	 "\n"
	 " uniform sampler2D fs_tex0_20;\n"
	 "\n"
	 "in vec4 varying_0;\n"
	 "in vec4 varying_1;\n"
	 "layout(location = 0) out vec4 frag_color0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    mediump vec4 _55 = texture(fs_tex0_20, vec2(varying_1.x, varying_1.y));\n"
	 "    uint _62 = packHalf2x16(vec2(_55.xy));\n"
	 "    uint _64 = packHalf2x16(vec2(_55.zw));\n"
	 "    frag_color0.x = float(float((float(float(varying_0.x * float(unpackFloat2x16(1073758208u).x))) * texelFetch(c3, ivec2((int(0u) >> 2) & 1023, int(0u) >> 12), 0)[int(0u) & 3]) * float(unpackFloat2x16(_62).x)));\n"
	 "    frag_color0.y = float(float((float(float(varying_0.y * float(unpackFloat2x16(1073758208u).x))) * texelFetch(c3, ivec2((int(1u) >> 2) & 1023, int(1u) >> 12), 0)[int(1u) & 3]) * float(unpackFloat2x16(_62).y)));\n"
	 "    frag_color0.z = float(float((float(float(varying_0.z * float(unpackFloat2x16(1073758208u).x))) * texelFetch(c3, ivec2((int(2u) >> 2) & 1023, int(2u) >> 12), 0)[int(2u) & 3]) * float(unpackFloat2x16(_64).x)));\n"
	 "    frag_color0.w = float(float(clamp((float(float(varying_0.w * float(unpackFloat2x16(1073758208u).x))) * texelFetch(c3, ivec2((int(3u) >> 2) & 1023, int(3u) >> 12), 0)[int(3u) & 3]) * float(unpackFloat2x16(_64).y), 0.0, 1.0)));\n"
	 "}\n"
	 "", 1},
	/* 22 dump-e6091e72 fragment */
	{"", "\n"
	 "#version 310 es\n"
	 "precision mediump float;\n"
	 "#define unpackFloat2x16(a) unpackHalf2x16(a)\n"
	 "#define packFloat2x16(a) packHalf2x16(a)\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "#if defined(GL_AMD_gpu_shader_half_float)\n"
	 "#elif defined(GL_EXT_shader_explicit_arithmetic_types_float16)\n"
	 "#else\n"
	 "\n"
	 "#endif\n"
	 "\n"
	 " \n"
	 "\n"
	 " uniform highp sampler2D c3_1;\n"
	 "\n"
	 " uniform sampler2D fs_tex0_20;\n"
	 "\n"
	 "in vec4 varying_0;\n"
	 "layout(location = 0) out vec4 frag_color0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    vec4 _68 = texture(fs_tex0_20, vec2(fma(varying_0.x, texelFetch(c3_1, ivec2((int(0u) >> 2) & 1023, int(0u) >> 12), 0)[int(0u) & 3], texelFetch(c3_1, ivec2((int(2u) >> 2) & 1023, int(2u) >> 12), 0)[int(2u) & 3]), fma(varying_0.y, texelFetch(c3_1, ivec2((int(1u) >> 2) & 1023, int(1u) >> 12), 0)[int(1u) & 3], texelFetch(c3_1, ivec2((int(3u) >> 2) & 1023, int(3u) >> 12), 0)[int(3u) & 3])));\n"
	 "    float _72 = _68.w;\n"
	 "    float _86 = float(fma(_68.z, uintBitsToFloat(0x3d916000u), float(float(fma(_68.y, uintBitsToFloat(0x3f350000u), float(float(_68.x * uintBitsToFloat(0x3e614000u))))))));\n"
	 "    float _94 = float(fma(float(_72 * float(_86)), unpackFloat2x16(1073758208u).x, _86));\n"
	 "    frag_color0.x = _94;\n"
	 "    frag_color0.y = _94;\n"
	 "    frag_color0.z = _94;\n"
	 "    frag_color0.w = _72;\n"
	 "}\n"
	 "", 1},
	/* 23 dump-f3327347 fragment */
	{"", "\n"
	 "#version 310 es\n"
	 "precision mediump float;\n"
	 "uniform sampler2D fs_tex0_20;\n"
	 "\n"
	 "in vec4 varying_0;\n"
	 "in vec4 varying_1;\n"
	 "layout(location = 0) out vec4 frag_color0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    vec4 _45 = texture(fs_tex0_20, vec2(varying_1.x, varying_1.y));\n"
	 "    frag_color0.x = (_45.x * 2.0) * varying_0.x;\n"
	 "    frag_color0.y = (_45.y * 2.0) * varying_0.y;\n"
	 "    frag_color0.z = (_45.z * 2.0) * varying_0.z;\n"
	 "    frag_color0.w = (_45.w * 2.0) * varying_0.w;\n"
	 "}\n"
	 "", 1},
	/* 24 main-86cac8 vertex */
	{"", "\n"
	 "#version 310 es\n"
	 "precision highp float;\n"
	 "layout(location = 0) in vec4 in_attr0;\n"
	 "layout(location = 1) in vec4 in_attr1;\n"
	 "out vec4 varying_0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_0 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    gl_Position.x = in_attr0.x;\n"
	 "    gl_Position.y = in_attr0.y;\n"
	 "    varying_0.x = in_attr1.x;\n"
	 "    varying_0.y = in_attr1.y;\n"
	 "}\n"
	 "", 0},
	/* 25 main-86d688 vertex */
	{"", "\n"
	 "#version 310 es\n"
	 "precision highp float;\n"
	 "layout(location = 0) in vec4 in_attr0;\n"
	 "layout(location = 1) in vec4 in_attr1;\n"
	 "out vec4 varying_0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_0 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    gl_Position.x = in_attr0.x;\n"
	 "    gl_Position.y = in_attr0.y;\n"
	 "    varying_0.x = in_attr1.x;\n"
	 "    varying_0.y = in_attr1.y;\n"
	 "    gl_Layer = int(floatBitsToUint(uintBitsToFloat(uint(gl_InstanceIndex) - uint(gl_BaseInstanceARB))));\n"
	 "}\n"
	 "", 0},
	/* 26 main-86e248 fragment */
	{"", "\n"
	 "#version 310 es\n"
	 "precision mediump float;\n"
	 "out vec4 frag_color0;\n"
	 "/* TEST-ONLY substitute: NOT a translation (see the vertex stage note). */\n"
	 "uniform sampler2D fs_tex0_20;\n"
	 "in vec4 varying_1;\n"
	 "void main() { frag_color0 = texture(fs_tex0_20, varying_1.xy); }\n"
	 "", 1},
	/* 27 main-86ef08 fragment */
	{"", "\n"
	 "#version 310 es\n"
	 "precision mediump float;\n"
	 "out vec4 frag_color0;\n"
	 "/* TEST-ONLY substitute: NOT a translation (see the vertex stage note). */\n"
	 "uniform sampler2D fs_tex0_20;\n"
	 "in vec4 varying_1;\n"
	 "void main() { frag_color0 = texture(fs_tex0_20, varying_1.xy); }\n"
	 "", 1},
	/* 28 main-86fcc8 fragment */
	{"", "\n"
	 "#version 310 es\n"
	 "precision mediump float;\n"
	 "out vec4 frag_color0;\n"
	 "/* TEST-ONLY substitute: NOT a translation (see the vertex stage note). */\n"
	 "uniform sampler2D fs_tex0_20;\n"
	 "in vec4 varying_1;\n"
	 "void main() { frag_color0 = texture(fs_tex0_20, varying_1.xy); }\n"
	 "", 1},
	/* 29 main-870b88 fragment */
	{"", "\n"
	 "#version 310 es\n"
	 "precision mediump float;\n"
	 "out vec4 frag_color0;\n"
	 "/* TEST-ONLY substitute: NOT a translation (see the vertex stage note). */\n"
	 "uniform sampler2D fs_tex0_20;\n"
	 "in vec4 varying_1;\n"
	 "void main() { frag_color0 = texture(fs_tex0_20, varying_1.xy); }\n"
	 "", 1},
	/* 30 main-871848 fragment */
	{"", "\n"
	 "#version 310 es\n"
	 "precision mediump float;\n"
	 "out vec4 frag_color0;\n"
	 "/* TEST-ONLY substitute: NOT a translation (see the vertex stage note). */\n"
	 "uniform sampler2D fs_tex0_20;\n"
	 "in vec4 varying_1;\n"
	 "void main() { frag_color0 = texture(fs_tex0_20, varying_1.xy); }\n"
	 "", 1},
	/* 31 main-872608 fragment */
	{"", "\n"
	 "#version 310 es\n"
	 "precision mediump float;\n"
	 "out vec4 frag_color0;\n"
	 "/* TEST-ONLY substitute: NOT a translation (see the vertex stage note). */\n"
	 "uniform sampler2D fs_tex0_20;\n"
	 "in vec4 varying_1;\n"
	 "void main() { frag_color0 = texture(fs_tex0_20, varying_1.xy); }\n"
	 "", 1},
	/* 32 main-8734c8 vertex */
	{"", "\n"
	 "#version 310 es\n"
	 "precision highp float;\n"
	 "layout(location = 0) in vec4 in_attr0;\n"
	 "layout(location = 1) in vec4 in_attr1;\n"
	 "out vec4 varying_0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_0 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    gl_Position.x = in_attr0.x;\n"
	 "    gl_Position.y = in_attr0.y;\n"
	 "    varying_0.x = in_attr1.x;\n"
	 "    varying_0.y = in_attr1.y;\n"
	 "}\n"
	 "", 0},
	/* 33 main-874088 fragment */
	{"", "\n"
	 "#version 310 es\n"
	 "precision mediump float;\n"
	 "uniform sampler2D fs_tex0_20;\n"
	 "\n"
	 "in vec4 varying_0;\n"
	 "layout(location = 0) out vec4 frag_color0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    float _53 = 1.0 / gl_FragCoord.w;\n"
	 "    vec4 _58 = texture(fs_tex0_20, vec2(_53 * (varying_0.x * gl_FragCoord.w), _53 * (varying_0.y * gl_FragCoord.w)));\n"
	 "    frag_color0.x = _58.x;\n"
	 "    frag_color0.y = _58.y;\n"
	 "    frag_color0.z = _58.z;\n"
	 "    frag_color0.w = _58.w;\n"
	 "}\n"
	 "", 1},
	/* 34 dump-ef14df61 fragment */
	{"", "\n"
	 "#version 310 es\n"
	 "precision highp int;\n"
	 "precision mediump float;\n"
	 "#extension GL_EXT_scalar_block_layout : require\n"
	 "\n"
	 "uniform highp sampler2D c3;\n"
	 "\n"
	 "uniform sampler2D fs_tex0_20;\n"
	 "\n"
	 "in vec4 varying_0;\n"
	 "layout(location = 0) out vec4 frag_color0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    float _62 = 1.0 / gl_FragCoord.w;\n"
	 "    if (texture(fs_tex0_20, vec2(_62 * (varying_0.x * gl_FragCoord.w), _62 * (varying_0.y * gl_FragCoord.w))).w < texelFetch(c3, ivec2((int(4u) >> 2) & 1023, int(4u) >> 12), 0)[int(4u) & 3])\n"
	 "    {\n"
	 "        discard;\n"
	 "    }\n"
	 "    frag_color0.x = texelFetch(c3, ivec2((int(0u) >> 2) & 1023, int(0u) >> 12), 0)[int(0u) & 3];\n"
	 "    frag_color0.y = texelFetch(c3, ivec2((int(1u) >> 2) & 1023, int(1u) >> 12), 0)[int(1u) & 3];\n"
	 "    frag_color0.z = texelFetch(c3, ivec2((int(2u) >> 2) & 1023, int(2u) >> 12), 0)[int(2u) & 3];\n"
	 "    frag_color0.w = texelFetch(c3, ivec2((int(3u) >> 2) & 1023, int(3u) >> 12), 0)[int(3u) & 3];\n"
	 "}\n"
	 "", 1},
	/* 35 dump-06993fc8 fragment */
	{"", "\n"
	 "#version 310 es\n"
	 "precision highp int;\n"
	 "precision mediump float;\n"
	 "#if defined(GL_AMD_gpu_shader_half_float)\n"
	 "#extension GL_AMD_gpu_shader_half_float : require\n"
	 "#elif defined(GL_EXT_shader_explicit_arithmetic_types_float16)\n"
	 "#extension GL_EXT_shader_explicit_arithmetic_types_float16 : require\n"
	 "#else\n"
	 "\n"
	 "#endif\n"
	 "#extension GL_EXT_shader_16bit_storage : require\n"
	 "#extension GL_EXT_scalar_block_layout : require\n"
	 "\n"
	 "\n"
	 "\n"
	 "uniform highp sampler2D c3_1;\n"
	 "\n"
	 "uniform sampler2D fs_tex0_20;\n"
	 "\n"
	 "in vec4 varying_0;\n"
	 "in vec4 varying_2;\n"
	 "layout(location = 0) out vec4 frag_color0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    vec4 _59 = texture(fs_tex0_20, vec2(varying_2.x, varying_2.y));\n"
	 "    float _74 = _59.w + texelFetch(c3_1, ivec2((int(3u) >> 2) & 1023, int(3u) >> 12), 0)[int(3u) & 3];\n"
	 "    if (float(float(_74 * varying_0.w)) < uintBitsToFloat(0x3a832000u))\n"
	 "    {\n"
	 "        discard;\n"
	 "    }\n"
	 "    frag_color0.x = (_59.x + texelFetch(c3_1, ivec2((int(0u) >> 2) & 1023, int(0u) >> 12), 0)[int(0u) & 3]) * varying_0.x;\n"
	 "    frag_color0.y = (_59.y + texelFetch(c3_1, ivec2((int(1u) >> 2) & 1023, int(1u) >> 12), 0)[int(1u) & 3]) * varying_0.y;\n"
	 "    frag_color0.z = (_59.z + texelFetch(c3_1, ivec2((int(2u) >> 2) & 1023, int(2u) >> 12), 0)[int(2u) & 3]) * varying_0.z;\n"
	 "    frag_color0.w = _74 * varying_0.w;\n"
	 "}\n"
	 "", 1},
	/* 36 dump-9fcf2f47 vertex */
	{"", "\n"
	 "#version 310 es\n"
	 "precision highp int;\n"
	 "precision highp float;\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "#extension GL_EXT_scalar_block_layout : require\n"
	 "\n"
	 "\n"
	 "\n"
	 "uniform highp sampler2D c3_1;\n"
	 "\n"
	 "layout(location = 0) in vec4 in_attr0;\n"
	 "layout(location = 1) in vec4 in_attr1;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    bool _55 = !(0.0 == texelFetch(c3_1, ivec2((int(6u) >> 2) & 1023, int(6u) >> 12), 0)[int(6u) & 3]);\n"
	 "    float _130 = fma(in_attr0.w, texelFetch(c3_1, ivec2((int(20u) >> 2) & 1023, int(20u) >> 12), 0)[int(20u) & 3], fma(in_attr0.z, texelFetch(c3_1, ivec2((int(16u) >> 2) & 1023, int(16u) >> 12), 0)[int(16u) & 3], fma(in_attr0.x, texelFetch(c3_1, ivec2((int(8u) >> 2) & 1023, int(8u) >> 12), 0)[int(8u) & 3], in_attr0.y * texelFetch(c3_1, ivec2((int(12u) >> 2) & 1023, int(12u) >> 12), 0)[int(12u) & 3])));\n"
	 "    float _143 = fma(in_attr0.w, texelFetch(c3_1, ivec2((int(21u) >> 2) & 1023, int(21u) >> 12), 0)[int(21u) & 3], fma(in_attr0.z, texelFetch(c3_1, ivec2((int(17u) >> 2) & 1023, int(17u) >> 12), 0)[int(17u) & 3], fma(in_attr0.x, texelFetch(c3_1, ivec2((int(9u) >> 2) & 1023, int(9u) >> 12), 0)[int(9u) & 3], in_attr0.y * texelFetch(c3_1, ivec2((int(13u) >> 2) & 1023, int(13u) >> 12), 0)[int(13u) & 3])));\n"
	 "    float _148 = fma(in_attr1.z, texelFetch(c3_1, ivec2((int(26u) >> 2) & 1023, int(26u) >> 12), 0)[int(26u) & 3], fma(in_attr1.y, texelFetch(c3_1, ivec2((int(25u) >> 2) & 1023, int(25u) >> 12), 0)[int(25u) & 3], in_attr1.x * texelFetch(c3_1, ivec2((int(24u) >> 2) & 1023, int(24u) >> 12), 0)[int(24u) & 3]));\n"
	 "    float _158 = fma(_130, -texelFetch(c3_1, ivec2((int(3u) >> 2) & 1023, int(3u) >> 12), 0)[int(3u) & 3], texelFetch(c3_1, ivec2((int(0u) >> 2) & 1023, int(0u) >> 12), 0)[int(0u) & 3]);\n"
	 "    float _162 = fma(in_attr1.z, texelFetch(c3_1, ivec2((int(30u) >> 2) & 1023, int(30u) >> 12), 0)[int(30u) & 3], fma(in_attr1.y, texelFetch(c3_1, ivec2((int(29u) >> 2) & 1023, int(29u) >> 12), 0)[int(29u) & 3], in_attr1.x * texelFetch(c3_1, ivec2((int(28u) >> 2) & 1023, int(28u) >> 12), 0)[int(28u) & 3]));\n"
	 "    float _166 = fma(in_attr0.w, texelFetch(c3_1, ivec2((int(22u) >> 2) & 1023, int(22u) >> 12), 0)[int(22u) & 3], fma(in_attr0.z, texelFetch(c3_1, ivec2((int(18u) >> 2) & 1023, int(18u) >> 12), 0)[int(18u) & 3], fma(in_attr0.x, texelFetch(c3_1, ivec2((int(10u) >> 2) & 1023, int(10u) >> 12), 0)[int(10u) & 3], in_attr0.y * texelFetch(c3_1, ivec2((int(14u) >> 2) & 1023, int(14u) >> 12), 0)[int(14u) & 3])));\n"
	 "    float _173 = fma(_143, -texelFetch(c3_1, ivec2((int(3u) >> 2) & 1023, int(3u) >> 12), 0)[int(3u) & 3], texelFetch(c3_1, ivec2((int(1u) >> 2) & 1023, int(1u) >> 12), 0)[int(1u) & 3]);\n"
	 "    float _178 = fma(in_attr1.z, texelFetch(c3_1, ivec2((int(34u) >> 2) & 1023, int(34u) >> 12), 0)[int(34u) & 3], fma(in_attr1.y, texelFetch(c3_1, ivec2((int(33u) >> 2) & 1023, int(33u) >> 12), 0)[int(33u) & 3], in_attr1.x * texelFetch(c3_1, ivec2((int(32u) >> 2) & 1023, int(32u) >> 12), 0)[int(32u) & 3]));\n"
	 "    float _189 = fma(_166, -texelFetch(c3_1, ivec2((int(3u) >> 2) & 1023, int(3u) >> 12), 0)[int(3u) & 3], texelFetch(c3_1, ivec2((int(2u) >> 2) & 1023, int(2u) >> 12), 0)[int(2u) & 3]);\n"
	 "    float _195 = fma(in_attr0.w, texelFetch(c3_1, ivec2((int(23u) >> 2) & 1023, int(23u) >> 12), 0)[int(23u) & 3], fma(in_attr0.z, texelFetch(c3_1, ivec2((int(19u) >> 2) & 1023, int(19u) >> 12), 0)[int(19u) & 3], fma(in_attr0.x, texelFetch(c3_1, ivec2((int(11u) >> 2) & 1023, int(11u) >> 12), 0)[int(11u) & 3], in_attr0.y * texelFetch(c3_1, ivec2((int(15u) >> 2) & 1023, int(15u) >> 12), 0)[int(15u) & 3])));\n"
	 "    float _198 = inversesqrt(fma(_178, _178, fma(_162, _162, _148 * _148)));\n"
	 "    float _199 = inversesqrt(fma(_189, _189, fma(_173, _173, _158 * _158)));\n"
	 "    float _200 = _148 * _198;\n"
	 "    float _201 = _162 * _198;\n"
	 "    float _206 = _178 * _198;\n"
	 "    float _208 = fma(_189 * _199, _206, fma(_173 * _199, _201, (_158 * _199) * _200));\n"
	 "    float _216 = sqrt(fma(_208, -_208, uintBitsToFloat(0x3f800000u))) * texelFetch(c3_1, ivec2((int(6u) >> 2) & 1023, int(6u) >> 12), 0)[int(6u) & 3];\n"
	 "    uint _226;\n"
	 "    if (_55)\n"
	 "    {\n"
	 "        _226 = floatBitsToUint(fma(_201, -_216, _143));\n"
	 "    }\n"
	 "    else\n"
	 "    {\n"
	 "        _226 = floatBitsToUint(_143);\n"
	 "    }\n"
	 "    uint _227;\n"
	 "    if (_55)\n"
	 "    {\n"
	 "        _227 = floatBitsToUint(fma(_200, -_216, _130));\n"
	 "    }\n"
	 "    else\n"
	 "    {\n"
	 "        _227 = floatBitsToUint(_130);\n"
	 "    }\n"
	 "    uint _228;\n"
	 "    if (_55)\n"
	 "    {\n"
	 "        _228 = floatBitsToUint(fma(_206, -_216, _166));\n"
	 "    }\n"
	 "    else\n"
	 "    {\n"
	 "        _228 = floatBitsToUint(_166);\n"
	 "    }\n"
	 "    float _247 = fma(_195, texelFetch(c3_1, ivec2((int(55u) >> 2) & 1023, int(55u) >> 12), 0)[int(55u) & 3], fma(uintBitsToFloat(_228), texelFetch(c3_1, ivec2((int(51u) >> 2) & 1023, int(51u) >> 12), 0)[int(51u) & 3], fma(uintBitsToFloat(_227), texelFetch(c3_1, ivec2((int(43u) >> 2) & 1023, int(43u) >> 12), 0)[int(43u) & 3], uintBitsToFloat(_226) * texelFetch(c3_1, ivec2((int(47u) >> 2) & 1023, int(47u) >> 12), 0)[int(47u) & 3])));\n"
	 "    gl_Position.w = _247;\n"
	 "    float _306 = fma(_195, texelFetch(c3_1, ivec2((int(54u) >> 2) & 1023, int(54u) >> 12), 0)[int(54u) & 3], fma(uintBitsToFloat(_228), texelFetch(c3_1, ivec2((int(50u) >> 2) & 1023, int(50u) >> 12), 0)[int(50u) & 3], fma(uintBitsToFloat(_227), texelFetch(c3_1, ivec2((int(42u) >> 2) & 1023, int(42u) >> 12), 0)[int(42u) & 3], uintBitsToFloat(_226) * texelFetch(c3_1, ivec2((int(46u) >> 2) & 1023, int(46u) >> 12), 0)[int(46u) & 3]))) + max(min(0.0, (1.0 / _247) * texelFetch(c3_1, ivec2((int(4u) >> 2) & 1023, int(4u) >> 12), 0)[int(4u) & 3]), -1.0);\n"
	 "    gl_Position.x = fma(_195, texelFetch(c3_1, ivec2((int(52u) >> 2) & 1023, int(52u) >> 12), 0)[int(52u) & 3], fma(uintBitsToFloat(_228), texelFetch(c3_1, ivec2((int(48u) >> 2) & 1023, int(48u) >> 12), 0)[int(48u) & 3], fma(uintBitsToFloat(_227), texelFetch(c3_1, ivec2((int(40u) >> 2) & 1023, int(40u) >> 12), 0)[int(40u) & 3], uintBitsToFloat(_226) * texelFetch(c3_1, ivec2((int(44u) >> 2) & 1023, int(44u) >> 12), 0)[int(44u) & 3])));\n"
	 "    gl_Position.y = fma(_195, texelFetch(c3_1, ivec2((int(53u) >> 2) & 1023, int(53u) >> 12), 0)[int(53u) & 3], fma(uintBitsToFloat(_228), texelFetch(c3_1, ivec2((int(49u) >> 2) & 1023, int(49u) >> 12), 0)[int(49u) & 3], fma(uintBitsToFloat(_227), texelFetch(c3_1, ivec2((int(41u) >> 2) & 1023, int(41u) >> 12), 0)[int(41u) & 3], uintBitsToFloat(_226) * texelFetch(c3_1, ivec2((int(45u) >> 2) & 1023, int(45u) >> 12), 0)[int(45u) & 3])));\n"
	 "    gl_Position.z = fma((-_306) + min(_247, _306), texelFetch(c3_1, ivec2((int(5u) >> 2) & 1023, int(5u) >> 12), 0)[int(5u) & 3], _306);\n"
	 "}\n"
	 "", 0},
	/* 37 dump-2643d9aa fragment */
	{"", "\n"
	 "#version 310 es\n"
	 "precision highp int;\n"
	 "precision mediump float;\n"
	 "layout(location = 0) out vec4 frag_color0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    frag_color0.x = 0.0;\n"
	 "    frag_color0.y = 0.0;\n"
	 "    frag_color0.z = 0.0;\n"
	 "    frag_color0.w = 0.0;\n"
	 "}\n"
	 "", 1},
	/* 38 dump-588a3fad vertex */
	{"", "\n"
	 "#version 310 es\n"
	 "precision highp int;\n"
	 "precision highp float;\n"
	 "uniform highp sampler2D c4;\n"
	 "\n"
	 "layout(location = 0) in vec4 in_attr0;\n"
	 "layout(location = 1) in vec4 in_attr1;\n"
	 "layout(location = 2) in vec4 in_attr2;\n"
	 "layout(location = 3) in vec4 in_attr3;\n"
	 "out vec4 varying_0;\n"
	 "out vec4 varying_1;\n"
	 "out vec4 varying_2;\n"
	 "out vec4 varying_3;\n"
	 "out vec4 varying_4;\n"
	 "out vec4 varying_5;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_0 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_1 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_2 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_3 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_4 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_5 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    float _81 = in_attr0.y * texelFetch(c4, ivec2((int(69u) >> 2) & 1023, int(69u) >> 12), 0)[int(69u) & 3];\n"
	 "    varying_5.w = 0.0;\n"
	 "    float _109 = in_attr0.x * texelFetch(c4, ivec2((int(68u) >> 2) & 1023, int(68u) >> 12), 0)[int(68u) & 3];\n"
	 "    varying_0.x = in_attr3.x * texelFetch(c4, ivec2((int(76u) >> 2) & 1023, int(76u) >> 12), 0)[int(76u) & 3] + texelFetch(c4, ivec2((int(78u) >> 2) & 1023, int(78u) >> 12), 0)[int(78u) & 3];\n"
	 "    float _122 = in_attr1.z * texelFetch(c4, ivec2((int(18u) >> 2) & 1023, int(18u) >> 12), 0)[int(18u) & 3] + (in_attr1.y * texelFetch(c4, ivec2((int(17u) >> 2) & 1023, int(17u) >> 12), 0)[int(17u) & 3] + (in_attr1.x * texelFetch(c4, ivec2((int(16u) >> 2) & 1023, int(16u) >> 12), 0)[int(16u) & 3]));\n"
	 "    varying_0.y = in_attr3.y * texelFetch(c4, ivec2((int(77u) >> 2) & 1023, int(77u) >> 12), 0)[int(77u) & 3] + texelFetch(c4, ivec2((int(79u) >> 2) & 1023, int(79u) >> 12), 0)[int(79u) & 3];\n"
	 "    float _145 = in_attr1.z * texelFetch(c4, ivec2((int(22u) >> 2) & 1023, int(22u) >> 12), 0)[int(22u) & 3] + (in_attr1.y * texelFetch(c4, ivec2((int(21u) >> 2) & 1023, int(21u) >> 12), 0)[int(21u) & 3] + (in_attr1.x * texelFetch(c4, ivec2((int(20u) >> 2) & 1023, int(20u) >> 12), 0)[int(20u) & 3]));\n"
	 "    float _165 = in_attr1.z * texelFetch(c4, ivec2((int(26u) >> 2) & 1023, int(26u) >> 12), 0)[int(26u) & 3] + (in_attr1.y * texelFetch(c4, ivec2((int(25u) >> 2) & 1023, int(25u) >> 12), 0)[int(25u) & 3] + (in_attr1.x * texelFetch(c4, ivec2((int(24u) >> 2) & 1023, int(24u) >> 12), 0)[int(24u) & 3]));\n"
	 "    float _192 = (in_attr0.z * texelFetch(c4, ivec2((int(9u) >> 2) & 1023, int(9u) >> 12), 0)[int(9u) & 3] + (_109 * texelFetch(c4, ivec2((int(1u) >> 2) & 1023, int(1u) >> 12), 0)[int(1u) & 3] + (_81 * texelFetch(c4, ivec2((int(5u) >> 2) & 1023, int(5u) >> 12), 0)[int(5u) & 3]))) + texelFetch(c4, ivec2((int(13u) >> 2) & 1023, int(13u) >> 12), 0)[int(13u) & 3];\n"
	 "    varying_2.y = _192;\n"
	 "    float _203 = inversesqrt(_165 * _165 + (_145 * _145 + (_122 * _122)));\n"
	 "    varying_3.y = (in_attr2.y * texelFetch(c4, ivec2((int(73u) >> 2) & 1023, int(73u) >> 12), 0)[int(73u) & 3]) * texelFetch(c4, ivec2((int(65u) >> 2) & 1023, int(65u) >> 12), 0)[int(65u) & 3];\n"
	 "    float _212 = (in_attr0.z * texelFetch(c4, ivec2((int(8u) >> 2) & 1023, int(8u) >> 12), 0)[int(8u) & 3] + (_109 * texelFetch(c4, ivec2((int(0u) >> 2) & 1023, int(0u) >> 12), 0)[int(0u) & 3] + (_81 * texelFetch(c4, ivec2((int(4u) >> 2) & 1023, int(4u) >> 12), 0)[int(4u) & 3]))) + texelFetch(c4, ivec2((int(12u) >> 2) & 1023, int(12u) >> 12), 0)[int(12u) & 3];\n"
	 "    varying_2.x = _212;\n"
	 "    varying_3.w = (in_attr2.w * texelFetch(c4, ivec2((int(75u) >> 2) & 1023, int(75u) >> 12), 0)[int(75u) & 3]) * texelFetch(c4, ivec2((int(67u) >> 2) & 1023, int(67u) >> 12), 0)[int(67u) & 3];\n"
	 "    float _234 = (in_attr0.z * texelFetch(c4, ivec2((int(10u) >> 2) & 1023, int(10u) >> 12), 0)[int(10u) & 3] + (_109 * texelFetch(c4, ivec2((int(2u) >> 2) & 1023, int(2u) >> 12), 0)[int(2u) & 3] + (_81 * texelFetch(c4, ivec2((int(6u) >> 2) & 1023, int(6u) >> 12), 0)[int(6u) & 3]))) + texelFetch(c4, ivec2((int(14u) >> 2) & 1023, int(14u) >> 12), 0)[int(14u) & 3];\n"
	 "    varying_2.z = _234;\n"
	 "    varying_3.x = (in_attr2.x * texelFetch(c4, ivec2((int(72u) >> 2) & 1023, int(72u) >> 12), 0)[int(72u) & 3]) * texelFetch(c4, ivec2((int(64u) >> 2) & 1023, int(64u) >> 12), 0)[int(64u) & 3];\n"
	 "    varying_1.y = _145 * _203;\n"
	 "    varying_3.z = (in_attr2.z * texelFetch(c4, ivec2((int(74u) >> 2) & 1023, int(74u) >> 12), 0)[int(74u) & 3]) * texelFetch(c4, ivec2((int(66u) >> 2) & 1023, int(66u) >> 12), 0)[int(66u) & 3];\n"
	 "    float _276 = (in_attr0.z * texelFetch(c4, ivec2((int(11u) >> 2) & 1023, int(11u) >> 12), 0)[int(11u) & 3] + (_109 * texelFetch(c4, ivec2((int(3u) >> 2) & 1023, int(3u) >> 12), 0)[int(3u) & 3] + (_81 * texelFetch(c4, ivec2((int(7u) >> 2) & 1023, int(7u) >> 12), 0)[int(7u) & 3]))) + texelFetch(c4, ivec2((int(15u) >> 2) & 1023, int(15u) >> 12), 0)[int(15u) & 3];\n"
	 "    varying_1.x = _122 * _203;\n"
	 "    varying_1.z = _165 * _203;\n"
	 "    gl_Position.x = _276 * texelFetch(c4, ivec2((int(44u) >> 2) & 1023, int(44u) >> 12), 0)[int(44u) & 3] + (_234 * texelFetch(c4, ivec2((int(40u) >> 2) & 1023, int(40u) >> 12), 0)[int(40u) & 3] + (_212 * texelFetch(c4, ivec2((int(32u) >> 2) & 1023, int(32u) >> 12), 0)[int(32u) & 3] + (_192 * texelFetch(c4, ivec2((int(36u) >> 2) & 1023, int(36u) >> 12), 0)[int(36u) & 3])));\n"
	 "    gl_Position.y = _276 * texelFetch(c4, ivec2((int(45u) >> 2) & 1023, int(45u) >> 12), 0)[int(45u) & 3] + (_234 * texelFetch(c4, ivec2((int(41u) >> 2) & 1023, int(41u) >> 12), 0)[int(41u) & 3] + (_212 * texelFetch(c4, ivec2((int(33u) >> 2) & 1023, int(33u) >> 12), 0)[int(33u) & 3] + (_192 * texelFetch(c4, ivec2((int(37u) >> 2) & 1023, int(37u) >> 12), 0)[int(37u) & 3])));\n"
	 "    gl_Position.z = _276 * texelFetch(c4, ivec2((int(46u) >> 2) & 1023, int(46u) >> 12), 0)[int(46u) & 3] + (_234 * texelFetch(c4, ivec2((int(42u) >> 2) & 1023, int(42u) >> 12), 0)[int(42u) & 3] + (_212 * texelFetch(c4, ivec2((int(34u) >> 2) & 1023, int(34u) >> 12), 0)[int(34u) & 3] + (_192 * texelFetch(c4, ivec2((int(38u) >> 2) & 1023, int(38u) >> 12), 0)[int(38u) & 3])));\n"
	 "    varying_4.x = _276 * texelFetch(c4, ivec2((int(60u) >> 2) & 1023, int(60u) >> 12), 0)[int(60u) & 3] + (_234 * texelFetch(c4, ivec2((int(56u) >> 2) & 1023, int(56u) >> 12), 0)[int(56u) & 3] + (_212 * texelFetch(c4, ivec2((int(48u) >> 2) & 1023, int(48u) >> 12), 0)[int(48u) & 3] + (_192 * texelFetch(c4, ivec2((int(52u) >> 2) & 1023, int(52u) >> 12), 0)[int(52u) & 3])));\n"
	 "    gl_Position.w = _276 * texelFetch(c4, ivec2((int(47u) >> 2) & 1023, int(47u) >> 12), 0)[int(47u) & 3] + (_234 * texelFetch(c4, ivec2((int(43u) >> 2) & 1023, int(43u) >> 12), 0)[int(43u) & 3] + (_212 * texelFetch(c4, ivec2((int(35u) >> 2) & 1023, int(35u) >> 12), 0)[int(35u) & 3] + (_192 * texelFetch(c4, ivec2((int(39u) >> 2) & 1023, int(39u) >> 12), 0)[int(39u) & 3])));\n"
	 "    varying_4.y = _276 * texelFetch(c4, ivec2((int(61u) >> 2) & 1023, int(61u) >> 12), 0)[int(61u) & 3] + (_234 * texelFetch(c4, ivec2((int(57u) >> 2) & 1023, int(57u) >> 12), 0)[int(57u) & 3] + (_212 * texelFetch(c4, ivec2((int(49u) >> 2) & 1023, int(49u) >> 12), 0)[int(49u) & 3] + (_192 * texelFetch(c4, ivec2((int(53u) >> 2) & 1023, int(53u) >> 12), 0)[int(53u) & 3])));\n"
	 "    varying_4.z = _276 * texelFetch(c4, ivec2((int(62u) >> 2) & 1023, int(62u) >> 12), 0)[int(62u) & 3] + (_234 * texelFetch(c4, ivec2((int(58u) >> 2) & 1023, int(58u) >> 12), 0)[int(58u) & 3] + (_212 * texelFetch(c4, ivec2((int(50u) >> 2) & 1023, int(50u) >> 12), 0)[int(50u) & 3] + (_192 * texelFetch(c4, ivec2((int(54u) >> 2) & 1023, int(54u) >> 12), 0)[int(54u) & 3])));\n"
	 "}\n"
	 "", 0},
	/* 39 lighting fragment */
	{"", "\n"
	 "#version 310 es\n"
	 "precision highp int;\n"
	 "precision mediump float;\n"
	 "#define unpackFloat2x16(a) unpackHalf2x16(a)\n"
	 "#define packFloat2x16(a) packHalf2x16(a)\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "#define lc2_half(a) unpackHalf2x16(packHalf2x16(vec2(float(a), 0.0))).x\n"
	 "/* GUARDED: c3[8] != 1.0 at every draw; enabled volume requires real backend. */\n"
	 "\n"
	 "uniform highp sampler2D c3;\n"
	 "\n"
	 "uniform sampler2D fs_tex0_20;\n"
	 "uniform sampler2D fs_tex0_28;\n"
	 "\n"
	 "\n"
	 "in vec4 varying_0;\n"
	 "in vec4 varying_1;\n"
	 "in vec4 varying_2;\n"
	 "in vec4 varying_3;\n"
	 "layout(location = 0) out vec4 frag_color0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    mediump vec4 _72 = texture(fs_tex0_20, vec2(varying_0.x, varying_0.y));\n"
	 "    uint _79 = packHalf2x16(vec2(_72.xy));\n"
	 "    uint _81 = packHalf2x16(vec2(_72.zw));\n"
	 "    uint _84 = floatBitsToUint(varying_2.x);\n"
	 "    uint _87 = floatBitsToUint(varying_2.y);\n"
	 "    uint _91 = floatBitsToUint(varying_2.z);\n"
	 "    float _101 = (-varying_2.x) + texelFetch(c3, ivec2((int(0u) >> 2) & 1023, int(0u) >> 12), 0)[int(0u) & 3];\n"
	 "    float _105 = (-varying_2.y) + texelFetch(c3, ivec2((int(1u) >> 2) & 1023, int(1u) >> 12), 0)[int(1u) & 3];\n"
	 "    float _109 = (-varying_2.z) + texelFetch(c3, ivec2((int(2u) >> 2) & 1023, int(2u) >> 12), 0)[int(2u) & 3];\n"
	 "    float _113 = inversesqrt(fma(_109, _109, fma(_105, _105, _101 * _101)));\n"
	 "    \n"
	 "    float _133 = lc2_half(float(unpackFloat2x16(_79).y) * varying_3.y);\n"
	 "    vec2 _135 = unpackFloat2x16(_79);\n"
	 "    _135.y = _133;\n"
	 "    float _144 = lc2_half(float(unpackFloat2x16(_81).x) * varying_3.z);\n"
	 "    vec2 _146 = unpackFloat2x16(_81);\n"
	 "    _146.x = _144;\n"
	 "    float _160 = float(lc2_half(float(_146.y) * varying_3.w));\n"
	 "    float _197 = fma(varying_2.z, texelFetch(c3, ivec2((int(48u) >> 2) & 1023, int(48u) >> 12), 0)[int(48u) & 3], fma(varying_2.x, texelFetch(c3, ivec2((int(40u) >> 2) & 1023, int(40u) >> 12), 0)[int(40u) & 3], varying_2.y * texelFetch(c3, ivec2((int(44u) >> 2) & 1023, int(44u) >> 12), 0)[int(44u) & 3])) + texelFetch(c3, ivec2((int(52u) >> 2) & 1023, int(52u) >> 12), 0)[int(52u) & 3];\n"
	 "    float _201 = fma(varying_2.z, texelFetch(c3, ivec2((int(49u) >> 2) & 1023, int(49u) >> 12), 0)[int(49u) & 3], fma(varying_2.x, texelFetch(c3, ivec2((int(41u) >> 2) & 1023, int(41u) >> 12), 0)[int(41u) & 3], varying_2.y * texelFetch(c3, ivec2((int(45u) >> 2) & 1023, int(45u) >> 12), 0)[int(45u) & 3])) + texelFetch(c3, ivec2((int(53u) >> 2) & 1023, int(53u) >> 12), 0)[int(53u) & 3];\n"
	 "    float _205 = fma(varying_2.z, texelFetch(c3, ivec2((int(50u) >> 2) & 1023, int(50u) >> 12), 0)[int(50u) & 3], fma(varying_2.x, texelFetch(c3, ivec2((int(42u) >> 2) & 1023, int(42u) >> 12), 0)[int(42u) & 3], varying_2.y * texelFetch(c3, ivec2((int(46u) >> 2) & 1023, int(46u) >> 12), 0)[int(46u) & 3])) + texelFetch(c3, ivec2((int(54u) >> 2) & 1023, int(54u) >> 12), 0)[int(54u) & 3];\n"
	 "    uint _319;\n"
	 "    uint _320;\n"
	 "    uint _321;\n"
	 "    uint _322;\n"
	 "    {\n"
	 "        _319 = _87;\n"
	 "        _320 = _84;\n"
	 "        _321 = _91;\n"
	 "        _322 = packFloat2x16(_146);\n"
	 "    }\n"
	 "    uint _332;\n"
	 "    uint _333;\n"
	 "    uint _334;\n"
	 "    uint _335;\n"
	 "    {\n"
	 "        uint _331 = floatBitsToUint(float((-unpackFloat2x16(0u).x) + unpackFloat2x16(1006648320u).x));\n"
	 "        _332 = _331;\n"
	 "        _333 = _331;\n"
	 "        _334 = _331;\n"
	 "        _335 = _331;\n"
	 "    }\n"
	 "    float _373 = max(0.0, fma(_109 * _113, varying_1.z, fma(_105 * _113, varying_1.y, (_101 * _113) * varying_1.x)));\n"
	 "    float _374 = clamp(fma(uintBitsToFloat(_332), texelFetch(c3, ivec2((int(7u) >> 2) & 1023, int(7u) >> 12), 0)[int(7u) & 3], fma(uintBitsToFloat(_333), texelFetch(c3, ivec2((int(6u) >> 2) & 1023, int(6u) >> 12), 0)[int(6u) & 3], fma(uintBitsToFloat(_334), texelFetch(c3, ivec2((int(5u) >> 2) & 1023, int(5u) >> 12), 0)[int(5u) & 3], uintBitsToFloat(_335) * texelFetch(c3, ivec2((int(4u) >> 2) & 1023, int(4u) >> 12), 0)[int(4u) & 3]))), 0.0, 1.0) * texture(fs_tex0_28, vec2(fma(_205, _205, fma(_201, _201, _197 * _197)))).x;\n"
	 "    frag_color0.x = float(lc2_half(_373 * float(lc2_half(float(lc2_half(_160 * float(lc2_half(float(_135.x) * varying_3.x)))) * (_374 * texelFetch(c3, ivec2((int(36u) >> 2) & 1023, int(36u) >> 12), 0)[int(36u) & 3])))));\n"
	 "    frag_color0.y = float(lc2_half(_373 * float(lc2_half(float(lc2_half(_160 * float(_133))) * (_374 * texelFetch(c3, ivec2((int(37u) >> 2) & 1023, int(37u) >> 12), 0)[int(37u) & 3])))));\n"
	 "    frag_color0.z = float(lc2_half(_373 * float(lc2_half(float(lc2_half(_160 * float(_144))) * (_374 * texelFetch(c3, ivec2((int(38u) >> 2) & 1023, int(38u) >> 12), 0)[int(38u) & 3])))));\n"
	 "    frag_color0.w = _160;\n"
	 "}\n"
	 "", 1},
	/* 40 dump-84137e66 vertex */
	{"", "\n"
	 "#version 310 es\n"
	 "precision highp int;\n"
	 "precision highp float;\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "uniform highp sampler2D c3;\n"
	 "\n"
	 "layout(location = 0) in vec4 in_attr0;\n"
	 "layout(location = 1) in vec4 in_attr1;\n"
	 "layout(location = 2) in vec4 in_attr2;\n"
	 "out vec4 varying_0;\n"
	 "out vec4 varying_1;\n"
	 "out vec4 varying_2;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_0 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_1 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_2 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    float _97 = in_attr0.y * texelFetch(c3, ivec2((int(53u) >> 2) & 1023, int(53u) >> 12), 0)[int(53u) & 3];\n"
	 "    float _101 = fma(in_attr1.z, texelFetch(c3, ivec2((int(18u) >> 2) & 1023, int(18u) >> 12), 0)[int(18u) & 3], fma(in_attr1.y, texelFetch(c3, ivec2((int(17u) >> 2) & 1023, int(17u) >> 12), 0)[int(17u) & 3], in_attr1.x * texelFetch(c3, ivec2((int(16u) >> 2) & 1023, int(16u) >> 12), 0)[int(16u) & 3]));\n"
	 "    float _105 = fma(in_attr1.z, texelFetch(c3, ivec2((int(22u) >> 2) & 1023, int(22u) >> 12), 0)[int(22u) & 3], fma(in_attr1.y, texelFetch(c3, ivec2((int(21u) >> 2) & 1023, int(21u) >> 12), 0)[int(21u) & 3], in_attr1.x * texelFetch(c3, ivec2((int(20u) >> 2) & 1023, int(20u) >> 12), 0)[int(20u) & 3]));\n"
	 "    float _109 = fma(in_attr1.z, texelFetch(c3, ivec2((int(26u) >> 2) & 1023, int(26u) >> 12), 0)[int(26u) & 3], fma(in_attr1.y, texelFetch(c3, ivec2((int(25u) >> 2) & 1023, int(25u) >> 12), 0)[int(25u) & 3], in_attr1.x * texelFetch(c3, ivec2((int(24u) >> 2) & 1023, int(24u) >> 12), 0)[int(24u) & 3]));\n"
	 "    float _113 = in_attr0.x * texelFetch(c3, ivec2((int(52u) >> 2) & 1023, int(52u) >> 12), 0)[int(52u) & 3];\n"
	 "    varying_2.x = (in_attr2.x * texelFetch(c3, ivec2((int(56u) >> 2) & 1023, int(56u) >> 12), 0)[int(56u) & 3]) * texelFetch(c3, ivec2((int(48u) >> 2) & 1023, int(48u) >> 12), 0)[int(48u) & 3];\n"
	 "    float _160 = inversesqrt(fma(_109, _109, fma(_105, _105, _101 * _101)));\n"
	 "    varying_2.y = (in_attr2.y * texelFetch(c3, ivec2((int(57u) >> 2) & 1023, int(57u) >> 12), 0)[int(57u) & 3]) * texelFetch(c3, ivec2((int(49u) >> 2) & 1023, int(49u) >> 12), 0)[int(49u) & 3];\n"
	 "    varying_2.z = (in_attr2.z * texelFetch(c3, ivec2((int(58u) >> 2) & 1023, int(58u) >> 12), 0)[int(58u) & 3]) * texelFetch(c3, ivec2((int(50u) >> 2) & 1023, int(50u) >> 12), 0)[int(50u) & 3];\n"
	 "    float _188 = fma(in_attr0.z, texelFetch(c3, ivec2((int(9u) >> 2) & 1023, int(9u) >> 12), 0)[int(9u) & 3], fma(_113, texelFetch(c3, ivec2((int(1u) >> 2) & 1023, int(1u) >> 12), 0)[int(1u) & 3], _97 * texelFetch(c3, ivec2((int(5u) >> 2) & 1023, int(5u) >> 12), 0)[int(5u) & 3])) + texelFetch(c3, ivec2((int(13u) >> 2) & 1023, int(13u) >> 12), 0)[int(13u) & 3];\n"
	 "    varying_1.y = _188;\n"
	 "    varying_0.x = _101 * _160;\n"
	 "    float _199 = fma(in_attr0.z, texelFetch(c3, ivec2((int(8u) >> 2) & 1023, int(8u) >> 12), 0)[int(8u) & 3], fma(_113, texelFetch(c3, ivec2((int(0u) >> 2) & 1023, int(0u) >> 12), 0)[int(0u) & 3], _97 * texelFetch(c3, ivec2((int(4u) >> 2) & 1023, int(4u) >> 12), 0)[int(4u) & 3])) + texelFetch(c3, ivec2((int(12u) >> 2) & 1023, int(12u) >> 12), 0)[int(12u) & 3];\n"
	 "    varying_1.x = _199;\n"
	 "    varying_0.y = _105 * _160;\n"
	 "    varying_0.z = _109 * _160;\n"
	 "    float _216 = fma(in_attr0.z, texelFetch(c3, ivec2((int(10u) >> 2) & 1023, int(10u) >> 12), 0)[int(10u) & 3], fma(_113, texelFetch(c3, ivec2((int(2u) >> 2) & 1023, int(2u) >> 12), 0)[int(2u) & 3], _97 * texelFetch(c3, ivec2((int(6u) >> 2) & 1023, int(6u) >> 12), 0)[int(6u) & 3])) + texelFetch(c3, ivec2((int(14u) >> 2) & 1023, int(14u) >> 12), 0)[int(14u) & 3];\n"
	 "    varying_1.z = _216;\n"
	 "    float _233 = fma(in_attr0.z, texelFetch(c3, ivec2((int(11u) >> 2) & 1023, int(11u) >> 12), 0)[int(11u) & 3], fma(_113, texelFetch(c3, ivec2((int(3u) >> 2) & 1023, int(3u) >> 12), 0)[int(3u) & 3], _97 * texelFetch(c3, ivec2((int(7u) >> 2) & 1023, int(7u) >> 12), 0)[int(7u) & 3])) + texelFetch(c3, ivec2((int(15u) >> 2) & 1023, int(15u) >> 12), 0)[int(15u) & 3];\n"
	 "    varying_2.w = (in_attr2.w * texelFetch(c3, ivec2((int(59u) >> 2) & 1023, int(59u) >> 12), 0)[int(59u) & 3]) * texelFetch(c3, ivec2((int(51u) >> 2) & 1023, int(51u) >> 12), 0)[int(51u) & 3];\n"
	 "    gl_Position.x = fma(_233, texelFetch(c3, ivec2((int(44u) >> 2) & 1023, int(44u) >> 12), 0)[int(44u) & 3], fma(_216, texelFetch(c3, ivec2((int(40u) >> 2) & 1023, int(40u) >> 12), 0)[int(40u) & 3], fma(_199, texelFetch(c3, ivec2((int(32u) >> 2) & 1023, int(32u) >> 12), 0)[int(32u) & 3], _188 * texelFetch(c3, ivec2((int(36u) >> 2) & 1023, int(36u) >> 12), 0)[int(36u) & 3])));\n"
	 "    gl_Position.y = fma(_233, texelFetch(c3, ivec2((int(45u) >> 2) & 1023, int(45u) >> 12), 0)[int(45u) & 3], fma(_216, texelFetch(c3, ivec2((int(41u) >> 2) & 1023, int(41u) >> 12), 0)[int(41u) & 3], fma(_199, texelFetch(c3, ivec2((int(33u) >> 2) & 1023, int(33u) >> 12), 0)[int(33u) & 3], _188 * texelFetch(c3, ivec2((int(37u) >> 2) & 1023, int(37u) >> 12), 0)[int(37u) & 3])));\n"
	 "    gl_Position.z = fma(_233, texelFetch(c3, ivec2((int(46u) >> 2) & 1023, int(46u) >> 12), 0)[int(46u) & 3], fma(_216, texelFetch(c3, ivec2((int(42u) >> 2) & 1023, int(42u) >> 12), 0)[int(42u) & 3], fma(_199, texelFetch(c3, ivec2((int(34u) >> 2) & 1023, int(34u) >> 12), 0)[int(34u) & 3], _188 * texelFetch(c3, ivec2((int(38u) >> 2) & 1023, int(38u) >> 12), 0)[int(38u) & 3])));\n"
	 "    gl_Position.w = fma(_233, texelFetch(c3, ivec2((int(47u) >> 2) & 1023, int(47u) >> 12), 0)[int(47u) & 3], fma(_216, texelFetch(c3, ivec2((int(43u) >> 2) & 1023, int(43u) >> 12), 0)[int(43u) & 3], fma(_199, texelFetch(c3, ivec2((int(35u) >> 2) & 1023, int(35u) >> 12), 0)[int(35u) & 3], _188 * texelFetch(c3, ivec2((int(39u) >> 2) & 1023, int(39u) >> 12), 0)[int(39u) & 3])));\n"
	 "}\n"
	 "", 0},
	/* 41 dump-6b33f390 fragment */
	{"", "\n"
	 "#version 310 es\n"
	 "precision highp int;\n"
	 "precision mediump float;\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "in vec4 varying_0;\n"
	 "layout(location = 0) out vec4 frag_color0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    frag_color0.x = fma(varying_0.x, 0.5, 0.5);\n"
	 "    frag_color0.y = fma(varying_0.y, 0.5, 0.5);\n"
	 "    frag_color0.z = fma(varying_0.z, 0.5, 0.5);\n"
	 "    frag_color0.w = 0.0;\n"
	 "}\n"
	 "", 1},
	/* 42 literal-vertex vertex */
	{"", "\n"
	 "#version 310 es\n"
	 "precision highp int;\n"
	 "precision highp float;\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "uniform highp sampler2D c3_1;\n"
	 "\n"
	 "layout(location = 0) in vec4 in_attr0;\n"
	 "layout(location = 1) in vec4 in_attr1;\n"
	 "layout(location = 2) in vec4 in_attr2;\n"
	 "layout(location = 3) in vec4 in_attr3;\n"
	 "out vec4 varying_0;\n"
	 "out vec4 varying_1;\n"
	 "out vec4 varying_2;\n"
	 "out vec4 varying_3;\n"
	 "out vec4 varying_4;\n"
	 "out vec4 varying_5;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_0 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_1 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_2 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_3 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_4 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    varying_5 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    float _93 = fma(in_attr1.z, texelFetch(c3_1, ivec2((int(50u) >> 2) & 1023, int(50u) >> 12), 0)[int(50u) & 3], fma(in_attr1.y, texelFetch(c3_1, ivec2((int(49u) >> 2) & 1023, int(49u) >> 12), 0)[int(49u) & 3], in_attr1.x * texelFetch(c3_1, ivec2((int(48u) >> 2) & 1023, int(48u) >> 12), 0)[int(48u) & 3]));\n"
	 "    float _101 = in_attr0.y * texelFetch(c3_1, ivec2((int(85u) >> 2) & 1023, int(85u) >> 12), 0)[int(85u) & 3];\n"
	 "    float _105 = fma(in_attr1.z, texelFetch(c3_1, ivec2((int(54u) >> 2) & 1023, int(54u) >> 12), 0)[int(54u) & 3], fma(in_attr1.y, texelFetch(c3_1, ivec2((int(53u) >> 2) & 1023, int(53u) >> 12), 0)[int(53u) & 3], in_attr1.x * texelFetch(c3_1, ivec2((int(52u) >> 2) & 1023, int(52u) >> 12), 0)[int(52u) & 3]));\n"
	 "    float _110 = fma(in_attr1.z, texelFetch(c3_1, ivec2((int(58u) >> 2) & 1023, int(58u) >> 12), 0)[int(58u) & 3], fma(in_attr1.y, texelFetch(c3_1, ivec2((int(57u) >> 2) & 1023, int(57u) >> 12), 0)[int(57u) & 3], in_attr1.x * texelFetch(c3_1, ivec2((int(56u) >> 2) & 1023, int(56u) >> 12), 0)[int(56u) & 3]));\n"
	 "    float _130 = in_attr0.x * texelFetch(c3_1, ivec2((int(84u) >> 2) & 1023, int(84u) >> 12), 0)[int(84u) & 3];\n"
	 "    float _132 = inversesqrt(fma(_110, _110, fma(_105, _105, _93 * _93)));\n"
	 "    float _156 = _93 * _132;\n"
	 "    float _157 = _105 * _132;\n"
	 "    float _162 = _110 * _132;\n"
	 "    float _177 = _156 * _157;\n"
	 "    float _182 = _157 * _162;\n"
	 "    float _188 = _162 * _162;\n"
	 "    float _214 = fma(in_attr0.z, texelFetch(c3_1, ivec2((int(41u) >> 2) & 1023, int(41u) >> 12), 0)[int(41u) & 3], fma(_130, texelFetch(c3_1, ivec2((int(33u) >> 2) & 1023, int(33u) >> 12), 0)[int(33u) & 3], _101 * texelFetch(c3_1, ivec2((int(37u) >> 2) & 1023, int(37u) >> 12), 0)[int(37u) & 3])) + texelFetch(c3_1, ivec2((int(45u) >> 2) & 1023, int(45u) >> 12), 0)[int(45u) & 3];\n"
	 "    float _230 = fma(_156, _156, -(_157 * _157));\n"
	 "    float _231 = _156 * _162;\n"
	 "    varying_0.x = fma(in_attr3.x, texelFetch(c3_1, ivec2((int(92u) >> 2) & 1023, int(92u) >> 12), 0)[int(92u) & 3], texelFetch(c3_1, ivec2((int(94u) >> 2) & 1023, int(94u) >> 12), 0)[int(94u) & 3]);\n"
	 "    varying_0.y = fma(in_attr3.y, texelFetch(c3_1, ivec2((int(93u) >> 2) & 1023, int(93u) >> 12), 0)[int(93u) & 3], texelFetch(c3_1, ivec2((int(95u) >> 2) & 1023, int(95u) >> 12), 0)[int(95u) & 3]);\n"
	 "    varying_1.y = _214;\n"
	 "    varying_4.w = 0.0;\n"
	 "    float _318 = fma(in_attr0.z, texelFetch(c3_1, ivec2((int(40u) >> 2) & 1023, int(40u) >> 12), 0)[int(40u) & 3], fma(_130, texelFetch(c3_1, ivec2((int(32u) >> 2) & 1023, int(32u) >> 12), 0)[int(32u) & 3], _101 * texelFetch(c3_1, ivec2((int(36u) >> 2) & 1023, int(36u) >> 12), 0)[int(36u) & 3])) + texelFetch(c3_1, ivec2((int(44u) >> 2) & 1023, int(44u) >> 12), 0)[int(44u) & 3];\n"
	 "    varying_1.x = _318;\n"
	 "    float _344 = fma(in_attr0.z, texelFetch(c3_1, ivec2((int(42u) >> 2) & 1023, int(42u) >> 12), 0)[int(42u) & 3], fma(_130, texelFetch(c3_1, ivec2((int(34u) >> 2) & 1023, int(34u) >> 12), 0)[int(34u) & 3], _101 * texelFetch(c3_1, ivec2((int(38u) >> 2) & 1023, int(38u) >> 12), 0)[int(38u) & 3])) + texelFetch(c3_1, ivec2((int(46u) >> 2) & 1023, int(46u) >> 12), 0)[int(46u) & 3];\n"
	 "    varying_1.z = _344;\n"
	 "    varying_2.x = (in_attr2.x * texelFetch(c3_1, ivec2((int(88u) >> 2) & 1023, int(88u) >> 12), 0)[int(88u) & 3]) * texelFetch(c3_1, ivec2((int(80u) >> 2) & 1023, int(80u) >> 12), 0)[int(80u) & 3];\n"
	 "    varying_2.z = (in_attr2.z * texelFetch(c3_1, ivec2((int(90u) >> 2) & 1023, int(90u) >> 12), 0)[int(90u) & 3]) * texelFetch(c3_1, ivec2((int(82u) >> 2) & 1023, int(82u) >> 12), 0)[int(82u) & 3];\n"
	 "    varying_2.w = (in_attr2.w * texelFetch(c3_1, ivec2((int(91u) >> 2) & 1023, int(91u) >> 12), 0)[int(91u) & 3]) * texelFetch(c3_1, ivec2((int(83u) >> 2) & 1023, int(83u) >> 12), 0)[int(83u) & 3];\n"
	 "    float _393 = fma(in_attr0.z, texelFetch(c3_1, ivec2((int(43u) >> 2) & 1023, int(43u) >> 12), 0)[int(43u) & 3], fma(_130, texelFetch(c3_1, ivec2((int(35u) >> 2) & 1023, int(35u) >> 12), 0)[int(35u) & 3], _101 * texelFetch(c3_1, ivec2((int(39u) >> 2) & 1023, int(39u) >> 12), 0)[int(39u) & 3])) + texelFetch(c3_1, ivec2((int(47u) >> 2) & 1023, int(47u) >> 12), 0)[int(47u) & 3];\n"
	 "    float _414 = fma(_393, texelFetch(c3_1, ivec2((int(78u) >> 2) & 1023, int(78u) >> 12), 0)[int(78u) & 3], fma(_344, texelFetch(c3_1, ivec2((int(74u) >> 2) & 1023, int(74u) >> 12), 0)[int(74u) & 3], fma(_318, texelFetch(c3_1, ivec2((int(66u) >> 2) & 1023, int(66u) >> 12), 0)[int(66u) & 3], _214 * texelFetch(c3_1, ivec2((int(70u) >> 2) & 1023, int(70u) >> 12), 0)[int(70u) & 3])));\n"
	 "    gl_Position.z = _414;\n"
	 "    varying_3.z = _414;\n"
	 "    varying_2.y = (in_attr2.y * texelFetch(c3_1, ivec2((int(89u) >> 2) & 1023, int(89u) >> 12), 0)[int(89u) & 3]) * texelFetch(c3_1, ivec2((int(81u) >> 2) & 1023, int(81u) >> 12), 0)[int(81u) & 3];\n"
	 "    float _433 = fma(_393, texelFetch(c3_1, ivec2((int(79u) >> 2) & 1023, int(79u) >> 12), 0)[int(79u) & 3], fma(_344, texelFetch(c3_1, ivec2((int(75u) >> 2) & 1023, int(75u) >> 12), 0)[int(75u) & 3], fma(_318, texelFetch(c3_1, ivec2((int(67u) >> 2) & 1023, int(67u) >> 12), 0)[int(67u) & 3], _214 * texelFetch(c3_1, ivec2((int(71u) >> 2) & 1023, int(71u) >> 12), 0)[int(71u) & 3])));\n"
	 "    float _437 = fma(_393, texelFetch(c3_1, ivec2((int(76u) >> 2) & 1023, int(76u) >> 12), 0)[int(76u) & 3], fma(_344, texelFetch(c3_1, ivec2((int(72u) >> 2) & 1023, int(72u) >> 12), 0)[int(72u) & 3], fma(_318, texelFetch(c3_1, ivec2((int(64u) >> 2) & 1023, int(64u) >> 12), 0)[int(64u) & 3], _214 * texelFetch(c3_1, ivec2((int(68u) >> 2) & 1023, int(68u) >> 12), 0)[int(68u) & 3])));\n"
	 "    gl_Position.w = _433;\n"
	 "    float _442 = fma(_393, texelFetch(c3_1, ivec2((int(77u) >> 2) & 1023, int(77u) >> 12), 0)[int(77u) & 3], fma(_344, texelFetch(c3_1, ivec2((int(73u) >> 2) & 1023, int(73u) >> 12), 0)[int(73u) & 3], fma(_318, texelFetch(c3_1, ivec2((int(65u) >> 2) & 1023, int(65u) >> 12), 0)[int(65u) & 3], _214 * texelFetch(c3_1, ivec2((int(69u) >> 2) & 1023, int(69u) >> 12), 0)[int(69u) & 3])));\n"
	 "    varying_3.w = _433;\n"
	 "    gl_Position.y = _442;\n"
	 "    gl_Position.x = _437;\n"
	 "    float _450 = _433 * 0.5;\n"
	 "    varying_3.x = fma(_437, 0.5, _450);\n"
	 "    varying_3.y = fma(_442 * texelFetch(c3_1, ivec2((int(0u) >> 2) & 1023, int(0u) >> 12), 0)[int(0u) & 3], 0.5, _450);\n"
	 "    varying_5.x = max(0.0, fma(exp2(log2(max(0.0, fma(_230, texelFetch(c3_1, ivec2((int(28u) >> 2) & 1023, int(28u) >> 12), 0)[int(28u) & 3], fma(_231, texelFetch(c3_1, ivec2((int(19u) >> 2) & 1023, int(19u) >> 12), 0)[int(19u) & 3], fma(_188, texelFetch(c3_1, ivec2((int(18u) >> 2) & 1023, int(18u) >> 12), 0)[int(18u) & 3], fma(_182, texelFetch(c3_1, ivec2((int(17u) >> 2) & 1023, int(17u) >> 12), 0)[int(17u) & 3], _177 * texelFetch(c3_1, ivec2((int(16u) >> 2) & 1023, int(16u) >> 12), 0)[int(16u) & 3])))) + (fma(_162, texelFetch(c3_1, ivec2((int(6u) >> 2) & 1023, int(6u) >> 12), 0)[int(6u) & 3], fma(_157, texelFetch(c3_1, ivec2((int(5u) >> 2) & 1023, int(5u) >> 12), 0)[int(5u) & 3], _156 * texelFetch(c3_1, ivec2((int(4u) >> 2) & 1023, int(4u) >> 12), 0)[int(4u) & 3])) + texelFetch(c3_1, ivec2((int(7u) >> 2) & 1023, int(7u) >> 12), 0)[int(7u) & 3]))) * 0.4166666567325592041015625), uintBitsToFloat(0x3f870a3du), -0.054999999701976776123046875));\n"
	 "    varying_5.y = max(0.0, fma(exp2(log2(max(0.0, fma(_230, texelFetch(c3_1, ivec2((int(29u) >> 2) & 1023, int(29u) >> 12), 0)[int(29u) & 3], fma(_231, texelFetch(c3_1, ivec2((int(23u) >> 2) & 1023, int(23u) >> 12), 0)[int(23u) & 3], fma(_188, texelFetch(c3_1, ivec2((int(22u) >> 2) & 1023, int(22u) >> 12), 0)[int(22u) & 3], fma(_182, texelFetch(c3_1, ivec2((int(21u) >> 2) & 1023, int(21u) >> 12), 0)[int(21u) & 3], _177 * texelFetch(c3_1, ivec2((int(20u) >> 2) & 1023, int(20u) >> 12), 0)[int(20u) & 3])))) + (fma(_162, texelFetch(c3_1, ivec2((int(10u) >> 2) & 1023, int(10u) >> 12), 0)[int(10u) & 3], fma(_157, texelFetch(c3_1, ivec2((int(9u) >> 2) & 1023, int(9u) >> 12), 0)[int(9u) & 3], _156 * texelFetch(c3_1, ivec2((int(8u) >> 2) & 1023, int(8u) >> 12), 0)[int(8u) & 3])) + texelFetch(c3_1, ivec2((int(11u) >> 2) & 1023, int(11u) >> 12), 0)[int(11u) & 3]))) * 0.4166666567325592041015625), uintBitsToFloat(0x3f870a3du), -0.054999999701976776123046875));\n"
	 "    varying_5.z = max(0.0, fma(exp2(log2(max(0.0, fma(_230, texelFetch(c3_1, ivec2((int(30u) >> 2) & 1023, int(30u) >> 12), 0)[int(30u) & 3], fma(_231, texelFetch(c3_1, ivec2((int(27u) >> 2) & 1023, int(27u) >> 12), 0)[int(27u) & 3], fma(_188, texelFetch(c3_1, ivec2((int(26u) >> 2) & 1023, int(26u) >> 12), 0)[int(26u) & 3], fma(_182, texelFetch(c3_1, ivec2((int(25u) >> 2) & 1023, int(25u) >> 12), 0)[int(25u) & 3], _177 * texelFetch(c3_1, ivec2((int(24u) >> 2) & 1023, int(24u) >> 12), 0)[int(24u) & 3])))) + (fma(_162, texelFetch(c3_1, ivec2((int(14u) >> 2) & 1023, int(14u) >> 12), 0)[int(14u) & 3], fma(_157, texelFetch(c3_1, ivec2((int(13u) >> 2) & 1023, int(13u) >> 12), 0)[int(13u) & 3], _156 * texelFetch(c3_1, ivec2((int(12u) >> 2) & 1023, int(12u) >> 12), 0)[int(12u) & 3])) + texelFetch(c3_1, ivec2((int(15u) >> 2) & 1023, int(15u) >> 12), 0)[int(15u) & 3]))) * 0.4166666567325592041015625), uintBitsToFloat(0x3f870a3du), -0.054999999701976776123046875));\n"
	 "}\n"
	 "", 0},
	/* 43 half-color fragment */
	{"", "\n"
	 "#version 310 es\n"
	 "precision highp int;\n"
	 "precision highp float;\n"
	 "#define unpackFloat2x16(a) unpackHalf2x16(a)\n"
	 "#define packFloat2x16(a) packHalf2x16(a)\n"
	 "#define lc2_half(a) unpackHalf2x16(packHalf2x16(vec2(float(a), 0.0))).x\n"
	 "\n"
	 "uniform sampler2D fs_tex0_20;\n"
	 "uniform sampler2D fs_tex0_28;\n"
	 "\n"
	 "in vec4 varying_0;\n"
	 "in vec4 varying_2;\n"
	 "in vec4 varying_3;\n"
	 "in vec4 varying_5;\n"
	 "layout(location = 0) out vec4 frag_color0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    float _58 = 1.0 / varying_3.w;\n"
	 "    vec4 _63 = texture(fs_tex0_28, vec2(varying_3.x * _58, varying_3.y * _58));\n"
	 "    mediump vec4 _69 = texture(fs_tex0_20, vec2(varying_0.x, varying_0.y));\n"
	 "    uint _76 = packHalf2x16(vec2(_69.xy));\n"
	 "    uint _78 = packHalf2x16(vec2(_69.zw));\n"
	 "    float _101 = lc2_half(float(unpackFloat2x16(_76).x) * varying_2.x);\n"
	 "    vec2 _103 = unpackFloat2x16(_76);\n"
	 "    _103.x = _101;\n"
	 "    float _109 = float(lc2_half(float(unpackFloat2x16(_78).y) * varying_2.w));\n"
	 "    frag_color0.x = float(lc2_half(_109 * float(_101))) * (varying_5.x + (-log2(_63.x)));\n"
	 "    frag_color0.y = float(lc2_half(_109 * float(lc2_half(float(_103.y) * varying_2.y)))) * (varying_5.y + (-log2(_63.y)));\n"
	 "    frag_color0.z = float(lc2_half(_109 * float(lc2_half(float(unpackFloat2x16(_78).x) * varying_2.z)))) * (varying_5.z + (-log2(_63.z)));\n"
	 "    frag_color0.w = _109;\n"
	 "}\n"
	 "", 1},
};

struct mm_shader_uniform {const char *name;unsigned stage,binding,offset,size,components,word_boolean,word_int,word_array;};
struct mm_shader_sampler {const char *name;unsigned stage,binding,offset,size_query,texel_fetch_bits,cpu_view;};
struct mm_shader_attribute {const char *name;unsigned location,kind;};
struct mm_shader_binding {
 const char *sha256,*error;unsigned control_size,code_size;
 unsigned uniform_count,sampler_count,attribute_count,color_write_mask,requires_fragment_highp,requires_fragment_mediump,wave_contract;
 unsigned varying_read_masks[8],varying_write_masks[8];
 uint8_t code_hash[32],control_hash[32];
 struct mm_shader_uniform uniforms[64];struct mm_shader_sampler samplers[8];struct mm_shader_attribute attributes[16];
};
static const struct mm_shader_binding nvn_megaman_shader_bindings[]={
 /* 0 dump-128077a9 fragment */
 {.sha256="128077a9d45399940bbcabfdefa45075",.error=NULL,.control_size=2176,.code_size=512,.sampler_count=1,.attribute_count=3,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=1,.uniforms={{.name="c3",.stage=1,.binding=0,.offset=0,.size=65536,.components=4,.word_boolean=0,.word_int=0,.word_array=4096}},
  .varying_read_masks={3,1,15,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0x12,0x80,0x77,0xa9,0xd4,0x53,0x99,0x94,0x0b,0xbc,0xab,0xfd,0xef,0xa4,0x50,0x75,0xcc,0x67,0x3f,0x41,0x78,0xbc,0xbc,0x41,0xbb,0xe9,0xd0,0x88,0x36,0x24,0x2c,0x89},.control_hash={0x14,0x1d,0xae,0x07,0x0e,0x83,0xe1,0x98,0x3b,0xdf,0x1f,0xea,0x7b,0xad,0xe8,0x4b,0x31,0x83,0xa1,0x50,0x26,0x4e,0x4d,0xd7,0x1a,0x67,0x4b,0xc1,0x81,0xc1,0xf0,0x73},
  .samplers={{.name="fs_tex0_20",.stage=1,.binding=14,.offset=0,.size_query=1,.texel_fetch_bits=0,.cpu_view=0}},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr1",.location=1,.kind=0},{.name="in_attr2",.location=2,.kind=0}}},
 /* 1 dump-12e9d131 fragment */
 {.sha256="12e9d131b44fe77db32ff7aaa723630f",.error=NULL,.control_size=2176,.code_size=512,.sampler_count=1,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=1,.uniforms={{.name="c3",.stage=1,.binding=0,.offset=0,.size=65536,.components=4,.word_boolean=0,.word_int=0,.word_array=4096}},
  .varying_read_masks={15,3,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0x12,0xe9,0xd1,0x31,0xb4,0x4f,0xe7,0x7d,0xb3,0x2f,0xf7,0xaa,0xa7,0x23,0x63,0x0f,0x8d,0xed,0xb5,0xef,0x56,0x60,0x17,0xba,0x66,0x0c,0xf3,0x23,0x5b,0xc6,0x66,0xd6},.control_hash={0x87,0xe9,0x53,0x50,0xfc,0x67,0x21,0x10,0x6e,0x2b,0x0d,0x4a,0x61,0x63,0xd3,0xfe,0x6b,0x41,0x96,0x66,0xe3,0x94,0x8c,0x1c,0x49,0x23,0x15,0xb1,0xf2,0x0e,0xa4,0xd0},
  .samplers={{.name="fs_tex0_20",.stage=1,.binding=14,.offset=0,.size_query=1,.texel_fetch_bits=0,.cpu_view=0}},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr1",.location=1,.kind=0}}},
 /* 2 dump-14196b8e vertex */
 {.sha256="14196b8ee2157ff89e85f75ee57fe690",.error=NULL,.control_size=2176,.code_size=768,.sampler_count=0,.attribute_count=3,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=1,.uniforms={{.name="c3",.stage=0,.binding=0,.offset=0,.size=65536,.components=4,.word_boolean=0,.word_int=0,.word_array=4096}},
  .varying_read_masks={7,15,3,0,0,0,0,0},.varying_write_masks={15,3,0,0,0,0,0,0},
  .code_hash={0x14,0x19,0x6b,0x8e,0xe2,0x15,0x7f,0xf8,0x9e,0x85,0xf7,0x5e,0xe5,0x7f,0xe6,0x90,0xf8,0xc9,0xb4,0x96,0x6a,0xb0,0x67,0x5b,0xea,0x9e,0xcd,0x20,0x17,0xa5,0x67,0x1e},.control_hash={0xee,0x95,0xcc,0x78,0xd0,0x0e,0xd0,0xe6,0xc2,0x2f,0x6b,0x9f,0x2f,0x56,0x63,0x3c,0x95,0x5e,0x0e,0x45,0x91,0x85,0x76,0x09,0xa3,0x58,0x3c,0x0c,0x18,0x2d,0xaa,0x3d},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr1",.location=1,.kind=0},{.name="in_attr2",.location=2,.kind=0}}},
 /* 3 dump-1792425422-0 fragment */
 {.sha256="d032944a8929b2cc5364e1df7f02f38a",.error=NULL,.control_size=2176,.code_size=768,.sampler_count=1,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=0,.uniforms={},
  .varying_read_masks={0,3,0,8,0,0,0,0},.varying_write_masks={0,0,0,0,0,0,0,0},
  .code_hash={0xd0,0x32,0x94,0x4a,0x89,0x29,0xb2,0xcc,0x53,0x64,0xe1,0xdf,0x7f,0x02,0xf3,0x8a,0x7f,0x31,0xd8,0x22,0x5f,0xe0,0x02,0xec,0xad,0x35,0x14,0x8f,0x3c,0xac,0xf9,0x68},.control_hash={0x8c,0x4f,0xe3,0x42,0x81,0xe7,0x46,0x7c,0x72,0x81,0x8a,0x14,0x81,0x90,0x2a,0x58,0x09,0x24,0xda,0x35,0x7e,0x05,0xb6,0x64,0x5b,0x5d,0x70,0x3e,0x3d,0x81,0x23,0xff},
  .samplers={{.name="fs_tex0_20",.stage=1,.binding=14,.offset=0,.size_query=1,.texel_fetch_bits=0,.cpu_view=0}},
  .attributes={{.name="in_attr1",.location=1,.kind=0},{.name="in_attr3",.location=3,.kind=0}}},
 /* 4 dump-2991ad4b fragment */
 {.sha256="2991ad4bcf25b8351ded83a14cc8c448",.error=NULL,.control_size=2176,.code_size=512,.sampler_count=1,.attribute_count=4,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=0,.uniforms={},
  .varying_read_masks={3,3,3,3,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0x29,0x91,0xad,0x4b,0xcf,0x25,0xb8,0x35,0x1d,0xed,0x83,0xa1,0x4c,0xc8,0xc4,0x48,0xb1,0xbf,0x2b,0x4a,0xcf,0x86,0x2b,0xf3,0x42,0x44,0x8d,0x1e,0xd3,0x84,0xce,0x50},.control_hash={0x25,0xa3,0x39,0xf6,0x00,0x3d,0x30,0xb4,0xde,0x2f,0x29,0x46,0xd2,0xfc,0xee,0xc7,0x0b,0x06,0x17,0x39,0x12,0xf5,0x63,0x91,0xd0,0x64,0x02,0x85,0xb4,0x07,0x0a,0x2e},
  .samplers={{.name="fs_tex0_20",.stage=1,.binding=14,.offset=0,.size_query=1,.texel_fetch_bits=0,.cpu_view=0}},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr1",.location=1,.kind=0},{.name="in_attr2",.location=2,.kind=0},{.name="in_attr3",.location=3,.kind=0}}},
 /* 5 dump-29d0db82 vertex */
 {.sha256="29d0db82b353bb6105f047d41637307f",.error=NULL,.control_size=2176,.code_size=2816,.sampler_count=0,.attribute_count=4,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=3,.uniforms={{.name="c0_1",.stage=0,.binding=0,.offset=0,.size=65536,.components=4,.word_boolean=0,.word_int=0,.word_array=4096},{.name="c1_3",.stage=0,.binding=1,.offset=0,.size=65536,.components=4,.word_boolean=0,.word_int=0,.word_array=4096},{.name="c3_3",.stage=0,.binding=2,.offset=0,.size=65536,.components=4,.word_boolean=0,.word_int=0,.word_array=4096}},
  .varying_read_masks={15,7,15,3,0,0,0,0},.varying_write_masks={0,3,0,15,0,0,0,0},
  .code_hash={0x29,0xd0,0xdb,0x82,0xb3,0x53,0xbb,0x61,0x05,0xf0,0x47,0xd4,0x16,0x37,0x30,0x7f,0xdb,0x24,0xfe,0x48,0x72,0x3c,0x22,0x31,0xe5,0x97,0x8b,0x3b,0xb5,0xd5,0xf1,0xd2},.control_hash={0x8b,0x4a,0x63,0xc3,0x7a,0xb9,0x21,0xa5,0x77,0x3d,0x05,0x9b,0x40,0x69,0x47,0xd7,0x4c,0x75,0xaf,0x25,0x5a,0x5c,0xba,0x52,0x44,0x07,0x2c,0x33,0xfd,0x88,0x25,0xbf},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr1",.location=1,.kind=0},{.name="in_attr2",.location=2,.kind=0},{.name="in_attr3",.location=3,.kind=0}}},
 /* 6 dump-33650b4b fragment */
 {.sha256="33650b4b250293b5c244b5b33e62a77c",.error=NULL,.control_size=2176,.code_size=1024,.sampler_count=2,.attribute_count=1,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=1,.uniforms={{.name="c3_1",.stage=1,.binding=1,.offset=0,.size=65536,.components=4,.word_boolean=0,.word_int=0,.word_array=4096}},
  .varying_read_masks={15,0,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0x33,0x65,0x0b,0x4b,0x25,0x02,0x93,0xb5,0xc2,0x44,0xb5,0xb3,0x3e,0x62,0xa7,0x7c,0x1f,0x03,0xed,0x85,0x71,0xac,0x3f,0xfd,0xda,0x93,0x68,0x34,0x7b,0xdc,0x61,0x66},.control_hash={0x7a,0x38,0xf8,0xcc,0x64,0x64,0xed,0xcb,0x26,0x5c,0x68,0x22,0x70,0x57,0x7a,0x3a,0x9b,0x46,0x68,0xac,0xf4,0x9d,0x26,0xee,0x9c,0x38,0x8b,0xdd,0x25,0x7b,0xbc,0x01},
  .samplers={{.name="fs_tex0_20",.stage=1,.binding=14,.offset=0,.size_query=1,.texel_fetch_bits=0,.cpu_view=0},{.name="fs_tex0_28",.stage=1,.binding=14,.offset=8,.size_query=1,.texel_fetch_bits=0,.cpu_view=0}},
  .attributes={{.name="in_attr0",.location=0,.kind=0}}},
 /* 7 dump-3a41323d vertex */
 {.sha256="3a41323d0d47e4265c808b26327df78e",.error=NULL,.control_size=2176,.code_size=1024,.sampler_count=0,.attribute_count=3,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=1,.uniforms={{.name="c4",.stage=0,.binding=0,.offset=0,.size=65536,.components=4,.word_boolean=0,.word_int=0,.word_array=4096}},
  .varying_read_masks={7,15,15,0,0,0,0,0},.varying_write_masks={15,1,15,0,0,0,0,0},
  .code_hash={0x3a,0x41,0x32,0x3d,0x0d,0x47,0xe4,0x26,0x5c,0x80,0x8b,0x26,0x32,0x7d,0xf7,0x8e,0x82,0x8a,0x2a,0xab,0xb9,0x01,0xef,0x5f,0xf0,0x06,0x9d,0xf8,0xad,0x19,0x0c,0x56},.control_hash={0xf4,0x45,0x58,0x4b,0x81,0x84,0x6d,0x9a,0x06,0x14,0x84,0xaa,0xb0,0x39,0x64,0xd7,0x33,0xda,0x78,0xec,0xf3,0x99,0x43,0xeb,0x78,0x70,0x05,0xf0,0xd6,0xec,0x0a,0xbb},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr1",.location=1,.kind=0},{.name="in_attr2",.location=2,.kind=0}}},
 /* 8 dump-3a75a7d0 vertex */
 {.sha256="3a75a7d07d489830954eabc424a380db",.error=NULL,.control_size=2176,.code_size=768,.sampler_count=0,.attribute_count=1,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=1,.uniforms={{.name="c3",.stage=0,.binding=0,.offset=0,.size=65536,.components=4,.word_boolean=0,.word_int=0,.word_array=4096}},
  .varying_read_masks={7,0,0,0,0,0,0,0},.varying_write_masks={0,0,0,0,0,0,0,0},
  .code_hash={0x3a,0x75,0xa7,0xd0,0x7d,0x48,0x98,0x30,0x95,0x4e,0xab,0xc4,0x24,0xa3,0x80,0xdb,0x64,0xa4,0x3c,0x2c,0x70,0xca,0x19,0x6d,0xf6,0xe0,0xbe,0x61,0x80,0x92,0x62,0x17},.control_hash={0x89,0x1f,0xf3,0x3d,0xb2,0xcb,0xae,0x81,0xdb,0xfe,0x7c,0x20,0x71,0x98,0x82,0x42,0xb2,0xa7,0xb3,0x1b,0x4a,0xc0,0xa5,0x53,0x9a,0xb3,0xb8,0x3c,0xe1,0x84,0x05,0x48},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=0}}},
 /* 9 dump-4b551bd7 fragment */
 {.sha256="4b551bd7a7732d410f3634916c38c1a6",.error=NULL,.control_size=2176,.code_size=512,.sampler_count=2,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=0,.uniforms={},
  .varying_read_masks={3,3,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0x4b,0x55,0x1b,0xd7,0xa7,0x73,0x2d,0x41,0x0f,0x36,0x34,0x91,0x6c,0x38,0xc1,0xa6,0x2d,0x9e,0x87,0x81,0x9c,0x50,0xe5,0x4c,0x9f,0x58,0x60,0x7b,0x46,0x60,0x67,0x84},.control_hash={0x78,0x36,0x9a,0x4e,0x5c,0x8a,0xb4,0x9a,0xa7,0x3a,0xc7,0x00,0xd1,0x35,0x4e,0x8c,0x06,0xa9,0x6b,0xeb,0xc1,0x62,0x66,0x77,0x5b,0x4f,0x9c,0x07,0xcd,0x09,0x8b,0xdd},
  .samplers={{.name="fs_tex0_20",.stage=1,.binding=14,.offset=0,.size_query=1,.texel_fetch_bits=0,.cpu_view=0},{.name="fs_tex0_28",.stage=1,.binding=14,.offset=8,.size_query=1,.texel_fetch_bits=0,.cpu_view=0}},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr1",.location=1,.kind=0}}},
 /* 10 dump-56844c6b vertex */
 {.sha256="56844c6ba737e9ef8558ff6f0fb935e8",.error=NULL,.control_size=2176,.code_size=1024,.sampler_count=0,.attribute_count=3,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=1,.uniforms={{.name="c3",.stage=0,.binding=0,.offset=0,.size=65536,.components=4,.word_boolean=0,.word_int=0,.word_array=4096}},
  .varying_read_masks={7,15,3,0,0,0,0,0},.varying_write_masks={15,3,0,0,0,0,0,0},
  .code_hash={0x56,0x84,0x4c,0x6b,0xa7,0x37,0xe9,0xef,0x85,0x58,0xff,0x6f,0x0f,0xb9,0x35,0xe8,0x67,0xfe,0x26,0xfa,0x0a,0xb8,0xbe,0x1d,0x65,0xf2,0x12,0x5a,0xb3,0x27,0xc4,0x8f},.control_hash={0xf8,0x2a,0x0a,0xef,0x7d,0x74,0xf5,0x2a,0xac,0x7a,0xf8,0x30,0x33,0x6f,0x64,0x71,0xdd,0x88,0x81,0x2d,0x9b,0xed,0xbd,0x5d,0x06,0x27,0x72,0x52,0x4e,0xbd,0x05,0x64},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr1",.location=1,.kind=0},{.name="in_attr2",.location=2,.kind=0}}},
 /* 11 dump-6054acba vertex */
 {.sha256="6054acba873a0922637dff386f4e1313",.error=NULL,.control_size=2176,.code_size=768,.sampler_count=0,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=1,.uniforms={{.name="c4",.stage=0,.binding=0,.offset=0,.size=65536,.components=4,.word_boolean=0,.word_int=0,.word_array=4096}},
  .varying_read_masks={7,3,0,0,0,0,0,0},.varying_write_masks={3,0,0,0,0,0,0,0},
  .code_hash={0x60,0x54,0xac,0xba,0x87,0x3a,0x09,0x22,0x63,0x7d,0xff,0x38,0x6f,0x4e,0x13,0x13,0xf4,0x53,0xe0,0xe7,0xc2,0x3a,0x02,0x61,0x06,0x74,0x4e,0xaf,0xb7,0xc2,0xb9,0x9a},.control_hash={0xca,0xd4,0x66,0x26,0x1f,0x04,0xa7,0x1f,0x88,0x49,0x9c,0x01,0xf8,0xef,0x35,0x6f,0x1f,0xcf,0x28,0xfe,0x9e,0xb1,0x07,0xba,0x4e,0x67,0xb7,0x74,0x66,0xe4,0x42,0x2d},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr1",.location=1,.kind=0}}},
 /* 12 dump-6a930d0e vertex */
 {.sha256="6a930d0edea444e0a29d3db880fe7620",.error=NULL,.control_size=2176,.code_size=1024,.sampler_count=0,.attribute_count=3,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=1,.uniforms={{.name="c4",.stage=0,.binding=1,.offset=0,.size=65536,.components=4,.word_boolean=0,.word_int=0,.word_array=4096}},
  .varying_read_masks={15,15,3,0,0,0,0,0},.varying_write_masks={15,15,3,0,0,0,0,0},
  .code_hash={0x6a,0x93,0x0d,0x0e,0xde,0xa4,0x44,0xe0,0xa2,0x9d,0x3d,0xb8,0x80,0xfe,0x76,0x20,0x3b,0x4f,0xa1,0x2a,0xa9,0x59,0xfa,0x8d,0xfb,0xcb,0x7b,0x00,0x1c,0xee,0x71,0xdd},.control_hash={0xcf,0x5e,0x12,0x22,0x15,0xb4,0x07,0x4a,0x22,0x8c,0x8b,0x1c,0x4c,0xf9,0xe3,0x95,0xd5,0x28,0x35,0xe4,0x06,0x5f,0x42,0x9f,0x67,0x22,0xfc,0x6c,0x4a,0x67,0x5f,0x76},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr1",.location=1,.kind=0},{.name="in_attr2",.location=2,.kind=0}}},
 /* 13 dump-7227c812 fragment */
 {.sha256="7227c812dba30ea82b90fc43945f4156",.error=NULL,.control_size=2176,.code_size=512,.sampler_count=1,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=0,.uniforms={},
  .varying_read_masks={15,15,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0x72,0x27,0xc8,0x12,0xdb,0xa3,0x0e,0xa8,0x2b,0x90,0xfc,0x43,0x94,0x5f,0x41,0x56,0xfe,0xa1,0xc4,0xef,0xaf,0x44,0x67,0xda,0x8c,0x5f,0x10,0x2b,0x30,0xf2,0x15,0x88},.control_hash={0x73,0x82,0xe6,0x2c,0x83,0x56,0xa7,0xb0,0x25,0x44,0xd9,0xc5,0x79,0x02,0x4b,0x5e,0x8d,0xc4,0xc8,0x8b,0xa5,0xc8,0x28,0xda,0x0a,0x9b,0xfb,0x70,0xfc,0xb1,0x2b,0x32},
  .samplers={{.name="fs_tex0_20",.stage=1,.binding=14,.offset=0,.size_query=1,.texel_fetch_bits=0,.cpu_view=0}},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr1",.location=1,.kind=0}}},
 /* 14 dump-800121db fragment */
 {.sha256="800121db9124384d3d3fd2c0452b3311",.error=NULL,.control_size=2176,.code_size=512,.sampler_count=1,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=1,.uniforms={{.name="c3",.stage=1,.binding=0,.offset=0,.size=65536,.components=4,.word_boolean=0,.word_int=0,.word_array=4096}},
  .varying_read_masks={15,0,3,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0x80,0x01,0x21,0xdb,0x91,0x24,0x38,0x4d,0x3d,0x3f,0xd2,0xc0,0x45,0x2b,0x33,0x11,0x16,0x7d,0x25,0x54,0x6e,0xfd,0x1d,0x53,0x81,0x11,0xfa,0xf3,0x55,0xdf,0x3c,0x1b},.control_hash={0xa9,0xad,0x70,0xc6,0xe7,0x9b,0xfe,0xeb,0x5e,0x23,0x24,0x5b,0x18,0xd1,0x97,0xe5,0x84,0x68,0x94,0x55,0xa9,0xfd,0xd3,0xb1,0x19,0x3a,0x37,0xe3,0x30,0x66,0xd6,0xae},
  .samplers={{.name="fs_tex0_20",.stage=1,.binding=14,.offset=0,.size_query=1,.texel_fetch_bits=0,.cpu_view=0}},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr2",.location=2,.kind=0}}},
 /* 15 dump-815bc387 fragment */
 {.sha256="815bc3875d5ebee554109af31f5502e8",.error=NULL,.control_size=2176,.code_size=256,.sampler_count=0,.attribute_count=0,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=0,.uniforms={},
  .varying_read_masks={0,0,0,0,0,0,0,0},.varying_write_masks={0,0,0,0,0,0,0,0},
  .code_hash={0x81,0x5b,0xc3,0x87,0x5d,0x5e,0xbe,0xe5,0x54,0x10,0x9a,0xf3,0x1f,0x55,0x02,0xe8,0x3c,0x24,0x50,0x87,0x28,0xa1,0xc9,0x6f,0x9d,0x2e,0xaf,0x72,0x0e,0x88,0x8e,0x2f},.control_hash={0x55,0x77,0x4a,0x1e,0x13,0x4b,0x14,0xb2,0x40,0xd4,0x92,0xb2,0x67,0x5c,0x1b,0xea,0xfb,0x58,0xe7,0x96,0x64,0x2a,0xcf,0xcf,0xe2,0xd0,0xc1,0xdc,0x28,0x4f,0x8f,0x11},
  .samplers={},
  .attributes={}},
 /* 16 dump-8af77a17 vertex */
 {.sha256="8af77a177b7838819ff46bb634747d44",.error=NULL,.control_size=2176,.code_size=2048,.sampler_count=0,.attribute_count=4,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=1,.uniforms={{.name="c4_1",.stage=0,.binding=1,.offset=0,.size=65536,.components=4,.word_boolean=0,.word_int=0,.word_array=4096}},
  .varying_read_masks={7,7,15,3,0,0,0,0},.varying_write_masks={3,7,7,15,7,0,0,0},
  .code_hash={0x8a,0xf7,0x7a,0x17,0x7b,0x78,0x38,0x81,0x9f,0xf4,0x6b,0xb6,0x34,0x74,0x7d,0x44,0x06,0xbd,0x08,0xae,0x4a,0xd4,0xfd,0xe1,0xca,0x20,0x2f,0xe9,0xef,0x85,0x4a,0xb9},.control_hash={0x63,0x2e,0xc0,0x3a,0x6c,0xee,0x39,0xda,0x99,0xda,0xe2,0x10,0x0a,0x0f,0x27,0x1e,0x1c,0xc0,0xac,0xd7,0xa6,0x21,0x92,0x3f,0x1c,0x33,0x3b,0xb2,0xf3,0xff,0xb1,0xfd},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr1",.location=1,.kind=0},{.name="in_attr2",.location=2,.kind=0},{.name="in_attr3",.location=3,.kind=0}}},
 /* 17 dump-b5d846ce vertex */
 {.sha256="b5d846ce116ab86d1ae9e9a9fd3ddb9f",.error=NULL,.control_size=2176,.code_size=1024,.sampler_count=0,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=1,.uniforms={{.name="c3",.stage=0,.binding=0,.offset=0,.size=65536,.components=4,.word_boolean=0,.word_int=0,.word_array=4096}},
  .varying_read_masks={7,3,0,0,0,0,0,0},.varying_write_masks={3,3,3,3,0,0,0,0},
  .code_hash={0xb5,0xd8,0x46,0xce,0x11,0x6a,0xb8,0x6d,0x1a,0xe9,0xe9,0xa9,0xfd,0x3d,0xdb,0x9f,0x4f,0xa8,0xb5,0xfe,0x0a,0x86,0x7e,0x5e,0x8a,0xee,0xc5,0x42,0xc4,0x9c,0x3c,0x42},.control_hash={0x0c,0x84,0xa9,0xac,0x97,0xf6,0x4a,0xa1,0xf6,0x50,0x72,0xcd,0xe5,0xdc,0xb4,0xe9,0x7e,0xbd,0x99,0xe0,0x54,0x41,0x32,0x3c,0x3d,0xa3,0xd6,0xdc,0x0b,0xed,0x26,0x01},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr1",.location=1,.kind=0}}},
 /* 18 dump-b894e79b vertex */
 {.sha256="b894e79b9c9c0637db3d015e6cda1d93",.error=NULL,.control_size=2176,.code_size=768,.sampler_count=0,.attribute_count=3,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=1,.uniforms={{.name="c4",.stage=0,.binding=0,.offset=0,.size=65536,.components=4,.word_boolean=0,.word_int=0,.word_array=4096}},
  .varying_read_masks={7,15,3,0,0,0,0,0},.varying_write_masks={15,3,0,0,0,0,0,0},
  .code_hash={0xb8,0x94,0xe7,0x9b,0x9c,0x9c,0x06,0x37,0xdb,0x3d,0x01,0x5e,0x6c,0xda,0x1d,0x93,0x89,0x78,0x90,0x2b,0x1a,0x57,0xe3,0xdc,0x22,0x3a,0xeb,0x5e,0x1a,0xde,0x24,0xa9},.control_hash={0x27,0x3f,0xbd,0x13,0x1c,0xac,0x9e,0x51,0x06,0xc4,0xf9,0x47,0x77,0x4a,0x65,0xf8,0x99,0xd8,0x2a,0xd8,0x59,0x4b,0x21,0x4f,0xbb,0xed,0xa1,0xe5,0x2a,0xbc,0xf6,0xb5},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr1",.location=1,.kind=0},{.name="in_attr2",.location=2,.kind=0}}},
 /* 19 dump-c523448a fragment */
 {.sha256="c523448a188e019468627cb25b9a59af",.error=NULL,.control_size=2176,.code_size=1024,.sampler_count=1,.attribute_count=5,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=1,.uniforms={{.name="c3",.stage=1,.binding=0,.offset=0,.size=65536,.components=4,.word_boolean=0,.word_int=0,.word_array=4096}},
  .varying_read_masks={3,7,0,15,7,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0xc5,0x23,0x44,0x8a,0x18,0x8e,0x01,0x94,0x68,0x62,0x7c,0xb2,0x5b,0x9a,0x59,0xaf,0xc6,0xa9,0x1a,0x94,0x82,0xb5,0x13,0x68,0xc1,0xa1,0x8d,0xa4,0xa6,0x21,0xba,0x1e},.control_hash={0x71,0xbd,0x2d,0x6a,0x9d,0x63,0xd4,0x00,0x31,0x49,0x7b,0x5a,0x4f,0x22,0xd5,0x67,0x10,0x29,0x6e,0x20,0x62,0x23,0xed,0xd4,0x28,0x01,0x94,0xc2,0x0e,0x8f,0x52,0x44},
  .samplers={{.name="fs_tex0_20",.stage=1,.binding=14,.offset=0,.size_query=1,.texel_fetch_bits=0,.cpu_view=0}},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr1",.location=1,.kind=0},{.name="in_attr2",.location=2,.kind=0},{.name="in_attr3",.location=3,.kind=0},{.name="in_attr4",.location=4,.kind=0}}},
 /* 20 dump-d032944a fragment */
 {.sha256="d032944a8929b2cc5364e1df7f02f38a",.error=NULL,.control_size=2176,.code_size=768,.sampler_count=1,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=0,.uniforms={},
  .varying_read_masks={0,3,0,8,0,0,0,0},.varying_write_masks={0,0,0,0,0,0,0,0},
  .code_hash={0xd0,0x32,0x94,0x4a,0x89,0x29,0xb2,0xcc,0x53,0x64,0xe1,0xdf,0x7f,0x02,0xf3,0x8a,0x7f,0x31,0xd8,0x22,0x5f,0xe0,0x02,0xec,0xad,0x35,0x14,0x8f,0x3c,0xac,0xf9,0x68},.control_hash={0x8c,0x4f,0xe3,0x42,0x81,0xe7,0x46,0x7c,0x72,0x81,0x8a,0x14,0x81,0x90,0x2a,0x58,0x09,0x24,0xda,0x35,0x7e,0x05,0xb6,0x64,0x5b,0x5d,0x70,0x3e,0x3d,0x81,0x23,0xff},
  .samplers={{.name="fs_tex0_20",.stage=1,.binding=14,.offset=0,.size_query=1,.texel_fetch_bits=0,.cpu_view=0}},
  .attributes={{.name="in_attr1",.location=1,.kind=0},{.name="in_attr3",.location=3,.kind=0}}},
 /* 21 dump-e4fb4243 fragment */
 {.sha256="e4fb424329549ccd60aad17d772a2487",.error=NULL,.control_size=2176,.code_size=512,.sampler_count=1,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=1,.uniforms={{.name="c3",.stage=1,.binding=0,.offset=0,.size=65536,.components=4,.word_boolean=0,.word_int=0,.word_array=4096}},
  .varying_read_masks={15,15,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0xe4,0xfb,0x42,0x43,0x29,0x54,0x9c,0xcd,0x60,0xaa,0xd1,0x7d,0x77,0x2a,0x24,0x87,0xb4,0xe7,0x63,0x45,0x5f,0xc2,0x74,0xe7,0xe8,0x77,0x8b,0x66,0x9d,0x21,0xd8,0x61},.control_hash={0xb3,0x14,0x37,0x34,0x54,0x45,0x6f,0x87,0x73,0xf7,0xcf,0xfe,0x48,0x1e,0xa8,0x0b,0xd1,0xd9,0x84,0x17,0x4a,0x44,0x08,0xe3,0x56,0x27,0xad,0x90,0x19,0x5b,0x7d,0x62},
  .samplers={{.name="fs_tex0_20",.stage=1,.binding=14,.offset=0,.size_query=1,.texel_fetch_bits=0,.cpu_view=0}},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr1",.location=1,.kind=0}}},
 /* 22 dump-e6091e72 fragment */
 {.sha256="e6091e727431c3272e5d6b9198de23df",.error=NULL,.control_size=2176,.code_size=768,.sampler_count=1,.attribute_count=1,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=1,.uniforms={{.name="c3_1",.stage=1,.binding=1,.offset=0,.size=65536,.components=4,.word_boolean=0,.word_int=0,.word_array=4096}},
  .varying_read_masks={3,0,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0xe6,0x09,0x1e,0x72,0x74,0x31,0xc3,0x27,0x2e,0x5d,0x6b,0x91,0x98,0xde,0x23,0xdf,0x1e,0xd2,0xf6,0x61,0xcb,0xe9,0xa7,0x4e,0x4b,0x03,0x5d,0xc6,0xe2,0xaa,0x45,0x93},.control_hash={0x39,0x34,0x06,0x5f,0x96,0x2a,0xf2,0xed,0xe8,0x54,0xb2,0x3c,0xb4,0x5c,0x9f,0x7f,0x7c,0xe4,0x45,0xfb,0xcf,0x92,0xfa,0xbc,0x5c,0xc3,0x4a,0x37,0x5f,0xb3,0x6b,0x2e},
  .samplers={{.name="fs_tex0_20",.stage=1,.binding=14,.offset=0,.size_query=1,.texel_fetch_bits=0,.cpu_view=0}},
  .attributes={{.name="in_attr0",.location=0,.kind=0}}},
 /* 23 dump-f3327347 fragment */
 {.sha256="f3327347207307f4ac851f8f7cc24dcd",.error=NULL,.control_size=2176,.code_size=512,.sampler_count=1,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=0,.uniforms={},
  .varying_read_masks={15,3,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0xf3,0x32,0x73,0x47,0x20,0x73,0x07,0xf4,0xac,0x85,0x1f,0x8f,0x7c,0xc2,0x4d,0xcd,0xef,0xd5,0xd8,0x0c,0xda,0x44,0x0d,0x50,0xbd,0x82,0x7e,0x93,0x10,0x6e,0x90,0x1e},.control_hash={0xad,0x1a,0xa1,0x3d,0xa8,0x3c,0xf3,0x6e,0x48,0x9f,0x39,0x81,0x84,0x47,0x36,0x7e,0x6e,0x2f,0x31,0x87,0x72,0x4d,0x1a,0x90,0x16,0xbe,0xd4,0xc2,0x21,0x10,0x68,0xb3},
  .samplers={{.name="fs_tex0_20",.stage=1,.binding=14,.offset=0,.size_query=1,.texel_fetch_bits=0,.cpu_view=0}},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr1",.location=1,.kind=0}}},
 /* 24 main-86cac8 vertex */
 {.sha256="b3913c5cf5773c0e3a8d943f162b9d6d",.error=NULL,.control_size=2176,.code_size=256,.sampler_count=0,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=0,.uniforms={},
  .varying_read_masks={3,3,0,0,0,0,0,0},.varying_write_masks={3,0,0,0,0,0,0,0},
  .code_hash={0xb3,0x91,0x3c,0x5c,0xf5,0x77,0x3c,0x0e,0x3a,0x8d,0x94,0x3f,0x16,0x2b,0x9d,0x6d,0x94,0x29,0x7f,0x26,0x94,0x02,0x69,0x03,0x06,0x57,0x51,0x86,0xa5,0x6e,0x88,0xff},.control_hash={0xb3,0x0b,0x42,0xeb,0x5e,0x91,0xad,0xc2,0xa6,0x2a,0x80,0x57,0x07,0x92,0x3b,0x37,0x04,0xa7,0xee,0xfd,0x91,0x6c,0x04,0xd3,0xae,0x32,0x7c,0xf1,0x45,0x3a,0x8a,0x87},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr1",.location=1,.kind=0}}},
 /* 25 main-86d688 vertex */
 {.sha256="06fab867aa4c0d624751d868dda96664",.error=NULL,.control_size=2176,.code_size=256,.sampler_count=0,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=0,.uniforms={},
  .varying_read_masks={3,3,0,0,0,0,0,0},.varying_write_masks={3,0,0,0,0,0,0,0},
  .code_hash={0x06,0xfa,0xb8,0x67,0xaa,0x4c,0x0d,0x62,0x47,0x51,0xd8,0x68,0xdd,0xa9,0x66,0x64,0x9e,0x4b,0xda,0x51,0xcc,0x14,0x61,0xa6,0x3b,0xcf,0x51,0xff,0xcd,0x2a,0x5d,0xfb},.control_hash={0x23,0x80,0xf0,0xf0,0xec,0x50,0xa6,0xc2,0x49,0x97,0xf1,0xb0,0xae,0xa3,0x0a,0x89,0x3c,0xd4,0x31,0xbf,0xff,0x81,0xe3,0xd4,0xd9,0xa9,0x84,0xd6,0xfd,0xbf,0xbb,0x52},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr1",.location=1,.kind=0}}},
 /* 26 main-86e248 fragment */
 {.sha256="f7d68113daeff747cbbc1d54f1cbb208",.error=NULL,.control_size=2176,.code_size=512,.sampler_count=1,.attribute_count=1,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=0,.uniforms={},
  .varying_read_masks={0,15,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0xf7,0xd6,0x81,0x13,0xda,0xef,0xf7,0x47,0xcb,0xbc,0x1d,0x54,0xf1,0xcb,0xb2,0x08,0x6b,0xca,0xf9,0x64,0x2c,0x65,0x66,0x0e,0xb2,0xab,0x27,0x5f,0x52,0x6e,0xb9,0xdd},.control_hash={0x79,0x18,0x8e,0x3c,0xd6,0xde,0x6e,0xe9,0x26,0x8a,0x5e,0x77,0xd7,0xb9,0x65,0xfe,0xca,0xf6,0x85,0xd4,0x90,0xa5,0x78,0xe2,0xa1,0xb7,0xb5,0x24,0x1d,0x68,0x5b,0x10},
  .samplers={{.name="fs_tex0_20",.stage=1,.binding=14,.offset=0,.size_query=1,.texel_fetch_bits=0,.cpu_view=0}},
  .attributes={{.name="in_attr0",.location=0,.kind=0}}},
 /* 27 main-86ef08 fragment */
 {.sha256="51e9503e3e9e5ffc0c9b19852a5ba042",.error=NULL,.control_size=2176,.code_size=768,.sampler_count=1,.attribute_count=1,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=0,.uniforms={},
  .varying_read_masks={0,15,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0x51,0xe9,0x50,0x3e,0x3e,0x9e,0x5f,0xfc,0x0c,0x9b,0x19,0x85,0x2a,0x5b,0xa0,0x42,0xaf,0x6e,0xe6,0x1f,0x3d,0x63,0xef,0x5b,0x78,0x66,0x6f,0x35,0xd4,0xf0,0xcb,0x57},.control_hash={0x54,0xae,0xa6,0x5a,0xae,0xad,0x02,0x95,0xb2,0x4c,0x41,0x82,0x9d,0x9a,0x47,0xf5,0x41,0x19,0xb3,0xfd,0x9c,0x7a,0xd9,0x59,0x29,0x7c,0x27,0x36,0x4d,0x86,0x1a,0x94},
  .samplers={{.name="fs_tex0_20",.stage=1,.binding=14,.offset=0,.size_query=1,.texel_fetch_bits=0,.cpu_view=0}},
  .attributes={{.name="in_attr0",.location=0,.kind=0}}},
 /* 28 main-86fcc8 fragment */
 {.sha256="283a226c935b89dff3ba47a0dfe2b811",.error=NULL,.control_size=2176,.code_size=1024,.sampler_count=1,.attribute_count=1,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=0,.uniforms={},
  .varying_read_masks={0,15,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0x28,0x3a,0x22,0x6c,0x93,0x5b,0x89,0xdf,0xf3,0xba,0x47,0xa0,0xdf,0xe2,0xb8,0x11,0xde,0xfb,0xde,0x50,0x9c,0x64,0x63,0x07,0x1f,0xf5,0x01,0x84,0x0f,0x12,0x46,0x3a},.control_hash={0xd1,0x69,0x4f,0xdc,0xe3,0xfe,0x75,0xb4,0xa3,0x3c,0x2e,0x49,0xa1,0xa4,0xbf,0x8d,0xf0,0x7c,0x5c,0x11,0x1e,0xdb,0x89,0xf0,0x87,0x79,0x07,0x33,0x13,0x91,0x05,0x96},
  .samplers={{.name="fs_tex0_20",.stage=1,.binding=14,.offset=0,.size_query=1,.texel_fetch_bits=0,.cpu_view=0}},
  .attributes={{.name="in_attr0",.location=0,.kind=0}}},
 /* 29 main-870b88 fragment */
 {.sha256="4137e113105451ea591ecc3eed5477e6",.error=NULL,.control_size=2176,.code_size=512,.sampler_count=2,.attribute_count=1,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=0,.uniforms={},
  .varying_read_masks={0,15,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0x41,0x37,0xe1,0x13,0x10,0x54,0x51,0xea,0x59,0x1e,0xcc,0x3e,0xed,0x54,0x77,0xe6,0x95,0xdd,0xaf,0xbe,0xef,0x9f,0x8d,0x10,0x9f,0x0f,0xd0,0xfc,0x81,0x5d,0xac,0x08},.control_hash={0x9f,0x90,0x77,0x63,0xe1,0x36,0xc6,0x77,0xab,0x55,0xd7,0xf4,0x0a,0xfd,0xc8,0x0d,0x9b,0x1b,0x07,0x47,0xd7,0xb2,0x6d,0xd9,0x7f,0x65,0x5c,0x50,0xcd,0x9e,0x66,0xd9},
  .samplers={{.name="fs_tex0_20",.stage=1,.binding=14,.offset=0,.size_query=1,.texel_fetch_bits=0,.cpu_view=0},{.name="fs_tex0_20_1",.stage=1,.binding=14,.offset=0,.size_query=1,.texel_fetch_bits=0,.cpu_view=0}},
  .attributes={{.name="in_attr0",.location=0,.kind=0}}},
 /* 30 main-871848 fragment */
 {.sha256="49351413ea33c9c09fddb670ac293145",.error=NULL,.control_size=2176,.code_size=768,.sampler_count=2,.attribute_count=1,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=0,.uniforms={},
  .varying_read_masks={0,15,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0x49,0x35,0x14,0x13,0xea,0x33,0xc9,0xc0,0x9f,0xdd,0xb6,0x70,0xac,0x29,0x31,0x45,0xa5,0xa8,0x99,0xbf,0xd0,0x7d,0x77,0x92,0x56,0x37,0xbd,0x0b,0x3e,0x47,0x0f,0x0b},.control_hash={0xb4,0x4a,0x7f,0x2f,0x16,0x3a,0xb2,0x38,0x4f,0xce,0x52,0x4f,0x93,0x1e,0xc5,0x1b,0xca,0x89,0x31,0xb2,0x77,0xdc,0xfb,0xb0,0x13,0xde,0x4e,0x39,0xce,0x96,0xba,0xe3},
  .samplers={{.name="fs_tex0_20",.stage=1,.binding=14,.offset=0,.size_query=1,.texel_fetch_bits=0,.cpu_view=0},{.name="fs_tex0_20_1",.stage=1,.binding=14,.offset=0,.size_query=1,.texel_fetch_bits=0,.cpu_view=0}},
  .attributes={{.name="in_attr0",.location=0,.kind=0}}},
 /* 31 main-872608 fragment */
 {.sha256="7a92670073b5efd71bc427239f94ac3f",.error=NULL,.control_size=2176,.code_size=1024,.sampler_count=2,.attribute_count=1,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=0,.uniforms={},
  .varying_read_masks={0,15,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0x7a,0x92,0x67,0x00,0x73,0xb5,0xef,0xd7,0x1b,0xc4,0x27,0x23,0x9f,0x94,0xac,0x3f,0x33,0xec,0xc2,0x53,0x73,0xf6,0x54,0xf0,0x72,0xc7,0xcc,0x86,0xaf,0x3a,0x5e,0x3f},.control_hash={0x6d,0x75,0x97,0x95,0xa4,0xee,0x23,0xf0,0xbf,0xf6,0x83,0x0c,0x40,0xda,0xbf,0xfa,0x89,0x26,0xa9,0x74,0xa2,0x1d,0xb2,0x9b,0x8b,0x99,0x94,0x0c,0xa8,0x99,0xe4,0xed},
  .samplers={{.name="fs_tex0_20",.stage=1,.binding=14,.offset=0,.size_query=1,.texel_fetch_bits=0,.cpu_view=0},{.name="fs_tex0_20_1",.stage=1,.binding=14,.offset=0,.size_query=1,.texel_fetch_bits=0,.cpu_view=0}},
  .attributes={{.name="in_attr0",.location=0,.kind=0}}},
 /* 32 main-8734c8 vertex */
 {.sha256="b3913c5cf5773c0e3a8d943f162b9d6d",.error=NULL,.control_size=2176,.code_size=256,.sampler_count=0,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=0,.uniforms={},
  .varying_read_masks={3,3,0,0,0,0,0,0},.varying_write_masks={3,0,0,0,0,0,0,0},
  .code_hash={0xb3,0x91,0x3c,0x5c,0xf5,0x77,0x3c,0x0e,0x3a,0x8d,0x94,0x3f,0x16,0x2b,0x9d,0x6d,0x94,0x29,0x7f,0x26,0x94,0x02,0x69,0x03,0x06,0x57,0x51,0x86,0xa5,0x6e,0x88,0xff},.control_hash={0x8d,0x52,0x7a,0x92,0x65,0x35,0xd6,0xb4,0xd5,0x38,0x78,0x4d,0xfc,0x99,0x93,0x83,0xc6,0x6c,0x32,0x76,0xc6,0x60,0xcb,0xa9,0x6c,0x43,0x09,0x6c,0x44,0x3b,0x36,0x13},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr1",.location=1,.kind=0}}},
 /* 33 main-874088 fragment */
 {.sha256="d97e37b36286e7b9110b2b0a5d85c3b8",.error=NULL,.control_size=2176,.code_size=256,.sampler_count=1,.attribute_count=1,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=0,.uniforms={},
  .varying_read_masks={3,0,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0xd9,0x7e,0x37,0xb3,0x62,0x86,0xe7,0xb9,0x11,0x0b,0x2b,0x0a,0x5d,0x85,0xc3,0xb8,0x44,0x71,0x68,0xed,0x31,0x5c,0xdc,0x36,0x8f,0x37,0x15,0x0f,0x34,0xc2,0x5b,0x9b},.control_hash={0xea,0xba,0x42,0x33,0xf4,0x38,0xa2,0xc8,0xf1,0x56,0x53,0x7d,0x8a,0xb8,0x60,0x4f,0x7a,0xa9,0xdf,0xb2,0x70,0xa0,0xb4,0x6f,0x7a,0x16,0x0e,0x3c,0x03,0x83,0x76,0x48},
  .samplers={{.name="fs_tex0_20",.stage=1,.binding=14,.offset=0,.size_query=1,.texel_fetch_bits=0,.cpu_view=0}},
  .attributes={{.name="in_attr0",.location=0,.kind=0}}},
 /* 34 dump-ef14df61 fragment */
 {.sha256="ef14df6126787c2d3334e1cf3b9d353a",.error=NULL,.control_size=2176,.code_size=512,.sampler_count=1,.attribute_count=1,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=1,.uniforms={{.name="c3",.stage=1,.binding=0,.offset=0,.size=65536,.components=4,.word_boolean=0,.word_int=0,.word_array=4096}},
  .varying_read_masks={15,0,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0xef,0x14,0xdf,0x61,0x26,0x78,0x7c,0x2d,0x33,0x34,0xe1,0xcf,0x3b,0x9d,0x35,0x3a,0x6b,0x49,0x09,0x55,0x49,0x13,0x2e,0xa0,0xe0,0xc7,0x3b,0x5a,0x63,0x54,0x5a,0x2b},.control_hash={0xa3,0xcf,0x1c,0xf3,0xc5,0x58,0x72,0x3a,0x88,0x68,0xff,0xbc,0x75,0xe1,0x54,0x14,0x34,0x75,0x78,0x85,0xf9,0x96,0x4d,0x25,0xf0,0x74,0xab,0xf9,0xd9,0xa8,0x9d,0xe5},
  .samplers={{.name="fs_tex0_20",.stage=1,.binding=14,.offset=0,.size_query=1,.texel_fetch_bits=0,.cpu_view=0}},
  .attributes={{.name="in_attr0",.location=0,.kind=0}}},
 /* 35 dump-06993fc8 fragment */
 {.sha256="06993fc833fade5562bb4dc7f0fe5449",.error=NULL,.control_size=2176,.code_size=768,.sampler_count=1,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=1,.uniforms={{.name="c3_1",.stage=1,.binding=1,.offset=0,.size=65536,.components=4,.word_boolean=0,.word_int=0,.word_array=4096}},
  .varying_read_masks={15,0,15,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0x06,0x99,0x3f,0xc8,0x33,0xfa,0xde,0x55,0x62,0xbb,0x4d,0xc7,0xf0,0xfe,0x54,0x49,0xf6,0x60,0xdb,0xb9,0x8c,0x2b,0x51,0x42,0x34,0x71,0x4e,0x1c,0xb6,0x92,0x2b,0xe6},.control_hash={0x3f,0xad,0x78,0x63,0x9a,0x79,0xf4,0xa7,0x0a,0xa2,0x16,0x09,0x37,0x58,0x98,0xcf,0xc8,0x27,0x64,0xc9,0x23,0xa0,0x6e,0x20,0x2d,0xdb,0xa5,0xc5,0x3f,0xf8,0xea,0xc7},
  .samplers={{.name="fs_tex0_20",.stage=1,.binding=14,.offset=0,.size_query=1,.texel_fetch_bits=0,.cpu_view=0}},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr2",.location=2,.kind=0}}},
 /* 36 dump-9fcf2f47 vertex */
 {.sha256="9fcf2f47d4306577930114aceabaf3dc",.error=NULL,.control_size=2176,.code_size=1536,.sampler_count=0,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=1,.uniforms={{.name="c3_1",.stage=0,.binding=1,.offset=0,.size=65536,.components=4,.word_boolean=0,.word_int=0,.word_array=4096}},
  .varying_read_masks={15,7,0,0,0,0,0,0},.varying_write_masks={0,0,0,0,0,0,0,0},
  .code_hash={0x9f,0xcf,0x2f,0x47,0xd4,0x30,0x65,0x77,0x93,0x01,0x14,0xac,0xea,0xba,0xf3,0xdc,0x3e,0x89,0x3f,0x22,0x70,0x7c,0x7b,0x60,0xb1,0x3a,0xf1,0x8b,0x85,0xd4,0x60,0xa9},.control_hash={0xe9,0x66,0x9f,0xb1,0xfa,0x1e,0xaa,0x26,0x47,0x00,0x0f,0x37,0x58,0x58,0xae,0xe8,0xf8,0xec,0x13,0x55,0x87,0x93,0xed,0xd2,0x51,0xf3,0xf2,0x76,0xf8,0xbe,0x77,0x1c},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr1",.location=1,.kind=0}}},
 /* 37 dump-2643d9aa fragment */
 {.sha256="2643d9aa4ae09b629cd47e66e00b87cf",.error=NULL,.control_size=2176,.code_size=256,.sampler_count=0,.attribute_count=0,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=0,.uniforms={},
  .varying_read_masks={0,0,0,0,0,0,0,0},.varying_write_masks={0,0,0,0,0,0,0,0},
  .code_hash={0x26,0x43,0xd9,0xaa,0x4a,0xe0,0x9b,0x62,0x9c,0xd4,0x7e,0x66,0xe0,0x0b,0x87,0xcf,0x4a,0xf9,0xaa,0xc7,0xf4,0x23,0x41,0xc1,0xfa,0x42,0xa6,0xce,0xb3,0x4b,0x67,0x3f},.control_hash={0xa2,0xcc,0x37,0xec,0x8c,0x6b,0x53,0x3a,0xa2,0x12,0x0f,0x6b,0xeb,0x40,0x52,0x52,0x76,0xfb,0x28,0x3f,0x1b,0x66,0x14,0x27,0x67,0xe9,0xff,0x87,0x13,0xa7,0xed,0xde},
  .samplers={},
  .attributes={}},
 /* 38 dump-588a3fad vertex */
 {.sha256="7a45f946fe5f9130ad89877e0862164b",.error=NULL,.control_size=2176,.code_size=1280,.sampler_count=0,.attribute_count=4,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=1,.uniforms={{.name="c4",.stage=0,.binding=1,.offset=0,.size=65536,.components=4,.word_boolean=0,.word_int=0,.word_array=4096}},
  .varying_read_masks={7,7,15,3,0,0,0,0},.varying_write_masks={3,7,7,15,7,0,0,0},
  .code_hash={0x7a,0x45,0xf9,0x46,0xfe,0x5f,0x91,0x30,0xad,0x89,0x87,0x7e,0x08,0x62,0x16,0x4b,0x80,0x57,0x34,0xd9,0xb1,0x73,0x90,0x93,0xe3,0x09,0x94,0x30,0xec,0x1b,0xbc,0xb7},.control_hash={0x58,0x8a,0x3f,0xad,0x73,0x06,0xd8,0x48,0xce,0x2f,0x3d,0x70,0xe8,0x5d,0x56,0x08,0xe7,0x97,0x3f,0x1c,0x09,0x3d,0x3b,0xb6,0x2b,0x94,0x0c,0x52,0xaa,0x44,0x19,0xe1},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr1",.location=1,.kind=0},{.name="in_attr2",.location=2,.kind=0},{.name="in_attr3",.location=3,.kind=0}}},
 /* 39 lighting fragment */
 {.sha256="e1d6ede5c901f5d441954877f35e624b",.error=NULL,.control_size=2176,.code_size=1280,.sampler_count=2,.attribute_count=4,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=1,.uniforms={{.name="c3",.stage=1,.binding=0,.offset=0,.size=65536,.components=4,.word_boolean=0,.word_int=0,.word_array=4096}},
  .varying_read_masks={15,15,15,15,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0xe1,0xd6,0xed,0xe5,0xc9,0x01,0xf5,0xd4,0x41,0x95,0x48,0x77,0xf3,0x5e,0x62,0x4b,0x59,0x1f,0x81,0x76,0x2c,0xa0,0xd9,0x62,0x34,0x32,0x06,0xa1,0xe9,0xd3,0x96,0xce},.control_hash={0x68,0x74,0x31,0x31,0x2e,0x0b,0x24,0x13,0xba,0xa9,0x41,0x9a,0x5d,0x8a,0x7d,0xc6,0x2c,0x02,0x45,0x69,0xbf,0x47,0x91,0x86,0x8c,0xac,0x82,0x49,0xd0,0x1c,0xca,0xd8},
  .samplers={{.name="fs_tex0_20",.stage=1,.binding=14,.offset=0,.size_query=1,.texel_fetch_bits=0,.cpu_view=0},{.name="fs_tex0_28",.stage=1,.binding=14,.offset=8,.size_query=1,.texel_fetch_bits=0,.cpu_view=0}},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr1",.location=1,.kind=0},{.name="in_attr2",.location=2,.kind=0},{.name="in_attr3",.location=3,.kind=0}}},
 /* 40 dump-84137e66 vertex */
 {.sha256="84137e66324271b0d35ebfa40eb3ed3a",.error=NULL,.control_size=2176,.code_size=1024,.sampler_count=0,.attribute_count=3,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=1,.uniforms={{.name="c3",.stage=0,.binding=0,.offset=0,.size=65536,.components=4,.word_boolean=0,.word_int=0,.word_array=4096}},
  .varying_read_masks={7,7,15,0,0,0,0,0},.varying_write_masks={7,7,15,0,0,0,0,0},
  .code_hash={0x84,0x13,0x7e,0x66,0x32,0x42,0x71,0xb0,0xd3,0x5e,0xbf,0xa4,0x0e,0xb3,0xed,0x3a,0x82,0xd0,0xe9,0x90,0xea,0x7c,0x53,0xe1,0x68,0x19,0x9c,0x91,0x72,0x71,0x91,0xf9},.control_hash={0x92,0x7f,0x18,0x41,0x53,0x45,0xdc,0x76,0x53,0x8f,0x23,0x47,0x87,0xa5,0xcb,0x30,0x8c,0x36,0x48,0x13,0xcf,0xb4,0x38,0x20,0xf4,0x01,0x9c,0x99,0x61,0xb1,0x65,0xbf},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr1",.location=1,.kind=0},{.name="in_attr2",.location=2,.kind=0}}},
 /* 41 dump-6b33f390 fragment */
 {.sha256="6b33f39005c64c58fff9689ea7c0fef9",.error=NULL,.control_size=2176,.code_size=256,.sampler_count=0,.attribute_count=1,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=0,.uniforms={},
  .varying_read_masks={15,0,0,0,0,0,0,0},.varying_write_masks={7,0,0,0,0,0,0,0},
  .code_hash={0x6b,0x33,0xf3,0x90,0x05,0xc6,0x4c,0x58,0xff,0xf9,0x68,0x9e,0xa7,0xc0,0xfe,0xf9,0x03,0xf7,0x53,0x3f,0xe7,0x6a,0xf1,0xdc,0xac,0xc3,0x0f,0xc8,0xcb,0x26,0xae,0xd9},.control_hash={0xa2,0x05,0x34,0x08,0x0b,0x72,0xd8,0xc5,0x0f,0x41,0xba,0xcb,0xf0,0x7b,0xfc,0x9e,0x37,0xd0,0xe6,0x55,0xfe,0xc1,0xac,0x34,0x23,0x7a,0x7b,0x73,0x76,0xe0,0x0c,0x45},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=0}}},
 /* 42 literal-vertex vertex */
 {.sha256="301af8ced90e7e506eb4d5ace0dfabd6",.error=NULL,.control_size=2176,.code_size=2304,.sampler_count=0,.attribute_count=4,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .uniform_count=1,.uniforms={{.name="c3_1",.stage=0,.binding=0,.offset=0,.size=65536,.components=4,.word_boolean=0,.word_int=0,.word_array=4096}},
  .varying_read_masks={7,7,15,3,0,0,0,0},.varying_write_masks={3,7,15,15,0,7,0,0},
  .code_hash={0x30,0x1a,0xf8,0xce,0xd9,0x0e,0x7e,0x50,0x6e,0xb4,0xd5,0xac,0xe0,0xdf,0xab,0xd6,0x54,0x53,0x55,0x7b,0xac,0x79,0xa7,0x4d,0xfe,0xba,0xce,0xf7,0x39,0x6b,0x30,0x98},.control_hash={0x13,0x07,0x78,0x97,0x91,0x80,0x8c,0x82,0xc0,0xb5,0xc7,0xa1,0x41,0xf3,0x4e,0xf4,0x78,0x0a,0x3e,0xc4,0x30,0x63,0x0b,0x15,0x88,0xb0,0x80,0x3e,0x4f,0xfb,0xa4,0xfe},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr1",.location=1,.kind=0},{.name="in_attr2",.location=2,.kind=0},{.name="in_attr3",.location=3,.kind=0}}},
 /* 43 half-color fragment */
 {.sha256="5ff482d48c9426db3f69965a3a6f96a3",.error=NULL,.control_size=2176,.code_size=768,.sampler_count=2,.attribute_count=4,.color_write_mask=15,.requires_fragment_highp=1,.requires_fragment_mediump=0,.wave_contract=0,
  .uniform_count=0,.uniforms={},
  .varying_read_masks={15,0,15,15,0,15,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0x5f,0xf4,0x82,0xd4,0x8c,0x94,0x26,0xdb,0x3f,0x69,0x96,0x5a,0x3a,0x6f,0x96,0xa3,0xfe,0x2e,0x99,0x4f,0x30,0x91,0x35,0xdd,0xf7,0x1c,0xda,0x1a,0x5f,0x18,0x4c,0x8a},.control_hash={0xcc,0xd3,0xfc,0xac,0xba,0x18,0x00,0x42,0xa8,0xfe,0x9c,0x99,0x1e,0x70,0x44,0x15,0x79,0x58,0xaa,0x0b,0x54,0xfa,0x58,0x2d,0x4f,0x8b,0xc2,0xeb,0x12,0x00,0xab,0x00},
  .samplers={{.name="fs_tex0_20",.stage=1,.binding=14,.offset=0,.size_query=1,.texel_fetch_bits=0,.cpu_view=0},{.name="fs_tex0_28",.stage=1,.binding=14,.offset=8,.size_query=1,.texel_fetch_bits=0,.cpu_view=0}},
  .attributes={{.name="in_attr0",.location=0,.kind=0},{.name="in_attr2",.location=2,.kind=0},{.name="in_attr3",.location=3,.kind=0},{.name="in_attr5",.location=5,.kind=0}}},
};
