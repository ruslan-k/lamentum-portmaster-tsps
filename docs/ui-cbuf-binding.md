# UI restored: hardware cbuf4 is NVN UBO1, not SPIR-V binding0

Status: real main-menu text and selection are visible on build202. Navigation
and Back have a demonstrated screen effect. Gameplay and audible audio are NOT
yet validated; this is not a claim of a finished port.

## Root cause, independently derived

The compiler's `backend/spirv/spirv_emit_context.cpp` names each constant-buffer
VARIABLE with `ctx.Name(id, fmt::format("c{}", desc.index))`. Its SPIR-V Binding
decoration is a separate sequential counter. Thus vertex12's `c4` identifies
Maxwell constant bank4, whereas its generated layout binding0 is not an NVN
application UBO index. This is NOT the rejected attempt to read bank numbers
from block TYPE names (`vs_cbuf_block_0f`, `fs_cbuf_block_4f`).

The title's SDK provides the other half of the contract:
`nvnCommandBufferBindUniformBuffers` at SDK+0x4752f0 copies argument w2 (the NVN
slot) into w20, shifts it by20, adds `0x300<<12`, then selects bits20..24 for
the hardware bind. Each next buffer increments this field by `0x100<<12`.
For graphics stages this is hardware bank = NVN slot +3. Therefore c4 -> UBO1.
`evidence/ui-pass-01/cbuf-mapping-contract.json` records the hash-pinned SDK
instruction checks and the compiler provenance.

## Real draw evidence before the correction

The native getters were also resolved, without invoking them or altering state:
managed activeInHierarchy resolves to main+0xd69a70, which calls main+0x4928f0.
The native cached activeSelf/hierarchy bytes are +0x56/+0x57. A read-only /proc
snapshot reports 1/1 for both CanvasMenuPrincipal and EscenaPrincipal. This
extends the earlier SetActive entry trace with actual native state evidence.
A hierarchy cache of0xff would require a slow-path evaluation, not guessing.

The frame300 dump shows six UI/Default draws using pair12/14, NOT candidate
pair12/35. Both app buffers are present:

- UBO0: 144 bytes, projection scale2, translation(-1,-1), color multiplier
  (1,1,0,0). It is not the UI projection and its alpha multiplier is zero.
- UBO1: 160 bytes, orthographic x/y scales approximately 2/1920 and 2/1080,
  color multiplier(1,1,1,1), UV scale/offset(1,1,0,0).

The catalogue incorrectly selected UBO0 for the c4 texture-fed constant bank.
`tools/analyze_ui_cbuf.py` replays VS12's actual float32 ALU sequence on the
first four captured positions of each draw: all24 positions are outside x/y
clip bounds with UBO0, and all24 are inside with UBO1. Old alpha is0, corrected
alpha is1. This is only a replay of captured positions, not pixel proof.

## Isolated correction and real pixel proof

Only one catalogue field changes: entry12, uniform c4, binding0 -> binding1.
Shader source, code/control identities, sampler lookup, texture dimensions,
other entries and runtime behaviour remain unchanged. No full regeneration.

Build201 is NOT an equivalent build and was never deployed. It was compiled
from the pre-correction catalogue: its embedded `shaders/nvn_shader_sources.h`
still carries `.name="c4",.stage=0,.binding=0,…` (header SHA-256
`4bcc233c2c0dea35feb5c5dea37c86f1e39dc852cf8b75008910c25448ee84ab`) and its
binary still contains the removed `LC2_UI_TRACE_AFTER` diagnostic, SHA-256
`3a7f04d0509e49cec5b128676aa0d08c57497b5419a8d3ff1e7796a3dab45310`. It is a
concurrent pre-edit snapshot: launched before both edits landed. Its existence
does not validate the correction. Build202's header
(`7cfa998886333aafd0c8ea3f84918dfcbca80a24add11527bd4421265891b719`) carries
`binding=1` and no trace string, and build202 is the only binary carrying the
correction. Both builds completed with zero `error:` lines.

Build202 SHA-256, independently read from the device:
`ff4454232247b935748db7a76b05a7af27e62f2a189d199b49d7d6d93f9d1fd2`.
The previous runtime is preserved as `lamentum-nextos.before-202`.

Actual DRM captures in `evidence/ui-cbuf-fixed-01/`:

- `live.png`: load-slot list1–9 and B Close;
- `slots-before.png` -> `slots-after-down.png`: selection moves1 ->2 after
  an agent-injected evdev hat-down on the real pad's event4 provider;
- `main-menu-after-back.png`: returning from the slots after guest B;
- `main-menu-options-selected.png` and `after-short-up-unchanged.png`: fully
  readable Load game, New game, Options, Credits; Options is selected.
  The short300ms Up did not visibly move it. Do not mislabel this as a selected
  New game or successful gameplay.
- `at-title.png` -> `after-confirm-a.png`: the scheduled A confirmation opens
  Options, with Language/English, Noise effect, Reading speed, Rumble,
  SFX/BGM sliders, Adjust brightness, How to play and Return all legible.

The main-menu rectangle x80..330/y390..620 has0 pixels above grayscale128 in
the baseline and2451 in the corrected capture. The published numerical report
keeps exact crop coordinates; legible text and selection are established by the
real captures, not just the brightness count.

There were pad-provider events before the automated frame400 confirmation.
They are not attributed to the scripted confirmation. The controlled down/back
actions above are agent evdev injection, not proof of a human pressing buttons.
Before exploring New game, the isolated save directory was copied and every
file's SHA-256 compared. Only PlayerPrefs.dat (132 bytes) existed; no numbered
game save was overwritten. The backup receipt is `save-backup.json`.

The bounded run ended deliberately at frame709 with TIME_LIMIT after520s.
Independent cleanup reports MainUI/principal.sh/runtime.sh=1 each, game/gdb=0,
and rechecks the installed SHA-256. `clean-menu.png` is the frontend's clock
screensaver, NOT game or menu proof; `clean-menu-awake.png` shows the actual
Spruce Recents list with Lamentum selected after a safe wake button.

## Regression and remaining work

The host suite includes tests pinning entry12's c4->UBO1 mapping and replaying
the real six-draw capture. It passed24 Python tests. Existing C diagnostics
remain separate from the actual fix.

The generator still treats descriptor binding/declaration ordinal as the guest
UBO index. Do not regenerate the catalogue or globally rewrite other entries:
future append work must preserve this correction and derive each application
bank from the compiler instance-name provenance plus the SDK mapping. Other
cbuf entries may need a measured audit, not a blanket unverified replacement.

Next: controlled New game startup and gameplay with bounded resource monitoring,
then sound and save/reload verification. A nonzero AUDOUT PCM counter is not a
substitute for an audible-output test. Diagnostic memory/GL settings are still
needed for these runs; production-default launch is not yet validated.
