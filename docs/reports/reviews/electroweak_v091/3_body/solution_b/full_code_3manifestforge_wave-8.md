---
id: report.electroweak.3_body.solution_b.full_code_3manifestforge_wave-8
class: report
authority: non-canonical
canonical_for: []
status: proposal
owner: repository-governance
version: 0.9.2a2
last_verified: 2026-08-31
purpose: Non-canonical candidate input to the Coding Max architecture convergence review.
audience:
  - contributor
  - architect
---

# full_code_3manifestforge — Wave 8
## Classificação Determinística e o Controller de Integração (código integral)

Estes são os dois arquivos mais densos do sistema e os que apareceram mais
elididos nos relatórios anteriores.

**Por que a classificação NÃO pode usar LLM:** `runtime/meta_controller.py::
guarded_consult` chama `assess` duas vezes com entradas idênticas e levanta se
as respostas diferirem. O `TaskProfile` alimenta o controller. Um classificador
estocástico upstream tornaria o controller inteiro irreprodutível — o substrato
transforma a *preferência* do §6 em **requisito rígido**.

---

## Cap. 8.1 — `vanguard/packages/apps/coding_max/profile.py`

**Status:** ARQUIVO NOVO (criar integralmente) · **394 linhas**

Classificador léxico + metadado. **Nunca chama modelo.** Budget clampa ao teto do manifest — a mesma regra que `validate_directive` impõe a diretivas do controller.

```python
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
```

---

## Cap. 8.2 — `vanguard/packages/apps/coding_max/controller.py`

**Status:** ARQUIVO NOVO (criar integralmente) · **433 linhas**

A costura única com o substrato. Registrado como `ports.meta_controller.MetaController` e ligado pelo campo `SessionPorts.meta_controller` já existente. Nada do episode loop, kernel ou modelo de eventos muda.

