# Build251 M3-A1 device A/B — 2026-10-22

**Result: INCONCLUSIVE; keep `LC2_BC_STRIPE_MEDIUM` default OFF.** The feature's owner-105 staging path changed as intended and the three ON runs show a repeatable first-present memory/swap signal. All six runs nevertheless stopped at `T2_MEMORY_FLOOR` with zero menu events. The baseline has one owned live KMS publisher-splash image; there is no candidate image, so pixel parity is unverified. This is not a playable-port or FPS result.

## Controlled matrix

Same installed build251 on the same boot, no input, strict GL, floor 96 MiB, texture cap 300 MiB. Arms alternated OFF/ON/OFF/ON/OFF/ON; only `LC2_BC_STRIPE_MEDIUM` changed. Full run UUIDs, raw-log hashes, per-arm `/proc` samples, STOP, errors, cleanup and replay classifications are in [`ab-summary.json`](ab-summary.json).

| Pair | OFF → ON | First-present Δ candidate−baseline (KiB): available / CMA / swap-free / VmRSS / VmSwap | Floor Δ (KiB): available / swap-free | Presents OFF→ON |
| --- | --- | --- | --- | ---: |
| 1 | `6d57acb9-4008-43a5-a121-0a32fcaca950` → `a90be04e-66d8-42cd-acbf-6bc97fc0abb5` | `+23520 / +4772 / +8244 / -35652 / -3348` | `+700 / +35640` | 11→17 |
| 2 | `320c8488-7127-4edd-ba85-024b901494ad` → `9c1e2d42-527a-4352-b7d3-e5a42083a505` | `+25936 / +1992 / +37876 / -7240 / -31560` | `-5452 / +42424` | 15→11 |
| 3 | `d11d7752-81f9-4c34-bf06-530d4bad2026` → `aa167dd9-c698-4828-a17c-14ea2f6c8b76` | `+15572 / -840 / +7680 / -15488 / -8480` | `-1400 / +1368` | 11→11 |

All six arms reached `T2_MEMORY_FLOOR`; none reached the menu. Every run had zero counted GL-error markers, no owned OOM evidence and `cleanup_errors=[]`. The three ON arms retained more `SwapFree` at first present and at the floor, but still lost a median **39,880 KiB** of `SwapFree` from prelaunch to the floor. `MemAvailable` at the floor was lower in two of three ON/OFF pairs. The observed swap use is not zero, and the runs do not demonstrate safe menu headroom. Presentation counts are not FPS.

## What changed, what did not

For BC3 owner 105 (`1920x1080`, format `0x44`), OFF recorded full initialize/refresh staging of **10,368,000 requested overlapping bytes per upload**; ON recorded striped allocation/refresh of **1,228,800 bytes** with resolution preserved. The largest known scratch request across these logs changed from **64,800,000** to **2,304,000 bytes**. These are requested CPU-buffer bounds, not measured RSS, `MemAvailable`, swap, or Mali residency. The matching first-present T2 budget-live value was `112325632` bytes in every main matrix run; final floor content/live-byte counts varied as runs stopped at different progress points.

The per-ID budget/pair replay reconciled only two runs (`baseline-01`, `candidate-02`). Four fail closed because one live budget owner is absent from the texture-pair journal: id `288` in `candidate-01` and `baseline-02`, id `280` in `baseline-03` and `candidate-03`. Each arm has 119 pair lines and zero pair/budget-event overflow; the missing coverage is unresolved, not evidence of overflow or a physical leak.

## Live image and cleanup

- Baseline run `3287a37d-4e62-4817-9b4c-3e00d4b2e393`: KMS capture at observed process elapsed `10.2949 s`, while PID `10676` / starttime `1303489` matched both before and after. Image: 1280×720, 25,857 bytes, SHA-256 `b17fb34f4046411d506ae9e0ed6811aaff123c518aae61c786c79db15118b185`. Visually it shows the **NEON DOCTRINE publisher splash**, not the Lamentum menu or world.
- Candidate run `7f7d6e6d-6465-4768-b842-1d830b5bef9b`: no candidate image. At the scheduled capture the owned `/proc/11805/stat` was already gone; no pixel comparison was made.
- After testing, one agent-injected Back (100 ms; not a physical user press) woke the idle clock overlay. Fresh KMS then showed the awake SpruceOS MainUI home screen, not Lamentum. MainUI PID/starttime `12165/1311172` remained up; game processes were absent; CPU mask was `4-7`; CPU0–3 remained offline, mode `0444`. Cleanup screenshot SHA-256 is recorded in `ab-summary.json`; PNGs are local-only.

Several earlier live-capture wrapper trials are retained locally but excluded from the A/B data; their run UUIDs and specific host-tooling/capture failures are listed in `ab-summary.json`. No product/runtime source was changed during this experiment. Build251 remains installed and its medium-stripe switch remains opt-in.

## Next gate

Proceed to M3-B: add a bounded, owner-qualified pre-first-present memory waterfall and an instrumentation-OFF overhead arm on the same build, following the current [roadmap §76](../../docs/performance-roadmap-30fps.md#76-build251-reassessment-evidence-led-headroom-first-playable-scene-then-real-30-fps-2026-10-22). Keep the 96 MiB floor and 300 MiB cap; do not enter New Game until the menu safety gate passes.

Raw `latest.log` files and KMS PNGs remain local-only. The published receipt contains run identities, hashes and compact metrics, not raw captures.
