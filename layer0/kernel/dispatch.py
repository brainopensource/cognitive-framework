"""The dispatch sequence (S0–S12). There is no second path."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from layer0.events.canonical import CanonicalisationError
from layer0.spi.types_gen import EffectContext, EffectRequest, EventKind, SinkClass
from .attenuation import Scope
from .budget import BudgetDenied, Governor, Lease
from .classifier import SinkRegistry
from .grants import Grant, GrantIssuer, MissingDescriptorBinding, descriptor_of
from .model import (
    ALERTABLE,
    AdapterOutcome,
    Event,
    FailurePath,
    Occurrence,
)
from .policy import Decision, Outcome
from .ports import Clock, EffectAdapter, EventSink, Ledger

__all__ = ["DispatchResult", "Kernel", "KernelAlarm", "SuspensionToken"]


@dataclass(frozen=True, slots=True)
class SuspensionToken:
    token_id: str
    descriptor_digest: str
    principal: str
    expires_at: str


@dataclass(frozen=True, slots=True)
class DispatchResult:
    failure: FailurePath
    descriptor_digest: str | None = None
    outcome: AdapterOutcome | None = None
    events: tuple[Event, ...] = field(default_factory=tuple)
    detail: str = ""
    suspension: SuspensionToken | None = None
    settlement: Mapping[str, int] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.failure is FailurePath.OK


class KernelAlarm(RuntimeError):
    """F-21a / F-24. Must page, not log (ADR-M0-09)."""


class Kernel:
    def __init__(
        self,
        *,
        adapters: Mapping[str, EffectAdapter],
        policy: Any,
        classifier: Any,
        governor: Governor,
        issuer: GrantIssuer,
        clock: Clock,
        ledger: Ledger,
        events: EventSink,
        sinks: SinkRegistry | None = None,
    ) -> None:
        self._adapters = dict(adapters)
        self._policy = policy
        self._classifier = classifier
        self._governor = governor
        self._issuer = issuer
        self._clock = clock
        self._ledger = ledger
        self._events = events
        self._sinks = sinks or SinkRegistry()

    def dispatch(
        self,
        request: EffectRequest,
        ctx: EffectContext,
        *,
        requested_scope: Scope,
        spans: Sequence[Any] | None = None,
        cross_process: bool = False,
        purpose_digest: str = "sha256:" + "0" * 64,
    ) -> DispatchResult:
        emitted: list[Event] = []

        problem = _validate(request, ctx)
        if problem is not None:
            return self._reject(request, ctx, FailurePath.SCHEMA, problem, emitted)

        adapter = self._adapters.get(request.verb)
        if adapter is None:
            return self._reject(request, ctx, FailurePath.UNKNOWN_ACTION,
                                f"no adapter for {request.verb!r}", emitted)
        try:
            healthy = adapter.healthy()
        except Exception as exc:
            healthy = False
            _ = exc
        if not healthy:
            return self._reject(request, ctx, FailurePath.ADAPTER_UNAVAILABLE,
                                f"adapter {request.verb!r} unhealthy", emitted)

        try:
            descriptor = descriptor_of(request.verb, dict(request.args))
        except (CanonicalisationError, TypeError, ValueError) as exc:
            return self._reject(request, ctx, FailurePath.DESCRIPTOR, str(exc), emitted)

        try:
            widens = bool(self._classifier.widens_capability(
                request, principal=ctx.principal, depth=ctx.depth))
        except Exception as exc:
            self._emit(emitted, ctx, EventKind.EFFECT_REJECTED.value, "classifier_error",
                       {"error": str(exc), "widensCapability": True})
            return DispatchResult(FailurePath.CLASSIFIER_ERROR, descriptor,
                                  events=tuple(emitted), detail=str(exc))

        self._emit(emitted, ctx, EventKind.AUTHORIZATION_REQUESTED.value, "authorize",
                   {"verb": request.verb, "descriptorDigest": descriptor})

        decision: Decision = self._policy.authorize(
            request, widens_capability=widens,
            requested_scope=requested_scope, spans=spans)
        if decision.attenuated and decision.granted_scope is not None:
            self._emit(emitted, ctx, EventKind.CAPABILITY_ATTENUATED.value, "sealed",
                       {"actions": sorted(decision.granted_scope.actions)})
        if decision.outcome is Outcome.REQUIRE_APPROVAL:
            token = SuspensionToken(
                token_id=f"approval-{descriptor[-12:]}",
                descriptor_digest=descriptor,
                principal=ctx.principal,
                expires_at=self._clock.now(),
            )
            self._emit(emitted, ctx, EventKind.APPROVAL_REQUESTED.value, "approval_required",
                       {"descriptorDigest": descriptor})
            return DispatchResult(FailurePath.APPROVAL_SUSPENDED, descriptor,
                                  events=tuple(emitted), suspension=token,
                                  detail=decision.reason)
        if decision.outcome is Outcome.REJECT:
            failure = decision.failure or FailurePath.DENIED_REJECT
            self._emit(emitted, ctx, EventKind.AUTHORIZATION_DENIED.value, failure.name.lower(),
                       {"requested": decision.requested, "grantable": decision.grantable,
                        "untrustedSpans": list(decision.untrusted_span_ids),
                        "descriptorDigest": descriptor},
                       alertable=failure in ALERTABLE or decision.alertable)
            return DispatchResult(failure, descriptor, events=tuple(emitted),
                                  detail=decision.reason)

        granted_scope = decision.granted_scope or requested_scope

        grant: Grant | None = None
        requires_grant = self._sinks.requires_grant(request.verb)
        if requires_grant:
            try:
                grant = self._issuer.issue(
                    grant_id=self._issuer.next_grant_id(),
                    principal=ctx.principal,
                    descriptor_digest=descriptor,
                    scope=granted_scope,
                    expires_at=granted_scope.constraints.expires_at,
                    purpose_digest=purpose_digest,
                    single_use=ctx.idempotency_key is None,
                    cross_process=cross_process,
                )
            except (MissingDescriptorBinding, ValueError) as exc:
                return self._reject(request, ctx, FailurePath.GRANT_ISSUE, str(exc), emitted)

        try:
            lease = self._governor.reserve(ctx.run_id, request.reservation, ctx.parent_lease)
        except BudgetDenied as exc:
            if exc.reason == "parent_closed":
                failure = FailurePath.PARENT_LEASE_CLOSED
                kind = EventKind.BUDGET_RELEASED.value
            else:
                failure = FailurePath.BUDGET_DENIED
                kind = EventKind.BUDGET_EXHAUSTED.value
            self._emit(emitted, ctx, kind, exc.reason,
                       {"dimension": exc.dimension, "requested": exc.requested,
                        "remaining": exc.remaining})
            return DispatchResult(failure, descriptor, events=tuple(emitted), detail=str(exc))

        return self._guarded(request, ctx, adapter, descriptor, grant, lease, emitted,
                             cross_process=cross_process)

    def resolve_approval(self, ctx: EffectContext, *, approved: bool, token_id: str) -> Event:
        """Ledgered ApprovalResolved (D-13). Re-entry is at S1, never at S6."""
        kind = EventKind.APPROVAL_RESOLVED.value
        event = Event(
            kind=kind, reason="approved" if approved else "denied",
            at=self._clock.now(), run_id=ctx.run_id, principal=ctx.principal,
            payload={"tokenId": token_id, "approved": approved},
        )
        self._publish(event)
        return event

    def revoke(self, ctx: EffectContext, grant_id: str) -> tuple[Event, ...]:
        revoked = self._issuer.revoke(grant_id)
        events = []
        for ident in revoked:
            event = Event(
                kind=EventKind.CAPABILITY_REVOKED.value, reason="revoked",
                at=self._clock.now(), run_id=ctx.run_id, principal=ctx.principal,
                payload={"grantId": ident},
            )
            self._publish(event)
            events.append(event)
        return tuple(events)

    def _guarded(
        self,
        request: EffectRequest,
        ctx: EffectContext,
        adapter: EffectAdapter,
        descriptor: str,
        grant: Grant | None,
        lease: Lease,
        emitted: list[Event],
        *,
        cross_process: bool,
    ) -> DispatchResult:
        failure = FailurePath.OK
        outcome: AdapterOutcome | None = None
        detail = ""
        settlement: Mapping[str, int] = {}
        intent: Event | None = None
        try:
            if grant is not None:
                verification = self._issuer.verify(
                    grant, descriptor_digest=descriptor,
                    now=self._clock.now(), cross_process=cross_process)
                if not verification.ok:
                    failure = verification.failure or FailurePath.GRANT_MISMATCH
                    detail = verification.detail
                else:
                    self._issuer.consume(grant)

            if failure is FailurePath.OK:
                intent = Event(
                    kind=EventKind.EFFECT_STARTED.value, reason="intent", at=self._clock.now(),
                    run_id=ctx.run_id, principal=ctx.principal,
                    payload={"descriptorDigest": descriptor,
                             "grantId": grant.grant_id if grant else None,
                             "idempotencyKey": ctx.idempotency_key,
                             "sinkClass": request.sink.value})
                try:
                    self._ledger.append_intent(intent)
                except Exception as exc:
                    failure = FailurePath.INTENT_APPEND_FAILED
                    detail = str(exc)
                    intent = None

            if failure is FailurePath.OK:
                try:
                    raw = adapter.execute(request, ctx)
                    outcome = raw if isinstance(raw, AdapterOutcome) else AdapterOutcome("ok")
                except Exception as exc:
                    detail = str(exc)
                    outcome = AdapterOutcome("error", Occurrence.UNDETERMINABLE, detail=detail)
                    failure = FailurePath.UNDETERMINABLE
                else:
                    failure = _failure_for(outcome)
                    detail = outcome.detail or ""

                try:
                    settlement = self._governor.commit(lease, dict(outcome.actual_cost))
                except Exception as exc:
                    failure = FailurePath.COMMIT_FAILED
                    detail = str(exc)
        finally:
            try:
                self._governor.release(lease)
            except Exception as exc:
                self._emit(emitted, ctx, EventKind.KERNEL_ALARM.value, "lease_leak",
                           {"leaseId": lease.lease_id, "error": str(exc)}, alertable=True)
                raise KernelAlarm(f"lease {lease.lease_id} leaked: {exc}") from exc

        if intent is not None:
            emitted.append(intent)
            self._publish(intent)
        return self._finish(
            request, ctx, emitted, failure, descriptor, outcome, detail, settlement,
            grant=grant, lease=lease,
        )

    def _finish(
        self,
        request: EffectRequest,
        ctx: EffectContext,
        emitted: list[Event],
        failure: FailurePath,
        descriptor: str,
        outcome: AdapterOutcome | None,
        detail: str,
        settlement: Mapping[str, int],
        *,
        grant: Grant | None = None,
        lease: Lease | None = None,
    ) -> DispatchResult:
        if failure is FailurePath.OK and grant is not None:
            self._emit(emitted, ctx, EventKind.CAPABILITY_GRANTED.value, "issued",
                       dict(grant.payload()))
        if failure is FailurePath.OK and lease is not None:
            self._emit(emitted, ctx, EventKind.BUDGET_RESERVED.value, "reserved",
                       {"leaseId": lease.lease_id, "reserved": dict(lease.reserved)})
            self._emit(emitted, ctx, EventKind.BUDGET_COMMITTED.value, "committed",
                       {"leaseId": lease.lease_id, "settlement": dict(settlement)})
        if failure is FailurePath.INTENT_APPEND_FAILED:
            self._emit(emitted, ctx, EventKind.KERNEL_ALARM.value, "intent_append_failed",
                       {"descriptorDigest": descriptor, "detail": detail}, alertable=True)
        elif failure in _GRANT_FAILURES:
            self._emit(emitted, ctx, EventKind.EFFECT_REJECTED.value, failure.name.lower(),
                       {"descriptorDigest": descriptor, "detail": detail},
                       alertable=failure in ALERTABLE)
        elif failure is FailurePath.UNDETERMINABLE:
            self._emit(emitted, ctx, EventKind.EFFECT_RECONCILED.value, "unknown",
                       {"descriptorDigest": descriptor, "detail": detail,
                        "occurrence": Occurrence.UNDETERMINABLE.value})
        elif failure is FailurePath.OK:
            self._emit(emitted, ctx, EventKind.EFFECT_COMPLETED.value, "ok",
                       {"descriptorDigest": descriptor,
                        "resultDigest": outcome.result_digest if outcome else None,
                        "settlement": dict(settlement), "detail": detail})
        else:
            self._emit(emitted, ctx, EventKind.EFFECT_FAILED.value, failure.name.lower(),
                       {"descriptorDigest": descriptor, "detail": detail})
        _ = request
        return DispatchResult(failure, descriptor, outcome, tuple(emitted), detail,
                              settlement=settlement)

    def _reject(self, request: EffectRequest, ctx: EffectContext, failure: FailurePath,
                detail: str, emitted: list[Event]) -> DispatchResult:
        _ = request
        self._emit(emitted, ctx, EventKind.EFFECT_REJECTED.value, failure.name.lower(),
                   {"detail": detail}, alertable=failure in ALERTABLE)
        return DispatchResult(failure, None, events=tuple(emitted), detail=detail)

    def _emit(self, emitted: list[Event], ctx: EffectContext, kind: str,
              reason: str, payload: Mapping[str, Any], *, alertable: bool = False) -> None:
        event = Event(kind=kind, reason=reason, at=self._clock.now(),
                      run_id=ctx.run_id, principal=ctx.principal,
                      payload=dict(payload), alertable=alertable)
        emitted.append(event)
        self._publish(event)

    def _publish(self, event: Event) -> None:
        try:
            self._events.emit(event)
        except Exception:
            pass


_GRANT_FAILURES = frozenset({
    FailurePath.GRANT_MISMATCH,
    FailurePath.GRANT_EXPIRED,
    FailurePath.GRANT_REPLAY,
    FailurePath.GRANT_FORGED,
})


def _failure_for(outcome: AdapterOutcome) -> FailurePath:
    if outcome.occurrence is Occurrence.UNDETERMINABLE:
        return FailurePath.UNDETERMINABLE
    return {
        "ok": FailurePath.OK,
        "error": FailurePath.ADAPTER_ERROR,
        "timeout": FailurePath.TIMEOUT,
        "cancelled": FailurePath.CANCELLED,
        "perimeter": FailurePath.PERIMETER_UNAVAILABLE,
    }.get(outcome.status, FailurePath.ADAPTER_ERROR)


def _validate(request: EffectRequest, ctx: EffectContext) -> str | None:
    if not isinstance(request, EffectRequest):
        return "not an EffectRequest"
    if not request.verb or not isinstance(request.verb, str):
        return "verb is required"
    if not ctx.principal:
        return "principal is required (CT-16)"
    if not ctx.run_id:
        return "runId is required"
    if not isinstance(request.args, Mapping):
        return "args must be an object"
    if not isinstance(request.selector, Mapping):
        return "selector must be a selector object"
    if ctx.depth < 0:
        return "depth must be non-negative"
    if request.sink not in tuple(SinkClass):
        return f"unknown sink class {request.sink!r}"
    return None
