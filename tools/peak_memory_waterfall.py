#!/usr/bin/env python3
"""Build separate, identity-qualified Lamentum memory ledgers; never sum unlike bases."""
import argparse
import hashlib
import json
import re
from pathlib import Path

from cma_readonly_compare import compare_snapshots
from ledger_bases import replay_texture_budget

_FIELD = re.compile(r"([A-Za-z0-9_-]+)=(\S+)")


def _fields(line):
    return dict(_FIELD.findall(line))


def _int_or_none(value):
    return int(value) if isinstance(value, str) and value.isdigit() else None


def _matches(row, expected, keys):
    return all(str(row.get(key)) == str(expected.get(key)) for key in keys)


def _timeline_records(timeline, expected):
    keys = ("run_uuid", "boot_id", "pid", "starttime", "elf_sha256")
    identity = timeline.get("identity")
    if not isinstance(identity, dict) or not _matches(timeline, expected, ("run_uuid", "elf_sha256")):
        raise ValueError("memory timeline run identity mismatch")
    if not _matches(identity, expected, ("boot_id", "pid", "starttime")):
        raise ValueError("mixed process identity in memory timeline")
    for key in ("elf_dev", "elf_ino"):
        if key in expected and str(identity.get(key)) != str(expected[key]):
            raise ValueError("memory timeline executable identity mismatch")

    samples = timeline.get("samples")
    if not isinstance(samples, list):
        raise ValueError("memory timeline samples must be a list")
    records = []
    reasons = []
    last_seq = last_ns = -1
    for row in samples:
        if not isinstance(row, dict) or not _matches(row, expected, keys):
            raise ValueError("mixed process identity in memory samples")
        seq, stamp = row.get("seq"), row.get("t_monotonic_ns")
        if type(seq) is not int or seq <= last_seq:
            raise ValueError("memory timeline sequence is not strictly increasing")
        if type(stamp) is not int or stamp <= last_ns:
            raise ValueError("memory timeline monotonic timestamps are not strictly increasing")
        last_seq, last_ns = seq, stamp
        status = row.get("sample_status")
        if status not in ("ok", "exited"):
            reasons.append("memory_sample_" + str(status or "missing_status"))
        if status == "ok" and row.get("running") is not True:
            reasons.append("memory_sample_running_state_mismatch")
        records.append({
            "run_uuid": row.get("run_uuid"), "boot_id": row.get("boot_id"),
            "pid": row.get("pid"), "starttime": row.get("starttime"),
            "elf_sha256": row.get("elf_sha256"), "monotonic_ns": stamp,
            "seq": seq, "phase": row.get("phase"), "sample_status": status,
            "present_serial": row.get("present_serial"),
            "present_serial_status": "observed" if type(row.get("present_serial")) is int else "unobserved",
            "process_kib": dict(row.get("process") or {}),
            "system_kib": dict(row.get("system") or {}),
            "pressure_memory": row.get("pressure_memory"),
            "pressure_status": "observed" if row.get("pressure_memory") is not None else "unavailable",
            "vmstat": dict(row.get("vmstat") or {}),
            "sample_duration_ns": row.get("sample_duration_ns"),
        })

    declared_count = timeline.get("sample_count")
    if type(declared_count) is not int or declared_count != len(samples):
        reasons.append("memory_sample_count_mismatch")
    if timeline.get("complete") is not True or timeline.get("dropped_samples") != 0:
        reasons.append("memory_timeline_incomplete")
    return records, list(dict.fromkeys(reasons))


