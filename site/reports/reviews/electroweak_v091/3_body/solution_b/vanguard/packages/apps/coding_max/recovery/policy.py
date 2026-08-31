"""Recovery strategies and bounded retries (`spec §26`, `§27`).

`spec §26` closes with the rule this module enforces mechanically: *"Every
retry must change the state or strategy."* `RecoveryPolicy.select` therefore
never returns a bare "try again" -- each action names a concrete state change,
and the retry budget refuses an action whose allowance is spent.

Actions are expressed as `StrategyDirective` kinds where one exists, so the
existing `guarded_consult` validation applies unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any, Mapping, Sequence

from .failures import FailureClass, FailureVerdict

__all__ = ["RecoveryAction", "RecoveryDecision", "RecoveryPolicy", "RetryBudget"]


class RecoveryAction(str, Enum):
    """Concrete state changes. Each maps to a directive the controller emits."""

    EXPAND_SEARCH = "expand_search"
    RETRIEVE_MISSING = "retrieve_missing"
    COMPRESS_CONTEXT = "compress_context"
    REFRESH_CONTEXT = "refresh_context"
    ROLLBACK_AND_REVIEW = "rollback_and_review"
    ANALYZE_TEST_FAILURE = "analyze_test_failure"
    REPLAN = "replan"
    ESCALATE_MODEL = "escalate_model"
    RETRY_TOOL = "retry_tool"
    SWITCH_TOOL = "switch_tool"
    NARROW_PATCH_SCOPE = "narrow_patch_scope"
    WIDEN_PATCH_SCOPE = "widen_patch_scope"
    ENTER_COMPLETION_MODE = "enter_completion_mode"
    ABANDON = "abandon"


#: `spec §26` mapping, extended to every class in the taxonomy.
_ACTIONS_FOR: Mapping[FailureClass, tuple[RecoveryAction, ...]] = {
    FailureClass.WRONG_FILE: (RecoveryAction.EXPAND_SEARCH, RecoveryAction.REPLAN),
    FailureClass.INSUFFICIENT_CONTEXT: (RecoveryAction.RETRIEVE_MISSING,
                                        RecoveryAction.EXPAND_SEARCH),
    FailureClass.EXCESSIVE_CONTEXT: (RecoveryAction.COMPRESS_CONTEXT,),
    FailureClass.BAD_PATCH: (RecoveryAction.ROLLBACK_AND_REVIEW,
                             RecoveryAction.NARROW_PATCH_SCOPE),
    FailureClass.INCOMPLETE_PATCH: (RecoveryAction.WIDEN_PATCH_SCOPE,
                                    RecoveryAction.RETRIEVE_MISSING),
    FailureClass.TEST_FAILURE: (RecoveryAction.ANALYZE_TEST_FAILURE,
                                RecoveryAction.REPLAN),
    FailureClass.REGRESSION: (RecoveryAction.ROLLBACK_AND_REVIEW,
                              RecoveryAction.NARROW_PATCH_SCOPE),
    FailureClass.WRONG_HYPOTHESIS: (RecoveryAction.REPLAN,
                                    RecoveryAction.EXPAND_SEARCH),
    FailureClass.TASK_MISUNDERSTOOD: (RecoveryAction.REPLAN,
                                      RecoveryAction.ESCALATE_MODEL),
    FailureClass.REPEATED_REASONING_FAILURE: (RecoveryAction.ESCALATE_MODEL,
                                              RecoveryAction.REPLAN),
    FailureClass.TOOL_FAILURE: (RecoveryAction.RETRY_TOOL, RecoveryAction.SWITCH_TOOL),
    FailureClass.ENVIRONMENT_FAILURE: (RecoveryAction.SWITCH_TOOL,
                                       RecoveryAction.REPLAN),
    FailureClass.STALE_MEMORY: (RecoveryAction.REFRESH_CONTEXT,),
    FailureClass.BUDGET_PRESSURE: (RecoveryAction.ENTER_COMPLETION_MODE,),
    FailureClass.NONE: (),
}

#: `spec §17` trigger for actions that imply replanning.
_REPLAN_TRIGGER_FOR: Mapping[FailureClass, str] = {
    FailureClass.WRONG_FILE: "wrong_localization",
    FailureClass.WRONG_HYPOTHESIS: "failed_assumption",
    FailureClass.INCOMPLETE_PATCH: "unexpected_dependency",
    FailureClass.BAD_PATCH: "repeated_failed_patch",
    FailureClass.TEST_FAILURE: "unexpected_test_behavior",
    FailureClass.INSUFFICIENT_CONTEXT: "major_context_discovery",
    FailureClass.BUDGET_PRESSURE: "budget_pressure",
}

#: Which `StrategyDirective` kind carries each action to the runtime. The
#: kinds are fixed by `ports/meta_controller.py::DIRECTIVE_KINDS`; nothing here
#: may invent one, which is what keeps this a policy plugin.
_DIRECTIVE_FOR: Mapping[RecoveryAction, str] = {
    RecoveryAction.EXPAND_SEARCH: "request_context",
    RecoveryAction.RETRIEVE_MISSING: "request_context",
    RecoveryAction.COMPRESS_CONTEXT: "request_context",
    RecoveryAction.REFRESH_CONTEXT: "request_context",
    RecoveryAction.ROLLBACK_AND_REVIEW: "delegate",
    RecoveryAction.ANALYZE_TEST_FAILURE: "change_verification",
    RecoveryAction.REPLAN: "revise_plan",
    RecoveryAction.ESCALATE_MODEL: "retry",
    RecoveryAction.RETRY_TOOL: "retry",
    RecoveryAction.SWITCH_TOOL: "redirect",
    RecoveryAction.NARROW_PATCH_SCOPE: "revise_plan",
    RecoveryAction.WIDEN_PATCH_SCOPE: "revise_plan",
    RecoveryAction.ENTER_COMPLETION_MODE: "conclude",
    RecoveryAction.ABANDON: "stop",
}


@dataclass
class RetryBudget:
    """`spec §27`. Bounded, and consumed by *strategy*, not by attempt count."""

    same_strategy: int = 1
    alternate_strategy: int = 2
    reviewer_escalation: int = 1
    model_escalation: int = 1
    _spent: dict[str, int] = field(default_factory=dict, repr=False)

    def remaining(self, dimension: str) -> int:
        return max(0, getattr(self, dimension, 0) - self._spent.get(dimension, 0))

    def can_spend(self, dimension: str) -> bool:
        return self.remaining(dimension) > 0

    def spend(self, dimension: str) -> bool:
        if not self.can_spend(dimension):
            return False
        self._spent[dimension] = self._spent.get(dimension, 0) + 1
        return True

    def exhausted(self) -> bool:
        return all(self.remaining(d) == 0 for d in
                   ("same_strategy", "alternate_strategy",
                    "reviewer_escalation", "model_escalation"))

    def to_dict(self) -> dict[str, Any]:
        return {d: self.remaining(d) for d in
                ("same_strategy", "alternate_strategy",
                 "reviewer_escalation", "model_escalation")}


@dataclass(frozen=True, slots=True)
class RecoveryDecision:
    action: RecoveryAction
    directive_kind: str
    reason: str
    replan_trigger: str | None = None
    scope: Mapping[str, Any] = field(default_factory=dict)
    budget_dimension: str = "alternate_strategy"

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action.value, "directiveKind": self.directive_kind,
            "reason": self.reason, "replanTrigger": self.replan_trigger,
            "scope": dict(self.scope), "budgetDimension": self.budget_dimension,
        }


class RecoveryPolicy:
    """Selects the next recovery action, honouring the retry budget."""

    def __init__(self, budget: RetryBudget | None = None) -> None:
        self._budget = budget or RetryBudget()
        self._history: list[RecoveryAction] = []

    @property
    def budget(self) -> RetryBudget:
        return self._budget

    def history(self) -> tuple[RecoveryAction, ...]:
        return tuple(self._history)

    def select(
        self,
        verdict: FailureVerdict,
        *,
        reviewer_available: bool = True,
        can_escalate_model: bool = True,
    ) -> RecoveryDecision:
        """Pick the first candidate not already tried and still affordable."""
        candidates = list(_ACTIONS_FOR.get(verdict.failure_class, ()))
        if not candidates:
            return self._decision(RecoveryAction.ABANDON, verdict,
                                  "no recovery action applies to this verdict")

        for action in candidates:
            # `spec §26`: a retry that repeats a spent strategy is not a
            # recovery, so an already-tried action is skipped rather than
            # re-issued with a different label.
            if action in self._history:
                continue
            if action is RecoveryAction.ESCALATE_MODEL:
                if not can_escalate_model or not self._budget.spend("model_escalation"):
                    continue
            elif action is RecoveryAction.ROLLBACK_AND_REVIEW:
                if not reviewer_available or not self._budget.spend("reviewer_escalation"):
                    continue
            elif action is RecoveryAction.RETRY_TOOL:
                if not self._budget.spend("same_strategy"):
                    continue
            elif not self._budget.spend("alternate_strategy"):
                continue

            self._history.append(action)
            return self._decision(action, verdict, verdict.rationale)

        # Every mapped strategy is spent. Finishing the best candidate under
        # completion mode beats looping, and beats abandoning outright.
        terminal = (RecoveryAction.ENTER_COMPLETION_MODE
                    if not self._budget.exhausted() or self._history
                    else RecoveryAction.ABANDON)
        self._history.append(terminal)
        return self._decision(terminal, verdict,
                              "all mapped recovery strategies are exhausted")

    def _decision(
        self, action: RecoveryAction, verdict: FailureVerdict, reason: str
    ) -> RecoveryDecision:
        return RecoveryDecision(
            action=action,
            directive_kind=_DIRECTIVE_FOR[action],
            reason=f"{verdict.failure_class.value}: {reason}"[:400],
            replan_trigger=_REPLAN_TRIGGER_FOR.get(verdict.failure_class),
            scope={"failureClass": verdict.failure_class.value,
                   "confidence": round(verdict.confidence, 3)},
            budget_dimension=("model_escalation"
                              if action is RecoveryAction.ESCALATE_MODEL
                              else "alternate_strategy"),
        )
