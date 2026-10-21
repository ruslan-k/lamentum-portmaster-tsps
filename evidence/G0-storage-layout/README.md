# G0 storage-layout component validation

Self-authored **host** fixtures and a pinned ARM64 build, not a game/device run.
Reviewed roadmap/main revision: **14d8f80**, §29.3 and §30.

Detailed report and remaining G0 acceptance gates:
[docs/g0-storage-layout.md](../../docs/g0-storage-layout.md).

Artifacts:

- `host-tests.json`: full 138-test suite result and pre-edit roadmap hash.
- `payload-cases.json`: compiled C results, seven synthetic explicit layouts,
  including every mip; no original asset or inferred id295 descriptor.
- `sanitizer.json`: initial missing-UBSan-library failure and the successfully
  executed compiler trap-on-UB alternative (12 tests).
- `build.json`: build226, baseline 435/435, container/source/ELF hashes;
  game executable **not deployed**.
- `publication-verification.json`: final clean-index export checks/rebuild;
  no private adapter checkout is needed for the exported host tests.

Two-mip 8192-square RGBA8 intent = **335544320 bytes**; the compiled actual
first-use helper rejects under the 300 MiB synthetic budget before the simulated
GL call site. Current runtime eligibility still admits only one mip. The fixture
budget/STOP collaborators are synthetic; it does not prove physical GPU storage,
global budget rollback or alias/context lifetime.

G0, T1, world activation, playable gameplay and stable **30 FPS remain open**.
