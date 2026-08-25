---
status: living
id: contract-manifests
class: contract-reference
authority: descriptive
canonical_for:
  - manifest-schema-contract
source_of_truth:
  - docs/02_decisions/0077-named-component-graph-manifest.md
  - docs/02_decisions/0088-m3c-m8-concept-lock.md
derived_from:
  - docs/02_decisions/0077-named-component-graph-manifest.md
applies_to:
  - v0.6.2
implementation_status: CONTRACT_LOCKED_M3C_IMPLEMENTATION_PENDING
owner: principal-systems-architect
version: "0.6.2"
last_verified: 2026-08-23
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# Named Component Graph Manifest (`mhf.manifest/2`)

> **Schema:** [`schemas/mhf/manifest_v2.schema.json`](../../schemas/mhf/manifest_v2.schema.json).
> **Status:** `/2` parser/compiler contracts exist; canonical public activation is M-3C work.

---

## Ratified structure

ADR-0077 requires typed named components, typed directed bindings, entrypoints, explicit profiles,
and capability-selector-based spawn authorization. All behavior-affecting values enter `D_H`.
Unknown kinds, dangling edges, incompatible bindings, and unconsumed authority fail at compose.
The graph is frozen composition data only. Runtime execution remains the unary sequential turn loop;
bindings cannot become a dynamic DAG scheduler. Multi-agent execution is unavailable before mediated
`agent.spawn` opens at M-6.

The canonical contract is:

```text
mhf.manifest/2 -> CanonicalManifest -> FrozenComposition[D_H]
  -> ActivationPlan[activation_digest] -> RunPlan[D_R]
```

`FrozenComposition` is logical immutable composition. `ActivationPlan` adds concrete cells,
validated interfaces, readiness, initialization dependencies, and reverse cleanup without adding
authority or workflow scheduling. `RunPlan` binds task/environment/store/model/oracle/authority/budget
for one execution. Supported `mhf.harness/1` bytes normalize at ingress through M-4 and MUST NOT
survive as a second internal value. See ADR-0088.
