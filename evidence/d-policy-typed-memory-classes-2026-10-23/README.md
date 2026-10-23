# D-policy source request-class map — 2026-10-23

## Decision

The source-level request classes can be distinguished, but their physical backing and peak overlap cannot. **D remains HOLD_RUNTIME**; no per-run margin is justified by this audit, and no game/launcher/device state was changed.

## Guard being evaluated

`native/t2_memwatch.h:107-145` implements `t2_storage_admit(gl_bytes, scratch_bytes, ...)`. It refuses an unset/invalid margin and, when configured, checks:

- `required_cma = gl_bytes + scratch_bytes + T2_STORAGE_MARGIN_MIB`
- `required_available = T2_MEMORY_FLOOR_MIB + required_cma`

The current default floor is 96 MiB. The calculation is deliberately conservative but does not establish that either request class consumes CMA. `nvn_bridge.h:168` includes `lc2_gl_admission.h` before `nvn_textures.h:169`; the direct GLES storage wrappers compute a format/layout payload and call admission before the raw GL function. They do not receive a per-call GL result or a physical-backing receipt.

## Source caller inventory

The current patched native tree contains 13 calls to `t2_storage_admit` plus its definition. This is a source map, not runtime reach or physical allocation evidence.

| Site | Guard request | Immediate source operation | What remains unknown |
|---|---|---|---|
| `native/lc2_gl_admission.h:27` | `gl=layout.bytes`, `scratch=0` | direct texture-image storage wrapper | GL success, driver allocation size, CMA/Mali backing |
| `native/lc2_gl_admission.h:39` | `gl=layout.bytes`, `scratch=0` | direct renderbuffer-storage wrapper | GL success, driver allocation size, CMA/Mali backing |
| `native/lc2_gl_admission.h:44` | `gl=size`, `scratch=0` | direct buffer-data wrapper | GL success, driver allocation size, CMA/Mali backing |
| `native/nvn_textures.h:440` | `scratch=bytes` | persistent CPU texture snapshot `malloc` | lifetime/overlap and physical page class |
| `native/nvn_textures.h:461` | `scratch=bytes+output_bytes` | CPU texture-view snapshot plus decoded `pixels` allocation | whether all counted bytes are newly live, lifetime/overlap, physical page class |
| `native/nvn_textures.h:506` | `scratch=bytes+linear_bytes` for BC6H | cube decode buffer plus linearization staging | stack/heap overlap and physical page class |
| `native/nvn_textures.h:690` | `scratch=plan.scratch_peak_u64` | BC stripe pixel buffer before upload | actual overlapping scratch lifetime and physical page class |
| `native/nvn_textures.h:826` | `scratch=scratch_peak` | BC first-use scratch when the logical texture budget is already charged | actual overlap/backing; this guard does not add a new GL charge |
| `native/nvn_textures.h:831` | `gl=layout.bytes`, `scratch=scratch_peak` | BC first-use decoded storage intent plus CPU decode peak | GL outcome/backing and whether this combined upper bound matches the physical overlap |
| `native/nvn_textures.h:886` | `scratch=scratch_peak` | CPU texture refresh `malloc`; a pending BC path may later respec GL storage | scratch lifetime/backing and GL outcome |
| `native/nvn_textures.h:1138` | `scratch=scratch_peak` | initial texture decode `malloc` before the GL upload | scratch backing and separate GL result/backing |
| `native/nvn_packaged_lazy.h:30` | `scratch=bytes` | packaged-texture decode buffer `malloc` | scratch lifetime/backing and subsequent GL result/backing |
| `native/nvn_vertex_stream.h:144` | `scratch=bytes` | stable-VBO CPU shadow `malloc` | shadow lifetime/overlap and physical page class |

A `scratch` request identifies requested userspace/temporary bytes, not a proven non-CMA class. A `gl` request is format-defined payload intent, not a successful driver allocation or physical CMA measurement. Do not promote either to `proven_cma_bytes` without an owner/timestamp-qualified source or runtime receipt.

## Existing replay and result

The A1 replay in [`evidence/a1-storage-admission-offline-replay-2026-10-23`](../a1-storage-admission-offline-replay-2026-10-23/README.md) reproduces the four build259 refusals exactly. Its typed records preserve `proven_cma_bytes=null` and `peak_overlapping_cpu_bytes=null` where unobserved:

- owner 61: 5,400,000 scratch bytes, class/phase/CPU peak unknown;
- owner 77: 10,368,000 scratch bytes, classified as `cpu_malloc` with the same requested CPU peak, but the supporting timeline association is log-order-only and does not prove CMA backing;
- owner 0: 512,000 and 8,294,400 GL bytes, with object/storage identity and specific GL class unknown.

The `proven_CMA_only` and `mixed_two_ledger` models refuse these unknown bases (`unknown-required-basis`). The four historical CmaFree denials validate the arithmetic, not a safe margin or the true backing class. The new stable D0 pair (`CmaFree=130,412 KiB`) does not fill those missing fields.

## Verification and disposition

- A1 offline replay focused tests: **15/15**.
- Current source inventory: 390 files, 77 GL/EGL candidates; 12 `wrapped+unmeasured`, 65 `unknown`.
- No production policy, launcher default, or device state changed in this source-map audit. `T2_STORAGE_MARGIN_MIB` remains unset. At that audit checkpoint no current game ELF was built/installed; the later post-H2a host ELF is recorded in [the host-build receipt](../current-elf-host-build-2026-10-23/README.md) and remains uninstalled. No game launch was attempted.

K1-B now gives a high-confidence mapping of live `/dev/dma_heap/reserved` to the default CMA heap: the linked initcall order and DMA-heap minors align, and `cma_heap_allocate` calls `cma_alloc`. K1-C identifies the live native Kbase page-pool path at migration parameter `0`: it requests `GFP_HIGHUSER|__GFP_ZERO`, whose exact-kernel Unmovable fallback excludes CMA. K1-D classifies the generic `/dev/dma_heap/system` page allocator path: its exact mask words omit both `__GFP_MOVABLE` and `__GFP_RECLAIMABLE`, and the Unmovable fallback excludes CMA. These findings narrow only those allocator paths; the 13 storage-admission callers are not joined to them, and Lamentum's imported DMA-BUF/GBM/EGL routes remain unknown. Do not assign all `gl_bytes` or `scratch_bytes` to a physical class from these findings. Keep `proven_cma_bytes` unknown for unmapped requests and maintain **HOLD_RUNTIME**; the per-run margin remains unreviewed. The latest complete same-boot D pair at `11:32:56.701–11:33:32.568Z` still showed `CmaFree=608 KiB` with no order-7+ CMA blocks; see the [staging/D preflight receipt](../current-host-elf-staging-preflight-2026-10-23/README.md).
