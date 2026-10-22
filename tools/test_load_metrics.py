import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import load_metrics

SYNTH = """NATIVE_PROBE_TIME_BUDGET seconds=900
NVN_TEXTURE_REAL object=0x1 format=0x44 size=8192x8192 levels=1 bytes=67108864 texture=1 depth=0 gpu-storage=allocated no-draw
LC2_BC_DEFERRED id=295 size=8192x8192 rgba-bytes=268435456 source=retained-guest-pool diagnostic=1
T2_TEXTURE_BUDGET add-bytes=268435456 live-MiB=411 count=151 budget-MiB=300
ROMFS_READ offset=0x0 size=0x50
NVN_PRESENT_PIXELS frame=806 nonblack=1656 max=154 white=0 texture-draws=2672 status=PIXELS
STOP status=T2_TEXTURE_BUDGET pc=main.text.seg+0x52d294 detail=0x19b
"""


class PayloadExecutionTests(unittest.TestCase):
    """The payload is a source string, so it can be compiled and checked without a device."""

    def test_payload_compiles(self):
        compile(load_metrics.PAYLOAD, '<payload>', 'exec')

    def test_payload_executes_against_a_synthetic_log(self):
        """Run the real payload locally with a rewritten log path: this is T0's missing test."""
        source = load_metrics.PAYLOAD.replace(
            "Path('/mnt/SDCARD/Roms/PORTS/lamentum-switch/logs/latest.log')", "Path(sys.argv[3])")
        source = source.replace("Path('/proc/meminfo').read_text().splitlines()", "[]")
        with tempfile.TemporaryDirectory() as td:
            log = Path(td) / 'latest.log'
            log.write_text(SYNTH)
            run = subprocess.run([sys.executable, '-c', source, '0', 'null', str(log)],
                                 capture_output=True, text=True, timeout=60)
            self.assertEqual(run.returncode, 0, run.stderr)
            out = json.loads(run.stdout)
        self.assertEqual(out['frame'], 806)
        self.assertEqual(out['stops'], ['T2_TEXTURE_BUDGET'])
        self.assertEqual(out['counters']['presents'], 1)
        self.assertEqual(out['counters']['textures'], 1)
        self.assertEqual(out['counters']['bc_deferred'], 1)
        self.assertEqual(out['counters']['budget_adds'], 1)
        self.assertIn('live-MiB=411', out['budget_last'])
        self.assertEqual(out['offset'], len(SYNTH))

    def test_payload_reports_rotation_instead_of_double_counting(self):
        source = load_metrics.PAYLOAD.replace(
            "Path('/mnt/SDCARD/Roms/PORTS/lamentum-switch/logs/latest.log')", "Path(sys.argv[3])")
        source = source.replace("Path('/proc/meminfo').read_text().splitlines()", "[]")
        with tempfile.TemporaryDirectory() as td:
            log = Path(td) / 'latest.log'
            log.write_text('short\n')
            run = subprocess.run([sys.executable, '-c', source, '999999', 'null', str(log)],
                                 capture_output=True, text=True, timeout=60)
            out = json.loads(run.stdout)
        self.assertTrue(out['rotated'])
        self.assertEqual(out['offset'], len('short\n'))


class ByteFramingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.log = Path(self.tmp.name) / 'latest.log'

    def poll(self, previous=None):
        # Exercise the exact request builder used by load_probe, including argument transport.
        source = load_metrics.collector_request(previous).replace(
            "Path('/mnt/SDCARD/Roms/PORTS/lamentum-switch/logs/latest.log')",
            'Path(%r)' % str(self.log))
        source = source.replace("Path('/proc/meminfo').read_text().splitlines()", "[]")
        run = subprocess.run([sys.executable, '-c', source], capture_output=True,
                             text=True, timeout=10)
        self.assertEqual(run.returncode, 0, run.stderr)
        return json.loads(run.stdout)

    def owned_header(self, run='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', pid=77):
        return {'schema': 1, 'run_uuid': run,
                'launch_nonce': 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',
                'boot_id': 'cccccccc-cccc-4ccc-8ccc-cccccccccccc', 'pid': pid, 'starttime': 42,
                'elf_dev': 1, 'elf_ino': 2, 'elf_sha256': 'a'*64,
                'launcher_sha256': 'b'*64, 'helper_sha256': 'c'*64,
                'image_sha256': None, 'catalogue_sha256': None, 'content_bindings_complete': False}

    def write_owned(self, header, body):
        self.log.write_bytes(b'LAMENTUM_RUN_HEADER ' + json.dumps(header, sort_keys=True).encode() + b'\n' + body)

    def owned_poll(self, previous=None, expected=None):
        self.assertIn('expected_run', __import__('inspect').signature(load_metrics.collector_request).parameters,
                      'collector has no owned-run contract')
        source = load_metrics.collector_request(previous, expected_run=expected).replace(
            "Path('/mnt/SDCARD/Roms/PORTS/lamentum-switch/logs/latest.log')", 'Path(%r)' % str(self.log))
        source = source.replace("Path('/proc/meminfo').read_text().splitlines()", '[]')
        run = subprocess.run([sys.executable, '-c', source], capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 0, run.stderr)
        return json.loads(run.stdout)

    def test_owned_same_inode_restart_at_greater_size_is_rejected(self):
        header = self.owned_header()
        self.write_owned(header, b'NVN_PRESENT_PIXELS frame=99 x\n')
        state = load_metrics.fold(None, self.owned_poll(expected={'run_uuid': header['run_uuid']}))
        inode = self.log.stat().st_ino
        newer = self.owned_header('dddddddd-dddd-4ddd-8ddd-dddddddddddd')
        self.write_owned(newer, b'NVN_PRESENT_PIXELS frame=3 x\n' + b'padding\n'*100)
        self.assertEqual(inode, self.log.stat().st_ino)
        sample = self.owned_poll(state)
        self.assertEqual(sample['status'], 'LOG_GENERATION_CHANGED')
        self.assertEqual(sample['counters']['presents'], 0)
        with self.assertRaisesRegex(RuntimeError, 'LOG_GENERATION_CHANGED'):
            load_metrics.fold(state, sample)
        self.assertEqual(state['presents'], 1)
        self.assertEqual(state['frame'], 99)

    def test_owned_new_inode_never_silently_resets_counter_baseline(self):
        header = self.owned_header()
        self.write_owned(header, b'NVN_PRESENT_PIXELS frame=9 x\n')
        state = load_metrics.fold(None, self.owned_poll(expected={'run_uuid': header['run_uuid']}))
        self.log.rename(self.log.with_suffix('.old'))
        self.write_owned(header, b'NVN_PRESENT_PIXELS frame=10 x\n')
        self.assertEqual(self.owned_poll(state)['status'], 'LOG_GENERATION_CHANGED')

    def test_owned_unchanged_header_but_rewritten_cursor_anchor_is_rejected(self):
        header = self.owned_header()
        self.write_owned(header, b'ROMFS_READ before\nNVN_PRESENT_PIXELS frame=99 x\n')
        state = load_metrics.fold(None, self.owned_poll(expected={'run_uuid': header['run_uuid']}))
        self.write_owned(header, b'ROMFS_READ after!\nNVN_PRESENT_PIXELS frame=88 x\n' + b'padding\n'*100)
        self.assertEqual(self.owned_poll(state)['status'], 'LOG_GENERATION_CHANGED')

    def test_owned_partial_records_preserve_identity_and_byte_cursor(self):
        header = self.owned_header()
        self.write_owned(header, b'\xff ROMFS_READ first\nNVN_PRESENT_PIXELS frame=8')
        state = load_metrics.fold(None, self.owned_poll(expected={'run_uuid': header['run_uuid']}))
        self.assertTrue(state['log_identity_qualified'])
        self.assertEqual(state['presents'], 0)
        with self.log.open('ab') as handle:
            handle.write(b'06 x\n')
        state = load_metrics.fold(state, self.owned_poll(state))
        self.assertEqual(state['presents'], 1)
        self.assertEqual(state['frame'], 806)
        self.assertEqual(state['run_header'], header)
        self.assertFalse(state['run_header']['content_bindings_complete'])

    def test_partial_replacement_header_cannot_downgrade_an_owned_cursor_to_pending(self):
        header = self.owned_header()
        self.write_owned(header, b'NVN_PRESENT_PIXELS frame=9 x\n')
        state = load_metrics.fold(None, self.owned_poll(expected={'run_uuid': header['run_uuid']}))
        self.log.write_bytes(b'LAMENTUM_RUN_HEADER ' + json.dumps(header).encode() + b' '*2048)
        result = self.owned_poll(state)
        self.assertEqual(result['status'], 'LOG_GENERATION_CHANGED')
        with self.assertRaisesRegex(RuntimeError, 'LOG_GENERATION_CHANGED'):
            load_metrics.fold(state, result)

    def test_owned_incomplete_header_is_pending_not_legacy_metrics(self):
        header = self.owned_header()
        raw = b'LAMENTUM_RUN_HEADER ' + json.dumps(header).encode()
        self.log.write_bytes(raw)
        sample = self.owned_poll(expected={'run_uuid': header['run_uuid']})
        self.assertEqual(sample['status'], 'LOG_HEADER_PENDING')
        self.assertEqual(sample['offset'], 0)
        self.assertEqual(sample['counters']['presents'], 0)
        with self.log.open('ab') as handle:
            handle.write(b'\nNVN_PRESENT_PIXELS frame=3 x\n')
        self.assertEqual(self.owned_poll(expected={'run_uuid': header['run_uuid']})['frame'], 3)

    def test_owned_same_uuid_but_reused_pid_generation_or_changed_elf_is_rejected(self):
        header = self.owned_header()
        for key, value in (('pid', 78), ('starttime', 43), ('elf_ino', 3), ('elf_sha256', 'd'*64)):
            with self.subTest(field=key):
                self.write_owned(header, b'NVN_PRESENT_PIXELS frame=9 x\n')
                state = load_metrics.fold(None, self.owned_poll(expected={'run_uuid': header['run_uuid']}))
                changed = dict(header, **{key: value})
                self.write_owned(changed, b'NVN_PRESENT_PIXELS frame=10 x\n' + b'padding\n'*100)
                self.assertEqual(self.owned_poll(state)['status'], 'LOG_GENERATION_CHANGED')

    def test_bounded_poll_reports_backlog_separately_from_split_line(self):
        from load_metrics import collect_log
        header = self.owned_header()
        self.write_owned(header, b'ROMFS_READ fixture\n' * 30000)
        first = collect_log(self.log, expected_run={'run_uuid': header['run_uuid']})
        self.assertLess(first['offset'], first['size'])
        self.assertIn('unconsumed_bytes', first, 'backlog and partial line bytes are conflated')
        self.assertGreater(first['unconsumed_bytes'], first['partial_bytes'])
        self.assertLess(first['partial_bytes'], len(b'ROMFS_READ fixture\n'))
        state = load_metrics.fold(None, dict(first, mem={}))
        for _ in range(10):
            if state['offset'] == state['size']:
                break
            second = collect_log(self.log, offset=state['offset'], expected_identity=state['identity'],
                                 expected_run=state['expected_run'], expected_header=state['header_sha256'],
                                 previous_anchor=state['anchor'])
            state = load_metrics.fold(state, dict(second, mem={}))
        self.assertEqual(state['romfs'], 30000)
        self.assertEqual(state['offset'], state['size'])

    def test_final_owned_read_returns_only_complete_current_run_text(self):
        import inspect
        self.assertIn('include_text', inspect.signature(load_metrics.collector_request).parameters,
                      'verified final log read is missing')
        header = self.owned_header()
        self.write_owned(header, b'NVN_PRESENT_PIXELS frame=7 x\nSTOP status=TIME_')
        source = load_metrics.collector_request(expected_run={'run_uuid': header['run_uuid']},
                                                include_text=True).replace(
            "Path('/mnt/SDCARD/Roms/PORTS/lamentum-switch/logs/latest.log')", 'Path(%r)' % str(self.log))
        source = source.replace("Path('/proc/meminfo').read_text().splitlines()", '[]')
        run = subprocess.run([sys.executable, '-c', source], text=True, capture_output=True, timeout=10)
        self.assertEqual(run.returncode, 0, run.stderr)
        result = json.loads(run.stdout)
        self.assertIn('frame=7', result['chunk_text'])
        self.assertNotIn('STOP status=', result['chunk_text'])
        self.assertEqual(result['partial_bytes'], len(b'STOP status=TIME_'))

    def test_legacy_parser_does_not_claim_owned_identity(self):
        self.log.write_text(SYNTH)
        self.assertIs(self.poll().get('log_identity_qualified'), False)

    def test_partial_present_not_counted_twice(self):
        prefix = b'ROMFS_READ a\n'
        self.log.write_bytes(prefix + b'NVN_PRESENT_PIXELS frame=80')
        first = self.poll()
        self.assertEqual(first['offset'], len(prefix))
        self.assertEqual(first['counters']['presents'], 0)
        self.assertIsNone(first['frame'])
        state = load_metrics.fold(None, first)
        with self.log.open('ab') as handle:
            handle.write(b'6 status=PIXELS\n')
        state = load_metrics.fold(state, self.poll(state))
        self.assertEqual(state['presents'], 1)
        self.assertEqual(state['frame'], 806)
        state = load_metrics.fold(state, self.poll(state))
        self.assertEqual(state['presents'], 1)
        self.assertEqual(state['romfs'], 1)

    def test_no_newline_means_no_consumption_or_stop(self):
        self.log.write_bytes(b'STOP status=T2_TEXTURE_BUDGET')
        first = self.poll()
        self.assertEqual(first['offset'], 0)
        self.assertEqual(first['stops'], [])
        with self.log.open('ab') as handle:
            handle.write(b'\n')
        second = self.poll(first)
        self.assertEqual(second['stops'], ['T2_TEXTURE_BUDGET'])
        self.assertEqual(second['offset'], self.log.stat().st_size)

    def test_invalid_and_split_utf8_preserve_byte_cursor(self):
        self.log.write_bytes(b'\xff ROMFS_READ a\n\xe2\x82')
        first = self.poll()
        self.assertEqual(first['offset'], len(b'\xff ROMFS_READ a\n'))
        self.assertEqual(first['counters']['romfs'], 1)
        with self.log.open('ab') as handle:
            handle.write(b'\xac NVN_PRESENT_PIXELS frame=9 x\n')
        second = self.poll(first)
        self.assertEqual(second['frame'], 9)
        self.assertEqual(second['offset'], self.log.stat().st_size)
        self.assertEqual(second['counters']['romfs'], 0)

    def test_new_inode_at_equal_or_greater_length_resets(self):
        for extra in (b'', b'extra padding\n'):
            with self.subTest(extra=extra):
                self.log.write_bytes(b'NVN_PRESENT_PIXELS frame=99 x\n')
                state = load_metrics.fold(None, self.poll())
                # Keep old inode alive to prevent allocator reuse.
                old = self.log.with_suffix('.old')
                self.log.replace(old)
                self.log.write_bytes(b'NVN_PRESENT_PIXELS frame=03 x\n' + extra)
                second = self.poll(state)
                self.assertTrue(second['rotated'])
                self.assertNotEqual(second['identity'], state['identity'])
                state = load_metrics.fold(state, second)
                self.assertEqual(state['presents'], 1)
                self.assertEqual(state['frame'], 3)
                old.unlink()

    def test_truncation_then_append_uses_new_cursor(self):
        self.log.write_text(SYNTH)
        state = load_metrics.fold(None, self.poll())
        self.log.write_bytes(b'ROMFS_READ fresh\n')
        second = self.poll(state)
        self.assertTrue(second['rotated'])
        state = load_metrics.fold(state, second)
        self.assertEqual(state['presents'], 0)
        self.assertIsNone(state['frame'])
        self.assertEqual(state['stops'], [])
        with self.log.open('ab') as handle:
            handle.write(b'NVN_PRESENT_PIXELS frame=2 x\n')
        state = load_metrics.fold(state, self.poll(state))
        self.assertEqual(state['presents'], 1)
        self.assertEqual(state['frame'], 2)


