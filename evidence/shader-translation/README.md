# Shader translation pipeline — feasibility proof

The Hades-lineage Maxwell compiler
(`spikes/wol-switch/tools/hades-eval/shader-compiler-rs`, built here as
`shader-compiler-cli`) translates this title's programs into **real, non-empty GLSL** — the
check that decides whether the port's shader work is automatable. Input is the program's code
blob exactly as the title stores it: 0x30-byte header, SPH at +0x30 (stage in bits 10-13:
1 = vertex, 5 = fragment), SASS from +0x80.

Programs found in the owner modules (10; all with a 0x880-byte control section):

| # | segment offset | code size | stage | code SHA-256 (first 16) | control SHA-256 (first 16) |
|---|---|---|---|---|---|
| 1 | main.rodata+0x86cac8 | 0x100 | vertex | `b3913c5cf5773c0e` | `b30b42eb5e91adc2` |
| 2 | main.rodata+0x86d688 | 0x100 | vertex | `06fab867aa4c0d62` | `2380f0f0ec50a6c2` |
| 3 | main.rodata+0x86e248 | 0x200 | fragment | `f7d68113daeff747` | `79188e3cd6de6ee9` |
| 4 | main.rodata+0x86ef08 | 0x300 | fragment | `51e9503e3e9e5ffc` | `54aea65aaead0295` |
| 5 | main.rodata+0x86fcc8 | 0x400 | fragment | `283a226c935b89df` | `d1694fdce3fe75b4` |
| 6 | main.rodata+0x870b88 | 0x200 | fragment | `4137e113105451ea` | `9f907763e136c677` |
| 7 | main.rodata+0x871848 | 0x300 | fragment | `49351413ea33c9c0` | `b44a7f2f163ab238` |
| 8 | main.rodata+0x872608 | 0x400 | fragment | `7a92670073b5efd7` | `6d759795a4ee23f0` |
| 9 | main.rodata+0x8734c8 | 0x100 | vertex | `b3913c5cf5773c0e` | `8d527a926535d6b4` |
| 10 | main.rodata+0x874088 | 0x100 | fragment | `d97e37b36286e7b9` | `eaba4233f438a2c8` |

Program #1 is the one the first device run asked for (`code-bytes=256 control-bytes=2176`,
hashes matching this table), and #9 shares its machine code with #1 while carrying a different
control section — the case the runtime documents, where the catalogue key must be
(code hash + control hash).

The two translated samples committed here are our own GLSL output (the title's blobs are not
committed): the vertex program is a 2D transform/uv passthrough and the fragment program
samples two mip levels and averages them — the title's pixel-art upscale path.

**Not done yet:** the catalogue entry format the runtime consumes (`mm_shader_binding`
metadata: attributes, uniform/sampler bindings, varying masks, colour-write mask, precision)
plus the ESSL100 rewrite of the compiler's `#version 450` output. That is the next work item.
