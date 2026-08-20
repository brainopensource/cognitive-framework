"""Domain ledger events and wire envelope parser.

Owning contract: VG-04 §12 / `CT-14`..`CT-16`, `CT-40`..`CT-50`;
`schemas/v4/event-envelope.schema.json`; `REQ-SCHEMA-007`.

Invariants:
- `EventEnvelope` parses all VG-04 wire fields.
- `scope` conditionally enforces `runId` and `episodeId` (04 §12.1).
- Past-tense verb phrases for all event kinds (04 §0.5).
- Unknown event payloads preserved for forward compatibility (CT-44).
- Zero I/O, zero clocks, zero randomness.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

from ..canonicalisation.digest import digest_of
from ..canonicalisation.jcs import canonicalise
from ..primitives.primitives import (
    ParseError,
    int_string_from_int,
    int_string_to_int,
    parse,
    parse_digest,
    parse_episode_id,
    parse_principal_id,
    parse_timestamp,
)

__all__ = [
    "EventEnvelope",
    "EVENT_KINDS",
    "VALID_SCOPES",
    "VALID_CONFIDENTIALITIES",
    "VALID_RETENTIONS",
    "VALID_TRAINABILITIES",
    "VALID_REDACTION_STATUSES",
    "VALID_PRINCIPAL_ROLES",
    "parse_event_envelope",
]

VALID_SCOPES = frozenset({"episode", "governance", "evolution", "recovery"})
VALID_CONFIDENTIALITIES = frozenset({"public", "internal", "confidential", "restricted"})
VALID_RETENTIONS = frozenset({"ephemeral", "standard", "extended", "legal_hold"})
VALID_TRAINABILITIES = frozenset({"prohibited", "opt_in_required", "opt_in_granted"})
VALID_REDACTION_STATUSES = frozenset({"none", "partial", "complete", "pending"})
VALID_PRINCIPAL_ROLES = frozenset({"user", "operator", "episode", "process", "evaluator", "release"})

# VG-04 §12.2 Minimum Event Set
EVENT_KINDS = frozenset({
    # Episode lifecycle
    "EpisodeStarted",
    "EpisodeStateChanged",
    "EpisodeCompleted",
    # Observation and cognition
    "ObservationRequested",
    "ObservationProduced",
    "OperatorSelected",
    "OperatorInvoked",
    "ProposalProduced",
    # Authorisation
    "AuthorizationRequested",
    "CapabilityGranted",
    "AuthorizationDenied",
    "CapabilityRevoked",
    # Budget
    "BudgetReserved",
    "BudgetCommitted",
    "BudgetReleased",
    # Effects
    "EffectPreviewed",
    "EffectStarted",
    "EffectCompleted",
    "EffectRejected",
    "EffectReconciled",
    "ConflictDetected",
    "KernelAlarm",
    # Evidence
    "EvaluationRequested",
    "EvidenceClaimProduced",
    # Competence
    "ArtifactCreated",
    "ActivationChanged",
    "CompetencePriorRecorded",
    # Human
    "ApprovalRequested",
    "ApprovalResolved",
    "CorrectionRecorded",
    # Liveness and recovery
    "Heartbeat",
    "RunRecovered",
    "RunAborted",
    # Evolution
    "CandidateBuilt",
    "CandidateAttested",
    "CanaryPromoted",
    "RollbackTriggered",
})

_UUIDV7_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


@dataclass(frozen=True, slots=True)
class EventEnvelope:
    """Normative EventEnvelope according to VG-04 §12.1."""

    schema_version: str
    event_id: str
    scope: str
    seq: str
    occurred_at: str
    recorded_at: str
    principal: str
    principal_role: str
    tenant_id: str
    owner_id: str
    confidentiality: str
    retention_class: str
    trainability: str
    redaction_status: str
    payload: Mapping[str, Any]
    run_id: Optional[str] = None
    episode_id: Optional[str] = None
    branch_id: Optional[int] = None
    parent_event_id: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    encryption_key_ref: Optional[str] = None
    environment_snapshot: Optional[str] = None
    project_id: Optional[str] = None
    principal_id: Optional[str] = None
    parent_principal_id: Optional[str] = None
    parent_episode_id: Optional[str] = None
    harness_digest: Optional[str] = None
    prev_digest: Optional[str] = None
    content_digest: Optional[str] = None
    causation_id: Optional[str] = None
    correlation_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    alertable: bool = False
    mhf_kind: Optional[str] = None
    mhf_branch_id: Optional[str] = None
    unknown_fields: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to canonical wire dictionary (camelCase)."""
        data: dict[str, Any] = {
            "schemaVersion": self.schema_version,
            "eventId": self.event_id,
            "scope": self.scope,
            "seq": self.seq,
            "occurredAt": self.occurred_at,
            "recordedAt": self.recorded_at,
            "principal": self.principal,
            "principalRole": self.principal_role,
            "tenantId": self.tenant_id,
            "ownerId": self.owner_id,
            "confidentiality": self.confidentiality,
            "retentionClass": self.retention_class,
            "trainability": self.trainability,
            "redactionStatus": self.redaction_status,
            "payload": dict(self.payload),
        }
        if self.run_id is not None:
            data["runId"] = self.run_id
        if self.episode_id is not None:
            data["episodeId"] = self.episode_id
        if self.branch_id is not None:
            data["branchId"] = self.branch_id
        if self.parent_event_id is not None:
            data["parentEventId"] = self.parent_event_id
        if self.trace_id is not None:
            data["traceId"] = self.trace_id
        if self.span_id is not None:
            data["spanId"] = self.span_id
        if self.encryption_key_ref is not None:
            data["encryptionKeyRef"] = self.encryption_key_ref
        if self.environment_snapshot is not None:
            data["environmentSnapshot"] = self.environment_snapshot
        if self.unknown_fields:
            for k, v in self.unknown_fields.items():
                if k not in data:
                    data[k] = v
        return data

    def canonical_json(self) -> str:
        """Serialize envelope to RFC 8785 canonical JSON text."""
        return canonicalise(self.to_dict())

    def digest(self) -> str:
        """Compute sha256 digest of canonical representation."""
        if self.schema_version == "mhf.event/1":
            if self.content_digest:
                return self.content_digest
            return digest_of(self.to_mhf_dict(include_digest=False))
        return digest_of(self.to_dict())

    def to_mhf_dict(self, *, include_digest: bool = True) -> dict[str, Any]:
        """`mhf.event/1` wire object (snake_case). Lineage keys are always present."""
        kind = self.mhf_kind or self.payload.get("kind") or "Heartbeat"
        payload = dict(self.payload)
        unsigned: dict[str, Any] = {
            "schema_version": "mhf.event/1",
            "event_id": self.event_id,
            "kind": kind,
            "seq": int(self.seq),
            "occurred_at": self.occurred_at,
            "run_id": self.run_id or "",
            "principal": self.principal,
            "payload": payload,
            "episode_id": self.episode_id,
            "parent_episode_id": self.parent_episode_id,
            "project_id": self.project_id,
            "principal_id": self.principal_id,
            "parent_principal_id": self.parent_principal_id,
            "harness_digest": self.harness_digest,
            "branch_id": self.mhf_branch_id or "main",
            "prev_digest": self.prev_digest,
            "causation_id": self.causation_id,
            "correlation_id": self.correlation_id or self.trace_id,
            "idempotency_key": self.idempotency_key,
            "alertable": bool(self.alertable),
        }
        if include_digest:
            unsigned["digest"] = self.content_digest or digest_of(
                {k: v for k, v in unsigned.items()}
            )
        return unsigned

    def wire_dict(self) -> dict[str, Any]:
        """Store/write shape: mhf.event/1 from the Wave-1 writer, else v4 camelCase."""
        if self.schema_version == "mhf.event/1":
            return self.to_mhf_dict()
        return self.to_dict()


