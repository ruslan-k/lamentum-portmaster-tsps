import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from admission_offline_replay import (
    MAX_SOURCE_LOG_BYTES,
    U64_MAX,
    AdmissionRequest,
    evaluate_all_bytes_maybe_cma,
    evaluate_mixed_two_ledger,
    evaluate_proven_cma_only,
    replay_summary,
)


BOOT_ID = "11111111-1111-4111-8111-111111111111"
ELF_SHA = "a" * 64
LAUNCHER_SHA = "b" * 64
HELPER_SHA = "c" * 64
RUNS = (
    {"margin": 64, "run_uuid": "00000000-0000-4000-8000-000000000101", "owner": 61,
     "gl": 0, "scratch": 5_400_000, "available": 540_244, "cma": 70_516,
     "required_cma": 72_508_864, "required_available": 173_172_160},
    {"margin": 48, "run_uuid": "00000000-0000-4000-8000-000000000102", "owner": 77,
     "gl": 0, "scratch": 10_368_000, "available": 524_708, "cma": 47_316,
     "required_cma": 60_699_648, "required_available": 161_362_944},
    {"margin": 32, "run_uuid": "00000000-0000-4000-8000-000000000103", "owner": 0,
     "gl": 512_000, "scratch": 0, "available": 509_188, "cma": 30_520,
     "required_cma": 34_066_432, "required_available": 134_729_728},
    {"margin": 24, "run_uuid": "00000000-0000-4000-8000-000000000104", "owner": 0,
     "gl": 8_294_400, "scratch": 0, "available": 493_096, "cma": 12_664,
     "required_cma": 33_460_224, "required_available": 134_123_520},
)


def make_request(**overrides):
    values = {
        "run_uuid": RUNS[2]["run_uuid"],
        "owner": 0,
        "storage_id": None,
        "storage_generation": None,
        "request_kind": "unknown",
        "requested_bytes": 512_000,
        "gl_bytes": 512_000,
        "scratch_bytes": 0,
        "peak_overlapping_cpu_bytes": None,
        "proven_cma_bytes": None,
        "kernel_source_confidence": "exact_firmware_build",
        "sample_time_ns": 123,
        "timestamp_source": "target_clock_monotonic",
        "phase": "unknown",
        "cma_provenance": "unattributed",
        "available_kib": 509_188,
        "cma_free_kib": 30_520,
        "floor_mib": 96,
        "margin_mib": 32,
        "synthetic": False,
    }
    values.update(overrides)
    return AdmissionRequest(**values)


