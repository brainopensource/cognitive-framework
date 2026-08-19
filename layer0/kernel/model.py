"""Kernel value types that are not generated from schemas."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping

__all__ = [
    "ALERTABLE",
    "AdapterOutcome",
    "Event",
    "FailurePath",
    "Occurrence",
    "Span",
    "Trust",
]


class Trust(str, Enum):
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
    span_id: str
    trust: Trust
    source_class: str


class Occurrence(str, Enum):
    OCCURRED = "occurred"
    DID_NOT_OCCUR = "did_not_occur"
    UNDETERMINABLE = "undeterminable"


@dataclass(frozen=True, slots=True)
class AdapterOutcome:
    status: str
    occurrence: Occurrence = Occurrence.OCCURRED
    actual_cost: Mapping[str, int] = field(default_factory=dict)
    result_digest: str | None = None
    detail: str | None = None


class FailurePath(str, Enum):
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


ALERTABLE = frozenset({
    FailurePath.DENIED_SCOPE_ESCALATION,
    FailurePath.GRANT_FORGED,
    FailurePath.LEASE_LEAK,
    FailurePath.INTENT_APPEND_FAILED,
})


@dataclass(frozen=True, slots=True)
class Event:
    kind: str
    reason: str
    at: str
    run_id: str
    principal: str
    payload: Mapping[str, object] = field(default_factory=dict)
    alertable: bool = False
