# Guarded probe-disabled fragment (build 180)

Status: NOT PLAYABLE. One remaining TEST fragment substitute (index 19) is now a
guarded translation of its measured-disabled branch. This is NOT 3D-sampler
support and does not establish a menu, gameplay, input or a complete frame.

## The measured branch

The captured fragment selects a probe-volume path on `c3.data[8] == 1.0` and
otherwise uses only its 2D texture/packed-colour path. A device probe
(`LC2_SHADER19_PROBE`, diagnostic, opt-in) read the live fragment constant range
at every draw of this program: every receipt reported 160 readable bytes with
flag 0x00000000 (`flag-bits=0x00000000`, 54/54 draws in the final run). The 160
bytes also cover the highest accessed element (index 38, byte 152).

The specialization therefore keeps the disabled path and selects it statically:
the two captured `_98`/`!_98` branches become straight-line code, literals
unchanged, and a stable sampler2D/packed-colour texture path remains. It removes
the sampler3D declaration and the flag reads it depended on.

## Runtime guard (mandatory, not optional)

Selecting a branch is only valid while the flag is false. The runtime validates
the exact fragment cbuf at EVERY draw of this catalogued program, before issuing
it (sources 16/19):
`lc2_probe_guard(bytes,word)` requires ≥156 bytes and `word != +1.0f`, and
otherwise stops with `LC2_PROBE_CBUF_REQUIRED` /
`LC2_PROBE_VOLUME_BACKEND_REQUIRED`. This does NOT permit rendering an enabled
probe; a real 3D backend remains required for that mode and has not been built.
Positive receipts: `LC2_PROBE_GUARD … allowed=1` on 54/54 draws.

## Verification

- Synthetic branch tests: nested false branch and negated true branch are
  selected; unknown flag element, missing `else` and unbalanced capture refuse.
  They do not claim validation of the captured GLSL as a whole.
- Guard boundary test: zeros/NaN/signed zero/short cbuf; exactly 1.0 refuses.
- Capture-identity guard: code AND control SHA-256 must match the catalogue
  before specializing; the general shader-literal tool is unchanged.
- Existing shader-literal, sampler/metadata, launcher tests pass; catalogue still
  has 34 programs, TEST substitutes 8 → 7.
- Build 180 cross-builds against the 435-file manifest-pinned baseline. Device
  hash `03182bdecc904212ed07891ba9ed4c42c7df3aad65309ee7419a4460c4a2cdcc`.
- Bounded run: TIME_LIMIT, 23.4 s of effective work in the 45-second budget,
  148 texture initializations, 54 presented frames, zero cbuf-unit collisions,
  no shader compile/link errors, and the guard admitted all 54 draws.
- Full-frame DRM captures at 25 s and 38 s still show dark, incomplete geometry
  with rain. The large opaque brown shape is gone, but no readable game text,
  object or UI is visible. Sparse `nonblack` counters are not treated as
  picture-level proof.

Evidence: `../evidence/shader19-guarded-01/` (raw logs, build log, exact env,
host checks, 54 probe receipts, captures, SHA receipt).

## Device cleanup

Build 180 remains installed (`lamentum-nextos.before-180` retains build 179).
Independent inspection: no port process, MainUI=1, principal=1, runtime=1. The
restored physical Spruce root menu is verified in `clean-menu.png`; the D-pad
event only woke the idle interface and is not game-input acceptance. No owner
image, texture resolution, launcher memory defaults or system VM settings changed.

## Remaining frontier

Seven TEST substitutes remain: one SSBO skinning vertex program (index 5), five
MSAA multi-sample fetch fragments (26–28, 29–31) and one dependent pair. The
color/geometry of the current scene is still incomplete, and the load-phase
physical-memory wall is unchanged and independent of this change.
