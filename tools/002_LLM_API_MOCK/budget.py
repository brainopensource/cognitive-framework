"""Live run budget gate and ledger ledger tracking for OpenRouter models."""

from __future__ import annotations

import os
from pathlib import Path

LEDGER_FILE = Path(__file__).resolve().parents[2] / "delete_me_later_dont_commit.md"
_CALL_COUNT = 0


def get_remaining_budget() -> float:
    """Read remaining USD budget from environment or delete_me_later_dont_commit.md."""
    if LEDGER_FILE.is_file():
        try:
            for line in LEDGER_FILE.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if "remaining" in line.lower() or "$" in line:
                    parts = line.replace("$", "").split()
                    for p in parts:
                        try:
                            val = float(p)
                            return val
                        except ValueError:
                            continue
        except Exception:
            pass

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


def record_live_call(band: str) -> None:
    """Track call count and append $0.05 ledger entry after 10 calls if ledger file exists."""
    global _CALL_COUNT
    _CALL_COUNT += 1

    if _CALL_COUNT % 10 == 0 and LEDGER_FILE.is_file():
        try:
            with LEDGER_FILE.open("a", encoding="utf-8") as f:
                f.write(f"\n- Ledger Entry: 10 live calls executed under band '{band}'. Deducted $0.05 USD.")
        except Exception:
            pass
