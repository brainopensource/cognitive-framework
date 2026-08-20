"""Ledger-triggered Evaluation Listener daemon (D-02, VG-05 §1.2).

Listens for `EpisodeCompleted` and appends `EvaluationRequested` through the
canonical `LedgerEmitter` (ADR-0076 §6). No invented seq or pseudo-UUIDv7.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping, Optional, Sequence

from ..domain.ledger.events import EventEnvelope
from ..ports.evaluator import EvaluationProtocol, EvaluatorPort, RunRef, Verdict
from ..ports.event_store import EventRange, EventStorePort
from .ledger_emitter import LedgerEmitter


class EvaluationRequestPayload:
    """Canonical payload for EvaluationRequested event."""

    def __init__(
        self,
        run_id: str,
        episode_id: str,
        protocol: str,
        environment_snapshot: Optional[str] = None,
        target_criteria: Optional[Mapping[str, Any]] = None,
    ) -> None:
        self.run_id = run_id
        self.episode_id = episode_id
        self.protocol = protocol
        self.environment_snapshot = environment_snapshot
        self.target_criteria = target_criteria

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
        emitter: Optional[LedgerEmitter] = None,
    ) -> None:
        self._store = event_store
        self._evaluator = evaluator
        self._default_protocol = default_protocol
        self._callback = on_verdict_callback
        self._emitter = emitter
        self._processed_event_ids: set[str] = set()

    def process_envelope(self, envelope: EventEnvelope) -> Optional[EventEnvelope]:
        if envelope.event_id in self._processed_event_ids:
            return None

        self._processed_event_ids.add(envelope.event_id)
        payload = envelope.payload
        kind = payload.get("kind") or envelope.mhf_kind

        if kind != "EpisodeCompleted":
            return None

        run_id = envelope.run_id or ""
        episode_id = envelope.episode_id or ""
        protocol_name = payload.get("evaluationProtocol", self._default_protocol)
        req_payload = EvaluationRequestPayload(
            run_id=run_id,
            episode_id=episode_id,
            protocol=protocol_name,
            environment_snapshot=envelope.environment_snapshot,
        )

        emitter = self._emitter or LedgerEmitter(
            self._store,
            episode_id=episode_id or "episode-eval",
            project_id=envelope.project_id or "project-default",
            principal_id=envelope.principal_id or envelope.principal,
            harness_digest=envelope.harness_digest or "sha256:" + ("0" * 64),
            parent_principal_id=envelope.parent_principal_id,
            parent_episode_id=envelope.parent_episode_id,
            role="scheduler",
        )
        eval_envelope = emitter.scheduler().emit_kind(
            "EvaluationRequested",
            run_id=run_id,
            principal="system:evaluator-listener",
            payload=req_payload.to_dict(),
            episode_id=episode_id,
            causation_id=envelope.event_id,
            correlation_id=envelope.trace_id or run_id,
        )

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
        res = self._store.read(EventRange())
        if not res.ok or res.value is None:
            return []

        emitted: list[EventEnvelope] = []
        for env in res.value:
            out = self.process_envelope(env)
            if out is not None:
                emitted.append(out)
        return emitted
