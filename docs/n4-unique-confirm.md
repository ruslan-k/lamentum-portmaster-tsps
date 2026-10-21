# N4-A/B: unique-frame Confirm and bounded monotonic waiting

Reviewed roadmap at 0344ac0, owner §48.2 N4-A/B and §48.4 priority 1.
This change fixes the pure navigation core, not the complete device driver.

## Reproduced before implementation

The five new Confirm regressions all fail as assertions on the prior navigator:
- a repeated serial can issue Confirm;
- an older serial than the first target observation can issue Confirm;
- conflicting cursor positions on one serial can issue an extra action;
- an unknown cursor does not clear the target evidence;
- leaving and returning to the target reuses old confirmation evidence.

Retained reproduction: evidence/n4-unique-confirm/red-base.txt, executed against
exact prior HEAD source in an isolated host directory. Four additional fake-clock
cases initially encountered the absent clock/timeout API, then passed after it
was implemented. No fake device data or gameplay receipts are involved.

## Implemented

Navigation records last_observed_serial and target_seen_serial. Only unique newer
observations advance the machine. Duplicate identical observations WAIT without
changing confirmation evidence; conflicting duplicates and backwards serials
REFUSE. A cursor outside a known band clears the streak. Leaving the target resets
it, so returning requires two new observations. Refusal clears confirmation evidence
and is terminal. UNKNOWN/unexpected pages remain fail-closed.

Replaced the three-poll stale budget with an injectable monotonic clock and a
positive finite response_timeout_s. A hundred immediate duplicate polls stay WAIT;
a post-deadline poll refuses even if a fresh expected page arrives. After Confirm,
newer MAIN_MENU observations do not extend the acknowledgment deadline. Timeout
receipts include elapsed_ms, last_serial, issued_serial, owner_verified=false.

The 5-second default is a bounded HOST diagnostic value, not an evidence-qualified
handheld timeout. Ownership is not inferred by this pure core. The integration
layer must verify UUID/boot/PID/starttime/ELF and discard the entire Navigation
instance on ownership/generation changes. No same-generation proof is added here.

The old test that expected refusal on the fourth immediate poll was updated to the
owner's new contract: 100 polls WAIT, then refusal after advancing a fake clock
past the deadline. No real sleep is needed in these tests.

## Verification and limits

Nine added tests; full host suite 239 PASS, including existing navigation/chain
fixtures. No runtime build/deploy needed: these are host Python changes only.
No device process, controller or runtime state changed in this step.

N4 remains OPEN as an end-to-end packet: stateful owned collector/oracle/pad wiring,
release acknowledgment, calibrated wall deadline and process-liveness receipts are
not yet qualified on the device. NEWGAME_CONFIG/CONTROLS fingerprints and the M1
96 MiB-safe memory gate remain prerequisites to a world attempt. No FPS improvement,
scene progression or playability is claimed.
