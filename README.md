# Lamentum — handheld port

Lamentum (Obscure Tales) is a Unity **2019.4.4f1**, Mono, Windows x86_64 build. This port runs it
natively on aarch64 Linux handhelds (TrimUI Smart Pro / SpruceOS) through Unity's **arm64 Android
IL2CPP player**, hosted by `ua_host` (the libhybris-style host from the portmaster-unity toolkit).
No emulation and no x86 translation: the game's managed code is compiled ahead of time by Unity's
own IL2CPP for the player that runs it.

What the conversion changes:

- **shaders** — the build ships Direct3D 11 programs only; `pmhlslcc` (Unity's HLSLcc) translates
  them to GLES3.
- **textures** — BC/DXT pixels re-encoded as ASTC **8x8** (the Mali GPU cannot sample BC; 4x4 pushed
  the data to 1.7 GB and ua_host died of OOM on the 1 GB handheld, 8x8 gives 482 MB).
- **settings** — graphics API set to GLES3.
- **audio** — clips kept compressed where the data allows.
- **quality** — the handheld profile (1 pixel light, hard shadows, 2 cascades, no MSAA) applied to
  the data's quality levels and passed to `ua_host` as run-time caps.

## Build

Needs: a portmaster-unity checkout with `tools/hlslcc/out/pmhlslcc` built, the unpacked
`UnitySetup-Android-Support-for-Editor-2019.4.4f1.exe` player package, a Python with
`convert/requirements.txt`, Docker (IL2CPP compiles in a container) and ~10 GB of disk.

```sh
UNITY_DATA="$HOME/Lamentum/Lamentum_Data" \
UNITY_PLAYER="$HOME/unity-android-2019.4.4f1" \
TOOLKIT="$HOME/portmaster-unity" \
./build.sh
```

`pmunity` fetches the 2019.4.4f1 IL2CPP tools and NDK by itself (`~/.cache/pmunity/il2cpp`).
The build is journaled: re-running resumes.

Result in `out/pack/zip/`:

```
Lamentum.apk            1763 MiB — assets/bin/Data (game data) + Managed/Metadata
android_package.json    package id, ABI, data version, quality caps
plugins.map             two native plugins: Steam stubs (the game ships no plugin this port uses)
Game_Data/              StreamingAssets (empty for this title)
```

Then, beside it on the device: `lib/` with `libmain.so`, `libunity.so` (from the 2019.4.4f1 player)
and `libil2cpp.so` (from the IL2CPP step), plus `ua_host`.

## Device layout

`/mnt/SDCARD/Roms/PORTS/lamentum/`

```
ua_host                 host runtime (arm64)
Lamentum.apk            data container
android_package.json
plugins.map
lib/{libmain,libunity,libil2cpp}.so
data/                   created by ua_host: shared_prefs, external/ (saves)
log.txt                 written on every run
```

The launcher `Lamentum.sh` keeps one instance (flock), stops MainUI (it holds the panel and the
ALSA device), runs `ua_host` with KMSDRM/ALSA, and brings MainUI back on exit. Launch it from the
Spruce Ports menu, so the principal flow owns the handoff.

## Port-specific fixes

**Input.** The game reads Unity's Input System package (373 call sites), and a desktop build's copy
has no layout for the Android player's game controller: `asmpatch --only=inputsystem-android` adds
the `AndroidGamepadForPlayer` / `AndroidXboxGamepadForPlayer` layouts (build.sh runs it).
`asmpatch --survey` also reports that `GameManager`'s gamepad check reads `Mouse.current` with no
null check, so the port needs pointer mode (`UA_POINTER=1`) if that coroutine runs.

**The resolution menu.** `ManagerMenuPrincipal.Start()` builds the resolution list from
`Screen.resolutions` and then reads `PosiblesResoluciones[Length - 1]` without checking for an
empty list. The Android player behind `ua_host` reports no display modes, so the list is empty and
the menu dies with `IndexOutOfRangeException`. `tools/lampatch` (Mono.Cecil) appends the panel's own
1280x720@60 to `ResolucionesCompatibles()` when the list would be empty; the patched
`Assembly-CSharp.dll` goes through IL2CPP like any other assembly.

```sh
DOTNET_ROLL_FORWARD=Major dotnet run --project tools/lampatch -- <Managed>/Assembly-CSharp.dll out/patched
```

## Licence

The port code here is GPL-3.0 (see LICENSE). The game — its data, art, audio, code and the IL2CPP
output built from it — is Obscure Tales' and is **not** in this repository.
