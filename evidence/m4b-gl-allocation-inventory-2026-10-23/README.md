# M4-B allocation-source census and generation fixture (host + target; partial)

This is the first M4-B substep, not completion of the allocation-lifetime gate.

- Scanned the exact patched build262 source tree under `native/` and `framework/`: **390 C/C++ files**, source-tree SHA-256 `1b995ea13bab7aa2afcf865f68006b095a401c3cc71b8321f83c778a052dabfb`.
- Adapter baseline `c8d01ca1fed5adab1ae7ad920605f199bb83a72e`; overlay patch SHA-256 `6c549b09797a403390d4ced13e770bc35c65f74d70240a01f2ec77f6e258eba4`.
- Inventory: **77** storage/attachment/copy/EGL source callsites — 69 direct and 8 indirect. Categories: 38 texture-storage, 6 buffer-storage, 3 renderbuffer-storage, 23 framebuffer attachments, 3 texture-copy, 4 EGL surfaces.
- Classification: **12 wrapped+unmeasured**, **65 unknown**, zero wrapped+measured and zero not-reached. Unknown is explicit; no missing event is treated as no allocation.
- Generation history: table capacity **512 → 2,048**; tests cover 1,200 distinct-name create/reuse, **1,024 create/delete pairs**, **24** same-name reuses, and identical GLuints in distinct share groups. Full-capacity and `UINT64_MAX` refusals pass. New `generation_history_overflow` and `live_owner_overflow` counters distinguish history exhaustion from the unchanged 512-entry live owner/subresource tables; storage/delete event-ring overflow is also detected.
- Static size: `sizeof(lc2_life_events_state)` **155,504 → 200,576 B**; compiled AArch64 `.bss` **12,809,440 → 12,854,512 B** (**+45,072 B**). This is static section size, not measured RSS or CMA; no heap allocation was added.
- Added `tools/gl_allocation_inventory.py` and a pinned callsite policy. `build_lamentum.sh` runs the checker after applying the overlay and before compilation; source-tree or callsite drift fails closed. A synthetic unwrapped `glBufferData` regression test fails policy validation.
- Verification: inventory tests **7/7**, generation/lifetime tests **10/10**, full tools suite **370/370** with zero skips/failures/errors, baseline **435/435**, exact source-tree scan **77/77**, and patch/overlay byte equality pass. Pinned AArch64 build262: ELF64 PIE, **2,206,936 B**, Build ID `9395a24ac719269308b30476f8631349f47242a4`, max GLIBC **2.27**, SHA-256 `dd13d4ab300fdaa1f51acd78e105a55a02af1de6de05526328d2242b07da1cbc`; still uninstalled.

## Target-side generation fixture (not a game run)

- Cross-compiled a standalone fixture from the **build262 patched header** in the pinned AArch64 container: ELF64 PIE, **22,432 B**, Build ID `c173fc69d70fdce80890cda7781500e54217ffbf`, max GLIBC **2.17**, SHA-256 `f4da9806df30504a946ac7af45191451ff4564237be854744781b18b3978a2fa`.
- On Longan/SpruceOS (aarch64, firmware **1.0.1**, kernel **5.15.147**, glibc **2.33**) the fixture exited **0** in **0.183 s** and printed `LAMENTUM_GEN_DEVICE_FIXTURE PASS cap=2048 churn=1024 reuse=24 share_groups=2 history_overflow=1 live_owner_overflow=1 ring_overflow=1`. It exercised 1,024 create/delete pairs, 24 same-name reuses, identical GLuints in two share groups, full-history and `UINT64_MAX` refusal, distinct owner/history overflow, and event-ring overflow.
- The copied test ELF hash was read back, then the temporary `/tmp` executable was removed and absence verified. MainUI stayed present; no game or pending principal command appeared; CPU mask stayed `4-7`; the installed build259 runtime hash remained `d72e2f69afa16dd5b846950f3fba80bc9926edcab9b2d45c57ed23faa14b9066`.
- Two complete same-boot read-only snapshots, **44.009 s** apart, showed `CmaFree=130,412 KiB` both times, `MemAvailable=703,500→704,048 KiB`, `SwapFree=2,065,884 KiB` unchanged, no CMA-allocation-failure or major-fault/swap-I/O deltas, no filtered kernel allocation/OOM warnings, and 31 free CMA order-10 blocks. These are point-in-time allocator observations, not a guarantee of any future request.
- This validates the generation logic on the target CPU only; **build262 was not installed or launched as a game**. `t2_storage_admit()` fails closed when `T2_STORAGE_MARGIN_MIB` is unset, and the current launcher leaves it unset. I did not introduce a per-run margin without explicit authorization, so the D game-runtime test remains held.

## Limits and next work

The source census remains a source-tree superset; exact compiler-unit/include-closure reachability is not yet classified. The inventory and standalone generation fixture do not prove game-runtime call reach, buffer/EGL backing, allocation success, driver residency, physical CMA or memory refunds. Build262 remains uninstalled. A fresh read-only preflight and target CPU fixture were completed, but no game runtime was launched because `T2_STORAGE_MARGIN_MIB` remains unset; follow roadmap §15 before any staged D run and require explicit approval before adding a per-run margin. The port remains **NOT PLAYABLE**; no gameplay FPS is verified.

Next M4-B work: exact compiler-unit/include closure and callsite reachability; context teardown/recreation epochs; full alias/view, transactional re-spec/delete and deferred-completion cases; buffer/EGL owner-generation accounting; then the separated owner/memory-class waterfall. Keep logical, requested, process, driver and physical-CMA bases distinct.

Machine-readable source census and per-callsite dispositions are in [`summary.json`](summary.json); the reviewed policy used by builds is [`tools/gl_storage_callsite_policy.json`](../../tools/gl_storage_callsite_policy.json).

## Current source refresh after H2a alias telemetry (2026-10-23)

The checked-in `summary.json` has been regenerated against the current 390-file source tree (SHA-256 `3fcc9e78155ecdfd71507e860c5120d313a6a2d81967eed2ece572215cf38689`) and adapter overlay (SHA-256 `5ab2d36f5dcb1fdc275bfcaa55b9be8cfcc2dace10044bc9c932f5083a0dee62`). It still reports **77** sites with **12 wrapped+unmeasured / 65 unknown**. The build262 ELF and 370/370 suite listed above are historical artifacts from the earlier M4-B generation-history step, not builds from this new digest. Current verification is recorded in [H2a/D0](../m4b-h2a-alias-d0-2026-10-23/README.md): host suite **405/405**, zero skips; no game ELF/device launch.
