# Constant-buffer texture-unit isolation (builds 175–177)

Status: not playable. Build 177 removes a demonstrated cbuf binding collision and
produces a partial rainy scene on physical scanout instead of a white field.
This is not a verified menu, complete rendering, input or gameplay result.

## Controlled A/B

Both runs use the SAME build-177 binary, identical owner content and identical
memory settings. Only `LC2_CBUF_LEGACY_UNIT=1` versus `=0` changes.
Each run has a 45-second runtime budget and stops with `TIME_LIMIT`, not the
memory floor. Runtime SHA-256:

`43ce05df27cf9a930e09bbe8693e957dbf7be9a9ddd7b676c6ee74365ecd4311`

| receipt | legacy unit 15 | distinct units |
|---|---:|---:|
| post-upload cbuf audit records | 101 | 101 |
| records reporting a repeated unit within one draw | 37 | 0 |
| frame ceiling | 58 | 52 |
| initialized textures | 154 | 149 |
| physical capture at ~25 seconds | white field | dark, partial scene with rain |

Frame and texture ceilings are observations of time-limited runs, not performance
or memory improvements. Sparse `NVN_PRESENT_PIXELS` counters do not measure a full
screen. See the full DRM captures instead:

- `../evidence/cbuf-unit-legacy-01/capture-25.png`
- `../evidence/cbuf-unit-distinct-01/capture-25.png`

Capture receipts show no MainUI and a live port PID (14510 / 15237 respectively).
The ~10-second capture attempts found no active framebuffers and produced no PNG;
they are not image evidence. The A/B summary, exact environments, logs, binary
hash receipts and capture status are in the corresponding evidence directories.

## Cause and implementation

The GLES cbuf emulation uploaded several RGBA32F textures but assigned every
active sampler uniform to unit 15. After the whole upload loop, the legacy pair
7/0 had BOTH vertex `c4` and fragment `c3` pointing at unit 15 / object 92.
Checking `glGetUniformiv` immediately after each individual upload missed this:
that check preceded subsequent overwrites.

The corrected pair 7/0 has vertex `c4` on unit 31 / object 90 and fragment `c3` on
unit 30 / object 91. The allocator reserves low ordinary/palette units and high
mip-mask helper units, assigns a separate unit AND GL texture object to each
active cbuf, and refuses exhaustion instead of wrapping into another resource.
The change is scoped by the Lamentum image contract `LC2_TEXTURE_VIEW_36`; other
profiles retain their historical behavior. Metadata and the eight TEST shader
substitutes are unchanged.

Diagnostics:

- `LC2_CBUF_AUDIT=<draw-count>` reads uniform units and bound GL objects AFTER all
  uploads. It reports collisions; it does not stop a run or modify guest memory.
- `LC2_CBUF_LEGACY_UNIT=1` deliberately restores the faulty allocation for A/B.
  It is diagnostic only, checked by value; unset or `=0` uses isolated units.

Host checks passed: seven sampler/catalogue regressions, launcher regression,
cbuf-unit boundary/uniqueness/exhaustion test, guest-quota test and fileback test.
The pinned cross-build completed for build 177; build 176 was a compile failure
from an unavailable env helper and was never deployed. Baseline source remains
read-only, with modifications carried by `runtime/lamentum-adapter.patch`.

## Rejected bank-number experiment and remaining frontier

Build 175 tried treating producer `cN` as NVN API slot N. On-device bank 4 was
unbound. The title's original `nvnCommandBufferBindUniformBuffers` at
`sdk.text.seg+0x4752f0` adds 0x300000 to an index shifted by 20 bits at `+0x118`:
API uniform slots map to hardware constant banks with a +3 offset. A compiler
hardware bank must not be used directly as an API slot.

Also distinguish bank 1's embedded per-shader literals from application cbufs.
Captured code contains its referenced literal data after the executable portion;
for example, the sRGB shader's first literal is 1.055, not a bound application
matrix. The control data offset/size and SDK contract need a separately validated
implementation. Block TYPE names such as `fs_cbuf_block_4f` are not bank numbers.
The bank-number experiment was reverted in source/catalogue, and its run is kept
under `../evidence/cbuf-guest-banks-01/`. No handle/bank scanning was added.

The earlier catalogue's MSAA filters also must not be mistaken for ordinary
sampler2D mip sampling: their four-argument fetches select individual samples.
They still require correct multisample translation/backend support, not a
quality-reducing rewrite. Fragment 19's TEST substitute remains; replacing it
requires validated 3D-sampler handling. These are unresolved rendering frontiers.

## Device state

Build 177 remains installed with device-side backups and an independently checked
hash. After both probes: no port process, MainUI=1, principal=1, runtime=1,
CPU online 0–7. `cleanup.txt` records the exact PIDs and hash. The first cleanup
capture shows Spruce's idle charging clock; a neutral D-pad event woke it, and
`clean-menu-awake.png` verifies the actual Spruce root menu. This UI wake is not
physical game-input acceptance. No texture resolution, owner image, launcher
memory defaults or system VM settings changed.
