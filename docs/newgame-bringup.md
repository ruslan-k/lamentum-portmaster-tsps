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

## Blobs captured; the translator refuses this program

`newgame-crash-03` ran with `LC2_SHADER_DUMP=1` and `AW_RELEASE=0` and wrote the pair for
exactly the failing identity:

```
LC2_SHADER_DUMPED sequence=0 code-bytes=1280 control-bytes=2176
nvn-lc2-shader-code-1792497924-0.bin   sha256 7a45f946…  (1280 B)
nvn-lc2-shader-control-1792497924-0.bin sha256 588a3fad…  (2176 B, magic 0x98761234)
```

Both hashes match the `ZERO_SHADER_UNRECOGNIZED` line byte-for-byte, so the dump is the
program the title really asked for. The blobs stay in the owner workspace and are not
committed.

Translation attempts with the hades-eval CLI, all on the same blob:

| Flags | Result |
|---|---|
| `--es 310` | `Buffer block cannot be expressed as any of std430, std140, scalar, even with enhanced layouts` |
| `--es 300` | same |
| `--es 310 --cbuf-ubo` | `CBUF_AS_UBO decorations-changed=0`, then the same error |

`decorations-changed=0` is the useful part: the existing `BufferBlock -> Block` /
`StorageBuffer -> Uniform` rewrite found nothing to flip, so this is not the read-only
cbuf case that the current catalogue handles. `--dump-decorations` shows a single
`Block` (decoration 2) plus a `NonWritable` set (30) and `Binding`/`DescriptorSet`
(33/34) — i.e. one block the ESSL backend cannot express, the same class as the SSBO
skinning programs already covered by TEST substitutes.

## The two honest options

1. **TEST-ONLY substitute** (fast, labelled): add an explicitly named TEST entry so the
   level load passes and the *next* blocker becomes visible. This is not a translation and
   must be marked as such in the catalogue, exactly like the seven existing ones. It gives
   a real gameplay frame only if this program does not affect visible geometry.
2. **Proper conversion** (slow, correct): extend the translator to express this block as a
   texture-fed uniform set like the cbuf path (sampler2D + texelFetch), with exact
   access-shape and bank mapping, then append it with `tools/append_program.py`.

Nothing here is a 30 FPS result: the port still cannot reach gameplay, and the measured
gap (replay 250 ms + guest 316 ms per frame) is unchanged.

## Fixed: New Game now passes the blocker (build210)

The failing program was a **vertex** shader whose single uniform block is
`{ float data[16384]; } c4` with `ArrayStride = 4`. ESSL only has std140, where that array
needs stride 16, so spirv-cross refused the whole module — this is a *layout* refusal, not
a missing `Block` decoration (`--block-decorate` changed 0 decorations).

Fix, in the offline translator only (the runtime is untouched):

1. `--fix-strides` raises a block array stride to the std140 minimum before cross-compiling.
   The element indices the shader uses are unchanged, and the catalogue serves this block
   from an RGBA32F texture through `texelFetch`, so the declared stride no longer decides
   the values — it only has to let spirv-cross emit the module.
2. The program was translated to `#version 310 es` and appended with
   `tools/append_program.py` as entry 38 (`dump-588a3fad vertex`, code 1280 B, control
   2176 B, hashes `7a45f946…` / `588a3fad…`).
3. The generator again emitted `.name="c4",.stage=0,.binding=0` for a hardware bank 4. That is
   the build202 defect: it was corrected by hand to `.binding=1` (NVN slot 1), exactly like
   program 12, and must keep being corrected until the generator derives banks from
   compiler instance names.

Result on the device (`newgame-07`, build210 `d4f3d1f6…`): after Accept the run presents 275
frames with **no STOP and zero `ZERO_SHADER_UNRECOGNIZED`**, 1108 `ROMFS_READ`s, and the
panel shows the game's own **controls/tutorial screen with "Press any button to continue"**,
followed by the studio splash. That is the first time a New Game start progressed past the
previous fail-closed exit.

Not yet: advancing from that screen into the first playable scene. The run's budget ended
at the prompt, so gameplay pixels are still unproven and no FPS claim applies.
