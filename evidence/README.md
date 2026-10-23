# Evidence

**Latest audited next-action roadmap:** [post-build262 gameplay recovery and 30 FPS execution plan](../docs/post-build262-gameplay-recovery-roadmap-2026-10-23.md), updated at main@3cb6b81 with [§10 audit](../docs/post-build262-gameplay-recovery-roadmap-2026-10-23.md#10-main3cb6-re-audit-and-next-implementation-slices-2026-10-23) and this branch's [§10.16 K1-D system DMA-heap page class](../docs/post-build262-gameplay-recovery-roadmap-2026-10-23.md#1016-k1-d-system-dma-heap-page-class-2026-10-23). H1 is complete at recorded compile/link-input scope; H2 alias telemetry is partial. K1-C and K1-D narrow the matched native Kbase and generic system-heap page paths, but actual GL/DMA-BUF routing and peak overlap remain unknown. The current candidate is staged inertly; the latest complete same-boot pair is **HOLD_RUNTIME** at `CmaFree=608 KiB` with no order-7+ CMA blocks. No game was launched and no FPS result exists.

**Current policy:** [roadmap §15](../docs/post-build260-cma-gameplay-performance-roadmap-2026-10-23.md#15-revised-publication-install-and-runtime-testing-gates-2026-10-23-overrides-indefinite-device-no-go) separates host/source publication, inert staging, fresh read-only preflight and runtime gates. The pre-hash pair was stable at `CmaFree=130,412 KiB`, but the post-read state fell to `532→576 KiB` and stayed near 604 KiB during idle. A fresh complete same-boot pair at `11:32:56–11:33:32Z` remained at `608 KiB`, with no order-7+ CMA blocks. The candidate is staged but not active; build259 remains active. K1-D narrows only generic system-heap allocation; GL/scratch ownership and overlap remain unknown. `T2_STORAGE_MARGIN_MIB` is unset and D is **HOLD_RUNTIME**.

## Latest evidence and safety disposition (2026-10-23)

- [K1 exact firmware kernel / CMA snapshots](m2b-k1-kernel-cma-provenance-2026-10-23/README.md): exact kernel warning-retry path verified, CMA backing/owner unresolved, idle CmaFree 15,456 KiB in recorded samples; **runtime unsafe at that historic checkpoint**.
- [A1 host-only admission replay](a1-storage-admission-offline-replay-2026-10-23/README.md): all four build259 denials reproduce conservative arithmetic; physical CMA assumption unqualified.
- [M4-A checked BC stripe sizing (host-only)](m4a-bc-stripe-capacity-2026-10-23/README.md): native fixture, pinned-container ASan/UBSan, full suite and AArch64 build pass; request sizing only, candidate uninstalled; §15 preflight required before any runtime launch.
- [M4-B source census and generation fixture (partial; host + target)](m4b-gl-allocation-inventory-2026-10-23/README.md): 77 source callsites (12 wrapped+unmeasured, 65 unknown); 2,048-entry history with 1,200-key create/reuse, 1,024 create/delete pairs, 24 reuses and same GLuints across share groups; overflow is fail-closed and separately counted. Standalone AArch64 fixture passed on Longan; build262 game runtime remains uninstalled/unrun pending margin approval. **Fresh read-only Longan pair:** CmaFree=130,412 KiB twice over 44.009 s, versus historical K1 pair=15,456 KiB (not a matched cross-session delta or proof of reclaimed memory). The launcher still has no `T2_STORAGE_MARGIN_MIB`; D game-runtime authorization remains separate.
- [M4-B H1 compile/link-input audit (host phase complete)](m4b-compiled-reach-2026-10-23/README.md): tracked wrapper/materializer regenerated the pinned build265 trace; all 77 statuses reproduced with zero delta (58/11/8 compile, 66/11 link inputs); 26 focused tests and full suite 396/396 pass. Per-function section retention and runtime remain unknown; no device action or game run.
- [M4-B H2 lifetime core (host/target CPU partial)](../docs/lifetime-core.md): context/share-group epochs, checked/unknown storage outcomes, a one-shot mock stencil caller, and per-object-generation alias telemetry on one zero-storage texture/renderbuffer path. Lifetime-core tests 7/7; life-event tests 11/11; full suite 405/405, zero skips. The target fixture is not GL/game backing; no actual game launch or FPS result.
- [M4-B H2a alias + D0 preflight](m4b-h2a-alias-d0-2026-10-23/README.md): pinned AArch64 fixture ran on Longan and was removed/hash-verified; fresh D0 pair stable at CmaFree 130,412 KiB. Game runtime remains HOLD because D-policy and reviewed one-run margin are unresolved.
- [D-policy source request-class map (partial)](d-policy-typed-memory-classes-2026-10-23/README.md): all 13 `t2_storage_admit` callers identified and separated into GL intent, CPU scratch, and combined requests; no physical backing/peak-overlap proof, so the runtime margin remains unjustified.
- [K1-B live CMA region and heap inventory](k1b-live-cma-region-2026-10-23/README.md): read-only live DT/boot-log/iomem confirms the 128 MiB pool at `0x73800000`; matched-kernel paths show the CMA heap allocator uses `cma_alloc`, and initcall/minor ordering strongly associates `/dev/dma_heap/reserved` with it. Explicit name input and per-buffer GL/scratch consumers remain unobserved; no launch preflight.
- [K1-C live Mali native page path](k1c-kbase-native-pages-2026-10-23/README.md): same-boot parameter `kbase_page_migration_enabled=0`; matched module traces its native page pool to `__alloc_pages(GFP_HIGHUSER|__GFP_ZERO)`, and the exact kernel Unmovable fallback excludes CMA. This narrows only that native Kbase path; GL/DMA-BUF routing and peak overlap remain unknown, so D stays **HOLD_RUNTIME**.
- [K1-D matched system DMA-heap page path](k1d-system-heap-page-path-2026-10-23/README.md): generic `system_heap_allocate` calls `__alloc_pages` with masks lacking movable/reclaimable bits; the matched Unmovable fallback excludes CMA. Live `system` exporter buffers observed are MainUI/system-state only; no Lamentum request is joined to this heap.
- [Current post-H2a source host ELF](current-elf-host-build-2026-10-23/README.md): 435/435 baseline manifest, 405 host tests, AArch64 PIE SHA-256 `c4671440…`, max GLIBC 2.27. The candidate/helper were later staged inertly with exact readback; no launch, build259 remains active.
- [Current host ELF staging and D preflight](current-host-elf-staging-preflight-2026-10-23/README.md): exact ELF/helper readback and ROMFS section hash verified; candidate remains inert. After the large read, a fresh complete pair at 11:32–11:33Z still showed `CmaFree=608 KiB` both samples and no order-7+ CMA blocks. D is **HOLD_RUNTIME**; no margin or cache/compaction/reboot action was taken.
- [build259 margin matrix](m2b-e3-build259-margin-sweep/README.md): 64/48/32/24 MiB all stopped before menu; no further margin sweep authorized.
- [M3B build256b observer OFF/ON](m3b-build256b-pair-20261022-01/README.md): BC/non-BC/depth windows covered, buffer/EGL/CMA ownership missing, no menu.
- [M3A build251 BC stripe pairs](m3a-bcstripe-b251-01/README.md): CPU staging changed, all six arms stopped at memory floor; no verified persistent memory saving.
- [E4 host-only owner-pair checkpoint](e4-owner-pair-host-2026-10-23/README.md): build260 diagnostics compiled, historical missing IDs remain unresolved, **not deployed**.

**Historical evidence-led technical work queue:** [post-build260 roadmap §13](../docs/post-build260-cma-gameplay-performance-roadmap-2026-10-23.md#13-evidence-first-execution-gates-after-the-main1604ed9-re-audit-2026-10-23). These are evidence records, not demonstrations of gameplay or 30 FPS. See older per-build directories for historical results only.

Use one directory per bounded device run: `device-01/`, `device-02/`, … Each
published directory contains:

- `README.md` — hypothesis, exact build/settings/run identity, measured result,
  limitations, and next gate;
- compact receipts — deployment hashes, run UUID/boot/PID identity, pre/post
  device state, cleanup, and screenshot metadata/hash where relevant.

Keep raw device data local-only and gitignored: `latest.log`, full kernel dumps,
and PNG/KMS captures. A report may cite their SHA-256, size, selected exact
records, and the local path; do not commit the raw files.

Rules that apply to every entry:

- A controlled stop is not a frame and not a failure of the game: it is the
  runtime refusing to guess. Name the stop code and the caller.
- Never report a picture without a physical KMS capture, and never report
  performance from a diagnostic build. Publish a capture receipt/hash, not the
  raw screenshot.
- Per-run claims must be traceable to the run-owned log identity and an exact
  record; cumulative values from different timestamps are not a live-set join.
- Label SpruceOS cleanup captures as cleanup evidence, never gameplay.
