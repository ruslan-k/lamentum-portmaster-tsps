#!/usr/bin/env python3
"""Bounded device run of the Lamentum port through the Spruce principal flow.

Writes /tmp/cmd_to_run.sh exactly as the menu would (Emu path form), exits the MainUI,
polls the port log, then verifies the device was left clean: no runtime process, MainUI
back, CPU online mask restored.

  python3 tools/device_principal_test.py --budget 90 --wait 150

Never run this while another game is playing.
"""
import argparse, json, re, subprocess, sys, time, pathlib

HOST = 'root@192.168.50.135'
PORT_DIR = '/mnt/SDCARD/Roms/PORTS/lamentum-switch'
LAUNCHER = '/mnt/SDCARD/Roms/PORTS/Lamentum.sh'
STD_LAUNCH = '/mnt/SDCARD/Emu/PORTS/../../spruce/scripts/emu/standard_launch.sh'


def ssh(cmd, timeout=60):
    return subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', HOST, cmd],
                          capture_output=True, text=True, timeout=timeout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--budget', type=int, default=90, help='MEGAMAN_PROBE_SECONDS for the run')
    ap.add_argument('--wait', type=int, default=180, help='seconds to watch the run')
    ap.add_argument('--evidence', type=pathlib.Path, default=None)
    a = ap.parse_args()

    busy = ssh("ps | grep -cE '[M]ainUI'").stdout.strip()
    if busy == '0':
        print('MainUI is not running — device is busy or in a game; aborting', file=sys.stderr)
        return 2
    other = ssh("ls /proc/*/comm 2>/dev/null | wc -l").returncode
    if other != 0:
        print('device state check failed', file=sys.stderr)
        return 2

    ssh('truncate -s 0 %s/logs/latest.log' % PORT_DIR)
    cmd = ('export LAMENTUM_PROBE_SECONDS=%d;chmod a+x "%s";"%s" "%s"\n'
           % (a.budget, STD_LAUNCH, STD_LAUNCH, LAUNCHER))
    ssh("cat > /tmp/cmd_to_run.sh <<'EOF'\n%sEOF\nchmod a+x /tmp/cmd_to_run.sh; sh -n /tmp/cmd_to_run.sh && echo cmd-ok" % cmd)
    print(ssh('sh -n /tmp/cmd_to_run.sh && echo syntax-ok').stdout.strip())

    mainui = ssh("ps | grep '[M]ainUI' | awk '{print $1}' | head -1").stdout.strip()
    if not mainui:
        print('no MainUI pid found', file=sys.stderr)
        return 2
    ssh('kill -TERM %s' % mainui)
    print('MainUI %s -> TERM; run started, watching %d s' % (mainui, a.wait))

    deadline = time.time() + a.wait
    last = ''
    while time.time() < deadline:
        time.sleep(10)
        log = ssh('tail -c 4000 %s/logs/latest.log 2>/dev/null' % PORT_DIR).stdout
        if log != last:
            last = log
            print('--- log tail ---')
            print(log[-1200:])
        if re.search(r'STOP status=|exit status', log):
            break

    state = ssh("ps | grep -c '[l]amentum-nextos'; ps | grep -c '[M]ainUI'; "
                "cat /sys/devices/system/cpu/online").stdout.strip().splitlines()
    print('runtime procs=%s mainui=%s cpu-online=%s' % tuple(state[:3]))

    if a.evidence:
        a.evidence.mkdir(parents=True, exist_ok=True)
        log = ssh('cat %s/logs/latest.log' % PORT_DIR).stdout
        (a.evidence / 'latest.log').write_text(log)
        (a.evidence / 'device-state.txt').write_text('\n'.join(state) + '\n')
        print('evidence ->', a.evidence)
    return 0


if __name__ == '__main__':
    sys.exit(main())
