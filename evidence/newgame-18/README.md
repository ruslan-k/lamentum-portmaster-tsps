# newgame-18 / build217: entry 44 links, the frontier moves to bb10c5c3

Facts: `NVN_LC2_PROGRAM_STAGES ... id=813 mask=1 sources=44/0 code-control-source=byte-exact` shows
entry 44 linked; the run then stopped with `ZERO_SHADER_NOT_PINNED` on code
`bb10c5c308ac2a145198a848f7a13ac9c2d510c02d208695c0dc5511adcf1c07` / control
`c28023ec007cc676bf9f5ad08db0a67053e04109679222c16f703f235fdaf540` (now entry 45). No
`LC2_SCENE_COLOR_VERTEX_GUARD` line was printed, so entry 44 was linked but not drawn.
Device after: game absent, MainUI back, principal/runtime unchanged, CPU mask `0-7`.
The guest-stack sampler never started (its 540 s delay was not reached before the stop).

Captures in this directory are agent-requested live kmsrab reads; inputs are evdev injection.
No gameplay, audio, save or FPS claim.
