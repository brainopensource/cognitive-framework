# Full Code Manifest — Wave 9: ToolScript, Especialistas Locais e Reviewer Condicional

## 0. Objetivo

Completar superfícies Forge/Chimera ainda abertas: scripts efêmeros limitados, especialistas locais baratos, reviewer externo condicional, distillation de branches e integração sem ampliar authority. Nenhum script executa Python arbitrário; nenhum modelo pequeno recebe tools além do papel; reviewer não substitui testes.

## 1. ToolScript IR

```python
# packs/code-default/coding_max/toolscript.py
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Sequence

class Op(str, Enum):
    SEARCH = "search"
    READ = "read"
    SYMBOL = "symbol"
    TESTS_FOR = "tests_for"
    FILTER = "filter"
    TAKE = "take"
    EMIT = "emit"

@dataclass(frozen=True, slots=True)
class Instruction:
    op: Op
    args: Mapping[str, Any]

@dataclass(frozen=True, slots=True)
class ToolScript:
    api: str
    script_id: str
    instructions: tuple[Instruction, ...]
    input_digests: tuple[str, ...]
    max_steps: int = 32
    max_results: int = 100

    def validate(self) -> None:
        if self.api != "aether.toolscript/1": raise ValueError("unsupported api")
        if not self.script_id: raise ValueError("script_id required")
        if not 1 <= len(self.instructions) <= self.max_steps: raise ValueError("step ceiling")
        if self.max_results <= 0 or self.max_results > 1000: raise ValueError("result ceiling")
```

## 2. ToolScript broker

```python
# packs/code-default/coding_max/toolscript_broker.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .toolscript import Op, ToolScript

@dataclass(frozen=True, slots=True)
class ToolScriptResult:
    script_id: str
    rows: tuple[Mapping[str, Any], ...]
    steps: int
    truncated: bool

class ToolScriptBroker:
    def __init__(self, intelligence, artifact_loader, *, max_bytes=1_000_000) -> None:
        self.intelligence = intelligence
        self.artifact_loader = artifact_loader
        self.max_bytes = max_bytes

    def execute(self, script: ToolScript) -> ToolScriptResult:
        script.validate()
        rows: list[Mapping[str, Any]] = []
        emitted = False
        for index, instruction in enumerate(script.instructions, 1):
            if instruction.op is Op.SEARCH:
                hits = self.intelligence.search(str(instruction.args["query"]), limit=script.max_results)
                rows = [hit.__dict__ for hit in hits]
            elif instruction.op is Op.SYMBOL:
                hits = self.intelligence.symbol(str(instruction.args["name"]), limit=script.max_results)
                rows = [hit.__dict__ for hit in hits]
            elif instruction.op is Op.TESTS_FOR:
                hits = self.intelligence.tests_for(str(instruction.args["target"]), limit=script.max_results)
                rows = [hit.__dict__ for hit in hits]
            elif instruction.op is Op.FILTER:
                key, value = str(instruction.args["key"]), instruction.args["equals"]
                rows = [row for row in rows if row.get(key) == value]
            elif instruction.op is Op.TAKE:
                rows = rows[:max(0, min(int(instruction.args["count"]), script.max_results))]
            elif instruction.op is Op.EMIT:
                emitted = True
                break
            else:
                raise ValueError(f"op not executable in MVP: {instruction.op}")
            if len(repr(rows).encode()) > self.max_bytes:
                rows = rows[: max(1, len(rows) // 2)]
        if not emitted: raise ValueError("script must terminate with emit")
        return ToolScriptResult(script.script_id, tuple(rows), index, len(rows) >= script.max_results)
```

Implementação real deve usar `dataclasses.asdict(hit)` em vez de `hit.__dict__` para dataclasses com slots.

## 3. Diff corretivo

```diff
+from dataclasses import asdict, dataclass
-                rows = [hit.__dict__ for hit in hits]
+                rows = [asdict(hit) for hit in hits]
```

## 4. Especialistas locais

