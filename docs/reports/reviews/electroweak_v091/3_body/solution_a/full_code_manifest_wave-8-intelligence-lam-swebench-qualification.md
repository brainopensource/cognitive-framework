---
id: report.electroweak.3_body.solution_a.full_code_manifest_wave-8-intelligence-lam-swebench-qualification
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

# Full Code Manifest — Wave 8: LDA/Atlas, LAM e Qualificação SWE-bench

## 0. Objetivo

Fechar CM-11/CM-16/CM-17 e transformar capacidade em evidência: provider externo opcional de repository intelligence, experiment adapter LAM sem answer leakage, runner real que aplica patches em checkouts isolados, executa evaluator externo e produz resultados ligados à trajectory.

## 1. Regras absolutas

- Resposta não vazia não é sucesso.
- `grounded` e `verified` nunca derivam do texto do modelo.
- Dry-run não produz benchmark result.
- Patch deve existir fisicamente.
- Evaluator deve rodar fora do agente.
- Toda row aponta para task, subject, patch, tests, model route, cost e trajectory.
- SWE-bench claim somente com protocolo oficial aplicável.

## 2. Novo arquivo: `packs/code-default/coding_max/lda_adapter.py`

```python
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .intelligence import RepositoryMap, SearchHit

@dataclass(frozen=True, slots=True)
class LdaConfig:
    executable: str = "lda"
    timeout_seconds: float = 10.0
    max_results: int = 50

class LdaUnavailable(RuntimeError): pass

class LdaRepositoryIntelligence:
    def __init__(self, root: Path, config: LdaConfig = LdaConfig()) -> None:
        self.root = root.resolve()
        self.config = config

    def available(self) -> bool:
        try:
            row = self._call(("health", "--json"))
            return row.get("status") == "ok" and int(row.get("entityCount", 0)) > 0
        except (LdaUnavailable, ValueError):
            return False

    def search(self, query: str, *, limit: int = 20) -> tuple[SearchHit, ...]:
        row = self._call(("search", "--query", query, "--limit", str(min(limit, self.config.max_results)), "--json"))
        return tuple(SearchHit(
            path=str(item["path"]), line=int(item.get("line", 1)),
            excerpt=str(item.get("excerpt", ""))[:300],
            score=float(item.get("score", 0.0)), provider="lda",
        ) for item in row.get("results", ()))

    def symbol(self, name: str, *, limit: int = 20) -> tuple[SearchHit, ...]:
        row = self._call(("symbol", "--name", name, "--limit", str(limit), "--json"))
        return tuple(SearchHit(str(i["path"]), int(i.get("line", 1)), str(i.get("symbol", name)), float(i.get("score", 1.0)), "lda") for i in row.get("results", ()))

    def tests_for(self, target: str, *, limit: int = 20) -> tuple[SearchHit, ...]:
        row = self._call(("tests", "--target", target, "--limit", str(limit), "--json"))
        return tuple(SearchHit(str(i["path"]), int(i.get("line", 1)), "test relation", float(i.get("score", 1.0)), "lda") for i in row.get("results", ()))

    def summarize(self) -> RepositoryMap:
        row = self._call(("map", "--json"))
        return RepositoryMap(
            tuple(row.get("languages", ())), tuple(row.get("modules", ())),
            tuple(row.get("entrypoints", ())), tuple(row.get("testRoots", ())),
            tuple(row.get("buildSystems", ())), int(row.get("fileCount", 0)),
        )

    def _call(self, args: Sequence[str]):
        try:
            completed = subprocess.run(
                (self.config.executable, *args), cwd=self.root,
                capture_output=True, text=True, timeout=self.config.timeout_seconds, check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise LdaUnavailable(str(exc)) from exc
        if completed.returncode != 0:
            raise LdaUnavailable(completed.stderr[-1000:])
        row = json.loads(completed.stdout)
        if not isinstance(row, dict):
            raise ValueError("LDA response must be object")
        return row
```

## 3. Novo arquivo: `packs/code-default/coding_max/intelligence_router.py`

```python
from __future__ import annotations

class ResilientIntelligence:
    def __init__(self, native, enriched=None) -> None:
        self.native = native
        self.enriched = enriched

    def _provider(self):
        return self.enriched if self.enriched is not None and self.enriched.available() else self.native

    def search(self, query, *, limit=20):
        try: return self._provider().search(query, limit=limit)
        except Exception: return self.native.search(query, limit=limit)

    def symbol(self, name, *, limit=20):
        try: return self._provider().symbol(name, limit=limit)
        except Exception: return self.native.symbol(name, limit=limit)

    def tests_for(self, target, *, limit=20):
        try: return self._provider().tests_for(target, limit=limit)
        except Exception: return self.native.tests_for(target, limit=limit)

    def summarize(self):
        try: return self._provider().summarize()
        except Exception: return self.native.summarize()
```

## 4. Novo arquivo: `benchmarks/coding_max/task_protocol.py`

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

@dataclass(frozen=True, slots=True)
class BenchmarkTask:
    task_id: str
    repository: str
    base_commit: str
    problem_statement: str
    evaluator_command: tuple[str, ...]
    timeout_seconds: int
    metadata: Mapping[str, object]

    def validate(self) -> None:
        if not self.task_id or not self.repository or len(self.base_commit) < 7:
            raise ValueError("task identity incomplete")
        if not self.evaluator_command:
            raise ValueError("external evaluator required")
        if self.timeout_seconds <= 0:
            raise ValueError("positive timeout required")
