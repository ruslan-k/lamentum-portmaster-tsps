# M4-B H1 compile-reach trace checkpoint (partial)

This is a host-only compiler-closure measurement for the exact patched build262 source tree. The analyzer and 14 regression tests now reproduce the 77-site classifications; H1 remains partial because the trace-capture wrapper/materializer is still local-only and eight sites remain explicitly unknown.

## Captured build

- Pinned container image ID: `sha256:e437308c01ce7af4a035c3f0652bc886e258889f66803f805bce53d05af75f0c` (`pmjs-arm64-spruce-local:20261002-gcc10`). Actual compiler output: `aarch64-linux-gnu-gcc 9.4.0`, target `aarch64-linux-gnu`.
- Source base `c8d01ca1fed5adab1ae7ad920605f199bb83a72e`; 390-file patched tree SHA-256 `1b995ea13bab7aa2afcf865f68006b095a401c3cc71b8321f83c778a052dabfb`; overlay SHA-256 `6c549b09797a403390d4ced13e770bc35c65f74d70240a01f2ec77f6e258eba4`.
- Trace build completed and passed the baseline, patch, and 77-site inventory gates. It recorded **36 compiler invocations** (**35 compile + 1 final link**) and **45 source translation units** (**43 C, 2 assembly**); all 45 per-unit dependency/preprocessor records completed across **275** project dependency paths. The captured effective flags include **11 `-I` paths** and **5 `-D` definitions**. The final link contains 32 object files plus one archive and uses `--gc-sections`; no per-function section-retention proof is available.
- Trace-build ELF: AArch64 PIE, max GLIBC **2.27**, SHA-256 `54d280b9ca7c76b1417f80ffc9480b632ef55b29524138b59fea9fd4c3e07026`. This is a trace-only local artifact, **not** build262 and not installed.

## Preliminary site mapping

The 77 source candidates were joined to complete per-translation-unit dependency files and preprocessed output using source path + original line + API/callee (including known GL admission macro replacements):

- **58 compiled-reachable**: exact source line and API/callee or known wrapper token appear in active preprocessed output.
- **11 compiled-unreachable**: source files appear in no direct compilation unit or per-unit dependency closure (8 `framework/nxgl/src/nxgl_gles2.c` dispatcher candidates plus 3 header callsites).
- **8 unknown**: source file is in the compile closure, but its exact callsite line was not found in preprocessed output. Keep these unknown; do not treat mere header inclusion as reachability.

The final-link input axis separately confirms **66** site paths through `native/loader.c` as a direct source input; the **11** absent sites are not link inputs. Because the link uses `--gc-sections`, this does **not** prove individual functions/sections survived the link. The machine-readable receipt records all 77 source/compile/link-input dispositions, each with its proof and translation units. The original source policy remains unchanged: **12 wrapped+unmeasured, 65 unknown**.

The 16 focused tests and full host suite **386/386** pass. They cover changed command flags, unexpanded response-file refusal, stale source identity, missing command/dep files, macro rewrites/string-literal rejection, conditional code kept unknown, indirect dispatch, reordered preprocessor line markers, and link-input versus post-GC retention. The trace analyzer is in `tools/gl_compiled_reach.py`; however, the wrapper/materializer that produced this exact raw trace remains local-only, so H1 is not yet fully reproducible from the repository alone.

## Remaining H1 work

Commit the trace-capture/materialization path, rerun it against the same pinned build identity, and reproduce the receipt from that tracked trace. Then keep the eight unknowns explicitly unknown unless guard/line evidence resolves them. Per-function section retention, runtime execution, driver allocation, and physical backing remain separate future evidence.