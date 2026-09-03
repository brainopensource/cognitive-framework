"""S5 AUTHORIZE — the decision, and only the decision.

Policy decides; the governor accounts; the adapter executes. This module
holds no budget state and no adapter knowledge (`01 §2`, single
responsibility).

The four outcomes correspond exactly to `F-06`..`F-10`. There is no fifth,
and there is no "allow with a warning": `K-26` forbids narrowing a request
without saying so, so a decision that is not `ALLOW` denies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence

from .attenuation import Scope, attenuate
from .model import EffectRequest, FailurePath, Span
from .provenance import authority_violation

__all__ = ["Decision", "Mode", "Outcome", "StandardPolicy"]


class Outcome(str, Enum):
    ALLOW = "allow"
    REJECT = "reject"
    REQUIRE_APPROVAL = "require_approval"


class Mode(str, Enum):
    """`K-17`: in benchmark mode approval never suspends, it denies (`F-07`).

    A run that blocks for a human has unbounded wall-clock *and* a human
    contributing to the measured outcome.
    """

    INTERACTIVE = "interactive"
    BENCHMARK = "benchmark"


@dataclass(frozen=True, slots=True)
class Decision:
    """What policy decided, and enough detail to record why (`K-25`)."""

    outcome: Outcome
    failure: FailurePath | None = None
    reason: str = ""
    granted_scope: Scope | None = None
    requested: Any = None
    grantable: Any = None
    alertable: bool = False
    untrusted_span_ids: tuple[str, ...] = field(default_factory=tuple)


class StandardPolicy:
    """Attenuation, the authority predicate and the approval rule, in order."""

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
        # 1. Scope. `F-10`, alertable (`K-27`): a child asking for more than
        #    its parent holds is the strongest intrusion signal available.
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

        # 1b. Sealed membership (`ADR-0067`). Keyed on the caller's grant, not
        #     on depth and not on a proper-subset requested_scope: spine's
        #     unsealed narrower scope may still widen on trusted justification.
        if requested_scope.sealed and request.action not in requested_scope.actions:
            return Decision(
                Outcome.REJECT,
                FailurePath.DENIED_SCOPE_ESCALATION,
                f"action {request.action!r} outside sealed scope",
                requested=sorted((request.action,)),
                grantable=sorted(requested_scope.actions),
                alertable=True,
            )

        # 2. The authority predicate. `F-09`: untrusted content may inform
        #    work, never authorise it. Evaluated over the *accumulated* spans.
        predicate = authority_violation(
            spans if spans is not None else request.justifying_spans,
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

        # 3. Approval. `F-07` in benchmark mode, `F-08` interactive.
        if self._needs_approval(request):
            if self._mode is Mode.BENCHMARK:
                return Decision(Outcome.REJECT, FailurePath.DENIED_ASK_FAIL_CLOSED,
                                "approval required; benchmark mode fails closed")
            return Decision(Outcome.REQUIRE_APPROVAL, FailurePath.APPROVAL_SUSPENDED,
                            "approval required", granted_scope=result.granted)

        return Decision(Outcome.ALLOW, None, "", granted_scope=result.granted)

    def _needs_approval(self, request: EffectRequest) -> bool:
        if self._approval_above is None:
            return False
        from .attenuation import RISK_ORDER

        risk = self._risk.get(request.action, "low")
        return RISK_ORDER.index(risk) > RISK_ORDER.index(self._approval_above)
