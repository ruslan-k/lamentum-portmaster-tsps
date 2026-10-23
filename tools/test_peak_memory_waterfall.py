import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from peak_memory_waterfall import build_waterfall
from test_ledger_bases import BUDGET_RUN, budget_log


RUN = dict(BUDGET_RUN, elf_dev=22, elf_ino=33)
ROOT = Path(__file__).resolve().parents[1]


def timeline(*, mixed_pid=False, reordered=False, complete=True):
    pid = int(RUN["pid"]) + (1 if mixed_pid else 0)
    times = [170, 150] if reordered else [150, 170]
    samples = []
    for seq, stamp in enumerate(times):
        samples.append({
            "run_uuid": RUN["run_uuid"], "boot_id": RUN["boot_id"],
            "pid": pid, "starttime": RUN["starttime"], "elf_sha256": RUN["elf_sha256"],
            "seq": seq, "t_monotonic_ns": stamp,
            "sample_status": "ok", "running": True,
            "process": {"VmRSS_kib": 700000 + seq, "VmHWM_kib": 710000,
                        "VmSwap_kib": 1000, "RssAnon_kib": 500000,
                        "RssFile_kib": 200000, "RssShmem_kib": 0},
            "system": {"MemAvailable_kib": 90000, "CmaFree_kib": 2000,
                       "SwapFree_kib": 10000},
            "vmstat": {"pgmajfault": 2, "pswpin": 0, "pswpout": 0},
            "sample_duration_ns": 5,
        })
    return {
        "schema_version": 1, "run_uuid": RUN["run_uuid"], "elf_sha256": RUN["elf_sha256"],
        "identity": {"boot_id": RUN["boot_id"], "pid": RUN["pid"],
                     "starttime": RUN["starttime"], "elf_dev": RUN["elf_dev"],
                     "elf_ino": RUN["elf_ino"]},
        "interval_ms": 100, "sample_limit": 2, "sample_count": 2,
        "dropped_samples": 0 if complete else 1,
        "complete": complete, "stop_reason": "exited" if complete else "sample-gap",
        "samples": samples,
    }


