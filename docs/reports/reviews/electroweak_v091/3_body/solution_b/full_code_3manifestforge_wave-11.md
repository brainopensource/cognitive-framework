---
id: report.electroweak.3_body.solution_b.full_code_3manifestforge_wave-11
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

# full_code_3manifestforge — Wave 11
## Verificação, Recuperação, Roteamento, Mapa e Erros (código integral)

Fecha o inventário de código. Todo arquivo do pacote `apps/coding_max` está
agora documentado integralmente entre as Waves 5–11.

---

## Cap. 11.1 — `vanguard/packages/apps/coding_max/verification/pipeline.py`

**Status:** ARQUIVO NOVO (criar integralmente) · **324 linhas**

Camadas V1–V9. O contrato §24: *uma tarefa não pode ser declarada bem-sucedida meramente porque o modelo diz que está resolvida.*

```python
"""Layered verification V1–V9 (`spec §23`, `§24`).

The contract this module exists to enforce is `spec §24`: *"A task cannot be
declared successful merely because the model says it is solved."* Every
`CheckResult` therefore carries the command that produced it and its exit
code. A layer with no command and no exit code cannot report `passed=True`.

Layers are selected by policy (`spec §23`), not run exhaustively: running the
full suite after a one-line edit spends minutes to learn what a targeted test
answers in seconds.
"""

from __future__ import annotations

import ast
import shlex
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from ....domain.canonicalisation.digest import digest_of

__all__ = [
    "CheckResult", "Layer", "VerificationPipeline", "VerificationResult",
    "VerificationScope", "select_layers",
]


class Layer(str, Enum):
    """`spec §23` ladder, cheapest first."""

    V1_SYNTAX = "V1_syntax"
    V2_FORMAT = "V2_format"
    V3_LINT = "V3_lint"
    V4_TYPECHECK = "V4_typecheck"
    V5_TARGETED_TESTS = "V5_targeted_tests"
    V6_RELATED_TESTS = "V6_related_tests"
    V7_BROADER_TESTS = "V7_broader_tests"
    V8_TASK_VERIFICATION = "V8_task_verification"
    V9_PATCH_REVIEW = "V9_patch_review"


class VerificationScope(str, Enum):
    """Why verification is running, which decides how much of it runs."""

    TINY_PATCH = "tiny_patch"
    CANDIDATE = "candidate_solution"
    FINAL = "final_solution"


#: `spec §23` policy table.
_LAYERS_FOR: Mapping[VerificationScope, tuple[Layer, ...]] = {
    VerificationScope.TINY_PATCH: (Layer.V1_SYNTAX, Layer.V5_TARGETED_TESTS),
    VerificationScope.CANDIDATE: (Layer.V1_SYNTAX, Layer.V3_LINT,
                                  Layer.V5_TARGETED_TESTS, Layer.V6_RELATED_TESTS),
    VerificationScope.FINAL: (Layer.V1_SYNTAX, Layer.V3_LINT, Layer.V4_TYPECHECK,
                              Layer.V5_TARGETED_TESTS, Layer.V6_RELATED_TESTS,
                              Layer.V7_BROADER_TESTS, Layer.V8_TASK_VERIFICATION),
}


def select_layers(
    scope: VerificationScope,
    *,
    changed_files: Sequence[str] = (),
    budget_pressure: bool = False,
) -> tuple[Layer, ...]:
    """Pick layers for this scope, then trim under budget pressure."""
    layers = list(_LAYERS_FOR[scope])
    if budget_pressure:
        # Completion mode (`spec §42`): keep only what can falsify the claim.
        layers = [l for l in layers if l in
                  (Layer.V1_SYNTAX, Layer.V5_TARGETED_TESTS, Layer.V8_TASK_VERIFICATION)]
    if not any(f.endswith(".py") for f in changed_files) and changed_files:
        layers = [l for l in layers if l not in (Layer.V1_SYNTAX, Layer.V4_TYPECHECK)]
    return tuple(layers)


@dataclass(frozen=True, slots=True)
class CheckResult:
    layer: Layer
    passed: bool
    command: str = ""
    exit_code: int | None = None
    stdout_tail: str = ""
    stderr_tail: str = ""
    duration_ms: int = 0
    skipped: bool = False
    skip_reason: str = ""

    @property
    def is_evidence(self) -> bool:
        """Whether this result can support a success claim.

        A skipped layer or one that never ran a command proves nothing. This
        is the guard against `spec §58`'s "fake test results".
        """
        return not self.skipped and self.exit_code is not None

    def to_dict(self) -> dict[str, Any]:
        return {
            "layer": self.layer.value, "passed": self.passed,
            "command": self.command, "exitCode": self.exit_code,
            "stdoutTail": self.stdout_tail[-2000:],
            "stderrTail": self.stderr_tail[-2000:],
            "durationMs": self.duration_ms,
            "skipped": self.skipped, "skipReason": self.skip_reason,
            "isEvidence": self.is_evidence,
        }


@dataclass(frozen=True, slots=True)
class VerificationResult:
    """`spec §24` contract."""

    passed: bool
    checks: tuple[CheckResult, ...] = ()
    failures: tuple[CheckResult, ...] = ()
    evidence: tuple[str, ...] = ()
    confidence: float = 0.0
    scope: VerificationScope = VerificationScope.CANDIDATE

    def to_canonical_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed, "scope": self.scope.value,
            "checks": [c.to_dict() for c in self.checks],
            "failures": [c.to_dict() for c in self.failures],
            "evidence": list(self.evidence),
            "confidence": round(self.confidence, 4),
        }

    def digest(self) -> str:
        return digest_of(self.to_canonical_dict())


class VerificationPipeline:
    """Runs layers as real subprocesses in the workspace.

    The runner is injectable so the harness can route execution through the
    kernel-authorised `proc.exec` adapter instead of calling out directly.
    The default direct runner exists for offline evaluation of the pipeline
    itself; production composition supplies the authorised runner
    (`spec §40`: adapters execute, policies authorise).
    """

    def __init__(
        self,
        root: Path | str,
        *,
        runner: Callable[[str, int], tuple[int, str, str]] | None = None,
        test_command: str = "python -m pytest",
        lint_command: str = "python -m ruff check",
        typecheck_command: str = "python -m mypy",
        timeout_s: int = 600,
    ) -> None:
        self._root = Path(root).resolve()
        self._runner = runner or self._default_runner
        self._test = test_command
        self._lint = lint_command
        self._typecheck = typecheck_command
        self._timeout = timeout_s

    # -- entry point -----------------------------------------------------

    def verify(
        self,
        *,
        scope: VerificationScope = VerificationScope.CANDIDATE,
        changed_files: Sequence[str] = (),
        targeted_tests: Sequence[str] = (),
        related_tests: Sequence[str] = (),
        budget_pressure: bool = False,
        task_check: Callable[[], CheckResult] | None = None,
    ) -> VerificationResult:
        layers = select_layers(scope, changed_files=changed_files,
                               budget_pressure=budget_pressure)
        checks: list[CheckResult] = []
        for layer in layers:
            check = self._run_layer(
                layer, changed_files=changed_files,
                targeted_tests=targeted_tests, related_tests=related_tests,
                task_check=task_check,
            )
            checks.append(check)
            # Stop at the first hard failure: later layers would report
            # cascading noise, and the classifier only needs the first cause.
            if not check.passed and not check.skipped:
                break

        failures = tuple(c for c in checks if not c.passed and not c.skipped)
        evidential = [c for c in checks if c.is_evidence]
        passed = not failures and bool(evidential)
        return VerificationResult(
            passed=passed,
            checks=tuple(checks),
            failures=failures,
            evidence=tuple(f"{c.layer.value}:exit={c.exit_code}" for c in evidential),
            confidence=self._confidence(checks, scope),
            scope=scope,
        )

    # -- layers ----------------------------------------------------------

    def _run_layer(
        self,
        layer: Layer,
        *,
        changed_files: Sequence[str],
        targeted_tests: Sequence[str],
        related_tests: Sequence[str],
        task_check: Callable[[], CheckResult] | None,
    ) -> CheckResult:
        if layer is Layer.V1_SYNTAX:
            return self._syntax(changed_files)
        if layer is Layer.V3_LINT:
            return self._command(layer, f"{self._lint} {' '.join(changed_files[:20])}"
                                 if changed_files else f"{self._lint} .",
                                 tolerate_missing=True)
        if layer is Layer.V4_TYPECHECK:
            return self._command(layer, f"{self._typecheck} {' '.join(changed_files[:20])}"
                                 if changed_files else "", tolerate_missing=True)
        if layer is Layer.V5_TARGETED_TESTS:
            return self._tests(layer, targeted_tests)
        if layer is Layer.V6_RELATED_TESTS:
            return self._tests(layer, related_tests)
        if layer is Layer.V7_BROADER_TESTS:
            return self._command(layer, f"{self._test} -q")
        if layer is Layer.V8_TASK_VERIFICATION:
            if task_check is None:
                return CheckResult(layer=layer, passed=True, skipped=True,
                                   skip_reason="no task-level check supplied")
            return task_check()
        return CheckResult(layer=layer, passed=True, skipped=True,
                           skip_reason="layer not implemented in this pipeline")

    def _syntax(self, changed_files: Sequence[str]) -> CheckResult:
        """Parse changed Python files. Cheap, local, and catches most bad patches."""
        started = time.monotonic()
        targets = [f for f in changed_files if f.endswith(".py")]
        if not targets:
            return CheckResult(layer=Layer.V1_SYNTAX, passed=True, skipped=True,
                               skip_reason="no python files changed")
        errors: list[str] = []
        for name in targets:
            path = self._root / name
            if not path.is_file():
                continue
            try:
                ast.parse(path.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError as exc:
                errors.append(f"{name}:{exc.lineno}: {exc.msg}")
            except OSError as exc:
                errors.append(f"{name}: {exc}")
        return CheckResult(
            layer=Layer.V1_SYNTAX, passed=not errors,
            command=f"ast.parse({len(targets)} files)",
            exit_code=0 if not errors else 1,
            stderr_tail="\n".join(errors),
            duration_ms=int((time.monotonic() - started) * 1000),
        )

    def _tests(self, layer: Layer, tests: Sequence[str]) -> CheckResult:
        if not tests:
            return CheckResult(layer=layer, passed=True, skipped=True,
                               skip_reason="no tests mapped to the changed target")
        return self._command(layer, f"{self._test} -q {' '.join(tests[:12])}")

    def _command(self, layer: Layer, command: str, *,
                 tolerate_missing: bool = False) -> CheckResult:
        if not command.strip():
            return CheckResult(layer=layer, passed=True, skipped=True,
                               skip_reason="no command for this layer")
        started = time.monotonic()
        exit_code, stdout, stderr = self._runner(command, self._timeout)
        # A missing optional tool is not a task failure. Reporting it as one
        # would make lint availability decide task outcomes.
        if tolerate_missing and exit_code != 0 and _tool_missing(stdout, stderr):
            return CheckResult(layer=layer, passed=True, skipped=True,
                               command=command, skip_reason="tool not installed")
        return CheckResult(
            layer=layer, passed=exit_code == 0, command=command, exit_code=exit_code,
            stdout_tail=stdout[-4000:], stderr_tail=stderr[-4000:],
            duration_ms=int((time.monotonic() - started) * 1000),
        )

    def _default_runner(self, command: str, timeout: int) -> tuple[int, str, str]:
        try:
            proc = subprocess.run(
                shlex.split(command), cwd=str(self._root), capture_output=True,
                text=True, timeout=timeout, check=False,
            )
            return proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired:
            return 124, "", f"timeout after {timeout}s"
        except (OSError, ValueError) as exc:
            return 127, "", str(exc)

    @staticmethod
    def _confidence(checks: Sequence[CheckResult], scope: VerificationScope) -> float:
        """Confidence tracks *evidence produced*, not layers attempted.

        Skipped layers contribute nothing. This keeps a run that skipped every
        test from reporting high confidence because nothing failed.
        """
        evidential = [c for c in checks if c.is_evidence]
        if not evidential:
            return 0.0
        passed = sum(1 for c in evidential if c.passed)
        base = passed / len(evidential)
        weight = {VerificationScope.TINY_PATCH: 0.6,
                  VerificationScope.CANDIDATE: 0.8,
                  VerificationScope.FINAL: 1.0}[scope]
        ran_tests = any(c.layer in (Layer.V5_TARGETED_TESTS, Layer.V6_RELATED_TESTS,
                                    Layer.V7_BROADER_TESTS) for c in evidential)
        return round(base * weight * (1.0 if ran_tests else 0.5), 4)


def _tool_missing(stdout: str, stderr: str) -> bool:
    blob = f"{stdout}\n{stderr}".lower()
    return any(marker in blob for marker in (
        "no module named", "command not found", "not recognized"))
```

