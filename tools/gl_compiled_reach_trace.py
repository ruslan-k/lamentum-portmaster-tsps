"""Opt-in compiler tracing and per-translation-unit preprocessing for H1."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Sequence

COMPILER = "aarch64-linux-gnu-gcc"
WRAPPER_FLAGS = (
    "-DZERO_ZX_GAME=0",
    "-Wno-error=unused-result",
    "-Wno-error=unused-function",
)
SOURCE_SUFFIXES = {".c", ".s", ".S"}
DEPENDENCY_FLAGS = {"-MD", "-MMD", "-MF", "-MT"}
COMPILE_FLAG_PREFIXES = ("-I", "-D", "-std=", "-O", "-f", "-pthread", "-include", "-isystem")


class CompileTraceError(ValueError):
    """A trace input is incomplete or cannot be mapped without guessing."""


def find_sources(argv: Sequence[str]) -> list[str]:
    """Return direct C/C++/preprocessed-assembly source arguments."""
    sources = []
    skip_next = False
    for arg in argv:
        if skip_next:
            skip_next = False
            continue
        if arg in {"-o", "-MF", "-MT", "-include", "-isystem", "-I", "-D"}:
            skip_next = True
            continue
        if arg.startswith("@"):
            continue
        if not arg.startswith("-") and Path(arg).suffix in SOURCE_SUFFIXES:
            sources.append(arg)
    return sources


def instrument_invocation(argv: Sequence[str], dependency_file: str) -> list[str]:
    """Add MMD output without changing the caller's argument list."""
    if any(arg in DEPENDENCY_FLAGS for arg in argv):
        raise CompileTraceError("compiler invocation already contains dependency flags")
    return [*argv, "-MMD", "-MF", dependency_file]


def _remove_compile_output(argv: Sequence[str]) -> list[str]:
    result = []
    skip_next = False
    for arg in argv:
        if skip_next:
            skip_next = False
            continue
        if arg == "-c":
            continue
        if arg == "-o":
            skip_next = True
            continue
        if arg in DEPENDENCY_FLAGS:
            if arg in {"-MF", "-MT"}:
                skip_next = True
            continue
        result.append(arg)
    if skip_next:
        raise CompileTraceError("compiler output flag is missing its value")
    return result


def preprocess_argv_for_compile(
    command: dict, source: str, output: str, dependency_file: str
) -> list[str]:
    argv = command.get("argv")
    if not isinstance(argv, list) or source not in argv:
        raise CompileTraceError(f"source is not in compile invocation: {source}")
    return [*_remove_compile_output(argv), "-E", "-MMD", "-MF", dependency_file,
            "-MT", source, "-o", output]


def preprocess_argv_for_link_source(
    command: dict, source: str, output: str, dependency_file: str
) -> list[str]:
    argv = command.get("argv")
    sources = command.get("source_files")
    if not isinstance(argv, list) or not isinstance(sources, list) or source not in sources:
        raise CompileTraceError(f"source is not in link invocation: {source}")
    try:
        source_indexes = [argv.index(name) for name in sources]
    except ValueError as exc:
        raise CompileTraceError("link source list does not match argv") from exc
    first_source = min(source_indexes)
    source_names = set(sources)
    trailing = [arg for arg in argv[first_source + 1:] if arg not in source_names]
    if any(arg in {"-I", "-D", "-include", "-isystem"}
           or arg.startswith(COMPILE_FLAG_PREFIXES) for arg in trailing):
        raise CompileTraceError("compile flags after source cannot be replayed safely")
    prefix = argv[:first_source]
    return [*prefix, source, "-E", "-MMD", "-MF", dependency_file,
            "-MT", source, "-o", output]


def validate_trace_commands(commands: list[dict]) -> list[dict]:
    if not isinstance(commands, list) or not commands:
        raise CompileTraceError("compiler command trace is empty")
    for row in commands:
        if not isinstance(row, dict) or row.get("kind") not in {"compile", "link"}:
            raise CompileTraceError("compiler trace has an invalid invocation")
        if "returncode" not in row:
            raise CompileTraceError("missing compiler return code")
        if row["returncode"] != 0:
            raise CompileTraceError(f"failed compiler invocation {row.get('sequence')}")
        if not isinstance(row.get("source_files"), list) or not row["source_files"]:
            raise CompileTraceError("compiler invocation has no source files")
        if not all(isinstance(path, str) for path in row["source_files"]):
            raise CompileTraceError("compiler invocation source files are malformed")
        if not isinstance(row.get("argv"), list) or not all(isinstance(arg, str) for arg in row["argv"]):
            raise CompileTraceError("compiler invocation arguments are malformed")
    if sum(row["kind"] == "compile" for row in commands) < 1 or sum(row["kind"] == "link" for row in commands) != 1:
        raise CompileTraceError("trace must contain compile commands and exactly one final link")
    return commands


