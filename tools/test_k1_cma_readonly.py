import errno
import gzip
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cma_readonly_snapshot import (
    MAX_PROC_TEXT_BYTES,
    collect_snapshot,
    parse_buddyinfo,
    parse_pagetypeinfo,
    parse_zoneinfo,
)
from cma_readonly_compare import compare_snapshots


BUDDYINFO = "Node 0, zone DMA    807    951    953    679    386    436    284    176     65     23      4\n"
PAGETYPEINFO = """Page block order: 10
Pages per block: 1024
Free pages count per migrate type at order       0      1      2      3      4      5      6      7      8      9     10
Node    0, zone      DMA, type    Unmovable    217    855    939    669    380    246    118     67     22      9      0
Node    0, zone      DMA, type      Movable      1      0      0      0      0    178    151    103     43     14      1
Node    0, zone      DMA, type          CMA    571     71      9      3      1      0      0      0      0      0      3
Number of blocks type     Unmovable      Movable  Reclaimable   HighAtomic          CMA      Isolate
Node 0, zone      DMA          101          110           12            1           32            0
"""
ZONEINFO = """Node 0, zone      DMA
  pages free     105291
        min      991
        low      1238
        high     1485
        cma      32768
      nr_free_cma  3864
Node 0, zone    DMA32
  pages free     0
        min      0
        low      0
        high     0
        cma      0
"""


def proc_stat(pid, comm, state="S", starttime=12345):
    fields = [state] + ["0"] * 18 + [str(starttime)] + ["0"] * 3
    return f"{pid} ({comm}) " + " ".join(fields) + "\n"


def make_snapshot(boot="boot-a", cma_free=15000, nr_free_cma=3750, cma_order4=1, t=100):
    counts = {str(i): 0 for i in range(11)}
    counts["4"] = cma_order4
    return {
        "schema_version": 1,
        "sample_status": "complete",
        "identity": {"boot_id": boot, "kernel_release": "5.15.147", "firmware_version": "1.0.1"},
        "timestamps": {"wall_time_ns": t, "monotonic_ns": t, "duration_ns": 10},
        "system": {
            "meminfo": {"status": "ok", "values_kib": {
                "MemFree": 420000, "CmaTotal": 131072, "CmaFree": cma_free,
                "MemAvailable": 680000, "SwapFree": 2000000}},
            "vmstat": {"status": "ok", "values": {
                "nr_free_cma": nr_free_cma, "cma_alloc_success": 36, "cma_alloc_fail": 0}},
        },
        "allocators": {
            "pagetypeinfo": {"status": "ok", "pages_per_block": 1024,
                "free_pages_by_migrate_type": [{"node": 0, "zone": "DMA", "migrate_type": "CMA",
                    "counts_by_order": counts}]},
        },
        "processes": {
            "status": "ok",
            "target_runtime": {"status": "ok", "exe_dev": 7, "exe_ino": 8},
            "mainui": [{"pid": 10, "starttime": 20, "exe_dev": 1, "exe_ino": 2,
                "fd_scan_truncated": False,
                "dma_fds": [{"fd": 3, "target": "/dev/dma_heap/system", "dev": 4, "ino": 5}]}],
        },
    }


