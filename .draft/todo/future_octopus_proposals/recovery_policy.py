"""Typed recovery policy: one classified failure, one specific corrective action.

This sits *above* the kernel and *beside* `protocol_recovery` (which owns the
narrow proposal-parsing state machine). It answers a different question: given
a failure of any class, what should the runtime do next?

Two invariants drive the whole design.

1. **No blind retry.** A retry that re-issues the same action against the same
   state is not recovery, it is a loop. Every decision carries an
   ``attempt_fingerprint``; the policy refuses to repeat one it has already
   spent and escalates the strategy instead.
2. **Recovery never widens authority.** Actions here change *how* we ask, not
   *what we may do*. No branch grants a capability, raises a budget, or relaxes
   a completion criterion.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any, Mapping

from ...domain.canonicalisation.digest import digest_of

__all__ = [
    "FailureClass",
    "RecoveryAction",
    "RecoveryPlan",
    "RecoveryLedger",
    "TypedRecoveryPolicy",
    "classify_failure",
]


class FailureClass(str, Enum):
    """The eight failure classes the runtime distinguishes."""

    TRANSPORT = "transport"        # socket reset, timeout, 5xx
    PROTOCOL = "protocol"          # unparseable / schema-violating reply
    TRUNCATION = "truncation"      # reply cut off mid-object
    TOOL_CALL = "tool_call"        # named tool absent, or args fail schema
    PATCH = "patch"                # preimage mismatch, hunk did not apply
    VERIFICATION = "verification"  # tests ran and failed
    PERMISSION = "permission"      # capability/scope/budget denial
    PROVIDER = "provider"          # auth, quota, model withdrawn
    UNKNOWN = "unknown"


class RecoveryAction(str, Enum):
    """What to actually do. Each maps to exactly one runtime behaviour."""

    RETRY_TRANSPORT = "retry_transport"          # same request, backoff
    REFORMAT_REDUCED = "reformat_reduced"        # re-ask with reduced schema
    DEGRADE_DIALECT = "degrade_dialect"          # drop to a simpler tool style
    CONTINUE_OUTPUT = "continue_output"          # ask for the remainder
    REPAIR_TOOL_CALL = "repair_tool_call"        # feed schema + valid names back
    RELOCATE_AND_RECOMPILE = "relocate_recompile"  # re-read file, rebuild context
    DIAGNOSE_TO_PLANNER = "diagnose_to_planner"  # return failing output to planner
    ESCALATE_APPROVAL = "escalate_approval"      # ask the human; never self-grant
    SWITCH_PROVIDER = "switch_provider"          # try a different model
    REPLAN = "replan"                            # budget spent, plan again
    TERMINATE = "terminate"                      # give up, explicitly


#: Which classes are retryable at all, and how many attempts each may spend.
#: PERMISSION is absent on purpose: a denial is a decision, not a transient.
_DEFAULT_BUDGETS: Mapping[FailureClass, int] = {
    FailureClass.TRANSPORT: 3,
    FailureClass.PROTOCOL: 2,
    FailureClass.TRUNCATION: 1,
    FailureClass.TOOL_CALL: 2,
    FailureClass.PATCH: 2,
    FailureClass.VERIFICATION: 3,
    FailureClass.PROVIDER: 1,
    FailureClass.PERMISSION: 0,
    FailureClass.UNKNOWN: 1,
}

#: Substrings that identify a class from an adapter's error string. Ordered:
#: the first match wins, so put the specific before the generic.
_SIGNATURES: tuple[tuple[FailureClass, tuple[str, ...]], ...] = (
    (FailureClass.PERMISSION, ("denied", "not permitted", "capability", "scope",
                               "budget_denied", "forbidden", "unauthorised")),
    (FailureClass.PROVIDER, ("api key", "unauthorized", "401", "402", "quota",
                             "insufficient_credits", "model_not_found", "decommissioned")),
    (FailureClass.TRUNCATION, ("truncated", "max_tokens", "length_exceeded",
                               "incomplete", "unterminated")),
    (FailureClass.PATCH, ("preimage", "hunk", "does not apply", "patch failed",
                          "context mismatch", "no such file")),
    (FailureClass.VERIFICATION, ("test failed", "assertion", "exit code 1",
                                 "failed tests", "pytest")),
    (FailureClass.TOOL_CALL, ("unknown tool", "no such tool", "invalid arguments",
                              "schema violation", "missing required")),
    (FailureClass.PROTOCOL, ("not_json", "json", "parse", "malformed",
                             "missing_kind", "not_an_object", "decode")),
    (FailureClass.TRANSPORT, ("timeout", "timed out", "connection", "reset",
                              "503", "502", "500", "temporarily unavailable")),
)


def classify_failure(
    signal: Any,
    *,
    hint: FailureClass | str | None = None,
) -> FailureClass:
    """Map a raw failure signal onto a class.

    ``hint`` wins when the caller already knows the class (the dialect
    normaliser, for instance, reports `truncated` structurally). Otherwise we
    match on the error text, which is all a provider gives us.
    """
    if isinstance(hint, FailureClass):
        return hint
    if isinstance(hint, str) and hint:
        try:
            return FailureClass(hint)
        except ValueError:
            pass

    if isinstance(signal, FailureClass):
        return signal

    text = ""
    if isinstance(signal, str):
        text = signal
    elif isinstance(signal, Mapping):
        text = " ".join(
            str(signal.get(key, "")) for key in ("failure", "error", "code", "message", "reason")
        )
    elif isinstance(signal, BaseException):
        text = f"{type(signal).__name__} {signal}"
    else:
        text = str(signal or "")

    lowered = text.lower()
    if not lowered.strip():
        return FailureClass.UNKNOWN
    for failure_class, needles in _SIGNATURES:
        if any(needle in lowered for needle in needles):
            return failure_class
    return FailureClass.UNKNOWN


@dataclass(frozen=True, slots=True)
class RecoveryPlan:
    """The corrective action, plus everything needed to execute and audit it."""

    failure_class: FailureClass
    action: RecoveryAction
    reason: str
    #: Guidance handed back to the model or planner. Never contains secrets.
    feedback: str = ""
    #: Delay before re-issuing, for transport backoff only.
    backoff_millis: int = 0
    #: Set when the action requires re-asking with a degraded dialect.
    reduced_schema: bool = False
    degrade_dialect: bool = False
    #: Identifies the (action, state) pair this plan responds to.
    attempt_fingerprint: str = ""
    #: True when the run should stop; the caller must not continue the loop.
    terminal: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Durable event payload."""
        return {
            "failure_class": self.failure_class.value,
            "action": self.action.value,
            "reason": self.reason,
            "backoff_millis": self.backoff_millis,
            "reduced_schema": self.reduced_schema,
            "degrade_dialect": self.degrade_dialect,
            "attempt_fingerprint": self.attempt_fingerprint,
            "terminal": self.terminal,
        }


