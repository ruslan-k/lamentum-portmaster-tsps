"""Stateful owned collector -> capture/oracle -> navigator -> released pad chain.

Transport callbacks are injected for host fixtures and supplied by nav_chain on
real runs. This is diagnostic wiring, not proof of semantic pages or safe RAM.
"""
import time
from navigator import Navigation, observe

OWNER_KEYS = ('boot_id', 'pid', 'starttime', 'elf_dev', 'elf_ino')


class OwnedNavigationDriver:
    def __init__(self, *, reader, remote, capture, press, verify_owner,
                 response_timeout_s, clock=time.monotonic, target='newgame', tap_ms=350):
        if not 1 <= tap_ms <= 400:
            raise ValueError('bounded diagnostic tap must be 1..400 ms')
        self.reader, self.remote = reader, remote
        self.capture, self.press, self.verify_owner = capture, press, verify_owner
        self.clock = clock
        self.navigation = Navigation(target=target, clock=clock, response_timeout_s=response_timeout_s)
        self.timeout = response_timeout_s
        self.started = clock()
        self.tap_ms = tap_ms
        self.generation = None
        self.owner = None
        self.events = []
        self.refused = None
        self.last_observation = None
        self.release_receipt = None

    def _emit(self, action, **fields):
        event = dict(action=action, **fields)
        self.events.append(event)
        return event

    def _refuse(self, reason):
        self.refused = reason
        self.navigation._refuse(reason)
        return self._emit('refuse', reason=reason, release_receipt=self.release_receipt)

    def _poll(self):
        sample = self.reader.poll(self.remote)
        if sample.get('status') != 'ok':
            raise RuntimeError('owned collector rejected: ' + str(sample.get('status')))
        state = self.reader.state
        header = state.get('run_header') or {}
        if not state.get('log_identity_qualified') or not state.get('header_sha256'):
            raise RuntimeError('owned log identity not qualified')
        owner = {key: header[key] for key in OWNER_KEYS}
        generation = state['header_sha256']
        if self.generation is None:
            self.generation, self.owner = generation, owner
        if generation != self.generation or owner != self.owner:
            raise RuntimeError('owned generation changed; navigation cannot rebind')
        if not self.verify_owner(self.owner):
            raise RuntimeError('owned process unavailable or changed')
        return sample

    def tick(self):
        if self.refused:
            return self._emit('refuse', reason=self.refused, release_receipt=self.release_receipt)
        if self.navigation.finished:
            return self._emit('done')
        try:
            if self.clock() - self.started >= self.timeout:
                return self._refuse('overall diagnostic deadline expired')
            before = self._poll()
            serial = before.get('serial')
            if not serial:
                if self.clock() - self.started >= self.timeout:
                    return self._refuse('present counter startup deadline expired')
                return self._emit('wait', reason='no complete presented serial')
            # Fast duplicate polls must still exercise the core wall deadline.
            if self.last_observation and serial == self.last_observation[2]:
                result = observe(self.navigation, *self.last_observation)
                if result['action'] == 'refuse':
                    return self._refuse(result['reason'])
                return self._emit('wait', reason='no newer captured frame')
            if self.clock() - self.started >= self.timeout and self.last_observation is None:
                return self._refuse('first capture deadline expired')
            capture_start = self.clock()
            image = self.capture()
            capture_end = self.clock()
            after = self._poll()  # verifies generation and process again AFTER capture
            self._emit('capture', started=capture_start, ended=capture_end,
                       elapsed_ms=round((capture_end-capture_start)*1000, 3),
                       serial_before=serial, serial_after=after.get('serial'))
            if self.clock() - self.started >= self.timeout:
                return self._refuse('overall deadline expired during capture')
            if after.get('serial') != serial:
                if self.clock() - self.started >= self.timeout:
                    return self._refuse('capture bracket deadline expired')
                return self._emit('wait', reason='present changed during capture; discard image')
            self.last_observation = (image['page'], image['cursor_y'], serial)
            result = observe(self.navigation, *self.last_observation)
            if result['action'] == 'refuse':
                return self._refuse(result['reason'])
            if result['action'] != 'press':
                return self._emit(result['action'], navigator=result)
            if result['button'] == 'confirm':
                return self._refuse('Confirm disabled pending semantic page and memory gates')
            # Recheck before input; never send an action based on a rotated log or
            # an observation already superseded by another presented frame.
            ready = self._poll()
            if ready.get('serial') != serial:
                return self._refuse('present changed before input')
            if self.clock() - self.started >= self.timeout:
                return self._refuse('overall deadline expired before input')
            self.release_receipt = self.press(result['button'], self.tap_ms)
            if (not isinstance(self.release_receipt, dict) or
                    self.release_receipt.get('released') is not True or
                    self.release_receipt.get('action') != result['button']):
                return self._refuse('missing or inconsistent button release receipt')
            self._poll()  # verified owner/generation after the synchronous release
            return self._emit('press', navigator=result, release_receipt=self.release_receipt,
                              owner_verified=True, owner=self.owner, generation=self.generation)
        except (RuntimeError, KeyError, OSError, TypeError, ValueError) as error:
            return self._refuse(str(error))
