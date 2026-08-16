"""Live run budget gate for OpenRouter models."""

from __future__ import annotations

import os
from pathlib import Path


def get_remaining_budget() -> float:
    """Read remaining USD budget from environment or default to 0.0."""
    val = os.environ.get("LAM_BUDGET_REMAINING", "0.0")
    try:
        return float(val)
    except ValueError:
        return 0.0


def allow_live_call(remaining_usd: float, band: str) -> None:
    """Verify whether a live call is allowed under the current budget and band rules."""
    band_name = band.lower().strip()
    if band_name == "free":
        return

    if remaining_usd <= 0.0:
        raise RuntimeError(
            f"Live call denied for paid band '{band_name}': remaining budget is ${remaining_usd:.2f} USD"
        )
