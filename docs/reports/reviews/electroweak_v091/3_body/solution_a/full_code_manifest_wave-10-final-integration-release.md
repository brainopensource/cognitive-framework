# Full Code Manifest — Wave 10: Integração Final, Migração e Release do Coding Harness

## 0. Finalidade

Este manifest é o índice executável que une Waves 1–9, resolve dependências, define commits/feature flags, testes mínimos, rollback, observabilidade e critérios honestos para declarar o harness pronto. Ele não repete todo o código; referencia os manifests que contêm os diffs completos.

## 1. Dependência total

```text
W1 classify/plan/presets
  ├─ W2 intelligence/context
  └─ W3 verify/recovery/routing
        ↓
W4 coordinator/Vanguard integration
        ↓
W5 workspace/tools/verification
        ↓
W6 durable state/checkpoint/resume
        ├─ W7 reflex/branch/mutation/capsules
        ├─ W8 LDA/LAM/benchmark qualification
        └─ W9 ToolScript/specialists/reviewer
                         ↓
                    W10 release
```

## 2. Estrutura final

```text
packs/code-default/
├── coding_max/
│   ├── __init__.py
│   ├── contracts.py
│   ├── classifier.py
│   ├── planning.py
│   ├── intelligence.py
│   ├── intelligence_router.py
│   ├── lda_adapter.py
│   ├── context.py
│   ├── test_selector.py
│   ├── verification.py
│   ├── verification_pipeline.py
│   ├── recovery.py
│   ├── routing.py
│   ├── workflow.py
│   ├── coordinator.py
│   ├── state_bridge.py
│   ├── durable_state.py
│   ├── durable_store.py
│   ├── resume.py
│   ├── workspace_tx.py
│   ├── tool_results.py
│   ├── reflex.py
│   ├── branch_search.py
│   ├── mutation.py
│   ├── capsules.py
│   ├── toolscript.py
│   ├── toolscript_broker.py
│   ├── specialists.py
│   ├── reviewer.py
│   └── distill.py
├── presets/
│   ├── coding-fast.yaml
│   ├── coding-balanced.yaml
│   └── coding-max.yaml
└── toolkits/
    ├── fs_toolkit.py
    ├── ast_patch.py
    └── terminal_runner.py
benchmarks/coding_max/
├── task_protocol.py
├── preflight.py
└── runner.py
test/packs/code_default/
├── test_coding_max.py
├── test_coding_max_coordinator.py
├── test_workspace_tools.py
├── test_durable_coding_state.py
├── test_metamorphosis.py
└── test_toolscript_specialists.py
```

## 3. Feature flags

```python
# packs/code-default/coding_max/features.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

@dataclass(frozen=True, slots=True)
class CodingFeatures:
    progressive_context: bool = True
    durable_state: bool = True
    lda: bool = False
    toolscript: bool = False
    specialists: bool = False
    conditional_reviewer: bool = False
    branch_search: bool = False
    mutation: bool = False
    capsules: bool = False

    @classmethod
    def from_mapping(cls, raw: Mapping[str, object]):
        unknown = set(raw) - set(cls.__dataclass_fields__)
        if unknown: raise ValueError(f"unknown coding feature flags: {sorted(unknown)}")
        return cls(**{key: bool(value) for key, value in raw.items()})
```

## 4. Presets finais

```yaml
# coding-fast
features:
  progressive_context: true
  durable_state: true
  lda: false
  toolscript: false
  specialists: false
  conditional_reviewer: false
  branch_search: false
  mutation: false
  capsules: false

# coding-balanced
features:
  progressive_context: true
  durable_state: true
  lda: optional
  toolscript: true
  specialists: false
  conditional_reviewer: true
  branch_search: false
  mutation: false
  capsules: false

# coding-max
features:
  progressive_context: true
  durable_state: true
  lda: optional
  toolscript: true
  specialists: true
  conditional_reviewer: true
  branch_search: conditional
  mutation: experiment_only
  capsules: governed_only
```

## 5. Composition factory

```python
# packs/code-default/coding_max/factory.py
from __future__ import annotations

from dataclasses import dataclass

from .features import CodingFeatures

@dataclass(frozen=True, slots=True)
class CodingMaxComponents:
    coordinator: object
    intelligence: object
    verifier: object
    resumer: object
    optional: dict[str, object]

def build_coding_max(*, ports, config, routes, preset) -> CodingMaxComponents:
    features = CodingFeatures.from_mapping(config.get("features", {}))
    native = config["native_intelligence_factory"](ports.workspace)
    enriched = None
    if features.lda:
        enriched = config["lda_factory"](ports.workspace)
    intelligence = config["intelligence_router"](native, enriched)
    verifier = config["verifier_factory"](ports.workspace)
    durable = config["durable_store_factory"](ports.artifacts, ports.blobs)
    resumer = config["resumer_factory"](ports.checkpoints, durable.load, ports.workspace.digest)
    workflow = config["workflow_factory"](routes)
    coordinator = config["coordinator_factory"](
        workflow=workflow, session_factory=ports.session_factory,
        workspace=ports.workspace, state_sink=durable, verifier=verifier.verify,
    )
    optional = {}
    if features.toolscript: optional["toolscript"] = config["toolscript_factory"](intelligence)
    if features.specialists: optional["specialists"] = config["specialist_factory"](ports.models)
    if features.conditional_reviewer: optional["reviewer"] = config["reviewer_factory"](ports.models)
    if features.branch_search: optional["branch_search"] = config["branch_factory"](ports.child_runtime)
    if features.mutation: optional["mutator"] = config["mutator_factory"]()
    if features.capsules: optional["capsules"] = config["capsule_registry_factory"]()
    return CodingMaxComponents(coordinator, intelligence, verifier, resumer, optional)
```

## 6. Startup validation

```python
def validate_startup(components, *, preset, profile):
    errors = []
    if components.coordinator is None: errors.append("coordinator unavailable")
    if components.verifier is None: errors.append("verifier unavailable")
    if components.resumer is None and preset != "coding-fast": errors.append("resume unavailable")
    if profile.promotion_eligible and profile.assurance_level != "hermetic":
        errors.append("promotion requires hermetic assurance")
    if errors: raise RuntimeError("; ".join(errors))
```

## 7. Migração

1. Merge W1–W3 em commit único de componentes puros.
2. Merge W4 com flag interna desligada.
3. Merge W5 e executar smoke transacional.
4. Merge W6 e executar fresh-process resume.
5. Ativar `coding-fast` para dogfood local.
6. Ativar `coding-balanced` após 20 tarefas internas sem regressão.
7. Merge W8 benchmark truth antes de otimização.
8. Merge W9 ToolScript/reviewer atrás de flags.
9. Merge W7 branch/mutation somente como experimento.
10. Promover `coding-max` após ablations.

## 8. Compatibilidade

| Surface | Compatibilidade | Estratégia |
|---|---|---|
| Harness manifest wire | preservada | presets externos |
| Kernel dispatch | preservada | nenhuma mudança |
| Event identities | preservadas | artifacts/metadata existentes |
| Run digest | preservado/aditivo via extensions | digest-pin config |
| Checkpoint | preservado | state digest metadata |
| CLI | backend-only nesta entrega | entrypoint posterior |
| Existing code-default | preservado | feature flags off |
| Model adapters | reutilizados | router compõe |

## 9. Commit plan

| Commit | Conteúdo | Reversível | Gate |
|---|---|---:|---|
| C1 | classifier/planning/context | sim | unit |
| C2 | verification/recovery/router | sim | pack tests |
| C3 | coordinator/state bridge | sim | session contract |
| C4 | workspace/tool hardening | sim | adversarial |
| C5 | durability/resume | sim | fresh process |
| C6 | benchmark truth | sim | preflight |
| C7 | LDA/ToolScript | flag | fallback |
| C8 | reviewer/specialists | flag | ablation |
| C9 | branching | flag | budget/authority |
| C10 | mutation/capsules | experiment | heldout/governance |

## 10. Test matrix

