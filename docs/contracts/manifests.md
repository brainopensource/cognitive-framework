---
status: living
id: contract-manifests
class: contract-reference
authority: descriptive
canonical_for:
  - manifest-schema-contract
source_of_truth:
  - docs/05_adr/0077-named-component-graph-manifest.md
derived_from:
  - docs/05_adr/0077-named-component-graph-manifest.md
applies_to:
  - v0.6.1
implementation_status: RATIFIED_NOT_IMPLEMENTED
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-23
supersedes: []
superseded_by: null
---

# Named Component Graph Manifest (`mhf.manifest/2`)

> **Schema:** Not present yet; `mhf.manifest/2` is an M-3 deliverable.
> **Status:** `RATIFIED_NOT_IMPLEMENTED` (Governed by ADR-0077; target milestone: **M-3**).

---

## Ratified structure

ADR-0077 requires typed named components, typed directed bindings, entrypoints, explicit profiles,
and capability-selector-based spawn authorization. All behavior-affecting values enter `D_H`.
Unknown kinds, dangling edges, incompatible bindings, and unconsumed authority fail at compose.
The graph is frozen composition data only. Runtime execution remains the unary sequential turn loop;
bindings cannot become a dynamic DAG scheduler. Multi-agent execution is unavailable before mediated
`agent.spawn` opens at M-6.

The current repository contains `schemas/mhf/harness_manifest.schema.json` for the existing
`mhf.harness/1` surface. There is no `mhf.manifest/2` schema or graph compiler on disk yet; M-3
must land the schema, parser, bindings, compatibility reader, and RF-28…RF-33 together. Therefore
this page deliberately provides no executable JSON example before the schema exists.