---

## Cap. 11.2 — `vanguard/packages/apps/coding_max/recovery/failures.py`

**Status:** ARQUIVO NOVO (criar integralmente) · **217 linhas**

Taxonomia §25. Lê saída de verificação, trajetória e estado do repositório — **nunca** o relato do próprio modelo, que é o mais provável de estar confiantemente errado.

```python
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
```

---

## Cap. 11.3 — `vanguard/packages/apps/coding_max/recovery/policy.py`

**Status:** ARQUIVO NOVO (criar integralmente) · **222 linhas**

§26 imposto mecanicamente: *todo retry deve mudar o estado ou a estratégia*.

```python
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
```

---

## Cap. 11.4 — `vanguard/packages/apps/coding_max/routing/router.py`

**Status:** ARQUIVO NOVO (criar integralmente) · **148 linhas**

Envolve o `RoleAwareRouter`/`TierLadder` existente. O substrato já é dono de bandas e mecânica; o que faltava é a política papel + histórico → banda.

```python
"""Role-aware model routing and escalation (`spec §28`, `§29`).

This wraps the substrate's existing `RoleAwareRouter`/`TierLadder`
(`runtime/tier_escalation.py`) rather than replacing it. The substrate already
owns band definitions and escalation mechanics; what is missing is the
*policy* mapping a Coding Max role and failure history onto a band.

`spec §29`: *"Do not escalate unnecessarily."* Escalation therefore requires a
recorded reason and consumes budget; it is never the default response to a
single failure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence

__all__ = ["CodingRole", "ModelRouter", "ModelSelection"]


class CodingRole(str, Enum):
    """`spec §28` roles."""

    CLASSIFIER = "classifier"
    PLANNER = "planner"
    WORKER = "worker"
    REVIEWER = "reviewer"
    REPLANNER = "replanner"
    SUMMARIZER = "summarizer"


#: Default band per role. Cheap models handle mechanical synthesis; the worker
#: and reviewer get the strong band because that is where correctness is
#: decided. Classification is absent: it is deterministic and needs no model.
_DEFAULT_BAND: Mapping[CodingRole, str] = {
    CodingRole.CLASSIFIER: "cheap",
    CodingRole.SUMMARIZER: "cheap",
    CodingRole.PLANNER: "mid",
    CodingRole.REPLANNER: "mid",
    CodingRole.WORKER: "strong",
    CodingRole.REVIEWER: "strong",
}

_LADDER: tuple[str, ...] = ("cheap", "mid", "strong", "frontier")


@dataclass(frozen=True, slots=True)
class ModelSelection:
    role: CodingRole
    band: str
    model: str
    reason: str
    escalated: bool = False
    attempt: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role.value, "band": self.band, "model": self.model,
            "reason": self.reason, "escalated": self.escalated,
            "attempt": self.attempt,
        }


class ModelRouter:
    """`spec §28` selector over the substrate's band configuration."""

    def __init__(
        self,
        bands: Mapping[str, Sequence[str]],
        *,
        default_model: str = "",
        allow_escalation: bool = True,
    ) -> None:
        self._bands = {k: tuple(v) for k, v in bands.items()}
        self._default = default_model
        self._allow_escalation = allow_escalation
        self._escalations: dict[CodingRole, int] = {}

    def select(
        self,
        role: CodingRole,
        *,
        task_profile: Any = None,
        previous_failures: int = 0,
        budget_can_escalate: bool = True,
        force_band: str | None = None,
    ) -> ModelSelection:
        band = force_band or _DEFAULT_BAND.get(role, "mid")
        reason = f"default band for {role.value}"
        escalated = False

        # A high-complexity task starts the worker one rung up rather than
        # discovering the need after two wasted failures.
        complexity = float(getattr(task_profile, "estimated_complexity", 0.0) or 0.0)
        if role is CodingRole.WORKER and complexity >= 0.75 and not force_band:
            band = _up(band)
            reason = f"task complexity {complexity:.2f} warrants a stronger worker"

        # `spec §29`: escalate on *repeated* failure, never on the first.
        if (previous_failures >= 2 and self._allow_escalation
                and budget_can_escalate and not force_band):
            band = _up(band)
            escalated = True
            self._escalations[role] = self._escalations.get(role, 0) + 1
            reason = (f"{previous_failures} prior failures in role {role.value}; "
                      f"escalating one band")

        return ModelSelection(
            role=role, band=band, model=self._model_for(band),
            reason=reason, escalated=escalated,
            attempt=self._escalations.get(role, 0),
        )

    def stronger_model(self, selection: ModelSelection) -> ModelSelection:
        """One rung up from an existing selection (`spec §29` helper)."""
        band = _up(selection.band)
        if band == selection.band:
            return selection
        return ModelSelection(
            role=selection.role, band=band, model=self._model_for(band),
            reason="explicit escalation after repeated difficult failure",
            escalated=True, attempt=selection.attempt + 1,
        )

    def _model_for(self, band: str) -> str:
        """First configured model in the band, degrading down the ladder.

        Degrading rather than raising matters: a deployment that configures
        only two bands must still run, and a missing `frontier` entry should
        quietly resolve to the strongest band that exists.
        """
        for candidate in (band, *reversed(_LADDER[: _LADDER.index(band)]
                                          if band in _LADDER else ())):
            models = self._bands.get(candidate, ())
            if models:
                return models[0]
        return self._default

    def escalation_count(self) -> Mapping[str, int]:
        return {role.value: count for role, count in self._escalations.items()}


def _up(band: str) -> str:
    if band not in _LADDER:
        return band
    index = _LADDER.index(band)
    return _LADDER[min(index + 1, len(_LADDER) - 1)]
```

