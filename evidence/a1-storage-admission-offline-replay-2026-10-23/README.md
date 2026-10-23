# A1 — build259 admission-policy replay (host only)

**Date:** 2026-10-23. **Branch:** `main`. This replays the four build259 refusals from the sanitized `ab-summary.json` against their local, run-bound `latest.log` receipts. The raw logs stay local and are not committed.

## Result

All four target `T2_STORAGE_ADMISSION` records were found in complete owned-log captures and reconciled with the arm summary, run UUID, boot, runtime SHA, header receipt, final byte cursor and tail anchor. Target timestamps are copied from `t-ns`; the source implementation uses `CLOCK_MONOTONIC`. No timestamp was synthesized.

The source-bound events reproduce the existing C arithmetic exactly:

- 64 MiB margin: owner 61, 5,400,000 scratch bytes; required CMA 72,508,864 B; refusal at 70,516 KiB.
- 48 MiB margin: owner 77, 10,368,000 scratch bytes; required CMA 60,699,648 B; refusal at 47,316 KiB. A same-run/owner `LC2_BC_FULL_STAGE` record identifies a 10,368,000 B requested CPU-scratch peak in `initialize`; that record has no timestamp, so it is linked by log order only. No time join is claimed.
- 32 MiB margin: owner 0, 512,000 GL-declared bytes; required CMA 34,066,432 B; refusal at 30,520 KiB.
- 24 MiB margin: owner 0, 8,294,400 GL-declared bytes; required CMA 33,460,224 B; refusal at 12,664 KiB.

Each observed reason is `cmafree-margin`; all four arm summaries record zero `LC2_GL_STORAGE_EVENT` rows after the refusal. The 64 MiB arm's memory timeline is incomplete, so no timeline interpolation was used. GL request subtype, physical CMA bytes and driver backing remain unknown.

## Model comparison and limits

- `all_bytes_maybe_CMA` reproduces the deployed `required_cma = GL + scratch + margin` and `required_available = 96 MiB + required_cma` checks. Its outputs match the observed refusals; that is a formula replay, not evidence that the requests physically consume CMA.
- `proven_CMA_only` and `mixed_two_ledger` fail closed for all four requests. `would_admit=false`, `qualification=unknown`: proven CMA backing and/or CPU peak inputs are missing, and no separate driver uncertainty margin is evidenced.
- The per-request GL API kind is left `unknown` where the admission record does not distinguish texture, renderbuffer or buffer. Owner `0` is preserved literally; storage ID/generation remain null.
- Current-copy log SHA-256 values are in [`summary.json`](summary.json). The owned-log header and tail anchor are append-only continuity evidence, not a full historical cryptographic attestation of every byte.

No production code, margin default, or device state was changed. The replay made **zero device actions**; the host validation passed **15 focused A1 tests**, the **359-test** tools suite, Python compilation, and `git diff --check`. No build, game, New Game, gameplay or FPS test was run. The device NO-GO remains: idle `CmaFree=15,456 KiB`, physical CMA ownership unknown.

The existing ledger tests already cover GL re-specification and mip/subresource accounting; the A1 tests focus on typed requests, fail-closed missing values, raw-log identity/completeness, overflow and explicit synthetic counterfactuals. Next host-only roadmap work is M4-A: checked BC stripe/small-mip capacity. Do not install or launch until the independent CMA go/no-go is reopened.
