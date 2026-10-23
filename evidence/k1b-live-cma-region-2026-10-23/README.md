# K1-B — effective CMA region and heap inventory (2026-10-23)

## Scope and identity

This was a read-only target probe, not a launch or D preflight. A Python stdlib collector was streamed over the established `ssh tsps` path; it read `/proc/device-tree`, `/proc/cmdline`, `/proc/config.gz`, `/proc/iomem`, `/dev/dma_heap`, `/sys`, and filtered boot-log lines. No device files or settings were written, no allocation was forced, and no game was launched.

- Target: firmware `1.0.1`, kernel `5.15.147`, `aarch64`; model `sun55iw3`; compatibles `allwinner,a523`, `arm,sun55iw3p1`.
- Boot ID: `15b97fe4-5c48-412c-ba39-92efb1823286`.
- Probe start: `2026-10-23T09:48:50.687Z`; one-off probe SHA-256 `e36d7ff61b547e919b2d03bd979db40c7a146a105610ed0deebaa17c36b18dbf` (local scratch, not committed).
- The command line and full dmesg were not preserved; only the `cma=` token and CMA reservation line are recorded.

## CMA reservation geometry — confirmed

The target's live `/proc/cmdline` and `/proc/device-tree/chosen/bootargs` both contain `cma=128M`. `/proc/config.gz` reports `CONFIG_CMA_SIZE_MBYTES=16` and `CONFIG_CMA_SIZE_SEL_MBYTES=y`; the observed boot argument overrides that compiled default. The boot log states `cma: Reserved 128 MiB at 0x0000000073800000`.

The same region appears in `/proc/iomem` as `73800000-7b7fffff : reserved`. The inclusive interval is exactly 134,217,728 bytes (128 MiB), and `/proc/meminfo` reports `CmaTotal=131072 kB`. This establishes the active CMA pool's base and size for this boot; the generic `reserved` label in `/proc/iomem` is interpreted as CMA only because the boot log identifies that exact base and size.

The live tree reports 1 GiB RAM at `0x40000000`, plus one explicit `/reserved-memory/bl31` region at `0x48000000` of 16 MiB. It contains no `linux,cma-default` node. The `memory-region` scan found no nonempty references across 758 tree nodes. This is consistent with the CMA pool being reserved from the `cma=128M` boot argument rather than a DT `linux,cma-default` node.

## GPU/display and DMA-heap observations

- The tree includes `arm,mali-valhall` at `0x01800000` (64 KiB register aperture) and `allwinner,display-engine-v350` at `0x05000000` (4 MiB register aperture). Neither has a standard `memory-region` reference. These are register mappings, not evidence about backing for textures or scanout buffers.
- Kernel config has `CONFIG_DMA_CMA=y`, `CONFIG_DMABUF_HEAPS_CMA=y`, and `CONFIG_DMABUF_HEAPS_SYSTEM=y`. `/sys/kernel/mm/cma` is not exposed.
- `/dev/dma_heap/system` maps to `/sys/devices/virtual/dma_heap/system` (character device 252:0); `/dev/dma_heap/reserved` maps to `/sys/devices/virtual/dma_heap/reserved` (252:1). No `/dev/dma_heap/cma` node was listed. The name `reserved` does not establish its allocator or physical backing.
- One gauge sample during the probe: `CmaFree=130412 kB`, `MemAvailable=671620 kB`, `SwapFree=2065884 kB`, `nr_free_cma=32603`, `cma_alloc_success/fail=8/0`. This is explicitly **not** a paired D preflight and not launch clearance.

## Matched-kernel heap paths — static evidence

The exact matched `vmlinux` (`SHA-256 806182f8823b0db340f3f9beccf303e39571deb20b99386ee6a76442b8761b19`, Build ID `175a7f4d4731ebfbbdeb7695329115202f8b813a`) shows:

