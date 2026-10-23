#!/usr/bin/env python3
"""Exercise the launcher with a fake runtime/sysfs tree, never a real device."""
import os
import pathlib
import subprocess
import tempfile
import unittest
import json
import hashlib

class LauncherTests(unittest.TestCase):
    def test_defaults_exit_and_cpu_restore(self):
        source = (pathlib.Path(__file__).parents[1] / 'port/Lamentum.sh').read_text()
        with tempfile.TemporaryDirectory(prefix='lamentum-launcher-') as root:
            root = pathlib.Path(root)
            game, cpu = root / 'game', root / 'cpu'
            game.mkdir()
            (game / 'run_identity.py').write_bytes((pathlib.Path(__file__).parents[1] / 'tools/run_identity.py').read_bytes())
            for index, state in enumerate(('0', '1', '0', '1')):
                p = cpu / ('cpu%d' % index) / 'online'
                p.parent.mkdir(parents=True)
                p.write_text(state)
                p.chmod(0o444)
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
            no_stat = root / 'no-stat-bin'
            no_stat.mkdir()
            (no_stat / 'stat').write_text('#!/bin/sh\nexit 127\n')
            (no_stat / 'stat').chmod(0o755)
            env['PATH'] = str(no_stat) + os.pathsep + env['PATH']
            result = subprocess.run(['bash', str(launcher)], env=env)
            self.assertEqual(result.returncode, 7)
            self.assertEqual((game / 'defaults.txt').read_text().strip(), '1 0 0 0 0 96')
            self.assertEqual(''.join((cpu / ('cpu%d' % i) / 'online').read_text()
                                    for i in range(4)), '0101')
            self.assertEqual([((cpu / ('cpu%d' % i) / 'online').stat().st_mode & 0o777)
                              for i in range(4)], [0o444] * 4)
            lines = (game / 'logs/latest.log').read_text().splitlines()
            self.assertTrue(lines[0].startswith('LAMENTUM_RUN_HEADER '), lines[:2])
            first = json.loads(lines[0].split(' ', 1)[1])
            self.assertFalse(first['content_bindings_complete'])
            again = subprocess.run(['bash', str(launcher)], env=env)
            self.assertEqual(again.returncode, 7)
            second = json.loads((game / 'logs/latest.log').read_text().splitlines()[0].split(' ', 1)[1])
            self.assertNotEqual(first['run_uuid'], second['run_uuid'])
            self.assertEqual(''.join((cpu / ('cpu%d' % i) / 'online').read_text()
                                    for i in range(4)), '0101')

    def test_candidate_launcher_uses_isolated_elf_and_preserves_guards(self):
        repo = pathlib.Path(__file__).parents[1]
        source = (repo / 'evidence/current-host-elf-staging-preflight-2026-10-23/'
                  'candidate-Lamentum.sh').read_text()
        self.assertNotIn('/sys/devices/system/cpu', source)
        self.assertNotIn('CPU_RESTORE', source)
        self.assertIn('export MEGAMAN_PROBE_SECONDS=30', source)
        self.assertIn('export LAMENTUM_PROBE_SECONDS=30', source)
        self.assertIn('export T2_MEMORY_FLOOR_MIB=96 T2_TEXTURE_BUDGET_MIB=300', source)
        self.assertNotIn('T2_STORAGE_MARGIN_MIB=', source)
        with tempfile.TemporaryDirectory(prefix='lamentum-candidate-') as directory:
            root = pathlib.Path(directory)
            game = root / 'game'
            candidate = game / '.candidate-h2a-20261023'
            candidate.mkdir(parents=True)
            helper = candidate / 'run_identity.py'
            helper.write_bytes((repo / 'tools/run_identity.py').read_bytes())
            runtime = candidate / 'lamentum-nextos'
            runtime.write_text(
                '#!/bin/bash\n'
                'printenv > defaults.txt\n'
                'exit 7\n')
            runtime.chmod(0o755)
            launcher = candidate / 'Lamentum.sh'
            launcher.write_text(source.replace(
                'GAMEDIR=/mnt/SDCARD/Roms/PORTS/lamentum-switch', f'GAMEDIR={game}'))
            launcher.chmod(0o755)
            syntax = subprocess.run(['bash', '-n', str(launcher)], capture_output=True, text=True)
            self.assertEqual(syntax.returncode, 0, syntax.stderr)
            env = {key: value for key, value in os.environ.items()
                   if not key.startswith(('LC2_', 'COTM_', 'T2_', 'LAMENTUM_', 'MEGAMAN_'))}
            env.update({'LAMENTUM_PROBE_SECONDS': '0', 'MEGAMAN_PROBE_SECONDS': '0',
                        'T2_MEMORY_FLOOR_MIB': '32', 'T2_TEXTURE_BUDGET_MIB': '420',
                        'T2_LAZY_MESH': '1', 'AW_RELEASE': '0', 'LC2_GLES3': '0',
                        'COTM_ASYNC_QUEUE': '1', 'T2_GPU_PIPELINE': '1',
                        'COTM_FB_PRESENT': '1', 'COTM_GL_ERROR_IGNORE': '1',
                        'LC2_TEXTURE_PAGEOUT': '1', 'LC2_BC_STRIPE_MEDIUM': '1'})
            result = subprocess.run(['bash', str(launcher)], env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 7, result.stderr)
            runtime_env = dict(line.split('=', 1) for line in (game / 'defaults.txt').read_text().splitlines())
            for key, value in {
                'MEGAMAN_PROBE_SECONDS': '30', 'LAMENTUM_PROBE_SECONDS': '30',
                'T2_MEMORY_FLOOR_MIB': '96', 'T2_TEXTURE_BUDGET_MIB': '300',
                'T2_LAZY_MESH': '0', 'AW_RELEASE': '1', 'LC2_GLES3': '1',
                'COTM_ASYNC_QUEUE': '0', 'T2_GPU_PIPELINE': '0',
                'COTM_FB_PRESENT': '0', 'COTM_GL_ERROR_IGNORE': '0',
                'LC2_TEXTURE_PAGEOUT': '0', 'LC2_BC_STRIPE_MEDIUM': '0',
            }.items():
                self.assertEqual(runtime_env.get(key), value, key)
            self.assertNotIn('T2_STORAGE_MARGIN_MIB', runtime_env)
            lines = (candidate / 'logs/latest.log').read_text().splitlines()
            header = json.loads(lines[0].split(' ', 1)[1])
            self.assertEqual(header['launcher_sha256'], hashlib.sha256(launcher.read_bytes()).hexdigest())
            self.assertEqual(header['helper_sha256'], hashlib.sha256(helper.read_bytes()).hexdigest())
            self.assertEqual(header['elf_sha256'], hashlib.sha256(runtime.read_bytes()).hexdigest())

if __name__ == '__main__':
    unittest.main()
