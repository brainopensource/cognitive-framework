"""Two-axis task disposition and settlement wire contract (T-72 / §EW-9.1).

This module separates the exterior task evaluation axis from the runtime's
terminal status axis. Oracle pass never implies terminal completed, and
a run may legitimately record terminal_status="abandoned" with disposition="passed".
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from ..canonicalisation.digest import digest_of

__all__ = [
    "SETTLEMENT_SCHEMA",
    "DispositionError",
    "SettlementReceipt",
    "TaskDisposition",
    "disposition_to_outcome",
    "parse_settlement",
]

#: Payload schema carried on the existing `VerdictRecorded` ledger kind.
SETTLEMENT_SCHEMA = "aether.settlement/1"


class DispositionError(ValueError):
    """A settlement that cannot be admitted. Raised at build or parse."""


class TaskDisposition(str, Enum):
    """The honest four-state settlement. `str` mixin so JCS sees the value."""

    PASSED = "passed"
    FAILED = "failed"
    UNDETERMINABLE = "undeterminable"
    NOT_RUN = "not_run"

    @property
    def satisfies_predicate(self) -> bool:
        """Only `passed` satisfies an acceptance predicate."""
        return self is TaskDisposition.PASSED

    @property
    def is_missingness(self) -> bool:
        """Absent evidence, distinguished from a negative result."""
        return self in (TaskDisposition.UNDETERMINABLE, TaskDisposition.NOT_RUN)


def disposition_to_outcome(disposition: TaskDisposition) -> str:
    """Project onto evidence outcome. Refuses on `NOT_RUN`."""
    if disposition is TaskDisposition.NOT_RUN:
        raise DispositionError(
            "not_run has no evidence outcome: a task that never executed "
            "cannot carry a signed envelope"
        )
    return disposition.value


@dataclass(frozen=True, slots=True)
class SettlementReceipt:
    """Immutable two-axis settlement receipt."""

    task_id: str
    disposition: TaskDisposition
    terminal_status: str = ""
    oracle_digest: str = ""
    verification_subject_digest: str = ""
    executed_test_count: int = 0
    envelope_digest: str = ""
    undeterminable_reason: str = ""

    def __post_init__(self) -> None:
        if not self.task_id or not self.task_id.strip():
            raise DispositionError("task_id must be non-empty")

        if not isinstance(self.disposition, TaskDisposition):
            raise DispositionError(f"invalid disposition: {self.disposition!r}")

        if self.executed_test_count < 0:
            raise DispositionError("executed_test_count must be >= 0")

        if self.disposition is TaskDisposition.PASSED:
            if self.executed_test_count <= 0:
                raise DispositionError(
                    "passed requires executed_test_count > 0"
                )
            if not self.oracle_digest or not self.verification_subject_digest:
                raise DispositionError(
                    "passed requires a bound oracle and verification subject"
                )

        if self.disposition is TaskDisposition.UNDETERMINABLE:
            if not self.undeterminable_reason.strip():
                raise DispositionError(
                    "undeterminable requires an explicit reason"
                )

        if self.disposition is TaskDisposition.NOT_RUN:
            if (
                self.executed_test_count
                or self.oracle_digest
                or self.verification_subject_digest
                or self.envelope_digest
            ):
                raise DispositionError(
                    "not_run cannot carry execution evidence"
                )

    @property
    def identity(self) -> str:
        return digest_of(self.to_wire())

    def to_wire(self) -> dict[str, Any]:
        wire: dict[str, Any] = {
            "schema": SETTLEMENT_SCHEMA,
            "taskId": self.task_id,
            "disposition": self.disposition.value,
            "executedTestCount": self.executed_test_count,
        }
        if self.terminal_status:
            wire["terminalStatus"] = self.terminal_status
        if self.oracle_digest:
            wire["oracleDigest"] = self.oracle_digest
        if self.verification_subject_digest:
            wire["verificationSubjectDigest"] = self.verification_subject_digest
        if self.envelope_digest:
            wire["envelopeDigest"] = self.envelope_digest
        if self.undeterminable_reason:
            wire["undeterminableReason"] = self.undeterminable_reason
        return wire


def parse_settlement(source: Mapping[str, Any]) -> SettlementReceipt:
    """Parse a wire settlement, refusing anything the constructor refuses."""
    if source.get("schema") != SETTLEMENT_SCHEMA:
        raise DispositionError(
            f"expected {SETTLEMENT_SCHEMA}, got {source.get('schema')!r}"
        )
    raw = str(source.get("disposition", ""))
    try:
        disposition = TaskDisposition(raw)
    except ValueError as exc:
        raise DispositionError(f"unknown disposition {raw!r}") from exc
    return SettlementReceipt(
        task_id=str(source.get("taskId", "")),
        disposition=disposition,
        terminal_status=str(source.get("terminalStatus", "")),
        oracle_digest=str(source.get("oracleDigest", "")),
        verification_subject_digest=str(
            source.get("verificationSubjectDigest", "")
        ),
        executed_test_count=int(source.get("executedTestCount", 0)),
        envelope_digest=str(source.get("envelopeDigest", "")),
        undeterminable_reason=str(source.get("undeterminableReason", "")),
    )
