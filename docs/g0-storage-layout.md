# G0 partial: checked format payload and deferred-BC admission

Reviewed upstream/main **14d8f80** and roadmap **§29.3 / §30** before this change.
The acceptance target remains **real gameplay at stable 30 FPS**. This component
change does not reach a world scene or close G0.

## Exact scope

The public adapter overlay adds `native/lc2_gl_storage.h`, a host-pure C layout
calculator, and calls it at deferred BC first-use admission in
`native/nvn_textures.h`. It checks every mip's decoded output payload before the
first-use `glBindTexture` and subsequent storage calls. It does **not** change
GL upload arguments, lazy eligibility, texture resolution, mip selection, memory
floors, swap, alias_physical, shaders, or the original game image.

Important limitation from source inspection: current `lc2_bc_lazy_eligible`
already requires `target == 1 && levels == 1`. Therefore a two/multilevel deferred
image is a **synthetic guard regression**, not a newly demonstrated reachable
Lamentum case. There is still no same-run proof of id295's original format,
actual mip count or immutability. This correction prevents future base-only
undercharging; it is not evidence mips caused the old GPU OOM.

## Calculator contract

Input is an explicit **sized GL internal-format intent**, target, dimensions,
layer/cube count, levels and **realized** samples. Output is the format-defined
per-level payload with dimensions, slices, byte offsets and checked total.

- Checked uint64 multiplication at every factor and checked accumulation.
- NPOT dimensions halve independently, clamping to one. Compressed blocks round
  up independently at **each** level, including the 1x1 tail.
- Arrays retain layer count; cubemaps have six faces; cubemap arrays use cube
  count as `layers`; only 3D depth shrinks per mip.
- Supported cases include RGBA8/sRGB8_ALPHA8, packed RGBA4/RGB5_A1, RGBA16F/32F,
  R8/RG8/RGB8, depth16/depth24-stencil8, BC1/BC3, ETC2/EAC RGBA and ASTC 4x4/6x6.
  Recognizing geometry is **not** proof the target driver supports that format.
- Reject unknown/unsized internal formats, including GL_RGBA and
  GL_SRGB_ALPHA_EXT, rather than guessing their storage from an external type.
  DEPTH_COMPONENT24 is deliberately unknown here; no three-byte physical
  allocation is fabricated for a driver that might store/pad it differently.
- Reject zero/GLsizei-invalid dimensions, impossible mip counts, invalid
  depth/layer/sample shapes and unimplemented compressed 3D/MS combinations.
- Any rejection leaves the entire caller output unchanged; successful output
  is published only after all mip arithmetic passes.

These bytes are **not a physical GPU memory measurement**. Tiling, alignment,
metadata, rounded MSAA, EGL images and retained/in-flight allocations remain
outside this pure calculation. The caller must prove the actual GL format,
context/storage generation, sampler completeness and alias lifetime separately.
A requested 2x sample count is not evidence the driver did not realize 4x.

## Executed synthetic examples

From the compiled C fixture, retained with every mip in
[`payload-cases.json`](../evidence/G0-storage-layout/payload-cases.json):

| Explicit self-authored descriptor | Format-defined bytes | MiB |
|---|---:|---:|
| RGBA8, 8192x8192, one level | 268435456 | 256 |
| RGBA8, 8192x8192, two levels | 335544320 | 320 |
| RGBA8, 8192x8192, full 14-level chain | 357913940 | 341.333332 |
| BC3 source blocks, 8192x4096, 14 levels | 44739280 | 42.666702 |
| Expanded RGBA8, 8192x4096, 14 levels | 178956972 | 170.666668 |
| ETC2/EAC RGBA8, 8192x8192, 14 levels | 89478512 | 85.333359 |

The compressed values are **arithmetic**, not an encoding, GL upload, physical
residency test or proposed conversion of the private id295 asset.

## First-use admission boundary

`lc2_bc_reserve_first_use` checks the pending 2D BC descriptor and maps the
existing decoded output intent explicitly: unsigned-byte RGBA to RGBA8/sRGBA8,
or linear float RGBA to RGBA32F. Unknown combinations fail closed. This mapping
specifies **decoded payload intent**, not a claim that the current legacy GL
calls have already been converted to sized/spec-correct GLES3 API triples.
Roadmap §29.2's sRGB upload correction and pixel fixture remain necessary.

