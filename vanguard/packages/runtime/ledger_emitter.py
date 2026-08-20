"""Canonical ledger writer (ADR-0076 §6). Grown from `LedgerBridge`.

All production envelope construction and appends flow through `LedgerEmitter`.
Callers hold role-scoped facades; there is no generic `append(any event)`.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Mapping

from ..domain.canonicalisation.digest import digest_of
from ..domain.ledger.events import EventEnvelope
from ..kernel.model import Event
from ..ports.event_store import EventRange, EventStorePort
from .determinism import SystemClock, SystemRandom, event_id

__all__ = [
    "LedgerBridge",
    "LedgerEmitter",
    "RoleScopedEmitter",
    "WriterAuthorityError",
    "WRITER_ROLES",
    "PRIVILEGED_KIND_OWNERS",
]

LINEAGE_FIELDS = (
    "project_id",
    "principal_id",
    "parent_principal_id",
    "parent_episode_id",
    "harness_digest",
)

# SPEC §1.2 / ADR-0074 writer authority. Orchestrator is not an owner of any
# privileged kind.
PRIVILEGED_KIND_OWNERS: Mapping[str, frozenset[str]] = {
    "CapabilityGranted": frozenset({"kernel"}),
    "CapabilityAttenuated": frozenset({"kernel"}),
    "CapabilityRevoked": frozenset({"kernel"}),
    "BudgetReserved": frozenset({"kernel"}),
    "BudgetCommitted": frozenset({"kernel"}),
    "BudgetReleased": frozenset({"kernel"}),
    "BudgetExhausted": frozenset({"kernel"}),
    "EffectStarted": frozenset({"kernel"}),
    "EffectCompleted": frozenset({"kernel"}),
    "EffectFailed": frozenset({"kernel"}),
    "EffectRejected": frozenset({"kernel"}),
    "EffectReconciled": frozenset({"kernel", "recovery"}),
    "AuthorizationRequested": frozenset({"kernel"}),
    "AuthorizationDenied": frozenset({"kernel"}),
    "KernelAlarm": frozenset({"kernel"}),
    "VerdictRecorded": frozenset({"evaluator_gateway"}),
    "PluginResolved": frozenset({"registry"}),
    "PluginActivated": frozenset({"registry"}),
    "PluginQuiesced": frozenset({"registry"}),
    "PluginRetired": frozenset({"registry"}),
    "PluginFaulted": frozenset({"registry"}),
    "ApprovalResolved": frozenset({"approval"}),
}

WRITER_ROLES = frozenset({
    "kernel",
    "scheduler",
    "registry",
    "evaluator_gateway",
    "approval",
    "recovery",
    "orchestrator",
    "session",  # kernel ∪ scheduler: the HarnessSession composition object
})

_SESSION_ROLES = frozenset({"kernel", "scheduler", "session"})


class WriterAuthorityError(PermissionError):
    """A role-scoped facade refused a kind it does not own."""


class LedgerEmitter:
    """`Ledger` + `EventSink` for the kernel, one `EventStorePort` underneath.

    Envelope construction is `mhf.event/1` with lineage and a `prev_digest`
    chain per `project_id`. `append_intent` durably persists or raises;
    `emit` never raises (`K-06` / `F-25`).
    """

    def __init__(
        self,
        store: EventStorePort,
        *,
        episode_id: str,
        project_id: str,
        principal_id: str,
        harness_digest: str,
        clock: Any | None = None,
        random: Any | None = None,
        parent_principal_id: str | None = None,
        parent_episode_id: str | None = None,
        role: str = "session",
        anchor: EventEnvelope | None = None,
    ) -> None:
        if not project_id:
            # 1.2-C: config-declared, never workspace-derived (see
            # `TaskContext.project_id`). No default here -- an emitter that
            # invented one would silently start a second chain.
            raise ValueError("project_id is required (config-declared; 1.2-C)")
        if not harness_digest:
            raise ValueError("harness_digest is required on every emitted envelope")
        if role not in WRITER_ROLES:
            raise ValueError(f"unknown writer role {role!r}")
        self._clock = clock or SystemClock()
        self._random = random or SystemRandom()
        self.store = store
        self.events: list[Event] = []
        self._episode_id = episode_id
        self._project_id = project_id
        self._principal_id = principal_id
        self._parent_principal_id = parent_principal_id
        self._parent_episode_id = parent_episode_id
        self._harness_digest = harness_digest
        self._role = role
        if anchor is not None:
            self._seq = int(anchor.seq) + 1
            if anchor.schema_version == "mhf.event/1":
                self._prev = anchor.content_digest or anchor.digest()
            else:
                self._prev = None
        else:
            self._seq, self._prev = self._load_chain(project_id)

    def kernel(self) -> RoleScopedEmitter:
        return RoleScopedEmitter(self, "kernel")

    def scheduler(self) -> RoleScopedEmitter:
        return RoleScopedEmitter(self, "scheduler")

    def registry(self) -> RoleScopedEmitter:
        return RoleScopedEmitter(self, "registry")

    def evaluator_gateway(self) -> RoleScopedEmitter:
        return RoleScopedEmitter(self, "evaluator_gateway")

    def approval(self) -> RoleScopedEmitter:
        return RoleScopedEmitter(self, "approval")

    def recovery(self) -> RoleScopedEmitter:
        return RoleScopedEmitter(self, "recovery")

    def orchestrator(self) -> RoleScopedEmitter:
        return RoleScopedEmitter(self, "orchestrator")

    def append_intent(self, event: Event) -> None:
        self._remember(event)
        self._write(event, role="intent", writer=self._role, swallow=False)

    def emit(self, event: Event) -> EventEnvelope | None:
        self._remember(event)
        try:
            return self._write(event, role="emitted", writer=self._role, swallow=False)
        except WriterAuthorityError:
            raise
        except Exception:
            return None

    def emit_kind(
        self,
        kind: str,
        *,
        run_id: str,
        principal: str,
        payload: Mapping[str, Any] | None = None,
        episode_id: str | None = None,
        occurred_at: str | None = None,
        alertable: bool = False,
        causation_id: str | None = None,
        correlation_id: str | None = None,
        idempotency_key: str | None = None,
        writer: str | None = None,
    ) -> EventEnvelope:
        body = dict(payload or {})
        body.setdefault("kind", kind)
        event = Event(
            kind=kind,
            reason=str(body.get("reason") or kind),
            at=occurred_at or self._clock.now(),
            run_id=run_id,
            principal=principal,
            payload=body,
            alertable=alertable,
        )
        return self._write(
            event,
            role="emitted",
            writer=writer or self._role,
            swallow=False,
            episode_id=episode_id,
            causation_id=causation_id,
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
        )

    def _remember(self, event: Event) -> None:
        if self.events and self.events[-1] is event:
            return
        self.events.append(event)

    def _assert_writer(self, writer: str, kind: str) -> None:
        owners = PRIVILEGED_KIND_OWNERS.get(kind)
        if owners is None:
            if writer == "orchestrator":
                return
            return
        effective = _SESSION_ROLES if writer == "session" else frozenset({writer})
        if owners.isdisjoint(effective):
            raise WriterAuthorityError(
                f"role {writer!r} cannot append privileged kind {kind!r}"
            )

    def _load_chain(self, project_id: str) -> tuple[int, str | None]:
        read = self.store.read(EventRange(project_id=project_id))
        envelopes = list(read.value) if read.ok and read.value else []
        if not envelopes:
            return 0, None
        last = envelopes[-1]
        try:
            seq = int(last.seq)
        except (TypeError, ValueError):
            seq = 0
        prev = None
        if last.schema_version == "mhf.event/1":
            prev = last.content_digest or last.digest()
        return seq + 1, prev

    def _write(
        self,
        event: Event,
        *,
        role: str,
        writer: str,
        swallow: bool,
        episode_id: str | None = None,
        causation_id: str | None = None,
        correlation_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> EventEnvelope:
        self._assert_writer(writer, event.kind)
        seq = self._seq
        prev = self._prev
        ident = event_id(clock=self._clock, random=self._random)
        payload = {"kind": event.kind, "reason": event.reason,
                   "alertable": bool(event.alertable), **dict(event.payload)}
        envelope = EventEnvelope(
            schema_version="mhf.event/1",
            event_id=ident,
            scope="episode",
            seq=str(seq),
            occurred_at=event.at,
            recorded_at=event.at,
            principal=event.principal,
            principal_role="episode",
            tenant_id="tenant-default",
            owner_id="owner-platform",
            confidentiality="internal",
            retention_class="extended",
            trainability="prohibited",
            redaction_status="none",
            payload=payload,
            run_id=event.run_id,
            episode_id=episode_id or self._episode_id,
            trace_id=correlation_id or event.run_id or self._episode_id,
            span_id=f"{role}-{seq}",
            project_id=self._project_id,
            principal_id=self._principal_id,
            parent_principal_id=self._parent_principal_id,
            parent_episode_id=self._parent_episode_id,
            harness_digest=self._harness_digest,
            prev_digest=prev,
            causation_id=causation_id,
            correlation_id=correlation_id or event.run_id,
            idempotency_key=idempotency_key,
            alertable=bool(event.alertable),
            mhf_kind=event.kind,
            mhf_branch_id="main",
        )
        unsigned = envelope.to_mhf_dict(include_digest=False)
        digest = digest_of(unsigned)
        envelope = replace(envelope, content_digest=digest)
        result = self.store.append([envelope])
        if not result.ok:
            raise OSError(result.error.message if result.error else "append rejected")
        self._seq = seq + 1
        self._prev = digest
        return envelope


class RoleScopedEmitter:
    """Facade that can only originate kinds its role owns."""

    def __init__(self, inner: LedgerEmitter, role: str) -> None:
        self._inner = inner
        self._role = role

    @property
    def store(self) -> EventStorePort:
        return self._inner.store

    @property
    def events(self) -> list[Event]:
        return self._inner.events

    def append_intent(self, event: Event) -> None:
        self._inner._remember(event)
        self._inner._write(event, role="intent", writer=self._role, swallow=False)

    def emit(self, event: Event) -> EventEnvelope | None:
        self._inner._remember(event)
        try:
            return self._inner._write(
                event, role="emitted", writer=self._role, swallow=False)
        except WriterAuthorityError:
            raise
        except Exception:
            return None

    def emit_kind(self, kind: str, **kwargs: Any) -> EventEnvelope:
        return self._inner.emit_kind(kind, writer=self._role, **kwargs)


# Backward-compatible name for existing `root.py` / test imports.
LedgerBridge = LedgerEmitter
