# newgame-12: build213 functional shader-tail test

New Game and controls continuation are visually reviewed with live PID/starttime capture receipts.
The run ends on ZERO_SHADER_NOT_PINNED at present serial 516, not gameplay.
See summary.json for the next exact code/control hashes, raw-log SHA and sampled memory minimum.
No new program39/40 draw-guard receipts occurred before the setup stop.

Cleanup passes: game absent, supervisors retained, CPU mask restored. clean-menu.png
shows the actual Spruce Recents menu after a D-pad wake (cleanup-wake.json); it is NOT game imagery.

The run differs in input latch hold floor (120 vs 700 ms), so it is not a same-condition
rendering-performance comparison. Original saves, game blobs and full logs remain owner-local.
