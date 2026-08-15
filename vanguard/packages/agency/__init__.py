"""Episode coordination (`ICD §2`, `VG-03 §6`).

May import `domain`, `ports` and `kernel`. Never adapters, evaluators or
governance authority: an episode **terminates**, it does not grade itself
(`VG-03 §6.1`, `ICD §3`).
"""

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
    "Episode",
    "EpisodeEngine",
    "EpisodeOutcome",
    "Proposal",
    "ProposalKind",
    "ProposalMalformed",
    "RunTermination",
    "Turn",
]