```

## 5. Novo arquivo: `benchmarks/coding_max/runner.py`

```python
from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

from .task_protocol import BenchmarkTask

@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    task_id: str
    base_commit: str
    patch_digest: str | None
    evaluator_exit_code: int | None
    resolved: bool
    trajectory_digest: str | None
    model_route: str
    prompt_tokens: int | None
    completion_tokens: int | None
    cost_usd: float | None
    latency_seconds: float
    instrument_error: str | None = None

class CodingBenchmarkRunner:
    def __init__(self, run_agent: Callable[[Path, BenchmarkTask], object]) -> None:
        self.run_agent = run_agent

    def run(self, task: BenchmarkTask) -> BenchmarkResult:
        task.validate()
        started = time.monotonic()
        with tempfile.TemporaryDirectory(prefix="aether-benchmark-") as tmp:
            root = Path(tmp) / "repo"
            clone = subprocess.run(
                ("git", "clone", "--no-checkout", task.repository, str(root)),
                capture_output=True, text=True, check=False, timeout=300,
            )
            if clone.returncode != 0:
                return self._instrument(task, started, "clone_failed")
            checkout = subprocess.run(
                ("git", "-C", str(root), "checkout", "--detach", task.base_commit),
                capture_output=True, text=True, check=False, timeout=120,
            )
            if checkout.returncode != 0:
                return self._instrument(task, started, "checkout_failed")

            agent_result = self.run_agent(root, task)
            diff = subprocess.run(
                ("git", "-C", str(root), "diff", "--binary", "--no-ext-diff"),
                capture_output=True, text=False, check=False, timeout=30,
            ).stdout
            patch_digest = "sha256:" + hashlib.sha256(diff).hexdigest() if diff else None
            if patch_digest is None:
                return BenchmarkResult(
                    task.task_id, task.base_commit, None, None, False,
                    getattr(agent_result, "trajectory_digest", None),
                    getattr(agent_result, "model_route", "unknown"),
                    getattr(agent_result, "prompt_tokens", None),
                    getattr(agent_result, "completion_tokens", None),
                    getattr(agent_result, "cost_usd", None),
                    time.monotonic() - started, "no_patch",
                )

            evaluation = subprocess.run(
                task.evaluator_command, cwd=root, capture_output=True, text=True,
                check=False, timeout=task.timeout_seconds,
            )
            return BenchmarkResult(
                task.task_id, task.base_commit, patch_digest, evaluation.returncode,
                evaluation.returncode == 0,
                getattr(agent_result, "trajectory_digest", None),
                getattr(agent_result, "model_route", "unknown"),
                getattr(agent_result, "prompt_tokens", None),
                getattr(agent_result, "completion_tokens", None),
                getattr(agent_result, "cost_usd", None),
                time.monotonic() - started, None,
            )

    def _instrument(self, task, started, reason):
        return BenchmarkResult(
            task.task_id, task.base_commit, None, None, False, None, "unavailable",
            None, None, None, time.monotonic() - started, reason,
        )
```

## 6. Novo arquivo: `benchmarks/coding_max/preflight.py`

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

@dataclass(frozen=True, slots=True)
class PreflightReport:
    valid: bool
    errors: tuple[str, ...]

def validate_tasks(tasks: Sequence[object]) -> PreflightReport:
    errors = []
    ids = set()
    for index, task in enumerate(tasks):
        try: task.validate()
        except Exception as exc: errors.append(f"task[{index}]: {exc}")
        if task.task_id in ids: errors.append(f"duplicate task id {task.task_id}")
        ids.add(task.task_id)
        if task.metadata.get("answer") or task.metadata.get("gold_patch"):
            errors.append(f"{task.task_id}: answer leakage field present")
    return PreflightReport(not errors, tuple(errors))
```

## 7. LAM adapter integration

```diff
@@ vanguard/packages/adapters/models/lam.py
+class LamExperimentMetadata:
+    dataset_digest: str
+    task_id: str
+    mock_protocol_version: str
+    answer_visibility: str = "hidden"
+
+def assert_no_answer_leakage(request):
+    forbidden = {"gold_patch", "answer", "oracle_output", "expected_diff"}
+    leaked = forbidden.intersection(request.keys())
+    if leaked:
+        raise ValueError(f"LAM request leaks benchmark fields: {sorted(leaked)}")
```

## 8. Resultado schema

```json
{
  "api": "aether.coding-benchmark-result/1",
  "taskId": "...",
  "baseCommit": "...",
  "patchDigest": "sha256:...",
  "evaluatorExitCode": 0,
  "resolved": true,
  "trajectoryDigest": "sha256:...",
  "modelRoute": "provider:model",
  "tokens": {"prompt": 0, "completion": 0},
  "costUsd": 0.0,
  "latencySeconds": 0.0,
  "instrumentError": null
}
```

## 9. Testes obrigatórios

```python
class BenchmarkTruthTests(unittest.TestCase):
    def test_nonempty_model_text_without_patch_is_unresolved(self): ...
    def test_patch_without_evaluator_is_unresolved(self): ...
    def test_zero_evaluator_exit_is_resolved(self): ...
    def test_dry_run_never_emits_result_row(self): ...
    def test_every_result_links_trajectory(self): ...
    def test_gold_patch_field_fails_preflight(self): ...
    def test_duplicate_task_id_fails_preflight(self): ...
    def test_checkout_uses_exact_base_commit(self): ...
    def test_evaluator_timeout_is_instrument_error(self): ...
    def test_cost_is_observed_not_synthesized(self): ...
```

