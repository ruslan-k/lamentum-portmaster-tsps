# CMA recovery experiment — preflight and authorization gate

**Status: prepared, not executed. No reboot has occurred.** This is a bounded recovery diagnosis for the temporary CMA runtime blocker; it does not classify the project as unachievable. Reboot execution awaits explicit operator authorization.

## Pre-reboot checks (2026-10-23 13:43–13:47 UTC)

- Recovery access works now: `/home/ruslan/tsps_ssh_key.sh` returned `ok`; `ssh tsps uname -m` returned `aarch64`. Target boot ID is `15b97fe4-5c48-412c-ba39-92efb1823286`, kernel `5.15.147`, firmware `1.0.1`.
- The boot path contains executable `/etc/init.d/S50sshd` and `S65ssh_keys`; `/etc/init.d/rcS` iterates `/etc/init.d/S??* start`. Three SSH daemon processes were present. This supports recovery by SSH, but *post-reboot reconnection has not been tested*.
- Immediately before the experiment, the read-only process census was complete and sequential/non-atomic: MainUI `2369/1079`, principal `2196/1023`, no Lamentum process and no `/tmp/cmd_to_run.sh`; zero persistent errors and PID reuse, one confirmed process-exit race.
- A separate sequential scan of 180 `/proc` PIDs found no FD owner for the hidden candidate path; it recorded two confirmed transient races, no persistent errors or PID reuse.
- The candidate remains only at `/mnt/SDCARD/Roms/PORTS/lamentum-switch/.candidate-h2a-20261023/`; its three file hashes/modes match the expected launcher/ELF/helper. It is not a PortMaster root entry. The sole root `Lamentum.sh` hash and active build259 hash remain unchanged.
- Host-local rollback copies were created outside the repository and verified: active launcher SHA-256 `f32204ff…`, build259 SHA-256 `d72e2f69…`. Device files were not changed.

## Current allocator state

The complete single snapshot at `13:43:29.448Z` reported `CmaFree=2,008 KiB` of `131,072 KiB`. The free CMA histogram had orders 0–6 `[93,21,13,7,6,3,1]`, with no free order-7+ blocks. Its 499-page histogram sum differed from `nr_free_cma=502` by 3 pages; the difference is preserved, not normalized. Six global DMA-BUFs were `system` exporter. The separate filtered dmesg capture at `13:47:34.333Z` matched zero allocation/OOM/CMA/Mali warnings; `/proc/pressure/memory` was unavailable. This is not a D pair or launch clearance.

## Experiment after authorization

1. Perform exactly one normal controlled reboot; no force flag and no other state changes.
2. Wait for SSH recovery and a changed boot ID. Save the first reachable sample, then identify the earliest complete stable snapshot with MainUI/principal identities, no game/pending command, buddy orders and DMA-BUF inventory.
3. Capture follow-ups at device uptime approximately 60, 300 and 900 seconds. Each record will include `CmaFree`, buddy/free-CMA orders, zoneinfo/vmstat, DMA-BUF inventory, process identities, memory PSI if exposed, and filtered kernel allocation/OOM/CMA/Mali warnings.
4. Compare within the new boot. Pageblock migration types and free-order histograms are not proof of active movable owners; DMA-BUF exporter/size is not proof of CMA backing. Label pinned/Mali-private ownership `unknown` unless directly supported.
5. Do not launch Lamentum merely because CMA rises. Keep `T2_STORAGE_MARGIN_MIB` unset; the complete D-preflight and independently justified positive class-specific reserve remain mandatory.

No reboot, game launch, compaction, cache drop, kernel setting change, firmware change, or admission bypass was performed in this preparation. Machine-readable details and local backup paths are in `summary.json` (the backup binaries remain local-only under Hermes scratch).