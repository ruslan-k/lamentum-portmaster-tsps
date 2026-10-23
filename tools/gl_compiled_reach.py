"""Classify GL allocation callsites against an exact compiler/preprocessor trace.

This reports compiler inclusion only. It does not prove linker retention,
runtime execution, driver allocation success, or physical backing.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shlex
import sys

from gl_allocation_inventory import (
    InventoryError,
    _mask_comments_and_literals,
    scan_source_tree,
    source_tree_identity,
    validate_policy,
)


class CompileReachError(ValueError):
    """The compiler trace is incomplete or does not match the source snapshot."""


LINE_MARKER = re.compile(r'^\s*#\s*(\d+)\s+"([^"]+)"(?:\s|$)')
DEFAULT_WRAPPERS = {
    "glTexImage2D": "lc2_gl_tex_image2d_admit",
    "glBufferData": "lc2_gl_buffer_data_admit",
    "glRenderbufferStorage": "lc2_gl_renderbuffer_storage_admit",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path, label: str):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CompileReachError(f"cannot read {label}: {path}: {exc}") from exc


def _load_jsonl(path: Path, label: str) -> list[dict]:
    if not path.is_file():
        raise CompileReachError(f"missing {label}: {path}")
    rows = []
    try:
        for number, text in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not text.strip():
                continue
            row = json.loads(text)
            if not isinstance(row, dict):
                raise ValueError("record is not an object")
            rows.append(row)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise CompileReachError(f"invalid {label} at {path}: {exc}") from exc
    if not rows:
        raise CompileReachError(f"empty {label}: {path}")
    return rows


def _safe_rel(value: str) -> str:
    path = PurePosixPath(value.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts:
        raise CompileReachError(f"unsafe relative source path: {value!r}")
    return path.as_posix()


def _map_recorded_path(
    value: str,
    source_root: Path,
    trace_dir: Path,
    container_source_root: str,
    container_trace_root: str,
) -> Path:
    source_prefix = container_source_root.rstrip("/")
    trace_prefix = container_trace_root.rstrip("/")
    if value == source_prefix or value.startswith(source_prefix + "/"):
        suffix = value[len(source_prefix):].lstrip("/")
        relative = _safe_rel(suffix) if suffix else ""
        return source_root / relative
    if value == trace_prefix or value.startswith(trace_prefix + "/"):
        suffix = value[len(trace_prefix):].lstrip("/")
        relative = _safe_rel(suffix) if suffix else ""
        return trace_dir / relative
    return Path(value)


def _source_relative(
    recorded_path: str,
    source_root: Path,
    trace_dir: Path,
    container_source_root: str,
    container_trace_root: str,
) -> str:
    mapped = _map_recorded_path(
        recorded_path, source_root, trace_dir, container_source_root, container_trace_root
    )
    try:
        return mapped.resolve().relative_to(source_root.resolve()).as_posix()
    except ValueError as exc:
        raise CompileReachError(
            f"translation unit is outside the exact source root: {recorded_path}"
        ) from exc


def parse_preprocessed(text: str, container_source_root: str) -> dict[tuple[str, int], list[str]]:
    """Map active preprocessor output to original patched-tree path and line."""
    root = container_source_root.rstrip("/")
    current_path = None
    current_line = 0
    result: dict[tuple[str, int], list[str]] = defaultdict(list)
    for output_line in text.splitlines():
        marker = LINE_MARKER.match(output_line)
        if marker:
            filename = marker.group(2)
            current_line = int(marker.group(1))
            if filename == root:
                current_path = ""
            elif filename.startswith(root + "/"):
                current_path = _safe_rel(filename[len(root) + 1:])
            else:
                current_path = None
            continue
        if current_path is not None:
            result[(current_path, current_line)].append(output_line.strip())
            current_line += 1
    return dict(result)


def classify_callsite(
    site: dict,
    dependency_units: dict[str, set[str]],
    preprocessed_lines: dict[tuple[str, int], list[str]],
    wrapper_symbols: dict[str, str] | None = None,
) -> dict:
    """Classify one site conservatively as reachable, unreachable, or unknown."""
    wrappers = DEFAULT_WRAPPERS if wrapper_symbols is None else wrapper_symbols
    path = site["path"]
    line = int(site["line"])
    units = sorted(dependency_units.get(path, set()))
    active = [
        text for text in preprocessed_lines.get((path, line), [])
        if text.strip() and not text.lstrip().startswith("#")
    ]
    active_code = _mask_comments_and_literals("\n".join(active))
    expected = [site.get("api", ""), site.get("callee", "")]
    if site.get("api") in wrappers:
        expected.append(wrappers[site["api"]])
    matched = []
    for token in expected:
        call = re.compile(rf"\b{re.escape(token)}\s*(?:\(|\)\s*\()")
        if token and token not in matched and call.search(active_code):
            matched.append(token)
    if matched:
        status = "compiled-reachable"
        proof = "active preprocessed source line invokes the API, callee, or known wrapper token"
    elif not units:
        status = "compiled-unreachable"
        proof = "source path is absent from every direct translation unit dependency closure"
    else:
        status = "unknown"
        proof = "source path is included, but the exact callsite line/token is absent from preprocessed output"
    return {
        "status": status,
        "matched_tokens": matched,
        "translation_units": units,
        "proof": proof,
    }


def classify_link_input(
    translation_units: set[str],
    direct_link_sources: set[str],
    object_outputs: dict[str, str],
    linked_objects: set[str],
    archive_present: bool = False,
) -> dict:
    """Classify link command input, not post-GC section retention."""
    direct = sorted(translation_units & direct_link_sources)
    if direct:
        status = "link-input-confirmed"
        units = direct
        proof = "translation unit is passed directly to the final link command"
    else:
        objects = sorted(
            unit for unit in translation_units
            if object_outputs.get(unit) in linked_objects
        )
        if objects:
            status = "link-input-confirmed"
            units = objects
            proof = "compiled object output is an exact input to the final link command"
        elif translation_units and archive_present:
            status = "unknown"
            units = sorted(translation_units)
            proof = "object is not a direct link input; archive membership was not traced"
        else:
            status = "not-in-link-input"
            units = []
            proof = "no direct source or compiled object from this site's translation units is linked"
    return {
        "status": status,
        "units": units,
        "live_section_retained": "unknown",
        "proof": proof,
    }


def _parse_depfile(path: Path) -> list[str]:
    if not path.is_file():
        raise CompileReachError(f"missing dependency file: {path}")
    text = path.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"\\\r?\n\s*", " ", text)
    if ":" not in text:
        raise CompileReachError(f"malformed dependency file: {path}")
    try:
        dependencies = shlex.split(text.split(":", 1)[1])
    except ValueError as exc:
        raise CompileReachError(f"malformed dependency file {path}: {exc}") from exc
    if not dependencies:
        raise CompileReachError(f"empty dependency list: {path}")
    return dependencies


def _extract_flags(commands: list[dict], wrapper_flags: tuple[str, ...]) -> dict:
    includes = set()
    defines = set()
    response_files = []
    all_args = [arg for command in commands for arg in command["argv"]] + list(wrapper_flags)
    index = 0
    while index < len(all_args):
        arg = all_args[index]
        if arg == "-I" and index + 1 < len(all_args):
            includes.add(all_args[index + 1])
            index += 2
            continue
        if arg.startswith("-I") and len(arg) > 2:
            includes.add(arg[2:])
        if arg == "-D" and index + 1 < len(all_args):
            defines.add(all_args[index + 1])
            index += 2
            continue
        if arg.startswith("-D") and len(arg) > 2:
            defines.add(arg[2:])
        if arg.startswith("@"):
            response_files.append(arg)
        index += 1
    return {
        "include_dirs": sorted(includes),
        "defines": sorted(defines),
        "response_files": sorted(set(response_files)),
    }


def analyze_trace_bundle(
    source_root: str | Path,
    inventory_path: str | Path,
    policy_path: str | Path,
    trace_dir: str | Path,
    container_source_root: str,
    container_trace_root: str,
    expected_commands_sha256: str | None = None,
    wrapper_flags: tuple[str, ...] = (),
) -> dict:
    """Validate a pinned compiler trace and return per-site compile dispositions."""
    source_root = Path(source_root).resolve()
    trace_dir = Path(trace_dir).resolve()
    inventory_path = Path(inventory_path)
    policy_path = Path(policy_path)
    for dirname in ("native", "framework"):
        if not (source_root / dirname).is_dir():
            raise CompileReachError(f"source tree missing {dirname}/")
    try:
        identity = source_tree_identity(source_root)
        scanned = scan_source_tree(source_root)
    except InventoryError as exc:
        raise CompileReachError(str(exc)) from exc
    inventory = _load_json(inventory_path, "callsite inventory")
    policy = _load_json(policy_path, "callsite policy")
    if not isinstance(inventory, dict) or not isinstance(policy, dict):
        raise CompileReachError("inventory and policy must be JSON objects")
    if inventory.get("source_tree") != identity:
        raise CompileReachError("inventory source tree identity mismatch")
    try:
        validate_policy(scanned, policy, identity)
    except InventoryError as exc:
        raise CompileReachError(str(exc)) from exc
    recorded_sites = inventory.get("call_sites")
    scanned_by_id = {site["id"]: site for site in scanned}
    if not isinstance(recorded_sites, list) or not all(isinstance(site, dict) for site in recorded_sites):
        raise CompileReachError("inventory call_sites must be a list of objects")
    if {site.get("id") for site in recorded_sites} != set(scanned_by_id):
        raise CompileReachError("inventory callsites do not match the exact source scan")
    for row in recorded_sites:
        actual = scanned_by_id[row["id"]]
        for key in ("path", "line", "api", "callee", "kind", "dispatch"):
            if row.get(key) != actual.get(key):
                raise CompileReachError(f"inventory callsite field mismatch for {row['id']}: {key}")

    commands_path = trace_dir / "commands.jsonl"
    commands = _load_jsonl(commands_path, "commands trace")
    commands_sha = _sha256(commands_path)
    if expected_commands_sha256 and commands_sha != expected_commands_sha256:
        raise CompileReachError("command trace SHA-256 mismatch")
    direct_units = set()
    direct_link_sources = set()
    object_outputs = {}
    link_commands = [command for command in commands if command["kind"] == "link"]
    linked_objects = {
        arg for command in link_commands for arg in command["argv"] if arg.endswith(".o")
    }
    linked_archives = {
        arg for command in link_commands for arg in command["argv"] if arg.endswith(".a")
    }
    for command in commands:
        if command.get("kind") not in {"compile", "link"}:
            raise CompileReachError("unknown compiler invocation kind")
        if not isinstance(command.get("argv"), list) or not all(isinstance(arg, str) for arg in command["argv"]):
            raise CompileReachError("compiler invocation has invalid argv")
        source_files = command.get("source_files")
        if not isinstance(source_files, list) or not source_files or not all(isinstance(path, str) for path in source_files):
            raise CompileReachError("compiler invocation has invalid source_files")
        for filename in source_files:
            relative = _source_relative(
                filename, source_root, trace_dir, container_source_root, container_trace_root
            )
            if not (source_root / relative).is_file():
                raise CompileReachError(f"missing direct translation unit: {relative}")
            direct_units.add(relative)
            if command["kind"] == "link":
                direct_link_sources.add(relative)
            elif command.get("output"):
                object_outputs[relative] = command["output"]
    if not direct_units:
        raise CompileReachError("compiler trace has no translation units")

    preprocess_records = []
    for name in ("preprocessed-summary.json", "preprocessed-objects-summary.json"):
        rows = _load_json(trace_dir / name, name)
        if not isinstance(rows, list):
            raise CompileReachError(f"{name} must contain a list")
        preprocess_records.extend(rows)
    replay_path = trace_dir / "preprocess_replays.jsonl"
    replay_rows = _load_jsonl(replay_path, "preprocess replay trace")
    replay_by_tu = {}
    for replay in replay_rows:
        tu = replay.get("translation_unit")
        if not isinstance(tu, str) or tu in replay_by_tu:
            raise CompileReachError("duplicate or invalid preprocessor replay translation unit")
        if replay.get("returncode") != 0:
            raise CompileReachError(f"preprocessor replay failed: {tu}")
        replay_by_tu[tu] = replay

    closure: dict[str, set[str]] = defaultdict(set)
    line_map: dict[tuple[str, int], list[str]] = defaultdict(list)
    preprocessed_tus = set()
    preprocessed_bytes = 0
    for record in preprocess_records:
        if not isinstance(record, dict) or record.get("returncode") != 0:
            raise CompileReachError("failed or malformed per-unit preprocessor record")
        recorded_tu = record.get("translation_unit")
        if not isinstance(recorded_tu, str):
            raise CompileReachError("preprocessor record missing translation_unit")
        tu_rel = _source_relative(
            recorded_tu, source_root, trace_dir, container_source_root, container_trace_root
        )
        if tu_rel in preprocessed_tus:
            raise CompileReachError(f"duplicate preprocessed translation unit: {tu_rel}")
        preprocessed_tus.add(tu_rel)
        output_name = record.get("preprocessed_file") or record.get("output")
        if not isinstance(output_name, str):
            raise CompileReachError(f"missing preprocessed output path: {tu_rel}")
        output_path = _map_recorded_path(
            output_name, source_root, trace_dir, container_source_root, container_trace_root
        )
        if not output_path.is_file():
            raise CompileReachError(f"missing preprocessed output: {output_path}")
        output_bytes = output_path.read_bytes()
        if record.get("bytes") != len(output_bytes) or record.get("sha256") != hashlib.sha256(output_bytes).hexdigest():
            raise CompileReachError(f"preprocessed output identity mismatch: {tu_rel}")
        preprocessed_bytes += len(output_bytes)

        replay = replay_by_tu.get(recorded_tu, {})
        dependency_name = record.get("depfile") or record.get("dependency_file") or replay.get("dependency_file")
        if not isinstance(dependency_name, str):
            raise CompileReachError(f"missing dependency file record: {tu_rel}")
        dependency_path = _map_recorded_path(
            dependency_name, source_root, trace_dir, container_source_root, container_trace_root
        )
        dependencies = _parse_depfile(dependency_path)
        unit_was_dependency = False
        for dependency in dependencies:
            mapped = _map_recorded_path(
                dependency, source_root, trace_dir, container_source_root, container_trace_root
            )
            try:
                relative = mapped.resolve().relative_to(source_root).as_posix()
            except ValueError:
                continue
            relative = _safe_rel(relative)
            closure[relative].add(tu_rel)
            if relative == tu_rel:
                unit_was_dependency = True
        if not unit_was_dependency:
            raise CompileReachError(f"dependency file omits its translation unit: {tu_rel}")
        parsed_lines = parse_preprocessed(output_bytes.decode("utf-8", errors="replace"), container_source_root)
        for key, lines in parsed_lines.items():
            line_map[key].extend(lines)
    if preprocessed_tus != direct_units:
        missing = sorted(direct_units - preprocessed_tus)
        extra = sorted(preprocessed_tus - direct_units)
        raise CompileReachError(f"preprocessed translation-unit set mismatch; missing={missing}, extra={extra}")

    policy_by_id = {row["id"]: row for row in policy["call_sites"]}
    sites = []
    status_counts = Counter()
    link_status_counts = Counter()
    for original in scanned:
        result = classify_callsite(original, closure, line_map)
        link_result = classify_link_input(
            set(result["translation_units"]), direct_link_sources,
            object_outputs, linked_objects, archive_present=bool(linked_archives),
        )
        row = dict(original)
        row["source_status"] = policy_by_id[row["id"]]["status"]
        row["compiled_status"] = result["status"]
        row["matched_tokens"] = result["matched_tokens"]
        row["translation_units"] = result["translation_units"]
        row["proof"] = result["proof"]
        row["link_input_status"] = link_result["status"]
        row["link_input_units"] = link_result["units"]
        row["link_input_proof"] = link_result["proof"]
        row["live_section_retained"] = link_result["live_section_retained"]
        sites.append(row)
        status_counts[row["compiled_status"]] += 1
        link_status_counts[row["link_input_status"]] += 1

    flag_summary = _extract_flags(commands, wrapper_flags)
    include_dirs = flag_summary["include_dirs"]
    defines = flag_summary["defines"]
    response_files = flag_summary["response_files"]
    if response_files:
        raise CompileReachError("response file arguments present but contents are not captured")
    source_status_counts = Counter(site["source_status"] for site in sites)
    link_args = [arg for command in link_commands for arg in command["argv"]]
    return {
        "schema_version": 1,
        "source_tree": identity,
        "source_base_commit": policy.get("source_base_commit"),
        "adapter_patch_sha256": policy.get("adapter_patch_sha256"),
        "compiler_flags": {
            "include_dirs": include_dirs,
            "defines": defines,
            "response_files": response_files,
            "wrapper_extra_flags": list(wrapper_flags),
        },
        "trace": {
            "compiler_invocations": len(commands),
            "compile_invocations": sum(command["kind"] == "compile" for command in commands),
            "link_invocations": len(link_commands),
            "translation_units": len(direct_units),
            "translation_unit_paths": sorted(direct_units),
            "per_unit_dependency_preprocessor_records": len(preprocess_records),
            "unique_project_dependencies": len(closure),
            "preprocessed_bytes": preprocessed_bytes,
            "commands_sha256": commands_sha,
            "link_uses_gc_sections": any("gc-sections" in arg for arg in link_args),
            "direct_link_source_units": sorted(direct_link_sources),
            "link_input_objects": len(linked_objects),
            "link_input_archives": len(linked_archives),
        },
        "source_status_counts": dict(source_status_counts),
        "compiled_status_counts": dict(status_counts),
        "link_input_status_counts": dict(link_status_counts),
        "call_sites": sites,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--inventory", required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--trace-dir", required=True)
    parser.add_argument("--container-source-root", required=True)
    parser.add_argument("--container-trace-root", required=True)
    parser.add_argument("--expected-commands-sha256")
    parser.add_argument("--wrapper-flag", action="append", default=[])
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        report = analyze_trace_bundle(
            args.source_root, args.inventory, args.policy, args.trace_dir,
            args.container_source_root, args.container_trace_root,
            args.expected_commands_sha256, tuple(args.wrapper_flag),
        )
    except (CompileReachError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    output = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
