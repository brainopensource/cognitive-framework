"""Trajectory-local rejection for premature explicit completion proposals.

This narrow guard complements the richer episode completion policy.  It owns
only the early T-82 invariant: an explicit ``finish`` cannot advance while a
write trajectory has no mutation, no verification, or an unparsed invocation.
It grants no completion authority.
"""

from __future__ import annotations

from typing import Any, Mapping

from .episode.admission_gate import AdmissionVerdict

__all__ = ["PREMATURE_FINISH_REJECTED", "admit_finish_candidate"]

PREMATURE_FINISH_REJECTED = "PREMATURE_FINISH_REJECTED"


def admit_finish_candidate(
    proposal: Mapping[str, Any],
    *,
    mutation_observed: bool,
    verification_observed: bool,
    unparsed_invocations: int = 0,
) -> AdmissionVerdict:
    """Reject an explicit finish before the full completion gate evaluates it."""
    if proposal.get("kind") != "finish":
        return AdmissionVerdict(True, "NOT_A_FINISH_CANDIDATE")
    if (
        not mutation_observed
        or not verification_observed
        or unparsed_invocations > 0
    ):
        return AdmissionVerdict(
            False,
            PREMATURE_FINISH_REJECTED,
            "Completion is premature: mutate and verify the requested change, "
            "and resolve every unparsed invocation before calling finish.",
        )
    return AdmissionVerdict(True, "FINISH_CANDIDATE_READY_FOR_COMPLETION_GATE")
