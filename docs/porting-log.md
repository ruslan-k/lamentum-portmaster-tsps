# Porting log — Lamentum on TSPS

One entry per bounded device run. Facts only: what was deployed (hash), what the runtime
logged, which controlled stop ended the run, and how the device was left.

## 2026-10-19 — bring-up preparation (host side)

| Step | Result |
|---|---|
| NSZ base v0 -> NSP -> NCA | Program NCA 1,866,153,984 B; title keys added for `0100EC901551C000`/`…C800` |
| NSO extraction | `rtld` 6,304+3,384+664 B, `main` 30,836,964 B text, `subsdk0` 3,492,064 B text, `sdk` 5,777,024 B text |
| RomFS | one section file 1,829,445,184 B, SHA-256 `56a6e97124aed316cb123fe79f1711b6d6de37168fdbdbb057e1be513f386d0b`, `hactool -t romfs --listromfs` lists 34 files |
| Owner image | padded container: 0x200 zero header + RomFS (`romfs_offset=0x200`, `romfs_size=1829445184`, section SHA-256 `14f832e8e92e4377284f5f72679fd17932473f11248f132c5fc2ea5c414340b9`) |
| Baseline | terminator2d release sources applied cleanly; 435/435 manifest entries match |
| Adapter patch | 2 files / 8 lines (helper hoisting + declaration) |
| Build 01 | failed: `-Werror` on the baseline's own `write()` diagnostics and unused helpers in the pinned gcc 9.4 container |
| Build 02 | failed: `ZERO_ZX_GAME` undeclared / helpers unreachable outside the ZX profile / `type-limits` from `romfs_offset=0` |
| Build 03 | **ok** — `lamentum-nextos` 1,808,328 B, SHA-256 `9265c9e3d77d83341a83d5f9ea4bca2fc05c42f67092f3d4205be790bfe61bb9`, GLIBC ≤ 2.27 (base v0 content, superseded) |
| Update merge | `hactool --basenca … --exefsdir/--romfsdir` and `--section1=` produce the merged content: `main` 23,861,213 → 23,878,177 B, `main.npdm` changed, 11 RomFS files changed. Merged section dump 1,832,059,520 B; its own extraction is byte-identical to the merged tree (34/34 files) |
| Merged image | 0x200 pad + merged RomFS → section SHA-256 `80ad4427164a0b7ad61c3a3fcd955bd158635aac1ee42ebb67d01dfae279b893` (1,832,060,032 B) |
| Build 04 | **ok** — merged-content ELF `lamentum-nextos` 1,808,328 B, SHA-256 `9332846797605be9404ea814b54b06aaf3d64cd470a93550b2051c73b90e1a79` |

Open questions this build does not answer: which NVN structure profile this SDK generation
actually uses, whether the guest survives to its first `ProgramSetShaders`, and what the
runtime's first controlled stop is on real hardware.

## Device runs

Environment: TSPS Longan (SpruceOS), kernel 5.15.147, 986 MB RAM, 2.0 GB swap; port directory
`/mnt/SDCARD/Roms/PORTS/lamentum-switch/`; launch through the Spruce principal flow
(`tools/device_principal_test.py` writes `/tmp/cmd_to_run.sh` in the Emu path form, TERMs MainUI,
polls the port log, then checks the device state).

### Run 01 — stop: missing owner segments

Deployed only the runtime binary and the RomFS section. Log:

```
START native-aarch64 … rtld-entry=0x8000000 shims=Memory,Threads,IPC guest-quota=1536MiB
segment open failed rtld.text.seg
```

My deployment error, not a runtime limit: the 12 segment files from the owner image were absent
from the port directory. Fixed by transferring `image-05/*.seg` (12 files, 64 MiB) and verifying
all 12 hashes on the device.

### Run 02 — stop: `T2_LAZY_MESH_SEGMENT`

```
STOP status=T2_LAZY_MESH_SEGMENT pc=main.text.seg+0x0 detail=0x1d6c898 query_memory_calls=0x0
```

The baseline carries a generated IL2CPP patch (`native/t2_lazy_mesh.h`) keyed to *another*
title's `main` module: it requires `T2_LAZY_MESH_TEXT_SIZE == 0x2253788` and a specific text
SHA-256. Our `main.text.seg` is `0x1d6d000`. The runtime refused instead of patching foreign
code — correct behaviour. Disabled the optimisation for this title (`T2_LAZY_MESH=0`, logged as
`T2_LAZY_MESH off (T2_LAZY_MESH=0)`); it is a load-time optimisation only.

### Run 03 — stop: guest `CPU_FAULT` at `sdk.text.seg+0x341e70`

Advanced far past the previous frontier (full log: `evidence/device-03/latest.log`):

- 12 segments mapped (`rtld` 0x08000000, `main` 0x08005000, `subsdk0` 0x0b132000, `sdk` 0x0b7e4000),
  `TLS_READ_STUBS sites=62`, "ENTER original rtld; bridges=103; no manual relocations".
- Real guest SVC traffic: `QueryMemory` (id 0x6) over every segment, service lookups
  (`aoc:u`, `pctl`, then `pctl:s/a/r` refused with `SM_DENIED_BY_NPDM` — the title's own NPDM
  does not list them, which is the same refusal a console gives), `svc 0x29`, `0x21`, `0x18`.
- Heap: `HEAP_MAPPING_POLICY address=0x1000000000 bytes=0x5ba00000` (the guest's own
  `SetHeapSize`), then `svc 0x1`, `svc 0x1d`.
- Then `FAULT signal=0xb code=0x1 lr=sdk.text.seg+0x341054 sp=0x600ffc40`,
  `STOP status=CPU_FAULT pc=sdk.text.seg+0x341e70 detail=0xc0 query_memory_calls=0x1b`.

Disassembly of the faulting site:

```
+0x341040  mov x22,x0 ; add x0,x0,#0x18 ; … ; bl +0x341e60
+0x341e70  ldr x0,[x0,#0xa8]      ← fault: x0 = 0x18, so address 0xc0 (SEGV_MAPERR)
```

So an object pointer that should be non-NULL is 0 and the code reads `[this+0xa8]`. Call chain
from the guest frame dump: `sdk+0x341040 ← sdk+0x33d4d0 ← main+0x5b8afc ← main+0x4a972c ←
main+0x4a59bc ← main+0x4a5c20 ← main+0x15e638 ← main+0x154 ← rtld+0x864 ← sdk+0x2a3860 ←
rtld+0xd4`. The faulting helper is reached from Unity startup through an SDK routine, i.e. some
SDK-side allocator/state object is still NULL when Unity allocates.