def make_summary_fixture(root, *, omit_event_for=None, interrupt_log_for=None):
    summary = {
        "schema": "lamentum-m2b-e3-margin-sweep-v1",
        "device": {"boot_id": BOOT_ID, "kernel": "5.15.147", "soc": "sun55iw3"},
        "binary": {"build": 259, "sha256": ELF_SHA},
        "common_run_config": {"floor_mib": 96, "texture_budget_mib": 300, "strict_gl": True,
                               "new_game_entered": False, "margin_was_per_run_only": True,
                               "launcher_margin_default": None},
        "synthetic_input": True,
        "arms": [],
    }
    for index, item in enumerate(RUNS):
        run_dir = Path(root) / f"m2b-e3-build259-margin{item['margin']}-01"
        run_dir.mkdir(parents=True)
        nonce = f"00000000-0000-4000-8000-{index + 201:012d}"
        header = {
            "schema": 1,
            "run_uuid": item["run_uuid"],
            "boot_id": BOOT_ID,
            "pid": 1000 + index,
            "starttime": 2000 + index,
            "elf_dev": 7,
            "elf_ino": 8,
            "elf_sha256": ELF_SHA,
            "launcher_sha256": LAUNCHER_SHA,
            "helper_sha256": HELPER_SHA,
            "launch_nonce": nonce,
        }
        header_line = b"LAMENTUM_RUN_HEADER " + json.dumps(header, sort_keys=True).encode() + b"\n"
        event_time = 50_000 + index
        event_line = (
            f"T2_STORAGE_ADMISSION run-id={item['run_uuid']} t-ns={event_time} decision=deny "
            f"reason=cmafree-margin owner={item['owner']} gl-bytes={item['gl']} scratch-bytes={item['scratch']} "
            f"margin-known=1 margin-mib={item['margin']} sample-known=1 available-kib={item['available']} "
            f"cma-known=1 cmafree-kib={item['cma']} requirements-known=1 "
            f"required-available-bytes={item['required_available']} required-cma-bytes={item['required_cma']} floor-mib=96\n"
        ).encode()
        summary_line = (
            f"T2_STORAGE_ADMISSION_SUMMARY run-id={item['run_uuid']} checks=10 allowed=9 refused=1 "
            f"margin-known=1 margin-mib={item['margin']}\n"
        ).encode()
        stop_line = b"STOP status=T2_STORAGE_ADMISSION pc=fixture detail=0\n"
        log_lines = [header_line]
        if item["run_uuid"] != omit_event_for:
            if item["owner"] == 77:
                log_lines.append(
                    f"LC2_BC_FULL_STAGE id=77 phase=initialize pixel-temporary-bytes=8294400 "
                    f"linearized-input-bytes=2073600 known-cpu-scratch-peak-bytes={item['scratch']} "
                    "staging-mode=separate basis=requested-live-mallocs\n".encode()
                )
            log_lines.extend((event_line, summary_line, stop_line))
        raw_log = b"".join(log_lines)
        if item["run_uuid"] == interrupt_log_for:
            raw_log = raw_log[:-1]
        (run_dir / "latest.log").write_bytes(raw_log)
        (run_dir / "expected-run.json").write_text(json.dumps({
            key: header[key] for key in (
                "run_uuid", "boot_id", "elf_dev", "elf_ino", "elf_sha256",
                "launcher_sha256", "helper_sha256",
            )
        }))
        tail_size = min(len(raw_log), 256)
        tail = raw_log[-tail_size:]
        owned = {
            "status": "ok" if raw_log.endswith(b"\n") else "partial",
            "log_identity_qualified": True,
            "offset": len(raw_log),
            "size": len(raw_log),
            "identity": [7, 8],
            "run_header": header,
            "expected_run": header,
            "header_sha256": hashlib.sha256(header_line).hexdigest(),
            "anchor": {"offset": len(raw_log) - tail_size, "bytes": tail_size,
                       "sha256": hashlib.sha256(tail).hexdigest()},
            "partial_bytes": 0 if raw_log.endswith(b"\n") else 1,
            "unconsumed_bytes": 0,
        }
        (run_dir / "owned-log-final.json").write_text(json.dumps(owned))
        summary["arms"].append({
            "margin_mib": item["margin"],
            "run_uuid": item["run_uuid"],
            "checks": 10,
            "allowed": 9,
            "refused": 1,
            "decision": "deny",
            "reason": "cmafree-margin",
            "owner": item["owner"],
            "request_gl_bytes": item["gl"],
            "request_scratch_bytes": item["scratch"],
            "available_at_refusal_kib": item["available"],
            "cmafree_at_refusal_kib": item["cma"],
            "required_cma_bytes": item["required_cma"],
            "storage_events_before_denial": 0,
            "storage_events_after_denial": 0,
            "timeline": {"complete": True},
        })
    return summary