## 10. Experimental design

### 10.1 Baseline
- Single-agent coding-balanced.
- Fixed model route.
- Native repository intelligence.
- No mutation, no branch search.

### 10.2 Treatments
- Progressive context.
- LDA enrichment.
- Adaptive route.
- Reflex controller.
- Branch search.
- Strategy capsule.

### 10.3 Metrics
- resolved rate with confidence interval.
- pass@1; pass@k only when k preregistered.
- tokens/task and cost/resolved task.
- latency p50/p95.
- patch apply rate.
- zero-test rejection rate.
- recovery success after first failure.
- context precision proxy.
- regression rate.
- instrument error rate.

### 10.4 Statistics
- Paired tasks across baseline/treatment.
- Bootstrap confidence intervals.
- McNemar for paired binary resolution.
- Wilcoxon/sign test for cost/latency where appropriate.
- Holm correction across multiple treatments.
- Report effect sizes, not only p-values.
- No post-hoc threshold changes.

## 11. Qualification ladder

| Gate | Dataset | Purpose | Promotion |
|---|---|---|---|
| Q0 | unit fixtures | mechanism | all deterministic tests |
| Q1 | local smoke | real patch/test | 4/4 causal flows |
| Q2 | heldout internal | strategy selection | preregistered lift |
| Q3 | SWE-bench subset | compatibility | no protocol deviation |
| Q4 | official SWE-bench Verified | claim | official evaluator |
| Q5 | SWE-bench Pro | hard generalization | externally reproducible |

## 12. Anti-cheating falsifiers

| ID | Falsifier | Expected |
|---|---|---|
| BENCH-001 | response text counted as pass | reject/instrument_error |
| BENCH-002 | model says tests passed | reject/instrument_error |
| BENCH-003 | filename mention counted grounded | reject/instrument_error |
| BENCH-004 | dry-run emits tokens | reject/instrument_error |
| BENCH-005 | synthetic latency | reject/instrument_error |
| BENCH-006 | gold patch in prompt | reject/instrument_error |
| BENCH-007 | oracle output in context | reject/instrument_error |
| BENCH-008 | task reused for training and heldout | reject/instrument_error |
| BENCH-009 | evaluator runs inside agent | reject/instrument_error |
| BENCH-010 | patch not applied to checkout | reject/instrument_error |
| BENCH-011 | wrong base commit | reject/instrument_error |
| BENCH-012 | dirty preexisting tree | reject/instrument_error |
| BENCH-013 | two attempts reported pass@1 | reject/instrument_error |
| BENCH-014 | missing trajectory | reject/instrument_error |
| BENCH-015 | missing model identity | reject/instrument_error |
| BENCH-016 | missing cost marked zero | reject/instrument_error |
| BENCH-017 | timeout marked task failure | reject/instrument_error |
| BENCH-018 | network failure marked unresolved task | reject/instrument_error |
| BENCH-019 | LDA stale index accepted | reject/instrument_error |
| BENCH-020 | index entity count zero accepted | reject/instrument_error |

## 13. Ordem de implementação

1. LDA adapter + health/fallback.
2. LDA provenance artifact.
3. LAM leakage guard.
4. Task schema/preflight.
5. Isolated checkout runner.
6. Real patch extraction.
7. External evaluator.
8. Result/trajectory linkage.
9. Deterministic/local matrix.
10. Preregistered canary.
11. Larger sample only if gate met.
12. Official evaluation before claim.

## 14. Checklist por superfície

