"""Port-level error taxonomy and protocols for evidence capture (ICD §2, ADR-0096 §14.2, C-02).

This module defines the port-level error taxonomy and protocol for evidence capture,
allowing Agency and other layers to depend on the contract without importing Runtime.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

__all__ = [
    "EvidenceCaptureError",
    "EvidenceCaptureRequiredError",
    "EvidenceCaptureDegraded",
    "EvidenceSink",
]


class EvidenceCaptureError(RuntimeError):
    """Base error for all evidence capture failures."""


class EvidenceCaptureRequiredError(EvidenceCaptureError):
    """Fatal. The evidentiary run must terminate; do not swallow."""


class EvidenceCaptureDegraded(EvidenceCaptureError):
    """Optional capture failed but was durably recorded as incomplete."""


@runtime_checkable
class EvidenceSink(Protocol):
    """Protocol for durable evidence sinks implemented by the runtime."""

    def append_event(self, event: Any) -> None:
        """Append an event to the evidence ledger, or raise."""

    def put_artifact(
        self,
        role: str,
        payload: bytes,
        *,
        required: bool = True,
    ) -> Any:
        """required=True -> raise EvidenceCaptureRequiredError on failure.
        required=False -> raise EvidenceCaptureDegraded (caller records).
        """
