# Title screen reached (build 193)

Status: NOT PLAYABLE, but the visible picture is now the game's own title screen
rather than an incomplete background. No menu list, input action, audio or save
has been demonstrated.

## What the panel shows

`../evidence/long-budget-420-01/capture-300.png` (frame ~549, 300 s into the run)
and `../evidence/title-input-01/at-title.png` both show the **"Lamentum" title
logo**: a blood-red calligraphic capital "L" with a torn swash, the remaining
letters in a bone/parchment blackletter face, on black, with two faint green-yellow
lamps and a barely visible kneeling silhouette. This is the title treatment drawn
by the game itself, so the text/UI rendering path (font/logo textures, alpha and
blending) works on this adapter.

Runtime: build 193 (catalogue 38 programs), SHA-256
`251a7a185e0ee73b36c4984853a590a966ddb1ffc5fec9d9a370804a2ac731cb`.

## How the run got there

Two changes, both measured, neither a shader guess:

1. `docs/catalogue-tail.md` — closing the shader tail by APPENDING captured
   programs (indexes 34–37) instead of regenerating the catalogue.
2. The 32-MiB diagnostic memory floor, which stops the load later than 64 MiB
   (575 textures / frame 321 versus 328 / 124).

The 420-second run ended on `TIME_LIMIT` at frame 669 with 563 texture
initializations: no shader refusal, no memory floor, no fault. A run that ends on
time rather than on a defect is the first time this port has done that at a phase
that renders the title screen.

## The input question is now the frontier, not the picture

Log receipts show the input stack is present and measured, not stubbed:
`HID_PHYSICAL_OPEN name=TRIMUI Player1 guid=0300a3845e0400008e02000014010000`,
`HID_FACE_POSITION … path=/dev/input/event4`, `HID_NPAD_STYLE player=0 style=1
provider=physical connected=1`.

Injection attempt during a live run (Start, `BTN_START` 0x13b on `/dev/input/event4`,
140 ms hold, `../evidence/title-input-01/post-start-*.png`): the screen did NOT
change away from the title. Two A/B/Y presses attempted afterwards are INVALID as
evidence — the port had already exited by then, so those captures show the Spruce
menu, not the game.

So the honest statement is: a physical Start press produced no visible change, and
it is not yet proven whether the guest received the event. The next measurement is
a HID-side receipt in the same window (what the adapter's shared-memory pad state
and the guest's read of it look like at press time), not more screenshots.

## Device state

Build 193 remains installed with `lamentum-nextos.before-<tag>` backups. After the
probe: no port process, MainUI=1. A stale `/tmp/cmd_to_run.sh` caused one extra
short launch that died on the memory floor at frame 4; it produced no picture and
was left to exit on its own.

## Next

- Instrument the HID path (pad state write + guest read) and repeat a Start press
  inside a live title screen; only then decide whether the mapping, the shared
  memory contract or the guest's poll cadence is wrong.
- Then the menu list, audio (`AUDOUT_HOST_FAILURE` still unaddressed) and saves.
