# T0 CPU clock and process-generation follow-up (§26.2.5)

## Scope

The current roadmap's T0 explicitly requires target-side SC_CLK_TCK, `/proc/PID/stat` parsing after
comm's closing parenthesis, TID/starttime keys and retained schedstat/faults. This change implements
that CPU-sampling portion. It is not a new game build, new gameplay run, C0 completion or FPS gain.

## Problems corrected

The former `tools/perf_sample.py` divided remote ticks by workstation SC_CLK_TCK and used host
wall-clock intervals. It split the whole proc stat line on whitespace (incorrect for thread names
containing spaces), paired threads by TID only, derived total CPU from the changing set of live
threads, retained only six thread deltas and turned SSH/JSON failures into `running=false`.
It also tried to estimate frame intervals from a 3 KB log tail not bound to a game/log generation.

## Implementation

- `tools/proc_metrics.py` contains the common proc-stat parser, target collector, request builder and
  CPU-delta function. The actual remote payload serializes these tested functions with
  `inspect.getsource`; there is no separate regex/parser mirror.
- Capture target `SC_CLK_TCK`, target monotonic timestamp, boot ID, PID/starttime and TID/starttime.
  Recheck process identity and boot after collection, and thread starttime around individual reads.
  Zombie/exited process states are not live samples.
- Initial discovery requires a unique runtime with the expected resolved executable path, not merely
  the shared/truncated `terminator2d-ne` comm. Once bound, pass expected boot/PID/starttime on every
  poll; PID reuse is rejected, not silently accepted as a continuation.
- Process CPU uses `/proc/PID/stat` total ticks rather than subtracting two different sets of live
  threads. Per-thread CPU uses matched TID/starttime only. Keep every matched thread in
  `thread_deltas`, plus a convenience top-six view, raw schedstat and fault counters.
- Formula: CPU percent = 100 * delta_process_ticks / (target_HZ * target_elapsed_seconds).
  Thread ms/s = 1000 * delta_thread_ticks / (target_HZ * target_elapsed_seconds).
- A missing sample, identity mismatch, negative CPU counter or nonpositive target interval does not
  produce a CPU delta. Transport errors stay explicit errors and break the baseline pair.
- `perf_sample.py` now imports without consuming argv or launching anything. Its CLI still starts
  the principal harness, which retains ownership of timeout/cleanup. The harness return status is
  propagated instead of silently becoming outer exit zero.
- Reuse the byte-framed incremental log collector rather than a tail. Mark retained frame serials
  as unverified log diagnostics and remove `guest_frame_ms`; these data are not gameplay FPS.

## Verification

`python3 -m unittest discover -s tools -p 'test_*.py'`: **87 tests PASS**.
Added tests cover target HZ=250 independent of host HZ, nested/spaced comm, process/reboot/clock
identity changes, reused TID, gaps, invalid deltas, all-thread retention, zombies, wrong-executable
comm rejection, actual generated payload execution, SSH failure and synthetic harness status=4.
The harness-boundary test uses explicitly mocked external services and does **not** contact a device.
The first new CPU test failed before the module existed, then passed; collector execution tests
likewise failed before the collector/request functions were added.

`python3 tools/perf_sample.py --help`: PASS, no launch.
Import-only smoke check: PASS, no argv/SSH/launch side effects.
`git diff --check`: PASS.

### Real TSPS read-only collector fixture

Executed the final serialized parser/collector in a short SSH Python helper on TSPS. The helper
sampled **itself**, ran a bounded 0.5-second busy phase, slept for 0.5 seconds, and checked an
intentionally stale expected starttime. This does not sample the game and is not evidence of
improved Loading performance. Raw target readings and source SHA: `target-self-probe-current.json`.

- Actual target SC_CLK_TCK: **100**.
- Busy helper interval: **99.316%** process CPU.
- Sleep interval including collector activity/quantization: **1.984%** process CPU.
- Collector-only CPU per snapshot: **3,205,000 / 3,214,667 / 3,307,375 ns**. This excludes Python
  startup, SSH overhead, game-thread-count scaling and log collection; it does not prove <5%
  profiler overhead in a real game run. Short intervals have coarse tick quantization; do not clip
  slightly >100% samples or mislabel that as game CPU.
- Stale starttime: rejected as `identity_mismatch`.
- Runtime discovery: absent. Follow-up independent SSH check: helper PID absent, MainUI count=1.
  No game, MainUI, audio/display configuration, executable or owner assets were changed.

## Review and remaining acceptance

Manual review against roadmap §26.2.5 and local tool style; no independent subagent review was run.
The change preserves the principal launcher/safety guards, does not guess guest PCs and keeps unknown
log-to-scene attribution explicit. Added final-state zombie rejection during review.

Still missing: full owned-run UUID/source/executable/image/catalogue identity across CPU and log
collectors, in-place truncate/regrow continuity, scene-specific navigation oracle, live-only memory
analysis and kernel-correlated termination taxonomy. The initial discovered process is path-checked
but not yet cryptographically bound to the principal harness run. An exec replacing the same PID
without changing its starttime is not covered by the starttime guard alone. The perf wrapper itself
has not been exercised with a new real game run after this edit; only its boundary test and the real
target collector fixture have run. Do not call T0 or C0 fully complete.

Follow §26.9 after the remaining T0 gates: exact id=295 descriptor/storage audit before changing
texture policy, then measured resource ownership and the actual Loading CPU hot path.
Gameplay and stable 30 FPS remain unverified.