def _output_arg(argv: Sequence[str]) -> str | None:
    for index, arg in enumerate(argv[:-1]):
        if arg == "-o":
            return argv[index + 1]
    return None


def _next_sequence(trace_dir: Path) -> int:
    counter = trace_dir / "sequence.txt"
    commands = trace_dir / "commands.jsonl"
    if not counter.exists() and commands.exists():
        raise CompileTraceError("trace directory has old commands but no sequence counter")
    sequence = int(counter.read_text()) + 1 if counter.exists() else 1
    counter.write_text(str(sequence))
    return sequence


def _source_root_prefix(sources: Sequence[str]) -> str:
    for source in sources:
        marker = "/source/"
        if marker in source:
            return source.split(marker, 1)[0] + "/source"
    raise CompileTraceError("cannot infer container source root; set COTM_TRACE_SOURCE_ROOT")


def _trace_metadata(trace_dir: Path, source_root: str, compiler: str) -> dict:
    compiler_path = shutil.which(compiler)
    if compiler_path is None:
        raise CompileTraceError(f"compiler not found on PATH: {compiler}")
    return {
        "schema_version": 1,
        "container_source_root": source_root,
        "container_trace_root": str(trace_dir),
        "compiler": compiler,
        "compiler_path": str(Path(compiler_path).resolve()),
        "compiler_version": subprocess.run(
            [compiler, "--version"], check=True, capture_output=True, text=True
        ).stdout.splitlines()[0],
        "target": subprocess.run(
            [compiler, "-dumpmachine"], check=True, capture_output=True, text=True
        ).stdout.strip(),
        "wrapper_flags": list(WRAPPER_FLAGS),
    }


def capture_wrapper_main(argv: Sequence[str] | None = None) -> int:
    """COTM_CC entrypoint. Records the actual args and adds dependency output."""
    args = list(sys.argv[1:] if argv is None else argv)
    trace_value = os.environ.get("COTM_TRACE_DIR")
    if not trace_value:
        print("COTM_TRACE_DIR is required for the trace compiler wrapper", file=sys.stderr)
        return 64
    if any(arg.startswith("@") for arg in args):
        print("response files are not supported by this trace wrapper", file=sys.stderr)
        return 65
    trace_dir = Path(trace_value)
    compiler = os.environ.get("COTM_REAL_CC", COMPILER)
    compiler_path = shutil.which(compiler)
    if compiler_path is None:
        print(f"compiler not found on PATH: {compiler}", file=sys.stderr)
        return 65
    trace_dir.mkdir(parents=True, exist_ok=True)
    sources = find_sources(args)
    if not sources:
        result = subprocess.run([compiler, *args, *WRAPPER_FLAGS])
        return result.returncode
    output = _output_arg(args)
    kind = "compile" if "-c" in args else "link" if output else "unsupported"
    if kind == "unsupported":
        print("source invocation is neither compile nor final link", file=sys.stderr)
        return 65
    source_root = os.environ.get("COTM_TRACE_SOURCE_ROOT") or _source_root_prefix(sources)
    metadata_path = trace_dir / "trace_metadata.json"
    expected_metadata = {
        "schema_version": 1,
        "container_source_root": source_root,
        "container_trace_root": str(trace_dir),
        "compiler": compiler,
        "compiler_path": str(Path(compiler_path).resolve()),
        "wrapper_flags": list(WRAPPER_FLAGS),
    }
    if metadata_path.exists():
        existing = json.loads(metadata_path.read_text())
        if any(existing.get(key) != value for key, value in expected_metadata.items()):
            print("trace metadata mismatch; use a fresh trace directory", file=sys.stderr)
            return 65
    else:
        metadata = _trace_metadata(trace_dir, source_root, compiler)
        metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    sequence = _next_sequence(trace_dir)
    dep_dir = trace_dir / "deps"
    dep_dir.mkdir(parents=True, exist_ok=True)
    output_name = Path(output).name if output else Path(sources[0]).name
    depfile = dep_dir / f"{sequence:04d}-{output_name}.d"
    effective_args = [*instrument_invocation(args, str(depfile)), *WRAPPER_FLAGS]
    record = {
        "sequence": sequence,
        "cwd": os.getcwd(),
        "argv": args,
        "effective_argv": [compiler, *effective_args],
        "compiler": compiler,
        "wrapper_flags": list(WRAPPER_FLAGS),
        "source_files": sources,
        "output": output,
        "dependency_file": str(depfile),
        "kind": kind,
    }
    result = subprocess.run([compiler, *effective_args], capture_output=True)
    record["returncode"] = result.returncode
    record["stdout_sha256"] = hashlib.sha256(result.stdout).hexdigest()
    record["stderr_sha256"] = hashlib.sha256(result.stderr).hexdigest()
    record["stderr_bytes"] = len(result.stderr)
    with (trace_dir / "commands.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")
    sys.stdout.buffer.write(result.stdout)
    sys.stderr.buffer.write(result.stderr)
    return result.returncode


