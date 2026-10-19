# Evidence

One directory per bounded device run: `device-01/`, `device-02/`, … Each contains

- `run.txt` — what was deployed (exact hashes), the launch method, the budget, and the
  controlled stop or clean exit the run ended with;
- `latest.log` — the port log as the runtime wrote it (trimmed only if it is enormous, and
  then the trim is stated);
- the post-run device state check (MainUI back, no test process, CPU online mask restored);
- a DRM capture from the device's own `kmsgrab` when the run claims anything about the screen —
  `fb0` is not the scanout on this board, and an X11 screenshot of the game window returns
  black even when the game is fine.

Rules that apply to every entry:

- A controlled stop is not a frame and not a failure of the game: it is the runtime refusing
  to guess. Name the stop code and the caller.
- Never report a picture without a physical capture, and never report performance from a
  diagnostic build.
- Per-run claims must be traceable to a line in that run's log.
