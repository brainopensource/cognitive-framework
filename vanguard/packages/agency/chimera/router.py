"""Mixture-of-Cognition (MoC) and Contextual Bandit Router for CHIMERA.

Routes decisions among symbolic solvers, local AST/retrieval tools,
cheap models, frontier deliberative models, and branch search.
Uses Thompson sampling over Beta/Gaussian priors with deterministic fallbacks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
import random
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from .blackboard import (
    CognitiveBlackboard,
    CognitiveDirective,
    TaskFeatures,
)


@dataclass
class BanditArm:
    """Thompson Sampling Beta Distribution Arm for route selection."""

    name: str
    alpha: float = 1.0  # Successes + prior
    beta_param: float = 1.0  # Failures + prior
    cost_weight: float = 0.1
    latency_weight: float = 0.05

    def sample(self) -> float:
        """Sample expected reward from Beta distribution."""
        return random.betavariate(max(0.1, self.alpha), max(0.1, self.beta_param))

    def update(self, reward: float, cost: float = 0.0) -> None:
        """Update posterior based on outcome."""
        if reward > 0.5:
            self.alpha += 1.0
        else:
            self.beta_param += 1.0


class CognitiveRouter:
    """Routes cognitive tasks across heterogeneous mechanisms."""

    def __init__(self, seed: int = 42) -> None:
        self._rng = random.Random(seed)
        self._arms: dict[str, BanditArm] = {
            "RULE": BanditArm("RULE", alpha=10.0, beta_param=1.0, cost_weight=0.0),
            "LDA_AST": BanditArm("LDA_AST", alpha=5.0, beta_param=1.0, cost_weight=0.01),
            "EMBEDDING": BanditArm("EMBEDDING", alpha=4.0, beta_param=2.0, cost_weight=0.01),
            "SYMBOLIC_SOLVER": BanditArm("SYMBOLIC_SOLVER", alpha=8.0, beta_param=1.0, cost_weight=0.0),
            "CHEAP_LLM": BanditArm("CHEAP_LLM", alpha=3.0, beta_param=2.0, cost_weight=0.02),
            "FRONTIER_LLM": BanditArm("FRONTIER_LLM", alpha=7.0, beta_param=2.0, cost_weight=0.20),
            "SEARCH": BanditArm("SEARCH", alpha=5.0, beta_param=3.0, cost_weight=0.15),
        }

    def select(
        self,
        directive: CognitiveDirective,
        board: CognitiveBlackboard,
    ) -> str:
        """Select concrete computational route for the given directive."""
        # 1. If directive has explicit deterministic route, respect it
        if directive.route in ("RULE", "SYMBOLIC_SOLVER"):
            return directive.route

        # 2. Extract context features
        features = board.task_features
        uncertainty = board.uncertainty.aggregate_uncertainty

        # 3. Filter candidate arms by feasibility
        candidates = ["CHEAP_LLM", "FRONTIER_LLM"]
        if features.mathematical_invariants:
            candidates.append("SYMBOLIC_SOLVER")
        if uncertainty > 0.7 or features.multi_file:
            candidates.append("FRONTIER_LLM")
            candidates.append("SEARCH")
        if directive.kind.value == "retrieve":
            return "LDA_AST"

        # 4. Thompson sampling across eligible candidate arms
        best_score = -1e9
        selected_arm = "FRONTIER_LLM"
        for arm_name in candidates:
            arm = self._arms.get(arm_name)
            if not arm:
                continue
            sample_val = arm.sample()
            # Net reward penalized by cost
            net_score = sample_val - (arm.cost_weight * (1.0 - uncertainty))
            if net_score > best_score:
                best_score = net_score
                selected_arm = arm_name

        return selected_arm

    def record_feedback(self, route: str, success: bool, cost_usd: float = 0.0) -> None:
        """Record reward feedback to adapt future route sampling."""
        arm = self._arms.get(route)
        if arm:
            reward = 1.0 if success else 0.0
            arm.update(reward=reward, cost=cost_usd)