class FoldTests(unittest.TestCase):
    def test_diagnostic_stop_substring_does_not_create_runtime_stop(self):
        chunk = chr(10).join((
            'LC2_MENU_LEDGER_PRESTOP status=gl-lock-unavailable',
            'LC2_MENU_FLOOR_CAPTURE status=gl-lock-unavailable',
            'STOP status=T2_MEMORY_FLOOR',
        )) + chr(10)
        self.assertEqual(load_metrics.parse_chunk(chunk)['stops'], ['T2_MEMORY_FLOOR'])

    def test_counters_accumulate_and_frames_take_the_latest(self):
        first = load_metrics.parse_chunk('NVN_PRESENT_PIXELS frame=10 x\nROMFS_READ a\n')
        first.update(offset=10, size=10, rotated=False, mem={'MemAvailable': 100})
        running = load_metrics.fold(None, first)
        second = load_metrics.parse_chunk('NVN_PRESENT_PIXELS frame=12 x\nROMFS_READ b\nSTOP status=T2_TEXTURE_BUDGET\n')
        second.update(offset=20, size=20, rotated=False, mem={'MemAvailable': 50})
        running = load_metrics.fold(running, second)
        self.assertEqual(running['presents'], 2)
        self.assertEqual(running['romfs'], 2)
        self.assertEqual(running['frame'], 12)
        self.assertEqual(running['stops'], ['T2_TEXTURE_BUDGET'])
        self.assertEqual(running['mem']['MemAvailable'], 50)

    def test_rotation_resets_running_totals(self):
        first = load_metrics.parse_chunk('NVN_PRESENT_PIXELS frame=99 x\n')
        first.update(offset=5, size=5, rotated=False, mem={})
        running = load_metrics.fold(None, first)
        fresh = load_metrics.parse_chunk('NVN_PRESENT_PIXELS frame=3 x\n')
        fresh.update(offset=4, size=4, rotated=True, mem={})
        running = load_metrics.fold(running, fresh)
        self.assertEqual(running['presents'], 1)
        self.assertEqual(running['frame'], 3)

    def test_killed_flag_is_sticky(self):
        first = load_metrics.parse_chunk('Killed  ./lamentum-nextos\n')
        first.update(offset=1, size=1, rotated=False, mem={})
        running = load_metrics.fold(None, first)
        calm = load_metrics.parse_chunk('NVN_PRESENT_PIXELS frame=1 x\n')
        calm.update(offset=2, size=2, rotated=False, mem={})
        self.assertTrue(load_metrics.fold(running, calm)['killed'])


