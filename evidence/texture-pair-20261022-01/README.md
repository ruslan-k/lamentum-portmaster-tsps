# Build-248 M1 texture-pair diagnostic

**Verdict: NOT PLAYABLE.** This was a bounded, no-input memory diagnostic; it did not enter New Game or establish a scene, controls, audio, save/load, or gameplay FPS.

## Run identity and setup

- Run UUID: `fcb27ba2-5d5a-49be-95d7-5e13072c8ede`; boot ID: `66203f22-4ac8-4a2a-a47c-cddc253d3bda`.
- Build-248 AArch64 runtime SHA-256: `1462d92791748650e951cd9256d1fee712213b18bc08e25b8eb22ab0b4aaa73a`; launcher: `f32204ff1b271dd66e38f79573f75c6f562af49174ea436e81dd9417dba1354a`; helper: `abe8e4847b18a750c0796af33d887cf43714126c9751ccdc8236715cb752401a`.
- Runtime backup `.before-248` was read back as build247 SHA-256 `ecef4ba2075946095e69120137366850c41184d26e3e82c995cdd98995bd6575`.
- Run flags: `LC2_LIFE_EVENTS=1`, `LC2_MENU_LEDGER=1`, strict GL, texture budget 300 MiB, memory floor 96 MiB; no input was sent during the runtime.
- Host checks: 273 tests passed; cross-build succeeded against the pinned container and 435-file baseline. The source/test patch is in commit `6773743664e4e031ed5b2f68e87d2931bd825f59`.

## Device result

The runtime identity was verified on device and it produced 8 `NVN_PRESENT_PIXELS` records. There were 0 `LC2_MENU_EVENT` records. The normal safety guard stopped it with `T2_MEMORY_FLOOR`; the watchdog reported 95 MiB available against the 96 MiB floor, with 1954 MiB swap free. The owned run receipt records no OOM evidence, no host kill, no observer/identity errors, and no cleanup errors.

The menu ledger recorded:

- `gl-init`: 0 ms, available 592,924 KiB, `CmaFree` 123,636 KiB.
- `first-present`: 6,574 ms / frame 1, available 130,156 KiB, `CmaFree` 3,504 KiB, budget-live 112,325,632 B (107.12 MiB), 91 live textures.
- `interval`: 7,603 ms / frame 8, available 77,908 KiB, `CmaFree` 11,764 KiB, budget-live 115,278,848 B (109.94 MiB), 93 live textures.

The 250 ms memory-watch stop sample and the asynchronous menu-ledger samples do not agree on `MemAvailable`; they must not be treated as one timestamp. This is one reason the roadmap's timestamped M2A timeline remains open.

## Per-texture observations

The opt-in lifetime ledger emitted 117 `phase=initialize` pair lines: 114 had a live GL storage record, 3 reported `no-live-gl-storage`, and pair overflow was zero. Cumulative event totals—not a live-set measurement—were:

- guest/charge payload: 116,851,712 B (111.44 MiB);
- declared GL texture storage: 239,125,808 B (228.05 MiB);
- declared GL renderbuffer storage: 11,980,800 B (11.43 MiB).

In 69/117 events, declared GL texture+renderbuffer bytes exceeded the charge; 68 exceeded 2× and 3 exceeded 4×. Examples: NVN id 61, 800×1500, format `0x42`, 614,400 B charged versus 4,800,000 B declared GL storage (7.812×); id 96, 1000×800, `0x42`, 524,288 versus 3,200,000 B (6.104×); id 99, 1920×1080, `0x42`, 1,474,560 versus 8,294,400 B (5.625×). These are wrapper-declared payloads, not measured Mali residency.

The lifetime summary reports 24 deletes and 24 GL-name reuses. Since the pair records lack timestamps and complete object/storage-generation, delete, alias, and retirement joins, the event sums cannot be compared as if they were a simultaneous live set. The remaining budget-versus-guest residual is **unresolved**, not evidence of a leak or a physical-memory conversion factor. Share-group identity remains unverified and GPU completion unobserved.

## Cleanup and screen

Post-run read-back verified the same boot, no game process, MainUI PID/starttime `13703/421845`, CPU mask `4-7`, and CPU0–3 `online=0`, mode `0444`. The runtime hash is still build248; build247 remains at `.before-248`.

The first cleanup KMS capture showed the idle clock overlay. One 100 ms agent-injected `Back` event (key 304, explicitly **not** a physical human press) woke SpruceOS; the subsequent 1280×720 KMS capture showed the SpruceOS MainUI home, not Lamentum. Screenshot SHA-256: `37aa625c1c800d3535fad8bf44563c3fe242ba9ba045f46ea1eac119f143ba66`.

## Evidence publication policy

Committed receipts: `device-baseline.json`, `expected-run.json`, `cleanup.json`, `device-post-run.json`, `wake-back.json`, `mainui-after-wake-snapshot.json`, and `screen-cleanup-receipt.json`. Raw `latest.log`, kernel dumps, and PNGs stay local-only. The local `latest.log` is 581,148 B, SHA-256 `74215f9b995ec3fe1cbc12e469dc613c522625380e25ee31a6a002442051979c`.

## Next gate

Finish M2A: add timestamped, generation-qualified per-object joins and a same-time live-set total, including deletes/name reuse; capture the missing early allocation/PSI landmarks. Do not lower the 96 MiB floor or enter New Game until menu headroom passes the owner's safety gate. Then address the measured memory wall before first-world and gameplay-FPS work.