- [ ] Q-R001 — `LdaRepositoryIntelligence.available`: timeout bounded.
- [ ] Q-R002 — `LdaRepositoryIntelligence.available`: fallback deterministic.
- [ ] Q-R003 — `LdaRepositoryIntelligence.available`: provenance retained.
- [ ] Q-R004 — `LdaRepositoryIntelligence.available`: stale index rejected.
- [ ] Q-R005 — `LdaRepositoryIntelligence.available`: empty index rejected.
- [ ] Q-R006 — `LdaRepositoryIntelligence.available`: exact subject pinned.
- [ ] Q-R007 — `LdaRepositoryIntelligence.available`: no answer leakage.
- [ ] Q-R008 — `LdaRepositoryIntelligence.available`: no synthetic metrics.
- [ ] Q-R009 — `LdaRepositoryIntelligence.available`: patch physically observed.
- [ ] Q-R010 — `LdaRepositoryIntelligence.available`: evaluator external.
- [ ] Q-R011 — `LdaRepositoryIntelligence.available`: trajectory linked.
- [ ] Q-R012 — `LdaRepositoryIntelligence.available`: model route linked.
- [ ] Q-R013 — `LdaRepositoryIntelligence.available`: cost nullable not fabricated.
- [ ] Q-R014 — `LdaRepositoryIntelligence.available`: latency observed.
- [ ] Q-R015 — `LdaRepositoryIntelligence.available`: instrument errors separate.
- [ ] Q-R016 — `LdaRepositoryIntelligence.available`: offline unit test.
- [ ] Q-R017 — `LdaRepositoryIntelligence.available`: integration test.
- [ ] Q-R018 — `LdaRepositoryIntelligence.available`: adversarial test.
- [ ] Q-R019 — `LdaRepositoryIntelligence.available`: duplicate identity rejected.
- [ ] Q-R020 — `LdaRepositoryIntelligence.available`: schema versioned.
- [ ] Q-R021 — `LdaRepositoryIntelligence.available`: unknown fields policy.
- [ ] Q-R022 — `LdaRepositoryIntelligence.available`: retention policy.
- [ ] Q-R023 — `LdaRepositoryIntelligence.available`: secret safety.
- [ ] Q-R024 — `LdaRepositoryIntelligence.available`: reproducible command.
- [ ] Q-R025 — `LdaRepositoryIntelligence.available`: confidence interval.
- [ ] Q-R026 — `LdaRepositoryIntelligence.search`: timeout bounded.
- [ ] Q-R027 — `LdaRepositoryIntelligence.search`: fallback deterministic.
- [ ] Q-R028 — `LdaRepositoryIntelligence.search`: provenance retained.
- [ ] Q-R029 — `LdaRepositoryIntelligence.search`: stale index rejected.
- [ ] Q-R030 — `LdaRepositoryIntelligence.search`: empty index rejected.
- [ ] Q-R031 — `LdaRepositoryIntelligence.search`: exact subject pinned.
- [ ] Q-R032 — `LdaRepositoryIntelligence.search`: no answer leakage.
- [ ] Q-R033 — `LdaRepositoryIntelligence.search`: no synthetic metrics.
- [ ] Q-R034 — `LdaRepositoryIntelligence.search`: patch physically observed.
- [ ] Q-R035 — `LdaRepositoryIntelligence.search`: evaluator external.
- [ ] Q-R036 — `LdaRepositoryIntelligence.search`: trajectory linked.
- [ ] Q-R037 — `LdaRepositoryIntelligence.search`: model route linked.
- [ ] Q-R038 — `LdaRepositoryIntelligence.search`: cost nullable not fabricated.
- [ ] Q-R039 — `LdaRepositoryIntelligence.search`: latency observed.
- [ ] Q-R040 — `LdaRepositoryIntelligence.search`: instrument errors separate.
- [ ] Q-R041 — `LdaRepositoryIntelligence.search`: offline unit test.
- [ ] Q-R042 — `LdaRepositoryIntelligence.search`: integration test.
- [ ] Q-R043 — `LdaRepositoryIntelligence.search`: adversarial test.
- [ ] Q-R044 — `LdaRepositoryIntelligence.search`: duplicate identity rejected.
- [ ] Q-R045 — `LdaRepositoryIntelligence.search`: schema versioned.
- [ ] Q-R046 — `LdaRepositoryIntelligence.search`: unknown fields policy.
- [ ] Q-R047 — `LdaRepositoryIntelligence.search`: retention policy.
- [ ] Q-R048 — `LdaRepositoryIntelligence.search`: secret safety.
- [ ] Q-R049 — `LdaRepositoryIntelligence.search`: reproducible command.
- [ ] Q-R050 — `LdaRepositoryIntelligence.search`: confidence interval.
- [ ] Q-R051 — `LdaRepositoryIntelligence.symbol`: timeout bounded.
- [ ] Q-R052 — `LdaRepositoryIntelligence.symbol`: fallback deterministic.
- [ ] Q-R053 — `LdaRepositoryIntelligence.symbol`: provenance retained.
- [ ] Q-R054 — `LdaRepositoryIntelligence.symbol`: stale index rejected.
- [ ] Q-R055 — `LdaRepositoryIntelligence.symbol`: empty index rejected.
- [ ] Q-R056 — `LdaRepositoryIntelligence.symbol`: exact subject pinned.
- [ ] Q-R057 — `LdaRepositoryIntelligence.symbol`: no answer leakage.
- [ ] Q-R058 — `LdaRepositoryIntelligence.symbol`: no synthetic metrics.
- [ ] Q-R059 — `LdaRepositoryIntelligence.symbol`: patch physically observed.
- [ ] Q-R060 — `LdaRepositoryIntelligence.symbol`: evaluator external.
- [ ] Q-R061 — `LdaRepositoryIntelligence.symbol`: trajectory linked.
- [ ] Q-R062 — `LdaRepositoryIntelligence.symbol`: model route linked.
- [ ] Q-R063 — `LdaRepositoryIntelligence.symbol`: cost nullable not fabricated.
- [ ] Q-R064 — `LdaRepositoryIntelligence.symbol`: latency observed.
- [ ] Q-R065 — `LdaRepositoryIntelligence.symbol`: instrument errors separate.
- [ ] Q-R066 — `LdaRepositoryIntelligence.symbol`: offline unit test.
- [ ] Q-R067 — `LdaRepositoryIntelligence.symbol`: integration test.
- [ ] Q-R068 — `LdaRepositoryIntelligence.symbol`: adversarial test.
- [ ] Q-R069 — `LdaRepositoryIntelligence.symbol`: duplicate identity rejected.
- [ ] Q-R070 — `LdaRepositoryIntelligence.symbol`: schema versioned.
- [ ] Q-R071 — `LdaRepositoryIntelligence.symbol`: unknown fields policy.
- [ ] Q-R072 — `LdaRepositoryIntelligence.symbol`: retention policy.
- [ ] Q-R073 — `LdaRepositoryIntelligence.symbol`: secret safety.
- [ ] Q-R074 — `LdaRepositoryIntelligence.symbol`: reproducible command.
- [ ] Q-R075 — `LdaRepositoryIntelligence.symbol`: confidence interval.
- [ ] Q-R076 — `LdaRepositoryIntelligence.tests_for`: timeout bounded.
- [ ] Q-R077 — `LdaRepositoryIntelligence.tests_for`: fallback deterministic.
- [ ] Q-R078 — `LdaRepositoryIntelligence.tests_for`: provenance retained.
- [ ] Q-R079 — `LdaRepositoryIntelligence.tests_for`: stale index rejected.
- [ ] Q-R080 — `LdaRepositoryIntelligence.tests_for`: empty index rejected.
- [ ] Q-R081 — `LdaRepositoryIntelligence.tests_for`: exact subject pinned.
- [ ] Q-R082 — `LdaRepositoryIntelligence.tests_for`: no answer leakage.
- [ ] Q-R083 — `LdaRepositoryIntelligence.tests_for`: no synthetic metrics.
- [ ] Q-R084 — `LdaRepositoryIntelligence.tests_for`: patch physically observed.
- [ ] Q-R085 — `LdaRepositoryIntelligence.tests_for`: evaluator external.
- [ ] Q-R086 — `LdaRepositoryIntelligence.tests_for`: trajectory linked.
- [ ] Q-R087 — `LdaRepositoryIntelligence.tests_for`: model route linked.
- [ ] Q-R088 — `LdaRepositoryIntelligence.tests_for`: cost nullable not fabricated.
- [ ] Q-R089 — `LdaRepositoryIntelligence.tests_for`: latency observed.
- [ ] Q-R090 — `LdaRepositoryIntelligence.tests_for`: instrument errors separate.
- [ ] Q-R091 — `LdaRepositoryIntelligence.tests_for`: offline unit test.
- [ ] Q-R092 — `LdaRepositoryIntelligence.tests_for`: integration test.
- [ ] Q-R093 — `LdaRepositoryIntelligence.tests_for`: adversarial test.
- [ ] Q-R094 — `LdaRepositoryIntelligence.tests_for`: duplicate identity rejected.
- [ ] Q-R095 — `LdaRepositoryIntelligence.tests_for`: schema versioned.
- [ ] Q-R096 — `LdaRepositoryIntelligence.tests_for`: unknown fields policy.
- [ ] Q-R097 — `LdaRepositoryIntelligence.tests_for`: retention policy.
- [ ] Q-R098 — `LdaRepositoryIntelligence.tests_for`: secret safety.
- [ ] Q-R099 — `LdaRepositoryIntelligence.tests_for`: reproducible command.
- [ ] Q-R100 — `LdaRepositoryIntelligence.tests_for`: confidence interval.
- [ ] Q-R101 — `ResilientIntelligence.search`: timeout bounded.
- [ ] Q-R102 — `ResilientIntelligence.search`: fallback deterministic.
- [ ] Q-R103 — `ResilientIntelligence.search`: provenance retained.
- [ ] Q-R104 — `ResilientIntelligence.search`: stale index rejected.
- [ ] Q-R105 — `ResilientIntelligence.search`: empty index rejected.
- [ ] Q-R106 — `ResilientIntelligence.search`: exact subject pinned.
- [ ] Q-R107 — `ResilientIntelligence.search`: no answer leakage.
- [ ] Q-R108 — `ResilientIntelligence.search`: no synthetic metrics.
- [ ] Q-R109 — `ResilientIntelligence.search`: patch physically observed.
- [ ] Q-R110 — `ResilientIntelligence.search`: evaluator external.
- [ ] Q-R111 — `ResilientIntelligence.search`: trajectory linked.
- [ ] Q-R112 — `ResilientIntelligence.search`: model route linked.
- [ ] Q-R113 — `ResilientIntelligence.search`: cost nullable not fabricated.
- [ ] Q-R114 — `ResilientIntelligence.search`: latency observed.
- [ ] Q-R115 — `ResilientIntelligence.search`: instrument errors separate.
- [ ] Q-R116 — `ResilientIntelligence.search`: offline unit test.
- [ ] Q-R117 — `ResilientIntelligence.search`: integration test.
- [ ] Q-R118 — `ResilientIntelligence.search`: adversarial test.
- [ ] Q-R119 — `ResilientIntelligence.search`: duplicate identity rejected.
- [ ] Q-R120 — `ResilientIntelligence.search`: schema versioned.
- [ ] Q-R121 — `ResilientIntelligence.search`: unknown fields policy.
- [ ] Q-R122 — `ResilientIntelligence.search`: retention policy.
- [ ] Q-R123 — `ResilientIntelligence.search`: secret safety.
- [ ] Q-R124 — `ResilientIntelligence.search`: reproducible command.
- [ ] Q-R125 — `ResilientIntelligence.search`: confidence interval.
- [ ] Q-R126 — `BenchmarkTask.validate`: timeout bounded.
- [ ] Q-R127 — `BenchmarkTask.validate`: fallback deterministic.
- [ ] Q-R128 — `BenchmarkTask.validate`: provenance retained.
- [ ] Q-R129 — `BenchmarkTask.validate`: stale index rejected.
- [ ] Q-R130 — `BenchmarkTask.validate`: empty index rejected.
- [ ] Q-R131 — `BenchmarkTask.validate`: exact subject pinned.
- [ ] Q-R132 — `BenchmarkTask.validate`: no answer leakage.
- [ ] Q-R133 — `BenchmarkTask.validate`: no synthetic metrics.
- [ ] Q-R134 — `BenchmarkTask.validate`: patch physically observed.
- [ ] Q-R135 — `BenchmarkTask.validate`: evaluator external.
- [ ] Q-R136 — `BenchmarkTask.validate`: trajectory linked.
- [ ] Q-R137 — `BenchmarkTask.validate`: model route linked.
- [ ] Q-R138 — `BenchmarkTask.validate`: cost nullable not fabricated.
- [ ] Q-R139 — `BenchmarkTask.validate`: latency observed.
- [ ] Q-R140 — `BenchmarkTask.validate`: instrument errors separate.
- [ ] Q-R141 — `BenchmarkTask.validate`: offline unit test.
- [ ] Q-R142 — `BenchmarkTask.validate`: integration test.
- [ ] Q-R143 — `BenchmarkTask.validate`: adversarial test.
- [ ] Q-R144 — `BenchmarkTask.validate`: duplicate identity rejected.
- [ ] Q-R145 — `BenchmarkTask.validate`: schema versioned.
- [ ] Q-R146 — `BenchmarkTask.validate`: unknown fields policy.
- [ ] Q-R147 — `BenchmarkTask.validate`: retention policy.
- [ ] Q-R148 — `BenchmarkTask.validate`: secret safety.
- [ ] Q-R149 — `BenchmarkTask.validate`: reproducible command.
- [ ] Q-R150 — `BenchmarkTask.validate`: confidence interval.
- [ ] Q-R151 — `validate_tasks`: timeout bounded.
- [ ] Q-R152 — `validate_tasks`: fallback deterministic.
- [ ] Q-R153 — `validate_tasks`: provenance retained.
- [ ] Q-R154 — `validate_tasks`: stale index rejected.
- [ ] Q-R155 — `validate_tasks`: empty index rejected.
- [ ] Q-R156 — `validate_tasks`: exact subject pinned.
- [ ] Q-R157 — `validate_tasks`: no answer leakage.
- [ ] Q-R158 — `validate_tasks`: no synthetic metrics.
- [ ] Q-R159 — `validate_tasks`: patch physically observed.
- [ ] Q-R160 — `validate_tasks`: evaluator external.
- [ ] Q-R161 — `validate_tasks`: trajectory linked.
- [ ] Q-R162 — `validate_tasks`: model route linked.
- [ ] Q-R163 — `validate_tasks`: cost nullable not fabricated.
- [ ] Q-R164 — `validate_tasks`: latency observed.
- [ ] Q-R165 — `validate_tasks`: instrument errors separate.
- [ ] Q-R166 — `validate_tasks`: offline unit test.
- [ ] Q-R167 — `validate_tasks`: integration test.
- [ ] Q-R168 — `validate_tasks`: adversarial test.
- [ ] Q-R169 — `validate_tasks`: duplicate identity rejected.
- [ ] Q-R170 — `validate_tasks`: schema versioned.
- [ ] Q-R171 — `validate_tasks`: unknown fields policy.
- [ ] Q-R172 — `validate_tasks`: retention policy.
- [ ] Q-R173 — `validate_tasks`: secret safety.
- [ ] Q-R174 — `validate_tasks`: reproducible command.
- [ ] Q-R175 — `validate_tasks`: confidence interval.
- [ ] Q-R176 — `CodingBenchmarkRunner.run`: timeout bounded.
- [ ] Q-R177 — `CodingBenchmarkRunner.run`: fallback deterministic.
- [ ] Q-R178 — `CodingBenchmarkRunner.run`: provenance retained.
- [ ] Q-R179 — `CodingBenchmarkRunner.run`: stale index rejected.
- [ ] Q-R180 — `CodingBenchmarkRunner.run`: empty index rejected.
- [ ] Q-R181 — `CodingBenchmarkRunner.run`: exact subject pinned.
- [ ] Q-R182 — `CodingBenchmarkRunner.run`: no answer leakage.
- [ ] Q-R183 — `CodingBenchmarkRunner.run`: no synthetic metrics.
- [ ] Q-R184 — `CodingBenchmarkRunner.run`: patch physically observed.
- [ ] Q-R185 — `CodingBenchmarkRunner.run`: evaluator external.
- [ ] Q-R186 — `CodingBenchmarkRunner.run`: trajectory linked.
- [ ] Q-R187 — `CodingBenchmarkRunner.run`: model route linked.
- [ ] Q-R188 — `CodingBenchmarkRunner.run`: cost nullable not fabricated.
- [ ] Q-R189 — `CodingBenchmarkRunner.run`: latency observed.
- [ ] Q-R190 — `CodingBenchmarkRunner.run`: instrument errors separate.
- [ ] Q-R191 — `CodingBenchmarkRunner.run`: offline unit test.
- [ ] Q-R192 — `CodingBenchmarkRunner.run`: integration test.
- [ ] Q-R193 — `CodingBenchmarkRunner.run`: adversarial test.
- [ ] Q-R194 — `CodingBenchmarkRunner.run`: duplicate identity rejected.
- [ ] Q-R195 — `CodingBenchmarkRunner.run`: schema versioned.
- [ ] Q-R196 — `CodingBenchmarkRunner.run`: unknown fields policy.
- [ ] Q-R197 — `CodingBenchmarkRunner.run`: retention policy.
- [ ] Q-R198 — `CodingBenchmarkRunner.run`: secret safety.
- [ ] Q-R199 — `CodingBenchmarkRunner.run`: reproducible command.
- [ ] Q-R200 — `CodingBenchmarkRunner.run`: confidence interval.
- [ ] Q-R201 — `CodingBenchmarkRunner._instrument`: timeout bounded.
- [ ] Q-R202 — `CodingBenchmarkRunner._instrument`: fallback deterministic.
- [ ] Q-R203 — `CodingBenchmarkRunner._instrument`: provenance retained.
- [ ] Q-R204 — `CodingBenchmarkRunner._instrument`: stale index rejected.
- [ ] Q-R205 — `CodingBenchmarkRunner._instrument`: empty index rejected.
- [ ] Q-R206 — `CodingBenchmarkRunner._instrument`: exact subject pinned.
- [ ] Q-R207 — `CodingBenchmarkRunner._instrument`: no answer leakage.
- [ ] Q-R208 — `CodingBenchmarkRunner._instrument`: no synthetic metrics.
- [ ] Q-R209 — `CodingBenchmarkRunner._instrument`: patch physically observed.
- [ ] Q-R210 — `CodingBenchmarkRunner._instrument`: evaluator external.
- [ ] Q-R211 — `CodingBenchmarkRunner._instrument`: trajectory linked.
- [ ] Q-R212 — `CodingBenchmarkRunner._instrument`: model route linked.
- [ ] Q-R213 — `CodingBenchmarkRunner._instrument`: cost nullable not fabricated.
- [ ] Q-R214 — `CodingBenchmarkRunner._instrument`: latency observed.
- [ ] Q-R215 — `CodingBenchmarkRunner._instrument`: instrument errors separate.
- [ ] Q-R216 — `CodingBenchmarkRunner._instrument`: offline unit test.
- [ ] Q-R217 — `CodingBenchmarkRunner._instrument`: integration test.
- [ ] Q-R218 — `CodingBenchmarkRunner._instrument`: adversarial test.
- [ ] Q-R219 — `CodingBenchmarkRunner._instrument`: duplicate identity rejected.
- [ ] Q-R220 — `CodingBenchmarkRunner._instrument`: schema versioned.
- [ ] Q-R221 — `CodingBenchmarkRunner._instrument`: unknown fields policy.
- [ ] Q-R222 — `CodingBenchmarkRunner._instrument`: retention policy.
- [ ] Q-R223 — `CodingBenchmarkRunner._instrument`: secret safety.
- [ ] Q-R224 — `CodingBenchmarkRunner._instrument`: reproducible command.
- [ ] Q-R225 — `CodingBenchmarkRunner._instrument`: confidence interval.
- [ ] Q-R226 — `assert_no_answer_leakage`: timeout bounded.
- [ ] Q-R227 — `assert_no_answer_leakage`: fallback deterministic.
- [ ] Q-R228 — `assert_no_answer_leakage`: provenance retained.
- [ ] Q-R229 — `assert_no_answer_leakage`: stale index rejected.
- [ ] Q-R230 — `assert_no_answer_leakage`: empty index rejected.
- [ ] Q-R231 — `assert_no_answer_leakage`: exact subject pinned.
- [ ] Q-R232 — `assert_no_answer_leakage`: no answer leakage.
- [ ] Q-R233 — `assert_no_answer_leakage`: no synthetic metrics.
- [ ] Q-R234 — `assert_no_answer_leakage`: patch physically observed.
- [ ] Q-R235 — `assert_no_answer_leakage`: evaluator external.
- [ ] Q-R236 — `assert_no_answer_leakage`: trajectory linked.
- [ ] Q-R237 — `assert_no_answer_leakage`: model route linked.
- [ ] Q-R238 — `assert_no_answer_leakage`: cost nullable not fabricated.
- [ ] Q-R239 — `assert_no_answer_leakage`: latency observed.
- [ ] Q-R240 — `assert_no_answer_leakage`: instrument errors separate.
- [ ] Q-R241 — `assert_no_answer_leakage`: offline unit test.
- [ ] Q-R242 — `assert_no_answer_leakage`: integration test.
- [ ] Q-R243 — `assert_no_answer_leakage`: adversarial test.
- [ ] Q-R244 — `assert_no_answer_leakage`: duplicate identity rejected.
- [ ] Q-R245 — `assert_no_answer_leakage`: schema versioned.
- [ ] Q-R246 — `assert_no_answer_leakage`: unknown fields policy.
- [ ] Q-R247 — `assert_no_answer_leakage`: retention policy.
- [ ] Q-R248 — `assert_no_answer_leakage`: secret safety.
- [ ] Q-R249 — `assert_no_answer_leakage`: reproducible command.
- [ ] Q-R250 — `assert_no_answer_leakage`: confidence interval.
- [ ] Q-R251 — `result serializer`: timeout bounded.
- [ ] Q-R252 — `result serializer`: fallback deterministic.
- [ ] Q-R253 — `result serializer`: provenance retained.
- [ ] Q-R254 — `result serializer`: stale index rejected.
- [ ] Q-R255 — `result serializer`: empty index rejected.
- [ ] Q-R256 — `result serializer`: exact subject pinned.
- [ ] Q-R257 — `result serializer`: no answer leakage.
- [ ] Q-R258 — `result serializer`: no synthetic metrics.
- [ ] Q-R259 — `result serializer`: patch physically observed.
- [ ] Q-R260 — `result serializer`: evaluator external.
- [ ] Q-R261 — `result serializer`: trajectory linked.
- [ ] Q-R262 — `result serializer`: model route linked.
- [ ] Q-R263 — `result serializer`: cost nullable not fabricated.
- [ ] Q-R264 — `result serializer`: latency observed.
- [ ] Q-R265 — `result serializer`: instrument errors separate.
- [ ] Q-R266 — `result serializer`: offline unit test.
- [ ] Q-R267 — `result serializer`: integration test.
- [ ] Q-R268 — `result serializer`: adversarial test.
- [ ] Q-R269 — `result serializer`: duplicate identity rejected.
- [ ] Q-R270 — `result serializer`: schema versioned.
- [ ] Q-R271 — `result serializer`: unknown fields policy.
- [ ] Q-R272 — `result serializer`: retention policy.
- [ ] Q-R273 — `result serializer`: secret safety.
- [ ] Q-R274 — `result serializer`: reproducible command.
- [ ] Q-R275 — `result serializer`: confidence interval.
- [ ] Q-R276 — `qualification aggregator`: timeout bounded.
- [ ] Q-R277 — `qualification aggregator`: fallback deterministic.
- [ ] Q-R278 — `qualification aggregator`: provenance retained.
- [ ] Q-R279 — `qualification aggregator`: stale index rejected.
- [ ] Q-R280 — `qualification aggregator`: empty index rejected.
- [ ] Q-R281 — `qualification aggregator`: exact subject pinned.
- [ ] Q-R282 — `qualification aggregator`: no answer leakage.
- [ ] Q-R283 — `qualification aggregator`: no synthetic metrics.
- [ ] Q-R284 — `qualification aggregator`: patch physically observed.
- [ ] Q-R285 — `qualification aggregator`: evaluator external.
- [ ] Q-R286 — `qualification aggregator`: trajectory linked.
- [ ] Q-R287 — `qualification aggregator`: model route linked.
- [ ] Q-R288 — `qualification aggregator`: cost nullable not fabricated.
- [ ] Q-R289 — `qualification aggregator`: latency observed.
- [ ] Q-R290 — `qualification aggregator`: instrument errors separate.
- [ ] Q-R291 — `qualification aggregator`: offline unit test.
- [ ] Q-R292 — `qualification aggregator`: integration test.
- [ ] Q-R293 — `qualification aggregator`: adversarial test.
- [ ] Q-R294 — `qualification aggregator`: duplicate identity rejected.
- [ ] Q-R295 — `qualification aggregator`: schema versioned.
- [ ] Q-R296 — `qualification aggregator`: unknown fields policy.
- [ ] Q-R297 — `qualification aggregator`: retention policy.
- [ ] Q-R298 — `qualification aggregator`: secret safety.
- [ ] Q-R299 — `qualification aggregator`: reproducible command.
- [ ] Q-R300 — `qualification aggregator`: confidence interval.