| Suite | Required per commit | Required before beta |
|---|---:|---:|
| new unit | yes | yes |
| code-default pack | yes | yes |
| agency admission/context | affected | yes |
| runtime session/checkpoint | affected | yes |
| boundary/TCB/duplication | yes | yes |
| secret scan | yes | yes |
| transactional smoke | C4+ | yes |
| fresh-process resume | C5+ | yes |
| LAM truth | C6+ | yes |
| real-model canary | no | yes |
| full suite | no | yes |
| official benchmark | no | claim-only |

## 11. Minimal command runbook

```bash
python3 -m unittest test.packs.code_default.test_coding_max -v
python3 -m unittest test.packs.code_default.test_coding_max_coordinator -v
python3 -m unittest test.packs.code_default.test_workspace_tools -v
python3 -m unittest test.packs.code_default.test_durable_coding_state -v
python3 -m unittest test.packs.code_default.test_metamorphosis -v
python3 -m unittest discover -s test/packs/code_default -t .
python3 tools/linters/check_boundaries.py
python3 tools/linters/check_tcb_budget.py
python3 tools/linters/check_duplication.py --enforce
python3 tools/linters/scan_secrets.py
```

## 12. Observability schema

Cada run deve expor: task/profile/preset, feature flags, composition/run digests, repository subject, model routes, context selection/drop metrics, tool calls, patch digests, test receipts/count/duration, failures, recoveries, branch summaries, reviewer verdict, state/checkpoint digests, tokens/cost/latency e terminal reason.

## 13. SLOs iniciais

| SLO | coding-fast | balanced | max |
|---|---:|---:|---:|
| startup p95 | <1s | <2s | <3s |
| first tool p95 | <5s | <10s | <15s |
| zero-test acceptance | 0% | 0% | 0% |
| stale receipt acceptance | 0% | 0% | 0% |
| resume correctness | 100% | 100% | 100% |
| branch ceiling | 1 | 1 | 3 |
| reviewer rate | 0 | conditional | conditional |

## 14. Rollback

- Feature flags permitem desligar LDA, ToolScript, specialists, reviewer, branch, mutation e capsules independentemente.
- Coordinator pode voltar ao planner atual sem migração de ledger.
- Artifacts novos são roles adicionais e podem permanecer legíveis.
- Checkpoints incompatíveis devem cold-fold events.
- Capsule rollback exige receipt e restaura configuração anterior.
- Nunca apagar evidência de runs falhos.

## 15. Stop-ship conditions

| ID | Condição |
|---|---|
| SS-001 | any path escape |
| SS-002 | any capability expansion |
| SS-003 | budget increase after resume |
| SS-004 | zero-test admitted |
| SS-005 | stale receipt admitted |
| SS-006 | no-patch marked success |
| SS-007 | synthetic benchmark metric |
| SS-008 | answer leakage |
| SS-009 | checkpoint trusted after pin mismatch |
| SS-010 | duplicate effect after resume |
| SS-011 | branch writes parent directly |
| SS-012 | reviewer overrides failed evaluator |
| SS-013 | capsule self-promotes |
| SS-014 | missing trajectory link |
| SS-015 | secret in artifact/log |
| SS-016 | full suite regression attributable to change |
| SS-017 | fallback silently disables verification |
| SS-018 | unbounded retry |
| SS-019 | unbounded branch |
| SS-020 | wrong Git subject |

## 16. Acceptance levels

### Alpha
- Single-agent path, real patch/test, recovery, durable resume.
- No SWE claim.

### Beta
- Pack/runtime suites green, dogfood, canary, flags/rollback.
- LDA/ToolScript optional.
- Branch/mutation experimental.

### Production
- Release qualification, installable artifact, backup/restore, security/performance gates.

### SOTA claim
- Official or reproducible benchmark protocol.
- Competitive score with exact model/hardware/cost disclosure.
- Ablations showing harness contribution.
- Independent reproduction.

## 17. Ownership map

| Surface | Owner | Forbidden owner action |
|---|---|---|
| kernel | core | coding semantics |
| coordinator | code pack | bypass dispatch |
| tools | code pack | expand capability |
| model adapter | adapters | decide completion |
| verifier | external/runtime | trust model prose |
| benchmark | benchmark program | synthesize result |
| capsule registry | governance | self-promotion |

## 18. Checklist final por arquivo

