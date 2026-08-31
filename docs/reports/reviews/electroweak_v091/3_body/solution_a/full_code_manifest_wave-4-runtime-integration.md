---
id: report.electroweak.3_body.solution_a.full_code_manifest_wave-4-runtime-integration
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

# Full Code Manifest — Wave 4: Integração Executável Coding Max → Vanguard

## 0. Identidade e resultado

- Branch alvo: `feat/beta-release_electroweak-v091`.
- Baseline inspecionada: `f242ced297216109736975376802f1e3dc4e29ce`.
- Autoridade de execução preservada: `HarnessSession`, kernel S0–S12, ledger e artifacts existentes.
- Objetivo: transformar as policies alfa em uma composição realmente executável, sem segundo runtime.
- Regra: workflow decide; Vanguard autoriza, executa, registra, avalia e recupera.

## 1. Gap fechado

Os manifests 1–3 criaram classificação, planning, contexto, verification e recovery isolados. Esta onda liga essas peças à sessão canônica, converte decisões em `EffectRequest`, mantém o estado de engenharia como artifact/event projection e impede conclusão sem `AdmissionGate`.

## 2. Fluxo final

```text
Task → CodingMaxCoordinator → HarnessSession.run()
  → classify/plan → compile context → model proposal
  → kernel dispatch → toolkit receipt → artifact capture
  → external verification → AdmissionGate
  → complete | classify failure → recovery directive → next episode
```

## 3. Novo arquivo: `packs/code-default/coding_max/contracts.py`

```python
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, Sequence

class Phase(str, Enum):
    UNDERSTAND = "understand"
    EXPLORE = "explore"
    PLAN = "plan"
    EXECUTE = "execute"
    VERIFY = "verify"
    RECOVER = "recover"
    COMPLETE = "complete"
    FAILED = "failed"

@dataclass(frozen=True, slots=True)
class EngineeringSnapshot:
    objective: str
    phase: Phase
    attempt: int
    plan_digest: str
    context_digest: str
    workspace_digest: str
    changed_files: tuple[str, ...] = ()
    verification_receipt: Mapping[str, Any] = field(default_factory=dict)
    recovery_history: tuple[str, ...] = ()
    next_action: str = ""

    def to_artifact(self) -> dict[str, Any]:
        return {
            "api": "aether.coding-engineering-state/1",
            "objective": self.objective,
            "phase": self.phase.value,
            "attempt": self.attempt,
            "planDigest": self.plan_digest,
            "contextDigest": self.context_digest,
            "workspaceDigest": self.workspace_digest,
            "changedFiles": list(self.changed_files),
            "verificationReceipt": dict(self.verification_receipt),
            "recoveryHistory": list(self.recovery_history),
            "nextAction": self.next_action,
        }

class SessionFactory(Protocol):
    def __call__(self, *, attempt: int, engineering_state: Mapping[str, Any]) -> Any: ...

class WorkspaceProbe(Protocol):
    def digest(self) -> str: ...
    def changed_files(self) -> Sequence[str]: ...

class StateSink(Protocol):
    def capture(self, snapshot: EngineeringSnapshot) -> str: ...
```

## 4. Novo arquivo: `packs/code-default/coding_max/state_bridge.py`

```python
from __future__ import annotations

from dataclasses import replace
from typing import Any, Mapping

from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.runtime.artifacts import ArtifactWriter
from vanguard.packages.runtime.task_state import CodingTaskState

from .contracts import EngineeringSnapshot, Phase
from .planning import Plan

def plan_digest(plan: Plan) -> str:
    return digest_of(plan.to_dict())

def to_runtime_task_state(snapshot: EngineeringSnapshot, plan: Plan) -> CodingTaskState:
    return CodingTaskState(
        objective=snapshot.objective,
        plan=tuple(item.description for item in plan.steps),
        strategy_steps=tuple(item.status.value for item in plan.steps),
        modified_files=snapshot.changed_files,
        verification_plan=plan.verification_strategy,
        last_verification=dict(snapshot.verification_receipt),
        failure_class=snapshot.recovery_history[-1] if snapshot.recovery_history else None,
        next_action=snapshot.next_action,
    )

class ArtifactStateSink:
    def __init__(self, writer: ArtifactWriter, *, run_id: str, episode_id: str) -> None:
        self.writer = writer
        self.run_id = run_id
        self.episode_id = episode_id

    def capture(self, snapshot: EngineeringSnapshot) -> str:
        ref = self.writer.capture(
            role="engineering_state",
            payload=snapshot.to_artifact(),
            run_id=self.run_id,
            episode_id=self.episode_id,
            required=True,
        )
        if not ref.digest:
            raise RuntimeError("engineering state capture produced no digest")
        return ref.digest

def advance(snapshot: EngineeringSnapshot, phase: Phase, **changes: Any) -> EngineeringSnapshot:
    return replace(snapshot, phase=phase, **changes)
```

