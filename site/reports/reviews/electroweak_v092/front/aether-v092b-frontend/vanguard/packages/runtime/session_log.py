"""The session log is a projection of the ledger (`W11-A`, `A-07`).

Everything a human or a report needs to see about a run -- which turn, which
verb, what came back, whether the context was compacted, whether the provider
cache missed, what it cost -- is already an event. Writing it a second time into
its own table is how a system ends up with two irreconcilable accounts of one
run, which is exactly what `runtime/coordination.py` was deleted for in
`S7-A-05`.

So there is **no second store here**. This reduces envelopes the ledger already
holds. If a field is not on the ledger it does not appear in the log, and that
absence is a finding about the ledger rather than something to paper over.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

__all__ = ["SessionLog", "SessionLogEntry", "session_log"]

#: Payload kinds that open a turn, in ledger order.
_TURN_KINDS = ("ProposalProduced",)
#: Payload kinds that close one, carrying what actually happened.
_RECEIPT_KINDS = ("EffectCompleted", "EffectRejected", "AuthorizationDenied",
                  "ApprovalRequested", "EffectFailed")


@dataclass(frozen=True, slots=True)
class SessionLogEntry:
    """One turn, as the ledger recorded it."""

    turn: int
    verb: str | None = None
    receipt: str | None = None
    compacted: bool = False
    cache_miss: bool | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "turn": self.turn,
            "verb": self.verb,
            "receipt": self.receipt,
            "compacted": self.compacted,
            "cacheMiss": self.cache_miss,
            "promptTokens": self.prompt_tokens,
            "completionTokens": self.completion_tokens,
            "detail": self.detail,
        }


@dataclass(frozen=True, slots=True)
class SessionLog:
    entries: tuple[SessionLogEntry, ...] = ()
    #: `C-01`. Why the episode ended when it ended without a turn. `None` on a
    #: run that produced turns normally. An episode that refused the model's
    #: first answer used to leave nothing behind at all.
    terminal_refusal: Mapping[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        rendered: dict[str, Any] = {
            "turns": [entry.to_dict() for entry in self.entries]}
        if self.terminal_refusal is not None:
            rendered["terminalRefusal"] = dict(self.terminal_refusal)
        return rendered

    @property
    def dead_end_details(self) -> tuple[Mapping[str, Any], ...]:
        """Refused turns with their verb and reason (`W12-A`).

        The next attempt should be told what has already been refused rather
        than rediscovering it, and a report should distinguish a run that
        explored badly from one that was refused repeatedly.
        """
        return tuple({"turn": e.turn, "verb": e.verb, "reason": e.detail}
                     for e in self.entries
                     if e.receipt in {"EffectRejected", "AuthorizationDenied"})

    @property
    def dead_ends(self) -> tuple[int, ...]:
        """Turns whose effect was refused. `W12-A`: a refusal is a dead end.

        Recorded so the next attempt can be told what has already failed
        instead of rediscovering it, and so a report can distinguish a run that
        explored badly from one that was refused repeatedly.
        """
        return tuple(e.turn for e in self.entries
                     if e.receipt in {"EffectRejected", "AuthorizationDenied"})

    @property
    def cache_misses(self) -> tuple[int, ...]:
        return tuple(e.turn for e in self.entries if e.cache_miss)

    def cache_miss_attribution(self) -> tuple[Mapping[str, Any], ...]:
        """Why the prefix stopped matching, per missed turn (`W12-A`).

        A cache-miss count is a number nobody can act on. What a pack author
        needs is *which turn* missed and *what changed on it* -- a compaction
        rewrote the prefix, or the turn before it was refused and the dialogue
        diverged. Attribution is derived from the log, so it cannot disagree
        with the turns it explains.
        """
        attribution: list[Mapping[str, Any]] = []
        for index, entry in enumerate(self.entries):
            if not entry.cache_miss:
                continue
            previous = self.entries[index - 1] if index else None
            if entry.compacted:
                cause = "compaction_rewrote_the_prefix"
            elif previous is not None and previous.receipt in {
                    "EffectRejected", "AuthorizationDenied"}:
                cause = "prior_turn_refused"
            elif index == 0:
                cause = "cold_prefix"
            else:
                cause = "unattributed"
            attribution.append({
                "turn": entry.turn,
                "cause": cause,
                "verb": entry.verb,
            })
        return tuple(attribution)


def _payload(event: Any) -> Mapping[str, Any]:
    payload = getattr(event, "payload", None)
    return payload if isinstance(payload, Mapping) else {}


def _kind(event: Any, payload: Mapping[str, Any]) -> str:
    """The event kind, wherever this producer puts it.

    Kernel `Event` carries `kind` as an attribute and leaves it out of the
    payload; ledger envelopes carry it inside. Reading only one shape is how
    this projection silently returned an empty log for every real run while
    passing against synthetic events built the way it expected.
    """
    attribute = getattr(event, "kind", None)
    if isinstance(attribute, str) and attribute:
        return attribute
    return str(payload.get("kind", ""))


def _verb(payload: Mapping[str, Any]) -> str | None:
    """The verb a proposal names, in either wire shape."""
    action = payload.get("action")
    if isinstance(action, str) and action:
        return action
    calls = payload.get("toolCalls")
    if isinstance(calls, Sequence) and calls and isinstance(calls[0], Mapping):
        candidate = calls[0].get("action") or calls[0].get("name")
        if isinstance(candidate, str):
            return candidate
    return None


def _int_or_none(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def session_log(events: Iterable[Any]) -> SessionLog:
    """Reduce ledger envelopes into a per-turn log. Pure; no store, no clock."""

    entries: list[SessionLogEntry] = []
    turn = 0
    open_entry: dict[str, Any] | None = None
    refusal: Mapping[str, Any] | None = None

    def flush() -> None:
        nonlocal open_entry
        if open_entry is not None:
            entries.append(SessionLogEntry(**open_entry))
            open_entry = None

    for event in events:
        payload = _payload(event)
        kind = _kind(event, payload)

        if kind in _TURN_KINDS:
            flush()
            turn += 1
            open_entry = {
                "turn": turn,
                "verb": _verb(payload),
                "compacted": bool(payload.get("compacted", False)),
                "cache_miss": (None if "cacheMiss" not in payload
                               else bool(payload.get("cacheMiss"))),
                "prompt_tokens": _int_or_none(payload.get("promptTokens")),
                "completion_tokens": _int_or_none(payload.get("completionTokens")),
            }
            continue

        if kind in _RECEIPT_KINDS and open_entry is not None:
            open_entry["receipt"] = kind
            # Producers disagree about where the reason lives: kernel events
            # put it on the event, envelopes in the payload. A blank reason on
            # a refusal is a refusal nobody can act on.
            reason = (payload.get("reason") or payload.get("detail")
                      or getattr(event, "reason", None))
            if isinstance(reason, str) and reason:
                open_entry["detail"] = reason
            if open_entry.get("verb") is None:
                open_entry["verb"] = _verb(payload)
            continue

        if kind == "ContextCompacted" and open_entry is not None:
            open_entry["compacted"] = True

        if kind == "EpisodeCompleted":
            outcome = str(payload.get("outcome", ""))
            reason = str(payload.get("detail", "") or "")
            if outcome and outcome != "resolved":
                refusal = {"outcome": outcome, "detail": reason,
                           "afterTurn": len(entries) + (1 if open_entry else 0)}

    flush()
    return SessionLog(entries=tuple(entries), terminal_refusal=refusal)