```python
# packs/code-default/coding_max/specialists.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence

@dataclass(frozen=True, slots=True)
class SpecialistTask:
    role: str
    input_artifacts: tuple[str, ...]
    question: str
    output_schema: Mapping[str, Any]
    budget: Mapping[str, int]

@dataclass(frozen=True, slots=True)
class SpecialistResult:
    role: str
    output_artifact: str
    model_route: str
    tokens: int
    valid: bool

class SpecialistRunner(Protocol):
    def run(self, task: SpecialistTask) -> SpecialistResult: ...

ROLE_CAPS = {
    "localizer": {"tools": ("search", "symbol", "tests_for"), "writes": False},
    "test_investigator": {"tools": ("read", "search", "test.run"), "writes": False},
    "patch_critic": {"tools": ("read",), "writes": False},
    "summarizer": {"tools": (), "writes": False},
}

def validate_specialist(task: SpecialistTask) -> None:
    if task.role not in ROLE_CAPS: raise ValueError("unknown specialist role")
    if int(task.budget.get("tokens", 0)) > 8000: raise ValueError("specialist token ceiling")
    if int(task.budget.get("turns", 0)) > 2: raise ValueError("specialist turn ceiling")
    if not task.output_schema: raise ValueError("structured output schema required")
```

## 5. Reviewer condicional

```python
# packs/code-default/coding_max/reviewer.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

@dataclass(frozen=True, slots=True)
class ReviewInput:
    task_digest: str
    plan_digest: str
    patch_digest: str
    verification_digest: str
    changed_files: tuple[str, ...]
    risk_signals: tuple[str, ...]

@dataclass(frozen=True, slots=True)
class ReviewVerdict:
    decision: str
    findings: tuple[str, ...]
    required_actions: tuple[str, ...]
    evidence_digest: str

class ReviewPolicy:
    def required(self, *, complexity: int, changed_files: Sequence[str], risk_signals: Sequence[str], attempts: int) -> bool:
        return complexity >= 4 or len(changed_files) >= 5 or bool(risk_signals) or attempts >= 3

class ReviewAdmission:
    def evaluate(self, verdict: ReviewVerdict) -> bool:
        if verdict.decision not in {"accept", "reject", "revise"}: raise ValueError("unknown review decision")
        if not verdict.evidence_digest: raise ValueError("review must be artifact-backed")
        return verdict.decision == "accept" and not verdict.required_actions
```

## 6. Trajectory distillation

```python
# packs/code-default/coding_max/distill.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

@dataclass(frozen=True, slots=True)
class BranchSummary:
    branch_id: str
    hypothesis: str
    evidence_digests: tuple[str, ...]
    patch_digest: str | None
    verification_digest: str | None
    failure_class: str | None
    cost: Mapping[str, int]

class TrajectoryDistiller:
    def distill(self, rows: Sequence[BranchSummary], *, max_rows: int = 8) -> tuple[Mapping[str, object], ...]:
        ordered = sorted(rows, key=lambda row: (row.verification_digest is None, row.branch_id))
        return tuple({
            "branchId": row.branch_id,
            "hypothesis": row.hypothesis[:500],
            "evidenceDigests": list(row.evidence_digests),
            "patchDigest": row.patch_digest,
            "verificationDigest": row.verification_digest,
            "failureClass": row.failure_class,
            "cost": dict(row.cost),
        } for row in ordered[:max_rows])
```

## 7. Integração no coordinator

```diff
@@ after verification failure:
+ directive = reflex.decide(
+     failure=failure.failure.value, repeated_signal=repeated_signal,
+     uncertainty=decision.profile.uncertainty,
+     remaining_budget=remaining_budget, context_misses=context_misses,
+ )
+ if directive.action == "expand_repository_evidence":
+     script = script_factory.for_directive(directive)
+     result = toolscript_broker.execute(script)
+     context = context_compiler.mutate(context, add=result_to_candidates(result))
+ elif directive.action in {"fork_hypotheses", "counterexample_branch"}:
+     branch_summaries = branch_executor.run(directive)
+     compact = distiller.distill(branch_summaries)
+     state_sink.capture_branch_summary(compact)
+ if review_policy.required(...):
+     verdict = reviewer.review(build_review_input(...))
+     if not review_admission.evaluate(verdict):
+         continue
```

## 8. ToolScript safety

