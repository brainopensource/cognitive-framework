"""Determinism ports (`S8-A-03`, `004` G3, `003` A12).

Replay that only reconstructs *state* is not replay. Counterfactual
re-execution -- rerunning a recorded episode with one thing changed and
attributing the difference -- is what makes a corpus attributable
(`GTS-13C` Ch. 11, stage 2), and it needs every nondeterministic draw to come
from somewhere a `Recording` can pin.

Two sources, two ports. Nothing else in the tree may reach the process-global
RNG or the wall clock on the trajectory path: a module that can do so silently
can break replay without any caller being able to see it.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

__all__ = ["ClockPort", "RandomPort"]


@runtime_checkable
class RandomPort(Protocol):
    """Every random draw on the trajectory path.

    `Recording.seed` pins this stream. An implementation must own its state --
    borrowing the process-global RNG would make one run's draws depend on every
    other caller in the process, which is exactly the bug this port closes.
    """

    def getrandbits(self, k: int) -> int:
        """Return `k` random bits as a non-negative int."""


@runtime_checkable
class ClockPort(Protocol):
    """Injected time, complete enough to drive determinism.

    `CT-08` already required `now()` for timestamps. Replay additionally needs
    the millisecond instant, because a UUIDv7 embeds it: an id generated from a
    re-read wall clock differs even when every other byte matches.

    `Recording.clockPolicy` selects the implementation -- `recorded` replays
    captured instants, `fixed` pins one, `logical` counts.
    """

    def now(self) -> str:
        """RFC 3339 UTC millisecond timestamp (`CT-08`)."""

    def now_ms(self) -> int:
        """The same instant as integer milliseconds since the epoch."""