def cma_snapshot(stamp, cmafree):
    mainui = {"pid": 90, "starttime": 80, "exe_dev": 1, "exe_ino": 2,
              "dma_fds": [], "fd_scan_truncated": False}
    return {
        "schema_version": 1, "sample_status": "complete",
        "identity": {"boot_id": RUN["boot_id"]},
        "timestamps": {"monotonic_ns": stamp},
        "system": {
            "meminfo": {"status": "ok", "values_kib": {
                "CmaTotal": 131072, "CmaFree": cmafree, "MemAvailable": 90000,
                "SwapFree": 10000, "MemFree": 1000}},
            "vmstat": {"status": "ok", "values": {
                "nr_free_cma": cmafree // 4, "cma_alloc_success": 8,
                "cma_alloc_fail": 0, "pswpin": 0, "pswpout": 0,
                "pgmajfault": 2, "pgfault": 20, "compact_stall": 0,
                "compact_fail": 0, "compact_success": 0,
                "pgmigrate_success": 0, "pgmigrate_fail": 0}},
        },
        "allocators": {
            "pagetypeinfo": {"status": "ok", "free_pages_by_migrate_type": [{
                "migrate_type": "CMA", "node": 0, "zone": "DMA",
                "counts_by_order": {str(i): (cmafree // 4 if i == 0 else 0) for i in range(11)}}]},
            "zoneinfo": {"status": "ok"},
        },
        "processes": {"status": "ok", "mainui": [mainui],
                      "target_runtime": {"status": "ok", "exe_dev": 22, "exe_ino": 33}},
        "dma_buf": {"status": "ok", "truncated": False, "entries": []},
    }


def owned_log(*, floor_memory=True, m3b=True):
    rows = budget_log().splitlines()
    insert = next(i for i, line in enumerate(rows) if line.startswith("LC2_LIFE_SUMMARY "))
    extra = []
    if floor_memory:
        extra.append("LC2_MENU_FLOOR_MEMORY run-id=u-1 floor-check-t-ns=149 snapshot-start-ns=150 snapshot-end-ns=155 snapshot-read-ns=5 floor-available-kib=90000 floor-swap-free-kib=10000 cmafree-kib=2000 vmrss-kib=700000 vmswap-kib=1000 meminfo-read=1 status-read=1")
    if m3b:
        extra.extend([
            "LC2_M3B_WINDOW run-id=u-1 event-seq=1 stage=bc-full-refresh t-start-ns=125 decode-start-ns=125 decode-end-ns=130 decode-wall-ns=5 gl-alloc-start-ns=130 gl-alloc-end-ns=135 gl-alloc-wall-ns=5 gl-upload-start-ns=135 gl-upload-end-ns=145 gl-upload-wall-ns=10 t-end-ns=150 owner-id=42 owner-generation=42 generation-basis=nvn-object-id object=0x1234 gl-name=9 storage-generation=1 storage-generation-known=1 content-generation=1 pool-id=99 pool-generation=1 source-compressed-bytes=200 rgba-requested-bytes=400 linear-requested-bytes=100 staging-live-requested-peak-bytes=500 gl-intent-bytes=400 size=10x10 level=0 format=0x41 allocate=1 proof-level=requested-overlap-only source-write-generation=untracked gl-error=unobserved-in-window driver-allocation=unknown gpu-inflight=unknown fileback-shadow=unmeasured mali-residency=unknown completion=unobserved",
            "LC2_M3B_SUMMARY run-id=u-1 configured=64 claimed=1 final-claimed=1 emitted=1 incomplete=0 active=0 dropped=0 format-errors=0 complete=1",
        ])
    extra.append("T2_MEMWATCH_SAMPLE checks=40 available-MiB=90 swap-free-MiB=10 vmrss-MiB=700 vmswap-MiB=1 level=0")
    extra.append("LC2_TEXTURE_OWNER_EVENTS_SUMMARY run-id=u-1 configured=512 claimed=0 final-claimed=0 emitted=0 incomplete=0 active=0 dropped=0 format-errors=0 complete=1")
    rows[insert:insert] = extra
    return "\n".join(rows) + "\n"


class PeakMemoryWaterfallTests(unittest.TestCase):
    def test_outputs_separate_bases_and_keeps_physical_cma_unknown(self):
        result = build_waterfall(owned_log(), timeline(),
                                [cma_snapshot(151, 2000), cma_snapshot(181, 2000)],
                                RUN, memory_floor_mib=64, kernel_warning_deltas={"boot_id": RUN["boot_id"], "capture_status": "ok", "records": []})
        self.assertEqual(result["status"], "complete", result["incomplete_reasons"])
        self.assertEqual(result["ledgers"]["cpu_bc_staging"]["peak_requested_bytes"], 500)
        self.assertEqual(result["ledgers"]["gl_nominal_storage"]["bytes_by_kind"], {})
        self.assertIsNone(result["ledgers"]["driver_dma"]["proven_cma_bytes"])
        self.assertEqual(result["ledgers"]["process_pages"][0]["VmRSS_kib"], 700000)
        self.assertEqual(result["cma"]["snapshots"][0]["CmaFree_kib"], 2000)
        self.assertNotIn("combined_bytes", result)
        self.assertEqual(result["memwatch"]["join_status"], "unjoined_no_timestamp")
        window = result["m3b_windows"][0]
        self.assertEqual(window["completion_state"], "unobserved")
        self.assertEqual(window["decode_interval"], {"start_ns": 125, "end_ns": 130, "wall_ns": 5, "status": "observed"})
        self.assertEqual(window["gl_alloc_interval"], {"start_ns": 130, "end_ns": 135, "wall_ns": 5, "status": "observed"})
        self.assertEqual(window["gl_upload_interval"], {"start_ns": 135, "end_ns": 145, "wall_ns": 10, "status": "observed"})
        self.assertEqual((window["width"], window["height"], window["level"], window["format"]), (10, 10, 0, 0x41))
        self.assertEqual(window["storage_generation"], 1)
        self.assertIsNone(window["owner_generation"])
        self.assertEqual(window["owner_generation_raw"], 42)
        self.assertEqual(window["owner_generation_status"], "source_policy_unbound")
        self.assertEqual(window["present_serial_status"], "not_emitted_by_m3b")
        self.assertEqual(result["kernel_warning_deltas"]["status"], "observed")
        self.assertTrue(result["owned_events"])
        self.assertTrue(all(event["boot_id"] == RUN["boot_id"] for event in result["owned_events"]))
        self.assertEqual(result["memory_samples"][0]["m3b_windows_overlapping_read"], [1])
        self.assertEqual(result["time_joins"]["floor_to_process"],
                         {"status": "interval_overlap", "sample_seqs": [0]})
        self.assertEqual(result["time_joins"]["cma_to_process"][0]["memory_sample_seqs"], [0])
        self.assertFalse(result["interpolation_used"])

    def test_missing_m3b_owner_identity_fails_closed(self):
        text = owned_log().replace("owner-id=42 owner-generation=42 generation-basis=nvn-object-id",
                                   "generation-basis=unknown")
        result = build_waterfall(text, timeline(),
                                 [cma_snapshot(151, 2000), cma_snapshot(181, 2000)], RUN,
                                 memory_floor_mib=64,
                                 kernel_warning_deltas={"boot_id": RUN["boot_id"], "capture_status": "ok", "records": []})
        self.assertEqual(result["status"], "incomplete")
        self.assertIn("m3b_window_owner_identity_missing", result["incomplete_reasons"])

    def test_unrecognized_generation_basis_stays_raw(self):
        text = owned_log().replace("generation-basis=nvn-object-id", "generation-basis=opaque-id")
        result = build_waterfall(text, timeline(),
                                 [cma_snapshot(151, 2000), cma_snapshot(181, 2000)], RUN,
                                 memory_floor_mib=64,
                                 kernel_warning_deltas={"boot_id": RUN["boot_id"], "capture_status": "ok", "records": []})
        window = result["m3b_windows"][0]
        self.assertIsNone(window["owner_generation"])
        self.assertEqual(window["owner_generation_raw"], 42)
        self.assertEqual(window["owner_generation_status"], "unverified_basis")

    def test_nvn_object_id_mismatch_is_incomplete(self):
        text = owned_log().replace("owner-id=42 owner-generation=42 generation-basis=nvn-object-id",
                                   "owner-id=42 owner-generation=43 generation-basis=nvn-object-id")
        result = build_waterfall(text, timeline(),
                                 [cma_snapshot(151, 2000), cma_snapshot(181, 2000)], RUN,
                                 kernel_warning_deltas={"boot_id": RUN["boot_id"], "capture_status": "ok", "records": []})
        self.assertEqual(result["status"], "incomplete")
        self.assertIn("m3b_window_nvn_object_id_mismatch", result["incomplete_reasons"])
        self.assertIsNone(result["m3b_windows"][0]["owner_generation"])

    def test_cli_round_trips_bounded_owned_bundle(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log = root / "owned.log"
            timeline_file = root / "timeline.json"
            cma_files = [root / "cma-1.json", root / "cma-2.json"]
            harness = root / "harness.json"
            warnings = root / "kernel-warnings.json"
            log.write_text(owned_log())
            timeline_file.write_text(json.dumps(timeline()))
            cma_files[0].write_text(json.dumps(cma_snapshot(151, 2000)))
            cma_files[1].write_text(json.dumps(cma_snapshot(181, 2000)))
            harness.write_text(json.dumps({"expected_run": RUN, "m3b_required": True}))
            warnings.write_text(json.dumps({"boot_id": RUN["boot_id"], "capture_status": "ok", "records": []}))
            env = dict(os.environ, PYTHONPATH=str(ROOT / "tools"))
            command = [sys.executable, str(ROOT / "tools/peak_memory_waterfall.py"),
                       "--log", str(log), "--timeline", str(timeline_file),
                       "--cma-snapshot", str(cma_files[0]), "--cma-snapshot", str(cma_files[1]),
                       "--harness", str(harness), "--kernel-warning-deltas", str(warnings),
                       "--memory-floor-mib", "64"]
            result = subprocess.run(command, capture_output=True, text=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "complete")
            self.assertIsNone(payload["m3b_windows"][0]["owner_generation"])
            self.assertEqual(payload["m3b_windows"][0]["owner_generation_status"], "source_policy_unbound")
            self.assertEqual(payload["input_sha256"]["cma_snapshots"], [
                hashlib.sha256(path.read_bytes()).hexdigest() for path in cma_files])
            self.assertEqual(payload["input_sha256"]["log_current_copy"],
                             hashlib.sha256(log.read_bytes()).hexdigest())
            self.assertNotIn("combined_bytes", payload)

    def test_missing_kernel_warning_capture_is_incomplete(self):
        result = build_waterfall(owned_log(), timeline(),
                                 [cma_snapshot(151, 2000), cma_snapshot(181, 2000)], RUN,
                                 memory_floor_mib=64)
        self.assertEqual(result["status"], "incomplete")
        self.assertIn("kernel_warning_deltas_missing", result["incomplete_reasons"])

    def test_rejects_mixed_process_identity(self):
        with self.assertRaisesRegex(ValueError, "mixed process identity"):
            build_waterfall(owned_log(), timeline(mixed_pid=True),
                            [cma_snapshot(151, 2000), cma_snapshot(181, 2000)], RUN,
                            memory_floor_mib=64)

    def test_rejects_reordered_monotonic_samples(self):
        with self.assertRaisesRegex(ValueError, "monotonic"):
            build_waterfall(owned_log(), timeline(reordered=True),
                            [cma_snapshot(151, 2000), cma_snapshot(181, 2000)], RUN,
                            memory_floor_mib=64)

    def test_marks_missing_64_mib_arm_samples_incomplete_without_interpolation(self):
        data = timeline(complete=False)
        data["samples"] = []
        data["sample_count"] = 0
        result = build_waterfall(owned_log(floor_memory=False, m3b=False), data,
                                 [cma_snapshot(151, 2000), cma_snapshot(181, 2000)], RUN,
                                 memory_floor_mib=64)
        self.assertEqual(result["status"], "incomplete")
        self.assertIn("memory_timeline_incomplete", result["incomplete_reasons"])
        self.assertIn("64_mib_floor_sample_missing", result["incomplete_reasons"])
        self.assertFalse(result["interpolation_used"])

    def test_late_280_and_288_pairs_fail_closed(self):
        for texture_id in ("280", "288"):
            with self.subTest(texture_id=texture_id):
                text = owned_log().replace("t-ns=105 phase=initialize id=43 object-generation=43 storage-owner=43",
                                           f"t-ns=170 phase=initialize id={texture_id} object-generation={texture_id} storage-owner={texture_id}")
                text = text.replace("texture-id=43", "texture-id=" + texture_id)
                result = build_waterfall(text, timeline(),
                                         [cma_snapshot(151, 2000), cma_snapshot(181, 2000)],
                                         RUN, memory_floor_mib=64, kernel_warning_deltas={"boot_id": RUN["boot_id"], "capture_status": "ok", "records": []})
                self.assertEqual(result["status"], "incomplete")
                self.assertIn("pair_not_yet_emitted", json.dumps(result["incomplete_reasons"]))

    def test_missing_owner_ring_is_incomplete(self):
        text = "\n".join(line for line in owned_log().splitlines()
                           if not line.startswith("LC2_TEXTURE_OWNER_EVENTS_SUMMARY ")) + "\n"
        result = build_waterfall(text, timeline(),
                                 [cma_snapshot(151, 2000), cma_snapshot(181, 2000)],
                                 RUN, memory_floor_mib=64, kernel_warning_deltas={"boot_id": RUN["boot_id"], "capture_status": "ok", "records": []})
        self.assertEqual(result["status"], "incomplete")
        self.assertIn("ledger_replay", json.dumps(result["incomplete_reasons"]))

    def test_incomplete_m3b_ring_is_not_promoted(self):
        text = owned_log().replace("dropped=0 format-errors=0 complete=1", "dropped=1 format-errors=0 complete=0")
        result = build_waterfall(text, timeline(),
                                 [cma_snapshot(151, 2000), cma_snapshot(181, 2000)],
                                 RUN, memory_floor_mib=64, kernel_warning_deltas={"boot_id": RUN["boot_id"], "capture_status": "ok", "records": []})
        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(result["m3b_status"], "incomplete")
        self.assertFalse(result["promotion_eligible"])

    def test_alias_views_do_not_multiply_gl_storage(self):
        lines = owned_log().splitlines()
        output = []
        for line in lines:
            if line.startswith("LC2_TEXTURE_PAIR ") and " id=43 " in line:
                output.append(line)
                output.append("LC2_TEXTURE_PAIR run-id=u-1 t-ns=106 phase=initialize id=44 object-generation=44 storage-owner=43 guest-bytes=30 charge-bytes=30 storage-status=recorded")
                continue
            if line.startswith("LC2_GL_STORAGE_EVENT "):
                output.append(line.replace("owner=42", "owner=43"))
                continue
            if line.startswith("LC2_GL_STORAGE_DELETE "):
                continue
            if line.startswith("LC2_TEXTURE_BUDGET_EVENT ") and "action=sub texture-id=42" in line:
                output.append("LC2_TEXTURE_BUDGET_EVENT run-id=u-1 t-ns=140 action=add texture-id=44 delta-bytes=30 live-bytes=160 charge-count=3 caller=1 status=recorded")
                output.append(line.replace("live-bytes=30 charge-count=2", "live-bytes=60 charge-count=3"))
                continue
            if line.startswith("LC2_TEXTURE_BUDGET_FLOOR "):
                line = line.replace("live-bytes=30 peak-bytes=130 charge-count=2 event-lines=3",
                                    "live-bytes=60 peak-bytes=160 charge-count=3 event-lines=4")
            if line.startswith("LC2_TEXTURE_OWNER_EVENTS_SUMMARY "):
                line = line.replace("claimed=0 final-claimed=0 emitted=0", "claimed=1 final-claimed=1 emitted=1")
            if line.startswith("LC2_LIFE_SUMMARY "):
                output.append("LC2_LIFE_SUMMARY share-group=unverified storage-calls=1 extends=0 deletes=0 delete-with-views=0 name-reuse=0 retained=400 peak=400 live=1 overflow=0 tex-bytes=400 tex-live=1 rb-bytes=0 rb-live=0 storage-event-lines=1 storage-event-overflow=0 delete-event-lines=0 delete-event-overflow=0")
                continue
            output.append(line)
        output.insert(1, "LC2_TEXTURE_OWNER_EVENT run-id=u-1 event-seq=1 t-ns=105 phase=alias-resolve nvn-id=44 object-generation=44 generation-basis=nvn-object-id storage-owner=43 storage-owner-status=resolved charge-bytes=30 pool-id=99 pool-generation=1 pool-status=recorded cpu-write-generation=0 source-write-generation=untracked status=alias-owner-resolved")
        result = build_waterfall("\n".join(output) + "\n", timeline(),
                                 [cma_snapshot(151, 2000), cma_snapshot(181, 2000)],
                                 RUN, memory_floor_mib=64, kernel_warning_deltas={"boot_id": RUN["boot_id"], "capture_status": "ok", "records": []})
        self.assertEqual(result["status"], "complete", result["incomplete_reasons"])
        self.assertEqual(result["accounting"]["budget"]["live_ids"], ["43", "44"])
        self.assertEqual(result["ledgers"]["gl_nominal_storage"]["live_records"], 1)
        self.assertEqual(result["ledgers"]["gl_nominal_storage"]["bytes_by_kind"], {"1": 400})
        self.assertNotIn("combined_bytes", result)

    def test_unmatched_subresource_is_not_silently_joined(self):
        text = owned_log().replace("bytes=400 total-bytes=400 status=recorded",
                                  "bytes=400 total-bytes=400 subresource=0 subresource-count=2 status=recorded")
        result = build_waterfall(text, timeline(),
                                 [cma_snapshot(151, 2000), cma_snapshot(181, 2000)],
                                 RUN, memory_floor_mib=64, kernel_warning_deltas={"boot_id": RUN["boot_id"], "capture_status": "ok", "records": []})
        self.assertEqual(result["status"], "incomplete")
        self.assertIn("subresource", json.dumps(result["incomplete_reasons"]))


if __name__ == "__main__":
    unittest.main()
