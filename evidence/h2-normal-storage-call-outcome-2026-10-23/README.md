# H2 partial: normal-path GL result remains explicit unknown

**Disposition:** host-only telemetry/reducer change; `H2` and `HOLD_RUNTIME` remain open.

## Change

When `LC2_LIFE_EVENTS=1`, `LC2_GL_STORAGE_EVENT` reports `call-result=unobserved`, separate from `status=recorded` (ledger row recorded) and `completion=unobserved` (GPU completion unknown). On the one `nvn_texture_cpu_view_name` 2D CPU-view `glTexImage2D` path, a bounded monotonic `call-id` now ties `attempt-recorded` and post-call `call-result-unobserved` owner events to the subsequent nominal storage event. These events use the existing bounded owner ring; its dropped/incomplete summary remains the gate. The event writer does not read or drain the GL error queue and does not alter admission, deletion, or the storage call.

`tools/ledger_bases.py::replay_texture_budget` counts `gl_storage.call_results_by_status` through the floor; absent legacy fields remain `unknown`, never success. For nonzero `call-id`, it now requires exactly one owner begin, one post-call `call-result-unobserved`, and one matching storage event; it checks owner/generation/bytes and timestamp order, and fails closed on incomplete or mismatched pairs. H3 exposes the correlated count and preserves raw fields.

## Source and build identity

- Current unbuilt overlay SHA-256: `9fb2e3bcb2607f1f27641ea39c7d96a57fc584a2efb82a8f298832250332a8c3`.
- Current applied source tree: 390 files, SHA-256 `0e1eae300e079a398dd73f4d55707fcc2e74d8832a17d97966de3bce9cfd887a`.
- GL allocation inventory remains 77 callsites: 12 `wrapped+unmeasured`, 65 `unknown`.
- Candidate ELF `c4671440…` is still bound to the prior build-time overlay SHA `5ab2d36f…` and source-tree SHA `3fcc9e78…`; this follow-up was **not built into that ELF**, staged, or run.

## Verification

- Focused `test_life_events`, `test_ledger_bases`, and `test_peak_memory_waterfall`: **57/57**.
- Full tools suite with `LAMENTUM_REQUIRE_ZERO_STORAGE_ALIAS_TEST=1`: **433/433**, zero skips.
- `gl_allocation_inventory.py`, `py_compile`, and `git diff --check` passed.

## Limits and next gate

The begin/result pair is correlated by `call-id` for one source path, while the normal GL result remains unobserved. The reducer fails closed on incomplete/mismatched pairs and incomplete owner-ring summaries; it does not inspect GL errors, prove GPU completion, or attribute physical CMA. The source-linked host fixture is supplemental, not a full `nvn_textures.h`/GL runtime test. No device action, game launch, reboot, margin, or firmware change was made. `T2_STORAGE_MARGIN_MIB` remains unset.