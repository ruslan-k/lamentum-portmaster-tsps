# Current-source ELF staging and D preflight — 2026-10-23

## Inert staging verified

On the same Longan boot (`15b97fe4-5c48-412c-ba39-92efb1823286`, firmware `1.0.1`, kernel `5.15.147`), an S-only check found one MainUI (`PID 2369`, starttime `1079`), the principal supervisor (`PID 2196`, starttime `1023`), no game process, and no `/tmp/cmd_to_run.sh`. The active build259 ELF remained SHA-256 `d72e2f69afa16dd5b846950f3fba80bc9926edcab9b2d45c57ed23faa14b9066`; launcher hash was `f32204ff1b271dd66e38f79573f75c6f562af49174ea436e81dd9417dba1354a`. SD free space before copy: **3,323,133,952 bytes**.

The refreshed host ELF and paired helper were copied to the inert hidden path `/mnt/SDCARD/Roms/PORTS/lamentum-switch/.candidate-h2a-20261023/`. Readback verified:

- candidate ELF: **2,203,096 bytes**, SHA-256 `c46714403f22074d92710192d1164cfe0b7a4f62f1a4890ffb7a1e224c542332`;
- helper: **8,310 bytes**, SHA-256 `abe8e4847b18a750c0796af33d887cf43714126c9751ccdc8236715cb752401a`;
- the staged directory contains exactly those two files and no launcher; active build259, launcher, and ROMFS section were not overwritten.

The existing device `lamentum-romfs.section` is **1,832,060,032 bytes**. Its read-only SHA-256 check matched the local owner-image section exactly: `80ad4427164a0b7ad61c3a3fcd955bd158635aac1ee42ebb67d01dfae279b893`. The target-side sequential read took **33.379 s**; no device file was written by the hash operation.

## Fresh D preflight and hold

The bounded `cma_readonly_snapshot.py` / `cma_readonly_compare.py` pair **before** the section hash was complete and stable:

- `11:05:29.659Z` → `11:05:55.338Z`, same boot; `CmaFree=130,412 KiB` both times, `MemAvailable=671,620→671,916 KiB`, `SwapFree=2,065,884 KiB` unchanged;
- CMA success/fail counters stayed `8/0`; `nr_free_cma=32,603`; 31 free CMA order-10 blocks; MainUI identity and DMA-FD set unchanged; no game process.

The next complete same-boot pair, **after** hashing the 1.83 GB section, showed a substantially different allocator state:

- `11:09:25.644Z` → `11:09:51.320Z`; `CmaFree=532→576 KiB`, `MemAvailable=669,640→669,720 KiB`, `Cached=578,624→578,652 KiB`, `SwapFree=2,065,116 KiB` unchanged within the pair;
- `nr_free_cma=133→144`; CMA success/fail remained `8/0`, no swap-in/out, no compaction or migration delta in this pair; complete CMA page-type histogram but **no free CMA blocks at orders 7–10**;
- MainUI PID/starttime/executable and DMA-FD set remained stable; no game process.

After a further **60.694 s** idle interval, another complete pair stayed low: `CmaFree=604 KiB` both samples, `nr_free_cma=151` both, no order-7-or-higher CMA blocks, `MemAvailable=671,244→670,800 KiB`, `SwapFree=2,065,116 KiB` unchanged. The `11:18:54.911Z` read likewise showed `604 KiB`; it was a single gauge, not a full pair. A fresh read-only pair at `11:32:56.701Z→11:33:32.568Z` was complete on the same boot and still showed `CmaFree=608 KiB` both times, `nr_free_cma=152` both, `MemAvailable=660,428→664,040 KiB`, `Cached=579,092 KiB` unchanged, and `SwapFree=2,065,116 KiB` unchanged. Its CMA histogram had zero order-7-or-higher blocks; CMA success/failure, swap, major-fault, compaction and migration counters were unchanged. MainUI identity/DMA-FDs and installed-runtime identity remained stable, with no game process. A fresh principal check at `11:33:55.118Z` confirmed no pending command and the same boot. A later **complete single snapshot** at `11:49:29.003Z` still showed `CmaFree=608 KiB`, `MemAvailable=663,068 KiB`, `SwapFree=2,065,116 KiB`, `nr_free_cma=152`, no CMA order-7-or-higher blocks, one stable MainUI (`2369/1079`), no game process, and six global DMA-BUFs from exporter `system`; the active runtime identity census was readable. A separate check at `11:49:29.745Z` found no pending principal command. This is a single current snapshot, **not** another D pair; the latest complete pair remains 11:32:56–11:33:32Z. The filtered dmesg check after the section hash found no OOM/page-allocation/CMA-failure warning lines; it has not been repeated for these later checks.

**Important observed association:** between the pre-hash and post-hash pairs, `Cached` rose from `145,640` to `578,624 KiB` while `CmaFree` fell from `130,412` to `532 KiB`. This followed the large read-only ROMFS hash. It is a correlation, not proof that those file-cache pages occupied CMA. No `drop_caches`, compaction, sysfs policy change, reboot, or game launch was attempted. I will not repeat the large section scan during this test sequence.

**D decision: HOLD_RUNTIME.** The latest complete same-boot pair is still about 0.6 MiB `CmaFree`, with no high-order CMA blocks; passive idle sampling did not recover the post-read state. The candidate is staged but inert; `T2_STORAGE_MARGIN_MIB` remains unset. Do not launch from this state. Re-evaluate only after passive recovery is independently observed and actual GL/DMA-BUF demand plus uncertainty are reviewed; no New Game or FPS claim.

Raw snapshot JSON, comparisons, and device command output remain local-only under Hermes scratch. The staged candidate is the only device write from this phase; active runtime/launcher/helper and owner section remain unchanged.

**Subsequent read-only follow-up:** this phase's 11:32Z recovery pair and 11:49Z single sample are superseded as the latest measurements by the complete 12:11Z pair and owner/debugfs audit in [K1-F](../k1f-cma-owners-debugfs-2026-10-23/README.md). It remained at `CmaFree=608 KiB`, with no order-7+ blocks; no game or lifecycle action occurred.

## Candidate launcher prepared (host-verified; device copy pending S gate)

`candidate-Lamentum.sh` is the candidate-specific launcher for the hidden directory. It keeps the production asset working directory but resolves the ELF/helper/log under `.candidate-h2a-20261023`, so it cannot run build259 or overwrite the production log. It is not placed at a PortMaster-discovered root path. It makes no `/sys` writes or CPU hotplug changes, fixes the no-input window at 30 seconds, pins `T2_MEMORY_FLOOR_MIB=96`, `T2_TEXTURE_BUDGET_MIB=300`, strict GL, synchronous queue, pageout off and BC medium stripe off; it does not assign a storage margin. SHA-256 `1a90c4efc55074d2d6ae4ac51134522e1cc7ac33cca6025ccb14d269715c18a7`, size 1,773 bytes, mode 0755.

Host validation: `bash -n` passed. `tools/test_launcher.py` exercised the candidate launcher with the real `run_identity.py` helper and a fake ELF, verified the emitted launcher/helper/ELF hashes, confirmed unsafe inherited overrides do not relax the fixed guards, and confirmed the fake runtime's exit status propagates. The focused admission/launcher set passed 18 tests; the complete tools suite passed 406 tests. **This launcher has not yet been copied to the device**; it remains an S-stage operation pending a fresh storage/busy-state/identity check and readback. The D runtime gate is still held.
