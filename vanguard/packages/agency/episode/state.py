"""Episode values and the reduction over them (`VG-03 §6`).

Values and one pure reduction. Every decision that carries authority lives in
the kernel; nothing here authorises anything, and nothing here evaluates the
episode — run termination and evaluation outcome are **separate axes**
(`VG-03 §6.2`), and only the first of the two exists in this package.

`CT-03`: a proposal arriving from a model provider is *parsed* here, never
cast. A malformed proposal is an instrument problem, not a task verdict.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any, Mapping, Sequence

from ...domain.canonicalisation.digest import digest_of

__all__ = [
    "Episode",
    "Proposal",
    "ProposalKind",
    "ProposalMalformed",
    "RunTermination",
    "SpawnResult",
    "Turn",
]


class RunTermination(str, Enum):
    """`VG-03 §6.2`, run-termination axis only.

    Collapsing this with the evaluation outcome is how instrument failure
    silently becomes task failure, so the evaluation axis is deliberately
    absent from `agency/`: the Evidence plane owns it (`ICD §3`).
    """

    COMPLETED = "completed"
    ABSTAINED = "abstained"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"
    BUDGET_EXHAUSTED = "budget_exhausted"
    INSTRUMENT_ERROR = "instrument_error"
    RUNTIME_ERROR = "runtime_error"
    ABANDONED = "abandoned"


@dataclass(frozen=True, slots=True)
class SpawnResult:
    """The structured, value-only outcome of spawning a child episode (S8-B-01).

    Never carries a mutable engine handle or shared mutable state.
    """

    ok: bool
    payload: Any = None
    terminal: RunTermination = RunTermination.COMPLETED
    detail: str = ""
    turns: int = 0


class ProposalKind(str, Enum):
    """What the operator asked for this turn."""

    EFFECT = "effect"
    FINISH = "finish"
    ABSTAIN = "abstain"
    ESCALATE = "escalate"
    SPAWN = "spawn"


#: Terminals a non-effect proposal reduces to directly (`VG-03 §6.1`).
TERMINAL_FOR_KIND: Mapping[ProposalKind, RunTermination] = {
    ProposalKind.FINISH: RunTermination.COMPLETED,
    ProposalKind.ABSTAIN: RunTermination.ABSTAINED,
    ProposalKind.ESCALATE: RunTermination.ESCALATED,
}


class ProposalMalformed(ValueError):
    """A provider returned something that is not a proposal (`CT-03`)."""


@dataclass(frozen=True, slots=True)
class Proposal:
    """A parsed operator proposal. It carries no authority of its own."""

    kind: ProposalKind
    action: str | None = None
    resource: Mapping[str, Any] = field(default_factory=dict)
    args: Mapping[str, Any] = field(default_factory=dict)
    reservation: Mapping[str, int] = field(default_factory=dict)
    note: str = ""

    @property
    def descriptor(self) -> str:
        """A stable digest of the proposal, for no-progress detection."""
        return digest_of({
            "kind": self.kind.value,
            "action": self.action,
            "resource": dict(self.resource),
            "args": dict(self.args),
        })


def parse_proposal(value: Any) -> Proposal:
    """Parse a provider payload into a `Proposal` or raise `ProposalMalformed`.

    The kernel re-parses the resulting request at S1 regardless (`05 §2`); this
    parse exists so a malformed payload terminates the run as an *instrument*
    error rather than arriving at the kernel as a cast.
    """
    if not isinstance(value, Mapping):
        raise ProposalMalformed(f"proposal is {type(value).__name__}, not an object")
    raw_kind = value.get("kind")
    try:
        kind = ProposalKind(raw_kind)
    except ValueError as exc:
        raise ProposalMalformed(f"unknown proposal kind {raw_kind!r}") from exc

    if kind == ProposalKind.SPAWN:
        args = value.get("args", {})
        if args is None:
            args = {}
        if not isinstance(args, Mapping):
            raise ProposalMalformed("args must be an object")
        return Proposal(
            kind=kind,
            action=str(value.get("action") or "spawn"),
            args=dict(args),
            note=str(value.get("note", "")),
        )

    if kind is not ProposalKind.EFFECT:
        return Proposal(kind=kind, note=str(value.get("note", "")))

    action = value.get("action")
    if not isinstance(action, str) or not action:
        raise ProposalMalformed("an effect proposal requires a non-empty action")
    resource = value.get("resource", {})
    args = value.get("args", {})
    reservation = value.get("reservation", {})
    if reservation is None:
        reservation = {}
    for name, member in (("resource", resource), ("args", args), ("reservation", reservation)):
        if not isinstance(member, Mapping):
            raise ProposalMalformed(f"{name} must be an object")
    for dimension, amount in reservation.items():
        if not isinstance(amount, int) or isinstance(amount, bool) or amount < 0:
            raise ProposalMalformed(
                f"reservation.{dimension} must be a non-negative integer (CT-06)")
    return Proposal(
        kind=kind,
        action=action,
        resource=dict(resource),
        args=dict(args),
        reservation={str(k): int(v) for k, v in reservation.items()},
        note=str(value.get("note", "")),
    )


@dataclass(frozen=True, slots=True)
class Turn:
    """One completed turn, as the no-progress tuple of `VG-03 §6.4`."""

    index: int
    state_digest: str
    proposal_descriptor: str
    receipt_digest: str | None
    progress_signal: str

    @property
    def signature(self) -> tuple[str, str, str | None, str]:
        return (self.state_digest, self.proposal_descriptor,
                self.receipt_digest, self.progress_signal)


@dataclass(frozen=True, slots=True)
class Episode:
    """Immutable episode state. Recursion: an episode may spawn child episodes under attenuated scope (S8-B-01)."""

    episode_id: str
    run_id: str
    principal: str
    brief: str = ""
    depth: int = 1
    turns: tuple[Turn, ...] = ()
    terminal: RunTermination | None = None
    detail: str = ""

    @property
    def is_terminal(self) -> bool:
        return self.terminal is not None

    @property
    def turn_count(self) -> int:
        return len(self.turns)

    def state_digest(self) -> str:
        """Digest of everything a turn is allowed to observe."""
        return digest_of({
            "episodeId": self.episode_id,
            "runId": self.run_id,
            "brief": self.brief,
            "turns": [
                {"index": turn.index,
                 "proposalDescriptor": turn.proposal_descriptor,
                 "receiptDigest": turn.receipt_digest,
                 "progressSignal": turn.progress_signal}
                for turn in self.turns
            ],
        })

    # -- reduction ------------------------------------------------------

    def with_turn(self, turn: Turn) -> Episode:
        return replace(self, turns=self.turns + (turn,))

    def terminated(self, terminal: RunTermination, detail: str = "") -> Episode:
        """`K`-style single exit: a terminated episode never reduces again."""
        if self.terminal is not None:
            return self
        return replace(self, terminal=terminal, detail=detail)

    def repeats(self, turn: Turn, *, limit: int) -> bool:
        """`VG-03 §6.4`: identical transitions without a change in state or
        progress signal, for a configured limit. Identical consecutive
        descriptors alone are not evidence of a livelock — re-running tests or
        polling a queue can be exactly correct.
        """
        if limit <= 0:
            return False
        recent: Sequence[Turn] = self.turns[-(limit - 1):] if limit > 1 else ()
        return len(recent) == limit - 1 and all(
            other.signature == turn.signature for other in recent)
