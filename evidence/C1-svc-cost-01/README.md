# C1-svc-cost-01 — incomplete legacy counters; performance verdict withdrawn

> **HISTORICAL REPORT — COST VERDICT WITHDRAWN.** The original performance conclusions
> below are superseded by [the C0 audit](../../docs/c0-profiler-audit.md). TLS publication
> omitted short-lived/sub-4096-call threads and tails; the reducer discarded TIDs. These
> are incomplete last-emitted counters, not complete cost/call totals. Absent rows do not
> establish zero calls. The run's TIME_LIMIT and clean cleanup remain valid. C0 stays open.

First arm of the C1 measurement the roadmap asks for. Build `cea1c902…80ed`
(`build-222`, overlay commit `87d6e6f`), previous binary kept as
`lamentum-nextos.before-221` (`602d05be…3391`), both hashes re-read from the device in `deploy.txt`.

Instrumentation: `native/lc2_cost.h`, opt-in `LC2_SVC_COST=1`, hooked at the svc dispatch
(`svc 0x1a` -> `mutex_wait`, `svc 0x1b` -> `mutex_release`) and around the `aout_dispatch`
call for `EP_AUDOUT` command 7/8. Per call it records **thread CPU time** and **wall time**,
aggregates count/total/mean/max per class per thread, and prints at most one bounded summary
per 4096 calls. Nesting is excluded (a class entered inside another measured region is
skipped), so overlapping regions cannot be summed into a fake total. No allocation, no I/O and
no behaviour change on the measured path.

## Result (whole arm: 443 frames, `STOP status=TIME_LIMIT`, cleanup clean)

| class | calls | CPU total | wall total | CPU mean/call | calls/frame | CPU ms/frame |
|---|---|---|---|---|---|---|
| `svc0x1a-wait` | **1** | 0.004 ms | 0.004 ms | 4.0 µs | 0.00 | 0.000 |
| `svc0x1b-release` | **0** | — | — | — | — | — |
| `audout-cmd7` | 10 734 | 279.4 ms | 309.2 ms | 26.0 µs | 24.2 | 0.631 |
| `audout-cmd8` | 30 225 | 598.8 ms | 835.9 ms | 19.8 µs | 68.2 | 1.352 |

Totals: **878.3 ms CPU / 1 145.2 ms wall over 300 s = 1.98 ms CPU per presented frame =
0.293 % of one core.**

## What this refutes

- **The mutex bridge is not the cost.** `svc 0x1a` is called once in the whole arm and
  `svc 0x1b` never, so the earlier "5 506 + 5 389 SVC calls, 84.1 %" figure was a
  round-robin sampler's occupancy of *sample slots*, not calls and not CPU share. This arm
  counts real calls on the real path.
- **AudioOut is not the bottleneck either.** 92 calls and 1.98 ms of CPU per frame — with the
  main thread measured at ~881 ms CPU per wall second in the same loading phase, AudioOut is
  ~0.3 % of that. Even at 30 fps it would be ~6 % of one core, not a blocker.

So the 1.6 fps loading path spends its CPU somewhere else: the BC decode/copy and the page
reclaim path (`docs/swap-attribution.md`), not the IPC bridge the roadmap suspected.

## Limits — read before quoting

- Stage: menu/loading, 1.48 fps; **not gameplay**, no FPS claim.
- `wall-floor-hits` is reported per summary and is *large* on this kernel (15 195 by the end):
  `CLOCK_MONOTONIC` here is coarser than `CLOCK_THREAD_CPUTIME_ID`, so a short call can read
  as more CPU than wall. The code applies the thread-CPU value as a wall floor and counts each
  such case instead of hiding it — so the wall column is a floor, and the CPU column is the
  trustworthy one at these call lengths.
- Numbers are per-thread sums on the AudioOut caller thread; they are not a share of total
  process CPU and must not be added to the sampler's per-thread figures.
- The `audout-cmd8` pressure (68 calls/frame) is a property of `AW_RELEASE=0` polling in this
  env; a different audio mode would change the call counts, not the per-call cost.

Artifacts: `preflight.json`, `env.json` (includes `LC2_SVC_COST=1`), `deploy.txt`,
`harness.log`, `harness-exit.json`, `cost-final.json` (parsed totals), `before.json`,
`cleanup.json`.
