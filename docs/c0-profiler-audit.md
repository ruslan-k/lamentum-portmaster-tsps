# C0 follow-up: withdraw the C1 cost verdict, validate the collector before the next game arm

Roadmap read: `origin/main` **46ea9a8**, including the full current §29 (the execution queue
remains §29, not the older priorities). This is an implementation/measurement correction,
not a claim of gameplay or 30 FPS. The next combined game arm must still satisfy G0 storage
identity, T1 run/phase identity and C0 overhead/coverage requirements.

## 1. Background completion receipts, without hiding the failure

- `swap-priority-01`: harness **8**, consistent with the saved `kernel_oom_sigkill`
  classification/victim receipt for the observed process generation. That is a failed arm,
  not a successful optimization. The original swap priority was restored. A single arm
  does not establish why zram priority changed the outcome.
- `C1-svc-cost-01`: harness **0**, runtime **TIME_LIMIT**, 443 presentation log records,
  cleanup errors empty. This validates bounded termination and cleanup, NOT the profiler's
  coverage or playability. Its old cost verdict is withdrawn below.
- `C2-bc-decode-01`: the host collection was interrupted. The retained `cost-final.json`
  was actually a preliminary 319-present snapshot with no STOP. There is no saved final
  harness receipt for that arm. The device has since rebooted; today's preserved `latest.log`
  must not be attached to that old process generation. Missing BC rows do NOT mean zero BC work.

## 2. Why the previous C1 conclusion was invalid

The original `native/lc2_cost.h` kept its counters exclusively in TLS and printed only when
that thread reached **4096 total instrumented calls**. It had no stop-time flush despite its
comment promising one. Thus a worker with one, ten or hundreds of mutex/BC calls could
finish without publishing any of them. Retired TLS was lost entirely.

The ad-hoc `by[class] = last_row` reduction then discarded TID and overwrote other threads
and cumulative snapshots. Reported 1/0 mutex counts were last-emitted/absent rows, not global
counts. The derived **1.98 ms/present**, **0.293% core** and "AudioOut/mutex bridge is not the
bottleneck; C1 closed" conclusions are NOT accepted performance measurements.

Additional problems:

- Skipping an inner timed scope does not make its enclosing scope exclusive: the parent
  still contains the child's time. The old `scope=caller-thread-exclusive` label was false
  for nested calls.
- CPU was read before wall on entry, then before wall on exit. Different read windows and
  probe overhead alone can produce `wall < CPU`; this does not prove a coarse monotonic clock.
  Replacing wall with CPU manufactured the reported wall total. The new test reports
  **1 ns advertised resolution for both clocks on this TSPS**. That does not qualify their
  accuracy or call overhead, but the old coarse-clock explanation is unsupported.
- Timing only `aout_dispatch` excludes outer IPC parsing, the earlier AudioOut operation
  wait, trap transport, kernel-mutex acquisition and other audio worker activity. Even a
  correct handler duration would not be the entire AudioOut/SVC bridge cost.
- The older 5506/5389 arbitration counts were parsed from **SVC log records**, not from
  round-robin PC slots (`tools/audit_audio_endpoint.py`, `summarize_arbitration_log`). Only
  the PC-sample occupancy fractions lack CPU-time meaning. The earlier attempt to reclassify
  the logged call histogram as sample occupancy is also withdrawn.
- The ~881 ms/s sample identified a hot **TID**, not a symbolized main-thread function.
  It did not establish that BC decode, reclaim, AudioOut, or Mali owned the remaining time.

Preserved legacy numbers are historical, incomplete counters. Do not retrofit missing
threads/tails by adding plausible values or extrapolating to 30 FPS.

## 3. What changed in the instrument (diagnostic only)

`native/lc2_cost.h` V2 and the existing call sites now provide:

1. A fixed **128-slot registry**, with immutable **TID + `/proc/self/task/TID/stat` starttime**.
   Registration is once per thread, before that thread's first timing interval; no heap
   allocation or profiler I/O occurs inside a timed handler. Registry fields use atomic accesses.
2. Counters for **entered, completed, valid and invalid** calls, CPU inclusive/exclusive,
   wall inclusive/exclusive, maxima and raw `wall_lt_cpu` observations. In-flight calls,
   identity failures, registry exhaustion and inconsistent snapshots are explicit.
3. Independent `CLOCK_THREAD_CPUTIME_ID` CPU and `CLOCK_MONOTONIC_RAW` wall timestamps.
   Zero is a valid timestamp. Clock failure invalidates the interval and does not become a
   zero-cost call. `errno` is preserved. Wall values are never clamped to CPU.
4. A bounded nesting stack. A parent subtracts each direct child's **inclusive** interval
   to obtain its exclusive interval. Nesting overflow invalidates affected intervals and
   flags coverage; it never changes handler execution or invents a successful guest call.
5. Explicit `lc2_cost_report_fd` before `stop()` calls `_exit`, using bounded integer
   formatting and `write`, not stdio, allocation, environment parsing or a new mutex in
   the stop path. Each row retains TID/starttime and includes sub-4096 tails, including
   already terminated workers. A bounded sequence snapshot reports inconsistency instead
   of spinning forever. SIGKILL cannot flush; missing final reports remain missing evidence.
6. The same narrow wait/release/AudioOut hooks, plus the previously interrupted BC wrapper.
   No texture format, image, shader catalogue, quota, swap order or allocation admission
   was changed. These hooks are still NOT a complete trap/scheduler/whole-frame profiler.

