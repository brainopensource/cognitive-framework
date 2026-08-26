"""Episode coordination (`ICD §2`, `VG-03 §6`).

May import `domain`, `ports` and `kernel`. Never adapters, evaluators or
governance authority: an episode **terminates**, it does not grade itself
(`VG-03 §6.1`, `ICD §3`).
"""

from .provenance import (
    CACHE,
    CAPTURE_INCOMPLETE,
    COMPACTION,
    CONTEXT_SELECTION,
    MODEL_IO,
    EvidenceCaptureRequiredError,
    NullProvenanceSink,
    ProvenanceRecord,
    ProvenanceSink,
)
from .episode import (
    Episode,
    EpisodeEngine,
    EpisodeOutcome,
    Proposal,
    ProposalKind,
    ProposalMalformed,
    RunTermination,
    Turn,
)

__all__ = [
    "CACHE",
    "CAPTURE_INCOMPLETE",
    "COMPACTION",
    "CONTEXT_SELECTION",
    "MODEL_IO",
    "Episode",
    "EpisodeEngine",
    "EpisodeOutcome",
    "Proposal",
    "ProposalKind",
    "ProposalMalformed",
    "EvidenceCaptureRequiredError",
    "NullProvenanceSink",
    "ProvenanceRecord",
    "ProvenanceSink",
    "RunTermination",
    "Turn",
]
