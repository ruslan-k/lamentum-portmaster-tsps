# K1-D — matched system DMA-heap page path

This host-side follow-up classifies the matched kernel's generic `system` DMA heap. It does **not** connect a Lamentum GL request or buffer to that heap.

## Static path in the exact firmware kernel

Using the already matched `vmlinux` (SHA-256 `806182f8823b0db340f3f9beccf303e39571deb20b99386ee6a76442b8761b19`, Build ID `175a7f4d4731ebfbbdeb7695329115202f8b813a`):

- `system_heap_create` registers heap name `system` (K1-B); live `/dev/dma_heap/system` is minor 0, distinct from the default-CMA-associated `reserved` heap.
- `system_heap_ops` at `0xffffffc008cf7b20` resolves to `system_heap_allocate` at `0xffffffc008539b54`.
- `system_heap_allocate` loads allocation-mask words from the adjacent table at `0xffffffc008cf7b28`; it calls `__alloc_pages` at `0xffffffc008539c70`.
- The table words used by the call are `0x001521c2`, `0x00140dc2`, and `0x00140dc2`. The exact kernel GFP table names `__GFP_MOVABLE=0x8` and `__GFP_RECLAIMABLE=0x10`; none of these masks sets either bit. The matched kernel's `Unmovable` fallback row is `[Reclaimable, Movable, sentinel(6)]`, and `CMA` is enum value 4, absent from that row.

Thus the matched `system` heap's direct page-allocation path requests the non-movable class and does not reach CMA through the generic Unmovable fallback. This is not the `cma_alloc` path used by `/dev/dma_heap/reserved`.

## Live exporter snapshot and limits

The same-boot read-only snapshots at `2026-10-23T11:09:25.644Z` and `11:09:51.320Z` found six global DMA-BUF entries, all with exporter name `system` (two 16,384-byte entries and four 3,686,400-byte entries). MainUI's FD list was stable and included `/dev/dma_heap/system`; it showed no `reserved` exporter. These are MainUI/system-state observations, **not** Lamentum allocation records or proof of per-buffer physical backing.

This narrows the generic system-heap path only. It does not show whether the game routes texture/renderbuffer/buffer/EGL requests through `system`, Kbase native pages, `reserved`, or another import path. Keep per-request ownership and overlap unknown; do not relax the admission guard or infer a gameplay reserve from this class alone. The candidate remains inert and D is **HOLD_RUNTIME** (latest complete same-boot pair `CmaFree=608 KiB` at 11:32:56–11:33:32Z; no order-7+ CMA blocks).

## Verification

- Eight assertions passed against the matched kernel: `system_heap_ops` relocation target, `__alloc_pages` callsite, three flag words, both non-movable bits, and the Unmovable/CMA fallback mapping.
- No new device command, file write, or game launch was performed for K1-D; it reuses the already captured same-boot DMA-BUF snapshots.
