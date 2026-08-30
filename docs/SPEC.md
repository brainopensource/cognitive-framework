---
id: spec.core
canonical_id: spec.core
class: normative
authority: normative
truth_plane: TARGET
status: living
implementation_status: PARTIAL
owner: principal-systems-architect
canonical_for:
  - normative requirements and invariant navigation
purpose: State the compact current TARGET contract and route implementation facts to their AS_BUILT owners.
audience:
  - developer
  - architect
  - contributor
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-08-29
normative_authority:
  - VISION.md
  - docs/SPEC.md
  - docs/01_law/
  - decision.index
relationships:
  - arch.system.overview
  - decision.index
  - execution.milestones
  - theory.agent-substrate
reviewer: delegated-tech-lead-block-e
confidence: high
---

# AETHER TARGET Specification

## Purpose

This page is the compact normative owner for the reconstructed **TARGET** contract. It does not describe implementation merely because a requirement exists. AS_BUILT structure and behavior remain owned by the [architecture](architecture/overview.md) and [reference](backend/reference/schemas.md) pages at analysis SHA `9fd444674bf3a97f2673ff36a5f5928ef046c574`.

RFC-2119 terms are normative. Each clause carries a Block E TARGET claim ID; the generated reconciliation register records its authority, implementation evidence, relationship, status, and gap.

## Identity and causal truth

- **`TC-E-001`** AETHER **MUST** remain a general event-sourced agentic-computation substrate, not a domain-specific harness, workflow engine, or certification system.
- **`TC-E-002`** The fundamental execution unit **MUST** be a typed causal operation within an execution lineage.
- **`TC-E-003`** Durable causal events **MUST** be authoritative facts; large content **MUST** be content-addressed artifacts; projections, indexes, caches, and telemetry **MUST NOT** become a second truth.
- **`TC-E-004`** Replay of persisted facts and probabilistic re-execution **MUST** remain distinct.
- **`TC-E-005`** An agent **MUST** be represented as identity, policy, event-derived projection, and execution boundary. No persistent in-memory Agent object may be required for semantic continuation.

## Trusted execution

- **`TC-E-022`** The S0–S12 microkernel **MUST** remain a bounded, domain-blind reference monitor for admissibility, authority, generic budgets, and effect settlement.
- **`TC-E-023`** Capability grants constrain agents; isolation policy constrains plugin code. Neither authority system may substitute for the other.
- **`TC-E-029`** All privileged effects **MUST** preserve declared-versus-emitted identity, merge controls at the call site, persist intent before dispatch, and fail closed on forged or widened authority.
- **`TC-E-030`** Production replay parity **MUST** reconstruct durable storage in a fresh process.
- **`TC-E-031`** Evaluation authority **MUST** remain exterior, identity-separated, and cryptographically bound.
- **`TC-E-032`** Plugins **MUST** be untrusted by default and isolation claims **MUST** be measured rather than asserted.
- **`TC-E-033`** The kernel and domain **MUST** remain domain-blind and within the ratified Trusted Core budget.

## Composition, turns, and extensibility

- **`TC-E-008`** Static composition declares available capabilities; the durable trajectory records what actually occurred. Neither graph may impersonate the other.
- **`TC-E-038`** The sole production chain **MUST** remain `mhf.manifest/2 -> CanonicalManifest -> FrozenComposition -> ActivationPlan -> RunPlan -> EpisodeEngine`.
- **`TC-E-039`** The canonical turn loop **MUST** remain unary and sequential except where a separately ratified, measured disposition explicitly authorizes a bounded case.
- **`TC-E-040`** Runtime profiles **MUST** be explicit and identity-bearing in `D_R`; unavailable requested containment **MUST** fail closed.
- **`TC-E-041`** Plugin activation **MUST** materialize a usable service or handle, or fail. Lifecycle metadata alone is not activation.
- **`TC-E-027`** JSON Schema, JCS, and golden vectors are the wire source of truth; generated readers SHOULD replace handwritten mirrors.
- **`TC-E-053`** Pure deterministic transforms, bounded protocol recovery with no silent execution, state-dependent tool policy, deterministic failure attribution, and fail-closed preflight are the accepted `ADR-0106` evolution seam.

