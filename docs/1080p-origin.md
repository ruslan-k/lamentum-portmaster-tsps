# Where the 1920×1080 targets come from

Short answer: **from the game, as hardcoded constants** — not from the panel, not
from the adapter's display answers, and not from a mode query. The panel path really
is 720p.

## Evidence 1 — the guest creates them, with literals

Log (`evidence/menu-targets-01/latest.log`):

```
NVN_CALL name=nvnTextureBuilderSetSize2D caller=main.text.seg+0x53bfe0 arg=0x780 arg=0x438   # 1920x1080
NVN_CALL name=nvnTextureBuilderSetSize2D caller=main.text.seg+0x53c074 arg=0x780 arg=0x438
NVN_CALL name=nvnTextureBuilderSetSize2D caller=main.text.seg+0x53c244 arg=0x780 arg=0x438
NVN_TEXTURE_REAL object=0xb0bab38 format=0x25 size=1920x1080 ... texture=1
NVN_TEXTURE_REAL object=0xb0babf8 format=0x25 size=1920x1080 ... texture=2
NVN_TEXTURE_REAL object=0xb0bacb8 format=0x25 size=1920x1080 ... texture=3
NVN_TEXTURE_REAL object=0x340dd3018 format=0x35 size=1920x1080 ... depth=1
```

Disassembly of the title's own code at that call site:

```
53bfcc: mov  w21, #0x438        ; 1080
53bfd0: sub  x0, x29, #0xd8
53bfd4: orr  w1, wzr, #0x780    ; 1920
53bfd8: mov  w2, w21
53bfdc: blr  x8                 ; nvnTextureBuilderSetSize2D(builder, 1920, 1080)
```

Both dimensions are **immediates in the instruction stream**. Nothing is read from a
struct, a service reply or the display: this is the title's own composition
resolution (the classic Unity 1080p reference target), chosen by the game.

The depth target goes through a different site (`main+0x533a40`) that takes its size
from a descriptor struct (`ldrh w1,[x20,#4]`, `ldrh w2,[x20,#6]`), and the same site
also builds the **1280×720** window target with `0x500×0x2d0`. So the guest keeps two
families: its 1080p composition trio (plus depth) and the 720p window/present family.

## Evidence 2 — we are not presenting 1080p

- `NVN_WINDOW_REAL framebuffer=1280x720 bpp=32 textures=3` in the same log.
- `display.h` answers the current-resolution query (`cmd 1102`) with `{1280, 720}`.
- `ListDisplays` advertises **maximum layer dimensions** `1, 1920, 1080` — that is the
  compositor's capacity field, not the mode; and since the trio's size is a literal,
  it cannot be the source of this choice.
- The adapter has no `GetOperationMode`/docked handling at all, so the title is not
  being told "docked" by us either.

## What "should be 720p" means here

- The **panel/swapchain path is already 1280×720**. Nothing is misconfigured there.
- The 1920×1080 images are the title's internal composition buffers; making them 720p
  is a **storage policy change**, and the adapter already ships the switch for exactly
  this family: `ZERO_RENDER_SCALE=2` maps `1920×1080 → 1280×720` and, per its own
  header, "preserves native 1280×720 composition/UI and only maps the 1080p window to
  the physical 720p framebuffer".
- That switch is **off by default**, and the owner roadmap already records
  `ZERO_RENDER_SCALE=2` as a *measured performance-negative* (fill/switch cost), not a
  memory win — which is why it is not a default. Those targets use **31.64 MiB before resizing** (three colour plus one depth-equivalent at 1080p), but still need **14.06 MiB at 1280×720**. The **maximum nominal saving is 17.58 MiB**, not 31.64 MiB, and driver physical savings have not been measured.

## Consequence for the next step

No new scaling code is needed: the A/B is one environment variable plus phase-matched in-run capture comparisons. `tools/frame_diff.py` defaults to tolerance=2, so its `identical()` verdict is **not byte-exact**; require tolerance=0 for exact matches and report a separate tolerant comparison for animation noise. The decision to
run it stays with the owner, because it changes image quality; the measurement will
report both what it saves in charged bytes and what it costs in pixels.
