# Full Code Manifest — Wave 1

## Escopo

Branch: `feat/beta-release_electroweak-v091`  
Baseline: `f242ced297216109736975376802f1e3dc4e29ce`

Esta onda implementa CM-01/CM-04/CM-15 no pack `code-default`: classificação determinística, fast-path, plano/TODO explícito e presets externos, sem alterar o schema do harness ou o runtime.

## Decisões

- O classificador não consome modelo quando sinais determinísticos bastam.
- TODOs possuem dependências, transições terminais e evidência anexável.
- Presets são configurações do pack; não entram em `HarnessManifest`, preservando compatibilidade wire.
- Nenhuma mudança em kernel, domain, ports ou runtime.

## Patch completo

```diff
diff --git a/packs/code-default/load.py b/packs/code-default/load.py
index b7782ea..79fa400 100644
--- a/packs/code-default/load.py
+++ b/packs/code-default/load.py
@@ -26,9 +26,12 @@ __all__ = [
     "load_declared_entry",
     "load_entry",
     "load_harness",
+    "load_preset",
+    "list_presets",
 ]
 
 PACK_ROOT = Path(__file__).resolve().parent
+PRESET_ROOT = PACK_ROOT / "presets"
 
 
 def load_harness(path: Path | None = None) -> dict[str, Any]:
@@ -39,6 +42,26 @@ def load_harness(path: Path | None = None) -> dict[str, Any]:
     return data
 
 
+def list_presets(pack_root: Path | None = None) -> tuple[str, ...]:
+    """Return pack-local execution presets without extending harness wire schema."""
+    root = (pack_root or PACK_ROOT) / "presets"
+    return tuple(path.stem for path in sorted(root.glob("*.yaml")))
+
+
+def load_preset(name: str, pack_root: Path | None = None) -> dict[str, Any]:
+    """Load a bounded pack configuration; presets are not runtime identities."""
+    if not name or any(char not in "abcdefghijklmnopqrstuvwxyz0123456789-" for char in name):
+        raise ValueError("preset name must contain only lowercase letters, digits, and hyphens")
+    root = (pack_root or PACK_ROOT) / "presets"
+    target = root / f"{name}.yaml"
+    if not target.is_file():
+        raise KeyError(name)
+    data = load_yaml(target.read_text(encoding="utf-8"))
+    if not isinstance(data, dict) or data.get("api") != "mhf.preset/1" or data.get("id") != name:
+        raise ValueError(f"invalid preset {name}")
+    return data
+
+
 def discover_plugins(pack_root: Path | None = None) -> dict[str, dict[str, Any]]:
     root = pack_root or PACK_ROOT
     catalog = load_yaml((root / "plugin.yaml").read_text(encoding="utf-8"))

diff --git a/packs/code-default/coding_max/classifier.py b/packs/code-default/coding_max/classifier.py
new file mode 100644
index 0000000..2758830
--- /dev/null
+++ b/packs/code-default/coding_max/classifier.py
@@ -0,0 +1,95 @@
+"""Cheap deterministic task classification before model invocation."""
+
+from __future__ import annotations
+
+import re
+from dataclasses import dataclass
+from typing import Mapping, Sequence
+
+TASK_TYPES = (
+    "simple_fix", "complex_bug", "test_failure", "refactor", "feature",
+    "multi_file_feature", "dependency_issue", "repository_exploration",
+    "greenfield", "long_task", "unknown",
+)
+
+
+@dataclass(frozen=True, slots=True)
+class TaskProfile:
+    task_type: str
+    estimated_complexity: int
+    uncertainty: float
+    repo_familiarity: float
+    suggested_workflow: str
+    initial_budget: Mapping[str, int]
+    reasons: tuple[str, ...] = ()
+
+    @property
+    def fast_path(self) -> bool:
+        return self.estimated_complexity <= 2 and self.uncertainty < 0.55
+
+
+class TaskClassifier:
+    """Classify from task/repository signals without spending an LLM call."""
+
+    _RULES = (
+        ("test_failure", re.compile(r"\b(test|pytest|unittest|spec)\b.*\b(fail|error|broken)", re.I)),
+        ("dependency_issue", re.compile(r"\b(dependenc|lockfile|package|version conflict|import error)", re.I)),
+        ("refactor", re.compile(r"\b(refactor|rename|extract|restructure|cleanup)\b", re.I)),
+        ("repository_exploration", re.compile(r"\b(explain|understand|explore|map|where is)\b", re.I)),
+        ("greenfield", re.compile(r"\b(greenfield|from scratch|new project|scaffold)\b", re.I)),
+        ("complex_bug", re.compile(r"\b(race|deadlock|intermittent|distributed|corruption|complex bug)\b", re.I)),
+        ("feature", re.compile(r"\b(add|implement|create|feature|support)\b", re.I)),
+        ("simple_fix", re.compile(r"\b(fix|typo|small|simple|one[- ]line)\b", re.I)),
+    )
+
+    def classify(
+        self,
+        task: str,
+        *,
+        repository_files: int = 0,
+        initial_hits: Sequence[str] = (),
+        available_tests: Sequence[str] = (),
+    ) -> TaskProfile:
+        text = task.strip()
+        reasons: list[str] = []
+        task_type = "unknown"
+        for candidate, pattern in self._RULES:
+            if pattern.search(text):
+                task_type = candidate
+                reasons.append(f"keyword:{candidate}")
+                break
+
+        multi_file = len(set(initial_hits)) >= 4 or bool(re.search(r"\b(multi[- ]file|across modules)\b", text, re.I))
+        long_task = len(text) > 1200 or bool(re.search(r"\b(long[- ]running|migration|all sprints)\b", text, re.I))
+        if multi_file and task_type == "feature":
+            task_type = "multi_file_feature"
+            reasons.append("surface:multi_file")
+        if long_task:
+            task_type = "long_task"
+            reasons.append("scope:long_task")
+
+        complexity = 1
+        complexity += int(repository_files > 500)
+        complexity += int(repository_files > 5000)
+        complexity += int(multi_file)
+        complexity += int(task_type in {"complex_bug", "dependency_issue", "greenfield", "long_task"}) * 2
+        complexity += int(not available_tests)
+        complexity = min(complexity, 5)
+
+        uncertainty = 0.2
+        uncertainty += 0.25 if not initial_hits else 0.0
+        uncertainty += 0.2 if task_type == "unknown" else 0.0
+        uncertainty += 0.15 if not available_tests else 0.0
+        uncertainty = min(1.0, uncertainty)
+        familiarity = 0.8 if initial_hits else (0.4 if repository_files else 0.1)
+        workflow = "fast" if complexity <= 2 and uncertainty < 0.55 else "coding-max"
+        scale = 1 if workflow == "fast" else max(2, complexity)
+        return TaskProfile(
+            task_type=task_type,
+            estimated_complexity=complexity,
+            uncertainty=uncertainty,
+            repo_familiarity=familiarity,
+            suggested_workflow=workflow,
+            initial_budget={"turns": 4 * scale, "tokens": 8000 * scale, "tool_calls": 8 * scale},
+            reasons=tuple(reasons),
+        )

diff --git a/packs/code-default/coding_max/planning.py b/packs/code-default/coding_max/planning.py
new file mode 100644
index 0000000..75c93fd
--- /dev/null
+++ b/packs/code-default/coding_max/planning.py
@@ -0,0 +1,91 @@
+"""Mutable plan and explicit TODO state, serializable as engineering artifacts."""
+
+from __future__ import annotations
+
+from dataclasses import dataclass, field, replace
+from enum import Enum
+from typing import Iterable, Mapping
+
+
+class TodoState(str, Enum):
+    PENDING = "pending"
+    ACTIVE = "active"
+    BLOCKED = "blocked"
+    DONE = "done"
+    FAILED = "failed"
+    SKIPPED = "skipped"
+
+
+@dataclass(frozen=True, slots=True)
+class TodoItem:
+    id: str
+    description: str
+    dependencies: tuple[str, ...] = ()
+    status: TodoState = TodoState.PENDING
+    evidence: tuple[str, ...] = ()
+
+
+@dataclass(frozen=True, slots=True)
+class Plan:
+    objective: str
+    assumptions: tuple[str, ...]
+    steps: tuple[TodoItem, ...]
+    verification_strategy: tuple[str, ...]
+    risk_points: tuple[str, ...]
+
+    def complete(self) -> bool:
+        return bool(self.steps) and all(s.status in {TodoState.DONE, TodoState.SKIPPED} for s in self.steps)
+
+    def to_dict(self) -> dict[str, object]:
+        return {
+            "objective": self.objective,
+            "assumptions": list(self.assumptions),
+            "steps": [
+                {"id": s.id, "description": s.description, "dependencies": list(s.dependencies),
+                 "status": s.status.value, "evidence": list(s.evidence)} for s in self.steps
+            ],
+            "verificationStrategy": list(self.verification_strategy),
+            "riskPoints": list(self.risk_points),
+        }
+
+
+class Planner:
+    def create(self, objective: str, *, has_tests: bool, complex_task: bool) -> Plan:
+        descriptions = ["reproduce or establish baseline", "localize implementation owner"]
+        if complex_task:
+            descriptions.append("validate assumptions and change surface")
+        descriptions.extend(["apply minimal implementation", "run targeted verification"])
+        if complex_task:
+            descriptions.append("run bounded regression verification")
+        steps = tuple(TodoItem(f"step-{i + 1}", value, (f"step-{i}",) if i else ())
+                      for i, value in enumerate(descriptions))
+        return Plan(
+            objective=objective,
+            assumptions=(),
+            steps=steps,
+            verification_strategy=("targeted tests" if has_tests else "executable smoke check",),
+            risk_points=("no existing tests",) if not has_tests else (),
+        )
+
+
+class TodoStore:
+    """Pure transition manager; callers persist emitted plan snapshots/events."""
+
+    def __init__(self, plan: Plan) -> None:
+        self.plan = plan
+
+    def transition(self, item_id: str, status: TodoState, *, evidence: Iterable[str] = ()) -> Plan:
+        by_id: Mapping[str, TodoItem] = {item.id: item for item in self.plan.steps}
+        if item_id not in by_id:
+            raise KeyError(item_id)
+        item = by_id[item_id]
+        if status is TodoState.ACTIVE:
+            incomplete = [dep for dep in item.dependencies if by_id[dep].status is not TodoState.DONE]
+            if incomplete:
+                raise ValueError(f"dependencies not done: {', '.join(incomplete)}")
+        terminal = {TodoState.DONE, TodoState.FAILED, TodoState.SKIPPED}
+        if item.status in terminal and status is not TodoState.PENDING:
+            raise ValueError(f"terminal todo {item_id} must be reopened before transition")
+        changed = replace(item, status=status, evidence=item.evidence + tuple(evidence))
+        self.plan = replace(self.plan, steps=tuple(changed if step.id == item_id else step for step in self.plan.steps))
+        return self.plan

diff --git a/packs/code-default/presets/coding-fast.yaml b/packs/code-default/presets/coding-fast.yaml
new file mode 100644
index 0000000..f5d2474
--- /dev/null
+++ b/packs/code-default/presets/coding-fast.yaml
@@ -0,0 +1,14 @@
+api: mhf.preset/1
+id: coding-fast
+workflow: fast
+planning: false
+context:
+  progressive: true
+  token_budget: 8000
+verification:
+  required: true
+  layers: [targeted]
+recovery:
+  max_attempts: 2
+review: false
+parallelism: 1

diff --git a/packs/code-default/presets/coding-balanced.yaml b/packs/code-default/presets/coding-balanced.yaml
new file mode 100644
index 0000000..fcf68b8
--- /dev/null
+++ b/packs/code-default/presets/coding-balanced.yaml
@@ -0,0 +1,14 @@
+api: mhf.preset/1
+id: coding-balanced
+workflow: adaptive
+planning: true
+context:
+  progressive: true
+  token_budget: 24000
+verification:
+  required: true
+  layers: [targeted, affected]
+recovery:
+  max_attempts: 4
+review: conditional
+parallelism: 1

diff --git a/packs/code-default/presets/coding-max.yaml b/packs/code-default/presets/coding-max.yaml
new file mode 100644
index 0000000..0b2fdc4
--- /dev/null
+++ b/packs/code-default/presets/coding-max.yaml
@@ -0,0 +1,22 @@
+api: mhf.preset/1
+id: coding-max
+workflow: coding-max
+planning: true
+todo: persistent
+context:
+  progressive: true
+  hierarchical: true
+  cache: true
+  token_budget: 64000
+  repository_intelligence: native
+  external_provider: optional
+verification:
+  required: true
+  layers: [targeted, affected, regression]
+recovery:
+  classify_failure: true
+  max_attempts: 6
+  strategy_switch: true
+review: conditional
+checkpoints: true
+parallelism: conditional
```

## Validação observada

- `test.packs.code_default.test_coding_max`: 11 testes, PASS.
- `test/packs/code_default`: 52 testes, PASS.
- Boundary, TCB, duplication e secret scan: PASS.

## Aceitação desta onda

Classificação, plano/TODO e presets são executáveis e testados. Persistência durável continua delegada aos eventos/artifacts/checkpoints já existentes no Vanguard; este pack não cria uma segunda store.

