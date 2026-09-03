"""Deterministic scripted ModelPort fake. No ambient I/O, clock, or network."""

from __future__ import annotations

from typing import Sequence, Union

from ...ports.event_store import Result
from ...ports.model import ContextBundle, Proposal, Sampling, ToolSchemas

__all__ = ["FakeModel"]

TapeItem = Union[Proposal, Result[Proposal]]


class FakeModel:
    """Serves recorded proposals in tape order; exhaustion is `instrument_error`."""

    def __init__(self, tape: Sequence[TapeItem]) -> None:
        self._tape = list(tape)
        self._cursor = 0

    def propose(
        self,
        context: ContextBundle,
        tools: ToolSchemas,
        sampling: Sampling,
    ) -> Result[Proposal]:
        del context, tools, sampling
        if self._cursor >= len(self._tape):
            return Result.fail(
                kind="instrument_error",
                message="scripted model exhausted: no more recorded interactions",
            )
        item = self._tape[self._cursor]
        self._cursor += 1
        if isinstance(item, Result):
            return item
        return Result.success(dict(item))
