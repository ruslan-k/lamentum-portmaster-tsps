# H3 memory-waterfall reducer — initial host implementation

**Status: initial host reducer implemented and tested; no real-run waterfall produced yet.** The observed post-boot CMA state is high, but runtime remains `HOLD_RUNTIME` because the game allocation classes, overlap and independent safety reserve are unqualified. No device launch or reboot was performed for this H3 work.

## Implementation

`tools/peak_memory_waterfall.py` reuses `ledger_bases.replay_texture_budget()` for owned budget/GL-storage/owner-event replay and `cma_readonly_compare.compare_snapshots()` for same-boot CMA order/process comparison. It accepts a run log, identity-pinned process timeline, two or three CMA snapshots, a harness identity, and a filtered kernel-warning delta bundle.

The output keeps separate ledgers for logical guest/budget bytes, per-window CPU BC/other staging requests, nominal GL storage, process pages, DMA-BUF inventory and CMA free orders. It does **not** sum them. Per-window requested peaks are reduced by maximum, not addition. M3B decode, GL-allocation and upload subintervals and per-event size/subresource fields are preserved. The runtime currently emits `owner-generation` equal to `owner-id` with `generation-basis=nvn-object-id`, so the reducer keeps that raw value but leaves semantic owner generation `unknown`; `storage-generation` remains separate. A targeted source check in the local build-266 tree found `zero_next_object_id()` is an atomic process-wide increment with a fatal overflow guard and no reset/write elsewhere, and texture initialization assigns its result. That supports uniqueness for that source build, but the historical M3B event bundle is not bound to that exact source/ELF, so the reducer does not promote the ID to a generation without run-bound provenance. `T2_MEMWATCH_SAMPLE` has no monotonic timestamp in its current schema, so it is retained as `unjoined_no_timestamp`; `present_serial` is explicitly unobserved when the source record does not emit one. Kernel warning deltas stay system-wide, not process-attributed. Fileback mirror, EGL/GBM/display backing, movable-page occupancy, pinned CMA and Mali-private physical bytes remain `unknown` unless supplied by evidence. DMA-BUF exporter size is not converted to CMA bytes, and promotion is never inferred from this reducer.

Fail-closed checks include mixed run/process identity, reordered timeline timestamps, missing 64 MiB floor samples, incomplete M3B/owner rings, late ID280/ID288 pairs through the existing ledger replay, and malformed subresource counts. Unknown GPU completion and physical backing prevent promotion. Local input files are bounded, checked for stability during read, and SHA-256 tagged in CLI output.

## Verification and remaining work

- Focused reducer/CLI fixtures: **12 passed**.
- Full tools suite: **425 passed**.
- `py_compile`, CLI `--help`, and `git diff --check` passed.
- The tracked `m3b-build256b-pair-20261022-01` directory contains only its README and compact `ab-summary.json`, not the raw owned log/timeline/CMA bundle. This receipt records tool behavior, **not** a newly measured peak or memory saving.
- Next H3 step: run the reducer only when a complete matching owned bundle is available; then use the separate ledgers to choose one evidence-backed M4-C retention candidate. Do not launch Lamentum from high `CmaFree` alone; `T2_STORAGE_MARGIN_MIB` remains unset.