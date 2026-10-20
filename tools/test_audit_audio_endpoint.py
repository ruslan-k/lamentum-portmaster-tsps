import hashlib
import tempfile
import unittest
from pathlib import Path
from audit_audio_endpoint import audit, summarize_arbitration_log, summarize_audio_log


class AudioEndpointAuditTests(unittest.TestCase):
    def test_wrong_elf_pin_aborts_before_source_or_compiler_access(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)
            elf = p / 'self-authored-not-an-elf.fixture'
            elf.write_bytes(b'unit fixture, never executed')
            with self.assertRaisesRegex(ValueError, 'ELF hash mismatch'):
                audit(p / 'absent-source', elf, p / 'absent-log', '0' * 64, p / 'absent-overlay')

    def test_mismatched_or_multiple_log_build_ids_abort_before_source_access(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)
            elf = p / 'self-authored.fixture'
            elf.write_bytes(b'unit fixture, never executed')
            sha = hashlib.sha256(elf.read_bytes()).hexdigest()
            log = p / 'capture.fixture'
            for text in ('LAMENTUM_BUILD_ID sha256=' + '0' * 64 + '\n',
                         ('LAMENTUM_BUILD_ID sha256=' + sha + '\n') * 2):
                log.write_text(text)
                with self.assertRaisesRegex(ValueError, 'exactly one matching executable build ID'):
                    audit(p / 'absent-source', elf, log, sha, p / 'absent-overlay')

    def test_arbitration_mutex_address_uses_different_registers_for_lock_and_unlock(self):
        text = ('SVC id=0x1a thread=0x2 pc=sdk.text.seg+0x100 arg0x0=0x444 arg0x1=0x340000048 arg0x2=0x445\n'
                'SVC id=0x1b thread=0x2 pc=sdk.text.seg+0x104 arg0x0=0x340000048 arg0x1=0xffffffff arg0x2=0x0\n')
        report = summarize_arbitration_log(text)
        self.assertEqual(report['mutex_addresses'], [['0x340000048', 2]])
        self.assertEqual(report['distinct_mutex_addresses'], 1)
        self.assertEqual(report['unlock_arg1_ffffffff_occurrences'], 1)
        self.assertNotIn('0xffffffff', dict(report['mutex_addresses']))

    def test_endpoint_tag_is_not_handle_and_other_endpoints_are_not_counted(self):
        text = ('GET_SERVICE name=audout:u\nAUDOUT_OPEN rate=48000 channels=2 PCM=S16 state=stopped\n'
                'IPC handle=0x45a endpoint=0x40 type=0x6 command=0x7 data_bytes=0x14\n'
                'IPC handle=0x45a endpoint=0x40 type=0x6 command=0x8 data_bytes=0x8\n'
                'IPC handle=0x40 endpoint=0x1d type=0x6 command=0x8 data_bytes=0x8\n')
        report = summarize_audio_log(text, manager=63, child=64)
        self.assertEqual(report['child_commands'], {'7': 1, '8': 1})
        self.assertEqual(report['child_handles'], ['0x45a'])
        self.assertEqual(report['service_requests'], 1)
        self.assertEqual(report['successful_opens'], 1)
        self.assertNotIn('cpu_share', report)

    def test_interval_audio_counts_sum_but_cumulative_nonzero_does_not(self):
        text = ('AUDOUT_HOST_PROFILE consumed-frames=10 underrun-frames=2 queue=3 buffers=1 nonzero-total=100 scope=interval\n'
                'AUDOUT_HOST_PROFILE consumed-frames=20 underrun-frames=4 queue=0 buffers=1 nonzero-total=120 scope=interval\n')
        report = summarize_audio_log(text, manager=63, child=64)
        self.assertEqual(report['audio_host']['consumed_frames'], 30)
        self.assertEqual(report['audio_host']['underrun_frames'], 6)
        self.assertEqual(report['audio_host']['maximum_nonzero_total'], 120)
        self.assertFalse(report['audio_host']['audibility_verified'])

    def test_malformed_child_receipt_does_not_increment_command_count(self):
        report = summarize_audio_log('IPC endpoint=0x40 command=0x7 handle=not-an-integer\n', manager=63, child=64)
        self.assertEqual(report['child_commands'], {})
        self.assertEqual(report['malformed_rows'], 1)

    def test_incomplete_and_unrelated_tokens_are_not_event_receipts(self):
        text = ('prefix IPC handle=1 endpoint=0x40 command=7\n'
                'GET_SERVICE name=audout:unrelated\n'
                'IPC handle=1 endpoint=0x40 command=7')
        report = summarize_audio_log(text, manager=63, child=64)
        self.assertEqual(report['service_requests'], 0)
        self.assertEqual(report['child_commands'], {})


if __name__ == '__main__':
    unittest.main()