def parse_event_envelope(raw: Mapping[str, Any]) -> EventEnvelope:
    """Parse v4 camelCase or `mhf.event/1` snake_case (ADR-0076 read-path dual)."""
    if not isinstance(raw, Mapping):
        raise ParseError("EventEnvelope", "type", f"expected mapping, got {type(raw).__name__}")

    schema_version = raw.get("schema_version") or raw.get("schemaVersion")
    if schema_version == "mhf.event/1" and "event_id" in raw:
        return _parse_mhf_event_envelope(raw)
    if schema_version != "vg.4":
        raise ParseError("EventEnvelope", "schemaVersion", f"must be 'vg.4', got {schema_version!r}")

    # eventId (UUIDv7)
    event_id = raw.get("eventId")
    if not isinstance(event_id, str) or not _UUIDV7_RE.match(event_id):
        raise ParseError("EventEnvelope", "eventId", f"eventId must be a UUIDv7, got {event_id!r}")

    # scope
    scope = raw.get("scope")
    if scope not in VALID_SCOPES:
        raise ParseError("EventEnvelope", "scope", f"invalid scope {scope!r}; must be one of {sorted(VALID_SCOPES)}")

    # seq (IntString)
    seq = raw.get("seq")
    if not isinstance(seq, str):
        raise ParseError("EventEnvelope", "seq", f"seq must be an IntString, got {type(seq).__name__}")
    parse("IntString", seq)

    # timestamps
    occurred_at = raw.get("occurredAt")
    if not isinstance(occurred_at, str):
        raise ParseError("EventEnvelope", "occurredAt", "missing or non-string occurredAt")
    parse_timestamp(occurred_at)

    recorded_at = raw.get("recordedAt")
    if not isinstance(recorded_at, str):
        raise ParseError("EventEnvelope", "recordedAt", "missing or non-string recordedAt")
    parse_timestamp(recorded_at)

    # identities
    principal = raw.get("principal")
    if not isinstance(principal, str) or not principal:
        raise ParseError("EventEnvelope", "principal", "missing or empty principal")
    parse_principal_id(principal)

    principal_role = raw.get("principalRole")
    if principal_role not in VALID_PRINCIPAL_ROLES:
        raise ParseError("EventEnvelope", "principalRole", f"invalid principalRole {principal_role!r}")

    tenant_id = raw.get("tenantId")
    if not isinstance(tenant_id, str) or not tenant_id:
        raise ParseError("EventEnvelope", "tenantId", "missing or empty tenantId")

    owner_id = raw.get("ownerId")
    if not isinstance(owner_id, str) or not owner_id:
        raise ParseError("EventEnvelope", "ownerId", "missing or empty ownerId")

    # classification & data policy
    confidentiality = raw.get("confidentiality")
    if confidentiality not in VALID_CONFIDENTIALITIES:
        raise ParseError("EventEnvelope", "confidentiality", f"invalid confidentiality {confidentiality!r}")

    retention_class = raw.get("retentionClass")
    if retention_class not in VALID_RETENTIONS:
        raise ParseError("EventEnvelope", "retentionClass", f"invalid retentionClass {retention_class!r}")

    trainability = raw.get("trainability")
    if trainability not in VALID_TRAINABILITIES:
        raise ParseError("EventEnvelope", "trainability", f"invalid trainability {trainability!r}")

    redaction_status = raw.get("redactionStatus")
    if redaction_status not in VALID_REDACTION_STATUSES:
        raise ParseError("EventEnvelope", "redactionStatus", f"invalid redactionStatus {redaction_status!r}")

    # payload
    payload = raw.get("payload")
    if not isinstance(payload, Mapping):
        raise ParseError("EventEnvelope", "payload", "payload must be a mapping")
    kind = payload.get("kind")
    if not isinstance(kind, str) or not kind:
        raise ParseError("EventEnvelope", "payload.kind", "payload must carry a non-empty string kind")

    # scope conditional checks (04 §12.1)
    run_id = raw.get("runId")
    if scope in ("episode", "recovery"):
        if not isinstance(run_id, str) or not run_id:
            raise ParseError("EventEnvelope", "runId", f"scope {scope!r} requires non-empty runId")

    episode_id = raw.get("episodeId")
    if scope == "episode":
        if not isinstance(episode_id, str) or not episode_id:
            raise ParseError("EventEnvelope", "episodeId", "scope 'episode' requires non-empty episodeId")
        parse_episode_id(episode_id)
    elif episode_id is not None:
        raise ParseError("EventEnvelope", "episodeId", f"scope {scope!r} cannot carry episodeId")
    if scope in ("governance", "evolution") and run_id is not None:
        raise ParseError("EventEnvelope", "runId", f"scope {scope!r} cannot carry runId")

    # optionals
    branch_id = raw.get("branchId")
    if branch_id is not None and not isinstance(branch_id, int):
        raise ParseError("EventEnvelope", "branchId", "branchId must be an integer")

    parent_event_id = raw.get("parentEventId")
    if parent_event_id is not None:
        if not isinstance(parent_event_id, str) or not _UUIDV7_RE.match(parent_event_id):
            raise ParseError("EventEnvelope", "parentEventId", "parentEventId must be UUIDv7")

    trace_id = raw.get("traceId")
    if not isinstance(trace_id, str) or not trace_id:
        raise ParseError("EventEnvelope", "traceId", "traceId must be a non-empty string")

    span_id = raw.get("spanId")
    if not isinstance(span_id, str) or not span_id:
        raise ParseError("EventEnvelope", "spanId", "spanId must be a non-empty string")

    encryption_key_ref = raw.get("encryptionKeyRef")
    if encryption_key_ref is not None and not isinstance(encryption_key_ref, str):
        raise ParseError("EventEnvelope", "encryptionKeyRef", "encryptionKeyRef must be string")

    environment_snapshot = raw.get("environmentSnapshot")
    if environment_snapshot is not None:
        if not isinstance(environment_snapshot, str):
            raise ParseError("EventEnvelope", "environmentSnapshot", "environmentSnapshot must be string")
        parse_digest(environment_snapshot)

    known_keys = {
        "schemaVersion", "eventId", "scope", "runId", "episodeId", "branchId",
        "parentEventId", "traceId", "spanId", "seq", "occurredAt", "recordedAt",
        "principal", "principalRole", "tenantId", "ownerId", "confidentiality", "retentionClass",
        "trainability", "redactionStatus", "encryptionKeyRef", "environmentSnapshot",
        "payload",
    }
    unknown_fields = {k: v for k, v in raw.items() if k not in known_keys}

    return EventEnvelope(
        schema_version=schema_version,
        event_id=event_id,
        scope=scope,
        run_id=run_id,
        episode_id=episode_id,
        branch_id=branch_id,
        parent_event_id=parent_event_id,
        trace_id=trace_id,
        span_id=span_id,
        seq=seq,
        occurred_at=occurred_at,
        recorded_at=recorded_at,
        principal=principal,
        principal_role=principal_role,
        tenant_id=tenant_id,
        owner_id=owner_id,
        confidentiality=confidentiality,
        retention_class=retention_class,
        trainability=trainability,
        redaction_status=redaction_status,
        encryption_key_ref=encryption_key_ref,
        environment_snapshot=environment_snapshot,
        payload=payload,
        unknown_fields=unknown_fields,
    )


