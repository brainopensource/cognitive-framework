"""Derived evaluator evidence state (ADR-0079)."""

from __future__ import annotations

from typing import Any, Mapping

__all__ = ["derive_evidence_state"]


def derive_evidence_state(
    evaluation: Mapping[str, Any],
    *,
    signed_verdict: Mapping[str, Any] | None,
    trajectory_complete: bool,
) -> Mapping[str, Any]:
    """Derive promotion eligibility from frozen policy and observed evidence.

    The result intentionally has no input-controlled ``promotable`` switch.
    Declared absence is operationally valid but never promotion-eligible;
    unsigned or wrongly shaped evidence is forged/broken, never absence.
    """
    mode = evaluation.get("mode") if isinstance(evaluation, Mapping) else None
    if signed_verdict is not None and not signed_verdict.get("signature"):
        return {
            "evidence_state": "forged_or_broken",
            "unattributable_for_promotion": True,
            "promotion_eligible": False,
            "reason": "unsigned_verdict",
        }
    if mode == "none":
        if signed_verdict is not None:
            return {
                "evidence_state": "forged",
                "unattributable_for_promotion": True,
                "promotion_eligible": False,
                "reason": "verdict_present_under_declared_absence",
            }
        return {
            "evidence_state": "absent_declared",
            "unattributable_for_promotion": True,
            "promotion_eligible": False,
            "reason": str(evaluation.get("absence_reason", "declared_absence")),
        }
    if signed_verdict is None:
        return {
            "evidence_state": "forged_or_broken",
            "unattributable_for_promotion": True,
            "promotion_eligible": False,
            "reason": "required_signed_verdict_missing",
        }
    if not trajectory_complete:
        return {
            "evidence_state": "forged_or_broken",
            "unattributable_for_promotion": True,
            "promotion_eligible": False,
            "reason": "trajectory_incomplete",
        }
    return {
        "evidence_state": "present_valid",
        "unattributable_for_promotion": False,
        "promotion_eligible": True,
        "reason": None,
    }
