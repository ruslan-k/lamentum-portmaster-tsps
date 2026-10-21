# N4-C/D integration: one owned reader, one navigator, release ACK

Reviewed 21e40fd / owner roadmap §48.2 C/D and §48.4 priority 1.
Host integration completed here; device qualification remains OPEN.

## Actual code path

`nav_chain.py` now delegates to `owned_nav_chain.py`. The former main routine
that discovered a PID by basename, constructed OwnedSerial without expected_run,
used an unbracketed capture and reset Navigation on later taps has been removed.
Historical pure sweep/row receipt functions remain only as analysis helpers.
No legacy `--sweep` control path is enabled.

CLI requires --expected-run (principal harness expected-run.json), --evidence,
--response-timeout-s (explicit finite 0..60-second diagnostic bound) and
--diagnostic-input. Omitting the latter rejects before file lookup/SSH/input.
It does not launch the game or change the floor; it attaches only to the pinned run.

One `OwnedNavigationDriver` retains one `Navigation` and one incremental
`OwnedSerial(expected_run=...)` for the entire attempt. Qualified header hash and
boot/PID/starttime/executable dev/inode are pinned on attachment. No qualified
header => no action. Rejection/change => terminal refusal, never a reset/rebind.

Each usable observation is bracketed by owned collector/process checks before
and after the common `pad.capture`/oracle path. Serial changing across capture
causes image discard, not a guessed binding. Immediately before input another
collector/liveness check must still match; immediately after the synchronous
press/release it is checked again. This narrows, but does not magically eliminate,
the cross-process race between the last check and evdev write. No atomic kernel
ownership/evdev transaction is claimed.

A press requires a matching action and `released is True` receipt. Raw receipts
from pad.press are retained. Missing release or post-press generation rejection
is terminal and cannot issue another press. A host receipt is not proof that the
guest sampled the event or that a human pressed it.

Overshoot is handled by the SAME navigator, so a two-row move cannot silently
construct a new navigator and issue a corrective tap. Fast duplicate serials do
not recapture/reissue input. Capture+transfer duration is logged separately.
Monotonic overall deadline is checked before and after capture and before input;
a slow capture cannot authorize a late press.

## Safety boundary

Confirm is deliberately blocked. This driver is row-only diagnosis until M1's
96 MiB-safe headroom and N5's measured config/controls page fingerprints exist.
No full-load legacy driver was enabled; no new device taps were made in this step.
No gameplay, safe-memory, physical-input or 30 FPS result is asserted.

## Executed verification

14 added host tests; full suite 253 PASS; Python 3.10 syntax parse PASS.
Transport fixtures: persistent overshoot refusal, changed generation, foreign
capture, a serial changing during capture, missing release, rotation during
press retaining release evidence, duplicate polling and terminal timeout,
unqualified log, Confirm block and slow capture deadline.

Additionally the REAL OwnedSerial/collector_request remote payload executes in a
local subprocess against temporary UUID-headed logs. Rewriting that log during
capture rejects generation continuity with zero press callbacks; a subsequent
poll does not revive the refused session. These temporary fixture logs are
synthetic and are NOT represented as handheld observations.

CLI refusal and delegation guards run as subprocesses without SSH. Tests and
help receipt live under evidence/n4-owned-driver/. A clean-export run is recorded
there separately before publication.

## Remaining N4 device gate

A real owned, released, serial-qualified ONE-ROW movement is still not qualified.
Timeout/tap calibration, observation overhead and guest-visible movement need
safe-menu testing after M1, not more blind/low-floor sweeps. Large Native Mali
allocations still need owner/generation attribution before a safe reduction.
