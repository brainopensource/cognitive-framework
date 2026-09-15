"""A skill index that fits in the frozen prefix (`W12-A`).

Names and one-line descriptions go in the prefix; **bodies do not**. A prefix
that grows with the skill library stops being a prefix: every added skill
invalidates the provider cache for every turn, and the thing that was supposed
to make capability cheap makes every request more expensive.

So the index is budgeted. It carries what an agent needs to *decide it wants*
a skill -- a name and a sentence -- and the body is fetched with the same
`fs.read` the agent already has. Loading bodies eagerly would also mean the
model reads instructions nobody asked for, which is how an unused skill starts
influencing unrelated work.

The budget is enforced, not documented: `build_skill_index` truncates and
reports what it dropped rather than silently exceeding the ceiling.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

from ..domain.artifacts.skill_index import SkillCard
from ..domain.canonicalisation.digest import digest_of

__all__ = [
    "DYNAMIC_SELECTION_POLICY",
    "SkillEntry",
    "SkillIndex",
    "SkillSelection",
    "build_skill_index",
    "select_skills_for_task",
]

#: `W12-A`. Characters, not tokens: the ceiling must be checkable without a
#: tokenizer, and a character bound is conservative against every tokenizer.
DEFAULT_BUDGET_CHARS = 4096


@dataclass(frozen=True, slots=True)
class SkillEntry:
    """One skill, as it appears in the prefix. Body deliberately absent."""

    name: str
    description: str
    path: str

    def render(self) -> str:
        return f"{self.name}: {self.description}"


@dataclass(frozen=True, slots=True)
class SkillIndex:
    entries: tuple[SkillEntry, ...] = ()
    #: Skills that did not fit. Named so a pack author can see the ceiling bite
    #: rather than wondering why a skill is never chosen.
    dropped: tuple[str, ...] = ()
    budget_chars: int = DEFAULT_BUDGET_CHARS

    def render(self) -> str:
        return "\n".join(entry.render() for entry in self.entries)

    @property
    def size_chars(self) -> int:
        return len(self.render())

    def path_of(self, name: str) -> str | None:
        """Where the body lives, for the agent to `fs.read` when it wants it."""
        for entry in self.entries:
            if entry.name == name:
                return entry.path
        return None


def build_skill_index(
    skills: Iterable[Mapping[str, str]],
    *,
    budget_chars: int = DEFAULT_BUDGET_CHARS,
) -> SkillIndex:
    """Fit as many name+description pairs as the budget allows, in order.

    Order is the caller's: a pack that wants a skill preferred puts it first.
    Truncation is by whole entries -- half a description is worse than an
    absent one, because the agent cannot tell it is reading a fragment.
    """

    entries: list[SkillEntry] = []
    dropped: list[str] = []
    used = 0
    for raw in skills:
        name = str(raw.get("name", "")).strip()
        description = " ".join(str(raw.get("description", "")).split())
        path = str(raw.get("path", "")).strip()
        if not name or not path:
            continue
        entry = SkillEntry(name=name, description=description, path=path)
        cost = len(entry.render()) + (1 if entries else 0)
        if used + cost > budget_chars:
            dropped.append(name)
            continue
        entries.append(entry)
        used += cost
    return SkillIndex(entries=tuple(entries), dropped=tuple(dropped),
                      budget_chars=budget_chars)


#: Identity of the selection rule, bound into every selection's provenance so a
#: changed rule produces a different receipt instead of silently reusing one.
DYNAMIC_SELECTION_POLICY = "skill-selection/task-overlap/v1"


@dataclass(frozen=True, slots=True)
class SkillSelection:
    """One task-conditioned selection over the composed skill cards.

    This is an **observation**, not an instruction: it says which skills look
    relevant to this task and where their bodies live. Bodies stay on disk
    behind `fs.read` exactly as they do in the frozen `L3` index, so selecting
    a skill costs a line, not a document.

    `omitted` names whole cards the ceiling excluded. Half a card is worse than
    an absent one, because the agent cannot tell it is reading a fragment.
    """

    selected: tuple[SkillCard, ...] = ()
    omitted: tuple[str, ...] = ()
    budget_chars: int = DEFAULT_BUDGET_CHARS
    query_digest: str = ""
    policy_identity: str = DYNAMIC_SELECTION_POLICY

    _HEADER = "Task-relevant skills (read bodyPath with fs.read when needed):"

    def render(self) -> str:
        if not self.selected:
            return ""
        lines = [self._HEADER]
        lines.extend(card.index_line() for card in self.selected)
        if self.omitted:
            # The ceiling biting is itself an observation. An agent that cannot
            # see the omission cannot tell a skill it never got from a skill
            # that does not exist. The footer reports a *count*: listing every
            # omitted id would grow without bound exactly when the budget is
            # already exhausted.
            lines.append(_omission_footer(len(self.omitted)))
        return "\n".join(lines)

    @property
    def size_chars(self) -> int:
        return len(self.render())

    def digest(self) -> str:
        """Provenance receipt: what was asked, by which rule, with what result."""
        return digest_of({
            "query": self.query_digest,
            "policy": self.policy_identity,
            "selected": [card.skill_id for card in self.selected],
            "omitted": list(self.omitted),
            "budget": self.budget_chars,
        })


def _omission_footer(count: int) -> str:
    return f"(omitted for W12-A ceiling: {count} skill card(s))"


#: Structural English words carry no evidence of relevance. Without this, every
#: brief matches every card through words like "the" and "not", and the
#: selector degenerates into a sort over the whole pack -- which is precisely
#: what it exists to avoid. Deliberately tiny: this is a stopword list, not a
#: language model, and a long one would start making topical judgements.
_STOPWORDS = frozenset({
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "do", "for", "from",
    "has", "have", "in", "into", "is", "it", "its", "not", "of", "on", "or",
    "that", "the", "their", "then", "there", "this", "to", "via", "was", "were",
    "when", "which", "with", "you", "your",
})


def _tokens(text: str) -> set[str]:
    """Alphanumeric word set, lowercased, minus structural words.

    No stemmer and no topical model: a heavier analyzer here would be a second
    ranking authority living in the runtime. The selector only needs to tell
    "mentions this" from "does not".
    """
    folded = "".join(char if char.isalnum() else " " for char in text.lower())
    return {
        part for part in folded.split()
        if len(part) >= 2 and part not in _STOPWORDS
    }


def select_skills_for_task(
    cards: Sequence[SkillCard],
    task_text: str,
    *,
    budget_chars: int = DEFAULT_BUDGET_CHARS,
) -> SkillSelection:
    """Select the composed skill cards this task actually implicates (`W12-A`).

    The stable index of *every* composed card rides the frozen `L3` prefix and
    is not this function's business. This is the dynamic half: a per-task
    observation that belongs in `L5`, because it changes with the brief and a
    prefix that changed with the brief would not be a prefix.

    A card scoring zero is **omitted, not ranked last**. Returning every card in
    relevance order would make two different briefs select the same set, which
    is a sort, not a selection.

    Ties keep composition order, so the selection is a deterministic function of
    (cards, task text, ceiling) and the same brief always yields the same
    receipt.
    """
    if budget_chars < 1:
        raise ValueError("skill selection budget must be positive")
    wanted = _tokens(task_text)
    if not wanted:
        return SkillSelection(budget_chars=budget_chars,
                              query_digest=digest_of({"task": task_text}))

    scored: list[tuple[int, int, SkillCard]] = []
    for position, card in enumerate(cards):
        name_tokens = _tokens(f"{card.skill_id} {card.name}")
        description_tokens = _tokens(card.description)
        # A name match is the stronger signal: a description mentions many
        # things a skill merely touches, a name says what it is.
        score = 3 * len(wanted & name_tokens) + len(wanted & description_tokens)
        if score > 0:
            scored.append((score, position, card))
    scored.sort(key=lambda item: (-item[0], item[1]))

    def _fit(reserve: int) -> tuple[list[SkillCard], list[str]]:
        chosen: list[SkillCard] = []
        dropped: list[str] = []
        used = len(SkillSelection._HEADER) + reserve
        for _score, _position, candidate in scored:
            cost = 1 + len(candidate.index_line())
            if used + cost > budget_chars:
                dropped.append(candidate.skill_id)
                continue
            chosen.append(candidate)
            used += cost
        return chosen, dropped

    # First pass assumes everything fits, so a selection that needs no footer
    # is never charged for one. If the ceiling does bite, refit against the
    # worst-case footer width; the second pass can only select fewer, so the
    # bound it was computed against still holds.
    selected, omitted = _fit(0)
    if omitted:
        selected, omitted = _fit(1 + len(_omission_footer(len(scored))))

    return SkillSelection(
        selected=tuple(selected),
        omitted=tuple(omitted),
        budget_chars=budget_chars,
        query_digest=digest_of({"task": task_text}),
    )
