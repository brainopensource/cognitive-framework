---
adr: 0082
title: "Universal Turn Loop mechanism and M-10 compatibility contract"
status: accepted
accepted_date: 2026-08-21
amended_date: 2026-08-21
source_section: "ALFA Tier S+ Director Ratification"
implementation_milestone: "M-2 mechanism proof; M-5 through M-10 compatibility gates"
---

# ADR-0082: Universal Turn Loop mechanism and M-10 compatibility contract

**Context.** AETHER must remain extensible enough for recursive agents, heterogeneous model routes,
memory/RAG, swarms, macro-tools, and learning without pre-building those systems or adding a new
engine for each algorithm. The stable target is therefore the **shape of future change**: authority,
state, evidence, identity, data, and extension seams. Algorithms remain replaceable policies.

**Decision.**

### Universal mechanism

1. `observe -> propose -> authorize -> effect -> receipt -> evaluate -> (reflect)*` is the one
   universal mechanism and is never a plugin. All concrete effects, including future spawn and
   macros, traverse S0–S12.
2. Debate, critic/reviser, tree search, evolutionary search, and swarms are expressed as component
   graph topology, planner/controller policy, and capability-mediated delegation—not alternate
   episode engines.
3. No inner loop may perform an outer-loop transition. An episode may propose a macro, skill,
   model, or harness candidate; it cannot certify or promote it.
4. RF-66 is the standing challenge: demonstrate an agentic algorithm that requires an engine diff
   and cannot be represented by graph composition plus mediated delegation. A real counterexample
   is reversal evidence, not a documentation failure.

### Cold continuation and swarm premise

5. RF-25 / NOVA-2 is an immediate M-2 gate: a file-backed SQLite WAL episode must lose all live
   process state, reconstruct in a fresh interpreter, continue legally, preserve budgets and digest
   lineage, avoid repeating settled effects, and keep unresolved intents undeterminable until
   reconciled.
6. RF-25 red keeps M-3 closed and invalidates the assumption that M-7 concurrency is merely a
   scheduler refactor. Sequential execution remains law until the M-7 measurement gate.

### M-10 Compatibility Contract — twelve stable substrate primitives

The following primitives are locked as stable seams through M-10. Stability means future features
enter behind them or reverse them explicitly by ADR; it does not mean every future field or
algorithm is implemented now.

| # | Stable primitive | Contract through M-10 | Future capability enabled |
|---:|---|---|---|
| 1 | **Named Component Graph** | Typed, content-addressed components/bindings freeze into `D_H`; graph is composition, not workflow authority. | Debate, critics, trees, swarms, harness builder. |
| 2 | **Universal Mechanism** | One episode/turn mechanism and S0–S12 effect path; no feature-specific engine. | New agent algorithms without foundational rewrites. |
| 3 | **Capability Selectors** | One fail-closed selector algebra; monotonic attenuation; unknown comparison denies. | Safe plugins, spawn, memory, remote/local tools. |
| 4 | **WAL Provenance** | State is reduced from single-writer events and immutable artifact refs; causation and authority lineage are durable. | Recovery, claims, concurrency, credit assignment, audit. |
| 5 | **`D_H/D_R/D_X` Identities** | Composition, execution, and experiment subjects remain distinct and recomputable. | Reproducible caching, pairing, routing, evaluation. |
| 6 | **Rich Trajectories** | Populated attribution, explicit missingness, measured economics, causal effects, artifacts, and exterior evidence. | Active Inference, RL/DPO, skills, cost collapse. |
| 7 | **Artifact References** | Large data is immutable/content-addressed; events carry refs; indices remain rebuildable. | RAG, ASTs, datasets, checkpoints, macro outputs. |
| 8 | **Model Port Metadata** | Provider-neutral model seam plus resolved route, model/fingerprint, usage, pricing provenance, latency, and typed failures. | Local/API mixtures, fallback, ensembles, Pareto routing. |
| 9 | **Index Port** | Retrieval is an exterior replaceable port; an index is a cache, never truth or authority. | Lexical/vector/graph/AST/hybrid search and memory. |
| 10 | **Exterior Evaluator** | The evaluated subject cannot reach or impersonate the signed-verdict authority. | Coding tests, formal proofs, human and benchmark oracles. |
| 11 | **Versioned Schemas** | Draft 2020-12 + JCS; behavior-affecting unknowns fail closed; compatibility readers and sunset gates are explicit. | Additive evolution without silent dialects. |
| 12 | **Human Promotion Pointer** | Automated systems nominate; only promotion authority moves the versioned default pointer, with rollback. | Safe self-improvement of macros, skills, models, harnesses. |

