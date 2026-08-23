---
status: living
id: contract-manifests
class: contract-reference
authority: descriptive
canonical_for:
  - manifest-schema-contract
source_of_truth:
  - docs/02_decisions/0077-named-component-graph-manifest.md
derived_from:
  - docs/02_decisions/0077-named-component-graph-manifest.md
applies_to:
  - v0.6.1
implementation_status: IMPLEMENTED_PENDING_M3_GATE
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-23
supersedes: []
superseded_by: null
---

# Named Component Graph Manifest (`mhf.manifest/2`)

> **Schema:** [`schemas/mhf/manifest_v2.schema.json`](../../schemas/mhf/manifest_v2.schema.json).
> **Status:** Implemented in the packages domain/compiler; M-3 falsifier closure remains required.

---

## Ratified structure

ADR-0077 requires typed named components, typed directed bindings, entrypoints, explicit profiles,
and capability-selector-based spawn authorization. All behavior-affecting values enter `D_H`.
Unknown kinds, dangling edges, incompatible bindings, and unconsumed authority fail at compose.
The graph is frozen composition data only. Runtime execution remains the unary sequential turn loop;
bindings cannot become a dynamic DAG scheduler. Multi-agent execution is unavailable before mediated
`agent.spawn` opens at M-6.

The frozen `mhf.harness/1` reader remains supported for compatibility. New `/2` values are parsed by
the domain named-graph reader and frozen through the packages registry compiler; runtime execution
still uses the unary sequential loop and never schedules graph edges.