def _run_preprocessor(compiler: str, argv: list[str], cwd: str, wrapper_flags: list[str]) -> tuple[int, str]:
    result = subprocess.run([compiler, *argv, *wrapper_flags], cwd=cwd,
                            capture_output=True, text=True)
    return result.returncode, result.stderr


def _materialize_record(
    command: dict, source: str, output: Path, depfile: Path, compiler: str,
    wrapper_flags: list[str], final_link_source: bool,
) -> dict:
    builder = preprocess_argv_for_link_source if final_link_source else preprocess_argv_for_compile
    argv = builder(command, source, str(output), str(depfile))
    returncode, stderr = _run_preprocessor(compiler, argv, command["cwd"], wrapper_flags)
    if returncode:
        raise CompileTraceError(f"preprocessor failed for {source}: {stderr}")
    if not output.is_file() or not depfile.is_file():
        raise CompileTraceError(f"preprocessor did not create output and dependency file for {source}")
    return {
        "translation_unit": source,
        "argv": argv,
        "returncode": returncode,
        "stderr": stderr,
        "bytes": output.stat().st_size,
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "dependency_file": str(depfile),
    }


def materialize_trace(trace_dir: str | Path) -> dict:
    """Create hashed per-unit preprocessed files and dependency summaries."""
    trace_dir = Path(trace_dir)
    metadata_path = trace_dir / "trace_metadata.json"
    commands_path = trace_dir / "commands.jsonl"
    if not metadata_path.is_file() or not commands_path.is_file():
        raise CompileTraceError("trace metadata or commands.jsonl is missing")
    metadata = json.loads(metadata_path.read_text())
    if metadata.get("schema_version") != 1:
        raise CompileTraceError("unsupported trace metadata schema")
    if any((trace_dir / name).exists() for name in
           ("preprocessed-summary.json", "preprocessed-objects-summary.json", "preprocess_replays.jsonl")):
        raise CompileTraceError("preprocessor summaries already exist; use a fresh trace directory")
    commands = [json.loads(line) for line in commands_path.read_text().splitlines() if line]
    commands = validate_trace_commands(commands)
    compiler = metadata["compiler"]
    wrapper_flags = metadata["wrapper_flags"]
    object_dir = trace_dir / "preprocessed-objects"
    link_dir = trace_dir / "preprocessed"
    object_dir.mkdir()
    link_dir.mkdir()
    object_rows = []
    link_rows = []
    replay_rows = []
    for command in commands:
        if command["kind"] == "compile":
            if len(command["source_files"]) != 1:
                raise CompileTraceError("compile invocation must have exactly one source")
            source = command["source_files"][0]
            basename = Path(source).name
            output = object_dir / f"{command['sequence']:04d}-{basename}.i"
            depfile = object_dir / f"{command['sequence']:04d}-{basename}.d"
            row = _materialize_record(command, source, output, depfile, compiler,
                                      wrapper_flags, final_link_source=False)
            row["preprocessed_file"] = str(output)
            object_rows.append(row)
        elif command["kind"] == "link":
            for index, source in enumerate(command["source_files"], 1):
                basename = Path(source).name
                stem = f"{command['sequence']:04d}-tu{index:02d}-{basename}"
                output = link_dir / f"{stem}.i"
                depfile = link_dir / f"{stem}.d"
                row = _materialize_record(command, source, output, depfile, compiler,
                                          wrapper_flags, final_link_source=True)
                row["output"] = str(output)
                link_rows.append(row)
                replay_rows.append({
                    "sequence": command["sequence"],
                    "translation_unit": source,
                    "argv": row["argv"],
                    "dependency_file": str(depfile),
                    "returncode": row["returncode"],
                    "stderr": row["stderr"],
                })
        else:
            raise CompileTraceError(f"unsupported recorded command kind: {command['kind']}")
    (trace_dir / "preprocessed-summary.json").write_text(
        json.dumps(link_rows, indent=2, sort_keys=True) + "\n")
    (trace_dir / "preprocessed-objects-summary.json").write_text(
        json.dumps(object_rows, indent=2, sort_keys=True) + "\n")
    with (trace_dir / "preprocess_replays.jsonl").open("w", encoding="utf-8") as stream:
        for row in replay_rows:
            stream.write(json.dumps(row, sort_keys=True) + "\n")
    return {
        "translation_units": len(link_rows) + len(object_rows),
        "object_units": len(object_rows),
        "link_source_units": len(link_rows),
        "preprocessed_bytes": sum(row["bytes"] for row in link_rows + object_rows),
    }


def materialize_main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(description="Materialize compiler trace per-unit preprocessor outputs.")
    parser.add_argument("--trace-dir", required=True)
    args = parser.parse_args(list(argv))
    try:
        result = materialize_trace(args.trace_dir)
    except (CompileTraceError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "materialize":
        return materialize_main(args[1:])
    return capture_wrapper_main(args)


if __name__ == "__main__":
    raise SystemExit(main())
