# K1-C — live Mali native page-allocation path

This read-only follow-up narrows one Kbase allocator class. It does **not** map Lamentum GL storage requests to that class or qualify a launch.

## Target observation

Captured `2026-10-23T10:45:17.795Z` on firmware `1.0.1`, kernel `5.15.147`, boot `15b97fe4-5c48-412c-ba39-92efb1823286`:

- `/sys/module/mali_kbase/parameters/kbase_page_migration_enabled` reads `0`, mode `0444`.
- Boot log: `[    2.875701] mali 1800000.gpu: No memory group manager is configured`.
- Read-only `/lib/modules/5.15.147/mali_kbase.ko` readback matches K1-B: 29,984,864 bytes, SHA-256 `2aaf1556a7a352caffec4db8821ea9d2f847529671321caa1a667de992d1ceb5`, Build ID `0dcaa84a5579b1122f98f29d0214723a2dff9603`.
- The probe wrote no device files and launched no game.

## Matched-module path

R2 addresses below are pseudo-VMAs in the relocatable module analysis map (`.text` begins at `0x08000040`), not runtime kernel virtual addresses.

1. `kbase_alloc_phy_pages_helper` calls `kbase_mem_pool_alloc_pages` at `0x08002d9c`; the pool path calls `kbase_mem_alloc_page` at `0x0801fdbc`.
2. `kbase_mem_init` stores the address of `kbase_native_mgm_dev` into the device's `+0x1518` slot (`0x08001470–0x08001480`). The first `.data` relocation in that manager table targets `.text+0x8094`, `kbase_native_mgm_alloc`.
3. `kbase_mem_alloc_page` reads `kbase_page_migration_enabled` and selects flags at `0x0801e63c–0x0801e658`, then calls the manager's first function pointer at `0x0801e668`.
4. `kbase_native_mgm_alloc` forwards the flags and order to `__alloc_pages` at `0x080080f0`. This is a page-allocator path, not a direct `cma_alloc` or DMA-heap call.

The exact matched `vmlinux` GFP-name/mask table resolves:

- `GFP_HIGHUSER` = `0x00100cc2`; `__GFP_ZERO` = `0x00000100`.
- `GFP_HIGHUSER_MOVABLE` = `0x01100cca`; `__GFP_MOVABLE` = `0x00000008`.

With the live parameter at `0`, the module selects `0x00100dc2` (`GFP_HIGHUSER | __GFP_ZERO`), not the migration-enabled `0x01100dca` (`GFP_HIGHUSER_MOVABLE | __GFP_ZERO`). The matched kernel's `migratetype_names` table assigns `Unmovable=0` and `CMA=4`; its `Unmovable` fallback row is `[Reclaimable, Movable, sentinel(6)]` and does not include CMA.

## Interpretation and limits

This is strong evidence that the **native Kbase page-pool path** under the observed configuration requests non-movable system pages and does not reach CMA through the generic unmovable fallback. It narrows that allocator class; it does not prove that every texture, renderbuffer, buffer, EGL/GBM allocation or GL request uses this path. The module imports DMA-BUF APIs, so imported buffers may have another backing path. No per-buffer owner, GL-to-ioctl join, live allocation, or overlap was observed.

Do not reclassify all `gl_bytes` or `scratch_bytes`, set `proven_cma_bytes` for a whole request class, or reduce the safety reserve from this finding alone. Keep `T2_STORAGE_MARGIN_MIB` unset and `HOLD_RUNTIME` until actual request routing, peak overlap/uncertainty, current ELF and reviewed one-run margin are established.

## Verification

- Live parameter, boot ID, log line and module SHA were read again from the target; the module SHA matches K1-B.
- Eight matched-vmlinux checks passed: four GFP name/mask mappings, two mask compositions, migratetype enum names, and the unmovable fallback row.
- This was a read-only diagnostic/documentation phase; no full host suite or gameplay test was run.
