"""Drive a session until the oracle is green or the budget is spent (`W11-A`).

A single `HarnessSession.run()` is one episode. A repair task is not: the agent
observes, proposes, applies an effect, runs the suite, reads the failure, and
goes again. Stopping after one pass and emitting a `completed` receipt reports
a task finished that was merely *attempted* -- the degenerate row the retraction
sweep existed to remove.

**Termination is proved, never assumed.** The loop stops on exactly three
things: the oracle passing, the budget running out, or no progress being made.
Each is reported by name, so a run that ran out of money is never mistaken for a
run that failed to fix the bug.

There is no second dispatch path here and no second loop inside the engine. This
composes `HarnessSession.run()` -- it re-enters the existing one (`AT-01`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

from .telemetry import RunTelemetry

__all__ = ["RepairOutcome", "StopReason", "drive_until_green"]


class StopReason:
    """Why the driver stopped. Named, because 'it stopped' is not a finding."""

    ORACLE_GREEN = "oracle_green"
    #: The token ceiling was reached. Distinct from `ATTEMPTS_EXHAUSTED`:
    #: a run that ran out of money and a run that ran out of tries fail for
    #: different reasons and warrant different next moves.
    BUDGET_EXHAUSTED = "budget_exhausted"
    ATTEMPTS_EXHAUSTED = "attempts_exhausted"
    NO_PROGRESS = "no_progress"
    INSTRUMENT_ERROR = "instrument_error"


@dataclass(frozen=True, slots=True)
class RepairOutcome:
    """What the repair loop did, and why it stopped."""

    stop_reason: str
    attempts: int
    oracle_green: bool
    telemetry: RunTelemetry
    results: tuple[Any, ...] = ()
    detail: str = ""

    @property
    def succeeded(self) -> bool:
        """Only a green oracle is success. Running out of turns is not."""
        return self.oracle_green


def drive_until_green(
    run_session: Callable[[int], Any],
    *,
    oracle: Callable[[Any], bool],
    max_attempts: int = 4,
    max_tokens: int | None = None,
    progress_of: Callable[[Any], str] | None = None,
) -> RepairOutcome:
    """Re-enter the session until the oracle is green or the budget is gone.

    `run_session(attempt)` runs one episode and returns its `RunResult`.
    `oracle(result)` reports whether the suite passes -- it is supplied by the
    caller and evaluated *outside* the episode, because a loop that grades its
    own work is the inversion of `A-05`.

    `progress_of` yields a per-attempt signal; two identical signals in a row
    mean the agent is repeating itself and the loop stops rather than burning
    the remaining budget on the same failed edit.
    """

    results: list[Any] = []
    prompt = completion = 0
    seen_any_tokens = False
    last_signal: str | None = None
    stop = StopReason.ATTEMPTS_EXHAUSTED
    detail = ""
    green = False

    for attempt in range(1, max(int(max_attempts), 1) + 1):
        result = run_session(attempt)
        results.append(result)

        telemetry = getattr(result, "telemetry", None)
        if telemetry is not None:
            if telemetry.prompt_tokens is not None:
                prompt += telemetry.prompt_tokens
                seen_any_tokens = True
            if telemetry.completion_tokens is not None:
                completion += telemetry.completion_tokens
                seen_any_tokens = True

        if getattr(result, "instrument_error", None):
            stop = StopReason.INSTRUMENT_ERROR
            detail = str(result.instrument_error)
            break

        if oracle(result):
            green = True
            stop = StopReason.ORACLE_GREEN
            break

        if max_tokens is not None and seen_any_tokens and prompt + completion >= max_tokens:
            stop = StopReason.BUDGET_EXHAUSTED
            detail = f"token budget {max_tokens} reached after {attempt} attempt(s)"
            break

        if progress_of is not None:
            signal = progress_of(result)
            if last_signal is not None and signal == last_signal:
                stop = StopReason.NO_PROGRESS
                detail = "two attempts produced an identical signal"
                break
            last_signal = signal
    else:
        detail = f"exhausted {max_attempts} attempt(s) without a green oracle"

    return RepairOutcome(
        stop_reason=stop,
        attempts=len(results),
        oracle_green=green,
        telemetry=RunTelemetry(
            turns=sum(getattr(getattr(r, "telemetry", None), "turns", 0) or 0
                      for r in results),
            prompt_tokens=prompt if seen_any_tokens else None,
            completion_tokens=completion if seen_any_tokens else None,
        ),
        results=tuple(results),
        detail=detail,
    )
