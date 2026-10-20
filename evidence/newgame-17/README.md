# newgame-17 / build217: the load runs past the guest governor

The title passed menu -> New Game configuration -> controls -> loading, then stayed on the load
screen while presenting ~1.14 frames/s at 0.836 s of main-thread CPU per frame with zero new
RomFS reads, textures or texel writes. The runtime's own 1800 s alarm never produced a
TIME_LIMIT stop; the run was ended by the operator and the device verified clean (game absent,
MainUI back, supervisors unchanged, CPU mask restored, fully lit Spruce menu captured).

No gameplay, audio, save/load or FPS result is claimed. Entry 44 was never drawn
(LC2_SCENE_COLOR_VERTEX_GUARD count 0) and no unknown shader was requested.
