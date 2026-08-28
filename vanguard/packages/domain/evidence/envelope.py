"""`aether.evidence/1` -- the receipt an acceptance gate may actually read.

`ADR-0101` draws a line this module enforces: causal facts, content-addressed
artifacts, derived projections, telemetry and attestations are *separate
evidence classes, and none substitutes for another*. A passing test suite is
not a receipt. A green CI page is not a receipt. Prose in a board is not a
receipt. What closes a gate is a signed envelope binding a claim to the exact
tree, dependencies, environment, run and artifacts that produced it -- so a
reviewer can recompute rather than believe.

The rules that are not expressible in a schema:

* **Unknown is never a pass.** `outcome` admits `undeterminable`, and a
  negative or undeterminable result is a legitimate envelope. What is refused
  is silence dressed as success (`ADR-0101 §4`).
* **The producer cannot accept its own work.** Independent acceptance is a
  *separate* envelope whose `producer.identity` differs from this one's. That
  is checked here, in `accepts`, rather than trusted.
* **Canonical bytes determine the digest**, and the signature covers exactly
  those bytes minus the signature value itself. Anything else lets a field be
  edited after signing.

This is an evidence protocol over the existing ledger and artifact substrate.
It is deliberately *not* a second ledger: it stores no history, and every
`materials` entry is a reference into a store that already holds the bytes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from ..canonicalisation.digest import digest_of
from ..canonicalisation.jcs import canonical_bytes

__all__ = [
    "EVIDENCE_SCHEMA",
    "OUTCOMES",
    "acceptance_defects",
    "EvidenceEnvelope",
    "EvidenceEnvelopeError",
    "Material",
    "Producer",
    "accepts",
    "envelope_digest",
    "parse_envelope",
    "signable_bytes",
]

EVIDENCE_SCHEMA = "aether.evidence/1"

#: `ADR-0101 §4`. `undeterminable` is a first-class outcome, not a failure to
#: report one: invalid instrumentation cannot close a gate, but it must still
#: be recordable, or the only way to describe a broken experiment is silence.
OUTCOMES = ("passed", "failed", "undeterminable")


class EvidenceEnvelopeError(ValueError):
    """An envelope that cannot be admitted. Raised at build or parse."""


@dataclass(frozen=True, slots=True)
class Material:
    """One digest-addressed input or output the claim depends on.

    `digest` is the identity; `ref` says where the bytes live. A material
    without a digest is a filename, and a filename is not evidence.
    """

    name: str
    digest: str
    ref: str = ""
    media_type: str = ""

    def __post_init__(self) -> None:
        if not self.name:
            raise EvidenceEnvelopeError("a material requires a name")
        if not self.digest or ":" not in self.digest:
            raise EvidenceEnvelopeError(
                f"material {self.name!r} requires an algorithm-prefixed digest")

    def to_wire(self) -> dict[str, Any]:
        wire: dict[str, Any] = {"name": self.name, "digest": self.digest}
        if self.ref:
            wire["ref"] = self.ref
        if self.media_type:
            wire["mediaType"] = self.media_type
        return wire


@dataclass(frozen=True, slots=True)
class Producer:
    """Who produced this envelope, and under which key."""

    identity: str
    key_id: str = ""
    role: str = "producer"

    def __post_init__(self) -> None:
        if not self.identity:
            raise EvidenceEnvelopeError("a producer requires an identity")

    def to_wire(self) -> dict[str, Any]:
        wire: dict[str, Any] = {"identity": self.identity, "role": self.role}
        if self.key_id:
            wire["keyId"] = self.key_id
        return wire


@dataclass(frozen=True, slots=True)
class EvidenceEnvelope:
    """One signed claim about one subject, bound to everything that made it."""

    claim: str
    protocol: str
    subjects: tuple[str, ...]
    materials: tuple[Material, ...]
    run: Mapping[str, Any]
    pins: Mapping[str, Any]
    environment: Mapping[str, Any]
    outcome: str
    producer: Producer
    artifact_refs: tuple[str, ...] = ()
    detail: str = ""
    signature: str = ""

    def __post_init__(self) -> None:
        if not self.claim:
            raise EvidenceEnvelopeError("an envelope requires a claim identity")
        if not self.protocol:
            raise EvidenceEnvelopeError(
                "an envelope requires a protocol identity; a claim whose "
                "method is unstated cannot be re-run")
        if self.outcome not in OUTCOMES:
            raise EvidenceEnvelopeError(
                f"unknown outcome {self.outcome!r}; the set is exactly {OUTCOMES}")
        if not self.subjects:
            raise EvidenceEnvelopeError("an envelope requires at least one subject")
        for required in ("commit", "tree"):
            if not self.pins.get(required):
                raise EvidenceEnvelopeError(
                    f"pins must bind {required!r}; without it the claim floats "
                    "free of the code that produced it")

    # -- wire ------------------------------------------------------------

    def body(self) -> dict[str, Any]:
        """Everything the signature covers. The signature itself is absent."""
        return {
            "schema": EVIDENCE_SCHEMA,
            "claim": self.claim,
            "protocol": self.protocol,
            "subject": list(self.subjects),
            "materials": [m.to_wire() for m in self.materials],
            "run": dict(sorted(self.run.items())),
            "pins": dict(sorted(self.pins.items())),
            "environment": dict(sorted(self.environment.items())),
            "outcome": self.outcome,
            "artifactRefs": list(self.artifact_refs),
            "producer": self.producer.to_wire(),
            **({"detail": self.detail} if self.detail else {}),
        }

    def to_wire(self) -> dict[str, Any]:
        wire = self.body()
        wire["digest"] = self.digest()
        if self.signature:
            wire["signature"] = self.signature
        return wire

    def digest(self) -> str:
        return digest_of(self.body())

    def signable_bytes(self) -> bytes:
        return canonical_bytes(self.body())


def envelope_digest(envelope: EvidenceEnvelope) -> str:
    return envelope.digest()


def signable_bytes(envelope: EvidenceEnvelope) -> bytes:
    """Canonical bytes a producer signs. Excludes only the signature value."""
    return envelope.signable_bytes()


def parse_envelope(wire: Mapping[str, Any]) -> EvidenceEnvelope:
    """Read an envelope back, verifying its own digest.

    A wire digest that does not match the recomputed one is a hard failure:
    it means a field moved after the digest was taken, which is precisely the
    manipulation content-addressing exists to detect.
    """
    if wire.get("schema") != EVIDENCE_SCHEMA:
        raise EvidenceEnvelopeError(
            f"expected {EVIDENCE_SCHEMA}, got {wire.get('schema')!r}")
    producer_wire = wire.get("producer") or {}
    envelope = EvidenceEnvelope(
        claim=str(wire.get("claim") or ""),
        protocol=str(wire.get("protocol") or ""),
        subjects=tuple(wire.get("subject") or ()),
        materials=tuple(
            Material(
                name=str(m.get("name") or ""),
                digest=str(m.get("digest") or ""),
                ref=str(m.get("ref") or ""),
                media_type=str(m.get("mediaType") or ""),
            )
            for m in (wire.get("materials") or ())
        ),
        run=dict(wire.get("run") or {}),
        pins=dict(wire.get("pins") or {}),
        environment=dict(wire.get("environment") or {}),
        outcome=str(wire.get("outcome") or ""),
        producer=Producer(
            identity=str(producer_wire.get("identity") or ""),
            key_id=str(producer_wire.get("keyId") or ""),
            role=str(producer_wire.get("role") or "producer"),
        ),
        artifact_refs=tuple(wire.get("artifactRefs") or ()),
        detail=str(wire.get("detail") or ""),
        signature=str(wire.get("signature") or ""),
    )
    declared = wire.get("digest")
    if declared and declared != envelope.digest():
        raise EvidenceEnvelopeError(
            "envelope digest does not match its canonical bytes")
    return envelope


def accepts(
    acceptance: EvidenceEnvelope, produced: EvidenceEnvelope,
) -> bool:
    """Whether `acceptance` is a valid independent acceptance of `produced`.

    Independence is checked, not assumed. A reviewer who is also the producer
    has reviewed nothing, and an acceptance whose subject digest has drifted
    is accepting a different artifact than the one on the table.
    """
    return not acceptance_defects(acceptance, produced)


def acceptance_defects(
    acceptance: EvidenceEnvelope, produced: EvidenceEnvelope,
) -> list[str]:
    """Every reason `acceptance` fails to accept `produced`, named individually.

    A single boolean cannot tell a reviewer who signed their own work from one
    who accepted a bundle nobody can reproduce, and those call for different
    repairs.
    """
    defects: list[str] = []
    if acceptance.producer.identity == produced.producer.identity:
        defects.append(
            f"reviewer identity {acceptance.producer.identity!r} is the producer's; "
            f"a producer cannot accept their own evidence"
        )
    if acceptance.producer.key_id and (
        acceptance.producer.key_id == produced.producer.key_id
    ):
        defects.append(
            f"reviewer signs with the producer's key {acceptance.producer.key_id!r}; "
            f"separate identities sharing one key are not separate authorities"
        )
    if acceptance.outcome != "passed":
        defects.append(f"acceptance outcome is {acceptance.outcome!r}, not 'passed'")
    if produced.digest() not in acceptance.subjects:
        defects.append(
            "acceptance subject does not include the produced bundle's digest; "
            "it accepts a different artifact than the one on the table"
        )
    # An acceptance reports a review of a result; it does not replace the
    # result. Accepting `passed` over a subject whose own outcome is
    # `undeterminable` or `failed` would let a signature convert unknown into
    # true, which is the one thing ADR-0101's three-valued outcome exists to
    # prevent. Reviewing an unreproducible bundle honestly yields
    # `undeterminable`, and `undeterminable` never satisfies a predicate.
    if produced.outcome != "passed":
        defects.append(
            f"subject bundle's own outcome is {produced.outcome!r}; an acceptance "
            f"may not report an outcome its subject does not support"
        )
    return defects
