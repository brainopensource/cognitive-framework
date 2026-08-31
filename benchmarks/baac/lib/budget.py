"""BaaC Fail-Closed Budget and Request Guard.

Enforces:
1. Strict Request Caps (default: max 300 requests per run).
2. Strict Cost Caps (default: max $0.10 USD per challenge).
3. Strict Model Allowlist (rejects unapproved or disallowed model literals).
4. Pre-call assertion: Aborts fail-closed BEFORE issuing any provider request if caps are met.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from vanguard.packages.runtime.root import resolve_model, get_pricing_usd_table


class BudgetExceededError(RuntimeError):
    """Raised when a budget or request cap is exceeded."""


class DisallowedModelError(ValueError):
    """Raised when an unapproved model is requested."""


@dataclass(frozen=True, slots=True)
class BudgetCapConfig:
    """Configurable budget and request limits."""

    max_requests: int = 300
    max_cost_usd: float = 0.10
    max_turns: int = 8
    allowed_models: tuple[str, ...] = (
        "deepseek/deepseek-v4-flash-0731",
        "z-ai/glm-5.3-flash",
        "openrouter/free",
        "lam-mock",
    )


class BudgetTracker:
    """Tracks token consumption, request counts, and cost pre-call."""

    def __init__(self, config: BudgetCapConfig | None = None) -> None:
        self.config = config or BudgetCapConfig()
        self.request_count = 0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost_usd = 0.0
        self.records: List[Dict[str, Any]] = []
        self._pricing = get_pricing_usd_table()

    @property
    def total_tokens(self) -> int:
        return self.total_prompt_tokens + self.total_completion_tokens

    def check_pre_call(self, model: str) -> None:
        """Pre-flight check before making an LLM API call."""
        # 1. Model Allowlist Check (LAM mock models are always allowed)
        if model != "lam-mock":
            resolved = resolve_model(model)
            if self.config.allowed_models and resolved not in self.config.allowed_models:
                raise DisallowedModelError(
                    f"Model {resolved!r} is not in the BaaC allowlist: {self.config.allowed_models}"
                )

        # 2. Request count cap
        if self.request_count >= self.config.max_requests:
            raise BudgetExceededError(
                f"Fail-closed abort: Request cap exceeded ({self.request_count}/{self.config.max_requests} requests)"
            )

        # 3. Cost cap
        if self.total_cost_usd >= self.config.max_cost_usd:
            raise BudgetExceededError(
                f"Fail-closed abort: Cost cap exceeded (${self.total_cost_usd:.5f} >= ${self.config.max_cost_usd:.5f} USD)"
            )

    def record_request(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        reported_cost: float | None = None,
    ) -> float:
        """Record an executed request and update cumulative budget metrics."""
        self.request_count += 1
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens

        # Compute cost via centralized pricing table if reported cost not given
        if reported_cost is not None and reported_cost > 0.0:
            call_cost = reported_cost
        elif model in self._pricing:
            p_rate, c_rate, _ = self._pricing[model]
            call_cost = ((prompt_tokens * p_rate) + (completion_tokens * c_rate)) / 1_000_000.0
        else:
            call_cost = 0.0

        self.total_cost_usd += call_cost

        self.records.append({
            "request_index": self.request_count,
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "call_cost_usd": call_cost,
            "cumulative_cost_usd": self.total_cost_usd,
        })

        return call_cost

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requestCount": self.request_count,
            "maxRequests": self.config.max_requests,
            "totalPromptTokens": self.total_prompt_tokens,
            "totalCompletionTokens": self.total_completion_tokens,
            "totalTokens": self.total_tokens,
            "totalCostUsd": self.total_cost_usd,
            "maxCostUsd": self.config.max_cost_usd,
        }
