# CMA recovery experiment — preflight and authorization gate

**Historical preflight capture before the observed boot transition.** At this capture, no reboot had occurred and explicit operator authorization was pending. A later boot-ID change and post-boot samples are recorded in [the observation receipt](../cma-reboot-observation-2026-10-23/README.md). The agent did not issue a reboot command; who initiated the transition remains unconfirmed.

## Pre-reboot checks (2026-10-23 13:43–13:47 UTC)

- Recovery access works now: `/home/ruslan/tsps_ssh_key.sh` returned `ok`; `ssh tsps uname -m` returned `aarch64`. Target boot ID is `15b97fe4-5c48-412c-ba39-92efb1823286`, kernel `5.15.147`, firmware `1.0.1`.
- The boot path contains executable `/etc/init.d/S50sshd` and `S65ssh_keys`; `/etc/init.d/rcS` iterates `/etc/init.d/S??* start`. Three SSH daemon processes were present. This supports recovery by SSH, but *post-reboot reconnection has not been tested*.
- Immediately before the experiment, the read-only process census was complete and sequential/non-atomic: MainUI `2369/1079`, principal `2196/1023`, no Lamentum process and no `/tmp/cmd_to_run.sh`; zero persistent errors and PID reuse, one confirmed process-exit race.
- A separate sequential scan of 180 `/proc` PIDs found no FD owner for the hidden candidate path; it recorded two confirmed transient races, no persistent errors or PID reuse.
- The candidate remains only at `/mnt/SDCARD/Roms/PORTS/lamentum-switch/.candidate-h2a-20261023/`; its three file hashes/modes match the expected launcher/ELF/helper. It is not a PortMaster root entry. The sole root `Lamentum.sh` hash and active build259 hash remain unchanged.
- Host-local rollback copies were created outside the repository and verified: active launcher SHA-256 `f32204ff…`, build259 SHA-256 `d72e2f69…`. Device files were not changed.

## Current allocator state

The complete single snapshot at `13:43:29.448Z` reported `CmaFree=2,008 KiB` of `131,072 KiB`. The free CMA histogram had orders 0–6 `[93,21,13,7,6,3,1]`, with no free order-7+ blocks. Its 499-page histogram sum differed from `nr_free_cma=502` by 3 pages; the difference is preserved, not normalized. Six global DMA-BUFs were `system` exporter. The separate filtered dmesg capture at `13:47:34.333Z` matched zero allocation/OOM/CMA/Mali warnings; `/proc/pressure/memory` was unavailable. This is not a D pair or launch clearance.

## Planned procedure (preflight capture)

The planned sequence was one normal reboot followed by samples at device uptime 60, 300 and 900 seconds. A boot-ID transition was subsequently observed and the post-boot measurements are in the [observation receipt](../cma-reboot-observation-2026-10-23/README.md). The agent did not send a reboot command; the transition's initiator is unconfirmed. **Do not issue another reboot for this experiment.** No game launch is justified by the high post-boot `CmaFree`: `T2_STORAGE_MARGIN_MIB` remains unset and the independent class-specific reserve/D gate are still required.

No reboot, game launch, compaction, cache drop, kernel setting change, firmware change, or admission bypass was performed in this preparation. Machine-readable details and local backup paths are in `summary.json` (the backup binaries remain local-only under Hermes scratch).