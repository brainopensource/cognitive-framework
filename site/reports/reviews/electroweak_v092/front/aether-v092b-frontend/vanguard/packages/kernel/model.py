"""Kernel value types: requests, spans, outcomes, events, failure paths.

Values only — no behaviour that decides anything. The decisions live in
`classifier.py`, `policy.py`, `attenuation.py`, `grants.py`, `budget.py` and
`dispatch.py`, one job each (`01 §2`, single responsibility).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence

__all__ = [
    "AdapterOutcome",
    "EffectRequest",
    "Event",
    "FailurePath",
    "Occurrence",
    "SinkClass",
    "Span",
    "Trust",
]


class SinkClass(str, Enum):
    """`system-architecture-icd.md` §3.

    `pure` and `observation` effects need no capability grant; observations
    stay selector-checked and provenance-labelled. `privileged` effects need a
    descriptor-bound grant verified at the point of effect. **All three are
    recorded** — skipping the record for a cheap effect is `MF-KRN-009`.
    """

    PURE = "pure"
    OBSERVATION = "observation"
    PRIVILEGED = "privileged"


class Trust(str, Enum):
    """Provenance trust, ordered by rank (`05 §5.1`).

    Ordering exists for exactly one operation: combining labels can only move
    down (`K-28`). It is not a general lattice — `04 §3.1` keeps the six axes
    orthogonal, and this is the instruction-authority axis alone.
    """

    OPERATOR = "operator"
    SYSTEM = "system"
    AGENT_DERIVED = "agent_derived"
    UNTRUSTED_DERIVED = "untrusted_derived"
    UNTRUSTED_EXTERNAL = "untrusted_external"

    @property
    def rank(self) -> int:
        return _TRUST_RANK[self]

    @property
    def is_untrusted(self) -> bool:
        """Untrusted content may inform work; it may never authorise it."""
        return self.rank >= Trust.UNTRUSTED_DERIVED.rank


_TRUST_RANK = {
    Trust.OPERATOR: 0,
    Trust.SYSTEM: 1,
    Trust.AGENT_DERIVED: 2,
    Trust.UNTRUSTED_DERIVED: 3,
    Trust.UNTRUSTED_EXTERNAL: 4,
}


@dataclass(frozen=True, slots=True)
class Span:
    """A justifying span: some content that contributed to this request.

    `K-30`: the label is set at construction by the source class, never at
    consumption, and never by a judgement made at a call site (`K-31`).
    """

    span_id: str
    trust: Trust
    source_class: str


@dataclass(frozen=True, slots=True)
class EffectRequest:
    """S0 ENTER. The complete input to the dispatch sequence."""

    action: str
    resource: Mapping[str, Any]
    args: Mapping[str, Any]
    principal: str
    run_id: str
    depth: int = 0
    justifying_spans: Sequence[Span] = field(default_factory=tuple)
    parent_lease: str | None = None
    declared_sink_class: SinkClass = SinkClass.PRIVILEGED
    idempotency_key: str | None = None


class Occurrence(str, Enum):
    """Did the effect happen? `UNDETERMINABLE` is first-class (`F-22`)."""

    OCCURRED = "occurred"
    DID_NOT_OCCUR = "did_not_occur"
    UNDETERMINABLE = "undeterminable"


@dataclass(frozen=True, slots=True)
class AdapterOutcome:
    """S9's typed result. Every adapter returns this shape, denial included."""

    status: str  # ok · error · timeout · cancelled
    occurrence: Occurrence = Occurrence.OCCURRED
    actual_cost: Mapping[str, int] = field(default_factory=dict)
    result_digest: str | None = None
    detail: str | None = None


class FailurePath(str, Enum):
    """`05 §2.3`. Every exit from the sequence is one of these.

    `AT-09` requires the set to be exhaustive: an exit not in this table is a
    defect, so `dispatch.py` never returns or raises without naming one.
    """

    OK = "ok"
    SCHEMA = "F-01"
    UNKNOWN_ACTION = "F-02"
    ADAPTER_UNAVAILABLE = "F-03"
    DESCRIPTOR = "F-04"
    CLASSIFIER_ERROR = "F-05"
    DENIED_REJECT = "F-06"
    DENIED_ASK_FAIL_CLOSED = "F-07"
    APPROVAL_SUSPENDED = "F-08"
    DENIED_UNTRUSTED_JUSTIFYING = "F-09"
    DENIED_SCOPE_ESCALATION = "F-10"
    GRANT_ISSUE = "F-11"
    BUDGET_DENIED = "F-12"
    PARENT_LEASE_CLOSED = "F-13"
    GRANT_MISMATCH = "F-14"
    GRANT_EXPIRED = "F-15"
    GRANT_REPLAY = "F-16"
    GRANT_FORGED = "F-17"
    ADAPTER_ERROR = "F-18"
    TIMEOUT = "F-19"
    CANCELLED = "F-20"
    PERIMETER_UNAVAILABLE = "F-21"
    INTENT_APPEND_FAILED = "F-21a"
    UNDETERMINABLE = "F-22"
    COMMIT_FAILED = "F-23"
    LEASE_LEAK = "F-24"
    EMIT_FAILED = "F-25"


#: Paths that must page rather than log (`F-10`, `F-17`, `F-24`, `K-27`).
ALERTABLE = frozenset({
    FailurePath.DENIED_SCOPE_ESCALATION,
    FailurePath.GRANT_FORGED,
    FailurePath.LEASE_LEAK,
    FailurePath.INTENT_APPEND_FAILED,
})


@dataclass(frozen=True, slots=True)
class Event:
    """A kernel event. Past tense, always (`04 §0.5`)."""

    kind: str
    reason: str
    at: str
    run_id: str
    principal: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    alertable: bool = False
