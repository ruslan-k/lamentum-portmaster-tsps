import tempfile
import unittest
from pathlib import Path

from gl_allocation_inventory import (
    InventoryError,
    scan_source_tree,
    scan_text,
    source_tree_identity,
    validate_policy,
)


class GlAllocationInventoryTests(unittest.TestCase):
    def test_scans_storage_attachment_and_surface_calls_but_ignores_comments_and_literals(self):
        source = '''
// glBufferData(GL_ARRAY_BUFFER, 1, 0, GL_STATIC_DRAW);
const char *note = "glTexImage2D(";
/* eglCreatePbufferSurface(d, c, a); */
void setup(void) {
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 4, 4, 0, GL_RGBA, GL_UNSIGNED_BYTE, 0);
    real_glBufferData(GL_ARRAY_BUFFER, 32, 0, GL_STREAM_DRAW);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, 7, 0);
    eglCreatePbufferSurface(display, config, attributes);
}
'''
        calls = scan_text("native/example.c", source)
        self.assertEqual(
            [(c["api"], c["kind"], c["dispatch"], c["line"]) for c in calls],
            [
                ("glTexImage2D", "texture-storage", "direct", 6),
                ("glBufferData", "buffer-storage", "indirect", 7),
                ("glFramebufferTexture2D", "framebuffer-attachment", "direct", 8),
                ("eglCreatePbufferSurface", "egl-surface", "direct", 9),
            ],
        )

    def test_new_unwrapped_gl_bufferdata_callsite_fails_policy_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            native = root / "native"
            framework = root / "framework"
            native.mkdir()
            framework.mkdir()
            (native / "first.c").write_text(
                "void first(void) { glBufferData(GL_ARRAY_BUFFER, 32, 0, GL_STATIC_DRAW); }\n"
            )
            original = scan_source_tree(root)
            policy = {
                "schema_version": 1,
                "call_sites": [
                    {
                        "id": original[0]["id"],
                        "status": "wrapped+unmeasured",
                        "rationale": "fixture's known callsite",
                    }
                ],
            }
            validate_policy(original, policy)
            (native / "new.c").write_text(
                "void new_path(void) { glBufferData(GL_ARRAY_BUFFER, 64, 0, GL_STATIC_DRAW); }\n"
            )
            with self.assertRaisesRegex(InventoryError, "unclassified callsite"):
                validate_policy(scan_source_tree(root), policy)

    def test_policy_rejects_stale_callsite_and_missing_rationale(self):
        calls = []
        stale = {"schema_version": 1, "call_sites": [
            {"id": "native/removed.c|glBufferData|1", "status": "unknown", "rationale": "old"}
        ]}
        with self.assertRaisesRegex(InventoryError, "stale inventory callsite"):
            validate_policy(calls, stale)
        call = scan_text(
            "native/example.c",
            "void setup(void) { glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, 4, 4); }\n",
        )[0]
        missing_rationale = {"schema_version": 1, "call_sites": [
            {"id": call["id"], "status": "unknown", "rationale": ""}
        ]}
        with self.assertRaisesRegex(InventoryError, "rationale"):
            validate_policy([call], missing_rationale)

    def test_indirect_function_pointer_dispatch_is_counted_but_declarations_are_not(self):
        source = '''
extern void (*nxgl_pfn_glBufferData)(unsigned int, long, const void *, unsigned int);
static void nxgl_d_glBufferData(unsigned int target, long size, const void *data, unsigned int usage) { if (nxgl_pfn_glBufferData == 0) return; nxgl_pfn_glBufferData(target, size, data, usage); (*nxgl_pfn_glBufferData)(target, size, data, usage); }
'''
        calls = scan_text("framework/nxgl_dispatch.c", source)
        self.assertEqual(
            [(c["api"], c["dispatch"], c["line"]) for c in calls],
            [("glBufferData", "indirect", 3), ("glBufferData", "indirect", 3)],
        )

    def test_policy_is_bound_to_source_snapshot_even_when_calls_do_not_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            native = root / "native"
            framework = root / "framework"
            native.mkdir()
            framework.mkdir()
            (native / "alloc.c").write_text(
                "void allocate(void) { glBufferData(GL_ARRAY_BUFFER, 64, 0, GL_STATIC_DRAW); }\\n"
            )
            extra = framework / "context.h"
            extra.write_text("/* build identity */\\n")
            calls = scan_source_tree(root)
            identity = source_tree_identity(root)
            policy = {
                "schema_version": 1,
                "source_tree_sha256": identity["sha256"],
                "call_sites": [{"id": calls[0]["id"], "status": "unknown", "rationale": "fixture"}],
            }
            validate_policy(calls, policy, identity)
            extra.write_text("/* modified build identity */\\n")
            changed = source_tree_identity(root)
            self.assertEqual(identity["file_count"], 2)
            self.assertNotEqual(identity["sha256"], changed["sha256"])
            with self.assertRaisesRegex(InventoryError, "source tree SHA-256 mismatch"):
                validate_policy(scan_source_tree(root), policy, changed)

    def test_build_recipe_scans_inventory_after_overlay_apply_and_before_compilation(self):
        recipe = Path(__file__).resolve().parents[1]
        build_script = (recipe / "build_lamentum.sh").read_text()
        self.assertIn("gl_allocation_inventory.py", build_script)
        apply_pos = build_script.index('git -C "$work" apply "$recipe/runtime/lamentum-adapter.patch"')
        inventory_pos = build_script.index("gl_allocation_inventory.py")
        compile_pos = build_script.index('bash "$work/native/build.sh" "$image" "$output/native-build"')
        self.assertLess(apply_pos, inventory_pos)
        self.assertLess(inventory_pos, compile_pos)
        self.assertIn('--source-root "$work"', build_script)
        self.assertIn('--policy "$recipe/tools/gl_storage_callsite_policy.json"', build_script)

    def test_tree_scan_requires_both_source_roots_and_uses_relative_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "native").mkdir()
            (root / "framework").mkdir()
            (root / "native" / "alloc.h").write_text(
                "void allocate(void) { glBufferStorage(GL_ARRAY_BUFFER, 64, 0, 0); }\n"
            )
            calls = scan_source_tree(root)
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["path"], "native/alloc.h")
            with self.assertRaisesRegex(InventoryError, "framework"):
                scan_source_tree(root / "native")


if __name__ == "__main__":
    unittest.main()
