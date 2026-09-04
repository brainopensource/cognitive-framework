"""Effect-boundary distillation: cap tool bodies and bind the full artifact."""

from __future__ import annotations

from dataclasses import dataclass

from ...domain.canonicalisation.digest import digest_of
from .layers import estimate_tokens

__all__ = ["TOOL_BODY_CHAR_CAP", "DistilledResult", "distill_tool_output"]

#: Compact tool bodies stay in the ~1–2k character band (v2 §3.3 / WRN-02).
TOOL_BODY_CHAR_CAP = 2000
_HEAD_CHARS = 1500
_TAIL_CHARS = 400


@dataclass(frozen=True, slots=True)
class DistilledResult:
    compact_text: str
    full_artifact_digest: str
    tokens_saved: int
    truncated: bool = False


def distill_tool_output(payload: str, *, cap_chars: int = TOOL_BODY_CHAR_CAP) -> DistilledResult:
    """Cap a tool body and bind the full preimage. Not a second engine."""
    digest = digest_of({"toolOutput": payload})
    if len(payload) <= cap_chars:
        return DistilledResult(
            compact_text=payload,
            full_artifact_digest=digest,
            tokens_saved=0,
            truncated=False,
        )
    head = max(1, min(_HEAD_CHARS, cap_chars * 3 // 4))
    tail = max(0, min(_TAIL_CHARS, cap_chars - head))
    marker = f"\n...[truncated digest={digest} chars={len(payload)}]...\n"
    compact = payload[:head] + marker + (payload[-tail:] if tail else "")
    saved = max(0, estimate_tokens(payload) - estimate_tokens(compact))
    return DistilledResult(
        compact_text=compact,
        full_artifact_digest=digest,
        tokens_saved=saved,
        truncated=True,
    )
