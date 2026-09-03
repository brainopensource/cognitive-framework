"""Capability-widening classification (`K-32`, `K-08`) and the sink registry.

> `K-32`. Capability widening is *true* when the request would grant an effect
> the principal does not already hold, or would escalate outside the
> perimeter; *false* when the request lies fully within the principal's
> declared actions and resources and escalates nothing.

The prototype hardcoded this to *true* for every subprocess call. The
authority predicate therefore appeared to fail closed on all tool use, and
three design documents recorded the resulting deadlock as a property of the
taint model. It was a constant standing in for a classifier that did not
exist, which is why `K-08` makes S4 a *call* and why `MF-KRN-001` fails
against any constant: no single boolean can satisfy both a within-authority
scenario and an escalation scenario.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from ..domain.selectors.resource_selector import decide
from .model import EffectRequest, SinkClass

__all__ = ["HeldAuthority", "SinkRegistry", "SinkMismatch", "StandardClassifier"]


@dataclass(frozen=True, slots=True)
class HeldAuthority:
    """What a principal already holds. The baseline widening is measured against."""

    principal: str
    actions: frozenset[str]
    resources: tuple[Mapping[str, Any], ...] = ()
    #: Depth ceiling the principal may not exceed without widening (`K-24`).
    max_depth: int = 8


class SinkMismatch(ValueError):
    """A registered effect declares a sink class weaker than it actually is.

    `MF-KRN-008`: a privileged sink declared `pure` skips the grant path
    entirely. The registry refuses the registration rather than the call, so
    the defect cannot reach dispatch.
    """


class SinkRegistry:
    """action → sink class. Open/closed: adding a capability is a registry
    entry plus a configuration line (`01 §2`), and the dispatcher never
    changes to accommodate one.
    """

    #: Actions whose namespace is privileged by construction. A registration
    #: claiming otherwise is a misclassification, not a preference.
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
        if actual is SinkClass.OBSERVATION and sink_class is SinkClass.PURE:
            raise SinkMismatch(
                f"{action!r} observes external state; declaring it 'pure' would skip "
                "the selector check and the provenance label (ICD §3)"
            )
        self._sinks[action] = sink_class

    def inferred_class(self, action: str) -> SinkClass:
        """What the action *is*, independent of what a caller declared."""
        if action.startswith(self.PRIVILEGED_PREFIXES):
            return SinkClass.PRIVILEGED
        if action.startswith(self.OBSERVATION_PREFIXES):
            return SinkClass.OBSERVATION
        return SinkClass.PURE

    def sink_class(self, action: str) -> SinkClass:
        """Registered class, or the inferred one. Unknown actions fail closed
        as privileged: an unregistered effect is not evidence of harmlessness."""
        if action in self._sinks:
            return self._sinks[action]
        inferred = self.inferred_class(action)
        return inferred if inferred is not SinkClass.PURE else SinkClass.PRIVILEGED

    def requires_grant(self, action: str) -> bool:
        """`ICD §3`: only privileged effects require a descriptor-bound grant."""
        return self.sink_class(action) is SinkClass.PRIVILEGED

    def registered(self) -> Mapping[str, SinkClass]:
        return dict(self._sinks)


class StandardClassifier:
    """`K-32`, as a computed predicate over the request and held authority."""

    def __init__(self, authorities: Sequence[HeldAuthority] = ()) -> None:
        self._by_principal = {held.principal: held for held in authorities}

    def hold(self, held: HeldAuthority) -> None:
        self._by_principal[held.principal] = held

    def widens_capability(self, request: EffectRequest) -> bool:
        held = self._by_principal.get(request.principal)
        if held is None:
            # An unknown principal holds nothing, so every request widens.
            return True
        if request.action not in held.actions:
            return True
        if request.depth > held.max_depth:
            # Depth is a budget dimension (`K-24`); exceeding the ceiling is an
            # escalation even when the action and resource are already held.
            return True
        # Resource containment uses the per-kind relation in `04 §5.3.1` via
        # `domain`. `K-48`: it denies every undefined pair, so an undecidable
        # comparison lands on the widening side — fail closed.
        return not any(decide(resource, request.resource).included
                       for resource in held.resources)


@dataclass(frozen=True, slots=True)
class ClassificationTrace:
    """Kept for the denial record: `K-25` requires denials to say what was
    requested *and* what was grantable."""

    widens: bool
    reason: str
    grantable: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