class AllocatorProcParserTests(unittest.TestCase):
    def test_buddyinfo_keeps_order_columns_and_zone_identity(self):
        parsed = parse_buddyinfo(BUDDYINFO)
        self.assertEqual(parsed["status"], "ok")
        self.assertEqual(parsed["rows"], [{
            "node": 0, "zone": "DMA",
            "free_blocks_by_order": [807, 951, 953, 679, 386, 436, 284, 176, 65, 23, 4],
        }])

    def test_pagetypeinfo_separates_free_pages_from_block_counts(self):
        parsed = parse_pagetypeinfo(PAGETYPEINFO)
        self.assertEqual(parsed["status"], "ok")
        self.assertEqual(parsed["page_block_order"], 10)
        self.assertEqual(parsed["pages_per_block"], 1024)
        cma = parsed["free_pages_by_migrate_type"][2]
        self.assertEqual((cma["node"], cma["zone"], cma["migrate_type"]), (0, "DMA", "CMA"))
        self.assertEqual(cma["counts_by_order"]["4"], 1)
        self.assertEqual(cma["counts_by_order"]["10"], 3)
        blocks = parsed["blocks_by_migrate_type"][0]
        self.assertEqual(blocks["counts_by_type"]["CMA"], 32)
        self.assertNotEqual(blocks["counts_by_type"]["CMA"], cma["counts_by_order"]["4"])

    def test_zoneinfo_preserves_cma_and_watermark_fields(self):
        parsed = parse_zoneinfo(ZONEINFO)
        self.assertEqual(parsed["status"], "ok")
        dma = parsed["zones"][0]
        self.assertEqual((dma["node"], dma["zone"]), (0, "DMA"))
        self.assertEqual(dma["values"]["nr_free_cma"], 3864)
        self.assertEqual(dma["values"]["cma"], 32768)
        self.assertEqual(dma["values"]["low"], 1238)

    def test_missing_cma_free_row_is_unknown_not_zero(self):
        text = """Page block order: 10
Pages per block: 1024
Free pages count per migrate type at order 0 1
Node 0, zone DMA, type Unmovable 3 1
Number of blocks type Unmovable Movable Reclaimable HighAtomic CMA Isolate
Node 0, zone DMA 1 0 0 0 0 0
"""
        parsed = parse_pagetypeinfo(text)
        self.assertEqual(parsed["status"], "partial")
        self.assertIsNone(parsed["cma_free_pages_from_histogram"])

    def test_truncated_or_malformed_proc_data_is_not_reported_as_zero(self):
        parsed = parse_pagetypeinfo("Page block order: 10\nPages per block: 1024\n", truncated=True)
        self.assertEqual(parsed["status"], "partial")
        self.assertEqual(parsed["free_pages_by_migrate_type"], [])
        self.assertIsNone(parsed["cma_free_pages_from_histogram"])
        malformed = parse_buddyinfo("Node 0, zone DMA 7 nope 2\n")
        self.assertEqual(malformed["status"], "partial")
        self.assertEqual(malformed["rows"], [])


