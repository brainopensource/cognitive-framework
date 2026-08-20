"""Route EffectRequest verbs across pack toolkits."""

from __future__ import annotations

from typing import ClassVar, Mapping, Sequence

from vanguard.packages.domain.wire.result import Err, Result
from vanguard.packages.domain.wire.types_gen import EffectContext, EffectRequest, Health, Receipt, ToolSchema

__all__ = ["CompositeToolkit"]


class CompositeToolkit:
    spi_version: ClassVar[str] = "1.0"

    def __init__(self, toolkits: Sequence[object]) -> None:
        self._toolkits = list(toolkits)

    def verbs(self) -> Mapping[str, ToolSchema]:
        merged: dict[str, ToolSchema] = {}
        for toolkit in self._toolkits:
            merged.update(toolkit.verbs())
        return merged

    def execute(self, request: EffectRequest, ctx: EffectContext) -> Result[Receipt]:
        for toolkit in self._toolkits:
            if request.verb in toolkit.verbs():
                return toolkit.execute(request, ctx)
        return Err("unknown_verb", request.verb)

    def compensate(self, receipt: Receipt) -> Result[Receipt]:
        if self._toolkits:
            return self._toolkits[0].compensate(receipt)
        return Err("unknown_verb", "no toolkit")

    def health(self) -> Health:
        return Health(ok=all(toolkit.health().ok for toolkit in self._toolkits))
