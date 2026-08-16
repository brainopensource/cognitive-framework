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
    "openai/gpt-4o-mini": (150_000, 600_000, 75_000),
    "openai/gpt-4o": (2_500_000, 10_000_000, 1_250_000),
    "anthropic/claude-3.5-sonnet": (3_000_000, 15_000_000, 300_000),
    "anthropic/claude-3-5-sonnet": (3_000_000, 15_000_000, 300_000),
    "anthropic/claude-3.5-haiku": (800_000, 4_000_000, 80_000),
    "anthropic/claude-3-5-haiku": (800_000, 4_000_000, 80_000),
    "google/gemini-2.0-flash-001": (100_000, 400_000, 25_000),
    "google/gemini-flash-1.5": (75_000, 300_000, 18_750),
    "deepseek/deepseek-chat": (140_000, 280_000, 14_000),
    "deepseek/deepseek-r1": (550_000, 2_190_000, 140_000),
    "meta-llama/llama-3.3-70b-instruct": (120_000, 300_000, 30_000),
}

def resolve_route(model: str) -> ModelRoute:
    if model == "openrouter/free":
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
