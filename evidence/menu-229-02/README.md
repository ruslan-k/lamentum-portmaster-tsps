# menu-229-02: build-229 regression arm (menu only)

Installed **build-229** (`b164cffd…4e82f`) with its mandatory `run_identity.py`
and the current launcher (previous ELF backed up under
`lamentum-switch/.before-229/`). One bounded principal-flow arm, `COTM_GL_ERROR_IGNORE=0`,
`LC2_BC_OWNER_RECEIPT=1`, `T2_TEXTURE_BUDGET_MIB=300`, and a **diagnostic**
`T2_MEMORY_FLOOR_MIB=32` (not a release setting).

## Result

- Owned run identity verified: header bound to the installed ELF SHA, PID/starttime
  and boot ignored nothing; cleanup errors none, one MainUI afterwards, no game process.
- **55 presented frames, 52 with pixels** (`NVN_PRESENT_PIXELS status=PIXELS`,
  peak `nonblack=104461 max=255`). The animated main menu renders.
- **The corrected upload triple ran on the real atlas once**:
  `LC2_BC_STRIPED_UPLOAD id=291 size=8192x4096 temporary-bytes=4194304`, through
  `lc2_gl_upload_for()`, with **zero** GL-error-family lines
  (`ZERO_TEXTURE_REFRESH_GL`, `ZERO_TEXEL_UPLOAD`, `ZERO_CUBE_UPLOAD`,
  `LC2_GL_UPLOAD_FORMAT`, `ZERO_SRGB_TEXTURE_BACKEND_REQUIRED`).
- Stop: `T2_MEMORY_FLOOR` — `available-MiB=29 floor-MiB=32 swap-free-MiB=1537`,
  `VmSwap=495996 kB`, after the memory series `checks=40 → 90 MiB`,
  `checks=80 → 52 MiB`, exit at 29 MiB. The menu alone consumes the board's margin.
- `LC2_BC_OWNER_RECEIPT` did **not** fire: no deferred-BC first use in the menu, so
  the B1 receipt is still unexercised on device.

## Limits

This is a menu regression arm. It is not a scene, not id295, not gameplay, not a
frame-rate measurement, and the owner-local kmsgrab was taken after the run
(Spruce restored, 56,908-byte PNG, not committed), so it is cleanup evidence only. The 32 MiB floor is diagnostic;
production keeps the safe floor. Files: `before.json`, `cleanup.json`,
`expected-run.json`, `latest.log`, `derived.json`, `kernel-*.json`,
plus `menu-229-01` (same arm stopped at the default
96 MiB floor after 2 frames).
