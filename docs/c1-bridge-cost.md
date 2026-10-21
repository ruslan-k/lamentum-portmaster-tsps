# C1 — historical incomplete counters; performance verdict withdrawn

The original C1-svc-cost-01 instrument did NOT establish complete handler or bridge cost.
See [the C0 audit and validated replacement](c0-profiler-audit.md).

What is retained: build222 ran to TIME_LIMIT with 443 presentation log records and clean
cleanup. The old JSON is a reduction of last-emitted per-class TLS rows, not an all-thread
final report. It lacks sub-4096-call tails and loses TID when multiple threads report.

Consequently, the claims **"only one lock and zero unlocks", "1.98 ms per frame", "0.293% of
a core", "AudioOut/mutex bridge is not the bottleneck" and "C1 closed" are withdrawn**.
The older SVC log histograms are logged-call counts, not PC-sample occupancy; the raw PC
round-robin fractions remain unsuitable as CPU-time percentages.

The original instrumentation also skipped nested timing without removing child time from the
parent and clamped wall to CPU. A coarse monotonic clock was not demonstrated. Timing only
aout_dispatch excludes earlier operation waits, IPC parsing and the trap/kernel-mutex bridge.
No remainder can be attributed to BC/reclaim/Unity/Mali by subtraction from this report.

V2 now retains all registered thread generations and short-lived tails, records true nested
inclusive/exclusive intervals with independent raw clocks, reports invalid/in-flight/dropped
coverage and flushes explicitly before _exit. The exact rebuilt header passed host tests and
an independent self-authored CPU fixture on TSPS. This qualifies the collector, NOT the game's
performance or a full C0 profile. C0 stays open pending §29.5 and the G0/T1 combined run.