**Hypothesis (not yet verified):** the baseline runtime targets a newer SDK generation
(its own banner says `sdk=19.3.9`) while this title is SDK 10.9.0.0; an init step that the
newer SDK performs before the first allocation is missing or answered differently here. The
next measurement is to identify which SDK function owns the NULL object (guest-side static
initialiser) and to compare the runtime's service/SVC answers around `SetHeapSize`.

Device left clean after every run: `runtime procs=0 mainui=1 cpu-online=4-7`.

### Run 03 — symbol resolution of the fault

The `sdk` module keeps 26,234 ELF symbols, so the faulting site resolves without guessing:

| address | symbol |
|---|---|
| `sdk+0x33d4b0` | `nn::os::AllocateAddressRegion(unsigned long*, unsigned long)` |
| `sdk+0x33d4a0` | `nn::os::InitializeVirtualAddressMemory()` |
| `sdk+0x340fa0` | `nn::os::detail::VammManager::AllocateAddressRegion(unsigned long*, unsigned long)` |
| `sdk+0x340e40` | `nn::os::detail::VammManager::IsVirtualAddressMemoryEnabled()` |
| `sdk+0x340e90` | `nn::os::detail::AddressRegionManager::AddressRegionManager(unsigned long, unsigned long)` |
| `sdk+0x2a3860` | `nn::init::Start(...)` |

Both `InitializeVirtualAddressMemory` and `AllocateAddressRegion` reach their state through one
global pointer:

```
adrp x8, #0xc452000
ldr  x8, [x8, #0x180]        ; x8 = *(0x0c452180)  — the SDK's OS/VAMM manager object
add  x0, x8, #0x3a0          ; this = manager + 0x3a0
```

The crash is *not* that call: it is a NULL `this` reaching a `VammManager`/`AddressRegionManager`
member (`ldr x0,[x0,#0xa8]` with `x0 = 0 + 0x18`). So the guest is in the SDK's **virtual address
memory (VAMM)** allocator path with an unconstructed manager.

Next measurement (not yet run): read `*(0x0c452180)` (and the constructor's target) at the moment
of the fault from inside the runtime, i.e. log the global before the first `AllocateAddressRegion`.
If it is NULL, the SDK's own init for VAMM did not run/complete on this title, and the question
becomes which init call the runtime answered differently (candidates: `svcGetInfo` heap/ASLR
information and the `InitializeVirtualAddressMemory` tail call through the bridge at `0x0bd5af80`).

## Runs 04-09 — the boot frontier moves into NVN

Each run below is one bounded principal-flow launch; `evidence/device-0N/` holds the port log
and the post-run device state (always `runtime procs=0 mainui=1 cpu-online=4-7`).

### Run 04 — relocation check by measurement

`MOMO_DUMP=0xc452140:0x100` at the stop showed the SDK's data table **is** relocated correctly
(word at `0x0c452180` = `0x0c4c5018`, a valid `sdk.data` pointer), so run 03's NULL `this` was
not a relocation failure.

### Runs 05-06 — the actual cause: `svcGetInfo(16)` reported 0

The runtime's own source documents the rule (`loader.c`, `case 16`):

```
/* MOMODORA (MEDIDO): Unity 2021 calls nn::os::AllocateAddressRegion unconditionally, so
 * VammManager::InitializeIfEnabled must enable itself. It enables on InfoType 16
 * (SystemResourceSizeTotal) != 0; the NPDM of this title declares 16 MiB. */
case 16:value=LC2_SYSTEM_RESOURCE_SIZE;break;
```

My owner-image generator had copied a constant `LC2_SYSTEM_RESOURCE_SIZE 0`, so the guest's SDK
saw system-resource size 0, skipped the VAMM init, and then dereferenced the unconstructed
address-region manager — exactly the `ldr x0,[x0,#0xa8]` fault of run 03.
`tools/prepare_lamentum_image.py` now reads the value from the title's own NPDM (`META` header,
`+0x14`): **16 MiB** for this title, and refuses to build an image when it is 0.

Result (run 06): the guest built its SDK managers, created 24+ threads, made 138 `QueryMemory`
calls and reached **NVN** (`nvnBootstrapLoader`).

### Run 06-08 — graphics entry trace and the window builder layout

- `GRAPHICS_TRACE_PROLOGUE` at `nvnBootstrapLoader`: this SDK's bootstrap opens with
  `str x20,[sp,#-0x20]!`, while the adapter only replayed `stp x29,x30` / `sub sp,sp,#imm`.
  The adapter patch now replays any pre-indexed `stp`/`str` prologue (the instruction's own
  registers and signed immediate), so the trace stays a faithful replay rather than a guess.
- `NVN_WINDOW_INTERVAL_REQUIRED`: the adapter decoded the window builder with the inherited
  17.5.3 profile (native +0x18, interval +0x20, textures +0x28) and read `+0x20` as the interval.
  `LC2_WINDOW_DUMP=1` printed the raw builder and the runtime's own NVN call trace named every
  field, so the layout is **measured** now:

  | offset | field | evidence |
  |---|---|---|
  | +0x08 | device | `nvnWindowBuilderSetDevice(builder, 0x340d70010)` |
  | +0x10 | texture count | `nvnWindowBuilderSetTextures(builder, 3, 0x600ffa80)` |
  | +0x18 | textures pointer | same call, array on the guest stack |
  | +0x20 | native window | `nvnWindowBuilderSetNativeWindow(builder, 0x340d77020)` |
  | +0x28 | present interval (minus one) | `nvnWindowBuilderSetPresentInterval(builder, 1)` |

### Run 09 — current frontier: the shader catalogue

```
NVN_WINDOW_REAL framebuffer=1280x720 bpp=32 textures=3 context-preserved=1 no-draw-no-present
ZERO_SHADER_UNRECOGNIZED code-bytes=256 control-bytes=2176 \
  code-hash=b3913c5cf5773c0e3a8d943f162b9d6d94297f269402690306575186a56e88ff \
  control-hash=b30b42eb5e91adc2a62a805707923b3704a7eefd916c04d3ae327cf1453a8a87
STOP status=ZERO_SHADER_NOT_PINNED pc=main.text.seg+0x542f1c
```

The runtime now creates the real 1280x720 window (three textures, context preserved, nothing
drawn or presented), Unity submits its first shader program, and the build - which ships the
empty catalogue stub - refuses to guess a translation. That refusal is the honest state of the
port: **no frame has been rendered yet**, and the shader catalogue is the next work item.

Current installed runtime: `lamentum-nextos` SHA-256 `85d4211b5e82e426eaca5d3e3b2cde44eb9d43c6d39237b2491f48b75ca0aace`.

