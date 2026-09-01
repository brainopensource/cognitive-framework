"""Parent remaining balance, computed once and read from two places.

The meta-controller asks "how much is left?" to decide strategy; the spawn
adapter asks the same question to decide whether a child may be created at all.
Those two answers must be the *same* answer. When they were two expressions,
a child could be granted a budget the controller had already spent.

`depth` and `turns` appear beside the four additive dimensions because callers
compare all six, but they remain structural: `remaining` reports headroom, and
nothing in the system ever *spends* it (`C-05`).
"""

from __future__ import annotations

from typing import Mapping

__all__ = ["ADDITIVE_DIMENSIONS", "remaining_budget"]

ADDITIVE_DIMENSIONS = ("usd_micros", "millis", "tokens", "bytes")


def remaining_budget(
    *,
    harness_budget: Mapping[str, int],
    budget_consumed: Mapping[str, int],
    max_turns: int,
    turns_consumed: int,
    max_depth: int,
    depth: int,
) -> Mapping[str, int]:
    """Headroom per dimension, floored at zero.

    Flooring matters: an overspent dimension reports `0`, never a negative
    number that a later subtraction could read as available headroom.
    """
    remaining = {
        dimension: max(
            0,
            int(harness_budget.get(dimension, 0) or 0)
            - int(budget_consumed.get(dimension, 0) or 0),
        )
        for dimension in ADDITIVE_DIMENSIONS
    }
    remaining["turns"] = max(0, int(max_turns) - int(turns_consumed))
    remaining["depth"] = max(0, int(max_depth) - int(depth))
    return remaining