def _floor_record(log_text, run_uuid):
    rows = [_fields(line) for line in log_text.splitlines()
            if line.startswith("LC2_MENU_FLOOR_MEMORY ")]
    if len(rows) != 1 or rows[0].get("run-id") != run_uuid:
        return None, "missing_or_ambiguous_menu_floor"
    row = rows[0]
    result = {key.replace("-", "_"): row.get(key) for key in (
        "floor-check-t-ns", "snapshot-start-ns", "snapshot-end-ns", "snapshot-read-ns",
        "floor-available-kib", "floor-swap-free-kib", "cmafree-kib", "vmrss-kib", "vmswap-kib",
        "meminfo-read", "status-read")}
    for key in ("floor_check_t_ns", "snapshot_start_ns", "snapshot_end_ns", "snapshot_read_ns",
                "floor_available_kib", "floor_swap_free_kib", "cmafree_kib", "vmrss_kib", "vmswap_kib"):
        value = result.get(key)
        if value is not None and value.isdigit():
            result[key] = int(value)
        else:
            result[key] = None
    if result["floor_check_t_ns"] is None:
        return result, "menu_floor_check_time_missing"
    if result["meminfo_read"] != "1" or result["status_read"] != "1":
        return result, "menu_floor_snapshot_incomplete"
    if any(result[key] is None for key in ("floor_check_t_ns", "snapshot_start_ns", "snapshot_end_ns",
                                               "floor_available_kib", "floor_swap_free_kib", "cmafree_kib",
                                               "vmrss_kib", "vmswap_kib")):
        return result, "menu_floor_snapshot_fields_missing"
    start, end, read = (result["snapshot_start_ns"], result["snapshot_end_ns"], result["snapshot_read_ns"])
    if start is None or end is None or read is None or read != end - start:
        return result, "menu_floor_snapshot_bracket_mismatch"
    if result["floor_check_t_ns"] > start:
        return result, "menu_floor_check_after_snapshot_start"
    return result, None


def _m3b_interval(row, prefix, outer_start, outer_end, reasons):
    start = _int_or_none(row.get(prefix + "-start-ns"))
    end = _int_or_none(row.get(prefix + "-end-ns"))
    wall = _int_or_none(row.get(prefix + "-wall-ns"))
    if start is None or end is None or wall is None:
        reasons.append("m3b_interval_fields_missing:" + prefix)
        return {"start_ns": None, "end_ns": None, "wall_ns": None, "status": "missing"}
    if start == end == wall == 0:
        status = "unobserved"
    elif start == 0 or end == 0 or end < start or wall != end - start:
        reasons.append("m3b_interval_inconsistent:" + prefix)
        status = "incomplete"
    elif start < outer_start or end > outer_end:
        reasons.append("m3b_interval_outside_window:" + prefix)
        status = "incomplete"
    else:
        status = "observed"
    return {"start_ns": start, "end_ns": end, "wall_ns": wall, "status": status}


