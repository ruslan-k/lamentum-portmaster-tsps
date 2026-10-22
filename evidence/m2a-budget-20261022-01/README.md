# Build250: per-object budget replay at the TSPS safety stop

**Status: NOT PLAYABLE.** This no-input diagnostic did not reach the menu or gameplay and produced no valid FPS result. The 96 MiB floor and 300 MiB texture cap were unchanged; New Game was not entered.

- Owned run: `40d57167-d5b1-4071-9bdf-a3b2dd028a92`; boot `66203f22-4ac8-4a2a-a47c-cddc253d3bda`; runtime PID/starttime `23644/851447`.
- Runtime: build250 AArch64 ELF64, GLIBC requirements 2.17/2.27; SHA-256 `fd83556cd52776f4371a1644e9d013cfcb317275d14e907c331f8f2ec7cbd74d`.
- The runtime patch SHA is `9cbdaa35d6a1dea783a29c3086251fa0731ac769e136072a38175f61d01df175`. Build249 was preserved on-device as `.before-250` (SHA-256 `0e62238c69c36e9fbd49669d5c062c0449ee56c2624b44acf37461c206cd588b`).
- Run flags: `LC2_LIFE_EVENTS=1`, `LC2_MENU_LEDGER=1`, `T2_MEMORY_FLOOR_MIB=96`, `T2_TEXTURE_BUDGET_MIB=300`, strict GL; no game input.

## Run outcome and memory

The owned log contains **5** `NVN_PRESENT_PIXELS` records and **0** `LC2_MENU_EVENT` records, then the sole owned stop `STOP status=T2_MEMORY_FLOOR`. The floor check measured `MemAvailable=97580 KiB` (95 MiB reported against floor96) and `SwapFree=1988100 KiB`. Prelaunch `SwapFree` was `2034520 KiB`; swap was consumed, so the no-swap target is unmet. No OOM evidence was found.

At first present (frame1, 6796 ms), `MemAvailable=144596 KiB`, `CmaFree=8220 KiB`, and `budget-live=112325632` B. `/proc/pressure/memory` was unavailable (`null`).

## Same-run budget and GL-storage replay

The T2 journal emitted 141 events: 117 adds totalling `116851712` B and 24 subtracts totalling `1572864` B, with zero event overflow. The nonblocking floor snapshot recorded `115278848` B live across 93 IDs. The tested `tools/ledger_bases.py:replay_texture_budget` reducer matched the snapshot and per-ID pair charges; the separate per-ID comparison found zero guest-vs-charge mismatches and zero missing pairs.

Three live charged IDs (`46`, `51`, `52`) have `no-live-gl-storage` status (1x1, format `0x25`); there are no live GL owners without a budget owner. Timestamped GL storage replay yields 90 live records: 88 textures / `232834352` B and 2 renderbuffers / `11980800` B, total `244815152` B. It matches `LC2_LIFE_SUMMARY` exactly; 164 storage events and 24 deletes, with zero reported overflow.

The floor check was at `t-ns=8524495203769`; the independent budget sample was 13208 ns later. No budget or GL-storage events occurred in that bracket. The direct GL live-pair snapshot still missed the mutex (`EBUSY=16`), so the GL set is reconstructed from the bounded journal, not a blocking snapshot. These are declared storage bytes—not proof of physical Mali residency, unique physical backing, or GPU completion. Share-group identity remains unverified. The legacy cumulative `tex-guest` summary has a different scope and is not substituted for this live per-object join.

## Cleanup and verification

- A fresh SSH readback verified build250 and its build249 backup hashes, no game process, the original boot ID, and CPU0–3 restored to `online=0`, mode `0444` with online mask `4-7`.
- The first KMS capture showed SpruceOS's idle clock overlay. After an explicitly agent-injected Back wake, KMS showed the awake SpruceOS home UI—not Lamentum. See `screen-cleanup-receipt.json` and `wake-back.json`.
- Run-scoped parsing now reports the current UUID's 5 presentations and sole T2 floor stop. The prelaunch log fields are labeled with the prior build249 UUID and are not counted for build250.
- Host suite: **280 tests passed**. The pinned target-compatible build and ELF/GLIBC checks passed.

No menu, world, gameplay input, sound, save/load, no-swap operation, or 30-FPS gameplay window was verified. Do not enter New Game until the menu safety gate passes. Next: choose one evidence-backed, quality-neutral first-present memory reduction path; lossy transcoding or render-resolution changes still need explicit quality acceptance.

Compact receipts include `expected-run.json`, `cleanup.json`, `before.json`, `device-baseline.json`, `device-post-run.json`, `budget-replay-receipt.json`, `screen-cleanup-receipt.json`, and `wake-back.json`. Raw `latest.log` (706659 bytes; SHA-256 `4f7233077f4dccd0b5fbd5b2972891eda5970f809ed661cbf3461dc2a1a896d2`), kernel captures, and PNGs remain local-only.
