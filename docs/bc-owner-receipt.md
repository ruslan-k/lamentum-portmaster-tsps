# B1: pre-refusal descriptor for a deferred-BC first-use owner (roadmap 32.4)

Component step under **§32.4 / PR B1**. Starting upstream **5ed8462**; previous
work §34 (upload triples). No budget, floor, swap or `alias_physical` change, no
game data read, and no device run in this step.

## Why a receipt before the charge

The budget refusal terminates the process, so the one thing needed to choose a
fix — *which* resource, with what descriptor, at what prospective cost — is
destroyed exactly when it becomes interesting. `lc2_bc_owner_receipt()` is called
immediately before `t2_texture_budget_add()`, so the record exists even when the
charge is refused.

## Contract

- Opt-in: `LC2_BC_OWNER_RECEIPT=1` (checked by value, so `0`/unset disables it).
- Bounded: at most **8 owners per run**; further owners set
  `lc2_bc_receipts.overflow=1` instead of growing any structure.
- Exactly once per owner id, so a repeated sampler bind cannot flood the log.
- **No guest memory is read**: no `nvn_pointer()`, no `memcmp()`, no content hash.
  Source facts are limited to adapter metadata; content identity stays
  `source-hash=not-read`, immutability `unproven`.
- Fields that do not exist yet say so (`phase=unavailable`,
  `present-serial=unavailable`, `storage-generation=untracked`,
  `driver-physical=unknown`, `gl-allocation=not-attempted`) rather than carrying a
  misleading zero.
- Emitted: run UUID, view/owner ids and objects, alias flag, NVN target/format/
  swizzle/flags/samples/dimensions/levels, block bytes, upload type, output
  bytes-per-pixel, prospective charge, already-charged owner bytes, budget
  live/peak/charges, guest storage bytes, pool object/address/size/generation/
  flags/offset, snapshot generation, GL name, depth buffer, draws, target-seen,
  references, caller, and a per-level `width/height/decoded-bytes` list.

## Verification

`tools/test_bc_owner_receipt.py` (4 tests) extracts the receipt body from the
public overlay and compiles it against stubs:

- disabled/`0` → nothing emitted, `1` → emitted (env read by value);
- three calls for one owner → exactly one record, with every required field
  present, including `prospective-charge-bytes=268435456`,
  `decoded-bytes=268435456` and `caller`;
- 40 distinct owners → 8 records and `overflow=1`;
- the body contains no `nvn_pointer(`/`memcmp(`;
- in the admission function the receipt call precedes `t2_texture_budget_add(`.

Full suite **170 tests PASS**; baseline **435/435**; ARM64 **build-229**
`b164cffd80bd0284fb6f86907db3825d63c0e1bf2d3f5a7a90f703fa0db4e82f`,
helper `abe8e484…` unchanged. `build-229` is **not deployed**.

## Still open in PR B

- The receipt cannot fire until a run actually reaches the id295 first use, which
  needs the guarded New Game arm of §32.2 and a verified navigator (§32.7).
- Content identity, immutability and render-target usage stay unproven; hashing the
  atlas is an offline, owner-private step, not something to do under pressure.
- B2 (all-class GL ownership ledger with transactional lifetimes) is untouched.
