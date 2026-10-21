# M1 / §48.5: executable lifetime-accounting core (host component)

Reviewed d8474fa. Implements the next host-contract component, not a completed
GL lifetime ledger and not a memory-saving device change.

## Artifact

runtime/lamentum-adapter.patch now carries native/lc2_lifetime.h, a standalone
C11 bounded state machine with no GL calls, heap allocation, environment switch,
or runtime callers. The existing nvn_texture/GL paths are unchanged. The public
host test extracts and compiles this exact header FROM THE OVERLAY, not from a
private source checkout.

Each committed storage entry has a unique monotonic storage token and a separate
object-generation identity. Object namespace is explicit (share group, kind,
GL name); respecification shares object generation but gets a new storage token.
Deletion/name reuse creates a fresh object generation. A pending allocation
cannot silently be replaced. At most64 storage slots and64 timeline identities;
capacity/uint64 overflow returns refusal without inventing an untracked owner.
Caller-supplied payload bytes are checked logical intents, not Mali residency.

Transitions:

- begin: reserve intent before allocation, no committed-byte credit yet;
- commit(success): transfer reservation into retained logical payload;
- commit(failure): roll back only pending intent, not older storage or physical RAM;
- attach/detach: views reference the SAME storage token, with no second byte charge;
- use: validated timeline and monotonic submission serial, disallow already-completed serials;
- retire: mark a candidate, do not decrement retained payload;
- can_delete: only retiring + zero views + completion covering last reader, valid group;
- deleted(success): reduce logical retained payload only after permitted deletion receipt;
- whole-share-group loss: invalidate entries but retain unresolved accounting.

The caller must serialize operations and supply VERIFIED share-group/namespace,
GL success and completion receipts. A true input flag is not independent evidence:
no production caller exists yet and no GL/EGL proof is claimed by these tests.
Contexts must not be treated as share groups by raw pointer equality.

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

Test initially failed because the overlay header was absent. A second explicit
red/green test caught a newly submitted reader reusing an already-completed
serial; the implementation now refuses it.

The extracted C fixture compiles with -std=c11 -Wall -Wextra -Werror and
-fsanitize=undefined -fsanitize-undefined-trap-on-error, then executes real
assertions for generation reuse, shared views, name namespace/share group,
allocation failure, unknown/stale token, in-flight reader, failed/lost fence,
completion regression, failed deletion, storage respecification, group loss,
capacity and uint64 overflow. Trap mode avoids depending on a missing host
libubsan.so; sanitizer checks are not disabled.

Full clean-export host suite265 PASS, Python3.10 AST check. Runtime build/deploy
NOT performed for an unreferenced header; installed build241 remains unchanged.
No new handheld run, memory reduction, FPS comparison or cleanup claim belongs
to this packet. Prior sampler-census device receipts remain historical.

## Next integration gate

Wire observation-only successful/failed storage events and exact object/share-group
generations into the real allocation paths, then alias-resolved readers and
completion. Audit every reachable GL storage/delete and exceptional exit path;
unknown/overflow must invalidate accounting, not stop a healthy title or permit
free. Validate real GL-name reuse, respecification, shared contexts and lost
fences on Mali before any ledger-controlled deletion/admission change.

Safe menu headroom, navigation/world, audio/save and30 FPS remain OPEN.
