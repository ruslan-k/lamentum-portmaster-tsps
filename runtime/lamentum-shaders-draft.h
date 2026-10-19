/* GENERATED DRAFT catalogue for Lamentum - our own translations, not game data.
 * Source: tools/build_lamentum_catalogue.py over the translate_lamentum_shaders.py workspace.
 * Every entry is a translation of the title's program; entries with an error string are
 * NOT translated and the runtime stops on them by design. */
#include <stddef.h>
#include <stdint.h>
#define ZERO_ZX_SHADER_PACKAGES 34
#define ZERO_SHADER_VARYING_SLOTS 8
#ifndef MOMO_SHADERS
#define MOMO_SHADERS 1
#endif
static const struct {const char *original,*gles;unsigned stage;} nvn_shader_sources[]={
	/* 0 dump-128077a9 fragment */
	{"", "\n"
	 "#version 300 es\n"
	 "precision mediump float;\n"
	 "#if defined(GL_AMD_gpu_shader_half_float)\n"
	 "#elif defined(GL_EXT_shader_explicit_arithmetic_types_float16)\n"
	 "#else\n"
	 "#error No extension available for FP16.\n"
	 "#endif\n"
	 "\n"
	 " uniform fs_cbuf_block_4f\n"
	 "{\n"
	 "    float data[16384];\n"
	 "} c3;\n"
	 "\n"
	 " uniform sampler2D fs_tex0_20;\n"
	 "\n"
	 "in vec4 in_attr0;\n"
	 "in vec4 in_attr1;\n"
	 "in vec4 in_attr2;\n"
	 "layout(location = 0) out vec4 frag_color0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    vec4 _56 = texture(fs_tex0_20, vec2(in_attr0.x, in_attr0.y));\n"
	 "    float _57 = _56.w;\n"
	 "    float16_t _93 = float16_t((_57 * c3.data[3u]) * in_attr2.w);\n"
	 "    frag_color0.x = float(_93 * float16_t(((in_attr2.w * in_attr2.x) * c3.data[0u]) * in_attr2.x)) * in_attr1.x;\n"
	 "    frag_color0.y = float(_93 * float16_t(((in_attr2.w * in_attr2.y) * c3.data[1u]) * in_attr2.y)) * in_attr1.x;\n"
	 "    frag_color0.z = float(_93 * float16_t(((in_attr2.w * in_attr2.z) * c3.data[2u]) * in_attr2.z)) * in_attr1.x;\n"
	 "    frag_color0.w = _57 * in_attr1.x;\n"
	 "}\n"
	 "", 1},
	/* 1 dump-12e9d131 fragment */
	{"", "\n"
	 "#version 300 es\n"
	 "precision mediump float;\n"
	 "uniform fs_cbuf_block_4f\n"
	 "{\n"
	 "    float data[16384];\n"
	 "} c3;\n"
	 "\n"
	 " uniform sampler2D fs_tex0_20;\n"
	 "\n"
	 "in vec4 in_attr0;\n"
	 "in vec4 in_attr1;\n"
	 "layout(location = 0) out vec4 frag_color0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    vec4 _51 = texture(fs_tex0_20, vec2(in_attr1.x, in_attr1.y));\n"
	 "    frag_color0.x = (_51.x * c3.data[0u]) * in_attr0.x;\n"
	 "    frag_color0.y = (_51.y * c3.data[1u]) * in_attr0.y;\n"
	 "    frag_color0.z = (_51.z * c3.data[2u]) * in_attr0.z;\n"
	 "    frag_color0.w = (_51.w * c3.data[3u]) * in_attr0.w;\n"
	 "}\n"
	 "", 1},
	/* 2 dump-14196b8e vertex */
	{"", "\n"
	 "#version 300 es\n"
	 "precision highp float;\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "uniform vs_cbuf_block_0f\n"
	 "{\n"
	 "    float data[16384];\n"
	 "} c3;\n"
	 "\n"
	 "layout(location = 0) in vec4 in_attr0;\n"
	 "layout(location = 1) in vec4 in_attr1;\n"
	 "layout(location = 2) in vec4 in_attr2;\n"
	 "out vec4 out_attr0;\n"
	 "out vec4 out_attr1;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr0 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr1 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr0.x = in_attr1.x;\n"
	 "    out_attr0.y = in_attr1.y;\n"
	 "    out_attr0.z = in_attr1.z;\n"
	 "    float _110 = fma(in_attr0.z, c3.data[9u], fma(in_attr0.x, c3.data[1u], in_attr0.y * c3.data[5u])) + c3.data[13u];\n"
	 "    out_attr0.w = in_attr1.w;\n"
	 "    out_attr1.x = fma(in_attr2.x, c3.data[32u], c3.data[34u]);\n"
	 "    float _122 = fma(in_attr0.z, c3.data[8u], fma(in_attr0.x, c3.data[0u], in_attr0.y * c3.data[4u])) + c3.data[12u];\n"
	 "    float _154 = fma(in_attr0.z, c3.data[10u], fma(in_attr0.x, c3.data[2u], in_attr0.y * c3.data[6u])) + c3.data[14u];\n"
	 "    float _158 = fma(in_attr0.z, c3.data[11u], fma(in_attr0.x, c3.data[3u], in_attr0.y * c3.data[7u])) + c3.data[15u];\n"
	 "    out_attr1.y = fma(in_attr2.y, c3.data[33u], c3.data[35u]);\n"
	 "    gl_Position.x = fma(_158, c3.data[28u], fma(_154, c3.data[24u], fma(_122, c3.data[16u], _110 * c3.data[20u])));\n"
	 "    gl_Position.y = fma(_158, c3.data[29u], fma(_154, c3.data[25u], fma(_122, c3.data[17u], _110 * c3.data[21u])));\n"
	 "    gl_Position.z = fma(_158, c3.data[30u], fma(_154, c3.data[26u], fma(_122, c3.data[18u], _110 * c3.data[22u])));\n"
	 "    gl_Position.w = fma(_158, c3.data[31u], fma(_154, c3.data[27u], fma(_122, c3.data[19u], _110 * c3.data[23u])));\n"
	 "}\n"
	 "", 0},
	/* 3 dump-1792425422-0 fragment */
	{"", "\n"
	 "#version 300 es\n"
	 "precision mediump float;\n"
	 "#if defined(GL_AMD_gpu_shader_half_float)\n"
	 "#elif defined(GL_EXT_shader_explicit_arithmetic_types_float16)\n"
	 "#else\n"
	 "#error No extension available for FP16.\n"
	 "#endif\n"
	 "\n"
	 " uniform fs_cbuf_block_4f\n"
	 "{\n"
	 "    float data[16384];\n"
	 "} c1;\n"
	 "\n"
	 " uniform sampler2D fs_tex0_20;\n"
	 " uniform sampler3D fs_tex0_28;\n"
	 "\n"
	 "in vec4 in_attr1;\n"
	 "in vec4 in_attr3;\n"
	 "layout(location = 0) out vec4 frag_color0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    if (float(unpackFloat2x16(packHalf2x16(vec2(texture(fs_tex0_28, vec3(gl_FragCoord.x * 0.25, gl_FragCoord.y * 0.25, float(float16_t(float(unpackFloat2x16(packHalf2x16(vec2(texture(fs_tex0_20, vec2(in_attr1.x, in_attr1.y)).w, 0.0))).x) * in_attr3.w) * unpackFloat2x16(998259584u).x))).w, 0.0))).x) < c1.data[0u])\n"
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
	 "#version 100\n"
	 "precision mediump float;\n"
	 "uniform sampler2D fs_tex0_20;\n"
	 "\n"
	 "varying vec4 in_attr0;\n"
	 "varying vec4 in_attr1;\n"
	 "varying vec4 in_attr2;\n"
	 "varying vec4 in_attr3;\n"
	 "varying vec4 gl_FragColor;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    vec4 _59 = texture(fs_tex0_20, vec2(in_attr1.x, in_attr1.y));\n"
	 "    vec4 _64 = texture(fs_tex0_20, vec2(in_attr2.x, in_attr2.y));\n"
	 "    vec4 _69 = texture(fs_tex0_20, vec2(in_attr3.x, in_attr3.y));\n"
	 "    vec4 _74 = texture(fs_tex0_20, vec2(in_attr0.x, in_attr0.y));\n"
	 "    gl_FragColor.x = max(max(_74.x, _59.x), max(_64.x, _69.x));\n"
	 "    gl_FragColor.y = min(min(_74.y, _59.y), min(_64.y, _69.y));\n"
	 "    gl_FragColor.z = _74.z;\n"
	 "    gl_FragColor.w = _74.w;\n"
	 "}\n"
	 "", 1},
	/* 5 dump-29d0db82 vertex */
	{"", "\n"
	 "#version 100\n"
	 "precision highp float;\n"
	 "/* TEST-ONLY substitute: NOT a translation of the title's program. Written so the\n"
	 " * replay can exercise draws/present while the real program is untranslated; the\n"
	 " * log marks it TEST and no picture claim may rest on it. */\n"
	 "attribute vec4 in_attr0;\n"
	 "attribute vec4 in_attr1;\n"
	 "varying vec4 out_attr0;\n"
	 "void main() { gl_Position = vec4(in_attr0.xy, in_attr0.z, 1.0); out_attr0 = in_attr1; }\n"
	 "", 0},
	/* 6 dump-33650b4b fragment */
	{"", "\n"
	 "#version 100\n"
	 "precision mediump float;\n"
	 "/* TEST-ONLY substitute: NOT a translation (see the vertex stage note). */\n"
	 "varying vec4 out_attr0;\n"
	 "void main() { gl_FragColor = vec4(0.5, 0.5, 0.5, 1.0); }\n"
	 "", 1},
	/* 7 dump-3a41323d vertex */
	{"", "\n"
	 "#version 300 es\n"
	 "precision highp float;\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "uniform vs_cbuf_block_0f\n"
	 "{\n"
	 "    float data[16384];\n"
	 "} c4;\n"
	 "\n"
	 "layout(location = 0) in vec4 in_attr0;\n"
	 "layout(location = 1) in vec4 in_attr1;\n"
	 "layout(location = 2) in vec4 in_attr2;\n"
	 "out vec4 out_attr0;\n"
	 "out vec4 out_attr1;\n"
	 "out vec4 out_attr2;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr0 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr1 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr2 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr0.x = in_attr2.x;\n"
	 "    out_attr2.y = in_attr1.y;\n"
	 "    float _121 = fma(in_attr0.z, c4.data[17u], fma(in_attr0.x, c4.data[9u], in_attr0.y * c4.data[13u])) + c4.data[21u];\n"
	 "    out_attr2.x = in_attr1.x;\n"
	 "    out_attr2.z = in_attr1.z;\n"
	 "    out_attr0.y = in_attr2.y;\n"
	 "    float _144 = fma(in_attr0.z, c4.data[16u], fma(in_attr0.x, c4.data[8u], in_attr0.y * c4.data[12u])) + c4.data[20u];\n"
	 "    out_attr0.z = in_attr2.z;\n"
	 "    out_attr0.w = in_attr2.w;\n"
	 "    out_attr2.w = in_attr1.w;\n"
	 "    float _180 = fma(in_attr0.z, c4.data[18u], fma(in_attr0.x, c4.data[10u], in_attr0.y * c4.data[14u])) + c4.data[22u];\n"
	 "    float _185 = fma(in_attr0.z, c4.data[19u], fma(in_attr0.x, c4.data[11u], in_attr0.y * c4.data[15u])) + c4.data[23u];\n"
	 "    out_attr1.x = fma(sin(c4.data[42u] * c4.data[3u]) * ((c4.data[40u] * c4.data[41u]) * cos(c4.data[42u] * c4.data[2u])), c4.data[7u], c4.data[40u]);\n"
	 "    gl_Position.x = fma(_185, c4.data[36u], fma(_180, c4.data[32u], fma(_144, c4.data[24u], _121 * c4.data[28u])));\n"
	 "    gl_Position.y = fma(_185, c4.data[37u], fma(_180, c4.data[33u], fma(_144, c4.data[25u], _121 * c4.data[29u])));\n"
	 "    gl_Position.z = fma(_185, c4.data[38u], fma(_180, c4.data[34u], fma(_144, c4.data[26u], _121 * c4.data[30u])));\n"
	 "    gl_Position.w = fma(_185, c4.data[39u], fma(_180, c4.data[35u], fma(_144, c4.data[27u], _121 * c4.data[31u])));\n"
	 "}\n"
	 "", 0},
	/* 8 dump-3a75a7d0 vertex */
	{"", "\n"
	 "#version 300 es\n"
	 "precision highp float;\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "uniform vs_cbuf_block_0f\n"
	 "{\n"
	 "    float data[16384];\n"
	 "} c3;\n"
	 "\n"
	 "layout(location = 0) in vec4 in_attr0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    float _90 = fma(in_attr0.z, c3.data[9u], fma(in_attr0.x, c3.data[1u], in_attr0.y * c3.data[5u])) + c3.data[13u];\n"
	 "    float _94 = fma(in_attr0.z, c3.data[8u], fma(in_attr0.x, c3.data[0u], in_attr0.y * c3.data[4u])) + c3.data[12u];\n"
	 "    float _114 = fma(in_attr0.z, c3.data[10u], fma(in_attr0.x, c3.data[2u], in_attr0.y * c3.data[6u])) + c3.data[14u];\n"
	 "    float _118 = fma(in_attr0.z, c3.data[11u], fma(in_attr0.x, c3.data[3u], in_attr0.y * c3.data[7u])) + c3.data[15u];\n"
	 "    gl_Position.x = fma(_118, c3.data[28u], fma(_114, c3.data[24u], fma(_94, c3.data[16u], _90 * c3.data[20u])));\n"
	 "    gl_Position.y = fma(_118, c3.data[29u], fma(_114, c3.data[25u], fma(_94, c3.data[17u], _90 * c3.data[21u])));\n"
	 "    gl_Position.z = fma(_118, c3.data[30u], fma(_114, c3.data[26u], fma(_94, c3.data[18u], _90 * c3.data[22u])));\n"
	 "    gl_Position.w = fma(_118, c3.data[31u], fma(_114, c3.data[27u], fma(_94, c3.data[19u], _90 * c3.data[23u])));\n"
	 "}\n"
	 "", 0},
	/* 9 dump-4b551bd7 fragment */
	{"", "\n"
	 "#version 100\n"
	 "precision mediump float;\n"
	 "uniform sampler2D fs_tex0_20;\n"
	 " uniform sampler2D fs_tex0_28;\n"
	 "\n"
	 "varying vec4 in_attr0;\n"
	 "varying vec4 in_attr1;\n"
	 "varying vec4 gl_FragColor;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    vec4 _50 = texture(fs_tex0_28, vec2(in_attr1.x, in_attr1.y));\n"
	 "    float _52 = _50.w;\n"
	 "    vec4 _55 = texture(fs_tex0_20, vec2(in_attr0.x, in_attr0.y));\n"
	 "    float _61 = 1.0 / _50.z;\n"
	 "    gl_FragColor.x = fma(_55.x, _61, -_52);\n"
	 "    gl_FragColor.y = fma(_55.y, _61, -_52);\n"
	 "    gl_FragColor.z = fma(_55.z, _61, -_52);\n"
	 "    gl_FragColor.w = _55.w;\n"
	 "}\n"
	 "", 1},
	/* 10 dump-56844c6b vertex */
	{"", "\n"
	 "#version 300 es\n"
	 "precision highp float;\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "uniform vs_cbuf_block_0f\n"
	 "{\n"
	 "    float data[16384];\n"
	 "} c3;\n"
	 "\n"
	 "layout(location = 0) in vec4 in_attr0;\n"
	 "layout(location = 1) in vec4 in_attr1;\n"
	 "layout(location = 2) in vec4 in_attr2;\n"
	 "out vec4 out_attr0;\n"
	 "out vec4 out_attr1;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr0 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr1 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    float _62 = in_attr0.y * c3.data[37u];\n"
	 "    float _69 = in_attr0.x * c3.data[36u];\n"
	 "    out_attr1.x = in_attr2.x;\n"
	 "    out_attr1.y = in_attr2.y;\n"
	 "    float _120 = fma(in_attr0.z, c3.data[9u], fma(_69, c3.data[1u], _62 * c3.data[5u])) + c3.data[13u];\n"
	 "    float _136 = fma(in_attr0.z, c3.data[8u], fma(_69, c3.data[0u], _62 * c3.data[4u])) + c3.data[12u];\n"
	 "    out_attr0.x = (in_attr1.x * c3.data[40u]) * c3.data[32u];\n"
	 "    out_attr0.y = (in_attr1.y * c3.data[41u]) * c3.data[33u];\n"
	 "    float _178 = fma(in_attr0.z, c3.data[10u], fma(_69, c3.data[2u], _62 * c3.data[6u])) + c3.data[14u];\n"
	 "    float _182 = fma(in_attr0.z, c3.data[11u], fma(_69, c3.data[3u], _62 * c3.data[7u])) + c3.data[15u];\n"
	 "    out_attr0.z = (in_attr1.z * c3.data[42u]) * c3.data[34u];\n"
	 "    out_attr0.w = (in_attr1.w * c3.data[43u]) * c3.data[35u];\n"
	 "    gl_Position.x = fma(_182, c3.data[28u], fma(_178, c3.data[24u], fma(_136, c3.data[16u], _120 * c3.data[20u])));\n"
	 "    gl_Position.y = fma(_182, c3.data[29u], fma(_178, c3.data[25u], fma(_136, c3.data[17u], _120 * c3.data[21u])));\n"
	 "    gl_Position.z = fma(_182, c3.data[30u], fma(_178, c3.data[26u], fma(_136, c3.data[18u], _120 * c3.data[22u])));\n"
	 "    gl_Position.w = fma(_182, c3.data[31u], fma(_178, c3.data[27u], fma(_136, c3.data[19u], _120 * c3.data[23u])));\n"
	 "}\n"
	 "", 0},
	/* 11 dump-6054acba vertex */
	{"", "\n"
	 "#version 300 es\n"
	 "precision highp float;\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "uniform vs_cbuf_block_0f\n"
	 "{\n"
	 "    float data[16384];\n"
	 "} c4;\n"
	 "\n"
	 "layout(location = 0) in vec4 in_attr0;\n"
	 "layout(location = 1) in vec4 in_attr1;\n"
	 "out vec4 out_attr0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr0 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr0.x = in_attr1.x;\n"
	 "    out_attr0.y = in_attr1.y;\n"
	 "    float _94 = fma(in_attr0.z, c4.data[9u], fma(in_attr0.x, c4.data[1u], in_attr0.y * c4.data[5u])) + c4.data[13u];\n"
	 "    float _102 = fma(in_attr0.z, c4.data[8u], fma(in_attr0.x, c4.data[0u], in_attr0.y * c4.data[4u])) + c4.data[12u];\n"
	 "    float _122 = fma(in_attr0.z, c4.data[10u], fma(in_attr0.x, c4.data[2u], in_attr0.y * c4.data[6u])) + c4.data[14u];\n"
	 "    float _142 = fma(in_attr0.z, c4.data[11u], fma(in_attr0.x, c4.data[3u], in_attr0.y * c4.data[7u])) + c4.data[15u];\n"
	 "    gl_Position.x = fma(_142, c4.data[28u], fma(_122, c4.data[24u], fma(_102, c4.data[16u], _94 * c4.data[20u])));\n"
	 "    gl_Position.y = fma(_142, c4.data[29u], fma(_122, c4.data[25u], fma(_102, c4.data[17u], _94 * c4.data[21u])));\n"
	 "    gl_Position.z = fma(_142, c4.data[30u], fma(_122, c4.data[26u], fma(_102, c4.data[18u], _94 * c4.data[22u])));\n"
	 "    gl_Position.w = fma(_142, c4.data[31u], fma(_122, c4.data[27u], fma(_102, c4.data[19u], _94 * c4.data[23u])));\n"
	 "}\n"
	 "", 0},
	/* 12 dump-6a930d0e vertex */
	{"", "\n"
	 "#version 300 es\n"
	 "precision highp float;\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "uniform vs_cbuf_block_0f\n"
	 "{\n"
	 "    float data[16384];\n"
	 "} c4;\n"
	 "\n"
	 "layout(location = 0) in vec4 in_attr0;\n"
	 "layout(location = 1) in vec4 in_attr1;\n"
	 "layout(location = 2) in vec4 in_attr2;\n"
	 "out vec4 out_attr0;\n"
	 "out vec4 out_attr1;\n"
	 "out vec4 out_attr2;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr0 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr1 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr2 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr1.z = in_attr0.z;\n"
	 "    out_attr1.y = in_attr0.y;\n"
	 "    out_attr2.x = fma(in_attr2.x, c4.data[36u], c4.data[38u]);\n"
	 "    out_attr1.x = in_attr0.x;\n"
	 "    out_attr1.w = in_attr0.w;\n"
	 "    float _117 = fma(in_attr0.z, c4.data[9u], fma(in_attr0.x, c4.data[1u], in_attr0.y * c4.data[5u])) + c4.data[13u];\n"
	 "    out_attr2.y = fma(in_attr2.y, c4.data[37u], c4.data[39u]);\n"
	 "    out_attr0.x = in_attr1.x * c4.data[32u];\n"
	 "    out_attr0.z = in_attr1.z * c4.data[34u];\n"
	 "    float _163 = fma(in_attr0.z, c4.data[8u], fma(in_attr0.x, c4.data[0u], in_attr0.y * c4.data[4u])) + c4.data[12u];\n"
	 "    float _171 = fma(in_attr0.z, c4.data[10u], fma(in_attr0.x, c4.data[2u], in_attr0.y * c4.data[6u])) + c4.data[14u];\n"
	 "    float _175 = fma(in_attr0.z, c4.data[11u], fma(in_attr0.x, c4.data[3u], in_attr0.y * c4.data[7u])) + c4.data[15u];\n"
	 "    out_attr0.y = in_attr1.y * c4.data[33u];\n"
	 "    out_attr0.w = in_attr1.w * c4.data[35u];\n"
	 "    gl_Position.x = fma(_175, c4.data[28u], fma(_171, c4.data[24u], fma(_163, c4.data[16u], _117 * c4.data[20u])));\n"
	 "    gl_Position.y = fma(_175, c4.data[29u], fma(_171, c4.data[25u], fma(_163, c4.data[17u], _117 * c4.data[21u])));\n"
	 "    gl_Position.z = fma(_175, c4.data[30u], fma(_171, c4.data[26u], fma(_163, c4.data[18u], _117 * c4.data[22u])));\n"
	 "    gl_Position.w = fma(_175, c4.data[31u], fma(_171, c4.data[27u], fma(_163, c4.data[19u], _117 * c4.data[23u])));\n"
	 "}\n"
	 "", 0},
	/* 13 dump-7227c812 fragment */
	{"", "\n"
	 "#version 100\n"
	 "precision mediump float;\n"
	 "/* TEST-ONLY substitute: NOT a translation (see the vertex stage note). */\n"
	 "varying vec4 out_attr0;\n"
	 "void main() { gl_FragColor = vec4(0.5, 0.5, 0.5, 1.0); }\n"
	 "", 1},
	/* 14 dump-800121db fragment */
	{"", "\n"
	 "#version 300 es\n"
	 "precision mediump float;\n"
	 "uniform fs_cbuf_block_4f\n"
	 "{\n"
	 "    float data[16384];\n"
	 "} c3;\n"
	 "\n"
	 " uniform sampler2D fs_tex0_20;\n"
	 "\n"
	 "in vec4 in_attr0;\n"
	 "in vec4 in_attr2;\n"
	 "layout(location = 0) out vec4 frag_color0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    vec4 _51 = texture(fs_tex0_20, vec2(in_attr2.x, in_attr2.y));\n"
	 "    frag_color0.x = (_51.x + c3.data[0u]) * in_attr0.x;\n"
	 "    frag_color0.y = (_51.y + c3.data[1u]) * in_attr0.y;\n"
	 "    frag_color0.z = (_51.z + c3.data[2u]) * in_attr0.z;\n"
	 "    frag_color0.w = (_51.w + c3.data[3u]) * in_attr0.w;\n"
	 "}\n"
	 "", 1},
	/* 15 dump-815bc387 fragment */
	{"", "\n"
	 "#version 100\n"
	 "precision mediump float;\n"
	 "varying vec4 gl_FragColor;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_FragColor.x = 1.0;\n"
	 "    gl_FragColor.y = 0.0;\n"
	 "    gl_FragColor.z = 1.0;\n"
	 "    gl_FragColor.w = 1.0;\n"
	 "}\n"
	 "", 1},
	/* 16 dump-8af77a17 vertex */
	{"", "\n"
	 "#version 300 es\n"
	 "precision highp float;\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "uniform vs_cbuf_block_0f\n"
	 "{\n"
	 "    float data[16384];\n"
	 "} c1;\n"
	 "\n"
	 " uniform c4\n"
	 "{\n"
	 "    float data[16384];\n"
	 "} c4_1;\n"
	 "\n"
	 "layout(location = 0) in vec4 in_attr0;\n"
	 "layout(location = 1) in vec4 in_attr1;\n"
	 "layout(location = 2) in vec4 in_attr2;\n"
	 "layout(location = 3) in vec4 in_attr3;\n"
	 "out vec4 out_attr0;\n"
	 "out vec4 out_attr1;\n"
	 "out vec4 out_attr2;\n"
	 "out vec4 out_attr3;\n"
	 "out vec4 out_attr4;\n"
	 "out vec4 out_attr5;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr0 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr1 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr2 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr3 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr4 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr5 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    float _93 = fma(in_attr1.z, c4_1.data[46u], fma(in_attr1.y, c4_1.data[45u], in_attr1.x * c4_1.data[44u]));\n"
	 "    float _101 = fma(in_attr1.z, c4_1.data[50u], fma(in_attr1.y, c4_1.data[49u], in_attr1.x * c4_1.data[48u]));\n"
	 "    float _106 = fma(in_attr1.z, c4_1.data[54u], fma(in_attr1.y, c4_1.data[53u], in_attr1.x * c4_1.data[52u]));\n"
	 "    float _110 = in_attr0.y * c4_1.data[81u];\n"
	 "    float _114 = in_attr0.x * c4_1.data[80u];\n"
	 "    float _125 = inversesqrt(fma(_106, _106, fma(_101, _101, _93 * _93)));\n"
	 "    float _145 = _93 * _125;\n"
	 "    float _146 = _101 * _125;\n"
	 "    float _147 = _106 * _125;\n"
	 "    float _169 = _145 * _146;\n"
	 "    float _170 = _146 * _147;\n"
	 "    float _171 = _145 * _147;\n"
	 "    float _178 = _147 * _147;\n"
	 "    float _248 = fma(_145, _145, -(_146 * _146));\n"
	 "    out_attr0.y = fma(in_attr3.y, c4_1.data[89u], c4_1.data[91u]);\n"
	 "    out_attr0.x = fma(in_attr3.x, c4_1.data[88u], c4_1.data[90u]);\n"
	 "    out_attr1.x = _145;\n"
	 "    out_attr1.y = _146;\n"
	 "    out_attr1.z = _147;\n"
	 "    out_attr5.w = 0.0;\n"
	 "    float _317 = fma(in_attr0.z, c4_1.data[37u], fma(_114, c4_1.data[29u], _110 * c4_1.data[33u])) + c4_1.data[41u];\n"
	 "    out_attr2.y = _317;\n"
	 "    float _330 = fma(in_attr0.z, c4_1.data[36u], fma(_114, c4_1.data[28u], _110 * c4_1.data[32u])) + c4_1.data[40u];\n"
	 "    out_attr2.x = _330;\n"
	 "    out_attr3.z = (in_attr2.z * c4_1.data[86u]) * c4_1.data[78u];\n"
	 "    out_attr3.y = (in_attr2.y * c4_1.data[85u]) * c4_1.data[77u];\n"
	 "    out_attr3.w = (in_attr2.w * c4_1.data[87u]) * c4_1.data[79u];\n"
	 "    float _380 = fma(in_attr0.z, c4_1.data[38u], fma(_114, c4_1.data[30u], _110 * c4_1.data[34u])) + c4_1.data[42u];\n"
	 "    out_attr2.z = _380;\n"
	 "    float _405 = fma(in_attr0.z, c4_1.data[39u], fma(_114, c4_1.data[31u], _110 * c4_1.data[35u])) + c4_1.data[43u];\n"
	 "    out_attr3.x = (in_attr2.x * c4_1.data[84u]) * c4_1.data[76u];\n"
	 "    gl_Position.x = fma(_405, c4_1.data[72u], fma(_380, c4_1.data[68u], fma(_330, c4_1.data[60u], _317 * c4_1.data[64u])));\n"
	 "    gl_Position.y = fma(_405, c4_1.data[73u], fma(_380, c4_1.data[69u], fma(_330, c4_1.data[61u], _317 * c4_1.data[65u])));\n"
	 "    gl_Position.z = fma(_405, c4_1.data[74u], fma(_380, c4_1.data[70u], fma(_330, c4_1.data[62u], _317 * c4_1.data[66u])));\n"
	 "    gl_Position.w = fma(_405, c4_1.data[75u], fma(_380, c4_1.data[71u], fma(_330, c4_1.data[63u], _317 * c4_1.data[67u])));\n"
	 "    out_attr4.x = max(0.0, fma(exp2(log2(max(0.0, fma(_248, c4_1.data[24u], fma(_171, c4_1.data[15u], fma(_178, c4_1.data[14u], fma(_170, c4_1.data[13u], _169 * c4_1.data[12u])))) + (fma(_147, c4_1.data[2u], fma(_146, c4_1.data[1u], _145 * c4_1.data[0u])) + c4_1.data[3u]))) * 0.4166666567325592041015625), c1.data[0u], -0.054999999701976776123046875));\n"
	 "    out_attr4.y = max(0.0, fma(exp2(log2(max(0.0, fma(_248, c4_1.data[25u], fma(_171, c4_1.data[19u], fma(_178, c4_1.data[18u], fma(_170, c4_1.data[17u], _169 * c4_1.data[16u])))) + (fma(_147, c4_1.data[6u], fma(_146, c4_1.data[5u], _145 * c4_1.data[4u])) + c4_1.data[7u]))) * 0.4166666567325592041015625), c1.data[0u], -0.054999999701976776123046875));\n"
	 "    out_attr4.z = max(0.0, fma(exp2(log2(max(0.0, fma(_248, c4_1.data[26u], fma(_171, c4_1.data[23u], fma(_178, c4_1.data[22u], fma(_170, c4_1.data[21u], _169 * c4_1.data[20u])))) + (fma(_147, c4_1.data[10u], fma(_146, c4_1.data[9u], _145 * c4_1.data[8u])) + c4_1.data[11u]))) * 0.4166666567325592041015625), c1.data[0u], -0.054999999701976776123046875));\n"
	 "}\n"
	 "", 0},
	/* 17 dump-b5d846ce vertex */
	{"", "\n"
	 "#version 300 es\n"
	 "precision highp float;\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "#if defined(GL_AMD_gpu_shader_half_float)\n"
	 "#elif defined(GL_EXT_shader_explicit_arithmetic_types_float16)\n"
	 "#else\n"
	 "#error No extension available for FP16.\n"
	 "#endif\n"
	 "\n"
	 " uniform vs_cbuf_block_0f\n"
	 "{\n"
	 "    float data[16384];\n"
	 "} c3;\n"
	 "\n"
	 "layout(location = 0) in vec4 in_attr0;\n"
	 "layout(location = 1) in vec4 in_attr1;\n"
	 "out vec4 out_attr0;\n"
	 "out vec4 out_attr1;\n"
	 "out vec4 out_attr2;\n"
	 "out vec4 out_attr3;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr0 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr1 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr2 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr3 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr0.x = fma(in_attr1.x, c3.data[32u], c3.data[34u]);\n"
	 "    out_attr1.x = fma(float(float16_t(in_attr1.x + float(unpackFloat2x16(0u).x))), c3.data[32u], c3.data[34u]);\n"
	 "    float _138 = fma(in_attr0.z, c3.data[9u], fma(in_attr0.x, c3.data[1u], in_attr0.y * c3.data[5u])) + c3.data[13u];\n"
	 "    out_attr0.y = fma(in_attr1.y, c3.data[33u], c3.data[35u]);\n"
	 "    float _151 = fma(float(float16_t(in_attr1.x + float(unpackFloat2x16(1006648320u).x))), c3.data[32u], c3.data[34u]);\n"
	 "    float _156 = fma(float(float16_t(in_attr1.y + float(unpackFloat2x16(1006648320u).x))), c3.data[33u], c3.data[35u]);\n"
	 "    out_attr2.x = _151;\n"
	 "    out_attr3.x = _151;\n"
	 "    out_attr2.y = fma(float(float16_t(in_attr1.y + float(unpackFloat2x16(0u).x))), c3.data[33u], c3.data[35u]);\n"
	 "    out_attr1.y = _156;\n"
	 "    out_attr3.y = _156;\n"
	 "    float _190 = fma(in_attr0.z, c3.data[8u], fma(in_attr0.x, c3.data[0u], in_attr0.y * c3.data[4u])) + c3.data[12u];\n"
	 "    float _202 = fma(in_attr0.z, c3.data[10u], fma(in_attr0.x, c3.data[2u], in_attr0.y * c3.data[6u])) + c3.data[14u];\n"
	 "    float _222 = fma(in_attr0.z, c3.data[11u], fma(in_attr0.x, c3.data[3u], in_attr0.y * c3.data[7u])) + c3.data[15u];\n"
	 "    gl_Position.x = fma(_222, c3.data[28u], fma(_202, c3.data[24u], fma(_190, c3.data[16u], _138 * c3.data[20u])));\n"
	 "    gl_Position.y = fma(_222, c3.data[29u], fma(_202, c3.data[25u], fma(_190, c3.data[17u], _138 * c3.data[21u])));\n"
	 "    gl_Position.z = fma(_222, c3.data[30u], fma(_202, c3.data[26u], fma(_190, c3.data[18u], _138 * c3.data[22u])));\n"
	 "    gl_Position.w = fma(_222, c3.data[31u], fma(_202, c3.data[27u], fma(_190, c3.data[19u], _138 * c3.data[23u])));\n"
	 "}\n"
	 "", 0},
	/* 18 dump-b894e79b vertex */
	{"", "\n"
	 "#version 300 es\n"
	 "precision highp float;\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "uniform vs_cbuf_block_0f\n"
	 "{\n"
	 "    float data[16384];\n"
	 "} c4;\n"
	 "\n"
	 "layout(location = 0) in vec4 in_attr0;\n"
	 "layout(location = 1) in vec4 in_attr1;\n"
	 "layout(location = 2) in vec4 in_attr2;\n"
	 "out vec4 out_attr0;\n"
	 "out vec4 out_attr1;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr0 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr1 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr0.x = in_attr1.x;\n"
	 "    out_attr0.y = in_attr1.y;\n"
	 "    out_attr0.z = in_attr1.z;\n"
	 "    float _110 = fma(in_attr0.z, c4.data[9u], fma(in_attr0.x, c4.data[1u], in_attr0.y * c4.data[5u])) + c4.data[13u];\n"
	 "    out_attr0.w = in_attr1.w;\n"
	 "    out_attr1.x = fma(in_attr2.x, c4.data[32u], c4.data[34u]);\n"
	 "    float _122 = fma(in_attr0.z, c4.data[8u], fma(in_attr0.x, c4.data[0u], in_attr0.y * c4.data[4u])) + c4.data[12u];\n"
	 "    float _154 = fma(in_attr0.z, c4.data[10u], fma(in_attr0.x, c4.data[2u], in_attr0.y * c4.data[6u])) + c4.data[14u];\n"
	 "    float _158 = fma(in_attr0.z, c4.data[11u], fma(in_attr0.x, c4.data[3u], in_attr0.y * c4.data[7u])) + c4.data[15u];\n"
	 "    out_attr1.y = fma(in_attr2.y, c4.data[33u], c4.data[35u]);\n"
	 "    gl_Position.x = fma(_158, c4.data[28u], fma(_154, c4.data[24u], fma(_122, c4.data[16u], _110 * c4.data[20u])));\n"
	 "    gl_Position.y = fma(_158, c4.data[29u], fma(_154, c4.data[25u], fma(_122, c4.data[17u], _110 * c4.data[21u])));\n"
	 "    gl_Position.z = fma(_158, c4.data[30u], fma(_154, c4.data[26u], fma(_122, c4.data[18u], _110 * c4.data[22u])));\n"
	 "    gl_Position.w = fma(_158, c4.data[31u], fma(_154, c4.data[27u], fma(_122, c4.data[19u], _110 * c4.data[23u])));\n"
	 "}\n"
	 "", 0},
	/* 19 dump-c523448a fragment */
	{"", "\n"
	 "#version 100\n"
	 "precision mediump float;\n"
	 "/* TEST-ONLY substitute: NOT a translation (see the vertex stage note). */\n"
	 "varying vec4 out_attr0;\n"
	 "void main() { gl_FragColor = vec4(0.5, 0.5, 0.5, 1.0); }\n"
	 "", 1},
	/* 20 dump-d032944a fragment */
	{"", "\n"
	 "#version 300 es\n"
	 "precision mediump float;\n"
	 "#if defined(GL_AMD_gpu_shader_half_float)\n"
	 "#elif defined(GL_EXT_shader_explicit_arithmetic_types_float16)\n"
	 "#else\n"
	 "#error No extension available for FP16.\n"
	 "#endif\n"
	 "\n"
	 " uniform fs_cbuf_block_4f\n"
	 "{\n"
	 "    float data[16384];\n"
	 "} c1;\n"
	 "\n"
	 " uniform sampler2D fs_tex0_20;\n"
	 " uniform sampler3D fs_tex0_28;\n"
	 "\n"
	 "in vec4 in_attr1;\n"
	 "in vec4 in_attr3;\n"
	 "layout(location = 0) out vec4 frag_color0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    if (float(unpackFloat2x16(packHalf2x16(vec2(texture(fs_tex0_28, vec3(gl_FragCoord.x * 0.25, gl_FragCoord.y * 0.25, float(float16_t(float(unpackFloat2x16(packHalf2x16(vec2(texture(fs_tex0_20, vec2(in_attr1.x, in_attr1.y)).w, 0.0))).x) * in_attr3.w) * unpackFloat2x16(998259584u).x))).w, 0.0))).x) < c1.data[0u])\n"
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
	 "#version 100\n"
	 "precision mediump float;\n"
	 "/* TEST-ONLY substitute: NOT a translation (see the vertex stage note). */\n"
	 "varying vec4 out_attr0;\n"
	 "void main() { gl_FragColor = vec4(0.5, 0.5, 0.5, 1.0); }\n"
	 "", 1},
	/* 22 dump-e6091e72 fragment */
	{"", "\n"
	 "#version 300 es\n"
	 "precision mediump float;\n"
	 "#define fma(a, b, c) ((a) * (b) + (c))\n"
	 "#if defined(GL_AMD_gpu_shader_half_float)\n"
	 "#elif defined(GL_EXT_shader_explicit_arithmetic_types_float16)\n"
	 "#else\n"
	 "#error No extension available for FP16.\n"
	 "#endif\n"
	 "\n"
	 " uniform fs_cbuf_block_4f\n"
	 "{\n"
	 "    float data[16384];\n"
	 "} c1;\n"
	 "\n"
	 " uniform c3\n"
	 "{\n"
	 "    float data[16384];\n"
	 "} c3_1;\n"
	 "\n"
	 " uniform sampler2D fs_tex0_20;\n"
	 "\n"
	 "in vec4 in_attr0;\n"
	 "layout(location = 0) out vec4 frag_color0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    vec4 _68 = texture(fs_tex0_20, vec2(fma(in_attr0.x, c3_1.data[0u], c3_1.data[2u]), fma(in_attr0.y, c3_1.data[1u], c3_1.data[3u])));\n"
	 "    float _72 = _68.w;\n"
	 "    float16_t _86 = float16_t(fma(_68.z, c1.data[2u], float(float16_t(fma(_68.y, c1.data[1u], float(float16_t(_68.x * c1.data[0u])))))));\n"
	 "    float _94 = float(fma(float16_t(_72 * float(_86)), unpackFloat2x16(1073758208u).x, _86));\n"
	 "    frag_color0.x = _94;\n"
	 "    frag_color0.y = _94;\n"
	 "    frag_color0.z = _94;\n"
	 "    frag_color0.w = _72;\n"
	 "}\n"
	 "", 1},
	/* 23 dump-f3327347 fragment */
	{"", "\n"
	 "#version 100\n"
	 "precision mediump float;\n"
	 "uniform sampler2D fs_tex0_20;\n"
	 "\n"
	 "varying vec4 in_attr0;\n"
	 "varying vec4 in_attr1;\n"
	 "varying vec4 gl_FragColor;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    vec4 _45 = texture(fs_tex0_20, vec2(in_attr1.x, in_attr1.y));\n"
	 "    gl_FragColor.x = (_45.x * 2.0) * in_attr0.x;\n"
	 "    gl_FragColor.y = (_45.y * 2.0) * in_attr0.y;\n"
	 "    gl_FragColor.z = (_45.z * 2.0) * in_attr0.z;\n"
	 "    gl_FragColor.w = (_45.w * 2.0) * in_attr0.w;\n"
	 "}\n"
	 "", 1},
	/* 24 main-86cac8 vertex */
	{"", "\n"
	 "#version 100\n"
	 "precision highp float;\n"
	 "attribute vec4 in_attr0;\n"
	 "attribute vec4 in_attr1;\n"
	 "varying vec4 out_attr0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr0 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    gl_Position.x = in_attr0.x;\n"
	 "    gl_Position.y = in_attr0.y;\n"
	 "    out_attr0.x = in_attr1.x;\n"
	 "    out_attr0.y = in_attr1.y;\n"
	 "}\n"
	 "", 0},
	/* 25 main-86d688 vertex */
	{"", "\n"
	 "#version 100\n"
	 "precision highp float;\n"
	 "attribute vec4 in_attr0;\n"
	 "attribute vec4 in_attr1;\n"
	 "varying vec4 out_attr0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr0 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    gl_Position.x = in_attr0.x;\n"
	 "    gl_Position.y = in_attr0.y;\n"
	 "    out_attr0.x = in_attr1.x;\n"
	 "    out_attr0.y = in_attr1.y;\n"
	 "    gl_Layer = int(floatBitsToUint(uintBitsToFloat(uint(gl_InstanceIndex) - uint(gl_BaseInstanceARB))));\n"
	 "}\n"
	 "", 0},
	/* 26 main-86e248 fragment */
	{"", "\n"
	 "#version 100\n"
	 "precision mediump float;\n"
	 "/* TEST-ONLY substitute: NOT a translation (see the vertex stage note). */\n"
	 "varying vec4 out_attr0;\n"
	 "void main() { gl_FragColor = vec4(0.5, 0.5, 0.5, 1.0); }\n"
	 "", 1},
	/* 27 main-86ef08 fragment */
	{"", "\n"
	 "#version 100\n"
	 "precision mediump float;\n"
	 "/* TEST-ONLY substitute: NOT a translation (see the vertex stage note). */\n"
	 "varying vec4 out_attr0;\n"
	 "void main() { gl_FragColor = vec4(0.5, 0.5, 0.5, 1.0); }\n"
	 "", 1},
	/* 28 main-86fcc8 fragment */
	{"", "\n"
	 "#version 100\n"
	 "precision mediump float;\n"
	 "/* TEST-ONLY substitute: NOT a translation (see the vertex stage note). */\n"
	 "varying vec4 out_attr0;\n"
	 "void main() { gl_FragColor = vec4(0.5, 0.5, 0.5, 1.0); }\n"
	 "", 1},
	/* 29 main-870b88 fragment */
	{"", "\n"
	 "#version 100\n"
	 "precision mediump float;\n"
	 "/* TEST-ONLY substitute: NOT a translation (see the vertex stage note). */\n"
	 "varying vec4 out_attr0;\n"
	 "void main() { gl_FragColor = vec4(0.5, 0.5, 0.5, 1.0); }\n"
	 "", 1},
	/* 30 main-871848 fragment */
	{"", "\n"
	 "#version 100\n"
	 "precision mediump float;\n"
	 "/* TEST-ONLY substitute: NOT a translation (see the vertex stage note). */\n"
	 "varying vec4 out_attr0;\n"
	 "void main() { gl_FragColor = vec4(0.5, 0.5, 0.5, 1.0); }\n"
	 "", 1},
	/* 31 main-872608 fragment */
	{"", "\n"
	 "#version 100\n"
	 "precision mediump float;\n"
	 "/* TEST-ONLY substitute: NOT a translation (see the vertex stage note). */\n"
	 "varying vec4 out_attr0;\n"
	 "void main() { gl_FragColor = vec4(0.5, 0.5, 0.5, 1.0); }\n"
	 "", 1},
	/* 32 main-8734c8 vertex */
	{"", "\n"
	 "#version 100\n"
	 "precision highp float;\n"
	 "attribute vec4 in_attr0;\n"
	 "attribute vec4 in_attr1;\n"
	 "varying vec4 out_attr0;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    out_attr0 = vec4(0.0, 0.0, 0.0, 1.0);\n"
	 "    gl_Position.x = in_attr0.x;\n"
	 "    gl_Position.y = in_attr0.y;\n"
	 "    out_attr0.x = in_attr1.x;\n"
	 "    out_attr0.y = in_attr1.y;\n"
	 "}\n"
	 "", 0},
	/* 33 main-874088 fragment */
	{"", "\n"
	 "#version 100\n"
	 "precision mediump float;\n"
	 "uniform sampler2D fs_tex0_20;\n"
	 "\n"
	 "varying vec4 in_attr0;\n"
	 "varying vec4 gl_FragColor;\n"
	 "\n"
	 "void main()\n"
	 "{\n"
	 "    float _53 = 1.0 / gl_FragCoord.w;\n"
	 "    vec4 _58 = texture(fs_tex0_20, vec2(_53 * (in_attr0.x * gl_FragCoord.w), _53 * (in_attr0.y * gl_FragCoord.w)));\n"
	 "    gl_FragColor.x = _58.x;\n"
	 "    gl_FragColor.y = _58.y;\n"
	 "    gl_FragColor.z = _58.z;\n"
	 "    gl_FragColor.w = _58.w;\n"
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
 {.sha256="128077a9d45399940bbcabfdefa45075",.error=NULL,.control_size=2176,.code_size=512,.uniform_count=0,.sampler_count=0,.attribute_count=3,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={3,1,15,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0x12,0x80,0x77,0xa9,0xd4,0x53,0x99,0x94,0x0b,0xbc,0xab,0xfd,0xef,0xa4,0x50,0x75,0xcc,0x67,0x3f,0x41,0x78,0xbc,0xbc,0x41,0xbb,0xe9,0xd0,0x88,0x36,0x24,0x2c,0x89},.control_hash={0x14,0x1d,0xae,0x07,0x0e,0x83,0xe1,0x98,0x3b,0xdf,0x1f,0xea,0x7b,0xad,0xe8,0x4b,0x31,0x83,0xa1,0x50,0x26,0x4e,0x4d,0xd7,0x1a,0x67,0x4b,0xc1,0x81,0xc1,0xf0,0x73},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2},{.name="in_attr1",.location=1,.kind=2},{.name="in_attr2",.location=2,.kind=2}}},
 /* 1 dump-12e9d131 fragment */
 {.sha256="12e9d131b44fe77db32ff7aaa723630f",.error=NULL,.control_size=2176,.code_size=512,.uniform_count=0,.sampler_count=0,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={15,3,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0x12,0xe9,0xd1,0x31,0xb4,0x4f,0xe7,0x7d,0xb3,0x2f,0xf7,0xaa,0xa7,0x23,0x63,0x0f,0x8d,0xed,0xb5,0xef,0x56,0x60,0x17,0xba,0x66,0x0c,0xf3,0x23,0x5b,0xc6,0x66,0xd6},.control_hash={0x87,0xe9,0x53,0x50,0xfc,0x67,0x21,0x10,0x6e,0x2b,0x0d,0x4a,0x61,0x63,0xd3,0xfe,0x6b,0x41,0x96,0x66,0xe3,0x94,0x8c,0x1c,0x49,0x23,0x15,0xb1,0xf2,0x0e,0xa4,0xd0},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2},{.name="in_attr1",.location=1,.kind=2}}},
 /* 2 dump-14196b8e vertex */
 {.sha256="14196b8ee2157ff89e85f75ee57fe690",.error=NULL,.control_size=2176,.code_size=768,.uniform_count=0,.sampler_count=0,.attribute_count=3,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={7,15,3,0,0,0,0,0},.varying_write_masks={15,3,0,0,0,0,0,0},
  .code_hash={0x14,0x19,0x6b,0x8e,0xe2,0x15,0x7f,0xf8,0x9e,0x85,0xf7,0x5e,0xe5,0x7f,0xe6,0x90,0xf8,0xc9,0xb4,0x96,0x6a,0xb0,0x67,0x5b,0xea,0x9e,0xcd,0x20,0x17,0xa5,0x67,0x1e},.control_hash={0xee,0x95,0xcc,0x78,0xd0,0x0e,0xd0,0xe6,0xc2,0x2f,0x6b,0x9f,0x2f,0x56,0x63,0x3c,0x95,0x5e,0x0e,0x45,0x91,0x85,0x76,0x09,0xa3,0x58,0x3c,0x0c,0x18,0x2d,0xaa,0x3d},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2},{.name="in_attr1",.location=1,.kind=2},{.name="in_attr2",.location=2,.kind=2}}},
 /* 3 dump-1792425422-0 fragment */
 {.sha256="d032944a8929b2cc5364e1df7f02f38a",.error=NULL,.control_size=2176,.code_size=768,.uniform_count=0,.sampler_count=0,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={0,3,0,8,0,0,0,0},.varying_write_masks={0,0,0,0,0,0,0,0},
  .code_hash={0xd0,0x32,0x94,0x4a,0x89,0x29,0xb2,0xcc,0x53,0x64,0xe1,0xdf,0x7f,0x02,0xf3,0x8a,0x7f,0x31,0xd8,0x22,0x5f,0xe0,0x02,0xec,0xad,0x35,0x14,0x8f,0x3c,0xac,0xf9,0x68},.control_hash={0x8c,0x4f,0xe3,0x42,0x81,0xe7,0x46,0x7c,0x72,0x81,0x8a,0x14,0x81,0x90,0x2a,0x58,0x09,0x24,0xda,0x35,0x7e,0x05,0xb6,0x64,0x5b,0x5d,0x70,0x3e,0x3d,0x81,0x23,0xff},
  .samplers={},
  .attributes={{.name="in_attr1",.location=1,.kind=2},{.name="in_attr3",.location=3,.kind=2}}},
 /* 4 dump-2991ad4b fragment */
 {.sha256="2991ad4bcf25b8351ded83a14cc8c448",.error=NULL,.control_size=2176,.code_size=512,.uniform_count=0,.sampler_count=0,.attribute_count=4,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={3,3,3,3,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0x29,0x91,0xad,0x4b,0xcf,0x25,0xb8,0x35,0x1d,0xed,0x83,0xa1,0x4c,0xc8,0xc4,0x48,0xb1,0xbf,0x2b,0x4a,0xcf,0x86,0x2b,0xf3,0x42,0x44,0x8d,0x1e,0xd3,0x84,0xce,0x50},.control_hash={0x25,0xa3,0x39,0xf6,0x00,0x3d,0x30,0xb4,0xde,0x2f,0x29,0x46,0xd2,0xfc,0xee,0xc7,0x0b,0x06,0x17,0x39,0x12,0xf5,0x63,0x91,0xd0,0x64,0x02,0x85,0xb4,0x07,0x0a,0x2e},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2},{.name="in_attr1",.location=1,.kind=2},{.name="in_attr2",.location=2,.kind=2},{.name="in_attr3",.location=3,.kind=2}}},
 /* 5 dump-29d0db82 vertex */
 {.sha256="29d0db82b353bb6105f047d41637307f",.error=NULL,.control_size=2176,.code_size=2816,.uniform_count=0,.sampler_count=0,.attribute_count=4,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={15,7,15,3,0,0,0,0},.varying_write_masks={0,3,0,15,0,0,0,0},
  .code_hash={0x29,0xd0,0xdb,0x82,0xb3,0x53,0xbb,0x61,0x05,0xf0,0x47,0xd4,0x16,0x37,0x30,0x7f,0xdb,0x24,0xfe,0x48,0x72,0x3c,0x22,0x31,0xe5,0x97,0x8b,0x3b,0xb5,0xd5,0xf1,0xd2},.control_hash={0x8b,0x4a,0x63,0xc3,0x7a,0xb9,0x21,0xa5,0x77,0x3d,0x05,0x9b,0x40,0x69,0x47,0xd7,0x4c,0x75,0xaf,0x25,0x5a,0x5c,0xba,0x52,0x44,0x07,0x2c,0x33,0xfd,0x88,0x25,0xbf},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2},{.name="in_attr1",.location=1,.kind=2},{.name="in_attr2",.location=2,.kind=2},{.name="in_attr3",.location=3,.kind=2}}},
 /* 6 dump-33650b4b fragment */
 {.sha256="33650b4b250293b5c244b5b33e62a77c",.error=NULL,.control_size=2176,.code_size=1024,.uniform_count=0,.sampler_count=0,.attribute_count=1,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={3,0,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0x33,0x65,0x0b,0x4b,0x25,0x02,0x93,0xb5,0xc2,0x44,0xb5,0xb3,0x3e,0x62,0xa7,0x7c,0x1f,0x03,0xed,0x85,0x71,0xac,0x3f,0xfd,0xda,0x93,0x68,0x34,0x7b,0xdc,0x61,0x66},.control_hash={0x7a,0x38,0xf8,0xcc,0x64,0x64,0xed,0xcb,0x26,0x5c,0x68,0x22,0x70,0x57,0x7a,0x3a,0x9b,0x46,0x68,0xac,0xf4,0x9d,0x26,0xee,0x9c,0x38,0x8b,0xdd,0x25,0x7b,0xbc,0x01},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2}}},
 /* 7 dump-3a41323d vertex */
 {.sha256="3a41323d0d47e4265c808b26327df78e",.error=NULL,.control_size=2176,.code_size=1024,.uniform_count=0,.sampler_count=0,.attribute_count=3,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={7,15,15,0,0,0,0,0},.varying_write_masks={15,1,15,0,0,0,0,0},
  .code_hash={0x3a,0x41,0x32,0x3d,0x0d,0x47,0xe4,0x26,0x5c,0x80,0x8b,0x26,0x32,0x7d,0xf7,0x8e,0x82,0x8a,0x2a,0xab,0xb9,0x01,0xef,0x5f,0xf0,0x06,0x9d,0xf8,0xad,0x19,0x0c,0x56},.control_hash={0xf4,0x45,0x58,0x4b,0x81,0x84,0x6d,0x9a,0x06,0x14,0x84,0xaa,0xb0,0x39,0x64,0xd7,0x33,0xda,0x78,0xec,0xf3,0x99,0x43,0xeb,0x78,0x70,0x05,0xf0,0xd6,0xec,0x0a,0xbb},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2},{.name="in_attr1",.location=1,.kind=2},{.name="in_attr2",.location=2,.kind=2}}},
 /* 8 dump-3a75a7d0 vertex */
 {.sha256="3a75a7d07d489830954eabc424a380db",.error=NULL,.control_size=2176,.code_size=768,.uniform_count=0,.sampler_count=0,.attribute_count=1,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={7,0,0,0,0,0,0,0},.varying_write_masks={0,0,0,0,0,0,0,0},
  .code_hash={0x3a,0x75,0xa7,0xd0,0x7d,0x48,0x98,0x30,0x95,0x4e,0xab,0xc4,0x24,0xa3,0x80,0xdb,0x64,0xa4,0x3c,0x2c,0x70,0xca,0x19,0x6d,0xf6,0xe0,0xbe,0x61,0x80,0x92,0x62,0x17},.control_hash={0x89,0x1f,0xf3,0x3d,0xb2,0xcb,0xae,0x81,0xdb,0xfe,0x7c,0x20,0x71,0x98,0x82,0x42,0xb2,0xa7,0xb3,0x1b,0x4a,0xc0,0xa5,0x53,0x9a,0xb3,0xb8,0x3c,0xe1,0x84,0x05,0x48},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2}}},
 /* 9 dump-4b551bd7 fragment */
 {.sha256="4b551bd7a7732d410f3634916c38c1a6",.error=NULL,.control_size=2176,.code_size=512,.uniform_count=0,.sampler_count=0,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={3,3,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0x4b,0x55,0x1b,0xd7,0xa7,0x73,0x2d,0x41,0x0f,0x36,0x34,0x91,0x6c,0x38,0xc1,0xa6,0x2d,0x9e,0x87,0x81,0x9c,0x50,0xe5,0x4c,0x9f,0x58,0x60,0x7b,0x46,0x60,0x67,0x84},.control_hash={0x78,0x36,0x9a,0x4e,0x5c,0x8a,0xb4,0x9a,0xa7,0x3a,0xc7,0x00,0xd1,0x35,0x4e,0x8c,0x06,0xa9,0x6b,0xeb,0xc1,0x62,0x66,0x77,0x5b,0x4f,0x9c,0x07,0xcd,0x09,0x8b,0xdd},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2},{.name="in_attr1",.location=1,.kind=2}}},
 /* 10 dump-56844c6b vertex */
 {.sha256="56844c6ba737e9ef8558ff6f0fb935e8",.error=NULL,.control_size=2176,.code_size=1024,.uniform_count=0,.sampler_count=0,.attribute_count=3,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={7,15,3,0,0,0,0,0},.varying_write_masks={15,3,0,0,0,0,0,0},
  .code_hash={0x56,0x84,0x4c,0x6b,0xa7,0x37,0xe9,0xef,0x85,0x58,0xff,0x6f,0x0f,0xb9,0x35,0xe8,0x67,0xfe,0x26,0xfa,0x0a,0xb8,0xbe,0x1d,0x65,0xf2,0x12,0x5a,0xb3,0x27,0xc4,0x8f},.control_hash={0xf8,0x2a,0x0a,0xef,0x7d,0x74,0xf5,0x2a,0xac,0x7a,0xf8,0x30,0x33,0x6f,0x64,0x71,0xdd,0x88,0x81,0x2d,0x9b,0xed,0xbd,0x5d,0x06,0x27,0x72,0x52,0x4e,0xbd,0x05,0x64},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2},{.name="in_attr1",.location=1,.kind=2},{.name="in_attr2",.location=2,.kind=2}}},
 /* 11 dump-6054acba vertex */
 {.sha256="6054acba873a0922637dff386f4e1313",.error=NULL,.control_size=2176,.code_size=768,.uniform_count=0,.sampler_count=0,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={7,3,0,0,0,0,0,0},.varying_write_masks={3,0,0,0,0,0,0,0},
  .code_hash={0x60,0x54,0xac,0xba,0x87,0x3a,0x09,0x22,0x63,0x7d,0xff,0x38,0x6f,0x4e,0x13,0x13,0xf4,0x53,0xe0,0xe7,0xc2,0x3a,0x02,0x61,0x06,0x74,0x4e,0xaf,0xb7,0xc2,0xb9,0x9a},.control_hash={0xca,0xd4,0x66,0x26,0x1f,0x04,0xa7,0x1f,0x88,0x49,0x9c,0x01,0xf8,0xef,0x35,0x6f,0x1f,0xcf,0x28,0xfe,0x9e,0xb1,0x07,0xba,0x4e,0x67,0xb7,0x74,0x66,0xe4,0x42,0x2d},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2},{.name="in_attr1",.location=1,.kind=2}}},
 /* 12 dump-6a930d0e vertex */
 {.sha256="6a930d0edea444e0a29d3db880fe7620",.error=NULL,.control_size=2176,.code_size=1024,.uniform_count=0,.sampler_count=0,.attribute_count=3,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={15,15,3,0,0,0,0,0},.varying_write_masks={15,15,3,0,0,0,0,0},
  .code_hash={0x6a,0x93,0x0d,0x0e,0xde,0xa4,0x44,0xe0,0xa2,0x9d,0x3d,0xb8,0x80,0xfe,0x76,0x20,0x3b,0x4f,0xa1,0x2a,0xa9,0x59,0xfa,0x8d,0xfb,0xcb,0x7b,0x00,0x1c,0xee,0x71,0xdd},.control_hash={0xcf,0x5e,0x12,0x22,0x15,0xb4,0x07,0x4a,0x22,0x8c,0x8b,0x1c,0x4c,0xf9,0xe3,0x95,0xd5,0x28,0x35,0xe4,0x06,0x5f,0x42,0x9f,0x67,0x22,0xfc,0x6c,0x4a,0x67,0x5f,0x76},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2},{.name="in_attr1",.location=1,.kind=2},{.name="in_attr2",.location=2,.kind=2}}},
 /* 13 dump-7227c812 fragment */
 {.sha256="7227c812dba30ea82b90fc43945f4156",.error=NULL,.control_size=2176,.code_size=512,.uniform_count=0,.sampler_count=0,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={15,3,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0x72,0x27,0xc8,0x12,0xdb,0xa3,0x0e,0xa8,0x2b,0x90,0xfc,0x43,0x94,0x5f,0x41,0x56,0xfe,0xa1,0xc4,0xef,0xaf,0x44,0x67,0xda,0x8c,0x5f,0x10,0x2b,0x30,0xf2,0x15,0x88},.control_hash={0x73,0x82,0xe6,0x2c,0x83,0x56,0xa7,0xb0,0x25,0x44,0xd9,0xc5,0x79,0x02,0x4b,0x5e,0x8d,0xc4,0xc8,0x8b,0xa5,0xc8,0x28,0xda,0x0a,0x9b,0xfb,0x70,0xfc,0xb1,0x2b,0x32},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2},{.name="in_attr1",.location=1,.kind=2}}},
 /* 14 dump-800121db fragment */
 {.sha256="800121db9124384d3d3fd2c0452b3311",.error=NULL,.control_size=2176,.code_size=512,.uniform_count=0,.sampler_count=0,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={15,0,3,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0x80,0x01,0x21,0xdb,0x91,0x24,0x38,0x4d,0x3d,0x3f,0xd2,0xc0,0x45,0x2b,0x33,0x11,0x16,0x7d,0x25,0x54,0x6e,0xfd,0x1d,0x53,0x81,0x11,0xfa,0xf3,0x55,0xdf,0x3c,0x1b},.control_hash={0xa9,0xad,0x70,0xc6,0xe7,0x9b,0xfe,0xeb,0x5e,0x23,0x24,0x5b,0x18,0xd1,0x97,0xe5,0x84,0x68,0x94,0x55,0xa9,0xfd,0xd3,0xb1,0x19,0x3a,0x37,0xe3,0x30,0x66,0xd6,0xae},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2},{.name="in_attr2",.location=2,.kind=2}}},
 /* 15 dump-815bc387 fragment */
 {.sha256="815bc3875d5ebee554109af31f5502e8",.error=NULL,.control_size=2176,.code_size=256,.uniform_count=0,.sampler_count=0,.attribute_count=0,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={0,0,0,0,0,0,0,0},.varying_write_masks={0,0,0,0,0,0,0,0},
  .code_hash={0x81,0x5b,0xc3,0x87,0x5d,0x5e,0xbe,0xe5,0x54,0x10,0x9a,0xf3,0x1f,0x55,0x02,0xe8,0x3c,0x24,0x50,0x87,0x28,0xa1,0xc9,0x6f,0x9d,0x2e,0xaf,0x72,0x0e,0x88,0x8e,0x2f},.control_hash={0x55,0x77,0x4a,0x1e,0x13,0x4b,0x14,0xb2,0x40,0xd4,0x92,0xb2,0x67,0x5c,0x1b,0xea,0xfb,0x58,0xe7,0x96,0x64,0x2a,0xcf,0xcf,0xe2,0xd0,0xc1,0xdc,0x28,0x4f,0x8f,0x11},
  .samplers={},
  .attributes={}},
 /* 16 dump-8af77a17 vertex */
 {.sha256="8af77a177b7838819ff46bb634747d44",.error=NULL,.control_size=2176,.code_size=2048,.uniform_count=0,.sampler_count=0,.attribute_count=4,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={7,7,15,3,0,0,0,0},.varying_write_masks={3,7,7,15,7,0,0,0},
  .code_hash={0x8a,0xf7,0x7a,0x17,0x7b,0x78,0x38,0x81,0x9f,0xf4,0x6b,0xb6,0x34,0x74,0x7d,0x44,0x06,0xbd,0x08,0xae,0x4a,0xd4,0xfd,0xe1,0xca,0x20,0x2f,0xe9,0xef,0x85,0x4a,0xb9},.control_hash={0x63,0x2e,0xc0,0x3a,0x6c,0xee,0x39,0xda,0x99,0xda,0xe2,0x10,0x0a,0x0f,0x27,0x1e,0x1c,0xc0,0xac,0xd7,0xa6,0x21,0x92,0x3f,0x1c,0x33,0x3b,0xb2,0xf3,0xff,0xb1,0xfd},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2},{.name="in_attr1",.location=1,.kind=2},{.name="in_attr2",.location=2,.kind=2},{.name="in_attr3",.location=3,.kind=2}}},
 /* 17 dump-b5d846ce vertex */
 {.sha256="b5d846ce116ab86d1ae9e9a9fd3ddb9f",.error=NULL,.control_size=2176,.code_size=1024,.uniform_count=0,.sampler_count=0,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={7,3,0,0,0,0,0,0},.varying_write_masks={3,3,3,3,0,0,0,0},
  .code_hash={0xb5,0xd8,0x46,0xce,0x11,0x6a,0xb8,0x6d,0x1a,0xe9,0xe9,0xa9,0xfd,0x3d,0xdb,0x9f,0x4f,0xa8,0xb5,0xfe,0x0a,0x86,0x7e,0x5e,0x8a,0xee,0xc5,0x42,0xc4,0x9c,0x3c,0x42},.control_hash={0x0c,0x84,0xa9,0xac,0x97,0xf6,0x4a,0xa1,0xf6,0x50,0x72,0xcd,0xe5,0xdc,0xb4,0xe9,0x7e,0xbd,0x99,0xe0,0x54,0x41,0x32,0x3c,0x3d,0xa3,0xd6,0xdc,0x0b,0xed,0x26,0x01},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2},{.name="in_attr1",.location=1,.kind=2}}},
 /* 18 dump-b894e79b vertex */
 {.sha256="b894e79b9c9c0637db3d015e6cda1d93",.error=NULL,.control_size=2176,.code_size=768,.uniform_count=0,.sampler_count=0,.attribute_count=3,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={7,15,3,0,0,0,0,0},.varying_write_masks={15,3,0,0,0,0,0,0},
  .code_hash={0xb8,0x94,0xe7,0x9b,0x9c,0x9c,0x06,0x37,0xdb,0x3d,0x01,0x5e,0x6c,0xda,0x1d,0x93,0x89,0x78,0x90,0x2b,0x1a,0x57,0xe3,0xdc,0x22,0x3a,0xeb,0x5e,0x1a,0xde,0x24,0xa9},.control_hash={0x27,0x3f,0xbd,0x13,0x1c,0xac,0x9e,0x51,0x06,0xc4,0xf9,0x47,0x77,0x4a,0x65,0xf8,0x99,0xd8,0x2a,0xd8,0x59,0x4b,0x21,0x4f,0xbb,0xed,0xa1,0xe5,0x2a,0xbc,0xf6,0xb5},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2},{.name="in_attr1",.location=1,.kind=2},{.name="in_attr2",.location=2,.kind=2}}},
 /* 19 dump-c523448a fragment */
 {.sha256="c523448a188e019468627cb25b9a59af",.error=NULL,.control_size=2176,.code_size=1024,.uniform_count=0,.sampler_count=0,.attribute_count=5,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={3,7,7,15,7,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0xc5,0x23,0x44,0x8a,0x18,0x8e,0x01,0x94,0x68,0x62,0x7c,0xb2,0x5b,0x9a,0x59,0xaf,0xc6,0xa9,0x1a,0x94,0x82,0xb5,0x13,0x68,0xc1,0xa1,0x8d,0xa4,0xa6,0x21,0xba,0x1e},.control_hash={0x71,0xbd,0x2d,0x6a,0x9d,0x63,0xd4,0x00,0x31,0x49,0x7b,0x5a,0x4f,0x22,0xd5,0x67,0x10,0x29,0x6e,0x20,0x62,0x23,0xed,0xd4,0x28,0x01,0x94,0xc2,0x0e,0x8f,0x52,0x44},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2},{.name="in_attr1",.location=1,.kind=2},{.name="in_attr2",.location=2,.kind=2},{.name="in_attr3",.location=3,.kind=2},{.name="in_attr4",.location=4,.kind=2}}},
 /* 20 dump-d032944a fragment */
 {.sha256="d032944a8929b2cc5364e1df7f02f38a",.error=NULL,.control_size=2176,.code_size=768,.uniform_count=0,.sampler_count=0,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={0,3,0,8,0,0,0,0},.varying_write_masks={0,0,0,0,0,0,0,0},
  .code_hash={0xd0,0x32,0x94,0x4a,0x89,0x29,0xb2,0xcc,0x53,0x64,0xe1,0xdf,0x7f,0x02,0xf3,0x8a,0x7f,0x31,0xd8,0x22,0x5f,0xe0,0x02,0xec,0xad,0x35,0x14,0x8f,0x3c,0xac,0xf9,0x68},.control_hash={0x8c,0x4f,0xe3,0x42,0x81,0xe7,0x46,0x7c,0x72,0x81,0x8a,0x14,0x81,0x90,0x2a,0x58,0x09,0x24,0xda,0x35,0x7e,0x05,0xb6,0x64,0x5b,0x5d,0x70,0x3e,0x3d,0x81,0x23,0xff},
  .samplers={},
  .attributes={{.name="in_attr1",.location=1,.kind=2},{.name="in_attr3",.location=3,.kind=2}}},
 /* 21 dump-e4fb4243 fragment */
 {.sha256="e4fb424329549ccd60aad17d772a2487",.error=NULL,.control_size=2176,.code_size=512,.uniform_count=0,.sampler_count=0,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={15,3,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0xe4,0xfb,0x42,0x43,0x29,0x54,0x9c,0xcd,0x60,0xaa,0xd1,0x7d,0x77,0x2a,0x24,0x87,0xb4,0xe7,0x63,0x45,0x5f,0xc2,0x74,0xe7,0xe8,0x77,0x8b,0x66,0x9d,0x21,0xd8,0x61},.control_hash={0xb3,0x14,0x37,0x34,0x54,0x45,0x6f,0x87,0x73,0xf7,0xcf,0xfe,0x48,0x1e,0xa8,0x0b,0xd1,0xd9,0x84,0x17,0x4a,0x44,0x08,0xe3,0x56,0x27,0xad,0x90,0x19,0x5b,0x7d,0x62},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2},{.name="in_attr1",.location=1,.kind=2}}},
 /* 22 dump-e6091e72 fragment */
 {.sha256="e6091e727431c3272e5d6b9198de23df",.error=NULL,.control_size=2176,.code_size=768,.uniform_count=0,.sampler_count=0,.attribute_count=1,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={3,0,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0xe6,0x09,0x1e,0x72,0x74,0x31,0xc3,0x27,0x2e,0x5d,0x6b,0x91,0x98,0xde,0x23,0xdf,0x1e,0xd2,0xf6,0x61,0xcb,0xe9,0xa7,0x4e,0x4b,0x03,0x5d,0xc6,0xe2,0xaa,0x45,0x93},.control_hash={0x39,0x34,0x06,0x5f,0x96,0x2a,0xf2,0xed,0xe8,0x54,0xb2,0x3c,0xb4,0x5c,0x9f,0x7f,0x7c,0xe4,0x45,0xfb,0xcf,0x92,0xfa,0xbc,0x5c,0xc3,0x4a,0x37,0x5f,0xb3,0x6b,0x2e},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2}}},
 /* 23 dump-f3327347 fragment */
 {.sha256="f3327347207307f4ac851f8f7cc24dcd",.error=NULL,.control_size=2176,.code_size=512,.uniform_count=0,.sampler_count=0,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={15,3,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0xf3,0x32,0x73,0x47,0x20,0x73,0x07,0xf4,0xac,0x85,0x1f,0x8f,0x7c,0xc2,0x4d,0xcd,0xef,0xd5,0xd8,0x0c,0xda,0x44,0x0d,0x50,0xbd,0x82,0x7e,0x93,0x10,0x6e,0x90,0x1e},.control_hash={0xad,0x1a,0xa1,0x3d,0xa8,0x3c,0xf3,0x6e,0x48,0x9f,0x39,0x81,0x84,0x47,0x36,0x7e,0x6e,0x2f,0x31,0x87,0x72,0x4d,0x1a,0x90,0x16,0xbe,0xd4,0xc2,0x21,0x10,0x68,0xb3},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2},{.name="in_attr1",.location=1,.kind=2}}},
 /* 24 main-86cac8 vertex */
 {.sha256="b3913c5cf5773c0e3a8d943f162b9d6d",.error=NULL,.control_size=2176,.code_size=256,.uniform_count=0,.sampler_count=0,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={3,3,0,0,0,0,0,0},.varying_write_masks={3,0,0,0,0,0,0,0},
  .code_hash={0xb3,0x91,0x3c,0x5c,0xf5,0x77,0x3c,0x0e,0x3a,0x8d,0x94,0x3f,0x16,0x2b,0x9d,0x6d,0x94,0x29,0x7f,0x26,0x94,0x02,0x69,0x03,0x06,0x57,0x51,0x86,0xa5,0x6e,0x88,0xff},.control_hash={0xb3,0x0b,0x42,0xeb,0x5e,0x91,0xad,0xc2,0xa6,0x2a,0x80,0x57,0x07,0x92,0x3b,0x37,0x04,0xa7,0xee,0xfd,0x91,0x6c,0x04,0xd3,0xae,0x32,0x7c,0xf1,0x45,0x3a,0x8a,0x87},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2},{.name="in_attr1",.location=1,.kind=2}}},
 /* 25 main-86d688 vertex */
 {.sha256="06fab867aa4c0d624751d868dda96664",.error=NULL,.control_size=2176,.code_size=256,.uniform_count=0,.sampler_count=0,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={3,3,0,0,0,0,0,0},.varying_write_masks={3,0,0,0,0,0,0,0},
  .code_hash={0x06,0xfa,0xb8,0x67,0xaa,0x4c,0x0d,0x62,0x47,0x51,0xd8,0x68,0xdd,0xa9,0x66,0x64,0x9e,0x4b,0xda,0x51,0xcc,0x14,0x61,0xa6,0x3b,0xcf,0x51,0xff,0xcd,0x2a,0x5d,0xfb},.control_hash={0x23,0x80,0xf0,0xf0,0xec,0x50,0xa6,0xc2,0x49,0x97,0xf1,0xb0,0xae,0xa3,0x0a,0x89,0x3c,0xd4,0x31,0xbf,0xff,0x81,0xe3,0xd4,0xd9,0xa9,0x84,0xd6,0xfd,0xbf,0xbb,0x52},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2},{.name="in_attr1",.location=1,.kind=2}}},
 /* 26 main-86e248 fragment */
 {.sha256="f7d68113daeff747cbbc1d54f1cbb208",.error=NULL,.control_size=2176,.code_size=512,.uniform_count=0,.sampler_count=0,.attribute_count=1,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={3,0,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0xf7,0xd6,0x81,0x13,0xda,0xef,0xf7,0x47,0xcb,0xbc,0x1d,0x54,0xf1,0xcb,0xb2,0x08,0x6b,0xca,0xf9,0x64,0x2c,0x65,0x66,0x0e,0xb2,0xab,0x27,0x5f,0x52,0x6e,0xb9,0xdd},.control_hash={0x79,0x18,0x8e,0x3c,0xd6,0xde,0x6e,0xe9,0x26,0x8a,0x5e,0x77,0xd7,0xb9,0x65,0xfe,0xca,0xf6,0x85,0xd4,0x90,0xa5,0x78,0xe2,0xa1,0xb7,0xb5,0x24,0x1d,0x68,0x5b,0x10},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2}}},
 /* 27 main-86ef08 fragment */
 {.sha256="51e9503e3e9e5ffc0c9b19852a5ba042",.error=NULL,.control_size=2176,.code_size=768,.uniform_count=0,.sampler_count=0,.attribute_count=1,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={3,0,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0x51,0xe9,0x50,0x3e,0x3e,0x9e,0x5f,0xfc,0x0c,0x9b,0x19,0x85,0x2a,0x5b,0xa0,0x42,0xaf,0x6e,0xe6,0x1f,0x3d,0x63,0xef,0x5b,0x78,0x66,0x6f,0x35,0xd4,0xf0,0xcb,0x57},.control_hash={0x54,0xae,0xa6,0x5a,0xae,0xad,0x02,0x95,0xb2,0x4c,0x41,0x82,0x9d,0x9a,0x47,0xf5,0x41,0x19,0xb3,0xfd,0x9c,0x7a,0xd9,0x59,0x29,0x7c,0x27,0x36,0x4d,0x86,0x1a,0x94},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2}}},
 /* 28 main-86fcc8 fragment */
 {.sha256="283a226c935b89dff3ba47a0dfe2b811",.error=NULL,.control_size=2176,.code_size=1024,.uniform_count=0,.sampler_count=0,.attribute_count=1,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={3,0,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0x28,0x3a,0x22,0x6c,0x93,0x5b,0x89,0xdf,0xf3,0xba,0x47,0xa0,0xdf,0xe2,0xb8,0x11,0xde,0xfb,0xde,0x50,0x9c,0x64,0x63,0x07,0x1f,0xf5,0x01,0x84,0x0f,0x12,0x46,0x3a},.control_hash={0xd1,0x69,0x4f,0xdc,0xe3,0xfe,0x75,0xb4,0xa3,0x3c,0x2e,0x49,0xa1,0xa4,0xbf,0x8d,0xf0,0x7c,0x5c,0x11,0x1e,0xdb,0x89,0xf0,0x87,0x79,0x07,0x33,0x13,0x91,0x05,0x96},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2}}},
 /* 29 main-870b88 fragment */
 {.sha256="4137e113105451ea591ecc3eed5477e6",.error=NULL,.control_size=2176,.code_size=512,.uniform_count=0,.sampler_count=0,.attribute_count=1,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={3,0,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0x41,0x37,0xe1,0x13,0x10,0x54,0x51,0xea,0x59,0x1e,0xcc,0x3e,0xed,0x54,0x77,0xe6,0x95,0xdd,0xaf,0xbe,0xef,0x9f,0x8d,0x10,0x9f,0x0f,0xd0,0xfc,0x81,0x5d,0xac,0x08},.control_hash={0x9f,0x90,0x77,0x63,0xe1,0x36,0xc6,0x77,0xab,0x55,0xd7,0xf4,0x0a,0xfd,0xc8,0x0d,0x9b,0x1b,0x07,0x47,0xd7,0xb2,0x6d,0xd9,0x7f,0x65,0x5c,0x50,0xcd,0x9e,0x66,0xd9},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2}}},
 /* 30 main-871848 fragment */
 {.sha256="49351413ea33c9c09fddb670ac293145",.error=NULL,.control_size=2176,.code_size=768,.uniform_count=0,.sampler_count=0,.attribute_count=1,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={3,0,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0x49,0x35,0x14,0x13,0xea,0x33,0xc9,0xc0,0x9f,0xdd,0xb6,0x70,0xac,0x29,0x31,0x45,0xa5,0xa8,0x99,0xbf,0xd0,0x7d,0x77,0x92,0x56,0x37,0xbd,0x0b,0x3e,0x47,0x0f,0x0b},.control_hash={0xb4,0x4a,0x7f,0x2f,0x16,0x3a,0xb2,0x38,0x4f,0xce,0x52,0x4f,0x93,0x1e,0xc5,0x1b,0xca,0x89,0x31,0xb2,0x77,0xdc,0xfb,0xb0,0x13,0xde,0x4e,0x39,0xce,0x96,0xba,0xe3},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2}}},
 /* 31 main-872608 fragment */
 {.sha256="7a92670073b5efd71bc427239f94ac3f",.error=NULL,.control_size=2176,.code_size=1024,.uniform_count=0,.sampler_count=0,.attribute_count=1,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={3,0,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0x7a,0x92,0x67,0x00,0x73,0xb5,0xef,0xd7,0x1b,0xc4,0x27,0x23,0x9f,0x94,0xac,0x3f,0x33,0xec,0xc2,0x53,0x73,0xf6,0x54,0xf0,0x72,0xc7,0xcc,0x86,0xaf,0x3a,0x5e,0x3f},.control_hash={0x6d,0x75,0x97,0x95,0xa4,0xee,0x23,0xf0,0xbf,0xf6,0x83,0x0c,0x40,0xda,0xbf,0xfa,0x89,0x26,0xa9,0x74,0xa2,0x1d,0xb2,0x9b,0x8b,0x99,0x94,0x0c,0xa8,0x99,0xe4,0xed},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2}}},
 /* 32 main-8734c8 vertex */
 {.sha256="b3913c5cf5773c0e3a8d943f162b9d6d",.error=NULL,.control_size=2176,.code_size=256,.uniform_count=0,.sampler_count=0,.attribute_count=2,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={3,3,0,0,0,0,0,0},.varying_write_masks={3,0,0,0,0,0,0,0},
  .code_hash={0xb3,0x91,0x3c,0x5c,0xf5,0x77,0x3c,0x0e,0x3a,0x8d,0x94,0x3f,0x16,0x2b,0x9d,0x6d,0x94,0x29,0x7f,0x26,0x94,0x02,0x69,0x03,0x06,0x57,0x51,0x86,0xa5,0x6e,0x88,0xff},.control_hash={0x8d,0x52,0x7a,0x92,0x65,0x35,0xd6,0xb4,0xd5,0x38,0x78,0x4d,0xfc,0x99,0x93,0x83,0xc6,0x6c,0x32,0x76,0xc6,0x60,0xcb,0xa9,0x6c,0x43,0x09,0x6c,0x44,0x3b,0x36,0x13},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2},{.name="in_attr1",.location=1,.kind=2}}},
 /* 33 main-874088 fragment */
 {.sha256="d97e37b36286e7b9110b2b0a5d85c3b8",.error=NULL,.control_size=2176,.code_size=256,.uniform_count=0,.sampler_count=0,.attribute_count=1,.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,
  .varying_read_masks={3,0,0,0,0,0,0,0},.varying_write_masks={15,0,0,0,0,0,0,0},
  .code_hash={0xd9,0x7e,0x37,0xb3,0x62,0x86,0xe7,0xb9,0x11,0x0b,0x2b,0x0a,0x5d,0x85,0xc3,0xb8,0x44,0x71,0x68,0xed,0x31,0x5c,0xdc,0x36,0x8f,0x37,0x15,0x0f,0x34,0xc2,0x5b,0x9b},.control_hash={0xea,0xba,0x42,0x33,0xf4,0x38,0xa2,0xc8,0xf1,0x56,0x53,0x7d,0x8a,0xb8,0x60,0x4f,0x7a,0xa9,0xdf,0xb2,0x70,0xa0,0xb4,0x6f,0x7a,0x16,0x0e,0x3c,0x03,0x83,0x76,0x48},
  .samplers={},
  .attributes={{.name="in_attr0",.location=0,.kind=2}}},
};