if __name__ == '__main__':
    unittest.main()


class PresentSerialTests(unittest.TestCase):
    def test_highest_frame_wins_and_missing_marker_is_zero(self):
        from load_metrics import present_serial
        text = ('NVN_PRESENT_PIXELS frame=1 nonblack=0 status=BLACK-SAMPLE\n'
                'NVN_PRESENT_PIXELS frame=42 nonblack=7 status=PIXELS\n'
                'NVN_PRESENT_PIXELS frame=9 nonblack=7 status=PIXELS\n'
                'ZERO_TEXTURE_FLUSH_UPLOADED id=3\n')
        self.assertEqual(present_serial(text), 42)
        self.assertEqual(present_serial('no presents here\n'), 0)
        self.assertEqual(present_serial(''), 0)


    def test_owned_serial_reads_incrementally_and_refuses_a_rotated_generation(self):
        from load_metrics import OwnedSerial
        chunks = [
            {'status': 'ok', 'chunk_text': 'NVN_PRESENT_PIXELS frame=1 status=PIXELS\n'
                                           'NVN_PRESENT_PIXELS frame=42 status=PIXELS\n'
                                           'NVN_PRESENT_PIXELS frame=9 status=PIXELS\n'},
            {'status': 'ok', 'chunk_text': ''},
            {'status': 'LOG_GENERATION_CHANGED', 'detail': 'opened-file identity changed'},
        ]
        seen = []

        def remote(payload):
            seen.append(payload)
            return chunks[min(len(seen) - 1, len(chunks) - 1)]

        reader = OwnedSerial()
        first = reader.poll(remote)
        self.assertEqual((first['status'], first['serial'], first['fresh']), ('ok', 42, True))
        second = reader.poll(remote)
        self.assertEqual((second['serial'], second['fresh']), (42, False))
        rotated = reader.poll(remote)
        self.assertEqual(rotated['status'], 'LOG_GENERATION_CHANGED')
        self.assertIsNone(rotated['serial'], 'a rejected generation must not hand back the old serial')

    def test_owned_serial_ignores_a_partial_trailing_line(self):
        from load_metrics import OwnedSerial
        script = [{'status': 'ok', 'chunk_text': 'NVN_PRESENT_PIXELS frame=7 status=PI'},
                  {'status': 'ok', 'chunk_text': 'NVN_PRESENT_PIXELS frame=7 status=PIXELS\n'}]
        reader = OwnedSerial()
        calls = []
        first = reader.poll(lambda payload: (calls.append(payload), script[0])[1])
        self.assertEqual((first['serial'], first['fresh']), (0, False))
        second = reader.poll(lambda payload: script[1])
        self.assertEqual(second['serial'], 7)

    def test_a_rotated_run_never_lends_its_serial_to_the_next_generation(self):
        """Roadmap 40.12: run A at frame 50, rotate to B at frame 1 - refuse, never reuse 50."""
        from load_metrics import OwnedSerial
        run_a = {'status': 'ok', 'chunk_text': 'NVN_PRESENT_PIXELS frame=50 status=PIXELS\n',
                 'offset': 4096}
        rotation = {'status': 'LOG_GENERATION_CHANGED',
                    'detail': 'previously owned header was truncated'}
        reader = OwnedSerial(expected_run={'run_uuid': 'a'})
        first = reader.poll(lambda payload: run_a)
        self.assertEqual((first['serial'], first['fresh']), (50, True))
        refused = reader.poll(lambda payload: rotation)
        self.assertIsNone(refused['serial'])
        self.assertEqual(refused['status'], 'LOG_GENERATION_CHANGED')
        self.assertFalse(refused['fresh'], 'a refused generation must not look like a fresh frame')
        self.assertEqual(reader.serial, 50, 'the old counter stays as history, not as a usable serial')

    def test_owned_serial_advances_its_cursor_instead_of_rescanning(self):
        from load_metrics import OwnedSerial
        states = [{'status': 'ok', 'chunk_text': 'NVN_PRESENT_PIXELS frame=5 status=PIXELS\n',
                   'offset': 100, 'identity': {'dev': 1, 'ino': 2}}]
        payloads = []
        reader = OwnedSerial()
        reader.poll(lambda payload: (payloads.append(payload), states[0])[1])
        self.assertEqual(reader.state.get('offset'), 100)
        second = '[%r]' % reader.state
        self.assertIn('100', second)

    def test_a_large_backlog_is_parsed_from_the_chunk_only(self):
        from load_metrics import OwnedSerial
        text = ''.join('NVN_PRESENT_PIXELS frame=%d status=PIXELS\n' % n for n in range(1, 30001))
        reader = OwnedSerial()
        result = reader.poll(lambda payload: {'status': 'ok', 'chunk_text': text})
        self.assertEqual(result['serial'], 30000)
        self.assertTrue(result['fresh'])
