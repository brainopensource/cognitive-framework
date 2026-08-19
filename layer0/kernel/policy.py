"""S5 AUTHORIZE — the decision, and only the decision."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence

from layer0.spi.types_gen import EffectRequest
from .attenuation import Scope, attenuate
from .model import FailurePath, Span
from .provenance import authority_violation

__all__ = ["Decision", "Mode", "Outcome", "StandardPolicy"]


class Outcome(str, Enum):
    ALLOW = "allow"
    REJECT = "reject"
    REQUIRE_APPROVAL = "require_approval"


class Mode(str, Enum):
    INTERACTIVE = "interactive"
    BENCHMARK = "benchmark"


@dataclass(frozen=True, slots=True)
class Decision:
    outcome: Outcome
    failure: FailurePath | None = None
    reason: str = ""
    granted_scope: Scope | None = None
    requested: Any = None
    grantable: Any = None
    alertable: bool = False
    untrusted_span_ids: tuple[str, ...] = field(default_factory=tuple)
    attenuated: bool = False


class StandardPolicy:
    def __init__(
        self,
        *,
        parent_scope: Scope,
        mode: Mode = Mode.INTERACTIVE,
        approval_required_above: str | None = None,
        risk_of: Mapping[str, str] | None = None,
    ) -> None:
        self._parent = parent_scope
        self._mode = mode
        self._approval_above = approval_required_above
        self._risk = dict(risk_of or {})

    def authorize(
        self,
        request: EffectRequest,
        *,
        widens_capability: bool,
        requested_scope: Scope,
        spans: Sequence[Span] | None = None,
    ) -> Decision:
        result = attenuate(self._parent, requested_scope)
        if not result.ok:
            denial = result.denial
            assert denial is not None
            return Decision(
                Outcome.REJECT,
                FailurePath.DENIED_SCOPE_ESCALATION,
                f"scope escalation on {denial.dimension}",
                requested=denial.requested,
                grantable=denial.grantable,
                alertable=True,
            )

        if requested_scope.sealed and request.verb not in requested_scope.actions:
            return Decision(
                Outcome.REJECT,
                FailurePath.DENIED_SCOPE_ESCALATION,
                f"action {request.verb!r} outside sealed scope",
                requested=sorted((request.verb,)),
                grantable=sorted(requested_scope.actions),
                alertable=True,
            )

        predicate = authority_violation(
            spans if spans is not None else (),
            widens_capability=widens_capability,
        )
        if predicate.violated:
            return Decision(
                Outcome.REJECT,
                FailurePath.DENIED_UNTRUSTED_JUSTIFYING,
                "capability widening justified by untrusted spans",
                alertable=True,
                untrusted_span_ids=predicate.untrusted_span_ids,
            )

        if self._needs_approval(request):
            if self._mode is Mode.BENCHMARK:
                return Decision(Outcome.REJECT, FailurePath.DENIED_ASK_FAIL_CLOSED,
                                "approval required; benchmark mode fails closed")
            return Decision(Outcome.REQUIRE_APPROVAL, FailurePath.APPROVAL_SUSPENDED,
                            "approval required", granted_scope=result.granted,
                            attenuated=bool(result.granted and result.granted.sealed))

        return Decision(
            Outcome.ALLOW, None, "", granted_scope=result.granted,
            attenuated=bool(result.granted and result.granted.sealed),
        )

    def _needs_approval(self, request: EffectRequest) -> bool:
        if self._approval_above is None:
            return False
        from .attenuation import RISK_ORDER

        risk = self._risk.get(request.verb, "low")
        return RISK_ORDER.index(risk) > RISK_ORDER.index(self._approval_above)