## 5. Novo arquivo: `packs/code-default/coding_max/coordinator.py`

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

from vanguard.packages.agency.episode.admission_gate import AdmissionGate, VerificationReceipt

from .contracts import EngineeringSnapshot, Phase, SessionFactory, StateSink, WorkspaceProbe
from .planning import Plan
from .recovery import RecoveryAction
from .verification import VerificationResult
from .workflow import CodingMaxWorkflow, WorkflowDecision

@dataclass(frozen=True, slots=True)
class CoordinatorResult:
    completed: bool
    attempts: int
    reason: str
    state_digest: str
    session_results: tuple[Any, ...]

class CodingMaxCoordinator:
    def __init__(
        self,
        workflow: CodingMaxWorkflow,
        session_factory: SessionFactory,
        workspace: WorkspaceProbe,
        state_sink: StateSink,
        verifier: Callable[[Sequence[Sequence[str]]], Sequence[VerificationResult]],
        *,
        max_attempts: int = 4,
    ) -> None:
        self.workflow = workflow
        self.session_factory = session_factory
        self.workspace = workspace
        self.state_sink = state_sink
        self.verifier = verifier
        self.max_attempts = max_attempts
        self.admission = AdmissionGate(require_patch_for_write_presets=True)

    def run(
        self,
        task: str,
        *,
        repository_files: int,
        initial_hits: Sequence[str],
        available_tests: Sequence[str],
        verification_commands: Sequence[Sequence[str]],
        preset: str = "coding-max",
    ) -> CoordinatorResult:
        decision = self.workflow.start(
            task, repository_files=repository_files,
            initial_hits=initial_hits, available_tests=available_tests,
        )
        snapshot = EngineeringSnapshot(
            objective=task, phase=Phase.UNDERSTAND, attempt=0,
            plan_digest="", context_digest="",
            workspace_digest=self.workspace.digest(),
            next_action=decision.next_action,
        )
        results: list[Any] = []
        recovery: list[RecoveryAction] = []
        last_digest = self.state_sink.capture(snapshot)

        for attempt in range(1, self.max_attempts + 1):
            snapshot = EngineeringSnapshot(
                objective=task, phase=Phase.EXECUTE, attempt=attempt,
                plan_digest=decision.plan.to_dict().get("objective", task),
                context_digest="pending-context-artifact",
                workspace_digest=self.workspace.digest(),
                changed_files=tuple(self.workspace.changed_files()),
                recovery_history=tuple(item.value for item in recovery),
                next_action=decision.next_action,
            )
            last_digest = self.state_sink.capture(snapshot)
            session = self.session_factory(
                attempt=attempt, engineering_state=snapshot.to_artifact(),
            )
            result = session.run()
            results.append(result)

            verification_rows = tuple(self.verifier(verification_commands))
            last = verification_rows[-1] if verification_rows else VerificationResult(
                command=(), exit_code=-1, test_count=0, duration_ms=0,
                stdout="", stderr="verification pipeline returned no result",
            )
            current_workspace = self.workspace.digest()
            receipt = VerificationReceipt(
                exit_code=last.exit_code,
                executed_test_count=last.test_count,
                workspace_digest=current_workspace,
            )
            verdict = self.admission.evaluate(
                preset, self.workspace.changed_files(),
                {"kind": "finish"},
                verification=receipt,
                current_workspace_digest=current_workspace,
                task_requirements_satisfied=True,
                model_requested_finish=True,
            )
            snapshot = EngineeringSnapshot(
                objective=task,
                phase=Phase.COMPLETE if verdict.admissible else Phase.RECOVER,
                attempt=attempt,
                plan_digest=snapshot.plan_digest,
                context_digest=snapshot.context_digest,
                workspace_digest=current_workspace,
                changed_files=tuple(self.workspace.changed_files()),
                verification_receipt={
                    "exitCode": last.exit_code,
                    "executedTestCount": last.test_count,
                    "workspaceDigest": current_workspace,
                    "admissionReason": verdict.reason,
                },
                recovery_history=tuple(item.value for item in recovery),
                next_action="complete" if verdict.admissible else "recover",
            )
            last_digest = self.state_sink.capture(snapshot)
            if verdict.admissible:
                return CoordinatorResult(True, attempt, verdict.reason, last_digest, tuple(results))

            decision = self.workflow.after_verification(
                decision, last, attempts=attempt, previous=tuple(recovery),
            )
            if decision.recovery is RecoveryAction.STOP:
                return CoordinatorResult(False, attempt, "recovery_stop", last_digest, tuple(results))
            if decision.recovery is not None:
                recovery.append(decision.recovery)

        return CoordinatorResult(False, self.max_attempts, "attempts_exhausted", last_digest, tuple(results))