```python
"""`CodingMaxController` — the single integration seam (`spec §40`, `§44`).

This is the whole reason Coding Max needs no kernel change. The substrate
already consults a between-turn policy plugin (`ports/meta_controller.py`) and
already validates its output fail-closed (`runtime/meta_controller.py::
guarded_consult`). Coding Max is an implementation of that protocol.

Three properties are load-bearing and are asserted by construction:

* **Determinism.** `guarded_consult` calls `assess` twice with identical
  inputs and raises if the answers differ. Every decision below is therefore a
  pure function of the view, the progress projection, and internal state that
  only mutates when `assess` is *not* being resampled.
* **No authority.** The controller returns `StrategyDirective` values whose
  `scope_slice` never carries a capability, grant, principal, or a budget
  larger than what remains. `validate_directive` enforces this; the code here
  simply never builds such a slice.
* **No side effects.** No emission, no store access, no model call, no tool
  execution. The controller reads a projection and returns a value.

The state machine of `spec §44` lives here as `HarnessState`, driven by
observed evidence rather than by model prose.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any, Mapping, Sequence

from ...domain.canonicalisation.digest import digest_of
from ...ports.meta_controller import StrategyDirective
from .planning.planner import Plan, Planner, ReplanTrigger, Replanner
from .planning.todo import TodoManager, TodoStatus
from .profile import TaskProfile, WorkflowKind
from .recovery.failures import FailureClass, FailureClassifier, FailureVerdict, TrajectorySignals
from .recovery.policy import RecoveryAction, RecoveryDecision, RecoveryPolicy, RetryBudget
from .routing.router import CodingRole, ModelRouter

__all__ = ["CodingMaxController", "HarnessState", "ControllerSnapshot"]


class HarnessState(str, Enum):
    """`spec §44` states."""

    RECEIVED = "received"
    CLASSIFYING = "classifying"
    EXPLORING = "exploring"
    PLANNING = "planning"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    DIAGNOSING = "diagnosing"
    REPAIRING = "repairing"
    REPLANNING = "replanning"
    REVIEWING = "reviewing"
    FINAL_VERIFY = "final_verify"
    COMPLETED = "completed"
    FAILED = "failed"


#: Legal transitions (`spec §44`). Absent edges are refused, so a trajectory
#: that claims COMPLETED without passing FINAL_VERIFY is structurally
#: impossible rather than merely discouraged.
_LEGAL_TRANSITIONS: Mapping[HarnessState, frozenset[HarnessState]] = {
    HarnessState.RECEIVED: frozenset({HarnessState.CLASSIFYING, HarnessState.FAILED}),
    HarnessState.CLASSIFYING: frozenset({HarnessState.EXPLORING, HarnessState.EXECUTING,
                                         HarnessState.PLANNING, HarnessState.FAILED}),
    HarnessState.EXPLORING: frozenset({HarnessState.PLANNING, HarnessState.EXECUTING,
                                       HarnessState.FAILED}),
    HarnessState.PLANNING: frozenset({HarnessState.EXECUTING, HarnessState.FAILED}),
    HarnessState.EXECUTING: frozenset({HarnessState.VERIFYING, HarnessState.EXECUTING,
                                       HarnessState.DIAGNOSING, HarnessState.FINAL_VERIFY,
                                       HarnessState.FAILED}),
    HarnessState.VERIFYING: frozenset({HarnessState.DIAGNOSING, HarnessState.EXECUTING,
                                       HarnessState.FINAL_VERIFY, HarnessState.FAILED}),
    HarnessState.DIAGNOSING: frozenset({HarnessState.REPAIRING, HarnessState.REPLANNING,
                                        HarnessState.REVIEWING, HarnessState.EXPLORING,
                                        HarnessState.FINAL_VERIFY, HarnessState.FAILED}),
    HarnessState.REPAIRING: frozenset({HarnessState.EXECUTING, HarnessState.VERIFYING,
                                       HarnessState.FAILED}),
    HarnessState.REPLANNING: frozenset({HarnessState.EXECUTING, HarnessState.FAILED}),
    HarnessState.REVIEWING: frozenset({HarnessState.REPAIRING, HarnessState.REPLANNING,
                                       HarnessState.EXPLORING, HarnessState.FINAL_VERIFY,
                                       HarnessState.FAILED}),
    HarnessState.FINAL_VERIFY: frozenset({HarnessState.COMPLETED, HarnessState.DIAGNOSING,
                                          HarnessState.FAILED}),
    HarnessState.COMPLETED: frozenset(),
    HarnessState.FAILED: frozenset(),
}

#: `spec §31`. The reviewer is conditional, never always-on (`spec §58`).
_REVIEW_COMPLEXITY = 0.68
_REVIEW_PATCH_FILES = 4


@dataclass(frozen=True, slots=True)
class ControllerSnapshot:
    """Durable controller state for checkpoint/resume (`spec §34`–`§36`)."""

    state: HarnessState
    plan_digest: str
    todo_digest: str
    failure_history: tuple[str, ...]
    recovery_history: tuple[str, ...]
    retry_budget: Mapping[str, int]
    escalations: Mapping[str, int]
    completion_mode: bool

    def to_canonical_dict(self) -> dict[str, Any]:
        return {
            "state": self.state.value, "planDigest": self.plan_digest,
            "todoDigest": self.todo_digest,
            "failureHistory": list(self.failure_history),
            "recoveryHistory": list(self.recovery_history),
            "retryBudget": dict(self.retry_budget),
            "escalations": dict(self.escalations),
            "completionMode": self.completion_mode,
        }

    def digest(self) -> str:
        return digest_of(self.to_canonical_dict())


class CodingMaxController:
    """A `MetaController` that adapts effort to evidence.

    Registered as `ports.meta_controller.MetaController` and bound through the
    existing `SessionPorts.meta_controller` field. Nothing about the episode
    loop, kernel, or event model changes.
    """

    def __init__(
        self,
        *,
        controller_id: str = "coding-max@1",
        profile: TaskProfile | None = None,
        plan: Plan | None = None,
        todos: TodoManager | None = None,
        router: ModelRouter | None = None,
        retry_budget: RetryBudget | None = None,
        reviewer_enabled: bool = True,
        parallel_investigators: bool = False,
    ) -> None:
        self.controller_id = controller_id
        self._profile = profile
        self._plan = plan
        self._todos = todos or TodoManager()
        self._router = router
        self._classifier = FailureClassifier()
        self._recovery = RecoveryPolicy(retry_budget or RetryBudget())
        self._replanner = Replanner()
        self._reviewer_enabled = reviewer_enabled
        self._parallel = parallel_investigators

        self._state = HarnessState.RECEIVED
        self._failures: list[str] = []
        self._recoveries: list[str] = []
        self._completion_mode = False
        self._last_verification: Any = None
        self._last_signals = TrajectorySignals()
        self._reviewed = False
        # `guarded_consult` resamples `assess` to prove determinism. Recovery
        # selection consumes retry budget, so it must run at most once per
        # distinct input; the resample is served from here instead.
        self._decision_cache: dict[str, StrategyDirective | None] = {}

    # -- state machine ---------------------------------------------------

    @property
    def state(self) -> HarnessState:
        return self._state

    def transition(self, target: HarnessState) -> HarnessState:
        """Move states, refusing an illegal edge (`spec §44`)."""
        if target is self._state:
            return self._state
        if target not in _LEGAL_TRANSITIONS[self._state]:
            raise ValueError(
                f"illegal harness transition {self._state.value} -> {target.value}")
        self._state = target
        return self._state

    # -- evidence intake -------------------------------------------------

    def observe(
        self,
        *,
        verification: Any = None,
        signals: TrajectorySignals | None = None,
    ) -> None:
        """Record observed evidence. Called by the harness, not by `assess`.

        Kept separate from `assess` precisely because `guarded_consult`
        resamples `assess`: if intake mutated state, the second sample would
        see different inputs and the determinism check would fire.
        """
        if verification is not None:
            self._last_verification = verification
        if signals is not None:
            self._last_signals = signals

    def set_plan(self, plan: Plan, todos: TodoManager | None = None) -> None:
        self._plan = plan
        if todos is not None:
            self._todos = todos

    # -- the MetaController protocol -------------------------------------

    def assess(
        self,
        view: Any,
        progress: Any,
        confidence: Sequence[Any] = (),
    ) -> StrategyDirective | None:
        """Pure decision. Same inputs -> same directive, always."""
        signals = self._signals_from(view, progress)
        key = self._input_digest(view, progress, signals)
        if key in self._decision_cache:
            return self._decision_cache[key]

        directive = self._decide(view, signals)
        self._decision_cache[key] = directive
        return directive

    def _decide(self, view: Any, signals: TrajectorySignals) -> StrategyDirective | None:
        # Nothing to say while the run is healthy and making progress. A
        # controller that speaks every turn is an orchestrator in disguise and
        # burns turns the worker needs (`spec §1`: minimum orchestration when
        # sufficient).
        if self._healthy(signals):
            return None

        verdict = self._classifier.classify(
            verification=self._last_verification,
            signals=signals,
            task=getattr(view, "goal", "") or "",
        )
        if verdict.failure_class is FailureClass.NONE:
            return None

        decision = self._recovery.select(
            verdict,
            reviewer_available=self._reviewer_enabled and not self._reviewed,
            can_escalate_model=self._router is not None,
        )
        self._failures.append(verdict.failure_class.value)
        self._recoveries.append(decision.action.value)
        if decision.action is RecoveryAction.ENTER_COMPLETION_MODE:
            self.enter_completion_mode()
        return self._directive_for(decision, verdict, signals)

    def _input_digest(
        self, view: Any, progress: Any, signals: TrajectorySignals
    ) -> str:
        """Identity of one consultation. Two calls with the same inputs are
        the same question and must receive the same answer."""
        verification = self._last_verification
        return digest_of({
            "goal": str(getattr(view, "goal", "") or ""),
            "epoch": int(getattr(view, "context_epoch", 0) or 0),
            "signals": {
                "turnsUsed": signals.turns_used,
                "turnsRemaining": signals.turns_remaining,
                "repeats": signals.repeated_proposal_digests,
                "edited": signals.distinct_files_edited,
                "patchFailures": signals.patch_apply_failures,
                "toolErrors": signals.tool_errors,
                "failedVerifications": signals.consecutive_failed_verifications,
                "searchHits": signals.search_hits_last,
                "regressed": signals.previously_passing_now_failing,
                "planRevisions": signals.plan_revisions,
            },
            "verification": (verification.digest()
                             if hasattr(verification, "digest") else ""),
        })

    # -- decision helpers ------------------------------------------------

    def _healthy(self, signals: TrajectorySignals) -> bool:
        """Whether the run needs no intervention this turn."""
        if signals.consecutive_failed_verifications == 0 and \
                signals.repeated_proposal_digests == 0 and \
                signals.patch_apply_failures == 0 and \
                signals.tool_errors == 0 and \
                signals.previously_passing_now_failing == 0:
            # An unknown budget (both counters zero) is not pressure. Reading
            # it as pressure would make every run open in completion mode.
            total = signals.turns_used + signals.turns_remaining
            return total == 0 or signals.budget_fraction_left >= 0.15
        return False

    def _directive_for(
        self,
        decision: RecoveryDecision,
        verdict: FailureVerdict,
        signals: TrajectorySignals,
    ) -> StrategyDirective:
        """Build the directive. Scope carries diagnosis only, never authority."""
        scope: dict[str, Any] = {
            "action": decision.action.value,
            "failureClass": verdict.failure_class.value,
            "confidence": round(verdict.confidence, 3),
        }
        if decision.replan_trigger:
            scope["replanTrigger"] = decision.replan_trigger
        if decision.action in (RecoveryAction.EXPAND_SEARCH,
                               RecoveryAction.RETRIEVE_MISSING):
            scope["retrievalHint"] = self._retrieval_hint(verdict)
        if decision.action is RecoveryAction.ENTER_COMPLETION_MODE:
            scope["completionMode"] = True

        brief = None
        if decision.directive_kind == "delegate":
            # A delegated reviewer inherits an attenuated brief; it never
            # receives the parent's tools or budget from here. Attenuation is
            # the kernel's job (`kernel/attenuation.py`), not the controller's.
            brief = (f"Review the current patch against the task. "
                     f"Diagnosis: {verdict.failure_class.value}. "
                     f"{verdict.rationale}")[:800]

        return StrategyDirective(
            kind=decision.directive_kind,
            controller_id=self.controller_id,
            reason=decision.reason,
            brief=brief,
            scope_slice=scope,
        )

    @staticmethod
    def _retrieval_hint(verdict: FailureVerdict) -> str:
        return {
            FailureClass.WRONG_FILE:
                "widen the search: try symbol lookup and dependency edges, "
                "not another literal grep of the same terms",
            FailureClass.INSUFFICIENT_CONTEXT:
                "retrieve the specific missing definitions named in the failure",
            FailureClass.INCOMPLETE_PATCH:
                "retrieve every call site of the changed symbol",
            FailureClass.STALE_MEMORY:
                "re-read the target files at current HEAD before re-patching",
        }.get(verdict.failure_class, "retrieve context targeted at the failure")

    def _signals_from(self, view: Any, progress: Any) -> TrajectorySignals:
        """Derive signals from the projection, falling back to recorded ones.

        The view is authoritative where it carries the field, because it is
        reducible from events by a second reader; the recorded signals fill
        gaps the projection does not model.
        """
        base = self._last_signals
        stall = int(getattr(progress, "stall_count", 0) or 0)
        repeats = len(getattr(progress, "repeat_signatures", ()) or ())
        consumed = dict(getattr(view, "budget_consumed", {}) or {})
        revisions = len(getattr(view, "plan_revisions", ()) or ())
        return replace(
            base,
            repeated_proposal_digests=max(base.repeated_proposal_digests, repeats),
            consecutive_failed_verifications=max(
                base.consecutive_failed_verifications, stall),
            plan_revisions=max(base.plan_revisions, revisions),
            turns_used=max(base.turns_used, int(consumed.get("turns", 0) or 0)),
        )

    # -- review policy (`spec §31`) --------------------------------------

    def should_review(
        self,
        *,
        patch_file_count: int = 0,
        interface_changed: bool = False,
        worker_confidence: float = 1.0,
        repeated_repair: bool = False,
    ) -> bool:
        """Conditional reviewer. Always-on review is an anti-pattern (`spec §58`)."""
        if not self._reviewer_enabled or self._reviewed:
            return False
        complexity = float(getattr(self._profile, "estimated_complexity", 0.0) or 0.0)
        ambiguous = float(getattr(self._profile, "uncertainty", 0.0) or 0.0) > 0.75
        return any((
            complexity >= _REVIEW_COMPLEXITY,
            patch_file_count >= _REVIEW_PATCH_FILES,
            interface_changed,
            worker_confidence < 0.5,
            repeated_repair,
            ambiguous,
        ))

    def mark_reviewed(self) -> None:
        self._reviewed = True

    # -- planning integration --------------------------------------------

    def apply_replan(self, trigger: ReplanTrigger, evidence: Sequence[str] = ()) -> Plan | None:
        if self._plan is None:
            return None
        completed = tuple(
            item.description for item in self._todos.items()
            if item.status is TodoStatus.DONE
        )
        self._plan = self._replanner.revise(
            self._plan, trigger, evidence=evidence, completed_steps=completed)
        return self._plan

    @property
    def plan(self) -> Plan | None:
        return self._plan

    @property
    def todos(self) -> TodoManager:
        return self._todos

    @property
    def completion_mode(self) -> bool:
        return self._completion_mode

    def enter_completion_mode(self) -> None:
        """`spec §42`. Irreversible within a run: reopening exploration after
        deciding to finish is how a run overruns its budget twice."""
        self._completion_mode = True

    # -- durability ------------------------------------------------------

    def snapshot(self) -> ControllerSnapshot:
        return ControllerSnapshot(
            state=self._state,
            plan_digest=self._plan.digest() if self._plan else "",
            todo_digest=self._todos.digest(),
            failure_history=tuple(self._failures),
            recovery_history=tuple(a.value for a in self._recovery.history()),
            retry_budget=self._recovery.budget.to_dict(),
            escalations=dict(self._router.escalation_count()) if self._router else {},
            completion_mode=self._completion_mode,
        )
```

