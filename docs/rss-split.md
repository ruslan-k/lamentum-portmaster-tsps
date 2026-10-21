# The pre-first-frame step is our own RSS (+520 MiB), not page cache

> ATTRIBUTION RETRACTED: see [same-run reconciliation](smaps-owner-reconciliation.md). System AnonPages cannot be subtracted from process VmRSS to derive a file-backed owner. Observed counters remain valid; the image-page ownership claim is not.

No rebuild was needed: `lc2_menu_ledger` already records `Cached`, `AnonPages`,
`Shmem`, `VmRSS` and `VmSwap` per record. The data settles the §54 caveat.

## gl-init → first-present, two independent arms

| quantity | `map-ledger-03` | `menu-early-01` |
|---|---|---|
| `MemAvailable` | **−471.4 MiB** | **−433.8 MiB** |
| `Cached` | **−55.6 MiB** | **−52.6 MiB** |
| `AnonPages` | **+240.4 MiB** | **+241.3 MiB** |
| `Shmem` | +0.0 MiB | +0.0 MiB |
| **own `VmRSS`** | **+521.0 MiB** | **+519.2 MiB** |
| `VmSwap` | +0.0 MiB | +0.0 MiB |
| charged textures | +107.1 MiB | +107.1 MiB |

## What this means

1. **Page cache does not explain the step — it *fell* by ~55 MiB.** My §54 warning that
   `MemAvailable` might be inflated by cache was correct as a caution, but the direction
   is the opposite: cache was reclaimed *into* the process.
2. **The owner is our own process: RSS grows ~520 MiB before the first frame.**
   System-wide anonymous only grows ~241 MiB, so roughly **half of that RSS is
   file-backed** — the 1.74 GB image read into the address space. The adapter's own
   mapping receipts (69.95 MiB of blob mappings) cover only adapter-served mappings,
   not the runtime's own file I/O.
3. **The end state is the whole story of the memory crisis**: at the stop, `VmRSS`
   731.7 MiB + `VmSwap` 415.1 MiB ≈ **1.12 GiB footprint on a 963 MiB board**. The floor
   stop is arithmetic, not a tuning artifact.
4. Charged texture storage (+107.1 MiB) is reproduced exactly across both arms, so the
   texture accounting is stable even though it is not the dominant term.

## Correction to the standing narrative

"Guest reserves N MiB at startup" is now measured as: **+241 MiB anonymous** plus
**~280 MiB file-backed pages** inside our own RSS. Neither is a single allocation the
adapter can decline; the file-backed half is the price of reading the game image, and
the anonymous half is guest heap. Any lever has to be judged against 520 MiB, which is
~30× the 17.58 MiB that the 720p experiment could return.

## Next

`/proc/self/smaps_rollup` per ledger record (`RssAnon`, `RssFile`, `RssShmem`) turns this
aggregate split into a per-record series, so the file-backed half can be watched frame by
frame and compared with the runtime's read path instead of inferred from two totals.
