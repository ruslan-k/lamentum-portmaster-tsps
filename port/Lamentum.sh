#!/bin/bash
# Lamentum — experimental native Horizon runtime launcher (Switch ARM64 -> TSPS/SpruceOS).
# Launch only through the Spruce/PortMaster principal flow; never beside another game.
GAMEDIR=/mnt/SDCARD/Roms/PORTS/lamentum-switch
cd "$GAMEDIR" || exit 1
mkdir -p logs save-laboratory
LOG="$GAMEDIR/logs/latest.log"
exec >"$LOG" 2>&1
printf 'LAMENTUM_LAUNCH native-horizon budget=%ss shader-catalogue=absent\n' "${LAMENTUM_PROBE_SECONDS:-0}"
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
# Bounded diagnostic budget; 0 = no alarm (ordinary play).
export MEGAMAN_PROBE_SECONDS="${LAMENTUM_PROBE_SECONDS:-0}"
export AW_RELEASE="${AW_RELEASE:-1}"

exec ./lamentum-nextos
