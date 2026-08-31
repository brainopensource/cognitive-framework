"""Failure taxonomy and classification (`spec §25`).

Classification is deterministic and evidence-driven. It reads verification
output, the trajectory, and repository state -- never the model's own account
of what went wrong, which is the thing most likely to be confidently wrong.

Order matters: the rules are evaluated most-specific first, because
`TEST_FAILURE` is true of almost every failed run and would otherwise absorb
the more actionable classes underneath it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence

__all__ = ["FailureClass", "FailureVerdict", "FailureClassifier", "TrajectorySignals"]


class FailureClass(str, Enum):
    """`spec §25` taxonomy, verbatim."""

    TASK_MISUNDERSTOOD = "TASK_MISUNDERSTOOD"
    WRONG_FILE = "WRONG_FILE"
    INSUFFICIENT_CONTEXT = "INSUFFICIENT_CONTEXT"
    EXCESSIVE_CONTEXT = "EXCESSIVE_CONTEXT"
    WRONG_HYPOTHESIS = "WRONG_HYPOTHESIS"
    BAD_PATCH = "BAD_PATCH"
    INCOMPLETE_PATCH = "INCOMPLETE_PATCH"
    TEST_FAILURE = "TEST_FAILURE"
    REGRESSION = "REGRESSION"
    TOOL_FAILURE = "TOOL_FAILURE"
    ENVIRONMENT_FAILURE = "ENVIRONMENT_FAILURE"
    REPEATED_REASONING_FAILURE = "REPEATED_REASONING_FAILURE"
    STALE_MEMORY = "STALE_MEMORY"
    BUDGET_PRESSURE = "BUDGET_PRESSURE"
    NONE = "NONE"


@dataclass(frozen=True, slots=True)
class TrajectorySignals:
    """What the classifier is allowed to know. All of it is observed fact."""

    turns_used: int = 0
    turns_remaining: int = 0
    repeated_proposal_digests: int = 0
    distinct_files_edited: int = 0
    patch_apply_failures: int = 0
    tool_errors: int = 0
    consecutive_failed_verifications: int = 0
    search_hits_last: int = 0
    context_tokens: int = 0
    context_budget: int = 1
    previously_passing_now_failing: int = 0
    edited_paths: tuple[str, ...] = ()
    plan_revisions: int = 0

    @property
    def context_saturation(self) -> float:
        return self.context_tokens / max(self.context_budget, 1)

    @property
    def budget_fraction_left(self) -> float:
        total = self.turns_used + self.turns_remaining
        return self.turns_remaining / total if total else 0.0


@dataclass(frozen=True, slots=True)
class FailureVerdict:
    failure_class: FailureClass
    confidence: float
    rationale: str
    evidence: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "failureClass": self.failure_class.value,
            "confidence": round(self.confidence, 4),
            "rationale": self.rationale,
            "evidence": list(self.evidence),
        }


#: Patterns over captured stderr/stdout. Each maps to the class whose recovery
#: action would actually help; a pattern with no distinct remedy is omitted.
_PATTERNS: tuple[tuple[str, FailureClass, str], ...] = (
    (r"no module named|importerror|modulenotfounderror",
     FailureClass.ENVIRONMENT_FAILURE, "a module could not be imported"),
    (r"command not found|no such file or directory|permission denied",
     FailureClass.ENVIRONMENT_FAILURE, "the command or path was unavailable"),
    (r"syntaxerror|indentationerror|unexpected token|parse error",
     FailureClass.BAD_PATCH, "the patch left the file unparseable"),
    (r"patch does not apply|hunk failed|corrupt patch|context mismatch",
     FailureClass.BAD_PATCH, "the patch did not apply to current state"),
    (r"timeout|timed out|killed",
     FailureClass.ENVIRONMENT_FAILURE, "execution exceeded its time limit"),
    (r"attributeerror|nameerror|typeerror.*not defined",
     FailureClass.INCOMPLETE_PATCH, "the change referenced something that does not exist"),
    (r"assertionerror|assert ",
     FailureClass.TEST_FAILURE, "an assertion failed"),
)


class FailureClassifier:
    """`spec §25`. Deterministic; identical inputs give identical verdicts."""

    def classify(
        self,
        *,
        verification: Any = None,
        signals: TrajectorySignals | None = None,
        task: str = "",
    ) -> FailureVerdict:
        signals = signals or TrajectorySignals()

        if verification is not None and getattr(verification, "passed", False):
            return FailureVerdict(FailureClass.NONE, 1.0, "verification passed")

        # -- structural classes, checked before any output parsing --------
        # These describe the *shape* of the trajectory and are more reliable
        # than log text, which often reports a symptom of an earlier cause.

        if signals.budget_fraction_left < 0.15 and signals.turns_used > 0:
            return FailureVerdict(
                FailureClass.BUDGET_PRESSURE, 0.9,
                "less than 15% of the turn budget remains",
                (f"turnsRemaining={signals.turns_remaining}",))

        if signals.repeated_proposal_digests >= 2:
            return FailureVerdict(
                FailureClass.REPEATED_REASONING_FAILURE, 0.85,
                "the same proposal was produced repeatedly, so retrying it "
                "unchanged cannot produce a different result",
                (f"repeats={signals.repeated_proposal_digests}",))

        if signals.patch_apply_failures >= 2:
            return FailureVerdict(
                FailureClass.STALE_MEMORY, 0.75,
                "repeated patch-application failures indicate the context "
                "no longer matches the file on disk",
                (f"patchFailures={signals.patch_apply_failures}",))

        if signals.previously_passing_now_failing > 0:
            return FailureVerdict(
                FailureClass.REGRESSION, 0.9,
                "tests that passed before the change now fail",
                (f"regressed={signals.previously_passing_now_failing}",))

        if signals.tool_errors >= 2:
            return FailureVerdict(
                FailureClass.TOOL_FAILURE, 0.8,
                "multiple tool invocations failed at the instrument level",
                (f"toolErrors={signals.tool_errors}",))

        # -- output-driven classes ----------------------------------------
        blob = _verification_blob(verification).lower()
        for pattern, failure_class, rationale in _PATTERNS:
            if re.search(pattern, blob):
                # A test failure with no edits yet is not a patch problem;
                # it is the reproduction step working as intended.
                if (failure_class is FailureClass.TEST_FAILURE
                        and signals.distinct_files_edited == 0):
                    return FailureVerdict(
                        FailureClass.WRONG_HYPOTHESIS, 0.6,
                        "a test fails but nothing has been edited, so no "
                        "hypothesis has been tested yet",
                        (pattern,))
                return FailureVerdict(failure_class, 0.8, rationale, (pattern,))

        # -- context-shaped classes ---------------------------------------
        if signals.search_hits_last == 0 and signals.distinct_files_edited == 0:
            return FailureVerdict(
                FailureClass.INSUFFICIENT_CONTEXT, 0.7,
                "no search results and no edits: the target has not been located",
                ("searchHits=0",))

        if signals.context_saturation > 0.92:
            return FailureVerdict(
                FailureClass.EXCESSIVE_CONTEXT, 0.65,
                "the working set is saturated, crowding out targeted retrieval",
                (f"saturation={signals.context_saturation:.2f}",))

        if signals.consecutive_failed_verifications >= 2 and signals.plan_revisions == 0:
            return FailureVerdict(
                FailureClass.WRONG_HYPOTHESIS, 0.7,
                "verification has failed repeatedly without the plan being revised",
                (f"consecutiveFailures={signals.consecutive_failed_verifications}",))

        if signals.distinct_files_edited == 1 and signals.consecutive_failed_verifications >= 1:
            return FailureVerdict(
                FailureClass.WRONG_FILE, 0.55,
                "a single file was edited and verification still fails; the "
                "localisation may be wrong",
                (f"editedPaths={list(signals.edited_paths)}",))

        if verification is not None and getattr(verification, "failures", ()):
            return FailureVerdict(
                FailureClass.TEST_FAILURE, 0.6, "verification reported failures",
                tuple(getattr(c, "layer", "?").value if hasattr(getattr(c, "layer", None), "value")
                      else str(getattr(c, "layer", "?"))
                      for c in verification.failures))

        return FailureVerdict(
            FailureClass.TASK_MISUNDERSTOOD, 0.3,
            "no specific failure signature matched; the task framing may be wrong")


def _verification_blob(verification: Any) -> str:
    if verification is None:
        return ""
    parts: list[str] = []
    for check in getattr(verification, "checks", ()) or ():
        parts.append(str(getattr(check, "stdout_tail", "")))
        parts.append(str(getattr(check, "stderr_tail", "")))
    return "\n".join(parts)