## Delegation, topology, and budgets

- **`TC-E-013`** `agent.spawn` **MUST** be the sole recursive-delegation primitive and re-enter the ordinary runtime through an attenuated child lineage.
- **`TC-E-014`** Child action, resource, constraint, depth, turn, and budget authority **MUST NOT** exceed the parent.
- **`TC-E-042`** Additive resources are exactly `usd_micros`, `millis`, `tokens`, and `bytes`; depth and turns are structural ceilings.
- **`TC-E-017`** Topology declarations carry no authority. Ready roles **MUST** execute as ordinary mediated children and exchange dependency context through authorized artifact references.
- **`TC-E-049`** The required direct, planner/executor/reviewer, and fork/read/merge topologies **MUST** demonstrate real effects and persisted artifact flow before acceptance.
- **`TC-E-052`** `mhf.topology/2` is an accepted workflow seam, not authority for a second runtime or unrestricted concurrent execution.

## State, memory, learning, and evidence

- **`TC-E-018`** Memory retrieval **MUST** verify scoped, revocation-aware authorization before ranking and artifact dereference; retention never authorizes capture.
- **`TC-E-019`** Learned compositions **MUST** be immutable, content-addressed, evaluated on held-out workloads, promoted by authority distinct from generator/evaluator, and reversibly rolled back.
- **`TC-E-026`** `D_H`, `D_R`, and `D_X` **MUST** remain distinct identities and bind every behavior-affecting input at their respective planes.
- **`TC-E-035`** A completed trajectory **MUST** preserve invoked-turn attribution, explicit missingness, conserved cost, and the verified pre-crash prefix.
- **`TC-E-043`** New production event envelopes **MUST** use `mhf.event/2`; compatibility readers may accept frozen predecessors without rewriting historical identities.
- **`TC-E-046`** Facts, artifacts, projections, telemetry, and attestations **MUST** remain distinct. Only exact-subject, digest-addressed, independently verified receipts may close mandatory gates.

## Product and release boundary

- **`TC-E-047`** M-9 remains a TARGET operational beta: unified configuration and clients, packaged CLI/API/TUI/Studio, real plugin lifecycle, health/readiness, two real workflows, restart/resume, and offline-after-install behavior.
- **`TC-E-048`** M-10 remains a TARGET final release: supported migrations, backup/restore, deployment profiles, fault injection, security/performance qualification, reproducible artifacts, soak evidence, and an exact-subject signed release envelope.
- **`TC-E-050`** Every client start-run path **MUST** select a valid runtime profile consistently with the identity-bearing profile contract.
- **`TC-E-051`** Client surfaces SHOULD converge on a coherent command and configuration model without moving runtime authority into the clients.

## Explicit implementation gap summary

The TARGET contract is `PARTIAL` at the recorded AS_BUILT SHA. The most important divergences are:

- The live TypeScript `StartRun` path contradicts the valid-profile requirement ([runtime-service reference](backend/reference/runtime-service.md)).
- Multi-role/topology mechanisms exist, but the full accepted real-effect/artifact-flow integration is only partial at the recorded SHA ([delegation architecture](backend/architecture/delegation-topology.md)).
- The M-9 unified product/client boundary and M-10 qualification contract remain planned ([milestone gates](execution/milestones.md)).
- Protocol-recovery, tool-policy, transform, and workflow seams exist, but the accepted `mhf.topology/2` workflow surface is not a canonical production execution path.

The complete claim-by-claim result is generated in `.generated/knowledge/target-as-built-reconciliation.jsonl`; this page owns the requirements, not the reconciliation ledger.

## Refusals

AETHER does not authorize a second runtime, a domain-aware kernel, authoritative in-memory agent state, a workflow DAG with independent authority, self-certified promotion, silent containment downgrade, or evidence backfill. Any reversal requires current normative amendment and the required falsifiers; implementation convenience is not authority.
