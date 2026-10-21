# Tap-length A/B on the live menu (roadmap 32.7 item 3)

`tools/nav_chain.py` is the repeatable wiring: oracle + navigator + the port's own
present counter + the owner-checked pad contract. It reports one of three things and
refuses the rest: a qualified one-row move, a qualified no-move, or "not qualified".

## What is established

| arm | tap | before | after | serial | verdict |
|---|---|---|---|---|---|
| `nav-chain-04` | **350 ms** | `MAIN_MENU` / `load` | `MAIN_MENU` / `load` | **19 → 23** (qualified) | press did not move the selection |
| `nav-chain-02` | 900 ms | `MAIN_MENU` / `load` | `MAIN_MENU` / `options` | not read (wrong log path) | **two rows** — hold-length overshoot |

So the window is narrow and real: 350 ms is lost between guest samples at ~1
presented frame/s, 900 ms spans more than one sample and moves two rows. A one-row
tap must sit between them, and the next arm should test ~500–600 ms with the same
serial qualification.

## What is *not* established, and why

Two 550 ms attempts failed for orchestration reasons, not for a tap-length result,
and are recorded as failures:

- `nav-chain-05`: the chain was started **before** the arm in a sequential shell
  (`;` instead of `&`), waited its full 240 s window with no game, and wrote
  `states: []`. The arm that ran afterwards had `stops: []` and verified execution;
  its chain does not exist.
- `nav-chain-06`: chain and arm overlapped correctly and the oracle did read the
  menu (`load`, 126,850 B), but the present counter was still **0** because a fresh
  run's log had no present line at that instant, so the navigator refused with
  "present serial not established". The tool now waits for the first present
  counter (`wait_serial(0)`) instead of reading a zero.

## Tool contract now

- Present serial is read from `.../lamentum-switch/logs/latest.log` through
  `load_metrics.present_serial` / `serial_request` (the earlier guessed sibling path
  returned 0 and silently removed the qualification).
- Default tap is **350 ms**; `summarise()` refuses a chain whose serials are missing
  or unchanged, reports a two-row move as an overshoot, and names the next lever
  when nothing moved.
- 199 host tests PASS (7 for `summarise`, 4 for the serial reader including an
  executed payload test).

## Limits

Menu only: one press, two frames, one page. No New Game configuration page, no
Loading, no scene, no id295, no FPS. Captures stay owner-local.
