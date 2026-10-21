# nav-oracle-01: in-run frames for the page oracle

One bounded principal arm on build229 (`COTM_GL_ERROR_IGNORE=0`,
`T2_TEXTURE_BUDGET_MIB=300`, diagnostic floor 32 MiB): 30 presents, 27 with pixels,
`T2_MEMORY_FLOOR` stop, clean cleanup, verified run identity.

Two kmsgrab frames were taken **during** the run (owner-local, not committed):
`nav-oracle-01-00.png` (boot, 2,759 B) and `nav-oracle-01-01.png` (main menu,
138,730 B). `oracle-real-frame.json` holds the oracle verdicts, the measured menu
geometry and the navigator action derived from them.

Measured geometry (this build): rows y **442/492/542/592**, pitch 50, text x
140..340, selection glyph x 40..120, list region y 380..660. The older
425/475/525/575 + "bright band at x 88..124" description does not hold here.

Reading side only: no input was injected, so there is no press->serial->row chain
in this evidence.
