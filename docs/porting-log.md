# Porting log — Lamentum on TSPS

One entry per bounded device run. Facts only: what was deployed (hash), what the runtime
logged, which controlled stop ended the run, and how the device was left.

## 2026-10-19 — bring-up preparation (host side)

| Step | Result |
|---|---|
| NSZ base v0 -> NSP -> NCA | Program NCA 1,866,153,984 B; title keys added for `0100EC901551C000`/`…C800` |
| NSO extraction | `rtld` 6,304+3,384+664 B, `main` 30,836,964 B text, `subsdk0` 3,492,064 B text, `sdk` 5,777,024 B text |
| RomFS | one section file 1,829,445,184 B, SHA-256 `56a6e97124aed316cb123fe79f1711b6d6de37168fdbdbb057e1be513f386d0b`, `hactool -t romfs --listromfs` lists 34 files |
| Owner image | padded container: 0x200 zero header + RomFS (`romfs_offset=0x200`, `romfs_size=1829445184`, section SHA-256 `14f832e8e92e4377284f5f72679fd17932473f11248f132c5fc2ea5c414340b9`) |
| Baseline | terminator2d release sources applied cleanly; 435/435 manifest entries match |
| Adapter patch | 2 files / 8 lines (helper hoisting + declaration) |
| Build 01 | failed: `-Werror` on the baseline's own `write()` diagnostics and unused helpers in the pinned gcc 9.4 container |
| Build 02 | failed: `ZERO_ZX_GAME` undeclared / helpers unreachable outside the ZX profile / `type-limits` from `romfs_offset=0` |
| Build 03 | **ok** — `lamentum-nextos` 1,808,328 B, SHA-256 `9265c9e3d77d83341a83d5f9ea4bca2fc05c42f67092f3d4205be790bfe61bb9`, GLIBC ≤ 2.27 (base v0 content, superseded) |
| Update merge | `hactool --basenca … --exefsdir/--romfsdir` and `--section1=` produce the merged content: `main` 23,861,213 → 23,878,177 B, `main.npdm` changed, 11 RomFS files changed. Merged section dump 1,832,059,520 B; its own extraction is byte-identical to the merged tree (34/34 files) |
| Merged image | 0x200 pad + merged RomFS → section SHA-256 `80ad4427164a0b7ad61c3a3fcd955bd158635aac1ee42ebb67d01dfae279b893` (1,832,060,032 B) |
| Build 04 | **ok** — merged-content ELF `lamentum-nextos` 1,808,328 B, SHA-256 `9332846797605be9404ea814b54b06aaf3d64cd470a93550b2051c73b90e1a79` |

Open questions this build does not answer: which NVN structure profile this SDK generation
actually uses, whether the guest survives to its first `ProgramSetShaders`, and what the
runtime's first controlled stop is on real hardware.
