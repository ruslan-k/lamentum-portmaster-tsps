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