## Shader inventory of the title's own modules (host-side scan)

Scanning the owner image segments for the NVN control-section magic `0x98761234` (version 1,
plausible control/code sizes) finds **10 programs**, all in `main.rodata`, each with a
`0x880`-byte control section and 0x100-0x400-byte code, e.g. at `main.rodata+0x86cac8`
(control 0x880, code 0x100). The size matches the runtime's own report
(`control-bytes=2176`, `code-bytes=256`) and the `MOMO_SHADERS` note about the `0x880` control
section, so this SDK generation is the modern-layout family.

That inventory is only what the title links into its modules: Unity 2019.4 keeps its
shader-variant set in the data partition (the 1.8 GB `Data/*.assets`/`level*` payload), so the
catalogue a playable build needs is larger than these ten and must be collected from the
programs the title actually requests at runtime (the runtime logs each request with both
hashes before it refuses).

## Shader translation is automatable for this title (verified locally)

The Hades-lineage Maxwell compiler (`spikes/wol-switch/tools/hades-eval/shader-compiler-rs`,
`cargo build --release` here in 1m54s) translates this title's program blobs into **real** GLSL
- not the empty-branch output that means instructions were dropped. Input layout: 0x30-byte
header, SPH at +0x30 (stage in bits 10-13: 1 = vertex, 5 = fragment), SASS from +0x80; the
blob is fed as-is.

All ten programs found in `main.rodata` translate (table and samples:
`evidence/shader-translation/README.md`). Program #1 (`code b3913c5c…`, `control b30b42eb…`)
is the program the last device run requested. Its translation is a 2D sprite vertex passthrough
(position from attribute 0, uv from attribute 1) and the paired fragment samples two mip levels
and averages them - the title's pixel-art upscale path, i.e. real game semantics.

`tools/translate_lamentum_shaders.py <image-dir> <workspace>` reproduces the pipeline offline
(owner blobs stay in the workspace; only our own GLSL and hashes may be published).

Remaining work before a frame: (1) per-program `mm_shader_binding` metadata (attributes,
varying masks, uniforms/samplers, colour-write mask, precision) and an ESSL100 rewrite of the
compiler's `#version 450`; (2) the runtime stops at the FIRST untranslated program, so the
catalogue has to grow until the title stops asking for new ones.

### Draft catalogue (not yet validated on device)

`tools/build_lamentum_catalogue.py` turns the translation workspace into a catalogue header in
the runtime's contract (`runtime/lamentum-shaders-draft.h`): our own ESSL100 rewrite of the
compiler output, attributes from the `in_attrN` declarations, per-slot varying masks inferred
from component usage, colour-write mask 15, mediump fragment contract.

Known limits of the draft, stated rather than hidden:

- six of the ten fragments use `texelFetch`/`textureSize`/`textureQueryLevels`, which ESSL100
  does not have. They are emitted with `error` set, so the runtime stops on them instead of
  drawing something that merely looks plausible; the rewrite (texture-size uniform +
  `texture2D` on a half-texel centre) is the next translation task;
- varying masks are inferred from the GLSL text, not measured on the device;
- `varying_read_masks` is only meaningful for fragment entries (for a vertex, `in` means
  attributes) - the draft prints both for every entry and the generator must be narrowed;
- no uniforms or samplers are declared yet; entries that need them must be extended from the
  control section's constant layout before they can be claimed as working.

The draft is therefore a scaffold for the next device iterations, not a working catalogue: the
runtime must be run, the next requested program read from the log, translated, added, and the
cycle repeated until the title stops asking for programs it does not have.

## Runs 10-13 — into the draw path, one measured contract at a time

| run | runtime SHA-256 (first 16) | stop | what it proved |
|---|---|---|---|
| 10 | `86f97fe1d43924ba` | `NVN_SAMPLER_PARAMETERS` | the generated catalogue was accepted: several `nvnProgramSetShaders` calls complete and the run moves past the shader stage |
| 11 | `7af845dca58086ba` | `NVN_GUEST_POINTER` at `main+0x526fb4` | after the sampler profile fix the sampler decodes correctly (`min=2 mag=0 wrap=1/1/1 lod=0:1000`) |
| 12 | `4b0d87c8d4eb8c63` | `NVN_GUEST_POINTER` | the refusal is our own diagnostic: `NVN_POINTER_REJECT id=154 address=0x0 bytes=48 perm=1` |
| 13 | `462aad71d45cc23c` | `NVN_RENDER_TARGET_VIEWS_REQUIRED` at `main+0x53024c` | the diagnostic no longer fail-closes (`T2P_CMDMEM_CALLBACK_TARGET … vtable=NULL`) and the run reaches render-target binding |

Two fixes landed here, both measured rather than guessed:

1. **Sampler builder for this SDK generation.** The title's own setters give the layout
   (`SetDevice` +0x00, `SetMinMagFilter` +0x08/+0x0c, `SetWrapMode` +0x10/+0x14/+0x18,
   `SetLodClamp` +0x1c/+0x20, `SetLodBias` +0x24, `SetCompare` +0x28/+0x2c,
   `SetMaxAnisotropy` +0x40, border +0x30..+0x3f; `nvnSamplerInitialize` copies 0x50 bytes to
   object+0x08). The inherited 17.5.3 profile is a *packed* builder and decoded this one as
   denormals. Selected by `LC2_SAMPLER_UNPACKED` in the owner image; the other profile is kept
   behind `#else`. This SDK also disables anisotropy with 0.0, which the inherited check
   rejected (`<1`).
2. **The command-memory-callback diagnostic was fail-closed.** It dereferenced the callback
   object's vtable through the strict pointer validator; this title carries a NULL vtable slot
   there, so our own probe stopped a healthy guest. It now checks membership first and prints
   what it finds (`vtable=NULL`, `unmapped`, …) instead of stopping — a diagnostic must never
   fail-close.

Frontier: `NVN_RENDER_TARGET_VIEWS_REQUIRED` — the guest binds a render target with an implicit
view; the next measurement is what this SDK's `nvnCommandBufferSetRenderTargets` actually passes.

### The render-target frontier, measured (run 13)

```
NVN_TEXTURE_REAL object=0x340dd3018 format=0x35 size=1920x1080 levels=1 depth=1
NVN_CALL name=nvnCommandBufferSetRenderTargets caller=main.text.seg+0x53024c
  arg=cmd 0x3403c1390  arg=count 0x1  arg=targets 0x6a5e9aa0  arg=views 0x6a5e9a60
  arg=depthStencil 0x340dd3018  arg=depthView 0x340d6f2c8
STOP status=NVN_RENDER_TARGET_VIEWS_REQUIRED detail=0x1
```

