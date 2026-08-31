---
id: report.electroweak.3_body.solution_a.full_code_manifest_wave-3
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

# Full Code Manifest — Wave 3

## Escopo

Branch: `feat/beta-release_electroweak-v091`  
Baseline: `f242ced297216109736975376802f1e3dc4e29ce`

Esta onda implementa CM-05/CM-06/CM-07/CM-09/CM-17: verificação real, taxonomia de falhas, recovery não idêntico, roteamento escalável e a policy de workflow que compõe tudo sobre os efeitos do Vanguard.

## Loop entregue

```text
classify → fast|max → plan → execute through Vanguard → verify subprocess
                                      ↑                 ↓
                         route/escalate ← recover ← classify failure
```

## Invariantes

- Exit code zero com zero testes não é sucesso.
- Texto do modelo nunca constitui verificação.
- Timeout, dependency, patch, test, model e budget têm estados distintos.
- Repetir a mesma recuperação causa mudança de estratégia ou STOP.
- Model routing respeita indisponibilidade e budget remanescente.
- O workflow decide; efeitos continuam no dispatch/authorization/event ledger existente.

## Patch completo

```diff
diff --git a/packs/code-default/coding_max/__init__.py b/packs/code-default/coding_max/__init__.py
new file mode 100644
index 0000000..ffcc420
--- /dev/null
+++ b/packs/code-default/coding_max/__init__.py
@@ -0,0 +1,19 @@
+"""Adaptive coding-harness composition for the code-default domain pack."""
+
+from .classifier import TaskClassifier, TaskProfile
+from .context import CompiledContext, ContextCandidate, ProgressiveContextCompiler
+from .intelligence import NativeRepositoryIntelligence, RepositoryMap, SearchHit
+from .planning import Plan, Planner, TodoItem, TodoState, TodoStore
+from .recovery import Failure, FailureClassifier, RecoveryAction, RecoveryPolicy
+from .routing import ModelRoute, ModelRouter
+from .verification import LayeredVerifier, VerificationResult
+from .workflow import CodingMaxWorkflow, WorkflowDecision
+
+__all__ = [
+    "CodingMaxWorkflow", "CompiledContext", "ContextCandidate", "Failure",
+    "FailureClassifier", "LayeredVerifier", "ModelRoute", "ModelRouter",
+    "NativeRepositoryIntelligence", "Plan", "Planner",
+    "ProgressiveContextCompiler", "RecoveryAction", "RecoveryPolicy",
+    "RepositoryMap", "SearchHit", "TaskClassifier", "TaskProfile", "TodoItem",
+    "TodoState", "TodoStore", "VerificationResult", "WorkflowDecision",
+]

diff --git a/packs/code-default/coding_max/verification.py b/packs/code-default/coding_max/verification.py
new file mode 100644
index 0000000..75cacbb
--- /dev/null
+++ b/packs/code-default/coding_max/verification.py
@@ -0,0 +1,72 @@
+"""Real subprocess verification with explicit zero-test and timeout semantics."""
+
+from __future__ import annotations
+
+import re
+import subprocess
+import time
+from dataclasses import dataclass
+from pathlib import Path
+from typing import Sequence
+
+
+@dataclass(frozen=True, slots=True)
+class VerificationResult:
+    command: tuple[str, ...]
+    exit_code: int
+    test_count: int
+    duration_ms: int
+    stdout: str
+    stderr: str
+    timed_out: bool = False
+
+    @property
+    def passed(self) -> bool:
+        return self.exit_code == 0 and self.test_count > 0 and not self.timed_out
+
+
+class LayeredVerifier:
+    """Execute selected commands; never derive success from model prose."""
+
+    _COUNTS = (
+        re.compile(r"Ran\s+(\d+)\s+tests?", re.I),
+        re.compile(r"(\d+)\s+passed", re.I),
+        re.compile(r"tests?\s+(\d+)", re.I),
+    )
+
+    def __init__(self, root: Path, *, timeout_seconds: float = 120.0, output_limit: int = 32_000) -> None:
+        self.root = root.resolve()
+        self.timeout_seconds = timeout_seconds
+        self.output_limit = output_limit
+
+    @classmethod
+    def _test_count(cls, output: str) -> int:
+        return max((int(match.group(1)) for pattern in cls._COUNTS for match in pattern.finditer(output)), default=0)
+
+    def run(self, command: Sequence[str]) -> VerificationResult:
+        if not command:
+            raise ValueError("verification command must be non-empty")
+        started = time.monotonic()
+        try:
+            completed = subprocess.run(
+                tuple(command), cwd=self.root, capture_output=True, text=True,
+                timeout=self.timeout_seconds, check=False,
+            )
+            stdout, stderr = completed.stdout[-self.output_limit:], completed.stderr[-self.output_limit:]
+            output = stdout + "\n" + stderr
+            return VerificationResult(tuple(command), completed.returncode, self._test_count(output),
+                                      int((time.monotonic() - started) * 1000), stdout, stderr)
+        except subprocess.TimeoutExpired as exc:
+            stdout = (exc.stdout or "")[-self.output_limit:] if isinstance(exc.stdout, str) else ""
+            stderr = (exc.stderr or "")[-self.output_limit:] if isinstance(exc.stderr, str) else ""
+            return VerificationResult(tuple(command), 124, self._test_count(stdout + stderr),
+                                      int((time.monotonic() - started) * 1000), stdout, stderr, True)
+
+    def verify(self, commands: Sequence[Sequence[str]]) -> tuple[VerificationResult, ...]:
+        results: list[VerificationResult] = []
+        for command in commands:
+            result = self.run(command)
+            results.append(result)
+            if not result.passed:
+                break
+        return tuple(results)

diff --git a/packs/code-default/coding_max/recovery.py b/packs/code-default/coding_max/recovery.py
new file mode 100644
index 0000000..2da1650
--- /dev/null
+++ b/packs/code-default/coding_max/recovery.py
@@ -0,0 +1,84 @@
+"""Typed failure classification and bounded non-identical recovery."""
+
+from __future__ import annotations
+
+import re
+from dataclasses import dataclass
+from enum import Enum
+from typing import Sequence
+
+from .verification import VerificationResult
+
+
+class Failure(str, Enum):
+    CONTEXT = "context"
+    PATCH = "patch"
+    TEST = "test"
+    DEPENDENCY = "dependency"
+    TIMEOUT = "timeout"
+    MODEL = "model"
+    BUDGET = "budget"
+    UNKNOWN = "unknown"
+
+
+class RecoveryAction(str, Enum):
+    RETRIEVE_CONTEXT = "retrieve_context"
+    REBASE_PATCH = "rebase_patch"
+    TARGET_FAILURE = "target_failure"
+    REPAIR_ENVIRONMENT = "repair_environment"
+    NARROW_SCOPE = "narrow_scope"
+    ESCALATE_MODEL = "escalate_model"
+    STOP = "stop"
+
+
+@dataclass(frozen=True, slots=True)
+class FailureDecision:
+    failure: Failure
+    reason: str
+
+
+class FailureClassifier:
+    def classify(self, verification: VerificationResult | None, *, model_error: str = "") -> FailureDecision:
+        if model_error:
+            lowered = model_error.lower()
+            if "budget" in lowered or "quota" in lowered:
+                return FailureDecision(Failure.BUDGET, model_error)
+            if "timeout" in lowered:
+                return FailureDecision(Failure.TIMEOUT, model_error)
+            return FailureDecision(Failure.MODEL, model_error)
+        if verification is None:
+            return FailureDecision(Failure.CONTEXT, "no verification subject available")
+        if verification.timed_out:
+            return FailureDecision(Failure.TIMEOUT, "verification timed out")
+        output = (verification.stdout + "\n" + verification.stderr).lower()
+        if re.search(r"modulenotfound|importerror|dependency|could not resolve|no matching distribution", output):
+            return FailureDecision(Failure.DEPENDENCY, "dependency/import failure")
+        if re.search(r"patch.*(failed|reject)|invalid context|does not apply", output):
+            return FailureDecision(Failure.PATCH, "patch/context mismatch")
+        if verification.exit_code != 0:
+            return FailureDecision(Failure.TEST, f"verification exited {verification.exit_code}")
+        if verification.test_count == 0:
+            return FailureDecision(Failure.TEST, "zero tests executed")
+        return FailureDecision(Failure.UNKNOWN, "no recognized failure")
+
+
+class RecoveryPolicy:
+    _ACTIONS = {
+        Failure.CONTEXT: RecoveryAction.RETRIEVE_CONTEXT,
+        Failure.PATCH: RecoveryAction.REBASE_PATCH,
+        Failure.TEST: RecoveryAction.TARGET_FAILURE,
+        Failure.DEPENDENCY: RecoveryAction.REPAIR_ENVIRONMENT,
+        Failure.TIMEOUT: RecoveryAction.NARROW_SCOPE,
+        Failure.MODEL: RecoveryAction.ESCALATE_MODEL,
+        Failure.BUDGET: RecoveryAction.STOP,
+        Failure.UNKNOWN: RecoveryAction.ESCALATE_MODEL,
+    }
+
+    def select(self, failure: Failure, *, attempts: int, max_attempts: int,
+               previous: Sequence[RecoveryAction] = ()) -> RecoveryAction:
+        if attempts >= max_attempts or failure is Failure.BUDGET:
+            return RecoveryAction.STOP
+        action = self._ACTIONS[failure]
+        if previous and previous[-1] is action:
+            return RecoveryAction.ESCALATE_MODEL if action is not RecoveryAction.ESCALATE_MODEL else RecoveryAction.STOP
+        return action

diff --git a/packs/code-default/coding_max/routing.py b/packs/code-default/coding_max/routing.py
new file mode 100644
index 0000000..e8ee25b
--- /dev/null
+++ b/packs/code-default/coding_max/routing.py
@@ -0,0 +1,35 @@
+"""Declarative model routing with evidence-triggered escalation."""
+
+from __future__ import annotations
+
+from dataclasses import dataclass
+from typing import Sequence
+
+
+@dataclass(frozen=True, slots=True)
+class ModelRoute:
+    provider: str
+    model: str
+    tier: int
+    max_complexity: int = 5
+    max_tokens: int = 64_000
+
+
+class ModelRouter:
+    def __init__(self, routes: Sequence[ModelRoute]) -> None:
+        if not routes:
+            raise ValueError("at least one model route is required")
+        self.routes = tuple(sorted(routes, key=lambda r: r.tier))
+
+    def select(self, *, complexity: int, failed_attempts: int = 0,
+               unavailable: Sequence[str] = (), remaining_tokens: int = 64_000) -> ModelRoute:
+        denied = set(unavailable)
+        eligible = [r for r in self.routes if f"{r.provider}:{r.model}" not in denied
+                    and complexity <= r.max_complexity and remaining_tokens > 0]
+        if not eligible:
+            raise RuntimeError("no eligible model route")
+        index = min(max(0, failed_attempts), len(eligible) - 1)
+        route = eligible[index]
+        if remaining_tokens < min(1000, route.max_tokens // 8):
+            raise RuntimeError("insufficient token budget for selected route")
+        return route

diff --git a/packs/code-default/coding_max/workflow.py b/packs/code-default/coding_max/workflow.py
new file mode 100644
index 0000000..5bbadf2
--- /dev/null
+++ b/packs/code-default/coding_max/workflow.py
@@ -0,0 +1,53 @@
+"""Thin orchestration policy over existing AETHER execution primitives."""
+
+from __future__ import annotations
+
+from dataclasses import dataclass
+from typing import Sequence
+
+from .classifier import TaskClassifier, TaskProfile
+from .planning import Plan, Planner
+from .recovery import FailureClassifier, RecoveryAction, RecoveryPolicy
+from .routing import ModelRoute, ModelRouter
+from .verification import VerificationResult
+
+
+@dataclass(frozen=True, slots=True)
+class WorkflowDecision:
+    profile: TaskProfile
+    plan: Plan
+    route: ModelRoute
+    next_action: str
+    recovery: RecoveryAction | None = None
+
+
+class CodingMaxWorkflow:
+    """Decide next composition step; effects still execute through Vanguard."""
+
+    def __init__(self, routes: Sequence[ModelRoute], *, max_attempts: int = 4) -> None:
+        self.classifier = TaskClassifier()
+        self.planner = Planner()
+        self.router = ModelRouter(routes)
+        self.failure_classifier = FailureClassifier()
+        self.recovery_policy = RecoveryPolicy()
+        self.max_attempts = max_attempts
+
+    def start(self, task: str, *, repository_files: int, initial_hits: Sequence[str],
+              available_tests: Sequence[str]) -> WorkflowDecision:
+        profile = self.classifier.classify(task, repository_files=repository_files,
+                                           initial_hits=initial_hits, available_tests=available_tests)
+        plan = self.planner.create(task, has_tests=bool(available_tests), complex_task=not profile.fast_path)
+        route = self.router.select(complexity=profile.estimated_complexity)
+        return WorkflowDecision(profile, plan, route, "fast_worker" if profile.fast_path else "repository_intelligence")
+
+    def after_verification(self, current: WorkflowDecision, result: VerificationResult,
+                           *, attempts: int, previous: Sequence[RecoveryAction] = ()) -> WorkflowDecision:
+        if result.passed:
+            return WorkflowDecision(current.profile, current.plan, current.route, "complete")
+        failure = self.failure_classifier.classify(result)
+        recovery = self.recovery_policy.select(failure.failure, attempts=attempts,
+                                               max_attempts=self.max_attempts, previous=previous)
+        route = current.route
+        if recovery is RecoveryAction.ESCALATE_MODEL:
+            route = self.router.select(complexity=current.profile.estimated_complexity, failed_attempts=attempts)
+        return WorkflowDecision(current.profile, current.plan, route, recovery.value, recovery)

diff --git a/test/packs/code_default/test_coding_max.py b/test/packs/code_default/test_coding_max.py
new file mode 100644
index 0000000..aa996f6
--- /dev/null
+++ b/test/packs/code_default/test_coding_max.py
@@ -0,0 +1,120 @@
+from __future__ import annotations
+
+import importlib
+import sys
+import tempfile
+import unittest
+from pathlib import Path
+
+ROOT = Path(__file__).resolve().parents[3]
+PACK = ROOT / "packs" / "code-default"
+if str(PACK) not in sys.path:
+    sys.path.insert(0, str(PACK))
+
+from coding_max.classifier import TaskClassifier
+from coding_max.context import ContextCandidate, ProgressiveContextCompiler
+from coding_max.intelligence import NativeRepositoryIntelligence
+from coding_max.planning import Planner, TodoState, TodoStore
+from coding_max.recovery import Failure, FailureClassifier, RecoveryAction, RecoveryPolicy
+from coding_max.routing import ModelRoute, ModelRouter
+from coding_max.verification import LayeredVerifier, VerificationResult
+from coding_max.workflow import CodingMaxWorkflow
+
+
+class TaskAndPlanningTests(unittest.TestCase):
+    def test_pack_presets_are_explicit_and_loadable(self) -> None:
+        from load import list_presets, load_preset
+
+        self.assertEqual(list_presets(), ("coding-balanced", "coding-fast", "coding-max"))
+        self.assertEqual(load_preset("coding-max")["verification"]["required"], True)
+        with self.assertRaises(ValueError):
+            load_preset("../escape")
+
+    def test_simple_fix_uses_fast_path(self) -> None:
+        profile = TaskClassifier().classify("Fix a small typo", repository_files=20,
+                                            initial_hits=("a.py",), available_tests=("test_a.py",))
+        self.assertTrue(profile.fast_path)
+        self.assertEqual(profile.suggested_workflow, "fast")
+
+    def test_long_multi_surface_task_uses_max(self) -> None:
+        profile = TaskClassifier().classify("Implement a feature across modules", repository_files=6000,
+                                            initial_hits=("a", "b", "c", "d"), available_tests=())
+        self.assertFalse(profile.fast_path)
+
+    def test_todo_dependencies_and_terminal_reopen(self) -> None:
+        store = TodoStore(Planner().create("fix", has_tests=True, complex_task=False))
+        with self.assertRaises(ValueError):
+            store.transition("step-2", TodoState.ACTIVE)
+        store.transition("step-1", TodoState.ACTIVE)
+        store.transition("step-1", TodoState.DONE, evidence=("baseline.txt",))
+        store.transition("step-2", TodoState.ACTIVE)
+        self.assertEqual(store.plan.steps[1].status, TodoState.ACTIVE)
+
+
+class IntelligenceAndContextTests(unittest.TestCase):
+    def test_native_search_symbol_tests_and_map(self) -> None:
+        with tempfile.TemporaryDirectory() as tmp:
+            root = Path(tmp)
+            (root / "src").mkdir()
+            (root / "test").mkdir()
+            (root / "src" / "engine.py").write_text("def settle_budget():\n    return 1\n", encoding="utf-8")
+            (root / "test" / "test_engine.py").write_text("from src.engine import settle_budget\n", encoding="utf-8")
+            (root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
+            intel = NativeRepositoryIntelligence(root)
+            self.assertEqual(intel.search("settle budget")[0].path, "src/engine.py")
+            self.assertEqual(intel.symbol("settle_budget")[0].line, 1)
+            self.assertEqual(intel.tests_for("src/engine.py")[0].path, "test/test_engine.py")
+            self.assertIn("Python", intel.summarize().languages)
+
+    def test_context_is_deduped_ranked_and_bounded(self) -> None:
+        compiler = ProgressiveContextCompiler()
+        context = compiler.compile((
+            ContextCandidate("a", "x" * 80, 0.2),
+            ContextCandidate("a", "better", 2.0),
+            ContextCandidate("b", "y" * 80, 1.0),
+        ), token_budget=10)
+        self.assertEqual(tuple(c.key for c in context.selected), ("a",))
+        self.assertIn("b", context.dropped)
+
+
+class VerificationRecoveryRoutingTests(unittest.TestCase):
+    def test_verifier_rejects_zero_test_success(self) -> None:
+        with tempfile.TemporaryDirectory() as tmp:
+            result = LayeredVerifier(Path(tmp)).run((sys.executable, "-c", "print('ok')"))
+            self.assertEqual(result.exit_code, 0)
+            self.assertFalse(result.passed)
+
+    def test_verifier_accepts_observed_test_count(self) -> None:
+        with tempfile.TemporaryDirectory() as tmp:
+            result = LayeredVerifier(Path(tmp)).run((sys.executable, "-c", "print('3 passed')"))
+            self.assertTrue(result.passed)
+
+    def test_failure_and_non_identical_recovery(self) -> None:
+        result = VerificationResult(("pytest",), 1, 1, 2, "", "ModuleNotFoundError: x")
+        decision = FailureClassifier().classify(result)
+        self.assertEqual(decision.failure, Failure.DEPENDENCY)
+        policy = RecoveryPolicy()
+        first = policy.select(decision.failure, attempts=1, max_attempts=4)
+        second = policy.select(decision.failure, attempts=2, max_attempts=4, previous=(first,))
+        self.assertEqual(first, RecoveryAction.REPAIR_ENVIRONMENT)
+        self.assertEqual(second, RecoveryAction.ESCALATE_MODEL)
+
+    def test_router_escalates_and_respects_unavailable(self) -> None:
+        routes = (ModelRoute("local", "small", 1), ModelRoute("remote", "frontier", 2))
+        router = ModelRouter(routes)
+        self.assertEqual(router.select(complexity=2).model, "small")
+        self.assertEqual(router.select(complexity=2, failed_attempts=1).model, "frontier")
+        self.assertEqual(router.select(complexity=2, unavailable=("local:small",)).model, "frontier")
+
+    def test_workflow_completes_only_on_real_verification(self) -> None:
+        workflow = CodingMaxWorkflow((ModelRoute("fake", "small", 1), ModelRoute("fake", "large", 2)))
+        decision = workflow.start("Fix a small bug", repository_files=30,
+                                  initial_hits=("a.py",), available_tests=("test_a.py",))
+        passed = VerificationResult(("pytest",), 0, 1, 2, "1 passed", "")
+        self.assertEqual(workflow.after_verification(decision, passed, attempts=1).next_action, "complete")
+        zero = VerificationResult(("pytest",), 0, 0, 2, "", "")
+        self.assertNotEqual(workflow.after_verification(decision, zero, attempts=1).next_action, "complete")
+
+
+if __name__ == "__main__":
+    unittest.main()
```

## Validação observada

- 11 testes Coding Max: PASS.
- 52 testes do pack code-default: PASS.
- 6 testes focados de routing/repo-map/admission: PASS.
- Boundary: PASS (633 arquivos).
- TCB: PASS, 1386/1438 LOC; nenhuma linha adicionada ao TCB.
- Duplication: PASS.
- Secret scan: PASS.
- `git diff --check`: PASS.

## O que não é alegado

Não foi executado benchmark SWE-bench, canary real, full suite nem qualificação M-8/M-9. LAM, LDA/Atlas, reviewer multiagente, patch tournament e paralelismo competitivo não foram ativados porque exigem integração/evidência própria e não pertencem ao caminho crítico single-agent validado nesta entrega.
