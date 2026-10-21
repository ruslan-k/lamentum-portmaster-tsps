# T1 partial: owned exec, log generation and observer boundaries

Reviewed roadmap **§29.6**, including its explicit requirement not to mix old
latest.log records with a new run. Starting upstream: **0caf515**. This is an
identity/safety component, **not T1 completion or gameplay/30 FPS acceptance**.
Before publication, fetched and fully reviewed owner revision **5ed8462**, including
new **§32.7 / PR E**, and merged it without overwriting the owner's §32 plan.
This component is recorded in **§33**; §32's execution priority remains authoritative.
Its next correctness item is **§32.3 / PR A**, the GLES3 sRGB upload contract.

## What changed

### Producer: UUID + pinned FD exec, before native performance records

`tools/run_identity.py` is a mandatory paired launcher helper, copied to build
output as `run_identity.py` and installed beside `lamentum-nextos`.
`port/Lamentum.sh` keeps its existing CPU restore trap and invokes this helper as
its child; the helper replaces **itself**, not the parent shell, with the runtime.

- The principal harness obtains the run UUID from the **target kernel's**
  `/proc/sys/kernel/random/uuid`, passes it explicitly, and writes a host
  `expected-run.json` before MainUI handoff. Non-probe menu launches obtain a
  fresh kernel UUID in the helper. No wall-clock second is an ownership token.
- A separate fresh kernel `launch_nonce` distinguishes individual bootstrap
  executions even if someone explicitly reuses a supplied run UUID.
- The first log record is `LAMENTUM_RUN_HEADER` JSON: schema, UUID, nonce, boot,
  PID/starttime, opened executable dev/inode/bytes/SHA-256, launcher SHA-256 and
  helper SHA-256. Complete header output is flushed **before exec/native logs**.
- The executable is opened without following symlinks, hashed through that FD,
  checked for metadata changes during hashing, then executed with
  **os.execve(fd)**. There is no pathname-exec fallback. PID/starttime survive
  exec; the observer separately verifies `/proc/PID/exe` after exec.
- Full UUID is exported as **LAMENTUM_RUN_UUID**. **COTM_RUN_ID remains a decimal
  label <=12 characters**: recovered `diagnostic_dump.h`, `audren_voice.h`,
  `audren.h` and `nvn_present.h` reject a hyphenated UUID. A decimal prefix-derived
  label preserves that ABI but is **never used as the unique ownership key**.

**Deliberate unknowns:** `image_sha256=null`, `catalogue_sha256=null`,
`content_bindings_complete=false`. The existing build/image pins are not replaced
with made-up current-run hashes. A verified image/catalogue deployment binding is
still required. SHA-256/dev/inode identity is not a digital signature or a proof
against a malicious concurrent writer.

### Consumer: opened-file generation + append-only continuity

`load_metrics.py` serializes the **actual tested parser/collector functions** into
its remote request. Strict mode requires the expected run UUID/build metadata.
Legacy parsing is retained for historical evidence and tests, explicitly with
`log_identity_qualified=false`.

Every owned poll checks:

1. Opened file's dev/inode and size against the byte cursor.
2. Complete bounded first header (8192-byte maximum), its identity fields and
   hash against the previously accepted generation.
3. A SHA-256 continuity anchor over up to the last **256 consumed bytes**.
4. Header and cursor boundary again before publishing parsed counters.
5. No second run header in the consumed body.

A changed UUID, nonce, PID/starttime, executable hash/inode, file replacement,
truncation or rewritten anchor refuses with **LOG_GENERATION_CHANGED**. Strict
`fold` raises instead of resetting/adding another run. A partial header may be
pending only **before attachment**; truncating an already-owned header cannot
silently downgrade the cursor to pending and reset its counts.

Reads are bounded to **262144 bytes per poll**. Only newline-terminated raw-byte
records advance the cursor; invalid/split UTF-8 cannot move offsets. Backlog
(`unconsumed_bytes`) is separate from the split record at the current read
boundary (`partial_bytes`). A fixture containing **30000 ROMFS records** drains
across bounded polls with the exact total preserved.

This is an **append-only producer contract**, not a full cryptographic audit of
every earlier byte against arbitrary edits outside the header/anchor. A correctly
bootstrapped new execution must always emit its fresh UUID/nonce. Do not promote
the bounded anchor into a stronger tamper-proof claim.

### Harness and control boundaries

- `device_principal_test.py` preflights the installed ELF/launcher/helper through
  opened-file hashes and requires the launcher/helper to match the repository.
  It refuses a busy device before touching logs or launch state; it no longer
  truncates the previous log itself.
- The exact principal command is read back before the normal menu handoff.
  The Emu/PORTS standard-launch path and principal cleanup remain authoritative.
- The observer attaches only after the expected header and live post-exec
  dev/inode match. PID/starttime alone no longer qualifies a changed executable.
  Existing VFAT os.path.samefile discovery remains in place; no lowercasing or
  process-name ownership shortcut was added.
