"""BaaC Fail-Closed Budget and Request Guard.

Enforces:
1. Strict Request Caps (configurable, default: max 500 requests per campaign).
2. Strict Cost Caps (configurable, default: max $0.10 per campaign).
3. Open/Configurable Model Allowlist (supports frontier, mid, cheap, free, local, and mock models).
4. Pre-call assertion: Aborts fail-closed BEFORE issuing any provider request if caps are met.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple


# USD Pricing Table per 1M tokens: (prompt_rate, completion_rate, display_name)
MODEL_PRICING_TABLE: Dict[str, Tuple[float, float, str]] = {
    # Frontier Models (SOTA)
    "anthropic/claude-3.7-sonnet": (3.00, 15.00, "Claude 3.7 Sonnet"),
    "anthropic/claude-3-opus": (15.00, 75.00, "Claude 3 Opus"),
    "openai/gpt-4.5-preview": (75.00, 150.00, "GPT-4.5 Preview"),
    "openai/o3-mini": (1.10, 4.40, "o3-mini"),
    "openai/gpt-4o": (2.50, 10.00, "GPT-4o"),
    "google/gemini-2.5-pro": (1.25, 5.00, "Gemini 2.5 Pro"),
    "google/gemini-2.0-flash": (0.10, 0.40, "Gemini 2.0 Flash"),
    
    # Cheap / Fast Cloud Models
    "deepseek/deepseek-v4-flash-0731": (0.065, 0.18, "DeepSeek V4 Flash"),
    "deepseek/deepseek-chat": (0.14, 0.28, "DeepSeek V3"),
    "deepseek/deepseek-r1": (0.55, 2.19, "DeepSeek R1"),
    "z-ai/glm-5.3-flash": (0.075, 0.25, "GLM 5.3 Flash"),
    "meta-llama/llama-3.3-70b-instruct": (0.12, 0.30, "Llama 3.3 70B"),
    
    # Free Cloud Models ($0.00)
    "openrouter/free": (0.00, 0.00, "OpenRouter Free"),
    "cohere/north-mini-code:free": (0.00, 0.00, "North Mini Code Free"),
    "deepseek/deepseek-r1:free": (0.00, 0.00, "DeepSeek R1 Free"),
    "meta-llama/llama-3.3-70b-instruct:free": (0.00, 0.00, "Llama 3.3 Free"),
    "qwen/qwen-2.5-coder-32b-instruct:free": (0.00, 0.00, "Qwen 2.5 Coder Free"),
    
    # Local Ollama Models ($0.00)
    "ollama/qwen2.5:1.5b": (0.00, 0.00, "Qwen 2.5 1.5B Local"),
    "ollama/qwen2.5:7b": (0.00, 0.00, "Qwen 2.5 7B Local"),
    "ollama/llama3.2:3b": (0.00, 0.00, "Llama 3.2 3B Local"),
    "ollama/deepseek-r1:14b": (0.00, 0.00, "DeepSeek R1 14B Local"),
    
    # LAM Mock Engine ($0.00)
    "lam-mock": (0.00, 0.00, "LAM Replay Engine"),
    "lam/t1-calculator": (0.00, 0.00, "LAM Scenario Replay"),
}


class BudgetExceededError(RuntimeError):
    """Raised when a budget or request cap is exceeded."""


class DisallowedModelError(ValueError):
    """Raised when an unapproved model is requested."""


class UnknownUsageError(RuntimeError):
    """Raised when token usage is unknown or missing."""


@dataclass(frozen=True, slots=True)
class BudgetCapConfig:
    """Configurable budget, token, and request limits."""

    max_requests: int = 500
    max_cost_usd: float = 0.10
    max_tokens: int = 1_000_000
    max_turns: int = 12
    allowed_models: Optional[tuple[str, ...]] = None  # None means all models permitted


class BudgetTracker:
    """Tracks token consumption, request counts, cached tokens, and cost pre-call."""

    def __init__(self, config: BudgetCapConfig | None = None) -> None:
        self.config = config or BudgetCapConfig()
        self.request_count = 0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cached_tokens = 0
        self.total_cost_usd = 0.0
        self.records: List[Dict[str, Any]] = []

    @property
    def total_tokens(self) -> int:
        return self.total_prompt_tokens + self.total_completion_tokens

    def check_pre_call(self, model: str) -> None:
        """Pre-flight check before issuing any LLM API call."""
        # 1. Model Allowlist Check (if configured)
        if self.config.allowed_models and len(self.config.allowed_models) > 0:
            if "all" not in self.config.allowed_models:
                clean_model = model.strip()
                if not any(clean_model == m or clean_model.startswith(m.rstrip("*")) for m in self.config.allowed_models):
                    raise DisallowedModelError(
                        f"Model {model!r} is not in the BaaC allowlist: {self.config.allowed_models}"
                    )

        # 2. Request count cap
        if self.request_count >= self.config.max_requests:
            raise BudgetExceededError(
                f"Fail-closed abort: Request cap exceeded ({self.request_count}/{self.config.max_requests} requests)"
            )

        # 3. Token count cap
        if self.total_tokens >= self.config.max_tokens:
            raise BudgetExceededError(
                f"Fail-closed abort: Token cap exceeded ({self.total_tokens}/{self.config.max_tokens} tokens)"
            )

        # 4. Cost cap
        if self.total_cost_usd >= self.config.max_cost_usd:
            raise BudgetExceededError(
                f"Fail-closed abort: Cost cap exceeded (${self.total_cost_usd:.5f} >= ${self.config.max_cost_usd:.5f} USD)"
            )

    def record_request(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        cached_tokens: int = 0,
        reported_cost: float | None = None,
    ) -> float:
        """Record an executed request and update cumulative budget metrics."""
        if prompt_tokens is None or completion_tokens is None or prompt_tokens < 0 or completion_tokens < 0:
            raise UnknownUsageError("Unknown or invalid token usage: usage cannot be None or negative and blocks execution.")

        self.request_count += 1
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.total_cached_tokens += max(0, cached_tokens)

        # Compute cost via centralized pricing table if reported cost not given
        if reported_cost is not None and reported_cost > 0.0:
            call_cost = reported_cost
        elif model in MODEL_PRICING_TABLE:
            p_rate, c_rate, _ = MODEL_PRICING_TABLE[model]
            call_cost = ((prompt_tokens * p_rate) + (completion_tokens * c_rate)) / 1_000_000.0
        elif model.startswith("lam") or "free" in model or "ollama" in model:
            call_cost = 0.0
        else:
            # Default fallback rate ($0.50 / $1.50 per M)
            call_cost = ((prompt_tokens * 0.50) + (completion_tokens * 1.50)) / 1_000_000.0

        self.total_cost_usd += call_cost

        self.records.append({
            "request_index": self.request_count,
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "cached_tokens": cached_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "call_cost_usd": round(call_cost, 6),
            "cumulative_cost_usd": round(self.total_cost_usd, 6),
        })

        return call_cost

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requestCount": self.request_count,
            "maxRequests": self.config.max_requests,
            "totalPromptTokens": self.total_prompt_tokens,
            "totalCompletionTokens": self.total_completion_tokens,
            "totalCachedTokens": self.total_cached_tokens,
            "totalTokens": self.total_tokens,
            "maxTokens": self.config.max_tokens,
            "totalCostUsd": round(self.total_cost_usd, 6),
            "maxCostUsd": self.config.max_cost_usd,
        }
