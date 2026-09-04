"""Unified Model Provider Factory (EVO-09, GTS-13C §7.1, ADR-0047).

Provides a single, authoritative factory `create_model(model_spec, **kwargs)`
that resolves model ports through the unified model registry with fail-closed fallback.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from ...ports.model import ModelPort
from .cassette import Cassette, CassettePlayer, CassetteRecorder
from .config import (
    get_band_model,
    get_default_model,
    get_free_model,
    get_medium_model,
    get_testing_model,
    load_model_registry,
    get_offline_default,
    resolve_model,
)
from .fake import FakeModel
from .llama_cpp import LlamaCppModel
from .openrouter import OpenRouterModel

__all__ = [
    "ModelResolutionError",
    "create_model",
]

class ModelResolutionError(ValueError, RuntimeError):
    """Raised when a model specifier cannot be resolved or fails validation."""
    pass


def _load_cassette_file(path: Path | str) -> Cassette:
    p = Path(path).resolve()
    if not p.exists():
        raise ModelResolutionError(f"Cassette file does not exist: {p}")
    try:
        content = p.read_text(encoding="utf-8")
        return Cassette.from_json(content)
    except Exception as exc:
        raise ModelResolutionError(f"Failed to load cassette from {p}: {exc}") from exc


def create_model(
    model_spec: str | Mapping[str, Any],
    *,
    cassette_path: Path | str | None = None,
    record: bool = False,
    fake_proposals: Sequence[Mapping[str, Any]] | None = None,
    env_loader: Any = None,
    **kwargs: Any,
) -> ModelPort:
    """Resolve and construct a ModelPort from a model specifier or alias.

    Resolves:
    - 'fake' / 'mock' -> FakeModel(fake_proposals or [])
    - 'cassette:<path>' or cassette_path (record=False) -> CassettePlayer
    - cassette_path (record=True) -> CassetteRecorder wrapping delegate
    - 'llama_cpp:<model_name>' / 'llama:<model_name>' -> LlamaCppModel(model=model_name)
    - 'openrouter:<model_name>' or provider alias -> OpenRouterModel(resolved_name)
    - Aliases:
      * 'free' -> OpenRouter free band model
      * 'fast' -> OpenRouter medium band model
      * 'smart' -> OpenRouter high band model
      * 'local' -> LlamaCppModel local model
      * 'testing' -> OpenRouter testing band model
    
    Fails closed with typed ModelResolutionError on unknown provider or invalid scheme.
    """
    # If a cassette path is given for replay (record=False)
    if cassette_path is not None and not record:
        cassette = _load_cassette_file(cassette_path)
        return CassettePlayer(cassette)

    # Normalize model_spec
    if isinstance(model_spec, Mapping):
        provider = str(model_spec.get("provider") or model_spec.get("type") or "").strip().lower()
        model_name = str(model_spec.get("model") or model_spec.get("name") or "").strip()
        if not provider and not model_name:
            raise ModelResolutionError(f"Invalid model mapping spec: {model_spec!r}")
        if provider in {"fake", "mock"}:
            proposals = model_spec.get("proposals", fake_proposals)
            inner_model: ModelPort = FakeModel(proposals or [])
        elif provider in {"llama_cpp", "llama", "ollama", "local"}:
            inner_model = LlamaCppModel(model=model_name or get_offline_default("llama_cpp"))
        elif provider == "openrouter":
            inner_model = OpenRouterModel(model=resolve_model(model_name or get_default_model()))
        elif provider == "cassette":
            cas_p = model_spec.get("path") or cassette_path
            if not cas_p:
                raise ModelResolutionError("Cassette spec requires 'path'")
            cassette = _load_cassette_file(cas_p)
            inner_model = CassettePlayer(cassette)
        elif model_name:
            return create_model(
                model_name,
                cassette_path=cassette_path,
                record=record,
                fake_proposals=fake_proposals,
                env_loader=env_loader,
                **kwargs,
            )
        else:
            raise ModelResolutionError(f"Unsupported model provider in mapping: {provider!r}")

    elif isinstance(model_spec, str):
        spec = model_spec.strip()
        if not spec:
            raise ModelResolutionError("model_spec cannot be empty")

        if spec in {"fake", "mock"}:
            inner_model = FakeModel(fake_proposals or [])

        elif spec.startswith("fake:") or spec.startswith("mock:"):
            inner_model = FakeModel(fake_proposals or [])

        elif spec.startswith("cassette:"):
            path_part = spec[len("cassette:"):].strip()
            if not path_part:
                raise ModelResolutionError("cassette: spec requires a valid path")
            if not record:
                cassette = _load_cassette_file(path_part)
                inner_model = CassettePlayer(cassette)
            else:
                base_model = FakeModel(fake_proposals or [])
                return CassetteRecorder(delegate=base_model, output_path=path_part)

        elif spec.startswith(("llama_cpp:", "llama:", "ollama:")):
            scheme, _, target_model = spec.partition(":")
            target_model = target_model.strip()
            if not target_model:
                raise ModelResolutionError(f"{scheme}: spec requires a model name")
            inner_model = LlamaCppModel(model=target_model)

        elif spec.startswith("openrouter:"):
            target_model = spec[len("openrouter:"):].strip()
            if not target_model:
                raise ModelResolutionError("openrouter: spec requires a model name")
            inner_model = OpenRouterModel(model=resolve_model(target_model))

        elif spec == "local":
            inner_model = LlamaCppModel(model=get_offline_default("llama_cpp"))

        elif spec == "free":
            inner_model = OpenRouterModel(model=resolve_model("free"))

        elif spec == "fast":
            inner_model = OpenRouterModel(model=resolve_model("fast"))

        elif spec == "smart":
            inner_model = OpenRouterModel(model=resolve_model("smart"))

        elif spec == "testing":
            inner_model = OpenRouterModel(model=resolve_model("testing"))

        elif ":" in spec and not spec.startswith(("http://", "https://")):
            scheme, _, _ = spec.partition(":")
            if scheme not in {"llama_cpp", "llama", "ollama", "openrouter", "cassette", "fake", "mock"}:
                raise ModelResolutionError(f"Unsupported provider scheme: {scheme!r} in {spec!r}")
            raise ModelResolutionError(f"Invalid model spec: {spec!r}")

        else:
            # Check registry
            try:
                registry = load_model_registry()
                bands = registry.get("bands", {})
                all_models = {registry.get("default_model"), registry.get("default_paid_model")}
                for model_list in bands.values():
                    all_models.update(model_list)
                pricing = registry.get("pricing_micros", {})
                all_models.update(pricing.keys())

                inner_model = OpenRouterModel(model=resolve_model(spec))
            except ModelResolutionError:
                raise
            except Exception as exc:
                raise ModelResolutionError(f"Failed to resolve model {spec!r}: {exc}") from exc

    else:
        raise ModelResolutionError(f"model_spec must be str or Mapping, got {type(model_spec).__name__}")

    # If recording was requested with an explicit cassette_path
    if cassette_path is not None and record:
        return CassetteRecorder(delegate=inner_model, output_path=cassette_path)

    return inner_model
