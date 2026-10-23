# K1-F — read-only CMA occupancy, DMA-BUF ownership and lifecycle check

This phase prioritizes safe first-gameplay readiness by checking the live memory state and visible owners. It does **not** infer a leak, reclaim memory, or make a game launch safe.

## Fresh same-boot allocator pair

A complete pair on boot `15b97fe4-5c48-412c-ba39-92efb1823286` (firmware `1.0.1`, kernel `5.15.147`) at `12:11:19.541Z→12:11:55.851Z` measured:

- `CmaTotal=131,072 KiB`; `CmaFree=608 KiB` in both snapshots; the arithmetic difference `130,464 KiB` is *non-free CMA capacity*, **not** a pinned-GPU or leak measurement.
- `MemAvailable=662,652→663,192 KiB`, `Cached=579,288 KiB` unchanged, `SwapFree=2,065,116 KiB` unchanged; `nr_free_cma=152` pages both times.
- CMA allocation counters stayed `success=8/fail=0`; swap, major-fault, compaction and migration counters had no delta. `pgfault_delta=169,239` was observed; no major-fault delta.
- Complete CMA histogram: free order-7–10 blocks were zero. The free-CMA histogram totals 149 pages while `nr_free_cma` and `CmaFree` report 152 pages (3-page discrepancy from separate, non-atomic proc reads); do not force equality. The order histogram had free CMA pages only in orders 0–6.
- DMA-zone `zoneinfo`: `pages_free=3,506`, `cma=32,768`, watermarks `min=2,015`, `low=2,262`, `high=2,509` pages. Pageblock counts were CMA 32, Movable 162, Reclaimable 14, Unmovable 48, HighAtomic/Isolate 0. These are pageblock-type counts, **not current allocated-page owners**.

This is a fresh low-CMA state, not recovery. No actual request failure was observed in the pair or filtered kernel log, but that does not prove that all possible allocations succeed or that an earlier failure did not occur.

## CMA/debugfs support and allocation-failure evidence

- `/proc/config.gz`: `CONFIG_CMA=y`, `CONFIG_DMA_CMA=y`, `CONFIG_CMA_DEBUGFS=not_set`, `CONFIG_DEBUG_FS=y`, `CONFIG_PAGE_OWNER=not_set`, `CONFIG_COMPACTION=y`.
- No debugfs or tracefs mount was present; `/sys/kernel/mm/cma` was absent; existing CMA, page-owner and Mali debug paths were therefore **unavailable**, not zero. No filesystem was mounted and no tracing or kernel setting was enabled.
- A source-filtered `dmesg` check found zero OOM, page-allocation-failure, CMA-failure or Mali-OOM matches. The same-boot `cma_alloc_fail` gauge remained zero during the measured pair. These observations establish no matching failure evidence in this sample window, not lifetime success.

## Read-only DMA-BUF ownership and processes

The current global `/sys/kernel/dmabuf/buffers` inventory had six entries, all `exporter=system`: inodes 1 and 6 at 16,384 bytes; inodes 3, 4, 5 and 7 at 3,686,400 bytes. The same six `(inode, exporter, size)` tuples and the same MainUI FD set were present in **all eight** saved samples covering the pre-hash pair, post-hash pair, idle pair and 11:32 recovery pair. Thus no change in the visible global DMA-BUF inventory or MainUI's exported-buffer FDs coincided with the historical CmaFree drop; private GPU allocations and movable-page occupancy are outside this inventory.

A bounded process-FD scan at `12:14:03Z` mapped all six visible DMA-BUFs:

- MainUI `PID 2369/starttime 1079` owns inodes 1, 3, 4 and 5, and holds `/dev/dri/card0`, `/dev/dma_heap/system` and `/dev/mali0`.
- `/mnt/sdcard/mmcblk1p1/spruce/bin64/display_text.elf`, `PID 31142/starttime 1800687`, owns inodes 6 and 7 and also holds `/dev/dri/card0`, `/dev/dma_heap/system` and `/dev/mali0`. Its observed parent chain is `battery_level_w` shells → `runtime.sh` → `updater`; treat it as platform-managed, not a user game.
- No `reserved` exporter or `/dev/dma_heap/reserved` FD was observed among these owners. The process census was **partial** due one unreadable `/proc` identity during scanning; it had no FD-scan errors or truncation, and every visible global DMA-BUF inode had an observed owner. Do not interpret this as proof that no other private or transient allocation exists.

K1-D classifies the generic `system` heap's direct `__alloc_pages` path as non-movable and not CMA-eligible through its Unmovable fallback. That narrows these exported buffers' allocator route, but does not classify the two processes' private Mali allocations. K1-C narrows only the native Kbase page-pool path; neither finding reveals all userspace driver routes.

## Why the historical change is not a leak finding

On the **same boot**, the 11:05 pre-hash pair was stable at `CmaFree=130,412 KiB`; after the read-only 1.832 GB ROMFS hash, the 11:09 pair was `532→576 KiB`, while `Cached` rose. The visible DMA-BUF inventory and MainUI FD set were unchanged across pre/post/idle/recovery samples. This excludes a change in those observed buffers as the measured explanation, but it does not show where the non-free CMA pages went. The large read and cache rise are temporal correlates only. The free CMA histogram, current process FDs and exporter labels do not expose **movable page occupants**, pinned non-DMA-BUF pages, or allocation lifetimes. No page-owner/debugfs source is enabled to distinguish them.

## Process lifecycle and runtime decision

No safe, reversible user-process lifecycle that is supported by evidence was identified. The only visible Mali/display/DMA-BUF owners are platform-managed MainUI and `display_text.elf`; both have system-heap buffers, and stopping or killing either would violate the system-process safety boundary without evidence that it would restore CMA. No game process was present. **No process was stopped, no cache was reclaimed, no compaction/reboot/sysfs change was attempted, and no game was launched.**

`CmaFree=608 KiB` with zero order-7+ CMA blocks remains the exact measured runtime blocker. `T2_STORAGE_MARGIN_MIB` remains unset; the candidate stays inert and build259 stays active. Do not attempt gameplay until a fresh complete D preflight establishes class-specific headroom and an explicitly reviewed positive reserve. The visible process lifecycle scan does not supply that reserve.

## Verification artifacts

- D snapshots/comparison, owner/debugfs probe output and hashes remain local-only under Hermes scratch; published JSON lists their SHA-256 values.
- The read-only owner scan's transient `/proc` identity error is explicitly retained as a limitation; it is not silently treated as a complete census.
