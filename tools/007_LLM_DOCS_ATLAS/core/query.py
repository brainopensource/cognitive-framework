"""Task-conditioned query analysis for LDA retrieval.

Parses an agent's task string into a deterministic QueryPlan: detected intent,
symbol-like tokens, stack-trace file:line frames, and expanded search terms.
Pure stdlib, fully deterministic — no model calls.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Tuple

from .standardizer import split_identifiers

# Intent cue vocabularies (ordered: first match wins).
_INTENT_CUES: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    (
        "bugfix",
        (
            "fix", "bug", "error", "exception", "traceback", "crash", "failing",
            "fails", "failure", "broken", "regression", "stack trace", "debug",
            "wrong", "incorrect", "does not work", "doesn't work", "leak",
        ),
    ),
    (
        "test",
        (
            "test", "tests", "unit test", "coverage", "falsifier", "spec test",
            "regression test", "assert",
        ),
    ),
    (
        "feature",
        (
            "add", "implement", "create", "introduce", "support", "new feature",
            "extend", "build", "wire", "enable",
        ),
    ),
    (
        "research",
        (
            "research", "understand", "how does", "why does", "compare",
            "investigate", "analyze", "explore", "improve", "refactor",
        ),
    ),
    (
        "explain",
        (
            "explain", "describe", "what is", "where is", "summarize", "overview",
            "document",
        ),
    ),
)

# Intents with no explicit cue fall back to a neutral retrieval mix.
_DEFAULT_INTENT = "explain"

# intent -> (docs_frac, code_frac, tests_frac); each row sums to 1.0.
DEFAULT_BUDGET_MIX: dict[str, Tuple[float, float, float]] = {
    "bugfix": (0.20, 0.55, 0.25),
    "feature": (0.30, 0.50, 0.20),
    "research": (0.50, 0.35, 0.15),
    "test": (0.20, 0.40, 0.40),
    "explain": (0.45, 0.35, 0.20),
}

_FRAME_PATTERNS = (
    re.compile(r"([A-Za-z0-9_./\\-]+\.(?:py|ts|tsx|js|jsx|rs|go|java|rb|php|cs|c|h|cpp|hpp)):(\d+)"),
    re.compile(
        r"([A-Za-z0-9_./\\-]+\.(?:py|ts|tsx|js|jsx|rs|go|java|rb|php|cs|c|h|cpp|hpp))"
        r"[\"',]*\s+(?:line|at)\s+(\d+)"
    ),
)


@dataclass(frozen=True)
class QueryPlan:
    """Deterministic analysis of a task string for retrieval conditioning."""

    raw: str
    intent: str
    keywords: List[str] = field(default_factory=list)
    symbol_tokens: List[str] = field(default_factory=list)
    frames: List[Tuple[str, str]] = field(default_factory=list)  # (path, line)

    @property
    def budget_mix(self) -> Tuple[float, float, float]:
        return DEFAULT_BUDGET_MIX.get(self.intent, DEFAULT_BUDGET_MIX[_DEFAULT_INTENT])


def _stem_fold(token: str) -> str:
    """Cheap deterministic suffix fold so 'testing' matches 'test' in FTS ORs."""
    for suffix in ("ing", "ies", "ied", "ers", "er", "ed", "es", "s"):
        if len(token) > 4 and token.endswith(suffix):
            return token[: -len(suffix)]
    return token


def analyze_query(task: str) -> QueryPlan:
    """Classify intent and extract retrieval tokens from a task string."""
    lowered = task.lower()
    intent = _DEFAULT_INTENT
    for name, cues in _INTENT_CUES:
        if any(cue in lowered for cue in cues):
            intent = name
            break

    # Stack-trace / file:line frames: the strongest routing signal a failing
    # agent can hand us — route straight to the named file.
    frames: List[Tuple[str, str]] = []
    for pattern in _FRAME_PATTERNS:
        for match in pattern.finditer(task):
            path = match.group(1).replace("\\", "/")
            frames.append((path, match.group(2)))
    if not frames:
        for pattern in _FRAME_PATTERNS:
            for match in pattern.finditer(task):
                path = match.group(1).replace("\\", "/")
                if (path, match.group(2)) not in frames:
                    frames.append((path, match.group(2)))

    # Symbol-like tokens: CamelCase / snake_case / dotted identifiers.
    symbol_tokens: List[str] = []
    for token in re.findall(r"[A-Za-z_][A-Za-z0-9_]{3,}", task):
        if "_" in token or any(c.isupper() for c in token[1:]):
            if token.lower() not in symbol_tokens:
                symbol_tokens.append(token)

    # Keyword terms with identifier splitting and stem folding (dedup, stable order).
    keywords: List[str] = []
    for token in re.findall(r"[A-Za-z0-9_/.-]{2,}", task):
        lower = token.lower()
        if lower in {"and", "for", "the", "with", "from", "that", "this", "into",
                     "over", "what", "when", "where", "which", "make", "help",
                     "need", "your", "you", "are", "not", "all", "any", "out",
                     "use", "using", "via", "per", "each"}:
            continue
        if lower not in keywords:
            keywords.append(lower)
        for part in split_identifiers(token):
            if part not in keywords:
                keywords.append(part)

    expanded: List[str] = []
    for term in keywords:
        folded = _stem_fold(term)
        if folded != term and folded not in expanded:
            expanded.append(folded)
    keywords.extend(t for t in expanded if t not in keywords)

    return QueryPlan(raw=task, intent=intent, keywords=keywords,
                     symbol_tokens=symbol_tokens, frames=frames)


__all__ = ["QueryPlan", "analyze_query", "DEFAULT_BUDGET_MIX"]
