"""Hierarchical Multi-Model Router & Planner/Worker Synergy for 006_LLM_INT_MACHINE.

Coordinates high-reasoning Supervisor models (e.g. Claude 3.7 Sonnet, DeepSeek-R1, DeepSeek-V4-Pro)
for POMDP hypothesis planning with ultra-fast, low-cost Worker models (e.g. DeepSeek-V4-Flash,
Xiaomi MiMo v2.5 Pro at $0.10/M tokens) for surgical AST patch execution and test verification.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

try:
    from .config import HarnessConfig
    from .llm_client import OpenRouterClient, MockLLMClient, LLMResponse
except ImportError:
    from config import HarnessConfig
    from llm_client import OpenRouterClient, MockLLMClient, LLMResponse


@dataclass
class RoutingDecision:
    phase: str
    selected_model: str
    temperature: float
    role_description: str


class HierarchicalModelRouter:
    """Orchestrates model allocation based on problem phase and cognitive demands."""

    def __init__(
        self,
        planner_model: str = "deepseek/deepseek-v4-pro-0813",
        worker_model: str = "deepseek/deepseek-v4-flash-0731",
        qa_model: str = "deepseek/deepseek-v4-flash-0731",
        enable_dynamic_escalation: bool = True,
    ) -> None:
        self.planner_model = planner_model
        self.worker_model = worker_model
        self.qa_model = qa_model
        self.enable_dynamic_escalation = enable_dynamic_escalation
        self.worker_consecutive_failures = 0

    def select_model_for_turn(self, turn_number: int, current_phase: str) -> RoutingDecision:
        """Selects the optimal model for the active turn."""
        if current_phase == "PLANNING" or turn_number == 1:
            return RoutingDecision(
                phase="PLANNING",
                selected_model=self.planner_model,
                temperature=0.0,
                role_description="Supervisor: Architectural POMDP hypothesis & file localization",
            )
        elif current_phase == "QA_VERIFICATION":
            return RoutingDecision(
                phase="QA_VERIFICATION",
                selected_model=self.qa_model,
                temperature=0.0,
                role_description="QA Verifier: Regression & mutation invariance checking",
            )
        else:
            # If worker failed twice consecutively, escalate to planner model for recovery
            if self.enable_dynamic_escalation and self.worker_consecutive_failures >= 2:
                return RoutingDecision(
                    phase="ESCALATED_RECOVERY",
                    selected_model=self.planner_model,
                    temperature=0.2,
                    role_description="Escalated Supervisor: Complex repair reformulation",
                )
            
            return RoutingDecision(
                phase="EXECUTION",
                selected_model=self.worker_model,
                temperature=0.0,
                role_description="Fast Worker: Surgical AST patch application & test execution",
            )

    def record_turn_outcome(self, success: bool) -> None:
        if success:
            self.worker_consecutive_failures = 0
        else:
            self.worker_consecutive_failures += 1
