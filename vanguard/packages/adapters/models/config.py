import json
from pathlib import Path
from typing import Any, Dict, List, Tuple, TypedDict, cast

class ModelRegistry(TypedDict, total=False):
    default_model: str
    default_paid_model: str
    bands: dict[str, list[str]]
    pricing_micros: dict[str, dict[str, int]]

_REGISTRY_CACHE: ModelRegistry | None = None

def load_model_registry(path: Path | None = None) -> ModelRegistry:
    global _REGISTRY_CACHE
    if _REGISTRY_CACHE is not None and path is None:
        return _REGISTRY_CACHE
    
    registry_path = path or (Path(__file__).parent / "models_registry.json")
    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if path is None:
                _REGISTRY_CACHE = data
            return data
    except Exception:
        fallback: ModelRegistry = {
            "default_model": "openrouter/free",
            "default_paid_model": "deepseek/deepseek-v4-flash-0731",
            "bands": {
                "free": ["openrouter/free"],
                "medium": ["deepseek/deepseek-v4-flash-0731"],
                "high": ["openai/gpt-5.6-luna"],
                "testing": ["openrouter/free"],
            },
            "pricing_micros": {
                "openrouter/free": {"prompt": 0, "completion": 0, "cached": 0},
                "deepseek/deepseek-v4-flash-0731": {"prompt": 140000, "completion": 280000, "cached": 14000},
            }
        }
        return fallback

def get_default_model() -> str:
    registry = load_model_registry()
    return registry.get("default_model", "openrouter/free")

def get_default_paid_model() -> str:
    registry = load_model_registry()
    return registry.get("default_paid_model", "deepseek/deepseek-v4-flash")

def get_band_models(band: str) -> tuple[str, ...]:
    registry = load_model_registry()
    bands = registry.get("bands", {})
    return tuple(bands.get(band, []))

def get_free_model(index: int = 0) -> str:
    models = get_band_models("free")
    if not models:
        return "openrouter/free"
    return models[index % len(models)]

def get_medium_model(index: int = 0) -> str:
    models = get_band_models("medium")
    if not models:
        return "deepseek/deepseek-v4-flash"
    return models[index % len(models)]

def get_high_model(index: int = 0) -> str:
    models = get_band_models("high")
    if not models:
        return "openai/gpt-4o"
    return models[index % len(models)]

def get_testing_model(index: int = 0) -> str:
    models = get_band_models("testing")
    if not models:
        return "openai/gpt-4o-mini"
    return models[index % len(models)]

def get_pricing_micros_table() -> dict[str, tuple[int, int, int]]:
    registry = load_model_registry()
    pricing = registry.get("pricing_micros", {})
    return {
        model: (
            prices.get("prompt", 0),
            prices.get("completion", 0),
            prices.get("cached", 0)
        )
        for model, prices in pricing.items()
    }

def get_pricing_usd_table() -> dict[str, tuple[float, float, float]]:
    micros = get_pricing_micros_table()
    return {
        model: (
            p / 1_000_000.0,
            c / 1_000_000.0,
            k / 1_000_000.0
        )
        for model, (p, c, k) in micros.items()
    }