---

## Cap. 11.5 — `vanguard/packages/apps/coding_max/repo_map.py`

**Status:** ARQUIVO NOVO (criar integralmente) · **193 linhas**

Mapa compacto §10. Camada de **roteamento**, não cópia da árvore.

```python
"""The compact repository map (`spec §10`).

`spec §10`: *"Avoid dumping the full repository. Use hierarchical detail."*
The map is a routing layer, not a copy of the tree. It answers "where would
this kind of change live" in a few hundred tokens, so the worker can spend its
context on the two or three files that actually matter.

`recently_relevant_files` is the highest-value field and the cheapest: git
churn is a strong localisation prior, and it is the one signal no amount of
static analysis can reconstruct.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

from ...domain.canonicalisation.digest import digest_of
from .intelligence.composite import CompositeIntelligence
from .intelligence.protocol import RepoScope

__all__ = ["RepositoryMap", "build_repository_map"]

#: Rendering ceiling. A map that grows without bound stops being a map.
_MAX_MODULES = 24
_MAX_RECENT = 20
_MAX_SYMBOLS = 24


@dataclass(frozen=True, slots=True)
class RepositoryMap:
    """`spec §10` shape, with the identity fields needed to cache it."""

    languages: tuple[str, ...] = ()
    modules: tuple[Mapping[str, Any], ...] = ()
    entrypoints: tuple[str, ...] = ()
    test_roots: tuple[str, ...] = ()
    build_system: str = ""
    important_symbols: tuple[Mapping[str, Any], ...] = ()
    dependencies: tuple[str, ...] = ()
    recently_relevant_files: tuple[str, ...] = ()
    file_count: int = 0
    head: str = ""
    branch: str = ""
    dirty: bool = False

    def to_canonical_dict(self) -> dict[str, Any]:
        return {
            "languages": list(self.languages),
            "modules": [dict(m) for m in self.modules],
            "entrypoints": list(self.entrypoints),
            "testRoots": list(self.test_roots),
            "buildSystem": self.build_system,
            "importantSymbols": [dict(s) for s in self.important_symbols],
            "dependencies": list(self.dependencies),
            "recentlyRelevantFiles": list(self.recently_relevant_files),
            "fileCount": self.file_count,
            "head": self.head,
            "branch": self.branch,
            "dirty": self.dirty,
        }

    def digest(self) -> str:
        return digest_of(self.to_canonical_dict())

    def render(self, *, max_chars: int = 2400) -> str:
        """Token-bounded text for the ENVIRONMENT context layer.

        Written as terse structured prose rather than JSON: the same
        information costs roughly 40% fewer tokens without the quoting and
        bracket overhead, and models localise from it just as well.
        """
        lines: list[str] = ["# Repository map"]
        if self.branch or self.head:
            state = "dirty" if self.dirty else "clean"
            lines.append(f"branch={self.branch} head={self.head[:12]} tree={state}")
        if self.languages:
            lines.append(f"languages: {', '.join(self.languages[:6])}")
        if self.build_system:
            lines.append(f"build: {self.build_system}")
        lines.append(f"files: {self.file_count}")

        if self.modules:
            lines.append("\n## Modules (by size)")
            for module in self.modules[:_MAX_MODULES]:
                lines.append(f"  {module.get('path')}/  ({module.get('files')} files)")
        if self.test_roots:
            lines.append(f"\ntest roots: {', '.join(self.test_roots)}")
        if self.entrypoints:
            lines.append(f"entrypoints: {', '.join(self.entrypoints[:8])}")
        if self.recently_relevant_files:
            lines.append("\n## Recently changed (localisation prior)")
            for path in self.recently_relevant_files[:_MAX_RECENT]:
                lines.append(f"  {path}")
        if self.important_symbols:
            lines.append("\n## Notable symbols")
            for symbol in self.important_symbols[:_MAX_SYMBOLS]:
                lines.append(
                    f"  {symbol.get('name')} ({symbol.get('kind')}) "
                    f"— {symbol.get('path')}:{symbol.get('line')}"
                )
        if self.dependencies:
            lines.append(f"\nexternal deps: {', '.join(self.dependencies[:20])}")

        text = "\n".join(lines)
        if len(text) <= max_chars:
            return text
        # Truncate on a line boundary so the tail is never a half-path that
        # the model might read as a real file name.
        clipped = text[:max_chars].rsplit("\n", 1)[0]
        return clipped + "\n  … (map truncated)"


def build_repository_map(
    intelligence: CompositeIntelligence,
    *,
    focus_symbols: Sequence[str] = (),
    max_entries: int = 200,
) -> RepositoryMap:
    """Assemble the map from whatever providers are live.

    Every field degrades independently. A repository with no git history still
    gets languages, modules, and test roots; it simply loses the churn prior.
    """
    summary = intelligence.summarize(RepoScope(max_entries=max_entries))
    git = intelligence.git

    recent: tuple[str, ...] = ()
    head = branch = ""
    dirty = False
    if git.available():
        head, branch = git.head(), git.branch()
        dirty = git.dirty()
        # Working-tree changes rank above historical churn: they are this
        # run's own edits, and the worker almost always needs to see them.
        changed = git.changed_files()
        recent = tuple(dict.fromkeys(changed + git.recent_files(limit=_MAX_RECENT)))

    symbols: list[Mapping[str, Any]] = []
    for name in focus_symbols[:8]:
        for definition in intelligence.symbol(name).definitions[:3]:
            symbols.append({
                "name": definition.name, "kind": definition.kind.value,
                "path": definition.path, "line": definition.line,
                "signature": definition.signature,
            })

    return RepositoryMap(
        languages=summary.languages,
        modules=summary.modules[:_MAX_MODULES],
        entrypoints=summary.entrypoints,
        test_roots=summary.test_roots,
        build_system=summary.build_system,
        important_symbols=tuple(symbols[:_MAX_SYMBOLS]),
        dependencies=_declared_dependencies(intelligence.root),
        recently_relevant_files=recent[:_MAX_RECENT],
        file_count=summary.file_count,
        head=head, branch=branch, dirty=dirty,
    )


def _declared_dependencies(root: Path) -> tuple[str, ...]:
    """External dependencies as *declared*, not as resolved.

    Reading the manifest rather than the installed environment is deliberate:
    the harness needs to know what the project claims it needs, which is what
    a dependency task will edit. The installed set is a separate question and
    belongs to verification.
    """
    names: list[str] = []
    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        try:
            import tomllib

            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
            project = data.get("project", {})
            for entry in project.get("dependencies", []) or []:
                names.append(str(entry).split("[")[0].split(">")[0]
                             .split("<")[0].split("=")[0].strip())
        except Exception:  # noqa: BLE001 - a malformed manifest is not fatal
            pass
    package_json = root / "package.json"
    if package_json.is_file():
        try:
            import json

            data = json.loads(package_json.read_text(encoding="utf-8"))
            names.extend(sorted((data.get("dependencies") or {}).keys()))
        except Exception:  # noqa: BLE001
            pass
    return tuple(dict.fromkeys(name for name in names if name))
```

