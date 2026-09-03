"""`vg why <artifact>` — the three questions an artifact must answer (`S10-A-04`).

An artifact that cannot say what activated it, what it predicts, and what would
demote it is an artifact nobody can audit and nobody can retire. `_cmd_ExplainArtifact`
returned an empty string, so the CLI command existed and answered nothing.

All three answers are *derived*: activation from the ledger, prediction and
demotion from the `Claim` store (`S8-A-05`). Nothing is stored twice, so an
explanation cannot drift from the events it explains (`A-07`).

**Absence is reported, never smoothed.** An artifact with no claims says it has
no evidence rather than returning an empty section that reads like "nothing is
wrong". That distinction is the whole value of the command: an unevidenced
artifact and a well-evidenced one must not look alike.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

from ..domain.evidence.claim import Claim

__all__ = ["Explanation", "explain_artifact"]

#: Ledger events that bear on whether an artifact is active.
_ACTIVATION_KINDS = ("ArtifactCreated", "ActivationChanged", "ArtifactRetired")


@dataclass(frozen=True, slots=True)
class Explanation:
    """What activated it, what it predicts, what would demote it."""

    artifact_id: str
    status: str
    activation: tuple[Mapping[str, Any], ...] = ()
    predictions: tuple[Mapping[str, Any], ...] = ()
    demotions: tuple[Mapping[str, Any], ...] = ()
    stale: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifactId": self.artifact_id,
            "status": self.status,
            "activation": [dict(entry) for entry in self.activation],
            "predicts": [dict(entry) for entry in self.predictions],
            "wouldDemote": [dict(entry) for entry in self.demotions],
            "staleClaims": list(self.stale),
            "notes": list(self.notes),
        }


def explain_artifact(
    artifact_id: str,
    *,
    events: Iterable[Any] = (),
    claims: Sequence[Claim] = (),
    substrate_profile: str | None = None,
) -> Explanation:
    """Derive the explanation. Pure: no I/O, no store, no clock."""

    activation: list[Mapping[str, Any]] = []
    status = "unknown"
    for event in events:
        payload = getattr(event, "payload", None)
        if not isinstance(payload, Mapping):
            continue
        kind = str(payload.get("kind", ""))
        if kind not in _ACTIVATION_KINDS:
            continue
        if str(payload.get("artifactId") or payload.get("id") or "") != artifact_id:
            continue
        entry = {
            "kind": kind,
            "at": getattr(event, "occurred_at", None),
            "seq": getattr(event, "seq", None),
        }
        if kind == "ArtifactCreated":
            status = "active"
        elif kind == "ActivationChanged":
            status = str(payload.get("toStatus", status))
            entry["toStatus"] = status
        elif kind == "ArtifactRetired":
            status = "retired"
        activation.append(entry)

    mine = [claim for claim in claims if claim.subject == artifact_id]
    predictions = tuple(
        {
            "claimId": claim.id,
            "predicate": claim.predicate,
            "value": claim.value,
            "uncertainty": claim.uncertainty.to_wire(),
            "validIn": list(claim.validity.domains),
            "evaluatorClass": claim.evaluator.evaluator_class,
        }
        for claim in mine
    )
    demotions = tuple(
        {
            "claimId": claim.id,
            "condition": condition.condition,
            "checkKind": condition.check_kind,
            "checkRef": condition.check_ref,
        }
        for claim in mine
        for condition in claim.invalidation_conditions
    )
    stale = ()
    if substrate_profile is not None:
        stale = tuple(claim.id for claim in mine
                      if claim.is_stale_under(substrate_profile=substrate_profile))

    notes: list[str] = []
    if not activation:
        notes.append("no activation event for this artifact on the ledger")
    if not mine:
        # The load-bearing case. An artifact with no claim predicts nothing and
        # nothing would demote it, which is a finding -- not an empty section.
        notes.append("no evidence claim names this artifact: "
                     "it predicts nothing and nothing would demote it")
    if stale:
        notes.append("substrate has moved since these claims were recorded")

    return Explanation(
        artifact_id=artifact_id,
        status=status,
        activation=tuple(activation),
        predictions=predictions,
        demotions=demotions,
        stale=stale,
        notes=tuple(notes),
    )
