# T1 owned-run/log identity component

Starting upstream **0caf515**, roadmap **§29.6**; detailed scope:
[docs/t1-owned-log.md](../../docs/t1-owned-log.md).

This is **not a game/New Game run and not T1/FPS acceptance**.

- `host-tests.json`: full host suite, shell syntax and Python 3.10 transport syntax.
- `build.json`: build227, 435 baseline files verified, packaged helper hash,
  unchanged native overlay/shader catalogue; **not deployed**.
- `device-capabilities.json`: read-only actual TSPS Python/process/installed-hash
  snapshot. Execve-FD support is reported; the new helper is not installed.
- `target-protocol-probe.json`: AArch64 syscall numbers from pinned compiler,
  target self-pidfd **signal 0** success (no process terminated), exact generated
  collector on target Python rejecting the old-header latest.log with zero
  counters consumed. No device log/content was rewritten.
- `publication-verification.json`: clean curated-index export tests/build checks.

Owned header carries UUID/nonce, boot/PID/starttime, ELF dev/inode/SHA and
launcher/helper SHA. Image/catalogue bindings are explicitly **null/incomplete**.
Strict counter folding refuses log-generation changes; legacy parsing is marked
unqualified. Old navigator CLIs are disabled by default pending a semantic oracle.

Device was not launched, modified or used for another menu-only timeout test.
Real host signal tests target only the test's own child. RPC/OOM integration
fixtures are explicitly synthetic, not reproduced device failures.

T1 semantic navigation, content pins, complete G0/id295/lifetime ledger, playable
world/input/audio/save gates and stable **30 FPS remain open**.
