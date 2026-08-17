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

__all__ = ["RunTelemetry"]


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