| Threat | Control | Falsifier |
|---|---|---|
| TS-001 arbitrary Python | finite typed IR | adversarial script 1 |
| TS-002 filesystem write | finite typed IR | adversarial script 2 |
| TS-003 network access | finite typed IR | adversarial script 3 |
| TS-004 process spawn | finite typed IR | adversarial script 4 |
| TS-005 unbounded loop | finite typed IR | adversarial script 5 |
| TS-006 unbounded rows | finite typed IR | adversarial script 6 |
| TS-007 unbounded bytes | finite typed IR | adversarial script 7 |
| TS-008 unknown op | finite typed IR | adversarial script 8 |
| TS-009 missing emit | finite typed IR | adversarial script 9 |
| TS-010 artifact escape | finite typed IR | adversarial script 10 |
| TS-011 capability expansion | finite typed IR | adversarial script 11 |
| TS-012 secret read | finite typed IR | adversarial script 12 |
| TS-013 path traversal | finite typed IR | adversarial script 13 |
| TS-014 recursive script | finite typed IR | adversarial script 14 |
| TS-015 self modification | finite typed IR | adversarial script 15 |
| TS-016 dynamic import | finite typed IR | adversarial script 16 |
| TS-017 reflection escape | finite typed IR | adversarial script 17 |
| TS-018 deserialization gadget | finite typed IR | adversarial script 18 |
| TS-019 timeout omission | finite typed IR | adversarial script 19 |
| TS-020 result spoofing | finite typed IR | adversarial script 20 |

## 9. Specialist roles

| Role | Input | Output | Model class | Stop |
|---|---|---|---|---|
| localizer | task + repo map | ranked locations | small local | schema valid |
| test investigator | failures + symbols | test mapping | small local | schema valid |
| patch critic | diff + task | findings | cheap remote/local | findings complete |
| summarizer | branch artifacts | compact summary | small local | size ceiling |
| primary worker | compiled context | patch/tools | frontier adaptive | verification |
| reviewer | task/patch/verification | verdict | independent route | typed verdict |

## 10. Tests

```python
class ToolScriptTests(unittest.TestCase):
    def test_unknown_op_rejected(self): ...
    def test_missing_emit_rejected(self): ...
    def test_step_ceiling_rejected(self): ...
    def test_result_ceiling_enforced(self): ...
    def test_no_write_operation_exists(self): ...

class SpecialistTests(unittest.TestCase):
    def test_unknown_role_rejected(self): ...
    def test_budget_ceiling_rejected(self): ...
    def test_structured_output_required(self): ...
    def test_specialist_cannot_write(self): ...

class ReviewerTests(unittest.TestCase):
    def test_simple_task_skips_reviewer(self): ...
    def test_high_risk_requires_reviewer(self): ...
    def test_review_without_evidence_rejected(self): ...
    def test_reviewer_cannot_override_failed_tests(self): ...
```

## 11. Model routing policy

```text
small/local: classification, localization, summarization, test mapping
cheap/remote: critique, alternate hypothesis, routine patches
frontier: ambiguous architecture, hard debugging, final synthesis
reviewer: independent route when risk gate fires
never escalate solely because a fixed turn number elapsed
```

## 12. Performance budgets

| Component | p95 target | Token cap | Calls |
|---|---:|---:|---:|
| classifier | 5 ms | 0 | 0 |
| native search | 2 s | 0 | bounded |
| ToolScript | 5 s | 0 | 32 steps |
| localizer | 15 s | 4k | 1 |
| summarizer | 10 s | 4k | 1 |
| reviewer | 60 s | 16k | conditional |
| branch search | task-dependent | parent budget | ≤3 |

## 13. Checklist por símbolo

