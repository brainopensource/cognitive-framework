# Full Code Manifest — Wave 6: Estado Durável, Artifacts, Checkpoints e Resume

## 0. Objetivo

Fechar CM-12/CM-13: tornar tarefas longas semanticamente retomáveis após crash, sem depender do transcript e sem criar uma segunda persistência. O estado autoritativo continua no ledger; payloads grandes ficam no CAS; checkpoints aceleram reconstrução e nunca substituem eventos.

## 1. Substrato real reutilizado

- `vanguard/packages/runtime/task_state.py::CodingTaskState`.
- `vanguard/packages/runtime/checkpoints.py::CheckpointManager`.
- `vanguard/packages/runtime/artifacts.py::ArtifactWriter`.
- `vanguard/packages/adapters/stores/event_store.py::SqliteEventStore`.
- `vanguard/packages/adapters/stores/blob_store.py::FileBlobStore`.
- `vanguard/packages/runtime/session.py::{checkpoint,reconstruct}`.
- `vanguard/packages/runtime/workflow_recovery.py::replay_workflow_events`.

## 2. Invariante de autoridade

```text
events = truth
artifacts = content-addressed payloads
checkpoint = verified acceleration
projection = reconstructed working state
transcript = optional context, never sole memory
```

## 3. Novo arquivo: `packs/code-default/coding_max/durable_state.py`

```python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.runtime.task_state import CodingTaskState

@dataclass(frozen=True, slots=True)
class AttemptRecord:
    attempt: int
    route: Mapping[str, Any]
    context_digest: str
    patch_digest: str | None
    verification_digest: str | None
    failure_class: str | None
    recovery_action: str | None

@dataclass(frozen=True, slots=True)
class DurableCodingState:
    api: str
    objective: str
    task_digest: str
    plan_digest: str
    todo_digest: str
    workspace_digest: str
    next_action: str
    attempts: tuple[AttemptRecord, ...] = ()
    pinned_context: tuple[str, ...] = ()
    changed_files: tuple[str, ...] = ()
    settled_effects: tuple[str, ...] = ()
    remaining_budget: Mapping[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.api != "aether.coding-state/1":
            raise ValueError("unsupported coding state api")
        if not self.objective or not self.task_digest:
            raise ValueError("objective and task_digest are required")
        if any(value < 0 for value in self.remaining_budget.values()):
            raise ValueError("remaining budget cannot be negative")

    def to_dict(self) -> dict[str, Any]:
        return {
            "api": self.api,
            "objective": self.objective,
            "taskDigest": self.task_digest,
            "planDigest": self.plan_digest,
            "todoDigest": self.todo_digest,
            "workspaceDigest": self.workspace_digest,
            "nextAction": self.next_action,
            "attempts": [
                {
                    "attempt": row.attempt,
                    "route": dict(row.route),
                    "contextDigest": row.context_digest,
                    "patchDigest": row.patch_digest,
                    "verificationDigest": row.verification_digest,
                    "failureClass": row.failure_class,
                    "recoveryAction": row.recovery_action,
                } for row in self.attempts
            ],
            "pinnedContext": list(self.pinned_context),
            "changedFiles": list(self.changed_files),
            "settledEffects": list(self.settled_effects),
            "remainingBudget": dict(self.remaining_budget),
        }

    def digest(self) -> str:
        return digest_of(self.to_dict())

    def to_runtime(self) -> CodingTaskState:
        return CodingTaskState(
            objective=self.objective,
            plan=(self.plan_digest,),
            strategy_steps=tuple(row.recovery_action or "execute" for row in self.attempts),
            modified_files=self.changed_files,
            verification_plan=("artifact:" + (self.attempts[-1].verification_digest or "absent"),) if self.attempts else (),
            failure_class=self.attempts[-1].failure_class if self.attempts else None,
            next_action=self.next_action,
            settled_effects=self.settled_effects,
            remaining_budgets=dict(self.remaining_budget),
        )

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "DurableCodingState":
        attempts = tuple(AttemptRecord(
            attempt=int(row["attempt"]),
            route=dict(row.get("route") or {}),
            context_digest=str(row.get("contextDigest") or ""),
            patch_digest=row.get("patchDigest"),
            verification_digest=row.get("verificationDigest"),
            failure_class=row.get("failureClass"),
            recovery_action=row.get("recoveryAction"),
        ) for row in raw.get("attempts", ()))
        return cls(
            api=str(raw.get("api") or ""),
            objective=str(raw.get("objective") or ""),
            task_digest=str(raw.get("taskDigest") or ""),
            plan_digest=str(raw.get("planDigest") or ""),
            todo_digest=str(raw.get("todoDigest") or ""),
            workspace_digest=str(raw.get("workspaceDigest") or ""),
            next_action=str(raw.get("nextAction") or ""),
            attempts=attempts,
            pinned_context=tuple(raw.get("pinnedContext") or ()),
            changed_files=tuple(raw.get("changedFiles") or ()),
            settled_effects=tuple(raw.get("settledEffects") or ()),
            remaining_budget={str(k): int(v) for k, v in dict(raw.get("remainingBudget") or {}).items()},
        )
```