---

## Cap. 11.6 — `vanguard/packages/apps/coding_max/errors.py`

**Status:** ARQUIVO NOVO (criar integralmente) · **105 linhas**

Modelo de erro tipado §48. `recoverable` decide recuperação vs. terminação.

```python
"""Typed errors for the Coding Max harness (`spec §48`).

Every error carries a `recoverable` flag. The distinction is operational, not
decorative: a recoverable error is folded into the trajectory as evidence and
routed to the recovery policy, while a terminal error ends the run as an
*instrument* failure and must never be reported as a task verdict.

This mirrors the substrate's existing separation of the run-termination axis
from the evaluation axis (`RunTermination` in `agency/episode/state.py`).
"""

from __future__ import annotations

__all__ = [
    "BudgetExceeded",
    "CheckpointError",
    "CodingMaxError",
    "ContextCompilationError",
    "IntelligenceUnavailable",
    "ModelError",
    "PatchApplicationError",
    "RepositoryAccessError",
    "ToolExecutionError",
    "VerificationError",
]


class CodingMaxError(RuntimeError):
    """Base class. `recoverable` decides recovery vs. termination."""

    recoverable: bool = False

    def __init__(self, message: str, *, detail: str = "") -> None:
        super().__init__(message)
        self.detail = detail

    def to_dict(self) -> dict[str, object]:
        return {
            "error": type(self).__name__,
            "message": str(self),
            "detail": self.detail,
            "recoverable": self.recoverable,
        }


class RepositoryAccessError(CodingMaxError):
    """The workspace could not be read (missing, permission, not a repo)."""

    recoverable = False


class IntelligenceUnavailable(CodingMaxError):
    """A repository-intelligence provider is absent or timed out.

    Always recoverable: the composite provider degrades to the next provider
    in the ladder. This is the error that keeps LDA optional (`spec §9`).
    """

    recoverable = True


class ContextCompilationError(CodingMaxError):
    """Context could not be compiled within the declared token budget."""

    recoverable = True


class ToolExecutionError(CodingMaxError):
    """A tool ran and failed in a way the worker may react to."""

    recoverable = True


class PatchApplicationError(CodingMaxError):
    """A patch did not apply against current repository state."""

    recoverable = True


class VerificationError(CodingMaxError):
    """The verification pipeline itself failed (not: checks reported failures).

    A failing *check* is a `VerificationResult` with `passed=False`; it is data.
    This exception means the pipeline could not produce a verdict at all.
    """

    recoverable = True


class ModelError(CodingMaxError):
    """A provider call failed. Recoverable while a fallback tier remains."""

    recoverable = True


class BudgetExceeded(CodingMaxError):
    """A budget dimension is exhausted. Terminal for the current strategy."""

    recoverable = False


class CheckpointError(CodingMaxError):
    """A checkpoint could not be captured or restored."""

    recoverable = False
```

