# T1 real-device acceptance slice: main-menu controls, discovery failure and verified correction

## Scope / current roadmap

Two sequential principal-flow **menu-only** runs of the unchanged build219 executable, each with
requested 120-second diagnostic budget, texture cap 300 MiB and fileback cap 512 MiB. No New Game,
quality/asset change, gameplay or FPS acceptance test. Both were allowed to finish before another
run began; saves and ELF/launcher backups were verified beforehand.

During this work origin/main advanced to `db2f197` with roadmap §27 and
`docs/build219-gameplay-performance-action-plan.md`. Those documentation updates were read and
merged, retaining the new priorities: remaining T1 integration, then direct C1 SVC/service-cost and
G1 resource-owner evidence. Do not interpret more menu timeout tests as runtime optimization.

## Pinned identity and safety

- ELF unchanged throughout: `b8407822b205b0012401ed327a82f9ae94e31344a0bfc1d77ccdc1f7b798df4a`.
- Launcher unchanged: `ae7622b858c1481ca73bfc6026b2dc317255d8f8d947373d0692297a531f978d`.
- Owner RomFS section: `80ad4427164a0b7ad61c3a3fcd955bd158635aac1ee42ebb67d01dfae279b893`.
- Every deployed NSO segment hash, section size and host catalogue hash were recorded in
  [arm 1 identity](../harness-live-01/identity.json); no image/runtime deployment occurred between arms.
- Arm 1 ran source `e19a9b9`; arm 2 ran source `b2b08bd` (the discovery-only host fix).
- Original PlayerPrefs save archive, ELF and launcher copies remain owner-private under
  `/home/ruslan/lamentum-work/private-backups/harness-live-01` and `harness-live-02`.
  Archive member SHA-256 values were compared to the live save tree. Before arm 2 and after arm 2,
  save hashes still matched the initial arm 1 baseline. No save contents are published.
- SD free before testing: 1,453,162,496 bytes; retained 512 MiB fileback envelope. Floor 32 MiB is
  explicitly diagnostic, not a release-default qualification. Original CPU mask was `0-7`.

## Arm 1: real instrument defect, not a successful process-identity validation

[Summary](../harness-live-01/summary.json),
[live menu capture](../harness-live-01/live-early.png),
[capture receipt](../harness-live-01/live-early.json).

The game was alive as PID 25030, starttime 6258404. A live owned-PID KMS capture showed the actual
Lamentum main menu (Load game/New game/Options/Credits, Load game highlighted). The newly tightened
proc discovery nevertheless returned `absent`; the harness's process_identity remained null.
Explicit-PID read-only samples could read that same live process. This arm therefore **failed the
discovery/identity part** of T1, although the runtime ended with TIME_LIMIT, harness status 0 and no
cleanup errors. It recorded 143 presents / final frame 143. Frame counts are not world FPS.

Live inspection found that `/proc/25030/exe` used `Roms/ports` while expected `.resolve()` used
`Roms/PORTS`. Case-insensitive VFAT resolved both to the same file, but Python Path string equality
rejected the differing spellings. No binary or mapping was missing.

Arm 1 ended before code was changed. MainUI restoration was independently captured in
[clean-menu.png](../harness-live-01/clean-menu.png), not mistaken for an in-game frame.

## Corrective change and regression test

`tools/proc_metrics.py` now uses `os.path.samefile` (device/inode identity) for the actual executable.
It does not lowercase/repair identifiers, accept comm alone, or accept a byte-identical copy with a
different inode. A hard-link fixture reproduces two unequal resolved strings naming one inode:
the test failed as `absent != exited` with the old comparison, then passed with samefile. Replacing
one alias with a separate file containing identical bytes must be rejected.

`runtime_path` is an optional fixture seam; the production runtime path is unchanged. The actual
remote payload still serializes the tested functions rather than a separate parser implementation.

## Arm 2: verified correction on the real runtime

[Summary](summary.json), [samefile proof](samefile-proof.json), [live menu](live-menu.png),
[capture receipt](live-menu.json), [raw read-only samples](live-samples.json).

- Real paths differed exactly as above; both reported dev/inode **45833 / 1419037** and
  `samefile=true`.
- Automatic discovery and the harness both bound PID **26581**, starttime **6286020**, boot
  `aedf014d-52ea-4c4c-8c42-f6650c7f8a91`; harness identity_errors was empty.
- Target HZ remained 100. CPU deltas were collected from target ticks/monotonic time, with complete
  thread/fault/schedstat receipts. These are diagnostic **menu** CPU data, not Loading ownership or
  gameplay throughput. No source has yet attributed exclusive SVC or IPC executing cost.
- Twelve memory/log samples were bracketed by live reads of the same pinned process before and
  after the remote collection. Minimum MemAvailable among those samples: **61,740 KiB**. A final
  unavailable-process sample was excluded rather than counting freed post-exit RAM as headroom.
- Completed with `STOP status=TIME_LIMIT`, termination kind `runtime_timeout`, harness status 0,
  host_terminated=null, cleanup_errors empty. Final frame/presents: **136 / 136**. This must not be
  compared to arm 1 as an FPS win/loss: diagnostics/capture timing were not a quiet matched benchmark.
- Game absent afterward, MainUI/principal/runtime counts each one, CPU mask restored `0-7 -> 0-7`.
  The actual awake Spruce Recents display was captured in [clean-menu.png](clean-menu.png).
  It contains a stored preview thumbnail for the selected recent item, not a running second game.
- [After-integrity](after-integrity.json): ELF, launcher and all save hashes unchanged.

## Verification and publication boundaries

`python3 -W error::ResourceWarning -m unittest discover -s tools -p 'test_*.py'`: **98 tests PASS**.
The final raw runtime logs were parsed separately: present-event count matched final serial in both
arms; the genuine TIME_LIMIT STOP was not confused with kernel OOM or an operator kill. Raw full
runtime and kernel logs stay owner-local; only selected counters, identities, receipts and verified
screenshots are published. No game assets, shader blobs or save data are included.

The documentation update also corrects the older `docs/load-cpu-attribution.md`: 387/400 round-robin
thread samples are 96.75% of samples, **not executing CPU time**. Neither those fractions nor diversity
of raw argument words proves a hot bridge routine, rules out a stall, or identifies endpoint0x40.
The raw counts are preserved; unsupported causal conclusions are withdrawn per roadmap §27.

## Acceptance status

This closes the **menu-level real-runtime discovery regression** and exercises the recent target
CPU observer/exit-classifier against the actual game with independently verified cleanup. It does
not close full T1: run UUID across every collector, byte-continuity through same-inode regrowth,
cryptographic launch binding, semantic configuration-page transitions and complete load-phase
acceptance still remain. No new native runtime optimization, world draw, physical player movement,
audible sound, cold save/load or 30 FPS result was produced. Follow the updated C1/G1 measurements;
do not choose a renderer, texture policy or synchronization shortcut from these menu samples.
