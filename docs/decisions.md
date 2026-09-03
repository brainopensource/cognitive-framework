---
id: decision.index
canonical_id: decision.index
class: decision
authority: current-decision-navigation
truth_plane: TARGET
status: living
implementation_status: IMPLEMENTED
owner: principal-systems-architect
canonical_for:
  - foundational architectural decisions
  - architectural rationale and trade-offs
purpose: Record the non-obvious philosophical choices, trade-offs, rejected alternatives, and reversal conditions governing AETHER.
audience:
  - architect
  - developer
  - contributor
  - auditor
version: 0.9.1a1
last_verified: 2026-09-03
normative_authority:
  - ./SPEC.md
relationships:
  - spec.core
  - arch.system.overview
  - arch.trust.kernel
  - arch.agency.turns
  - arch.state.causal
  - arch.composition.extensibility
  - arch.orchestration.delegation
  - arch.memory.learning
  - arch.assurance.evaluation
reviewer: principal-systems-architect
confidence: high
---

# Architectural Decisions & Philosophical Rationale

This document is the single canonical repository for the foundational architectural choices and trade-offs governing AETHER. It answers strictly **why** non-obvious directions were chosen over defensible alternatives.

Normative requirements belong exclusively to [`spec.core`](SPEC.md), implementation structure to [`architecture`](architecture/overview.md) and [`reference`](backend/reference/schemas.md), and execution status to [`execution.active`](execution/active.md).

---

## DEC-01 — General Agentic Substrate over Domain-Specific Harness or Workflow Engine

**Decision:** AETHER is intentionally designed as a general event-sourced agentic computation substrate rather than a workflow engine, coding harness, or domain-specific application.

**Rationale:** Hardcoding workflow DAGs or domain semantics into the substrate constrains future cognitive topologies and couples low-level execution to ephemeral task structures. Substrate primitives must remain universally reusable.

**Rejected alternative:** A specialized workflow DAG orchestrator or language-model-specific coding harness with hardcoded task phases.

**Reversal condition:** Empirically demonstrable proof that general substrate primitives cannot express required agentic topologies without unacceptable overhead or ergonomic burden.

**Canonical owners:** [`spec.core`](SPEC.md), [`arch.system.overview`](architecture/overview.md) *(Provenance: ADR-0069, ADR-0095)*

---

## DEC-02 — Domain-Blind Minimal Trusted Computing Base (TCB)

**Decision:** The privileged execution kernel is strictly domain-blind, dependency-free, and capped at an auditable code budget ($\le 1438$ logical LOC).

**Rationale:** Privilege escalation, mediation flaws, and non-deterministic leaks scale with TCB complexity. A small reference monitor operating solely on generic action descriptors, scopes, and budgets ensures formal and human auditability.

**Rejected alternative:** Embedding agent memory, model heuristics, or task domain validation directly inside the kernel dispatch path.

**Reversal condition:** Formal mathematical proof that dynamic multi-tenant agent mediation requires domain-aware kernel operations that cannot be safely expressed via user-space capability attenuation.

**Canonical owners:** [`spec.core`](SPEC.md), [`arch.trust.kernel`](backend/architecture/kernel.md) *(Provenance: ADR-0069, ADR-0074, ADR-0096)*

---

## DEC-03 — Authoritative Causal History over Mutable In-Memory State

**Decision:** Authoritative state is defined strictly by the append-only causal event stream; all in-memory objects, projection graphs, and caches are disposable views.

**Rationale:** Mutable in-memory state creates competing truths across crashes, restarts, and distributed processes. Deterministic event folding over an append-only log guarantees crash consistency, provenance auditability, and cold replayability.

**Rejected alternative:** Object-oriented persistence where state machines mutate in-place and serialize periodic snapshots.

**Reversal condition:** Workload evidence demonstrating that deterministic event folding cannot meet latency budgets even when assisted by discardable checkpoint caches.

**Canonical owners:** [`arch.state.causal`](backend/architecture/causal-state.md), [`ref.events`](backend/reference/events.md) *(Provenance: ADR-0071, ADR-0096, ADR-0098)*

---

## DEC-04 — Agent as Ephemeral Projection over Persistent Entity

**Decision:** An agent is an ephemeral identity, policy, and causal projection boundary, not a long-running, stateful in-memory process.

**Rationale:** Stateful agent processes leak memory, fail across process boundaries, and complicate multi-agent coordination. Reconstructing agent perspective on demand from event lineage guarantees stateless resumption and recovery.

**Rejected alternative:** Persistent thread-per-agent or actor-per-agent daemons retaining in-memory cognitive state.

**Reversal condition:** Evidence that cognitive streaming continuation requires low-latency in-memory state that cannot be reconstructed via prefix-cached token buffers.

**Canonical owners:** [`arch.agency.turns`](backend/architecture/agency.md), [`arch.state.causal`](backend/architecture/causal-state.md) *(Provenance: ADR-0070, ADR-0095, ADR-0096)*

---

## DEC-05 — Static Composition Distinct from Observed Trajectory

**Decision:** Declarative composition (`mhf.manifest/2`) declares available capabilities; the durable event trajectory records what actually occurred. Neither may impersonate the other.

**Rationale:** Conflating declared intent with observed execution prevents truthful post-mortem auditing, hides runtime attenuation, and allows unverified declarations to pass as evidence.

**Rejected alternative:** Dynamic manifest mutation during execution to reflect intermediate turn outcomes.

**Reversal condition:** None; maintaining declared versus observed separation is an inviolable architectural auditability invariant.

**Canonical owners:** [`arch.composition.extensibility`](backend/architecture/composition-extensibility.md), [`ref.manifests`](backend/reference/manifests.md) *(Provenance: ADR-0077, ADR-0088)*

