"""Effect-boundary distillation: cap tool bodies and bind the full artifact.

Two shapes of oversized output arrive here and they are not the same fact.

* An ordinary tool body is *material*: capping it costs detail, and the
  artifact digest is how the operator gets the rest back.
* A verification body is *proof*. `NT-C04` permits the raw log to be omitted,
  and `NT-C05` requires what the log attested — which command ran, in which
  environment, against which subject, how many tests were collected and
  executed, with which exit status and how fresh — to survive that omission.
  A receipt that kept only "the suite ran" would let a stale green authorise a
  finish, which is the exact failure the identity fields exist to prevent.

The receipt is a value: it reads no clock, opens no file and verifies nothing
itself. It restates identity that a verification tool already produced.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping

from ...domain.canonicalisation.digest import digest_of
from .layers import estimate_tokens

__all__ = [
    "TOOL_BODY_CHAR_CAP",
    "VERIFICATION_FIELD_CHARS",
    "DistilledResult",
    "VerificationReceipt",
    "distill_tool_output",
    "verification_receipt_from",
]

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


#: Each identity field is a short token, not a transcript. A receipt whose
#: fields were unbounded would reintroduce the body it replaced.
VERIFICATION_FIELD_CHARS = 160

#: Accepted spellings per identity field. Verification payloads are produced
#: by several toolkits and by replayed fixtures; a receipt that only read one
#: spelling would silently degrade to "no verification identity" exactly when
#: a different runner produced the evidence.
_COMMAND_KEYS = ("command", "argv", "commandLine", "command_line")
_ENVIRONMENT_KEYS = ("environment", "environmentIdentity", "environment_identity", "env")
_COLLECTED_KEYS = ("collected", "collectedCount", "collected_count", "total")
_EXECUTED_KEYS = ("executed", "executedCount", "executed_count", "ran", "run")
_EXIT_KEYS = ("exit_status", "exitStatus", "exit", "exit_code", "exitCode", "returncode")
_FRESHNESS_KEYS = ("freshness", "fresh")


def _clip(value: str) -> str:
    text = " ".join(str(value).split())
    if len(text) <= VERIFICATION_FIELD_CHARS:
        return text
    return text[: VERIFICATION_FIELD_CHARS - 3] + "..."


def _first(raw: Mapping[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in raw:
            return raw[key]
    return None


def _number(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _count(value: Any) -> int | None:
    """A cardinality. A negative one is a malformed report, not a count."""
    number = _number(value)
    return number if number is not None and number >= 0 else None


@dataclass(frozen=True, slots=True)
class VerificationReceipt:
    """What a verification attested, once its raw output is gone (`NT-C05`).

    Every field is identity. There is deliberately no verdict field beyond the
    exit status the runner itself reported: a receipt that carried a derived
    "passed" flag would be a second, weaker oracle.
    """

    command: str
    environment: str
    subject: str
    artifact: str
    collected: int | None
    executed: int | None
    exit_status: int | None
    freshness: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "command": self.command,
            "environment": self.environment,
            "subject": self.subject,
            "artifact": self.artifact,
            "collected": self.collected,
            "executed": self.executed,
            "exitStatus": self.exit_status,
            "freshness": self.freshness,
        }

    def render(self) -> str:
        """One bounded line. The body it replaced is reachable by artifact."""
        def number(value: int | None) -> str:
            return "unknown" if value is None else str(value)

        return (
            f"[verification command={self.command} "
            f"environment={self.environment} subject={self.subject} "
            f"collected={number(self.collected)} executed={number(self.executed)} "
            f"exit={number(self.exit_status)} freshness={self.freshness} "
            f"artifact={self.artifact}]"
        )


def verification_receipt_from(
    payload: Any,
    *,
    subject: str,
    artifact: str,
    fresh: bool,
) -> VerificationReceipt | None:
    """Read a verification identity out of a tool body, or report there is none.

    Returns `None` rather than an empty receipt when the payload is not a
    verification result: inventing identity fields for an ordinary tool body
    would be a fabricated receipt, which is worse than no receipt.
    """
    raw: Any = payload
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8", "replace")
    if isinstance(raw, str):
        text = raw.strip()
        if not text.startswith("{"):
            return None
        try:
            raw = json.loads(text)
        except ValueError:
            return None
    if not isinstance(raw, Mapping):
        return None

    command = _first(raw, _COMMAND_KEYS)
    if command is None:
        return None
    if isinstance(command, (list, tuple)):
        command = " ".join(str(part) for part in command)
    elif not isinstance(command, str):
        return None
    if not str(command).strip():
        return None

    environment = _first(raw, _ENVIRONMENT_KEYS)
    declared = _first(raw, _FRESHNESS_KEYS)
    if isinstance(declared, bool):
        freshness = "fresh" if declared else "stale"
    elif isinstance(declared, str) and declared.strip():
        freshness = _clip(declared)
    else:
        freshness = "fresh" if fresh else "stale"

    return VerificationReceipt(
        command=_clip(command),
        environment=_clip(environment) if environment is not None else "unknown",
        subject=subject,
        artifact=artifact,
        collected=_count(_first(raw, _COLLECTED_KEYS)),
        executed=_count(_first(raw, _EXECUTED_KEYS)),
        # An exit status may be negative: a runner killed by a signal
        # reports one, and that is precisely the case a receipt must keep.
        exit_status=_number(_first(raw, _EXIT_KEYS)),
        freshness=freshness,
    )
