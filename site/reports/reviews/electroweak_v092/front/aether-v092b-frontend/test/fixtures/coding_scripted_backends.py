"""Deterministic scripted backends. apps/coding was retired (M3)."""

from __future__ import annotations

from typing import Any, Callable, Mapping

__all__ = ["scripted_backend", "fake_backend"]


def scripted_backend(kind: str) -> Callable[[Mapping[str, Any]], tuple[Any, list[dict[str, Any]]]]:
    def backend(request: Mapping[str, Any]) -> tuple[Any, list[dict[str, Any]]]:
        _ = request
        raise RuntimeError(f"scripted backend {kind!r} requires packs/code-default compose")

    return backend


def fake_backend(kind: str) -> Callable[[Mapping[str, Any]], tuple[Any, list[dict[str, Any]]]]:
    return scripted_backend(kind)
