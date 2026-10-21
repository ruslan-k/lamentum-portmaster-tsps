# G1 large-BC audit arm (build-220) — negative on the audit, positive on swap pressure

> **HISTORICAL INTERPRETATION CORRECTED.** See [the audit](../../docs/c0-profiler-audit.md).
> No id295 receipt was observed on this unqualified menu/loading arm. The missing large
> reservation neither demotes its later GPU hazard nor identifies the bottleneck. Anonymous
> swap is not semantic texture/guest/GPU ownership. Rate and phase claims below are not an
> accepted game benchmark, and the hot sampled TID was not proved to be the main thread.

Build: `602d05be6f24fcdbdbebb73123c11d2ce0dc1dede70486d0d77c1f4025063391`
(`runtime/lamentum-adapter.patch` overlay commit `5ec6dbc`, 106 tests PASS).
Previous binary kept on device as `lamentum-nextos.before-220`
(`b8407822b205b0012401ed327a82f9ae94e31344a0bfc1d77ccdc1f7b798df4a`), see `deploy.txt`.

## What the arm was for

`docs/gpu-ledger.md` §26.3 records an 8192x8192 first-use BC reservation as a separately
proven OOM hazard. The adapter could not say *which* descriptor that reservation belongs to,
so this arm added one bounded, opt-in diagnostic (`LC2_LARGE_BC_AUDIT=1`) that prints at most
four ≥128 MiB reservation attempts, before the texture budget check, with the owner/view
identity, builder fields, pool identity, mip chain and per-level decoded bytes. It reads
existing host metadata only: no guest page restore, no GPU allocation, no format change, no
budget change, and it marks `storage-generation=untracked`, `source-hash=not-read`,
`immutable=unproven` so it cannot be mistaken for a residency claim.

## Result: the audit did not fire

On-device log for the full 600 s arm: **0** `LC2_BC_RESERVE_AUDIT` lines, **0**
`LC2_BC_AUDIT_LEVEL` lines, and no reservation above the threshold — the largest first-use
reserve in the run was:

    LC2_BC_GPU_RESERVE id=105 bytes=8294400 materialization=first-use

572 textures materialised, 448 BC-deferred, 12 budget charges, plateau
`T2_TEXTURE_BUDGET ... live-MiB=114 count=128 budget-MiB=300`.

So on this path the 8192x8192 reservation is **not reached**: the hazard stays documented but
is not on the menu/loading path this arm exercised. The gate itself is verified: the same
binary charged 572 textures without emitting a single audit line, i.e. the ≥128 MiB filter
suppresses small reserves (regression test `tools/test_large_bc_audit.py` compiles the real
added C block and asserts exactly that, plus the opt-in switch and the mip metadata).

## What the arm did measure (read-only samples, 63 x 8 s)

`perf_sample`-style sampling bound to the exact owner `pid=31371 starttime=6503852`:

| quantity | value |
|---|---|
| window | 539.6 s, frames 76 -> 944 |
| presented frames/s | **1.61** |
| process CPU | mean **158.4 %** (max 206.6 %) |
| busiest thread | `31379` mean **881 ms CPU per wall second** |
| second thread | `31422` mean 182 ms/s |
| RSS | 586 MB -> peak **712 MB** |
| swap (VmSwap of the game) | 46 MB -> peak **913.5 MB**, growing **8.41 MB/s** |
| samples in `state=D` | 3/62, wchan `wait_on_page_bit_common` |
| major faults | ~98/s |

The game is not GPU-bound at 1.6 fps: it is CPU/IO bound while the kernel swaps out ~913 MB
of it. `SwapFree` on the box fell from 1.98 GB to ~1.06 GB during the arm and recovered only
after exit. This is the concrete mechanism behind the earlier "MemAvailable 440 -> ~70 MiB,
VmSwap ~870 MiB" observation in `docs/gpu-ledger.md`, now measured on the live process rather
than inferred from /proc/meminfo.

## Limits of this arm — do not overclaim

- Stage is menu/loading, **not gameplay**; 1.61 fps here is not an in-game frame rate.
- Zero audit lines is a **negative** result for reachability, not evidence that the 8192x8192
  texture is harmless.
- The 913 MB swap peak says the working set does not fit, but it does not name the owner of
  the swapped pages. `smaps` attribution per mapping is the next read-only step.
- No texture policy, budget, resolution, compressed-format or partial-decode change was made,
  and none is justified by this arm alone.
- Menu navigation in this arm used agent evdev injection, recorded per press in
  `control-actions.jsonl`; it is not physical human input. The run ended on
  `STOP status=TIME_LIMIT`, cleanup errors empty, `MainUI=1`, CPU mask restored.

## Artifacts

`identity.json` (pre-run hashes + verified backups), `deploy.txt`, `env.json`,
`watchdog-owner.json` + `watchdog.json` (pidfd-bound owner watchdog: 600 s bound, natural exit
before it fired), `samples.jsonl` (63 read-only samples), `harness.log`, `harness-exit.json`,
`main-menu.png`, `newgame-selected.png`, `config-page.png`, `cfg-down-0.png`,
`control-actions.jsonl`.
