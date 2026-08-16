"""Provider registry and factory."""

from __future__ import annotations

from .base import BaseLLMProvider, LLMResponse
from .openrouter import OpenRouterProvider
from .ollama import OllamaProvider
from .mock_provider import MockProvider


def get_provider(name: str, **kwargs) -> BaseLLMProvider:
    provider_name = name.lower().strip()
    if provider_name in ("openrouter", "or"):
        return OpenRouterProvider(**kwargs)
    elif provider_name in ("ollama", "local"):
        return OllamaProvider(**kwargs)
    elif provider_name in ("mock", "stub", "lam"):
        return MockProvider(**kwargs)
    else:
        raise ValueError(f"Unknown provider '{name}'. Choose from: openrouter, ollama, mock")
