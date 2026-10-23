#!/usr/bin/env python3
"""Host-only replay of build259 storage-admission evidence and typed alternatives.

This tool reads a sanitized margin-sweep summary and optional local raw owned-log
receipts. It never talks to a device or changes the production admission policy.
Raw runtime logs are intentionally not copied into the result.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from load_metrics import collect_log
from run_identity import validate_uuid

U64_MAX = (1 << 64) - 1
MIB = 1 << 20
KIB = 1 << 10
MAX_SOURCE_LOG_BYTES = 2 * 1024 * 1024
EXPECTED_REQUESTS = (
    (64, 61, 0, 5_400_000),
    (48, 77, 0, 10_368_000),
    (32, 0, 512_000, 0),
    (24, 0, 8_294_400, 0),
)
REQUEST_KINDS = frozenset({
    "cpu_malloc", "gl_tex", "gl_rb", "gl_buffer", "dma_heap", "egl_swapchain", "unknown",
})
KERNEL_CONFIDENCE = frozenset({"exact_firmware_build", "analogue", "unknown"})


def _require_u64(value: Any, name: str) -> int:
    if type(value) is not int or value < 0 or value > U64_MAX:
        raise ValueError(f"{name} must be a non-negative uint64")
    return value


def _u64(value: Any, name: str, *, optional: bool = False) -> int | None:
    if value is None and optional:
        return None
    return _require_u64(value, name)


def checked_add_u64(*values: int) -> int:
    total = 0
    for value in values:
        value = _require_u64(value, "addend")
        if value > U64_MAX - total:
            raise OverflowError("uint64 addition overflow")
        total += value
    return total


def checked_mul_u64(left: int, right: int) -> int:
    left = _require_u64(left, "left operand")
    right = _require_u64(right, "right operand")
    if left and right > U64_MAX // left:
        raise OverflowError("uint64 multiplication overflow")
    return left * right


def _mib_bytes(value: int) -> int:
    return checked_mul_u64(_require_u64(value, "MiB value"), MIB)


def _kib_bytes(value: int) -> int:
    return checked_mul_u64(_require_u64(value, "KiB value"), KIB)


@dataclass(frozen=True)
class AdmissionRequest:
    """Typed request; unknown physical backing stays null, never inferred as zero."""

    run_uuid: str
    owner: int | None
    storage_id: int | None
    storage_generation: int | None
    request_kind: str
    requested_bytes: int | None
    gl_bytes: int | None
    scratch_bytes: int | None
    peak_overlapping_cpu_bytes: int | None
    proven_cma_bytes: int | None
    kernel_source_confidence: str
    sample_time_ns: int | None
    timestamp_source: str | None
    phase: str
    cma_provenance: str
    available_kib: int | None
    cma_free_kib: int | None
    floor_mib: int | None
    margin_mib: int | None
    synthetic: bool

    def __post_init__(self):
        validate_uuid(self.run_uuid)
        if type(self.synthetic) is not bool:
            raise ValueError("synthetic must be an explicit boolean")
        if self.request_kind not in REQUEST_KINDS:
            raise ValueError("unsupported request_kind")
        if self.kernel_source_confidence not in KERNEL_CONFIDENCE:
            raise ValueError("unsupported kernel_source_confidence")
        for name in ("owner", "storage_id", "storage_generation", "requested_bytes", "gl_bytes",
                     "scratch_bytes", "peak_overlapping_cpu_bytes", "proven_cma_bytes", "sample_time_ns",
                     "available_kib", "cma_free_kib", "floor_mib", "margin_mib"):
            _u64(getattr(self, name), name, optional=True)
        if self.requested_bytes is not None and self.gl_bytes is not None and self.scratch_bytes is not None:
            if self.requested_bytes != checked_add_u64(self.gl_bytes, self.scratch_bytes):
                raise ValueError("requested_bytes must preserve GL plus scratch components")
        if not isinstance(self.phase, str) or not self.phase:
            raise ValueError("phase must be explicit; use 'unknown' when unavailable")
        if not isinstance(self.cma_provenance, str) or not self.cma_provenance:
            raise ValueError("cma_provenance must be explicit; use 'unattributed' when unknown")
        if self.sample_time_ns is None:
            if self.timestamp_source is not None:
                raise ValueError("timestamp_source without sample_time_ns is not allowed")
            if not self.synthetic:
                raise ValueError("observed requests require a source-backed monotonic timestamp")
        elif self.synthetic:
            if self.timestamp_source != "synthetic_fixture":
                raise ValueError("synthetic timestamps must be explicitly labeled synthetic_fixture")
        elif self.timestamp_source != "target_clock_monotonic":
            raise ValueError("observed timestamp must come from target CLOCK_MONOTONIC")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _missing_policy_input(request: AdmissionRequest, fields: tuple[str, ...]):
    return [name for name in fields if getattr(request, name) is None]


def evaluate_all_bytes_maybe_cma(request: AdmissionRequest) -> dict[str, Any]:
    """Reproduce the deployed conservative C formula; this is not safety approval."""
    base = {"model": "all_bytes_maybe_CMA", "synthetic": request.synthetic,
            "qualification": "unknown", "requested_bytes": request.requested_bytes,
            "required_available_bytes": None, "required_cma_bytes": None}
    if request.margin_mib is None:
        return {**base, "would_admit": False, "reason": "policy-unset", "missing": ["margin_mib"]}
    margin_mib = _require_u64(request.margin_mib, "margin_mib")
    if margin_mib == 0 or margin_mib > 4096:
        return {**base, "would_admit": False, "reason": "policy-invalid", "missing": []}
    if request.floor_mib == 0:
        return {**base, "would_admit": False, "reason": "floor-disabled", "missing": []}
    missing = _missing_policy_input(request, (
        "gl_bytes", "scratch_bytes", "available_kib", "cma_free_kib", "floor_mib",
    ))
    if missing:
        reason = "request-basis-unknown" if any(key in missing for key in ("gl_bytes", "scratch_bytes")) else "meminfo-unavailable"
        return {**base, "would_admit": False, "reason": reason, "missing": missing}
    gl_bytes = _require_u64(request.gl_bytes, "gl_bytes")
    scratch_bytes = _require_u64(request.scratch_bytes, "scratch_bytes")
    available_kib = _require_u64(request.available_kib, "available_kib")
    cma_free_kib = _require_u64(request.cma_free_kib, "cma_free_kib")
    floor_mib = _require_u64(request.floor_mib, "floor_mib")
    margin_mib = _require_u64(request.margin_mib, "margin_mib")
    try:
        margin_bytes = _mib_bytes(margin_mib)
        floor_bytes = _mib_bytes(floor_mib)
        requested_bytes = checked_add_u64(gl_bytes, scratch_bytes)
        required_cma = checked_add_u64(requested_bytes, margin_bytes)
        required_available = checked_add_u64(floor_bytes, required_cma)
        available_bytes = _kib_bytes(available_kib)
        cma_free_bytes = _kib_bytes(cma_free_kib)
    except (ValueError, OverflowError):
        return {**base, "would_admit": False, "reason": "size-overflow", "missing": []}
    mem_low = available_bytes < required_available
    cma_low = cma_free_bytes < required_cma
    reason = ("memavailable-and-cmafree" if mem_low and cma_low else
              "memavailable-floor" if mem_low else "cmafree-margin" if cma_low else "allow")
    return {
        **base,
        "would_admit": not (mem_low or cma_low),
        "reason": reason,
        "qualification": "synthetic_counterfactual" if request.synthetic else "formula_replay_only",
        "required_available_bytes": required_available,
        "required_cma_bytes": required_cma,
        "available_bytes": available_bytes,
        "cma_free_bytes": cma_free_bytes,
    }


def _unqualified_model(name: str, reason: str, missing_fields: tuple[str, ...] = ()):
    return {"model": name, "would_admit": False, "reason": reason, "qualification": "unknown",
            "synthetic": True, "missing_fields": list(missing_fields),
            "required_available_bytes": None, "required_cma_bytes": None}


def evaluate_proven_cma_only(request: AdmissionRequest, *, cma_uncertainty_margin_bytes: int | None):
    """Use only proven CMA bytes; unknown backing is a fail-closed denial, not zero."""
    missing = [name for name, value in (
        ("proven_cma_bytes", request.proven_cma_bytes),
        ("peak_overlapping_cpu_bytes", request.peak_overlapping_cpu_bytes),
        ("cma_uncertainty_margin_bytes", cma_uncertainty_margin_bytes),
        ("available_kib", request.available_kib), ("cma_free_kib", request.cma_free_kib),
        ("floor_mib", request.floor_mib)) if value is None]
    if missing:
        return _unqualified_model("proven_CMA_only", "unknown-required-basis", tuple(missing))
    cpu_peak_bytes = _require_u64(request.peak_overlapping_cpu_bytes, "peak_overlapping_cpu_bytes")
    proven_cma_bytes = _require_u64(request.proven_cma_bytes, "proven_cma_bytes")
    cma_margin_bytes = _require_u64(cma_uncertainty_margin_bytes, "CMA uncertainty margin")
    available_kib = _require_u64(request.available_kib, "available_kib")
    cma_free_kib = _require_u64(request.cma_free_kib, "cma_free_kib")
    floor_mib = _require_u64(request.floor_mib, "floor_mib")
    try:
        required_available = checked_add_u64(_mib_bytes(floor_mib), cpu_peak_bytes)
        required_cma = checked_add_u64(proven_cma_bytes, cma_margin_bytes)
        available_bytes = _kib_bytes(available_kib)
        cma_free_bytes = _kib_bytes(cma_free_kib)
    except (ValueError, OverflowError):
        return _unqualified_model("proven_CMA_only", "size-overflow")
    admitted = available_bytes >= required_available and cma_free_bytes >= required_cma
    return {"model": "proven_CMA_only", "would_admit": admitted,
            "reason": "allow" if admitted else "ledger-headroom-insufficient",
            "qualification": "synthetic_only" if request.synthetic else "policy_model_not_safety_qualified",
            "synthetic": True, "required_available_bytes": required_available,
            "required_cma_bytes": required_cma}


def evaluate_mixed_two_ledger(request: AdmissionRequest, *, driver_uncertainty_margin_bytes: int | None):
    """Separate CPU peak from proven-CMA bytes; require an explicit driver margin."""
    missing = [name for name, value in (
        ("peak_overlapping_cpu_bytes", request.peak_overlapping_cpu_bytes),
        ("proven_cma_bytes", request.proven_cma_bytes),
        ("driver_uncertainty_margin_bytes", driver_uncertainty_margin_bytes),
        ("available_kib", request.available_kib), ("cma_free_kib", request.cma_free_kib),
        ("floor_mib", request.floor_mib)) if value is None]
    if missing:
        return _unqualified_model("mixed_two_ledger", "unknown-required-basis", tuple(missing))
    cpu_peak_bytes = _require_u64(request.peak_overlapping_cpu_bytes, "peak_overlapping_cpu_bytes")
    proven_cma_bytes = _require_u64(request.proven_cma_bytes, "proven_cma_bytes")
    driver_margin_bytes = _require_u64(driver_uncertainty_margin_bytes, "driver uncertainty margin")
    available_kib = _require_u64(request.available_kib, "available_kib")
    cma_free_kib = _require_u64(request.cma_free_kib, "cma_free_kib")
    floor_mib = _require_u64(request.floor_mib, "floor_mib")
    try:
        required_available = checked_add_u64(_mib_bytes(floor_mib), cpu_peak_bytes)
        required_cma = checked_add_u64(proven_cma_bytes, driver_margin_bytes)
        available_bytes = _kib_bytes(available_kib)
        cma_free_bytes = _kib_bytes(cma_free_kib)
    except (ValueError, OverflowError):
        return _unqualified_model("mixed_two_ledger", "size-overflow")
    admitted = available_bytes >= required_available and cma_free_bytes >= required_cma
    return {"model": "mixed_two_ledger", "would_admit": admitted,
            "reason": "allow" if admitted else "ledger-headroom-insufficient",
            "qualification": "synthetic_only" if request.synthetic else "policy_model_not_safety_qualified",
            "synthetic": True, "required_available_bytes": required_available,
            "required_cma_bytes": required_cma}


def _load_json(path: Path, description: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {description}: {type(exc).__name__}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{description} must be a JSON object")
    return value


def _fields(line: str, record_name: str) -> dict[str, str]:
    if not line.startswith(record_name + " "):
        raise ValueError(f"not a {record_name} record")
    values: dict[str, str] = {}
    for token in line.split()[1:]:
        if "=" not in token:
            raise ValueError(f"malformed {record_name} token")
        key, value = token.split("=", 1)
        if not key or key in values:
            raise ValueError(f"duplicate or empty {record_name} key")
        values[key] = value
    return values


def _decimal(fields: dict[str, str], name: str, *, max_value: int = U64_MAX) -> int:
    raw = fields.get(name)
    if raw is None or not re.fullmatch(r"\d+", raw):
        raise ValueError(f"missing or invalid {name}")
    value = int(raw, 10)
    if value > max_value:
        raise ValueError(f"{name} exceeds its allowed range")
    return value


def _check_summary_match(event: dict[str, str], arm: dict[str, Any], common: dict[str, Any]):
    expected = {
        "run_uuid": arm.get("run_uuid"),
        "margin_mib": arm.get("margin_mib"),
        "owner": arm.get("owner"),
        "gl_bytes": arm.get("request_gl_bytes"),
        "scratch_bytes": arm.get("request_scratch_bytes"),
        "available_kib": arm.get("available_at_refusal_kib"),
        "cma_free_kib": arm.get("cmafree_at_refusal_kib"),
        "required_cma_bytes": arm.get("required_cma_bytes"),
        "decision": arm.get("decision"),
        "reason": arm.get("reason"),
    }
    actual = {
        "run_uuid": event.get("run-id"),
        "margin_mib": _decimal(event, "margin-mib"),
        "owner": _decimal(event, "owner"),
        "gl_bytes": _decimal(event, "gl-bytes"),
        "scratch_bytes": _decimal(event, "scratch-bytes"),
        "available_kib": _decimal(event, "available-kib"),
        "cma_free_kib": _decimal(event, "cmafree-kib"),
        "required_cma_bytes": _decimal(event, "required-cma-bytes"),
        "decision": event.get("decision"),
        "reason": event.get("reason"),
    }
    for key, value in expected.items():
        if actual[key] != value:
            raise ValueError(f"summary/raw admission mismatch: {key}")
    if event.get("floor-mib") != str(common.get("floor_mib")):
        raise ValueError("summary/raw admission mismatch: floor_mib")
    for key in ("margin-known", "sample-known", "cma-known", "requirements-known"):
        if event.get(key) != "1":
            raise ValueError(f"admission event lacks known {key} evidence")
    if event.get("decision") != "deny" or event.get("reason") != "cmafree-margin":
        raise ValueError("expected a source-backed cmafree-margin refusal")
    request_total = checked_add_u64(actual["gl_bytes"], actual["scratch_bytes"])
    required_cma = checked_add_u64(request_total, _mib_bytes(actual["margin_mib"]))
    required_available = checked_add_u64(_mib_bytes(int(common["floor_mib"])), required_cma)
    if _decimal(event, "required-cma-bytes") != required_cma:
        raise ValueError("raw required-cma-bytes does not match the source formula")
    if _decimal(event, "required-available-bytes") != required_available:
        raise ValueError("raw required-available-bytes does not match the source formula")
    if _kib_bytes(actual["available_kib"]) < required_available:
        raise ValueError("recorded denial also fails the MemAvailable floor")
    if _kib_bytes(actual["cma_free_kib"]) >= required_cma:
        raise ValueError("recorded cmafree-margin denial does not fail CMA check")
    return actual


def load_observed_arm(summary: dict[str, Any], arm: dict[str, Any], raw_dir: Path, *,
                      kernel_source_confidence: str = "unknown", source_is_synthetic: bool = False):
    """Validate one owned raw log and bind its real admission event to the summary."""
    if kernel_source_confidence not in KERNEL_CONFIDENCE:
        raise ValueError("unsupported kernel source confidence")
    margin = arm.get("margin_mib")
    if type(margin) is not int:
        raise ValueError("arm has no valid margin_mib")
    expected_run_file = _load_json(raw_dir / "expected-run.json", "expected-run receipt")
    owned = _load_json(raw_dir / "owned-log-final.json", "owned-log-final receipt")
    log_path = raw_dir / "latest.log"
    if owned.get("status") != "ok" or owned.get("log_identity_qualified") is not True:
        raise ValueError("log_truncated: owned log identity is not qualified")
    for key in ("offset", "size", "partial_bytes", "unconsumed_bytes"):
        if type(owned.get(key)) is not int:
            raise ValueError(f"log_truncated: missing {key}")
    if owned["offset"] != owned["size"] or owned["partial_bytes"] or owned["unconsumed_bytes"]:
        raise ValueError("log_truncated: owned log cursor is incomplete")
    if not isinstance(owned.get("expected_run"), dict) or not isinstance(owned.get("run_header"), dict):
        raise ValueError("owned log is missing run identity")
    expected_run = owned["expected_run"]
    for key, value in expected_run_file.items():
        if expected_run.get(key) != value:
            raise ValueError(f"run identity mismatch: expected-run {key}")
    if expected_run.get("run_uuid") != arm.get("run_uuid"):
        raise ValueError("run identity mismatch: arm UUID")
    if expected_run.get("boot_id") != summary.get("device", {}).get("boot_id"):
        raise ValueError("run identity mismatch: boot ID")
    if expected_run.get("elf_sha256") != summary.get("binary", {}).get("sha256"):
        raise ValueError("run identity mismatch: runtime SHA")
    try:
        size_before = log_path.stat().st_size
        if size_before > MAX_SOURCE_LOG_BYTES:
            raise ValueError("source log exceeds bounded read limit")
        local_bytes = log_path.read_bytes()
        size_after = log_path.stat().st_size
    except OSError as exc:
        raise ValueError(f"cannot read raw log: {type(exc).__name__}") from exc
    if size_after != size_before or len(local_bytes) != size_before:
        raise ValueError("raw log changed during bounded read")
    try:
        captured = collect_log(log_path, offset=0, expected_run=expected_run,
                               expected_header=owned.get("header_sha256"),
                               max_bytes=MAX_SOURCE_LOG_BYTES, include_text=True)
    except (OSError, ValueError) as exc:
        raise ValueError(f"owned log validation failed: {type(exc).__name__}") from exc
    if (captured.get("status") != "ok" or captured.get("log_identity_qualified") is not True
            or captured.get("partial_bytes") != 0 or captured.get("unconsumed_bytes") != 0
            or captured.get("offset") != owned["size"] or captured.get("size") != owned["size"]):
        raise ValueError("log_truncated: raw owned log is incomplete or changed")
    if (captured.get("header_sha256") != owned.get("header_sha256")
            or captured.get("run_header") != owned.get("run_header")
            or captured.get("anchor") != owned.get("anchor")):
        raise ValueError("log generation or final anchor changed")
    text = captured.get("chunk_text")
    if not isinstance(text, str) or not text.endswith("\n"):
        raise ValueError("log_truncated: complete newline-terminated log required")
    try:
        parsed_bytes = text.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError("raw log capture is not byte-preserving UTF-8") from exc
    if parsed_bytes != local_bytes:
        raise ValueError("raw log bytes differ from parsed capture")
    lines = text.splitlines()
    event_rows = [(index, line) for index, line in enumerate(lines)
                  if line.startswith("T2_STORAGE_ADMISSION ")]
    if len(event_rows) != 1:
        raise ValueError("missing or duplicate admission event")
    event_index, event_line = event_rows[0]
    event = _fields(event_line, "T2_STORAGE_ADMISSION")
    if event.get("run-id") != arm.get("run_uuid"):
        raise ValueError("admission event run UUID mismatch")
    event_time = _decimal(event, "t-ns")
    if event_time == 0:
        raise ValueError("fabricated or unavailable target monotonic timestamp")
    summary_rows = [(index, line) for index, line in enumerate(lines)
                    if line.startswith("T2_STORAGE_ADMISSION_SUMMARY ")]
    stop_rows = [(index, line) for index, line in enumerate(lines)
                 if line.startswith("STOP status=T2_STORAGE_ADMISSION ")]
    if len(summary_rows) != 1 or summary_rows[0][0] <= event_index:
        raise ValueError("missing admission summary or incorrect event order")
    if len(stop_rows) != 1 or stop_rows[0][0] <= event_index:
        raise ValueError("missing admission stop or incorrect event order")
    summary_fields = _fields(summary_rows[0][1], "T2_STORAGE_ADMISSION_SUMMARY")
    if summary_fields.get("run-id") != arm.get("run_uuid"):
        raise ValueError("admission summary run UUID mismatch")
    for log_key, summary_key in (("checks", "checks"), ("allowed", "allowed"),
                                 ("refused", "refused"), ("margin-mib", "margin_mib")):
        if _decimal(summary_fields, log_key) != arm.get(summary_key):
            raise ValueError(f"admission summary mismatch: {log_key}")
    storage_event_indexes = [index for index, line in enumerate(lines)
                             if line.startswith("LC2_GL_STORAGE_EVENT ")]
    before_count = sum(index < event_index for index in storage_event_indexes)
    after_count = sum(index > event_index for index in storage_event_indexes)
    if before_count != arm.get("storage_events_before_denial") or after_count != arm.get("storage_events_after_denial"):
        raise ValueError("GL storage event counts do not match the source summary")
    actual = _check_summary_match(event, arm, summary.get("common_run_config", {}))
    cpu_peak_context = None
    request_kind = "unknown"
    peak_cpu_bytes = None
    phase = "unknown"
    stage_rows = []
    for index, line in enumerate(lines[:event_index]):
        if line.startswith("LC2_BC_FULL_STAGE "):
            stage = _fields(line, "LC2_BC_FULL_STAGE")
            if stage.get("id") == str(actual["owner"]):
                stage_rows.append((index, stage))
    if len(stage_rows) == 1:
        stage_index, stage = stage_rows[0]
        raw_peak = stage.get("known-cpu-scratch-peak-bytes")
        if raw_peak is not None and raw_peak.isdecimal():
            stage_peak = int(raw_peak, 10)
            if (actual["gl_bytes"] == 0 and stage_peak == actual["scratch_bytes"]
                    and stage.get("staging-mode") == "separate"):
                request_kind = "cpu_malloc"
                peak_cpu_bytes = stage_peak
                phase = stage.get("phase", "unknown")
                cpu_peak_context = {
                    "source_record": "LC2_BC_FULL_STAGE",
                    "line": stage_index + 1,
                    "timestamp_ns": None,
                    "known_cpu_scratch_peak_bytes": stage_peak,
                    "basis": stage.get("basis"),
                    "staging_mode": stage.get("staging-mode"),
                    "association": "same run and owner; log order only",
                }
    event_sha = hashlib.sha256((event_line + "\n").encode()).hexdigest()
    log_sha = hashlib.sha256(local_bytes).hexdigest()
    request = AdmissionRequest(
        run_uuid=event["run-id"], owner=actual["owner"], storage_id=None, storage_generation=None,
        request_kind=request_kind,
        requested_bytes=checked_add_u64(actual["gl_bytes"], actual["scratch_bytes"]),
        gl_bytes=actual["gl_bytes"], scratch_bytes=actual["scratch_bytes"],
        peak_overlapping_cpu_bytes=peak_cpu_bytes, proven_cma_bytes=None,
        kernel_source_confidence=kernel_source_confidence,
        sample_time_ns=event_time,
        timestamp_source="synthetic_fixture" if source_is_synthetic else "target_clock_monotonic",
        phase=phase, cma_provenance="unattributed",
        available_kib=actual["available_kib"], cma_free_kib=actual["cma_free_kib"],
        floor_mib=int(summary["common_run_config"]["floor_mib"]), margin_mib=actual["margin_mib"],
        synthetic=source_is_synthetic,
    )
    source = {
        "source_complete": True,
        "source_is_synthetic": source_is_synthetic,
        "log_bytes": captured["size"],
        "log_sha256_current_copy": log_sha,
        "header_sha256": captured["header_sha256"],
        "final_anchor_sha256": captured["anchor"]["sha256"],
        "admission_event_sha256": event_sha,
        "admission_event_line": event_index + 1,
        "memory_timeline_complete": arm.get("timeline", {}).get("complete"),
        "cpu_peak_context": cpu_peak_context,
        "gl_storage_events_before": before_count,
        "gl_storage_events_after": after_count,
        "log_hash_limit": "Current-copy digest only; header+tail receipt is append-only continuity evidence, not full historical attestation.",
    }
    return request, source, event


def replay_summary(summary: dict[str, Any], raw_root: Path, *,
                   kernel_source_confidence: str = "unknown", source_is_synthetic: bool = False):
    """Replay exactly the four build259 arms; models remain host-only and non-deployable."""
    if summary.get("schema") != "lamentum-m2b-e3-margin-sweep-v1":
        raise ValueError("unsupported margin-sweep summary schema")
    common = summary.get("common_run_config")
    binary = summary.get("binary")
    device = summary.get("device")
    if not isinstance(common, dict) or not isinstance(device, dict):
        raise ValueError("summary identity/config sections must be objects")
    if not isinstance(binary, dict) or binary.get("build") != 259:
        raise ValueError("expected build259 evidence")
    if (common.get("floor_mib") != 96 or common.get("texture_budget_mib") != 300
            or common.get("strict_gl") is not True):
        raise ValueError("unexpected build259 policy configuration")
    if (common.get("margin_was_per_run_only") is not True
            or common.get("launcher_margin_default") is not None):
        raise ValueError("refusing summary without per-run margin evidence")
    if common.get("new_game_entered") is not False:
        raise ValueError("refusing summary that entered New Game")
    arms = summary.get("arms")
    if not isinstance(arms, list) or len(arms) != len(EXPECTED_REQUESTS):
        raise ValueError("expected the four pinned build259 arms")
    actual_order = []
    requests = []
    for arm in arms:
        if not isinstance(arm, dict):
            raise ValueError("malformed margin-sweep arm")
        margin = arm.get("margin_mib")
        raw_dir = Path(raw_root) / f"m2b-e3-build259-margin{margin}-01"
        request, source, event = load_observed_arm(
            summary, arm, raw_dir, kernel_source_confidence=kernel_source_confidence,
            source_is_synthetic=source_is_synthetic)
        current = evaluate_all_bytes_maybe_cma(request)
        observed_reason = event["reason"]
        if (current["would_admit"] != (event["decision"] == "allow")
                or current["reason"] != observed_reason
                or current.get("required_cma_bytes") != _decimal(event, "required-cma-bytes")
                or current.get("required_available_bytes") != _decimal(event, "required-available-bytes")):
            raise ValueError("existing C admission formula did not exactly replay the raw event")
        proven = evaluate_proven_cma_only(request, cma_uncertainty_margin_bytes=None)
        mixed = evaluate_mixed_two_ledger(request, driver_uncertainty_margin_bytes=None)
        actual_order.append((margin, request.owner, request.gl_bytes, request.scratch_bytes))
        requests.append({
            "observed": {**request.to_dict(), "decision": event["decision"], "reason": observed_reason,
                         "required_available_bytes": _decimal(event, "required-available-bytes"),
                         "required_cma_bytes": _decimal(event, "required-cma-bytes"), "source": source},
            "models": {
                "all_bytes_maybe_CMA": current,
                "proven_CMA_only": proven,
                "mixed_two_ledger": mixed,
            },
        })
    if tuple(actual_order) != EXPECTED_REQUESTS:
        raise ValueError("historical request set/order differs from the four pinned refusals")
    return {
        "schema_version": 1,
        "replay_status": "complete",
        "scope": "host-only policy reconstruction; not allocation success or gameplay",
        "device_actions": 0,
        "gameplay_result": "not_run",
        "synthetic_input": source_is_synthetic,
        "kernel_source_confidence": kernel_source_confidence,
        "requests": requests,
        "conclusion": (
            "All four source-bound build259 cmafree-margin refusals reproduce exactly under the "
            "deployed conservative formula. Typed and mixed models remain unqualified because "
            "physical CMA backing and an evidenced driver uncertainty margin are unknown."
        ),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", required=True, help="sanitized build259 ab-summary.json")
    parser.add_argument("--raw-root", required=True, help="local root containing margin{64,48,32,24}-01 logs")
    parser.add_argument("--kernel-source-confidence", choices=sorted(KERNEL_CONFIDENCE), default="unknown")
    parser.add_argument("--synthetic-input", action="store_true",
                        help="explicitly label self-authored fixture logs; never use for device evidence")
    args = parser.parse_args(argv)
    try:
        summary = _load_json(Path(args.summary), "margin-sweep summary")
        report = replay_summary(summary, Path(args.raw_root),
                                kernel_source_confidence=args.kernel_source_confidence,
                                source_is_synthetic=args.synthetic_input)
    except (OSError, ValueError, OverflowError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
