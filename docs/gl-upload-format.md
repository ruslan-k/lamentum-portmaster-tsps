# GLES upload triples for decoded textures (roadmap 32.3 / PR A)

Component result, not gameplay. Starting upstream: **5ed8462**. This closes the
*contract* half of PR A: the runtime no longer passes one value as both the sized
internal format and the client `format` argument. It does **not** prove the
Loading stop was caused by it, and it changes no budget, floor, swap policy or
`alias_physical` behaviour.

## The defect that was in the overlay

`native/nvn_textures.h` and `native/zero_texture_writes.h` emitted

```c
glTexImage2D(GL_TEXTURE_2D, level, 0x8c42U, w, h, 0, 0x8c42U, type, pixels);
```

`GL_SRGB_ALPHA_EXT` (0x8C42) is a **storage** enum. The last `format` argument
describes the client array and must be a colour format (`GL_RGBA`). The same
value in both positions appeared in five places: the striped BC upload, the
non-striped refresh branch, the deferred first-use materialisation, the
CPU texel flush, and partial-mip completion (which took one `format` parameter
and used it twice).

## What replaced it

`native/lc2_gl_format.h` is a pure mapper — no GL calls, no game data:

| payload | ES3 storage | ES2 storage | client |
|---|---|---|---|
| 8-bit sRGB RGBA | `GL_SRGB8_ALPHA8` 0x8C43 | `GL_SRGB_ALPHA_EXT` 0x8C42 (needs `GL_EXT_sRGB`) | `GL_RGBA` / `GL_UNSIGNED_BYTE` |
| 8-bit linear RGBA | `GL_RGBA8` 0x8058 | `GL_RGBA` (ES2 has no sized colour formats) | `GL_RGBA` / `GL_UNSIGNED_BYTE` |
| verified float | `GL_RGBA32F` 0x8814 | `GL_RGBA` | `GL_RGBA` / `GL_FLOAT` |
| sRGB + float/half | refused (`UNSUPPORTED`) | refused | — |
| sRGB without ES3/`GL_EXT_sRGB` | refused (`SRGB_UNAVAILABLE`) | refused | — |
| half / packed payloads | not mapped: proven legacy unsized RGBA triple retained | same | payload type |

`lc2_gl_upload_for()` in `nvn_textures.h` resolves the triple **per EGLContext**
(GL_VERSION and the extension string are context state), refuses sRGB payloads it
cannot express instead of guessing, and keeps the legacy unsized triple only for
the half/packed payloads that already used it. The resolution is a non-GL
declaration, so the G0 rule "charge the whole mip chain before any GL call" still
holds; the compiled G0 fixture continues to assert `adds==1, gl_calls==0` on a
refused admission.

`zero_mip_complete_storage()` now takes the resolved `struct lc2_gl_upload`
instead of one format used twice.

## Device evidence (Mali-G57, self-authored fixture)

`tools/gles_srgb_fixture.py` runs through the Spruce principal flow on an
explicitly requested GBM display with a **surfaceless** context (no window, no
swap, no modeset), uploads an 8x8 RGBA ramp in **3-row stripes** (the last stripe
is 2 rows), samples it into an owned linear RGBA8 FBO and reads bytes back.

Result — `evidence/gl-upload-format/result.json`, `pass: true`:

- renderer `Mali-G57`, version `OpenGL ES 3.2 v1.r32p0-…`;
- sRGB decode: stored byte **160** sampled as **90**, exactly the sRGB→linear
  value (delta 0), while the identical byte ramp in a linear texture samples
  **160** — sRGB storage really decodes, it is not a label;
- partial final stripe, mip level 1 bytes and context recreation: byte-exact;
- the retired double-use triple produced `GL_INVALID_ENUM 0x500` in the explicit
  ES3 context, but was **accepted without error** in the context created with
  client version 2 — which on this driver still reports ES3.2. That leniency is
  exactly why the game never stopped on the old call, and why the correction is a
  portability/correctness fix rather than a proven Loading blocker.

Because Mali answers ES3.2 even for a version-2 request, the runtime mapper on
this device selects the sized 0x8C43 path. The 0x8C42 branch remains for a real
ES2-only driver and was exercised by the fixture's first scenario only in the
sense that the enumeration is valid there.

## Verification

- `tools/test_gl_upload_format.py` (7 tests) compiles the mapper out of the
  public overlay and checks every table row, the refusals, and the absence of any
  doubled `0x8c42U` call in the overlay.
- Full host suite: **166 tests PASS**; baseline **435/435**; ARM64 **build-228**
  `9f348c6c3ada5a12d71275153ff16e6702ca772da6d7bd8a835d79d7bd0100af`,
  helper `abe8e484…` unchanged.
- Fixture and host copy are byte-identical (`device-fixture-sha256.json`); the
  device PORTS entry used for the run was removed and Spruce is back to
  `MainUI=1, runtime.sh=1, principal.sh=1, port=0`.

## Not claimed

- Build-228 is **not deployed**, no game run happened, and no scene, id295,
  memory or FPS statement follows from this.
- Owner image and shader catalogue are unchanged; no texture resolution, budget
  or policy was modified.
- The elided question — did the invalid triple ever execute in a real Loading
  run — stays open. Answering it needs the guarded New Game arm of roadmap 32.2
  with `COTM_GL_ERROR_IGNORE=0`.
