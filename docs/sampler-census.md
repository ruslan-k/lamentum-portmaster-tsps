# M1: generic sampler preparation census before lifetime changes

Reviewed 0896412 / owner §48.5. This packet uses build241 unchanged; no new
runtime/storage/quality/admission/alias policy. LC2_STORAGE_PROBE=0,
T2_DRAW_TEXTURE_EVERY=1, strict GL, floor96, texture cap300. Principal launch,
65-second runtime budget and independent harness bound; no input injection.

## Device result

Owned run a0b66728-3a1e-4296-91b9-4b93a8efcdb6, PID15458/start2146607,
ELF b4c8df27e5c9ea18d2dac8a13f563863844b2e311d6ee0282256923e488c47e5.
The complete final log has 630 generic sampler-preparation records, frames1..13,
30 observed sampler NVN IDs, 17 distinct target IDs on those records. NVN81 and
NVN92 have zero records as sampler IDs or as targets on those sampler records.
Both do have direct-write/source-update receipts in this run:

- 81: 3600x2160, 7776000 native bytes.
- 92: 3600x3600, 12960000 native bytes.

Examples of positively observed users: NVN82 (1032x1122) has65 bindings,
NVN84 (800x450) has26; NVN172 is sampled26 times and also occurs as a target.
These counts are sampler events, NOT draws or FPS, and roles are not storage
charges. All per-ID counts/frames/pairs/targets are in census.json.

Runtime STOP T2_MEMORY_FLOOR, final present13. Harness returns4 (guest stop),
cleanup_errors=[], identity_errors=[], execution_verified=true; no OOM receipt.
No cross-run headroom/FPS improvement is claimed from a later stop than §63:
observer settings differ and repeated controls are absent.

## What this does NOT prove

T2_DRAW_TEXTURE is emitted in generic sampler/uniform preparation in nvn_render.h,
before eventual draw submission. Alternate specialized draw paths, CPU views,
backing-storage aliases, GL generations, EGL share groups and in-flight readers
are NOT completely traced. A zero ID count is not proof of no resource consumer,
immutable content, reclaimability or completion. Target IDs are only targets of
recorded sampler events, NOT a complete render-target census.

Guest finalize and actual GL-delete outcomes are not covered by this diagnostic;
source audit locates finalize at NI_nvnTextureFinalize with existing finish/flush
policy, zero_texture_storage_release and glDeleteTextures. None of these prove
physical refund without a matching generation/counter receipt. No deletion,
extra glFinish, lazy-storage change or speculative release was introduced.

Next implementation requirement remains §48.5's creation/storage generation ->
alias-resolved reader -> real completion -> retirement ledger. This result only
narrows a possible startup-eager-materialization question. Do not free81/92 or
claim 84.69 MiB recoverable by adding earlier bracket sizes.

## Reproducible tool / cleanup

New offline tools/sampler_census.py parses only newline-complete events, preserves
order, rejects frame regression/missing/duplicate/invalid numeric fields, keeps
sampler and target roles separate and explicitly reports absence_proves_unused=false,
physical_refund_bytes=null, fence_completion=unobserved. This tool is not an owned
navigation collector; use it only after the harness's run/log verification.
Six red/green regressions, entire host suite264 PASS in a clean index export.
Runtime patch is unchanged, so build241's prior435 baseline/clean PT_LOAD check
applies; no new runtime build is claimed.

Independent post-run snapshot: game0, MainUI1, principal1, runtime1, CPU4-7;
pending launch absent, debugfs remains unmounted. KMS final-menu.png visibly shows
Spruce home (cleanup only). Raw full log and kernel receipts stay owner-local;
published hashes, exact filtered sampler records and harness receipts bind results.
