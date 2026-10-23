# M4-B source callsite census (host-only)

This is the first M4-B substep, not completion of the allocation-lifetime gate.

- Scanned the exact patched build261 source tree under `native/` and `framework/`: **390 C/C++ files**, source-tree SHA-256 `8d244eede356a5f9e28d3a125f3d50dee8dc477b379149ca4168fb339cfd603d`.
- Adapter baseline `c8d01ca1fed5adab1ae7ad920605f199bb83a72e`; overlay patch SHA-256 `23762e1bcd4c5b759c7417647f24e1df4430bcd4fd32e56f0c2a007954db50a8`.
- Inventory: **77** storage/attachment/copy/EGL source callsites — 69 direct and 8 indirect. Categories: 38 texture-storage, 6 buffer-storage, 3 renderbuffer-storage, 23 framebuffer attachments, 3 texture-copy, 4 EGL surfaces.
- Classification: **12 wrapped+unmeasured**, **65 unknown**, zero wrapped+measured and zero not-reached. Unknown is explicit; no missing event is treated as no allocation.
- Added `tools/gl_allocation_inventory.py` and a pinned callsite policy. `build_lamentum.sh` runs the checker after applying the overlay and before compilation; source-tree or callsite drift fails closed. A synthetic unwrapped `glBufferData` regression test fails policy validation.
- Verification: focused inventory tests **7/7**; full tools suite **366/366**, zero skips/failures/errors; exact source-tree CLI scan **77/77** callsites; `bash -n build_lamentum.sh` passed.

## Limits and next work

The scanner covers a source-tree superset; exact compiler-unit/include-closure reachability is not yet classified. In particular, indirect NXGL dispatch candidates remain unknown. The census does not prove runtime reach, owner generations, buffer/EGL backing, allocation success, driver residency, physical CMA, or memory refunds. The build261 AArch64 candidate (`0958651d1e9cb1333023c9a9418be781b6cf2b49d628dc5b9a8c122a80c96332`) remains uninstalled; the last read-only `CmaFree=15,456 KiB` is a historical sample. No fresh preflight or staging/runtime action was performed. Follow roadmap §15 for non-executing staging; hold runtime until fresh positive preflight. The port remains **NOT PLAYABLE**; no gameplay FPS is verified.

Next M4-B work: exact callsite reach/wrapper classification, >1024 distinct/reused GL-object generation tests, transactional re-spec/delete/alias/context-loss coverage, and generation-aware buffer/EGL owner accounting. Keep separate logical, requested, process, driver, and physical-CMA bases.

Machine-readable source census and per-callsite dispositions are in [`summary.json`](summary.json); the reviewed policy used by builds is [`tools/gl_storage_callsite_policy.json`](../../tools/gl_storage_callsite_policy.json).