## 4. Novo arquivo: `packs/code-default/coding_max/durable_store.py`

```python
from __future__ import annotations

import json
from typing import Any

from vanguard.packages.runtime.artifacts import ArtifactWriter

from .durable_state import DurableCodingState

class DurableCodingStateStore:
    def __init__(self, writer: ArtifactWriter, blob_store: Any, *, run_id: str, episode_id: str) -> None:
        self.writer = writer
        self.blob_store = blob_store
        self.run_id = run_id
        self.episode_id = episode_id

    def save(self, state: DurableCodingState) -> str:
        ref = self.writer.capture(
            role="coding_state", payload=state.to_dict(),
            run_id=self.run_id, episode_id=self.episode_id, required=True,
        )
        if ref.digest is None:
            raise RuntimeError("coding state was not retained")
        return ref.digest

    def load(self, digest: str) -> DurableCodingState:
        result = self.blob_store.get(digest)
        if hasattr(result, "error"):
            raise KeyError(digest)
        raw = json.loads(result.value.decode("utf-8"))
        state = DurableCodingState.from_dict(raw)
        if state.digest() == "":
            raise ValueError("invalid state digest")
        return state
```

## 5. Novo arquivo: `packs/code-default/coding_max/resume.py`

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from vanguard.packages.runtime.checkpoints import CheckpointManager, Reconstruction

from .durable_state import DurableCodingState

@dataclass(frozen=True, slots=True)
class ResumePlan:
    source: str
    state: DurableCodingState
    reconstructed_event_count: int
    workspace_matches: bool
    next_action: str

class SemanticResumer:
    def __init__(
        self, checkpoint_manager: CheckpointManager, state_loader: Callable[[str], DurableCodingState],
        workspace_digest: Callable[[], str],
    ) -> None:
        self.checkpoints = checkpoint_manager
        self.state_loader = state_loader
        self.workspace_digest = workspace_digest

    def resume(self, *, state_digest: str, verify: bool = True) -> ResumePlan:
        reconstruction = self.checkpoints.restore_latest(verify=verify)
        state = self.state_loader(state_digest)
        matches = self.workspace_digest() == state.workspace_digest
        action = state.next_action if matches else "reconcile_workspace"
        return ResumePlan(
            source=reconstruction.source,
            state=state,
            reconstructed_event_count=reconstruction.event_count,
            workspace_matches=matches,
            next_action=action,
        )
