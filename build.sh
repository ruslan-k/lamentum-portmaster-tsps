#!/bin/bash
# Builds the Lamentum port from the game's Windows/Unity data:
#   convert (D3D11 shaders -> GLES3, BC -> ASTC) -> managed patches -> IL2CPP -> APK + Game_Data.
# Env: UNITY_DATA=<...>/Lamentum_Data  UNITY_PLAYER=<unpacked Unity 2019.4.4f1 Android player>
#      TOOLKIT=<portmaster-unity checkout>  OUT=<build dir>  JOBS=<compiles>  DOTNET=<dotnet>
set -euo pipefail

UNITY_DATA=${UNITY_DATA:?set UNITY_DATA to the Lamentum_Data directory}
UNITY_PLAYER=${UNITY_PLAYER:?set UNITY_PLAYER to the unpacked Android player package}
TOOLKIT=${TOOLKIT:?set TOOLKIT to the portmaster-unity checkout}
OUT=${OUT:-$PWD/out}
JOBS=${JOBS:-$(nproc)}
DOTNET=${DOTNET:-$(command -v dotnet || echo "$HOME/.dotnet/dotnet")}
HERE=$(cd "$(dirname "$0")" && pwd)
export PMUNITY_IL2CPP_HOME=${PMUNITY_IL2CPP_HOME:-$HOME/.cache/pmunity/il2cpp}
export PMUNITY_ANDROID_PLAYER=$UNITY_PLAYER
export DOTNET_ROOT=${DOTNET_ROOT:-$(dirname "$DOTNET")}
# pmunity's `convert` wrapper does not forward the shader source to the shaders step, so that step
# runs on its own: --from d3d11 translates the Windows build's DXBC programs with pmhlslcc.
export PMHLSLCC=${PMHLSLCC:-$TOOLKIT/tools/hlslcc/out/pmhlslcc}
PY=${PYTHON:-python3}

rm -rf "$OUT"; mkdir -p "$OUT"

echo "== shaders (Direct3D 11 -> GLES3)"
(cd "$TOOLKIT/convert" && PYTHONPATH=$PWD "$PY" -m pmunity shaders "$UNITY_DATA" "$OUT/conv" --from d3d11)

echo "== convert (textures, settings, audio, quality)"
(cd "$TOOLKIT/convert" && PYTHONPATH=$PWD "$PY" -m pmunity convert "$UNITY_DATA" "$OUT/conv" \
    --config "$HERE/lam.convert.json" --steps textures,settings,audio,quality)

echo "== data tree"
cp -a "$UNITY_DATA" "$OUT/src"
cp -a "$OUT/conv/." "$OUT/src/"

echo "== managed patches"
"$DOTNET" build -c Release -o "$OUT/build/lampatch" "$HERE/tools/lampatch" >/dev/null
"$DOTNET" "$OUT/build/lampatch/lampatch.dll" "$OUT/src/Managed/Assembly-CSharp.dll" "$OUT/patched"
cp "$OUT/patched"/*.dll "$OUT/src/Managed/"
# the desktop build's Input System has no layout for the Android player's game controller
"$DOTNET" build -c Release -o "$OUT/build/asmpatch" "$TOOLKIT/tools/asmpatch" >/dev/null
"$DOTNET" "$OUT/build/asmpatch/asmpatch.dll" --only=inputsystem-android "$OUT/src/Managed" "$OUT/asmp"
cp "$OUT/asmp"/*.dll "$OUT/src/Managed/"

echo "== IL2CPP (no stripping: the data asks for engine types the linker drops)"
(cd "$TOOLKIT/convert" && PYTHONPATH=$PWD "$PY" -m pmunity il2cpp "$OUT/src" "$OUT/il2cpp" \
    --abi arm64-v8a --pkg "$UNITY_PLAYER" --unity 2019.4.4f1 --strip none --jobs "$JOBS")

echo "== pack"
(cd "$TOOLKIT/convert" && PYTHONPATH=$PWD "$PY" -m pmunity android-data --src "$OUT/src" --pkg "$UNITY_PLAYER" \
    --il2cpp "$OUT/il2cpp" --out "$OUT/pack" --name Lamentum --package com.pmunity.lamentum \
    --streaming-assets both --data-version keep --pack all)

echo "done: $OUT/pack/zip - add lib/{libmain,libunity}.so from the player and lib/libil2cpp.so from $OUT/il2cpp"
