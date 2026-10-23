# K1-E — candidate user-mode GL dependency path

This is an offline ELF/dependency audit plus small read-only target metadata checks. It identifies the candidate's expected loader path; it does **not** observe Lamentum execution or prove the GL allocator's backing.

## Candidate ABI and direct imports

Candidate ELF: SHA-256 `c46714403f22074d92710192d1164cfe0b7a4f62f1a4890ffb7a1e224c542332`, Build ID `5b1b3412da7b43442a0ebf097e904cb8cbef0c8e`, 2,203,096 bytes. `readelf` reports ELF64 little-endian AArch64 PIE and interpreter `/lib/ld-linux-aarch64.so.1`; undefined version requirements include `GLIBC_2.17` and `GLIBC_2.27` (maximum GLIBC 2.27). It has no `RPATH` or `RUNPATH`.

`DT_NEEDED` includes `libSDL2-2.0.so.0`, `libEGL.so.1`, and `libGLESv2.so.2`. The ELF has 345 unique undefined symbols; 157 are directly relevant imports: 46 `SDL_`, 20 `egl*`, 91 `gl*`. No direct `gbm*`/`drm*` undefined symbols or `DT_NEEDED` entries were found. The launcher sets `SDL_VIDEODRIVER=kmsdrm` and `SDL_AUDIODRIVER=alsa`, but no `LD_LIBRARY_PATH` or `LD_PRELOAD`. `run_identity.py` copies `os.environ` then uses `execve` on the pinned ELF FD, so it does not discard the caller's loader environment.

## Expected loader resolution on the Spruce principal path

The installed `standard_launch.sh` dispatches PORTS through `ports_functions.sh`; its `run_port` prepends `PORTS_LD_LIBRARY_PATH` to the inherited `LD_LIBRARY_PATH`. The live principal environment supplied `PORTS_LD_LIBRARY_PATH` beginning `/mnt/SDCARD/spruce/flip/lib/:/usr/lib:...` and `LD_LIBRARY_PATH=/usr/trimui/lib:/usr/lib:/lib`. The first directory contained none of the candidate's named runtime libraries; the first matching files were in `/usr/lib`. Their ELF headers were class ELF64 / machine AArch64 (183):

- `libSDL2-2.0.so.0` → `/usr/lib/libSDL2-2.0.so.0.3200.6` (dev/inode `b3:04/1268`);
- `libEGL.so.1` → `/usr/lib/libEGL.so.1.4.0` (`b3:04/1244`);
- `libGLESv2.so.2` → `/usr/lib/libGLESv2.so.2.1.0` (`b3:04/1256`).

Read-only `/proc/2369/maps` showed the same SDL2, EGL and GLES files mapped by MainUI, along with `/usr/lib/libmali.so.0.32.0` (`b3:04/1750`), `libgbm.so.1.0.0` (`b3:04/1623`) and `libdrm.so.2.4.0` (`b3:04/1539`). The EGL and GLES wrappers are each 5,864 bytes and directly list `libmali.so.0` in `DT_NEEDED`; their verified local-copy SHA-256 values are `0a1a6d494bd3ad2b6a72d7139a05242efd3f9eb2760e124395b3ea7169a3c2b8` and `2148bdf031d9efa63295fbdf1cc484e4d573afa378e4b7ded88b74ad01b76745`. This supports the expected candidate dependency chain `SDL2 + EGL/GLES wrappers → libmali`; GBM/DRM may be transitive or loaded by SDL's KMSDRM backend, but no candidate process was run to observe that.

The live `libmali.so.0.32.0` is 49,377,264 bytes. It was **not** copied, hashed or disassembled because current free CMA is only about 0.6 MiB and the large ROMFS read previously correlated with a sharp CmaFree drop. No raw proprietary driver binary is committed.

## Current device gate

At the K1-E capture time, the latest complete same-boot D pair was `11:32:56.701–11:33:32.568Z`: `CmaFree=608 KiB` both samples, no order-7+ blocks. The complete 11:49 snapshot was still 608 KiB but was not a pair. The later complete 12:11 pair also remained at 608 KiB; its read-only DMA-BUF/process ownership, debugfs availability and lifecycle result are in the [K1-F follow-up](../k1f-cma-owners-debugfs-2026-10-23/README.md). That newer evidence still provides no launch authorization. Candidate remains staged/inert; build259 remains active; `T2_STORAGE_MARGIN_MIB` is unset.

## What this does not prove

The dynamic dependency path is high-confidence based on ELF requirements, PortMaster environment construction, first-match file metadata, and MainUI's live maps. It is still not a Lamentum runtime observation. It does not join `glTexImage2D`, renderbuffer, EGL surface or swapchain requests to Kbase native pages, `/dev/dma_heap/system`, `/dev/dma_heap/reserved`, or GBM buffers. K1-C/K1-D classify particular kernel allocator paths only; they do not attribute these candidate calls. Maintain **HOLD_RUNTIME**; no launch, New Game, or FPS claim.

## Verification and actions

- Candidate identity, `DT_NEEDED`, interpreter, symbol versions and import counts were parsed from the host ELF with `readelf` and checked against its recorded SHA-256.
- Target EGL/GLES wrapper copies were capped at 16 KiB each, hash-verified against device reads, and kept only in Hermes scratch. `CmaFree` stayed `608 KiB` before/after those reads.
- Target maps, launch environment and library path metadata were read-only; no device files/settings were changed, no allocation probe ran, and no game launched.