---

## Cap. 8.3 — Os dois bugs que o smoke test capturou

### 8.3.1 Não-determinismo (crítico — o controller seria rejeitado pelo kernel)

A primeira versão de `assess` chamava `RecoveryPolicy.select` diretamente.
`select` **consome budget de retry**. Quando `guarded_consult` reamostra
`assess` para provar determinismo, a segunda chamada via um budget diferente e
retornava diretiva diferente:

```
DETERMINISM (same obj): False     ← controller seria recusado
```

**Correção — memoização por digest de entrada:**

```diff
     def assess(self, view, progress, confidence=()) -> StrategyDirective | None:
+        """Pure decision. Same inputs -> same directive, always."""
         signals = self._signals_from(view, progress)
+        key = self._input_digest(view, progress, signals)
+        if key in self._decision_cache:
+            return self._decision_cache[key]
+        directive = self._decide(view, signals)
+        self._decision_cache[key] = directive
+        return directive
+
+    def _decide(self, view, signals) -> StrategyDirective | None:
         if self._healthy(signals):
             return None
         ...
```

E o cache declarado no `__init__`:

```diff
         self._reviewed = False
+        # `guarded_consult` resamples `assess` to prove determinism. Recovery
+        # selection consumes retry budget, so it must run at most once per
+        # distinct input; the resample is served from here instead.
+        self._decision_cache: dict[str, StrategyDirective | None] = {}
```

