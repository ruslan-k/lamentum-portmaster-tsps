#!/usr/bin/env python3
"""Exercise the launcher with a fake runtime/sysfs tree, never a real device."""
import os
import pathlib
import subprocess
import tempfile
import unittest

class LauncherTests(unittest.TestCase):
    def test_defaults_exit_and_cpu_restore(self):
        source = (pathlib.Path(__file__).parents[1] / 'port/Lamentum.sh').read_text()
        with tempfile.TemporaryDirectory(prefix='lamentum-launcher-') as root:
            root = pathlib.Path(root)
            game, cpu = root / 'game', root / 'cpu'
            game.mkdir()
            for index, state in enumerate(('0', '1', '0', '1')):
                p = cpu / ('cpu%d' % index) / 'online'
                p.parent.mkdir(parents=True)
                p.write_text(state)
            runtime = game / 'lamentum-nextos'
            runtime.write_text('#!/bin/bash\n'
                'printf "%s %s %s %s %s %s\\n" "$LC2_GLES3" "$COTM_ASYNC_QUEUE" '
                '"$COTM_FB_PRESENT" "$COTM_GL_ERROR_IGNORE" "$LC2_TEXTURE_PAGEOUT" '
                '"$T2_MEMORY_FLOOR_MIB" > defaults.txt\n'
                'exit 7\n')
            runtime.chmod(0o755)
            launcher = root / 'launch.sh'
            launcher.write_text(source.replace('/mnt/SDCARD/Roms/PORTS/lamentum-switch', str(game))
                               .replace('/sys/devices/system/cpu', str(cpu)))
            env = {k: v for k, v in os.environ.items()
                   if not k.startswith(('LC2_', 'COTM_', 'T2_', 'LAMENTUM_'))}
            result = subprocess.run(['bash', str(launcher)], env=env)
            self.assertEqual(result.returncode, 7)
            self.assertEqual((game / 'defaults.txt').read_text().strip(), '1 0 0 0 0 96')
            self.assertEqual(''.join((cpu / ('cpu%d' % i) / 'online').read_text()
                                    for i in range(4)), '0101')

if __name__ == '__main__':
    unittest.main()
