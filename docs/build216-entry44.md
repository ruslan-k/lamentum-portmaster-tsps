# Build216: entry 44 admitted; the load now runs past the old shader frontier

Roadmap position: §22.2 P0-FRONTIER (continue the exact shader-tail chain) and §22.3
(measured receipts). This is not an FPS result and not gameplay.

## What was added

Entry **44**, pinned to code `801b91aed1fb1660a5c1ae9413994c0113547d596e4be5ef5143582addc325d0` /
control `ada676aaf675d0510aa7fea908d1473518596087a1a9dadf5a0cc43235eee820` (2048 / 2176 bytes,
vertex execution model). The original Vulkan GLSL carries two 16384-float scalar blocks: the
literal bank `c1` and the application bank `c3` emitted as `c3_1` after SPIRV-Cross's name
collision. `tools/append_scene_color_vertex.py` verifies both capture hashes and the vertex IR
OpName provenance (`c1` = 43, `c3` = 44, Uniform storage), inlines `c1` from the captured code
range with the existing bit-preserving tool, converts only `c3_1` to the texelFetch form and
authorizes the alias `c3_1 -> hardware c3 -> NVN UBO0` **only** for this exact pair.

Measured access contract: 82 static read-only scalar loads, highest word index 91, so the
mandatory UBO0 extent is **368 bytes**. No stride was mutated; no earlier catalogue entry was
regenerated; the catalogue remains append-only (45 entries, 0..44).

`nvn_render.h` gains a per-draw guard `LC2_SCENE_COLOR_VERTEX_CBUF_REQUIRED`: it rejects a null
or shorter-than-368-byte UBO0 and prints `LC2_SCENE_COLOR_VERTEX_GUARD` receipts (first four
draws, then every 64th). A host test compiles the same predicate out of `runtime/lamentum-adapter.patch`
and checks the four boundary cases (null, 367, 368, 512, overflow) so the guard cannot silently
drift from its documented contract.

Build216 ELF SHA-256: `6b1171257de082b0b7dcbc1150c3f815f6fc62f2d0b95228b45fb605099d894a`.
Baseline manifest verified 435/435 before the build; previous executable kept as
`lamentum-nextos.before-216` (`19329da2…`). Host suite: 43 Python tests pass.

## newgame-15 device result (build216, 900 s budget)

Facts from the final log (`evidence/newgame-15`, raw log SHA-256 `a5bdb178…`, 19,343,594 bytes):

- Stop: **`TIME_LIMIT` only**. No `ZERO_SHADER_NOT_PINNED`, no unknown shader request at all.
- 1469 presented frames; last `NVN_PRESENT_PIXELS` frame 1469.
- 1111 `ROMFS_READ` calls; the read high-water mark reaches the full container
  (`0x6d330280` = 1,832,059,520 bytes), i.e. the asset pass covered the whole RomFS.
- 14 distinct catalogue program ids were bound (0,2,5,7,8,10,11,12,16,17,18,24,25,36);
  entry 44 was **never drawn** (`LC2_SCENE_COLOR_VERTEX_GUARD` count 0).
- Cleanup: `cleanup_errors: []`, MainUI back, supervisors unchanged, CPU online mask restored.

Interpretation, kept separate from the facts above: the run spent its whole budget inside the
level's load/display loop (a dark screen with a small amount of drawn content, ~1.6 fps) and
never reached the program that stopped newgame-14. Entry 44 is admitted but unproven at draw
time, exactly as entries 40-43 were when they were first added. No pixels, input response,
audio or save behaviour are claimed for it.

This corrects a provisional reading of the same log where the last `ROMFS_READ` offset
(`0x6aa60000`) was mistaken for the loading high-water mark; the maximum read *end* offset
covers the entire container. The next run therefore raises the budget rather than changing the
load path.

## What the next run answers

`newgame-16` uses the same build and env with a 2400 s budget. It decides between two outcomes
that this run cannot distinguish: (a) the load completes and a draw of entry 44 produces the
first `LC2_SCENE_COLOR_VERTEX_GUARD` receipt, moving the frontier to the next program; or
(b) the load stays in the same loop, which makes the load itself - not the shader catalogue -
the next measured problem, to be attributed with the quiet-environment profiling of §22.4
instead of another catalogue entry.
