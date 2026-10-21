"""Single navigation core for the New Game path (roadmap 32.7, item 3).

Pure state machine: it consumes observations (page, measured cursor row, present
serial) and returns one action. No device I/O, no pixel heuristics, no OCR. The
rules it enforces are the ones that have already produced wrong answers here:

  * a press counts only after a NEW presented frame (at 1-2 fps a tap can land
    entirely between two samples, and a stale serial means the press was never
    observed);
  * one press must move at most one row - a two-row move is an overshoot caused
    by hold length, not evidence for a second press;
  * a changed picture is not a page change; the page transition must be seen at
    a later serial;
  * an unknown page or a cursor that is not inside a known band refuses instead
    of guessing.
"""
from dataclasses import dataclass, field

# Measured on a live frame of this build (evidence/nav-oracle-01): rows at
# y 442/492/542/592 (pitch 50), selection marked by a cursor glyph left of the
# row. The earlier 425/475/525/575 table came from a different build/scale.
ROWS_MAIN_MENU = {'load': 442, 'newgame': 492, 'options': 542, 'credits': 592}
ROW_TOLERANCE = 12
MAX_ROW_STEP = 1
STALE_SERIAL_LIMIT = 3

MAIN_MENU = 'MAIN_MENU'
NEWGAME_CONFIG = 'NEWGAME_CONFIG'
CONTROLS = 'CONTROLS'
LOADING = 'LOADING'
WORLD = 'WORLD_VISIBLE'
PAGES = (MAIN_MENU, NEWGAME_CONFIG, CONTROLS, LOADING, WORLD)
# Pages that end the navigation stage. WORLD is never claimed from a picture here.
TERMINAL_PAGES = (NEWGAME_CONFIG, CONTROLS, LOADING, WORLD)


@dataclass(frozen=True)
class Observation:
    page: str
    cursor_y: int
    present_serial: int


@dataclass
class Navigation:
    target: str = 'newgame'
    rows: dict = field(default_factory=lambda: dict(ROWS_MAIN_MENU))
    tolerance: int = ROW_TOLERANCE
    issued_serial: int = -1
    confirmed_serial: int = -1
    last_row: str | None = None
    stale: int = 0
    events: list = field(default_factory=list)
    finished: bool = False
    refused: str | None = None

    def row_at(self, cursor_y):
        best, distance = None, None
        for name, y in self.rows.items():
            delta = abs(cursor_y - y)
            if delta <= self.tolerance and (distance is None or delta < distance):
                best, distance = name, delta
        return best

    def _emit(self, action, **extra):
        event = {'action': action, **extra}
        self.events.append(event)
        return event

    def observe(self, observation):
        if self.finished:
            return self._emit('done', reason='navigation finished')
        if self.refused:
            return self._emit('refuse', reason=self.refused)
        if observation.page not in PAGES:
            self.refused = 'unknown page %r' % (observation.page,)
            return self._emit('refuse', reason=self.refused)
        if observation.present_serial <= 0:
            self.refused = 'present serial not established'
            return self._emit('refuse', reason=self.refused)
        # A press or confirm is only qualified by a strictly later frame.
        if self.issued_serial >= observation.present_serial:
            self.stale += 1
            if self.stale > STALE_SERIAL_LIMIT:
                self.refused = 'present serial not advancing'
                return self._emit('refuse', reason=self.refused)
            return self._emit('wait', reason='no new presented frame', serial=observation.present_serial)
        self.stale = 0

        if observation.page in TERMINAL_PAGES:
            # Reaching a later page is a navigation result; whether it is a world
            # is decided by scene receipts, never by this component.
            if self.confirmed_serial >= 0 or observation.page != MAIN_MENU:
                self.finished = True
                return self._emit('done', page=observation.page, serial=observation.present_serial)

        row = self.row_at(observation.cursor_y)
        if row is None:
            return self._emit('wait', reason='cursor not inside a known band',
                              cursor_y=observation.cursor_y, serial=observation.present_serial)

        if self.last_row is not None and row != self.last_row:
            pitch = max(1, abs(self.rows['newgame'] - self.rows['load']))
            steps = round(abs(self.rows[row] - self.rows[self.last_row]) / pitch)
            if steps > MAX_ROW_STEP:
                self._emit('overshoot', from_row=self.last_row, to_row=row, steps=steps,
                           reason='one press moved %d rows - hold length, not a new press' % steps)
        self.last_row = row

        if row != self.target:
            self.issued_serial = observation.present_serial
            return self._emit('press', button='down', row=row, serial=observation.present_serial)
        if self.confirmed_serial < 0:
            self.confirmed_serial = observation.present_serial
            return self._emit('press', button='confirm', row=row, serial=observation.present_serial)
        return self._emit('wait', reason='waiting for the config page',
                          row=row, serial=observation.present_serial)


def observe(navigation, page, cursor_y, present_serial):
    return navigation.observe(Observation(page=page, cursor_y=cursor_y, present_serial=present_serial))
