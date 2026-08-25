---
id: adr-0095-vision-as-law-zero-and-roadmap-reconciliation
adr: 0095
class: decision
authority: binding-decision
canonical_for:
  - documentation-authority-hierarchy
  - architectural-identity-lock
  - v07-roadmap-reconciliation
  - milestone-identifier-mapping
status: accepted
owner: engineering-director
version: "0.7.0"
last_verified: 2026-08-25
accepted_date: 2026-08-25
extends:
  - ADR-0094
supersedes:
  - ADR-0088-roadmap-sequencing-m5-through-m8
  - ADR-0093-milestone-identifier-semantics
superseded_by: null
---

# ADR-0095 — `VISION.md` as Law Zero, and the v0.7+ roadmap reconciliation

## Context

`VISION.md` states the architectural thesis the project has accepted for v0.7+: AETHER is a general
event-sourced agentic computation framework and experimental substrate, in which an agent is a
*projection* over a region of the causal event graph rather than a persistent object.

That thesis was written with `authority: descriptive` frontmatter while `SPEC.md` carried
`authority: normative`. The declared precedence ladder in `SPEC.md` and `docs/README.md` therefore
made every historical law leaf, ADR, roadmap row, and README paragraph *formally superior* to the
accepted architecture. The document also opened with a self-declaration ("law number zero") that no
machine-readable metadata supported, and its frontmatter had been copied from `README.md`
(`canonical_for: repository-overview, quick-start`), which is not what it is canonical for.

The practical consequence was a governance inversion. A developer could correctly cite
`01_law/RUNTIME.md`, ADR-0088, or the milestone ladder to reject a Vision concept — not because the
concept was wrong, but because older lower-level text still described the previous architecture. The
same inversion had already produced the RF-85 blockage that ADR-0094 corrected: an assurance
mechanism became the critical path because the documents that named it outranked the documents that
scoped it.

This ADR fixes the hierarchy itself rather than arguing the architecture again.

## Decision

### 1. `VISION.md` is Law Zero

`VISION.md` is promoted to `class: charter`, `authority: constitutional`, `status: locked`. It is the
binding architectural and product authority for v0.7+. Its frontmatter is corrected to declare what it
is actually canonical for: architectural identity, agentic ontology, product principles, long-term
direction.

The precedence ladder becomes, highest first:

```text
0  VISION.md                    constitutional   identity, ontology, direction
1  SPEC.md + 01_law/            normative        requirements and invariants
2  02_decisions/                binding          local decisions, may refine not contradict
3  05_contracts/, 06_protocols/, schemas/        wire realization
4  03_execution/milestones.md   sequencing       delivery order and gates
5  03_execution/sprint_active.md authorization   the only board that authorizes work
6  README, 04_architecture/, 07_engineering/, 08_theory/   communication only
```

A lower document MUST NOT be used to reject a concept accepted in the locked Vision. Where a lower
document contradicts it, the lower document is stale and MUST be reconciled.

### 2. The locked architectural thesis

Subordinate documents MUST preserve all of the following:

- AETHER is a general event-sourced agentic computation framework and experimental substrate — not
  primarily a security-certification system, a coding harness, or a workflow engine.
- The fundamental unit is a **typed causal operation within an execution lineage**.
- **Agent is not a privileged persistent object.** It is a dynamic projection over lineage, events,
  artifacts, policy, context, budget, and execution boundaries.
- Events are canonical causal history; artifacts retain large relevant content; projections
  reconstruct semantic state; caches and indexes remain derived and rebuildable.
- The kernel stays minimal and domain-blind, owning only generic authority and effect invariants.
- Runtime owns composition, lifecycle, sessions, persistence, and execution. Agency owns generic
  transition/interaction mechanics. Plugins, adapters, and primitives implement concrete
  capabilities. Policies decide behavior. Topologies define structural relationships. The scheduler
  controls readiness, placement, and temporal execution.
- Memory, skills, learning, and metacognition are higher-level projections, plugins, or policies
  built from the same primitives. **They never become kernel semantics.**

### 3. The reconciled roadmap