## 15. Release evidence bundle

Deve conter: exact Git SHA/tree/parent, clean status, environment lock digests, task preregistration digest, runner digest, model/provider fingerprint, prompts/context artifacts, tool receipts, patch digest, evaluator stdout/stderr digests, trajectory digest, cost/tokens/latency, aggregate script digest e independent reproduction receipt.

## 16. Acceptance gates

- [ ] LDA desligado não reduz corretude.
- [ ] LDA indisponível faz fallback sem abortar task.
- [ ] LAM não recebe answer fields.
- [ ] Runner trabalha em checkout exato e limpo.
- [ ] No patch = unresolved.
- [ ] No evaluator = unresolved.
- [ ] Dry-run não entra no corpus.
- [ ] Result rows apontam trajectory.
- [ ] Canary segue número de tentativas preregistrado.
- [ ] Claims coincidem literalmente com protocolo executado.

## 17. Definition of Done

A onda fecha quando o harness produz patches e resultados reais, reprodutíveis e externamente avaliados; até lá existe capacidade de engenharia, não score SWE-bench. SOTA é uma conclusão experimental, nunca uma propriedade declarada do código.

- [ ] Q-X729 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X730 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X731 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X732 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X733 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X734 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X735 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X736 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X737 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X738 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X739 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X740 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X741 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X742 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X743 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X744 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X745 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X746 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X747 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X748 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X749 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X750 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X751 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X752 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X753 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X754 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X755 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X756 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X757 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X758 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X759 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X760 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X761 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X762 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X763 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X764 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X765 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X766 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X767 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X768 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X769 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X770 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X771 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X772 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X773 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X774 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X775 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X776 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X777 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X778 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X779 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X780 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X781 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X782 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X783 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X784 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X785 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X786 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X787 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X788 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X789 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X790 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X791 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X792 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X793 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X794 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X795 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X796 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X797 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X798 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X799 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X800 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X801 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X802 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X803 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X804 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X805 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X806 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X807 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X808 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X809 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X810 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X811 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X812 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X813 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X814 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X815 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X816 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X817 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X818 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X819 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X820 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X821 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X822 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X823 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X824 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X825 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X826 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X827 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X828 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X829 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X830 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X831 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X832 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X833 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X834 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X835 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X836 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X837 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X838 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X839 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X840 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X841 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X842 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X843 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X844 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X845 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X846 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X847 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X848 — Auditar obrigação experimental remanescente antes de publicar score.
- [ ] Q-X849 — Auditar obrigação experimental remanescente antes de publicar score.