Resultado após correção:

```
DETERMINISM: True
budget preserved: {'same_strategy':1,'alternate_strategy':1,
                   'reviewer_escalation':1,'model_escalation':1}
```

O budget **não** é consumido duas vezes pela reamostragem.

### 8.3.2 Budget desconhecido lido como pressão

`TrajectorySignals()` default tem `turns_used=0, turns_remaining=0`, logo
`budget_fraction_left = 0.0 < 0.15`. **Todo run abria em modo de conclusão.**

```diff
                 signals.previously_passing_now_failing == 0:
-                signals.budget_fraction_left >= 0.15:
-            return True
-        return False
+            # An unknown budget (both counters zero) is not pressure. Reading
+            # it as pressure would make every run open in completion mode.
+            total = signals.turns_used + signals.turns_remaining
+            return total == 0 or signals.budget_fraction_left >= 0.15
+        return False
```

---

## Cap. 8.4 — `observe` separado de `assess`

```python
    def observe(self, *, verification=None, signals=None) -> None:
        """Record observed evidence. Called by the harness, not by `assess`.

        Kept separate from `assess` precisely because `guarded_consult`
        resamples `assess`: if intake mutated state, the second sample would
        see different inputs and the determinism check would fire.
        """
```

Esta separação é a mesma disciplina do bug 8.3.1, aplicada preventivamente à
entrada de evidência.