@dataclass(frozen=True, slots=True)
class RecoveryLedger:
    """Immutable record of what has already been tried.

    Kept as a value so it serialises into a checkpoint and survives a resume:
    a restarted run must not re-spend retries it already burned.
    """

    spent: Mapping[str, int] = field(default_factory=dict)
    fingerprints: tuple[str, ...] = ()

    def count(self, failure_class: FailureClass) -> int:
        return int(self.spent.get(failure_class.value, 0))

    def has_seen(self, fingerprint: str) -> bool:
        return bool(fingerprint) and fingerprint in self.fingerprints

    def record(self, failure_class: FailureClass, fingerprint: str) -> "RecoveryLedger":
        spent = dict(self.spent)
        spent[failure_class.value] = spent.get(failure_class.value, 0) + 1
        seen = self.fingerprints
        if fingerprint and fingerprint not in seen:
            seen = (*seen, fingerprint)
        return RecoveryLedger(spent=spent, fingerprints=seen)

    def to_dict(self) -> dict[str, Any]:
        return {"spent": dict(self.spent), "fingerprints": list(self.fingerprints)}

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any] | None) -> "RecoveryLedger":
        if not isinstance(raw, Mapping):
            return cls()
        spent = raw.get("spent")
        fingerprints = raw.get("fingerprints") or ()
        return cls(
            spent=dict(spent) if isinstance(spent, Mapping) else {},
            fingerprints=tuple(str(f) for f in fingerprints),
        )


