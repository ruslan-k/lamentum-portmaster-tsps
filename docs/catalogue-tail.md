# Visible-frame census, memory floor experiment and the shader tail

Status: NOT PLAYABLE. This round produced one real measurement that changes the
plan, one memory result, and a repeatable way to close the remaining shader tail.
No menu, input, audio or gameplay was reached.

## 1. The visible frame does not use the TEST substitutes

`LC2_PAIR_CENSUS=<frames>` (diagnostic, opt-in) counts the `(vertex, fragment)`
program pairs actually drawn. At frame 36 the visible frame drew 11 pairs:
16/19, 7/0, 18/1, 18/21, 10/13, 11/22, 17/4, 11/6, 11/9, 12/14, 2/23.

None of them is a TEST substitute (5, 26–31). So the remaining seven substitutes
were NOT the reason the picture was incomplete — a plan that assumed otherwise
would have spent days translating programs this frame never touches.

`LC2_PAIR_DETAIL=<vs>/<fs>` measured the two heaviest pairs:

- 17/4 (350 draws / 18 frames) writes eight targets, 640x360 down to 5x2, RGBA8,
  no depth, blend on, cull on — the bloom/mip chain, not scene geometry.
- 16/19 (one draw per frame) is the full-screen composite.

`LC2_SAMPLER_TRACE=<vs>/<fs>` resolved that composite's sampler: handle
`0x16000000820` → texture 56, 1000x1000, BC3 (0x44), one level, sampler 43,
neither texture nor sampler missing. The composite therefore samples a real BC3
image, and the dark rainy picture IS that decoded art — not a placeholder.

## 2. The scene is not reached because of our own memory floor

`T2_MEMORY_FLOOR_MIB=32` on the same configuration reached 575 texture
initializations and frame 321 before stopping on an uncatalogued shader, where
the 64-MiB floor had stopped at 328 textures / frame 124. This is not a rendering
regression or a speed claim: the run simply got further before the floor.
MemAvailable at the 64-MiB stop was 58–61 MiB, so the earlier wall was the floor,
not proven kernel OOM. `T2_MEMORY_FLOOR_MIB` remains a diagnostic setting; the
installed launcher keeps 96 MiB.

## 3. Shader tail: append, never regenerate

`build_lamentum_catalogue.py --placeholder` re-derives every entry from the
workspace and therefore REVERTS hand-validated work (the three real replacements,
the literal specialization, the guarded fragment). Measured: regenerating turned
7 TEST substitutes back into 9.

`tools/append_program.py` adds exactly one captured program, verifies the two
catalogue arrays agree on the program count, refuses a duplicate code hash, and
leaves every existing entry byte-identical (checked by diffing the prefix).

`tools/catalogue_cycle.py` closes the loop unattended: build → deploy (verified
SHA-256) → run with the memory configuration that reaches the scene → fetch the
dumped blobs → translate → append → repeat, stopping on any stop that is not
`ZERO_SHADER_NOT_PINNED`.

Programs added this way: index 34 `dump-ef14df61` (a solid-colour masked sprite
whose alpha test uses `demote`), 35 `dump-06993fc8`, 36 `dump-9fcf2f47`. The
catalogue is now 37 programs; each cycle costs roughly seven minutes and the run
still ends on the next uncatalogued program, so the tail is real and bounded only
by measurement — no count of remaining programs is claimed.

`demote;` (GL_EXT_demote_to_helper_invocation) has no ESSL 3.10 spelling. The
captured users write no derivatives and no outputs on that path, so it is lowered
to `discard;` and the extension directive is dropped; four regression tests cover
the inline-brace form and the untouched case.

## 4. Verification

- New host tests: `test_demote_lowering.py` (4), `test_append_program.py` (3),
  plus the existing sampler, literal, probe-guard, cbuf-unit, launcher, guest-quota
  and fileback suites.
- Builds 188–191 cross-build against the 435-file manifest-pinned baseline (build
  187 and 188 were compile failures of the append tool's text surgery and were
  never deployed).
- Installed runtime: build 191, SHA-256
  `4d379c0d816c32e50307f7ebe0ee0db24bea326ba87ea068c93b91b1d6d5fd54`, read back
  on the device; `lamentum-nextos.before-<tag>` keeps the previous binary.
- Device cleanup: no port process, MainUI=1, principal=1, runtime=1; the restored
  Spruce root menu is verified in `../evidence/cycle2-01/clean-menu.png`.

## 5. Next

The frontier is now purely "the title asks for a program the catalogue lacks", and
each answer is a measured capture rather than a guess. The seven TEST substitutes
stay listed but are demonstrably outside the visible frame, so they are not on the
critical path to a first menu. Input, audio and saves remain untouched.
