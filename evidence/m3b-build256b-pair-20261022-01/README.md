# Build256b M3-B OFF/ON: non-BC and depth windows captured, waterfall still partial

## Setup

- Commit: `07c2434a930a9873d0c790a1a7386f2cfb4fdbed`; PR #1 remains open.
- Runtime: build256b, SHA-256 `27a2f9a8fcb00761ac6673937145929e675a75c641afde221dc01f96df39d771`; AArch64 ELF64, GLIBC ≤2.27.
- Installed through the Spruce principal flow after preflight. Build254 was preserved at `.before-256b` (SHA-256 `b6a84e4cd423cbbd88661502c53f1f6de81ab81d1de9c504700d289e96d417e1`); build253 `.before-254` and build251 `.before-253` were read back unchanged. Postflight verified build256b still installed, MainUI only, no game, no pending principal command, CPU mask `4-7`, CPU0–3 offline/mode `0444`.
- Both were no-input runs with floor96, `T2_TEXTURE_BUDGET_MIB=300`, strict GL, `LC2_LIFE_EVENTS=1`, `LC2_MENU_LEDGER=1`, ring capacity64, identical 100 ms memory timeline, `LC2_BC_STRIPE_MEDIUM` unset, and `LC2_BC_INPLACE_DECODE` unset. Only `LC2_M3B_TIMELINE` changed (`0`/`1`).

## Device result

Both owned runs executed the exact build256b ELF, emitted `STOP status=T2_MEMORY_FLOOR`, had zero menu events and no cleanup errors. Neither reached the menu or gameplay. The OFF kernel-log delta added one order-4 page-allocation failure for `terminator2d-ne` (PID 30017), through `system_heap_allocate -> dma_heap_ioctl`; the contemporaneous kernel `Mem-Info` reported `free=8399` pages and `free_cma=4122` pages. No OOM-killer or `Killed process` entry appeared in that delta. The ON delta contained no additional page-allocation failure, but retains the OFF event in its baseline, so this is not an independent clean-kernel result.

- **OFF**, run `eb0df8ff-d369-4caa-9e5d-abc749a18bb6`: floor `MemAvailable=92,404 KiB`, `SwapFree=1,962,064 KiB`, `CmaFree=7,836 KiB`, `VmRSS=699,000 KiB`, `VmSwap=62,008 KiB`; proc snapshot duration 145,792 ns. `LC2_M3B_WINDOW`/mark records: 0, as expected with the ring disabled. Timeline: 109 samples, 107 live, 3 dropped, `complete=false`.
- **ON**, run `df657097-c8f2-4635-b7a9-eb02ada2689b`: floor `MemAvailable=91,616 KiB`, `SwapFree=1,975,176 KiB`, `CmaFree=92 KiB`, `VmRSS=711,928 KiB`, `VmSwap=48,776 KiB`; proc snapshot duration 146,875 ns. Timeline: 107 samples, 105 live, 4 dropped, `complete=false`.

The ON ring emitted **44/44** records (41 windows + 3 marks), no incomplete/active/dropped/format-error records. It captured 25 BC initialize + 4 BC refresh windows, 9 non-BC texture initialize + 1 non-BC refresh window, and both depth renderbuffers. Every window had a known storage generation, but source-write/content epochs remain untracked. GL errors, driver allocations, GPU in-flight work, fileback shadows, and physical Mali residency are not attributed by these windows. Owners 92/81 remain the largest BC overlaps: 64,800,000 B and 38,880,000 B; decode wall 558.9/323.6 ms. The non-BC and depth windows now cover the previously missing large NVN texture/renderbuffer paths.

The nearest independent runtime samples were 38.6 ms (OFF) and 74.5 ms (ON) before the floor timestamp; they are asynchronous brackets, not exact floor measurements. Prelaunch-to-floor `SwapFree` fell by 71,424 KiB OFF and 58,624 KiB ON. Both timelines are incomplete and floor/CMA readings differ, so this single sequential pair does not establish a causal memory or ring-overhead effect. The floor snapshot and declared-storage totals do not identify physical Mali residency.

## Cleanup and display

OFF cleanup initially showed the idle-clock overlay. A released 100 ms agent-injected BACK was recorded; a subsequent KMS capture verified the awake MainUI home (SHA-256 `a6200d17688528dceaac7099ec4a724da40d70d08128a9270622a6496b91da11`). ON KMS showed awake MainUI directly (SHA-256 `7eb118fbcde0ee19c5891d54592ad36357638149cb530dd442ac95c649fe60d4`). These are cleanup-only captures, not game pixels.

Raw `latest.log`, memory timelines, and screenshots remain local-only. `ab-summary.json` is the compact receipt.

## Verdict and next step

M3-B now covers the observed large BC, non-BC texture, and depth-renderbuffer request windows. The OFF arm also produced one order-4 DMA-heap page-allocation failure (`system_heap_allocate -> dma_heap_ioctl`); the allocating object/texture is unknown. The live-set still reports buffer storage 0 and the EGL path is an 8×8 pbuffer; driver backing/physical residency and the missing periodic sample intervals remain unknown. No-swap operation is not achieved; no menu/gameplay or FPS result exists. The read-only post-run preflight measured `MemAvailable=688,148 KiB`, `CmaFree=102,600 KiB`, `SwapFree=2,032,836 KiB`, MainUI only, with build256b hash intact.

Next: follow roadmap order 3 (M2B-E3 exact subresource/lifecycle accounting and pre-allocation admission) and analyze the observed DMA-heap page-allocation failure before another risky device launch. Keep `LC2_BC_INPLACE_DECODE` default-off. Only after that gate is implemented and tested should the same-build C1 classifier run with ring ON and the in-place flag as the sole changed variable; retain floor96 and never enter New Game.
