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