---

## Cap. 11.7 — `vanguard/packages/apps/coding_max/__init__.py`

**Status:** ARQUIVO NOVO (criar integralmente) · **18 linhas**

Superfície pública do pacote.

```python
"""AETHER Coding Max harness — an outer-layer composition over the Vanguard substrate.

Nothing in this package holds authority. Effects are proposed and dispatched
through `Kernel.dispatch` exactly as any other agent's are (`spec §40`); this
package supplies classification, retrieval, planning, verification, and
recovery *policy* around that unchanged path.
"""

from __future__ import annotations

from .errors import CodingMaxError
from .profile import RepoSignals, TaskClassifier, TaskProfile, TaskType, WorkflowKind
from .repo_map import RepositoryMap, build_repository_map

__all__ = [
    "CodingMaxError", "RepoSignals", "RepositoryMap", "TaskClassifier",
    "TaskProfile", "TaskType", "WorkflowKind", "build_repository_map",
]
```

---

## Cap. 11.8 — O predicado que impede fraude de verificação

```python
    @property
    def is_evidence(self) -> bool:
        """Whether this result can support a success claim.

        A skipped layer or one that never ran a command proves nothing. This
        is the guard against `spec §58`'s "fake test results".
        """
        return not self.skipped and self.exit_code is not None
```

