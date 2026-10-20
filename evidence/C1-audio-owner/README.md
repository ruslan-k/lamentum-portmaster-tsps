# C1: endpoint0x40 is AudioOut; opcode-specific mutex operands recovered

## Result and scope

The frequently logged `endpoint=0x40` is **not an unknown guest handle or an unidentified polling
service**. It is the adapter enum tag **EP_AUDOUT**, the AudioOut child returned by **audout:u**.
For that child, command 7 appends a PCM buffer and command 8 retrieves released buffer tags.
This is a source/ELF-pinned identification backed by existing real-run acquisition/open/IPC receipts.
It is **not** proof that audio IPC dominates executing CPU, a stalled loader, audible sound, or FPS.

No native runtime code, installed ELF, assets, safety limits or device state were changed in this
work. No additional menu/Loading timeout run was needed to establish this identity.

## Reproducible binding, not a guessed numeric service ID

`tools/audit_audio_endpoint.py` was executed on the real retained build218/build219 ELFs and four
captured logs. It:

1. Requires the exact supplied ELF SHA-256 and exactly one matching LAMENTUM_BUILD_ID in the
   captured log; wrong pins, mismatched IDs and concatenated run headers fail before source/compiler access.
2. Checks the working adapter diff is byte-equal to checked-in `runtime/lamentum-adapter.patch`.
3. Checks `ipc.h`, `audout.h`, `guest_profile.h`, `loader.c`, and `threading.h` against the retained
   `build-218/source/native` or `build-219/source/native` input next to that ELF. These relevant files
   are byte-identical across the two builds; the overall ELFs remain correctly distinguished.
4. Compiles the **actual unconditional C enum** with host cc and executes only that self-generated
   enum probe: EP_AUDOUT_MANAGER=63 (0x3f), EP_AUDOUT=64 (0x40). It does not execute the ARM64 game
   or infer an enum ordinal by counting in prose.
5. Verifies the reviewed service/dispatch/argument source shapes, emits file/overlay/log/ELF hashes,
   and counts only complete newline-terminated event receipts from the real captured logs.

Source chain reviewed in the matched inputs:

- `native/ipc.h:12–22`: endpoint enum; `:62–75`: session validates/stores its endpoint metadata.
- `ipc.h:279–314`: `sm_lookup("audout:u") -> EP_AUDOUT_MANAGER`.
- `ipc.h:501–515`: CMIF service request allocates the manager session; requests alone are not proof
  of successful acquisition, so the tool labels their count `service_requests`.
- `ipc.h:365–389`: the printed `endpoint` is resolved session/domain **enum metadata**, not the guest
  `handle` printed in the separate field.
- `native/audout.h:148–167`: validated open creates `ipc_child(...EP_AUDOUT...)`, stores generation,
  returns the moved child and prints AUDOUT_OPEN.
- `audout.h:171–192`: generation-checked AudioOut child, command7 append via `aout_push`, command8
  release retrieval via `aout_release`. No synchronization or return semantics were bypassed.

The retained logs show audout:u requests, manager traffic at endpoint0x3f (handles 0x459/0xc59),
one AUDOUT_OPEN, then child traffic at endpoint0x40 (handle 0x45a in these particular runs).
The numeric handle is a per-run handle-generation value, not a universal service identifier.
Selected startup receipts and all pins are included in each JSON; full private logs are not copied.

## Actual census (different phases, not a performance comparison)

| captured arm | build / phase | AudioOut cmd7 appends | cmd8 release queries | actual mutex-address count |
|---|---|---:|---:|---:|
| load-probe-08 | 218, startup/New Game/Loading until budget stop | 10,376 | 29,140 | 41 |
| load-probe-10 | 219, startup/Loading until operator TERM | 16,567 | 47,698 | 36 |
| harness-live-01 | 219, startup/main menu | 4,466 | 11,826 | 39 |
| harness-live-02 | 219, startup/main menu | 4,513 | 12,001 | 45 |

All four have two logged audout:u service requests and one successful-open receipt; the exact
startup request types differ from child data operations. Do not treat raw manager command numbers
as data-command semantics without their CMIF/control type. No malformed parsed rows were found.

Audio host counters include underruns and nonzero PCM. The audit sums interval consumed/underrun
counts but takes the maximum cumulative `nonzero-total`, not its sum. Nonzero PCM and consumed
buffers do **not** establish audible output on the handheld. Nor do counts alone show that a
release query is a mistaken busy wait: normal playback must append and retire buffers.

## Important correction: the earlier 1,011 "keys" were not mutex addresses

