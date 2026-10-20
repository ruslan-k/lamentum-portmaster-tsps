# T0 follow-up: complete byte records and opened-log identity

## Scope and roadmap

Re-read `docs/performance-roadmap-30fps.md` through §26 at current origin/main. The latest
implementation order is §26.9, starting with T0. This change addresses §26.2.1 and the log-file
part of §26.2.2. It does **not** close all of T0, and it makes no rendering/performance claim.
No new executable was built or deployed and no game run was started.

## Reproduced failure, not just a proposed fix

Executed the previous committed `PAYLOAD` from Git HEAD and the changed payload against a file
containing a complete ROMFS line followed by `NVN_PRESENT_PIXELS frame=80` **without newline**.
Both cursors remained at byte 13, but the old payload already reported one present/frame 80.
The next poll would reparse that trailing record. The changed payload reports zero presents and
no frame until a complete line exists. Exact outputs: `regression.json`.

The old code also derived byte offsets by re-encoding replacement-decoded Unicode. Invalid UTF-8
can expand into more bytes and skip genuine records. Cursor movement now uses raw byte lengths.

## Changes

- `tools/load_metrics.py`: open the log once, `fstat` that descriptor, retain `(dev, inode)`, read
  bytes up to the observed size, split at the last complete newline, then decode only that prefix.
  No complete newline means no consumption and no event. Negative offsets are rejected.
- Detect observed shrink and replacement inode, including replacement logs whose lengths are equal
  to or greater than the previous cursor. Reset counters on a changed log identity.
- `collector_request()` transports cursor and identity together; `load_probe.py` now calls it.
- `tools/test_load_metrics.py`: five added test methods execute the actual generated payload in
  subprocesses. Cases: split frame numbers, no newline, invalid/split UTF-8, replacement inode at
  equal/greater length, and observed truncation followed by append.
- `tools/verify_load_collector.py`: reusable host-only replay of a private captured log, with uneven
  append boundaries and splits inside actual event names/numbers. Public output is counters and
  source SHA-256 only; it does not copy owner log contents.

## Verification

`python3 -m unittest discover -s tools -p 'test_*.py'`: **76 tests PASS**.
`git diff --check`: PASS after removing a trailing empty line in the corrected G0 report.

Replayed actual captured logs through the actual collector and fold function. Compared every
cumulative counter, last frame, STOP list, last budget receipt, Killed token and consumed byte cursor
with a single-pass parse of complete lines. All comparisons passed (`replay.json`):

| captured arm | source bytes | incremental polls | presents / last frame | final STOPs |
|---|---:|---:|---:|---|
| load-probe-08 | 6,065,651 | 49 | 461 / 461 | T2_TEXTURE_BUDGET |
| load-probe-09 | 5,831,985 | 49 | 440 / 440 | T2_TEXTURE_BUDGET |
| load-probe-10 | 8,330,344 | 46 | 501 / 501 | none |

These are **host replays of existing device logs**, not additional device runs. Arm 10's lack of a
runtime STOP is consistent with its operator TERM, not a clean guard-stop receipt.
The synthetic tests and replay establish framing/counter behavior, not on-device overhead.

## Corrected earlier G0 report

`docs/gpu-ledger.md` and `evidence/load-probe-10/summary.json` no longer assert that stable charged
textures prove the guest heap is the consumer or that Mali memory necessarily overlaps RSS.
Those were unsupported deductions. The exact large-texture first-use reservation remains relevant;
other GL/driver/guest owners and alias overlap must still be measured. Arms 04/07/08/09 used build218;
arm 10 used build219 and was operator-terminated. The earlier attribution of those guard stops to
build219 was also incorrect.

## Remaining acceptance gaps / next scope

T0 is still open: boot/run UUID and owned PID/starttime checks (including PID reuse), complete-line
and log-generation receipts integrated with phase/process liveness, target-correct CPU metrics,
page-specific configuration-screen selection oracle, correlated exit taxonomy and live-only memory
minima. An inode and length are **not** a full run identity. In-place truncate+regrow beyond the old
cursor between polls can evade current detection if the inode stays unchanged; do not claim it is
covered by the observed-shrink test. A run UUID/process identity or validated continuity mechanism
is still required. Missing log paths currently raise an error for the caller to record, not empty
success metrics.

After T0, follow §26.3's exact id=295 descriptor/storage audit. No format, texture policy, safety cap,
shader catalogue or original asset change is authorized or implied here. Neither gameplay nor
30 FPS has been demonstrated.
