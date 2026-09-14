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

__all__ = ["SkillIndex", "SkillEntry", "build_skill_index", "retrieve_skills_for_task"]

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


def retrieve_skills_for_task(
    skills: Iterable[Mapping[str, str]],
    task_description: str,
    *,
    budget_chars: int = DEFAULT_BUDGET_CHARS,
) -> SkillIndex:
    """Task-conditioned skill selection respecting the W12-A <= 4096 char ceiling.

    Scores candidate skills by relevance against `task_description`.
    Candidate skills with higher overlap are prioritized. Fits as many relevant
    skills as possible within `budget_chars <= 4096`. Truncation is by whole entries.
    """
    raw_list = list(skills)
    if not task_description:
        return build_skill_index(raw_list, budget_chars=budget_chars)

    task_tokens = set(
        part.lower() for part in "".join(c if c.isalnum() else " " for c in task_description).split()
        if len(part) >= 2
    )

    def score_skill(raw: Mapping[str, str]) -> int:
        name = str(raw.get("name", "")).lower()
        desc = str(raw.get("description", "")).lower()
        name_tokens = set("".join(c if c.isalnum() else " " for c in name).split())
        desc_tokens = set("".join(c if c.isalnum() else " " for c in desc).split())
        name_score = sum(3 for t in task_tokens if t in name_tokens or t in name)
        desc_score = sum(1 for t in task_tokens if t in desc_tokens)
        return name_score + desc_score

    scored = []
    for idx, raw in enumerate(raw_list):
        score = score_skill(raw)
        scored.append((score, -idx, raw))
    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)

    sorted_skills = [item[2] for item in scored]
    return build_skill_index(sorted_skills, budget_chars=budget_chars)
