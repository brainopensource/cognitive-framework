"""Deterministic task classification (`spec §6`, `§7`).

`spec §6` is explicit: *"Do not require an expensive LLM call when
deterministic classification is sufficient."* This module therefore does the
whole job with lexical signals over the task text plus cheap repository
metadata. It never calls a model.

Determinism is not a stylistic preference here. The classifier's output picks
the workflow, the budget, and whether the fast path is taken, and the
`guarded_consult` path in `runtime/meta_controller.py` refuses a controller
that answers differently to identical inputs. A stochastic classifier upstream
would make the whole controller non-reproducible.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence

from ...domain.canonicalisation.digest import digest_of

__all__ = [
    "SIMPLE_THRESHOLD",
    "TaskClassifier",
    "TaskProfile",
    "TaskType",
    "WorkflowKind",
]

#: Below this complexity the fast path is taken (`spec §7`).
SIMPLE_THRESHOLD = 0.35


class TaskType(str, Enum):
    """The taxonomy from `spec §6`, verbatim."""

    SIMPLE_FIX = "simple_fix"
    COMPLEX_BUG = "complex_bug"
    TEST_FAILURE = "test_failure"
    REFACTOR = "refactor"
    FEATURE = "feature"
    MULTI_FILE_FEATURE = "multi_file_feature"
    DEPENDENCY_ISSUE = "dependency_issue"
    REPOSITORY_EXPLORATION = "repository_exploration"
    GREENFIELD = "greenfield"
    LONG_TASK = "long_task"
    UNKNOWN = "unknown"


class WorkflowKind(str, Enum):
    """Which composition the profile recommends."""

    FAST = "fast"
    BALANCED = "balanced"
    MAX = "max"


#: Lexical evidence per task type. Weights are small integers on purpose: the
#: score is a ranking signal, not a probability, and inventing calibrated
#: floats here would imply an accuracy this has not earned.
_SIGNALS: Mapping[TaskType, tuple[tuple[str, int], ...]] = {
    TaskType.TEST_FAILURE: (
        (r"\btest(s)? (are |is )?fail", 4), (r"\bfailing test", 4),
        (r"\bpytest\b", 2), (r"\bassertion ?error", 3), (r"\btraceback\b", 2),
        (r"\bmake (the )?test(s)? pass", 4), (r"\bred test", 3),
    ),
    TaskType.COMPLEX_BUG: (
        (r"\bbug\b", 2), (r"\bcrash", 3), (r"\bsegfault", 3),
        (r"\brace condition", 4), (r"\bdeadlock", 4), (r"\bmemory leak", 4),
        (r"\bintermittent", 4), (r"\bflaky", 3), (r"\bregression", 3),
        (r"\bincorrect(ly)? (result|value|output)", 3), (r"\bedge case", 2),
    ),
    TaskType.SIMPLE_FIX: (
        (r"\btypo\b", 5), (r"\brename\b", 3), (r"\bone[- ]line", 4),
        (r"\bsmall fix", 4), (r"\boff[- ]by[- ]one", 3),
        (r"\bupdate (the )?(string|message|constant|docstring)", 3),
        (r"\bchange (the )?default", 2),
    ),
    TaskType.REFACTOR: (
        (r"\brefactor", 5), (r"\bextract (a )?(method|function|class)", 4),
        (r"\bclean ?up", 3), (r"\bdeduplicat", 3), (r"\bsimplify", 2),
        (r"\brestructure", 3), (r"\bmigrat(e|ion) (the )?api", 4),
    ),
    TaskType.FEATURE: (
        (r"\badd (a |an )?(new )?(feature|option|flag|endpoint|command)", 4),
        (r"\bimplement\b", 3), (r"\bsupport for\b", 3), (r"\ballow (the )?user", 2),
    ),
    TaskType.MULTI_FILE_FEATURE: (
        (r"\bacross (the )?(codebase|repo|modules)", 4),
        (r"\bevery (module|file|package)", 4), (r"\bend[- ]to[- ]end", 3),
        (r"\bwire (it |this )?(up )?through", 3), (r"\bplumb\b", 3),
    ),
    TaskType.DEPENDENCY_ISSUE: (
        (r"\bdependenc", 4), (r"\bimport ?error", 4), (r"\bmodulenotfound", 5),
        (r"\bversion conflict", 4), (r"\bpin (the )?version", 3),
        (r"\brequirements\.txt", 3), (r"\bpyproject\.toml", 2), (r"\bupgrade\b", 2),
    ),
    TaskType.REPOSITORY_EXPLORATION: (
        (r"\bexplain\b", 4), (r"\bhow does\b", 4), (r"\bwhere is\b", 3),
        (r"\bwalk me through", 4), (r"\bwhat does .* do\b", 3),
        (r"\bdocument\b", 2), (r"\bsummari[sz]e", 3),
    ),
    TaskType.GREENFIELD: (
        (r"\bfrom scratch", 5), (r"\bnew (project|package|service|module)", 4),
        (r"\bscaffold", 4), (r"\bbootstrap a\b", 4), (r"\bgreenfield", 5),
    ),
    TaskType.LONG_TASK: (
        (r"\bentire (codebase|repository|project)", 4),
        (r"\brewrite\b", 4), (r"\bport (the )?(whole|entire)", 4),
        (r"\ball (occurrences|call sites|usages)", 3),
    ),
}

#: Task types that always warrant the max composition regardless of score.
_INHERENTLY_HARD = frozenset({
    TaskType.COMPLEX_BUG, TaskType.MULTI_FILE_FEATURE,
    TaskType.GREENFIELD, TaskType.LONG_TASK,
})

#: Task types that never need the planner if the repo is small.
_INHERENTLY_EASY = frozenset({TaskType.SIMPLE_FIX, TaskType.REPOSITORY_EXPLORATION})

_STACKTRACE = re.compile(r'File "[^"]+", line \d+|at [\w.$]+\([\w.]+:\d+\)')
_PATH_LIKE = re.compile(r"[\w./-]+\.(py|ts|tsx|js|go|rs|java|rb|c|cc|cpp|h|hpp)\b")


@dataclass(frozen=True, slots=True)
class TaskProfile:
    """`spec §6` output. Immutable; a reclassification produces a new value."""

    task_type: TaskType
    estimated_complexity: float
    uncertainty: float
    repo_familiarity: float
    suggested_workflow: WorkflowKind
    initial_budget: Mapping[str, int]
    signals: tuple[str, ...] = ()
    mentioned_paths: tuple[str, ...] = ()
    has_stacktrace: bool = False
    reproduction_available: bool = False

    @property
    def simple(self) -> bool:
        """Whether the fast path applies (`spec §7`)."""
        return self.estimated_complexity <= SIMPLE_THRESHOLD

    def to_canonical_dict(self) -> dict[str, Any]:
        return {
            "taskType": self.task_type.value,
            "estimatedComplexity": round(self.estimated_complexity, 4),
            "uncertainty": round(self.uncertainty, 4),
            "repoFamiliarity": round(self.repo_familiarity, 4),
            "suggestedWorkflow": self.suggested_workflow.value,
            "initialBudget": dict(self.initial_budget),
            "signals": list(self.signals),
            "mentionedPaths": list(self.mentioned_paths),
            "hasStacktrace": self.has_stacktrace,
            "reproductionAvailable": self.reproduction_available,
        }

    def digest(self) -> str:
        return digest_of(self.to_canonical_dict())


@dataclass(frozen=True, slots=True)
class RepoSignals:
    """Cheap repository metadata the classifier is allowed to consult.

    Deliberately small. Anything expensive belongs behind
    `RepositoryIntelligence`, which runs *after* classification decides
    whether the expense is warranted.
    """

    file_count: int = 0
    total_bytes: int = 0
    has_tests: bool = False
    test_roots: tuple[str, ...] = ()
    languages: tuple[str, ...] = ()
    initial_hits: int = 0
    known_repository: bool = False


class TaskClassifier:
    """Lexical + metadata classifier. No model call, no I/O of its own."""

    def __init__(self, *, simple_threshold: float = SIMPLE_THRESHOLD) -> None:
        self._threshold = simple_threshold

    def classify(
        self,
        task: str,
        repo: RepoSignals | None = None,
        *,
        budget_ceiling: Mapping[str, int] | None = None,
    ) -> TaskProfile:
        repo = repo or RepoSignals()
        text = (task or "").lower()
        if not text.strip():
            raise ValueError("task text is required for classification")

        scores, matched = self._score_types(text)
        task_type = self._winner(scores)
        paths = tuple(sorted({match.group(0) for match in _PATH_LIKE.finditer(task)}))
        has_trace = bool(_STACKTRACE.search(task))

        complexity = self._complexity(task_type, text, repo, paths, scores)
        uncertainty = self._uncertainty(task_type, scores, repo, paths, has_trace)
        familiarity = self._familiarity(repo)
        workflow = self._workflow(task_type, complexity, uncertainty)

        return TaskProfile(
            task_type=task_type,
            estimated_complexity=complexity,
            uncertainty=uncertainty,
            repo_familiarity=familiarity,
            suggested_workflow=workflow,
            initial_budget=self._budget(workflow, complexity, budget_ceiling),
            signals=matched,
            mentioned_paths=paths,
            has_stacktrace=has_trace,
            reproduction_available=has_trace or repo.has_tests,
        )

    # -- scoring ---------------------------------------------------------

    def _score_types(self, text: str) -> tuple[dict[TaskType, int], tuple[str, ...]]:
        scores: dict[TaskType, int] = {}
        matched: list[str] = []
        for task_type, patterns in _SIGNALS.items():
            total = 0
            for pattern, weight in patterns:
                if re.search(pattern, text):
                    total += weight
                    matched.append(f"{task_type.value}:{pattern}")
            if total:
                scores[task_type] = total
        return scores, tuple(matched)

    @staticmethod
    def _winner(scores: Mapping[TaskType, int]) -> TaskType:
        if not scores:
            return TaskType.UNKNOWN
        # Ties break toward the more expensive interpretation: mistaking a
        # complex bug for a simple fix costs a wasted fast-path attempt plus
        # an escalation, while the reverse costs only unused orchestration.
        ordering = sorted(
            scores.items(),
            key=lambda kv: (kv[1], kv[0] in _INHERENTLY_HARD, kv[0].value),
            reverse=True,
        )
        return ordering[0][0]

    def _complexity(
        self,
        task_type: TaskType,
        text: str,
        repo: RepoSignals,
        paths: Sequence[str],
        scores: Mapping[TaskType, int],
    ) -> float:
        base = {
            TaskType.SIMPLE_FIX: 0.12,
            TaskType.REPOSITORY_EXPLORATION: 0.20,
            TaskType.TEST_FAILURE: 0.38,
            TaskType.DEPENDENCY_ISSUE: 0.42,
            TaskType.FEATURE: 0.50,
            TaskType.REFACTOR: 0.55,
            TaskType.COMPLEX_BUG: 0.70,
            TaskType.MULTI_FILE_FEATURE: 0.78,
            TaskType.GREENFIELD: 0.80,
            TaskType.LONG_TASK: 0.90,
            TaskType.UNKNOWN: 0.55,
        }[task_type]

        # Repository scale. A 20k-file repo makes every task harder to
        # localise, independent of what the task says.
        if repo.file_count > 5000:
            base += 0.12
        elif repo.file_count > 1000:
            base += 0.07
        elif repo.file_count > 200:
            base += 0.03

        # An explicit target path is the single strongest simplifier: it
        # removes localisation, which is where most of the cost lives.
        if paths:
            base -= 0.10
        if len(paths) > 3:
            base += 0.08  # many paths means multi-file, not well-localised

        # A long brief usually encodes more constraints, not more clarity.
        words = len(text.split())
        if words > 250:
            base += 0.10
        elif words > 120:
            base += 0.05
        elif words < 15:
            base -= 0.03

        # Competing strong signals mean the task spans categories.
        if len([s for s in scores.values() if s >= 4]) >= 2:
            base += 0.08

        if not repo.has_tests:
            base += 0.06  # nothing cheap to verify against

        return _clamp(base)

    def _uncertainty(
        self,
        task_type: TaskType,
        scores: Mapping[TaskType, int],
        repo: RepoSignals,
        paths: Sequence[str],
        has_trace: bool,
    ) -> float:
        if task_type is TaskType.UNKNOWN:
            value = 0.85
        else:
            top = max(scores.values()) if scores else 0
            runner_up = sorted(scores.values(), reverse=True)[1] if len(scores) > 1 else 0
            margin = (top - runner_up) / max(top, 1)
            value = 0.75 - 0.45 * margin
        if has_trace:
            value -= 0.20     # a stack trace is near-direct localisation
        if paths:
            value -= 0.15
        if repo.initial_hits == 0:
            value += 0.12     # the first search found nothing to stand on
        elif repo.initial_hits > 40:
            value += 0.08     # everything matched, so nothing is localised
        return _clamp(value)

    @staticmethod
    def _familiarity(repo: RepoSignals) -> float:
        value = 0.5 if repo.known_repository else 0.15
        if repo.languages:
            value += 0.10
        if repo.has_tests:
            value += 0.10
        if repo.file_count and repo.file_count < 300:
            value += 0.10
        return _clamp(value)

    def _workflow(
        self, task_type: TaskType, complexity: float, uncertainty: float
    ) -> WorkflowKind:
        if task_type in _INHERENTLY_HARD:
            return WorkflowKind.MAX
        if complexity <= self._threshold and task_type in _INHERENTLY_EASY:
            return WorkflowKind.FAST
        if complexity <= self._threshold and uncertainty < 0.45:
            return WorkflowKind.FAST
        if complexity >= 0.68 or uncertainty >= 0.72:
            return WorkflowKind.MAX
        return WorkflowKind.BALANCED

    @staticmethod
    def _budget(
        workflow: WorkflowKind,
        complexity: float,
        ceiling: Mapping[str, int] | None,
    ) -> Mapping[str, int]:
        """Budgets scale with the workflow, then clamp to the manifest ceiling.

        The ceiling is the manifest's `budgetPolicy`. A profile may ask for
        less than the manifest allows and never for more -- the same rule
        `validate_directive` enforces on controller directives.
        """
        table = {
            WorkflowKind.FAST: {"turns": 12, "tokens": 60_000, "effects": 24,
                                "wallClockMillis": 300_000, "evaluations": 4},
            WorkflowKind.BALANCED: {"turns": 30, "tokens": 180_000, "effects": 64,
                                    "wallClockMillis": 900_000, "evaluations": 10},
            WorkflowKind.MAX: {"turns": 60, "tokens": 400_000, "effects": 128,
                               "wallClockMillis": 1_800_000, "evaluations": 16},
        }[workflow]
        scaled = {
            key: max(1, int(value * (0.75 + 0.5 * complexity)))
            for key, value in table.items()
        }
        if ceiling:
            scaled = {
                key: min(value, int(ceiling[key]))
                if key in ceiling else value
                for key, value in scaled.items()
            }
        return scaled


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))
