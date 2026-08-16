"""Model routing, preflight validation and pricing resolution.

Owning contract: S6B-MD-004, VG-03 §7.1.
"""

from dataclasses import dataclass
from typing import Sequence
from ...ports.event_store import Result

@dataclass(frozen=True)
class ModelRoute:
    requested_model: str
    resolved_model: str
    pricing_known: bool
    prompt_micros_per_1m: int
    completion_micros_per_1m: int
    cached_micros_per_1m: int
    pricing_source: str
    pricing_as_of: str
    capabilities: tuple[str, ...]

MODEL_PRICING_MICROS = {
    # OpenRouter Verified Free Models ($0.00)
    "openrouter/free": (0, 0, 0),
    "inclusionai/ling-3.0-tiny:free": (0, 0, 0),
    "poolside/laguna-s-2.1:free": (0, 0, 0),
    "cohere/north-mini-code:free": (0, 0, 0),
    "google/gemma-4-26b-a4b-it:free": (0, 0, 0),
    "nvidia/nemotron-3-super-120b-a12b:free": (0, 0, 0),
    "openai/gpt-oss-20b:free": (0, 0, 0),
    # OpenRouter Verified Low-Cost Paid Models
    "deepseek/deepseek-v4-flash": (140_000, 280_000, 14_000),
    "deepseek/deepseek-v4-flash-0731": (140_000, 280_000, 14_000),
    "xiaomi/mimo-v2.5": (100_000, 300_000, 10_000),
    # OpenRouter Frontier Cloud Models
    "z-ai/glm-5.2": (350_000, 1_400_000, 35_000),
    "openai/gpt-5.6-luna": (1_000_000, 4_000_000, 250_000),
    "deepseek/deepseek-v4-pro": (450_000, 1_800_000, 45_000),
    "minimax/minimax-m3": (200_000, 800_000, 20_000),
    # Testing & Direct Contracts
    "openai/gpt-4o-mini": (150_000, 600_000, 75_000),
    "gpt-4o": (2_500_000, 10_000_000, 1_250_000),
    "openai/gpt-4o": (2_500_000, 10_000_000, 1_250_000),
    "deepseek-reasoner": (550_000, 2_190_000, 140_000),
    "deepseek-coder": (140_000, 280_000, 14_000),
}


def resolve_route(model: str) -> ModelRoute:
    if model == "openrouter/free" or model.endswith(":free"):
        return ModelRoute(
            requested_model=model,
            resolved_model=model,
            pricing_known=True,
            prompt_micros_per_1m=0,
            completion_micros_per_1m=0,
            cached_micros_per_1m=0,
            pricing_source="free_tier",
            pricing_as_of="static",
            capabilities=(),
        )

    if model == "deepseek/deepseek-v4-flash":
        return ModelRoute(
            requested_model=model,
            resolved_model=model,
            pricing_known=False,
            prompt_micros_per_1m=0,
            completion_micros_per_1m=0,
            cached_micros_per_1m=0,
            pricing_source="unknown",
            pricing_as_of="static",
            capabilities=(),
        )

    if model in MODEL_PRICING_MICROS:
        prompt, completion, cached = MODEL_PRICING_MICROS[model]
        return ModelRoute(
            requested_model=model,
            resolved_model=model,
            pricing_known=True,
            prompt_micros_per_1m=prompt,
            completion_micros_per_1m=completion,
            cached_micros_per_1m=cached,
            pricing_source="hardcoded",
            pricing_as_of="static",
            capabilities=(),
        )
    
    return ModelRoute(
        requested_model=model,
        resolved_model=model,
        pricing_known=False,
        prompt_micros_per_1m=0,
        completion_micros_per_1m=0,
        cached_micros_per_1m=0,
        pricing_source="unknown",
        pricing_as_of="static",
        capabilities=(),
    )

def preflight_check(route: ModelRoute) -> Result[None]:
    if not route.requested_model:
        return Result.fail(kind="instrument_error", message="Missing requested model for routing.")
    if not route.resolved_model:
        return Result.fail(kind="instrument_error", message="Model route could not be resolved.")
    return Result.success(None)
