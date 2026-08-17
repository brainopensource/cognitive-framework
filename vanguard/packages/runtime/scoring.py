"""Score a coding arm from the ledger projection, and nothing else (`W15-A`).

`REQ-TRUST-001`. Every field here is reduced from events the run already
emitted -- turns, verbs, denials, cache-miss attribution, compactions, dead
ends, termination. Nothing is recomputed from a second source, because two
accounts of one run eventually disagree and the disagreement is discovered
after the number has been quoted.

**The denominator holds absent tasks.** A workspace that was not on disk is
`inconclusive:workspace_missing` and stays counted. Dropping it reports a rate
over whatever happened to be present, which is the failure the retraction sweep
existed to remove.

This module scores; it never runs, never judges an artifact with a model, and
never touches a workspace.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .repair import StopReason
from .session_log import SessionLog

__all__ = ["ArmScore", "score_arm", "score_session"]

#: Outcomes that mean "no measurement", not "a failed attempt".
INCONCLUSIVE_PREFIX = "inconclusive:"


@dataclass(frozen=True, slots=True)
class ArmScore:
    """One arm's numbers, all ledger-derived."""

    label: str
    resolved: int = 0
    attempted: int = 0
    inconclusive: tuple[str, ...] = ()
    turns: int = 0
    denials: int = 0
    dead_ends: int = 0
    compact_count: int = 0
    cache_misses: int = 0
    terminations: Mapping[str, int] = None  # type: ignore[assignment]

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "resolved": self.resolved,
            "attempted": self.attempted,
            "inconclusive": list(self.inconclusive),
            "turns": self.turns,
            "denials": self.denials,
            "deadEnds": self.dead_ends,
            "compactCount": self.compact_count,
            "cacheMisses": self.cache_misses,
            "terminations": dict(self.terminations or {}),
        }

    @property
    def denominator(self) -> int:
        """Every task attempted, inconclusive ones included."""
        return self.attempted

    def rate_text(self) -> str:
        """A rate is never a bare number: it names its denominator.

        `resolved/attempted` printed alone invites the reader to assume the
        denominator was the tasks that could run. It was not.
        """
        return (f"{self.resolved}/{self.attempted} resolved"
                f" ({len(self.inconclusive)} inconclusive, still counted)")


def score_session(log: SessionLog) -> Mapping[str, int]:
    """Per-run counts from the session-log projection."""
    return {
        "turns": len(log.entries),
        "denials": len(log.dead_ends),
        "deadEnds": len(log.dead_end_details),
        "compactCount": sum(1 for entry in log.entries if entry.compacted),
        "cacheMisses": len(log.cache_miss_attribution()),
    }


def score_arm(label: str, task_reports: Sequence[Mapping[str, Any]]) -> ArmScore:
    """Fold per-task reports into one arm score.

    `task_reports` are the driver's own output, so scoring adds no third
    representation of a run.
    """

    resolved = 0
    inconclusive: list[str] = []
    turns = denials = dead_ends = compacts = misses = 0
    terminations: dict[str, int] = {}

    for report in task_reports:
        outcome = str(report.get("outcome", ""))
        terminations[outcome] = terminations.get(outcome, 0) + 1
        if outcome == StopReason.ORACLE_GREEN:
            resolved += 1
        if (outcome.startswith(INCONCLUSIVE_PREFIX)
                or outcome.startswith(StopReason.INSTRUMENT_ERROR)):
            inconclusive.append(str(report.get("taskId") or report.get("task_id") or "unnamed"))

        turns += int(report.get("turns", 0) or 0)
        session = report.get("session") or ()
        compacts += sum(1 for entry in session if entry.get("compacted"))
        dead = report.get("deadEnds") or report.get("dead_ends") or ()
        dead_ends += len(dead)
        denials += len(dead)
        misses += len(report.get("cacheMissAttribution")
                      or report.get("cache_misses") or ())

    return ArmScore(
        label=label,
        resolved=resolved,
        attempted=len(task_reports),
        inconclusive=tuple(inconclusive),
        turns=turns,
        denials=denials,
        dead_ends=dead_ends,
        compact_count=compacts,
        cache_misses=misses,
        terminations=terminations,
    )
