# H2 partial: normal-path GL result remains explicit unknown

**Disposition:** host-only telemetry/reducer change; `H2` and `HOLD_RUNTIME` remain open.

## Change

When `LC2_LIFE_EVENTS=1`, `LC2_GL_STORAGE_EVENT` now reports `call-result=unobserved`, separate from `status=recorded` (the ledger row was recorded) and `completion=unobserved` (GPU completion is unknown). The event writer does not read or drain the GL error queue and does not affect admission, texture storage, deletion, or gameplay behavior.

`tools/ledger_bases.py::replay_texture_budget` now counts `gl_storage.call_results_by_status` for events at or before the floor sample. A missing field in legacy logs remains `unknown`; it is not promoted to success or `unobserved`. `tools/peak_memory_waterfall.py` exposes the distribution in `ledgers.gl_nominal_storage`.

## Source and build identity

- Current unbuilt overlay SHA-256: `030b2eaa6b942f90e293c5d1cc766e7dafece67cee5553f7dd8982d47eaad5d5`.
- Current applied source tree: 390 files, SHA-256 `422485fa93a7336023dbdf0ba93a21465937787ca3590fa672a67a63d8ec7f9f`.
- GL allocation inventory remains 77 callsites: 12 `wrapped+unmeasured`, 65 `unknown`.
- Candidate ELF `c4671440…` is still bound to the prior build-time overlay SHA `5ab2d36f…` and source-tree SHA `3fcc9e78…`; this follow-up was **not built into that ELF**, staged, or run.

## Verification

- Focused `test_life_events`, `test_ledger_bases`, and `test_peak_memory_waterfall`: **55/55**.
- Full tools suite with `LAMENTUM_REQUIRE_ZERO_STORAGE_ALIAS_TEST=1`: **431/431**, zero skips.
- `gl_allocation_inventory.py`, `py_compile`, and `git diff --check` passed.

## Limits and next gate

This records an explicit unknown, not a per-call GL success/failure result. There is no begin/result correlation ID, no GL error inspection, no GPU completion proof, and no physical CMA attribution. A future per-call transaction must stay within an explicitly owned diagnostic error queue; do not add `glGetError()` to normal title telemetry. No device action, game launch, reboot, margin, or firmware change was made. `T2_STORAGE_MARGIN_MIB` remains unset.