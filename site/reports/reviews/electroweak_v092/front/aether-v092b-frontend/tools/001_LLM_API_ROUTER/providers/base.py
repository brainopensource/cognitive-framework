"""Abstract base class for LLM providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str
    latency_ms: int
    ttft_ms: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd_micros: int
    raw_payload: Dict[str, Any]
    error: Optional[str] = None


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.2,
        stream: bool = False,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate response from the LLM provider."""
        raise NotImplementedError
