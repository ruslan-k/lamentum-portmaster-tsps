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

### What was measured (`../evidence/title-input-02/`)

Two injections during a LIVE title screen, each verified in the adapter's own pad
receipt (`HID_SAMPLE … player=0`):

| physical button | host code | guest mask seen by the adapter | screen reaction |
|---|---|---:|---|
| A (south) | 0x130 | `0x2` | none |
| Start | 0x13b | `0x400` | none |

So the host path works end to end inside the adapter: the press is read from
`/dev/input/event4` and published as the guest's button mask. It is NOT yet proven
that the guest consumes that state.

Pixel measurement between the title capture and both post-press captures:
mean luminance 3.68 → 3.76 → 3.74, 5272 changed pixels with max delta 63 spread
across the whole frame (animated embers/rain), and the centre-left band stays at
1.4–1.8 mean with no text-shaped region. A zoomed crop shows no legible glyphs.
A first visual read of the same image suggested a "Continue / New Game / Options"
menu; the numbers and the crop do not support it, so that reading is withdrawn.

The earlier press in `../evidence/title-input-01/` is weaker evidence: the harness
bug (`python3 -c -`) meant no event was actually delivered there, and the later
A/B/Y attempts ran after the port had exited.

### Next measurement

Decide whether the guest polls the published pad state at all: log the EP_HID
command mix the title issues (101/121/200/... ) and derive the SDK 10.9.0.0 shared
in-memory pad layout from the title's own `sdk` module before touching the
mapping. Until that receipt exists, "input is broken" and "the title is still
loading and ignores input" remain equally unproven; the second is supported by the
fact that texture initialisations plateau at 563–577 rather than completing.


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
