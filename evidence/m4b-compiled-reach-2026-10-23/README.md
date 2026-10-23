# M4-B H1 compile/link-input reach audit (host phase complete)

H1 is complete at the **compiler/preprocessor and final-link-input** scope for the exact patched build262 source tree. The tracked wrapper, per-translation-unit materializer, analyzer, and tests regenerated and reproduced the 77-site receipt from build265. The eight line/token mismatches remain explicitly `unknown`; `--gc-sections` retention and all runtime/backing claims remain outside this phase.

## Captured build

- Pinned container image ID: `sha256:e437308c01ce7af4a035c3f0652bc886e258889f66803f805bce53d05af75f0c` (`pmjs-arm64-spruce-local:20261002-gcc10`). Compiler: `/usr/bin/aarch64-linux-gnu-gcc-9`, version `aarch64-linux-gnu-gcc 9.4.0`, target `aarch64-linux-gnu`.
- Source base `c8d01ca1fed5adab1ae7ad920605f199bb83a72e`; 390-file patched tree SHA-256 `1b995ea13bab7aa2afcf865f68006b095a401c3cc71b8321f83c778a052dabfb`; overlay SHA-256 `6c549b09797a403390d4ced13e770bc35c65f74d70240a01f2ec77f6e258eba4`.
- Tracked compiler wrapper/materializer regenerated the trace in the pinned container. Baseline manifest: **435/435**; patched source tree: 390 files, SHA-256 `1b995ea13bab7aa2afcf865f68006b095a401c3cc71b8321f83c778a052dabfb`; adapter overlay: `6c549b09797a403390d4ced13e770bc35c65f74d70240a01f2ec77f6e258eba4`.
- It recorded **36 compiler invocations** (**35 compile + 1 final link**) and **45 source translation units** (**43 C, 2 assembly**); all per-unit dependency/preprocessor records completed across **275** project dependencies. Effective flags: **11 `-I` paths**, **5 `-D` definitions**, no response files. The link included 32 objects plus one archive and used `--gc-sections`.
- Trace-build ELF: AArch64 PIE, **2,206,936 B**, Build ID `5c60e42b66321320580fb62e1801dd7ffa27b266`, max GLIBC **2.27**, SHA-256 `278612aab77012c09c3287f8e21a7fbb81dec3abea9eb81af60f6cba82e68b54`. This build265 trace artifact is **not installed** and is not a gameplay result.

## Site dispositions

The 77 source candidates were joined to complete per-translation-unit dependency files and preprocessed output using source path + original line + API/callee (including known GL admission macro replacements):

- **58 compiled-reachable**: exact source line and API/callee or known wrapper token appear in active preprocessed output.
- **11 compiled-unreachable**: source files appear in no direct compilation unit or per-unit dependency closure (8 `framework/nxgl/src/nxgl_gles2.c` dispatcher candidates plus 3 header callsites).
- **8 unknown**: source file is in the compile closure, but its exact callsite line was not found in preprocessed output. Keep these unknown; do not treat mere header inclusion as reachability.

The final-link input axis separately confirms **66** site paths through `native/loader.c` as a direct source input; the **11** absent sites are not link inputs. Because the link uses `--gc-sections`, this does **not** prove individual functions/sections survived the link. The machine-readable receipt records every site, proof, and translation unit; the regenerated site-status delta versus the initial H1 receipt is **0**. The original source policy remains unchanged: **12 wrapped+unmeasured, 65 unknown**.

The 26 focused H1 tests and full host suite **396/396** pass. They cover source identity, compiler-flag changes, unexpanded response-file refusal, missing command/dep files, macro rewrites/string-literal rejection, conditional code kept unknown, indirect dispatch, reordered line markers, direct link inputs, and explicit post-GC uncertainty. The tools are `tools/cc_trace_lamentum.py`, `tools/gl_compiled_reach_trace.py`, and `tools/gl_compiled_reach.py`.

## Reproduction and remaining M4-B work

For a fresh, non-executing host trace, set `COTM_CC=/work/tools/cc_trace_lamentum.py`, `COTM_TRACE_DIR` to a new mounted trace directory, and `COTM_TRACE_SOURCE_ROOT` to the new build's patched `source/` path; run the normal `build_lamentum.sh` in the pinned container, then `python3 tools/gl_compiled_reach_trace.py materialize --trace-dir "$COTM_TRACE_DIR"`. `tools/gl_compiled_reach.py` reads the path roots and wrapper flags from `trace_metadata.json`; pass the recorded command SHA when reproducing a published receipt. Raw command/dependency/preprocessed files remain local; only the compact receipt is committed.

Next M4-B work is H2 transactional storage/lifetime coverage, then buffer/EGL owner accounting and the separate memory-class waterfall. Per-function section retention, runtime execution, driver allocation, and physical backing remain unknown; no device action or game run occurred.