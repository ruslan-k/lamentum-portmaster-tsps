# E4 owner-pair host checkpoint — 2026-10-23

## Scope and verdict

Host/source/build work for roadmap §78 P0-1/E4 is implemented and verified. This is **not** a device qualification: build260 was not installed, no TSPS process was launched, and no gameplay or FPS claim is made. The device gate remains blocked by the §86 low-CMA stop; the immediate next device-related action is read-only CMA investigation.

## Replayed build251 evidence

All six existing `latest.log` files were SHA-256 checked against `evidence/m3a-bcstripe-b251-01/ab-summary.json`; each run UUID also matches its summary. Every log has 119 `LC2_TEXTURE_PAIR` records but contains **no** `LC2_TEXTURE_OWNER_EVENT` record or owner-event summary, so the old artifacts cannot establish the lifecycle cause for the unresolved IDs.

- `baseline-01` — `reconciled`; log SHA-256 `56f122c0fbeb6239c8d3b3cc506258819d67f61fee1f9d62b2398f2418f61023`.
- `candidate-01` — `288=unresolved`; log SHA-256 `d37f7b0049c9e387f507075ea29af3096f80a145c8952fda83e0b6feee33f213`.
- `baseline-02` — `288=unresolved`; log SHA-256 `ba99b1a211baa7ab9e72271c7eff553825bd5eb267af97d77cabcd455c738006`.
- `candidate-02` — `reconciled`; log SHA-256 `18417ff9df8f82cfa1e983cf847f90e848f10c29539f8996113bbace0a0c5bbc`.
- `baseline-03` — `280=pair_not_yet_emitted`; its matching pair was timestamped **71,920,625 ns (71.920625 ms) after** the floor snapshot. Log SHA-256 `d5dda96074c517e68e31e38c002cd74d0f7d04a5867668fdff8acebbee1bf9d1`.
- `candidate-03` — `280=unresolved`; log SHA-256 `971f21cc6703bd756e9a49369f755695c13cc4e0b396df07e8954425857562b8`.

The three unresolved cases remain unresolved. They were not discarded or converted into successful joins.

## Changes

- `runtime/lamentum-adapter.patch` now includes a fixed-capacity **512-entry** owner-event ring gated by `LC2_LIFE_EVENTS=1` (default off). It emits run ID, sequence, monotonic timestamp, NVN ID/object identity, explicit generation basis, storage owner, charge/pool fields, status, and a completion/overflow summary. The current object-generation identity is the adapter's monotonic NVN object ID; physical storage generation and source-write generation remain distinct/unproven (`source-write-generation=untracked`).
- Owner observations cover budget charge, initialization, pair/materialization, alias resolution, first-use reservation, CPU texel-write, and retirement entry points. These are diagnostic receipts only; they do not prove immutable content, physical Mali residency, or safe reclamation.
- `tools/ledger_bases.py` retains fail-closed replay and classifies missing coverage as `pair_not_yet_emitted`, `missing_owner_path`, `generation_mismatch`, `alias_scope_mismatch`, `log_truncated`, or `over_capacity`; no active owner is silently dropped. `replay_texture_budget(..., owner_events_expected=True)` requires the ring summary for a schema-capable candidate; legacy build251 replay keeps that expectation off and remains `unresolved` when it has no owner events. Generation conflicts are evaluated at the floor timestamp, so a later NVN ID generation cannot rewrite the earlier live-set join. `tools/test_ledger_bases.py` now exercises IDs 280/288, late pairs, missing owner path, incomplete ring/final line, schema mismatch, late-generation isolation, duplicate BC materialization, alias resolution, conflicting generations, zero charge, independent subtract, nonmonotonic time, and overflow.

## Verification

- Full host suite: **317 tests passed**.
- Focused ledger/life-event/GL-storage suite: **45 tests passed**; Python compilation passed.
- Recovered source baseline: **435/435** manifest entries verified; `git apply --check` and `git diff --check` passed.
- Adapter source diff and `runtime/lamentum-adapter.patch` are byte-identical at SHA-256 `72b309b02242377d7faf524fe091e9603013d5051098c0c7037ed434d661b6dd`.
- The 1,832,060,032-byte `image-09/lamentum-romfs.section` was streamed through SHA-256 and matched its generated image-table digest `80ad4427164a0b7ad61c3a3fcd955bd158635aac1ee42ebb67d01dfae279b893`.
- Pinned container `pmjs-arm64-spruce-local:20261002-gcc10` (`sha256:e437308c01ce7af4a035c3f0652bc886e258889f66803f805bce53d05af75f0c`) built local `build-260/lamentum-nextos`: AArch64 ELF64 PIE, 2,202,664 bytes, BuildID `ef6f6ecc292036ac70d9d5fe2b021da1a3719cef`, SHA-256 `f2930135ecc431ffab92595b6324486cbf5df0b6484138d9dcf33d8cc1c680af`, maximum GLIBC requirement 2.27. The binary contains the owner-event record and summary markers. Build warnings were the baseline's ignored `write()` results and unused optional functions.

## Not verified / next gate

Build260 is a host-only diagnostic candidate and was **not deployed**. No owner-event device capture or observer-OFF control exists yet. Per the latest §86 read, free CMA remained around 15 MiB; do not install or launch until read-only CMA investigation identifies a safe baseline and the device gate is re-evaluated. Build259 remains the last reported installed runtime. Gameplay, a correct world, save/load, and ≥30 FPS remain unverified.