Propaga-se ao veredito:

```python
        evidential = [c for c in checks if c.is_evidence]
        passed = not failures and bool(evidential)    # exige evidência POSITIVA
```

E à confiança:

```python
        evidential = [c for c in checks if c.is_evidence]
        if not evidential:
            return 0.0
```

Verificado no repositório real — sintaxe passou, nenhum teste rodou:

```
passed True  conf 0.3        ← não 1.0
  V1_syntax          True  exit=0
  V5_targeted_tests  True  skip  "no tests mapped to the changed target"
```

E com pytest real falhando:

```
verify pass=False conf=0.4
  [('V1_syntax',True,ran), ('V3_lint',True,skipped), ('V5_targeted_tests',False,ran)]
```

---

## Cap. 11.9 — Ferramenta ausente ≠ falha de tarefa

```python
        # A missing optional tool is not a task failure. Reporting it as one
        # would make lint availability decide task outcomes.
        if tolerate_missing and exit_code != 0 and _tool_missing(stdout, stderr):
            return CheckResult(layer=layer, passed=True, skipped=True,
                               command=command, skip_reason="tool not installed")
```

Sem isso, um deployment sem `ruff` reprovaria toda tarefa. Note que o resultado
é `skipped=True`, logo `is_evidence=False` — ele não passa a *contar* como
evidência de sucesso, apenas deixa de contar como falha.