def _m3b_records(log_text, run_uuid, required):
    windows, marks = [], []
    summary = None
    last_seq = last_start = last_event_ns = -1
    reasons = []
    size_fields = ("source-compressed-bytes", "rgba-requested-bytes", "linear-requested-bytes",
                   "staging-live-requested-peak-bytes", "gl-intent-bytes")
    for line in log_text.splitlines():
        if line.startswith("LC2_M3B_WINDOW "):
            row = _fields(line)
            if row.get("run-id") != run_uuid:
                raise ValueError("foreign M3B window")
            seq, start, end = (row.get(key) for key in ("event-seq", "t-start-ns", "t-end-ns"))
            if not (seq and start and end and seq.isdigit() and start.isdigit() and end.isdigit()):
                reasons.append("m3b_window_timestamp_missing")
                continue
            seq, start, end = int(seq), int(start), int(end)
            if seq <= last_seq or start < last_start or start < last_event_ns or end < start:
                raise ValueError("M3B event sequence or monotonic timestamps reordered")
            last_seq, last_start, last_event_ns = seq, start, start
            metrics = {}
            for key in size_fields:
                value = row.get(key)
                metrics[key.replace("-", "_")] = int(value) if value and value.isdigit() else None
                if metrics[key.replace("-", "_")] is None:
                    reasons.append("m3b_window_size_missing:" + key)
            intervals = {name + "_interval": _m3b_interval(row, prefix, start, end, reasons)
                        for name, prefix in (("decode", "decode"), ("gl_alloc", "gl-alloc"), ("gl_upload", "gl-upload"))}
            size_match = re.fullmatch(r"(\d+)x(\d+)", row.get("size", ""))
            width, height = (int(size_match.group(1)), int(size_match.group(2))) if size_match else (None, None)
            if size_match is None:
                reasons.append("m3b_window_size_dimensions_missing")
            format_value = row.get("format")
            try:
                format_value = int(format_value, 0) if format_value is not None else None
            except ValueError:
                format_value = None
                reasons.append("m3b_window_format_missing")
            level, allocate = _int_or_none(row.get("level")), _int_or_none(row.get("allocate"))
            if level is None or allocate not in (0, 1):
                reasons.append("m3b_window_subresource_or_allocate_missing")
            owner_id = _int_or_none(row.get("owner-id"))
            owner_generation_raw = _int_or_none(row.get("owner-generation"))
            generation_basis = row.get("generation-basis")
            if owner_id is None or owner_generation_raw is None or generation_basis in (None, "unknown", "untracked"):
                reasons.append("m3b_window_owner_identity_missing")
            owner_generation = (owner_generation_raw if generation_basis not in (None, "nvn-object-id", "unknown", "untracked")
                               else None)
            owner_generation_status = ("source_basis_is_object_id_only" if generation_basis == "nvn-object-id"
                                       else "unverified" if owner_generation is None else "basis_present_not_independently_proven")
            windows.append({
                "run_uuid": run_uuid, "event_seq": seq, "phase": row.get("stage"),
                "t_start_ns": start, "t_end_ns": end, **intervals,
                "owner_id": owner_id, "owner_generation": owner_generation,
                "owner_generation_raw": owner_generation_raw, "owner_generation_status": owner_generation_status,
                "generation_basis": generation_basis,
                "object": row.get("object"), "gl_name": _int_or_none(row.get("gl-name")),
                "storage_generation": _int_or_none(row.get("storage-generation")),
                "storage_generation_known": row.get("storage-generation-known") == "1",
                "content_generation": _int_or_none(row.get("content-generation")),
                "pool_id": _int_or_none(row.get("pool-id")),
                "pool_generation": _int_or_none(row.get("pool-generation")),
                "width": width, "height": height, "level": level, "format": format_value,
                "allocate": allocate, **metrics,
                "gl_error": row.get("gl-error", "unknown"),
                "driver_allocation": row.get("driver-allocation", "unknown"),
                "gpu_inflight": row.get("gpu-inflight", "unknown"),
                "fileback_shadow": row.get("fileback-shadow", "unknown"),
                "mali_residency": row.get("mali-residency", "unknown"),
                "completion_state": row.get("completion", "unknown"),
                "present_serial": None, "present_serial_status": "not_emitted_by_m3b",
                "source_write_generation": row.get("source-write-generation", "unknown"),
                "confidence": "requested-overlap-only",
            })
        elif line.startswith("LC2_M3B_MARK "):
            row = _fields(line)
            if row.get("run-id") != run_uuid:
                raise ValueError("foreign M3B mark")
            seq, stamp = row.get("event-seq"), row.get("t-ns")
            if not (seq and stamp and seq.isdigit() and stamp.isdigit()):
                reasons.append("m3b_mark_timestamp_missing")
                continue
            seq, stamp = int(seq), int(stamp)
            if seq <= last_seq or stamp < last_event_ns:
                raise ValueError("M3B mark sequence or monotonic timestamps reordered")
            last_seq, last_event_ns = seq, stamp
            marks.append({"event_seq": seq, "t_ns": stamp,
                          "name": row.get("name"), "value": row.get("value")})
        elif line.startswith("LC2_M3B_SUMMARY "):
            if summary is not None:
                reasons.append("multiple_m3b_summaries")
            summary = _fields(line)

    if summary is not None:
        if summary.get("run-id") != run_uuid:
            raise ValueError("foreign M3B summary")
        try:
            configured = int(summary.get("configured", "-1"))
            claimed = int(summary.get("claimed", "-1"))
            final_claimed = int(summary.get("final-claimed", "-1"))
            emitted = int(summary.get("emitted", "-1"))
            ring_errors = any(int(summary.get(key, "0")) for key in ("incomplete", "active", "dropped", "format-errors"))
        except ValueError:
            configured = claimed = final_claimed = emitted = -1
            ring_errors = True
        if (summary.get("complete") != "1" or configured < 0 or claimed < 0 or claimed > configured
                or final_claimed != claimed or emitted != len(windows) + len(marks) or ring_errors):
            reasons.append("m3b_ring_incomplete")
    elif required or windows or marks:
        reasons.append("m3b_summary_missing")
    if required and not windows:
        reasons.append("m3b_windows_missing")
    return windows, marks, summary, list(dict.fromkeys(reasons))


