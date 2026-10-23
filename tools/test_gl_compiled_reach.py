import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from gl_allocation_inventory import scan_source_tree, source_tree_identity
from gl_compiled_reach import (
    CompileReachError,
    analyze_trace_bundle,
    classify_callsite,
    classify_link_input,
    parse_preprocessed,
)


class GlCompiledReachTests(unittest.TestCase):
    def test_preprocessed_line_markers_track_original_paths_and_reordered_lines(self):
        text = '''
# 41 "/work/p/source/native/late.h"
active_late_call();
# 3 "/work/p/source/native/early.h"
active_early_call();
'''
        lines = parse_preprocessed(text, "/work/p/source")
        self.assertEqual(lines[("native/late.h", 41)], ["active_late_call();"])
        self.assertEqual(lines[("native/early.h", 3)], ["active_early_call();"])

    def test_macro_rewritten_callsite_is_compiled_reachable(self):
        site = {
            "path": "native/calls.h",
            "line": 7,
            "api": "glTexImage2D",
            "callee": "glTexImage2D",
        }
        result = classify_callsite(
            site,
            {"native/calls.h": {"native/unit.c"}},
            {("native/calls.h", 7): ["lc2_gl_tex_image2d_admit("]},
        )
        self.assertEqual(result["status"], "compiled-reachable")
        self.assertEqual(result["matched_tokens"], ["lc2_gl_tex_image2d_admit"])

    def test_api_name_in_string_literal_does_not_prove_call_compiled(self):
        site = {"path": "native/calls.h", "line": 7,
                "api": "glTexImage2D", "callee": "glTexImage2D"}
        result = classify_callsite(
            site,
            {"native/calls.h": {"native/unit.c"}},
            {("native/calls.h", 7): ['const char *s = "glTexImage2D(";']},
        )
        self.assertEqual(result["status"], "unknown")

    def test_absent_source_file_is_compiled_unreachable(self):
        site = {"path": "framework/nxgl_gles2.c", "line": 9,
                "api": "glBufferData", "callee": "nxgl_gles2_pfn_glBufferData"}
        result = classify_callsite(site, {}, {})
        self.assertEqual(result["status"], "compiled-unreachable")

    def test_included_but_preprocessed_out_callsite_remains_unknown(self):
        site = {"path": "native/conditional.h", "line": 12,
                "api": "glFramebufferTexture2D", "callee": "glFramebufferTexture2D"}
        result = classify_callsite(
            site,
            {"native/conditional.h": {"native/unit.c"}},
            {},
        )
        self.assertEqual(result["status"], "unknown")

    def test_indirect_dispatch_is_matched_by_its_function_pointer_callee(self):
        site = {"path": "framework/nxgl_dispatch.c", "line": 3,
                "api": "glBufferData", "callee": "nxgl_gles2_pfn_glBufferData",
                "dispatch": "indirect"}
        result = classify_callsite(
            site,
            {"framework/nxgl_dispatch.c": {"framework/nxgl_dispatch.c"}},
            {("framework/nxgl_dispatch.c", 3):
             ["nxgl_gles2_pfn_glBufferData(target, size, data, usage);"]},
        )
        self.assertEqual(result["status"], "compiled-reachable")
        self.assertIn("nxgl_gles2_pfn_glBufferData", result["matched_tokens"])

    def test_direct_source_is_link_input_without_claiming_live_section_retention(self):
        result = classify_link_input(
            {"native/loader.c"}, {"native/loader.c"}, {}, set(), archive_present=False
        )
        self.assertEqual(result["status"], "link-input-confirmed")
        self.assertEqual(result["units"], ["native/loader.c"])
        self.assertEqual(result["live_section_retained"], "unknown")

    def test_compiled_object_must_match_an_exact_final_link_input(self):
        result = classify_link_input(
            {"framework/nxgl/src/used.c"}, set(),
            {"framework/nxgl/src/used.c": "/build/used.o"},
            {"/build/used.o"}, archive_present=False,
        )
        self.assertEqual(result["status"], "link-input-confirmed")
        self.assertEqual(result["units"], ["framework/nxgl/src/used.c"])

    def test_unmapped_archive_member_remains_unknown(self):
        result = classify_link_input(
            {"framework/audio.c"}, set(),
            {"framework/audio.c": "/build/audio.o"},
            set(), archive_present=True,
        )
        self.assertEqual(result["status"], "unknown")

    def _make_bundle(self, tmp, source_text, preprocessed_text, dep_extra=""):
        root = Path(tmp)
        source_root = root / "source"
        (source_root / "native").mkdir(parents=True)
        (source_root / "framework").mkdir()
        (source_root / "native" / "unit.c").write_text("#include \"calls.h\"\nvoid unit(void) {}\n")
        (source_root / "native" / "calls.h").write_text(source_text)
        trace = root / "trace"
        trace.mkdir()
        container_source = "/work/project/source"
        container_trace = "/scratch/trace"
        dep_text = ("unit.o: /work/project/source/native/unit.c "
                    "/work/project/source/native/calls.h " + dep_extra + "\n")
        (trace / "unit.d").write_text(dep_text)
        pp = trace / "unit.i"
        pp.write_text(preprocessed_text)
        calls = scan_source_tree(source_root)
        identity = source_tree_identity(source_root)
        inventory = {"source_tree": identity, "call_sites": calls}
        policy = {"schema_version": 1, "source_tree_sha256": identity["sha256"],
                  "call_sites": [{"id": c["id"], "status": "unknown", "rationale": "fixture"}
                                 for c in calls]}
        inventory_path = root / "inventory.json"
        policy_path = root / "policy.json"
        inventory_path.write_text(json.dumps(inventory))
        policy_path.write_text(json.dumps(policy))
        command = {"kind": "compile", "argv": ["aarch64-linux-gnu-gcc", "-DMOMO_SHADERS=1",
                    "-I/work/project/source/native", "-c", "/work/project/source/native/unit.c"],
                   "source_files": ["/work/project/source/native/unit.c"]}
        link = {"kind": "link", "argv": ["aarch64-linux-gnu-gcc", "/work/project/source/native/unit.c", "-Wl,--gc-sections"], "source_files": ["/work/project/source/native/unit.c"]}
        (trace / "commands.jsonl").write_text(json.dumps(command) + "\n" + json.dumps(link) + "\n")
        record = {"translation_unit": "/work/project/source/native/unit.c",
                  "output": "/scratch/trace/unit.i", "returncode": 0,
                  "bytes": pp.stat().st_size,
                  "sha256": hashlib.sha256(pp.read_bytes()).hexdigest()}
        (trace / "preprocessed-summary.json").write_text(json.dumps([record]))
        (trace / "preprocessed-objects-summary.json").write_text("[]\n")
        replay = {"translation_unit": record["translation_unit"],
                  "dependency_file": "/scratch/trace/unit.d", "returncode": 0}
        (trace / "preprocess_replays.jsonl").write_text(json.dumps(replay) + "\n")
        return source_root, inventory_path, policy_path, trace, container_source, container_trace

    def test_trace_bundle_classifies_active_header_callsite_and_captures_flags(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = "void draw(void) { glTexImage2D(0,0,0,1,1,0,0,0,0); }\n"
            pre = ('# 1 "/work/project/source/native/unit.c"\n'
                   '# 1 "/work/project/source/native/calls.h" 1\n'
                   'void draw(void) { lc2_gl_tex_image2d_admit(0,0,0,1,1,0,0,0,0); }\n')
            args = self._make_bundle(tmp, source, pre)
            source_root, inv, policy, trace, cs, ct = args
            result = analyze_trace_bundle(source_root, inv, policy, trace, cs, ct)
            self.assertEqual(result["compiled_status_counts"], {"compiled-reachable": 1})
            self.assertEqual(result["link_input_status_counts"], {"link-input-confirmed": 1})
            self.assertEqual(result["call_sites"][0]["live_section_retained"], "unknown")
            self.assertTrue(result["trace"]["link_uses_gc_sections"])
            self.assertIn("MOMO_SHADERS=1", result["compiler_flags"]["defines"])
            self.assertIn("/work/project/source/native", result["compiler_flags"]["include_dirs"])

    def test_included_conditional_header_with_no_active_line_is_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = "#if ENABLE_DIAG\nvoid draw(void) { glFramebufferTexture2D(0,0,0,1,0); }\n#endif\n"
            pre = ('# 1 "/work/project/source/native/unit.c"\n'
                   '# 1 "/work/project/source/native/calls.h" 1\n')
            args = self._make_bundle(tmp, source, pre)
            result = analyze_trace_bundle(*args)
            self.assertEqual(result["compiled_status_counts"], {"unknown": 1})

    def test_trace_metadata_supplies_path_roots_and_effective_wrapper_flags(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = "void draw(void) { glTexImage2D(0,0,0,1,1,0,0,0,0); }\n"
            pre = ('# 1 "/work/project/source/native/unit.c"\n'
                   '# 1 "/work/project/source/native/calls.h" 1\n'
                   'lc2_gl_tex_image2d_admit();\n')
            args = self._make_bundle(tmp, source, pre)
            metadata = {"schema_version": 1, "container_source_root": args[4],
                        "container_trace_root": args[5], "wrapper_flags": ["-DTRACE_ONLY=1"]}
            (args[3] / "trace_metadata.json").write_text(json.dumps(metadata))
            result = analyze_trace_bundle(args[0], args[1], args[2], args[3], None, None)
            self.assertIn("TRACE_ONLY=1", result["compiler_flags"]["defines"])
            self.assertEqual(result["compiled_status_counts"], {"compiled-reachable": 1})

    def test_missing_dependency_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = "void draw(void) { glTexImage2D(0,0,0,1,1,0,0,0,0); }\n"
            pre = ('# 1 "/work/project/source/native/unit.c"\n'
                   '# 1 "/work/project/source/native/calls.h" 1\n'
                   'lc2_gl_tex_image2d_admit();\n')
            args = self._make_bundle(tmp, source, pre)
            (args[3] / "unit.d").unlink()
            with self.assertRaisesRegex(CompileReachError, "dependency"):
                analyze_trace_bundle(*args)

    def test_missing_command_trace_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = "void draw(void) { glTexImage2D(0,0,0,1,1,0,0,0,0); }\\n"
            pre = ('# 1 "/work/project/source/native/unit.c"\\n'
                   '# 1 "/work/project/source/native/calls.h" 1\\n'
                   'lc2_gl_tex_image2d_admit();\\n')
            args = self._make_bundle(tmp, source, pre)
            (args[3] / "commands.jsonl").unlink()
            with self.assertRaisesRegex(CompileReachError, "commands trace"):
                analyze_trace_bundle(*args)

    def test_unexpanded_response_file_flags_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = "void draw(void) { glTexImage2D(0,0,0,1,1,0,0,0,0); }\\n"
            pre = ('# 1 "/work/project/source/native/unit.c"\\n'
                   '# 1 "/work/project/source/native/calls.h" 1\\n'
                   'lc2_gl_tex_image2d_admit();\\n')
            args = self._make_bundle(tmp, source, pre)
            command_path = args[3] / "commands.jsonl"
            commands = [json.loads(line) for line in command_path.read_text().splitlines()]
            commands[0]["argv"].append("@/work/build/flags.rsp")
            command_path.write_text("\n".join(json.dumps(command) for command in commands) + "\n")
            with self.assertRaisesRegex(CompileReachError, "response file"):
                analyze_trace_bundle(*args)

    def test_changed_compiler_defines_fail_expected_trace_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = "void draw(void) { glTexImage2D(0,0,0,1,1,0,0,0,0); }\n"
            pre = ('# 1 "/work/project/source/native/unit.c"\n'
                   '# 1 "/work/project/source/native/calls.h" 1\n'
                   'lc2_gl_tex_image2d_admit();\n')
            args = self._make_bundle(tmp, source, pre)
            command_path = args[3] / "commands.jsonl"
            digest = hashlib.sha256(command_path.read_bytes()).hexdigest()
            analyze_trace_bundle(*args, expected_commands_sha256=digest)
            commands = [json.loads(line) for line in command_path.read_text().splitlines()]
            commands[0]["argv"][1] = "-DMOMO_SHADERS=0"
            command_path.write_text(json.dumps(commands[0]) + "\n" + json.dumps(commands[1]) + "\n")
            with self.assertRaisesRegex(CompileReachError, "command trace SHA-256"):
                analyze_trace_bundle(*args, expected_commands_sha256=digest)

    def test_stale_source_tree_identity_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = "void draw(void) { glTexImage2D(0,0,0,1,1,0,0,0,0); }\n"
            pre = ('# 1 "/work/project/source/native/unit.c"\n'
                   '# 1 "/work/project/source/native/calls.h" 1\n'
                   'lc2_gl_tex_image2d_admit();\n')
            args = self._make_bundle(tmp, source, pre)
            (args[0] / "native" / "calls.h").write_text(source + "/* changed */\n")
            with self.assertRaisesRegex(CompileReachError, "source tree"):
                analyze_trace_bundle(*args)


if __name__ == "__main__":
    unittest.main()
