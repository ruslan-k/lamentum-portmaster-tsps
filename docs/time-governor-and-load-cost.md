# The guest time governor does not stop this title (measured), so the harness bounds it

Roadmap: §22.4 (attribute the guest cost before optimizing it) and §20.2-20.3 acceptance
gates. This note records a defect in the test instrument, its measurement, and the host-side
bound that replaces it. It is not a performance result.

## What was measured

`newgame-17` (build217, `--budget 1800`) navigated the real menu, the New Game configuration
page, the control page and the load, then stayed on the load screen to the end of the run.

Facts from that run:

- `NATIVE_PROBE_TIME_BUDGET seconds=1800` was parsed and `alarm(1800)` armed at start.
- No `STOP status=` of any kind appeared, including `TIME_LIMIT`, although the guest main
  thread had accumulated **2599.7 s** of CPU (well past the budget) before the harness ended it.
- Presented frames reached 2176; the run had to be terminated by the operator with
  `kill -TERM <game pid>`.
- After that termination: game absent, `MainUI` back, `principal.sh` and `runtime.sh`
  identities unchanged, CPU online mask `0-7` restored, and a fresh kmsgrab shows a fully
  lit Spruce menu (every sampled pixel non-black).

So the earlier statement "the run ends by TIME_LIMIT + cleanup" holds for shorter budgets on
earlier builds, but is **not** guaranteed: a title that blocks or never returns to a point
where the signal is handled keeps running past its own limit. A test instrument whose only
stop is inside the code under test is not a bound.

## The fix in the harness, not in the title

`tools/device_principal_test.py` now keeps a host-side bound at `budget + 120 s`. When it
expires it reads the live process table and terminates **only the exact game pids** it just
observed - never `principal.sh`, `runtime.sh` or `MainUI`, so the Spruce principal flow still
restores the menu. The outcome is recorded as `host_terminated` and returns exit code **6**,
distinct from `0` (title's own `TIME_LIMIT`), `4` (guest fail-closed stop), `5` (rejected
harness parameter) and `3` (dirty cleanup). `tools/test_device_principal_hard_stop.py` pins
the predicate: no deadline or no live game means no kill.

## What the load actually costs (the number that matters for 30 FPS)

A 20 s delta taken during the static load screen, on the running game:

| Measurement | Value |
|---|---:|
| presented frames per second | 1.14 |
| main-thread CPU per presented frame | **0.836 s** |
| total thread CPU per presented frame | 1.63 s |
| new `ROMFS_READ` calls in the window | 0 |
| new textures / texel writes / BC deferrals | 0 / 0 / 0 |
| new `NVN_COMMANDS_EXECUTED` | 1 |

The guest is not loading assets and not drawing; it burns almost a whole core on the main
thread and presents an unchanged frame. 30 FPS needs 33.3 ms per frame, i.e. about a 25x
reduction of that single-threaded work, and shader-catalogue or replay work cannot supply it.

## Next measurement (instrumented, not guessed)

The runtime already carries a bounded guest-stack sampler: `MOMO_STACK_SAMPLE_MS`,
`MOMO_STACK_SAMPLES`, `MOMO_STACK_SAMPLE_AFTER` (SIGPROF round-robin over live guest threads,
printing `MOMO_SAMPLE ... pc=<seg+off>` plus the guest frame chain). `tools/analyze_guest_samples.py`
buckets those samples by interrupted PC and caller frame, keeps unresolved locations as raw
`<seg>+0x<off>` strings, and never invents a symbol; six host tests cover it.

The next device run samples the steady-state loop with a bounded count and does not need any
catalogue change. Its outcome decides whether the 836 ms/frame is a removable adapter/guest
path or intrinsic Unity/IL2CPP work - and therefore whether "30 FPS" is a target or a ceiling
to document.
