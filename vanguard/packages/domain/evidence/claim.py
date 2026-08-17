"""`EvidenceClaim` as a domain type (`VG-04 §10.2`, `GTS-13C T1.9`).

This is a **format lock** (`L-1`). Every run after it records evidence in the
final shape; every run before it needs migration. The shape is therefore not
invented here: `schemas/v4/evidence-claim.schema.json` and `VG-04 §10.2` own
it, and `T1.9` is explicit that v4's claim is kept exactly as written. What
this module adds is the part a JSON Schema cannot say.

**Two rules beyond the schema.**

`INV-1` is structural in the schema already: `invalidationConditions` is
required and non-empty. A claim that cannot state what would refute it is not
admissible, and an empty array fails at parse rather than at review.

`C-12` / `INV-2` is not, and it is the one this module exists for: at least one
condition must be **automatic**, and a claim whose `substrateProfile` digest has
moved is stale *without human review*. A claim whose staleness only a person
can notice is a claim whose staleness is never noticed -- the corpus rots
quietly and every number computed from it keeps looking fine. Automatic
staleness is a pure function of two digests, so nothing has to remember to run.

**Recorded, not consumed.** `support_count`, `last_corroborated_at` and
`protection_class` are carried on the type and read by nothing. This is the
argument `T4.11` already accepted for the competence prior: recording now costs
nothing, and retrofitting later costs a corpus migration. They are deliberately
withheld from `to_wire()` -- `VG-04` sets `additionalProperties: false`, so
emitting them before the Joint amendment (`S8-J-01`) would produce claims the
normative reader rejects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

__all__ = [
    "Claim",
    "ClaimError",
    "Evaluator",
    "InvalidationCondition",
    "Uncertainty",
    "Validity",
    "parse_claim",
]

#: `VG-04 §10.2`. No class receives abstract objectivity; claim strength is
#: predicate-scoped (`06 §4`).
EVALUATOR_CLASSES = (
    "mechanically_reproducible",
    "externally_grounded",
    "human_adjudicated",
    "learned_proxy",
    "composite",
    "inconclusive",
)
CHECK_KINDS = ("automatic", "scheduled", "manual")
UNCERTAINTY_KINDS = ("interval", "point", "qualitative", "unknown")
PROTECTION_CLASSES = ("none", "load_bearing", "pinned")


class ClaimError(ValueError):
    """A claim that cannot be admitted. Raised at parse, never later."""

    def __init__(self, path: str, message: str) -> None:
        super().__init__(f"{path}: {message}")
        self.path = path


def _require(source: Mapping[str, Any], keys: Sequence[str], path: str) -> None:
    missing = [key for key in keys if key not in source]
    if missing:
        raise ClaimError(path, f"missing required field(s): {', '.join(sorted(missing))}")


def _digest(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.startswith("sha256:") or len(value) != 71:
        raise ClaimError(path, "expected a sha256 digest")
    return value


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise ClaimError(path, "expected a non-empty string")
    return value


@dataclass(frozen=True, slots=True)
class InvalidationCondition:
    """What would show the claim no longer holds.

    `CT-53`: no mutable field inside a content-addressed artifact. Whether the
    check has *run* lives in `InvalidationCheckRecord`, not here.
    """

    condition: str
    check_kind: str
    check_ref: str | None = None

    @property
    def is_automatic(self) -> bool:
        return self.check_kind == "automatic"

    def to_wire(self) -> dict[str, Any]:
        wire: dict[str, Any] = {"condition": self.condition, "checkKind": self.check_kind}
        if self.check_ref is not None:
            wire["checkRef"] = self.check_ref
        return wire


@dataclass(frozen=True, slots=True)
class Evaluator:
    evaluator_id: str
    evaluator_class: str
    image_digest: str

    def to_wire(self) -> dict[str, Any]:
        return {
            "evaluatorId": self.evaluator_id,
            "class": self.evaluator_class,
            "imageDigest": self.image_digest,
        }


@dataclass(frozen=True, slots=True)
class Uncertainty:
    """An interval, never a point estimate -- when the kind says interval.

    A point estimate reported as if it were the finding is how a measurement
    stops carrying its own error bars.
    """

    kind: str
    lower: float | None = None
    upper: float | None = None
    n: int | None = None
    note: str | None = None

    def to_wire(self) -> dict[str, Any]:
        wire: dict[str, Any] = {"kind": self.kind}
        for key, value in (("lower", self.lower), ("upper", self.upper),
                           ("n", self.n), ("note", self.note)):
            if value is not None:
                wire[key] = value
        return wire


@dataclass(frozen=True, slots=True)
class Validity:
    """Where the claim held. Distinct from what would show it no longer holds."""

    domains: tuple[str, ...]
    note: str | None = None

    def to_wire(self) -> dict[str, Any]:
        wire: dict[str, Any] = {"domains": list(self.domains)}
        if self.note is not None:
            wire["note"] = self.note
        return wire


@dataclass(frozen=True, slots=True)
class Claim:
    """One measured statement, with the conditions that would refute it."""

    id: str
    subject: str
    predicate: str
    value: Any
    protocol: str
    evaluator: Evaluator
    environment_profile: str
    substrate_profile: str
    task_distribution: str
    uncertainty: Uncertainty
    validity: Validity
    invalidation_conditions: tuple[InvalidationCondition, ...]
    evidence_refs: tuple[str, ...] = ()
    derived_from: tuple[str, ...] = ()
    contradicts: tuple[str, ...] = ()
    expires_at: str | None = None

    # -- recorded, not consumed (withheld from the wire until `S8-J-01`) ----
    support_count: int = 0
    last_corroborated_at: str | None = None
    protection_class: str = "none"

    # -- `C-12` / `INV-2` ---------------------------------------------------

    def is_stale_under(self, *, substrate_profile: str) -> bool:
        """True when the substrate has moved out from under the measurement.

        No human review, no scheduled sweep, no reviewer remembering: two
        digests differ, so the claim no longer describes the thing it measured.
        """
        return substrate_profile != self.substrate_profile

    def staleness_reason(self, *, substrate_profile: str) -> str | None:
        if self.is_stale_under(substrate_profile=substrate_profile):
            return "substrate_profile_changed"
        return None

    @property
    def automatic_conditions(self) -> tuple[InvalidationCondition, ...]:
        return tuple(c for c in self.invalidation_conditions if c.is_automatic)

    def to_wire(self) -> dict[str, Any]:
        """The `VG-04 §10.2` shape, and nothing the reader would reject."""
        wire: dict[str, Any] = {
            "id": self.id,
            "subject": self.subject,
            "predicate": self.predicate,
            "value": self.value,
            "protocol": self.protocol,
            "evaluator": self.evaluator.to_wire(),
            "environmentProfile": self.environment_profile,
            "substrateProfile": self.substrate_profile,
            "taskDistribution": self.task_distribution,
            "uncertainty": self.uncertainty.to_wire(),
            "validity": self.validity.to_wire(),
            "invalidationConditions": [c.to_wire() for c in self.invalidation_conditions],
        }
        for key, value in (("evidenceRefs", self.evidence_refs),
                           ("derivedFrom", self.derived_from),
                           ("contradicts", self.contradicts)):
            if value:
                wire[key] = list(value)
        if self.expires_at is not None:
            wire["expiresAt"] = self.expires_at
        return wire


def _parse_conditions(raw: Any) -> tuple[InvalidationCondition, ...]:
    path = "EvidenceClaim/invalidationConditions"
    if not isinstance(raw, list):
        raise ClaimError(path, "expected an array")
    # `INV-1`, structural: a claim that cannot state what would refute it is
    # not admissible. This is the whole point of the field.
    if not raw:
        raise ClaimError(path, "at least one invalidationConditions entry is required")

    conditions: list[InvalidationCondition] = []
    for index, entry in enumerate(raw):
        where = f"{path}/{index}"
        if not isinstance(entry, Mapping):
            raise ClaimError(where, "expected an object")
        _require(entry, ("condition", "checkKind"), where)
        check_kind = _text(entry["checkKind"], f"{where}/checkKind")
        if check_kind not in CHECK_KINDS:
            raise ClaimError(f"{where}/checkKind", f"expected one of {CHECK_KINDS}")
        check_ref = entry.get("checkRef")
        if check_kind == "automatic" and check_ref is None:
            raise ClaimError(where, "an automatic condition must name its checkRef")
        if check_ref is not None:
            check_ref = _text(check_ref, f"{where}/checkRef")
        conditions.append(InvalidationCondition(
            condition=_text(entry["condition"], f"{where}/condition"),
            check_kind=check_kind,
            check_ref=check_ref,
        ))

    # `C-12` / `INV-2`: staleness that only a human can notice is staleness
    # that is never noticed. At least one condition must fire on its own.
    if not any(c.is_automatic for c in conditions):
        raise ClaimError(path, "at least one condition must be automatic (C-12)")
    return tuple(conditions)


def _parse_uncertainty(raw: Any) -> Uncertainty:
    path = "EvidenceClaim/uncertainty"
    if not isinstance(raw, Mapping):
        raise ClaimError(path, "expected an object")
    _require(raw, ("kind",), path)
    kind = _text(raw["kind"], f"{path}/kind")
    if kind not in UNCERTAINTY_KINDS:
        raise ClaimError(f"{path}/kind", f"expected one of {UNCERTAINTY_KINDS}")
    lower, upper = raw.get("lower"), raw.get("upper")
    if kind == "interval":
        if lower is None or upper is None:
            raise ClaimError(path, "an interval needs both lower and upper bounds")
        if not isinstance(lower, (int, float)) or not isinstance(upper, (int, float)):
            raise ClaimError(path, "interval bounds must be numbers")
        if lower > upper:
            raise ClaimError(path, "interval lower bound exceeds its upper bound")
    n = raw.get("n")
    if n is not None and (not isinstance(n, int) or n < 0):
        raise ClaimError(f"{path}/n", "expected a non-negative integer")
    return Uncertainty(kind=kind, lower=lower, upper=upper, n=n, note=raw.get("note"))


def _parse_validity(raw: Any) -> Validity:
    path = "EvidenceClaim/validity"
    if not isinstance(raw, Mapping):
        raise ClaimError(path, "expected an object")
    _require(raw, ("domains",), path)
    domains = raw["domains"]
    if not isinstance(domains, list) or not domains:
        raise ClaimError(f"{path}/domains", "expected a non-empty array")
    return Validity(
        domains=tuple(_text(d, f"{path}/domains") for d in domains),
        note=raw.get("note"),
    )


def _parse_evaluator(raw: Any) -> Evaluator:
    path = "EvidenceClaim/evaluator"
    if not isinstance(raw, Mapping):
        raise ClaimError(path, "expected an object")
    _require(raw, ("evaluatorId", "class", "imageDigest"), path)
    evaluator_class = _text(raw["class"], f"{path}/class")
    if evaluator_class not in EVALUATOR_CLASSES:
        raise ClaimError(f"{path}/class", f"expected one of {EVALUATOR_CLASSES}")
    return Evaluator(
        evaluator_id=_text(raw["evaluatorId"], f"{path}/evaluatorId"),
        evaluator_class=evaluator_class,
        image_digest=_digest(raw["imageDigest"], f"{path}/imageDigest"),
    )


def parse_claim(
    value: Any,
    *,
    support_count: int = 0,
    last_corroborated_at: str | None = None,
    protection_class: str = "none",
) -> Claim:
    """Parse a `VG-04 §10.2` claim. Fails closed, at parse, with a path."""

    path = "EvidenceClaim"
    if not isinstance(value, Mapping):
        raise ClaimError(path, "expected an object")
    _require(value, (
        "id", "subject", "predicate", "value", "protocol", "evaluator",
        "environmentProfile", "substrateProfile", "taskDistribution",
        "uncertainty", "validity", "invalidationConditions",
    ), path)
    if protection_class not in PROTECTION_CLASSES:
        raise ClaimError(f"{path}/protectionClass", f"expected one of {PROTECTION_CLASSES}")

    return Claim(
        id=_text(value["id"], f"{path}/id"),
        subject=_text(value["subject"], f"{path}/subject"),
        predicate=_text(value["predicate"], f"{path}/predicate"),
        value=value["value"],
        protocol=_digest(value["protocol"], f"{path}/protocol"),
        evaluator=_parse_evaluator(value["evaluator"]),
        environment_profile=_digest(value["environmentProfile"], f"{path}/environmentProfile"),
        substrate_profile=_digest(value["substrateProfile"], f"{path}/substrateProfile"),
        task_distribution=_digest(value["taskDistribution"], f"{path}/taskDistribution"),
        uncertainty=_parse_uncertainty(value["uncertainty"]),
        validity=_parse_validity(value["validity"]),
        invalidation_conditions=_parse_conditions(value["invalidationConditions"]),
        evidence_refs=tuple(value.get("evidenceRefs", ()) or ()),
        derived_from=tuple(value.get("derivedFrom", ()) or ()),
        contradicts=tuple(value.get("contradicts", ()) or ()),
        expires_at=value.get("expiresAt"),
        support_count=support_count,
        last_corroborated_at=last_corroborated_at,
        protection_class=protection_class,
    )
