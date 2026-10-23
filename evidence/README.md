# Evidence

**Current policy:** [roadmap §15](../docs/post-build260-cma-gameplay-performance-roadmap-2026-10-23.md#15-revised-publication-install-and-runtime-testing-gates-2026-10-23-overrides-indefinite-device-no-go) separates unrestricted host/source publication, non-executing staged install with backup and hash checks, fresh read-only runtime preflight, and subsequent gameplay qualification. The 15,456 KiB CMA measurement below is **historical**. If reproduced without justified headroom, HOLD the runtime, **not host work or safe staging**. M4-A source is already published at main@509cc985; build261 has no recorded target run.

## Latest evidence and safety disposition (2026-10-23)

- [K1 exact firmware kernel / CMA snapshots](m2b-k1-kernel-cma-provenance-2026-10-23/README.md): exact kernel warning-retry path verified, CMA backing/owner unresolved, idle CmaFree 15,456 KiB in recorded samples; **runtime unsafe at that historic checkpoint**.
- [A1 host-only admission replay](a1-storage-admission-offline-replay-2026-10-23/README.md): all four build259 denials reproduce conservative arithmetic; physical CMA assumption unqualified.
- [M4-A checked BC stripe sizing (host-only)](m4a-bc-stripe-capacity-2026-10-23/README.md): native fixture, pinned-container ASan/UBSan, full suite and AArch64 build pass; request sizing only, candidate uninstalled; §15 preflight required before any runtime launch.
- [M4-B source and generation census (host-only, partial)](m4b-gl-allocation-inventory-2026-10-23/README.md): 77 source callsites (12 wrapped+unmeasured, 65 unknown); 2,048-entry history with 1,200-key create/reuse, 1,024 create/delete pairs, 24 reuses and same GLuints across share groups; overflow is fail-closed and separately counted; build262 cross-built but uninstalled.
- [build259 margin matrix](m2b-e3-build259-margin-sweep/README.md): 64/48/32/24 MiB all stopped before menu; no further margin sweep authorized.
- [M3B build256b observer OFF/ON](m3b-build256b-pair-20261022-01/README.md): BC/non-BC/depth windows covered, buffer/EGL/CMA ownership missing, no menu.
- [M3A build251 BC stripe pairs](m3a-bcstripe-b251-01/README.md): CPU staging changed, all six arms stopped at memory floor; no verified persistent memory saving.
- [E4 host-only owner-pair checkpoint](e4-owner-pair-host-2026-10-23/README.md): build260 diagnostics compiled, historical missing IDs remain unresolved, **not deployed**.

**Historical evidence-led technical work queue:** [post-build260 roadmap §13](../docs/post-build260-cma-gameplay-performance-roadmap-2026-10-23.md#13-evidence-first-execution-gates-after-the-main1604ed9-re-audit-2026-10-23). These are evidence records, not demonstrations of gameplay or 30 FPS. See older per-build directories for historical results only.

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