def _owned_event_records(log_text, run_uuid):
    prefixes = ("LC2_TEXTURE_BUDGET_EVENT ", "LC2_TEXTURE_PAIR ",
                "LC2_TEXTURE_OWNER_EVENT ", "LC2_GL_STORAGE_EVENT ", "LC2_GL_STORAGE_DELETE ")
    result, reasons = [], []
    for index, line in enumerate(log_text.splitlines()):
        prefix = next((value for value in prefixes if line.startswith(value)), None)
        if prefix is None:
            continue
        row = _fields(line)
        if row.get("run-id") != run_uuid:
            raise ValueError("foreign owned memory event")
        stamp = _int_or_none(row.get("t-ns"))
        if stamp is None:
            reasons.append("owned_event_timestamp_missing")
        result.append({
            "event_type": prefix.strip(), "log_index": index, "run_uuid": run_uuid,
            "monotonic_ns": stamp, "owner_id": row.get("owner", row.get("texture-id", row.get("nvn-id"))),
            "object_generation": row.get("object-generation"), "gl_name": row.get("gl-name"),
            "storage_generation": row.get("storage-generation"), "fields": row,
        })
    return result, list(dict.fromkeys(reasons))


def _cma_records(snapshots, expected):
    reasons = []
    if not isinstance(snapshots, list) or len(snapshots) not in (2, 3):
        return [], None, ["cma_snapshot_count_not_two_or_three"]
    last_ns = -1
    rows = []
    for snap in snapshots:
        if not isinstance(snap, dict) or snap.get("sample_status") != "complete":
            reasons.append("cma_snapshot_incomplete")
            continue
        boot = snap.get("identity", {}).get("boot_id")
        stamp = snap.get("timestamps", {}).get("monotonic_ns")
        if str(boot) != str(expected.get("boot_id")):
            raise ValueError("CMA snapshot boot ID differs from owned run")
        if type(stamp) is not int or stamp <= last_ns:
            raise ValueError("CMA snapshot monotonic timestamps are not strictly increasing")
        last_ns = stamp
        mem = snap.get("system", {}).get("meminfo", {}).get("values_kib", {})
        free_rows = snap.get("allocators", {}).get("pagetypeinfo", {}).get("free_pages_by_migrate_type", [])
        cma_row = next((row for row in free_rows if row.get("migrate_type") == "CMA"), None)
        processes = snap.get("processes", {})
        mainui_rows = processes.get("mainui", [])
        mainui = mainui_rows[0] if isinstance(mainui_rows, list) and len(mainui_rows) == 1 else None
        runtime = processes.get("target_runtime")
        dma = snap.get("dma_buf", {})
        if dma.get("status") != "ok" or dma.get("truncated") is not False:
            reasons.append("dma_buf_inventory_unavailable_or_truncated")
        rows.append({
            "boot_id": boot, "monotonic_ns": stamp,
            "CmaTotal_kib": mem.get("CmaTotal"), "CmaFree_kib": mem.get("CmaFree"),
            "MemAvailable_kib": mem.get("MemAvailable"), "SwapFree_kib": mem.get("SwapFree"),
            "free_cma_blocks_by_order": (cma_row or {}).get("counts_by_order"),
            "dma_buf_status": snap.get("dma_buf", {}).get("status"),
            "dma_buf_entries": snap.get("dma_buf", {}).get("entries"),
            "mainui_identity": ({key: mainui.get(key) for key in ("pid", "starttime", "exe_dev", "exe_ino")}
                                if mainui else None),
            "target_runtime_identity": ({key: runtime.get(key) for key in ("exe_dev", "exe_ino")}
                                        if isinstance(runtime, dict) and runtime.get("status") == "ok" else None),
            "game_count": len(processes.get("game_processes", [])),
            "process_scan_status": processes.get("status"),
            "cma_page_owner": "unknown",
        })
    comparison = None
    if not reasons:
        comparison = compare_snapshots(snapshots)
        if comparison.get("comparison_status") != "complete":
            reasons.append("cma_snapshot_comparison_incomplete")
    return rows, comparison, list(dict.fromkeys(reasons))


