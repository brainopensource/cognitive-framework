"""Domain ledger types and pure reducers.

No project imports, no I/O, no clocks, no randomness (ICD §2, `domain`).
"""

from .events import (
    EVENT_KINDS,
    VALID_CONFIDENTIALITIES,
    VALID_REDACTION_STATUSES,
    VALID_RETENTIONS,
    VALID_SCOPES,
    VALID_TRAINABILITIES,
    EventEnvelope,
    parse_event_envelope,
)
from .coding_session import project_coding_session
from .reducer import (
    ReducerError,
    compute_state_digest,
    initial_state,
    reconstruct_state,
    reduce_batch,
    reduce_event,
)
from .state import (
    ApprovalRecord,
    ArtifactRecord,
    BudgetLeaseState,
    EffectRecord,
    EpisodeState,
    EvidenceRecord,
    LedgerState,
)

__all__ = [
    "EventEnvelope",
    "EVENT_KINDS",
    "VALID_SCOPES",
    "VALID_CONFIDENTIALITIES",
    "VALID_RETENTIONS",
    "VALID_TRAINABILITIES",
    "VALID_REDACTION_STATUSES",
    "parse_event_envelope",
    "LedgerState",
    "EpisodeState",
    "BudgetLeaseState",
    "EffectRecord",
    "ArtifactRecord",
    "EvidenceRecord",
    "ApprovalRecord",
    "ReducerError",
    "initial_state",
    "reduce_event",
    "reduce_batch",
    "reconstruct_state",
    "compute_state_digest",
    "project_coding_session",
]
