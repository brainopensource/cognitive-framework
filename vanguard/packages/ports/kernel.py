"""The interfaces the kernel depends on, and nothing it implements.

`01 §2` (dependency inversion): the kernel depends on ports, never on
adapters, and only the composition root knows a concrete implementation.
Every protocol here is small and role-specific (`01 §2`, interface
segregation) — there is no runtime god-object.

These protocols live in the approved `ports` package.  They deliberately use
structural values at this layer: exchange models are supplied by callers, so
`ports` never imports the higher-level `kernel` package merely for annotations.

**Liskov (`01 §2`).** The failure mode is the half of the contract that breaks
substitution, so each protocol states it:

* `EffectAdapter.execute` returns a typed outcome for *every* result including
  denial and undeterminable occurrence. It raises only for genuine defects.
* `Clock.now` is monotone within a run and injected, never read from the
  environment — a fake clock is a first-class implementation, which is what
  makes expiry testable (`MF-KRN-005`).
* `EventSink.emit` never raises in a way that fails an effect (`F-25`).
* `Ledger.append_intent` either durably persists or raises; there is no
  "probably written" outcome, because `F-21a` depends on the difference.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

__all__ = [
    "Clock",
    "EffectAdapter",
    "EventSink",
    "Ledger",
]


@runtime_checkable
class Clock(Protocol):
    """Injected time. `domain` forbids clocks; the kernel takes one as a port."""

    def now(self) -> str:
        """RFC 3339 UTC millisecond timestamp (`CT-08`)."""


@runtime_checkable
class EffectAdapter(Protocol):
    """One typed effect. It coordinates nothing and decides no policy."""

    name: str

    def healthy(self) -> bool:
        """False routes to `F-03` before any lease is opened."""

    def execute(self, request: Any) -> Any:
        """Perform the effect and report what happened.

        Returns a typed outcome for success, error, timeout, cancellation and
        **undeterminable occurrence** (`F-22`). Resolving an undeterminable
        external effect to success or failure is manufacturing evidence.
        """


@runtime_checkable
class EventSink(Protocol):
    """Where kernel events go. Emission failure never fails an effect (`F-25`)."""

    def emit(self, event: Any) -> None: ...


@runtime_checkable
class Ledger(Protocol):
    """Durable intent, written before the effect begins (`K-47`)."""

    def append_intent(self, event: Any) -> None:
        """Persist and flush. Raising routes to `F-21a`; the effect never starts."""
