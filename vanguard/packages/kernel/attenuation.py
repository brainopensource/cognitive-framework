"""Attenuation: a child grant is never wider than its parent (`05 §4`).

A child is valid only when its actions are a subset, its resources are a
subset, and its constraints never increase time, uses, bytes, budget, risk or
resource surface.

Two rules carry the weight here:

* `K-26` — **there is no silent intersection.** An over-broad request is
  denied whole, recording what was requested and what was grantable (`K-25`),
  and the denial is alertable (`K-27`, `F-10`). A child repeatedly asking for
  authority beyond its parent is the strongest intrusion signal this shape of
  system produces, and narrowing it quietly discards that signal while looking
  more helpful.
* `K-48` — resource inclusion is the per-kind relation from `04 §5.3.1`. It is
  total on the defined pairs and denies every undefined pair, cross-kind
  comparisons included. A checker that returns "unknown" fails closed.

`MF-KRN-004` fails against either a widening selector or a silent
intersection.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Mapping, Sequence

from ..domain.selectors.resource_selector import decide
from .model import FailurePath

__all__ = [
    "AttenuationDenied",
    "AttenuationResult",
    "Constraints",
    "Scope",
    "attenuate",
    "RISK_ORDER",
]

#: `04 §1` RiskTier, ordered. A child may never raise the tier.
RISK_ORDER = ("low", "medium", "high", "critical")


@dataclass(frozen=True, slots=True)
class Constraints:
    """The bounded dimensions of a grant (`04 §5.2`).

    Every field is a ceiling: a child may lower it and never raise it.
    `max_uses`, `max_bytes` and `budget_usd_micros` are decimal strings on the
    wire (`CT-06`, VG-04 §0.4) and integers here, parsed at the boundary.
    """

    expires_at: str
    max_uses: int
    budget_usd_micros: int
    max_bytes: int | None = None
    max_effects: int | None = None
    risk_ceiling: str = "critical"
    max_depth: int = 8
    network_policy: str = "deny"

    def narrower_than(self, other: "Constraints") -> tuple[bool, str]:
        """Is `self` within `other` on every dimension? Reports the first
        dimension that widens, because a denial has to name a cause."""
        if self.expires_at > other.expires_at:
            return False, "expiresAt"
        if self.max_uses > other.max_uses:
            return False, "maxUses"
        if self.budget_usd_micros > other.budget_usd_micros:
            return False, "budget"
        if _exceeds(self.max_bytes, other.max_bytes):
            return False, "maxBytes"
        if _exceeds(self.max_effects, other.max_effects):
            return False, "maxEffects"
        if RISK_ORDER.index(self.risk_ceiling) > RISK_ORDER.index(other.risk_ceiling):
            return False, "requireApprovalAboveRisk"
        if self.max_depth > other.max_depth:
            return False, "depth"
        if other.network_policy == "deny" and self.network_policy != "deny":
            return False, "networkPolicy"
        return True, ""


def _exceeds(child: int | None, parent: int | None) -> bool:
    """`None` on a parent means unbounded; `None` on a child means it inherits
    the parent's bound, which is never a widening."""
    if child is None:
        return False
    if parent is None:
        return False
    return child > parent


@dataclass(frozen=True, slots=True)
class Scope:
    """The authority surface of a grant or a request for one.

    `sealed` is set by `attenuate()` when the parent withholds verbs. A sealed
    grant may not execute an action outside `actions` (`ADR-0067`). Unsealed
    grants may still widen on trusted justification.
    """

    actions: frozenset[str]
    resources: tuple[Mapping[str, Any], ...]
    constraints: Constraints
    depth: int = 0
    sealed: bool = False


@dataclass(frozen=True, slots=True)
class AttenuationDenied:
    """`K-25`: the denial records both sides. Never just "denied"."""

    dimension: str
    requested: Any
    grantable: Any
    failure: FailurePath = FailurePath.DENIED_SCOPE_ESCALATION
    alertable: bool = True


@dataclass(frozen=True, slots=True)
class AttenuationResult:
    granted: Scope | None
    denial: AttenuationDenied | None = None

    @property
    def ok(self) -> bool:
        return self.granted is not None


def attenuate(parent: Scope, request: Scope) -> AttenuationResult:
    """Narrow `request` under `parent`, or deny (`K-23`, `K-25`, `K-26`).

    On success the result is exactly the request, which is by then proven to
    be a subset of both operands — so the function is idempotent, and a second
    application over its own output changes nothing.
    """
    extra_actions = sorted(request.actions - parent.actions)
    if extra_actions:
        return AttenuationResult(None, AttenuationDenied(
            "actions", extra_actions, sorted(parent.actions)))

    ungrantable = [
        resource for resource in request.resources
        if not any(decide(held, resource).included for held in parent.resources)
    ]
    if ungrantable:
        # `K-26`: the grantable subset is *reported*, never substituted.
        grantable = [
            resource for resource in request.resources
            if any(decide(held, resource).included for held in parent.resources)
        ]
        return AttenuationResult(None, AttenuationDenied(
            "resources", list(ungrantable), grantable))

    narrower, dimension = request.constraints.narrower_than(parent.constraints)
    if not narrower:
        return AttenuationResult(None, AttenuationDenied(
            "constraints." + dimension,
            getattr(request.constraints, _FIELD_BY_DIMENSION.get(dimension, dimension), None),
            getattr(parent.constraints, _FIELD_BY_DIMENSION.get(dimension, dimension), None)))

    # `K-24`: a child's depth is the parent's plus one, bounded.
    depth = parent.depth + 1
    if depth > parent.constraints.max_depth:
        return AttenuationResult(None, AttenuationDenied(
            "depth", depth, parent.constraints.max_depth))

    return AttenuationResult(replace(
        request,
        depth=depth,
        sealed=request.sealed or request.actions < parent.actions,
    ))


_FIELD_BY_DIMENSION = {
    "expiresAt": "expires_at",
    "maxUses": "max_uses",
    "budget": "budget_usd_micros",
    "maxBytes": "max_bytes",
    "maxEffects": "max_effects",
    "requireApprovalAboveRisk": "risk_ceiling",
    "networkPolicy": "network_policy",
}


def covers(parent: Scope, child: Scope) -> bool:
    """Is `child` entirely within `parent`? The relation `attenuate` decides,
    exposed for the property tests that check monotone decrease."""
    if not child.actions <= parent.actions:
        return False
    if not all(any(decide(held, resource).included for held in parent.resources)
               for resource in child.resources):
        return False
    narrower, _ = child.constraints.narrower_than(parent.constraints)
    return narrower


def resource_subset(parent: Sequence[Mapping[str, Any]],
                    child: Sequence[Mapping[str, Any]]) -> bool:
    """`K-48`, spelled out: every child selector under some parent selector,
    with undefined pairs denied by `domain`'s relation."""
    return all(any(decide(held, resource).included for held in parent)
               for resource in child)
