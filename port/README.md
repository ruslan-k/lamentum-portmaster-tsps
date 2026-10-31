# port/

What goes on the SD card:

```
port/
  Lamentum.sh       launcher (SpruceOS Ports menu)
  port.env          runtime options (pad name)
  lamentum/         game directory, filled from the build output
```

After `build.sh`, `lamentum/` holds `Lamentum.apk`, `android_package.json`, `plugins.map`,
`Game_Data/`, and — added by hand from the player package and the IL2CPP output —
`lib/{libmain,libunity,libil2cpp}.so` plus `ua_host`.

The launcher switches to KMSDRM, stops MainUI (it holds the panel and the ALSA device), runs
`ua_host`, and brings MainUI back on exit. Log: `lamentum/log.txt`.

Environment: `SDL_AUDIODRIVER=alsa`, `AUDIODEV=plughw:0,0`, `UA_AUDIO_SINK=pipe` — one sink only,
two leave ALSA in `PREPARED` and the game is silent.
