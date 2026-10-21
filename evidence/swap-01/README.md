# swap-01 — read-only per-mapping swap attribution

> **HISTORICAL INTERPRETATION CORRECTED.** [Audit](../../docs/c0-profiler-audit.md): this
> payload read `smaps_rollup Swap`, NOT `status VmSwap`; the two reads are not atomic.
> "Anonymous" totals inferred by pathname absence are not semantic allocation ownership.
> They do not rule out texture/staging/driver memory or the id295 GPU wall. The old rate
> used assumed polling spacing; it is not a qualified loading rate. The fail-closed
> PHYSICAL_MEMORY_CONFLICT and clean cleanup remain valid; no gameplay was established.

Purpose: name the owner of the ~766 MB `VmSwap` seen inside the game process
(`docs/swap-attribution.md`). Build `602d05be6f24fcdbdbebb73123c11d2ce0dc1dede70486d0d77c1f4025063391`
(the build-220 audit binary already installed from `evidence/G1-large-bc-01`; no new deploy).

Method: `tools/swap_attribution.py` over SSH, 12 samples at 12 s, bound to the exact owner
generation (`owner.json`: boot `aedf014d-…`, pid 1815, starttime 6577541) using `samefile` on
`/proc/PID/exe`. Read-only: `smaps`, `smaps_rollup`, `status`, `stat`.

## Result

| quantity | value |
|---|---|
| process `VmSwap` (last sample) | 784 704 kB = 766.3 MiB |
| sum of per-mapping `Swap` | 784 692 kB |
| unattributed gap | 12 kB (0.002 %) |
| anonymous | 782 004 kB (99.66 %) |
| file-backed | 2 688 kB (0.34 %) |
| dominant mapping | `366580000-38e216000 rw-p` anon, 637 MiB, **432 284 kB swapped (55.1 % of all swap)** |
| second / third | 74 MiB map 86.6 % swapped / 64 MiB map 84.3 % swapped |
| growth | 0 -> 766 MiB in 96 s = **9.0 MiB/s** |

Series (kB): 8 884, 18 352, 79 452, 168 456, 361 284, 529 100, 631 540, 784 704.

## What it rules out

The BC file-backing is not the swapper: 2.6 MiB file-backed against 763.7 MiB anonymous. Any
"keep textures resident / change BC format" argument has to explain this split first.

## Honest limits

- The arm stopped at `STOP status=PHYSICAL_MEMORY_CONFLICT` at frame 162 (fail-closed in
  `loader.c`, the same class as load-probe-01), so this is a loading-stage profile, not a
  gameplay profile.
- Cleanup was clean (`cleanup.json`: no game process, `MainUI=1`, CPU mask `0-7` restored,
  `errors: []`).
- These samples were produced by the first payload revision, which took the process total from
  `smaps_rollup Swap` and computed the anonymous/file split by path presence; the committed
  payload now also reads `status VmSwap`, reports `coverage_percent` and refuses to turn a
  stray rollup header into a counter (4 tests in `tools/test_swap_attribution.py`).
- Mapping ranges differ per run and must not be used as cross-boot identifiers.

Artifacts: `preflight.json`, `env.json`, `owner.json`, `swap.jsonl`, `harness.log`,
`harness-exit.json`, `before.json`, `cleanup.json`, `kernel-before.json`, `kernel-after.json`,
`latest.log` (owner-local full log).
