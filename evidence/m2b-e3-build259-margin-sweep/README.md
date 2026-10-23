# Build259 M2B-E3 device margin sweep — 2026-10-23

## Result

After the user delegated margin selection (“Тестируй разные значения сам”), ran the same build259 through Spruce's principal flow with per-run `T2_STORAGE_MARGIN_MIB` values **64, 48, 32, 24 MiB**. The only per-arm change was the margin. Every run failed closed at `T2_STORAGE_ADMISSION`, reason `cmafree-margin`; none reached the menu. No New Game or in-run input was used. The 96 MiB floor, 300 MiB texture cap, strict GL setting, and default-off M3-B ring were unchanged. The launcher still has no margin default.

All four receipts are bound to build259 SHA-256 `d72e2f69afa16dd5b846950f3fba80bc9926edcab9b2d45c57ed23faa14b9066` on boot `66203f22-4ac8-4a2a-a47c-cddc253d3bda` (Linux 5.15.147, `sun55iw3`). Detailed machine-readable results: [ab-summary.json](ab-summary.json). Per-arm raw `latest.log`, kernel dumps, and `memory-timeline.raw.json` remain local and are not committed; cleanup screenshots also remain local.

| Margin | Run UUID | Admission checks (allowed/refused) | Refused request | At refusal: CmaFree / required CMA; MemAvailable | CmaFree after process exit | Timeline |
|---:|---|---:|---|---|---:|---|
| 64 MiB | `c11ee013-91bf-46c0-80d6-41ebd44b3a89` | 106 (105/1) | owner 61, scratch 5,400,000 B | 70,516 KiB / 72,508,864 B; 540,244 KiB | 97,380 KiB | 29 live / 31 total; incomplete, 0 dropped |
| 48 MiB | `8bc3f0cd-e245-4637-bdd5-5a81cc98f1e3` | 192 (191/1) | owner 77, scratch 10,368,000 B | 47,316 KiB / 60,699,648 B; 524,708 KiB | 88,436 KiB | 17 live / 19 total; complete, 0 dropped |
| 32 MiB | `c4157aca-ffd0-4738-a686-f80cf06b30ca` | 177 (176/1) | owner 0, GL 512,000 B | 30,520 KiB / 34,066,432 B; 509,188 KiB | 87,712 KiB | 16 live / 18 total; complete, 0 dropped |
| 24 MiB | `143d309a-cf1e-4df3-981c-b475ad69c895` | 193 (192/1) | owner 0, GL 8,294,400 B | 12,664 KiB / 33,460,224 B; 493,096 KiB | 14,244 KiB | 17 live / 19 total; complete, 0 dropped |

In every arm, `SwapFree` was unchanged from the run's before to after snapshot. The exact denial preceded the stop, and there were **zero** subsequent `LC2_GL_STORAGE_EVENT` lines. No new kernel OOM, `Killed process`, or page-allocation-failure warning appeared in any kernel delta. This demonstrates the typed fail-closed refusal path; it does **not** demonstrate safe gameplay or a reliable production margin.

## Safety stop

The margin24 arm's direct refusal sample had `CmaFree=12,664 KiB`; after exit it was 14,244 KiB and after a further 20-second idle read-only wait it remained only **15,384 KiB**. The earlier build256b warning recorded `free_cma=4,122` pages (16,488 KiB at 4 KiB/page). No new warning occurred, but current CMA free remained below that prior warning context. A later read-only `/proc` sample, at 4 KiB page size, showed `CmaTotal=131,072 KiB`, `CmaFree=15,416 KiB`, and `nr_free_cma=3,854` pages. Current vmstat counters were `cma_alloc_success=36`, `cma_alloc_fail=0`; they were not captured as a pre/post pair, so they do not attribute the change to this test. A separate 30 s idle pair with the same MainUI PID/build kept `CmaFree=15,456 KiB`, `nr_free_cma=3,864`, and the CMA success/fail counters unchanged. MainUI had FD 10 to `/dev/dma_heap/system` and four `system`-exporter DMA-BUF FDs (16,384 B and three 3,686,400 B buffers; 11,075,584 B total). This FD census does not prove those buffers occupy CMA or explain the drop. Debugfs DMA-buf, DMA-heap, CMA, and Mali accounting paths were absent; the retained/physical backing cause is **unknown**. The latest read-only preflight still showed `CmaFree=15,456 KiB` (`MemAvailable=686,396 KiB`, `SwapFree=2,033,604 KiB`), build259 installed, MainUI only, and no pending principal command.

For margin24, the 100 ms memory timeline fell from 87,604 KiB CmaFree at seq13 to 71,712 (seq14), 47,836 (seq15), and 17,248 (seq16), followed by the admission snapshot at 12,664 KiB. GL storage journal events occurred in that interval, including owners 58, 60, and 61; this is temporal correlation only, not proof that those logical payloads equal physical CMA consumption.

**Do not test below 24 MiB or launch again now.** Investigate CMA accounting/retention and wait for a safe read-only baseline before another device launch. Build259 remains installed with `.before-259` verified as the previous build256b (`27a2f9a8fcb00761ac6673937145929e675a75c641afde221dc01f96df39d771`). MainUI returned after every arm; the first cleanup capture showed the idle clock overlay, then a released 100 ms BACK restored the awake Spruce MainUI. Subsequent KMS cleanup captures showed the awake MainUI. CPU mask returned to `4-7`, CPUs 0–3 remained offline/mode `0444`, and no game or pending principal command remained.

## Not established

No menu event or presented frame was recorded in any arm. No-swap gameplay, a playable world, and ≥30 FPS remain unverified. `CmaFree` is an allocator metric, not proof of Mali residency or DMA-buf ownership.
