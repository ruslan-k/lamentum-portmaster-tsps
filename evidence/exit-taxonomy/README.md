# T0: evidence-gated exit taxonomy and propagated probe status

## Roadmap scope

This implements the termination-evidence part of §26.2.7 of the current roadmap, not the full T0
gate. No game binary, shader, texture policy, owner asset, safety cap or display/audio setting was
changed. No new game run or OOM stress test was performed.

## Corrected failure modes

1. `is_killed_without_stop()` formerly documented every shell `Killed`/exit-137 token as the kernel
   OOM path. Such a token can also be caused by an operator, supervisor or unknown signal source.
   It is now explicitly a log-only hint, not OOM proof.
2. `load_probe.main()` printed a nonzero `harness_rc` but returned None, causing `sys.exit(None)` to
   report outer exit zero. A new integration test reproduced `None != 4` before the one-line fix;
   the probe now returns the harness status. Navigation exceptions still propagate as exceptions.
3. A busy-state check now happens **before** old-log truncation. The fresh post-truncation snapshot
   remains the baseline used for this run; stale previous STOPs are not copied into it.

## New classifier and receipts

`tools/exit_outcome.py` returns one of:

- `runtime_timeout`: only TIME_LIMIT stops, without an additional kill hint;
- `invalid_configuration`: invalid runtime probe configuration;
- `runtime_stop`: other genuine STOP records, such as T2_TEXTURE_BUDGET;
- `host_timeout`: the host recorded its termination request (cleanup remains separately checked);
- `sigkill_unknown`: shell kill hint without sufficient cause attribution;
- `kernel_oom_sigkill`: a matching kernel victim receipt;
- `exit_unknown`: none of these receipts is sufficient.

A kernel OOM classification requires available before/after kernel captures, one matching boot,
consistent target HZ, the observed runtime PID/starttime, an in-window timestamped kernel
`Out of memory: Killed process PID (comm)` record, and consistency with any PID in the shell kill
line. The timestamp must be at or after both the pre-launch bound and the process start, and no
later than the after-capture bound. Old victims, other PIDs/boots, future timestamps, unavailable
kernel logs and Mali notifier text alone do not establish OOM. Unknown kernel formats or unresolved
clock alignment remain unknown rather than guessed positives.

A TIME_LIMIT printed before a kill during teardown no longer hides that kill: preserve the STOP
list but classify the additional evidence and do not mark `runtime_ok=true`.

The principal harness now captures kernel evidence before launch and after cleanup and retains
`termination`, `process_identity`, `identity_errors` in cleanup.json. The existing target proc
collector discovers a unique runtime by executable path and pins boot/PID/starttime for subsequent
polls. A runtime which exits before it is observed has no owner receipt and cannot receive a
positive OOM attribution from this classifier.

Exit status compatibility: cleanup failure=3, other runtime stop/unknown exit=4, invalid config=5,
host timeout=6, cause-unknown SIGKILL hint=7. **New code 8 means kernel-correlated OOM.** Zero still
means a clean diagnostic TIME_LIMIT run, not successful gameplay. `perf_sample` already propagates
the harness status; `load_probe` now does as well. Cleanup failure retains precedence while the
underlying termination evidence remains in the JSON.

Raw `kernel-before.json` / `kernel-after.json` are owner-local diagnostic artifacts; do not blindly
stage them with proprietary runtime logs or dumps. Public reports should use the relevant victim
receipt/metadata, not assume all local evidence is suitable for publication.

## Verification

`python3 -W error::ResourceWarning -m unittest discover -s tools -p 'test_*.py'`: **97 tests PASS**.
`git diff --check`: PASS. The new probe-boundary test exposed an unclosed parent-side harness.log
handle; it is now closed immediately after Popen inherits its descriptor, and the warning-strict
suite passes.

Synthetic tests cover unknown kill cause, exact matching OOM, old/future timestamps, foreign PID,
changed boot, process-start bounds, unavailable kernel capture, absent owner, Mali-only notifier,
STOP/config/host taxonomy and kills after TIME_LIMIT. Mocked external SSH/process-boundary tests
execute the principal harness's real orchestration, write/read its JSON and verify statuses 7/8,
without launching or killing a real process. Busy preflight is checked to leave the old log alone.
The load-probe supervisor-boundary test verifies that harness code 4 is no longer outer success.

Real TSPS smoke: executed the **read-only** kernel collector twice and then inspected process state.
Both captures were available, same boot, target HZ=100, monotonic bounds ordered, with 1,741
bracket-timestamped kernel lines. State: game=0, MainUI=1, principal=1, runtime=1. The unmodified
kernel snapshots were kept outside the repository in the owner's local workspace. Public measured
metadata and payload SHA-256: `read-only-smoke.json`.

Log-only replay of existing captures (deliberately without historical correlated kernel/owner
receipts): newgame-20 and load-probe-03 => `sigkill_unknown`; load-probe-08 => `runtime_stop` with
T2_TEXTURE_BUDGET; load-probe-10 => `exit_unknown`. This demonstrates that the new code does not
invent missing receipts. It does **not** disprove separately reviewed historical OOM findings, and
arm 10's separately documented operator TERM remains known from that action record.

Manual review against §26.2.7; no independent subagent review was run. The actual principal launcher
was not invoked for this change. Unit/boundary tests and the live read-only collector smoke are the
extent of verification; a new full device run with the changed harness is still needed.

## Remaining gates

Full run UUID/owner-image/catalogue/source binding across harness, CPU collector and log stream;
same-inode truncate/regrow continuity; live-only memory minima; page-specific navigation oracle;
identity-safe host signal delivery and reliable final log generation binding remain open. Initial
path-based process discovery is not a cryptographic run binding. Existing hard-stop signaling and
full-log snapshots were not replaced in this scoped change. No claim of full T0/C0 completion,
playability or 30 FPS follows from these fixes.
