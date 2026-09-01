"""Plan construction and revision (`spec §15`, `§17`).

The planner is deterministic and template-driven. A model-authored plan is
supported (`Plan.from_mapping`) but is not required, because `spec §6`'s rule
about avoiding needless model calls applies just as much here: for a
`test_failure` the plan is always "reproduce, localise, patch, verify", and
paying a strong model to rediscover that is waste.

`spec §15`: *"Planner must remain mutable."* Revision is therefore a first
class operation that records why it happened.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any, Mapping, Sequence

from ....domain.canonicalisation.digest import digest_of
from ..profile import TaskProfile, TaskType
from .todo import TodoManager

__all__ = ["Plan", "Planner", "ReplanTrigger", "Replanner"]


@dataclass(frozen=True, slots=True)
class Plan:
    objective: str
    assumptions: tuple[str, ...] = ()
    steps: tuple[str, ...] = ()
    verification_strategy: tuple[str, ...] = ()
    risk_points: tuple[str, ...] = ()
    revision: int = 0
    reason: str = "initial"

    def to_canonical_dict(self) -> dict[str, Any]:
        return {
            "objective": self.objective, "assumptions": list(self.assumptions),
            "steps": list(self.steps),
            "verificationStrategy": list(self.verification_strategy),
            "riskPoints": list(self.risk_points),
            "revision": self.revision, "reason": self.reason,
        }

    def digest(self) -> str:
        return digest_of(self.to_canonical_dict())

    def to_todos(self) -> TodoManager:
        return TodoManager.from_steps(self.steps)

    def render(self) -> str:
        lines = [f"# Plan (rev {self.revision}): {self.objective}"]
        if self.assumptions:
            lines.append("\n## Assumptions (falsify these first)")
            lines += [f"  - {a}" for a in self.assumptions]
        lines.append("\n## Steps")
        lines += [f"  {i}. {s}" for i, s in enumerate(self.steps, start=1)]
        if self.verification_strategy:
            lines.append("\n## Verification")
            lines += [f"  - {v}" for v in self.verification_strategy]
        if self.risk_points:
            lines.append("\n## Risks")
            lines += [f"  - {r}" for r in self.risk_points]
        return "\n".join(lines)

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any], *, objective: str = "") -> "Plan":
        """Parse a model-authored plan. Parsed, never cast (`CT-03` posture)."""
        steps = tuple(str(s) for s in (raw.get("steps") or ()) if str(s).strip())
        if not steps:
            raise ValueError("a plan must contain at least one step")
        return cls(
            objective=str(raw.get("objective") or objective or "unspecified"),
            assumptions=tuple(str(a) for a in (raw.get("assumptions") or ())),
            steps=steps,
            verification_strategy=tuple(
                str(v) for v in (raw.get("verificationStrategy")
                                 or raw.get("verification_strategy") or ())),
            risk_points=tuple(str(r) for r in (raw.get("riskPoints")
                                               or raw.get("risk_points") or ())),
        )


#: Step templates per task type. `spec §15`'s worked example is the
#: `complex_bug` row; the others are the same shape adapted to what the task
#: actually requires evidence of.
_TEMPLATES: Mapping[TaskType, tuple[str, ...]] = {
    TaskType.TEST_FAILURE: (
        "Run the failing test and capture the exact failure output",
        "Read the failing assertion and the code under test",
        "Form a hypothesis for the defect and name the owning file",
        "Apply a minimal patch to the implementation",
        "Re-run the targeted test",
        "Run related tests to check for regression",
    ),
    TaskType.COMPLEX_BUG: (
        "Reproduce the reported failure deterministically",
        "Identify the implementation owner of the failing behaviour",
        "Inspect related tests and existing invariants",
        "Form and record a hypothesis with its falsifier",
        "Apply a minimal scoped patch",
        "Run targeted tests",
        "Inspect the diff for interface changes and run related tests",
    ),
    TaskType.SIMPLE_FIX: (
        "Locate the exact target",
        "Apply the minimal edit",
        "Verify syntax and run any directly related test",
    ),
    TaskType.REFACTOR: (
        "Map the current structure and all call sites",
        "Establish a green baseline before changing anything",
        "Apply the restructuring in reviewable increments",
        "Re-run the baseline test set after each increment",
        "Confirm no public interface changed unintentionally",
    ),
    TaskType.FEATURE: (
        "Identify the module that should own the new behaviour",
        "Inspect neighbouring code for conventions to follow",
        "Implement the behaviour",
        "Add or extend a test that fails without the change",
        "Run the targeted and related tests",
    ),
    TaskType.MULTI_FILE_FEATURE: (
        "Build a repository map of the affected subsystems",
        "Enumerate every call site and integration point",
        "Establish a green baseline",
        "Implement the core behaviour in its owning module",
        "Wire the behaviour through each integration point",
        "Add tests covering the seams",
        "Run targeted, related, and broader test sets",
    ),
    TaskType.DEPENDENCY_ISSUE: (
        "Reproduce the import or resolution failure",
        "Inspect the declared dependency manifest",
        "Determine the correct constraint",
        "Apply the manifest change",
        "Re-run the failing import and the test suite entrypoint",
    ),
    TaskType.REPOSITORY_EXPLORATION: (
        "Build a repository map",
        "Read the entrypoints and canonical modules",
        "Trace the specific flow the question concerns",
        "Answer with file and line citations",
    ),
    TaskType.GREENFIELD: (
        "Confirm the target layout and build system",
        "Scaffold the module skeleton",
        "Implement the core behaviour",
        "Add tests that exercise the public surface",
        "Run the full new-module test set",
    ),
    TaskType.LONG_TASK: (
        "Build a repository map and establish a green baseline",
        "Partition the work into independently verifiable units",
        "Execute one unit and verify it before starting the next",
        "Checkpoint after each verified unit",
        "Run the broader test set once all units are complete",
    ),
}

_DEFAULT_STEPS: tuple[str, ...] = (
    "Search the repository for the relevant code",
    "Read the candidate files",
    "Apply a minimal change",
    "Verify with the available tests",
)

_VERIFICATION_FOR: Mapping[TaskType, tuple[str, ...]] = {
    TaskType.SIMPLE_FIX: ("V1 syntax", "V5 targeted tests"),
    TaskType.TEST_FAILURE: ("V1 syntax", "V5 targeted tests", "V6 related tests"),
    TaskType.REPOSITORY_EXPLORATION: ("V8 task verification",),
}
_DEFAULT_VERIFICATION = ("V1 syntax", "V3 lint", "V5 targeted tests",
                         "V6 related tests", "V8 task verification")


class Planner:
    """Deterministic plan construction from a `TaskProfile`."""

    def create(
        self,
        task: str,
        profile: TaskProfile,
        *,
        repo_map: Any = None,
        extra_assumptions: Sequence[str] = (),
    ) -> Plan:
        steps = _TEMPLATES.get(profile.task_type, _DEFAULT_STEPS)
        assumptions = list(extra_assumptions)
        if profile.mentioned_paths:
            assumptions.append(
                f"The change belongs in one of: {', '.join(profile.mentioned_paths)}")
        if profile.has_stacktrace:
            assumptions.append("The stack trace names the failing frame accurately")
        if not profile.reproduction_available:
            assumptions.append(
                "No reproduction exists yet; one must be built before patching")

        risks: list[str] = []
        if profile.uncertainty > 0.6:
            risks.append("Localisation is uncertain; expect to revise the target file")
        if profile.repo_familiarity < 0.4:
            risks.append("Repository is unfamiliar; conventions must be read, not assumed")
        if getattr(repo_map, "dirty", False):
            risks.append("Working tree is dirty; baseline may not be green")

        return Plan(
            objective=task.strip()[:400],
            assumptions=tuple(assumptions),
            steps=steps,
            verification_strategy=_VERIFICATION_FOR.get(
                profile.task_type, _DEFAULT_VERIFICATION),
            risk_points=tuple(risks),
        )


class ReplanTrigger(str, Enum):
    """`spec §17`. Each trigger names an observation, not a mood."""

    FAILED_ASSUMPTION = "failed_assumption"
    WRONG_LOCALIZATION = "wrong_localization"
    UNEXPECTED_DEPENDENCY = "unexpected_dependency"
    REPEATED_FAILED_PATCH = "repeated_failed_patch"
    UNEXPECTED_TEST_BEHAVIOR = "unexpected_test_behavior"
    MAJOR_CONTEXT_DISCOVERY = "major_context_discovery"
    BUDGET_PRESSURE = "budget_pressure"


class Replanner:
    """Revises a plan in response to evidence (`spec §17`).

    Revision is additive where possible. Discarding the whole plan on the
    first contradiction throws away the steps that already produced evidence,
    and re-deriving them costs turns the budget cannot spare.
    """

    #: How each trigger reshapes the remaining plan.
    _INSERTIONS: Mapping[ReplanTrigger, tuple[str, ...]] = {
        ReplanTrigger.WRONG_LOCALIZATION: (
            "Widen the repository search with different terms and symbol lookup",
            "Re-identify the owning file from fresh evidence",
        ),
        ReplanTrigger.FAILED_ASSUMPTION: (
            "Record the falsified assumption and its contradicting evidence",
            "Re-derive the hypothesis from the observed behaviour",
        ),
        ReplanTrigger.UNEXPECTED_DEPENDENCY: (
            "Map the dependency edges around the target",
            "Extend the patch scope to cover the affected callers",
        ),
        ReplanTrigger.REPEATED_FAILED_PATCH: (
            "Roll back to the last verified state",
            "Re-read the target at current HEAD before re-patching",
        ),
        ReplanTrigger.UNEXPECTED_TEST_BEHAVIOR: (
            "Read the failing test to establish what it actually asserts",
            "Reconcile the implementation with the asserted contract",
        ),
        ReplanTrigger.MAJOR_CONTEXT_DISCOVERY: (
            "Re-rank context against the new discovery",
        ),
        ReplanTrigger.BUDGET_PRESSURE: (
            "Drop speculative exploration and finish the best current candidate",
        ),
    }

    def revise(
        self,
        current_plan: Plan,
        trigger: ReplanTrigger,
        *,
        evidence: Sequence[str] = (),
        completed_steps: Sequence[str] = (),
    ) -> Plan:
        remaining = tuple(s for s in current_plan.steps if s not in set(completed_steps))
        insertions = self._INSERTIONS.get(trigger, ())

        if trigger is ReplanTrigger.BUDGET_PRESSURE:
            # Completion mode (`spec §42`): shrink rather than grow.
            steps = insertions + tuple(
                s for s in remaining if "broader" not in s.lower()
                and "speculative" not in s.lower())
        else:
            steps = insertions + remaining

        assumptions = current_plan.assumptions
        if trigger is ReplanTrigger.FAILED_ASSUMPTION and assumptions:
            # The falsified assumption is dropped, not silently retained --
            # a plan that still asserts a disproven premise will keep
            # producing the same wrong step.
            assumptions = assumptions[1:]

        return replace(
            current_plan,
            steps=steps or current_plan.steps,
            assumptions=assumptions,
            risk_points=tuple(dict.fromkeys(
                current_plan.risk_points + tuple(evidence))),
            revision=current_plan.revision + 1,
            reason=trigger.value,
        )
