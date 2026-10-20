# The load now ends on the GPU memory wall, not on a shader

Roadmap §22.2 -> §22.5. Facts from `newgame-20` (build218), measured on the device.

## What this run proved

1. **Entry 45 is accepted and linked.** The final log carries
   `NVN_LC2_PROGRAM_STAGES object=0x341d23400 id=803 mask=2 sources=0/45 code-control-source=byte-exact
   link=on-native-pair-draw`. The half-arithmetic MRT fragment therefore reached a real program
   link instead of a `ZERO_SHADER_NOT_PINNED` stop, and no unknown shader was requested afterwards.
2. **The menu path is now driven from measured state, not from counts.** The highlighted row is a
   numeric band at x 88..124: y = 425 Load game, 475 New game, 525 Options, 575 Credits. The run
   walked to y=475, confirmed, crossed the New Game page and the "Press any button to continue"
   controls page, and entered the load.
3. **The load then died by OOM, not by the runtime.** The launcher printed `Killed` (SIGKILL), and
   dmesg holds 75 Mali OOM-notifier rows for `terminator2d-ne` with **725 992 kB** of GPU memory on
   a board whose `MemTotal` is 986 064 kB; `MemAvailable` was back to 683 012 kB afterwards. There is
   no `STOP status=` line at all, so this must not be reported as a fail-closed runtime stop.
4. **Cleanup is clean, but the first capture lied.** Immediately after the kill, kmsrab returned a
   mostly black frame (1 769 of 102 480 sampled pixels) because the panel had blanked; after one
   D-pad wake the same panel showed a fully lit Spruce menu (102 480/102 480). Game absent,
   `MainUI` 1, `principal.sh` 1, `runtime.sh` 1, CPU mask `0-7`.

## Why the earlier navigator failed twice

Press counting is not a navigation primitive at 1-2 fps: one press can move two rows, and animated
background pixels change the capture without the cursor moving (measured deltas 4, 4, 4, 4, 2, 0 on
repeated Down presses while the cursor sat still). The fix is to read the cursor band itself:
`cursor_row()` in the host tools now returns the y of the highlighted row, and the tool moves until
that y equals the wanted row.

## Consequence for the 30 FPS goal

The frontier is no longer "another missing shader". With the catalogue complete through entry 45 the
load walks into the same wall this board always shows: an unswappable Mali heap of ~709 MiB on a
963 MiB device. That puts the next experiments on the GPU-residency side of the roadmap (§22.5
ranks 3-4), not on the shader side:

- measure the Mali heap growth curve during the load against decoded texture bytes, using the
  existing BC deferral/file-backing counters, and identify which single asset class drives it;
- keep the conservative memory floor (the 32 MiB diagnostic floor is not a production setting);
- only then consider residency reductions that preserve exact pixels.

The 0.836 s/frame main-thread cost measured earlier still stands; even with the memory wall removed
it is the binding constraint on frame rate, and it needs the guest-stack sampler (`MOMO_STACK_SAMPLE_*`)
attribution before any optimization claim.

## Tool changes in this step

- `tools/newgame_navigate.py` keeps the bottom-anchor as a sanity check but the decisive primitive is
  the measured cursor row; a mismatch fails the run.
- Host suite: 56 tests pass.
- Device harvest lesson recorded: wake the panel before judging a post-run capture, and never treat
  "Killed" as a runtime stop.
