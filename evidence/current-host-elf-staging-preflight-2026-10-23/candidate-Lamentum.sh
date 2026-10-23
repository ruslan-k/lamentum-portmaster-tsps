#!/bin/bash
# Inert candidate launcher for the hidden H2a staging directory; never menu-discovered.
# Uses the production asset root but keeps the candidate ELF/helper/logs isolated.
LAUNCHER_PATH=$(readlink -f -- "${BASH_SOURCE[0]}") || exit 1
GAMEDIR=/mnt/SDCARD/Roms/PORTS/lamentum-switch
CANDIDATE_DIR="$GAMEDIR/.candidate-h2a-20261023"
cd "$GAMEDIR" || exit 1
mkdir -p "$CANDIDATE_DIR/logs" "$GAMEDIR/save-laboratory"
LOG="$CANDIDATE_DIR/logs/latest.log"
exec >"$LOG" 2>&1
[ -r "$CANDIDATE_DIR/run_identity.py" ] || { printf 'LAMENTUM_RUN_HELPER_MISSING\n'; exit 1; }
[ -x "$CANDIDATE_DIR/lamentum-nextos" ] || { printf 'LAMENTUM_RUNTIME_MISSING_OR_NOT_EXECUTABLE\n'; exit 1; }

export HOME="$GAMEDIR"
export SDL_VIDEODRIVER=kmsdrm SDL_AUDIODRIVER=alsa
export SDL_NO_SIGNAL_HANDLERS=1
export SDL_GAMECONTROLLERCONFIG='0300a3845e0400008e02000014010000,TRIMUI Player1,a:b0,b:b1,back:b6,dpdown:h0.4,dpleft:h0.8,dpright:h0.2,dpup:h0.1,guide:b8,leftshoulder:b4,leftstick:b9,lefttrigger:a2,leftx:a0,lefty:a1,rightshoulder:b5,rightstick:b10,righttrigger:a5,rightx:a3,righty:a4,start:b7,x:b2,y:b3,platform:Linux,'
export T2_LAZY_MESH=0
export MEGAMAN_PROBE_SECONDS=30
export LAMENTUM_PROBE_SECONDS=30
export AW_RELEASE=1 LC2_GLES3=1
export COTM_ASYNC_QUEUE=0 T2_GPU_PIPELINE=0
export COTM_FB_PRESENT=0 COTM_GL_ERROR_IGNORE=0
export LC2_TEXTURE_PAGEOUT=0 LC2_BC_STRIPE_MEDIUM=0
# Preserve the approved guards; the uncertainty margin is deliberately not set here.
export T2_MEMORY_FLOOR_MIB=96 T2_TEXTURE_BUDGET_MIB=300

run_args=()
if [ "${LAMENTUM_RUN_UUID+x}" ]; then run_args+=(--run-uuid "$LAMENTUM_RUN_UUID"); fi
python3 "$CANDIDATE_DIR/run_identity.py" exec --runtime "$CANDIDATE_DIR/lamentum-nextos" --launcher "$LAUNCHER_PATH" "${run_args[@]}"
status=$?
exit "$status"
