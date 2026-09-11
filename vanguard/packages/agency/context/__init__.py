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
    CapabilityPrefixExceeded,
    CompetencePriorRecorder,
    ContextBudgetExceeded,
    ContextCompiler,
)
from .distiller import (
    VerificationReceipt,
    distill_tool_output,
    verification_receipt_from,
)
from .packet import (
    INDEX_PORT_UNBOUND,
    ContextPacket,
    ContextPacketError,
    SectionAddress,
    build_context_packet,
    validate_completion_epoch,
    validate_completion_omissions,
    validate_resume_identity,
)
from .layers import (
    BREAKPOINT_LAYERS,
    CAPABILITY_PREFIX_CEILING,
    LAYER_ORDER,
    NEWEST_INTERACTION_SOURCE,
    PINNED_L5_SOURCES,
    PREFIX_LAYERS,
    ROLE_FOR_LAYER,
    Block,
    CompiledContext,
    ContextBudget,
    Fragment,
    Interaction,
    Layer,
    estimate_tokens,
)

__all__ = [
    "BREAKPOINT_LAYERS",
    "CAPABILITY_PREFIX_CEILING",
    "Block",
    "CacheBreakpointCeilingExceeded",
    "CapabilityPrefixExceeded",
    "CompetencePriorRecorder",
    "CompiledContext",
    "ContextBudgetExceeded",
    "ContextBudget",
    "ContextCompiler",
    "ContextPacket", "ContextPacketError", "SectionAddress",
    "INDEX_PORT_UNBOUND",
    "build_context_packet", "validate_completion_epoch", "validate_completion_omissions",
    "validate_resume_identity",
    "Fragment",
    "Interaction",
    "LAYER_ORDER",
    "Layer",
    "NEWEST_INTERACTION_SOURCE",
    "PINNED_L5_SOURCES",
    "PREFIX_LAYERS",
    "ROLE_FOR_LAYER",
    "VerificationReceipt",
    "distill_tool_output",
    "estimate_tokens",
    "verification_receipt_from",
]