- [ ] FINAL-0001 — `classifier.py`: path exists.
- [ ] FINAL-0002 — `classifier.py`: types strict.
- [ ] FINAL-0003 — `classifier.py`: public exports.
- [ ] FINAL-0004 — `classifier.py`: unknown inputs rejected.
- [ ] FINAL-0005 — `classifier.py`: typed errors.
- [ ] FINAL-0006 — `classifier.py`: budget bound.
- [ ] FINAL-0007 — `classifier.py`: authority preserved.
- [ ] FINAL-0008 — `classifier.py`: artifacts referenced.
- [ ] FINAL-0009 — `classifier.py`: unit success.
- [ ] FINAL-0010 — `classifier.py`: unit failure.
- [ ] FINAL-0011 — `classifier.py`: adversarial test.
- [ ] FINAL-0012 — `classifier.py`: integration coverage.
- [ ] FINAL-0013 — `classifier.py`: offline deterministic.
- [ ] FINAL-0014 — `classifier.py`: timeout.
- [ ] FINAL-0015 — `classifier.py`: idempotency.
- [ ] FINAL-0016 — `classifier.py`: replay semantics.
- [ ] FINAL-0017 — `classifier.py`: telemetry.
- [ ] FINAL-0018 — `classifier.py`: secret safety.
- [ ] FINAL-0019 — `classifier.py`: backward compatibility.
- [ ] FINAL-0020 — `classifier.py`: feature flag.
- [ ] FINAL-0021 — `classifier.py`: rollback.
- [ ] FINAL-0022 — `classifier.py`: docs manifest reference.
- [ ] FINAL-0023 — `planning.py`: path exists.
- [ ] FINAL-0024 — `planning.py`: types strict.
- [ ] FINAL-0025 — `planning.py`: public exports.
- [ ] FINAL-0026 — `planning.py`: unknown inputs rejected.
- [ ] FINAL-0027 — `planning.py`: typed errors.
- [ ] FINAL-0028 — `planning.py`: budget bound.
- [ ] FINAL-0029 — `planning.py`: authority preserved.
- [ ] FINAL-0030 — `planning.py`: artifacts referenced.
- [ ] FINAL-0031 — `planning.py`: unit success.
- [ ] FINAL-0032 — `planning.py`: unit failure.
- [ ] FINAL-0033 — `planning.py`: adversarial test.
- [ ] FINAL-0034 — `planning.py`: integration coverage.
- [ ] FINAL-0035 — `planning.py`: offline deterministic.
- [ ] FINAL-0036 — `planning.py`: timeout.
- [ ] FINAL-0037 — `planning.py`: idempotency.
- [ ] FINAL-0038 — `planning.py`: replay semantics.
- [ ] FINAL-0039 — `planning.py`: telemetry.
- [ ] FINAL-0040 — `planning.py`: secret safety.
- [ ] FINAL-0041 — `planning.py`: backward compatibility.
- [ ] FINAL-0042 — `planning.py`: feature flag.
- [ ] FINAL-0043 — `planning.py`: rollback.
- [ ] FINAL-0044 — `planning.py`: docs manifest reference.
- [ ] FINAL-0045 — `intelligence.py`: path exists.
- [ ] FINAL-0046 — `intelligence.py`: types strict.
- [ ] FINAL-0047 — `intelligence.py`: public exports.
- [ ] FINAL-0048 — `intelligence.py`: unknown inputs rejected.
- [ ] FINAL-0049 — `intelligence.py`: typed errors.
- [ ] FINAL-0050 — `intelligence.py`: budget bound.
- [ ] FINAL-0051 — `intelligence.py`: authority preserved.
- [ ] FINAL-0052 — `intelligence.py`: artifacts referenced.
- [ ] FINAL-0053 — `intelligence.py`: unit success.
- [ ] FINAL-0054 — `intelligence.py`: unit failure.
- [ ] FINAL-0055 — `intelligence.py`: adversarial test.
- [ ] FINAL-0056 — `intelligence.py`: integration coverage.
- [ ] FINAL-0057 — `intelligence.py`: offline deterministic.
- [ ] FINAL-0058 — `intelligence.py`: timeout.
- [ ] FINAL-0059 — `intelligence.py`: idempotency.
- [ ] FINAL-0060 — `intelligence.py`: replay semantics.
- [ ] FINAL-0061 — `intelligence.py`: telemetry.
- [ ] FINAL-0062 — `intelligence.py`: secret safety.
- [ ] FINAL-0063 — `intelligence.py`: backward compatibility.
- [ ] FINAL-0064 — `intelligence.py`: feature flag.
- [ ] FINAL-0065 — `intelligence.py`: rollback.
- [ ] FINAL-0066 — `intelligence.py`: docs manifest reference.
- [ ] FINAL-0067 — `context.py`: path exists.
- [ ] FINAL-0068 — `context.py`: types strict.
- [ ] FINAL-0069 — `context.py`: public exports.
- [ ] FINAL-0070 — `context.py`: unknown inputs rejected.
- [ ] FINAL-0071 — `context.py`: typed errors.
- [ ] FINAL-0072 — `context.py`: budget bound.
- [ ] FINAL-0073 — `context.py`: authority preserved.
- [ ] FINAL-0074 — `context.py`: artifacts referenced.
- [ ] FINAL-0075 — `context.py`: unit success.
- [ ] FINAL-0076 — `context.py`: unit failure.
- [ ] FINAL-0077 — `context.py`: adversarial test.
- [ ] FINAL-0078 — `context.py`: integration coverage.
- [ ] FINAL-0079 — `context.py`: offline deterministic.
- [ ] FINAL-0080 — `context.py`: timeout.
- [ ] FINAL-0081 — `context.py`: idempotency.
- [ ] FINAL-0082 — `context.py`: replay semantics.
- [ ] FINAL-0083 — `context.py`: telemetry.
- [ ] FINAL-0084 — `context.py`: secret safety.
- [ ] FINAL-0085 — `context.py`: backward compatibility.
- [ ] FINAL-0086 — `context.py`: feature flag.
- [ ] FINAL-0087 — `context.py`: rollback.
- [ ] FINAL-0088 — `context.py`: docs manifest reference.
- [ ] FINAL-0089 — `verification.py`: path exists.
- [ ] FINAL-0090 — `verification.py`: types strict.
- [ ] FINAL-0091 — `verification.py`: public exports.
- [ ] FINAL-0092 — `verification.py`: unknown inputs rejected.
- [ ] FINAL-0093 — `verification.py`: typed errors.
- [ ] FINAL-0094 — `verification.py`: budget bound.
- [ ] FINAL-0095 — `verification.py`: authority preserved.
- [ ] FINAL-0096 — `verification.py`: artifacts referenced.
- [ ] FINAL-0097 — `verification.py`: unit success.
- [ ] FINAL-0098 — `verification.py`: unit failure.
- [ ] FINAL-0099 — `verification.py`: adversarial test.
- [ ] FINAL-0100 — `verification.py`: integration coverage.
- [ ] FINAL-0101 — `verification.py`: offline deterministic.
- [ ] FINAL-0102 — `verification.py`: timeout.
- [ ] FINAL-0103 — `verification.py`: idempotency.
- [ ] FINAL-0104 — `verification.py`: replay semantics.
- [ ] FINAL-0105 — `verification.py`: telemetry.
- [ ] FINAL-0106 — `verification.py`: secret safety.
- [ ] FINAL-0107 — `verification.py`: backward compatibility.
- [ ] FINAL-0108 — `verification.py`: feature flag.
- [ ] FINAL-0109 — `verification.py`: rollback.
- [ ] FINAL-0110 — `verification.py`: docs manifest reference.
- [ ] FINAL-0111 — `recovery.py`: path exists.
- [ ] FINAL-0112 — `recovery.py`: types strict.
- [ ] FINAL-0113 — `recovery.py`: public exports.
- [ ] FINAL-0114 — `recovery.py`: unknown inputs rejected.
- [ ] FINAL-0115 — `recovery.py`: typed errors.
- [ ] FINAL-0116 — `recovery.py`: budget bound.
- [ ] FINAL-0117 — `recovery.py`: authority preserved.
- [ ] FINAL-0118 — `recovery.py`: artifacts referenced.
- [ ] FINAL-0119 — `recovery.py`: unit success.
- [ ] FINAL-0120 — `recovery.py`: unit failure.
- [ ] FINAL-0121 — `recovery.py`: adversarial test.
- [ ] FINAL-0122 — `recovery.py`: integration coverage.
- [ ] FINAL-0123 — `recovery.py`: offline deterministic.
- [ ] FINAL-0124 — `recovery.py`: timeout.
- [ ] FINAL-0125 — `recovery.py`: idempotency.
- [ ] FINAL-0126 — `recovery.py`: replay semantics.
- [ ] FINAL-0127 — `recovery.py`: telemetry.
- [ ] FINAL-0128 — `recovery.py`: secret safety.
- [ ] FINAL-0129 — `recovery.py`: backward compatibility.
- [ ] FINAL-0130 — `recovery.py`: feature flag.
- [ ] FINAL-0131 — `recovery.py`: rollback.
- [ ] FINAL-0132 — `recovery.py`: docs manifest reference.
- [ ] FINAL-0133 — `routing.py`: path exists.
- [ ] FINAL-0134 — `routing.py`: types strict.
- [ ] FINAL-0135 — `routing.py`: public exports.
- [ ] FINAL-0136 — `routing.py`: unknown inputs rejected.
- [ ] FINAL-0137 — `routing.py`: typed errors.
- [ ] FINAL-0138 — `routing.py`: budget bound.
- [ ] FINAL-0139 — `routing.py`: authority preserved.
- [ ] FINAL-0140 — `routing.py`: artifacts referenced.
- [ ] FINAL-0141 — `routing.py`: unit success.
- [ ] FINAL-0142 — `routing.py`: unit failure.
- [ ] FINAL-0143 — `routing.py`: adversarial test.
- [ ] FINAL-0144 — `routing.py`: integration coverage.
- [ ] FINAL-0145 — `routing.py`: offline deterministic.
- [ ] FINAL-0146 — `routing.py`: timeout.
- [ ] FINAL-0147 — `routing.py`: idempotency.
- [ ] FINAL-0148 — `routing.py`: replay semantics.
- [ ] FINAL-0149 — `routing.py`: telemetry.
- [ ] FINAL-0150 — `routing.py`: secret safety.
- [ ] FINAL-0151 — `routing.py`: backward compatibility.
- [ ] FINAL-0152 — `routing.py`: feature flag.
- [ ] FINAL-0153 — `routing.py`: rollback.
- [ ] FINAL-0154 — `routing.py`: docs manifest reference.
- [ ] FINAL-0155 — `workflow.py`: path exists.
- [ ] FINAL-0156 — `workflow.py`: types strict.
- [ ] FINAL-0157 — `workflow.py`: public exports.
- [ ] FINAL-0158 — `workflow.py`: unknown inputs rejected.
- [ ] FINAL-0159 — `workflow.py`: typed errors.
- [ ] FINAL-0160 — `workflow.py`: budget bound.
- [ ] FINAL-0161 — `workflow.py`: authority preserved.
- [ ] FINAL-0162 — `workflow.py`: artifacts referenced.
- [ ] FINAL-0163 — `workflow.py`: unit success.
- [ ] FINAL-0164 — `workflow.py`: unit failure.
- [ ] FINAL-0165 — `workflow.py`: adversarial test.
- [ ] FINAL-0166 — `workflow.py`: integration coverage.
- [ ] FINAL-0167 — `workflow.py`: offline deterministic.
- [ ] FINAL-0168 — `workflow.py`: timeout.
- [ ] FINAL-0169 — `workflow.py`: idempotency.
- [ ] FINAL-0170 — `workflow.py`: replay semantics.
- [ ] FINAL-0171 — `workflow.py`: telemetry.
- [ ] FINAL-0172 — `workflow.py`: secret safety.
- [ ] FINAL-0173 — `workflow.py`: backward compatibility.
- [ ] FINAL-0174 — `workflow.py`: feature flag.
- [ ] FINAL-0175 — `workflow.py`: rollback.
- [ ] FINAL-0176 — `workflow.py`: docs manifest reference.
- [ ] FINAL-0177 — `coordinator.py`: path exists.
- [ ] FINAL-0178 — `coordinator.py`: types strict.
- [ ] FINAL-0179 — `coordinator.py`: public exports.
- [ ] FINAL-0180 — `coordinator.py`: unknown inputs rejected.
- [ ] FINAL-0181 — `coordinator.py`: typed errors.
- [ ] FINAL-0182 — `coordinator.py`: budget bound.
- [ ] FINAL-0183 — `coordinator.py`: authority preserved.
- [ ] FINAL-0184 — `coordinator.py`: artifacts referenced.
- [ ] FINAL-0185 — `coordinator.py`: unit success.
- [ ] FINAL-0186 — `coordinator.py`: unit failure.
- [ ] FINAL-0187 — `coordinator.py`: adversarial test.
- [ ] FINAL-0188 — `coordinator.py`: integration coverage.
- [ ] FINAL-0189 — `coordinator.py`: offline deterministic.
- [ ] FINAL-0190 — `coordinator.py`: timeout.
- [ ] FINAL-0191 — `coordinator.py`: idempotency.
- [ ] FINAL-0192 — `coordinator.py`: replay semantics.
- [ ] FINAL-0193 — `coordinator.py`: telemetry.
- [ ] FINAL-0194 — `coordinator.py`: secret safety.
- [ ] FINAL-0195 — `coordinator.py`: backward compatibility.
- [ ] FINAL-0196 — `coordinator.py`: feature flag.
- [ ] FINAL-0197 — `coordinator.py`: rollback.
- [ ] FINAL-0198 — `coordinator.py`: docs manifest reference.
- [ ] FINAL-0199 — `state_bridge.py`: path exists.
- [ ] FINAL-0200 — `state_bridge.py`: types strict.
- [ ] FINAL-0201 — `state_bridge.py`: public exports.
- [ ] FINAL-0202 — `state_bridge.py`: unknown inputs rejected.
- [ ] FINAL-0203 — `state_bridge.py`: typed errors.
- [ ] FINAL-0204 — `state_bridge.py`: budget bound.
- [ ] FINAL-0205 — `state_bridge.py`: authority preserved.
- [ ] FINAL-0206 — `state_bridge.py`: artifacts referenced.
- [ ] FINAL-0207 — `state_bridge.py`: unit success.
- [ ] FINAL-0208 — `state_bridge.py`: unit failure.
- [ ] FINAL-0209 — `state_bridge.py`: adversarial test.
- [ ] FINAL-0210 — `state_bridge.py`: integration coverage.
- [ ] FINAL-0211 — `state_bridge.py`: offline deterministic.
- [ ] FINAL-0212 — `state_bridge.py`: timeout.
- [ ] FINAL-0213 — `state_bridge.py`: idempotency.
- [ ] FINAL-0214 — `state_bridge.py`: replay semantics.
- [ ] FINAL-0215 — `state_bridge.py`: telemetry.
- [ ] FINAL-0216 — `state_bridge.py`: secret safety.
- [ ] FINAL-0217 — `state_bridge.py`: backward compatibility.
- [ ] FINAL-0218 — `state_bridge.py`: feature flag.
- [ ] FINAL-0219 — `state_bridge.py`: rollback.
- [ ] FINAL-0220 — `state_bridge.py`: docs manifest reference.
- [ ] FINAL-0221 — `workspace_tx.py`: path exists.
- [ ] FINAL-0222 — `workspace_tx.py`: types strict.
- [ ] FINAL-0223 — `workspace_tx.py`: public exports.
- [ ] FINAL-0224 — `workspace_tx.py`: unknown inputs rejected.
- [ ] FINAL-0225 — `workspace_tx.py`: typed errors.
- [ ] FINAL-0226 — `workspace_tx.py`: budget bound.
- [ ] FINAL-0227 — `workspace_tx.py`: authority preserved.
- [ ] FINAL-0228 — `workspace_tx.py`: artifacts referenced.
- [ ] FINAL-0229 — `workspace_tx.py`: unit success.
- [ ] FINAL-0230 — `workspace_tx.py`: unit failure.
- [ ] FINAL-0231 — `workspace_tx.py`: adversarial test.
- [ ] FINAL-0232 — `workspace_tx.py`: integration coverage.
- [ ] FINAL-0233 — `workspace_tx.py`: offline deterministic.
- [ ] FINAL-0234 — `workspace_tx.py`: timeout.
- [ ] FINAL-0235 — `workspace_tx.py`: idempotency.
- [ ] FINAL-0236 — `workspace_tx.py`: replay semantics.
- [ ] FINAL-0237 — `workspace_tx.py`: telemetry.
- [ ] FINAL-0238 — `workspace_tx.py`: secret safety.
- [ ] FINAL-0239 — `workspace_tx.py`: backward compatibility.
- [ ] FINAL-0240 — `workspace_tx.py`: feature flag.
- [ ] FINAL-0241 — `workspace_tx.py`: rollback.
- [ ] FINAL-0242 — `workspace_tx.py`: docs manifest reference.
- [ ] FINAL-0243 — `tool_results.py`: path exists.
- [ ] FINAL-0244 — `tool_results.py`: types strict.
- [ ] FINAL-0245 — `tool_results.py`: public exports.
- [ ] FINAL-0246 — `tool_results.py`: unknown inputs rejected.
- [ ] FINAL-0247 — `tool_results.py`: typed errors.
- [ ] FINAL-0248 — `tool_results.py`: budget bound.
- [ ] FINAL-0249 — `tool_results.py`: authority preserved.
- [ ] FINAL-0250 — `tool_results.py`: artifacts referenced.
- [ ] FINAL-0251 — `tool_results.py`: unit success.
- [ ] FINAL-0252 — `tool_results.py`: unit failure.
- [ ] FINAL-0253 — `tool_results.py`: adversarial test.
- [ ] FINAL-0254 — `tool_results.py`: integration coverage.
- [ ] FINAL-0255 — `tool_results.py`: offline deterministic.
- [ ] FINAL-0256 — `tool_results.py`: timeout.
- [ ] FINAL-0257 — `tool_results.py`: idempotency.
- [ ] FINAL-0258 — `tool_results.py`: replay semantics.
- [ ] FINAL-0259 — `tool_results.py`: telemetry.
- [ ] FINAL-0260 — `tool_results.py`: secret safety.
- [ ] FINAL-0261 — `tool_results.py`: backward compatibility.
- [ ] FINAL-0262 — `tool_results.py`: feature flag.
- [ ] FINAL-0263 — `tool_results.py`: rollback.
- [ ] FINAL-0264 — `tool_results.py`: docs manifest reference.
- [ ] FINAL-0265 — `test_selector.py`: path exists.
- [ ] FINAL-0266 — `test_selector.py`: types strict.
- [ ] FINAL-0267 — `test_selector.py`: public exports.
- [ ] FINAL-0268 — `test_selector.py`: unknown inputs rejected.
- [ ] FINAL-0269 — `test_selector.py`: typed errors.
- [ ] FINAL-0270 — `test_selector.py`: budget bound.
- [ ] FINAL-0271 — `test_selector.py`: authority preserved.
- [ ] FINAL-0272 — `test_selector.py`: artifacts referenced.
- [ ] FINAL-0273 — `test_selector.py`: unit success.
- [ ] FINAL-0274 — `test_selector.py`: unit failure.
- [ ] FINAL-0275 — `test_selector.py`: adversarial test.
- [ ] FINAL-0276 — `test_selector.py`: integration coverage.
- [ ] FINAL-0277 — `test_selector.py`: offline deterministic.
- [ ] FINAL-0278 — `test_selector.py`: timeout.
- [ ] FINAL-0279 — `test_selector.py`: idempotency.
- [ ] FINAL-0280 — `test_selector.py`: replay semantics.
- [ ] FINAL-0281 — `test_selector.py`: telemetry.
- [ ] FINAL-0282 — `test_selector.py`: secret safety.
- [ ] FINAL-0283 — `test_selector.py`: backward compatibility.
- [ ] FINAL-0284 — `test_selector.py`: feature flag.
- [ ] FINAL-0285 — `test_selector.py`: rollback.
- [ ] FINAL-0286 — `test_selector.py`: docs manifest reference.
- [ ] FINAL-0287 — `verification_pipeline.py`: path exists.
- [ ] FINAL-0288 — `verification_pipeline.py`: types strict.
- [ ] FINAL-0289 — `verification_pipeline.py`: public exports.
- [ ] FINAL-0290 — `verification_pipeline.py`: unknown inputs rejected.
- [ ] FINAL-0291 — `verification_pipeline.py`: typed errors.
- [ ] FINAL-0292 — `verification_pipeline.py`: budget bound.
- [ ] FINAL-0293 — `verification_pipeline.py`: authority preserved.
- [ ] FINAL-0294 — `verification_pipeline.py`: artifacts referenced.
- [ ] FINAL-0295 — `verification_pipeline.py`: unit success.
- [ ] FINAL-0296 — `verification_pipeline.py`: unit failure.
- [ ] FINAL-0297 — `verification_pipeline.py`: adversarial test.
- [ ] FINAL-0298 — `verification_pipeline.py`: integration coverage.
- [ ] FINAL-0299 — `verification_pipeline.py`: offline deterministic.
- [ ] FINAL-0300 — `verification_pipeline.py`: timeout.
- [ ] FINAL-0301 — `verification_pipeline.py`: idempotency.
- [ ] FINAL-0302 — `verification_pipeline.py`: replay semantics.
- [ ] FINAL-0303 — `verification_pipeline.py`: telemetry.
- [ ] FINAL-0304 — `verification_pipeline.py`: secret safety.
- [ ] FINAL-0305 — `verification_pipeline.py`: backward compatibility.
- [ ] FINAL-0306 — `verification_pipeline.py`: feature flag.
- [ ] FINAL-0307 — `verification_pipeline.py`: rollback.
- [ ] FINAL-0308 — `verification_pipeline.py`: docs manifest reference.
- [ ] FINAL-0309 — `durable_state.py`: path exists.
- [ ] FINAL-0310 — `durable_state.py`: types strict.
- [ ] FINAL-0311 — `durable_state.py`: public exports.
- [ ] FINAL-0312 — `durable_state.py`: unknown inputs rejected.
- [ ] FINAL-0313 — `durable_state.py`: typed errors.
- [ ] FINAL-0314 — `durable_state.py`: budget bound.
- [ ] FINAL-0315 — `durable_state.py`: authority preserved.
- [ ] FINAL-0316 — `durable_state.py`: artifacts referenced.
- [ ] FINAL-0317 — `durable_state.py`: unit success.
- [ ] FINAL-0318 — `durable_state.py`: unit failure.
- [ ] FINAL-0319 — `durable_state.py`: adversarial test.
- [ ] FINAL-0320 — `durable_state.py`: integration coverage.
- [ ] FINAL-0321 — `durable_state.py`: offline deterministic.
- [ ] FINAL-0322 — `durable_state.py`: timeout.
- [ ] FINAL-0323 — `durable_state.py`: idempotency.
- [ ] FINAL-0324 — `durable_state.py`: replay semantics.
- [ ] FINAL-0325 — `durable_state.py`: telemetry.
- [ ] FINAL-0326 — `durable_state.py`: secret safety.
- [ ] FINAL-0327 — `durable_state.py`: backward compatibility.
- [ ] FINAL-0328 — `durable_state.py`: feature flag.
- [ ] FINAL-0329 — `durable_state.py`: rollback.
- [ ] FINAL-0330 — `durable_state.py`: docs manifest reference.
- [ ] FINAL-0331 — `durable_store.py`: path exists.
- [ ] FINAL-0332 — `durable_store.py`: types strict.
- [ ] FINAL-0333 — `durable_store.py`: public exports.
- [ ] FINAL-0334 — `durable_store.py`: unknown inputs rejected.
- [ ] FINAL-0335 — `durable_store.py`: typed errors.
- [ ] FINAL-0336 — `durable_store.py`: budget bound.
- [ ] FINAL-0337 — `durable_store.py`: authority preserved.
- [ ] FINAL-0338 — `durable_store.py`: artifacts referenced.
- [ ] FINAL-0339 — `durable_store.py`: unit success.
- [ ] FINAL-0340 — `durable_store.py`: unit failure.
- [ ] FINAL-0341 — `durable_store.py`: adversarial test.
- [ ] FINAL-0342 — `durable_store.py`: integration coverage.
- [ ] FINAL-0343 — `durable_store.py`: offline deterministic.
- [ ] FINAL-0344 — `durable_store.py`: timeout.
- [ ] FINAL-0345 — `durable_store.py`: idempotency.
- [ ] FINAL-0346 — `durable_store.py`: replay semantics.
- [ ] FINAL-0347 — `durable_store.py`: telemetry.
- [ ] FINAL-0348 — `durable_store.py`: secret safety.
- [ ] FINAL-0349 — `durable_store.py`: backward compatibility.
- [ ] FINAL-0350 — `durable_store.py`: feature flag.
- [ ] FINAL-0351 — `durable_store.py`: rollback.
- [ ] FINAL-0352 — `durable_store.py`: docs manifest reference.
- [ ] FINAL-0353 — `resume.py`: path exists.
- [ ] FINAL-0354 — `resume.py`: types strict.
- [ ] FINAL-0355 — `resume.py`: public exports.
- [ ] FINAL-0356 — `resume.py`: unknown inputs rejected.
- [ ] FINAL-0357 — `resume.py`: typed errors.
- [ ] FINAL-0358 — `resume.py`: budget bound.
- [ ] FINAL-0359 — `resume.py`: authority preserved.
- [ ] FINAL-0360 — `resume.py`: artifacts referenced.
- [ ] FINAL-0361 — `resume.py`: unit success.
- [ ] FINAL-0362 — `resume.py`: unit failure.
- [ ] FINAL-0363 — `resume.py`: adversarial test.
- [ ] FINAL-0364 — `resume.py`: integration coverage.
- [ ] FINAL-0365 — `resume.py`: offline deterministic.
- [ ] FINAL-0366 — `resume.py`: timeout.
- [ ] FINAL-0367 — `resume.py`: idempotency.
- [ ] FINAL-0368 — `resume.py`: replay semantics.
- [ ] FINAL-0369 — `resume.py`: telemetry.
- [ ] FINAL-0370 — `resume.py`: secret safety.
- [ ] FINAL-0371 — `resume.py`: backward compatibility.
- [ ] FINAL-0372 — `resume.py`: feature flag.
- [ ] FINAL-0373 — `resume.py`: rollback.
- [ ] FINAL-0374 — `resume.py`: docs manifest reference.
- [ ] FINAL-0375 — `reflex.py`: path exists.
- [ ] FINAL-0376 — `reflex.py`: types strict.
- [ ] FINAL-0377 — `reflex.py`: public exports.
- [ ] FINAL-0378 — `reflex.py`: unknown inputs rejected.
- [ ] FINAL-0379 — `reflex.py`: typed errors.
- [ ] FINAL-0380 — `reflex.py`: budget bound.
- [ ] FINAL-0381 — `reflex.py`: authority preserved.
- [ ] FINAL-0382 — `reflex.py`: artifacts referenced.
- [ ] FINAL-0383 — `reflex.py`: unit success.
- [ ] FINAL-0384 — `reflex.py`: unit failure.
- [ ] FINAL-0385 — `reflex.py`: adversarial test.
- [ ] FINAL-0386 — `reflex.py`: integration coverage.
- [ ] FINAL-0387 — `reflex.py`: offline deterministic.
- [ ] FINAL-0388 — `reflex.py`: timeout.
- [ ] FINAL-0389 — `reflex.py`: idempotency.
- [ ] FINAL-0390 — `reflex.py`: replay semantics.
- [ ] FINAL-0391 — `reflex.py`: telemetry.
- [ ] FINAL-0392 — `reflex.py`: secret safety.
- [ ] FINAL-0393 — `reflex.py`: backward compatibility.
- [ ] FINAL-0394 — `reflex.py`: feature flag.
- [ ] FINAL-0395 — `reflex.py`: rollback.
- [ ] FINAL-0396 — `reflex.py`: docs manifest reference.
- [ ] FINAL-0397 — `branch_search.py`: path exists.
- [ ] FINAL-0398 — `branch_search.py`: types strict.
- [ ] FINAL-0399 — `branch_search.py`: public exports.
- [ ] FINAL-0400 — `branch_search.py`: unknown inputs rejected.
- [ ] FINAL-0401 — `branch_search.py`: typed errors.
- [ ] FINAL-0402 — `branch_search.py`: budget bound.
- [ ] FINAL-0403 — `branch_search.py`: authority preserved.
- [ ] FINAL-0404 — `branch_search.py`: artifacts referenced.
- [ ] FINAL-0405 — `branch_search.py`: unit success.
- [ ] FINAL-0406 — `branch_search.py`: unit failure.
- [ ] FINAL-0407 — `branch_search.py`: adversarial test.
- [ ] FINAL-0408 — `branch_search.py`: integration coverage.
- [ ] FINAL-0409 — `branch_search.py`: offline deterministic.
- [ ] FINAL-0410 — `branch_search.py`: timeout.
- [ ] FINAL-0411 — `branch_search.py`: idempotency.
- [ ] FINAL-0412 — `branch_search.py`: replay semantics.
- [ ] FINAL-0413 — `branch_search.py`: telemetry.
- [ ] FINAL-0414 — `branch_search.py`: secret safety.
- [ ] FINAL-0415 — `branch_search.py`: backward compatibility.
- [ ] FINAL-0416 — `branch_search.py`: feature flag.
- [ ] FINAL-0417 — `branch_search.py`: rollback.
- [ ] FINAL-0418 — `branch_search.py`: docs manifest reference.
- [ ] FINAL-0419 — `mutation.py`: path exists.
- [ ] FINAL-0420 — `mutation.py`: types strict.
- [ ] FINAL-0421 — `mutation.py`: public exports.
- [ ] FINAL-0422 — `mutation.py`: unknown inputs rejected.
- [ ] FINAL-0423 — `mutation.py`: typed errors.
- [ ] FINAL-0424 — `mutation.py`: budget bound.
- [ ] FINAL-0425 — `mutation.py`: authority preserved.
- [ ] FINAL-0426 — `mutation.py`: artifacts referenced.
- [ ] FINAL-0427 — `mutation.py`: unit success.
- [ ] FINAL-0428 — `mutation.py`: unit failure.
- [ ] FINAL-0429 — `mutation.py`: adversarial test.
- [ ] FINAL-0430 — `mutation.py`: integration coverage.
- [ ] FINAL-0431 — `mutation.py`: offline deterministic.
- [ ] FINAL-0432 — `mutation.py`: timeout.
- [ ] FINAL-0433 — `mutation.py`: idempotency.
- [ ] FINAL-0434 — `mutation.py`: replay semantics.
- [ ] FINAL-0435 — `mutation.py`: telemetry.
- [ ] FINAL-0436 — `mutation.py`: secret safety.
- [ ] FINAL-0437 — `mutation.py`: backward compatibility.
- [ ] FINAL-0438 — `mutation.py`: feature flag.
- [ ] FINAL-0439 — `mutation.py`: rollback.
- [ ] FINAL-0440 — `mutation.py`: docs manifest reference.
- [ ] FINAL-0441 — `capsules.py`: path exists.
- [ ] FINAL-0442 — `capsules.py`: types strict.
- [ ] FINAL-0443 — `capsules.py`: public exports.
- [ ] FINAL-0444 — `capsules.py`: unknown inputs rejected.
- [ ] FINAL-0445 — `capsules.py`: typed errors.
- [ ] FINAL-0446 — `capsules.py`: budget bound.
- [ ] FINAL-0447 — `capsules.py`: authority preserved.
- [ ] FINAL-0448 — `capsules.py`: artifacts referenced.
- [ ] FINAL-0449 — `capsules.py`: unit success.
- [ ] FINAL-0450 — `capsules.py`: unit failure.
- [ ] FINAL-0451 — `capsules.py`: adversarial test.
- [ ] FINAL-0452 — `capsules.py`: integration coverage.
- [ ] FINAL-0453 — `capsules.py`: offline deterministic.
- [ ] FINAL-0454 — `capsules.py`: timeout.
- [ ] FINAL-0455 — `capsules.py`: idempotency.
- [ ] FINAL-0456 — `capsules.py`: replay semantics.
- [ ] FINAL-0457 — `capsules.py`: telemetry.
- [ ] FINAL-0458 — `capsules.py`: secret safety.
- [ ] FINAL-0459 — `capsules.py`: backward compatibility.
- [ ] FINAL-0460 — `capsules.py`: feature flag.
- [ ] FINAL-0461 — `capsules.py`: rollback.
- [ ] FINAL-0462 — `capsules.py`: docs manifest reference.
- [ ] FINAL-0463 — `toolscript.py`: path exists.
- [ ] FINAL-0464 — `toolscript.py`: types strict.
- [ ] FINAL-0465 — `toolscript.py`: public exports.
- [ ] FINAL-0466 — `toolscript.py`: unknown inputs rejected.
- [ ] FINAL-0467 — `toolscript.py`: typed errors.
- [ ] FINAL-0468 — `toolscript.py`: budget bound.
- [ ] FINAL-0469 — `toolscript.py`: authority preserved.
- [ ] FINAL-0470 — `toolscript.py`: artifacts referenced.
- [ ] FINAL-0471 — `toolscript.py`: unit success.
- [ ] FINAL-0472 — `toolscript.py`: unit failure.
- [ ] FINAL-0473 — `toolscript.py`: adversarial test.
- [ ] FINAL-0474 — `toolscript.py`: integration coverage.
- [ ] FINAL-0475 — `toolscript.py`: offline deterministic.
- [ ] FINAL-0476 — `toolscript.py`: timeout.
- [ ] FINAL-0477 — `toolscript.py`: idempotency.
- [ ] FINAL-0478 — `toolscript.py`: replay semantics.
- [ ] FINAL-0479 — `toolscript.py`: telemetry.
- [ ] FINAL-0480 — `toolscript.py`: secret safety.
- [ ] FINAL-0481 — `toolscript.py`: backward compatibility.
- [ ] FINAL-0482 — `toolscript.py`: feature flag.
- [ ] FINAL-0483 — `toolscript.py`: rollback.
- [ ] FINAL-0484 — `toolscript.py`: docs manifest reference.
- [ ] FINAL-0485 — `toolscript_broker.py`: path exists.
- [ ] FINAL-0486 — `toolscript_broker.py`: types strict.
- [ ] FINAL-0487 — `toolscript_broker.py`: public exports.
- [ ] FINAL-0488 — `toolscript_broker.py`: unknown inputs rejected.
- [ ] FINAL-0489 — `toolscript_broker.py`: typed errors.
- [ ] FINAL-0490 — `toolscript_broker.py`: budget bound.
- [ ] FINAL-0491 — `toolscript_broker.py`: authority preserved.
- [ ] FINAL-0492 — `toolscript_broker.py`: artifacts referenced.
- [ ] FINAL-0493 — `toolscript_broker.py`: unit success.
- [ ] FINAL-0494 — `toolscript_broker.py`: unit failure.
- [ ] FINAL-0495 — `toolscript_broker.py`: adversarial test.
- [ ] FINAL-0496 — `toolscript_broker.py`: integration coverage.
- [ ] FINAL-0497 — `toolscript_broker.py`: offline deterministic.
- [ ] FINAL-0498 — `toolscript_broker.py`: timeout.
- [ ] FINAL-0499 — `toolscript_broker.py`: idempotency.
- [ ] FINAL-0500 — `toolscript_broker.py`: replay semantics.
- [ ] FINAL-0501 — `toolscript_broker.py`: telemetry.
- [ ] FINAL-0502 — `toolscript_broker.py`: secret safety.
- [ ] FINAL-0503 — `toolscript_broker.py`: backward compatibility.
- [ ] FINAL-0504 — `toolscript_broker.py`: feature flag.
- [ ] FINAL-0505 — `toolscript_broker.py`: rollback.
- [ ] FINAL-0506 — `toolscript_broker.py`: docs manifest reference.
- [ ] FINAL-0507 — `specialists.py`: path exists.
- [ ] FINAL-0508 — `specialists.py`: types strict.
- [ ] FINAL-0509 — `specialists.py`: public exports.
- [ ] FINAL-0510 — `specialists.py`: unknown inputs rejected.
- [ ] FINAL-0511 — `specialists.py`: typed errors.
- [ ] FINAL-0512 — `specialists.py`: budget bound.
- [ ] FINAL-0513 — `specialists.py`: authority preserved.
- [ ] FINAL-0514 — `specialists.py`: artifacts referenced.
- [ ] FINAL-0515 — `specialists.py`: unit success.
- [ ] FINAL-0516 — `specialists.py`: unit failure.
- [ ] FINAL-0517 — `specialists.py`: adversarial test.
- [ ] FINAL-0518 — `specialists.py`: integration coverage.
- [ ] FINAL-0519 — `specialists.py`: offline deterministic.
- [ ] FINAL-0520 — `specialists.py`: timeout.
- [ ] FINAL-0521 — `specialists.py`: idempotency.
- [ ] FINAL-0522 — `specialists.py`: replay semantics.
- [ ] FINAL-0523 — `specialists.py`: telemetry.
- [ ] FINAL-0524 — `specialists.py`: secret safety.
- [ ] FINAL-0525 — `specialists.py`: backward compatibility.
- [ ] FINAL-0526 — `specialists.py`: feature flag.
- [ ] FINAL-0527 — `specialists.py`: rollback.
- [ ] FINAL-0528 — `specialists.py`: docs manifest reference.
- [ ] FINAL-0529 — `reviewer.py`: path exists.
- [ ] FINAL-0530 — `reviewer.py`: types strict.
- [ ] FINAL-0531 — `reviewer.py`: public exports.
- [ ] FINAL-0532 — `reviewer.py`: unknown inputs rejected.
- [ ] FINAL-0533 — `reviewer.py`: typed errors.
- [ ] FINAL-0534 — `reviewer.py`: budget bound.
- [ ] FINAL-0535 — `reviewer.py`: authority preserved.
- [ ] FINAL-0536 — `reviewer.py`: artifacts referenced.
- [ ] FINAL-0537 — `reviewer.py`: unit success.
- [ ] FINAL-0538 — `reviewer.py`: unit failure.
- [ ] FINAL-0539 — `reviewer.py`: adversarial test.
- [ ] FINAL-0540 — `reviewer.py`: integration coverage.
- [ ] FINAL-0541 — `reviewer.py`: offline deterministic.
- [ ] FINAL-0542 — `reviewer.py`: timeout.
- [ ] FINAL-0543 — `reviewer.py`: idempotency.
- [ ] FINAL-0544 — `reviewer.py`: replay semantics.
- [ ] FINAL-0545 — `reviewer.py`: telemetry.
- [ ] FINAL-0546 — `reviewer.py`: secret safety.
- [ ] FINAL-0547 — `reviewer.py`: backward compatibility.
- [ ] FINAL-0548 — `reviewer.py`: feature flag.
- [ ] FINAL-0549 — `reviewer.py`: rollback.
- [ ] FINAL-0550 — `reviewer.py`: docs manifest reference.
- [ ] FINAL-0551 — `distill.py`: path exists.
- [ ] FINAL-0552 — `distill.py`: types strict.
- [ ] FINAL-0553 — `distill.py`: public exports.
- [ ] FINAL-0554 — `distill.py`: unknown inputs rejected.
- [ ] FINAL-0555 — `distill.py`: typed errors.
- [ ] FINAL-0556 — `distill.py`: budget bound.
- [ ] FINAL-0557 — `distill.py`: authority preserved.
- [ ] FINAL-0558 — `distill.py`: artifacts referenced.
- [ ] FINAL-0559 — `distill.py`: unit success.
- [ ] FINAL-0560 — `distill.py`: unit failure.
- [ ] FINAL-0561 — `distill.py`: adversarial test.
- [ ] FINAL-0562 — `distill.py`: integration coverage.
- [ ] FINAL-0563 — `distill.py`: offline deterministic.
- [ ] FINAL-0564 — `distill.py`: timeout.
- [ ] FINAL-0565 — `distill.py`: idempotency.
- [ ] FINAL-0566 — `distill.py`: replay semantics.
- [ ] FINAL-0567 — `distill.py`: telemetry.
- [ ] FINAL-0568 — `distill.py`: secret safety.
- [ ] FINAL-0569 — `distill.py`: backward compatibility.
- [ ] FINAL-0570 — `distill.py`: feature flag.
- [ ] FINAL-0571 — `distill.py`: rollback.
- [ ] FINAL-0572 — `distill.py`: docs manifest reference.
- [ ] FINAL-0573 — `lda_adapter.py`: path exists.
- [ ] FINAL-0574 — `lda_adapter.py`: types strict.
- [ ] FINAL-0575 — `lda_adapter.py`: public exports.
- [ ] FINAL-0576 — `lda_adapter.py`: unknown inputs rejected.
- [ ] FINAL-0577 — `lda_adapter.py`: typed errors.
- [ ] FINAL-0578 — `lda_adapter.py`: budget bound.
- [ ] FINAL-0579 — `lda_adapter.py`: authority preserved.
- [ ] FINAL-0580 — `lda_adapter.py`: artifacts referenced.
- [ ] FINAL-0581 — `lda_adapter.py`: unit success.
- [ ] FINAL-0582 — `lda_adapter.py`: unit failure.
- [ ] FINAL-0583 — `lda_adapter.py`: adversarial test.
- [ ] FINAL-0584 — `lda_adapter.py`: integration coverage.
- [ ] FINAL-0585 — `lda_adapter.py`: offline deterministic.
- [ ] FINAL-0586 — `lda_adapter.py`: timeout.
- [ ] FINAL-0587 — `lda_adapter.py`: idempotency.
- [ ] FINAL-0588 — `lda_adapter.py`: replay semantics.
- [ ] FINAL-0589 — `lda_adapter.py`: telemetry.
- [ ] FINAL-0590 — `lda_adapter.py`: secret safety.
- [ ] FINAL-0591 — `lda_adapter.py`: backward compatibility.
- [ ] FINAL-0592 — `lda_adapter.py`: feature flag.
- [ ] FINAL-0593 — `lda_adapter.py`: rollback.
- [ ] FINAL-0594 — `lda_adapter.py`: docs manifest reference.
- [ ] FINAL-0595 — `intelligence_router.py`: path exists.
- [ ] FINAL-0596 — `intelligence_router.py`: types strict.
- [ ] FINAL-0597 — `intelligence_router.py`: public exports.
- [ ] FINAL-0598 — `intelligence_router.py`: unknown inputs rejected.
- [ ] FINAL-0599 — `intelligence_router.py`: typed errors.
- [ ] FINAL-0600 — `intelligence_router.py`: budget bound.
- [ ] FINAL-0601 — `intelligence_router.py`: authority preserved.
- [ ] FINAL-0602 — `intelligence_router.py`: artifacts referenced.
- [ ] FINAL-0603 — `intelligence_router.py`: unit success.
- [ ] FINAL-0604 — `intelligence_router.py`: unit failure.
- [ ] FINAL-0605 — `intelligence_router.py`: adversarial test.
- [ ] FINAL-0606 — `intelligence_router.py`: integration coverage.
- [ ] FINAL-0607 — `intelligence_router.py`: offline deterministic.
- [ ] FINAL-0608 — `intelligence_router.py`: timeout.
- [ ] FINAL-0609 — `intelligence_router.py`: idempotency.
- [ ] FINAL-0610 — `intelligence_router.py`: replay semantics.
- [ ] FINAL-0611 — `intelligence_router.py`: telemetry.
- [ ] FINAL-0612 — `intelligence_router.py`: secret safety.
- [ ] FINAL-0613 — `intelligence_router.py`: backward compatibility.
- [ ] FINAL-0614 — `intelligence_router.py`: feature flag.
- [ ] FINAL-0615 — `intelligence_router.py`: rollback.
- [ ] FINAL-0616 — `intelligence_router.py`: docs manifest reference.
- [ ] FINAL-0617 — `factory.py`: path exists.
- [ ] FINAL-0618 — `factory.py`: types strict.
- [ ] FINAL-0619 — `factory.py`: public exports.
- [ ] FINAL-0620 — `factory.py`: unknown inputs rejected.
- [ ] FINAL-0621 — `factory.py`: typed errors.
- [ ] FINAL-0622 — `factory.py`: budget bound.
- [ ] FINAL-0623 — `factory.py`: authority preserved.
- [ ] FINAL-0624 — `factory.py`: artifacts referenced.
- [ ] FINAL-0625 — `factory.py`: unit success.
- [ ] FINAL-0626 — `factory.py`: unit failure.
- [ ] FINAL-0627 — `factory.py`: adversarial test.
- [ ] FINAL-0628 — `factory.py`: integration coverage.
- [ ] FINAL-0629 — `factory.py`: offline deterministic.
- [ ] FINAL-0630 — `factory.py`: timeout.
- [ ] FINAL-0631 — `factory.py`: idempotency.
- [ ] FINAL-0632 — `factory.py`: replay semantics.
- [ ] FINAL-0633 — `factory.py`: telemetry.
- [ ] FINAL-0634 — `factory.py`: secret safety.
- [ ] FINAL-0635 — `factory.py`: backward compatibility.
- [ ] FINAL-0636 — `factory.py`: feature flag.
- [ ] FINAL-0637 — `factory.py`: rollback.
- [ ] FINAL-0638 — `factory.py`: docs manifest reference.
- [ ] FINAL-0639 — `features.py`: path exists.
- [ ] FINAL-0640 — `features.py`: types strict.
- [ ] FINAL-0641 — `features.py`: public exports.
- [ ] FINAL-0642 — `features.py`: unknown inputs rejected.
- [ ] FINAL-0643 — `features.py`: typed errors.
- [ ] FINAL-0644 — `features.py`: budget bound.
- [ ] FINAL-0645 — `features.py`: authority preserved.
- [ ] FINAL-0646 — `features.py`: artifacts referenced.
- [ ] FINAL-0647 — `features.py`: unit success.
- [ ] FINAL-0648 — `features.py`: unit failure.
- [ ] FINAL-0649 — `features.py`: adversarial test.
- [ ] FINAL-0650 — `features.py`: integration coverage.
- [ ] FINAL-0651 — `features.py`: offline deterministic.
- [ ] FINAL-0652 — `features.py`: timeout.
- [ ] FINAL-0653 — `features.py`: idempotency.
- [ ] FINAL-0654 — `features.py`: replay semantics.
- [ ] FINAL-0655 — `features.py`: telemetry.
- [ ] FINAL-0656 — `features.py`: secret safety.
- [ ] FINAL-0657 — `features.py`: backward compatibility.
- [ ] FINAL-0658 — `features.py`: feature flag.
- [ ] FINAL-0659 — `features.py`: rollback.
- [ ] FINAL-0660 — `features.py`: docs manifest reference.
- [ ] FINAL-0661 — `benchmarks/coding_max/runner.py`: path exists.
- [ ] FINAL-0662 — `benchmarks/coding_max/runner.py`: types strict.
- [ ] FINAL-0663 — `benchmarks/coding_max/runner.py`: public exports.
- [ ] FINAL-0664 — `benchmarks/coding_max/runner.py`: unknown inputs rejected.
- [ ] FINAL-0665 — `benchmarks/coding_max/runner.py`: typed errors.
- [ ] FINAL-0666 — `benchmarks/coding_max/runner.py`: budget bound.
- [ ] FINAL-0667 — `benchmarks/coding_max/runner.py`: authority preserved.
- [ ] FINAL-0668 — `benchmarks/coding_max/runner.py`: artifacts referenced.
- [ ] FINAL-0669 — `benchmarks/coding_max/runner.py`: unit success.
- [ ] FINAL-0670 — `benchmarks/coding_max/runner.py`: unit failure.
- [ ] FINAL-0671 — `benchmarks/coding_max/runner.py`: adversarial test.
- [ ] FINAL-0672 — `benchmarks/coding_max/runner.py`: integration coverage.
- [ ] FINAL-0673 — `benchmarks/coding_max/runner.py`: offline deterministic.
- [ ] FINAL-0674 — `benchmarks/coding_max/runner.py`: timeout.
- [ ] FINAL-0675 — `benchmarks/coding_max/runner.py`: idempotency.
- [ ] FINAL-0676 — `benchmarks/coding_max/runner.py`: replay semantics.
- [ ] FINAL-0677 — `benchmarks/coding_max/runner.py`: telemetry.
- [ ] FINAL-0678 — `benchmarks/coding_max/runner.py`: secret safety.
- [ ] FINAL-0679 — `benchmarks/coding_max/runner.py`: backward compatibility.
- [ ] FINAL-0680 — `benchmarks/coding_max/runner.py`: feature flag.
- [ ] FINAL-0681 — `benchmarks/coding_max/runner.py`: rollback.
- [ ] FINAL-0682 — `benchmarks/coding_max/runner.py`: docs manifest reference.
- [ ] FINAL-0683 — `benchmarks/coding_max/preflight.py`: path exists.
- [ ] FINAL-0684 — `benchmarks/coding_max/preflight.py`: types strict.
- [ ] FINAL-0685 — `benchmarks/coding_max/preflight.py`: public exports.
- [ ] FINAL-0686 — `benchmarks/coding_max/preflight.py`: unknown inputs rejected.
- [ ] FINAL-0687 — `benchmarks/coding_max/preflight.py`: typed errors.
- [ ] FINAL-0688 — `benchmarks/coding_max/preflight.py`: budget bound.
- [ ] FINAL-0689 — `benchmarks/coding_max/preflight.py`: authority preserved.
- [ ] FINAL-0690 — `benchmarks/coding_max/preflight.py`: artifacts referenced.
- [ ] FINAL-0691 — `benchmarks/coding_max/preflight.py`: unit success.
- [ ] FINAL-0692 — `benchmarks/coding_max/preflight.py`: unit failure.
- [ ] FINAL-0693 — `benchmarks/coding_max/preflight.py`: adversarial test.
- [ ] FINAL-0694 — `benchmarks/coding_max/preflight.py`: integration coverage.
- [ ] FINAL-0695 — `benchmarks/coding_max/preflight.py`: offline deterministic.
- [ ] FINAL-0696 — `benchmarks/coding_max/preflight.py`: timeout.
- [ ] FINAL-0697 — `benchmarks/coding_max/preflight.py`: idempotency.
- [ ] FINAL-0698 — `benchmarks/coding_max/preflight.py`: replay semantics.
- [ ] FINAL-0699 — `benchmarks/coding_max/preflight.py`: telemetry.
- [ ] FINAL-0700 — `benchmarks/coding_max/preflight.py`: secret safety.
- [ ] FINAL-0701 — `benchmarks/coding_max/preflight.py`: backward compatibility.
- [ ] FINAL-0702 — `benchmarks/coding_max/preflight.py`: feature flag.
- [ ] FINAL-0703 — `benchmarks/coding_max/preflight.py`: rollback.
- [ ] FINAL-0704 — `benchmarks/coding_max/preflight.py`: docs manifest reference.

## 19. Definition of Done final

O harness está implementado quando o caminho causal completo funciona em repositório real, sobre Vanguard, com patch transacional, verificação externa, recuperação, resume fresh-process, artifacts/trajectory e budgets corretos. Está qualificado quando canary e release gates passam. É SOTA apenas quando benchmark oficial/reprodutível e ablations sustentam a afirmação.