---

## Cap. 11.10 — Ordem do classificador: estrutura antes de texto

```python
        # -- structural classes, checked before any output parsing --------
        # These describe the *shape* of the trajectory and are more reliable
        # than log text, which often reports a symptom of an earlier cause.
```

Um `AssertionError` no log é verdadeiro em quase toda falha. Se ele fosse
checado primeiro, absorveria `REPEATED_REASONING_FAILURE`, `STALE_MEMORY` e
`REGRESSION` — as três classes que têm remédio específico.

Desambiguação adicional:

```python
                # A test failure with no edits yet is not a patch problem;
                # it is the reproduction step working as intended.
                if (failure_class is FailureClass.TEST_FAILURE
                        and signals.distinct_files_edited == 0):
                    return FailureVerdict(FailureClass.WRONG_HYPOTHESIS, 0.6, ...)
```

Verificado:

```
turns 9/1                        -> BUDGET_PRESSURE
repeated_proposal_digests=3      -> REPEATED_REASONING_FAILURE
previously_passing_now_failing=2 -> REGRESSION
search_hits_last=0, edits=0      -> INSUFFICIENT_CONTEXT
```

---

## Cap. 11.11 — A escada de recuperação, verificada

`RecoveryPolicy.select` nunca repete estratégia gasta:

```python
            # `spec §26`: a retry that repeats a spent strategy is not a
            # recovery, so an already-tried action is skipped rather than
            # re-issued with a different label.
            if action in self._history:
                continue
```

Execução real:

