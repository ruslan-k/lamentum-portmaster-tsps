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

## Owner/backing matrix and gate

| Class | Result |
|---|---|
| CMA pool base/size | **Proven for this boot**: boot log + `cma=128M` + `CmaTotal` + matching `/proc/iomem` range |
| `guest_malloc` pages | **Unknown** whether/how they consume CMA pages |
| GLES GL texture/buffer/renderbuffer | **Unknown** driver allocation path, per-call success, and physical backing |
| `DMA_HEAP_SYSTEM` | Heap endpoint exists; per-buffer backing and relation to GL remain unknown |
| CMA heap | Kernel support is enabled, but no `cma` device node was exposed; usage remains unknown |
| `DMA_HEAP_RESERVED` | Endpoint exists; implementation and backing remain unknown |
| Mali/KMS/GBM/EGL working buffers | **Unknown**; the DT register map does not assign a memory pool or identify runtime buffers |
| Current CMA occupancy owner | **Unknown**; no game ran and the single free-space gauge identifies no owner |

This closes only the reservation-geometry part of K1-B. It does not complete D-policy class attribution or provide a justified per-run uncertainty margin. Keep `T2_STORAGE_MARGIN_MIB` unset and `HOLD_RUNTIME`; build259 remains the installed runtime, and no current game ELF is available for a bounded launch.

**Next handoff:** trace the exact `reserved` and `system` DMA-heap registration/allocation paths and the Mali/GBM allocation route against the matched firmware binary and available runtime artifacts. Keep user-space scratch and GL storage as possible/unknown CMA consumers until that mapping is demonstrated.
