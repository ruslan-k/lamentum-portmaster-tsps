"""Navigator core under the owner's P0-N2 contract (roadmap 40.3).

Explicit state machine, direction from ordered row indices, overshoot refused by
default, and a confirm that needs two independent newer observations. Pure: no
device I/O, no pixels - the caller supplies (page, cursor_y, present_serial).

Why each rule exists here (all of them were wrong answers once):
  * a press is an ACTION, not an observation: a second press is never issued while
    the first one is unacknowledged;
  * direction comes from ordered row indices, so a row below the target presses Up;
  * a move of more than one row is refused by default: at 1-2 fps a long hold
    advances two entries and continuing would walk past the target;
  * confirming needs two newer observations that agree, because one frame can be a
    leftover or a mid-animation state;
  * the page after a confirm must be the expected one; anything else is refused.
"""
from dataclasses import dataclass, field
import math
import time
from typing import Callable

# Measured on a live frame of build229 (evidence/nav-oracle-01): rows at
# y 442/492/542/592 (pitch 50), selection marked by a cursor glyph left of the row.
ROWS_MAIN_MENU = {'load': 442, 'newgame': 492, 'options': 542, 'credits': 592}
ROW_TOLERANCE = 12
CONFIRM_OBSERVATIONS = 2

IDLE = 'IDLE'
ACTION_ISSUED = 'ACTION_ISSUED'
AWAIT_NEW_PRESENT = 'AWAIT_NEW_PRESENT'
OBSERVED_EFFECT = 'OBSERVED_EFFECT'
DONE = 'DONE'
REFUSED = 'REFUSED'

