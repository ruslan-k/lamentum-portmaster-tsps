# H2a alias-generation diagnostic and D0 preflight — 2026-10-23

## Result

The per-object alias-generation telemetry passes host and target-CPU fixtures. The fresh read-only D0 preflight is complete and stable, but **the game launch remains HOLD_RUNTIME**: the existing launcher has no `T2_STORAGE_MARGIN_MIB`, and a reviewed D-policy reserve is not established. No game was launched, installed, or modified in this phase.

## Change under test

- `lc2_life_event` now tracks `alias_views` per `(share_group, GLuint, kind, object_generation)` while retaining the global aggregate. `zero_texture_storage` snapshots the diagnostic generation at publish and supplies it on texture/renderbuffer join and release.
- Missing/stale generations and per-object underflow increment `overflow`; an old-generation release cannot decrement a reused GLuint. Delete records include `alias-views`; `delete_with_views` is raised when caller or ledger sees views.
- This is observation only. `delete_key` still retires the logical record and subtracts nominal `retained_bytes`; it does not prove physical retention or completion and does not change runtime deletion/admission policy.

Current source identities: 390 C/C++ files, source-tree SHA-256 `3fcc9e78155ecdfd71507e860c5120d313a6a2d81967eed2ece572215cf38689`; adapter overlay SHA-256 `5ab2d36f5dcb1fdc275bfcaa55b9be8cfcc2dace10044bc9c932f5083a0dee62`. The inventory remains 77 sites: 12 `wrapped+unmeasured`, 65 `unknown`.

## Verification

- `test_life_events`: **11/11**; lifetime core: **7/7**.
- Full host suite with required zero-storage caller test enabled: **405/405**, zero skips.
- The source-bound host fixture compiles the complete `zero_texture_storage.h` and current `lc2_life_events.h`; it checks texture and renderbuffer owner generation, join/release, stale-generation refusal, and underflow. Required mode rejects a missing adapter source instead of silently skipping.
- Patch bytes match `git diff --binary` from the pinned adapter source. The overlay applies cleanly to the local native/framework baseline. The checked inventory report retains all 77 callsites.

## Target CPU fixture (not a game launch)

Pinned container `pmjs-arm64-spruce-local:20261002-gcc10` produced ELF64 PIE, Build ID `606078e973a3252f53d9afca2e40e30e7270c12b`, SHA-256 `d6b0c54d050dc7c8da7007f2f1ae3dffb820b10b0aa669e03b4fc8457ada02dc`, maximum GLIBC 2.17.

On Longan/SpruceOS (AArch64, firmware 1.0.1, kernel 5.15.147), the fixture exited **0**. It exercised a color-texture join/release and a depth-renderbuffer join/release. The temporary device copy’s SHA-256 matched; the file was removed and its absence verified. Post-run read-only checks showed one MainUI, zero game processes, CPU online mask `4-7`, no pending principal command, and no change in `CmaFree`. This proves target CPU logic/ABI only—not GL execution, physical backing, display, input, audio, gameplay, or FPS.

## Fresh D0 read-only preflight

Two complete snapshots on boot `15b97fe4-5c48-412c-ba39-92efb1823286` were captured at **2026-10-23 13:12:08 and 13:12:34 +04**, 25.683 s apart. Device identity: `allwinner,a523` / `arm,sun55iw3p1`, firmware 1.0.1, kernel 5.15.147.

- `CmaFree`: **130,412 KiB** in both snapshots; `nr_free_cma`: **32,603**.
- `MemAvailable`: **701,032 → 701,152 KiB**; `SwapFree`: **2,065,884 KiB** unchanged.
- CMA alloc success/fail counters: **8/0** unchanged. No deltas in major faults, swap I/O, compaction, or migration; minor-fault delta 8,318.
- CMA order histogram unchanged: 31 blocks at order 10; one each at orders 9, 8, 6, 4, and 3; zero at other reported orders.
- MainUI identity and its DMA-FD set were stable; process inventory complete. Filtered dmesg showed no CMA allocation/OOM/page-allocation warning (only boot-time CMA reservation and memory summary).
- CPU online `4-7`; no pending `/tmp/cmd_to_run.sh`. Installed `Lamentum.sh` SHA-256 `f32204ff1b271dd66e38f79573f75c6f562af49174ea436e81dd9417dba1354a` and `run_identity.py` SHA-256 `abe8e4847b18a750c0796af33d887cf43714126c9751ccdc8236715cb752401a` match the repository; installed runtime remains build259, SHA-256 `d72e2f69afa16dd5b846950f3fba80bc9926edcab9b2d45c57ed23faa14b9066`.

These are stable allocator observations, not proof that a title allocation will succeed or that Mali backing is reclaimable. The launcher still does not provide `T2_STORAGE_MARGIN_MIB`. Per roadmap §15, D-policy must map request classes and justify a reserve plus uncertainty; the high idle CMA pair alone is not launch clearance. Therefore no game launch was attempted and no safety limit was changed.

## Next

The first source-only request-class map is now recorded in [the D-policy receipt](../d-policy-typed-memory-classes-2026-10-23/README.md). It distinguishes GL payload intent, CPU scratch and combined requests, but does not prove physical backing or peak overlap. Before any one-run margin or runtime launch, exact firmware-backed class/overlap evidence and explicit approval for the reviewed value are required; then take another fresh preflight and use only the Spruce principal flow. New Game remains unauthorized; no gameplay or 30 FPS result exists.