def _parse_mhf_event_envelope(raw: Mapping[str, Any]) -> EventEnvelope:
    """Read-path adapter: `mhf.event/1` → the v4 dataclass plus lineage fields."""
    event_id = raw.get("event_id")
    if not isinstance(event_id, str) or not event_id:
        raise ParseError("EventEnvelope", "event_id", "mhf.event/1 requires event_id")
    kind = raw.get("kind")
    if not isinstance(kind, str) or not kind:
        raise ParseError("EventEnvelope", "kind", "mhf.event/1 requires kind")
    seq = raw.get("seq")
    if isinstance(seq, int):
        seq_str = str(seq)
    elif isinstance(seq, str):
        seq_str = seq
    else:
        raise ParseError("EventEnvelope", "seq", "mhf.event/1 seq must be an integer")
    occurred_at = raw.get("occurred_at")
    if not isinstance(occurred_at, str) or not occurred_at:
        raise ParseError("EventEnvelope", "occurred_at", "missing occurred_at")
    run_id = raw.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        raise ParseError("EventEnvelope", "run_id", "mhf.event/1 requires run_id")
    principal = raw.get("principal")
    if not isinstance(principal, str) or not principal:
        raise ParseError("EventEnvelope", "principal", "missing principal")
    payload = raw.get("payload")
    if not isinstance(payload, Mapping):
        raise ParseError("EventEnvelope", "payload", "payload must be a mapping")
    payload_dict = dict(payload)
    if "kind" not in payload_dict:
        payload_dict["kind"] = kind
    digest = raw.get("digest")
    if digest is not None and not isinstance(digest, str):
        raise ParseError("EventEnvelope", "digest", "digest must be a string")
    correlation = raw.get("correlation_id")
    return EventEnvelope(
        schema_version="mhf.event/1",
        event_id=event_id,
        scope="episode",
        seq=seq_str,
        occurred_at=occurred_at,
        recorded_at=occurred_at,
        principal=principal,
        principal_role="episode",
        tenant_id="tenant-default",
        owner_id="owner-platform",
        confidentiality="internal",
        retention_class="extended",
        trainability="prohibited",
        redaction_status="none",
        payload=payload_dict,
        run_id=run_id,
        episode_id=raw.get("episode_id") if isinstance(raw.get("episode_id"), str) else None,
        trace_id=correlation if isinstance(correlation, str) and correlation else run_id,
        span_id=event_id,
        project_id=raw.get("project_id") if isinstance(raw.get("project_id"), str) else None,
        principal_id=raw.get("principal_id") if isinstance(raw.get("principal_id"), str) else None,
        parent_principal_id=(
            raw.get("parent_principal_id")
            if isinstance(raw.get("parent_principal_id"), str) else None
        ),
        parent_episode_id=(
            raw.get("parent_episode_id")
            if isinstance(raw.get("parent_episode_id"), str) else None
        ),
        harness_digest=raw.get("harness_digest") if isinstance(raw.get("harness_digest"), str) else None,
        prev_digest=raw.get("prev_digest") if isinstance(raw.get("prev_digest"), str) else None,
        content_digest=digest if isinstance(digest, str) else None,
        causation_id=raw.get("causation_id") if isinstance(raw.get("causation_id"), str) else None,
        correlation_id=correlation if isinstance(correlation, str) else None,
        idempotency_key=(
            raw.get("idempotency_key") if isinstance(raw.get("idempotency_key"), str) else None
        ),
        alertable=bool(raw.get("alertable", False)),
        mhf_kind=kind,
        mhf_branch_id=raw.get("branch_id") if isinstance(raw.get("branch_id"), str) else "main",
    )
