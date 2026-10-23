#!/usr/bin/env python3
"""Classify a live kernel against an extracted firmware-vmlinux receipt.

Input is JSON with ``device`` and ``firmware`` records. The report deliberately
omits absolute kernel symbol addresses; keep raw kallsyms receipts local.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from contextlib import nullcontext
from pathlib import Path
from typing import Any


def _address(value: Any) -> int | None:
    if isinstance(value, int) and value >= 0:
        return value
    if isinstance(value, str):
        try:
            return int(value, 16)
        except ValueError:
            return None
    return None


def _hex_delta(value: int) -> str:
    return ("-" if value < 0 else "") + hex(abs(value))


def _same_version(left: Any, right: Any) -> bool:
    return bool(left) and left == right


def classify_kernel_match(device: dict, firmware: dict) -> dict[str, Any]:
    """Return a compact match assessment from two pinned metadata receipts."""
    device = device if isinstance(device, dict) else {}
    firmware = firmware if isinstance(firmware, dict) else {}
    raw_vmlinux = firmware.get("vmlinux")
    vmlinux: dict[str, Any] = raw_vmlinux if isinstance(raw_vmlinux, dict) else {}

    firmware_version_match = _same_version(device.get("firmware_version"), firmware.get("firmware_version"))
    release_match = _same_version(device.get("kernel_release"), firmware.get("kernel_release"))
    banner_match = _same_version(device.get("kernel_banner"), firmware.get("kernel_banner"))

    raw_asset = firmware.get("asset")
    asset: dict[str, Any] = raw_asset if isinstance(raw_asset, dict) else {}
    asset_sha = asset.get("sha256")
    asset_sha256_verified = (asset.get("sha256_verified") is True and isinstance(asset_sha, str)
                             and re.fullmatch(r"[0-9a-f]{64}", asset_sha) is not None)
    vmlinux_sha = vmlinux.get("sha256")
    build_id = vmlinux.get("build_id")
    vmlinux_metadata_valid = (
        isinstance(vmlinux_sha, str) and re.fullmatch(r"[0-9a-f]{64}", vmlinux_sha) is not None
        and isinstance(build_id, str) and re.fullmatch(r"[0-9a-f]{40}", build_id) is not None
        and vmlinux.get("architecture") == "aarch64"
    )

    raw_live_symbols = device.get("kallsyms")
    live_symbols: dict[str, Any] = raw_live_symbols if isinstance(raw_live_symbols, dict) else {}
    raw_image_symbols = vmlinux.get("symbols")
    image_symbols: dict[str, Any] = raw_image_symbols if isinstance(raw_image_symbols, dict) else {}
    relocation_deltas = {}
    for name in sorted(set(live_symbols) & set(image_symbols)):
        live_address = _address(live_symbols.get(name))
        image_info = image_symbols.get(name)
        image_address = _address(image_info.get("address")) if isinstance(image_info, dict) else None
        if live_address is not None and live_address > 0 and image_address is not None and image_address > 0:
            relocation_deltas[name] = live_address - image_address
    unique_deltas = set(relocation_deltas.values())
    relocation_consistent = len(relocation_deltas) >= 3 and len(unique_deltas) == 1
    relocation_delta = next(iter(unique_deltas)) if relocation_consistent else None

    raw_stack_frames = device.get("warning_stack_frames")
    stack_frames: dict[str, Any] = raw_stack_frames if isinstance(raw_stack_frames, dict) else {}
    extent_checks = []
    for name, frame in stack_frames.items():
        image_info = image_symbols.get(name)
        if not isinstance(frame, dict) or not isinstance(image_info, dict):
            continue
        frame_extent = _address(frame.get("extent"))
        expected_extent = _address(image_info.get("next_symbol_delta"))
        if expected_extent is None:
            expected_extent = _address(image_info.get("st_size"))
        if frame_extent is not None and expected_extent is not None:
            extent_checks.append(frame_extent == expected_extent)
    extent_match = bool(extent_checks) and all(extent_checks)

    raw_image_return = vmlinux.get("warning_return")
    image_return: dict[str, Any] = raw_image_return if isinstance(raw_image_return, dict) else {}
    return_symbol = image_return.get("symbol")
    device_return_frame = stack_frames.get(return_symbol, {}) if isinstance(return_symbol, str) else {}
    image_offset = _address(image_return.get("offset"))
    device_offset = _address(device_return_frame.get("offset")) if isinstance(device_return_frame, dict) else None
    warning_return_match = image_offset is not None and device_offset is not None and image_offset == device_offset

    exact = all((asset_sha256_verified, vmlinux_metadata_valid,
                 firmware_version_match, release_match, banner_match,
                 relocation_consistent, extent_match, warning_return_match))
    if exact:
        match_class = "exact"
    elif release_match and (firmware_version_match or banner_match):
        match_class = "analogue"
    else:
        match_class = "unknown"

    orders = vmlinux.get("orders")
    if not isinstance(orders, list) or any(type(order) is not int or order < 0 for order in orders):
        orders = None
    retry_on_null = vmlinux.get("null_return_retries")
    if type(retry_on_null) is not bool:
        retry_on_null = None
    if orders is not None and retry_on_null is True:
        retry_possible = len(orders) > 1
    else:
        retry_possible = None

    device_vmlinux_hash = device.get("vmlinux_sha256")
    firmware_vmlinux_hash = vmlinux.get("sha256")
    whole_kernel_hash_match = None
    if isinstance(device_vmlinux_hash, str) and isinstance(firmware_vmlinux_hash, str):
        whole_kernel_hash_match = device_vmlinux_hash == firmware_vmlinux_hash

    return {
        "schema_version": 1,
        "match_class": match_class,
        "firmware_version_match": firmware_version_match,
        "kernel_release_match": release_match,
        "banner_match": banner_match,
        "asset_sha256_verified": asset_sha256_verified,
        "vmlinux_metadata_valid": vmlinux_metadata_valid,
        "symbols_matched": len(relocation_deltas),
        "kaslr_relocation_consistent": relocation_consistent,
        "relocation_delta": _hex_delta(relocation_delta) if relocation_delta is not None else None,
        "symbol_extents_match": extent_match if extent_checks else None,
        "warning_return_match": warning_return_match if image_offset is not None and device_offset is not None else None,
        "vmlinux_build_id": build_id,
        "vmlinux_sha256": firmware_vmlinux_hash,
        "whole_kernel_hash_match": whole_kernel_hash_match,
        "source_tree_available": firmware.get("source_tree_available"),
        "source_path": vmlinux.get("source_path"),
        "warning_semantics": {
            "orders": orders,
            "null_return_retries": retry_on_null,
            "intermediate_order_warning_possible": retry_possible,
            "request_completion": "unknown",
        },
        "limits": [
            "Exact firmware-build evidence is not a whole-image cryptographic match unless the live kernel image is hashed.",
            "A page-allocation warning at one order does not establish the enclosing DMA-heap request result.",
            "Source path in DWARF identifies a build input location, not an available source tree.",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default="-", help="JSON receipt with device/firmware objects, or stdin")
    args = parser.parse_args(argv)
    try:
        source_context = nullcontext(sys.stdin) if args.input == "-" else Path(args.input).open()
        with source_context as source:
            record = json.load(source)
        report = classify_kernel_match(record.get("device", {}), record.get("firmware", {}))
    except (OSError, json.JSONDecodeError, AttributeError) as exc:
        parser.error(f"cannot read source-match receipt: {type(exc).__name__}")
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