The title binds one 1920x1080 colour target **and a 1920x1080 depth-stencil texture (format 0x35)**.
The baseline's default profile refuses any depth attachment (`a[0]>1 || a[4]`) and only its
`ZERO_ZX_GAME` profile records the depth target plus both views. Supporting this title therefore
means giving it that record/replay shape under its own macro — record the colour target+view and
the depth target+view, and replay them as an FBO with a depth attachment — not relaxing the check.

## Runs 14-20 — depth targets, the 36-byte texture view, and the shader-capture loop

| run | stop | fix that moved the frontier |
|---|---|---|
| 14 | `ZERO_TEXEL_VIEW_RESERVED detail=4` | depth-stencil render target admitted (`LC2_RENDER_TARGET_DEPTH`: colour + depth recorded, replay already attaches depth/stencil) |
| 15-16 | same | the stop is the view decoder, not the target binder |
| 17-18 | `ZERO_TEXEL_VIEW_REQUIRED detail=0x23` | texture view re-keyed to the **36-byte** form measured from this SDK's own setters |
| 19 | **textures upload**, then `ZERO_SHADER_NOT_PINNED` | `ZERO_TEXEL_WRITE` lines: 640x512, 1920x1080, a mip chain, 512x512, 1280x720 - the title's real texture data reaches the host |
| 20 | `ZERO_SHADER_NOT_PINNED` (new program) | capture loop: `LC2_SHADER_DUMP=1` wrote the untranslated program's blobs |

Measured texture-view layout for this SDK generation (from `sdk.text` setters, not inherited):

| setter | address | store | meaning |
|---|---|---|---|
| `nvnTextureViewSetDefaults` | `sdk+0x469ec0` | zeroes 0x24 bytes | the view is **36 bytes** |
| `nvnTextureViewSetLevels` | `sdk+0x469ed0` | flag bit 0, base u8 +1, count u8 +2 | level range |
| `nvnTextureViewSetLayers` | `sdk+0x469ef0` | flag bit 1, u16 base +4, u16 count +6 | layer range |
| `nvnTextureViewSetFormat` | `sdk+0x469f10` | flag bit 2, u32 +8 | format |
| `nvnTextureViewSetSwizzle` | `sdk+0x469f30` | flag bit 3, 4xu32 +0xc | swizzle |
| `nvnTextureViewSetDepthStencilMode` | `sdk+0x469f50` | flag bit 4, u32 +0x1c | depth-stencil mode |
| (target) | — | flag bit 5, byte +0x20 | observed as flags `0x23` in a texel write |

(The 16-byte SDK 18 layout read those layer words as reserved bytes and refused the program.)

### The shader loop is now closed

1. the runtime refuses an untranslated program and, with `LC2_SHADER_DUMP=1`, writes
   `nvn-lc2-shader-{control,code}-<run>-<n>.bin` next to the port;
2. `shader-compiler-cli` translates the blob into GLSL (measured stage from the SPH);
3. `tools/build_lamentum_catalogue.py` folds it into the catalogue header;
4. rebuild, redeploy, run - the next program appears.

Run 20 captured the first data-partition program: code 2816 B, control 2176 B, hashes
`29d0db82…` / `8b4a63c3…`, stage 1 (vertex). Its translation declares **constant buffers**
(`layout(set = 0, binding = 0, scalar) uniform vs_cbuf_block_0u { uint data[16384]; } c0;`), so
the catalogue entry needs uniform/constant-bank metadata — the builder currently emits only
attributes and samplers. That metadata is the next work item; without it the entry would compile
but read no transforms.

### The captured vertex program: why the shader phase is the real wall

Run 20's program (`code 29d0db82…`, stage vertex) translates into this interface:

```glsl
layout(set = 0, binding = 0, scalar) uniform vs_cbuf_block_0u { uint data[16384]; } c0;
layout(set = 0, binding = 1, scalar) uniform c1            { uint data[16384]; } c1_1;
layout(set = 0, binding = 2, scalar) uniform c3            { uint data[16384]; } c3_1;
layout(set = 0, binding = 0, scalar) uniform vs_cbuf_block_0f { float data[16384]; } c0_1;
layout(set = 0, binding = 3, std430) buffer ssbo0          { uint _m0[]; } ssbo0_1;
```

It is a **skinned-mesh** vertex program: it computes a per-instance bone matrix offset from
`c0.data[68]` and `c3.data[24]` (`_86 * 56`, `>> 2`) and reads the bone matrix itself out of an
**SSBO**. GLES2 has no storage buffers, no integer bit operations and no `uint` uniform arrays, so
this program cannot be mechanically lowered: it has to be re-authored against the runtime's
uniform model (`uniform highp vec4 cN[…]` fed from the guest constant bank, kind 7) with the
skinning done from uniforms. That is the same class of work the West of Loathing port did by hand
for its sprite/mesh programs - and this title has one such program family per material, plus the
data-partition variants.

Status before this is solved: the port boots the original game code, creates its NVN device and
1280x720 window, uploads textures, and stops on the first program whose semantics ESSL2 cannot
express. No frame has been rendered.

## Run 21 — the shader-model ceiling, measured

Two capability experiments, both real:

1. **The runtime runs on an OpenGL ES 3 context.** `LC2_GLES3=1` switches the EGL renderable
   type and context version; the run then uploads the same textures and reaches the same shader
   request (`ZERO_SHADER_NOT_PINNED`). So the ES2 request is not a driver limitation - the ceiling
   can be raised without breaking the recorded-command path.
2. **The translator can emit GLSL ES.** `shader-compiler-cli --es 310` adds an ESSL 3.10 target
   (spirv-cross `V3_10Es`, `vulkan_semantics=false`). The ten built-in programs still translate.
   The captured skinned vertex program fails with:

   ```
   Buffer block cannot be expressed as any of std430, std140, scalar, even with enhanced layouts.
   You can try flattening this block to support a more flexible layout.
   ```

   i.e. its SSBO uses a scalar layout ESSL 3.10 cannot declare as an SSBO. Rendering that program
   on this backend therefore needs either a flattened SSBO layout or a texture-based bone-matrix
   feed - both are per-program re-authoring, not a flag.

Verdict recorded for the record: the port's remaining work is the shader-catalogue phase (one
re-authored program family per material plus the data-partition variants), followed by command
replay, memory, audio and input. That is a multi-week effort of the same shape as the West of
Loathing port, not a continuation of the contract fixes that carried runs 01-21.

## Automated catalogue loop and the frontiers after the shader stage

