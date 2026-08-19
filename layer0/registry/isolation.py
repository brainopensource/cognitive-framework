"""Isolation broker stub. M1 exposes the interface; subprocess cells arrive in M2."""

from __future__ import annotations

from enum import Enum

__all__ = ["IsolationBroker", "IsolationTier"]


class IsolationTier(str, Enum):
    IN_PROCESS = "in_process"
    SUBPROCESS = "subprocess"
    CONTAINER = "container"
    WASM = "wasm"


class IsolationBroker:
    def start(self, plugin_id: str, tier: IsolationTier) -> str:
        if tier is IsolationTier.IN_PROCESS:
            return f"cell:{plugin_id}:in_process"
        raise NotImplementedError(f"{tier.value} isolation is an M2 substrate")

    def stop(self, cell_id: str) -> None:
        _ = cell_id
