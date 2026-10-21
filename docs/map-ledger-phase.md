# `alias_physical` belongs to a later phase, and MemAvailable is not "game memory"

Build237 `ee28f264afe6` adds unmap receipts (`svc 0x2d`) and a periodic
`LC2_MAP_SUMMARY` every 64 events, so class totals survive the bounded line window.
Arm `map-ledger-03`: clean `T2_MEMORY_FLOOR` stop, verified identity, zero cleanup
errors.

## Measured

| event | frames | available | CMA free | charged textures |
|---|---|---|---|---|
| `gl-init` | 0 | **599.9 MiB** | 0.01 MiB | 0 |
| `first-present` | 1 | **128.4 MiB** | 20.6 MiB | 107.1 MiB |
| stop (`T2_MEMORY_FLOOR`) | 42 | **31.4 MiB** | 5.5 MiB | 157.3 MiB |

Mapping receipts in this arm: **13 blob/file events, 73,359,360 B = 69.95 MiB**, then
**zero `alias_physical` events** before the floor stopped the run. The summary line
confirms it: `alias-bytes=0/0 alias-unmapped=0/0 events=13`.

## Three corrections to §53

1. **`alias_physical` is not part of the pre-first-frame step.** It first appears only
   in the longer (OOM) arm, i.e. after the menu's floor-limited window — during
   decoding/loading, not during the menu. My §53 phrasing ("≥124.6 MiB in the menu
   window") described an arm that had already run past the menu's memory limit.
2. **The `svc 1` main-heap path stays unused** (0 calls in every arm), so neither of the
   two structured paths explains the step between `gl-init` and `first-present`.
3. **`MemAvailable` is contaminated.** The −471.5 MiB step measured by `available` is
   not "memory the game owns": the runtime reads a 1.74 GB image and fills page cache
   in exactly that window, and page cache is reclaimable. The only honest owners are
   the receipts above (69.95 MiB of file mappings) plus whatever anon/shmem grows to,
   and `VmData` (1,022,876 kB at the end) is **virtual**, not resident. Any claim of the
   form "the guest reserves N MiB" needs anon+shmem numbers, not `MemAvailable`.

## What the receipt tooling now guarantees

- Class totals are printed even when the 48-line bound is exhausted (`why=line-bound`,
  and every 64 events), so a truncated window no longer hides the totals.
- Alias unmaps are receipted two-sidedly (`alias-unmapped`, `alias-live`). They were not
  exercised here because the alias phase was never reached in a floor-limited arm.

## Next

1. Re-run one arm at the same floor with the ledger on and record anon/shmem beside
   `MemAvailable`, which separates page cache from committed guest memory.
2. Reach the alias phase deliberately (a longer budget at the current floor) purely to
   exercise `alias-live`, and label it as a loading-phase measurement, not a menu one.
3. Keep the 720p ceiling (17.58 MiB) where it is: nothing measured so far makes it the
   dominant lever.