MAIN_MENU = 'MAIN_MENU'
NEWGAME_CONFIG = 'NEWGAME_CONFIG'
CONTROLS = 'CONTROLS'
LOADING = 'LOADING'
WORLD = 'WORLD_VISIBLE'
PAGES = (MAIN_MENU, NEWGAME_CONFIG, CONTROLS, LOADING, WORLD)
EXPECTED_AFTER_CONFIRM = (NEWGAME_CONFIG,)


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
    recovery: bool = False
    state: str = IDLE
    issued_serial: int = -1
    confirmed_serial: int = -1
    last_row: str | None = None
    confirm_seen: int = 0
    events: list = field(default_factory=list)
    refused: str | None = None
    target_seen_serial: int = -1
    last_observed_serial: int = -1
    last_observation: Observation | None = None
    clock: Callable[[], float] = field(default=time.monotonic, repr=False)
    response_timeout_s: float = 5.0  # bounded diagnostic default, not device-qualified
    waiting_since: float | None = None

    def __post_init__(self):
        if not math.isfinite(self.response_timeout_s) or self.response_timeout_s <= 0:
            raise ValueError('positive finite response timeout required')

    def _reset_confirm_evidence(self):
        self.confirm_seen = 0
        self.target_seen_serial = -1

    @property
    def finished(self):
        return self.state == DONE

    # --- geometry --------------------------------------------------------
    def ordered_rows(self):
        return sorted(self.rows, key=lambda name: self.rows[name])

    def index_of(self, row):
        return self.ordered_rows().index(row)

    def direction_to(self, row):
        return 'down' if self.index_of(row) < self.index_of(self.target) else 'up'

    def row_at(self, cursor_y):
        best, distance = None, None
        for name, y in self.rows.items():
            delta = abs(cursor_y - y)
            if delta <= self.tolerance and (distance is None or delta < distance):
                best, distance = name, delta
        return best

    def _pitch(self):
        ordered = [self.rows[name] for name in self.ordered_rows()]
        return max(1, ordered[1] - ordered[0])

    # --- receipts --------------------------------------------------------
    def _emit(self, action, **extra):
        event = {'action': action, 'state': self.state, **extra}
        self.events.append(event)
        return event

    def _refuse(self, reason, **extra):
        self.state = REFUSED
        self.refused = reason
        self._reset_confirm_evidence()
        return self._emit('refuse', reason=reason, **extra)

    # --- state machine ---------------------------------------------------
    def observe(self, observation):
        if self.state == DONE:
            return self._emit('done', reason='navigation finished')
        if self.state == REFUSED:
            return self._emit('refuse', reason=self.refused)
        if observation.page not in PAGES:
            return self._refuse('unknown page %r' % (observation.page,))
        if observation.present_serial <= 0:
            return self._refuse('present serial not established')
        now = self.clock()
        if not math.isfinite(now):
            return self._refuse('invalid monotonic clock')
        if self.waiting_since is None:
            self.waiting_since = now
        elapsed = now - self.waiting_since
        if elapsed < 0:
            return self._refuse('monotonic clock went backwards')
        if elapsed >= self.response_timeout_s:
            return self._refuse('response deadline expired; present serial not advancing or action unacknowledged',
                                elapsed_ms=round(elapsed * 1000, 3),
                                last_serial=self.last_observed_serial,
                                issued_serial=self.issued_serial,
                                owner_verified=False)
        if observation.present_serial < self.last_observed_serial:
            return self._refuse('present serial went backwards: lagged or foreign frame')
        if observation.present_serial == self.last_observed_serial:
            if observation != self.last_observation:
                return self._refuse('conflicting observations for the same present serial')
            return self._emit('wait', reason='no unique newer frame', serial=observation.present_serial)
        self.last_observed_serial = observation.present_serial
        self.last_observation = observation

        # A confirm is only satisfied by the expected page at a newer serial.
        if self.confirmed_serial >= 0 and observation.present_serial > self.confirmed_serial:
            if observation.page in EXPECTED_AFTER_CONFIRM:
                self.state = DONE
                return self._emit('done', page=observation.page, serial=observation.present_serial)
            if observation.page != MAIN_MENU:
                return self._refuse('unexpected page %r after confirm' % (observation.page,))
            self.confirm_seen = 0
            return self._emit('wait', reason='confirm not acknowledged yet; menu still shown',
                              serial=observation.present_serial)

        # A page that only follows a confirm cannot appear without one: a
        # screenshot change is not evidence that the menu was left.
        if self.confirmed_serial < 0 and observation.page != MAIN_MENU:
            return self._refuse('page %r seen without a preceding confirm' % (observation.page,),
                                page=observation.page)

        row = self.row_at(observation.cursor_y)
        if row is None:
            self._reset_confirm_evidence()
            return self._emit('wait', reason='cursor not inside a known band',
                              cursor_y=observation.cursor_y, serial=observation.present_serial)

        if self.last_row is not None and row != self.last_row:
            steps = round(abs(self.rows[row] - self.rows[self.last_row]) / self._pitch())
            if steps > 1:
                if not self.recovery:
                    return self._refuse(
                        'one action moved %d rows (%s -> %s): overshoot, explicit recovery required'
                        % (steps, self.last_row, row), from_row=self.last_row, to_row=row, steps=steps)
                self._emit('overshoot', from_row=self.last_row, to_row=row, steps=steps,
                           reason='recovery enabled for a diagnostic arm')
        self.last_row = row

        if row != self.target:
            self._reset_confirm_evidence()
            self.waiting_since = now
            self.state = ACTION_ISSUED
            self.issued_serial = observation.present_serial
            return self._emit('press', button=self.direction_to(row), row=row,
                              serial=observation.present_serial)

        if self.confirm_seen == 0:
            self.confirm_seen = 1
            self.target_seen_serial = observation.present_serial
            self.waiting_since = now
            self.state = AWAIT_NEW_PRESENT
            return self._emit('wait', reason='target row seen once; confirm needs a second frame',
                              row=row, serial=observation.present_serial)
        self.confirm_seen += 1
        if self.confirm_seen < CONFIRM_OBSERVATIONS:
            self.state = AWAIT_NEW_PRESENT
            return self._emit('wait', reason='waiting for the second agreeing observation',
                              row=row, serial=observation.present_serial)
        self.state = ACTION_ISSUED
        self.waiting_since = now
        self.confirmed_serial = observation.present_serial
        self.issued_serial = observation.present_serial
        return self._emit('press', button='confirm', row=row, serial=observation.present_serial)


def observe(navigation, page, cursor_y, present_serial):
    return navigation.observe(Observation(page=page, cursor_y=cursor_y, present_serial=present_serial))
