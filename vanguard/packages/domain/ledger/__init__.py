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
from .agent_view import (
    AGENT_VIEW_REDUCER_VERSION,
    AgentView,
    AgentViewCheckpoint,
    fold_agent_view,
)
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
    VerdictRecord,
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
    "AGENT_VIEW_REDUCER_VERSION",
    "AgentView",
    "AgentViewCheckpoint",
    "fold_agent_view",
    "LedgerState",
    "EpisodeState",
    "BudgetLeaseState",
    "EffectRecord",
    "ArtifactRecord",
    "EvidenceRecord",
    "ApprovalRecord",
    "VerdictRecord",
    "ReducerError",
    "initial_state",
    "reduce_event",
    "reduce_batch",
    "reconstruct_state",
    "compute_state_digest",
]