7. Architecture fitness tests must show: a new pack does not change domain/kernel; a new topology
   does not change kernel/episode engine; a model or index implementation enters through its port;
   a macro enters as a least-privilege plugin; indices rebuild from immutable sources; and learned
   state never widens authority.
8. Do not freeze replaceable choices now: vector database, embedding model/dimension, VFE/EFE
   weights, Elo constants, fixed latency/token bands, swarm scheduler, RAG algorithm, DPO trainer,
   or model vendor.
9. `F-*` remains the kernel-control namespace. Proposal/register falsifiers use `RF-*`; RF-72
   enforces uniqueness and the one-time alias table for historical register IDs.
10. The five-SPI freeze remains through M-8 and is reviewed at M-9. A sixth SPI requires two
    independent implementations, a stable wire, a boundary owner, and net complexity deletion.
11. Documentation collapses to SPEC/annexes, accepted ADRs, and one living board at M-5 after M-4,
    never before the foundation evidence exists.

**Bound falsifiers.** RF-25 cold continuation is the immediate M-2 gate. RF-65 runs four advanced
topologies without engine changes at M-8. RF-66 is the standing universal-loop challenge. RF-72
enforces namespace uniqueness. Each of the twelve primitives gains at least one architecture
fitness test before its first consumer ships.

**Alternatives rejected.** Implementing M-10 now; promising zero future refactoring; a plugin turn
loop; mutable in-memory blackboard authority; generic event append; graph database authority; or
freezing particular retrieval/model/learning algorithms as substrate law.

**Reversal condition.** A bounded counterexample to RF-66; a stable primitive preventing two real
independent implementations; or evidence that the compatibility contract forces more system-wide
change than it prevents. Reversal requires a newer ADR and migration/falsifier plan.

**Owner · status.** Engineering Director / Principal Systems Architect · accepted · 2026-08-21

---

## Amendment — 2026-08-23: documentation timing superseded by ADR-0087

Decision clause 11's M-5 timing constraint is superseded by ADR-0087. The content-preserving
topology migration completed before M-4 under link, metadata, duplication, and preservation gates.
This amendment changes navigation only: it does not claim foundation evidence, open a milestone,
or weaken any runtime, compatibility, or authority gate in this ADR.

---

## Amendment — 2026-08-21: name deferred compatibility fitness tests

Naming these tests closes their contracts without implementing their future capabilities:

- **RF-76 — compatibility-reader fidelity (M-3):**
  `test.runtime.test_compatibility_readers.CompatibilityReaderFidelity.test_supported_old_wal_rows_rebuild_equivalent_state`
  proves explicitly supported old WAL rows remain readable through versioned readers and reduce to
  equivalent state, lineage, and artifact identities without invented defaults.
- **RF-77 — rebuildable indices (M-9):**
  `test.contracts.test_index_port_rebuild.IndexRebuildabilityFalsifier.test_deleting_index_and_rebuilding_from_immutable_artifacts_preserves_results_and_citations`
  proves an index can be deleted and reconstructed solely from immutable artifact references while
  preserving retrieval results and source-digest citations.

No executable RF-76 or RF-77 test is added before its named milestone opens.

---

## Amendment — 2026-08-23: RF-25 and RF-23 form one recovery evidence gate

Cold continuation restores more than reducible control state. In the fresh interpreter, the runtime
must verify and fold the SQLite-WAL prefix, reconstruct digest/sequence and Governor state, and
reconcile every pending lease so no reserved budget leaks or becomes spendable twice. Open S8a
intents remain undeterminable until exterior reconciliation. The canonical writer then emits
`RunRecovered` and resumes the legal turn. At `EpisodeCompleted`, RF-23 consumes that same verified
prefix and all post-recovery turns exactly once to produce the complete `mhf.trajectory/1` record.
RF-25 is therefore not green if recovery succeeds while trajectory history is truncated.