def _kernel_records(bundle, expected):
    if bundle is None:
        return {"status": "unavailable", "records": None}, ["kernel_warning_deltas_missing"]
    if not isinstance(bundle, dict) or bundle.get("capture_status") != "ok":
        return {"status": "incomplete", "records": None}, ["kernel_warning_capture_incomplete"]
    if str(bundle.get("boot_id")) != str(expected["boot_id"]):
        raise ValueError("kernel warning delta boot ID differs from owned run")
    rows = bundle.get("records")
    if not isinstance(rows, list):
        return {"status": "invalid", "records": None}, ["kernel_warning_delta_records_missing"]
    result = []
    last_ns = -1
    reasons = []
    for row in rows:
        stamp = row.get("monotonic_ns") if isinstance(row, dict) else None
        if not isinstance(row, dict) or str(row.get("boot_id")) != str(expected["boot_id"]):
            raise ValueError("kernel warning delta boot ID differs from owned run")
        if type(stamp) is not int or stamp <= last_ns:
            raise ValueError("kernel warning delta timestamps are not strictly increasing")
        last_ns = stamp
        lines = row.get("matching_lines")
        if not isinstance(lines, list):
            reasons.append("kernel_warning_delta_lines_missing")
            lines = None
        result.append({"boot_id": row["boot_id"], "monotonic_ns": stamp,
                       "matching_lines": lines, "scope": "system-wide; not process-attributed"})
    return {"status": "observed" if not reasons else "incomplete", "records": result}, reasons


