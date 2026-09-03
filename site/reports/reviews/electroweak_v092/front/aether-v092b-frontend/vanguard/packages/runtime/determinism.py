"""The real/fake pair behind the determinism ports (`S8-A-03`).

`root.py` already held `_SystemClock` for the same reason these live here: the
composition root is the one place allowed to know a concrete implementation.

`event_id` is the point of the exercise. Every event id used to come from
`uuidv7()`, which reads `time.time()` and the process-global RNG, so two runs
of one recording could not produce the same bytes however faithfully everything
else replayed. The id is built here from the two injected ports instead, and
the result is still a conforming RFC 9562 UUIDv7.
"""

from __future__ import annotations

import random as _random
import time as _time
from datetime import datetime, timedelta, timezone

from ..ports.determinism import ClockPort, RandomPort

__all__ = ["FixedClock", "SeededRandom", "SystemClock", "SystemRandom", "event_id"]

_ISO = "%Y-%m-%dT%H:%M:%S."


def _format(moment: datetime) -> str:
    return moment.strftime(_ISO) + f"{moment.microsecond // 1000:03d}Z"


class SystemRandom:
    """The live source. Used when a run is being recorded, not replayed."""

    def __init__(self) -> None:
        # Its own generator, not the module-global one: a `random.seed()`
        # anywhere else in the process must not perturb a run.
        self._rng = _random.Random()

    def getrandbits(self, k: int) -> int:
        return self._rng.getrandbits(k)


class SeededRandom:
    """The replay source. `Recording.seed` pins the whole stream."""

    def __init__(self, *, seed: int) -> None:
        self.seed = int(seed)
        self._rng = _random.Random(self.seed)

    def getrandbits(self, k: int) -> int:
        return self._rng.getrandbits(k)


class SystemClock:
    """`CT-08` timestamps from the wall clock. Injected, never read by `domain`."""

    def now(self) -> str:
        return _format(datetime.now(timezone.utc))

    def now_ms(self) -> int:
        return int(_time.time() * 1000)


class FixedClock:
    """`clockPolicy: fixed` at `step_ms=0`; `logical` when it advances.

    A logical clock is a counter, not a measurement: it makes ordering
    reproducible without pretending to know how long anything took.
    """

    def __init__(self, *, at: str, step_ms: int = 0) -> None:
        self._at = datetime.strptime(at, "%Y-%m-%dT%H:%M:%S.%fZ").replace(
            tzinfo=timezone.utc)
        self._step = timedelta(milliseconds=int(step_ms))
        self._ticks = 0

    def _current(self) -> datetime:
        moment = self._at + self._step * self._ticks
        if self._step:
            self._ticks += 1
        return moment

    def now(self) -> str:
        return _format(self._current())

    def now_ms(self) -> int:
        return int(self._current().timestamp() * 1000)


def event_id(*, clock: ClockPort, random: RandomPort) -> str:
    """An RFC 9562 UUIDv7 built from injected sources.

    Identical to `domain.primitives.uuidv7` in layout; it differs only in
    where the 48 timestamp bits and 74 random bits come from, which is the
    whole of the determinism problem.
    """
    millis = clock.now_ms() & ((1 << 48) - 1)
    rand_a = random.getrandbits(12)
    rand_b = random.getrandbits(62)
    value = (millis << 80) | (0x7 << 76) | (rand_a << 64) | (0x2 << 62) | rand_b
    digits = f"{value:032x}"
    return f"{digits[:8]}-{digits[8:12]}-{digits[12:16]}-{digits[16:20]}-{digits[20:]}"
