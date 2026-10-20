# newgame-15 / build216: TIME_LIMIT inside the level load

Facts: stop `TIME_LIMIT`, 1469 presented frames, 1111 ROMFS_READ calls whose high-water end offset
reaches the full 1,832,059,520-byte container, 14 distinct catalogue program ids bound, zero
`LC2_SCENE_COLOR_VERTEX_GUARD` lines, zero unknown-shader requests, `cleanup_errors: []`.
Raw log is owner-local; its SHA-256 and byte size are pinned in summary.json.

Not proven here: gameplay, entry 44 at draw time, audio, save/load, or any FPS figure. Captures are
agent-requested kmsgrab reads of the live scanout, and input receipts state that presses are evdev
injection rather than physical human input.
