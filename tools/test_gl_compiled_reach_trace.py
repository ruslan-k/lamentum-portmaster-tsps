import json
import os
import tempfile
import unittest
from pathlib import Path

from gl_compiled_reach_trace import (
    CompileTraceError,
    capture_wrapper_main,
    find_sources,
    instrument_invocation,
    materialize_trace,
    preprocess_argv_for_compile,
    preprocess_argv_for_link_source,
    validate_trace_commands,
)


class GlCompiledReachTraceTests(unittest.TestCase):
    def test_capture_wrapper_records_actual_args_and_dependency_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            trace = root / "trace"
            source_root = root / "source"
            source = source_root / "native" / "unit.c"
            source.parent.mkdir(parents=True)
            source.write_text("int unit(void) { return 0; }\n")
            fake = root / "fake-cc"
            fake.write_text(
                "#!/usr/bin/env python3\n"
                "import sys\n"
                "if '--version' in sys.argv: print('fake gcc 1.0')\n"
                "elif '-dumpmachine' in sys.argv: print('aarch64-linux-gnu')\n"
            )
            fake.chmod(0o755)
            previous = {key: os.environ.get(key) for key in
                        ('COTM_TRACE_DIR', 'COTM_TRACE_SOURCE_ROOT', 'COTM_REAL_CC')}
            os.environ.update({'COTM_TRACE_DIR': str(trace),
                               'COTM_TRACE_SOURCE_ROOT': str(source_root),
                               'COTM_REAL_CC': str(fake)})
            try:
                rc = capture_wrapper_main(['-O2', '-c', str(source), '-o', str(root / 'unit.o')])
            finally:
                for key, value in previous.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value
            record = json.loads((trace / 'commands.jsonl').read_text())
            self.assertEqual(rc, 0)
            self.assertEqual(record['source_files'], [str(source)])
            self.assertEqual(record['kind'], 'compile')
            self.assertEqual(record['returncode'], 0)
            self.assertIn('-MMD', record['effective_argv'])
            metadata = json.loads((trace / "trace_metadata.json").read_text())
            self.assertEqual(metadata['target'], 'aarch64-linux-gnu')
            self.assertEqual(metadata['compiler_path'], str(fake.resolve()))

    def test_failed_or_incomplete_compiler_records_fail_closed(self):
        valid = {"sequence":1,"kind":"compile","returncode":0,
                 "source_files":["/src/a.c"],"argv":["-c","/src/a.c"]}
        link = {"sequence":2,"kind":"link","returncode":0,
                "source_files":["/src/a.c"],"argv":["/src/a.c","-o","app"]}
        self.assertEqual(validate_trace_commands([valid, link]), [valid, link])
        with self.assertRaisesRegex(CompileTraceError, "exactly one final link"):
            validate_trace_commands([valid])
        failed = dict(valid, returncode=1)
        with self.assertRaisesRegex(CompileTraceError, "failed compiler invocation"):
            validate_trace_commands([failed, link])
        incomplete = dict(valid)
        incomplete.pop("returncode")
        with self.assertRaisesRegex(CompileTraceError, "missing compiler return code"):
            validate_trace_commands([incomplete])

    def test_materializer_writes_hashed_outputs_and_dependency_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_dir = root / "source"
            source_dir.mkdir()
            source_a = source_dir / "a.c"
            source_b = source_dir / "b.S"
            source_a.write_text("int a(void) { return 1; }\n")
            source_b.write_text(".text\n")
            fake = root / "fake-cc"
            fake.write_text("\n".join([
                "#!/usr/bin/env python3",
                "import pathlib, sys",
                "a=sys.argv[1:]",
                "src=next(x for x in a if x.endswith(('.c','.S','.s'))) ",
                "out=a[a.index('-o')+1]; dep=a[a.index('-MF')+1]; target=a[a.index('-MT')+1]",
                "pathlib.Path(out).write_text(pathlib.Path(src).read_text())",
                "pathlib.Path(dep).write_text(target + ': ' + src + chr(10))",
            ]) + "\n")
            fake.chmod(0o755)
            trace = root / "trace"
            trace.mkdir()
            compile_cmd = {"sequence":1,"kind":"compile","returncode":0,"argv":["-O2","-c",str(source_a),"-o",str(root/"a.o")],
                           "source_files":[str(source_a)],"output":str(root/"a.o"),"cwd":str(root)}
            link_cmd = {"sequence":2,"kind":"link","returncode":0,"argv":["-O2",str(source_b),str(root/"a.o"),"-Wl,--gc-sections","-o",str(root/"app")],
                        "source_files":[str(source_b)],"output":str(root/"app"),"cwd":str(root)}
            (trace / "commands.jsonl").write_text("\n".join([json.dumps(compile_cmd), json.dumps(link_cmd)]) + "\n")
            (trace / "trace_metadata.json").write_text(json.dumps({"schema_version":1,"compiler":str(fake),"wrapper_flags":[]}))
            result = materialize_trace(trace)
            self.assertEqual(result["translation_units"], 2)
            self.assertEqual(result["object_units"], 1)
            self.assertEqual(result["link_source_units"], 1)
            self.assertEqual(len(json.loads((trace/"preprocessed-objects-summary.json").read_text())),1)
            self.assertEqual(len(json.loads((trace/"preprocessed-summary.json").read_text())),1)
            self.assertEqual(len((trace/"preprocess_replays.jsonl").read_text().splitlines()),1)

    def test_source_discovery_keeps_direct_c_and_assembly_units_only(self):
        argv = ["-O2", "-I/include", "src/a.c", "src/b.S", "obj/c.o", "@flags.rsp", "-o", "out.elf"]
        self.assertEqual(find_sources(argv), ["src/a.c", "src/b.S"])

    def test_compile_instrumentation_appends_dependency_file_flags(self):
        argv = ["-O2", "-I/include", "-c", "src/a.c", "-o", "a.o"]
        result = instrument_invocation(argv, "trace/0001-a.d")
        self.assertEqual(argv, ["-O2", "-I/include", "-c", "src/a.c", "-o", "a.o"])
        self.assertEqual(result[-3:], ["-MMD", "-MF", "trace/0001-a.d"])

    def test_existing_dependency_flags_are_not_duplicated(self):
        argv = ["-MMD", "-MF", "old.d", "-c", "src/a.c", "-o", "a.o"]
        with self.assertRaisesRegex(CompileTraceError, "already contains dependency flags"):
            instrument_invocation(argv, "trace/new.d")

    def test_preprocess_compile_preserves_flags_and_omits_object_output(self):
        command = {"argv": ["-O2", "-DMODE=1", "-I/inc", "-c", "/src/a.c", "-o", "/out/a.o"]}
        result = preprocess_argv_for_compile(command, "/src/a.c", "/trace/a.i", "/trace/a.d")
        self.assertEqual(result, ["-O2", "-DMODE=1", "-I/inc", "/src/a.c", "-E",
                                  "-MMD", "-MF", "/trace/a.d", "-MT", "/src/a.c", "-o", "/trace/a.i"])

    def test_preprocess_link_source_uses_compile_flags_before_source(self):
        command = {"argv": ["-O2", "-DMODE=1", "-I/inc", "/src/a.c", "/src/b.S",
                            "/obj/x.o", "-Wl,--gc-sections", "-o", "/out/app"],
                   "source_files": ["/src/a.c", "/src/b.S"]}
        result = preprocess_argv_for_link_source(command, "/src/b.S", "/trace/b.i", "/trace/b.d")
        self.assertEqual(result, ["-O2", "-DMODE=1", "-I/inc", "/src/b.S", "-E",
                                  "-MMD", "-MF", "/trace/b.d", "-MT", "/src/b.S", "-o", "/trace/b.i"])

    def test_link_compile_flags_after_first_source_fail_closed(self):
        command = {"argv": ["/src/a.c", "-DCHANGED=1", "-Wl,--gc-sections"],
                   "source_files": ["/src/a.c"]}
        with self.assertRaisesRegex(CompileTraceError, "compile flags after source"):
            preprocess_argv_for_link_source(command, "/src/a.c", "/trace/a.i", "/trace/a.d")


if __name__ == "__main__":
    unittest.main()