`tools/cost_report.py` preserves `(report,TID,starttime,class)`, rejects duplicates and
ambiguous reused report IDs, uses only the latest complete cumulative snapshot (does not
add repeated totals), retains raw per-thread wall values and never presents their sum as
elapsed time. It returns `no_complete_report`, not zero cost, for old V1 or absent output.
It explicitly reports `profiler_overhead_qualified=false`.

## 4. Host regression checks

The exact new header is extracted from the published adapter patch for testing; tests no
longer require the private adapter checkout. Fixtures cover:

- four short-lived workers, including one-call tails, followed by `_exit`;
- three-level deterministic nesting (subtract direct-child inclusive cost, not child exclusive);
- raw wall below CPU, a valid zero timestamp, clock failure and `errno` preservation;
- disabled/unset/0/2 switch, with no clock reads and no profile output;
- active calls at snapshot and bounded registry exhaustion, both incomplete rather than zero;
- thread `comm` containing spaces/parentheses and field-22 starttime parsing;
- repeated cumulative snapshots, truncated final snapshots and reused generation IDs.

Full suite: **126 tests PASS** with ResourceWarning promoted to error. `git diff --check`
passes. This is functional collector qualification, not observation-overhead qualification.

## 5. Rebuild and real TSPS component test

The pinned cross-build verified **435/435 baseline files**, applied the overlay and built
AArch64 successfully. The recovered baseline was not edited.

- build225 game ELF: `eee3e5ce041ff6be8dd1dbb1d8820f3c296e4d1a497909f4360d5361040124d5`
- self-authored fixture ELF: `1b3091ad20762fdb375d92822741380abdbe2bf5d5c5b0c5320b4565da1f7807`
- The fixture uses the exact header from the rebuilt source. Build/source/catalogue hashes:
  [`evidence/C0-profiler-validation/build.json`](../evidence/C0-profiler-validation/build.json).

The curated publication tree was then exported without the private adapter checkout and
retested: **126/126 host tests**, **435/435** baseline checks and the full AArch64 rebuild
passed again. Its fixture ELF is byte-identical to the device-tested fixture, and its
header is byte-identical to the tested header. The separate game ELF hash differs and is
reported rather than called identical; it was not deployed. See
[`publication-verification.json`](../evidence/C0-profiler-validation/publication-verification.json).
Full game/kernel logs and pre-existing unrelated working edits remain owner-local. Earlier
unpublished commits are retained in a local-only backup; publication consolidates their
qualified evidence and corrected source without exposing the raw kernel dumps.

**Only the self-authored CPU-only fixture was deployed and run.** It contains no game data,
no PCM, no GL/display/audio calls. It ran through Spruce principal/standard_launch with
MainUI absent; native alarm bounds it to eight seconds. The unchanged game was NOT launched.
The fixture creates four workers, each performing three synthetic nested work/wait intervals
and one short release interval. Workers join before the process reports and uses `_exit`.

Actual device result, ON and OFF separately:

| Check | Observed result |
|---|---|
| ON / OFF process exit | 0 / 0 |
| ON surviving retired thread generations | 4 |
| ON class rows | 12 |
| completed synthetic wait / BC / release intervals | 12 / 12 / 4 |
| invalid / missing coverage | none; `coverage_complete=true` |
| OFF profile rows | none |
| advertised CPU / MONOTONIC_RAW resolution | 1 ns / 1 ns |
| installed game ELF / game launcher hashes | unchanged |
| remaining fixture/game processes | none |
| CPU online mask before/after | **4-7 / 4-7** (do not impose the previous boot's 0-7) |
| Spruce restore | one MainUI, original supervisor identities, real nonblank KMS menu |

The synthetic class names identify the instrumented buckets; they are NOT actual game
SVC/BC measurements. No BC performance, real world frame, input/audio or save acceptance is
inferred. The fresh game ELF is built but NOT deployed. The installed ELF remains build223
`86649c51854e4017fdbaddab16b7c53d327fb6a138c45c1106275c67a1727815`.

## 6. Other claims corrected while auditing

- Anonymous VMAs do not identify a semantic owner: they can include guest data, decoded
  textures, allocator staging, driver heaps or private-COW pages. A process's VmSwap is not
  a measurement of Mali physical texture storage. Therefore "99.66% anonymous means textures
  cannot help / Mali is not the bottleneck" is withdrawn. G0 id295 remains a distinct hazard.
- VMA boundaries can merge/split; a moving boundary alone does not prove one downward-growing
  arena or its allocator/immutability. Mapping ranges are per run.
- Swap priority plus process VmSwap cannot identify which physical device stores that
  process's pages. The names SDCARD/UDISK alone do not establish distinct physical media.
- One priority-100 arm with OOM at 115 presents is a negative result, NOT a matched-phase
  causal proof that RAM-first always fails or file-first is necessary. No follow-up policy
  experiment was authorized or run here.

## 7. What is still open / next execution

**C0 remains OPEN.** It still needs a UUID/phase-bound game run, all relevant trap/IPC/wait
boundaries, return/queue outcomes, same-run native maps and an equivalent Loading OFF/ON
observation-overhead comparison. Do not close it based on this fixture.

Follow §29's critical path: G0 checked multi-mip storage layout/transactional accounting and
id295 descriptor/GL lifetime receipt; G1 independent GLES compressed-storage/physical-memory
fixture; T1 run generation plus a single semantic New Game navigator; then one guarded
combined New Game arm. No further menu-only timeout run, unsafe cap increase, guessed owner,
texture quality reduction, swap experiment or renderer bypass was used for this correction.

During active work, re-fetch and read roadmap changes every **30–60 minutes** and before a
new experimental phase. Record the reviewed source revision and evidence limits in the repo;
this is an active-work practice, not a background notification/cron promise.
