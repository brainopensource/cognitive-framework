"""Attenuation: a child grant is never wider than its parent (K-26, K-48)."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Mapping, Sequence

from layer0.events.selectors import decide
from .model import FailurePath

__all__ = [
    "AttenuationDenied",
    "AttenuationResult",
    "Constraints",
    "RISK_ORDER",
    "Scope",
    "attenuate",
    "covers",
    "resource_subset",
]

RISK_ORDER = ("low", "medium", "high", "critical")


@dataclass(frozen=True, slots=True)
class Constraints:
    expires_at: str
    max_uses: int
    budget_usd_micros: int
    max_bytes: int | None = None
    max_effects: int | None = None
    risk_ceiling: str = "critical"
    max_depth: int = 8
    network_policy: str = "deny"

    def narrower_than(self, other: "Constraints") -> tuple[bool, str]:
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
    if child is None or parent is None:
        return False
    return child > parent


@dataclass(frozen=True, slots=True)
class Scope:
    actions: frozenset[str]
    resources: tuple[Mapping[str, Any], ...]
    constraints: Constraints
    depth: int = 0
    sealed: bool = False


@dataclass(frozen=True, slots=True)
class AttenuationDenied:
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
    extra_actions = sorted(request.actions - parent.actions)
    if extra_actions:
        return AttenuationResult(None, AttenuationDenied(
            "actions", extra_actions, sorted(parent.actions)))

    ungrantable = [
        resource for resource in request.resources
        if not any(decide(held, resource).included for held in parent.resources)
    ]
    if ungrantable:
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
    if not child.actions <= parent.actions:
        return False
    if not all(any(decide(held, resource).included for held in parent.resources)
               for resource in child.resources):
        return False
    narrower, _ = child.constraints.narrower_than(parent.constraints)
    return narrower


def resource_subset(parent: Sequence[Mapping[str, Any]],
                    child: Sequence[Mapping[str, Any]]) -> bool:
    return all(any(decide(held, resource).included for held in parent)
               for resource in child)
