# Post-boot CMA observations — 2026-10-23

## Event and scope

A fresh check after the operator's approval found boot ID `76212e98-f521-4f2e-8e93-76f58f48991a`, different from preflight boot `15b97fe4-5c48-412c-ba39-92efb1823286`. The agent had **not** sent a reboot command. Estimated boot time is `13:52:34.987Z`; the boot transition occurred after the last pre-transition dmesg capture at `13:47:34.333Z` and before the first new-boot snapshot at `13:53:04.659Z`. Its initiator is unknown; the operator may have performed the approved reboot. No further reboot was issued.

## Measurements

The earliest stable compact snapshot was at device uptime `29.67 s`: complete census, MainUI `2368/1075`, principal `2210/1021`, no game/pending command, `CmaFree=130,412 KiB`, `nr_free_cma=32,603` and 31 free order-10 CMA blocks. Its saved compact record omitted DMA-BUF inventory, PSI and warning-filter output. The first retained full inventory sample followed at uptime `115.96 s` (**55.96 s after the 60 s target**). Follow-ups were captured at `340.99 s` (**40.99 s after 5 min**) and `905.30 s` (**5.30 s after 15 min**).

Across all three full snapshots on the new boot:

- `CmaFree=130,412 KiB` and `nr_free_cma=32,603` remained unchanged; each free-CMA histogram had 31 order-10 blocks, one order-9 block, one order-8 block, zero order-7 blocks, and one block each at orders 6, 4 and 3.
- The histogram represented 32,600 pages, a preserved 3-page difference from `nr_free_cma`.
- `cma_alloc_success/fail` remained `8/0`; `SwapFree=2,065,884 KiB`, swap-in/out deltas were zero, and filtered dmesg found no allocation/OOM/CMA/Mali warnings. Memory PSI was unavailable.
- MainUI `2368/1075` and principal `2210/1021` remained stable; no game process or pending principal command appeared. Each process census was complete and identity-ready.
- Four visible DMA-BUF entries remained, all `system` exporter (inodes 1, 3, 4, 5). Two `system` entries (inodes 6, 7) present in the preboot six-entry inventory were absent. This does not prove CMA backing or explain the preboot low reading.

The preboot reference was a single `CmaFree=2,008 KiB` sample at `13:43:29Z`, not immediately before the transition. The cross-boot difference is descriptive, not an owner or leak attribution. Page-owner/CMA-debugfs data are unavailable; movable versus pinned/Mali-private ownership of the prior non-free pages remains **unknown**.

## Conclusion and gate

The new boot began with high free CMA and stayed at that level for the first 15 minutes without Lamentum running. This argues against rapid CMA depletion during ordinary early boot in the observed idle state and shows the prior low reading was not a permanent hardware-capacity ceiling. It does **not** identify what occupied CMA before the boot, rule out slower/later workload growth, or justify a game allocation reserve. The observed return is associated with the boot transition, but the agent did not initiate it and its cause has not been confirmed.

**Runtime remains `HOLD_RUNTIME`.** No game was launched. `T2_STORAGE_MARGIN_MIB` remains unset; any future probe still requires the existing complete D-preflight and an independently justified positive class-specific reserve. The observed boot is counted; do not reboot again for this experiment.

Raw read-only snapshots are retained locally under Hermes scratch; `summary.json` contains the compact measurements and provenance.