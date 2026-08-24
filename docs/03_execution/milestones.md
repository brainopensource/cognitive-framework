---
id: macro-milestones-ladder
class: execution
authority: execution
canonical_for:
  - macro-milestones-ladder
  - wave-gates
status: living
owner: engineering-director
version: "0.6.2"
last_verified: 2026-08-23
supersedes: []
superseded_by: null
---

# Macro Milestones — AETHER / Vanguard (M-0 → M-10)

**Status:** authoritative sequencing and future backlog. Only tasks opened in
[`sprint_active.md`](sprint_active.md) authorize implementation. A milestone closes on objective
evidence from the canonical executable path, never because schemas, isolated unit tests, or code
merges exist.

---

## Foundation Phases (Waves 0 → 4)

| Milestone | Version | Outcome | Exit gate | Status | Depends on |
|---|---|---|---|---|---|
| **M-0 Engineering truth** | v0.6.0 | CI measures `vanguard/packages/` and named falsifiers | Production suites, F-01…F-21, codegen, and architecture gates wired | **COMPLETE** | ADR-0075 |
| **M-1 Trust Spine** | v0.6.0 | Unforgeable authority, state, identity, and signed evidence | S0–S12 falsifiers green; single writer; exterior verifier; TCB `<= 1438` LOC | **COMPLETE (GREEN)** | M-0 |
| **M-2 One runtime and recovery** | v0.6.1 | Truthful trajectories and restart-safe state | RF-23 rich/conserved `mhf.trajectory/1` plus RF-25 fresh-process SQLite-WAL continuation | **COMPLETE (GREEN)** | M-1 |
| **M-3 Extensibility contracts** | v0.6.2 | Named graph, packages registry lifecycle, and Layer-0 retirement components | RF-28…RF-45 and prior NOVA-4 evidence retained | **OPERATIONAL CLOSURE REOPENED** | M-2 |
| **M-3C Canonical Composition Convergence** | v0.6.2 | One canonical public `compose -> freeze -> activate -> run` authority across code and table probes | G0–G4 / RF-78–RF-84: canonical identity, lifecycle, durable evidence lineage, zero competing production authority | **CLOSED (GREEN) — DIRECTOR DECISION 2026-08-24** | M-2 plus retained M-3 evidence |
| **M-4 Foundation E2E (STOP)** | v0.6.3 | One honest coding-agent run through the complete substrate | RF-85: nine source-derived rows, one uninterrupted lineage, zero human repair or synthetic substitution | **ACTIVE — ENVIRONMENT QUALIFICATION; CONCEPT LOCKED** | M-3C |

### Why M-3C exists

The prior M-3 work implemented valuable `/2` graph and registry contracts and removed the `layer0/`
tree, but static reconciliation found that the public runtime still executes through the legacy pack
reader and global bindings while named composition and lifecycle remain side paths. M-3C repairs that
bounded seam. It does not rewrite the kernel, episode mechanism, identity algebra, ledger, evaluator,
or sandbox.

### M-3C objective evidence contract

| Gate | Required observation | Objective evidence |
|---|---|---|
| **G0 — Authority/RED** | ADR-0088 and law agree before refactoring | Decision/law ratified; RF-78/RF-79 allocated and red against the diagnosed public path |
| **G1 — Canonical composition** | One authored `/2` shape and one normalized immutable composition identity | RF-78/RF-79: both domains enter one API; compatibility preserves facts; identity-complete `D_H`; unknown authority denies |
| **G2 — Public activation** | Registry lifecycle is reachable from production execution | RF-80/RF-81: both domains activate and retire through one lineage; deterministic cleanup; no graph scheduling or privileged plugin writer |
| **G3 — Durable evidence** | Release execution is restart-safe and M-4 evidence is source-derived | RF-82/RF-83: file WAL, crash continuation, preserved identities, verified cross-digests/signature; asserted booleans deny |
| **G4 — Convergence proof** | No competing production authority remains | RF-84: trace, compatibility parity, clean gates and independent review; legacy stops at ingress |

### M-4 single-run evidence contract

All nine rows MUST bind the same uninterrupted `run_id`, episode lineage, composition, event range,
and immutable artifacts. A stitched trace, cassette/fake substitution, manually copied verdict,
host-execution fallback, or separately passing runs does not satisfy this gate.

