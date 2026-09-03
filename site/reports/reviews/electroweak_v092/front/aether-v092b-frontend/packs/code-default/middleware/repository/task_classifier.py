"""Deterministic classification of coding-task statements."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TaskKind = Literal["bugfix", "feature", "refactor", "migration", "greenfield", "read-only", "unknown"]


@dataclass(frozen=True, slots=True)
class TaskClassification:
    """Stable classification evidence suitable for durable task state."""

    kind: TaskKind
    confidence: float
    signals: tuple[str, ...] = ()
    ambiguous: bool = False


_RULES: tuple[tuple[TaskKind, tuple[str, ...]], ...] = (
    ("migration", ("migrate", "migration", "deprecat", "backward compat", "backwards compat", "rename api")),
    ("greenfield", ("from scratch", "greenfield", "new project", "scaffold", "empty repository")),
    ("read-only", ("explain", "summarize", "document", "analyze", "audit", "inspect only", "read-only")),
    ("refactor", ("refactor", "restructure", "cleanup", "clean up", "reorganize", "extract")),
    ("bugfix", ("bug", "bugfix", "fix", "broken", "regression", "incorrect", "fails", "failure", "traceback")),
    ("feature", ("feature", "implement", "add", "support", "introduce", "build")),
)


class TaskClassifier:
    """Callable object form for composition registries and dependency injection."""

    def classify(self, text: str) -> TaskClassification:
        return classify_task(text)


def classify_task(text: str) -> TaskClassification:
    """Classify task text using ordered deterministic rules.

    Specific compatibility and lifecycle work wins over broad verbs such as
    ``add``. Ties are reported as ambiguous rather than inventing confidence.
    """
    normalized = " ".join(text.lower().split())
    matches: list[tuple[TaskKind, str]] = []
    for kind, keywords in _RULES:
        for keyword in keywords:
            if keyword in normalized:
                matches.append((kind, keyword))
                break
    if not matches:
        return TaskClassification("unknown", 0.0, ambiguous=True)
    kind = matches[0][0]
    same_kind = [signal for candidate, signal in matches if candidate == kind]
    # The ordered rules intentionally resolve broad secondary verbs (for
    # example ``add``) beneath a specific primary intent (``migration``).
    ambiguous = False
    confidence = min(1.0, 0.65 + 0.1 * (len(same_kind) - 1))
    if ambiguous:
        confidence = min(confidence, 0.55)
    return TaskClassification(kind, round(confidence, 3), tuple(same_kind), ambiguous)
