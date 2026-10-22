# Evidence

Use one directory per bounded device run: `device-01/`, `device-02/`, … Each
published directory contains:

- `README.md` — hypothesis, exact build/settings/run identity, measured result,
  limitations, and next gate;
- compact receipts — deployment hashes, run UUID/boot/PID identity, pre/post
  device state, cleanup, and screenshot metadata/hash where relevant.

Keep raw device data local-only and gitignored: `latest.log`, full kernel dumps,
and PNG/KMS captures. A report may cite their SHA-256, size, selected exact
records, and the local path; do not commit the raw files.

Rules that apply to every entry:

- A controlled stop is not a frame and not a failure of the game: it is the
  runtime refusing to guess. Name the stop code and the caller.
- Never report a picture without a physical KMS capture, and never report
  performance from a diagnostic build. Publish a capture receipt/hash, not the
  raw screenshot.
- Per-run claims must be traceable to the run-owned log identity and an exact
  record; cumulative values from different timestamps are not a live-set join.
- Label SpruceOS cleanup captures as cleanup evidence, never gameplay.
