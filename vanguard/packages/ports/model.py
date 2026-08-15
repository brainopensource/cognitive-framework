"""ModelPort interface.

Owning contract: ICD §4 ModelProvider, REQ-PORT-002, CT-33.
Invariants:
- Ports accept and return domain/schema types only.
- Provider failures are typed `instrument_error` values, never task failures.
- Zero concrete implementation in this package.
"""

from __future__ import annotations

from typing import Any, Mapping, Protocol, Sequence

from .event_store import Result

__all__ = [
    "ContextBundle",
    "ToolSchemas",
    "Sampling",
    "Proposal",
    "ModelPort",
]

ContextBundle = Mapping[str, Any]
ToolSchemas = Sequence[Mapping[str, Any]]
Sampling = Mapping[str, Any]
Proposal = Mapping[str, Any]


class ModelPort(Protocol):
    """Inference seam. Cassette/fake in Sprint 3; live provider is REQ-PORT-006."""

    def propose(
        self,
        context: ContextBundle,
        tools: ToolSchemas,
        sampling: Sampling,
    ) -> Result[Proposal]:
        """Return a proposal, or a typed instrument error.

        Rate limits, timeouts, cassette exhaustion and malformed provider
        replies are `instrument_error`. They are not task failures.
        """
        ...