`tools/shader_loop.py` closes the loop: build -> deploy -> principal-flow run with
`LC2_SHADER_DUMP=1 AW_RELEASE=0` -> fetch the dumped program -> translate -> fold into the
catalogue (TEST-ONLY substitutes where ESSL cannot express the program) -> next iteration. It
stops as soon as a run ends on something other than `ZERO_SHADER_NOT_PINNED`.

What it found (each iteration is one build + one device run):

| frontier | detail | action |
|---|---|---|
| `ZERO_SHADER_NOT_PINNED` (768 B program) | second data-partition program | translated, catalogue 12 entries |
| `UNIMPLEMENTED_SERVICE detail=1` | `GET_SERVICE name=pl:u` | PlayLog stubbed like the other laboratory services (`pl:u`, `pl:s`), commands succeed with no output |
| `TIME_LIMIT` after 45 s | 32 guest threads alive, 98 textures, RSS 630 MB, 0 `DrawArrays/DrawElements`, 123 RomFS reads | the title runs but issues **no draws** yet |
| `T2_MEMORY_FLOOR` (default 140 MiB, then 64) | `available-MiB=58` while the guest holds ~600 MB | raised for the run only, never as a fix |
| `AUDOUT_HOST_FAILURE` | nxaudio stream start/pause error in one run (the previous run had audio with underruns) | device-level flakiness, not yet separated |

So the port now gets past SDK init, NVN device, window, textures, the shader catalogue and the
PlayLog service, and then sits in the title's own loading/initialisation without issuing a single
draw. The next work is therefore not more shader entries but (a) why the title never reaches its
first draw and (b) the memory headroom on a 986 MB board, with audio to be separated afterwards.

## Why there are no draws: the title spins on `pl:u` (measured with the stack profiler)

Run with `MOMO_STACK_SAMPLE_MS=1500 MOMO_STACK_SAMPLE_AFTER=8` (guest stack profiler). The
interrupted-PC histogram over the run is dominated by the SVC wrappers:

```
935  sdk.text.seg+0x393d98   -> SVC 0x16 (CloseHandle)
417  sdk.text.seg+0x393dc8
372  sdk.text.seg+0x393dd0
205  sdk.text.seg+0x393e78
```

and the service log explains it exactly:

```
931  GET_SERVICE name=pl:u
```

Every attempt looks like this:

```
GET_SERVICE name=pl:u
IPC handle=0x463 endpoint=0x3c type=0x6 command=0x1 data_bytes=0xc object=0x0
AW_STUB_SERVICE command=0x1 data=0xc
IPC_SESSION_PEER_CLOSED handle=0x463
SVC id=0x16 ... arg0x0=0x463          (CloseHandle)
```

So the PlayLog service (`pl:u`) is requested ~931 times in 100 s: the title's SDK initialises it,
the session ends right after our laboratory stub answers command 1, the SDK treats that as a
failure and retries, closing the handle each time. The guest therefore never leaves its
initialisation loop and never issues a draw - the "no draws" frontier is a *service-semantics*
problem, not a rendering one.

Note: this is not the earlier `UNIMPLEMENTED_SERVICE` (that one was fixed by routing `pl:u`/`pl:s`
to the stub). The remaining question is what the SDK needs from the `pl:u` session: who closes it
(the runtime's session lifecycle or the guest after an error) and which reply shape makes
`nn::pl::Initialize` succeed. That is the next measurement; no re-authored shader or draw work can
make progress before it.

### The `pl:u` retry loop is the platform (shared-font) service, and the guest closes the session

Refinement of the `pl:u` finding:

- `pl:u` in this SDK is **`nn::pl` = the platform service**, not PlayLog. Its symbols in the title's
  own `sdk` module are `nn::pl::RequestSharedFontLoad(fontType)`, `nn::pl::GetSharedFontLoadState(fontType)`,
  `nn::pl::GetCurrentIlluminance`, `nn::pl::BeginVrMode` - i.e. shared-font and platform queries.
- The runtime prints `IPC_SESSION_PEER_CLOSED` only when the **guest** sends a session-close
  message (`loader.c`, `h0==2`). So the SDK closes the `pl:u` session itself, immediately after our
  laboratory stub answers command 1 with "success, no output". The SDK then retries: 931
  `GET_SERVICE name=pl:u` in 100 s, with a `CloseHandle` spin (935 profiler samples at the
  CloseHandle wrapper).
- In other words the loop is not our session dying: it is the SDK rejecting the reply shape and
  closing the session. The reply must carry what the platform proxy expects, and the shared-font
  data the title asks for does not exist in this port at all.

Physical check while the title "ran": the device's own `kmsgrab` capture taken mid-run shows the
SpruceOS standby clock (`08:19 PM / Monday, October 19 / 90%`), i.e. nothing of the game reached
the panel - consistent with zero draws.

Next step: implement the platform service's shared-font contract (the load-state query and the
font payload), or prove the title can boot with a font substitution. Until that reply is right the
guest never leaves its initialisation loop, so no shader, draw or memory work can produce a frame.

## `pl:u` contract implemented - the 931-request loop is gone

The Switchbrew "Glue services" page documents the platform service (`pl:u`, `nn::pl::sharedresource::
detail::IPlatformSharedResourceManager`) that this title uses for shared fonts:

```
0 RequestLoad(SharedFontType u32)              no output
1 GetLoadState(SharedFontType u32)             -> LoadState u32 {0x00 Loading, 0x01 Loaded}
2 GetSize(SharedFontType u32)                  -> u32
3 GetSharedMemoryAddressOffset(SharedFontType)  -> u32
4 GetSharedMemoryNativeHandle()                -> SharedMemory handle (mapped 0x1100000, R--, TTF data)
5 GetSharedFontInOrderOfPriority(LanguageCode u64, 3 x type-0x6 buffers) -> u8 loaded, u32 count
```

`EP_PL` now implements 0/1/2/3/5 (state reports Loaded, sizes zero because no font blob is bundled).

Measured effect on the device: `GET_SERVICE name=pl:u` dropped from **931 requests per 100 s to 2**,
and the CloseHandle spin disappeared - the title leaves its initialisation loop.

New frontier, same run: after the second `pl:u` request the guest sends command 4
(`GetSharedMemoryNativeHandle`) and then stops with

```
STOP status=INVALID_SESSION_HANDLE pc=sdk.text.seg+0x393d70 detail=0x0
```

i.e. the SDK stored the (missing) shared-memory handle and later used it. The runtime has no
shared-memory object kind (SVC 0x2c/0x2d here are MapPhysicalMemory/UnmapPhysicalMemory), so
serving the font requires a new subsystem: allocate the 0x1100000 region, hand out a handle for it,
implement svcMapSharedMemory/UnmapSharedMemory with R-- permissions, and place a TTF at offset 0.
Still zero draws.

