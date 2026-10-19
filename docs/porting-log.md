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
