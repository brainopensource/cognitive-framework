"""Typed errors for the Coding Max harness (`spec §48`).

Every error carries a `recoverable` flag. The distinction is operational, not
decorative: a recoverable error is folded into the trajectory as evidence and
routed to the recovery policy, while a terminal error ends the run as an
*instrument* failure and must never be reported as a task verdict.

This mirrors the substrate's existing separation of the run-termination axis
from the evaluation axis (`RunTermination` in `agency/episode/state.py`).
"""

from __future__ import annotations

__all__ = [
    "BudgetExceeded",
    "CheckpointError",
    "CodingMaxError",
    "ContextCompilationError",
    "IntelligenceUnavailable",
    "ModelError",
    "PatchApplicationError",
    "RepositoryAccessError",
    "ToolExecutionError",
    "VerificationError",
]


class CodingMaxError(RuntimeError):
    """Base class. `recoverable` decides recovery vs. termination."""

    recoverable: bool = False

    def __init__(self, message: str, *, detail: str = "") -> None:
        super().__init__(message)
        self.detail = detail

    def to_dict(self) -> dict[str, object]:
        return {
            "error": type(self).__name__,
            "message": str(self),
            "detail": self.detail,
            "recoverable": self.recoverable,
        }


class RepositoryAccessError(CodingMaxError):
    """The workspace could not be read (missing, permission, not a repo)."""

    recoverable = False


class IntelligenceUnavailable(CodingMaxError):
    """A repository-intelligence provider is absent or timed out.

    Always recoverable: the composite provider degrades to the next provider
    in the ladder. This is the error that keeps LDA optional (`spec §9`).
    """

    recoverable = True


class ContextCompilationError(CodingMaxError):
    """Context could not be compiled within the declared token budget."""

    recoverable = True


class ToolExecutionError(CodingMaxError):
    """A tool ran and failed in a way the worker may react to."""

    recoverable = True


class PatchApplicationError(CodingMaxError):
    """A patch did not apply against current repository state."""

    recoverable = True


class VerificationError(CodingMaxError):
    """The verification pipeline itself failed (not: checks reported failures).

    A failing *check* is a `VerificationResult` with `passed=False`; it is data.
    This exception means the pipeline could not produce a verdict at all.
    """

    recoverable = True


class ModelError(CodingMaxError):
    """A provider call failed. Recoverable while a fallback tier remains."""

    recoverable = True


class BudgetExceeded(CodingMaxError):
    """A budget dimension is exhausted. Terminal for the current strategy."""

    recoverable = False


class CheckpointError(CodingMaxError):
    """A checkpoint could not be captured or restored."""

    recoverable = False