```

## 6. Diff em `packs/code-default/load.py`

```diff
@@
 __all__ = [
     "compile_pack",
+    "load_coding_max",
 ]
+def load_coding_max(*, routes, session_factory, workspace, state_sink, verifier, max_attempts=4):
+    from coding_max.workflow import CodingMaxWorkflow
+    from coding_max.coordinator import CodingMaxCoordinator
+    workflow = CodingMaxWorkflow(routes, max_attempts=max_attempts)
+    return CodingMaxCoordinator(
+        workflow, session_factory, workspace, state_sink, verifier,
+        max_attempts=max_attempts,
+    )
```

## 7. Diff em `packs/code-default/coding_max/workflow.py`

```diff
@@ class CodingMaxWorkflow:
+    def snapshot(self, decision: WorkflowDecision) -> dict[str, object]:
+        return {
+            "profile": {
+                "taskType": decision.profile.task_type,
+                "complexity": decision.profile.estimated_complexity,
+                "uncertainty": decision.profile.uncertainty,
+                "workflow": decision.profile.suggested_workflow,
+                "budget": dict(decision.profile.initial_budget),
+            },
+            "plan": decision.plan.to_dict(),
+            "route": {
+                "provider": decision.route.provider,
+                "model": decision.route.model,
+                "tier": decision.route.tier,
+            },
+            "nextAction": decision.next_action,
+            "recovery": decision.recovery.value if decision.recovery else None,
+        }
```

## 8. Testes novos: `test/packs/code_default/test_coding_max_coordinator.py`

```python
from __future__ import annotations

import unittest
from dataclasses import dataclass

from coding_max.coordinator import CodingMaxCoordinator
from coding_max.routing import ModelRoute
from coding_max.verification import VerificationResult
from coding_max.workflow import CodingMaxWorkflow

class FakeWorkspace:
    def __init__(self) -> None:
        self.version = 0
        self.files: list[str] = []
    def digest(self) -> str:
        return f"workspace-{self.version}"
    def changed_files(self):
        return tuple(self.files)

class FakeSink:
    def __init__(self) -> None:
        self.rows = []
    def capture(self, snapshot):
        self.rows.append(snapshot)
        return f"state-{len(self.rows)}"

@dataclass
class FakeSessionResult:
    terminal: str = "COMPLETED"

class FakeSession:
    def __init__(self, workspace, patch):
        self.workspace = workspace
        self.patch = patch
    def run(self):
        if self.patch:
            self.workspace.files[:] = ["src/a.py"]
            self.workspace.version += 1
        return FakeSessionResult()

class CoordinatorTests(unittest.TestCase):
    def make(self, *, patch=True, results=()):
        workspace = FakeWorkspace()
        sink = FakeSink()
        workflow = CodingMaxWorkflow((
            ModelRoute("fake", "small", 1),
            ModelRoute("fake", "frontier", 2),
        ))
        coordinator = CodingMaxCoordinator(
            workflow,
            lambda **_: FakeSession(workspace, patch),
            workspace, sink, lambda _: results,
            max_attempts=2,
        )
        return coordinator, workspace, sink

    def test_real_patch_and_fresh_tests_complete(self):
        result_row = VerificationResult(("pytest",), 0, 3, 1, "3 passed", "")
        coordinator, _, sink = self.make(results=(result_row,))
        result = coordinator.run(
            "fix bug", repository_files=10, initial_hits=("a.py",),
            available_tests=("test_a.py",), verification_commands=(("pytest",),),
        )
        self.assertTrue(result.completed)
        self.assertEqual(sink.rows[-1].phase.value, "complete")

    def test_no_patch_never_completes(self):
        result_row = VerificationResult(("pytest",), 0, 3, 1, "3 passed", "")
        coordinator, _, _ = self.make(patch=False, results=(result_row,))
        result = coordinator.run(
            "fix bug", repository_files=10, initial_hits=("a.py",),
            available_tests=("test_a.py",), verification_commands=(("pytest",),),
        )
        self.assertFalse(result.completed)

    def test_zero_tests_never_complete(self):
        row = VerificationResult(("pytest",), 0, 0, 1, "", "")
        coordinator, _, _ = self.make(results=(row,))
        result = coordinator.run(
            "fix bug", repository_files=10, initial_hits=("a.py",),
            available_tests=("test_a.py",), verification_commands=(("pytest",),),
        )
        self.assertFalse(result.completed)

    def test_state_is_captured_before_and_after_session(self):
        row = VerificationResult(("pytest",), 0, 1, 1, "1 passed", "")
        coordinator, _, sink = self.make(results=(row,))
        coordinator.run(
            "fix bug", repository_files=10, initial_hits=("a.py",),
            available_tests=("test_a.py",), verification_commands=(("pytest",),),
        )
        self.assertGreaterEqual(len(sink.rows), 3)
