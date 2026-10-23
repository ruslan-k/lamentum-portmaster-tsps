# Build254 M3-B: first floor-snapshot OFF/ON pair

**Result:** the new one-shot floor snapshot was read back on TSPS in both arms, including the ring-ON run where the later GL-storage trylock failed. The wider memory waterfall is still incomplete: the periodic sampler dropped scheduled samples in both arms, and the ring still covers BC windows only. Both runs stopped safely at the 96 MiB floor before the menu; this is not gameplay or FPS evidence.

## Artifact and setup

- Source commit: `f3029b61522aeac0b99fc47b9ff80d23b573158f`.
- TSPS runtime: build254, SHA-256 `b6a84e4cd423cbbd88661502c53f1f6de81ab81d1de9c504700d289e96d417e1`.
- Backups retained: build253 at `.before-254`, SHA-256 `7acd58704b662184d4f2103d782d911b06c40e18fe7f4505f2753a06242bc6b9`; build251 at `.before-253`, SHA-256 `1bcb32a4bac2e1e30e4c64ab8bb5d8ddd58c3cc59363a785919991eac4ab6b78`.
- No input. Both arms used floor96, cap300, strict GL, `LC2_LIFE_EVENTS=1`, `LC2_MENU_LEDGER=1`, `LC2_M3B_MAX_EVENTS=64`, `LC2_BC_STRIPE_MEDIUM` unset/default-off, and the same 100 ms process timeline. Only `LC2_M3B_TIMELINE` changed (0/1).

## Exact floor snapshots

- **OFF** — run `f9868a42-8ccb-4ebc-9df7-72156ab0a151`: at `T2_MEMORY_FLOOR`, `MemAvailable=97,356 KiB`, `SwapFree=1,956,736 KiB`; snapshot bracketed the floor check from +56,667 ns to +211,584 ns (154,917 ns read duration), `CmaFree=720 KiB`, `VmRSS=699,520 KiB`, `VmSwap=67,032 KiB`. T2 live budget was 117,441,536 B across 119 charges. The GL live-set trylock succeeded.
- **ON** — run `47ed1738-f227-4668-99f6-374bb43c68d5`: at `T2_MEMORY_FLOOR`, `MemAvailable=86,388 KiB`, `SwapFree=1,984,232 KiB`; snapshot bracketed the floor check from +40,459 ns to +204,417 ns (163,958 ns read duration), `CmaFree=9,644 KiB`, `VmRSS=728,876 KiB`, `VmSwap=40,436 KiB`. T2 live budget was 109,618,176 B across 119 charges. The subsequent GL trylock failed (`lock-rc=16`), but `LC2_MENU_FLOOR_MEMORY` was already emitted with the full host snapshot.

The prelaunch-to-floor SwapFree decreases were 77,312 KiB OFF and 48,640 KiB ON; neither is no-swap. These are one sequential pair with different debug present-probe counts (15/17), different floor state, and incomplete periodic timelines; do not attribute their deltas to the ring.

## Largest recorded BC contributors

The ring reported 33/33 events (30 windows + 3 marks), with no incomplete/active/dropped/format-error event. Its largest windows were:

- Owner 92, 3600×3600: compressed source 14,745,600 B; requested RGBA 51,840,000 B + linear staging 12,960,000 B; 64,800,000 B requested overlap. Decode wall 527.8 ms; GL upload bracket 198.1 ms.
- Owner 81, 3600×2160: compressed source 9,216,000 B; requested RGBA 31,104,000 B + linear staging 7,776,000 B; 38,880,000 B requested overlap. Decode wall 317.4 ms; GL upload bracket 50.3 ms.

The OFF arm's floor live-set receipt reported 241,485,104 B unique declared GL texture payload + 11,980,800 B renderbuffer payload, versus 117,441,536 B in the T2 budget. Owners 92 and 81 accounted for 51,840,000 B and 31,104,000 B of declared texture payload. This is a reconciliation target only: share-group identity, GPU completion, driver allocation and physical Mali residency remain unverified. The ring still does not cover non-BC GL/EGL/buffer allocations.

Nearest 100 ms samples bracketed the long owner 81/92 windows and showed concurrent RSS rises, but are not exact event-time snapshots. The periodic timeline itself is `complete=false` in both arms: 3 missed samples OFF and 7 ON; maximum sample durations were 212.1 ms and 308.8 ms with only 4.35 ms and 4.13 ms of collector CPU. The cause of the long elapsed rows is unclassified. The exact floor snapshot is available despite that sidecar incompleteness.

## Cleanup and evidence limits

Both runs had zero menu events, no owned OOM and no cleanup errors. Post-run checks verified build254 installed, both backups intact, MainUI only, no game process, `/tmp/cmd_to_run.sh` absent, online mask `4-7`, and CPU0–3 offline with sysfs mode `0444`. KMS captures show the awake SpruceOS MainUI home; they are cleanup-only, not gameplay evidence.

Raw timelines and logs, and PNG captures, remain local-only and ignored. `ab-summary.json` is the compact committed receipt. The port remains **NOT PLAYABLE**; menu admission, no-swap operation, and gameplay 30 FPS remain unverified.