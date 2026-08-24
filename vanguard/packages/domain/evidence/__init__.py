"""Evidence types. Pure, stdlib-only, no I/O (`VG-03 §4`, `LT-1`)."""

from .audit import (
    EvidenceAuditResult,
    REQUIRED_ROW_COUNT,
    REQUIRED_ROW_NAMES,
    audit_foundation_evidence,
)
from .claim import (
    Claim,
    ClaimError,
    Evaluator,
    InvalidationCondition,
    Uncertainty,
    Validity,
    parse_claim,
)
from .foundation import (
    API as FOUNDATION_EVIDENCE_API,
    EvidenceRow,
    FoundationEvidence,
    FoundationEvidenceError,
    absent,
    build_foundation_evidence,
    derived,
)
from .guardrails import derive_evidence_state
from .preregistration import (
    API as PREREGISTRATION_API,
    Preregistration,
    PreregistrationError,
)

__all__ = [
    "Claim",
    "ClaimError",
    "Evaluator",
    "InvalidationCondition",
    "Uncertainty",
    "Validity",
    "parse_claim",
    "derive_evidence_state",
    "EvidenceAuditResult",
    "REQUIRED_ROW_COUNT",
    "REQUIRED_ROW_NAMES",
    "audit_foundation_evidence",
    "FOUNDATION_EVIDENCE_API",
    "EvidenceRow",
    "FoundationEvidence",
    "FoundationEvidenceError",
    "absent",
    "build_foundation_evidence",
    "derived",
    "PREREGISTRATION_API",
    "Preregistration",
    "PreregistrationError",
]
