"""Mock Provider Implementation using local stub."""

from __future__ import annotations

from typing import Any
from .base import BaseLLMProvider, LLMResponse


class MockProvider(BaseLLMProvider):
    def __init__(self, message: str = "") -> None:
        self.message = message or (
            "this is not your answer, this is only a mocked llm api response stub, "
            "route correctly for the right llm api"
        )

    def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.2,
        stream: bool = False,
        **kwargs: Any,
    ) -> LLMResponse:
        prompt_tokens = max(1, len(prompt.split()))
        completion_tokens = max(1, len(self.message.split()))
        if stream:
            print(self.message)

        return LLMResponse(
            content=self.message,
            model=model,
            provider="mock",
            latency_ms=1,
            ttft_ms=1,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            cost_usd_micros=0,
            raw_payload={"mock": True},
        )
