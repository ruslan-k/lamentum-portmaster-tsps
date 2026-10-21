# menu-ledger-02: per-class attribution of the menu loss

Build231 `41d6b4f8…c682` (435/435), deployed with a `.before-231` backup. One arm
with `LC2_MENU_LEDGER=1`, strict GL, 300 MiB texture budget, diagnostic floor 32 MiB:
`T2_MEMORY_FLOOR` stop, verified identity, zero cleanup errors.

- `attribution.json` — start/low values per class and the numbers quoted in
  `docs/menu-class-attribution.md`.
- `ledger-lines.txt` — the raw `LC2_MENU_LEDGER` records.

At the low point (frame 31): available 50.5 MiB (−76.3), CmaFree 0.83 MiB (from
27.3), game VmSwap 407.4 MiB, charged textures 157.3 MiB (+50.1), colour targets
19 (+3, +15.9 MiB estimate), depth renderbuffers 2 / 22.9 MiB **constant**, and
`scaled`/`half`/`bc-pending`/`joined` all zero.

Every class figure is a format-defined estimate from adapter state, not Mali
residency; `buffers`, `egl-surfaces` and driver-retained storage stay untracked.
