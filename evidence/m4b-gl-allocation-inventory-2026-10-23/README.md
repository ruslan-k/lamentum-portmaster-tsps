# M4-B allocation-source and generation census (host-only)

This is the first M4-B substep, not completion of the allocation-lifetime gate.

- Scanned the exact patched build262 source tree under `native/` and `framework/`: **390 C/C++ files**, source-tree SHA-256 `1b995ea13bab7aa2afcf865f68006b095a401c3cc71b8321f83c778a052dabfb`.
- Adapter baseline `c8d01ca1fed5adab1ae7ad920605f199bb83a72e`; overlay patch SHA-256 `6c549b09797a403390d4ced13e770bc35c65f74d70240a01f2ec77f6e258eba4`.
- Inventory: **77** storage/attachment/copy/EGL source callsites — 69 direct and 8 indirect. Categories: 38 texture-storage, 6 buffer-storage, 3 renderbuffer-storage, 23 framebuffer attachments, 3 texture-copy, 4 EGL surfaces.
- Classification: **12 wrapped+unmeasured**, **65 unknown**, zero wrapped+measured and zero not-reached. Unknown is explicit; no missing event is treated as no allocation.
- Generation history: table capacity **512 → 2,048**; tests cover 1,200 distinct-name create/reuse, **1,024 create/delete pairs**, **24** same-name reuses, and identical GLuints in distinct share groups. Full-capacity and `UINT64_MAX` refusals pass. New `generation_history_overflow` and `live_owner_overflow` counters distinguish history exhaustion from the unchanged 512-entry live owner/subresource tables; storage/delete event-ring overflow is also detected.
- Static size: `sizeof(lc2_life_events_state)` **155,504 → 200,576 B**; compiled AArch64 `.bss` **12,809,440 → 12,854,512 B** (**+45,072 B**). This is static section size, not measured RSS or CMA; no heap allocation was added.
- Added `tools/gl_allocation_inventory.py` and a pinned callsite policy. `build_lamentum.sh` runs the checker after applying the overlay and before compilation; source-tree or callsite drift fails closed. A synthetic unwrapped `glBufferData` regression test fails policy validation.
- Verification: inventory tests **7/7**, generation/lifetime tests **10/10**, full tools suite **370/370** with zero skips/failures/errors, baseline **435/435**, exact source-tree scan **77/77**, and patch/overlay byte equality pass. Pinned AArch64 build262: ELF64 PIE, **2,206,936 B**, Build ID `9395a24ac719269308b30476f8631349f47242a4`, max GLIBC **2.27**, SHA-256 `dd13d4ab300fdaa1f51acd78e105a55a02af1de6de05526328d2242b07da1cbc`; still uninstalled.

## Limits and next work

The source census remains a source-tree superset; exact compiler-unit/include-closure reachability is not yet classified. The inventory and generation fixture do not prove runtime call reach, buffer/EGL backing, allocation success, driver residency, physical CMA or memory refunds. The build262 AArch64 candidate (`dd13d4ab300fdaa1f51acd78e105a55a02af1de6de05526328d2242b07da1cbc`) remains uninstalled. No fresh preflight or device action occurred; follow roadmap §15 for non-executing staging, and hold runtime until fresh positive preflight. The port remains **NOT PLAYABLE**; no gameplay FPS is verified.

Next M4-B work: exact compiler-unit/include closure and callsite reachability; context teardown/recreation epochs; full alias/view, transactional re-spec/delete and deferred-completion cases; buffer/EGL owner-generation accounting; then the separated owner/memory-class waterfall. Keep logical, requested, process, driver and physical-CMA bases distinct.

Machine-readable source census and per-callsite dispositions are in [`summary.json`](summary.json); the reviewed policy used by builds is [`tools/gl_storage_callsite_policy.json`](../../tools/gl_storage_callsite_policy.json).
