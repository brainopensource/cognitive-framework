---
adr: 0070
title: "Recursive substrate: Agent = Principal + HarnessInstance; spawn is the only delegation primitive; swarm is policy; graphs are event projections"
status: accepted
source_section: "v0.6 Concept Lock"
---

# ADR-0070: Recursive substrate — Agent, spawn, swarm-as-policy

**Context.** Proposals introduce Agent, SubAgent, MetaAgent, and swarm participants as if they
needed distinct engines. The as-built runtime already has recursive `EpisodeEngine.spawn()` with
attenuation and `causationId` tagging (`vanguard/packages/agency/episode/engine.py:531-687`).
`layer0/scheduler/driver.py:170-192` emits `CHILD_SPAWNED` then immediate `CHILD_RETURNED` with
`spans: []` — a stub, not a primitive. ADR-0003 already forbids a runtime workflow graph.
ADR-M0-12 already forbids treating a tool as an episode. SPEC §6.3 described multi-agent
delegation as Phase 3; delaying the *primitive* until then would force a structural migration.

**Decision.**

1. Canonical execution abstraction:
   `Agent = Principal + HarnessInstance`.
   `SubAgent = ChildPrincipal + HarnessInstance` via the same `spawn`.
   Meta-capabilities are additional grants on the same pair, not a `MetaLoopEngine`
   (ADR-M0-12, ADR-0041).
2. `spawn(parent, harness, capabilities, budget)` is the only delegation primitive.
   Invariants (semantics locked now; engine completeness is a later code wave):
   - `Capabilities(child) ⊆ Capabilities(parent)`
   - `Budget(child) ≼ remaining(parent)` component-wise on the six-dimension reservation
     (ADR-M0-07)
3. Swarm / multi-agent coordination is a **policy** over agents, not a swarm engine.
4. Relations `spawned_by`, `caused_by`, `produced`, `consumed`, `evaluated_by` are **projections
   of events**. They MUST NOT become a graph database or a DAG workflow runtime (ADR-0003,
   `DEFERRED_REJECTED.md` REJ-01).
5. Every new event kind MUST carry: `project_id`, `principal_id`, optional
   `parent_principal_id`, `episode_id`, optional `parent_episode_id`, `harness_digest`,
   `causation_id`, `correlation_id`. Existing optional envelope fields in
   `layer0/events/envelope.py` become mandatory rather than a second identity scheme.

v0.6 does **not** ship heterogeneous swarms, market allocators, or nested meta-agents. It ships
the primitive so those can later compose without a new engine.

**Alternative considered (and rejected).**

- Separate SubAgent / Swarm / MetaAgent engines. Rejected: falsifies domain-blindness and
  recreates workflow machinery.
- Defer all spawn envelope fields until Phase 3. Rejected: retrofit would migrate the corpus.
- Core graph primitive or graph DB. Rejected: ADR-0003; projections suffice.
- Treat layer0 stub spawn as the implementation. Rejected: it does not run a child.

**Evidence / bound test / links.** Forensic §§8–10, 19 P0-4/P0-5; `agency/episode/engine.py`
spawn + `_CausationEventAdapter`; ADR-0003; ADR-M0-07; ADR-M0-12. Bound tests for subset
invariants and envelope completeness land in the code phase. `REQ-TRUST-001`.

**Reversal condition.** A workload that cannot be expressed as attenuated `spawn` under a
HarnessInstance without a second execution engine, documented with a failed composition
attempt and a newer ADR. Aesthetic preference for "orchestrators" is not reversal.

**Owner · status.** Principal Staff Engineer / Tech Lead · accepted · 2026-08-20 · accepted