```

## 6. Diff em `coordinator.py`

```diff
@@ class CodingMaxCoordinator.__init__(
+        durable_store=None, checkpoint=None,
@@
+        self.durable_store = durable_store
+        self.checkpoint_manager = checkpoint
@@ for attempt in ...:
+            durable_digest = None
+            if self.durable_store is not None:
+                durable_digest = self.durable_store.save(build_durable_state(snapshot, decision))
+            if self.checkpoint_manager is not None:
+                self.checkpoint_manager.capture(
+                    state=session.ledger_state(),
+                    reason=f"coding-max-attempt-{attempt}",
+                    metadata={"codingStateDigest": durable_digest},
+                )
```

## 7. Diff em `task_state.py`

```diff
@@ class CodingTaskState:
+    engineering_state_digest: str = ""
@@ def to_canonical_dict(self):
+            "engineeringStateDigest": self.engineering_state_digest,
@@ def from_mapping(cls, raw):
+            engineering_state_digest=str(raw.get("engineeringStateDigest", "")),
```

Observação: alterar `CodingTaskState` somente se o contrato aceita evolução aditiva. Se isso mudar schema/digest normativo, manter o digest em metadata de checkpoint/artifact e não tocar runtime nesta release.

## 8. Testes: `test/packs/code_default/test_durable_coding_state.py`

```python
from __future__ import annotations

import unittest

from coding_max.durable_state import AttemptRecord, DurableCodingState

class DurableCodingStateTests(unittest.TestCase):
    def state(self):
        return DurableCodingState(
            api="aether.coding-state/1",
            objective="fix race", task_digest="sha256:task",
            plan_digest="sha256:plan", todo_digest="sha256:todo",
            workspace_digest="sha256:workspace", next_action="verify",
            attempts=(AttemptRecord(
                1, {"provider": "fake", "model": "m"},
                "sha256:context", "sha256:patch", None, "test", "target_failure",
            ),),
            changed_files=("src/a.py",),
            settled_effects=("effect-1",),
            remaining_budget={"turns": 3, "tokens": 1000},
        )

    def test_roundtrip_is_digest_stable(self):
        first = self.state()
        second = DurableCodingState.from_dict(first.to_dict())
        self.assertEqual(first.digest(), second.digest())

    def test_runtime_projection_has_next_action(self):
        projected = self.state().to_runtime()
        self.assertEqual(projected.next_action, "verify")
        self.assertEqual(projected.modified_files, ("src/a.py",))

    def test_negative_budget_is_rejected(self):
        raw = self.state().to_dict()
        raw["remainingBudget"] = {"tokens": -1}
        with self.assertRaises(ValueError):
            DurableCodingState.from_dict(raw)
```

## 9. Testes de crash/resume

```python
class ResumeFalsifiers(unittest.TestCase):
    def test_crash_after_intent_before_receipt_reconciles_effect(self): ...
    def test_crash_after_patch_before_verification_resumes_at_verify(self): ...
    def test_crash_after_verification_before_completion_rechecks_admission(self): ...
    def test_corrupt_checkpoint_falls_back_to_cold_fold(self): ...
    def test_missing_state_artifact_fails_closed(self): ...
    def test_workspace_drift_selects_reconcile_action(self): ...
    def test_settled_effect_is_not_reexecuted(self): ...
    def test_remaining_budget_never_increases(self): ...
```

## 10. Crash matrix

| Crash point | Durable facts | Resume action | Prohibited |
|---|---|---|---|
| before session | task/state | execute | invent receipt |
| after intent | intent only | reconcile effect | duplicate effect |
| after patch receipt | patch digest | verify | reapply patch |
| during test | proc intent | rerun bounded test | claim pass |
| after test receipt | verification | admission | rerun patch |
| after checkpoint | events + checkpoint | verified suffix fold | trust checkpoint blindly |
| after completion event | terminal | return completed | new attempt |

## 11. Retention roles

| Role | Required | Typical size | Retention |
|---|---:|---:|---|
| task | yes | small | durable |
| plan | yes | small | durable |
| todo | yes | small | durable |
| coding_state | yes | small | durable |
| context | yes | medium | policy |
| patch | yes | medium | durable |
| test_stdout | optional | large | bounded |
| test_receipt | yes | small | durable |
| model_io | profile | large | policy |
| checkpoint | yes for resume | medium | rolling |

## 12. Invariantes

| ID | Regra |
|---|---|
| DR-001 | Events override checkpoint |
| DR-002 | Checkpoint pins composition/run/profile |
| DR-003 | State artifact is content addressed |
| DR-004 | Budget cannot increase on resume |
| DR-005 | Settled effects are idempotent |
| DR-006 | Workspace drift is explicit |
| DR-007 | Missing artifact fails closed |
| DR-008 | Corrupt checkpoint cold-folds |
| DR-009 | No transcript-only state |
| DR-010 | Next action is semantic |
| DR-011 | Verification freshness survives restart |
| DR-012 | Model route identity retained |
| DR-013 | Patch digest retained |
| DR-014 | Failure history retained |
| DR-015 | Recovery history retained |
| DR-016 | Todo dependencies retained |
| DR-017 | Artifact redaction retained |
| DR-018 | Retention policy independent |
| DR-019 | Replay deterministic |
| DR-020 | Completion not duplicated |

## 13. Ordem de implementação

1. Implementar `DurableCodingState` puro.
2. Validar roundtrip/digest.
3. Implementar store sobre ArtifactWriter/blob port.
4. Integrar save antes/depois de cada tentativa.
5. Capturar checkpoint com state digest.
6. Implementar SemanticResumer.
7. Adicionar falsificadores de crash.
8. Validar cold fold e corrupted checkpoint.
9. Rodar fresh-process resume.
10. Proibir promotion sem esse smoke.

## 14. Checklist por componente

- [ ] DR-R001 — `DurableCodingState.to_dict`: canonical serialization.
- [ ] DR-R002 — `DurableCodingState.to_dict`: unknown field policy.
- [ ] DR-R003 — `DurableCodingState.to_dict`: missing field policy.
- [ ] DR-R004 — `DurableCodingState.to_dict`: digest stability.
- [ ] DR-R005 — `DurableCodingState.to_dict`: artifact existence.
- [ ] DR-R006 — `DurableCodingState.to_dict`: corruption handling.
- [ ] DR-R007 — `DurableCodingState.to_dict`: budget conservation.
- [ ] DR-R008 — `DurableCodingState.to_dict`: effect idempotency.
- [ ] DR-R009 — `DurableCodingState.to_dict`: workspace binding.
- [ ] DR-R010 — `DurableCodingState.to_dict`: route provenance.
- [ ] DR-R011 — `DurableCodingState.to_dict`: failure provenance.
- [ ] DR-R012 — `DurableCodingState.to_dict`: next-action fidelity.
- [ ] DR-R013 — `DurableCodingState.to_dict`: offline unit test.
- [ ] DR-R014 — `DurableCodingState.to_dict`: fresh-process test.
- [ ] DR-R015 — `DurableCodingState.to_dict`: crash test.
- [ ] DR-R016 — `DurableCodingState.to_dict`: cold-fold fallback.
- [ ] DR-R017 — `DurableCodingState.to_dict`: retention compatibility.
- [ ] DR-R018 — `DurableCodingState.to_dict`: secret safety.
- [ ] DR-R019 — `DurableCodingState.to_dict`: schema compatibility.
- [ ] DR-R020 — `DurableCodingState.to_dict`: backward compatibility.
- [ ] DR-R021 — `DurableCodingState.to_dict`: telemetry.
- [ ] DR-R022 — `DurableCodingState.to_dict`: no duplicate store.
- [ ] DR-R023 — `DurableCodingState.to_dict`: no transcript dependency.
- [ ] DR-R024 — `DurableCodingState.to_dict`: terminal semantics.
- [ ] DR-R025 — `DurableCodingState.to_dict`: documentation.
- [ ] DR-R026 — `DurableCodingState.from_dict`: canonical serialization.
- [ ] DR-R027 — `DurableCodingState.from_dict`: unknown field policy.
- [ ] DR-R028 — `DurableCodingState.from_dict`: missing field policy.
- [ ] DR-R029 — `DurableCodingState.from_dict`: digest stability.
- [ ] DR-R030 — `DurableCodingState.from_dict`: artifact existence.
- [ ] DR-R031 — `DurableCodingState.from_dict`: corruption handling.
- [ ] DR-R032 — `DurableCodingState.from_dict`: budget conservation.
- [ ] DR-R033 — `DurableCodingState.from_dict`: effect idempotency.
- [ ] DR-R034 — `DurableCodingState.from_dict`: workspace binding.
- [ ] DR-R035 — `DurableCodingState.from_dict`: route provenance.
- [ ] DR-R036 — `DurableCodingState.from_dict`: failure provenance.
- [ ] DR-R037 — `DurableCodingState.from_dict`: next-action fidelity.
- [ ] DR-R038 — `DurableCodingState.from_dict`: offline unit test.
- [ ] DR-R039 — `DurableCodingState.from_dict`: fresh-process test.
- [ ] DR-R040 — `DurableCodingState.from_dict`: crash test.
- [ ] DR-R041 — `DurableCodingState.from_dict`: cold-fold fallback.
- [ ] DR-R042 — `DurableCodingState.from_dict`: retention compatibility.
- [ ] DR-R043 — `DurableCodingState.from_dict`: secret safety.
- [ ] DR-R044 — `DurableCodingState.from_dict`: schema compatibility.
- [ ] DR-R045 — `DurableCodingState.from_dict`: backward compatibility.
- [ ] DR-R046 — `DurableCodingState.from_dict`: telemetry.
- [ ] DR-R047 — `DurableCodingState.from_dict`: no duplicate store.
- [ ] DR-R048 — `DurableCodingState.from_dict`: no transcript dependency.
- [ ] DR-R049 — `DurableCodingState.from_dict`: terminal semantics.
- [ ] DR-R050 — `DurableCodingState.from_dict`: documentation.
- [ ] DR-R051 — `DurableCodingState.digest`: canonical serialization.
- [ ] DR-R052 — `DurableCodingState.digest`: unknown field policy.
- [ ] DR-R053 — `DurableCodingState.digest`: missing field policy.
- [ ] DR-R054 — `DurableCodingState.digest`: digest stability.
- [ ] DR-R055 — `DurableCodingState.digest`: artifact existence.
- [ ] DR-R056 — `DurableCodingState.digest`: corruption handling.
- [ ] DR-R057 — `DurableCodingState.digest`: budget conservation.
- [ ] DR-R058 — `DurableCodingState.digest`: effect idempotency.
- [ ] DR-R059 — `DurableCodingState.digest`: workspace binding.
- [ ] DR-R060 — `DurableCodingState.digest`: route provenance.
- [ ] DR-R061 — `DurableCodingState.digest`: failure provenance.
- [ ] DR-R062 — `DurableCodingState.digest`: next-action fidelity.
- [ ] DR-R063 — `DurableCodingState.digest`: offline unit test.
- [ ] DR-R064 — `DurableCodingState.digest`: fresh-process test.
- [ ] DR-R065 — `DurableCodingState.digest`: crash test.
- [ ] DR-R066 — `DurableCodingState.digest`: cold-fold fallback.
- [ ] DR-R067 — `DurableCodingState.digest`: retention compatibility.
- [ ] DR-R068 — `DurableCodingState.digest`: secret safety.
- [ ] DR-R069 — `DurableCodingState.digest`: schema compatibility.
- [ ] DR-R070 — `DurableCodingState.digest`: backward compatibility.
- [ ] DR-R071 — `DurableCodingState.digest`: telemetry.
- [ ] DR-R072 — `DurableCodingState.digest`: no duplicate store.
- [ ] DR-R073 — `DurableCodingState.digest`: no transcript dependency.
- [ ] DR-R074 — `DurableCodingState.digest`: terminal semantics.
- [ ] DR-R075 — `DurableCodingState.digest`: documentation.
- [ ] DR-R076 — `DurableCodingState.to_runtime`: canonical serialization.
- [ ] DR-R077 — `DurableCodingState.to_runtime`: unknown field policy.
- [ ] DR-R078 — `DurableCodingState.to_runtime`: missing field policy.
- [ ] DR-R079 — `DurableCodingState.to_runtime`: digest stability.
- [ ] DR-R080 — `DurableCodingState.to_runtime`: artifact existence.
- [ ] DR-R081 — `DurableCodingState.to_runtime`: corruption handling.
- [ ] DR-R082 — `DurableCodingState.to_runtime`: budget conservation.
- [ ] DR-R083 — `DurableCodingState.to_runtime`: effect idempotency.
- [ ] DR-R084 — `DurableCodingState.to_runtime`: workspace binding.
- [ ] DR-R085 — `DurableCodingState.to_runtime`: route provenance.
- [ ] DR-R086 — `DurableCodingState.to_runtime`: failure provenance.
- [ ] DR-R087 — `DurableCodingState.to_runtime`: next-action fidelity.
- [ ] DR-R088 — `DurableCodingState.to_runtime`: offline unit test.
- [ ] DR-R089 — `DurableCodingState.to_runtime`: fresh-process test.
- [ ] DR-R090 — `DurableCodingState.to_runtime`: crash test.
- [ ] DR-R091 — `DurableCodingState.to_runtime`: cold-fold fallback.
- [ ] DR-R092 — `DurableCodingState.to_runtime`: retention compatibility.
- [ ] DR-R093 — `DurableCodingState.to_runtime`: secret safety.
- [ ] DR-R094 — `DurableCodingState.to_runtime`: schema compatibility.
- [ ] DR-R095 — `DurableCodingState.to_runtime`: backward compatibility.
- [ ] DR-R096 — `DurableCodingState.to_runtime`: telemetry.
- [ ] DR-R097 — `DurableCodingState.to_runtime`: no duplicate store.
- [ ] DR-R098 — `DurableCodingState.to_runtime`: no transcript dependency.
- [ ] DR-R099 — `DurableCodingState.to_runtime`: terminal semantics.
- [ ] DR-R100 — `DurableCodingState.to_runtime`: documentation.
- [ ] DR-R101 — `DurableCodingStateStore.save`: canonical serialization.
- [ ] DR-R102 — `DurableCodingStateStore.save`: unknown field policy.
- [ ] DR-R103 — `DurableCodingStateStore.save`: missing field policy.
- [ ] DR-R104 — `DurableCodingStateStore.save`: digest stability.
- [ ] DR-R105 — `DurableCodingStateStore.save`: artifact existence.
- [ ] DR-R106 — `DurableCodingStateStore.save`: corruption handling.
- [ ] DR-R107 — `DurableCodingStateStore.save`: budget conservation.
- [ ] DR-R108 — `DurableCodingStateStore.save`: effect idempotency.
- [ ] DR-R109 — `DurableCodingStateStore.save`: workspace binding.
- [ ] DR-R110 — `DurableCodingStateStore.save`: route provenance.
- [ ] DR-R111 — `DurableCodingStateStore.save`: failure provenance.
- [ ] DR-R112 — `DurableCodingStateStore.save`: next-action fidelity.
- [ ] DR-R113 — `DurableCodingStateStore.save`: offline unit test.
- [ ] DR-R114 — `DurableCodingStateStore.save`: fresh-process test.
- [ ] DR-R115 — `DurableCodingStateStore.save`: crash test.
- [ ] DR-R116 — `DurableCodingStateStore.save`: cold-fold fallback.
- [ ] DR-R117 — `DurableCodingStateStore.save`: retention compatibility.
- [ ] DR-R118 — `DurableCodingStateStore.save`: secret safety.
- [ ] DR-R119 — `DurableCodingStateStore.save`: schema compatibility.
- [ ] DR-R120 — `DurableCodingStateStore.save`: backward compatibility.
- [ ] DR-R121 — `DurableCodingStateStore.save`: telemetry.
- [ ] DR-R122 — `DurableCodingStateStore.save`: no duplicate store.
- [ ] DR-R123 — `DurableCodingStateStore.save`: no transcript dependency.
- [ ] DR-R124 — `DurableCodingStateStore.save`: terminal semantics.
- [ ] DR-R125 — `DurableCodingStateStore.save`: documentation.
- [ ] DR-R126 — `DurableCodingStateStore.load`: canonical serialization.
- [ ] DR-R127 — `DurableCodingStateStore.load`: unknown field policy.
- [ ] DR-R128 — `DurableCodingStateStore.load`: missing field policy.
- [ ] DR-R129 — `DurableCodingStateStore.load`: digest stability.
- [ ] DR-R130 — `DurableCodingStateStore.load`: artifact existence.
- [ ] DR-R131 — `DurableCodingStateStore.load`: corruption handling.
- [ ] DR-R132 — `DurableCodingStateStore.load`: budget conservation.
- [ ] DR-R133 — `DurableCodingStateStore.load`: effect idempotency.
- [ ] DR-R134 — `DurableCodingStateStore.load`: workspace binding.
- [ ] DR-R135 — `DurableCodingStateStore.load`: route provenance.
- [ ] DR-R136 — `DurableCodingStateStore.load`: failure provenance.
- [ ] DR-R137 — `DurableCodingStateStore.load`: next-action fidelity.
- [ ] DR-R138 — `DurableCodingStateStore.load`: offline unit test.
- [ ] DR-R139 — `DurableCodingStateStore.load`: fresh-process test.
- [ ] DR-R140 — `DurableCodingStateStore.load`: crash test.
- [ ] DR-R141 — `DurableCodingStateStore.load`: cold-fold fallback.
- [ ] DR-R142 — `DurableCodingStateStore.load`: retention compatibility.
- [ ] DR-R143 — `DurableCodingStateStore.load`: secret safety.
- [ ] DR-R144 — `DurableCodingStateStore.load`: schema compatibility.
- [ ] DR-R145 — `DurableCodingStateStore.load`: backward compatibility.
- [ ] DR-R146 — `DurableCodingStateStore.load`: telemetry.
- [ ] DR-R147 — `DurableCodingStateStore.load`: no duplicate store.
- [ ] DR-R148 — `DurableCodingStateStore.load`: no transcript dependency.
- [ ] DR-R149 — `DurableCodingStateStore.load`: terminal semantics.
- [ ] DR-R150 — `DurableCodingStateStore.load`: documentation.
- [ ] DR-R151 — `SemanticResumer.resume`: canonical serialization.
- [ ] DR-R152 — `SemanticResumer.resume`: unknown field policy.
- [ ] DR-R153 — `SemanticResumer.resume`: missing field policy.
- [ ] DR-R154 — `SemanticResumer.resume`: digest stability.
- [ ] DR-R155 — `SemanticResumer.resume`: artifact existence.
- [ ] DR-R156 — `SemanticResumer.resume`: corruption handling.
- [ ] DR-R157 — `SemanticResumer.resume`: budget conservation.
- [ ] DR-R158 — `SemanticResumer.resume`: effect idempotency.
- [ ] DR-R159 — `SemanticResumer.resume`: workspace binding.
- [ ] DR-R160 — `SemanticResumer.resume`: route provenance.
- [ ] DR-R161 — `SemanticResumer.resume`: failure provenance.
- [ ] DR-R162 — `SemanticResumer.resume`: next-action fidelity.
- [ ] DR-R163 — `SemanticResumer.resume`: offline unit test.
- [ ] DR-R164 — `SemanticResumer.resume`: fresh-process test.
- [ ] DR-R165 — `SemanticResumer.resume`: crash test.
- [ ] DR-R166 — `SemanticResumer.resume`: cold-fold fallback.
- [ ] DR-R167 — `SemanticResumer.resume`: retention compatibility.
- [ ] DR-R168 — `SemanticResumer.resume`: secret safety.
- [ ] DR-R169 — `SemanticResumer.resume`: schema compatibility.
- [ ] DR-R170 — `SemanticResumer.resume`: backward compatibility.
- [ ] DR-R171 — `SemanticResumer.resume`: telemetry.
- [ ] DR-R172 — `SemanticResumer.resume`: no duplicate store.
- [ ] DR-R173 — `SemanticResumer.resume`: no transcript dependency.
- [ ] DR-R174 — `SemanticResumer.resume`: terminal semantics.
- [ ] DR-R175 — `SemanticResumer.resume`: documentation.
- [ ] DR-R176 — `CheckpointManager.capture`: canonical serialization.
- [ ] DR-R177 — `CheckpointManager.capture`: unknown field policy.
- [ ] DR-R178 — `CheckpointManager.capture`: missing field policy.
- [ ] DR-R179 — `CheckpointManager.capture`: digest stability.
- [ ] DR-R180 — `CheckpointManager.capture`: artifact existence.
- [ ] DR-R181 — `CheckpointManager.capture`: corruption handling.
- [ ] DR-R182 — `CheckpointManager.capture`: budget conservation.
- [ ] DR-R183 — `CheckpointManager.capture`: effect idempotency.
- [ ] DR-R184 — `CheckpointManager.capture`: workspace binding.
- [ ] DR-R185 — `CheckpointManager.capture`: route provenance.
- [ ] DR-R186 — `CheckpointManager.capture`: failure provenance.
- [ ] DR-R187 — `CheckpointManager.capture`: next-action fidelity.
- [ ] DR-R188 — `CheckpointManager.capture`: offline unit test.
- [ ] DR-R189 — `CheckpointManager.capture`: fresh-process test.
- [ ] DR-R190 — `CheckpointManager.capture`: crash test.
- [ ] DR-R191 — `CheckpointManager.capture`: cold-fold fallback.
- [ ] DR-R192 — `CheckpointManager.capture`: retention compatibility.
- [ ] DR-R193 — `CheckpointManager.capture`: secret safety.
- [ ] DR-R194 — `CheckpointManager.capture`: schema compatibility.
- [ ] DR-R195 — `CheckpointManager.capture`: backward compatibility.
- [ ] DR-R196 — `CheckpointManager.capture`: telemetry.
- [ ] DR-R197 — `CheckpointManager.capture`: no duplicate store.
- [ ] DR-R198 — `CheckpointManager.capture`: no transcript dependency.
- [ ] DR-R199 — `CheckpointManager.capture`: terminal semantics.
- [ ] DR-R200 — `CheckpointManager.capture`: documentation.
- [ ] DR-R201 — `CheckpointManager.restore_latest`: canonical serialization.
- [ ] DR-R202 — `CheckpointManager.restore_latest`: unknown field policy.
- [ ] DR-R203 — `CheckpointManager.restore_latest`: missing field policy.
- [ ] DR-R204 — `CheckpointManager.restore_latest`: digest stability.
- [ ] DR-R205 — `CheckpointManager.restore_latest`: artifact existence.
- [ ] DR-R206 — `CheckpointManager.restore_latest`: corruption handling.
- [ ] DR-R207 — `CheckpointManager.restore_latest`: budget conservation.
- [ ] DR-R208 — `CheckpointManager.restore_latest`: effect idempotency.
- [ ] DR-R209 — `CheckpointManager.restore_latest`: workspace binding.
- [ ] DR-R210 — `CheckpointManager.restore_latest`: route provenance.
- [ ] DR-R211 — `CheckpointManager.restore_latest`: failure provenance.
- [ ] DR-R212 — `CheckpointManager.restore_latest`: next-action fidelity.
- [ ] DR-R213 — `CheckpointManager.restore_latest`: offline unit test.
- [ ] DR-R214 — `CheckpointManager.restore_latest`: fresh-process test.
- [ ] DR-R215 — `CheckpointManager.restore_latest`: crash test.
- [ ] DR-R216 — `CheckpointManager.restore_latest`: cold-fold fallback.
- [ ] DR-R217 — `CheckpointManager.restore_latest`: retention compatibility.
- [ ] DR-R218 — `CheckpointManager.restore_latest`: secret safety.
- [ ] DR-R219 — `CheckpointManager.restore_latest`: schema compatibility.
- [ ] DR-R220 — `CheckpointManager.restore_latest`: backward compatibility.
- [ ] DR-R221 — `CheckpointManager.restore_latest`: telemetry.
- [ ] DR-R222 — `CheckpointManager.restore_latest`: no duplicate store.
- [ ] DR-R223 — `CheckpointManager.restore_latest`: no transcript dependency.
- [ ] DR-R224 — `CheckpointManager.restore_latest`: terminal semantics.
- [ ] DR-R225 — `CheckpointManager.restore_latest`: documentation.
- [ ] DR-R226 — `Coordinator checkpoint integration`: canonical serialization.
- [ ] DR-R227 — `Coordinator checkpoint integration`: unknown field policy.
- [ ] DR-R228 — `Coordinator checkpoint integration`: missing field policy.
- [ ] DR-R229 — `Coordinator checkpoint integration`: digest stability.
- [ ] DR-R230 — `Coordinator checkpoint integration`: artifact existence.
- [ ] DR-R231 — `Coordinator checkpoint integration`: corruption handling.
- [ ] DR-R232 — `Coordinator checkpoint integration`: budget conservation.
- [ ] DR-R233 — `Coordinator checkpoint integration`: effect idempotency.
- [ ] DR-R234 — `Coordinator checkpoint integration`: workspace binding.
- [ ] DR-R235 — `Coordinator checkpoint integration`: route provenance.
- [ ] DR-R236 — `Coordinator checkpoint integration`: failure provenance.
- [ ] DR-R237 — `Coordinator checkpoint integration`: next-action fidelity.
- [ ] DR-R238 — `Coordinator checkpoint integration`: offline unit test.
- [ ] DR-R239 — `Coordinator checkpoint integration`: fresh-process test.
- [ ] DR-R240 — `Coordinator checkpoint integration`: crash test.
- [ ] DR-R241 — `Coordinator checkpoint integration`: cold-fold fallback.
- [ ] DR-R242 — `Coordinator checkpoint integration`: retention compatibility.
- [ ] DR-R243 — `Coordinator checkpoint integration`: secret safety.
- [ ] DR-R244 — `Coordinator checkpoint integration`: schema compatibility.
- [ ] DR-R245 — `Coordinator checkpoint integration`: backward compatibility.
- [ ] DR-R246 — `Coordinator checkpoint integration`: telemetry.
- [ ] DR-R247 — `Coordinator checkpoint integration`: no duplicate store.
- [ ] DR-R248 — `Coordinator checkpoint integration`: no transcript dependency.
- [ ] DR-R249 — `Coordinator checkpoint integration`: terminal semantics.
- [ ] DR-R250 — `Coordinator checkpoint integration`: documentation.

## 15. Acceptance gates

- [ ] Processo A cria estado, eventos e checkpoint.
- [ ] Processo A é encerrado sem shutdown limpo.
- [ ] Processo B abre SQLite/CAS existentes.
- [ ] Checkpoint é verificado contra pins.
- [ ] Suffix fold reconstrói estado exato.
- [ ] Next action retoma em verify/recover, não no início.
- [ ] Efeitos settled não repetem.
- [ ] Budget remanescente não aumenta.
- [ ] Workspace divergente não recebe patch automaticamente.
- [ ] Completion continua sujeito ao AdmissionGate.

## 16. Definition of Done

A onda só fecha com fresh-process continuation demonstrando identidade, budget, settled effects, patch, verificação e next-action corretos. Serialização verde no mesmo processo não basta.

- [ ] DR-X645 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X646 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X647 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X648 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X649 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X650 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X651 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X652 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X653 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X654 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X655 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X656 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X657 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X658 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X659 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X660 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X661 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X662 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X663 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X664 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X665 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X666 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X667 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X668 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X669 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X670 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X671 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X672 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X673 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X674 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X675 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X676 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X677 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X678 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X679 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X680 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X681 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X682 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X683 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X684 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X685 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X686 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X687 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X688 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X689 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X690 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X691 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X692 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X693 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X694 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X695 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X696 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X697 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X698 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X699 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X700 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X701 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X702 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X703 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X704 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X705 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X706 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X707 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X708 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X709 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X710 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X711 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X712 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X713 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X714 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X715 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X716 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X717 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X718 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X719 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X720 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X721 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X722 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X723 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X724 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X725 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X726 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X727 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X728 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X729 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X730 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X731 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X732 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X733 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X734 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X735 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X736 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X737 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X738 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X739 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X740 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X741 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X742 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X743 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X744 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X745 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X746 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X747 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X748 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X749 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X750 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X751 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X752 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X753 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X754 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X755 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X756 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X757 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X758 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X759 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X760 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X761 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X762 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X763 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X764 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X765 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X766 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X767 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X768 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X769 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X770 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X771 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X772 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X773 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X774 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X775 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X776 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X777 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X778 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X779 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X780 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X781 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X782 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X783 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X784 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X785 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X786 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X787 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X788 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X789 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X790 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X791 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X792 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X793 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X794 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X795 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X796 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X797 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X798 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X799 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X800 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X801 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X802 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X803 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X804 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X805 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X806 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X807 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X808 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X809 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X810 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X811 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X812 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X813 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X814 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X815 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X816 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X817 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X818 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X819 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X820 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X821 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X822 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X823 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X824 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X825 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X826 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X827 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X828 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X829 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X830 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X831 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X832 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X833 — Verificar propriedade adicional de replay antes de promoção.
- [ ] DR-X834 — Verificar propriedade adicional de replay antes de promoção.
