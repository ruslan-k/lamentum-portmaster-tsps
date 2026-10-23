# K1-F continuation — S launcher readback and fresh D hold (2026-10-23)

## S result: `STAGED_READBACK_VERIFIED_NOT_RUN`

The candidate-specific launcher was transferred only into the hidden, non-autostart candidate directory. It was first copied as `Lamentum.sh.tmp`, read back and hash-checked, then renamed within the same directory and `sync`ed. Final target readback at `12:51:43.062604Z` found exactly three candidate files and no temporary file:

- `Lamentum.sh`: 1,773 bytes, SHA-256 `1a90c4efc55074d2d6ae4ac51134522e1cc7ac33cca6025ccb14d269715c18a7`, mode `0777` on FAT, executable;
- `lamentum-nextos`: 2,203,096 bytes, SHA-256 `c46714403f22074d92710192d1164cfe0b7a4f62f1a4890ffb7a1e224c542332`;
- `run_identity.py`: 8,310 bytes, SHA-256 `abe8e4847b18a750c0796af33d887cf43714126c9751ccdc8236715cb752401a`.

The root menu launcher remained the sole `Lamentum.sh` in `/mnt/SDCARD/Roms/PORTS/`, unchanged at SHA-256 `f32204ff1b271dd66e38f79573f75c6f562af49174ea436e81dd9417dba1354a`; active build259 remained SHA-256 `d72e2f69afa16dd5b846950f3fba80bc9926edcab9b2d45c57ed23faa14b9066`. The post-stage gate confirmed MainUI `2369/1079`, principal `2196/1023`, no game, no pending principal command, no candidate-path FD owner, and no blocking process-scan errors. SD free space was `3,320,807,424` bytes. Rollback is limited to removing this new hidden candidate launcher; no active file was overwritten.

The launcher stays inert and does not write CPU/sysfs settings. It pins the approved floor/cap and strict/synchronous/default-off flags, uses a 30-second internal probe bound, and does not assign a storage margin. It is not a PortMaster root menu entry. No game was started and no safety guard was relaxed.

## Fresh complete D pair after staging

Two read-only snapshots on the unchanged boot `15b97fe4-5c48-412c-ba39-92efb1823286`, kernel `5.15.147`, at `12:52:30.558321Z→12:52:56.246752Z` were both complete; the comparator returned `comparison_status=complete`, pair `status=ok`. MainUI PID/starttime/executable, MainUI DMA-FD set and installed-runtime identity were unchanged; both snapshots listed no game process.

- `CmaTotal=131,072 KiB`; `CmaFree=792→1,332 KiB`; `MemAvailable=669,760→669,572 KiB`; `Cached=573,868→572,668 KiB`; `SwapFree=2,065,116 KiB` unchanged.
- `nr_free_cma=198→333`; CMA allocation counters stayed `success/fail=8/0`. The free `MIGRATE_CMA` histogram summed 195 then 334 pages, a −3/+1 page discrepancy against sequential `nr_free_cma` reads. Both histograms had **zero free CMA blocks at orders 7–10** (indeed no free CMA blocks above order 4).
- DMA zone reported 32,768 CMA pages; `pages_free=1,706→1,959`, with unchanged `min/low/high=991/1,238/1,485` pages. The ordinary `pgmigrate_success/fail` counters moved `+233/+9`; these are global counters, not CMA-owner evidence. `pgfault_delta=119,568`, `pgmajfault=0`, and swap-in/out deltas were zero.
- Six global DMA-BUFs were again `system` exporter (inodes 1,3,4,5,6,7), matching the K1-F inventory. Exporter labels/sizes do not identify private Mali allocations or CMA backing.

A target-side dmesg filter at `12:53:44.010442Z` returned successfully with **0** page-allocation, OOM, CMA-failure or Mali-OOM matches. `cma_alloc_fail` also remained zero. This is no failure evidence in this interval, not proof that all allocations succeed.

## CMA variability: separate observations, no leak or recovery claim

Identity-qualified same-boot readings include the earlier high pair (`130,412/130,412 KiB` before the ROMFS read), the post-read pair (`532→576 KiB`), the K1-F pair (`608/608 KiB` at 12:11), and this post-stage D pair (`792→1,332 KiB` at 12:52). A pre-transfer S-check singleton read `3,244 KiB` without recording its capture timestamp; the post-stage S readback singleton was `700 KiB`, and the later process-census singleton was `1,996 KiB` at `13:11:28.910289Z`. The singletons are not paired deltas and are not used to infer a trend or recovery.

`CmaTotal-CmaFree` is non-free pool capacity—not pinned-memory attribution. `/proc/pagetypeinfo` gives free CMA blocks and pageblock migration types, not active movable occupants. `CONFIG_PAGE_OWNER` and `CONFIG_CMA_DEBUGFS` are unavailable on this firmware; debugfs/tracefs are not mounted. The visible system-exporter buffers are platform-owned; K1-D classifies the generic system-heap path, but private Kbase allocations remain unknown. Fragmentation is evidenced by no free order-7+ CMA block; this does not prove a specific request failed. No cause for the large same-boot swing is established.

## Updated process-census code check

`tools/cma_readonly_snapshot.py` now labels its result `sequential_non_atomic`, validates PID/starttime and executable identity before/after scanning, counts ENOENT/ESRCH only as transient when the PID directory is confirmed gone, and treats EACCES, persistent errors and PID reuse as partial/HOLD. It reports principal identity and pending-command state separately from MainUI/game identity.

A post-change target snapshot at `13:11:28.910289Z` was complete: one MainUI `2369/1079`, one principal `2196/1023`, no game or pending command, one confirmed transient exit race, zero persistent read errors and zero PID reuse. The process-identity gate was ready. Its single `CmaFree=1,996 KiB` gauge is not a D pair or a launch gate.

Positive/negative host fixtures cover stable identities, an exited-PID ENOENT race, live-path EACCES/persistent ENOENT, PID reuse, missing principal, game present, pending command and non-atomic labeling. The focused read-only tests pass **27/27**, including confirmed disappearance during `/proc/PID/exe` lookup; the full tools suite passes **413/413**.

**Runtime decision: `HOLD_RUNTIME`.** The fresh pair has at most `1,332 KiB` free CMA and zero order-7+ blocks; the GL/DMA request classes and uncertainty reserve are still unqualified. There is no justified positive class-specific reserve. `T2_STORAGE_MARGIN_MIB` remains unset. No game launch, cache reclaim, compaction, reboot, process termination or kernel-setting change was performed.

Raw D snapshots/comparison remain local-only under Hermes scratch; their SHA-256 values are in `summary.json`.
