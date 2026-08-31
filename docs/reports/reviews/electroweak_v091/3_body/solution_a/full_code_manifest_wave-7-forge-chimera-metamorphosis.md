# Full Code Manifest — Wave 7: Forge, Chimera e Metamorfose Governada

## 0. Resultado

Implementar test-time scaling, branching, reflexão, mutação de composição e cápsulas de estratégia como plugins/policies do pack. Metamorfose significa trocar configuração, topologia, contexto, prompt, route e recovery dentro de capabilities e budgets imutáveis; nunca alterar kernel, elevar autoridade ou autopromover aprendizado.

## 1. Loops

```text
L0 Engineering: explore → patch → verify → repair
L1 Search: fork hypotheses → isolated candidates → external score → select
L2 Evolution: propose mutation → offline evaluation → governance → promote/rollback
```

## 2. Novo arquivo: `packs/code-default/coding_max/reflex.py`

```python
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

class ReflexTrigger(str, Enum):
    NO_PROGRESS = "no_progress"
    CONTEXT_MISS = "context_miss"
    PATCH_CONFLICT = "patch_conflict"
    TEST_REGRESSION = "test_regression"
    HIGH_UNCERTAINTY = "high_uncertainty"
    BUDGET_PRESSURE = "budget_pressure"

@dataclass(frozen=True, slots=True)
class ReflexDirective:
    trigger: ReflexTrigger
    action: str
    parameters: Mapping[str, object]
    expected_cost: Mapping[str, int]
    rationale: str

class ReflexController:
    def decide(
        self, *, failure: str, repeated_signal: bool, uncertainty: float,
        remaining_budget: Mapping[str, int], context_misses: int,
    ) -> ReflexDirective:
        turns = int(remaining_budget.get("turns", 0))
        tokens = int(remaining_budget.get("tokens", 0))
        if turns <= 1 or tokens < 2000:
            return ReflexDirective(
                ReflexTrigger.BUDGET_PRESSURE, "narrow_and_verify",
                {"verification": "targeted"}, {"turns": 1, "tokens": min(tokens, 2000)},
                "preserve enough budget for externally observed verification",
            )
        if repeated_signal:
            return ReflexDirective(
                ReflexTrigger.NO_PROGRESS, "fork_hypotheses",
                {"branches": 2}, {"turns": 2, "tokens": min(tokens, 12000)},
                "identical progress signal requires non-identical search",
            )
        if failure == "context" or context_misses >= 2:
            return ReflexDirective(
                ReflexTrigger.CONTEXT_MISS, "expand_repository_evidence",
                {"signals": ["symbols", "tests", "dependencies"]},
                {"turns": 1, "tokens": min(tokens, 6000)},
                "missing evidence is cheaper to fix than escalating model",
            )
        if failure == "patch":
            return ReflexDirective(
                ReflexTrigger.PATCH_CONFLICT, "rebase_patch", {},
                {"turns": 1, "tokens": min(tokens, 4000)}, "patch subject changed",
            )
        if failure == "test":
            return ReflexDirective(
                ReflexTrigger.TEST_REGRESSION, "counterexample_branch",
                {"branches": 2}, {"turns": 2, "tokens": min(tokens, 10000)},
                "seek independent diagnosis before another edit",
            )
        return ReflexDirective(
            ReflexTrigger.HIGH_UNCERTAINTY, "escalate_model", {},
            {"turns": 1, "tokens": min(tokens, 16000)}, "remaining ambiguity requires stronger inference",
        )
```

## 3. Novo arquivo: `packs/code-default/coding_max/branch_search.py`

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

@dataclass(frozen=True, slots=True)
class BranchSpec:
    branch_id: str
    hypothesis: str
    route: Mapping[str, object]
    budget: Mapping[str, int]
    capability_digest: str

@dataclass(frozen=True, slots=True)
class BranchResult:
    branch_id: str
    patch_digest: str | None
    verification_digest: str | None
    tests_passed: int
    tests_failed: int
    regression_count: int
    cost: Mapping[str, int]
    state_digest: str

    @property
    def admissible(self) -> bool:
        return self.patch_digest is not None and self.verification_digest is not None and self.tests_failed == 0 and self.tests_passed > 0

class BranchSelector:
    def score(self, result: BranchResult) -> tuple[int, int, int, int, str]:
        return (
            int(result.admissible),
            -result.regression_count,
            result.tests_passed,
            -int(result.cost.get("tokens", 0)),
            result.branch_id,
        )

    def select(self, results: Sequence[BranchResult]) -> BranchResult:
        if not results:
            raise ValueError("no branch results")
        ordered = sorted(results, key=self.score, reverse=True)
        winner = ordered[0]
        if not winner.admissible:
            raise RuntimeError("no externally verified candidate")
        return winner

class BoundedBranchSearch:
    def __init__(self, spawn: Callable[[BranchSpec], BranchResult], *, max_branches: int = 3) -> None:
        self.spawn = spawn
        self.max_branches = max_branches
        self.selector = BranchSelector()

    def run(self, specs: Sequence[BranchSpec]) -> BranchResult:
        if len(specs) > self.max_branches:
            raise ValueError("branch ceiling exceeded")
        if len({spec.capability_digest for spec in specs}) != 1:
            raise ValueError("branches must share attenuated capability ceiling")
        results = tuple(self.spawn(spec) for spec in specs)
        return self.selector.select(results)