### Shared font: the handle must be a CMIF copy-handle descriptor

`pl:u` command 4 (`GetSharedMemoryNativeHandle`) needed a real shared-memory object, and the runtime
already had the subsystem (`shared_create`, `EP_SHARED`, SVC 0x13 MapSharedMemory). Two things were
missing:

1. `shared_create` refused anything above 16 MiB; the platform font region is 0x1100000 (17 MiB).
2. The reply shape: passing the handle through `ipc_reply`'s move field produced `handle=0` on the
   guest side (it then called `MapSharedMemory(0, ...)` and stopped with INVALID_SESSION_HANDLE).
   The shape the SDK parses is the CMIF **copy-handle descriptor**, the same one the HID
   shared-memory reply uses:

```
ipc_reply(buffer,req.token,0,NULL,0,0,req.domain);
put32(buffer+4,read32(buffer+4)|0x80000000U);put32(buffer+8,2);put32(buffer+12,handle);
```

With that, the title maps the font region and continues: `INVALID_SESSION_HANDLE` disappeared and the
run moved on to `ZERO_SHADER_NOT_PINNED` again, i.e. back into shader compilation. The font itself is
a real TTF copied into the region (`PL_SHARED_FONT path=/mnt/SDCARD/spruce/Font Files/Noto.ttf
bytes=0x1e9f18`); `LC2_SHARED_FONT` overrides the path.

That means the service side of the port now holds: SDK init, NVN device/window/textures, the platform
service with a real shared font, and the automated shader catalogue. The remaining gate before the
first draw is the catalogue size: `tools/shader_loop.py` folds one program per build+run cycle
(build-43..48 in six iterations, all translated, zero ESSL100 texel-fetch entries left).

## Two host-side fixes that moved the port to real draws

1. **Host mappings are invisible to the guest** (`HOST_MAPPINGS_RESERVED count=0x46 regions=0x52`).
   The guest shares the address space with the host, but `svcQueryMemory` only knew guest regions, so
   the title's allocator picked an address inside the host's libc/EGL range and its MapSharedMemory
   failed: `SHARED_MAP_FAILED detail=0x7f6e204000`. `host_mappings_reserve()` now reads
   `/proc/self/maps` at startup and registers every host mapping below the guest limit as occupied.
   Effect: the font maps, and the same run recorded **11** `DrawElements` calls (was 1, earlier 0).

2. **The clip wrapper required `void main() {` on one line**, but the translator emits
   `void main()` with the brace on the next line, so program 0x10 stopped with
   `NVN_LC2_CLIP_VERTEX_SOURCE`. The wrapper now matches `void main(` and renames the entry point in
   place, keeping `()` and any parameters.

Catalogue status after the automated loop: 21 translated programs, no ESSL100 texel-fetch entries
left, 11 draws per run. Current stop: `NVN_SHADER_COMPILE_FAILED` for program 0x10 with
`0:4: P0001: Extension directive must occur before any non-preprocessor tokens` - the `#extension`
block ends up after non-preprocessor tokens once the runtime's later wrappers (varying interface /
precision) are prepended, so the fix belongs in the runtime's final source assembly (hoist
`#extension` right after `#version`), not in the catalogue files (which were normalised anyway).

## Shader source normalisation: extensions first, then version

The compile gate for program 0x10 moved three times, each step exposing the next real defect:

| attempt | driver error | cause | fix |
|---|---|---|---|
| 1 | `0:4: P0001: Extension directive must occur before any non-preprocessor tokens` | translator/wrapper preludes pushed `#extension` below other tokens | `nvn_hoist_extensions()` pulls `#version` and every `#extension` out and rebuilds the source as version, extensions, rest |
| 2 | `0:3: P0003: Extension 'GL_EXT_scalar_block_layout' not supported` | translator asks for scalar layout, Mali has none | unsupported extension dropped instead of required |
| 3 | `0:4: L0001: Typename expected, found 'layout'` | the source carries `layout(...)`/`in`/`out` but **no `#version` line**, so the driver parses it as ESSL 1.00 | not fixed yet: prepend `#version 300 es` when a source uses ES3 syntax and declares no version |

Draws are stable at 11 per run through all of this; the environment (SDK, platform service, font,
catalogue) holds. The next step is the version-less-source case above, after which the compile gate
should clear and the run can reach its first present.

### The real cause of the `layout` error: the catalogue carries Vulkan GLSL

Dumping the compiled source (`LC2_DUMP_SHADER=1`) settled it:

```
#version 100
precision highp float;
layout(set = 0, binding = 0, scalar) uniform vs_cbuf_block_0f
{ float data[16384]; } c1;
```

That is **Vulkan GLSL** (spirv-cross default semantics: `set`, `binding`, `scalar`), wrapped in a
`#version 100` header. Mali parses it as ESSL 1.00 and rejects the qualifier
(`L0001: Typename expected, found 'layout'`). Runtime-side rewrites (hoist, drop unsupported
extensions, qualifier stripping, forced `#version 300 es`) do not clear it, so the fix belongs one
level up: **translate the programs with `--es 310`** (`shader-compiler-cli --es 310` already exists and
emits ESSL blocks without set/binding/scalar), then rebuild the catalogue. That also removes the
`GL_EXT_scalar_block_layout` request that Mali refuses.

State: 11 draws per run unchanged, present still not reached, device clean.

### The catalogue builder re-headers every entry as ESSL 1.00

With the programmes converted to ESSL 3 (`#version 300 es`, `set/binding/scalar` removed, `std430`
turned into `std140` for uniform blocks, `#extension` lines stripped), the compiled source still came
out as:

```
#version 100
precision highp float;
uniform vs_cbuf_block_0f
{ float data[16384]; } c1;
```

and Mali answered `0:3: L0001: Typename expected, found 'vs_cbuf_block_0f'` - interface blocks do not
exist in ESSL 1.00. The re-headering is `tools/build_lamentum_catalogue.py` itself: it prepends
`#version 100` plus a precision line for every entry (lines 26 and 75), so the 300 es header written in
the `.glsl` files never reaches the runtime. Confirmed locally: 13 entries in the generated header carry
`#version 100`, none carry `300 es`.

Next step is therefore a builder change, not a runtime one: keep `#version 300 es` (and the precision
line) for entries whose body uses interface blocks or in/out declarations, keep the ESSL 1.00 header for
the legacy attribute/varying programmes.

### ESSL 3 catalogue: compile gate cleared, link gate is next

