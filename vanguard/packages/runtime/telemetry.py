"""Integer telemetry for a benchmarked run (`S9-A-02`, `S6B-MD-009`).

Every quantity the instrument reports is an integer or absent. No float is ever
the truth: a number that has been through a division no longer sums, and a
corpus of rounded floats cannot be re-added to check itself. Cost is USD
micros, time is integer milliseconds, tokens are counts.

**Absent is not zero.** A run whose provider never answered has `None` tokens,
not `0`. Reporting zero makes a failed instrument look like a free run, which
is the degenerate-row problem the retraction sweep existed to remove.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

__all__ = ["RunTelemetry", "compute_run_telemetry", "instrument_error"]


@dataclass(frozen=True, slots=True)
class RunTelemetry:
    """What one run cost, in integers, with absence preserved."""

    #: Turns actually taken, counted from the ledger rather than from a loop.
    turns: int
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    #: Cost in USD micros. Integer because money does not round twice.
    usd_micros: int | None = None
    wall_millis: int | None = None

    def __post_init__(self) -> None:
        for name in ("turns", "prompt_tokens", "completion_tokens",
                     "usd_micros", "wall_millis"):
            value = getattr(self, name)
            if value is None:
                continue
            # `bool` is an `int` subclass and would silently pass; a flag is
            # not a measurement.
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(
                    f"{name} must be an integer or None, got {value!r}: "
                    "floats are not truth (S6B-MD-009)")

    @property
    def total_tokens(self) -> int | None:
        """Prompt + completion, or `None` when either side was never reported."""
        if self.prompt_tokens is None or self.completion_tokens is None:
            return None
        return self.prompt_tokens + self.completion_tokens


def compute_run_telemetry(contexts: Iterable[Any], turns: int) -> RunTelemetry:
    """Sum reported token usage across operator contexts, absence preserved.

    Extracted from `HarnessSession._telemetry` (EVO-06): a pure function over
    the contexts a caller already has, so it is testable and reusable without
    a live session. Behavior is unchanged -- a provider that reported no
    usage still contributes nothing to the sum rather than a false zero
    (`S9-A-02`).
    """
    prompt: int | None = None
    completion: int | None = None
    for context in contexts:
        if not isinstance(context, Mapping):
            continue
        for key, current in (("prompt_tokens", prompt), ("completion_tokens", completion)):
            reported = context.get(key)
            if isinstance(reported, bool) or not isinstance(reported, int):
                continue
            if key == "prompt_tokens":
                prompt = reported if current is None else current + reported
            else:
                completion = reported if current is None else current + reported
    return RunTelemetry(turns=turns, prompt_tokens=prompt, completion_tokens=completion)


def instrument_error(turns: int) -> str | None:
    """Why this arm produced no usable measurement, or `None`.

    Extracted from `HarnessSession._instrument_error` (EVO-06), unchanged.
    `None` means the instrument worked; it does not mean the run succeeded --
    a refused run is a result, an unmeasured one is not.
    """
    if turns == 0:
        return "model_not_invoked"
    return None