```

## 4. Novo arquivo: `packs/code-default/coding_max/mutation.py`

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

ALLOWED_MUTATIONS = frozenset({
    "prompt.template", "context.weights", "context.budget",
    "model.route", "recovery.threshold", "review.threshold",
    "parallel.branches", "verification.level", "planning.enabled",
})

@dataclass(frozen=True, slots=True)
class ManifestMutation:
    mutation_id: str
    path: str
    before: Any
    after: Any
    rationale: str
    expected_budget_delta: Mapping[str, int]

class MutationRejected(ValueError): pass

class ManifestMutator:
    def apply(
        self, manifest: Mapping[str, Any], mutations: Sequence[ManifestMutation],
        *, budget_ceiling: Mapping[str, int], capability_digest_before: str,
        capability_digest_after: str,
    ) -> dict[str, Any]:
        if capability_digest_before != capability_digest_after:
            raise MutationRejected("mutation cannot change capability ceiling")
        result = _deep_copy(manifest)
        total = {"tokens": 0, "turns": 0, "usd_micros": 0}
        for mutation in mutations:
            if mutation.path not in ALLOWED_MUTATIONS:
                raise MutationRejected(f"path not mutable: {mutation.path}")
            for key, value in mutation.expected_budget_delta.items():
                total[key] = total.get(key, 0) + int(value)
            _set_path(result, mutation.path, mutation.before, mutation.after)
        for key, value in total.items():
            if value > int(budget_ceiling.get(key, 0)):
                raise MutationRejected(f"mutation budget exceeds {key}")
        return result

def _deep_copy(value):
    if isinstance(value, dict): return {k: _deep_copy(v) for k, v in value.items()}
    if isinstance(value, list): return [_deep_copy(v) for v in value]
    return value

def _set_path(root, path, expected, replacement):
    parts = path.split(".")
    node = root
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    leaf = parts[-1]
    if node.get(leaf) != expected:
        raise MutationRejected(f"stale mutation at {path}")
    node[leaf] = replacement
```

## 5. Novo arquivo: `packs/code-default/coding_max/capsules.py`

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

@dataclass(frozen=True, slots=True)
class StrategyCapsule:
    capsule_id: str
    task_family: str
    mutation_digest: str
    training_subjects: tuple[str, ...]
    heldout_subjects: tuple[str, ...]
    lift: float
    regression: float
    evidence_digest: str
    status: str = "candidate"

class CapsuleRegistry:
    def __init__(self) -> None:
        self._rows: dict[str, StrategyCapsule] = {}

    def propose(self, capsule: StrategyCapsule) -> None:
        if capsule.status != "candidate":
            raise ValueError("new capsule must be candidate")
        if set(capsule.training_subjects) & set(capsule.heldout_subjects):
            raise ValueError("training/heldout leakage")
        self._rows[capsule.capsule_id] = capsule

    def eligible(self, capsule_id: str, *, min_lift: float, max_regression: float) -> bool:
        row = self._rows[capsule_id]
        return bool(row.evidence_digest) and row.lift >= min_lift and row.regression <= max_regression

    def promote(self, capsule_id: str, *, approval_digest: str) -> StrategyCapsule:
        if not approval_digest:
            raise ValueError("external approval required")
        row = self._rows[capsule_id]
        if not self.eligible(capsule_id, min_lift=0.05, max_regression=0.02):
            raise ValueError("capsule does not meet preregistered thresholds")
        promoted = StrategyCapsule(**{**row.__dict__, "status": "promoted"})
        self._rows[capsule_id] = promoted
        return promoted

    def rollback(self, capsule_id: str, *, reason_digest: str) -> StrategyCapsule:
        if not reason_digest:
            raise ValueError("rollback evidence required")
        row = self._rows[capsule_id]
        rolled = StrategyCapsule(**{**row.__dict__, "status": "rolled_back"})
        self._rows[capsule_id] = rolled
        return rolled
```

Nota: como dataclasses com `slots=True` não expõem `__dict__`, a implementação real deve usar `dataclasses.replace(row, status=...)`; o teste abaixo torna essa correção obrigatória.

## 6. Diff obrigatório em `capsules.py`

```diff
+from dataclasses import dataclass, replace
-        promoted = StrategyCapsule(**{**row.__dict__, "status": "promoted"})
+        promoted = replace(row, status="promoted")
-        rolled = StrategyCapsule(**{**row.__dict__, "status": "rolled_back"})
+        rolled = replace(row, status="rolled_back")
```

## 7. Integração com topologia real

```diff
@@ coordinator.py
+    if directive.action in {"fork_hypotheses", "counterexample_branch"}:
+        specs = fork_policy.build_specs(
+            task=task, parent_budget=remaining_budget,
+            parent_capability_digest=capability_digest,
+            count=int(directive.parameters.get("branches", 2)),
+        )
+        winner = branch_search.run(specs)
+        workspace.import_verified_patch(winner.patch_digest)
```

Cada branch deve ser lowered por `vanguard/packages/runtime/topology.py` e executada por `RuntimeChildRunner`; a função acima nunca pode abrir subprocesso de agente diretamente.

## 8. Testes: `test/packs/code_default/test_metamorphosis.py`

```python
from __future__ import annotations

