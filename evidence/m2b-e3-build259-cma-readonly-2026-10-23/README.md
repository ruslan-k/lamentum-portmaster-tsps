# Read-only CMA audit — build259 idle state (2026-10-23)

## Scope

This is a read-only TSPS audit following roadmap §86. No runtime was installed or launched, no CPU state was changed, and no game process was present. Two fresh non-multiplexed SSH snapshots 20.4 seconds apart were taken, followed by a post-probe identity/cleanup read-back. Boot ID remained `66203f22-4ac8-4a2a-a47c-cddc253d3bda`.

## Current state

- Installed runtime is still build259, SHA-256 `d72e2f69afa16dd5b846950f3fba80bc9926edcab9b2d45c57ed23faa14b9066`.
- MainUI was PID `28250`, starttime `4031805`, state `S`; `principal.sh` PID `2191`. No Lamentum/`terminator2d` process was found.
- CPU online mask was `4-7`; CPU0–3 were `online=0`, sysfs mode `0444`.
- Read-only pair, 20.4 s apart: `CmaTotal=131072 KiB`, `CmaFree=15456 KiB` in both samples; `nr_free_cma=3864` pages, `cma_alloc_success=36`, `cma_alloc_fail=0` in both. Page size was `4096` bytes. `MemAvailable` was `683448` then `683528 KiB`; `SwapFree=2033604 KiB` in both.
- A later read-back after diagnostic probes still showed `CmaFree=15456 KiB`, `nr_free_cma=3864`, the same CMA counters, MainUI PID/starttime, and no debugfs mount or temporary mount directory.

## Kernel and DMA-BUF evidence

The current boot's dmesg contained **8** order-4 `terminator2d-ne` page-allocation failures through `dma_heap_ioctl`. The latest was at kernel uptime `22380.157231 s` (PID `30017`), with `free_cma=4122` pages. Current `nr_free_cma=3864` pages is 258 pages (1,032 KiB) below that historical snapshot. This is a comparison of two observations, not a safe threshold or proof of a causal allocation. The filtered dmesg contained no explicit `out of memory`, `oom-kill`, or `killed process` match. No new matching warning appeared between the paired reads.

MainUI had one `/dev/dma_heap/system` FD and four DMA-BUF FDs, all `system` exporter: 16,384 B and three 3,686,400 B buffers. `/sys/kernel/dmabuf/buffers` listed matching inodes and sizes. Exporter/size metadata does **not** prove CMA backing or explain the free-CMA value.

`/proc/config.gz` reports `CONFIG_DEBUG_FS=y`, `CONFIG_CMA=y`, `CONFIG_DMA_CMA=y`, `CONFIG_DMABUF_HEAPS=y`, `CONFIG_DMABUF_HEAPS_SYSTEM=y`, and `# CONFIG_CMA_DEBUGFS is not set`. `/sys/kernel/mm/cma` is absent. No debugfs mount was present. Read-only debugfs mount attempts at `/sys/kernel/debug` and a temporary `/tmp` mountpoint failed with “already mounted or mount point busy”; post-checks verified no debugfs mount or temporary path remained. `mem_view` was never opened.

## Verdict and next gate

CMA is persistently low but stable during idle sampling; the available counters do not attribute retained CMA pages to a specific owner. The MainUI DMA-BUFs are metadata evidence only. The exact vendor allocator path and the reason the read-only debugfs mount is busy remain unresolved. Keep the device launch blocked; do not install build260 or enter New Game. Next safe work is host-side identification of the exact kernel/vendor heap implementation and a documented retry path, then reassess whether any additional non-invasive device evidence is available.