"""Injected kernel ports. Kernel never imports adapters."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

__all__ = ["Clock", "EffectAdapter", "EventSink", "Ledger"]


@runtime_checkable
class Clock(Protocol):
    def now(self) -> str: ...


@runtime_checkable
class EffectAdapter(Protocol):
    name: str

    def healthy(self) -> bool: ...

    def execute(self, request: object, ctx: object) -> object: ...


@runtime_checkable
class EventSink(Protocol):
    def emit(self, event: object) -> None: ...


@runtime_checkable
class Ledger(Protocol):
    def append_intent(self, event: object) -> None: ...