---

## DEC-06 — Authority Exclusion from Topology Declarations

**Decision:** Topology graphs and role declarations carry zero intrinsic authority; all child agents and workflows re-enter mediated kernel dispatch.

**Rationale:** Workflow definitions and role graphs are untrusted inputs. Treating DAG edges or role names as capability grants creates privilege escalation vulnerabilities.

**Rejected alternative:** Direct inter-agent peer invocation bypassing kernel reference monitoring.

**Reversal condition:** Hardware-enforced cryptographic capabilities that render software kernel reference monitoring redundant.

**Canonical owners:** [`arch.orchestration.delegation`](backend/architecture/delegation-topology.md), [`spec.core`](SPEC.md) *(Provenance: ADR-0080, ADR-0099)*

---

## DEC-07 — Exterior Evaluator and Promotion Authority

**Decision:** Evaluation, grading, and memory promotion authority must remain exterior to the agent cognition loop and bound to independent cryptographic identities.

**Rationale:** Systems cannot self-certify. Self-grading agents create self-fulfilling reward loops, conceal alignment failures, and introduce catastrophic bias into persistent memory.

**Rejected alternative:** Self-evaluating agent turns where agents score and commit their own learned skills.

**Reversal condition:** Theoretical proof that self-referential cognitive systems can prevent reward hacking without external ground truth.

**Canonical owners:** [`arch.assurance.evaluation`](backend/architecture/assurance-evaluation.md), [`arch.memory.learning`](backend/architecture/memory-learning.md) *(Provenance: ADR-0072, ADR-0079, ADR-0100, ADR-0104)*

---

## DEC-08 — Sequential Turn Simplicity until Concurrency Proves Value

**Decision:** The canonical turn loop and topology execution remain strictly unary and sequential by default; concurrent dispatch is admitted only when justified by measured wall-time advantage on provably disjoint operations.

**Rationale:** Unrestricted concurrency introduces non-determinism, race conditions in budget accounting, replay divergence, and complex recovery semantics without guaranteed performance improvement.

**Rejected alternative:** Default asynchronous / multi-threaded turn dispatch across all agent nodes.

**Reversal condition:** Preregistered empirical benchmark evidence demonstrating $\ge 20\%$ median wall-time reduction with byte-identical result ordering on disjoint, read-only operations.

**Canonical owners:** [`arch.agency.turns`](backend/architecture/agency.md), [`arch.orchestration.delegation`](backend/architecture/delegation-topology.md) *(Provenance: ADR-0070, ADR-0099, ADR-0105, indexed ADR-0106)*

---

## DEC-09 — Orthogonal Separation of Capability Grants and Plugin Isolation

**Decision:** Agent capability grants (attenuated S0–S12 permissions) and plugin isolation policies (OS sandboxing/containerization) are enforced as independent, orthogonal boundaries.

**Rationale:** Model safety (what an agent is allowed to request) and process security (what plugin binaries can execute on the host) protect against different threat vectors. Neither can substitute for the other.

**Rejected alternative:** Relying exclusively on process sandboxing to restrict agent actions, or relying exclusively on model-level capability tokens to contain untrusted binaries.

**Reversal condition:** A unified capability-secure OS substrate where user-space process execution and cognitive model calls share a single hardware capability architecture.

**Canonical owners:** [`arch.trust.kernel`](backend/architecture/kernel.md), [`arch.composition.extensibility`](backend/architecture/composition-extensibility.md) *(Provenance: ADR-0072, ADR-0074)*

---

## DEC-10 — Authorization-Before-Ranking in Memory Retrieval

**Decision:** Memory retrieval must verify principal access scope, category isolation, and legal hold/revocation *before* relevance ranking and artifact dereference.

**Rationale:** Post-ranking filtering leaks existence and metadata of unauthorized memory entries through relevance score distortions and token side-channels.

**Rejected alternative:** Retrieve-and-rank first, followed by downstream output filtering of unauthorized documents.

**Reversal condition:** Zero-knowledge cryptographic vector search that provably prevents cross-principal information leakage during un-authenticated indexing.

**Canonical owners:** [`arch.memory.learning`](backend/architecture/memory-learning.md), [`ref.artifacts`](backend/reference/artifacts-memory.md) *(Provenance: ADR-0096, ADR-0100)*

---

## DEC-11 — Repository Intelligence as an Optional Authority-Free Projection

**Decision:** Repository-intelligence systems such as local symbol indexes, full-text search, dependency graphs, LDA, or SCIP-style providers are optional, reconstructible projections consumed above the substrate through the existing context and index seams. They may select and rank bounded context, but carry no execution authority and never supersede canonical documentation, source, tests, schemas, or causal evidence.

**Rationale:** High-density indexes materially reduce exploratory reads and context cost, especially for language-model agents, but coupling Vanguard to one index implementation would turn a navigation accelerator into a platform dependency and potential competing truth. Keeping retrieval value-only and provider-neutral preserves domain blindness, deterministic fallback, replaceability, and honest degradation when an index is empty, stale, or invalid.

**Rejected alternative:** Embedding LDA or another repository-intelligence engine into the kernel/runtime authority path, treating index health as evidence of source correctness, or requiring a populated external index for ordinary execution.

**Reversal condition:** Reproducible evidence that no provider-neutral context/index contract can preserve the required retrieval semantics or performance, together with a ratified replacement that maintains domain blindness, causal authority, offline operation, and deterministic fallback.

**Canonical owners:** [`spec.core`](SPEC.md), [`arch.agency.turns`](backend/architecture/agency.md), [`arch.composition.extensibility`](backend/architecture/composition-extensibility.md)
