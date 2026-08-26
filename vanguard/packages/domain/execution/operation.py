"""Protocol shape for a causally attributable operation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class OperationStatus(str, Enum):
    PROPOSED = "proposed"
    AUTHORIZED = "authorized"
    DISPATCHED = "dispatched"
    OBSERVED = "observed"
    SETTLED = "settled"
    COMMITTED = "committed"
    INVALIDATED = "invalidated"


@dataclass(frozen=True, slots=True)
class OperationRecord:
    """An operation's causal references and settlement status.

    The record deliberately has no verb subclasses: verbs are domain data,
    while authority and attenuation remain outside this value object.
    """

    operation_id: str
    verb: str
    input_refs: tuple[str, ...]
    output_refs: tuple[str, ...]
    causation_id: str | None
    lineage_id: str
    scope_digest: str
    status: OperationStatus | str
    resources: Mapping[str, int]

    def __post_init__(self) -> None:
        if not self.operation_id or not self.verb or not self.lineage_id:
            raise ValueError("operation_id, verb, and lineage_id are required")
        if not self.scope_digest:
            raise ValueError("scope_digest is required")
        if isinstance(self.status, str) and self.status not in {
            status.value for status in OperationStatus
        }:
            raise ValueError(f"unknown operation status: {self.status!r}")
        if any(int(value) < 0 for value in self.resources.values()):
            raise ValueError("operation resources cannot be negative")
