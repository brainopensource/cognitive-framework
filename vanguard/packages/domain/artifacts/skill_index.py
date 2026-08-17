"""Frozen skill index for the prompt prefix (Reasonix atom, P1-4).

Bodies stay on disk and are read with ``fs.read``. Only names and descriptions
enter the frozen prefix, and only up to ``MAX_SKILL_INDEX_CHARS``. Cards that
do not fit are omitted whole — never truncated mid-card.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

__all__ = [
    "MAX_SKILL_INDEX_CHARS",
    "SkillCard",
    "SkillIndexError",
    "format_skill_index",
    "parse_skill_card",
]

MAX_SKILL_INDEX_CHARS = 4000


class SkillIndexError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class SkillCard:
    skill_id: str
    name: str
    description: str
    body_path: str

    def index_line(self) -> str:
        return f"- {self.skill_id}: {self.name} — {self.description}"


def parse_skill_card(raw: Mapping[str, Any]) -> SkillCard:
    skill_id = raw.get("id") or raw.get("skillId")
    name = raw.get("name")
    description = raw.get("description")
    body_path = raw.get("bodyPath") or raw.get("body_path")
    if not all(isinstance(v, str) and v.strip() for v in (skill_id, name, description, body_path)):
        raise SkillIndexError("skill card requires id, name, description, bodyPath")
    return SkillCard(
        skill_id=str(skill_id).strip(),
        name=str(name).strip(),
        description=str(description).strip(),
        body_path=str(body_path).strip(),
    )


def format_skill_index(
    cards: Sequence[SkillCard],
    *,
    ceiling: int = MAX_SKILL_INDEX_CHARS,
) -> str:
    """Render a prefix block. Empty input yields empty string (no decorative header)."""
    if ceiling < 1:
        raise SkillIndexError("skill index ceiling must be positive")
    lines: list[str] = []
    used = 0
    header = "Skills (read bodyPath with fs.read when needed):"
    for card in cards:
        line = card.index_line()
        block = f"{header}\n{line}" if not lines else line
        extra = len(block) + (1 if lines else 0)
        if used + extra > ceiling:
            break
        if not lines:
            lines.append(header)
            used += len(header)
        lines.append(line)
        used += 1 + len(line)
    return "\n".join(lines)
