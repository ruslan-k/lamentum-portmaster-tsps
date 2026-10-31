#!/bin/bash
# Lamentum - SpruceOS launcher (standalone: no PortMaster control.txt needed).
P=/mnt/SDCARD/Roms/PORTS/lamentum
cd "$P" || exit 1
# one instance only: a second ua_host fights the first for DRM (pageflip -16) and doubles RAM use
exec 9>"$P/.run.lock"
flock -n 9 || exit 0
exec >"$P/log.txt" 2>&1

# Spruce's UI is PyUI (mainui.py) and its process name is not always "MainUI": match both. Left
# running, it keeps the DRM plane and the ALSA device, and the game's page flips fail with -16.
for pid in $(pgrep -f "[m]ainui.py"; pgrep -x MainUI); do kill -TERM "$pid" 2>/dev/null; done
sleep 3
for pid in $(pgrep -f "[m]ainui.py"; pgrep -x MainUI); do kill -9 "$pid" 2>/dev/null; done

export SDL_VIDEODRIVER=kmsdrm
export SDL_AUDIODRIVER=alsa
export AUDIODEV=plughw:0,0
export UA_AUDIO_SINK=pipe
export UA_FPS=0   # no frame-stat lines in the log
. ./port.env   # runtime options; a variable already set in the environment wins

./ua_host "$P"

pgrep -f "[m]ainui.py" >/dev/null || pgrep -x MainUI >/dev/null || \
    setsid /mnt/SDCARD/spruce/flip/bin/MainUI /mnt/SDCARD/App/PyUI/main-ui/mainui.py >/dev/null 2>&1 &
