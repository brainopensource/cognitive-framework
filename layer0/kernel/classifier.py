"""Capability-widening classification (K-32, K-08) and sink-class mediation (ADR-M0-11)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from layer0.events.selectors import decide
from layer0.spi.types_gen import EffectRequest, SinkClass

__all__ = ["HeldAuthority", "SinkMismatch", "SinkRegistry", "StandardClassifier"]


@dataclass(frozen=True, slots=True)
class HeldAuthority:
    principal: str
    actions: frozenset[str]
    resources: tuple[Mapping[str, Any], ...] = ()
    max_depth: int = 8


class SinkMismatch(ValueError):
    """Privileged sink declared weaker than it is (MF-KRN-008)."""


class SinkRegistry:
    PRIVILEGED_PREFIXES = ("fs.write", "fs.delete", "net.", "exec.", "proc.", "secret.")
    OBSERVATION_PREFIXES = ("fs.read", "fs.stat", "fs.list", "git.read")

    def __init__(self) -> None:
        self._sinks: dict[str, SinkClass] = {}

    def register(self, action: str, sink_class: SinkClass) -> None:
        actual = self.inferred_class(action)
        if actual is SinkClass.PRIVILEGED and sink_class is not SinkClass.PRIVILEGED:
            raise SinkMismatch(
                f"{action!r} is a privileged sink; declaring it {sink_class.value!r} "
                "would skip the descriptor-bound grant (MF-KRN-008)"
            )
        if actual is SinkClass.OBSERVATION and sink_class is SinkClass.ADVISORY:
            raise SinkMismatch(
                f"{action!r} observes external state; declaring it 'advisory' would skip "
                "the selector check and the provenance label"
            )
        self._sinks[action] = sink_class

    def inferred_class(self, action: str) -> SinkClass:
        if action.startswith(self.PRIVILEGED_PREFIXES):
            return SinkClass.PRIVILEGED
        if action.startswith(self.OBSERVATION_PREFIXES):
            return SinkClass.OBSERVATION
        return SinkClass.ADVISORY

    def sink_class(self, action: str) -> SinkClass:
        if action in self._sinks:
            return self._sinks[action]
        inferred = self.inferred_class(action)
        return inferred if inferred is not SinkClass.ADVISORY else SinkClass.PRIVILEGED

    def requires_grant(self, action: str) -> bool:
        return self.sink_class(action) is SinkClass.PRIVILEGED

    def registered(self) -> Mapping[str, SinkClass]:
        return dict(self._sinks)


class StandardClassifier:
    def __init__(self, authorities: Sequence[HeldAuthority] = ()) -> None:
        self._by_principal = {held.principal: held for held in authorities}

    def hold(self, held: HeldAuthority) -> None:
        self._by_principal[held.principal] = held

    def widens_capability(self, request: EffectRequest, *, principal: str, depth: int) -> bool:
        held = self._by_principal.get(principal)
        if held is None:
            return True
        if request.verb not in held.actions:
            return True
        if depth > held.max_depth:
            return True
        return not any(decide(resource, request.selector).included
                       for resource in held.resources)


@dataclass(frozen=True, slots=True)
class ClassificationTrace:
    widens: bool
    reason: str
    grantable: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
