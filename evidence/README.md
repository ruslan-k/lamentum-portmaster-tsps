# Evidence

## Latest evidence and safety disposition (2026-10-23)

- [K1 exact firmware kernel / CMA snapshots](m2b-k1-kernel-cma-provenance-2026-10-23/README.md): exact kernel warning-retry path verified, CMA backing/owner unresolved, idle CmaFree 15,456 KiB; **device NO-GO**.
- [A1 host-only admission replay](a1-storage-admission-offline-replay-2026-10-23/README.md): all four build259 denials reproduce conservative arithmetic; physical CMA assumption unqualified.
- [build259 margin matrix](m2b-e3-build259-margin-sweep/README.md): 64/48/32/24 MiB all stopped before menu; no further margin sweep authorized.
- [M3B build256b observer OFF/ON](m3b-build256b-pair-20261022-01/README.md): BC/non-BC/depth windows covered, buffer/EGL/CMA ownership missing, no menu.
- [M3A build251 BC stripe pairs](m3a-bcstripe-b251-01/README.md): CPU staging changed, all six arms stopped at memory floor; no verified persistent memory saving.
- [E4 host-only owner-pair checkpoint](e4-owner-pair-host-2026-10-23/README.md): build260 diagnostics compiled, historical missing IDs remain unresolved, **not deployed**.

**Execution queue and evidence gates:** [post-build260 roadmap §13](../docs/post-build260-cma-gameplay-performance-roadmap-2026-10-23.md#13-evidence-first-execution-gates-after-the-main1604ed9-re-audit-2026-10-23). These are evidence records, not demonstrations of gameplay or 30 FPS. See older per-build directories for historical results only.

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
