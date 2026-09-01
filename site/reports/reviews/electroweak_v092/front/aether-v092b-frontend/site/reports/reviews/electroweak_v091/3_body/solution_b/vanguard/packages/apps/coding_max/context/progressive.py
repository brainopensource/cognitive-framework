"""Progressive context with mutation operations (`spec §12`).

`spec §12` forbids loading everything up front. The model starts with a
minimal working set, states what it is missing, and the harness retrieves
exactly that. This object owns the working set and the six mutation verbs.

One invariant matters above the rest: mid-run additions go to the DIALOGUE
layer, never into the prefix. The substrate's `ContextCompiler` caches the
SYSTEM/TOOLS/ENVIRONMENT prefix and breaks that cache if it changes, so a
retrieval that rewrote the prefix would silently multiply the token cost of
every remaining turn.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Mapping, Sequence

from ....domain.canonicalisation.digest import digest_of
from .scoring import Candidate, ScoreBreakdown, score_candidates

__all__ = ["ContextEntry", "ProgressiveContext"]


@dataclass(frozen=True, slots=True)
class ContextEntry:
    key: str
    label: str
    text: str
    source: str
    pinned: bool = False
    epoch: int = 0
    score: float = 0.0

    @property
    def token_estimate(self) -> int:
        return max(1, len(self.text) // 4)

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key, "label": self.label, "source": self.source,
            "pinned": self.pinned, "epoch": self.epoch,
            "tokens": self.token_estimate, "score": round(self.score, 4),
        }


class ProgressiveContext:
    """The working set. `epoch` increments on every mutation.

    The epoch is not decoration: `runtime/meta_controller.py::validate_confidence`
    refuses a confidence record whose `contextEpoch` does not match the current
    view, so a stale signal cannot drive a directive. Every mutation here must
    therefore be visible as an epoch bump.
    """

    def __init__(self, *, token_budget: int = 120_000) -> None:
        self._entries: dict[str, ContextEntry] = {}
        self._budget = token_budget
        self._epoch = 0
        self._dropped: list[str] = []
        self._history: list[Mapping[str, Any]] = []

    # -- introspection ---------------------------------------------------

    @property
    def epoch(self) -> int:
        return self._epoch

    @property
    def token_budget(self) -> int:
        return self._budget

    def total_tokens(self) -> int:
        return sum(entry.token_estimate for entry in self._entries.values())

    def entries(self) -> tuple[ContextEntry, ...]:
        return tuple(sorted(
            self._entries.values(),
            key=lambda e: (e.pinned, e.score), reverse=True,
        ))

    def paths(self) -> tuple[str, ...]:
        return tuple(entry.key for entry in self._entries.values())

    def digest(self) -> str:
        return digest_of({
            "epoch": self._epoch,
            "entries": [e.to_dict() for e in self.entries()],
        })

    def history(self) -> tuple[Mapping[str, Any], ...]:
        return tuple(self._history)

    # -- mutation verbs (`spec §12`) -------------------------------------

    def add(self, key: str, text: str, *, label: str = "", source: str = "",
            score: float = 0.0, pinned: bool = False) -> bool:
        """Admit one entry. Returns False if it was already present unchanged."""
        existing = self._entries.get(key)
        if existing is not None and existing.text == text:
            return False
        self._entries[key] = ContextEntry(
            key=key, label=label or key, text=text, source=source,
            pinned=pinned, epoch=self._epoch + 1, score=score,
        )
        self._bump("add", {"key": key, "tokens": max(1, len(text) // 4)})
        self._evict_if_needed()
        return True

    def drop(self, key: str) -> bool:
        entry = self._entries.get(key)
        if entry is None or entry.pinned:
            return False
        del self._entries[key]
        self._dropped.append(key)
        self._bump("drop", {"key": key})
        return True

    def pin(self, key: str) -> bool:
        """Protect an entry from eviction and compression."""
        entry = self._entries.get(key)
        if entry is None or entry.pinned:
            return False
        self._entries[key] = replace(entry, pinned=True, epoch=self._epoch + 1)
        self._bump("pin", {"key": key})
        return True

    def compress(self, key: str, summary: str) -> bool:
        """Replace a body with a summary, keeping the key reachable.

        Compression is lossy and irreversible within a run, so it never
        touches a pinned entry and never shrinks something already small --
        a summary of forty tokens costs more than it saves.
        """
        entry = self._entries.get(key)
        if entry is None or entry.pinned or entry.token_estimate < 200:
            return False
        self._entries[key] = replace(
            entry, text=summary, epoch=self._epoch + 1,
            label=f"{entry.label} (compressed)",
        )
        self._bump("compress", {"key": key})
        return True

    def refresh(self, key: str, text: str) -> bool:
        """Re-read an entry whose underlying file changed."""
        entry = self._entries.get(key)
        if entry is None:
            return False
        if entry.text == text:
            return False
        self._entries[key] = replace(entry, text=text, epoch=self._epoch + 1)
        self._bump("refresh", {"key": key})
        return True

    def replace_all(self, entries: Sequence[ContextEntry]) -> None:
        """Wholesale swap, preserving pins. Used on strategy change."""
        pinned = {k: v for k, v in self._entries.items() if v.pinned}
        self._entries = dict(pinned)
        for entry in entries:
            self._entries.setdefault(entry.key, entry)
        self._bump("replace", {"count": len(entries)})

    # -- retrieval -------------------------------------------------------

    def admit_ranked(
        self,
        candidates: Sequence[Candidate],
        *,
        task: str = "",
        limit: int = 12,
        **signals: Any,
    ) -> tuple[str, ...]:
        """Score candidates and admit the best that fit the budget.

        Candidates already in the working set are skipped rather than
        re-scored: re-admitting an entry would reset its epoch and make every
        outstanding confidence record stale for no informational gain.
        """
        ranked = score_candidates(candidates, task=task, **signals)
        admitted: list[str] = []
        for candidate, breakdown in ranked:
            if len(admitted) >= limit:
                break
            if candidate.path in self._entries:
                continue
            if self.total_tokens() + candidate.token_estimate > self._budget:
                continue
            if self.add(candidate.path, candidate.text,
                        source=candidate.provider, score=breakdown.total,
                        pinned=candidate.pinned):
                admitted.append(candidate.path)
        return tuple(admitted)

    def needs_update(self, *, missing: Sequence[str] = ()) -> bool:
        return bool(missing) or self.total_tokens() > self._budget

    # -- internals -------------------------------------------------------

    def _evict_if_needed(self) -> None:
        """Evict lowest-scoring unpinned entries until inside budget."""
        if self.total_tokens() <= self._budget:
            return
        evictable = sorted(
            (e for e in self._entries.values() if not e.pinned),
            key=lambda e: e.score,
        )
        for entry in evictable:
            if self.total_tokens() <= self._budget:
                break
            del self._entries[entry.key]
            self._dropped.append(entry.key)
            self._history.append({"op": "evict", "key": entry.key, "epoch": self._epoch})

    def _bump(self, operation: str, payload: Mapping[str, Any]) -> None:
        self._epoch += 1
        self._history.append({"op": operation, "epoch": self._epoch, **dict(payload)})