class AdmissionRequestTests(unittest.TestCase):
    def test_existing_formula_replays_exact_ordered_deny(self):
        request = make_request()
        replay = evaluate_all_bytes_maybe_cma(request)
        self.assertFalse(replay["would_admit"])
        self.assertEqual(replay["reason"], "cmafree-margin")
        self.assertEqual(replay["required_cma_bytes"], 34_066_432)
        self.assertEqual(replay["required_available_bytes"], 134_729_728)
        self.assertFalse(replay["synthetic"])
        self.assertEqual(replay["qualification"], "formula_replay_only")

    def test_missing_cma_or_margin_fails_closed_not_as_zero(self):
        no_cma = evaluate_all_bytes_maybe_cma(make_request(cma_free_kib=None))
        no_margin = evaluate_all_bytes_maybe_cma(make_request(margin_mib=None))
        self.assertFalse(no_cma["would_admit"])
        self.assertEqual(no_cma["qualification"], "unknown")
        self.assertIsNone(no_cma.get("required_cma_bytes"))
        self.assertFalse(no_margin["would_admit"])
        self.assertEqual(no_margin["reason"], "policy-unset")

    def test_unknown_backing_never_becomes_proven_cma(self):
        request = make_request()
        proven = evaluate_proven_cma_only(request, cma_uncertainty_margin_bytes=16 * 1024 * 1024)
        mixed = evaluate_mixed_two_ledger(request, driver_uncertainty_margin_bytes=16 * 1024 * 1024)
        for result in (proven, mixed):
            self.assertFalse(result["would_admit"])
            self.assertEqual(result["qualification"], "unknown")
            self.assertTrue(result["synthetic"])
            self.assertIn("unknown", result["reason"])

    def test_direct_dma_heap_request_without_cma_receipt_stays_unknown(self):
        request = make_request(request_kind="dma_heap", gl_bytes=0, scratch_bytes=4096,
                               requested_bytes=4096, synthetic=True, sample_time_ns=None,
                               timestamp_source=None)
        result = evaluate_proven_cma_only(request, cma_uncertainty_margin_bytes=0)
        self.assertFalse(result["would_admit"])
        self.assertEqual(result["qualification"], "unknown")
        self.assertIn("proven_cma_bytes", result["missing_fields"])

    def test_mixed_model_requires_separate_driver_margin_evidence(self):
        request = make_request(request_kind="gl_rb", requested_bytes=1024, gl_bytes=1024,
                               scratch_bytes=0, peak_overlapping_cpu_bytes=0,
                               proven_cma_bytes=1024, cma_provenance="synthetic",
                               synthetic=True, sample_time_ns=None, timestamp_source=None,
                               available_kib=200_000, cma_free_kib=50_000)
        result = evaluate_mixed_two_ledger(request, driver_uncertainty_margin_bytes=None)
        self.assertFalse(result["would_admit"])
        self.assertEqual(result["qualification"], "unknown")
        self.assertIn("driver_uncertainty_margin_bytes", result["missing_fields"])

    def test_synthetic_cpu_scratch_and_mixed_ledgers_stay_separate(self):
        request = make_request(
            run_uuid="00000000-0000-4000-8000-000000000301",
            request_kind="cpu_malloc",
            requested_bytes=5_400_000,
            gl_bytes=0,
            scratch_bytes=5_400_000,
            peak_overlapping_cpu_bytes=5_400_000,
            proven_cma_bytes=0,
            cma_provenance="synthetic",
            available_kib=700_000,
            cma_free_kib=100_000,
            sample_time_ns=None,
            timestamp_source=None,
            synthetic=True,
        )
        proven = evaluate_proven_cma_only(request, cma_uncertainty_margin_bytes=8 * 1024 * 1024)
        mixed = evaluate_mixed_two_ledger(request, driver_uncertainty_margin_bytes=16 * 1024 * 1024)
        self.assertTrue(proven["would_admit"])
        self.assertTrue(mixed["would_admit"])
        self.assertEqual(mixed["required_available_bytes"], 96 * 1024 * 1024 + 5_400_000)
        self.assertEqual(mixed["required_cma_bytes"], 16 * 1024 * 1024)
        self.assertEqual(mixed["qualification"], "synthetic_only")
        self.assertTrue(mixed["synthetic"])

    def test_framebuffer_depth_multiplicity_is_preserved_but_unqualified(self):
        composite = 4 * 8_294_400  # three color targets plus one depth-equivalent surface
        request = make_request(
            request_kind="unknown",
            requested_bytes=composite,
            gl_bytes=composite,
            scratch_bytes=0,
            proven_cma_bytes=None,
            cma_provenance="unattributed",
            synthetic=True,
            sample_time_ns=None,
            timestamp_source=None,
        )
        result = evaluate_all_bytes_maybe_cma(request)
        self.assertEqual(result["requested_bytes"], composite)
        self.assertEqual(result["required_cma_bytes"], composite + 32 * 1024 * 1024)
        self.assertTrue(result["synthetic"])
        self.assertEqual(result["qualification"], "synthetic_counterfactual")

    def test_parallel_cpu_and_gl_request_uses_distinct_ledgers(self):
        request = make_request(
            request_kind="gl_tex",
            requested_bytes=4 * 1024 * 1024,
            gl_bytes=4 * 1024 * 1024,
            scratch_bytes=0,
            peak_overlapping_cpu_bytes=2 * 1024 * 1024,
            proven_cma_bytes=4 * 1024 * 1024,
            cma_provenance="synthetic",
            available_kib=101_000,
            cma_free_kib=30_720,
            synthetic=True,
            sample_time_ns=None,
            timestamp_source=None,
        )
        result = evaluate_mixed_two_ledger(request, driver_uncertainty_margin_bytes=16 * 1024 * 1024)
        self.assertTrue(result["would_admit"])
        self.assertEqual(result["required_available_bytes"], 96 * 1024 * 1024 + 2 * 1024 * 1024)
        self.assertEqual(result["required_cma_bytes"], 20 * 1024 * 1024)

    def test_overflow_negative_bytes_and_fabricated_timestamps_are_rejected(self):
        with self.assertRaises(ValueError):
            make_request(gl_bytes=-1, requested_bytes=-1)
        with self.assertRaises((ValueError, OverflowError)):
            make_request(requested_bytes=U64_MAX, gl_bytes=U64_MAX, scratch_bytes=1)
        with self.assertRaises(ValueError):
            make_request(sample_time_ns=123, timestamp_source="invented")
        with self.assertRaises(ValueError):
            make_request(synthetic=True, sample_time_ns=123, timestamp_source="target_clock_monotonic")
        overflow = make_request(requested_bytes=U64_MAX, gl_bytes=U64_MAX, scratch_bytes=0, margin_mib=1)
        result = evaluate_all_bytes_maybe_cma(overflow)
        self.assertFalse(result["would_admit"])
        self.assertEqual(result["reason"], "size-overflow")

    def test_raw_four_arm_replay_matches_exact_observed_denials(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            summary = make_summary_fixture(root)
            result = replay_summary(summary, root, kernel_source_confidence="exact_firmware_build",
                                    source_is_synthetic=True)
        self.assertEqual(result["replay_status"], "complete")
        self.assertTrue(result["synthetic_input"])
        self.assertEqual(len(result["requests"]), 4)
        self.assertEqual([row["observed"]["owner"] for row in result["requests"]], [61, 77, 0, 0])
        self.assertEqual([row["observed"]["gl_bytes"] for row in result["requests"]],
                         [0, 0, 512_000, 8_294_400])
        self.assertEqual([row["observed"]["scratch_bytes"] for row in result["requests"]],
                         [5_400_000, 10_368_000, 0, 0])
        known_cpu = result["requests"][1]["observed"]
        self.assertEqual(known_cpu["request_kind"], "cpu_malloc")
        self.assertEqual(known_cpu["peak_overlapping_cpu_bytes"], 10_368_000)
        self.assertEqual(known_cpu["phase"], "initialize")
        self.assertIsNone(known_cpu["source"]["cpu_peak_context"]["timestamp_ns"])
        for row in result["requests"]:
            self.assertTrue(row["observed"]["synthetic"])
            self.assertFalse(row["models"]["all_bytes_maybe_CMA"]["would_admit"])
            self.assertTrue(row["models"]["all_bytes_maybe_CMA"]["synthetic"])
            self.assertEqual(row["models"]["all_bytes_maybe_CMA"]["reason"], "cmafree-margin")
            self.assertEqual(row["models"]["proven_CMA_only"]["qualification"], "unknown")
            self.assertEqual(row["models"]["mixed_two_ledger"]["qualification"], "unknown")

    def test_oversized_raw_log_is_rejected_before_reading(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            summary = make_summary_fixture(root)
            oversized = root / "m2b-e3-build259-margin64-01/latest.log"
            with oversized.open("ab") as stream:
                stream.truncate(MAX_SOURCE_LOG_BYTES + 1)
            with patch.object(Path, "read_bytes", side_effect=AssertionError("unbounded log read")):
                with self.assertRaisesRegex(ValueError, "exceeds bounded read limit"):
                    replay_summary(summary, root, source_is_synthetic=True)

    def test_rejects_non_build259_or_persisted_margin_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            summary = make_summary_fixture(root)
            summary["binary"]["build"] = 260
            with self.assertRaisesRegex(ValueError, "build259"):
                replay_summary(summary, root, source_is_synthetic=True)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            summary = make_summary_fixture(root)
            summary["common_run_config"]["margin_was_per_run_only"] = False
            summary["common_run_config"]["launcher_margin_default"] = 24
            with self.assertRaisesRegex(ValueError, "per-run margin"):
                replay_summary(summary, root, source_is_synthetic=True)

    def test_log_mutation_between_hash_and_parse_is_refused(self):
        from admission_offline_replay import collect_log

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            summary = make_summary_fixture(root)

            def mutated_capture(*args, **kwargs):
                capture = collect_log(*args, **kwargs)
                capture["chunk_text"] = capture["chunk_text"].replace(
                    "available-kib=540244", "available-kib=540245", 1)
                return capture

            with patch("admission_offline_replay.collect_log", side_effect=mutated_capture):
                with self.assertRaisesRegex(ValueError, "raw log bytes differ from parsed capture"):
                    replay_summary(summary, root, source_is_synthetic=True)

    def test_replay_rejects_nonobject_identity_sections(self):
        for section in ("device", "common_run_config"):
            with self.subTest(section=section), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                summary = make_summary_fixture(root)
                summary[section] = None
                with self.assertRaisesRegex(ValueError, "summary"):
                    replay_summary(summary, root, source_is_synthetic=True)

    def test_missing_event_and_interrupted_log_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            summary = make_summary_fixture(root, omit_event_for=RUNS[0]["run_uuid"])
            with self.assertRaisesRegex(ValueError, "admission event"):
                replay_summary(summary, root, source_is_synthetic=True)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            summary = make_summary_fixture(root, interrupt_log_for=RUNS[0]["run_uuid"])
            with self.assertRaisesRegex(ValueError, "partial|truncated|incomplete"):
                replay_summary(summary, root, source_is_synthetic=True)


if __name__ == "__main__":
    unittest.main()
