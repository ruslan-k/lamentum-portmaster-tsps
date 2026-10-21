# Evidence: GLES upload-triple fixture on Mali-G57

Self-authored offscreen fixture (`tools/gles_srgb_fixture.py`, SHA-256 in
`device-fixture-sha256.json`, byte-identical on host and device). Launched
through the Spruce principal flow after the menu exited; the fixture dir was
removed afterwards and `device-state.json` records the restored frontend.

- `result.json` — full fixture output, `pass: true` for the version-2 request and
  the explicit ES3 request.
- `rc.txt` — fixture exit code 0.
- `error.txt` — empty (no stderr).
- `boot-id.txt` — device boot the run belongs to.
- `device-fixture-sha256.json` — host/device continuity for both scripts.
- `build.json` — build-228 ELF/helper hashes, baseline count, container digest.
- `host-tests.json` — full host suite at the published tree.

What this is: a driver-level check of the sRGB upload contract and its pixel
readback. What this is **not**: a game frame, an id295 residency measurement, a
Loading-stop attribution or an FPS result. No deployment of build-228 occurred.