- [ ] TS-R001 — `ToolScript.validate`: finite execution.
- [ ] TS-R002 — `ToolScript.validate`: typed input.
- [ ] TS-R003 — `ToolScript.validate`: typed output.
- [ ] TS-R004 — `ToolScript.validate`: budget bound.
- [ ] TS-R005 — `ToolScript.validate`: authority unchanged.
- [ ] TS-R006 — `ToolScript.validate`: no filesystem write.
- [ ] TS-R007 — `ToolScript.validate`: no network.
- [ ] TS-R008 — `ToolScript.validate`: no subprocess.
- [ ] TS-R009 — `ToolScript.validate`: artifact-backed.
- [ ] TS-R010 — `ToolScript.validate`: provenance.
- [ ] TS-R011 — `ToolScript.validate`: timeout.
- [ ] TS-R012 — `ToolScript.validate`: size ceiling.
- [ ] TS-R013 — `ToolScript.validate`: row ceiling.
- [ ] TS-R014 — `ToolScript.validate`: offline test.
- [ ] TS-R015 — `ToolScript.validate`: adversarial test.
- [ ] TS-R016 — `ToolScript.validate`: failure isolation.
- [ ] TS-R017 — `ToolScript.validate`: fallback.
- [ ] TS-R018 — `ToolScript.validate`: determinism.
- [ ] TS-R019 — `ToolScript.validate`: secret safety.
- [ ] TS-R020 — `ToolScript.validate`: no self-promotion.
- [ ] TS-R021 — `ToolScript.validate`: no test override.
- [ ] TS-R022 — `ToolScript.validate`: conditional invocation.
- [ ] TS-R023 — `ToolScript.validate`: telemetry.
- [ ] TS-R024 — `ToolScript.validate`: cost accounting.
- [ ] TS-R025 — `ToolScript.validate`: ablation.
- [ ] TS-R026 — `ToolScriptBroker.execute`: finite execution.
- [ ] TS-R027 — `ToolScriptBroker.execute`: typed input.
- [ ] TS-R028 — `ToolScriptBroker.execute`: typed output.
- [ ] TS-R029 — `ToolScriptBroker.execute`: budget bound.
- [ ] TS-R030 — `ToolScriptBroker.execute`: authority unchanged.
- [ ] TS-R031 — `ToolScriptBroker.execute`: no filesystem write.
- [ ] TS-R032 — `ToolScriptBroker.execute`: no network.
- [ ] TS-R033 — `ToolScriptBroker.execute`: no subprocess.
- [ ] TS-R034 — `ToolScriptBroker.execute`: artifact-backed.
- [ ] TS-R035 — `ToolScriptBroker.execute`: provenance.
- [ ] TS-R036 — `ToolScriptBroker.execute`: timeout.
- [ ] TS-R037 — `ToolScriptBroker.execute`: size ceiling.
- [ ] TS-R038 — `ToolScriptBroker.execute`: row ceiling.
- [ ] TS-R039 — `ToolScriptBroker.execute`: offline test.
- [ ] TS-R040 — `ToolScriptBroker.execute`: adversarial test.
- [ ] TS-R041 — `ToolScriptBroker.execute`: failure isolation.
- [ ] TS-R042 — `ToolScriptBroker.execute`: fallback.
- [ ] TS-R043 — `ToolScriptBroker.execute`: determinism.
- [ ] TS-R044 — `ToolScriptBroker.execute`: secret safety.
- [ ] TS-R045 — `ToolScriptBroker.execute`: no self-promotion.
- [ ] TS-R046 — `ToolScriptBroker.execute`: no test override.
- [ ] TS-R047 — `ToolScriptBroker.execute`: conditional invocation.
- [ ] TS-R048 — `ToolScriptBroker.execute`: telemetry.
- [ ] TS-R049 — `ToolScriptBroker.execute`: cost accounting.
- [ ] TS-R050 — `ToolScriptBroker.execute`: ablation.
- [ ] TS-R051 — `validate_specialist`: finite execution.
- [ ] TS-R052 — `validate_specialist`: typed input.
- [ ] TS-R053 — `validate_specialist`: typed output.
- [ ] TS-R054 — `validate_specialist`: budget bound.
- [ ] TS-R055 — `validate_specialist`: authority unchanged.
- [ ] TS-R056 — `validate_specialist`: no filesystem write.
- [ ] TS-R057 — `validate_specialist`: no network.
- [ ] TS-R058 — `validate_specialist`: no subprocess.
- [ ] TS-R059 — `validate_specialist`: artifact-backed.
- [ ] TS-R060 — `validate_specialist`: provenance.
- [ ] TS-R061 — `validate_specialist`: timeout.
- [ ] TS-R062 — `validate_specialist`: size ceiling.
- [ ] TS-R063 — `validate_specialist`: row ceiling.
- [ ] TS-R064 — `validate_specialist`: offline test.
- [ ] TS-R065 — `validate_specialist`: adversarial test.
- [ ] TS-R066 — `validate_specialist`: failure isolation.
- [ ] TS-R067 — `validate_specialist`: fallback.
- [ ] TS-R068 — `validate_specialist`: determinism.
- [ ] TS-R069 — `validate_specialist`: secret safety.
- [ ] TS-R070 — `validate_specialist`: no self-promotion.
- [ ] TS-R071 — `validate_specialist`: no test override.
- [ ] TS-R072 — `validate_specialist`: conditional invocation.
- [ ] TS-R073 — `validate_specialist`: telemetry.
- [ ] TS-R074 — `validate_specialist`: cost accounting.
- [ ] TS-R075 — `validate_specialist`: ablation.
- [ ] TS-R076 — `ReviewPolicy.required`: finite execution.
- [ ] TS-R077 — `ReviewPolicy.required`: typed input.
- [ ] TS-R078 — `ReviewPolicy.required`: typed output.
- [ ] TS-R079 — `ReviewPolicy.required`: budget bound.
- [ ] TS-R080 — `ReviewPolicy.required`: authority unchanged.
- [ ] TS-R081 — `ReviewPolicy.required`: no filesystem write.
- [ ] TS-R082 — `ReviewPolicy.required`: no network.
- [ ] TS-R083 — `ReviewPolicy.required`: no subprocess.
- [ ] TS-R084 — `ReviewPolicy.required`: artifact-backed.
- [ ] TS-R085 — `ReviewPolicy.required`: provenance.
- [ ] TS-R086 — `ReviewPolicy.required`: timeout.
- [ ] TS-R087 — `ReviewPolicy.required`: size ceiling.
- [ ] TS-R088 — `ReviewPolicy.required`: row ceiling.
- [ ] TS-R089 — `ReviewPolicy.required`: offline test.
- [ ] TS-R090 — `ReviewPolicy.required`: adversarial test.
- [ ] TS-R091 — `ReviewPolicy.required`: failure isolation.
- [ ] TS-R092 — `ReviewPolicy.required`: fallback.
- [ ] TS-R093 — `ReviewPolicy.required`: determinism.
- [ ] TS-R094 — `ReviewPolicy.required`: secret safety.
- [ ] TS-R095 — `ReviewPolicy.required`: no self-promotion.
- [ ] TS-R096 — `ReviewPolicy.required`: no test override.
- [ ] TS-R097 — `ReviewPolicy.required`: conditional invocation.
- [ ] TS-R098 — `ReviewPolicy.required`: telemetry.
- [ ] TS-R099 — `ReviewPolicy.required`: cost accounting.
- [ ] TS-R100 — `ReviewPolicy.required`: ablation.
- [ ] TS-R101 — `ReviewAdmission.evaluate`: finite execution.
- [ ] TS-R102 — `ReviewAdmission.evaluate`: typed input.
- [ ] TS-R103 — `ReviewAdmission.evaluate`: typed output.
- [ ] TS-R104 — `ReviewAdmission.evaluate`: budget bound.
- [ ] TS-R105 — `ReviewAdmission.evaluate`: authority unchanged.
- [ ] TS-R106 — `ReviewAdmission.evaluate`: no filesystem write.
- [ ] TS-R107 — `ReviewAdmission.evaluate`: no network.
- [ ] TS-R108 — `ReviewAdmission.evaluate`: no subprocess.
- [ ] TS-R109 — `ReviewAdmission.evaluate`: artifact-backed.
- [ ] TS-R110 — `ReviewAdmission.evaluate`: provenance.
- [ ] TS-R111 — `ReviewAdmission.evaluate`: timeout.
- [ ] TS-R112 — `ReviewAdmission.evaluate`: size ceiling.
- [ ] TS-R113 — `ReviewAdmission.evaluate`: row ceiling.
- [ ] TS-R114 — `ReviewAdmission.evaluate`: offline test.
- [ ] TS-R115 — `ReviewAdmission.evaluate`: adversarial test.
- [ ] TS-R116 — `ReviewAdmission.evaluate`: failure isolation.
- [ ] TS-R117 — `ReviewAdmission.evaluate`: fallback.
- [ ] TS-R118 — `ReviewAdmission.evaluate`: determinism.
- [ ] TS-R119 — `ReviewAdmission.evaluate`: secret safety.
- [ ] TS-R120 — `ReviewAdmission.evaluate`: no self-promotion.
- [ ] TS-R121 — `ReviewAdmission.evaluate`: no test override.
- [ ] TS-R122 — `ReviewAdmission.evaluate`: conditional invocation.
- [ ] TS-R123 — `ReviewAdmission.evaluate`: telemetry.
- [ ] TS-R124 — `ReviewAdmission.evaluate`: cost accounting.
- [ ] TS-R125 — `ReviewAdmission.evaluate`: ablation.
- [ ] TS-R126 — `TrajectoryDistiller.distill`: finite execution.
- [ ] TS-R127 — `TrajectoryDistiller.distill`: typed input.
- [ ] TS-R128 — `TrajectoryDistiller.distill`: typed output.
- [ ] TS-R129 — `TrajectoryDistiller.distill`: budget bound.
- [ ] TS-R130 — `TrajectoryDistiller.distill`: authority unchanged.
- [ ] TS-R131 — `TrajectoryDistiller.distill`: no filesystem write.
- [ ] TS-R132 — `TrajectoryDistiller.distill`: no network.
- [ ] TS-R133 — `TrajectoryDistiller.distill`: no subprocess.
- [ ] TS-R134 — `TrajectoryDistiller.distill`: artifact-backed.
- [ ] TS-R135 — `TrajectoryDistiller.distill`: provenance.
- [ ] TS-R136 — `TrajectoryDistiller.distill`: timeout.
- [ ] TS-R137 — `TrajectoryDistiller.distill`: size ceiling.
- [ ] TS-R138 — `TrajectoryDistiller.distill`: row ceiling.
- [ ] TS-R139 — `TrajectoryDistiller.distill`: offline test.
- [ ] TS-R140 — `TrajectoryDistiller.distill`: adversarial test.
- [ ] TS-R141 — `TrajectoryDistiller.distill`: failure isolation.
- [ ] TS-R142 — `TrajectoryDistiller.distill`: fallback.
- [ ] TS-R143 — `TrajectoryDistiller.distill`: determinism.
- [ ] TS-R144 — `TrajectoryDistiller.distill`: secret safety.
- [ ] TS-R145 — `TrajectoryDistiller.distill`: no self-promotion.
- [ ] TS-R146 — `TrajectoryDistiller.distill`: no test override.
- [ ] TS-R147 — `TrajectoryDistiller.distill`: conditional invocation.
- [ ] TS-R148 — `TrajectoryDistiller.distill`: telemetry.
- [ ] TS-R149 — `TrajectoryDistiller.distill`: cost accounting.
- [ ] TS-R150 — `TrajectoryDistiller.distill`: ablation.
- [ ] TS-R151 — `script_factory.for_directive`: finite execution.
- [ ] TS-R152 — `script_factory.for_directive`: typed input.
- [ ] TS-R153 — `script_factory.for_directive`: typed output.
- [ ] TS-R154 — `script_factory.for_directive`: budget bound.
- [ ] TS-R155 — `script_factory.for_directive`: authority unchanged.
- [ ] TS-R156 — `script_factory.for_directive`: no filesystem write.
- [ ] TS-R157 — `script_factory.for_directive`: no network.
- [ ] TS-R158 — `script_factory.for_directive`: no subprocess.
- [ ] TS-R159 — `script_factory.for_directive`: artifact-backed.
- [ ] TS-R160 — `script_factory.for_directive`: provenance.
- [ ] TS-R161 — `script_factory.for_directive`: timeout.
- [ ] TS-R162 — `script_factory.for_directive`: size ceiling.
- [ ] TS-R163 — `script_factory.for_directive`: row ceiling.
- [ ] TS-R164 — `script_factory.for_directive`: offline test.
- [ ] TS-R165 — `script_factory.for_directive`: adversarial test.
- [ ] TS-R166 — `script_factory.for_directive`: failure isolation.
- [ ] TS-R167 — `script_factory.for_directive`: fallback.
- [ ] TS-R168 — `script_factory.for_directive`: determinism.
- [ ] TS-R169 — `script_factory.for_directive`: secret safety.
- [ ] TS-R170 — `script_factory.for_directive`: no self-promotion.
- [ ] TS-R171 — `script_factory.for_directive`: no test override.
- [ ] TS-R172 — `script_factory.for_directive`: conditional invocation.
- [ ] TS-R173 — `script_factory.for_directive`: telemetry.
- [ ] TS-R174 — `script_factory.for_directive`: cost accounting.
- [ ] TS-R175 — `script_factory.for_directive`: ablation.
- [ ] TS-R176 — `result_to_candidates`: finite execution.
- [ ] TS-R177 — `result_to_candidates`: typed input.
- [ ] TS-R178 — `result_to_candidates`: typed output.
- [ ] TS-R179 — `result_to_candidates`: budget bound.
- [ ] TS-R180 — `result_to_candidates`: authority unchanged.
- [ ] TS-R181 — `result_to_candidates`: no filesystem write.
- [ ] TS-R182 — `result_to_candidates`: no network.
- [ ] TS-R183 — `result_to_candidates`: no subprocess.
- [ ] TS-R184 — `result_to_candidates`: artifact-backed.
- [ ] TS-R185 — `result_to_candidates`: provenance.
- [ ] TS-R186 — `result_to_candidates`: timeout.
- [ ] TS-R187 — `result_to_candidates`: size ceiling.
- [ ] TS-R188 — `result_to_candidates`: row ceiling.
- [ ] TS-R189 — `result_to_candidates`: offline test.
- [ ] TS-R190 — `result_to_candidates`: adversarial test.
- [ ] TS-R191 — `result_to_candidates`: failure isolation.
- [ ] TS-R192 — `result_to_candidates`: fallback.
- [ ] TS-R193 — `result_to_candidates`: determinism.
- [ ] TS-R194 — `result_to_candidates`: secret safety.
- [ ] TS-R195 — `result_to_candidates`: no self-promotion.
- [ ] TS-R196 — `result_to_candidates`: no test override.
- [ ] TS-R197 — `result_to_candidates`: conditional invocation.
- [ ] TS-R198 — `result_to_candidates`: telemetry.
- [ ] TS-R199 — `result_to_candidates`: cost accounting.
- [ ] TS-R200 — `result_to_candidates`: ablation.
- [ ] TS-R201 — `specialist runner`: finite execution.
- [ ] TS-R202 — `specialist runner`: typed input.
- [ ] TS-R203 — `specialist runner`: typed output.
- [ ] TS-R204 — `specialist runner`: budget bound.
- [ ] TS-R205 — `specialist runner`: authority unchanged.
- [ ] TS-R206 — `specialist runner`: no filesystem write.
- [ ] TS-R207 — `specialist runner`: no network.
- [ ] TS-R208 — `specialist runner`: no subprocess.
- [ ] TS-R209 — `specialist runner`: artifact-backed.
- [ ] TS-R210 — `specialist runner`: provenance.
- [ ] TS-R211 — `specialist runner`: timeout.
- [ ] TS-R212 — `specialist runner`: size ceiling.
- [ ] TS-R213 — `specialist runner`: row ceiling.
- [ ] TS-R214 — `specialist runner`: offline test.
- [ ] TS-R215 — `specialist runner`: adversarial test.
- [ ] TS-R216 — `specialist runner`: failure isolation.
- [ ] TS-R217 — `specialist runner`: fallback.
- [ ] TS-R218 — `specialist runner`: determinism.
- [ ] TS-R219 — `specialist runner`: secret safety.
- [ ] TS-R220 — `specialist runner`: no self-promotion.
- [ ] TS-R221 — `specialist runner`: no test override.
- [ ] TS-R222 — `specialist runner`: conditional invocation.
- [ ] TS-R223 — `specialist runner`: telemetry.
- [ ] TS-R224 — `specialist runner`: cost accounting.
- [ ] TS-R225 — `specialist runner`: ablation.
- [ ] TS-R226 — `reviewer adapter`: finite execution.
- [ ] TS-R227 — `reviewer adapter`: typed input.
- [ ] TS-R228 — `reviewer adapter`: typed output.
- [ ] TS-R229 — `reviewer adapter`: budget bound.
- [ ] TS-R230 — `reviewer adapter`: authority unchanged.
- [ ] TS-R231 — `reviewer adapter`: no filesystem write.
- [ ] TS-R232 — `reviewer adapter`: no network.
- [ ] TS-R233 — `reviewer adapter`: no subprocess.
- [ ] TS-R234 — `reviewer adapter`: artifact-backed.
- [ ] TS-R235 — `reviewer adapter`: provenance.
- [ ] TS-R236 — `reviewer adapter`: timeout.
- [ ] TS-R237 — `reviewer adapter`: size ceiling.
- [ ] TS-R238 — `reviewer adapter`: row ceiling.
- [ ] TS-R239 — `reviewer adapter`: offline test.
- [ ] TS-R240 — `reviewer adapter`: adversarial test.
- [ ] TS-R241 — `reviewer adapter`: failure isolation.
- [ ] TS-R242 — `reviewer adapter`: fallback.
- [ ] TS-R243 — `reviewer adapter`: determinism.
- [ ] TS-R244 — `reviewer adapter`: secret safety.
- [ ] TS-R245 — `reviewer adapter`: no self-promotion.
- [ ] TS-R246 — `reviewer adapter`: no test override.
- [ ] TS-R247 — `reviewer adapter`: conditional invocation.
- [ ] TS-R248 — `reviewer adapter`: telemetry.
- [ ] TS-R249 — `reviewer adapter`: cost accounting.
- [ ] TS-R250 — `reviewer adapter`: ablation.

