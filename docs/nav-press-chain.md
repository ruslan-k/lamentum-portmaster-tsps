# First press → row chain, and the overshoot it measured

Roadmap **§32.7 item 3**. One bounded arm (`nav-chain-02`, build229,
`COTM_GL_ERROR_IGNORE=0`, `T2_TEXTURE_BUDGET_MIB=300`, diagnostic floor 32 MiB),
frames taken **inside** the run, input injected through the owner-checked pad
contract (evdev injection, not a human hand).

## The chain

| step | capture | oracle verdict |
|---|---|---|
| before | 134,434 B | `MAIN_MENU`, row **`load`**, cursor_y **442** |
| press `down`, hold 900 ms | — | — |
| after (7 s later) | 137,614 B | `MAIN_MENU`, row **`options`**, cursor_y **542** |

So one 900 ms press moved the selection **two rows**, not one. That is the
documented hold-length failure reproduced on hardware: at ~1 presented frame/s a
900 ms hold spans more than one guest sample, and the adapter's tap latch extends
the bit for a frame. The navigation core already reports this as `overshoot` and
refuses to treat it as two presses; the press length must come down (a frame-paced
tap), not the row arithmetic.

Two more facts from the same arm:

- The oracle read the live menu correctly **twice, at different cursor positions**,
  which is the first real evidence that the calibrated geometry generalises within
  the menu (not just the one frame used to calibrate it).
- The **present serial was not read**: the helper looked at
  `lamentum-switch/latest.log` while the runtime writes
  `lamentum-switch/logs/latest.log`. The press therefore is **not yet
  serial-qualified**. The reader is fixed in `tools/load_metrics.py`
  (`PORT_LOG`, `present_serial()`, `serial_request()`, two tests) so the next arm can
  qualify it; this arm's `serial: 0` is preserved rather than back-filled.

## Arm state

`T2_MEMORY_FLOOR` stop, 0 cleanup errors, execution verified against the installed
ELF, device afterwards `MainUI=1, runtime.sh=1, principal.sh=1, port=0`.

## Limits

One press, one page, two frames. No `NEWGAME_CONFIG`, no Loading, no scene, no
id295 and no FPS claim. The captures are owner-local (game imagery is not
committed); `chain.json` holds the verdicts, the owner identity and the press
record.