```
WRONG_FILE                 -> expand_search         kind=request_context   alt=1
WRONG_FILE                 -> replan                kind=revise_plan       alt=0
BAD_PATCH                  -> rollback_and_review   kind=delegate          rev=0
REPEATED_REASONING_FAILURE -> escalate_model        kind=retry             esc=0
BUDGET_PRESSURE            -> enter_completion_mode kind=conclude
```

Nunca repete → escala → entra em modo de conclusão. **Loop infinito é
estruturalmente impossível.**

### Nada aqui inventa um directive kind

```python
#: Which `StrategyDirective` kind carries each action to the runtime. The
#: kinds are fixed by `ports/meta_controller.py::DIRECTIVE_KINDS`; nothing here
#: may invent one, which is what keeps this a policy plugin.
```

---

## Cap. 11.12 — Router: escala em falha repetida, nunca na primeira

```python
        # `spec §29`: escalate on *repeated* failure, never on the first.
        if (previous_failures >= 2 and self._allow_escalation
                and budget_can_escalate and not force_band):
```

E degrada em vez de levantar:

```python
    def _model_for(self, band: str) -> str:
        """First configured model in the band, degrading down the ladder.

        Degrading rather than raising matters: a deployment that configures
        only two bands must still run, and a missing `frontier` entry should
        quietly resolve to the strongest band that exists.
        """
```

Verificado:

```
classifier                -> cheap    gpt-4o-mini
worker (default)          -> strong   claude-opus
worker (complexity 0.85)  -> frontier claude-opus-thinking  "complexity warrants stronger"
worker (3 prior failures) -> frontier claude-opus-thinking  escalated=True
```

`CLASSIFIER` mapeia para `cheap` mas na prática **nunca é chamado**: a
classificação é determinística. A linha existe para que um deployment que
queira um classificador auxiliar saiba onde ele iria.

---

## Cap. 11.13 — Inventário final

| Arquivo | Linhas | Wave |
|---|---|---|
| `adapters/bindings/repo.py` | 302 | 5 |
| `apps/coding_max/artifacts.py` | 264 | 5 |
| `apps/coding_max/harness.py` | 462 | 6 |
| `apps/coding_max/intelligence/native.py` | 440 | 7 |
| `apps/coding_max/intelligence/composite.py` | 387 | 7 |
| `apps/coding_max/profile.py` | 394 | 8 |
| `apps/coding_max/controller.py` | 449 | 8 |
| `apps/coding_max/intelligence/protocol.py` | 262 | 9 |
| `apps/coding_max/intelligence/gitprov.py` | 199 | 9 |
| `apps/coding_max/intelligence/lda.py` | 257 | 9 |
| `apps/coding_max/context/scoring.py` | 128 | 10 |
| `apps/coding_max/context/progressive.py` | 217 | 10 |
| `apps/coding_max/planning/todo.py` | 266 | 10 |
| `apps/coding_max/planning/planner.py` | 302 | 10 |
| `apps/coding_max/verification/pipeline.py` | 324 | 11 |
| `apps/coding_max/recovery/failures.py` | 217 | 11 |
| `apps/coding_max/recovery/policy.py` | 222 | 11 |
| `apps/coding_max/routing/router.py` | 148 | 11 |
| `apps/coding_max/repo_map.py` | 193 | 11 |
| `apps/coding_max/errors.py` | 105 | 11 |
| `__init__.py` × 6 | ~85 | 11 |

**Arquivos do framework modificados: 4** — `bindings/base.py`,
`bindings/__init__.py`, `runtime/wiring.py`, `manifests/registry.json`.

**Mudanças em kernel, ports, domain, agency/episode: ZERO.**

---

## Cap. 11.14 — Ordem completa de aplicação

```
1.  apps/coding_max/errors.py
2.  apps/coding_max/profile.py
3.  apps/coding_max/intelligence/{protocol,native,gitprov,lda,composite,__init__}.py
4.  apps/coding_max/repo_map.py
5.  apps/coding_max/context/{scoring,progressive,__init__}.py
6.  apps/coding_max/planning/{todo,planner,__init__}.py
7.  apps/coding_max/verification/{pipeline,__init__}.py
8.  apps/coding_max/recovery/{failures,policy,__init__}.py
9.  apps/coding_max/routing/{router,__init__}.py
10. apps/coding_max/controller.py
11. apps/coding_max/artifacts.py
12. apps/coding_max/harness.py
13. apps/coding_max/__init__.py
14. adapters/bindings/repo.py
15. DIFF adapters/bindings/base.py
16. DIFF adapters/bindings/__init__.py
17. DIFF runtime/wiring.py            <- antes dos manifests
18. manifests/vg-code-{max,balanced,fast}/*
19. DIFF manifests/registry.json
20. Verificar: Runtime.compose() nos três presets
```
