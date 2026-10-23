# M4-B H2: portable lifetime contract (host-only checkpoint)

H2 host-contract work is still partial. The portable core now backs one default-off, one-shot stencil storage diagnostic; it is not a completed GL ledger or a memory-saving device change.

## Artifact

`runtime/lamentum-adapter.patch` carries `native/lc2_lifetime.h`, a standalone
C11 bounded state machine with no direct GL symbols, heap allocation, or
automatic deletion. Its callback transaction drains GL errors before and after
one storage operation; a preexisting error skips the operation, a clean
`GL_NO_ERROR` commits logical bytes, and a post-call error leaves the request
pending/unknown. The only current caller is the default-off one-shot
`momo_stencil_selftest` in `native/momo_stencil_bench.h`; its table is local to
the diagnostic and is not a persistent runtime ledger. Normal texture and
present paths are unchanged. The host fixture compiles the exact lifetime
header from the public overlay.

Each record carries an explicit `lc2_life_identity`: share-group epoch, context epoch, GLuint name and object kind. `context_epoch=0` scopes storage to the share group; a nonzero epoch distinguishes context-local objects with the same numeric name. The caller supplies monotonic, verified epochs; a context handle/pointer is not itself an epoch. Respecifications keep object generation and receive a fresh monotonic storage token; name reuse after retirement receives a fresh object generation. Context loss invalidates only that context's nonzero-epoch entries; share-group loss invalidates the whole epoch and preserves a tombstone so its identity cannot be recycled from the bounded table. At most 64 storage slots and 64 timeline identities; capacity/uint64 overflow refuses without inventing an untracked owner. Caller bytes are checked logical intents, not Mali residency.

Transitions:

- begin: reserve intent before allocation, no committed-byte credit yet;
- begin_storage_only: reserve intent without fabricating a completion timeline; a later checked GL-success commit remains logically charged and cannot be reclaimed here;
- commit(success): transfer reservation into retained logical payload;
- commit(failure): roll back only pending intent, not older storage or physical RAM;
- attach/detach: views reference the SAME storage token, with no second byte charge;
- use: validated timeline and monotonic submission serial, disallow already-completed serials;
- retire: mark a candidate, do not decrement retained payload;
- can_delete: only retiring + zero views + completion covering last reader, valid group;
- deleted(success): reduce logical retained payload only after permitted deletion receipt;
- context loss: invalidate only context-local entries for the matching epoch; retain accounting and permit a fresh context epoch in the surviving share group;
- share-group loss: invalidate every entry in that epoch and retain unresolved accounting; a replacement group must use a fresh share-group epoch;
- ambiguous storage outcome: mark the pending record `outcome_unknown`, keep its reserved bytes, and block commit/reuse/delete.

The general caller contract still requires serialization, verified share-group/context epochs, per-call GL outcomes, and completion receipts. `context_epoch=0` remains limited to shareable classes; Khronos `GL_OES_framebuffer_object` explicitly permits texture and renderbuffer images to be shared between contexts ([spec](https://registry.khronos.org/OpenGL/extensions/OES/OES_framebuffer_object.txt)). The selftest's mock does not prove target extension support, runtime execution, backing, or cross-context completion. Per-level/face/layer subresources and window/pbuffer/EGL ownership remain outside this core.

## Conservative cases deliberately left unresolved

A new storage specification retains the old generation's charge. While both
versions share a live GL name, neither can be independently glDeleted by this
core: deleting the older name would delete the replacement too. It refuses rather
than inventing an old-storage refund. Future separate driver/storage-retirement
receipts are needed to resolve that over-accounting safely.

Cross-timeline readers are rejected rather than conflated; multi-queue/context
support needs real per-domain receipts. Lost fences/context groups do not produce
logical credit. Payload accounting never claims physical_refund_bytes. Allocation
layout/format/mips arithmetic remains the existing lc2_gl_storage responsibility.
This is not yet the all-class window/EGL/PBO/FBO/texture ledger requested in §48.5.

## Executed verification

The focused fixture compiles the exact overlay header with `-std=c11 -Wall -Wextra -Werror` and UBSan trap mode. RED/GREEN cases establish: (1) same GLuint/kind under two context epochs receives distinct object generations while epoch-zero share-group storage remains shared; context loss preserves other entries and does not refund logical bytes; (2) share-group-loss tombstones survive slot churn; (3) a checked, definitely-failing GL result (including `0x0505`) rolls back only replacement intent; (4) an ambiguous result retains the pending reservation and blocks commit/reuse/delete; (5) storage-only commit without a completion timeline remains charged and cannot be used or deleted; (6) callback storage transactions skip on preexisting errors, commit only on clean per-call success, and leave post-call errors pending/unknown. Focused lifetime-core tests: **7/7**. The actual `momo_stencil_selftest` caller was compiled and exercised with mocked GL for default-off, success, preexisting-error skip, and post-call-error cases: **1/1**.

The full host suite passes **403/403**. The inventory gate accepts the patched source tree: 390 C/C++ files, 77 callsites (12 wrapped+unmeasured, 65 unknown), source-tree SHA-256 `76c87011069d987c3d0212a585ef07ca1848282c6e0af9fba46e148a99b8bd57`, overlay SHA-256 `4a3599edcb1859f790e58f3354635e349fb1f7046289fc45dc1a6a47b2cc4494`. A standalone mock fixture cross-compiles to AArch64 ELF64 (Build ID `c30335df5cb18cb1c8a8c09c4c16873e0c682c33`, SHA-256 `aeaea683b9e152f185345ac8f6e33e45de200eb75bd6c6aae84710e1fa51aa22`); QEMU is unavailable, so it was not run. The full game ELF build did not complete: host cross-compiler was absent; the pinned-container build passed inventory then stopped on `ZERO_ZX_GAME` undefined and unrelated `-Werror` diagnostics. No candidate was installed, and no GL/EGL/device/gameplay/FPS evidence is claimed.

## Real callsite map (source inspection only)

`lc2_gl_admission.h` still provides pre-call admission without owner/result accounting. The three opt-in `glBufferData` paths in `nvn_vertex_stream.h` and the presenter VBO in `nvn_present.h` log storage without local result checks; framebuffer caches and EGL surface estimates remain nominal. The default-off one-shot `momo_stencil_selftest` is now the bounded seam: its 64×64 texture and renderbuffer stores each run through `lc2_life_gl_storage_transaction`, which drains the caller-owned error queue before/after the single GL operation, skips on a prior error, commits only a clean result, and retains a post-call error as pending/unknown. The local accounting table is discarded when the diagnostic returns; it is not persistent tracking or a deletion/admission gate.

`lc2_life_commit_gl_result()` accepts `GL_NO_ERROR` as success; a nonzero code is a failure only when the caller knows the operation had no effect. The storage transaction helper treats post-call errors as unknown instead, keeps the reservation, and never converts them into a refund. `lc2_life_mark_unknown()` has no automatic resolution path.

## Next integration gate

Next H2 gate: replace the one-shot diagnostic scope with persistent owner-generation accounting at one real texture allocation path, while keeping admission and deletion unchanged. Then add aliases/attachments, per-context versus shared completion, buffers/EGL surface classes, and the remaining failure/overflow matrix. Unknown/overflow must preserve charge and invalidate evidence, not stop a healthy title or permit free. Validate GL-name reuse, respecification, shared contexts, and lost fences before any ledger-controlled deletion/admission change.

Safe menu headroom, navigation/world, audio/save and30 FPS remain OPEN.
