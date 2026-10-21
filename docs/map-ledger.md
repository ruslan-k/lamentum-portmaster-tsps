# Who reserves the guest's memory: map receipts (owner §48 / M1)

Build236 `5a1c04148c65` adds `LC2_MAP_LEDGER=1`: bounded receipts for the three
mapping classes the adapter serves — main heap (`svc 1`), `alias_physical`
(`svc 0x2c/0x2d`, Unity VammManager) and blob/file mappings. Sizes are the requested
ranges; commitment stays `rss=unknown`. No behaviour change.

## Arm 1 (`map-ledger-01`) — tooling defect, recorded as such

The 48-line bound was consumed by **blob** mappings before the first
`alias_physical` line, so the arm reported `heap=0/0 alias=0/0` and only blob data.
Fixed by a per-class quota (12 blob lines, totals still counted) plus a
`LC2_MAP_SUMMARY` line. The arm itself was otherwise clean
(`T2_MEMORY_FLOOR`, verified identity, zero cleanup errors).

## Arm 2 (`map-ledger-02`) — data, and an OOM

**This arm ended in a kernel OOM kill** (`termination.kind=kernel_oom_sigkill`,
`HARNESS_RC=8`, no STOP taxonomy): an honest failed arm, not a result of the STOP path.

| class | recorded | count | notes |
|---|---|---|---|
| blob / file data | **73,359,360 B = 69.95 MiB** | 13 | largest single 30,855,168 B (29.4 MiB); totals complete |
| `alias_physical` | **≥130,654,208 B = 124.6 MiB** | ≥36 | still growing when the line window closed, so a **floor, not a total** |
| main heap (`svc 1`) | **0** | 0 | this title never reserves through that path |

`alias_physical` includes one **67,108,864 B (64 MiB)** and one **33,558,528 B (32 MiB)**
mapping, then a long tail of 1 MiB / 256 KiB / 4–8 KiB pieces — i.e. the guest builds
its arenas out of many small physical aliases with two big pieces on top.

## What this establishes, and what it does not

- **Established:** the −433.8 MiB step between `gl-init` and the first present is *not*
  a main-heap reservation; `svc 1` is unused here. Two owners are now measured:
  ~70 MiB of file/blob mapping and **at least** 124.6 MiB of `alias_physical`.
- **Not established:** the remainder (~240 MiB at the observed floor) has no receipt
  yet, because the alias total is truncated by the line window and because blob
  *unmappings* are not receipted at all, so allocate/free balance is one-sided.
- **Not claimed:** that `alias_physical` "leaks". Its unmaps (`svc 0x2d`) are not
  instrumented yet, so only the allocation side is visible.

## Next

1. Emit a periodic `LC2_MAP_SUMMARY` (e.g. every 64th event and at every stop) so
   class totals survive the bounded line window; add unmap receipts for both classes.
2. Re-run once for a clean (non-OOM) alias total, then compare classes against the
   measured 568.7 → 134.9 MiB step to see what remains unattributed.
3. Only after that decide whether the alias arenas are the thing to shrink — the 720p
   experiment's 17.58 MiB ceiling stays unchanged and remains the smaller lever.
