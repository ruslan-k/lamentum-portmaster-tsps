# K1 — exact TG5050 firmware-kernel match and read-only CMA pair

**Date:** 2026-10-23. **Repo branch:** `main`, based on `31f5baae`. This is host-side firmware analysis plus fresh, read-only target snapshots; it is not a runtime or gameplay test.

## Firmware and kernel identity

The user-provided [SpruceOS repository](https://github.com/spruceUI/spruceOS) is pinned here to commit [`46d321b4d350c682c882f320f1187d1ef5d25a06`](https://github.com/spruceUI/spruceOS/tree/46d321b4d350c682c882f320f1187d1ef5d25a06). Its `SmartProS.cfg` selects `trimui_tg5050.awimg` and target firmware `1.0.1`; the updater downloads the matching `.7z` from `spruceUI/spruceSource`.

Downloaded the release asset to host scratch only. GitHub's release digest and the complete downloaded archive hash both equal `e825878608d0c979ba9cfcde71c104f0b334c9979774e783f5174f9356360f8a` (278,741,768 bytes). The IMAGEWTY image bounds and all 36 member ranges were validated before extracting only `vmlinux.fex`; its bzip2 stream and nested one-member tar were checked before extracting the 330,641,200-byte AArch64 ELF. Proprietary image/kernel bytes remain outside the repository.

The extracted unstripped ELF has Build ID `175a7f4d4731ebfbbdeb7695329115202f8b813a` and SHA-256 `806182f8823b0db340f3f9beccf303e39571deb20b99386ee6a76442b8761b19`. Its Linux 5.15.147 build banner/compiler matches live `/proc/version`; live `/etc/version` is also `1.0.1`. Four live `/proc/kallsyms` functions share the same `0x80000` relocation from the firmware ELF, and the two relevant kallsyms stack extents match the firmware ELF's next-symbol spans. This establishes an **exact firmware-build match for the analyzed kernel layout**, not a whole-live-image cryptographic hash. DWARF points to `.../drivers/dma-buf/heaps/system_heap.c`; the original vendor source tree itself was not found in the inspected Spruce source repository.

## Allocation-warning result

The exact firmware binary has the `system_heap_allocate` candidate-order table `{8,4,0}`. The warning return site at `system_heap_allocate+0x120` is the instruction after `__alloc_pages`; a null result branches back to the candidate loop. Thus an order-4 warning can be an intermediate failure followed by an order-0 attempt. Exhaustion can still return `-ENOMEM`; the historical warnings do not carry the enclosing DMA-heap request result. The exact *warning semantics* are resolved; historical request completion and CMA backing are not.

## Fresh CMA evidence

The read-only collector was streamed to the handheld over fresh, non-multiplexed SSH connections and executed from stdin; it wrote nothing to the device. Two complete snapshots from the same boot were 22.178 seconds apart:

- `CmaTotal=131,072 KiB`; `CmaFree=15,456 KiB` in both reads; `nr_free_cma=3,864` pages in both.
- `MemAvailable=676,432 → 676,316 KiB` (−116 KiB); `SwapFree=2,033,604 KiB` unchanged. `cma_alloc_success/fail=36/0` unchanged; no new page migration, compaction, major-fault, or swap counters during the pair; `pgfault` increased by 15,780.
- `/proc/pagetypeinfo` showed `MIGRATE_CMA` free-block counts by order 0–10: `571,71,9,3,1,0,0,0,0,0,3`. The derived 3,861 free pages differ by 3 pages (12 KiB) from the separately read `nr_free_cma`; proc files are sequential, so the mismatch is preserved rather than forced equal.
- `CONFIG_CMA_DEBUGFS` and `CONFIG_PAGE_OWNER` are unset; tracepoint directories are unavailable. `/sys/kernel/dmabuf/buffers` exposes four `system` exporter entries (16 KiB and three 3.5 MiB). Their inode IDs match MainUI's corresponding DMA-BUF FDs, but this does **not** prove CMA backing or physical Mali residency.
- MainUI PID/starttime `28250/4031805`, executable inode identity, and DMA-related FD set were stable. The complete process scan matched executables by the installed runtime's exact device/inode identity and found zero running instances; the build259 file hash remained unchanged.

After tightening the reducer to reject missing scalar deltas/histograms, counter resets, non-increasing sample times, or MainUI/runtime-identity drift, a second same-boot pair was captured at `02:35:48–02:36:10Z`. The comparator returned pair status `ok`: `CmaFree` and `nr_free_cma` were unchanged, `MemAvailable` rose by 896 KiB, `SwapFree` and CMA allocation counters were unchanged, the order histogram and MainUI DMA-FD set were stable, and the exact runtime inode scan still found no running instance. The installed build259 hash matched in both reads.

## Gate and next step

Host validation after the collector/comparator hardening: `PYTHONPATH=tools python3 -m unittest discover -s tools -p 'test_*.py'` — **344 tests passed**; `py_compile` for the five K1 Python files and `git diff --check` passed.

Read-only device readback confirms build259 remains installed at SHA-256 `d72e2f69afa16dd5b846950f3fba80bc9926edcab9b2d45c57ed23faa14b9066`. Build260 was **not** installed or launched. The low idle CMA state remains a hard NO-GO; the snapshots do not attribute occupancy or establish a safe margin. Continue host-only A1 admission-policy replay and CMA-accounting work. Do not relax the guard or enter New Game until the independent device go/no-go is reopened.

Machine-readable compact receipt: [`summary.json`](summary.json). Full firmware, extracted image/kernel, raw disassembly, and raw proc captures remain host-local; no raw dumps or proprietary blobs are committed.
