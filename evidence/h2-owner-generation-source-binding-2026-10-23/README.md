# H2 source binding: NVN texture object identity

**Disposition:** source semantics are bound for the current host-built candidate ELF. This does not bind historical build256b logs, prove persistent telemetry was exercised, or establish GL/driver/CMA allocation success.

## Independently checked identity chain

- `runtime/lamentum-adapter.patch` SHA-256: `5ab2d36f5dcb1fdc275bfcaa55b9be8cfcc2dace10044bc9c932f5083a0dee62`.
- At build time, the applied `adapter-src` diff had the same SHA-256; its base is `c8d01ca1fed5adab1ae7ad920605f199bb83a72e`.
- The build-time applied tree inventory was 390 source files, SHA-256 `3fcc9e78155ecdfd71507e860c5120d313a6a2d81967eed2ece572215cf38689`, and 77 classified callsites (12 `wrapped+unmeasured`, 65 `unknown`). This matches `current-elf-host-build-2026-10-23/summary.json`.
- The current ELF receipt binds that source inventory and overlay to ELF SHA-256 `c46714403f22074d92710192d1164cfe0b7a4f62f1a4890ffb7a1e224c542332`, Build ID `5b1b3412da7b43442a0ebf097e904cb8cbef0c8e`. Existing staging readback evidence records the same candidate ELF; it remains not run.
- Source file hashes in the applied tree: `native/nvn_memory.h` `1e3bf3c97cb5c0dd28e9f290aad9606c18e6c1b2a72b0d9aea2c1618de4d3db9`; `native/nvn_textures.h` `aada1fb2ec8f914950509b04b8871f5c2bd34c09f9eb2911571916704efc45af`.

## Proven semantics for this ELF only

`loader.c` includes `nvn_bridge.h`; that header includes `nvn_memory.h` and `nvn_textures.h` in the same translation unit. `zero_next_object_id()` uses the translation unit's shared `nvn_next_object_id` with atomic fetch-add, returns `previous + 1`, and stops on `UINT64_MAX` rather than wrapping. `nvnTextureInitialize` assigns `.id=zero_next_object_id()`. Its owner event passes `t->id` as both `nvn-id` and `object-generation`; the texture-pair formatter likewise emits `object-generation=p->nvn_id`, and the initialize pair sets that to `t->id`.

Therefore, for a run whose recorded ELF SHA-256 is exactly the candidate hash above, `generation-basis=nvn-object-id` identifies a monotonically assigned NVN object identity within that process. It is not a GL name generation, GL storage generation, pool-write generation, or physical allocation identity. GL name/storage generations and pool generations remain separate fields. Physical backing and completion remain unknown.

This source interpretation does **not** apply to the historical build256b ON log: its ELF differs, so that run's `owner-generation` remains raw/semantically unknown. No runtime behavior, admission rule, deletion, margin, firmware, or device state was changed for this receipt.

## Unbuilt follow-up overlay

The later host-only telemetry overlay adds `call-result=unobserved` and bounded `call-id` begin/result events for the `nvn_texture_cpu_view_name` 2D CPU-view `glTexImage2D` call; no GL error queue is read. Current unbuilt overlay SHA-256 is `9fb2e3bcb2607f1f27641ea39c7d96a57fc584a2efb82a8f298832250332a8c3`; source-tree SHA-256 is `0e1eae300e079a398dd73f4d55707fcc2e74d8832a17d97966de3bce9cfd887a` (390 files, 77 callsites unchanged). The staged ELF `c4671440…` remains bound to the earlier build-time overlay/source hashes above; it does **not** contain this telemetry. No device binary was replaced or run.

## Host fixture

`tools/test_life_events.py::test_texture_owner_generation_tracks_nvn_identity_separately_from_gl_storage` checks source/overlay identity, compiles the exact `zero_next_object_id()` implementation with the event header, and pins production owner/pair callsites. `test_candidate_share_group_epoch_drives_storage_identity` compiles the exact root share-group helpers and generation branch. `test_storage_attempt_call_id_pairs_begin_result_and_nominal_storage` compiles the event header, pins source-call order, and verifies the same call-id links begin/result/storage records without invoking `glGetError`. These are supplemental source-contract tests, **not** a full `nvn_textures.h` build or EGL/GL/game run. Focused `test_life_events`: **14/14**; full tools suite with required source fixture: **433/433**, zero skips.

## Next gate

Use this interpretation only when future telemetry is bound to the exact ELF SHA above. Persistent owner-event coverage, per-call GL outcomes, GPU completion, matched CMA snapshots, and a positive independently justified reserve are still required before any runtime probe. `T2_STORAGE_MARGIN_MIB` remains unset.
