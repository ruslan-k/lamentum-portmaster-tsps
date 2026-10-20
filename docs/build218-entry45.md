# Build218: entry 45 keeps the captured half-precision products

Roadmap §22.2 P0-FRONTIER. Facts only; this is not an FPS result and not gameplay.

## The program

`newgame-18` (build217) advanced past entry 44 — the log shows
`NVN_LC2_PROGRAM_STAGES object=0x3e8b85940 id=813 mask=1 sources=44/0 code-control-source=byte-exact
link=on-native-pair-draw`, i.e. the new vertex linked against the catalogue — and then stopped on the
next program during setup:

- code `bb10c5c308ac2a145198a848f7a13ac9c2d510c02d208695c0dc5511adcf1c07` (768 bytes)
- control `c28023ec007cc676bf9f5ad08db0a67053e04109679222c16f703f235fdaf540` (2176 bytes)
- execution model: fragment (verified from the SPIR-V `OpEntryPoint`, not from instruction shape)

The captured Vulkan GLSL is a 4-output MRT fragment that samples `fs_tex0_20` (reserved NVN
table 14, offset 0) and multiplies **half** lanes: `float16_t`, `f16vec2`, `packHalf2x16` and
`unpackFloat2x16`.

## Why a plain type replacement would be wrong

Widening `float16_t` to `float` and keeping `_97 * _90` changes the arithmetic: the original
rounds every product to binary16 before widening. `tools/half_mrt_lowering.py` matches the pinned
statements **exactly** (input GLSL SHA-256 is pinned; any drift raises) and wraps each product in
`lc2_half()` — a pack/unpack round-trip — so `_90`, `_97`, `_108`, `_110` and `_112` keep their
original rounding points. `unpackFloat2x16` becomes `unpackHalf2x16`. If any f16 construct
survives the lowering the tool refuses.

`tools/append_half_mrt_fragment.py` verifies both capture hashes, the fragment execution model and
the sampler provenance (`fs_tex0_20` -> binding 14 offset 0) before appending entry **45**. The
catalogue stays append-only: all 45 earlier entries are byte-identical (verified by re-splitting
the generated header and comparing the previous prefix).

Build218 ELF SHA-256: `034c8f963d7e6b3eb5a2d2e305e59c4e1d58756ced309b304252c2ff71e324c3`.
Previous executable kept as `lamentum-nextos.before-218` (`9c6ecc47…`). Host suite: 54 tests.

## Instrument that removes a manual dependency

`tools/newgame_navigate.py` drives menu -> New Game configuration -> controls from live captures:
every Confirm is preceded and followed by a kmsrab capture, a cursor step needs a non-zero change,
a screen transition needs >= 50 changed grid cells, and a step that never changes the screen is
retried only a bounded number of times and then fails. So a run can no longer record "confirmed"
for a screen it did not observe, and the whole cycle no longer depends on an operator pressing
buttons by hand.

## Open, measured problems carried forward

- Entry 45 is appended and deployed but **not yet proven at draw time**; `newgame-19` runs it.
- The title's own `alarm()` governor did not stop a run 800 s past its budget (`newgame-17`), so
  the harness now hard-stops the exact game pids; see `docs/time-governor-and-load-cost.md`.
- The load still costs ~0.836 s of main-thread CPU per presented frame with no new RomFS reads,
  textures or draws in a 20 s window. Until that is attributed with the guest-stack sampler, the
  30 FPS target has no measured path.
