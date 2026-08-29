"""LAR Pareto Frontier Cost & Token Optimizer for Vanguard Harness."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from vanguard.packages.adapters.models.config import get_band_models, get_default_paid_model, get_pricing_micros_table


class ProviderOptimizer:
    def __init__(self) -> None:
        self.pricing_micros = {"lam": 0, "ollama": 0, **get_pricing_micros_table()}
        self.free_model = get_band_models("free")[0]
        self.paid_model = get_default_paid_model()

    def recommend_provider(
        self,
        scenario_tier: int,
        policy: str = "balanced",
        budget_remaining_usd: float = 0.50,
        calibration_passed: bool = False,
    ) -> Dict[str, Any]:
        """Recommend a provider. Paid/high tiers require calibration_passed."""
        policy_clean = policy.lower().strip()

        if not calibration_passed:
            if scenario_tier <= 2 or policy_clean in {"min-cost", "balanced"}:
                if scenario_tier <= 2:
                    return {
                        "provider": "ollama",
                        "model": "llama3.2:3b",
                        "reason": "Calibration-first: local until a hidden-oracle patch exists",
                    }
                return {
                    "provider": "ollama",
                    "model": "llama3.2:3b",
                    "reason": "Calibration-first: refuse paid routing before T1 pass",
                }

        if policy_clean == "min-cost" or budget_remaining_usd <= 0.0:
            if scenario_tier <= 2:
                return {"provider": "ollama", "model": "llama3.2:3b", "reason": "Zero-cost local GPU execution"}
                return {"provider": "openrouter", "model": self.free_model, "reason": "Zero-cost cloud free tier"}

        if policy_clean == "min-tokens":
            if scenario_tier <= 2:
                return {"provider": "ollama", "model": "qwen2.5:1.5b", "reason": "Minimal prompt overhead"}
            return {"provider": "openrouter", "model": self.paid_model, "reason": "Configured token-efficient model"}

        # Default: Balanced Policy
        if scenario_tier <= 2:
            return {"provider": "ollama", "model": "llama3.2:3b", "reason": "Local GPU Tier 1/2 balance"}
        elif scenario_tier <= 3:
            return {"provider": "openrouter", "model": "cohere/north-mini-code:free", "reason": "Cloud Light Free balance"}
        elif scenario_tier <= 4:
            return {"provider": "openrouter", "model": self.paid_model, "reason": "Configured cloud balance"}
        else:
            return {"provider": "openrouter", "model": self.paid_model, "reason": "Configured highest enabled tier"}
