# C0 collector validation — self-authored CPU fixture, not a game performance result

Full analysis and withdrawn claims: [docs/c0-profiler-audit.md](../../docs/c0-profiler-audit.md).

- Pinned build225: 435/435 baseline files verified; overlay applied; AArch64 game and fixture
  built successfully. Exact source/header/catalogue/executable hashes are in `build.json`.
- Only `lc2-cost-fixture` and its separate test launcher were deployed. The game executable,
  game launcher, image and shader catalogue on the handheld were NOT replaced.
- Launch was through Spruce principal -> standard_launch -> fixture launcher. The fixture
  rejects a still-live MainUI, has an eight-second native alarm and contains no GL/audio/game
  data. Host waiting was independently bounded.
- ON/OFF returns: **0/0** (`result.json`).
- ON: **four retired thread generations, twelve rows**, synthetic completed wait/BC/release
  intervals **12/12/4**, balanced valid counters and complete coverage of these fixture calls.
- OFF: no profile rows. Clock metadata is emitted by the fixture itself, not the disabled
  profiler. CPU and MONOTONIC_RAW advertised resolution: **1 ns / 1 ns**.
- MainUI restored, original supervisor identities and **4-7** CPU mask preserved; no remaining
  fixture/game process. Game/launcher hashes unchanged. `cleanup-menu.png` is a live KMS
  screenshot of the restored Spruce icon menu, not an in-game image; nonblack pixels were
  measured as 921600/921600 using max-channel >16.

`on.txt` and `off.txt` are game-independent native fixture output, safe to publish. The parser
keeps every (report,TID,starttime,class) and does not sum cumulative snapshots. It explicitly
says overhead is not qualified. This validates collection/clock/nesting/tail contracts only;
no handler cost, Loading/world FPS, BC performance, physical input, audio or save claim follows.

Files: `build.json`, `principal-receipt.json`, `device-before.json`, `device-after.json`,
`on.txt`, `off.txt`, `parsed-on.json`, `result.json`, `boot-id.txt`, `launcher-receipt.txt`,
`cleanup-menu.png`, `cleanup-menu.json`. No private game assets or full kernel dumps.

`publication-verification.json` records the independent clean-export test/rebuild:
126 tests, 435 baseline checks, identical tested fixture/header hashes. The source export
does not require the private adapter checkout to run its host tests.