Four driver-compatibility defects were cleared in sequence, each visible only after the previous one
(`0:4 layout` -> `0:3 block name` -> `0:33 fma` -> `0:18 location on vertex output`):

1. the catalogue builder re-headered every entry as `#version 100`; entries with interface blocks or
   `std140` blocks now keep `#version 300 es`;
2. ESSL 3.10 has no `fma` -> `#define fma(a, b, c) ((a) * (b) + (c))` in the ES3 prelude;
3. `layout(location)` is illegal on vertex outputs in ESSL 3.10 (`S0060`) -> varyings are matched by
   name, spirv-cross keeps the names identical across stages;
4. result: both stages **compile**, and the run now stops on
   `NVN_PROGRAM_LINK_FAILED detail=0x1` with `L0001 Shader languages do not match` - the vertex stage is
   ESSL 3.00 (interface blocks) while its fragment partner is still ESSL 1.00, because the builder
   decides the dialect per file, not per program.

Next step: decide the dialect per program pair (if either stage needs ES3, both are ES3; the fragment then
keeps `out frag_color0`/`in` instead of `varying`/`gl_FragColor`). Draws stay at 11 per run, no present yet.

### Compile and link gates are cleared; the draw now stops on attribute kinds

With one ESSL 3.00 dialect for the whole catalogue (`#version 300 es` for all 34 entries, zero
`#version 100`), both stages compile **and link**, and the run reaches the draw path:

```
NVN_ATTRIB_KIND_MISMATCH index=0x0 shader-kind=0x2 format=0x22 format-kind=0x0
STOP status=NVN_LC2_VERTEX_SHADER_KIND_MISMATCH detail=0x22
```

Attribute 0 is declared as an integer/uinteger attribute by the program while the guest binds NVN
format 0x22, which decodes to 3 x float32. The instrumented stop (added this run) names the index and
both kinds, so the next step is to find which catalogue entry reports kind 2 for attribute 0 - the
builder's `attributes_of` derives it from the declared GLSL type, and no `uvec`/`ivec` appears in the
generated header, so the kind most likely comes from the compiled program (`glGetActiveAttrib`) for a
program whose GLSL types were rewritten. Either the affected program needs its attribute type preserved
as integer, or Unity's packed attribute must be declared the way the title expects.

Draws still 11 per run; no present yet; device clean after the reboot.

### Draw path reached with real clears: the ESSL3 gates are cleared

Sequence of defects closed in one session, each visible only after the previous (all in our glue):

| # | driver / runtime report | cause | fix |
|---|---|---|---|
| 1 | `0:4 layout` | catalogue re-headered every entry `#version 100` | builder keeps `#version 300 es` for block programs |
| 2 | `0:3 block name` | dialect chosen per file, not per program | one ES3 dialect for every entry (34/34) |
| 3 | `L0001 Shader languages do not match` | ES3 vertex linked with ESSL1 fragment | same |
| 4 | `L0007 varying in_attr2 not declared in vertex` | two stages name varyings differently | varyings renamed `varying_<location>` in both stages from the translator's locations |
| 5 | `S0060 location on vertex output` / `P0003 separate_shader_objects not supported` | Mali has no such extension | locations dropped, names carry the pairing |
| 6 | `0:33 fma`, `unpackFloat2x16`, `#error FP16` | GLSL 4.x / fp16 in an ES3 world | `#define fma(...)`, `unpackHalf2x16`, fp16 promoted to fp32 |
| 7 | `NVN_LC2_VERTEX_SHADER_KIND_MISMATCH index=0 shader-kind=2 format=0x22` | builder mapped `vec4` -> kind 2 (uint) and everything else -> 1 | kind from the type: float 0, int 1, uint 2 |
| 8 | `NVN_LC2_UNDEFINED_FRAGMENT_COLOR detail=0xffffffff` | Animal Well's "programme 6 writes no colour" special case keyed on the id | keyed on the declaration (`declared_mask==0`) |

Measured now:

```
MOMO_CLEAR_COLOR target=176 rgba=0.0235294,0.0235294,0.0235294,0 mask=0xf draws=0
MOMO_CLEAR_COLOR target=221 rgba=0,0,0,1 mask=0xf draws=17
```

draws 17 per run (was 11), two render targets cleared with real colours, and the next stop is a varying
one: `NVN_LC2_SHADER_UNDEFINED_VARYING detail=0x1` - a fragment reading `varying_1` that its vertex
partner does not write, i.e. the remaining work is pairing varyings per program (the builder renames by
location, so the offending pair must disagree on which locations the vertex writes).

### Varyings completed instead of failing closed; 29 draws, and the replay now reports GL state

The `NVN_LC2_SHADER_UNDEFINED_VARYING` stop was Mali-specific: the console accepts an unmatched varying
(the value is undefined), Mali refuses to link a fragment input its vertex partner never declares
(`L0007`). The runtime now records the gap, appends `out vec4 varying_<n>;` to the vertex stage
(unwritten, exactly as undefined as on the console) and continues:

```
NVN_VARYING_UNDECLARED location=0x1 read=0x3 written=0x0
NVN_VARYING_COMPLETED declarations=1
MOMO_CLEAR_COLOR target=2 rgba=0,0,0,1 mask=0xf draws=29
STOP status=NVN_REPLAY_GL_ERROR detail=0x505
```

draws 29 (17 before, 11 at the start of this run of fixes), three targets cleared, and the next stop is
`detail=0x505` = `GL_INVALID_FRAMEBUFFER_OPERATION` during replay: something draws into an incomplete
framebuffer. That is the next concrete gate - a framebuffer completeness question, not a shader one.

### First present reached (frame is black) and what stops right after

Two diagnostic switches (both labelled, neither a fix) made the failure visible:

- `COTM_FBO_CHECK=1` - completeness check on cached framebuffer binds: **no stale framebuffer**, so the
  `0x505` is not a binding problem.
- `COTM_GL_ERROR_PER_OP=1` - per-command `glGetError()`: **no error after any single command**, so the
  error is raised by the batched boundary itself (its own fence/publication work), not by the replay.

With `COTM_GL_ERROR_IGNORE=1` (records the error and continues, explicitly a diagnostic) the run gets
past it and **presents a frame**:

```
NVN_REPLAY_GL_ERROR_IGNORED error=0x505 draws=0x1f frame=0x0
NVN_PRESENT_PIXELS frame=1 nonblack=0 max=0 white=0 texture-draws=13 status=BLACK-SAMPLE
STOP status=NVN_QUEUE_CONTEXT pc=main.text.seg+0x53b8d8 detail=0x300d
```