Matched dispatcher code explicitly calls:

    svc 0x1a: mutex_wait(r[1], r[0], r[2], pc)
    svc 0x1b: mutex_release(r[0], pc)

`threading.h:149–166` establishes the first function argument as the mutex address. Thus the address
operand is **X1 for ArbitrateLock, X0 for ArbitrateUnlock**. Combining X1 from both opcodes mixed
actual lock addresses with an unused unlock register. In load-probe-08, all 1,493 occurrences of
unlock X1=`0xffffffff` are **not the unlock mutex operand**; no sentinel semantics need be invented.

Reprocessing the actual full log with the correct operands yields **41 distinct mutex addresses**,
not 1,011. SVC counts remain exactly 5,506 lock / 5,389 unlock. Top combined addresses:

| address token | logged calls |
|---|---:|
| 0x34073d08c | 4,638 |
| 0x340000048 | 2,073 |
| 0xb0b40e0 | 2,027 |

These counts still do not prove acquisition outcomes, wait duration, ownership/wake correctness,
a relationship to AudioOut, or an executing CPU bottleneck. The tool preserves original tokens and
separates caller PC/opcode counts; it does not symbolize PCs without a same-run map.

## Reuse the existing profiler, but respect its gaps

`COTM_GUEST_PROFILE` and its strings are already present in build219. Source audit of
`native/guest_profile.h` and `loader.c:650–662` shows:

- In-memory calling-thread counters and jittered timing already use CLOCK_MONOTONIC and
  CLOCK_THREAD_CPUTIME_ID. No need to duplicate this instrument blindly.
- Only the **presenting thread's TLS** is printed/reset at the present boundary (`guest_profile.h:
  230–261`). Calls on other threads may be absent from reports; a missing audio bucket does not
  prove no audio work. Startup counters are dropped at the first present.
- SVC CPU timing starts after acquiring kernel_mutex (`guest_profile_locked`), and ends before the
  final gate/broadcast/unlock. It is not full trap-entry/return CPU cost or mutex-acquisition CPU.
- IPC buckets receive the same enclosing sampled-SVC timing (`guest_profile_end:201–202`). Those
  are **overlapping views**, not exclusive pure IPC timings; never add their costs to the SVC total.
- `ipc.h:388–389` currently labels AUDREN as AUDIO but **AUDOUT falls into OTHER**. Category OTHER
  is not proof of non-audio work. This audit does not silently change that runtime label.
- Existing rows provide sampled mean/max/counts, not the requested full P50/P95 or a complete
  contended/uncontended/result/wake ownership profile. The opt-in observer still needs an overhead
  A/B and extended coverage before choosing a fast path.

Therefore C1 service identification and opcode operand interpretation are advanced, but per-call
exclusive executing cost and dominant CPU ownership remain open. Do not globally skip locks, mute
or disable audio, fake completion, change clocks, or suppress valid buffer lifecycle operations.

## Verification

`python3 -W error::ResourceWarning -m unittest discover -s tools -p 'test_*.py'`: **105 tests PASS**.
`git diff --check`: PASS. The audit and CLI were exercised on the actual retained artifacts; no
synthetic service replies or fabricated latency data substitute for a device measurement.
Manual review against the current C1 plan and tool conventions; no independent subagent review ran.

- Host tests cover endpoint-vs-handle separation, incomplete/unrelated events, malformed rows,
  interval-vs-cumulative counters, correct lock/unlock operand selection, and wrong ELF rejection.
- The actual cc enum probe and full audit ran successfully against all four captured game logs.
- The actual CLI was also exercised for load-probe-08; `cli-load-probe-08.json` preserves its output.
- Public artifacts contain hashes and scalar event/contract measurements only. Original ELF,
  captures' full logs, PCM, owner assets and saves remain local.

Reproduce (owner-local paths; requires retained build input and cc):

    python3 tools/audit_audio_endpoint.py --adapter /home/ruslan/lamentum-work/adapter-src \
      --elf build-218/lamentum-nextos --log evidence/load-probe-08/latest.log \
      --expected-elf-sha256 034c8f963d7e6b3eb5a2d2e305e59c4e1d58756ced309b304252c2ff71e324c3

The next C1 measurement must cover the actual AudioOut caller threads, exclusive CPU/wall and
lock/return/wake paths, with same-run mappings and probe-overhead control, rather than claiming
another menu timeout as a performance win. G1's id295/GL lifetime ledger remains independently
required. Gameplay and 30 FPS are still not demonstrated.
