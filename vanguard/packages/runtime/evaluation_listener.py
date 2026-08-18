"""Ledger-triggered Evaluation Listener daemon (D-02, VG-05 §2.1, ADR-0061).

Listens for `EpisodeCompleted` events on the event ledger L and emits `EvaluationRequested`
to trigger the out-of-process Exterior Evaluator (UID 10002) asynchronously, completely
decoupling evaluation from the synchronous episode loop.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Optional, Sequence

from ..domain.ledger.events import EventEnvelope
from ..ports.evaluator import EvaluationProtocol, EvaluatorPort, RunRef, Verdict
from ..ports.event_store import EventRange, EventStorePort, Result


@dataclass(frozen=True, slots=True)
class EvaluationRequestPayload:
    """Canonical payload for EvaluationRequested event."""

    run_id: str
    episode_id: str
    protocol: str
    environment_snapshot: Optional[str] = None
    target_criteria: Optional[Mapping[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "kind": "EvaluationRequested",
            "runId": self.run_id,
            "episodeId": self.episode_id,
            "protocol": self.protocol,
        }
        if self.environment_snapshot:
            data["environmentSnapshot"] = self.environment_snapshot
        if self.target_criteria:
            data["targetCriteria"] = dict(self.target_criteria)
        return data


class EvaluationListener:
    """Subscribes to ledger events and triggers exterior evaluation upon episode completion."""

    def __init__(
        self,
        event_store: EventStorePort,
        evaluator: Optional[EvaluatorPort] = None,
        *,
        default_protocol: str = "oracle_green",
        on_verdict_callback: Optional[Callable[[Verdict], None]] = None,
    ) -> None:
        self._store = event_store
        self._evaluator = evaluator
        self._default_protocol = default_protocol
        self._callback = on_verdict_callback
        self._processed_event_ids: set[str] = set()

    def process_envelope(self, envelope: EventEnvelope) -> Optional[EventEnvelope]:
        """Process a single ledger event envelope. If EpisodeCompleted, emits EvaluationRequested."""
        if envelope.event_id in self._processed_event_ids:
            return None

        self._processed_event_ids.add(envelope.event_id)
        payload = envelope.payload
        kind = payload.get("kind")

        if kind != "EpisodeCompleted":
            return None

        # Build EvaluationRequested envelope
        run_id = envelope.run_id or ""
        episode_id = envelope.episode_id or ""
        protocol_name = payload.get("evaluationProtocol", self._default_protocol)

        req_payload = EvaluationRequestPayload(
            run_id=run_id,
            episode_id=episode_id,
            protocol=protocol_name,
            environment_snapshot=envelope.environment_snapshot,
        )

        now_ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        # UUIDv7 format for eventId
        new_event_id = f"{uuid.uuid4().hex[:8]}-{uuid.uuid4().hex[8:12]}-7{uuid.uuid4().hex[13:16]}-8{uuid.uuid4().hex[17:20]}-{uuid.uuid4().hex[20:32]}"

        eval_envelope = EventEnvelope(
            schema_version="4.0.0",
            event_id=new_event_id,
            scope="episode",
            seq=str(int(envelope.seq) + 1),
            occurred_at=now_ts,
            recorded_at=now_ts,
            principal="system:evaluator-listener",
            principal_role="evaluator",
            tenant_id=envelope.tenant_id,
            owner_id=envelope.owner_id,
            confidentiality="internal",
            retention_class="standard",
            trainability="prohibited",
            redaction_status="none",
            run_id=run_id,
            episode_id=episode_id,
            parent_event_id=envelope.event_id,
            trace_id=envelope.trace_id or "trace-eval-001",
            span_id="span-eval-req",
            payload=req_payload.to_dict(),
        )

        # Append to event store
        self._store.append([eval_envelope])

        # If evaluator port is present, execute evaluation asynchronously/delegated
        if self._evaluator is not None and run_id:
            proto = EvaluationProtocol(
                name=protocol_name,
                parameters={"timeout_seconds": 30.0},
            )
            res = self._evaluator.evaluate(RunRef(run_id=run_id, episode_id=episode_id), proto)
            if res.ok and res.value is not None and self._callback is not None:
                self._callback(res.value)

        return eval_envelope

    def process_all_new(self) -> Sequence[EventEnvelope]:
        """Scan event store and process any unhandled EpisodeCompleted events."""
        res = self._store.read(EventRange())
        if not res.ok or res.value is None:
            return []

        emitted: list[EventEnvelope] = []
        for env in res.value:
            out = self.process_envelope(env)
            if out is not None:
                emitted.append(out)

        return emitted
