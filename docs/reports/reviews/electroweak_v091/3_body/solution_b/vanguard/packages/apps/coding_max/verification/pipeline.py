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
