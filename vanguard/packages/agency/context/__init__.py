"""Context assembly: the L1–L5 prefix-stable compiler (`REQ-CTX-001`).

`VG-03 §10` — the actual quality bottleneck and the largest cost lever in the
system. Two exports carry the requirement: `ContextCompiler` assembles the
layered, token-budgeted, provenance-tagged prompt vector, and
`CompetencePriorRecorder` puts the pre-action prior on the ledger before turn 1.

Nothing here holds authority, evaluates anything, or knows what domain the task
belongs to (`M11`): a coding harness and a research harness differ only in the
strings handed to the constructor.
"""

from .compiler import (
    CacheBreakpointCeilingExceeded,
    CompetencePriorRecorder,
    ContextBudgetExceeded,
    ContextCompiler,
)
from .packet import (
    ContextPacket,
    ContextPacketError,
    SectionAddress,
    build_context_packet,
    validate_completion_epoch,
    validate_resume_identity,
)
from .layers import (
    BREAKPOINT_LAYERS,
    LAYER_ORDER,
    PREFIX_LAYERS,
    ROLE_FOR_LAYER,
    Block,
    CompiledContext,
    Fragment,
    Layer,
    estimate_tokens,
)

__all__ = [
    "BREAKPOINT_LAYERS",
    "Block",
    "CacheBreakpointCeilingExceeded",
    "CompetencePriorRecorder",
    "CompiledContext",
    "ContextBudgetExceeded",
    "ContextCompiler",
    "ContextPacket", "ContextPacketError", "SectionAddress",
    "build_context_packet", "validate_completion_epoch", "validate_resume_identity",
    "Fragment",
    "LAYER_ORDER",
    "Layer",
    "PREFIX_LAYERS",
    "ROLE_FOR_LAYER",
    "estimate_tokens",
]
