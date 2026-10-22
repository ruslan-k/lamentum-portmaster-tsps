# Build 249: timestamped storage-lifetime diagnostic

**Status: NOT PLAYABLE.** This run did not reach the menu or gameplay and produced no valid FPS measurement. The 96 MiB safety floor remained unchanged; New Game was not entered.

- Device: TSPS/SpruceOS, boot `66203f22-4ac8-4a2a-a47c-cddc253d3bda`.
- Owned run: `cc013fc9-af26-4e2f-84b6-38e5c7af35dd`.
- Runtime: `build-249/lamentum-nextos`, AArch64 ELF64, GLIBC requirements no higher than 2.27; SHA-256 `0e62238c69c36e9fbd49669d5c062c0449ee56c2624b44acf37461c206cd588b`.
- Previous build-248 preserved on device as `.before-249`, SHA-256 `1462d92791748650e951cd9256d1fee712213b18bc08e25b8eb22ab0b4aaa73a`.
- Launcher SHA-256 `f32204ff1b271dd66e38f79573f75c6f562af49174ea436e81dd9417dba1354a`; helper SHA-256 `abe8e4847b18a750c0796af33d887cf43714126c9751ccdc8236715cb752401a`.

## Run outcome

- Configuration: `LC2_LIFE_EVENTS=1`, `LC2_MENU_LEDGER=1`, `T2_MEMORY_FLOOR_MIB=96`, `T2_TEXTURE_BUDGET_MIB=300`, strict GL error handling.
- The owned log contains **3** `NVN_PRESENT_PIXELS` records and **0** `LC2_MENU_EVENT` records.
- First-present sample: `t-ns=6558465654561`, frame 1, `MemAvailable=119140 KiB`, `CmaFree=17512 KiB`, budget-live `112325632` bytes, 91 live textures.
- Stop: `STOP status=T2_MEMORY_FLOOR`; the configured floor was 96 MiB. At the stop sample, the runtime reported 68 MiB available and 1983 MiB swap free; the pre-stop record has the exact sample `available-kib=70304`, `swap-free-kib=2031356`, `t-ns=6558723780460`. OOM evidence is empty.
- No world, player input, sound, saves, or performance/FPS was verified.

## M2A storage journal

The run emitted 116 timestamped `LC2_TEXTURE_PAIR` records (113 `recorded`, 3 `no-live-gl-storage`, no overflow), 163 storage events (50 extends), and 24 delete events; all event caps reported zero overflow. The cumulative pair-event payload sums were:

- guest/charged payload: `113902592` bytes (108.626 MiB)
- GL texture storage: `230831408` bytes (220.138 MiB)
- GL renderbuffer storage: `11980800` bytes (11.426 MiB)

The floor callback's non-blocking GL-lock attempt returned `EBUSY` (`lock-rc=16`), so it did not emit a direct `LC2_TEXTURE_LIVE_SET` snapshot. Replaying the timestamped storage create/extend/delete events through the floor timestamp reconstructs **89 live GL-storage records**: 87 textures totaling `224539952` bytes and 2 renderbuffers totaling `11980800` bytes. The reconstructed total, `236520752` bytes, matches the subsequent `LC2_LIFE_SUMMARY` (`live=89`, `tex-live=87`, `rb-live=2`, `retained=236520752`) exactly. This validates the per-generation GL-storage journal for this run; it does not establish physical GPU residency or completion.

The exact per-object T2 budget live value at the floor is still not closed: budget subtracts are not timestamped per NVN object, and the lock-busy path did not read the independent T2 budget counter. That is the next instrumentation gap. The first-present budget sample is not the same timestamp as the stop sample.

## Cleanup and evidence caveats

- A fresh post-run readback verified the original boot ID, `MainUI` PID/starttime `19116/656003`, no game process, CPU online mask `4-7`, and CPU0–3 restored to `online=0`, mode `0444`. Build 249 and the build-248 backup hashes were read back successfully.
- KMS capture after an agent-injected Back wake shows the SpruceOS home UI, not Lamentum. See `screen-cleanup-receipt.json` and `wake-back.json`.
- The raw append-only log's SHA-256 is `7829a74249b98ba21abf301a30dd17333811121c9ce0530f9b8f0fd0ecb774e8` (662073 bytes); it remains local-only. Raw screenshots and kernel dumps also remain local-only.
- The uncommitted generated `cleanup.json` snapshot parser used an unanchored `STOP status=` search, so its `stops` field falsely classifies `LC2_MENU_LEDGER_PRESTOP status=gl-lock-unavailable` as a second runtime stop. `run-outcome-receipt.json` records the correction: the actual owned log has only `STOP status=T2_MEMORY_FLOOR`; the false positive is a parser defect, not a runtime termination. The global `before.frame=8` also came from the previous append-only log generation; the owned current-run log has 3 presents. Both parser issues need correction before the next evidence run.
- `/proc/pressure/memory` was unavailable (`psi_memory=null`).

Compact receipts: `device-baseline.json`, `expected-run.json`, `run-outcome-receipt.json`, `device-post-run.json`, and `screen-cleanup-receipt.json`. The complete `device_principal_test.py` output and raw artifacts remain local-only.
