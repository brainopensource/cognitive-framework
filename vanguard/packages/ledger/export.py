"""Line-delimited JSON export and import with redaction support.

Owning contract: VG-04 §12.3 / `CT-42`, GTS-13C T3.5.

Invariants:
- Line-delimited JSON is export, replay and interchange format (CT-42).
- Redaction preserves envelope metadata, correlation IDs (traceId, spanId,
  parentEventId, runId, episodeId), seq, timestamps, and principal/tenancy.
- Redacted payloads mask sensitive fields while preserving payload kind and digests.
- Unknown fields preserved during import/export.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Iterable, Optional, Sequence, TextIO

from ..domain.canonicalisation.digest import digest_of
from ..domain.ledger.events import EventEnvelope, parse_event_envelope

__all__ = [
    "RedactionPolicy",
    "redact_envelope",
    "export_jsonl",
    "import_jsonl",
]


@dataclass(frozen=True, slots=True)
class RedactionPolicy:
    """Rules defining which events or payload fields to redact during export."""

    redact_confidential: bool = True
    redact_restricted: bool = True
    mask_custom_keys: frozenset[str] = field(
        default_factory=lambda: frozenset({"secret", "token", "password", "apiKey", "privateKey"})
    )


def redact_envelope(envelope: EventEnvelope, policy: Optional[RedactionPolicy] = None) -> EventEnvelope:
    """Apply redaction to an envelope while strictly preserving correlation IDs and metadata."""
    pol = policy or RedactionPolicy()
    should_redact_all = (
        (envelope.confidentiality == "restricted" and pol.redact_restricted)
        or (envelope.confidentiality == "confidential" and pol.redact_confidential)
        or (envelope.redaction_status in ("partial", "complete"))
    )

    orig_payload = dict(envelope.payload)
    kind = orig_payload.get("kind", "")

    if should_redact_all:
        redacted_payload: dict[str, Any] = {
            "kind": kind,
            "[redacted]": True,
            "originalPayloadDigest": digest_of(orig_payload),
        }
        # Keep references if present
        for ref_key in ("descriptorDigest", "receiptDigest", "resultDigest", "contentDigest", "grantId", "leaseId"):
            if ref_key in orig_payload:
                redacted_payload[ref_key] = orig_payload[ref_key]

        return EventEnvelope(
            schema_version=envelope.schema_version,
            event_id=envelope.event_id,
            scope=envelope.scope,
            run_id=envelope.run_id,
            episode_id=envelope.episode_id,
            branch_id=envelope.branch_id,
            parent_event_id=envelope.parent_event_id,
            trace_id=envelope.trace_id,
            span_id=envelope.span_id,
            seq=envelope.seq,
            occurred_at=envelope.occurred_at,
            recorded_at=envelope.recorded_at,
            principal=envelope.principal,
            tenant_id=envelope.tenant_id,
            owner_id=envelope.owner_id,
            confidentiality=envelope.confidentiality,
            retention_class=envelope.retention_class,
            trainability="prohibited" if should_redact_all else envelope.trainability,
            redaction_status="complete",
            encryption_key_ref=envelope.encryption_key_ref,
            environment_snapshot=envelope.environment_snapshot,
            payload=redacted_payload,
            unknown_fields=envelope.unknown_fields,
        )

    # Selective key masking
    masked_payload: dict[str, Any] = {}
    any_masked = False
    for k, v in orig_payload.items():
        if k in pol.mask_custom_keys:
            masked_payload[k] = "[REDACTED]"
            any_masked = True
        else:
            masked_payload[k] = v

    return EventEnvelope(
        schema_version=envelope.schema_version,
        event_id=envelope.event_id,
        scope=envelope.scope,
        run_id=envelope.run_id,
        episode_id=envelope.episode_id,
        branch_id=envelope.branch_id,
        parent_event_id=envelope.parent_event_id,
        trace_id=envelope.trace_id,
        span_id=envelope.span_id,
        seq=envelope.seq,
        occurred_at=envelope.occurred_at,
        recorded_at=envelope.recorded_at,
        principal=envelope.principal,
        tenant_id=envelope.tenant_id,
        owner_id=envelope.owner_id,
        confidentiality=envelope.confidentiality,
        retention_class=envelope.retention_class,
        trainability=envelope.trainability,
        redaction_status="partial" if any_masked else envelope.redaction_status,
        encryption_key_ref=envelope.encryption_key_ref,
        environment_snapshot=envelope.environment_snapshot,
        payload=masked_payload,
        unknown_fields=envelope.unknown_fields,
    )


def export_jsonl(
    events: Iterable[EventEnvelope],
    writer: TextIO,
    redact: bool = False,
    policy: Optional[RedactionPolicy] = None,
) -> int:
    """Export an iterable of EventEnvelopes to line-delimited JSON (JSONL).
    
    Returns:
        Number of events exported.
    """
    count = 0
    pol = policy or RedactionPolicy()
    for event in events:
        target = redact_envelope(event, pol) if redact else event
        line = json.dumps(target.to_dict(), separators=(",", ":"), ensure_ascii=False)
        writer.write(line + "\n")
        count += 1
    return count


def import_jsonl(reader: TextIO) -> list[EventEnvelope]:
    """Import a stream of line-delimited JSON into validated EventEnvelope instances."""
    envelopes: list[EventEnvelope] = []
    for line_num, line in enumerate(reader, 1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            raw = json.loads(stripped)
            envelope = parse_event_envelope(raw)
            envelopes.append(envelope)
        except Exception as exc:
            raise ValueError(f"JSONL import error on line {line_num}: {exc}") from exc
    return envelopes
