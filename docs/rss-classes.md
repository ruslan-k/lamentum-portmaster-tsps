# RSS by class: half guest heap, half image pages (build239)

> ATTRIBUTION RETRACTED: see [same-run reconciliation](smaps-owner-reconciliation.md). Status RssFile does not establish an ordinary image working set; low RssShmem does not rule out driver/DMA memory. Preserve the raw status values, not these causal conclusions. No drop A/B is justified by them.

`LC2_MENU_RSS` now prints `RssAnon`/`RssFile`/`RssShmem` from `/proc/self/status` on
every ledger record (`source=proc-self-status`), with `-1` for "unknown" so a missing key
can never read as zero. Arm `rss-split-02`: clean `T2_MEMORY_FLOOR` stop at frame 61,
verified identity, zero cleanup errors.

| record | frames | anon | file | shmem |
|---|---|---|---|---|
| `gl-init` | 0 | 122.3 MiB | 72.2 MiB | 0.11 MiB |
| `first-present` | 1 | **363.1 MiB** | **327.2 MiB** | 0.27 MiB |
| interval | 11 | 333.1 MiB | 350.9 MiB | 0.27 MiB |
| interval | 53 | **207.9 MiB** | **497.9 MiB** | 0.26 MiB |
| stop | 61 | 218.9 MiB | 492.2 MiB | 0.26 MiB |

`gl-init → first-present`: **anon +240.8 MiB, file +255.0 MiB** — reproducing the
aggregate +519.2/+521.0 MiB `VmRSS` from the previous section to within a few MiB, now
split by class.

## What the series shows

1. **The pre-first-frame step is half guest heap, half image pages** (241 / 255 MiB).
   Neither half is a single declinable allocation: the anonymous half is the guest's
   arenas, the file half is the 1.74 GB game image being read into the address space.
2. **Afterwards the halves move in opposite directions**: anon falls 363 → 219 MiB
   (pushed to swap, `VmSwap` ~415 MiB) while file rises to ~492 MiB. So the steady state
   is a small anonymous core plus a large resident image working set — the swap traffic
   is the anon half being churned out, not the image.
3. **`shmem` is negligible** (~0.26 MiB), which rules out shared-memory/dma-buf
   accounting as an explanation for the RSsS gap.

## Consequence for levers

- The **file half is the larger addressable term at steady state** (~492 MiB). It is
  reclaimable in principle, but nothing in the adapter currently advises the kernel to
  drop image pages after use, and no receipt shows whether the runtime re-reads them
  (which would cost swap-free memory *and* I/O). That is now a concrete, testable
  question rather than a guess.
- The 720p storage question stays at **17.58 MiB** nominal — one thirtieth of the file
  half alone.
- No claim is made here that dropping image pages would raise FPS; it would change
  memory pressure, which currently stops the run at frame ~61.

## Next

Instrument the image read path (how many file pages are touched, re-read, and whether a
drop hint exists) and measure a single reversible A/B of dropping already-consumed image
pages. Only if that keeps the frame loop alive past the floor does it become a
performance lever rather than a memory one.
