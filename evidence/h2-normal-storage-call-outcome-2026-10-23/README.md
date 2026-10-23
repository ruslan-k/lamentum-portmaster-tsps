# H2 partial: normal-path GL result remains explicit unknown

**Disposition:** host-only telemetry/reducer change; `H2` and `HOLD_RUNTIME` remain open.

## Change

When `LC2_LIFE_EVENTS=1`, `LC2_GL_STORAGE_EVENT` reports `call-result=unobserved`, separate from `status=recorded` (ledger row recorded) and `completion=unobserved` (GPU completion unknown). Bounded monotonic `call-id` pairs now cover the CPU-view `glTexImage2D` path and the normal per-mip texture-initialization `glTexImage2D` path; each echoes into its nominal storage event. The events use the existing bounded owner ring, whose dropped/incomplete summary remains the gate. The event writer does not read or drain the GL error queue and does not alter admission, deletion, or storage behavior.

`tools/ledger_bases.py::replay_texture_budget` counts `gl_storage.call_results_by_status` through the floor; absent legacy fields remain `unknown`, never success. For nonzero `call-id`, it now requires exactly one owner begin, one post-call `call-result-unobserved`, and one matching storage event; it checks owner/generation/bytes and timestamp order, and fails closed on incomplete or mismatched pairs. H3 exposes the correlated count and preserves raw fields.

## Source and build identity

- Current unbuilt overlay SHA-256: `6c1c881181ed8f33f106fa442206df945490bea5032c9b54fef830616a7cf74a`.
- Current applied source tree: 390 files, SHA-256 `00f785f1f953888a9b0b072fb6e1a5856f824d3cf668b1239764dc41089231e3`.
- GL allocation inventory remains 77 callsites: 12 `wrapped+unmeasured`, 65 `unknown`.
- Candidate ELF `c4671440…` is still bound to the prior build-time overlay SHA `5ab2d36f…` and source-tree SHA `3fcc9e78…`; this follow-up was **not built into that ELF**, staged, or run.

## Verification

- Focused `test_life_events`, `test_ledger_bases`, and `test_peak_memory_waterfall`: **57/57**.
- Full tools suite with `LAMENTUM_REQUIRE_ZERO_STORAGE_ALIAS_TEST=1`: **433/433**, zero skips.
- `gl_allocation_inventory.py`, `py_compile`, and `git diff --check` passed.

## Limits and next gate

The begin/result pair is correlated by `call-id` for one source path, while the normal GL result remains unobserved. The reducer fails closed on incomplete/mismatched pairs and incomplete owner-ring summaries; it does not inspect GL errors, prove GPU completion, or attribute physical CMA. The source-linked host fixture is supplemental, not a full `nvn_textures.h`/GL runtime test. No device action, game launch, reboot, margin, or firmware change was made. `T2_STORAGE_MARGIN_MIB` remains unset.