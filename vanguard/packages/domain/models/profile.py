"""Versioned model behavior declarations.

These values describe protocol behavior only. Pricing, availability, and
observed reliability remain adapter/registry concerns.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Mapping

from ..canonicalisation.digest import digest_of


class ToolCallStyle(str, Enum):
    NATIVE = "native"
    JSON_SCHEMA = "json_schema"
    FENCED_JSON = "fenced_json"
    TEXT_GRAMMAR = "text_grammar"


@dataclass(frozen=True, slots=True)
class ModelCapabilityProfile:
    model_id: str
    version: str = "1"
    tool_call_style: ToolCallStyle = ToolCallStyle.FENCED_JSON
    supports_parallel_tool_calls: bool = False
    supports_system_role: bool = True
    supports_streaming: bool = True
    emits_reasoning: bool = False

    def __post_init__(self) -> None:
        if not self.model_id.strip() or not self.version.strip():
            raise ValueError("model_id and version are required")

    @property
    def identity(self) -> str:
        return digest_of(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "version": self.version,
            "tool_call_style": self.tool_call_style.value,
            "supports_parallel_tool_calls": self.supports_parallel_tool_calls,
            "supports_system_role": self.supports_system_role,
            "supports_streaming": self.supports_streaming,
            "emits_reasoning": self.emits_reasoning,
        }

    def degraded(self) -> "ModelCapabilityProfile":
        downgrade = {
            ToolCallStyle.NATIVE: ToolCallStyle.JSON_SCHEMA,
            ToolCallStyle.JSON_SCHEMA: ToolCallStyle.FENCED_JSON,
            ToolCallStyle.FENCED_JSON: ToolCallStyle.TEXT_GRAMMAR,
            ToolCallStyle.TEXT_GRAMMAR: ToolCallStyle.TEXT_GRAMMAR,
        }
        return replace(self, tool_call_style=downgrade[self.tool_call_style],
                       supports_parallel_tool_calls=False)


_PROFILES: dict[str, ModelCapabilityProfile] = {
    "fake": ModelCapabilityProfile(
        "fake",
        tool_call_style=ToolCallStyle.JSON_SCHEMA,
        supports_system_role=True,
    ),
    "openrouter/free": ModelCapabilityProfile(
        "openrouter/free",
        tool_call_style=ToolCallStyle.FENCED_JSON,
    ),
    # Primary production route: DeepSeek V4 Flash
    "deepseek/deepseek-v4-flash-0731": ModelCapabilityProfile(
        "deepseek/deepseek-v4-flash-0731",
        tool_call_style=ToolCallStyle.NATIVE,
        supports_parallel_tool_calls=True,
    ),
    # First fallback: GLM 5.3 Flash
    "z-ai/glm-5.3-flash": ModelCapabilityProfile(
        "z-ai/glm-5.3-flash",
        tool_call_style=ToolCallStyle.NATIVE,
    ),
    # Unverified routes remain on the degradation path until a provider-shape
    # vector proves native patch.apply and finish dispatch.
    "deepseek/deepseek-v4-pro": ModelCapabilityProfile(
        "deepseek/deepseek-v4-pro",
        tool_call_style=ToolCallStyle.FENCED_JSON,
    ),
    "google/gemini-3.8-flash": ModelCapabilityProfile(
        "google/gemini-3.8-flash",
        tool_call_style=ToolCallStyle.FENCED_JSON,
    ),
    # Native local inference via llama.cpp / llama-server
    "local-model": ModelCapabilityProfile(
        "local-model",
        tool_call_style=ToolCallStyle.NATIVE,
        supports_parallel_tool_calls=True,
    ),
}

_ALIASES: dict[str, str] = {
    "deepseek/deepseek-v4-flash": "deepseek/deepseek-v4-flash-0731",
    "deepseek-v4-flash": "deepseek/deepseek-v4-flash-0731",
    "deepseek/flash": "deepseek/deepseek-v4-flash-0731",
    "deepseek-v4-pro": "deepseek/deepseek-v4-pro",
    "deepseek/pro": "deepseek/deepseek-v4-pro",
    "glm-5.3-flash": "z-ai/glm-5.3-flash",
    "gemini-3.8-flash": "google/gemini-3.8-flash",
    "gemini-flash": "google/gemini-3.8-flash",
    "llama_cpp": "local-model",
    "llama": "local-model",
}


def profile_for(model_id: str | None) -> ModelCapabilityProfile:
    key = (model_id or "unknown").strip()
    resolved_key = _ALIASES.get(key, key)
    profile = _PROFILES.get(resolved_key)
    if profile is not None:
        return profile
    for prefix in ("openrouter:", "llama_cpp:", "llama:"):
        if resolved_key.startswith(prefix):
            stripped = resolved_key[len(prefix):]
            target = _ALIASES.get(stripped, stripped)
            if target in _PROFILES:
                return _PROFILES[target]
    return ModelCapabilityProfile(key or "unknown")

