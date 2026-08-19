"""Worst-case spend expressed as a 6D Reservation settled by kernel Governor."""

from __future__ import annotations

import math

from layer0.kernel.budget import BudgetDenied, Governor
from layer0.spi.types_gen import Reservation

__all__ = ["BudgetDenied", "Governor", "is_free_model", "worst_case_reservation"]


def is_free_model(model: str) -> bool:
    return (
        model == "openrouter/free"
        or model.endswith(":free")
        or model.startswith("mock")
        or model.startswith("ollama")
    )


def worst_case_reservation(
    *,
    model: str,
    pricing: tuple[int, int, int] | None,
    max_prompt_tokens: int = 8192,
    max_completion_tokens: int = 4096,
    millis: int = 60_000,
    turns: int = 1,
    depth: int = 1,
    bytes_ceiling: int = 0,
) -> Reservation:
    """Pre-call ceiling. Unknown paid pricing is not represented as zero."""
    if is_free_model(model):
        return Reservation(
            usd_micros=0,
            millis=millis,
            tokens=max_prompt_tokens + max_completion_tokens,
            bytes=bytes_ceiling,
            turns=turns,
            depth=depth,
        )
    if pricing is None:
        raise BudgetDenied("usd_micros", 0, 0, "price_unknown")
    prompt_rate, completion_rate, _cached = pricing
    usd = math.ceil((max_prompt_tokens * prompt_rate) / 1_000_000) + math.ceil(
        (max_completion_tokens * completion_rate) / 1_000_000
    )
    return Reservation(
        usd_micros=usd,
        millis=millis,
        tokens=max_prompt_tokens + max_completion_tokens,
        bytes=bytes_ceiling,
        turns=turns,
        depth=depth,
    )
