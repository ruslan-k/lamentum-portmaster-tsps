# Shader-bank alias and real GLES fixture (builds 214–215)

This advances roadmap P0 shader-tail and §22.3 driver-fixture gates, not FPS acceptance.

## Entry 42: real literal-backed vertex, no TEST substitution

Pinned original code/control: 301af8ced90e7e506eb4d5ace0dfabd65453557bac79a74dfebacef7396b3098 /
1307789791808c82c0b5c7a141f34ef4780a3ec430630b1588b0803e4ffba4fe.

SPIR-V OpName identifies Uniform variables 43=c1 and 44=c3. The Vulkan GLSL's
`uniform c3 { ... } c3_1` suffix is a SPIRV-Cross name collision, NOT NVN slot 1.
`append_literal_vertex.py` validates both capture hashes and the vertex IR execution
model, specializes static c1 loads from the exact captured literal range using the
existing bit-preserving tool, and explicitly authorizes c3_1 -> hardware c3 -> UBO0.
`append_program.py` rejects the alias without exact code AND control hash pins.

The remaining application block has 83 static float loads through element 95:
384 bytes. A mandatory per-draw range guard rejects a shorter UBO0. No stride is
mutated and no earlier catalogue entry is regenerated. New literal-bank/alias tests
cover stage mismatch, truncated IR, unknown suffix mapping and incorrect control hash.

Build214 SHA-256: 9b8a02f5321c8f0f1bc13ea60dbc38f2e0ff3baf76c0cbbb42b1421c23797da3.
`newgame-13` admits entry42, then stops during setup on a new 768-byte fragment,
5ff482d48c9426db3f69965a3a6f96a3fe2e994f309135ddf71cda1a5f184c8a /
ccd3fcacba180042a8fe9c991e7044157958aa0b54fa582d4f8bc2eb1200ab00.
No new per-draw range/probe receipts occurred before that stop, so visible scene
contribution and actual gameplay are NOT established.

## Entry 43: real two-texture color fragment

`append_half_color.py` pins that exact pair, verifies fragment execution model and
samplers fs_tex0_20/fs_tex0_28 -> reserved NVN table14 offsets 0/8. It preserves
explicit scalar float16 conversion points through half pack/unpack, rather than
merely replacing the type with float32. Remaining float arithmetic is highp.
The f16vec2 variable in this captured program only holds unpacked half lanes and
already-rounded scalar assignments; arbitrary half-vector arithmetic is not supported.

Build215 SHA-256: 19329da2cc00adebe9dcd9668344f0ea5865f13da93f6086c11e2d9662cfc828.
newgame-14 admits both entries42/43, then stops on another original vertex:
801b91aed1fb1660a5c1ae9413994c0113547d596e4be5ef5143582addc325d0 /
ada676aaf675d0510aa7fea908d1473518596087a1a9dadf5a0cc43235eee820,
2048/2176 bytes, captured and translated to Vulkan GLSL but not appended.
No per-draw guard receipts occurred before this setup stop; game pixels are unproven.
Last present520; sampled MemAvailable minimum43 MiB. Kernel-pressure extraction
from the actual game process start (target HZ100) has no matching OOM/Mali/allocation
warning/error rows. That narrow kernel check is not a production memory qualification.
Cleanup passes, and clean-menu.png proves Spruce Recents is back on scanout.
Build215's original backup is lamentum-nextos.before-215. Host suite: 40 Python tests pass.

## Actual Mali GLES fixture, not just host algebra

`tools/gles_cbuf_fixture.py` uses self-authored source/data only. Both attempts ran
through Spruce principal with a 45-second subprocess bound; no game was running.
No window, swap, modeset, audio, guest assets or VM/sysctl changes were involved.

1. Default EGLDisplay attempt FAILED at eglInitialize (raw result.json retained).
2. Explicit GBM display + verified EGL surfaceless-context support PASSED on
   Mali-G57, OpenGL ES 3.2 v1.r32p0-01eac1.3634895aa082dda7c3407d9f3e199919.
   The 1024x2 RGBA32F source was sampled into a 1x1 RGBA32F FBO and read as floats.

Ten checked draws match expected finite values within 1e-6, with clean GL errors:
word indices 0/1/3/4, row boundary 4095/4096/4097, last word8191, first-texel update,
and rebinding a different cbuf texture/unit. Each draw also verifies the explicit
half conversion of 1.0003 to 1.0. Both attempts restore MainUI and the original CPU
mask; raw cleanup snapshots are retained.

Limits: this is not NaN-payload/signaling-NaN validation, complete f16 instruction
emulation, context-loss/name-reuse/in-flight-lifetime testing, a rendered game scene,
or a performance result. It validates this narrow lane/row/half/update/binding contract
on the actual GPU driver. The old pbuffer wording in the fixture's raw scope label
is generic; the successful GBM attempt used a surfaceless context and an FBO.

Evidence: evidence/newgame-13, evidence/newgame-14, evidence/gles-cbuf-fixture.
Original shader binaries, saves and game assets remain owner-local.
