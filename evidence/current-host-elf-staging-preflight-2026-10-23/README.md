# Current-source ELF staging and D preflight — 2026-10-23

## Inert staging verified

On the same Longan boot (`15b97fe4-5c48-412c-ba39-92efb1823286`, firmware `1.0.1`, kernel `5.15.147`), an S-only check found one MainUI (`PID 2369`, starttime `1079`), the principal supervisor (`PID 2196`, starttime `1023`), no game process, and no `/tmp/cmd_to_run.sh`. The active build259 ELF remained SHA-256 `d72e2f69afa16dd5b846950f3fba80bc9926edcab9b2d45c57ed23faa14b9066`; launcher hash was `f32204ff1b271dd66e38f79573f75c6f562af49174ea436e81dd9417dba1354a`. SD free space before copy: **3,323,133,952 bytes**.

The refreshed host ELF and paired helper were copied to the inert hidden path `/mnt/SDCARD/Roms/PORTS/lamentum-switch/.candidate-h2a-20261023/`. Readback verified:

- candidate ELF: **2,203,096 bytes**, SHA-256 `c46714403f22074d92710192d1164cfe0b7a4f62f1a4890ffb7a1e224c542332`;
- helper: **8,310 bytes**, SHA-256 `abe8e4847b18a750c0796af33d887cf43714126c9751ccdc8236715cb752401a`;
- at the initial ELF/helper-only stage, the hidden directory contained exactly those two files and no launcher; active build259, launcher, and ROMFS section were not overwritten.

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

**Initial D decision (11:32–11:33Z): `HOLD_RUNTIME`.** That complete pair was about 0.6 MiB `CmaFree` with no high-order CMA blocks. It is now superseded by the [post-stage D receipt](../d-preflight-poststage-2026-10-23/README.md), which records the fresh 12:52Z pair. `T2_STORAGE_MARGIN_MIB` remains unset; no game or New Game run.

Raw snapshot JSON, comparisons, and device command output remain local-only under Hermes scratch. The initial stage wrote the ELF/helper into the hidden candidate directory; the later S phase added only `Lamentum.sh` there. Active build259, root launcher, and ROMFS section remain unchanged.

**Subsequent read-only follow-ups:** K1-F's complete 12:11Z pair and owner/debugfs audit are recorded in [K1-F](../k1f-cma-owners-debugfs-2026-10-23/README.md). The newer post-stage 12:52Z pair and interpretation are in the [post-stage D receipt](../d-preflight-poststage-2026-10-23/README.md); neither establishes recovery, a leak, or a safe runtime reserve.

## Candidate launcher (host-verified; S readback verified, not run)

`candidate-Lamentum.sh` is the candidate-specific launcher for the hidden directory. It keeps the production asset working directory but resolves the ELF/helper/log under `.candidate-h2a-20261023`, so it cannot run build259 or overwrite the production log. It is not placed at a PortMaster-discovered root path. It makes no `/sys` writes or CPU hotplug changes, fixes the no-input window at 30 seconds, pins `T2_MEMORY_FLOOR_MIB=96`, `T2_TEXTURE_BUDGET_MIB=300`, strict GL, synchronous queue, pageout off and BC medium stripe off; it does not assign a storage margin. SHA-256 `1a90c4efc55074d2d6ae4ac51134522e1cc7ac33cca6025ccb14d269715c18a7`, size 1,773 bytes, mode 0755.

Host validation: `bash -n` passed. `tools/test_launcher.py` exercised the candidate launcher with the real `run_identity.py` helper and a fake ELF, verified the emitted launcher/helper/ELF hashes, confirmed unsafe inherited overrides do not relax the fixed guards, and confirmed the fake runtime's exit status propagates. The focused admission/launcher tests passed 18/18 at the launcher checkpoint; the later process-census changes passed 27/27 focused K1 tests, including a confirmed process-exit race during executable lookup; the full tools suite passed 413/413. The launcher was read back at `12:51:43.062604Z` with exact hash and executable mode. **It remains not run.** The fresh post-stage D pair is in [the D receipt](../d-preflight-poststage-2026-10-23/README.md); runtime remains held.