| # | Required observation | Objective evidence |
|---:|---|---|
| 1 | Real model invocation | Non-fake, non-cassette provider/model/fingerprint and measured usage |
| 2 | Authorized effect | Descriptor-bound grant, decision, reservation, S8 point-of-effect verification, and matching request |
| 3 | Real filesystem change | Before/after artifact digests and patch receipt inside the run workspace |
| 4 | Rootless sandbox | Attested UID, mount, network, and syscall probes; evaluator path absent; no host fallback |
| 5 | Exterior signed evaluation | Oracle/image/subject/protocol binding and cryptographically verified evaluator signature |
| 6 | SQLite-WAL record | Complete event range, project hash-chain continuity, and durable S8a intent |
| 7 | Cold reconstruction | Fresh process folds the persisted chain to the same state and legally continues without repeating a settled effect |
| 8 | Rich trajectory | Populated `mhf.trajectory/1` with ordered invocations, explicit measurement status, conserved cost, identities, receipts, outcome, and evidence |
| 9 | One runtime authority | Trace/import evidence proves the canonical composition/activation/session path and no alternate production driver |

---

## Post-Foundation Macro Roadmap (Waves 5 → 10)

These are non-authorizing horizons until their dependencies close. Any change to the accepted
universal-loop, SPI, identity, authority, or promotion contracts requires its reversal evidence and a
successor ADR; roadmap prose cannot reopen them.

| Milestone | Version | Focus and outcome | Exit gate | Status | Depends on |
|---|---|---|---|---|---|
| **M-5 Generality Proof** | v0.7.0 | Substantive Math/Formal Pack #2 and attributable T0 witness | RF-86: same public path as Pack #1 and zero semantic diff under `domain/`, `ports/`, `kernel/`, `agency/`, or `runtime/` during the proof | **LOCKED; PLANNED** | M-4 |
| **M-6 Mediated Delegation** | v0.8.0 | `agent.spawn` as an ordinary S0–S12 capability-mediated effect | RF-55–RF-59 and RF-26; no grant denies; authority, budget, depth, turns, and lineage attenuate; recovery never repeats settled spawn | **LOCKED; PLANNED** | M-5 |
| **M-7 Measured Scheduler and Bounded Concurrency** | v0.9.0 | Measure first, then optionally lift I-11 for independence groups, leases, and Pareto profiles | Accepted measurement ADR; reproducible sequential baseline; RF-46–RF-48; no duplicate/unknown effect; explicit Director lift of I-11 | **CONCEPT LOCKED** | M-5, M-6 |
| **M-8 Explicit Topology Support** | v0.9.x | Debate, critic/reviser, planner/executor/verifier, bounded trees, evolution, and swarms expressed through composition plus mediated delegation | RF-65 reference topologies with zero kernel/episode-engine diff; RF-66 universal-loop challenge adjudicated with evidence | **CONCEPT LOCKED** | M-6, M-7 |
| **M-9 Retrieval, Skills, and Macro Laboratory** | post-v1 research horizon | Rebuildable retrieval, evidence-ranked skills, scaled orchestration measurement, and least-privilege macro candidates | RF-77 rebuild equality; held-out lift; RF-67–RF-68 selector hull/dispatch; five-SPI review; published scale evidence | **NON-AUTHORIZING HORIZON** | M-7, M-8, separate v1 review |
| **M-10 Governed Meta-Cognition** | post-v1 research horizon | Attributable belief/policy experiments and reversible human promotion | RF-69–RF-70; preregistered prediction; exact paired McNemar, A/A floor, effect interval, exterior verdict, human pointer, and tested rollback | **NON-AUTHORIZING HORIZON** | M-8, M-9 |

### M-5 and M-6 pre-implementation contracts

M-5 selects the exact formal workload and verifier at its R2 gate, then proves Pack #2 through the
unchanged public substrate. The proof interval is invalid if the domain requires a semantic change in
`domain`, `ports`, `kernel`, `agency`, or `runtime`; that outcome returns an architectural finding
instead of weakening RF-86.

```text
formal_pack -> canonical_compose -> activate -> RunPlan
-> sequential EpisodeEngine -> S0..S12 -> WAL/recovery -> trajectory -> signed verdict
```

M-6 models delegation as a normal requested effect. The kernel authorizes and settles the generic
descriptor; only a runtime adapter interprets an authorized durable intent as child creation.
Authority, six-dimensional budget, turns, depth, lineage, cancellation, and recovery all attenuate.

```text
parent request(agent.spawn) -> S0..S8a durable intent -> runtime spawn adapter
-> attenuated child context -> ChildSpawned/ChildReturned -> S9..S12 settlement
```

---

## Dependency-Ordered Sprint Register

