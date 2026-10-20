# HID input: guest-read evidence and correction of the accessor analysis

The port has reached the title screen, but gameplay/input is not yet verified.

## Correction: the +0x18 pointer table is NOT in shared memory

The earlier version of this document confused two different objects. Its claims
that a zero shared-memory head was a defect, that SDK10.9 needed a different
Npad layout, and that broadcasting had ruled out routing were not justified.
Those claims are withdrawn. Build196's `LC2_HID_SDK109` experiment did not fix
input; build199 removes its writes from the publisher.

The missing step was the SDK's `NpadSharedMemoryAccessor::Attach` at
`sdk+0x208370`. It takes `this` in x0 and `SharedMemoryFormat*` in x1, retained
as x19 and x20. After successful IPC, its stores are:

- private accessor `this+0x18+8*i` <- `shared+0x9a00+0x5000*i`, i=0..9;
- `GetInternalState` indexes that PRIVATE table, not the shared-memory head;
- FullKey count/tail/first slot are at entry+0x40/+0x38/+0x48;
- Handheld count/tail/first slot are at entry+0x390/+0x388/+0x398;
- the existing publisher's ring base entry+0x28, stride0x350, slot stride0x30
  matches those offsets: the Handheld ring is ring1.

The table in build196's experiment at `shared+0x18` is therefore unrelated.
A zero there never established that the guest read a NULL Npad pointer.

Reproduce the ten exact accessor stores (read-only, hash-pinned SDK input):

    python3 tools/inspect_hid109_attach.py OWNER_IMAGE_DIR

`evidence/hid-watch-region-01/sdk-accessor-contract.json` is the generated
receipt. It contains offsets and the SDK hash, no game binary or key material.

## Guest reads are now directly observed

`LC2_HID_WATCH=1` protects the guest's read-only 0x40000 mapping with PROT_NONE.
The host writes through a different mapping of the shared object, unchanged.
On first access to a page, the signal handler restores PROT_READ and logs the
fault address and guest PC. This is diagnostic only; it changes neither game
instructions nor HID content. Build199 uses a bounded stack log plus write(),
not stdio in the signal handler, checks restoration failure, and does not
swallow later faults on an already-restored page.

Build198, `evidence/hid-watch-region-01/latest.log`, records:

- shared mapping at 0x6710604000, size0x40000;
- style reads at SDK+0x208814 for all ten canonical entries (including
  shared+0x9a00 and shared+0x31a00);
- a read at shared+0x32008, SDK+0x208ce4. Disassembly identifies it as the
  Handheld reader's slot-sequence load, not FullKey and not the region head.

Thus the guest DOES consult the canonical shared-memory entries and the
Handheld state path. First-page-only watch build197 recorded no fault because
none of these accesses touches page0. That negative result said nothing about
the rest of the region.

The watch is first-access-per-page, not a per-frame trace. It does not prove
that any particular pressed button was consumed, nor whether all state types
are read later on pages already restored.

## What earlier input tests actually established

- The physical SDL provider opens `TRIMUI Player1`, GUID
  `0300a3845e0400008e02000014010000`, /dev/input/event4.
- Injecting Linux BTN_SOUTH (0x130) produces guest buttons0x2, i.e. Switch B,
  not Switch A. BTN_START (0x13b) produces buttons0x400.
- Earlier 140ms injections produced no demonstrated menu transition. A short
  press at low frame rate can be missed; host publication is not consumption.
- `LC2_HID_BROADCAST` forced FullKey style even on the Handheld entry. Its
  negative visual result did not exclude a style-dependent routing issue.
- No asset reads or texture initialization after frame~200 in the previous
  long run supports an idle title scene, but says nothing about menu readiness
  or the correctness of its input gates.

## Next bounded input measurement

Build199 keeps the canonical publisher, removes the unrelated head-table
experiment, and can watch the region independently. Compare long (1500ms)
BTN_EAST/SOUTH/WEST/NORTH/START presses with and without the existing
`MOMO_NPAD_HANDHELD=1` diagnostic. Require a real in-run DRM capture, numerical
image comparison and guest/host receipts before claiming a menu transition.
Do not call diagnostic routing a shipping fix without a matched control.

Completed on the same build199 binary (1500ms holds, five-button sweep):

| run | final presented frame | stop | mean capture luminance range | visible menu |
|---|---:|---|---|---|
| hid-long-fullkey-01 | 681 | TIME_LIMIT | 3.717–3.819 | not demonstrated |
| hid-long-handheld-clean-01 | 648 | TIME_LIMIT | 3.688–3.738 | not demonstrated |

Both collected device states report runtime=0, MainUI=1, CPU0–7 online.
The separate `hid-long-handheld-01` is contaminated by debugging: a first GDB
attach stopped at an unrelated runtime SIGTRAP, not the requested load. A
second attempt passed an execution-breakpoint trap into the adapter, causing
UNKNOWN_TRAP at SDK+0x208cf4. Neither GDB dump proves consumption of a button.
Do not count harness exit0 as a successful game run. The clean repeat above
contains no debugger and ends at TIME_LIMIT.

The earlier short button timing is therefore not the whole explanation.
Direct tracing of menu initialization is documented in `menu-initialization.md`.

## Host regression

    cc -Wall -Wextra -Werror -I ADAPTER/native tools/test_hid_watch.c -o TEST
    TEST

This actually triggers SIGSEGVs on three mmap pages, checks first access,
repeat reads, bounds rejection and that a later fault on a restored page is
not swallowed. A passing test proves watch mechanics, not game input.