- `system_heap_create` calls `dma_heap_add` with the literal heap name `system`.
- `add_default_cma_heap` obtains the area name through `cma_get_name()` and passes it to `dma_heap_add`; `cma_get_name()` returns the CMA object's name field. `cma_heap_allocate` calls `cma_alloc`, so allocations through this implementation use the CMA API.
- If `cma_init_reserved_mem` receives no explicit name, its compiled fallback formats `cma%d`. The live node `/dev/dma_heap/reserved` therefore indicates either an explicit CMA-area name or another registration path; do not identify it from its name alone.
- A bounded scan of the single executable `PT_LOAD` segment found exactly two direct AArch64 `BL` sites targeting `dma_heap_add`, at `0xffffffc0085396d8` (`system_heap_create`) and `0xffffffc00853a7a4` (`add_default_cma_heap`). This is a direct-call scan of linked vmlinux only; it does not cover indirect/module call paths.
- The initcall table places `system_heap_create` at `0xffffffc0091de2d8` immediately before `add_default_cma_heap` at `0xffffffc0091de2dc`. The live device nodes are `system` minor 0 and `reserved` minor 1, matching that registration order. Together with the two direct vmlinux call sites and the Mali module import check below, this is a **high-confidence inference** that `reserved` is the default CMA heap for this boot, but not an exhaustive module-wide proof; only the Mali module was checked for heap API imports.
- The live `/lib/modules/5.15.147/mali_kbase.ko` was read-only copied to local scratch and SHA-256-verified against the device: 29,984,864 bytes, SHA-256 `2aaf1556a7a352caffec4db8821ea9d2f847529671321caa1a667de992d1ceb5`, Build ID `0dcaa84a5579b1122f98f29d0214723a2dff9603`. Its undefined-symbol list contains `__alloc_pages` and `dma_buf_*` operations, but not `dma_heap_add` or `cma_alloc`. Thus this Mali module does not directly register the heap through those APIs; its `__alloc_pages` route still does not prove whether its pages use CMA.

**Interpretation:** registration order and live minors strongly associate `reserved` with the default CMA heap, but the explicit name source and other-module registration paths are not fully audited. No per-buffer or game GL allocation was observed. Do not infer that Lamentum textures use this heap or that the idle CMA occupancy belongs to Lamentum.

## Owner/backing matrix and gate

| Class | Result |
|---|---|
| CMA pool base/size | **Proven for this boot**: boot log + `cma=128M` + `CmaTotal` + matching `/proc/iomem` range |
| `guest_malloc` pages | **Unknown** whether/how they consume CMA pages |
| GLES GL texture/buffer/renderbuffer | **Unknown** driver allocation path, per-call success, and physical backing |
| `DMA_HEAP_SYSTEM` | Generic allocator path is non-movable `__alloc_pages` (see [K1-D](../k1d-system-heap-page-path-2026-10-23/README.md)); per-buffer backing and relation to GL remain unknown |
| CMA heap implementation | **Proven in matched kernel** to allocate through `cma_alloc` |
| `DMA_HEAP_RESERVED` | **High-confidence registration inference** to default-CMA heap from initcall/minor ordering; explicit name input and per-buffer consumer remain unknown |
| Mali/KMS/GBM/EGL working buffers | **Unknown**; the DT register map does not assign a memory pool or identify runtime buffers |
| Current CMA occupancy owner | **Unknown**; no game ran and the single free-space gauge identifies no owner |

This closes the reservation geometry and identifies the likely default-CMA DMA-heap endpoint, but not any game allocation or physical occupancy owner. D-policy still lacks per-class peak overlap and uncertainty, so keep `T2_STORAGE_MARGIN_MIB` unset and `HOLD_RUNTIME`; build259 remains active, while the current-source ELF candidate is inertly staged and not run.

**Follow-up:** [K1-D](../k1d-system-heap-page-path-2026-10-23/README.md) later traces the generic `system_heap_allocate` path to `__alloc_pages` with masks lacking `__GFP_MOVABLE` and `__GFP_RECLAIMABLE`; the matched Unmovable fallback excludes CMA. That classifies the generic system heap allocator, not individual buffers or Lamentum's GL requests.

**Next:** trace user-mode GL/EGL/GBM routing and imports to `system`, `reserved`, or native Kbase; measure overlapping demands without allocating test buffers. Keep unjoined game requests and scratch as unknown until proven otherwise.
