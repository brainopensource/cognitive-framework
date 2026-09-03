"""Token and as-if-cloud price estimates. LAM itself is always $0."""

from __future__ import annotations

# Approximate OpenRouter Claude Sonnet input/output USD per token (order of magnitude).
_SONNET_IN = 3.0 / 1_000_000
_SONNET_OUT = 15.0 / 1_000_000


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, len(text) // 4)


def sonnet_usd(prompt_tokens: int, completion_tokens: int) -> float:
    return round(prompt_tokens * _SONNET_IN + completion_tokens * _SONNET_OUT, 6)
