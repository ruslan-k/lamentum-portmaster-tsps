# TSPS launcher smoke — 2026-10-22

## Purpose and result

This is a launcher/runtime smoke test, **not gameplay or FPS acceptance**. The updated `Lamentum.sh` works on Spruce even though its shell environment has no `stat` utility: it reads CPU sysfs modes with Python's standard library, runs the ARM64 runtime through `principal.sh`, and restores CPU state/modes on exit.

The runtime emitted 12 `NVN_PRESENT_PIXELS` records, then stopped itself with `T2_MEMORY_FLOOR`: `MemAvailable=62 MiB`, configured floor `96 MiB`, `SwapFree=1986 MiB`. The owned-run classifier found no kernel-OOM evidence. There were zero `LC2_MENU_EVENT` records; no menu, world, input, or FPS result is claimed. The non-black counters in the log are not visual proof.

## Artifact and run identity

- Source commit: `3bb74d3c2c56e87e5d2741da4208a5864e6a996a` (pushed to `main`).
- Device: TSPS/Spruce, boot ID `66203f22-4ac8-4a2a-a47c-cddc253d3bda`.
- Run UUID: `da207fdd-f695-491a-a35c-3068f69bfb59`.
- Runtime: `lamentum-nextos`, SHA-256 `ecef4ba2075946095e69120137366850c41184d26e3e82c995cdd98995bd6575`.
- Installed launcher: SHA-256 `f32204ff1b271dd66e38f79573f75c6f562af49174ea436e81dd9417dba1354a`.
- `run_identity.py`: SHA-256 `abe8e4847b18a750c0796af33d887cf43714126c9751ccdc8236715cb752401a`.
- Game process identity: PID `6944`, starttime `169845`, ELF device/inode `45833:7732`.

The previous installed launcher was backed up at `/mnt/SDCARD/Roms/PORTS/.Lamentum.sh.before-3bb74d3`, SHA-256 `63bfac5bddd45b7a5e3176d4094f804756992bf264f19a9e419225c1b9804948`.

## Cleanup and physical display

`device_principal_test.py` reported `cleanup_errors=[]`, no remaining game PID, and restored `MainUI`, `principal.sh`, and `runtime.sh`. CPU online mask was `4-7` before and after. CPU0–3 were `online=0, mode=0444` both before and after; see `cpu-mode-before.json` and `cpu-mode-after.json`.

`mainui-after.png` is a **local-only** post-cleanup physical KMS capture at 1280×720, SHA-256 `81905538c11d728fe3accb5e3096ee19c16b53d60341ce61d9916bf1dd5c4ff3`. It shows Spruce's PORTS list (Sally Face selected), confirming the frontend returned. It is **not** a Lamentum frame and remains excluded from Git by the repository's capture policy. The full `latest.log` is also local-only (SHA-256 `1599f394c0905fecaf1ed0c0166170d067e1278ca779e0ef707808b25152a00c`). Public evidence contains the concise report and run receipts, not raw logs, kernel dumps, or screenshots.

## Next gate

Do not enter New Game or lower the 96 MiB safety floor: this run crossed it and stopped at 62 MiB. Continue the roadmap's M1 per-texture guest/decoded/charged accounting and safe menu-headroom work first. A true world scene, controls, and 30 FPS remain unverified.
