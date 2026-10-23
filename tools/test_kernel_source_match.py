import json
import subprocess
import sys
import unittest
from pathlib import Path

from kernel_source_match import classify_kernel_match


BANNER = (
    "Linux version 5.15.147 (TRIMUIDEV@NUC) (aarch64-none-linux-gnu-gcc "
    "(GNU Toolchain for the A-profile Architecture 10.3-2021.07 (arm-10.29)) "
    "10.3.1 20210621, GNU ld (GNU Toolchain for the A-profile Architecture "
    "10.3-2021.07 (arm-10.29)) 2.36.1.20210621) #42 SMP PREEMPT Thu Dec 18 "
    "22:31:41 CST 2025"
)
FIRMWARE = {
    "firmware_version": "1.0.1",
    "kernel_release": "5.15.147",
    "kernel_banner": BANNER,
    "source_tree_available": False,
    "asset": {"name": "trimui_tg5050.awimg.7z", "sha256": "e825878608d0c979ba9cfcde71c104f0b334c9979774e783f5174f9356360f8a", "sha256_verified": True},
    "vmlinux": {
        "sha256": "806182f8823b0db340f3f9beccf303e39571deb20b99386ee6a76442b8761b19",
        "build_id": "175a7f4d4731ebfbbdeb7695329115202f8b813a",
        "architecture": "aarch64",
        "source_path": "/home2/trimuidev/tg5050/tina_1.0.0/kernel/linux-5.15/drivers/dma-buf/heaps/system_heap.c",
        "symbols": {
            "__alloc_pages": {"address": "0xffffffc000100000", "st_size": "0xc18", "next_symbol_delta": "0xc20"},
            "dma_heap_ioctl": {"address": "0xffffffc000500000", "st_size": "0x320"},
            "system_heap_allocate": {"address": "0xffffffc000510000", "st_size": "0x388", "next_symbol_delta": "0x38c"},
            "system_heap_attach": {"address": "0xffffffc00051038c"},
        },
        "warning_return": {"symbol": "system_heap_allocate", "offset": "0x120", "instruction": "cbz x0, retry_candidate"},
        "orders": [8, 4, 0],
        "null_return_retries": True,
    },
}
DEVICE = {
    "firmware_version": "1.0.1",
    "kernel_release": "5.15.147",
    "kernel_banner": BANNER,
    "kallsyms": {
        "__alloc_pages": "0xffffffc000180000",
        "dma_heap_ioctl": "0xffffffc000580000",
        "system_heap_allocate": "0xffffffc000590000",
        "system_heap_attach": "0xffffffc00059038c",
    },
    "warning_stack_frames": {
        "__alloc_pages": {"offset": "0xbe0", "extent": "0xc20"},
        "system_heap_allocate": {"offset": "0x120", "extent": "0x38c"},
        "dma_heap_ioctl": {"offset": "0x14c", "extent": "0x320"},
    },
}


class KernelSourceMatchTests(unittest.TestCase):
    def test_consistent_kaslr_delta_and_frame_extents_confirm_firmware_build(self):
        result = classify_kernel_match(DEVICE, FIRMWARE)
        self.assertEqual(result["match_class"], "exact")
        self.assertEqual(result["relocation_delta"], "0x80000")
        self.assertEqual(result["symbols_matched"], 4)
        self.assertTrue(result["banner_match"])
        self.assertTrue(result["firmware_version_match"])
        self.assertTrue(result["warning_return_match"])
        self.assertEqual(result["warning_semantics"]["orders"], [8, 4, 0])
        self.assertEqual(result["warning_semantics"]["request_completion"], "unknown")
        self.assertFalse(result["source_tree_available"])
        self.assertIsNone(result["whole_kernel_hash_match"])
        serialized = json.dumps(result)
        self.assertNotIn("ffffffc000180000", serialized)
        self.assertNotIn("ffffffc000590000", serialized)

    def test_proc_kallsyms_hex_without_prefix_matches_firmware_elf(self):
        device = json.loads(json.dumps(DEVICE))
        device["kallsyms"] = {name: value.removeprefix("0x")
                              for name, value in device["kallsyms"].items()}
        result = classify_kernel_match(device, FIRMWARE)
        self.assertEqual(result["match_class"], "exact")
        self.assertEqual(result["relocation_delta"], "0x80000")

    def test_zeroed_kallsyms_addresses_stay_unmatched(self):
        device = json.loads(json.dumps(DEVICE))
        device["kallsyms"] = {name: "0000000000000000" for name in device["kallsyms"]}
        result = classify_kernel_match(device, FIRMWARE)
        self.assertEqual(result["symbols_matched"], 0)
        self.assertIsNone(result["relocation_delta"])

    def test_unverified_firmware_asset_cannot_be_classified_exact(self):
        firmware = json.loads(json.dumps(FIRMWARE))
        firmware["asset"]["sha256_verified"] = False
        result = classify_kernel_match(DEVICE, firmware)
        self.assertEqual(result["match_class"], "analogue")
        self.assertFalse(result["asset_sha256_verified"])

    def test_inconsistent_symbol_relocation_downgrades_to_analogue(self):
        device = json.loads(json.dumps(DEVICE))
        device["kallsyms"]["system_heap_allocate"] = "0xffffffc000590004"
        result = classify_kernel_match(device, FIRMWARE)
        self.assertEqual(result["match_class"], "analogue")
        self.assertIsNone(result["relocation_delta"])
        self.assertTrue(result["warning_return_match"])
        self.assertEqual(result["warning_semantics"]["request_completion"], "unknown")

    def test_cli_reads_receipt_and_emits_only_sanitized_match(self):
        script = Path(__file__).with_name("kernel_source_match.py")
        payload = json.dumps({"device": DEVICE, "firmware": FIRMWARE})
        run = subprocess.run([sys.executable, str(script), "-"], input=payload,
                             capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 0, run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual(result["match_class"], "exact")
        self.assertNotIn("ffffffc000180000", run.stdout)

    def test_missing_identity_or_symbols_stays_unknown(self):
        device = {"kernel_release": "5.15.147", "kallsyms": {}}
        result = classify_kernel_match(device, FIRMWARE)
        self.assertEqual(result["match_class"], "unknown")
        self.assertIsNone(result["relocation_delta"])
        self.assertEqual(result["symbols_matched"], 0)
        self.assertEqual(result["warning_semantics"]["request_completion"], "unknown")


if __name__ == "__main__":
    unittest.main()
