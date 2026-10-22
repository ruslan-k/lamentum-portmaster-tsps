# Build 253 M3-B: first same-build ring OFF/ON pair

**Result: inconclusive, and not a gameplay/FPS result.** Both no-input principal-flow runs stopped at the 96 MiB safety floor before the menu gate. The ring-on arm emitted a complete bounded set of BC allocation windows, but the sampler missed a short floor transient and the observer still omits non-BC allocation owners. No New Game or gameplay was entered.

## Setup and integrity

- Device: TSPS, AArch64, boot `66203f22-4ac8-4a2a-a47c-cddc253d3bda`.
- Installed runtime: build253, SHA-256 `7acd58704b662184d4f2103d782d911b06c40e18fe7f4505f2753a06242bc6b9`.
- Preserved build251 runtime backup: `lamentum-nextos.before-253`, SHA-256 `1bcb32a4bac2e1e30e4c64ab8bb5d8ddd58c3cc59363a785919991eac4ab6b78`. Launcher and paired helper hashes remained unchanged.
- Both arms used the same runtime and sampler, with no input, `T2_MEMORY_FLOOR_MIB=96`, `T2_TEXTURE_BUDGET_MIB=300`, strict GL (`COTM_GL_ERROR_IGNORE=0`), `LC2_LIFE_EVENTS=1`, `LC2_MENU_LEDGER=1`, `LC2_M3B_MAX_EVENTS=64`; `LC2_BC_STRIPE_MEDIUM` remained unset/default-off.
- Only arm difference: `LC2_M3B_TIMELINE=0` (OFF) versus `=1` (ON). The external process timeline was enabled in both (100 ms, at most 256 samples; sparse `smaps_rollup`).

## Device observations

- **OFF** — run `645c0df7-180f-4ef5-aa8c-8f99dc7c69b3`: 104 live samples, 106 total, timeline complete to process exit, zero dropped. No `LC2_M3B_*` records. First present was frame 1 at 128,752 KiB MemAvailable / 18,472 KiB CmaFree / 1,992,936 KiB SwapFree. At the floor check: 90,960 KiB available, 1,971,432 KiB SwapFree, 117,441,536 requested live texture bytes, 119 charges. SwapFree fell 62,208 KiB from prelaunch to floor.
- **ON** — run `774459c8-c3a0-4915-9d2c-0cd6406916a1`: 89 live samples, 91 total, timeline complete to process exit, zero dropped. The bounded ring reported 30/30 events (27 windows + 3 marks), no incomplete/active/dropped/format-error events. At the floor check: 84,140 KiB available, 2,015,460 KiB SwapFree, 112,329,728 requested live texture bytes, 116 charges. SwapFree fell 17,664 KiB from prelaunch to floor.
- The two arms are not a causal A/B result: OFF recorded 13 debug present-probe records and ON 2 before the same safety stop (not FPS), and exact floor conditions were not matched. Neither is an FPS measurement.

## Largest recorded BC owner

Owner 105, 1920×1080, format `0x44`: compressed source 2,949,120 B; requested RGBA 8,294,400 B plus linear staging 2,073,600 B; requested overlap peak 10,368,000 B. Full initialization decode wall time was 85.9 ms and its GL allocation/upload bracket 8.77 ms; refresh decode was 90.3 ms and GL upload 12.81 ms. These are requested bytes and wall-time brackets, not measured Mali residency or CPU-frame cost. Driver allocation, source-write generation, GPU completion/in-flight, stage-local GL error and physical Mali residency remain unknown/unobserved.

## Limitation exposed by the run

The ON sampler's nearest live sample was 64.8 ms before the floor and showed 124,384 KiB MemAvailable; the exact floor record showed 84,140 KiB, a 40,244 KiB gap. The floor-side ledger could not acquire the GL lock, so exact floor CMA/RSS/VmSwap were not captured. Thus `timeline.complete=true` means the bounded sampler ran through process exit; it does **not** prove that it captured the transient peak. The next M3-B step is a lock-free, one-shot floor snapshot (CmaFree and process RSS/VmSwap) and broader non-BC owner coverage before drawing memory-attribution conclusions.

## Cleanup and retained evidence

Both runs reported no cleanup errors; afterward the device had MainUI only, no game process, `/tmp/cmd_to_run.sh` absent, CPU mask `4-7`, and CPU0–3 offline with sysfs mode `0444`. The post-ON KMS capture first showed the idle clock; one released, agent-injected BACK (100 ms, **not physical input**) restored the awake MainUI home, then a second KMS capture verified it. These are cleanup screenshots only, not game screenshots.

`ab-summary.json` is the compact committed receipt. Raw `memory-timeline.raw.json`, `latest.log`, and KMS PNGs remain local-only and ignored by Git.