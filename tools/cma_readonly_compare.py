#!/usr/bin/env python3
"""Compare two or three read-only CMA snapshots without inferring ownership."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SCALAR_MEMINFO_KEYS = ("CmaTotal", "CmaFree", "MemAvailable", "SwapFree", "MemFree")
GAUGE_KEYS = ("nr_free_cma",)
COUNTER_KEYS = ("cma_alloc_success", "cma_alloc_fail", "pswpin", "pswpout",
                "pgmajfault", "pgfault", "compact_stall", "compact_fail", "compact_success",
                "pgmigrate_success", "pgmigrate_fail")
VMSTAT_KEYS = GAUGE_KEYS + COUNTER_KEYS


def _int_value(value):
    return value if type(value) is int else None


def _cma_rows(snapshot):
    info = snapshot.get("allocators", {}).get("pagetypeinfo", {})
    if info.get("status") != "ok":
        return None
    result = {}
    for row in info.get("free_pages_by_migrate_type", []):
        if str(row.get("migrate_type", "")).upper() != "CMA":
            continue
        key = f"{row.get('node')}: {row.get('zone')}"
        counts = row.get("counts_by_order")
        if not isinstance(counts, dict):
            return None
        parsed = {str(order): _int_value(count) for order, count in counts.items()}
        if any(value is None or value < 0 for value in parsed.values()):
            return None
        result[key] = parsed
    return result or None


def _mainui_identity(snapshot):
    processes = snapshot.get("processes", {})
    if not isinstance(processes, dict):
        return None
    rows = processes.get("mainui")
    if processes.get("status") != "ok" or not isinstance(rows, list) or len(rows) != 1:
        return None
    row = rows[0]
    if any(type(row.get(key)) is not int for key in ("pid", "starttime", "exe_dev", "exe_ino")):
        return None
    return row


def _target_runtime_identity(snapshot):
    processes = snapshot.get("processes", {})
    if not isinstance(processes, dict) or processes.get("status") != "ok":
        return None
    runtime = processes.get("target_runtime")
    if not isinstance(runtime, dict) or runtime.get("status") != "ok":
        return None
    if any(type(runtime.get(key)) is not int for key in ("exe_dev", "exe_ino")):
        return None
    return runtime


def _compare_pair(previous, current, previous_index, current_index):
    old_boot = previous.get("identity", {}).get("boot_id")
    new_boot = current.get("identity", {}).get("boot_id")
    pair = {
        "from_index": previous_index,
        "to_index": current_index,
        "status": "ok",
        "elapsed_monotonic_ns": None,
        "deltas": {},
        "counter_status": {},
        "cma_free_blocks_by_order_delta": {},
        "cma_histogram_status": "unavailable",
        "mainui_identity": {"same": None, "dma_fds_same": None},
        "target_runtime_identity": {"same": None},
        "interpretation": (
            "A free MIGRATE_CMA order histogram is a point-in-time buddy observation; "
            "it is not proof that a particular allocation succeeds, nor proof of Mali backing."
        ),
    }
    old_t = previous.get("timestamps", {}).get("monotonic_ns")
    new_t = current.get("timestamps", {}).get("monotonic_ns")
    if type(old_t) is int and type(new_t) is int and new_t > old_t:
        pair["elapsed_monotonic_ns"] = new_t - old_t
    if not old_boot or not new_boot or old_boot != new_boot:
        pair["status"] = "identity_mismatch"
        for key in SCALAR_MEMINFO_KEYS:
            pair["deltas"][key + "_kib"] = None
        for key in VMSTAT_KEYS:
            result_key = "nr_free_cma_pages" if key == "nr_free_cma" else key + "_delta"
            pair["deltas"][result_key] = None
            pair["counter_status"][key] = "identity_mismatch"
        pair["cma_histogram_status"] = "identity_mismatch"
        return pair

    old_mem = previous.get("system", {}).get("meminfo", {}).get("values_kib", {})
    new_mem = current.get("system", {}).get("meminfo", {}).get("values_kib", {})
    for key in SCALAR_MEMINFO_KEYS:
        old_value, new_value = _int_value(old_mem.get(key)), _int_value(new_mem.get(key))
        pair["deltas"][key + "_kib"] = new_value - old_value if old_value is not None and new_value is not None else None

    old_vm = previous.get("system", {}).get("vmstat", {}).get("values", {})
    new_vm = current.get("system", {}).get("vmstat", {}).get("values", {})
    for key in VMSTAT_KEYS:
        old_value, new_value = _int_value(old_vm.get(key)), _int_value(new_vm.get(key))
        result_key = "nr_free_cma_pages" if key == "nr_free_cma" else key + "_delta"
        if old_value is None or new_value is None:
            pair["deltas"][result_key] = None
            pair["counter_status"][key] = "unavailable"
        elif key in GAUGE_KEYS:
            pair["deltas"][result_key] = new_value - old_value
            pair["counter_status"][key] = "ok"
        elif new_value < old_value:
            pair["deltas"][result_key] = None
            pair["counter_status"][key] = "reset_or_reordered_sample"
        else:
            pair["deltas"][result_key] = new_value - old_value
            pair["counter_status"][key] = "ok"

    old_rows, new_rows = _cma_rows(previous), _cma_rows(current)
    if old_rows is None or new_rows is None:
        pair["cma_histogram_status"] = "unavailable_or_partial"
    else:
        pair["cma_histogram_status"] = "ok"
        for zone in sorted(set(old_rows) | set(new_rows)):
            old_counts, new_counts = old_rows.get(zone), new_rows.get(zone)
            if old_counts is None or new_counts is None:
                pair["cma_free_blocks_by_order_delta"][zone] = None
                pair["cma_histogram_status"] = "partial"
                continue
            orders = sorted(set(old_counts) | set(new_counts), key=lambda value: int(value))
            deltas = {}
            for order in orders:
                before, after = old_counts.get(order), new_counts.get(order)
                deltas[order] = after - before if before is not None and after is not None else None
                if deltas[order] is None:
                    pair["cma_histogram_status"] = "partial"
            pair["cma_free_blocks_by_order_delta"][zone] = deltas

    old_main, new_main = _mainui_identity(previous), _mainui_identity(current)
    if old_main is not None and new_main is not None:
        same_identity = all(old_main.get(key) == new_main.get(key)
                            for key in ("pid", "starttime", "exe_dev", "exe_ino"))
        pair["mainui_identity"]["same"] = same_identity
        old_fds, new_fds = old_main.get("dma_fds"), new_main.get("dma_fds")
        if (old_main.get("fd_scan_truncated") is False and new_main.get("fd_scan_truncated") is False
                and isinstance(old_fds, list) and isinstance(new_fds, list)):
            fd_fields = ("fd", "target", "dev", "ino")
            key_fn = lambda row: tuple(row.get(field) for field in fd_fields)
            pair["mainui_identity"]["dma_fds_same"] = sorted(key_fn(row) for row in old_fds) == sorted(key_fn(row) for row in new_fds)

    old_runtime = _target_runtime_identity(previous)
    new_runtime = _target_runtime_identity(current)
    if old_runtime is not None and new_runtime is not None:
        pair["target_runtime_identity"]["same"] = all(
            old_runtime.get(key) == new_runtime.get(key) for key in ("exe_dev", "exe_ino"))

    statuses = (previous.get("sample_status"), current.get("sample_status"))
    required_deltas = tuple(key + "_kib" for key in SCALAR_MEMINFO_KEYS) + ("nr_free_cma_pages",)
    counter_reset = any(status == "reset_or_reordered_sample" for status in pair["counter_status"].values())
    if (any(status != "complete" for status in statuses)
            or any(pair["deltas"].get(key) is None for key in required_deltas)
            or pair["elapsed_monotonic_ns"] is None
            or pair["cma_histogram_status"] != "ok"
            or pair["mainui_identity"]["same"] is not True
            or pair["mainui_identity"]["dma_fds_same"] is not True
            or pair["target_runtime_identity"]["same"] is not True
            or counter_reset):
        pair["status"] = "partial"
    return pair


def compare_snapshots(snapshots):
    if not isinstance(snapshots, list) or len(snapshots) not in (2, 3):
        raise ValueError("provide exactly two or three snapshots")
    if any(not isinstance(snapshot, dict) or snapshot.get("schema_version") != 1 for snapshot in snapshots):
        raise ValueError("all inputs must be schema_version=1 snapshot objects")
    pairs = [_compare_pair(snapshots[index], snapshots[index + 1], index, index + 1)
             for index in range(len(snapshots) - 1)]
    if any(pair["status"] == "identity_mismatch" for pair in pairs):
        status = "identity_mismatch"
    elif any(pair["status"] != "ok" for pair in pairs):
        status = "partial"
    else:
        status = "complete"
    return {"schema_version": 1, "comparison_status": status,
            "snapshot_count": len(snapshots), "pairs": pairs,
            "interpretation_limits": [
                "Comparisons are valid only within a matching boot and do not establish causation.",
                "Proc allocator files are read sequentially; histogram and vmstat values are not atomic.",
                "No DMA-BUF exporter size or CMA page count proves Mali physical residency.",
            ]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshots", nargs="+", help="two or three JSON snapshot files")
    args = parser.parse_args(argv)
    if len(args.snapshots) not in (2, 3):
        parser.error("provide exactly two or three snapshot files")
    snapshots = [json.loads(Path(path).read_text()) for path in args.snapshots]
    print(json.dumps(compare_snapshots(snapshots), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
