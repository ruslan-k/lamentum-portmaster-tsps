# C2-bc-decode-01 — interrupted preliminary collection, not a completed BC cost result

Build223 was deployed and a 300 s principal-flow arm was started. The host collection was
interrupted. The retained `cost-final.json` is actually a preliminary snapshot at 319
presentation log records, with no STOP and no final harness return code. No final cleanup
or kernel receipt was saved for this arm. Later device state was observed after a reboot;
its retained game log cannot be assigned to the original run generation.

The old profiler emitted only after a per-thread threshold of 4096 calls and had no final
tail flush. Therefore absent `bc-decode` rows do NOT mean no BC calls or negligible BC cost.
The old `by[class]` reducer also discarded TID. Nothing here identifies a CPU bottleneck,
qualifies a Loading/world FPS result or closes roadmap C0.

See [the correction audit](../../docs/c0-profiler-audit.md) and
[the validated game-independent replacement fixture](../C0-profiler-validation/README.md).
Original preliminary files are retained for provenance, not promoted to a final result.
The new game ELF was built but not deployed or run as part of collector validation.
