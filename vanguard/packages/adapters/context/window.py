"""Prefix-stable context window with suffix sliding/truncation (SPEC §2.2)."""

from __future__ import annotations

from typing import ClassVar, Sequence

from layer0.spi.result import Ok, Result
from layer0.spi.types_gen import (
    CompactionReport,
    ContextBundle,
    EffectFailure,
    EpisodeView,
    Receipt,
)

__all__ = ["DefaultContextAdapter"]


class DefaultContextAdapter:
    spi_version: ClassVar[str] = "1.0"

    def __init__(self, system_prefix: str = "") -> None:
        self._prefix = system_prefix
        self._notes: list[str] = []

    def compile(self, view: EpisodeView, budget_tokens: int) -> Result[ContextBundle]:
        suffix = self._suffix(view)
        if budget_tokens > 0:
            suffix = _fit(suffix, budget_tokens)
        tokens = _tokens(self._prefix) + _tokens(suffix)
        return Ok(ContextBundle(prefix=self._prefix, suffix=suffix, token_count=tokens))

    def ingest(self, receipts: Sequence[Receipt]) -> None:
        for receipt in receipts:
            self._notes.append(f"{receipt.outcome}:{receipt.request_digest}")

    def compact(self, pressure: float) -> Result[CompactionReport]:
        removed = _tokens("\n".join(self._notes))
        if pressure >= 1.0:
            self._notes.clear()
        elif self._notes:
            self._notes = self._notes[-1:]
        return Ok(CompactionReport(removed_tokens=removed, strategy="slide"))

    def reground(self, error: EffectFailure) -> Result[ContextBundle]:
        self._notes.append(f"reground:{error.verb}:{error.detail}")
        return Ok(ContextBundle(prefix=self._prefix, suffix=error.detail, token_count=_tokens(error.detail)))

    def _suffix(self, view: EpisodeView) -> str:
        parts = [view.goal]
        if view.notes:
            parts.append(view.notes)
        parts.extend(self._notes)
        return "\n".join(parts)


def _tokens(text: str) -> int:
    return max(0, (len(text) + 3) // 4)


def _fit(text: str, budget_tokens: int) -> str:
    budget = max(0, budget_tokens * 4)
    if len(text) <= budget:
        return text
    return text[-budget:]