So: 31 draws, a real `present`, and the sampled frame is entirely black (`nonblack=0`). The next stop is
`NVN_QUEUE_CONTEXT detail=0x300d` = `EGL_BAD_SURFACE` from `nvn_single_make_current(surface, surface,
context)` right after `nvnQueueWaitSync` - the surface is no longer valid at that point, most likely
because it was recreated by the swap path.

Next two gates, in order: (1) EGL_BAD_SURFACE at the queue wait, (2) why the presented frame is black
while 13 texture draws are recorded (asset upload / final composition source).

### After the first present the window surface stops being usable for make_current

Measured (build-98/99, `COTM_GL_ERROR_IGNORE=1`):

```
NVN_PRESENT_PIXELS frame=1 nonblack=0 max=0 white=0 texture-draws=13 status=BLACK-SAMPLE
NVN_QUEUE_CONTEXT_DETAIL display=0x55b7ac00e0 surface=0x55b7c1c670 context=0x55b7c1cd40 egl=0x300d
STOP status=NVN_QUEUE_CONTEXT pc=main.text.seg+0x53b8d8
```

`0x300d` = `EGL_BAD_SURFACE`. The handles are the objects the present path had just used successfully, so
the surface is not a stale value - the driver refuses it after `eglSwapBuffers` on the fbdev window
surface. A detach-and-retry (`eglMakeCurrent(NO_SURFACE)` then retry, build-99) does **not** clear it, so
it is not a stale binding.

Next step: separate the render binding from the present binding - render into the pbuffer/FBOs and bind
the window surface only for the swap - instead of returning to `make_current(window surface)` after the
present. That is also where the black frame has to be investigated: 13 texture draws are recorded before
the present, and the sampled backbuffer is uniformly black.

### The fbdev window surface can be swapped exactly once

Three attempts, all measured on device:

1. **Render on the pbuffer, bind the window surface only for the swap** (build-100): the replay stops
   asking for `make_current` on the window surface, and the run gets one frame further - the failure
   moves from the queue acquire (`NVN_QUEUE_CONTEXT`) to the *second present* (`NVN_PRESENT_CONTEXT
   detail=0x300d`). So rendering is fine on the pbuffer; presenting is the problem.
2. **Recreate the window surface when the bind fails** (build-101): a freshly created
   `eglCreateWindowSurface` for the same native window is refused too - no recreation is logged because
   the retry fails before the log line, and the stop is the same.
3. **`eglReleaseThread()` after the swap** (build-102, gated by `COTM_EGL_RELEASE_AFTER_SWAP=1`): the
   release line never appears, because the next present stops at the bind before reaching that code.

Conclusion: on this Mali/fbdev stack a window surface accepts one `eglSwapBuffers` and then refuses every
`eglMakeCurrent`, including on a recreated surface. Presentation therefore cannot stay on
`eglSwapBuffers`; the next step is the framebuffer-copy path (`nvn_direct_composition.h` in this runtime
already binds the default framebuffer, and TSPS ports normally present by writing the composited texture
to the panel), driven from the same "copy the final texture" step the present path already performs.
Also still open: the first frame is black (`nonblack=0`) with 13 texture draws before it.

## Panel presentation implemented (COTM_FB_PRESENT=1)

`eglSwapBuffers` on this Mali/fbdev stack accepts one swap and then refuses every `make_current`
(build-100..102). Presentation now bypasses EGL entirely: the present quad renders into an offscreen
FBO, the frame is read back (`GL_BGRA_EXT`, rows flipped) and copied into the mapped `/dev/fb0`, with
`FBIOPAN_DISPLAY` flipping between the two pages. `nvn_fb_present.h` holds it; the render binding stays
on the pbuffer, so the broken window surface is never touched again.

Measured (build-105/106):

```
NVN_FB_PRESENT enabled=1 fb=1280x720 line=0xb40 pages=2 swap=none
NVN_PRESENT_PIXELS frame=1 ... status=BLACK-SAMPLE
NVN_PRESENT_PIXELS frame=2 ... status=BLACK-SAMPLE
NVN_PRESENT_PIXELS frame=3 ... status=BLACK-SAMPLE
STOP status=NVN_COMMAND_REUSE_BEFORE_COMPLETION detail=0x2
```

So frames are now presented through the panel path (three before the stop, instead of one), and the stop
moved to the command-list recycling that the swap used to mark complete; marking the GL completion after
the readback did not clear it (the list's `completed` flag is set by the queue path, not by the GL
serial).

Two facts to keep straight: (a) the physical screenshot taken 105 s into the run still shows the Spruce
PORTS menu with Lamentum selected, so the panels' pixels are not yet ours at that moment; (b) every
presented frame samples black (`nonblack=0`) even though 13 texture draws precede it. The next work is
therefore (1) the command-list completion after a panel present, and (2) why the composed frame is black.

## Why the frame is black: the swapchain textures are untouched, and most programs are TEST substitutes

`COTM_WINDOW_SAMPLE=1` samples each swapchain texture at present time:

```
NVN_WINDOW_SAMPLE index=0 id=2 texture=1 size=1920x1080 nonblack=0 max=0 status=0x8cd5
NVN_WINDOW_SAMPLE index=1 id=3 texture=2 size=1920x1080 nonblack=0 max=0 status=0x8cd5
NVN_WINDOW_SAMPLE index=2 id=4 texture=3 size=1920x1080 nonblack=0 max=0 status=0x8cd5
```

`0x8cd5` is `GL_FRAMEBUFFER_COMPLETE`, so the sample is valid and the three window textures are
**completely black** (`max=0`, not merely dark). The clears the log shows (`target=176 rgba=0.0235…`,
`target=221 rgba=0 0 0 1`, `target=2`) go to intermediate render targets, never to the swapchain: the
title's final composite pass does not write into the window textures in this run.

The reason is in the catalogue: 11 of its sources are TEST-ONLY substitutes (`grep -c TEST-ONLY`), i.e.
about ten programs are placeholders, not translations. They are placeholders because their constant
buffers are **SSBO storage blocks** (`uniform … { float data[16384]; }`), which ESSL 3.10 does not have,
and spirv-cross refuses to express them: "Buffer block cannot be expressed as any of std430, std140,
scalar, even with enhanced layouts."

Next step, concrete and bounded: convert those blocks to **uniform blocks** in the SPIR-V before
cross-compiling - rewrite `OpDecorate BufferBlock` to `Block` and the variable's storage class from
`StorageBuffer` to `Uniform` - then translate with `--es 310`. A read-only cbuf is a UBO semantically,
and the Mali-G57 uniform-block limit (64 KB) covers `float data[16384]`. That turns the placeholders into
real translations, which is the precondition for anything appearing on the panel.