def build_waterfall(log_text, memory_timeline, cma_snapshots, expected_run, *,
                    memory_floor_mib=None, owner_events_expected=True, m3b_required=True,
                    kernel_warning_deltas=None):
    """Join only owned/time-bracketed records; unlike memory bases remain separate."""
    required = ("run_uuid", "boot_id", "pid", "starttime", "elf_sha256")
    if not isinstance(expected_run, dict) or any(key not in expected_run for key in required):
        raise ValueError("expected run identity is incomplete")
    if memory_floor_mib is not None and (type(memory_floor_mib) is not int or memory_floor_mib <= 0):
        raise ValueError("memory_floor_mib must be a positive integer")

    memory_records, reasons = _timeline_records(memory_timeline, expected_run)
    cma_rows, cma_comparison, cma_reasons = _cma_records(cma_snapshots, expected_run)
    reasons.extend(cma_reasons)
    kernel_records, kernel_reasons = _kernel_records(kernel_warning_deltas, expected_run)
    reasons.extend(kernel_reasons)
    floor, floor_error = _floor_record(log_text, expected_run["run_uuid"])
    if floor_error:
        reasons.append(floor_error)
    windows, marks, m3b_summary, m3b_reasons = _m3b_records(log_text, expected_run["run_uuid"], m3b_required)
    reasons.extend(m3b_reasons)
    owned_events, owned_event_reasons = _owned_event_records(log_text, expected_run["run_uuid"])
    reasons.extend(owned_event_reasons)
    if memory_floor_mib == 64 and (floor is None or not any(row["sample_status"] == "ok" for row in memory_records)):
        reasons.append("64_mib_floor_sample_missing")

    try:
        accounting = replay_texture_budget(log_text, expected_run, owner_events_expected=owner_events_expected)
        accounting_status = "reconciled"
    except (ValueError, KeyError, TypeError) as exc:
        accounting = None
        accounting_status = "incomplete"
        reasons.append("ledger_replay:" + str(exc))

    cpu_bc_peaks = [row["staging_live_requested_peak_bytes"] for row in windows
                    if row.get("phase", "").startswith("bc-") and row.get("staging_live_requested_peak_bytes") is not None]
    cpu_other_peaks = [row["staging_live_requested_peak_bytes"] for row in windows
                       if not row.get("phase", "").startswith("bc-") and row.get("staging_live_requested_peak_bytes") is not None]
    gpu_unknown = any(row["gpu_inflight"] in (None, "unknown") or
                      row["completion_state"] in (None, "unknown", "unobserved") for row in windows)
    if not m3b_required and not windows:
        m3b_status = "not_enabled"
    elif m3b_summary and m3b_summary.get("complete") == "1" and not m3b_reasons:
        m3b_status = "complete"
    else:
        m3b_status = "incomplete"

    if accounting:
        budget = accounting["budget"]
        gl = accounting["gl_storage"]
        guest_ledger = {key: budget.get(key) for key in (
            "guest_bytes", "pair_charge_bytes", "live_bytes", "peak_bytes", "live_ids", "pair_coverage")}
        gl_ledger = {key: gl.get(key) for key in ("bytes_by_kind", "records_by_kind", "live_records", "summary_matches")}
    else:
        guest_ledger = {"status": "unknown", "live_bytes": None, "peak_bytes": None}
        gl_ledger = {"status": "unknown", "bytes_by_kind": None, "live_records": None}

    for row in windows:
        row.update({key: expected_run[key] for key in ("boot_id", "pid", "starttime", "elf_sha256")})
        row["share_group"] = None
    for event in owned_events:
        event.update({key: expected_run[key] for key in ("boot_id", "pid", "starttime", "elf_sha256")})
        event["present_serial"] = None
        event["present_serial_status"] = "not_emitted_by_event"
    for mark in marks:
        mark.update({key: expected_run[key] for key in ("boot_id", "pid", "starttime", "elf_sha256")})
        mark["present_serial"] = None
        mark["present_serial_status"] = "marker_value_not_verified_as_present_serial"

    for row in memory_records:
        duration = row.get("sample_duration_ns")
        end = row["monotonic_ns"] + duration if type(duration) is int and duration >= 0 else None
        row["read_end_monotonic_ns"] = end
        row["m3b_windows_overlapping_read"] = [window["event_seq"] for window in windows
            if end is not None and window["t_start_ns"] <= end and window["t_end_ns"] >= row["monotonic_ns"]]
        row["owned_event_log_indices_overlapping_read"] = [event["log_index"] for event in owned_events
            if end is not None and type(event["monotonic_ns"]) is int
            and row["monotonic_ns"] <= event["monotonic_ns"] <= end]

    floor_start = floor.get("snapshot_start_ns") if floor else None
    floor_end = floor.get("snapshot_end_ns") if floor else None
    if type(floor_start) is int and type(floor_end) is int:
        floor_sample_seqs = [row["seq"] for row in memory_records
                             if type(row.get("read_end_monotonic_ns")) is int
                             and row["monotonic_ns"] <= floor_end
                             and row["read_end_monotonic_ns"] >= floor_start]
        floor_join_status = "interval_overlap" if floor_sample_seqs else "no_interval_overlap"
    else:
        floor_sample_seqs, floor_join_status = [], "unavailable"
    cma_sample_joins = []
    for index, point in enumerate(cma_rows):
        cma_sample_joins.append({"cma_snapshot_index": index,
            "memory_sample_seqs": [row["seq"] for row in memory_records
                if type(row.get("read_end_monotonic_ns")) is int
                and row["monotonic_ns"] <= point["monotonic_ns"] <= row["read_end_monotonic_ns"]]})

    memwatch = []
    for line in log_text.splitlines():
        if line.startswith("T2_MEMWATCH_SAMPLE "):
            memwatch.append(_fields(line))
    memwatch_status = "unjoined_no_timestamp" if memwatch and not any(
        row.get("t-ns") or row.get("t-monotonic-ns") for row in memwatch) else ("present" if memwatch else "missing")

    reasons = list(dict.fromkeys(reasons))
    status = "complete" if not reasons and accounting_status == "reconciled" and m3b_status in ("complete", "not_enabled") else "incomplete"
    return {
        "schema_version": 1, "status": status, "run": {key: expected_run[key] for key in required},
        "incomplete_reasons": reasons, "interpolation_used": False,
        "memory_floor_mib": memory_floor_mib, "floor_snapshot": floor,
        "accounting_status": accounting_status, "accounting": accounting,
        "m3b_status": m3b_status, "m3b_windows": windows, "m3b_marks": marks,
        "owned_events": owned_events,
        "memwatch": {"records": memwatch, "join_status": memwatch_status},
        "time_joins": {"method": "exact captured interval overlap only; no nearest-sample interpolation",
                       "floor_to_process": {"status": floor_join_status, "sample_seqs": floor_sample_seqs},
                       "cma_to_process": cma_sample_joins},
        "kernel_warning_deltas": kernel_records,
        "memory_samples": memory_records,
        "cma": {"snapshots": cma_rows, "comparison": cma_comparison,
                "physical_owner": "unknown"},
        "ledgers": {
            "guest_source": guest_ledger,
            "cpu_bc_staging": {"peak_requested_bytes": max(cpu_bc_peaks) if cpu_bc_peaks else None,
                                "aggregation": "maximum of individual BC windows; never summed",
                                "physical_bytes": None},
            "cpu_other_staging": {"peak_requested_bytes": max(cpu_other_peaks) if cpu_other_peaks else None,
                                  "aggregation": "maximum of individual non-BC windows; never summed",
                                  "physical_bytes": None},
            "gl_nominal_storage": {**gl_ledger, "physical_bytes": None,
                                    "completion_state": "unknown" if gpu_unknown else "unproven"},
            "fileback_mirror": {"bytes": None, "status": "unmeasured"},
            "egl_gbm_display": {"bytes": None, "status": "unmeasured"},
            "process_pages": [{"monotonic_ns": row["monotonic_ns"], **row["process_kib"]}
                              for row in memory_records],
            "driver_dma": {"proven_cma_bytes": None, "pinned_cma_bytes": None,
                           "mali_private_bytes": None, "physical_attribution": "unknown"},
        },
        "promotion_eligible": False,
        "promotion_blockers": ["GPU completion/physical backing are not proven",
                                "no measured same-run retained overlap and retirement floor"],
    }