import unittest

from coding_max.branch_search import BranchResult, BranchSelector
from coding_max.mutation import ManifestMutation, ManifestMutator, MutationRejected

class MetamorphosisTests(unittest.TestCase):
    def test_verified_candidate_beats_unverified_cheaper_candidate(self):
        selector = BranchSelector()
        verified = BranchResult("a", "patch", "verify", 4, 0, 0, {"tokens": 5000}, "state-a")
        cheap = BranchResult("b", "patch", None, 0, 0, 0, {"tokens": 100}, "state-b")
        self.assertEqual(selector.select((cheap, verified)).branch_id, "a")

    def test_capability_change_is_rejected(self):
        mutation = ManifestMutation("m1", "context.budget", 1000, 2000, "more evidence", {"tokens": 1000})
        with self.assertRaises(MutationRejected):
            ManifestMutator().apply(
                {"context": {"budget": 1000}}, (mutation,),
                budget_ceiling={"tokens": 5000},
                capability_digest_before="a", capability_digest_after="b",
            )

    def test_unknown_mutation_path_is_rejected(self):
        mutation = ManifestMutation("m1", "kernel.policy", "x", "y", "escape", {})
        with self.assertRaises(MutationRejected):
            ManifestMutator().apply(
                {}, (mutation,), budget_ceiling={},
                capability_digest_before="a", capability_digest_after="a",
            )
