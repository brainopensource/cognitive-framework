"""The dispatch sequence (`05 §2`). There is no second path.

```
 S0  ENTER      EffectRequest
 S1  PARSE      validate against the contract schema
 S2  RESOLVE    action -> adapter                    <-- BEFORE any lease
 S3  DESCRIBE   descriptor = digest(canonical(name, normalisedArgs))
 S4  CLASSIFY   widensCapability := classifier(request)   <-- not a constant
 S5  AUTHORIZE  decision := policy.authorize(...)
 S6  GRANT      grant := issue(descriptor, principal, resources, ttl)
 S7  RESERVE    lease := governor.reserve(runId, resources, parentLease)
 +-- try --------------------------------------------------------------+
 | S8  VERIFY   the grant binds THIS descriptor and is unexpired        |
 | S8a INTENT   durably append EffectStarted and FSYNC  <-- BEFORE      |
 | S9  DISPATCH adapter.execute(...)                                    |
 | S10 COMMIT   governor.commit(lease, actual)                          |
 +-- finally ----------------------------------------------------------+
 S11 RELEASE    governor.release(lease)              <-- every path
 S12 EMIT       outcome events                       <-- after release
```

Every ordering rule below is a defect that actually shipped:

* `K-04` — S2 precedes S7, so an unknown action cannot strand a lease.
* `K-05` — S8 is inside the guarded block, after S7: the grant is verified at
  the point of effect, so a resumed run or a mutated request cannot ride an
  earlier grant.
* `K-06` — S11 precedes S12. If the emit raises, the lease is already back; a
  leaked lease is worse than a lost event.
* `K-07` — S10 debits reality, overruns included.
* `K-08` — S4 is a classifier call, per request.
* `K-47` — S8a is durable **before** S9, so a crash between dispatch and emit
  leaves the effect *undeterminable* rather than invisible.

`05 §2.3` enumerates every exit. `FailurePath` is that table, and
`DispatchResult.failure` always names one — an exit not in the table is a
defect (`AT-09`), which `test/kernel/test_dispatch.py` asserts directly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from ..domain.canonicalisation.jcs import CanonicalisationError
from .attenuation import Scope
from .budget import BudgetDenied, Governor, Lease, Reservation
from .classifier import SinkRegistry
from .grants import Grant, GrantIssuer, MissingDescriptorBinding, descriptor_of
from .model import (
    ALERTABLE,
    AdapterOutcome,
    EffectRequest,
    Event,
    FailurePath,
    Occurrence,
    SinkClass,
)
from .policy import Decision, Outcome
from ..ports.kernel import Clock, EffectAdapter, EventSink, Ledger

__all__ = ["DispatchResult", "Kernel", "SuspensionToken"]


@dataclass(frozen=True, slots=True)
class SuspensionToken:
    """`K-15`: the token binds the descriptor, so an approval cannot be
    transplanted onto a different call. `K-16`: expiry resolves as denied."""

    token_id: str
    descriptor_digest: str
    principal: str
    expires_at: str


@dataclass(frozen=True, slots=True)
class DispatchResult:
    """The single return type of the single path."""

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
    """`F-24`. A release failure is unrecoverable and must page, not log."""


class Kernel:
    """The only path from a proposal to an effect (`ICD §3`, `AT-01`)."""

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
        self._grant_counter = 0

    # ------------------------------------------------------------------
    # The sequence
    # ------------------------------------------------------------------

    def dispatch(
        self,
        request: EffectRequest,
        *,
        requested_scope: Scope,
        reservation: Reservation,
        spans: Sequence[Any] | None = None,
        cross_process: bool = False,
        purpose_digest: str = "sha256:" + "0" * 64,
    ) -> DispatchResult:
        emitted: list[Event] = []

        # -- S1 PARSE ---------------------------------------------------
        problem = _validate(request)
        if problem is not None:
            return self._reject(request, FailurePath.SCHEMA, problem, emitted)

        # -- S2 RESOLVE (before any lease — `K-04`) ---------------------
        adapter = self._adapters.get(request.action)
        if adapter is None:
            return self._reject(request, FailurePath.UNKNOWN_ACTION,
                                f"no adapter for {request.action!r}", emitted)
        try:
            healthy = adapter.healthy()
        except Exception as exc:  # an adapter that raises on a health check is unhealthy
            healthy = False
            _ = exc
        if not healthy:
            return self._reject(request, FailurePath.ADAPTER_UNAVAILABLE,
                                f"adapter {request.action!r} unhealthy", emitted)

        # -- S3 DESCRIBE ------------------------------------------------
        try:
            descriptor = descriptor_of(request.action, request.args)
        except (CanonicalisationError, TypeError, ValueError) as exc:
            return self._reject(request, FailurePath.DESCRIPTOR, str(exc), emitted)

        # -- S4 CLASSIFY (a call, never a constant — `K-08`) ------------
        try:
            widens = bool(self._classifier.widens_capability(request))
        except Exception as exc:
            # `F-05`, fail closed: an exception in the classifier must not
            # disable the authority predicate. That is the single most
            # attractive target in the kernel.
            self._emit(emitted, request, "EffectRejected", "classifier_error",
                       {"error": str(exc), "widensCapability": True})
            return DispatchResult(FailurePath.CLASSIFIER_ERROR, descriptor,
                                  events=tuple(emitted), detail=str(exc))

        # -- S5 AUTHORIZE -----------------------------------------------
        decision: Decision = self._policy.authorize(
            request, widens_capability=widens,
            requested_scope=requested_scope, spans=spans)
        if decision.outcome is Outcome.REQUIRE_APPROVAL:
            token = SuspensionToken(
                token_id=f"approval-{descriptor[-12:]}",
                descriptor_digest=descriptor,
                principal=request.principal,
                expires_at=self._clock.now(),
            )
            # `K-13`: no lease is held across a suspension. `K-14`: re-entry
            # is at S1, never at S6.
            self._emit(emitted, request, "ApprovalRequested", "approval_required",
                       {"descriptorDigest": descriptor})
            return DispatchResult(FailurePath.APPROVAL_SUSPENDED, descriptor,
                                  events=tuple(emitted), suspension=token,
                                  detail=decision.reason)
        if decision.outcome is Outcome.REJECT:
            failure = decision.failure or FailurePath.DENIED_REJECT
            self._emit(emitted, request, "AuthorizationDenied", failure.name.lower(),
                       {"requested": decision.requested, "grantable": decision.grantable,
                        "untrustedSpans": list(decision.untrusted_span_ids),
                        "descriptorDigest": descriptor},
                       alertable=failure in ALERTABLE or decision.alertable)
            return DispatchResult(failure, descriptor, events=tuple(emitted),
                                  detail=decision.reason)

        granted_scope = decision.granted_scope or requested_scope

        # -- S6 GRANT ---------------------------------------------------
        grant: Grant | None = None
        requires_grant = self._sinks.requires_grant(request.action)
        if requires_grant:
            self._grant_counter += 1
            try:
                grant = self._issuer.issue(
                    grant_id=f"grant-{self._grant_counter}",
                    principal=request.principal,
                    descriptor_digest=descriptor,
                    scope=granted_scope,
                    expires_at=granted_scope.constraints.expires_at,
                    purpose_digest=purpose_digest,
                    single_use=request.idempotency_key is None,  # `K-19`
                    cross_process=cross_process,
                )
            except (MissingDescriptorBinding, ValueError) as exc:
                return self._reject(request, FailurePath.GRANT_ISSUE, str(exc), emitted)

        # -- S7 RESERVE -------------------------------------------------
        try:
            lease = self._governor.reserve(request.run_id, reservation, request.parent_lease)
        except BudgetDenied as exc:
            failure = (FailurePath.PARENT_LEASE_CLOSED if exc.reason == "parent_closed"
                       else FailurePath.BUDGET_DENIED)
            self._emit(emitted, request, "BudgetReleased", exc.reason,
                       {"dimension": exc.dimension, "requested": exc.requested,
                        "remaining": exc.remaining})
            return DispatchResult(failure, descriptor, events=tuple(emitted), detail=str(exc))

        return self._guarded(request, adapter, descriptor, grant, lease, emitted,
                             cross_process=cross_process)

    # ------------------------------------------------------------------
    # S8..S12 — the guarded block and the paths out of it
    # ------------------------------------------------------------------

    def _guarded(
        self,
        request: EffectRequest,
        adapter: EffectAdapter,
        descriptor: str,
        grant: Grant | None,
        lease: Lease,
        emitted: list[Event],
        *,
        cross_process: bool,
    ) -> DispatchResult:
        """S8..S10 inside the guard, S11 in `finally`, S12 only afterwards.

        Nothing in this block emits. `K-06` puts release strictly before emit,
        and a `return` inside `try` evaluates its expression *before* the
        `finally` runs — so emitting from here would silently reverse the two
        and reintroduce exactly the defect the rule exists to prevent. The
        block therefore records an outcome and lets `_finish` emit it.
        """
        failure = FailurePath.OK
        outcome: AdapterOutcome | None = None
        detail = ""
        settlement: Mapping[str, int] = {}
        intent: Event | None = None
        try:
            # -- S8 VERIFY, at the point of effect (`K-05`) -------------
            if grant is not None:
                verification = self._issuer.verify(
                    grant, descriptor_digest=descriptor,
                    now=self._clock.now(), cross_process=cross_process)
                if not verification.ok:
                    failure = verification.failure or FailurePath.GRANT_MISMATCH
                    detail = verification.detail
                else:
                    self._issuer.consume(grant)

            # -- S8a INTENT, durable before the effect begins (`K-47`) --
            if failure is FailurePath.OK:
                intent = Event(
                    kind="EffectStarted", reason="intent", at=self._clock.now(),
                    run_id=request.run_id, principal=request.principal,
                    payload={"descriptorDigest": descriptor,
                             "grantId": grant.grant_id if grant else None,
                             "idempotencyKey": request.idempotency_key,
                             "sinkClass": self._sinks.sink_class(request.action).value})
                try:
                    self._ledger.append_intent(intent)
                except Exception as exc:
                    # `F-21a`: the effect never starts.
                    failure = FailurePath.INTENT_APPEND_FAILED
                    detail = str(exc)
                    intent = None

            # -- S9 DISPATCH -------------------------------------------
            if failure is FailurePath.OK:
                try:
                    outcome = adapter.execute(request)
                except Exception as exc:
                    # An adapter that raises leaves occurrence unknown: it may
                    # have reached the external system before failing (`F-22`).
                    detail = str(exc)
                    outcome = AdapterOutcome("error", Occurrence.UNDETERMINABLE, detail=detail)
                    failure = FailurePath.UNDETERMINABLE
                else:
                    failure = _failure_for(outcome)
                    detail = outcome.detail or ""

                # -- S10 COMMIT — debits reality, overruns included ----
                try:
                    settlement = self._governor.commit(lease, dict(outcome.actual_cost))
                except Exception as exc:
                    failure = FailurePath.COMMIT_FAILED
                    detail = str(exc)
        finally:
            # -- S11 RELEASE — every path, always, before S12 (`K-06`) --
            try:
                self._governor.release(lease)
            except Exception as exc:  # `F-24`: leaked. This must page, not log.
                self._emit(emitted, request, "KernelAlarm", "lease_leak",
                           {"leaseId": lease.lease_id, "error": str(exc)}, alertable=True)
                raise KernelAlarm(f"lease {lease.lease_id} leaked: {exc}") from exc

        # -- S12 EMIT ---------------------------------------------------
        if intent is not None:
            emitted.append(intent)
            self._publish(intent)
        return self._finish(request, emitted, failure, descriptor, outcome, detail, settlement)

    def _finish(
        self,
        request: EffectRequest,
        emitted: list[Event],
        failure: FailurePath,
        descriptor: str,
        outcome: AdapterOutcome | None,
        detail: str,
        settlement: Mapping[str, int],
    ) -> DispatchResult:
        """S12 EMIT. The lease is already released on every path reaching here."""
        if failure is FailurePath.INTENT_APPEND_FAILED:
            self._emit(emitted, request, "KernelAlarm", "intent_append_failed",
                       {"descriptorDigest": descriptor, "detail": detail}, alertable=True)
        elif failure in _GRANT_FAILURES:
            self._emit(emitted, request, "EffectRejected", failure.name.lower(),
                       {"descriptorDigest": descriptor, "detail": detail},
                       alertable=failure in ALERTABLE)
        elif failure is FailurePath.UNDETERMINABLE:
            # `F-22`: uncertainty is preserved, never resolved to success or
            # failure. Resolving it would be manufacturing evidence.
            self._emit(emitted, request, "EffectReconciled", "unknown",
                       {"descriptorDigest": descriptor, "detail": detail,
                        "occurrence": Occurrence.UNDETERMINABLE.value})
        else:
            self._emit(emitted, request, "EffectCompleted",
                       "ok" if failure is FailurePath.OK else failure.name.lower(),
                       {"descriptorDigest": descriptor,
                        "resultDigest": outcome.result_digest if outcome else None,
                        "settlement": dict(settlement), "detail": detail})
        return DispatchResult(failure, descriptor, outcome, tuple(emitted), detail,
                              settlement=settlement)

    # ------------------------------------------------------------------

    def _reject(self, request: EffectRequest, failure: FailurePath, detail: str,
                emitted: list[Event]) -> DispatchResult:
        """A pre-lease exit: `F-01`..`F-04`, `F-11`. No lease was ever opened."""
        self._emit(emitted, request, "EffectRejected", failure.name.lower(),
                   {"detail": detail}, alertable=failure in ALERTABLE)
        return DispatchResult(failure, None, events=tuple(emitted), detail=detail)

    def _emit(self, emitted: list[Event], request: EffectRequest, kind: str,
              reason: str, payload: Mapping[str, Any], *, alertable: bool = False) -> None:
        event = Event(kind=kind, reason=reason, at=self._clock.now(),
                      run_id=request.run_id, principal=request.principal,
                      payload=dict(payload), alertable=alertable)
        emitted.append(event)
        self._publish(event)

    def _publish(self, event: Event) -> None:
        try:
            self._events.emit(event)
        except Exception:
            # `F-25`: log, do not fail the effect. The lease is already back
            # by the time anything is emitted (`K-06`).
            pass


_GRANT_FAILURES = frozenset({
    FailurePath.GRANT_MISMATCH,
    FailurePath.GRANT_EXPIRED,
    FailurePath.GRANT_REPLAY,
    FailurePath.GRANT_FORGED,
})


def _failure_for(outcome: AdapterOutcome) -> FailurePath:
    """S9's typed result mapped onto the failure table (`05 §2.3`)."""
    if outcome.occurrence is Occurrence.UNDETERMINABLE:
        return FailurePath.UNDETERMINABLE
    return {
        "ok": FailurePath.OK,
        "error": FailurePath.ADAPTER_ERROR,
        "timeout": FailurePath.TIMEOUT,
        "cancelled": FailurePath.CANCELLED,
        "perimeter": FailurePath.PERIMETER_UNAVAILABLE,
    }.get(outcome.status, FailurePath.ADAPTER_ERROR)


def _validate(request: EffectRequest) -> str | None:
    """S1 PARSE. `CT-03`: a cast on external data is not a parse."""
    if not isinstance(request, EffectRequest):
        return "not an EffectRequest"
    if not request.action or not isinstance(request.action, str):
        return "action is required"
    if not request.principal:
        return "principal is required (CT-16)"
    if not request.run_id:
        return "runId is required"
    if not isinstance(request.args, Mapping):
        return "args must be an object"
    if not isinstance(request.resource, Mapping):
        return "resource must be a selector object"
    if request.depth < 0:
        return "depth must be non-negative"
    if request.declared_sink_class not in tuple(SinkClass):
        return f"unknown sink class {request.declared_sink_class!r}"
    return None