class ReadOnlySnapshotTests(unittest.TestCase):
    def _fixture_root(self, parent):
        root = Path(parent)
        proc = root / "proc"
        (proc / "sys/kernel/random").mkdir(parents=True)
        (proc / "sys/kernel/random/boot_id").write_text("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa\n")
        (proc / "sys/kernel/osrelease").write_text("5.15.147\n")
        (proc / "version").write_text("Linux version 5.15.147 (TRIMUIDEV@NUC)\n")
        (proc / "cmdline").write_text("root=/dev/mmcblk0p2 cma=128M serial=DO_NOT_EMIT\n")
        (proc / "meminfo").write_text(
            "MemTotal: 1000000 kB\nMemAvailable: 680000 kB\nCmaTotal: 131072 kB\n"
            "CmaFree: 15456 kB\nSwapFree: 2000000 kB\nCached: 1000 kB\nMlocked: 0 kB\n"
            "Unevictable: 0 kB\nSlab: 10 kB\nSReclaimable: 5 kB\n")
        (proc / "vmstat").write_text(
            "nr_free_cma 3864\ncma_alloc_success 36\ncma_alloc_fail 0\n"
            "compact_stall 228\npgmigrate_success 578142\npswpin 100\npswpout 200\npgmajfault 8\n")
        (proc / "buddyinfo").write_text(BUDDYINFO)
        (proc / "pagetypeinfo").write_text(PAGETYPEINFO)
        (proc / "zoneinfo").write_text(ZONEINFO)
        (proc / "config.gz").write_bytes(gzip.compress(
            b"CONFIG_CMA=y\nCONFIG_DMA_CMA=y\nCONFIG_DEBUG_FS=y\n"
            b"# CONFIG_CMA_DEBUGFS is not set\n# CONFIG_PAGE_OWNER is not set\nCONFIG_COMPACTION=y\n"))
        compatible = root / "sys/firmware/devicetree/base/compatible"
        compatible.parent.mkdir(parents=True)
        compatible.write_bytes(b"allwinner,sun55iw3p1\0trimui,tg5050\0")
        (root / "lib/modules/5.15.147").mkdir(parents=True)
        (root / "etc").mkdir()
        (root / "etc/version").write_text("1.0.1\n")
        (root / "dev/dma_heap").mkdir(parents=True)
        heap = root / "dev/dma_heap/system"
        heap.write_text("")
        mainui = proc / "100"
        (mainui / "fd").mkdir(parents=True)
        (mainui / "comm").write_text("MainUI\n")
        (mainui / "stat").write_text(proc_stat(100, "MainUI", starttime=200))
        (mainui / "exe").symlink_to(heap)
        (mainui / "fd/10").symlink_to(heap)
        runtime = root / "mnt/SDCARD/Roms/PORTS/lamentum-switch/lamentum-nextos"
        runtime.parent.mkdir(parents=True)
        runtime.write_text("self-authored runtime fixture")
        game = proc / "101"
        game.mkdir()
        (game / "comm").write_text("lamentum-nextos\n")
        (game / "stat").write_text(proc_stat(101, "lamentum-nextos", starttime=201))
        (game / "exe").symlink_to(runtime)
        shell = root / "bin/bash"
        shell.parent.mkdir(parents=True)
        shell.write_text("fixture shell")
        principal = proc / "102"
        (principal / "fd").mkdir(parents=True)
        (principal / "comm").write_text("principal.sh\n")
        (principal / "stat").write_text(proc_stat(102, "principal.sh", starttime=202))
        (principal / "exe").symlink_to(shell)
        (principal / "cmdline").write_bytes(b"/bin/bash /mnt/SDCARD/spruce/scripts/principal.sh\\0")
        (root / "tmp").mkdir()
        return root

    def test_snapshot_is_bounded_redacts_cmdline_and_keeps_unavailable_distinct(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._fixture_root(directory)
            before = sorted(str(p.relative_to(root)) for p in root.rglob("*"))
            snap = collect_snapshot(root=str(root))
            after = sorted(str(p.relative_to(root)) for p in root.rglob("*"))
            self.assertEqual(before, after)
            self.assertEqual(snap["schema_version"], 1)
            self.assertEqual(snap["sample_status"], "complete")
            self.assertEqual(snap["identity"]["boot_id"], "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
            self.assertEqual(snap["identity"]["firmware_version"], "1.0.1")
            self.assertEqual(snap["system"]["meminfo"]["values_kib"]["CmaFree"], 15456)
            self.assertEqual(snap["system"]["vmstat"]["values"]["nr_free_cma"], 3864)
            self.assertEqual(snap["config"]["values"]["CONFIG_CMA_DEBUGFS"], "not_set")
            self.assertEqual(snap["config"]["values"]["CONFIG_PAGE_OWNER"], "not_set")
            self.assertEqual(snap["device_tree"]["compatible"], ["allwinner,sun55iw3p1", "trimui,tg5050"])
            self.assertEqual(snap["processes"]["mainui"][0]["pid"], 100)
            self.assertEqual(snap["processes"]["mainui"][0]["dma_fds"][0]["target"], "/dev/dma_heap/system")
            self.assertEqual(snap["processes"]["game_processes"][0]["comm"], "lamentum-nextos")
            self.assertNotIn("DO_NOT_EMIT", json.dumps(snap))
            self.assertEqual(snap["dma_buf"]["status"], "unavailable")

    def test_s_preflight_is_non_atomic_and_passes_stable_mainui_principal_without_game(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._fixture_root(directory)
            shutil.rmtree(root / "proc/101")
            snap = collect_snapshot(root=str(root))
            processes = snap["processes"]
            self.assertEqual(processes["snapshot_consistency"], "sequential_non_atomic")
            self.assertEqual(processes["principal"][0]["pid"], 102)
            self.assertEqual(processes["principal"][0]["starttime"], 202)
            self.assertFalse(processes["pending_principal_command"])
            self.assertEqual(processes["process_identity_status"], "ready")
            self.assertTrue(processes["process_identity_checks"]["mainui_unique_identity"])
            self.assertTrue(processes["process_identity_checks"]["principal_unique_identity"])

    def test_s_preflight_holds_for_game_or_pending_principal_command(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._fixture_root(directory)
            snap = collect_snapshot(root=str(root))
            self.assertEqual(snap["processes"]["process_identity_status"], "hold")
            self.assertFalse(snap["processes"]["process_identity_checks"]["no_game_process"])
            (root / "tmp/cmd_to_run.sh").write_text("pending\n")
            shutil.rmtree(root / "proc/101")
            pending = collect_snapshot(root=str(root))
            self.assertTrue(pending["processes"]["pending_principal_command"])
            self.assertEqual(pending["processes"]["process_identity_status"], "hold")
            self.assertFalse(pending["processes"]["process_identity_checks"]["no_pending_principal_command"])

    def test_s_preflight_holds_when_principal_identity_is_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._fixture_root(directory)
            shutil.rmtree(root / "proc/101")
            shutil.rmtree(root / "proc/102")
            snap = collect_snapshot(root=str(root))
            self.assertEqual(snap["processes"]["process_identity_status"], "hold")
            self.assertFalse(snap["processes"]["process_identity_checks"]["principal_unique_identity"])

    def test_enoent_is_transient_only_when_process_directory_disappears(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._fixture_root(directory)
            stale = root / "proc/104"
            (stale / "fd").mkdir(parents=True)
            (stale / "comm").write_text("shortlived\n")
            (stale / "stat").write_text(proc_stat(104, "shortlived", starttime=204))
            (stale / "exe").symlink_to(root / "bin/bash")
            original = Path.read_text
            def exit_during_comm(path, *args, **kwargs):
                if path == stale / "comm":
                    shutil.rmtree(stale)
                    raise FileNotFoundError(errno.ENOENT, "exited", str(path))
                return original(path, *args, **kwargs)
            with patch.object(Path, "read_text", exit_during_comm):
                snap = collect_snapshot(root=str(root))
            processes = snap["processes"]
            self.assertEqual(processes["transient_exit_count"], 1)
            self.assertEqual(processes["persistent_read_errors"], [])
            self.assertEqual(processes["status"], "ok")
            self.assertEqual(snap["sample_status"], "complete")

    def test_enoent_during_exe_read_is_transient_when_process_directory_disappears(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._fixture_root(directory)
            shutil.rmtree(root / "proc/101")
            stale = root / "proc/104"
            (stale / "fd").mkdir(parents=True)
            (stale / "comm").write_text("shortlived\\n")
            (stale / "stat").write_text(proc_stat(104, "shortlived", starttime=204))
            (stale / "exe").symlink_to(root / "bin/bash")
            original_stat = os.stat

            def exit_during_exe(path, *args, **kwargs):
                if Path(path) == stale / "exe":
                    shutil.rmtree(stale)
                    raise FileNotFoundError(errno.ENOENT, "exited", str(path))
                return original_stat(path, *args, **kwargs)

            with patch("cma_readonly_snapshot.os.stat", side_effect=exit_during_exe):
                snap = collect_snapshot(root=str(root))
            processes = snap["processes"]
            self.assertEqual(processes["transient_exit_count"], 1)
            self.assertEqual(processes["unreadable_exe_count"], 0)
            self.assertEqual(processes["persistent_read_error_count"], 0)
            self.assertEqual(processes["status"], "ok")
            self.assertEqual(snap["sample_status"], "complete")

    def test_live_pid_eacces_and_persistent_enoent_are_hold(self):
        for error in (PermissionError(errno.EACCES, "denied"), FileNotFoundError(errno.ENOENT, "still present")):
            with self.subTest(error=type(error).__name__), tempfile.TemporaryDirectory() as directory:
                root = self._fixture_root(directory)
                process = root / "proc/104"
                (process / "fd").mkdir(parents=True)
                (process / "stat").write_text(proc_stat(104, "blocked", starttime=204))
                (process / "exe").symlink_to(root / "bin/bash")
                (process / "comm").write_text("blocked\n")
                original = Path.read_text
                def fail_live_read(path, *args, **kwargs):
                    if path == process / "comm":
                        raise type(error)(error.errno, str(error), str(path))
                    return original(path, *args, **kwargs)
                with patch.object(Path, "read_text", fail_live_read):
                    snap = collect_snapshot(root=str(root))
                self.assertEqual(snap["processes"]["status"], "partial")
                self.assertGreaterEqual(snap["processes"]["persistent_read_error_count"], 1)
                self.assertEqual(snap["sample_status"], "partial")

    def test_pid_reuse_between_census_brackets_is_hold(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._fixture_root(directory)
            mainui_stat = root / "proc/100/stat"
            original = Path.read_text
            calls = 0
            def reuse_pid(path, *args, **kwargs):
                nonlocal calls
                if path == mainui_stat:
                    calls += 1
                    return proc_stat(100, "MainUI", starttime=200 if calls == 1 else 201)
                return original(path, *args, **kwargs)
            with patch.object(Path, "read_text", reuse_pid):
                snap = collect_snapshot(root=str(root))
            self.assertGreaterEqual(calls, 2)
            self.assertEqual(snap["processes"]["pid_reuse_count"], 1)
            self.assertEqual(snap["processes"]["status"], "partial")
            self.assertEqual(snap["sample_status"], "partial")

    def test_dma_buf_inventory_keeps_inode_size_and_exporter(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._fixture_root(directory)
            buffer = root / "dmabuf" / "buffer"
            buffer.parent.mkdir()
            buffer.write_text("fixture")
            inode = os.stat(buffer).st_ino
            entry = root / "sys/kernel/dmabuf/buffers" / str(inode)
            entry.mkdir(parents=True)
            (entry / "size").write_text("16384\n")
            (entry / "exporter_name").write_text("system\n")
            (root / "proc/100/fd/11").symlink_to(buffer)
            snap = collect_snapshot(root=str(root))
            self.assertEqual(snap["dma_buf"]["status"], "ok")
            self.assertEqual(snap["dma_buf"]["entries"], [{
                "inode": inode, "size_bytes": 16384, "exporter": "system",
            }])
            fds = snap["processes"]["mainui"][0]["dma_fds"]
            self.assertTrue(any(row["ino"] == inode for row in fds))

    def test_kernel_threads_without_executable_do_not_make_census_partial(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._fixture_root(directory)
            task = root / "proc/103"
            task.mkdir()
            (task / "comm").write_text("kworker/0:1\n")
            (task / "stat").write_text(proc_stat(103, "kworker/0:1", starttime=203))
            (task / "cmdline").write_bytes(b"")
            (task / "status").write_text("Name:\tkworker/0:1\nPPid:\t2\n")
            snap = collect_snapshot(root=str(root))
            self.assertEqual(snap["processes"]["status"], "ok")
            self.assertEqual(snap["processes"]["kernel_threads_skipped"], 1)
            self.assertEqual(snap["sample_status"], "complete")

    def test_missing_mainui_makes_snapshot_partial(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._fixture_root(directory)
            shutil.rmtree(root / "proc/100")
            snap = collect_snapshot(root=str(root))
            self.assertEqual(snap["sample_status"], "partial")

    def test_missing_target_runtime_identity_makes_process_snapshot_partial(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._fixture_root(directory)
            (root / "mnt/SDCARD/Roms/PORTS/lamentum-switch/lamentum-nextos").unlink()
            snap = collect_snapshot(root=str(root))
            self.assertEqual(snap["processes"]["target_runtime"]["status"], "unavailable")
            self.assertEqual(snap["processes"]["status"], "partial")
            self.assertEqual(snap["sample_status"], "partial")

    def test_missing_and_oversized_core_files_make_snapshot_partial(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._fixture_root(directory)
            (root / "proc/pagetypeinfo").write_text("x" * (MAX_PROC_TEXT_BYTES + 1))
            snap = collect_snapshot(root=str(root))
            self.assertEqual(snap["sample_status"], "partial")
            self.assertTrue(snap["allocators"]["pagetypeinfo"]["capture"]["truncated"])
            self.assertEqual(snap["allocators"]["pagetypeinfo"]["status"], "partial")
            self.assertIsNone(snap["allocators"]["pagetypeinfo"].get("cma_free_pages_from_histogram"))


class SnapshotComparisonTests(unittest.TestCase):
    def test_same_boot_comparison_reports_free_cma_and_histogram_deltas_without_claims(self):
        first = make_snapshot(cma_free=15456, nr_free_cma=3864, cma_order4=1, t=100)
        second = make_snapshot(cma_free=15000, nr_free_cma=3750, cma_order4=0, t=20400000100)
        report = compare_snapshots([first, second])
        self.assertEqual(report["comparison_status"], "complete")
        pair = report["pairs"][0]
        self.assertEqual(pair["deltas"]["CmaFree_kib"], -456)
        self.assertEqual(pair["deltas"]["nr_free_cma_pages"], -114)
        self.assertEqual(pair["cma_free_blocks_by_order_delta"]["0: DMA"]["4"], -1)
        self.assertTrue(pair["mainui_identity"]["same"])
        self.assertIn("not proof", pair["interpretation"])

    def test_different_boots_and_missing_values_never_produce_false_deltas(self):
        first = make_snapshot(boot="boot-a", cma_free=15456, t=100)
        second = make_snapshot(boot="boot-b", cma_free=10000, t=200)
        report = compare_snapshots([first, second])
        self.assertEqual(report["comparison_status"], "identity_mismatch")
        self.assertIsNone(report["pairs"][0]["deltas"]["CmaFree_kib"])
        first = make_snapshot(boot="boot-a", cma_free=15456, t=100)
        second = make_snapshot(boot="boot-a", cma_free=10000, t=200)
        second["system"]["meminfo"]["values_kib"]["CmaFree"] = None
        partial = compare_snapshots([first, second])
        self.assertEqual(partial["comparison_status"], "partial")
        self.assertIsNone(partial["pairs"][0]["deltas"]["CmaFree_kib"])

    def test_missing_mainui_fd_identity_makes_pair_partial(self):
        first = make_snapshot(cma_free=15456, t=100)
        second = make_snapshot(cma_free=15456, t=200)
        second["processes"]["mainui"][0]["dma_fds"] = None
        report = compare_snapshots([first, second])
        self.assertEqual(report["comparison_status"], "partial")
        self.assertTrue(report["pairs"][0]["mainui_identity"]["same"])
        self.assertIsNone(report["pairs"][0]["mainui_identity"]["dma_fds_same"])

    def test_missing_required_meminfo_value_makes_pair_partial(self):
        first = make_snapshot(t=100)
        second = make_snapshot(t=200)
        second["system"]["meminfo"]["values_kib"]["MemAvailable"] = None
        report = compare_snapshots([first, second])
        self.assertEqual(report["comparison_status"], "partial")
        self.assertIsNone(report["pairs"][0]["deltas"]["MemAvailable_kib"])

    def test_missing_cma_histogram_makes_pair_partial(self):
        first = make_snapshot(t=100)
        second = make_snapshot(t=200)
        second["allocators"]["pagetypeinfo"]["status"] = "partial"
        report = compare_snapshots([first, second])
        self.assertEqual(report["comparison_status"], "partial")
        self.assertEqual(report["pairs"][0]["cma_histogram_status"], "unavailable_or_partial")

    def test_counter_reset_makes_pair_partial_and_delta_unknown(self):
        first = make_snapshot(t=100)
        second = make_snapshot(t=200)
        second["system"]["vmstat"]["values"]["cma_alloc_success"] = 35
        report = compare_snapshots([first, second])
        pair = report["pairs"][0]
        self.assertEqual(pair["status"], "partial")
        self.assertEqual(pair["counter_status"]["cma_alloc_success"], "reset_or_reordered_sample")
        self.assertIsNone(pair["deltas"]["cma_alloc_success_delta"])

    def test_nonincreasing_monotonic_time_makes_pair_partial(self):
        first = make_snapshot(t=100)
        second = make_snapshot(t=100)
        report = compare_snapshots([first, second])
        self.assertEqual(report["comparison_status"], "partial")
        self.assertIsNone(report["pairs"][0]["elapsed_monotonic_ns"])

    def test_target_runtime_inode_drift_makes_pair_partial(self):
        first = make_snapshot(t=100)
        second = make_snapshot(t=200)
        second["processes"]["target_runtime"]["exe_ino"] = 99
        report = compare_snapshots([first, second])
        pair = report["pairs"][0]
        self.assertEqual(pair["status"], "partial")
        self.assertFalse(pair["target_runtime_identity"]["same"])

    def test_compare_requires_two_or_three_snapshots(self):
        with self.assertRaises(ValueError):
            compare_snapshots([make_snapshot()])
        with self.assertRaises(ValueError):
            compare_snapshots([make_snapshot()] * 4)


if __name__ == "__main__":
    unittest.main()
