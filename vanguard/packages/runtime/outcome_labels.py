"""Canonical outcome labels and failure causes (REQ-TRUST-001, S21, S31, S32).

Holds explicit, attributable outcome strings so that budget exhaustion, attempts exhaustion,
instrument errors, verification failures, and progress stalls are distinguishable across telemetry.
"""

from __future__ import annotations

__all__ = [
    "OutcomeLabel",
    "classify_failure_cause",
    "classify_instrument_error",
]


class OutcomeLabel:
    """Canonical terminal outcome labels."""

    ORACLE_GREEN = "oracle_green"
    STEP_VERIFIED = "step_verified"
    BUDGET_EXHAUSTED = "budget_exhausted"
    ATTEMPTS_EXHAUSTED = "attempts_exhausted"
    NO_PROGRESS = "no_progress"
    INSTRUMENT_ERROR = "instrument_error"
    REPLAN_REQUESTED = "replan_requested"
    DIAGNOSTIC_NEEDED = "diagnostic_needed"
    ABSTAINED = "abstained"
    DENIED_SCOPE_ESCALATION = "denied_scope_escalation"
    PRICE_UNKNOWN = "instrument_error:price_unknown"
    PROVIDER_KEY_MISSING = "instrument_error:provider_key_missing"
    WORKSPACE_MISSING = "instrument_error:workspace_missing"
    PAID_MODEL_REFUSED = "instrument_error:paid_model_refused"
    UNCLASSIFIED = "instrument_error:unclassified"


def classify_failure_cause(detail: str) -> str:
    """Map a detailed error string to a canonical failure cause."""
    lowered = (detail or "").lower()
    if not lowered:
        return OutcomeLabel.UNCLASSIFIED
    if "multiple actions" in lowered or "multi_action" in lowered:
        return "instrument_error:multi_action_proposal"
    if "timed out" in lowered or "timeout" in lowered:
        return "instrument_error:provider_timeout"
    if "is not pulled" in lowered or "tag_absent" in lowered:
        return "instrument_error:model_tag_absent"
    if "no daemon answering" in lowered or "unreachable" in lowered:
        return "instrument_error:provider_unreachable"
    if "key" in lowered and ("missing" in lowered or "not set" in lowered):
        return OutcomeLabel.PROVIDER_KEY_MISSING
    if "refusing to spend" in lowered or "free band" in lowered:
        return OutcomeLabel.PAID_MODEL_REFUSED
    if "model_not_invoked" in lowered:
        return "instrument_error:model_not_invoked"
    if "price" in lowered and ("unknown" in lowered or "not registered" in lowered):
        return OutcomeLabel.PRICE_UNKNOWN
    if "workspace" in lowered and ("missing" in lowered or "not exist" in lowered):
        return OutcomeLabel.WORKSPACE_MISSING
    if "malformed" in lowered:
        return "instrument_error:provider_malformed_response"
    return OutcomeLabel.UNCLASSIFIED


#: Backward-compatible alias used in runtime drivers
classify_instrument_error = classify_failure_cause