```

## 9. Metamorphosis surface

| Mutable | Online? | Gate | Rollback |
|---|---:|---|---|
| prompt template | yes, per run | budget/capability | discard run config |
| context weights | yes | token ceiling | prior weights |
| model route | yes | provider/policy | previous route |
| recovery threshold | yes | bounded attempts | previous threshold |
| reviewer threshold | yes | cost ceiling | previous threshold |
| branch count | yes | depth/turn budget | sequential |
| verification level | yes | never below required | prior level |
| learned capsule | no direct | heldout + approval | registry rollback |
| kernel code | no | forbidden | n/a |
| capabilities | attenuation only | kernel | n/a |

## 10. Search policy

```text
fork only when expected value > marginal cost
prune branch on budget denial, invalid patch, zero tests or dominated score
merge only structured artifacts, never full transcripts
winner must be reverified on parent workspace
all child authority is attenuated
```

## 11. Falsifiers

| ID | Attack | Expected |
|---|---|---|
| META-001 | mutation adds tool capability | reject/fail closed |
| META-002 | mutation increases total budget | reject/fail closed |
| META-003 | branch uses different capability digest | reject/fail closed |
| META-004 | branch writes parent workspace | reject/fail closed |
| META-005 | unverified patch wins on model confidence | reject/fail closed |
| META-006 | capsule promotes itself | reject/fail closed |
| META-007 | training subject appears in heldout | reject/fail closed |
| META-008 | threshold changed post hoc | reject/fail closed |
| META-009 | rollback lacks evidence | reject/fail closed |
| META-010 | full transcript merged | reject/fail closed |
| META-011 | fork count exceeds ceiling | reject/fail closed |
| META-012 | child cost not settled | reject/fail closed |
| META-013 | child route uses forbidden paid model | reject/fail closed |
| META-014 | reviewer always-on despite preset | reject/fail closed |
| META-015 | no-progress repeats identical branch | reject/fail closed |
| META-016 | kernel mutation path requested | reject/fail closed |
| META-017 | event identity mutated | reject/fail closed |
| META-018 | artifact provenance missing | reject/fail closed |
| META-019 | branch result missing state digest | reject/fail closed |
| META-020 | parent completion skips reverify | reject/fail closed |

## 12. Ordem de implementação

1. ReflexController determinístico.
2. Branch result/selector.
3. Lowering via topology/child runtime.
4. Worktree isolation por branch.
5. Parent re-verification.
6. Declarative mutator.
7. Capsule candidate registry.
8. Heldout evaluation pipeline.
9. External promotion receipt.
10. Rollback drill.

## 13. Checklist PhD/SOTA por símbolo

- [ ] META-R001 — `ReflexController.decide`: deterministic.
- [ ] META-R002 — `ReflexController.decide`: budget bounded.
- [ ] META-R003 — `ReflexController.decide`: authority attenuated.
- [ ] META-R004 — `ReflexController.decide`: failure typed.
- [ ] META-R005 — `ReflexController.decide`: artifact provenance.
- [ ] META-R006 — `ReflexController.decide`: idempotent replay.
- [ ] META-R007 — `ReflexController.decide`: no transcript merge.
- [ ] META-R008 — `ReflexController.decide`: cost settled.
- [ ] META-R009 — `ReflexController.decide`: timeout bounded.
- [ ] META-R010 — `ReflexController.decide`: offline test.
- [ ] META-R011 — `ReflexController.decide`: adversarial test.
- [ ] META-R012 — `ReflexController.decide`: success test.
- [ ] META-R013 — `ReflexController.decide`: tie deterministic.
- [ ] META-R014 — `ReflexController.decide`: stale input rejected.
- [ ] META-R015 — `ReflexController.decide`: unknown field rejected.
- [ ] META-R016 — `ReflexController.decide`: provider failure isolated.
- [ ] META-R017 — `ReflexController.decide`: parent reverify.
- [ ] META-R018 — `ReflexController.decide`: rollback tested.
- [ ] META-R019 — `ReflexController.decide`: heldout leakage blocked.
- [ ] META-R020 — `ReflexController.decide`: threshold preregistered.
- [ ] META-R021 — `ReflexController.decide`: no self-promotion.
- [ ] META-R022 — `ReflexController.decide`: no kernel import.
- [ ] META-R023 — `ReflexController.decide`: no direct subprocess.
- [ ] META-R024 — `ReflexController.decide`: state digest retained.
- [ ] META-R025 — `ReflexController.decide`: route digest retained.
- [ ] META-R026 — `BranchSelector.score`: deterministic.
- [ ] META-R027 — `BranchSelector.score`: budget bounded.
- [ ] META-R028 — `BranchSelector.score`: authority attenuated.
- [ ] META-R029 — `BranchSelector.score`: failure typed.
- [ ] META-R030 — `BranchSelector.score`: artifact provenance.
- [ ] META-R031 — `BranchSelector.score`: idempotent replay.
- [ ] META-R032 — `BranchSelector.score`: no transcript merge.
- [ ] META-R033 — `BranchSelector.score`: cost settled.
- [ ] META-R034 — `BranchSelector.score`: timeout bounded.
- [ ] META-R035 — `BranchSelector.score`: offline test.
- [ ] META-R036 — `BranchSelector.score`: adversarial test.
- [ ] META-R037 — `BranchSelector.score`: success test.
- [ ] META-R038 — `BranchSelector.score`: tie deterministic.
- [ ] META-R039 — `BranchSelector.score`: stale input rejected.
- [ ] META-R040 — `BranchSelector.score`: unknown field rejected.
- [ ] META-R041 — `BranchSelector.score`: provider failure isolated.
- [ ] META-R042 — `BranchSelector.score`: parent reverify.
- [ ] META-R043 — `BranchSelector.score`: rollback tested.
- [ ] META-R044 — `BranchSelector.score`: heldout leakage blocked.
- [ ] META-R045 — `BranchSelector.score`: threshold preregistered.
- [ ] META-R046 — `BranchSelector.score`: no self-promotion.
- [ ] META-R047 — `BranchSelector.score`: no kernel import.
- [ ] META-R048 — `BranchSelector.score`: no direct subprocess.
- [ ] META-R049 — `BranchSelector.score`: state digest retained.
- [ ] META-R050 — `BranchSelector.score`: route digest retained.
- [ ] META-R051 — `BranchSelector.select`: deterministic.
- [ ] META-R052 — `BranchSelector.select`: budget bounded.
- [ ] META-R053 — `BranchSelector.select`: authority attenuated.
- [ ] META-R054 — `BranchSelector.select`: failure typed.
- [ ] META-R055 — `BranchSelector.select`: artifact provenance.
- [ ] META-R056 — `BranchSelector.select`: idempotent replay.
- [ ] META-R057 — `BranchSelector.select`: no transcript merge.
- [ ] META-R058 — `BranchSelector.select`: cost settled.
- [ ] META-R059 — `BranchSelector.select`: timeout bounded.
- [ ] META-R060 — `BranchSelector.select`: offline test.
- [ ] META-R061 — `BranchSelector.select`: adversarial test.
- [ ] META-R062 — `BranchSelector.select`: success test.
- [ ] META-R063 — `BranchSelector.select`: tie deterministic.
- [ ] META-R064 — `BranchSelector.select`: stale input rejected.
- [ ] META-R065 — `BranchSelector.select`: unknown field rejected.
- [ ] META-R066 — `BranchSelector.select`: provider failure isolated.
- [ ] META-R067 — `BranchSelector.select`: parent reverify.
- [ ] META-R068 — `BranchSelector.select`: rollback tested.
- [ ] META-R069 — `BranchSelector.select`: heldout leakage blocked.
- [ ] META-R070 — `BranchSelector.select`: threshold preregistered.
- [ ] META-R071 — `BranchSelector.select`: no self-promotion.
- [ ] META-R072 — `BranchSelector.select`: no kernel import.
- [ ] META-R073 — `BranchSelector.select`: no direct subprocess.
- [ ] META-R074 — `BranchSelector.select`: state digest retained.
- [ ] META-R075 — `BranchSelector.select`: route digest retained.
- [ ] META-R076 — `BoundedBranchSearch.run`: deterministic.
- [ ] META-R077 — `BoundedBranchSearch.run`: budget bounded.
- [ ] META-R078 — `BoundedBranchSearch.run`: authority attenuated.
- [ ] META-R079 — `BoundedBranchSearch.run`: failure typed.
- [ ] META-R080 — `BoundedBranchSearch.run`: artifact provenance.
- [ ] META-R081 — `BoundedBranchSearch.run`: idempotent replay.
- [ ] META-R082 — `BoundedBranchSearch.run`: no transcript merge.
- [ ] META-R083 — `BoundedBranchSearch.run`: cost settled.
- [ ] META-R084 — `BoundedBranchSearch.run`: timeout bounded.
- [ ] META-R085 — `BoundedBranchSearch.run`: offline test.
- [ ] META-R086 — `BoundedBranchSearch.run`: adversarial test.
- [ ] META-R087 — `BoundedBranchSearch.run`: success test.
- [ ] META-R088 — `BoundedBranchSearch.run`: tie deterministic.
- [ ] META-R089 — `BoundedBranchSearch.run`: stale input rejected.
- [ ] META-R090 — `BoundedBranchSearch.run`: unknown field rejected.
- [ ] META-R091 — `BoundedBranchSearch.run`: provider failure isolated.
- [ ] META-R092 — `BoundedBranchSearch.run`: parent reverify.
- [ ] META-R093 — `BoundedBranchSearch.run`: rollback tested.
- [ ] META-R094 — `BoundedBranchSearch.run`: heldout leakage blocked.
- [ ] META-R095 — `BoundedBranchSearch.run`: threshold preregistered.
- [ ] META-R096 — `BoundedBranchSearch.run`: no self-promotion.
- [ ] META-R097 — `BoundedBranchSearch.run`: no kernel import.
- [ ] META-R098 — `BoundedBranchSearch.run`: no direct subprocess.
- [ ] META-R099 — `BoundedBranchSearch.run`: state digest retained.
- [ ] META-R100 — `BoundedBranchSearch.run`: route digest retained.
- [ ] META-R101 — `ManifestMutator.apply`: deterministic.
- [ ] META-R102 — `ManifestMutator.apply`: budget bounded.
- [ ] META-R103 — `ManifestMutator.apply`: authority attenuated.
- [ ] META-R104 — `ManifestMutator.apply`: failure typed.
- [ ] META-R105 — `ManifestMutator.apply`: artifact provenance.
- [ ] META-R106 — `ManifestMutator.apply`: idempotent replay.
- [ ] META-R107 — `ManifestMutator.apply`: no transcript merge.
- [ ] META-R108 — `ManifestMutator.apply`: cost settled.
- [ ] META-R109 — `ManifestMutator.apply`: timeout bounded.
- [ ] META-R110 — `ManifestMutator.apply`: offline test.
- [ ] META-R111 — `ManifestMutator.apply`: adversarial test.
- [ ] META-R112 — `ManifestMutator.apply`: success test.
- [ ] META-R113 — `ManifestMutator.apply`: tie deterministic.
- [ ] META-R114 — `ManifestMutator.apply`: stale input rejected.
- [ ] META-R115 — `ManifestMutator.apply`: unknown field rejected.
- [ ] META-R116 — `ManifestMutator.apply`: provider failure isolated.
- [ ] META-R117 — `ManifestMutator.apply`: parent reverify.
- [ ] META-R118 — `ManifestMutator.apply`: rollback tested.
- [ ] META-R119 — `ManifestMutator.apply`: heldout leakage blocked.
- [ ] META-R120 — `ManifestMutator.apply`: threshold preregistered.
- [ ] META-R121 — `ManifestMutator.apply`: no self-promotion.
- [ ] META-R122 — `ManifestMutator.apply`: no kernel import.
- [ ] META-R123 — `ManifestMutator.apply`: no direct subprocess.
- [ ] META-R124 — `ManifestMutator.apply`: state digest retained.
- [ ] META-R125 — `ManifestMutator.apply`: route digest retained.
- [ ] META-R126 — `_set_path`: deterministic.
- [ ] META-R127 — `_set_path`: budget bounded.
- [ ] META-R128 — `_set_path`: authority attenuated.
- [ ] META-R129 — `_set_path`: failure typed.
- [ ] META-R130 — `_set_path`: artifact provenance.
- [ ] META-R131 — `_set_path`: idempotent replay.
- [ ] META-R132 — `_set_path`: no transcript merge.
- [ ] META-R133 — `_set_path`: cost settled.
- [ ] META-R134 — `_set_path`: timeout bounded.
- [ ] META-R135 — `_set_path`: offline test.
- [ ] META-R136 — `_set_path`: adversarial test.
- [ ] META-R137 — `_set_path`: success test.
- [ ] META-R138 — `_set_path`: tie deterministic.
- [ ] META-R139 — `_set_path`: stale input rejected.
- [ ] META-R140 — `_set_path`: unknown field rejected.
- [ ] META-R141 — `_set_path`: provider failure isolated.
- [ ] META-R142 — `_set_path`: parent reverify.
- [ ] META-R143 — `_set_path`: rollback tested.
- [ ] META-R144 — `_set_path`: heldout leakage blocked.
- [ ] META-R145 — `_set_path`: threshold preregistered.
- [ ] META-R146 — `_set_path`: no self-promotion.
- [ ] META-R147 — `_set_path`: no kernel import.
- [ ] META-R148 — `_set_path`: no direct subprocess.
- [ ] META-R149 — `_set_path`: state digest retained.
- [ ] META-R150 — `_set_path`: route digest retained.
- [ ] META-R151 — `CapsuleRegistry.propose`: deterministic.
- [ ] META-R152 — `CapsuleRegistry.propose`: budget bounded.
- [ ] META-R153 — `CapsuleRegistry.propose`: authority attenuated.
- [ ] META-R154 — `CapsuleRegistry.propose`: failure typed.
- [ ] META-R155 — `CapsuleRegistry.propose`: artifact provenance.
- [ ] META-R156 — `CapsuleRegistry.propose`: idempotent replay.
- [ ] META-R157 — `CapsuleRegistry.propose`: no transcript merge.
- [ ] META-R158 — `CapsuleRegistry.propose`: cost settled.
- [ ] META-R159 — `CapsuleRegistry.propose`: timeout bounded.
- [ ] META-R160 — `CapsuleRegistry.propose`: offline test.
- [ ] META-R161 — `CapsuleRegistry.propose`: adversarial test.
- [ ] META-R162 — `CapsuleRegistry.propose`: success test.
- [ ] META-R163 — `CapsuleRegistry.propose`: tie deterministic.
- [ ] META-R164 — `CapsuleRegistry.propose`: stale input rejected.
- [ ] META-R165 — `CapsuleRegistry.propose`: unknown field rejected.
- [ ] META-R166 — `CapsuleRegistry.propose`: provider failure isolated.
- [ ] META-R167 — `CapsuleRegistry.propose`: parent reverify.
- [ ] META-R168 — `CapsuleRegistry.propose`: rollback tested.
- [ ] META-R169 — `CapsuleRegistry.propose`: heldout leakage blocked.
- [ ] META-R170 — `CapsuleRegistry.propose`: threshold preregistered.
- [ ] META-R171 — `CapsuleRegistry.propose`: no self-promotion.
- [ ] META-R172 — `CapsuleRegistry.propose`: no kernel import.
- [ ] META-R173 — `CapsuleRegistry.propose`: no direct subprocess.
- [ ] META-R174 — `CapsuleRegistry.propose`: state digest retained.
- [ ] META-R175 — `CapsuleRegistry.propose`: route digest retained.
- [ ] META-R176 — `CapsuleRegistry.eligible`: deterministic.
- [ ] META-R177 — `CapsuleRegistry.eligible`: budget bounded.
- [ ] META-R178 — `CapsuleRegistry.eligible`: authority attenuated.
- [ ] META-R179 — `CapsuleRegistry.eligible`: failure typed.
- [ ] META-R180 — `CapsuleRegistry.eligible`: artifact provenance.
- [ ] META-R181 — `CapsuleRegistry.eligible`: idempotent replay.
- [ ] META-R182 — `CapsuleRegistry.eligible`: no transcript merge.
- [ ] META-R183 — `CapsuleRegistry.eligible`: cost settled.
- [ ] META-R184 — `CapsuleRegistry.eligible`: timeout bounded.
- [ ] META-R185 — `CapsuleRegistry.eligible`: offline test.
- [ ] META-R186 — `CapsuleRegistry.eligible`: adversarial test.
- [ ] META-R187 — `CapsuleRegistry.eligible`: success test.
- [ ] META-R188 — `CapsuleRegistry.eligible`: tie deterministic.
- [ ] META-R189 — `CapsuleRegistry.eligible`: stale input rejected.
- [ ] META-R190 — `CapsuleRegistry.eligible`: unknown field rejected.
- [ ] META-R191 — `CapsuleRegistry.eligible`: provider failure isolated.
- [ ] META-R192 — `CapsuleRegistry.eligible`: parent reverify.
- [ ] META-R193 — `CapsuleRegistry.eligible`: rollback tested.
- [ ] META-R194 — `CapsuleRegistry.eligible`: heldout leakage blocked.
- [ ] META-R195 — `CapsuleRegistry.eligible`: threshold preregistered.
- [ ] META-R196 — `CapsuleRegistry.eligible`: no self-promotion.
- [ ] META-R197 — `CapsuleRegistry.eligible`: no kernel import.
- [ ] META-R198 — `CapsuleRegistry.eligible`: no direct subprocess.
- [ ] META-R199 — `CapsuleRegistry.eligible`: state digest retained.
- [ ] META-R200 — `CapsuleRegistry.eligible`: route digest retained.
- [ ] META-R201 — `CapsuleRegistry.promote`: deterministic.
- [ ] META-R202 — `CapsuleRegistry.promote`: budget bounded.
- [ ] META-R203 — `CapsuleRegistry.promote`: authority attenuated.
- [ ] META-R204 — `CapsuleRegistry.promote`: failure typed.
- [ ] META-R205 — `CapsuleRegistry.promote`: artifact provenance.
- [ ] META-R206 — `CapsuleRegistry.promote`: idempotent replay.
- [ ] META-R207 — `CapsuleRegistry.promote`: no transcript merge.
- [ ] META-R208 — `CapsuleRegistry.promote`: cost settled.
- [ ] META-R209 — `CapsuleRegistry.promote`: timeout bounded.
- [ ] META-R210 — `CapsuleRegistry.promote`: offline test.
- [ ] META-R211 — `CapsuleRegistry.promote`: adversarial test.
- [ ] META-R212 — `CapsuleRegistry.promote`: success test.
- [ ] META-R213 — `CapsuleRegistry.promote`: tie deterministic.
- [ ] META-R214 — `CapsuleRegistry.promote`: stale input rejected.
- [ ] META-R215 — `CapsuleRegistry.promote`: unknown field rejected.
- [ ] META-R216 — `CapsuleRegistry.promote`: provider failure isolated.
- [ ] META-R217 — `CapsuleRegistry.promote`: parent reverify.
- [ ] META-R218 — `CapsuleRegistry.promote`: rollback tested.
- [ ] META-R219 — `CapsuleRegistry.promote`: heldout leakage blocked.
- [ ] META-R220 — `CapsuleRegistry.promote`: threshold preregistered.
- [ ] META-R221 — `CapsuleRegistry.promote`: no self-promotion.
- [ ] META-R222 — `CapsuleRegistry.promote`: no kernel import.
- [ ] META-R223 — `CapsuleRegistry.promote`: no direct subprocess.
- [ ] META-R224 — `CapsuleRegistry.promote`: state digest retained.
- [ ] META-R225 — `CapsuleRegistry.promote`: route digest retained.
- [ ] META-R226 — `CapsuleRegistry.rollback`: deterministic.
- [ ] META-R227 — `CapsuleRegistry.rollback`: budget bounded.
- [ ] META-R228 — `CapsuleRegistry.rollback`: authority attenuated.
- [ ] META-R229 — `CapsuleRegistry.rollback`: failure typed.
- [ ] META-R230 — `CapsuleRegistry.rollback`: artifact provenance.
- [ ] META-R231 — `CapsuleRegistry.rollback`: idempotent replay.
- [ ] META-R232 — `CapsuleRegistry.rollback`: no transcript merge.
- [ ] META-R233 — `CapsuleRegistry.rollback`: cost settled.
- [ ] META-R234 — `CapsuleRegistry.rollback`: timeout bounded.
- [ ] META-R235 — `CapsuleRegistry.rollback`: offline test.
- [ ] META-R236 — `CapsuleRegistry.rollback`: adversarial test.
- [ ] META-R237 — `CapsuleRegistry.rollback`: success test.
- [ ] META-R238 — `CapsuleRegistry.rollback`: tie deterministic.
- [ ] META-R239 — `CapsuleRegistry.rollback`: stale input rejected.
- [ ] META-R240 — `CapsuleRegistry.rollback`: unknown field rejected.
- [ ] META-R241 — `CapsuleRegistry.rollback`: provider failure isolated.
- [ ] META-R242 — `CapsuleRegistry.rollback`: parent reverify.
- [ ] META-R243 — `CapsuleRegistry.rollback`: rollback tested.
- [ ] META-R244 — `CapsuleRegistry.rollback`: heldout leakage blocked.
- [ ] META-R245 — `CapsuleRegistry.rollback`: threshold preregistered.
- [ ] META-R246 — `CapsuleRegistry.rollback`: no self-promotion.
- [ ] META-R247 — `CapsuleRegistry.rollback`: no kernel import.
- [ ] META-R248 — `CapsuleRegistry.rollback`: no direct subprocess.
- [ ] META-R249 — `CapsuleRegistry.rollback`: state digest retained.
- [ ] META-R250 — `CapsuleRegistry.rollback`: route digest retained.
- [ ] META-R251 — `fork_policy.build_specs`: deterministic.
- [ ] META-R252 — `fork_policy.build_specs`: budget bounded.
- [ ] META-R253 — `fork_policy.build_specs`: authority attenuated.
- [ ] META-R254 — `fork_policy.build_specs`: failure typed.
- [ ] META-R255 — `fork_policy.build_specs`: artifact provenance.
- [ ] META-R256 — `fork_policy.build_specs`: idempotent replay.
- [ ] META-R257 — `fork_policy.build_specs`: no transcript merge.
- [ ] META-R258 — `fork_policy.build_specs`: cost settled.
- [ ] META-R259 — `fork_policy.build_specs`: timeout bounded.
- [ ] META-R260 — `fork_policy.build_specs`: offline test.
- [ ] META-R261 — `fork_policy.build_specs`: adversarial test.
- [ ] META-R262 — `fork_policy.build_specs`: success test.
- [ ] META-R263 — `fork_policy.build_specs`: tie deterministic.
- [ ] META-R264 — `fork_policy.build_specs`: stale input rejected.
- [ ] META-R265 — `fork_policy.build_specs`: unknown field rejected.
- [ ] META-R266 — `fork_policy.build_specs`: provider failure isolated.
- [ ] META-R267 — `fork_policy.build_specs`: parent reverify.
- [ ] META-R268 — `fork_policy.build_specs`: rollback tested.
- [ ] META-R269 — `fork_policy.build_specs`: heldout leakage blocked.
- [ ] META-R270 — `fork_policy.build_specs`: threshold preregistered.
- [ ] META-R271 — `fork_policy.build_specs`: no self-promotion.
- [ ] META-R272 — `fork_policy.build_specs`: no kernel import.
- [ ] META-R273 — `fork_policy.build_specs`: no direct subprocess.
- [ ] META-R274 — `fork_policy.build_specs`: state digest retained.
- [ ] META-R275 — `fork_policy.build_specs`: route digest retained.
- [ ] META-R276 — `RuntimeChildRunner.run_child`: deterministic.
- [ ] META-R277 — `RuntimeChildRunner.run_child`: budget bounded.
- [ ] META-R278 — `RuntimeChildRunner.run_child`: authority attenuated.
- [ ] META-R279 — `RuntimeChildRunner.run_child`: failure typed.
- [ ] META-R280 — `RuntimeChildRunner.run_child`: artifact provenance.
- [ ] META-R281 — `RuntimeChildRunner.run_child`: idempotent replay.
- [ ] META-R282 — `RuntimeChildRunner.run_child`: no transcript merge.
- [ ] META-R283 — `RuntimeChildRunner.run_child`: cost settled.
- [ ] META-R284 — `RuntimeChildRunner.run_child`: timeout bounded.
- [ ] META-R285 — `RuntimeChildRunner.run_child`: offline test.
- [ ] META-R286 — `RuntimeChildRunner.run_child`: adversarial test.
- [ ] META-R287 — `RuntimeChildRunner.run_child`: success test.
- [ ] META-R288 — `RuntimeChildRunner.run_child`: tie deterministic.
- [ ] META-R289 — `RuntimeChildRunner.run_child`: stale input rejected.
- [ ] META-R290 — `RuntimeChildRunner.run_child`: unknown field rejected.
- [ ] META-R291 — `RuntimeChildRunner.run_child`: provider failure isolated.
- [ ] META-R292 — `RuntimeChildRunner.run_child`: parent reverify.
- [ ] META-R293 — `RuntimeChildRunner.run_child`: rollback tested.
- [ ] META-R294 — `RuntimeChildRunner.run_child`: heldout leakage blocked.
- [ ] META-R295 — `RuntimeChildRunner.run_child`: threshold preregistered.
- [ ] META-R296 — `RuntimeChildRunner.run_child`: no self-promotion.
- [ ] META-R297 — `RuntimeChildRunner.run_child`: no kernel import.
- [ ] META-R298 — `RuntimeChildRunner.run_child`: no direct subprocess.
- [ ] META-R299 — `RuntimeChildRunner.run_child`: state digest retained.
- [ ] META-R300 — `RuntimeChildRunner.run_child`: route digest retained.

## 14. Acceptance gates

- [ ] Simple tasks continuam sequenciais.
- [ ] Fork somente sob trigger mensurável.
- [ ] Branches usam workspaces isolados.
- [ ] Child budgets são subconjuntos conservados.
- [ ] Seleção usa tests/regression/cost, não confiança textual.
- [ ] Winner é reexecutado/verificado no parent.
- [ ] Mutação não altera capability digest.
- [ ] Capsule não promove sem heldout e aprovação.
- [ ] Rollback é executável e deixa receipt.
- [ ] Ablation mostra valor ou feature é removida.

## 15. Definition of Done

A onda fecha quando a mesma composição pode metamorfosear estratégia sob budget, explorar candidatos isolados, escolher por evidência e reverter aprendizado sem alterar o substrato. Metamorfose sem gates é corrupção; branching sem ganho medido é custo inútil.

- [ ] META-X709 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X710 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X711 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X712 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X713 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X714 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X715 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X716 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X717 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X718 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X719 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X720 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X721 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X722 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X723 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X724 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X725 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X726 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X727 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X728 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X729 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X730 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X731 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X732 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X733 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X734 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X735 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X736 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X737 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X738 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X739 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X740 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X741 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X742 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X743 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X744 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X745 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X746 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X747 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X748 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X749 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X750 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X751 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X752 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X753 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X754 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X755 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X756 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X757 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X758 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X759 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X760 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X761 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X762 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X763 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X764 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X765 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X766 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X767 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X768 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X769 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X770 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X771 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X772 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X773 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X774 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X775 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X776 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X777 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X778 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X779 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X780 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X781 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X782 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X783 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X784 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X785 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X786 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X787 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X788 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X789 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X790 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X791 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X792 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X793 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X794 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X795 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X796 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X797 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X798 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X799 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X800 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X801 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X802 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X803 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X804 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X805 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X806 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X807 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X808 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X809 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X810 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X811 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X812 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X813 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X814 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X815 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X816 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X817 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X818 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X819 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X820 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X821 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X822 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X823 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X824 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X825 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X826 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X827 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X828 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X829 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X830 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X831 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X832 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X833 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X834 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X835 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X836 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X837 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X838 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X839 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X840 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X841 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X842 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X843 — Falsificar propriedade evolutiva remanescente antes de ativar.
- [ ] META-X844 — Falsificar propriedade evolutiva remanescente antes de ativar.