---

## Cap. 8.5 — Validação contra o kernel real

```python
view = AgentView(lineage_id='lin-1', goal='fix the parser bug',
                 context_epoch=3, budget_consumed={'turns':5})
progress = ProgressView(assessment='stalled', stall_count=2)
conf = [ConfidenceRecord(signal='external_verifier', value=0.3, subject_ref='goal',
                         basis=('V5_targeted_tests:exit=1',),
                         calibration={'contextEpoch':3})]
p = guarded_consult(controller, view, progress, conf,
                    remaining_budget={'turns':20,'tokens':50000})
```

```
GUARDED CONSULT PASSED all 5 falsifiers
 kind       : revise_plan
 reason     : WRONG_HYPOTHESIS: verification has failed repeatedly without the plan...
 scope      : {'action':'replan','failureClass':'WRONG_HYPOTHESIS',
               'confidence':0.7,'replanTrigger':'failed_assumption'}
 controller : coding-max@1
 inputDigest: sha256:118019883c74f2759ab2567

 STALE REFUSED: ControllerInputError — confidence for epoch 1 is stale at epoch 3
```

Os cinco falsificadores M-6.5 passam, e confiança obsoleta é corretamente
recusada.

---

## Cap. 8.6 — `scope_slice` nunca carrega autoridade