- Both the intentional MainUI handoff and game hard stop use a generation-checked
  **pidfd**, with no unowned numeric-PID TERM fallback. The target Python lacks
  pidfd wrappers; the AArch64 syscall ABI was rechecked against the pinned
  cross-toolchain. Unsupported pidfd paths fail rather than choosing another PID.
- Final records are re-read through the **same owned complete-line protocol**;
  raw cat/tail cannot substitute a later run's log. Rejected/incomplete final
  evidence cannot produce success: observer failure has distinct harness **9**.
- `load_probe.py` waits for the principal-owned header/executable before enabling
  controls. The pad/capture boundary checks the owned boot/PID/starttime/ELF
  before an injected press and around KMS capture. This remains agent injection,
  not proof of physical human input.
- Device selection is explicit via **LAMENTUM_DEVICE**; SSH bypasses stale
  multiplexing. No new device address is hardcoded in these control paths.

## Navigation is NOT fixed by identity

The two old navigators still lack a shared semantic configuration/controls/world
oracle. Their blind configuration presses/content-change/bottom-anchor behavior
is **disabled by default** in both CLIs, before a launch or input action. It can
only be invoked with the explicitly diagnostic `--allow-unverified-navigation`.
That switch does not qualify a phase; the old standalone walker no longer emits
`reachable=true` or claims controls were accepted from content change alone.

Do not use this diagnostic switch to pass T1 or claim a world scene. Remaining
work is the **single semantic MAIN_MENU -> NEWGAME_CONFIG -> CONTROLS -> LOADING
-> WORLD_OR_STOP state machine**, row + page/prompt identity, new present serial,
press/release receipts and dropped/duplicated press tests. Existing fixed bank,
shader and renderer contracts are untouched.

## Actually executed validation

- **159 host tests PASS**, including compiled self-authored native exec fixture,
  real helper UUID/PID/dev/inode/hash propagation, numeric legacy ABI, CPU mask
  restoration and exit 7 through the actual shell launcher.
- A real host child receives no signal for a deliberately mismatched starttime;
  the matching child is then terminated through the exact generated pidfd RPC.
  No unrelated process is signalled by this test.
- Real serialized collectors are exercised against same-inode truncate/regrow at
  greater size, equal/greater-length inode replacement, changed executable or
  PID generation, rewritten cursor anchor, partial headers/UTF-8/records and
  bounded multi-chunk backlog. Synthetic RPC integration separately preserves
  TIME_LIMIT / unknown SIGKILL / matched kernel OOM taxonomy and rejects a
  replaced final log. **Those RPC/OOМ fixtures do not induce a real device OOM.**
- Shell syntax passes. Changed Python transport modules parse as Python **3.10**.
- **Build227 succeeds**, with **435/435** baseline verification, non-root pinned
  AArch64 builder and byte-verified packaged helper. Native overlay and shader
  catalogue are unchanged from G0 build226. ELF SHA-256:
  `58b2ae65e5a98541995582f0a6d1e47c27954dab7dec041e77ad2a40cceb8f5e`.
- Clean curated export repeats **159 tests** and the full **435/435** rebuild;
  the packaged helper and both **PT_LOAD** segments match. Whole unstripped ELF
  SHA values differ, so byte-reproducibility is not claimed. The first export
  caught an omitted `test_launcher.py` helper-fixture update (exit 1, expected
  fixture exit 7); staging that update and rerunning resolved it without bypassing
  the product's missing-helper refusal. Full receipt: `publication-verification.json`.

### Read-only TSPS checks, not a game test

Actual target reports **Python 3.10.4**, FD-exec support, no Python pidfd APIs.
Pinned headers report pidfd_open **434**, pidfd_send_signal **424**. A target
self-pidfd **signal 0** probe succeeds; it does not terminate any process.
The exact strict collector executes on that Python and rejects the installed
old-header log, consuming **zero** performance counters instead of adopting it.

At the read-only snapshot: **MainUI=1, principal=1, runtime=1, game=0**, CPU online
**4-7**. This is process state, **not a newly captured physical menu proof**.
Observed installed ELF SHA-256:
`86649c51854e4017fdbaddab16b7c53d327fb6a138c45c1106275c67a1727815`.
New helper is absent. **No launcher/helper/runtime was deployed; no game launched;
no device file was written in this step.** Read-only receipts are in
[evidence/T1-owned-log](../evidence/T1-owned-log/README.md).

## Deployment/acceptance boundary

A future authorized paired install must back up and independently verify both
`port/Lamentum.sh` and `build/run_identity.py` beside the runtime. Installing the
new launcher alone intentionally refuses with LAMENTUM_RUN_HELPER_MISSING before
CPU online changes. The principal harness also refuses stale/mismatched helpers.

The new launcher/harness have **host fixture validation, not a real principal
New Game acceptance run**. Content binding, semantic navigation, all-class GL
lifetime ledger and exact id295 source/descriptor remain open. First finish those
gates, then use the one combined guarded G0/T1/C0 New Game arm from §29, not
another menu-only timeout. No gameplay or FPS improvement is claimed.