| Milestone | Outcome |
|---|---|
| **M-4** | Useful coding product plus scientific trajectory capture |
| **M-5a** | Event-derived `AgentView` and lineage semantics; re-tag the substrate baseline |
| **M-5b** | Formal Pack #2 as the generality falsifier against that new baseline |
| **M-6** | Recursive delegation through nested lineages |
| **M-6.5** | Adaptive strategy / metacognition as policy, reducer, or plugin |
| **M-7** | Declarative topologies plus measured concurrency and parallelism where justified |
| **M-8** | Memory, retrieval, skills, and learning |
| **M-9** | Integrated AETHER v1.0 General Agent Framework |

The substrate freeze moves **after** M-5a. Proving zero semantic diff while simultaneously changing
the semantics of agent state was self-contradictory in the previous ordering; RF-86 is measured
against the post-M-5a baseline instead. RF-86 itself is not weakened.

### 4. Milestone identifier mapping (provenance preserved)

Historical identifiers keep their historical meaning. Documents referring to a milestone by its
pre-0095 sense MUST be read through this table, which is authoritative for translation:

| Historical id | Historical meaning | v0.7+ successor |
|---|---|---|
| M-4 (ADR-0094) | Product coding proof, RF-95 | **M-4**, unchanged, plus trajectory capture |
| M-5 (ADR-0088) | Formal Pack #2, RF-86 | split into **M-5a** (AgentView) then **M-5b** (RF-86) |
| M-6 (ADR-0080/0090) | Mediated `agent.spawn` | **M-6**, reframed as nested lineages; event roster unchanged |
| M-7 (ADR-0092) | Measured scheduler and bounded concurrency | folded into **M-7**; the M7-01 measurement lane keeps its identifier |
| M-8 (ADR-0088) | Declarative topology support | folded into **M-7** alongside concurrency |
| M-9 (ADR-0088) | Retrieval, skills, macro laboratory | **M-8** memory/retrieval/skills/learning |
| M-10 (ADR-0088) | Governed meta-cognition | **M-6.5** (operational meta-control) and **M-9** (v1.0 integration) |

`M-6.5` is a new identifier, not a renamed one. **M7-01 keeps its name and remains a named parallel
measurement lane**; it terminates in an explicit Director decision to implement, simplify, or cancel,
and that decision is recorded as a successor ADR. Its provenance is not absorbed silently.

### 5. What is superseded

- ADR-0088's roadmap sequencing for M-5 through M-8 is superseded by §3 and §4 above. Its concept-lock
  content on composition, identity, and refusals is **retained**.
- ADR-0093's milestone identifier semantics are superseded by the mapping in §4. Its release-baseline
  content is retained.
- ADR-0094 is **extended, not superseded**: product-first M-4 and optional assurance remain in force.

No prior ADR file is edited. All remain immutable historical provenance.

### 6. Assurance remains available and honest

Security, containment, cryptographic evaluation, hermetic execution, and RF-85 remain fully available
as optional profiles and capabilities. They are not the identity of AETHER and are not prerequisites
for ordinary framework development. The following honesty invariants are **unaffected by this ADR**
and remain binding:

- the resolved `ExecutionProfile` enters `D_R`; no profile may disguise its assurance level;
- `evaluation: none` derives `unattributable_for_promotion = true`;
- unsigned or forged verdicts fail closed (I-5);
- an explicitly requested containment mode that is unavailable **fails closed**, never falls back to
  the host under the same `D_R`.

### 7. Blocking is technical, never ceremonial

A team is blocked only when its work depends on an unfinished interface, schema, invariant, primitive,
or runtime contract. Milestone-wide locks are removed. Every remaining blocked status MUST name its
technical dependency.

## Consequences

The repository gains one coherent hierarchy, one architectural thesis, and one roadmap. The cost is
that `VISION.md` now carries real obligation: changing direction requires a Vision-superseding ADR
rather than an edit, and subordinate documents must be kept reconciled rather than allowed to drift.

Documents describing implementation that has not yet reached the Vision must say so explicitly as
*current-state gap / planned migration*. Known gaps at acceptance: agent state still lives partly in
`Episode`/`HarnessSession` objects rather than in projections (M-5a); `runtime/entrypoint.py`,
`runtime/scoring.py`, and `runtime/autonomous_grant.py` still carry coding-domain knowledge that
belongs in packs and adapters; `agent.spawn` is inert; no topology, scheduler, memory, or
meta-control layer exists.