The active M-3C task contracts and file ownership live only in
[`sprint_active.md`](sprint_active.md#3-authorized-sprint-sequence). This register preserves macro
sequencing without duplicating implementation instructions.

| Sprint | Primary outcome | Parallel ownership | Gate / dependency | State |
|---|---|---|---|---|
| **3C.0** | Ratify authority, reconcile law, allocate falsifiers, and confirm RED against the public path | A: architecture/decision; B: baseline/characterization | G0; M-2 and retained M-3 evidence | **COMPLETE** |
| **3C.1** | Canonical authored manifest, normalization, composition identity, and code/table ingress | A: core contract/path; B: packs/binding providers/vectors | G1 after G0 | **COMPLETE** |
| **3C.2** | Public activation, registry lifecycle, shared lineage, and deterministic cleanup | A: runtime/registry integration; B: caller/lifecycle/fault integration | G2 after G1 | **COMPLETE** |
| **3C.3** | File-backed release durability and source-derived evidence bundle | A: identity/evidence join; B: runner/recovery/environment fixtures | G3 after G2; preparatory sub-slices may start after G0 interfaces freeze | **COMPLETE** |
| **3C.4** | Retire alternate authority and independently certify convergence | A: production retirement/audit; B: migration/full gates/docs sync | G4 after G1–G3 | **COMPLETE** |
| **4.1** | One real coding-agent run from preregistration to signed completion | Release + independent evidence review | M-3C/G4 and real provider/evaluator environment | **ACTIVE — ENVIRONMENT QUALIFICATION** |
| **5.1** | Math/Formal Pack #2 generality proof | Future allocation | M-4 | **LOCKED** |
| **5.2** | Exact attributable T0 witness and consolidation | Future allocation | Sprint 5.1 | **LOCKED** |
| **6.1** | Capability-mediated `agent.spawn` | Future allocation | M-5 | **LOCKED** |
| **7.1** | Sequential measurements and concurrency decision ADR | Future allocation | M-6 | **LOCKED** |
| **7.2** | Bounded concurrency and feasible Pareto routing, only if authorized | Future allocation | Sprint 7.1 and Director lift of I-11 | **LOCKED** |
| **8.1** | Reference topologies through ordinary composition/delegation | Future allocation | M-7 | **LOCKED** |
| **9.1** | Retrieval/skills/macro laboratory | Future allocation | M-8 | **HORIZON** |
| **10.1** | Governed meta-cognition experiment and reversible promotion proof | Future allocation | M-9 | **HORIZON** |

---

## Two-Lane Delivery Model

| Dimension | Devs A — Principal / Specialist / PhD | Devs B — Senior Developers |
|---|---|---|
| Primary responsibility | Irreversible or cross-module architecture, contract ownership, identity, lifecycle, composition/activation integration, and final technical arbitration within ratified law | Bounded implementation of frozen contracts: packs, adapters, persistence wiring, fixtures, callers, conformance, CI, and migrations |
| Autonomy | May decide high-level reversible design within the active charter without per-task approval | May decide local implementation details without changing an interface, authority boundary, or accepted decision |
| Prohibited delegation | Unresolved ontology, trust, identity, event-writer, compatibility-sunset, or recovery decisions cannot be delegated to B | Must not redesign kernel, authority, identity, canonicalization, lifecycle ownership, event semantics, or recovery |
| Integration | Publishes interface + RED contract; owns shared hotspots and cross-lane merge | Builds against frozen interfaces; rebases after A contract slices; reports architectural gaps as falsifiers |
| Acceptance | Cannot self-certify a cross-lane gate | Cannot close a milestone from local tests alone |

### Required task packet

Every future task moved to the active board MUST state: owner lane/class, exact outcome, affected
modules, dependencies, architectural risk, migration path, rollback, acceptance criterion, allocated
falsifier, evidence artifact, definition of done, and prohibited scope.

### Merge and rollback discipline

```text
A interface + RED -> B bounded implementation -> A integration
-> cross-lane gate -> full repository gates -> independent sign-off
```

Rollback is slice-local and must preserve durable compatibility. A legacy reader may remain as bounded
ingress through its ratified sunset; a legacy execution authority may not remain as fallback after G4.

---

## Standing Architectural Constraints

- `sprint_active.md` is the only current implementation authority.
- S0–S12, monotonic attenuation, typed budgets, JCS, `D_H/D_R/D_X`, single-writer WAL truth,
  exterior evaluation, rootless isolation, and I-9 continuity remain frozen through M-3C.
- I-11 sequential execution remains mandatory until M-7 measurement and explicit governance.
- The graph is static composition, never a runtime DAG or alternate episode engine.
- Supported legacy manifests are compatibility ingress through M-4, not a second internal model.
- M-3C adds neither a sixth SPI nor a new event kind without successor decision, allocation, writer,
  reducer, schema, conformance vector, and coverage proof.
- No broad rewrite, third runtime, domain-specific kernel branch, or package-per-concept taxonomy.
- M-4 evidence must be source-derived and cryptographically verified; synthetic preparation evidence
  remains useful but ineligible.
- M-5+ implementation stays locked until each preceding objective gate closes.

---

## Common Gate Sequence

```text
allocated red falsifier -> focused package suites -> cross-lane integration
-> complete production suites -> schema/codegen vectors
-> boundaries/TCB/domain/isolation/duplication
-> RF IDs/metadata/links/stale paths/secrets
-> clean-environment evidence -> independent milestone decision
```
