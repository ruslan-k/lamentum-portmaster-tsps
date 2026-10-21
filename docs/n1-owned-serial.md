# N1: retire the full-log serial scan, use the owned incremental collector

Owner roadmap **§40.2 (P0-N1)** and **§40.11 item 1**. Roadmap revision read at
`a0aa160` (§40 unchanged, sections 41–47 are my reports).

## What was wrong

`serial_request()` built a remote program that read the **whole** `latest.log` on
every poll and parsed the present counter with `re.findall(marker + r"\d+")`. Two
defects: the match was not a capture group (so `int()` would raise once a present was
logged), and each poll cost O(entire growing log) with no generation check, so a
rotated log could hand back a counter from a previous run.

## What replaces it

- `serial_request()` and `PRESENT_MARKER`-based full-file scanning are **removed**
  from the control path.
- `load_metrics.OwnedSerial` polls the existing **owned byte-framed collector**
  (`collector_request` + `fold`) with `include_text=True`, so each poll advances a
  byte cursor (cost proportional to new output) and carries the generation/anchor
  checks that were already tested.
- A rejected generation returns `serial: None` and `fresh: False`: the old counter is
  kept only as history and can never qualify a press in the new generation.
- `present_serial()` now counts **complete lines only**; a trailing partial record is
  ignored, because counting it would qualify a press with a frame that was never
  fully written.
- `tools/nav_chain.py` uses one `OwnedSerial` per chain: the before-frame serial and
  the after-press serial come from the same cursor, so both belong to the same
  generation.

## Tests (roadmap §40.12 first-PR red/green targets)

- Multi-record chunk `frame=1/42/9` → serial **42**, no exception (the retired code
  raised `ValueError` here).
- Second poll with no new text → serial unchanged, `fresh=False`.
- **Run A at frame 50 → rotation → refuses**, `serial=None`, `fresh=False`, and the
  stored 50 remains only as history.
- Partial trailing line ignored, then completed by the next chunk → 7.
- Cursor advances (offset adopted from the sample) instead of rescanning.
- 30 000-record backlog parsed from the chunk alone → 30000.

**217 host tests PASS.**

## Still open in N1

- The device-side acceptance from §40.2 item 6 (before image → owned serial S →
  short press → owned serial S+ → after image, same PID/starttime) has **not** run
  with the new reader yet; the previous arm qualified serial 19 → 23 through the
  retired path, which is now replaced.
- `expected_run` coupling exists in `OwnedSerial` but `nav_chain` currently polls
  without it (it only knows the process identity from `/proc`); wiring the run UUID
  from the header into the reader is the next tightening.
