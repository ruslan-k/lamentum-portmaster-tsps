# Portable layout

```
Lamentum.sh              PortMaster-style launcher; launch only through the Spruce principal flow
lamentum-switch/
  lamentum-nextos        runtime binary (GPL-3.0; built from the recovered baseline + runtime/lamentum-adapter.patch)
  lamentum-romfs.section ← YOU must add this from your own game copy (not distributed)
  logs/latest.log        written by the launcher on every run
  save-laboratory/       isolated save directory used by diagnostic runs
```

Before runtime start, the launcher temporarily enables CPU0–3 as needed and restores each CPU's original online value and sysfs permissions on exit.

The launcher verifies nothing about the game data beyond the runtime's own checks: the runtime
compares the section file's size with the size pinned in the owner image and refuses to start
(`VERIFIED_ROMFS_SECTION_UNAVAILABLE`) when they differ. Validate the image offline (segment
hashes, RomFS section hash, module identities) instead of trusting the device.

Nothing extracted from the game — NSO segments, RomFS, NPDM, saves, textures, shaders — may be
committed to this repository or uploaded anywhere. The owner image is owner data.