```

## 9. Contratos de integração

| ID | Contrato | Condição de falha | Resposta |
|---|---|---|---|
| RT-001 | Uma tentativa cria exatamente uma sessão canônica | segunda engine/loop interno | rejeitar composição |
| RT-002 | Todo efeito passa por `HarnessSession` | toolkit chamado diretamente | falha arquitetural |
| RT-003 | Estado precede efeitos | snapshot ausente | não iniciar sessão |
| RT-004 | Verificação é externa ao modelo | self-report | inaceitável |
| RT-005 | Workspace digest vincula receipt | digest divergente | VERIFICATION_STALE |
| RT-006 | Patch é obrigatório em preset write | lista vazia | MISSING_SOURCE_PATCH |
| RT-007 | Zero testes não passa | test_count=0 | VERIFICATION_FAILED |
| RT-008 | Recovery é bounded | attempt >= max | STOP |
| RT-009 | Estado é artifact-backed | capture sem digest | falha terminal |
| RT-010 | Modelo pode mudar, autoridade não | route troca kernel | rejeitar |

## 10. Sequência de implementação

1. Adicionar `contracts.py` e seus tipos puros.
2. Adicionar `state_bridge.py` reutilizando `ArtifactWriter` e `CodingTaskState`.
3. Adicionar `coordinator.py` sem importar adapters concretos.
4. Expor factory mínima em `load.py`.
5. Adicionar testes com sessão/workspace/sink falsos.
6. Conectar factory ao entrypoint backend existente somente após testes de contrato.
7. Executar testes do pack e admission gate.
8. Executar boundary/TCB/duplication/secret checks.
9. Rodar smoke real em repositório descartável.
10. Capturar trajectory e engineering-state digests.

## 11. Matriz de cenários obrigatórios

| Cenário | Patch | Testes | Resultado esperado | Evento/artefato |
|---|---:|---:|---|---|
| simple fix | sim | 1 pass | complete | engineering_state |
| no-op model | não | pass | reject | admission rejection |
| stale test | sim | pass antigo | reject | VERIFICATION_STALE |
| zero tests | sim | 0 | recover | failure:test |
| dependency error | sim | erro | repair environment | failure:dependency |
| timeout | sim | timeout | narrow scope | failure:timeout |
| same recovery twice | sim | fail | escalate/stop | recovery history |
| budget exhausted | sim | fail | stop | budget receipt |
| provider unavailable | n/a | n/a | route fallback | route artifact |
| artifact failure | n/a | n/a | terminal fail | capture degradation |

## 12. Observabilidade mínima

- Cada tentativa registra `attempt`, `phase`, `nextAction` e route.
- Cada verificação registra comando, exit code, count, duration e workspace digest.
- Cada recuperação registra failure class e strategy transition.
- Cada completion aponta para patch digest, test receipt e engineering-state digest.
- Nenhum payload grande entra inline no ledger; somente referências CAS.

## 13. Falhas e tratamento

| Falha | Recoverable | Estratégia | Terminal quando |
|---|---:|---|---|
| session factory | não | corrigir composição | sempre |
| model unavailable | sim | próxima route | nenhuma route |
| patch missing | sim | feedback explícito | attempts exhausted |
| tests failing | sim | target failure | max attempts |
| tests timeout | sim | narrow suite | repetição |
| artifact capture | não | fail closed | sempre |
| stale receipt | sim | rerun tests | budget exhausted |
| budget denied | não | stop | imediatamente |

## 14. Gates de aceite

- [ ] Nenhum import novo em kernel.
- [ ] Nenhum schema wire alterado.
- [ ] `HarnessSession.run()` é o único executor.
- [ ] AdmissionGate rejeita no-op, zero-test e stale receipt.
- [ ] Engineering state é reconstruível sem transcript.
- [ ] Recovery troca ação ou para; nunca repete indefinidamente.
- [ ] Route escalation não amplia capabilities.
- [ ] Testes focados passam offline.
- [ ] Smoke aplica patch real e executa teste real.
- [ ] Trajectory liga task, patch, test e completion.

## 15. Checklist de revisão por símbolo

- [ ] RT-R001 — `EngineeringSnapshot`: input types verified.
- [ ] RT-R002 — `EngineeringSnapshot`: empty values rejected.
- [ ] RT-R003 — `EngineeringSnapshot`: identity bound.
- [ ] RT-R004 — `EngineeringSnapshot`: budget propagated.
- [ ] RT-R005 — `EngineeringSnapshot`: authority unchanged.
- [ ] RT-R006 — `EngineeringSnapshot`: artifact referenced.
- [ ] RT-R007 — `EngineeringSnapshot`: failure typed.
- [ ] RT-R008 — `EngineeringSnapshot`: retry bounded.
- [ ] RT-R009 — `EngineeringSnapshot`: replay deterministic.
- [ ] RT-R010 — `EngineeringSnapshot`: test covers success.
- [ ] RT-R011 — `EngineeringSnapshot`: test covers failure.
- [ ] RT-R012 — `EngineeringSnapshot`: telemetry emitted.
- [ ] RT-R013 — `EngineeringSnapshot`: secret payload excluded.
- [ ] RT-R014 — `EngineeringSnapshot`: workspace freshness checked.
- [ ] RT-R015 — `EngineeringSnapshot`: backward compatibility retained.
- [ ] RT-R016 — `EngineeringSnapshot`: provider failure isolated.
- [ ] RT-R017 — `EngineeringSnapshot`: completion externally admitted.
- [ ] RT-R018 — `EngineeringSnapshot`: state serializable.
- [ ] RT-R019 — `EngineeringSnapshot`: no transcript dependency.
- [ ] RT-R020 — `EngineeringSnapshot`: no duplicate runtime.
- [ ] RT-R021 — `ArtifactStateSink`: input types verified.
- [ ] RT-R022 — `ArtifactStateSink`: empty values rejected.
- [ ] RT-R023 — `ArtifactStateSink`: identity bound.
- [ ] RT-R024 — `ArtifactStateSink`: budget propagated.
- [ ] RT-R025 — `ArtifactStateSink`: authority unchanged.
- [ ] RT-R026 — `ArtifactStateSink`: artifact referenced.
- [ ] RT-R027 — `ArtifactStateSink`: failure typed.
- [ ] RT-R028 — `ArtifactStateSink`: retry bounded.
- [ ] RT-R029 — `ArtifactStateSink`: replay deterministic.
- [ ] RT-R030 — `ArtifactStateSink`: test covers success.
- [ ] RT-R031 — `ArtifactStateSink`: test covers failure.
- [ ] RT-R032 — `ArtifactStateSink`: telemetry emitted.
- [ ] RT-R033 — `ArtifactStateSink`: secret payload excluded.
- [ ] RT-R034 — `ArtifactStateSink`: workspace freshness checked.
- [ ] RT-R035 — `ArtifactStateSink`: backward compatibility retained.
- [ ] RT-R036 — `ArtifactStateSink`: provider failure isolated.
- [ ] RT-R037 — `ArtifactStateSink`: completion externally admitted.
- [ ] RT-R038 — `ArtifactStateSink`: state serializable.
- [ ] RT-R039 — `ArtifactStateSink`: no transcript dependency.
- [ ] RT-R040 — `ArtifactStateSink`: no duplicate runtime.
- [ ] RT-R041 — `CodingMaxCoordinator.run`: input types verified.
- [ ] RT-R042 — `CodingMaxCoordinator.run`: empty values rejected.
- [ ] RT-R043 — `CodingMaxCoordinator.run`: identity bound.
- [ ] RT-R044 — `CodingMaxCoordinator.run`: budget propagated.
- [ ] RT-R045 — `CodingMaxCoordinator.run`: authority unchanged.
- [ ] RT-R046 — `CodingMaxCoordinator.run`: artifact referenced.
- [ ] RT-R047 — `CodingMaxCoordinator.run`: failure typed.
- [ ] RT-R048 — `CodingMaxCoordinator.run`: retry bounded.
- [ ] RT-R049 — `CodingMaxCoordinator.run`: replay deterministic.
- [ ] RT-R050 — `CodingMaxCoordinator.run`: test covers success.
- [ ] RT-R051 — `CodingMaxCoordinator.run`: test covers failure.
- [ ] RT-R052 — `CodingMaxCoordinator.run`: telemetry emitted.
- [ ] RT-R053 — `CodingMaxCoordinator.run`: secret payload excluded.
- [ ] RT-R054 — `CodingMaxCoordinator.run`: workspace freshness checked.
- [ ] RT-R055 — `CodingMaxCoordinator.run`: backward compatibility retained.
- [ ] RT-R056 — `CodingMaxCoordinator.run`: provider failure isolated.
- [ ] RT-R057 — `CodingMaxCoordinator.run`: completion externally admitted.
- [ ] RT-R058 — `CodingMaxCoordinator.run`: state serializable.
- [ ] RT-R059 — `CodingMaxCoordinator.run`: no transcript dependency.
- [ ] RT-R060 — `CodingMaxCoordinator.run`: no duplicate runtime.
- [ ] RT-R061 — `CodingMaxWorkflow.snapshot`: input types verified.
- [ ] RT-R062 — `CodingMaxWorkflow.snapshot`: empty values rejected.
- [ ] RT-R063 — `CodingMaxWorkflow.snapshot`: identity bound.
- [ ] RT-R064 — `CodingMaxWorkflow.snapshot`: budget propagated.
- [ ] RT-R065 — `CodingMaxWorkflow.snapshot`: authority unchanged.
- [ ] RT-R066 — `CodingMaxWorkflow.snapshot`: artifact referenced.
- [ ] RT-R067 — `CodingMaxWorkflow.snapshot`: failure typed.
- [ ] RT-R068 — `CodingMaxWorkflow.snapshot`: retry bounded.
- [ ] RT-R069 — `CodingMaxWorkflow.snapshot`: replay deterministic.
- [ ] RT-R070 — `CodingMaxWorkflow.snapshot`: test covers success.
- [ ] RT-R071 — `CodingMaxWorkflow.snapshot`: test covers failure.
- [ ] RT-R072 — `CodingMaxWorkflow.snapshot`: telemetry emitted.
- [ ] RT-R073 — `CodingMaxWorkflow.snapshot`: secret payload excluded.
- [ ] RT-R074 — `CodingMaxWorkflow.snapshot`: workspace freshness checked.
- [ ] RT-R075 — `CodingMaxWorkflow.snapshot`: backward compatibility retained.
- [ ] RT-R076 — `CodingMaxWorkflow.snapshot`: provider failure isolated.
- [ ] RT-R077 — `CodingMaxWorkflow.snapshot`: completion externally admitted.
- [ ] RT-R078 — `CodingMaxWorkflow.snapshot`: state serializable.
- [ ] RT-R079 — `CodingMaxWorkflow.snapshot`: no transcript dependency.
- [ ] RT-R080 — `CodingMaxWorkflow.snapshot`: no duplicate runtime.
- [ ] RT-R081 — `AdmissionGate.evaluate`: input types verified.
- [ ] RT-R082 — `AdmissionGate.evaluate`: empty values rejected.
- [ ] RT-R083 — `AdmissionGate.evaluate`: identity bound.
- [ ] RT-R084 — `AdmissionGate.evaluate`: budget propagated.
- [ ] RT-R085 — `AdmissionGate.evaluate`: authority unchanged.
- [ ] RT-R086 — `AdmissionGate.evaluate`: artifact referenced.
- [ ] RT-R087 — `AdmissionGate.evaluate`: failure typed.
- [ ] RT-R088 — `AdmissionGate.evaluate`: retry bounded.
- [ ] RT-R089 — `AdmissionGate.evaluate`: replay deterministic.
- [ ] RT-R090 — `AdmissionGate.evaluate`: test covers success.
- [ ] RT-R091 — `AdmissionGate.evaluate`: test covers failure.
- [ ] RT-R092 — `AdmissionGate.evaluate`: telemetry emitted.
- [ ] RT-R093 — `AdmissionGate.evaluate`: secret payload excluded.
- [ ] RT-R094 — `AdmissionGate.evaluate`: workspace freshness checked.
- [ ] RT-R095 — `AdmissionGate.evaluate`: backward compatibility retained.
- [ ] RT-R096 — `AdmissionGate.evaluate`: provider failure isolated.
- [ ] RT-R097 — `AdmissionGate.evaluate`: completion externally admitted.
- [ ] RT-R098 — `AdmissionGate.evaluate`: state serializable.
- [ ] RT-R099 — `AdmissionGate.evaluate`: no transcript dependency.
- [ ] RT-R100 — `AdmissionGate.evaluate`: no duplicate runtime.
- [ ] RT-R101 — `HarnessSession.run`: input types verified.
- [ ] RT-R102 — `HarnessSession.run`: empty values rejected.
- [ ] RT-R103 — `HarnessSession.run`: identity bound.
- [ ] RT-R104 — `HarnessSession.run`: budget propagated.
- [ ] RT-R105 — `HarnessSession.run`: authority unchanged.
- [ ] RT-R106 — `HarnessSession.run`: artifact referenced.
- [ ] RT-R107 — `HarnessSession.run`: failure typed.
- [ ] RT-R108 — `HarnessSession.run`: retry bounded.
- [ ] RT-R109 — `HarnessSession.run`: replay deterministic.
- [ ] RT-R110 — `HarnessSession.run`: test covers success.
- [ ] RT-R111 — `HarnessSession.run`: test covers failure.
- [ ] RT-R112 — `HarnessSession.run`: telemetry emitted.
- [ ] RT-R113 — `HarnessSession.run`: secret payload excluded.
- [ ] RT-R114 — `HarnessSession.run`: workspace freshness checked.
- [ ] RT-R115 — `HarnessSession.run`: backward compatibility retained.
- [ ] RT-R116 — `HarnessSession.run`: provider failure isolated.
- [ ] RT-R117 — `HarnessSession.run`: completion externally admitted.
- [ ] RT-R118 — `HarnessSession.run`: state serializable.
- [ ] RT-R119 — `HarnessSession.run`: no transcript dependency.
- [ ] RT-R120 — `HarnessSession.run`: no duplicate runtime.
- [ ] RT-R121 — `ArtifactWriter.capture`: input types verified.
- [ ] RT-R122 — `ArtifactWriter.capture`: empty values rejected.
- [ ] RT-R123 — `ArtifactWriter.capture`: identity bound.
- [ ] RT-R124 — `ArtifactWriter.capture`: budget propagated.
- [ ] RT-R125 — `ArtifactWriter.capture`: authority unchanged.
- [ ] RT-R126 — `ArtifactWriter.capture`: artifact referenced.
- [ ] RT-R127 — `ArtifactWriter.capture`: failure typed.
- [ ] RT-R128 — `ArtifactWriter.capture`: retry bounded.
- [ ] RT-R129 — `ArtifactWriter.capture`: replay deterministic.
- [ ] RT-R130 — `ArtifactWriter.capture`: test covers success.
- [ ] RT-R131 — `ArtifactWriter.capture`: test covers failure.
- [ ] RT-R132 — `ArtifactWriter.capture`: telemetry emitted.
- [ ] RT-R133 — `ArtifactWriter.capture`: secret payload excluded.
- [ ] RT-R134 — `ArtifactWriter.capture`: workspace freshness checked.
- [ ] RT-R135 — `ArtifactWriter.capture`: backward compatibility retained.
- [ ] RT-R136 — `ArtifactWriter.capture`: provider failure isolated.
- [ ] RT-R137 — `ArtifactWriter.capture`: completion externally admitted.
- [ ] RT-R138 — `ArtifactWriter.capture`: state serializable.
- [ ] RT-R139 — `ArtifactWriter.capture`: no transcript dependency.
- [ ] RT-R140 — `ArtifactWriter.capture`: no duplicate runtime.
- [ ] RT-R141 — `CodingTaskState`: input types verified.
- [ ] RT-R142 — `CodingTaskState`: empty values rejected.
- [ ] RT-R143 — `CodingTaskState`: identity bound.
- [ ] RT-R144 — `CodingTaskState`: budget propagated.
- [ ] RT-R145 — `CodingTaskState`: authority unchanged.
- [ ] RT-R146 — `CodingTaskState`: artifact referenced.
- [ ] RT-R147 — `CodingTaskState`: failure typed.
- [ ] RT-R148 — `CodingTaskState`: retry bounded.
- [ ] RT-R149 — `CodingTaskState`: replay deterministic.
- [ ] RT-R150 — `CodingTaskState`: test covers success.
- [ ] RT-R151 — `CodingTaskState`: test covers failure.
- [ ] RT-R152 — `CodingTaskState`: telemetry emitted.
- [ ] RT-R153 — `CodingTaskState`: secret payload excluded.
- [ ] RT-R154 — `CodingTaskState`: workspace freshness checked.
- [ ] RT-R155 — `CodingTaskState`: backward compatibility retained.
- [ ] RT-R156 — `CodingTaskState`: provider failure isolated.
- [ ] RT-R157 — `CodingTaskState`: completion externally admitted.
- [ ] RT-R158 — `CodingTaskState`: state serializable.
- [ ] RT-R159 — `CodingTaskState`: no transcript dependency.
- [ ] RT-R160 — `CodingTaskState`: no duplicate runtime.
- [ ] RT-R161 — `LayeredVerifier.verify`: input types verified.
- [ ] RT-R162 — `LayeredVerifier.verify`: empty values rejected.
- [ ] RT-R163 — `LayeredVerifier.verify`: identity bound.
- [ ] RT-R164 — `LayeredVerifier.verify`: budget propagated.
- [ ] RT-R165 — `LayeredVerifier.verify`: authority unchanged.
- [ ] RT-R166 — `LayeredVerifier.verify`: artifact referenced.
- [ ] RT-R167 — `LayeredVerifier.verify`: failure typed.
- [ ] RT-R168 — `LayeredVerifier.verify`: retry bounded.
- [ ] RT-R169 — `LayeredVerifier.verify`: replay deterministic.
- [ ] RT-R170 — `LayeredVerifier.verify`: test covers success.
- [ ] RT-R171 — `LayeredVerifier.verify`: test covers failure.
- [ ] RT-R172 — `LayeredVerifier.verify`: telemetry emitted.
- [ ] RT-R173 — `LayeredVerifier.verify`: secret payload excluded.
- [ ] RT-R174 — `LayeredVerifier.verify`: workspace freshness checked.
- [ ] RT-R175 — `LayeredVerifier.verify`: backward compatibility retained.
- [ ] RT-R176 — `LayeredVerifier.verify`: provider failure isolated.
- [ ] RT-R177 — `LayeredVerifier.verify`: completion externally admitted.
- [ ] RT-R178 — `LayeredVerifier.verify`: state serializable.
- [ ] RT-R179 — `LayeredVerifier.verify`: no transcript dependency.
- [ ] RT-R180 — `LayeredVerifier.verify`: no duplicate runtime.
- [ ] RT-R181 — `RecoveryPolicy.select`: input types verified.
- [ ] RT-R182 — `RecoveryPolicy.select`: empty values rejected.
- [ ] RT-R183 — `RecoveryPolicy.select`: identity bound.
- [ ] RT-R184 — `RecoveryPolicy.select`: budget propagated.
- [ ] RT-R185 — `RecoveryPolicy.select`: authority unchanged.
- [ ] RT-R186 — `RecoveryPolicy.select`: artifact referenced.
- [ ] RT-R187 — `RecoveryPolicy.select`: failure typed.
- [ ] RT-R188 — `RecoveryPolicy.select`: retry bounded.
- [ ] RT-R189 — `RecoveryPolicy.select`: replay deterministic.
- [ ] RT-R190 — `RecoveryPolicy.select`: test covers success.
- [ ] RT-R191 — `RecoveryPolicy.select`: test covers failure.
- [ ] RT-R192 — `RecoveryPolicy.select`: telemetry emitted.
- [ ] RT-R193 — `RecoveryPolicy.select`: secret payload excluded.
- [ ] RT-R194 — `RecoveryPolicy.select`: workspace freshness checked.
- [ ] RT-R195 — `RecoveryPolicy.select`: backward compatibility retained.
- [ ] RT-R196 — `RecoveryPolicy.select`: provider failure isolated.
- [ ] RT-R197 — `RecoveryPolicy.select`: completion externally admitted.
- [ ] RT-R198 — `RecoveryPolicy.select`: state serializable.
- [ ] RT-R199 — `RecoveryPolicy.select`: no transcript dependency.
- [ ] RT-R200 — `RecoveryPolicy.select`: no duplicate runtime.

## 16. Definition of Done

Esta onda está concluída somente quando o coordinator executa um patch real através da sessão canônica, recebe receipts do kernel, roda verificação externa sobre o digest corrente, persiste estado de engenharia e obtém admissão explícita. Teste verde isolado não substitui esse smoke causal.

## 17. Não objetivos

- Não implementar swarm nesta onda.
- Não implementar mutation learning nesta onda.
- Não alterar o kernel para conhecer coding.
- Não usar resposta textual como evidência.
- Não promover benchmark sintético.

- [ ] RT-X700 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X701 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X702 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X703 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X704 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X705 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X706 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X707 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X708 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X709 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X710 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X711 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X712 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X713 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X714 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X715 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X716 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X717 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X718 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X719 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X720 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X721 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X722 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X723 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X724 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X725 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X726 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X727 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X728 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X729 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X730 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X731 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X732 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X733 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X734 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X735 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X736 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X737 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X738 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X739 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X740 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X741 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X742 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X743 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X744 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X745 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X746 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X747 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X748 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X749 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X750 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X751 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X752 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X753 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X754 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X755 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X756 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X757 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X758 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X759 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X760 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X761 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X762 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X763 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X764 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X765 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X766 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X767 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X768 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X769 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X770 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X771 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X772 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X773 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X774 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X775 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X776 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X777 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X778 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X779 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X780 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X781 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X782 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X783 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X784 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X785 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X786 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X787 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X788 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X789 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X790 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X791 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X792 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X793 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X794 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X795 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X796 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X797 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X798 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X799 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X800 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X801 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X802 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X803 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X804 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X805 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X806 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X807 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X808 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X809 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X810 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X811 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X812 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X813 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X814 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X815 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X816 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X817 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X818 — Verificar integração causal adicional antes de promover esta onda.
- [ ] RT-X819 — Verificar integração causal adicional antes de promover esta onda.