```python
        scope: dict[str, Any] = {
            "action": decision.action.value,
            "failureClass": verdict.failure_class.value,
            "confidence": round(verdict.confidence, 3),
        }
```

Sem capability. Sem grant. Sem principal. Sem budget maior que o restante.
`validate_directive` impõe isso; o código simplesmente nunca constrói tal slice.

Para `delegate`:

```python
            # A delegated reviewer inherits an attenuated brief; it never
            # receives the parent's tools or budget from here. Attenuation is
            # the kernel's job (`kernel/attenuation.py`), not the controller's.
            brief = (f"Review the current patch against the task. "
                     f"Diagnosis: {verdict.failure_class.value}. "
                     f"{verdict.rationale}")[:800]
```

---

## Cap. 8.7 — Desempate do classificador

```python
        # Ties break toward the more expensive interpretation: mistaking a
        # complex bug for a simple fix costs a wasted fast-path attempt plus
        # an escalation, while the reverse costs only unused orchestration.
```

Assimetria de custo real, não cautela genérica. Verificado:

```
simple_fix    cx=0.16 unc=0.42 wf=fast  turns=9   simple=True
test_failure  cx=0.32 unc=0.27 wf=fast  turns=10  simple=True
refactor      cx=0.67 unc=0.78 wf=max   turns=65  simple=False
complex_bug   cx=0.64 unc=--   wf=max   (via harness.prepare, repo real)
```