def _read_stable(path, limit):
    path = Path(path)
    before = path.stat()
    if before.st_size > limit:
        raise ValueError("input exceeds bounded read limit: " + str(path))
    raw = path.read_bytes()
    after = path.stat()
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
            after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
        raise ValueError("input changed during bounded read: " + str(path))
    if len(raw) != before.st_size:
        raise ValueError("input size changed during read: " + str(path))
    return raw, hashlib.sha256(raw).hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--timeline", type=Path, required=True)
    parser.add_argument("--cma-snapshot", type=Path, action="append", required=True)
    parser.add_argument("--harness", type=Path, required=True)
    parser.add_argument("--kernel-warning-deltas", type=Path, required=True)
    parser.add_argument("--memory-floor-mib", type=int)
    parser.add_argument("--allow-legacy-owner-ring", action="store_true")
    args = parser.parse_args(argv)
    log_raw, log_sha = _read_stable(args.log, 16 * 1024 * 1024)
    timeline_raw, _ = _read_stable(args.timeline, 4 * 1024 * 1024)
    harness_raw, harness_sha = _read_stable(args.harness, 1024 * 1024)
    warnings_raw, warnings_sha = _read_stable(args.kernel_warning_deltas, 1024 * 1024)
    cma_data = [_read_stable(path, 4 * 1024 * 1024) for path in args.cma_snapshot]
    harness = json.loads(harness_raw)
    expected = harness["expected_run"]
    result = build_waterfall(log_raw.decode("utf-8", "replace"), json.loads(timeline_raw),
                             [json.loads(raw) for raw, _ in cma_data], expected,
                             memory_floor_mib=args.memory_floor_mib,
                             owner_events_expected=not args.allow_legacy_owner_ring,
                             m3b_required=harness.get("m3b_required", True),
                             kernel_warning_deltas=json.loads(warnings_raw))
    result["input_sha256"] = {"log_current_copy": log_sha, "timeline": hashlib.sha256(timeline_raw).hexdigest(),
                              "harness": harness_sha, "cma_snapshots": [digest for _, digest in cma_data],
                              "kernel_warning_deltas": warnings_sha}
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