## 14. Acceptance gates

- [ ] ToolScript IR não possui write/exec/network.
- [ ] Scripts terminam dentro de max_steps.
- [ ] Especialistas usam outputs estruturados.
- [ ] Especialistas não recebem authority de escrita.
- [ ] Reviewer é condicional.
- [ ] Reviewer não aceita failed tests.
- [ ] Branch merge usa summaries/artifacts, não transcripts.
- [ ] Small-model path tem fallback determinístico.
- [ ] Custos entram no budget pai.
- [ ] Ablation justifica cada especialista.

## 15. Definition of Done

A onda fecha quando scripts limitados reduzem tool calls/context, especialistas baratos produzem artefatos válidos, reviewer atua apenas em risco alto e nenhuma dessas extensões pode executar efeitos fora do Vanguard ou converter opinião em verificação.

- [ ] TS-X595 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X596 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X597 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X598 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X599 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X600 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X601 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X602 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X603 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X604 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X605 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X606 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X607 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X608 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X609 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X610 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X611 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X612 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X613 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X614 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X615 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X616 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X617 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X618 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X619 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X620 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X621 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X622 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X623 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X624 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X625 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X626 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X627 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X628 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X629 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X630 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X631 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X632 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X633 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X634 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X635 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X636 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X637 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X638 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X639 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X640 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X641 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X642 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X643 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X644 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X645 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X646 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X647 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X648 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X649 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X650 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X651 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X652 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X653 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X654 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X655 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X656 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X657 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X658 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X659 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X660 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X661 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X662 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X663 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X664 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X665 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X666 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X667 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X668 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X669 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X670 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X671 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X672 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X673 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X674 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X675 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X676 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X677 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X678 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X679 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X680 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X681 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X682 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X683 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X684 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X685 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X686 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X687 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X688 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X689 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X690 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X691 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X692 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X693 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X694 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X695 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X696 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X697 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X698 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X699 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X700 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X701 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X702 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X703 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X704 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X705 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X706 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X707 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X708 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X709 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X710 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X711 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X712 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X713 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X714 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X715 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X716 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X717 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X718 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X719 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X720 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X721 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X722 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X723 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X724 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X725 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X726 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X727 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X728 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X729 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X730 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X731 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X732 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X733 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X734 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X735 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X736 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X737 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X738 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X739 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X740 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X741 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X742 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X743 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X744 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X745 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X746 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X747 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X748 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X749 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X750 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X751 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X752 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X753 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X754 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X755 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X756 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X757 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X758 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X759 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X760 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X761 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X762 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X763 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X764 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X765 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X766 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X767 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X768 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X769 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X770 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X771 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X772 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X773 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X774 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X775 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X776 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X777 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X778 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X779 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X780 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X781 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X782 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X783 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X784 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X785 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X786 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X787 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X788 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X789 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X790 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X791 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X792 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X793 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X794 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X795 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X796 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X797 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X798 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X799 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X800 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X801 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X802 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X803 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X804 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X805 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X806 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X807 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X808 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X809 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X810 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X811 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X812 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X813 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X814 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X815 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X816 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X817 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X818 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X819 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X820 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X821 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X822 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X823 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X824 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X825 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X826 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X827 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X828 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X829 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X830 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X831 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X832 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X833 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X834 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X835 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X836 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X837 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X838 — Validar controle adicional de especialista antes de produção.
- [ ] TS-X839 — Validar controle adicional de especialista antes de produção.
