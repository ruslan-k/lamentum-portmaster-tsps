# New Game bring-up: attempts and what each one proved

Goal (roadmap §2, P0-FUNC): reach a real gameplay scene, not another menu, and only then
talk about performance. Every attempt below ran through the Spruce principal flow with
`tools/device_principal_test.py`; the device was verified clean (`MainUI`,
`principal.sh`, `runtime.sh` = 1, game and gdb = 0) before and after.

## Why the earlier "confirm" was not a New Game

`newgame-01` pressed A when a frame counter passed 400. That counter reaches 400 while the
loading screen is still up, so the run navigated a screen it never verified. The capture
shows the slot list afterwards, not gameplay. The lesson: trigger on the title's own
state, not on a frame number.

## Method now used

`tools/newgame_start.py` waits for `LC2_MENU_EVENT` from the hash-pinned
`ManagerMenuPrincipal` trace — the guest itself announcing that the menu is alive. It then
presses Up once (the measured default selection is Options), captures, presses A, captures,
and keeps capturing the following scene every 25 s until the run's own time limit.

The tool counts menu events cumulatively (`grep -c`). An earlier version read the last 4 KB
of the log; at this log rate the event scrolls out within seconds, which is exactly why
`newgame-02` reported `menu_seen: false` while four `LC2_MENU_EVENT` lines were present in
the saved log.

## Attempts

| Run | Result | What it proved |
|---|---|---|
| `newgame-02` | `menu_seen: false`, no presses | Only that a 4 KB tail misses the event. Fixed in the tool. |
| `newgame-03` | `menu_seen: true`, `confirmed: true`, 18 scene captures | The menu event fires and the up/A sequence reaches the pad, **but** the cursor landed on **Load game** (verified on the capture) and the screen never left the main menu: `menu-1` vs `after-confirm` differ by only 6100 pixels, and 18 later captures are still the main menu. |
| `newgame-04` | `harness_rc: 2`, no captures | `MainUI is not running — device is busy or in a game; aborting`. A transient right after the previous run; the device was clean on the next independent check. Nothing about the game. |

Two distinct defects came out of `newgame-03`:

1. **One 600 ms Up press moved the selection two entries**, from Options to Load game.
2. **A 600 ms A press did not register at all.** At ~1.7 presented frames per second a
   600 ms hold is shorter than one guest frame, so the title can sample the pad before the
   press and after the release and never see the button down.

Both are the same root cause: the guest samples input about once per 600–900 ms while it
runs at this speed. `lc2_input_latch.h` exists for exactly this and is now opt-in
(`LC2_INPUT_LATCH=1`, window forced with `LC2_INPUT_MIN_HOLD_MS`).

## In flight

`newgame-05`: same quiet memory environment, `LC2_MENU_TRACE=1`, `LC2_INPUT_LATCH=1`,
`LC2_INPUT_MIN_HOLD_MS=700`, taps shortened to 150 ms. The latch should give exactly one
guest-visible edge per tap, so Up moves one entry and A lands inside a sampled frame.

Acceptance for the next report is explicit: a capture that is neither the main menu nor a
loading/slot screen, produced while the game process is alive, with the device restored
afterwards. Anything less stays a failure in this file.

## New Game failure reproduced: it is a fail-closed stop, not a guest crash

`newgame-crash-01` pressed Accept (A) on the measured default selection and reached the
level load: frame 174 at 152.8 ms/frame (about 6.5 fps, four times faster than the menu),
with fresh `ROMFS_READ` traffic for the new scene. The runtime then stopped with

```
STOP status=ZERO_SHADER_NOT_PINNED pc=main.text.seg+0x542b68 detail=0x3fec0d70
```

so the "crash" is the adapter refusing to draw a program it has no translation for. The
kernel `page allocation failure: order:4` in dmesg is memory pressure during the same load,
not the cause of the exit.

The unrecognised program's identity is printed unconditionally, before the fail-closed exit:

```
ZERO_SHADER_UNRECOGNIZED code-bytes=1280 control-bytes=2176
  code-hash=7a45f946fe5f9130ad89877e0862164b805734d9b1739093e3099430ec1bbcb7
  control-hash=588a3fad7306d848ce2f3d70e85d5608e7973f1c093d3bb62b940c52aa4419e1
```

This is the same program the earlier `perf-01` and `perf-quiet-b0` runs hit after ~670
frames: the menu path never needs it, the level load does.

## Fix path (roadmap §2 step 4)

1. Re-run with `LC2_SHADER_DUMP=1` and `AW_RELEASE=0` to write `nvn-lc2-shader-code-*.bin`
   and `nvn-lc2-shader-control-*.bin` for this exact pair (owner data, stays local).
2. Translate with the hades-eval compiler (`--es 310 --cbuf-ubo`), apply the known Mali
   fixes, and record stage, samplers, hardware-bank +3 mapping and NVN binding.
3. Append it with `tools/append_program.py` — never regenerate the catalogue, which would
   revert the build202 `c4 -> NVN UBO1` correction and the literal/probe specializations.
4. Rebuild, redeploy, and repeat the same Accept-at-menu run until the level loads; only
   then is there a gameplay frame to talk about.
