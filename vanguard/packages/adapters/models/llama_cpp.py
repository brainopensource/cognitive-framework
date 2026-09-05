"""Local llama.cpp (llama-server) ModelPort adapter with OpenAI-compatible endpoint.

Invariants:
- Uses standard OpenAI /v1/chat/completions API format.
- Reuses OpenRouterModel transport, parsing, and streaming without code duplication.
- Local endpoint requires no remote credentials or legacy provider daemon.
"""

from __future__ import annotations

import os
from typing import Any, Mapping

from ...ports.event_store import Result
from ...ports.model import ContextBundle, Proposal, Sampling, ToolSchemas
from .openrouter import OpenRouterModel, Transport, StreamTransport

__all__ = ["LlamaCppModel", "DEFAULT_LLAMA_ENDPOINT", "DEFAULT_LLAMA_MODEL"]

DEFAULT_LLAMA_ENDPOINT = os.environ.get(
    "VANGUARD_LLAMA_ENDPOINT", "http://127.0.0.1:8080/v1/chat/completions"
)
DEFAULT_LLAMA_MODEL = os.environ.get("VANGUARD_LLAMA_MODEL", "local-model")


class LlamaCppModel(OpenRouterModel):
    """Local llama.cpp ModelPort adapter targeting llama-server."""

    def __init__(
        self,
        *,
        model: str = DEFAULT_LLAMA_MODEL,
        endpoint: str = DEFAULT_LLAMA_ENDPOINT,
        api_key_ref: str = "LLAMA_API_KEY",
        timeout_seconds: float = 120.0,
        transport: Transport | None = None,
        stream_transport: StreamTransport | None = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            model=model,
            endpoint=endpoint,
            api_key_ref=api_key_ref,
            provider="llama_cpp",
            request_timeout=timeout_seconds,
            transport=transport,
            stream_transport=stream_transport,
            stream=stream,
            **kwargs,
        )

    def _lookup_secret(self) -> str | None:
        # Local llama-server does not require an API key by default
        secret = super()._lookup_secret()
        return secret or "local-llama-cpp"

    @property
    def provider(self) -> str:
        return "llama_cpp"
