---
id: theory.agent-substrate
canonical_id: theory.agent-substrate
class: theory
authority: conceptual
truth_plane: TARGET
status: living
implementation_status: EXPERIMENTAL
owner: principal-systems-architect
canonical_for:
  - conceptual model and research questions
purpose: Explain the current conceptual agentic-substrate thesis without implying implementation or authorization.
audience:
  - researcher
  - architect
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-08-29
normative_authority:
  - VISION.md
relationships:
  - spec.core
  - arch.agency.turns
  - arch.orchestration.delegation
  - arch.memory.learning
reviewer: delegated-tech-lead-block-e
confidence: high
---

# Agentic Substrate Theory

## Status boundary

This page is **TARGET conceptual framing** with status `EXPERIMENTAL`. It does not claim that every concept below is implemented, accepted by a milestone, or authorized for current work. Exact implementation belongs to the [AS_BUILT agency](../architecture/agency.md), [delegation](../architecture/delegation-topology.md), and [memory](../architecture/memory-learning.md) owners.

## Central thesis

AETHER treats complex agentic behavior as composition over a small substrate of typed causal operations, durable events, content-addressed artifacts, derived projections, bounded authority, and replaceable policies. Coding agents, researchers, planners, critics, teams, memory systems, and metacognitive controllers should be organizations over the same primitives rather than independent runtimes.

Conceptually:

```text
Agent = Identity + Policy + Event-Derived Projection + Execution Boundary
```

The formula is an ontology and design constraint, not a requirement that a specific Python class exist. Runtime objects may optimize a live process, but durable semantic continuation must be recoverable from causal facts and artifacts.

## Two graphs

- **Composition graph:** the frozen space of components, capabilities, policies, limits, and providers available to a run.
- **Causal trajectory:** the operations actually used, their ordering, inputs, outputs, artifacts, and outcomes.

Future topology and scheduling research may constrain or exploit these graphs, but must not grant authority to graph structure or create a second runtime.

## Derived capability families

Memory, context, topology, scheduling, delegation, learning, skills, and meta-control are derived capability families. They may be projections, plugins, policies, adapters, or versioned configuration. They are not mandatory independent layers and do not become kernel semantics.

## Research questions

- When does bounded read concurrency provide material benefit after coordination and recovery costs?
- Which trajectory variables are causally sufficient for replay, comparison, and resimulation without indiscriminate content capture?
- Which deterministic transforms should replace agent/model steps while preserving attribution?
- When does adaptive strategy improve outcomes beyond its measurement and control overhead?
- How can immutable compositions be learned, evaluated, promoted, and rolled back without collapsing generator, evaluator, and promoter authority?
- Which protocol vocabulary is stable enough to support heterogeneous agents and tools without encoding domain ontology in the kernel?

These questions remain `EXPERIMENTAL` unless current law, an indexed accepted ADR, implementation evidence, and the applicable acceptance receipts establish a stronger status.
