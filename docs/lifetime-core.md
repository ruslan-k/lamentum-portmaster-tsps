# M4-B H2: portable lifetime contract (host-only checkpoint)

H2 host-contract work is in progress. This checkpoint adds explicit context/share-group identity to the portable lifetime model; it is not a completed GL ledger or a memory-saving device change.

## Artifact

runtime/lamentum-adapter.patch now carries native/lc2_lifetime.h, a standalone
C11 bounded state machine with no GL calls, heap allocation, environment switch,
or runtime callers. The existing nvn_texture/GL paths are unchanged. The public
host test extracts and compiles this exact header FROM THE OVERLAY, not from a
private source checkout.

Each record carries an explicit `lc2_life_identity`: share-group epoch, context epoch, GLuint name and object kind. `context_epoch=0` scopes storage to the share group; a nonzero epoch distinguishes context-local objects with the same numeric name. The caller supplies monotonic, verified epochs; a context handle/pointer is not itself an epoch. Respecifications keep object generation and receive a fresh monotonic storage token; name reuse after retirement receives a fresh object generation. Context loss invalidates only that context's nonzero-epoch entries; share-group loss invalidates the whole epoch and preserves a tombstone so its identity cannot be recycled from the bounded table. At most 64 storage slots and 64 timeline identities; capacity/uint64 overflow refuses without inventing an untracked owner. Caller bytes are checked logical intents, not Mali residency.

Transitions:

- begin: reserve intent before allocation, no committed-byte credit yet;
- commit(success): transfer reservation into retained logical payload;
- commit(failure): roll back only pending intent, not older storage or physical RAM;
- attach/detach: views reference the SAME storage token, with no second byte charge;
- use: validated timeline and monotonic submission serial, disallow already-completed serials;
- retire: mark a candidate, do not decrement retained payload;
- can_delete: only retiring + zero views + completion covering last reader, valid group;
- deleted(success): reduce logical retained payload only after permitted deletion receipt;
- context loss: invalidate only context-local entries for the matching epoch; retain accounting and permit a fresh context epoch in the surviving share group;
- share-group loss: invalidate every entry in that epoch and retain unresolved accounting; a replacement group must use a fresh share-group epoch.

The caller must serialize operations and supply verified share-group and context epochs, GL success and completion receipts. `context_epoch=0` is valid only for object classes proven shareable; do not use a context handle/pointer as an epoch. A true input flag is not independent evidence: no production caller exists yet and no GL/EGL proof is claimed by these tests. Per-level/face/layer GL subresources and window/pbuffer/EGL ownership are not represented in this core.

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

The focused fixture compiles the exact overlay header with `-std=c11 -Wall -Wextra -Werror` and UBSan trap mode. New RED/GREEN cases establish: (1) same GLuint/kind under two context epochs receives distinct object generations while epoch-zero share-group storage remains shared; context loss preserves other entries and does not refund logical bytes; (2) share-group-loss tombstones survive slot churn; (3) a checked GL error code (including `0x0505`, not merely boolean `1`) rolls back only the replacement intent, keeps the prior storage charged, and a later successful result commits the new logical bytes. Focused lifetime-core tests: **4/4**.

Full host suite: **399/399**. No production caller, runtime build/deploy, GL/EGL execution, target run, memory reduction, or FPS result is claimed. The adapter overlay applies cleanly to the manifest-verified recovered baseline. The device/runtime remains unqualified.

## Real callsite map (source inspection only)

`lc2_gl_admission.h` performs pre-call admission then invokes raw `glTexImage2D`, `glRenderbufferStorage`, or `glBufferData`; it does not bind a result to an owner or check the per-call GL result. `nvn_textures.h` emits storage events after image/renderbuffer calls; the full-refresh path checks `glGetError()` after the mip loop rather than committing each level separately. The three opt-in `glBufferData` paths in `nvn_vertex_stream.h` and the presenter VBO in `nvn_present.h` log storage after the call without a local result check. `nvn_framebuffers.h` caches attachment IDs/names but not storage generations; `nvn_window.h` records EGL width×height×4 as a nominal estimate only. None of this source inspection proves a GL call succeeded or that bytes are physically backed.

`lc2_life_commit_gl_result()` expects the error code from that exact operation (`0` means success); it returns true only if GL succeeded and the ledger transition was accepted. A nonzero error rolls back only the pending replacement intent and returns false. A prior/stale error cannot be attributed to this operation. The core still has no `unknown-result` commit state, so do not wire ambiguous GL error queues as either success or definite failure.

## Next integration gate

Use the checked-result contract at one real, bounded storage seam with the GL error queue isolated, then extend to all texture/renderbuffer/buffer classes. Add alias/attachment ownership, per-context vs shared GPU completion, buffer/EGL surface classes, and the full H2 failure/overflow matrix. Audit every reachable storage/delete and exceptional exit path; unknown/overflow must preserve the charge and invalidate evidence, not stop a healthy title or permit free. Validate real GL-name reuse, respecification, shared contexts and lost fences before any ledger-controlled deletion/admission change.

Safe menu headroom, navigation/world, audio/save and30 FPS remain OPEN.
