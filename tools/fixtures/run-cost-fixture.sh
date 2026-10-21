#!/bin/sh
# CPU-only self-authored fixture, invoked through Spruce principal/standard_launch.
# Do not substitute the Lamentum launcher or run concurrently with MainUI.
set -u
ulimit -c 0
D=$(dirname "$0")
if pidof MainUI >/dev/null 2>&1; then
    printf 'Refused: MainUI still owns this session\n' >"$D/refused.txt"
    exit 2
fi
cat /proc/sys/kernel/random/boot_id >"$D/boot-id.txt"
printf 'fixture_launcher_pid=%s\n' "$$" >"$D/launcher-receipt.txt"
LC2_SVC_COST=1 "$D/lc2-cost-fixture" >"$D/on.txt" 2>&1
on=$?
LC2_SVC_COST=0 "$D/lc2-cost-fixture" >"$D/off.txt" 2>&1
off=$?
printf '{"on":%s,"off":%s}\n' "$on" "$off" >"$D/result.json"
sync
if [ "$on" -ne 0 ] || [ "$off" -ne 0 ]; then exit 1; fi
exit 0
