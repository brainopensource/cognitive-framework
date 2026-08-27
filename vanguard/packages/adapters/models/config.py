"""Unified model registry loader.

This module is the ONLY accessor for model identities in production code.
Model names, band membership, per-band fallbacks and pricing live
exclusively in ``models_registry.json`` (the single source of truth).

Policy:
- No model-name literals are ever declared in Python code.
- Loading is fail-closed: a missing or corrupt registry raises
  ``ModelRegistryError`` instead of silently substituting hardcoded names.
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple, TypedDict

REGISTRY_FILENAME = "models_registry.json"


class ModelRegistry(TypedDict, total=False):
    default_model: str
    default_paid_model: str
    bands: Dict[str, List[str]]
    band_fallbacks: Dict[str, str]
    pricing_micros: Dict[str, Dict[str, int]]


class ModelRegistryError(RuntimeError):
    """Raised when the unified model registry is missing, invalid or incomplete."""


_REGISTRY_CACHE: ModelRegistry | None = None
_DEFAULT_REGISTRY_PATH = Path(__file__).parent / REGISTRY_FILENAME


def _require(registry: ModelRegistry, key: str) -> Any:
    value = registry.get(key)
    if value is None or value == {}:
        raise ModelRegistryError(
            f"model registry is missing required key {key!r}"
        )
    return value


def load_model_registry(path: Path | None = None) -> ModelRegistry:
    """Load (and cache) the unified model registry.

    An explicit ``path`` bypasses the cache and never pollutes it; callers
    using an explicit path receive fresh data on every call.
    """
    global _REGISTRY_CACHE
    if _REGISTRY_CACHE is not None and path is None:
        return _REGISTRY_CACHE

    registry_path = path if path is not None else _DEFAULT_REGISTRY_PATH
    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            data: ModelRegistry = json.load(f)
    except Exception as exc:
        raise ModelRegistryError(
            f"cannot load unified model registry from {registry_path}: {exc}"
        ) from exc

    # Fail closed on structural corruption so that no accessor can ever
    # invent a model name outside the JSON source of truth.
    _require(data, "default_model")
    _require(data, "default_paid_model")
    _require(data, "bands")

    if path is None:
        _REGISTRY_CACHE = data
    return data


def get_default_model() -> str:
    return str(load_model_registry()["default_model"])


def get_default_paid_model() -> str:
    return str(load_model_registry()["default_paid_model"])


def get_band_models(band: str) -> tuple[str, ...]:
    bands: dict[str, list[str]] = load_model_registry()["bands"]
    return tuple(bands.get(band, ()))


def get_band_model(band: str, index: int = 0) -> str:
    models = get_band_models(band)
    if models:
        return models[index % len(models)]
    fallbacks: Dict[str, str] = load_model_registry().get("band_fallbacks", {})
    try:
        return fallbacks[band]
    except KeyError:
        raise ModelRegistryError(
            f"model band {band!r} is empty and has no 'band_fallbacks' entry "
            f"in the unified model registry"
        ) from None


def get_free_model(index: int = 0) -> str:
    return get_band_model("free", index)


def get_medium_model(index: int = 0) -> str:
    return get_band_model("medium", index)


def get_high_model(index: int = 0) -> str:
    return get_band_model("high", index)


def get_testing_model(index: int = 0) -> str:
    return get_band_model("testing", index)


def get_pricing_micros_table() -> dict[str, tuple[int, int, int]]:
    pricing = load_model_registry().get("pricing_micros", {})
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
