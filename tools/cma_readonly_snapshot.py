#!/usr/bin/env python3
"""Bounded, read-only CMA/allocator snapshot for TSPS K1.

Run on a target with ``python3 - < tools/cma_readonly_snapshot.py`` to stream a
single JSON receipt over SSH. This module never mounts, writes sysfs/procfs,
allocates test buffers, reads process memory, or changes allocator policy.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import re
import time
from pathlib import Path

SCHEMA_VERSION = 1
MAX_PROC_TEXT_BYTES = 65536
MAX_CONFIG_RAW_BYTES = 4 * 1024 * 1024
MAX_CONFIG_TEXT_BYTES = 16 * 1024 * 1024
MAX_DMABUF_ENTRIES = 128
MAX_PROCESS_ENTRIES = 512
MAX_PROCESS_FDS = 256
MEMINFO_KEYS = (
    "MemTotal", "MemAvailable", "MemFree", "CmaTotal", "CmaFree", "SwapFree",
    "Cached", "Mlocked", "Unevictable", "Slab", "SReclaimable",
)
VMSTAT_EXACT_KEYS = {
    "nr_free_cma", "cma_alloc_success", "cma_alloc_fail", "pswpin", "pswpout",
    "pgmajfault", "pgfault", "compact_stall", "compact_fail", "compact_success",
    "pgmigrate_success", "pgmigrate_fail",
}
VMSTAT_PREFIXES = ("compact_", "pgmigrate_", "pgscan_", "allocstall")
CONFIG_KEYS = (
    "CONFIG_PAGE_OWNER", "CONFIG_CMA_DEBUGFS", "CONFIG_DEBUG_FS", "CONFIG_COMPACTION",
    "CONFIG_CMA", "CONFIG_DMA_CMA", "CONFIG_DMABUF_HEAPS_SYSTEM",
)
INTERESTING_CMDLINE_KEYS = {"cma", "mem", "root", "rootfstype", "console", "earlycon", "loglevel", "sunxi"}
ZONEINFO_KEYS = {"pages_free", "min", "low", "high", "cma", "nr_free_cma"}


def _read_bounded(path: Path, limit: int):
    """Read at most limit bytes plus one sentinel byte; return no raw bytes in metadata."""
    try:
        with path.open("rb") as stream:
            raw = stream.read(limit + 1)
    except OSError as exc:
        return None, {"status": "unavailable", "error": type(exc).__name__, "truncated": False}
    truncated = len(raw) > limit
    captured = raw[:limit]
    return captured, {
        "status": "partial" if truncated else "ok",
        "bytes_read": len(raw),
        "captured_bytes": len(captured),
        "sha256": hashlib.sha256(captured).hexdigest(),
        "truncated": truncated,
    }


def _text_capture(path: Path, limit: int):
    raw, capture = _read_bounded(path, limit)
    if raw is None:
        return None, capture
    return raw.decode("utf-8", "replace"), capture


def _int_or_none(value):
    try:
        return int(value, 10)
    except (TypeError, ValueError):
        return None


def parse_meminfo(text: str | None, truncated: bool = False):
    values: dict[str, int | None] = {key: None for key in MEMINFO_KEYS}
    if text is not None:
        for line in text.splitlines():
            if ":" not in line:
                continue
            key, rest = line.split(":", 1)
            if key not in values:
                continue
            fields = rest.split()
            if not fields or (len(fields) > 1 and fields[1] != "kB"):
                continue
            values[key] = _int_or_none(fields[0])
    required = ("CmaTotal", "CmaFree", "MemAvailable")
    status = "ok" if not truncated and text is not None and all(values[k] is not None for k in required) else "partial"
    return {"status": status, "values_kib": values}


def parse_vmstat(text: str | None, truncated: bool = False):
    values = {}
    if text is not None:
        for line in text.splitlines():
            fields = line.split()
            if len(fields) < 2:
                continue
            key, value = fields[0], _int_or_none(fields[1])
            if value is None:
                continue
            if key in VMSTAT_EXACT_KEYS or key.startswith(VMSTAT_PREFIXES):
                values[key] = value
    required = ("nr_free_cma", "cma_alloc_success", "cma_alloc_fail")
    status = "ok" if not truncated and text is not None and all(k in values for k in required) else "partial"
    return {"status": status, "values": values}


def parse_buddyinfo(text: str | None, truncated: bool = False):
    rows = []
    malformed = False
    if text is not None:
        for line in text.splitlines():
            if not line.strip():
                continue
            match = re.match(r"^\s*Node\s+(\d+),\s*zone\s+(\S+)\s+(.*)$", line)
            if not match:
                malformed = True
                continue
            counts = [_int_or_none(value) for value in match.group(3).split()]
            if not counts or any(value is None or value < 0 for value in counts):
                malformed = True
                continue
            rows.append({"node": int(match.group(1)), "zone": match.group(2),
                         "free_blocks_by_order": counts})
    status = "ok" if rows and not malformed and not truncated else "partial"
    return {"status": status, "rows": rows}


def parse_pagetypeinfo(text: str | None, truncated: bool = False):
    page_block_order = None
    pages_per_block = None
    orders = []
    block_types = []
    free_rows = []
    block_rows = []
    section = None
    malformed = False
    if text is not None and not truncated:
        for line in text.splitlines():
            stripped = line.strip()
            lower = stripped.lower()
            if lower.startswith("page block order:"):
                page_block_order = _int_or_none(stripped.split(":", 1)[1].strip())
                continue
            if lower.startswith("pages per block:"):
                pages_per_block = _int_or_none(stripped.split(":", 1)[1].strip())
                continue
            if lower.startswith("free pages count per migrate type at order"):
                orders = [int(value) for value in re.findall(r"\d+", stripped.split("order", 1)[1])]
                section = "free"
                continue
            if lower.startswith("number of blocks type"):
                block_types = stripped.split("type", 1)[1].split()
                section = "blocks"
                continue
            if not stripped.startswith("Node"):
                continue
            if section == "free":
                match = re.match(r"^Node\s+(\d+),\s*zone\s+(\S+),\s*type\s+(\S+)\s+(.*)$", stripped)
                if not match:
                    malformed = True
                    continue
                counts = [_int_or_none(value) for value in match.group(4).split()]
                if not orders or len(counts) != len(orders) or any(v is None or v < 0 for v in counts):
                    malformed = True
                    continue
                free_rows.append({
                    "node": int(match.group(1)), "zone": match.group(2), "migrate_type": match.group(3),
                    "counts_by_order": {str(order): count for order, count in zip(orders, counts)},
                })
            elif section == "blocks":
                match = re.match(r"^Node\s+(\d+),\s*zone\s+(\S+)\s+(.*)$", stripped)
                if not match:
                    malformed = True
                    continue
                counts = [_int_or_none(value) for value in match.group(3).split()]
                if not block_types or len(counts) != len(block_types) or any(v is None or v < 0 for v in counts):
                    malformed = True
                    continue
                block_rows.append({
                    "node": int(match.group(1)), "zone": match.group(2),
                    "counts_by_type": {kind: count for kind, count in zip(block_types, counts)},
                })
    cma_rows = [row for row in free_rows if row["migrate_type"].upper() == "CMA"]
    complete = bool(
        text is not None and not truncated and not malformed and page_block_order is not None
        and pages_per_block is not None and orders and free_rows and block_types and block_rows and cma_rows
    )
    cma_pages = None
    if complete:
        cma_pages = sum(
            count * (1 << int(order))
            for row in cma_rows
            for order, count in row["counts_by_order"].items()
        )
    return {
        "status": "ok" if complete else "partial",
        "page_block_order": page_block_order,
        "pages_per_block": pages_per_block,
        "orders": orders,
        "free_pages_by_migrate_type": free_rows,
        "blocks_by_migrate_type": block_rows,
        "cma_free_pages_from_histogram": cma_pages,
    }


def parse_zoneinfo(text: str | None, truncated: bool = False):
    zones = []
    current = None
    malformed = False
    if text is not None:
        for line in text.splitlines():
            match = re.match(r"^\s*Node\s+(\d+),\s*zone\s+(\S+)\s*$", line)
            if match:
                if current is not None:
                    zones.append(current)
                current = {"node": int(match.group(1)), "zone": match.group(2), "values": {}}
                continue
            if current is None:
                continue
            fields = line.split()
            if len(fields) >= 2 and fields[0] == "pages" and fields[1] == "free":
                key, raw_value = "pages_free", fields[-1]
            elif len(fields) >= 2 and fields[0] in ZONEINFO_KEYS:
                key, raw_value = fields[0], fields[-1]
            elif len(fields) >= 3 and fields[0] == "nr_free_cma":
                key, raw_value = "nr_free_cma", fields[-1]
            else:
                continue
            value = _int_or_none(raw_value)
            if value is None or value < 0:
                malformed = True
                continue
            current["values"][key] = value
    if current is not None:
        zones.append(current)
    complete = bool(zones) and not malformed and not truncated and all(
        all(key in zone["values"] for key in ("pages_free", "min", "low", "high", "cma", "nr_free_cma"))
        for zone in zones if zone["zone"] == "DMA"
    )
    if not any(zone["zone"] == "DMA" for zone in zones):
        complete = False
    return {"status": "ok" if complete else "partial", "zones": zones}


def _parse_config(raw: bytes | None, capture: dict):
    if raw is None:
        return {"status": "unavailable", "capture": capture, "values": {key: None for key in CONFIG_KEYS}}
    if capture.get("truncated"):
        return {"status": "partial", "capture": capture, "values": {key: None for key in CONFIG_KEYS}}
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            text = stream.read(MAX_CONFIG_TEXT_BYTES + 1).decode("utf-8", "replace")
    except (OSError, EOFError):
        return {"status": "invalid", "capture": capture, "values": {key: None for key in CONFIG_KEYS}}
    if len(text.encode("utf-8")) > MAX_CONFIG_TEXT_BYTES:
        return {"status": "partial", "capture": capture, "values": {key: None for key in CONFIG_KEYS}}
    values: dict[str, str | None] = {key: None for key in CONFIG_KEYS}
    for line in text.splitlines():
        match = re.match(r"^#\s*(CONFIG_[A-Z0-9_]+)\s+is not set\s*$", line)
        if match and match.group(1) in values:
            values[match.group(1)] = "not_set"
            continue
        match = re.match(r"^(CONFIG_[A-Z0-9_]+)=(.*)$", line)
        if match and match.group(1) in values:
            values[match.group(1)] = match.group(2)
    return {"status": "ok" if all(value is not None for value in values.values()) else "partial",
            "capture": capture, "values": values}


def _parse_starttime(text: str):
    end = text.rindex(")")
    fields = text[end + 1:].split()
    if len(fields) <= 19:
        raise ValueError("short proc stat")
    return fields[0], int(fields[19])


def _display_target(link: str, root: Path):
    target = Path(link)
    try:
        relative = target.relative_to(root)
        return "/" + str(relative)
    except ValueError:
        return link


def _process_inventory(proc_root: Path, root: Path):
    mainui = []
    game_processes = []
    scanned = 0
    unreadable_exe_count = 0
    truncated = False
    runtime_path = root / "mnt/SDCARD/Roms/PORTS/lamentum-switch/lamentum-nextos"
    try:
        runtime = os.stat(runtime_path)
        target_runtime = {"status": "ok", "exe_dev": runtime.st_dev, "exe_ino": runtime.st_ino}
    except OSError:
        runtime = None
        target_runtime = {"status": "unavailable", "exe_dev": None, "exe_ino": None}
    try:
        entries = sorted((p for p in proc_root.iterdir() if p.name.isdigit()), key=lambda p: int(p.name))
    except OSError as exc:
        return {"status": "unavailable", "error": type(exc).__name__, "mainui": [], "game_processes": [],
                "target_runtime": target_runtime}
    for process in entries:
        scanned += 1
        if scanned > MAX_PROCESS_ENTRIES:
            truncated = True
            break
        try:
            comm = (process / "comm").read_text().strip()
        except OSError:
            continue
        if comm == "MainUI":
            is_mainui = True
        elif comm.startswith("["):
            continue
        else:
            is_mainui = False
        try:
            exe = os.stat(process / "exe")
        except OSError:
            if not is_mainui:
                try:
                    command_line = (process / "cmdline").read_bytes()
                except OSError:
                    unreadable_exe_count += 1
                else:
                    if command_line:
                        unreadable_exe_count += 1
            continue
        is_target = (runtime is not None and (exe.st_dev, exe.st_ino) == (runtime.st_dev, runtime.st_ino))
        if not is_mainui and not is_target:
            continue
        try:
            state, starttime = _parse_starttime((process / "stat").read_text())
        except (OSError, ValueError, IndexError):
            state, starttime = None, None
        item = {"pid": int(process.name), "comm": comm, "state": state, "starttime": starttime,
                "exe_dev": exe.st_dev, "exe_ino": exe.st_ino}
        if is_mainui:
            dma_fds = []
            fds_truncated = False
            fd_dir = process / "fd"
            try:
                fds = sorted(fd_dir.iterdir(), key=lambda p: int(p.name) if p.name.isdigit() else MAX_PROCESS_FDS)
            except OSError:
                fds = []
                item["fd_status"] = "unavailable"
            for index, fd in enumerate(fds):
                if index >= MAX_PROCESS_FDS:
                    fds_truncated = True
                    break
                try:
                    target = _display_target(os.readlink(fd), root)
                    if not any(token in target.lower() for token in ("dma_heap", "dma_buf", "dmabuf", "/dev/dri/")):
                        continue
                    stat = os.stat(fd)
                    dma_fds.append({"fd": int(fd.name) if fd.name.isdigit() else None,
                                    "target": target, "dev": stat.st_dev, "ino": stat.st_ino})
                except (OSError, ValueError):
                    continue
            item["dma_fds"] = dma_fds
            item["fd_scan_truncated"] = fds_truncated
            mainui.append(item)
        else:
            game_processes.append(item)
    status = "ok" if runtime is not None and not truncated and unreadable_exe_count == 0 else "partial"
    return {"status": status, "scanned_processes": min(scanned, MAX_PROCESS_ENTRIES),
            "unreadable_exe_count": unreadable_exe_count, "truncated": truncated,
            "target_runtime": target_runtime, "mainui": mainui, "game_processes": game_processes}


def _dmabuf_inventory(sys_root: Path):
    candidates = (sys_root / "kernel/dmabuf/buffers", sys_root / "kernel/dma_buf/buffers")
    selected = next((path for path in candidates if path.is_dir()), None)
    if selected is None:
        return {"status": "unavailable", "entries": []}
    entries = []
    truncated = False
    incomplete = False
    try:
        children = sorted(selected.iterdir(), key=lambda path: path.name)
    except OSError as exc:
        return {"status": "unavailable", "error": type(exc).__name__, "entries": []}
    for index, child in enumerate(children):
        if index >= MAX_DMABUF_ENTRIES:
            truncated = True
            break
        if not child.is_dir():
            continue
        inode = _int_or_none(child.name)
        size_bytes = None
        exporter = None
        try:
            size_bytes = _int_or_none((child / "size").read_text().strip())
        except OSError:
            pass
        for filename in ("exporter_name", "name"):
            try:
                exporter = (child / filename).read_text().strip()
                break
            except OSError:
                continue
        if inode is None or size_bytes is None or exporter is None:
            incomplete = True
        entries.append({"inode": inode, "size_bytes": size_bytes, "exporter": exporter})
    status = "partial" if truncated or incomplete else "ok"
    return {"status": status, "path": str(selected), "truncated": truncated, "entries": entries}


def _config_and_tracepoints(proc_root: Path, sys_root: Path):
    raw, capture = _read_bounded(proc_root / "config.gz", MAX_CONFIG_RAW_BYTES)
    config = _parse_config(raw, capture)
    trace_roots = (sys_root / "kernel/tracing/events", sys_root / "kernel/debug/tracing/events")
    trace_root = next((path for path in trace_roots if path.is_dir()), None)
    if trace_root is None:
        tracepoints = {"status": "unavailable", "groups": {"cma": None, "compaction": None, "kmem": None}}
    else:
        tracepoints = {"status": "ok", "path": str(trace_root),
                       "groups": {key: (trace_root / key).is_dir() for key in ("cma", "compaction", "kmem")}}
    return config, tracepoints


def collect_snapshot(root="/"):
    """Capture bounded read-only K1 state rooted at ``root`` (``/`` on the target)."""
    root = Path(root)
    proc_root, sys_root = root / "proc", root / "sys"
    start = time.monotonic_ns()
    wall_time_ns = time.time_ns()

    def text(path, limit=MAX_PROC_TEXT_BYTES):
        return _text_capture(path, limit)

    def identity_value(path, limit=8192):
        value, capture = text(path, limit)
        return (value.strip() if value is not None else None), capture

    boot_id, boot_capture = identity_value(proc_root / "sys/kernel/random/boot_id")
    kernel_release, release_capture = identity_value(proc_root / "sys/kernel/osrelease")
    kernel_version, version_capture = identity_value(proc_root / "version")
    firmware_version, firmware_capture = identity_value(root / "etc/version")

    mem_text, mem_capture = text(proc_root / "meminfo")
    meminfo = parse_meminfo(mem_text, mem_capture.get("truncated", False))
    meminfo["capture"] = mem_capture
    vm_text, vm_capture = text(proc_root / "vmstat")
    vmstat = parse_vmstat(vm_text, vm_capture.get("truncated", False))
    vmstat["capture"] = vm_capture

    allocator_specs = (
        ("buddyinfo", parse_buddyinfo), ("pagetypeinfo", parse_pagetypeinfo), ("zoneinfo", parse_zoneinfo),
    )
    allocators = {}
    for name, parser in allocator_specs:
        raw_text, capture = text(proc_root / name)
        result = parser(raw_text, capture.get("truncated", False))
        result["capture"] = capture
        allocators[name] = result

    cmdline_text, cmdline_capture = text(proc_root / "cmdline", 8192)
    selected_tokens: list[str] = []
    if cmdline_text is not None:
        for token in cmdline_text.split():
            key = token.split("=", 1)[0].lower()
            if key in INTERESTING_CMDLINE_KEYS:
                selected_tokens.append(token)
    cmdline = {"capture": cmdline_capture, "selected_tokens": selected_tokens}

    config, tracepoints = _config_and_tracepoints(proc_root, sys_root)
    compatible: list[str] | None = None
    compatible_capture = {"status": "unavailable", "truncated": False}
    for path in (sys_root / "firmware/devicetree/base/compatible", proc_root / "device-tree/compatible"):
        raw, compatible_capture = _read_bounded(path, 4096)
        if raw is not None:
            compatible = [part.decode("utf-8", "replace") for part in raw.split(b"\0") if part]
            break
    device_tree = {"status": "ok" if compatible is not None and not compatible_capture.get("truncated") else "unavailable",
                   "capture": compatible_capture, "compatible": compatible}

    module_path = root / "lib/modules" / (kernel_release or "__unknown_kernel_release__")
    modules = {"status": "ok" if module_path.is_dir() else "unavailable",
               "release": kernel_release, "directory_present": module_path.is_dir(),
               "markers": {name: (module_path / name).is_file()
                           for name in ("modules.dep", "modules.alias", "modules.builtin")}}

    processes = _process_inventory(proc_root, root)
    dma_buf = _dmabuf_inventory(sys_root)
    mainui_rows = processes.get("mainui")
    mainui_complete = (
        processes.get("status") == "ok"
        and processes.get("target_runtime", {}).get("status") == "ok"
        and isinstance(mainui_rows, list) and len(mainui_rows) == 1
        and all(type(mainui_rows[0].get(key)) is int for key in ("pid", "starttime", "exe_dev", "exe_ino"))
        and mainui_rows[0].get("fd_scan_truncated") is False
        and mainui_rows[0].get("fd_status") is None
        and isinstance(mainui_rows[0].get("dma_fds"), list)
    )
    required = (
        boot_id is not None, kernel_release is not None,
        meminfo["status"] == "ok", vmstat["status"] == "ok",
        all(allocators[key]["status"] == "ok" for key in ("buddyinfo", "pagetypeinfo", "zoneinfo")),
        mainui_complete,
    )
    sample_status = "complete" if all(required) else "partial"
    ended = time.monotonic_ns()
    return {
        "schema_version": SCHEMA_VERSION,
        "sample_status": sample_status,
        "timestamps": {"wall_time_ns": wall_time_ns, "monotonic_ns": start, "duration_ns": ended - start},
        "identity": {"boot_id": boot_id, "kernel_release": kernel_release,
                     "kernel_version": kernel_version, "firmware_version": firmware_version,
                     "captures": {"boot_id": boot_capture, "kernel_release": release_capture,
                                  "kernel_version": version_capture, "firmware_version": firmware_capture}},
        "system": {"meminfo": meminfo, "vmstat": vmstat},
        "allocators": allocators,
        "config": config,
        "tracepoints": tracepoints,
        "command_line": cmdline,
        "device_tree": device_tree,
        "modules": modules,
        "dma_buf": dma_buf,
        "processes": processes,
        "interpretation_limits": [
            "CMA and buddy histograms are separately read and are not an atomic allocator snapshot.",
            "Free MIGRATE_CMA blocks do not prove that a particular GFP/order request will succeed.",
            "DMA-BUF exporter names and sizes do not prove CMA backing or physical Mali residency.",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default="/", help="read-only fixture/device filesystem root (default: /)")
    args = parser.parse_args(argv)
    print(json.dumps(collect_snapshot(args.root), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