def _fingerprint(failure_class: FailureClass, context: Mapping[str, Any] | None) -> str:
    """Identity of one recovery attempt: the class plus the state it acted on.

    Two attempts with the same fingerprint would be the same retry against the
    same world, which is precisely what we refuse to do twice.
    """
    payload = {
        "class": failure_class.value,
        "action": (context or {}).get("action"),
        "target": (context or {}).get("target"),
        "state": (context or {}).get("state_digest"),
    }
    return digest_of(payload)


class TypedRecoveryPolicy:
    """Maps a classified failure to exactly one corrective action.

    Stateless: the caller threads a `RecoveryLedger` through, so the policy is
    safe to share and trivially testable.
    """

    def __init__(self, budgets: Mapping[FailureClass, int] | None = None) -> None:
        self.budgets = dict(_DEFAULT_BUDGETS)
        if budgets:
            self.budgets.update(budgets)

    def budget_for(self, failure_class: FailureClass) -> int:
        return self.budgets.get(failure_class, 1)

    def decide(
        self,
        signal: Any,
        ledger: RecoveryLedger | None = None,
        *,
        hint: FailureClass | str | None = None,
        context: Mapping[str, Any] | None = None,
        alternate_provider_available: bool = False,
    ) -> tuple[RecoveryPlan, RecoveryLedger]:
        """Classify, choose an action, and return the updated ledger.

        Returning the ledger rather than mutating it keeps resume correct: the
        caller decides when the attempt is durably recorded.
        """
        current = ledger or RecoveryLedger()
        failure_class = classify_failure(signal, hint=hint)
        fingerprint = _fingerprint(failure_class, context)
        spent = current.count(failure_class)
        budget = self.budget_for(failure_class)

        # A permission denial is a decision by the kernel. Recovery may ask a
        # human, never re-attempt the denied effect.
        if failure_class is FailureClass.PERMISSION:
            return self._plan(
                failure_class, RecoveryAction.ESCALATE_APPROVAL,
                "authority denied; escalation is the only lawful continuation",
                feedback=("The requested effect was denied. Propose an action within "
                          "the granted scope, or finish and report the blocker."),
                fingerprint=fingerprint,
            ), current.record(failure_class, fingerprint)

        # Budget exhausted for this class: stop retrying, replan or terminate.
        if spent >= budget:
            if failure_class in {FailureClass.VERIFICATION, FailureClass.PATCH}:
                return self._plan(
                    failure_class, RecoveryAction.REPLAN,
                    f"{failure_class.value} retries exhausted ({spent}/{budget})",
                    feedback=("Repeated attempts failed. Re-plan from the observed "
                              "diagnostics rather than re-editing the same location."),
                    fingerprint=fingerprint,
                ), current.record(failure_class, fingerprint)
            return self._plan(
                failure_class, RecoveryAction.TERMINATE,
                f"{failure_class.value} retries exhausted ({spent}/{budget})",
                fingerprint=fingerprint, terminal=True,
            ), current.record(failure_class, fingerprint)

        # Refuse to repeat an attempt we have already made against this state.
        # Escalate the strategy instead of looping.
        if current.has_seen(fingerprint):
            escalated = self._escalate(failure_class, alternate_provider_available)
            return self._plan(
                failure_class, escalated,
                "identical attempt already spent; escalating strategy",
                feedback=("The previous corrective attempt did not change the "
                          "outcome. Change approach rather than repeating it."),
                fingerprint=fingerprint,
                reduced_schema=escalated is RecoveryAction.REFORMAT_REDUCED,
                degrade_dialect=escalated is RecoveryAction.DEGRADE_DIALECT,
                terminal=escalated is RecoveryAction.TERMINATE,
            ), current.record(failure_class, fingerprint)

        plan = self._first_attempt(failure_class, spent, alternate_provider_available, fingerprint)
        return plan, current.record(failure_class, fingerprint)

    # -- internals ---------------------------------------------------------

    def _first_attempt(
        self,
        failure_class: FailureClass,
        spent: int,
        alternate_provider: bool,
        fingerprint: str,
    ) -> RecoveryPlan:
        if failure_class is FailureClass.TRANSPORT:
            return self._plan(
                failure_class, RecoveryAction.RETRY_TRANSPORT,
                "transient transport failure",
                backoff_millis=500 * (2 ** spent),  # 500, 1000, 2000
                fingerprint=fingerprint,
            )

        if failure_class is FailureClass.PROTOCOL:
            # First protocol failure: re-ask with a reduced schema. Second:
            # drop the dialect a rung, because the format itself is the problem.
            if spent == 0:
                return self._plan(
                    failure_class, RecoveryAction.REFORMAT_REDUCED,
                    "reply did not parse; re-asking with a reduced schema",
                    feedback=("Your previous reply could not be parsed. Reply with "
                              "one JSON object and no other text."),
                    reduced_schema=True, fingerprint=fingerprint,
                )
            return self._plan(
                failure_class, RecoveryAction.DEGRADE_DIALECT,
                "repeated parse failure; degrading dialect",
                feedback="Use the simplest supported reply format.",
                reduced_schema=True, degrade_dialect=True, fingerprint=fingerprint,
            )

        if failure_class is FailureClass.TRUNCATION:
            return self._plan(
                failure_class, RecoveryAction.CONTINUE_OUTPUT,
                "reply was cut off; requesting the remainder",
                feedback=("Your reply was truncated. Reply again, more concisely, "
                          "keeping the object complete."),
                fingerprint=fingerprint,
            )

        if failure_class is FailureClass.TOOL_CALL:
            return self._plan(
                failure_class, RecoveryAction.REPAIR_TOOL_CALL,
                "tool name or arguments invalid",
                feedback=("That action is not available or its arguments were "
                          "invalid. Choose from the listed actions and match the "
                          "declared parameters exactly."),
                fingerprint=fingerprint,
            )

        if failure_class is FailureClass.PATCH:
            # The file moved under us or the context was stale. Re-read before
            # re-editing — never re-apply the same hunk to the same preimage.
            return self._plan(
                failure_class, RecoveryAction.RELOCATE_AND_RECOMPILE,
                "patch did not apply; re-locating the target",
                feedback=("The edit did not apply because the file content "
                          "differs from what the patch expected. Re-read the "
                          "target region and rebuild the edit from current content."),
                fingerprint=fingerprint,
            )

        if failure_class is FailureClass.VERIFICATION:
            return self._plan(
                failure_class, RecoveryAction.DIAGNOSE_TO_PLANNER,
                "tests failed; returning diagnostics",
                feedback=("Verification failed. Read the failing output and fix the "
                          "cause. Do not weaken or delete the test."),
                fingerprint=fingerprint,
            )

        if failure_class is FailureClass.PROVIDER:
            if alternate_provider:
                return self._plan(
                    failure_class, RecoveryAction.SWITCH_PROVIDER,
                    "provider unusable; routing to an alternate model",
                    fingerprint=fingerprint,
                )
            return self._plan(
                failure_class, RecoveryAction.TERMINATE,
                "provider unusable and no alternate is configured",
                fingerprint=fingerprint, terminal=True,
            )

        return self._plan(
            failure_class, RecoveryAction.REPLAN,
            "unclassified failure; replanning once",
            feedback="An unexpected error occurred. Reassess before acting again.",
            fingerprint=fingerprint,
        )

    @staticmethod
    def _escalate(failure_class: FailureClass, alternate_provider: bool) -> RecoveryAction:
        """The next strategy up when the obvious one already failed."""
        if failure_class in {FailureClass.PROTOCOL, FailureClass.TRUNCATION}:
            return RecoveryAction.DEGRADE_DIALECT
        if failure_class is FailureClass.TRANSPORT:
            return (RecoveryAction.SWITCH_PROVIDER if alternate_provider
                    else RecoveryAction.TERMINATE)
        if failure_class in {FailureClass.PATCH, FailureClass.VERIFICATION,
                             FailureClass.TOOL_CALL}:
            return RecoveryAction.REPLAN
        return RecoveryAction.TERMINATE

    @staticmethod
    def _plan(
        failure_class: FailureClass,
        action: RecoveryAction,
        reason: str,
        *,
        feedback: str = "",
        backoff_millis: int = 0,
        reduced_schema: bool = False,
        degrade_dialect: bool = False,
        fingerprint: str = "",
        terminal: bool = False,
    ) -> RecoveryPlan:
        return RecoveryPlan(
            failure_class=failure_class,
            action=action,
            reason=reason,
            feedback=feedback,
            backoff_millis=backoff_millis,
            reduced_schema=reduced_schema,
            degrade_dialect=degrade_dialect,
            attempt_fingerprint=fingerprint,
            terminal=terminal,
        )