The full layout is calculated before budget admission. The owner charge is
published only after the existing `t2_texture_budget_add` returns. A repeated
pending call with the same amount adds nothing; a stale amount is rejected.
Normal already-materialized refresh does not reserve a second time. The audit
field is now `requested-storage-bytes`, since it is no longer base-only.

The compiled regression uses the **actual added native helper**, with explicitly
synthetic STOP/budget collaborators and no GL implementation:

1. An 8192-square **two-level** RGBA8 intent asks for 335544320 bytes, exceeds the
   unchanged 300 MiB fixture cap, and never reaches the simulated GL-call site.
2. One level asks for 268435456 bytes and publishes one owner charge.
3. Repeated pending/materialized calls do not double charge.
4. A mismatched prior charge and unknown upload type stop before a new charge.
5. The public diff places the helper before the existing first-use GL bind.

Do **not** infer transactional global accounting from that fixture. The existing
`t2_texture_budget_add` still records the attempted amount before its process-wide
fail-closed STOP. No claim is made that this change fixes refund-on-error, alias
retirement, replacement or context loss. Existing finalization remains unchanged.
This is a narrowly scoped admission arithmetic correction, not the complete G0
allocation/lifetime ledger or a measured physical-memory saving.

## Validation and artifacts

- Test-first RED: missing calculator produced 11 expected failures; the later
  missing native admission helper produced one expected failure.
- GREEN: **138 full host tests PASS**, including **12** new G0 tests. The new
  tests execute compiled C extracted from the **public overlay**, not a private
  adapter checkout. They include **1024** fixed-seed randomized array/mip layouts
  against an independent arbitrary-precision Python reference.
- Trap-on-UB compiler instrumentation: all **12 G0 tests PASS** with
  `-fsanitize=undefined -fsanitize-undefined-trap-on-error -O1 -g`.
  The first ordinary UBSan attempt could not link because this host lacks
  `libubsan.so.1.0.0`; that failure is preserved in `sanitizer.json`, not called a
  successful sanitizer run. Trap mode removes that runtime-library dependency.
- **Build226**: pinned ARM64 container, **435/435** baseline files verified,
  full runtime build succeeds. Built `nvn_textures.h` and `lc2_gl_storage.h`
  match the working overlay source. ELF SHA-256:
  `1a8a242eab1f15cb9fbc550fee19c3ee8cd72d2ef6b58fd06941b4e58f669e32`.
- Shader catalogue SHA is unchanged. No original asset/shader blob or full
  private log is included in this evidence.
- **Not deployed; no device test in this step.** No new game/memory/display or
  FPS result is claimed. Clean publication export repeated all **138 tests** and the full
 AArch64 rebuild, with GLIBC requirements **<= 2.27**. The rebuilt whole ELF
 has a different SHA because **11 bytes** of compiler temporary object names
 differ in non-allocated `.strtab`; **both PT_LOAD segments are byte-identical**.
 The initially over-strong whole-ELF identity assertion and root-owned temporary
 cleanup failure are recorded in `publication-verification.json`; the exact
 disposable build directory was subsequently removed. This is not claimed as
 a byte-reproducible unstripped build.

## Still required before the next guarded game arm

1. Exact pre-refusal id295 descriptor, source identity, write generation,
   sampler and first consumer, tied to an owned run/phase (T1).
2. Transactional GL storage generations and exact refund/retirement on alias,
   replacement, error and context change; enumerate all untracked GL classes.
3. Spec-valid sRGB/linear uploads and a tiny independently checked GLES3 pixel
   fixture; no ignored GL errors.
4. Independent G1 compressed-driver physical/visual proof before any private
   BC3 -> ETC2 cache branch. Current ASTC/ETC2 calculator cases prove no support.
5. One owned guarded New Game probe at the **300 MiB** diagnostic cap, retaining
   exact pre-refusal memory and clean frontend restoration. Do not reproduce
   OOM to obtain metadata. Full G0 and 30 FPS remain **open**.
