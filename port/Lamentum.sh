#!/bin/bash
# Lamentum — experimental native Horizon runtime launcher (Switch ARM64 -> TSPS/SpruceOS).
# Launch only through the Spruce/PortMaster principal flow; never beside another game.
GAMEDIR=/mnt/SDCARD/Roms/PORTS/lamentum-switch
cd "$GAMEDIR" || exit 1
mkdir -p logs save-laboratory
LOG="$GAMEDIR/logs/latest.log"
exec >"$LOG" 2>&1
printf 'LAMENTUM_LAUNCH native-horizon budget=%ss shader-catalogue=draft-with-TEST-substitutes\n' "${LAMENTUM_PROBE_SECONDS:-120}"
printf 'LAMENTUM_BUILD_ID sha256=%s\n' "$(sha256sum ./lamentum-nextos 2>/dev/null | cut -d ' ' -f1)"

# The recovered runtime pins its threads to cores 0-3, which Spruce keeps offline.
# Remember each file's original state and restore it on exit.
CPU_RESTORE=""
for c in 0 1 2 3; do
    p="/sys/devices/system/cpu/cpu${c}/online"
    [ -e "$p" ] || continue
    previous=$(cat "$p")
    CPU_RESTORE="$CPU_RESTORE $c:$previous"
    chmod u+w "$p" 2>/dev/null || true
    if [ "$previous" = 0 ]; then printf 1 >"$p" || true; fi
done
restore_cpu() {
    for entry in $CPU_RESTORE; do
        c=${entry%%:*}; want=${entry##*:}
        p="/sys/devices/system/cpu/cpu${c}/online"
        [ -e "$p" ] || continue
        printf '%s' "$want" >"$p" 2>/dev/null || true
    done
}
trap restore_cpu EXIT

export HOME="$GAMEDIR"
export SDL_VIDEODRIVER=kmsdrm SDL_AUDIODRIVER=alsa
# SDL's crash handlers hide the runtime's own fault reporting.
export SDL_NO_SIGNAL_HANDLERS=1
# TSPS trimsui virtual pad: SDL GUID carries a CRC16 of the device name.
export SDL_GAMECONTROLLERCONFIG='0300a3845e0400008e02000014010000,TRIMUI Player1,a:b0,b:b1,back:b6,dpdown:h0.4,dpleft:h0.8,dpright:h0.2,dpup:h0.1,guide:b8,leftshoulder:b4,leftstick:b9,lefttrigger:a2,leftx:a0,lefty:a1,rightshoulder:b5,rightstick:b10,righttrigger:a5,rightx:a3,righty:a4,start:b7,x:b2,y:b3,platform:Linux,'
export COTM_RUN_ID=$(date +%s)
# The baseline's lazy-mesh IL2CPP patch is keyed to another title's main module (segment size
# and text SHA-256 pins); on this title it fail-closes as T2_LAZY_MESH_SEGMENT. It is a load-time
# optimisation only, so it stays off here.
export T2_LAZY_MESH="${T2_LAZY_MESH:-0}"
# Bounded bring-up only: no playable launch is claimed. Explicit 0 disables the timer.
export MEGAMAN_PROBE_SECONDS="${LAMENTUM_PROBE_SECONDS:-120}"
export AW_RELEASE="${AW_RELEASE:-1}"
export LC2_GLES3="${LC2_GLES3:-1}"
# Synchronous completion and SDL/KMSDRM swaps are the measured path.
export COTM_ASYNC_QUEUE="${COTM_ASYNC_QUEUE:-0}" T2_GPU_PIPELINE="${T2_GPU_PIPELINE:-0}"
export COTM_FB_PRESENT="${COTM_FB_PRESENT:-0}" COTM_GL_ERROR_IGNORE="${COTM_GL_ERROR_IGNORE:-0}"
# Keep the failed pageout experiment off and stop early under scene-load pressure.
export LC2_TEXTURE_PAGEOUT="${LC2_TEXTURE_PAGEOUT:-0}"
export T2_MEMORY_FLOOR_MIB="${T2_MEMORY_FLOOR_MIB:-96}"

# Do not exec: replacing this shell prevents its EXIT trap from restoring CPU state.
./lamentum-nextos
status=$?
exit "$status"
