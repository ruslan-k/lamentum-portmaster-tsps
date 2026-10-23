# M4-B H2: portable lifetime contract (host-only checkpoint)

H2 host-contract work is still partial. The portable core backs one default-off, one-shot stencil storage diagnostic; the opt-in event ledger now also records object-generation alias views on the zero-storage path. Neither is a complete physical GL ledger or a memory-saving device change.

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

The separate `lc2_life_events` telemetry now holds `alias_views` per `(share_group, GLuint, kind, object_generation)`. `zero_texture_storage` snapshots that generation at publish and passes it on texture or renderbuffer join/release. Unknown/stale generations and per-object underflow increment `overflow`; a stale release cannot decrement a reused name's current generation. Delete records include `alias-views` and increment `delete_with_views` when either the caller or ledger sees aliases. They **still** clear the event and subtract nominal `retained_bytes`; an orphaned global count stays conservative, and neither counter gates actual deletion/admission or proves physical retention. The event record remains 64 bytes because the new counter uses prior struct padding.

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

The focused fixture compiles the exact overlay header with `-std=c11 -Wall -Wextra -Werror` and UBSan trap mode. RED/GREEN cases establish: (1) same GLuint/kind under two context epochs receives distinct object generations while epoch-zero share-group storage remains shared; context loss preserves other entries and does not refund logical bytes; (2) share-group-loss tombstones survive slot churn; (3) a checked, definitely-failing GL result (including `0x0505`) rolls back only replacement intent; (4) an ambiguous result retains the pending reservation and blocks commit/reuse/delete; (5) storage-only commit without a completion timeline remains charged and cannot be used or deleted; (6) callback storage transactions skip on preexisting errors, commit only on clean per-call success, and leave post-call errors pending/unknown. Focused lifetime-core tests: **7/7**. The actual `momo_stencil_selftest` caller was compiled and exercised with mocked GL for default-off, success, preexisting-error skip, and post-call-error cases: **1/1**. A separate source-bound integration fixture compiles the full `zero_texture_storage.h` caller against mocked NVN objects and exercises texture and renderbuffer joins/releases.

The full host suite passes **405/405** with zero skips when `LAMENTUM_REQUIRE_ZERO_STORAGE_ALIAS_TEST=1` (the fixture refuses to silently skip if the adapter source is missing). The inventory gate accepts the current patched source tree: 390 C/C++ files, 77 callsites (12 wrapped+unmeasured, 65 unknown), source-tree SHA-256 `3fcc9e78155ecdfd71507e860c5120d313a6a2d81967eed2ece572215cf38689`, overlay SHA-256 `5ab2d36f5dcb1fdc275bfcaa55b9be8cfcc2dace10044bc9c932f5083a0dee62`. The original bounded mock fixture remains AArch64-cross-compiled; the new zero-storage alias fixture also cross-compiled and ran on Longan (AArch64 ELF64, Build ID `606078e973a3252f53d9afca2e40e30e7270c12b`, SHA-256 `d6b0c54d050dc7c8da7007f2f1ae3dffb820b10b0aa669e03b4fc8457ada02dc`, max GLIBC 2.17). It verifies diagnostic alias counts for texture and renderbuffer join/release only; it is not a game/GL/backing test. Device evidence and the fresh D0 pair are in [the H2a/D0 receipt](../evidence/m4b-h2a-alias-d0-2026-10-23/README.md). No current game ELF was built/installed/launched; device runtime remains held by the unresolved D-policy/margin gate, and no gameplay/FPS evidence is claimed.

## Real callsite map (source inspection only)

`lc2_gl_admission.h` still provides pre-call admission without owner/result accounting. The three opt-in `glBufferData` paths in `nvn_vertex_stream.h` and the presenter VBO in `nvn_present.h` log storage without local result checks; framebuffer caches and EGL surface estimates remain nominal. The default-off one-shot `momo_stencil_selftest` is now the bounded seam: its 64×64 texture and renderbuffer stores each run through `lc2_life_gl_storage_transaction`, which drains the caller-owned error queue before/after the single GL operation, skips on a prior error, commits only a clean result, and retains a post-call error as pending/unknown. The local accounting table is discarded when the diagnostic returns; it is not persistent tracking or a deletion/admission gate.

`lc2_life_commit_gl_result()` accepts `GL_NO_ERROR` as success; a nonzero code is a failure only when the caller knows the operation had no effect. The storage transaction helper treats post-call errors as unknown instead, keeps the reservation, and never converts them into a refund. `lc2_life_mark_unknown()` has no automatic resolution path.

## Next integration gate

Next H2 gate: integrate persistent owner/storage accounting at one production texture path. The current candidate's exact source binding is now recorded in [the owner-generation receipt](../evidence/h2-owner-generation-source-binding-2026-10-23/README.md): for ELF `c4671440…`, `object-generation=t->id` is a unique monotonic NVN object ID within that process, not a GL/storage/pool generation. The new source-linked host fixture in that receipt compiles the exact NVN ID generator and owner-event header, pins the texture initialize/alias/pair callsite expressions, and verifies NVN identity remains distinct from GL-name storage generation. It is not a GL/game runtime test. Focused `test_life_events` is **12/12** and the full suite **430/430** with the required source fixture enabled. Delete/respec accounting lacks separate logical-name versus possibly-GPU-retained bytes, attachment/subresource identities, normal-path per-call allocation outcomes, and completion receipts. Then add buffers/EGL owner classes and the remaining failure/overflow matrix. Unknown/overflow must preserve uncertainty rather than stop a healthy title or permit free. Keep admission/deletion behavior unchanged until GL-name reuse, shared contexts, completion and lost-fence cases are proven.

Safe menu headroom, navigation/world, audio/save and30 FPS remain OPEN.
