---
id: macro-milestones-ladder
class: execution
authority: execution
canonical_for:
  - macro-milestones-ladder
  - wave-gates
status: living
owner: engineering-director
version: "0.6.1"
last_verified: 2026-08-23
supersedes: []
superseded_by: null
---

# Macro Milestones — AETHER / Vanguard (M-0 → M-10)

**Status:** Authoritative macro execution ladder and future backlog. Only the currently opened tasks
in [`docs/03_execution/sprint_active.md`](sprint_active.md) authorize implementation;
the delivery slices below remain ordered, non-active backlog until their dependency gates open.

**Principle:** A milestone is complete only when its objective falsifiers and gates pass on the canonical path—never when code merely merges.

---

## Foundation Phases (Waves 0 → 4)

| Milestone | Version | Wave | Outcome | Exit Gate (Objective Evidence) | Status | Depends on |
|---|---|---:|---|---|---|---|
| **M-0 Engineering truth** | v0.6.0 | 0 | Living CI measures `vanguard/packages/` and named falsifiers | Production suites wired in CI; F-01…F-21 registered as tests; codegen `--check` wired | **COMPLETE** | Director approval (ADR-0075) |
| **M-1 Trust spine** | v0.6.0 | 1 | Unforgeable evidence, provable state, complete identity, typed budgets, real trajectories | F-01…F-15 green on canonical path; suites of record green; TCB budget ≤ 1438 LOC | **COMPLETE (GREEN)** | M-0 |
| **M-2 One runtime** | v0.6.1 | 2 | One canonical runtime plus economically truthful trajectories and restart-safe state | RF-23 populated/conserved `mhf.trajectory/1` green; RF-25 fresh-interpreter SQLite-WAL continuation green; retained convergence gates green | **COMPLETE (GREEN)** | M-1 |
| **M-3 Extensibility** | v0.6.2 | 3 | Typed Named Component Graph and complete plugin lifecycle on the canonical path | RF-28…RF-45; echo lifecycle over wire; NOVA-4 negatives; `layer0/` source/package/CI surface atomically absent | **COMPLETE (GREEN)** | M-2 |
| **M-4 Foundation E2E (STOP)** | v0.6.3 | 4 | One honest coding-agent run through the complete substrate | Nine populated evidence rows, one uninterrupted `run_id`, zero human intervention or stitched/cassette substitution | **ACTIVE — ENVIRONMENT BLOCKED** | M-1, M-2, M-3 |

---

### M-4 single-run evidence contract

All nine rows MUST bind the same uninterrupted `run_id` and causal lineage. A stitched trace,
cassette/fake substitution, manually copied verdict, host-execution fallback, or separately passing
runs do not satisfy this gate.

| # | Required observation | Objective evidence |
|---:|---|---|
| 1 | Real model invocation | Non-fake, non-cassette provider/model/fingerprint plus measured usage |
| 2 | Authorized effect | Descriptor-bound grant, authorization decision, reservation, point-of-effect verification, and matching request |
| 3 | Real filesystem change | Before/after artifact digests and patch receipt inside the run workspace |
| 4 | Rootless sandbox | Recorded UID, mount, network, and syscall probes; evaluator path absent; no host fallback |
| 5 | Exterior signed evaluation | Oracle/image/subject/protocol binding and a verifiable signature from the exterior evaluator |
| 6 | SQLite-WAL record | Complete event range, project hash-chain continuity, and durable S8a intent |
| 7 | Cold reconstruction | Fresh process reduces the persisted chain to the same state and legally continues without repeating a settled effect |
| 8 | Rich trajectory | Populated, schema-valid `mhf.trajectory/1` with ordered invocations, conserved cost, `D_H/D_R/D_X`, receipts, outcome, and evidence |
| 9 | One runtime authority | Trace/import evidence shows the canonical compose/session path and no alternate driver or Layer-0 runtime |

---

## Post-Foundation Macro Roadmap (Waves 5 → 10)

*These milestones define outcomes and gates only. Sprint-level detail is deferred until the preceding milestone is completed.*

| Milestone | Version | Wave | Focus & Outcome | Exit Gate (Objective Evidence) | Depends on |
|---|---|---:|---|---|---|
| **M-5 Generality Proof & Consolidation** | v0.7.0 | 5 | Pack #2 **Math & Formal Deductive Verification** and exact T0 witness memo | Zero diffs under `packages/{domain,kernel}/`; trajectory/evidence parity with Pack #1; memo key binds subject, inputs, environment, checker, toolchain, assurance, and policy version | M-4 |
| **M-6 Mediated Delegation (`agent.spawn`)** | v0.8.0 | 6 | `agent.spawn` becomes one capability-mediated S0–S12 effect; recursion stays policy | RF-55…RF-59 and RF-26; no grant means deny; child authority/budget/depth monotonically attenuate; kernel remains ≤1438 LOC | M-5 |
| **M-7 Controlled Concurrency & Pareto Routing** | v0.9.0 | 7 | Independence groups, bounded worker pool, WAL-backed claims/leases, and alpha↔delta controller activation | M-7 measurement ADR plus named falsifiers; no duplicate/unknown effect; measured calls, envelopes, bytes, WAL contention, retries, critical path, and cost per signed pass; I-11 lifted only by ADR | M-5, M-6 |
| **M-8 Framework Builder Abstraction** | v0.9.0 | 8 | Debate, critic/reviser, bounded trees, and evolutionary search expressed as manifests plus SDK/CLI clients | RF-65 runs reference topologies with zero kernel/episode-engine diff; RF-66 universal-loop challenge adjudicated | M-6, M-7 |
| **M-9 Retrieval, Skills & Macro Laboratory** | v1.0.0 candidate | 9 | Replaceable hybrid retrieval, evidence-ranked skills, scaled orchestration measurement, and least-privilege macro candidates | RF-77 index rebuild; source-digest citations; held-out retrieval lift; macro selector hull and adversarial replay; five-SPI review; published scale measurements | M-7, M-8 |
| **M-10 Governed Meta-Cognition (1.0)** | v1.0.0 | 10 | VFE belief fitting, EFE policy selection, attributable DPO/trajectory credit, and reversible promotion | RF-67…RF-70; prediction recorded before observation; Pareto-safe exact paired McNemar with A/A floor, effect interval, exterior verdict, human pointer, and tested rollback | M-8, M-9 |

---

## Standing Architectural Constraints

- **Single Execution Board:** Live sprint tasks live exclusively in [`docs/03_execution/sprint_active.md`](sprint_active.md).
- **Sequential Execution (I-11):** Sequential execution remains mandatory until the M-7 measurement gate fires.
- **TCB Budget:** Microkernel in `vanguard/packages/kernel/` must not exceed $\le 1438$ LOC.
- **Refusals:** Strictly adhere to the non-claims and refusals in [`SPEC.md` §9](../SPEC.md#9-what-this-specification-refuses-to-build).

---

## Future Backlog by Milestone and Sprint

This register replaces a separate `backlog.md`, which is intentionally not created under the
repository's anti-sprawl rule. A slice moves to the active board only after every dependency is green.

| Sprint | Milestone | Deliverable | Acceptance and bound falsifier | Dependency | State |
|---|---|---|---|---|---|
| **3.1** | M-3 | Compile `mhf.manifest/2`: named instances, typed bindings, profiles, compatibility reader, one canonical parser | RF-28–RF-33, RF-46, RF-73–RF-74, and RF-76 green; edge-only changes alter `D_H`; unknown or unconsumed authority fails closed | M-2 | COMPLETE |
| **3.2** | M-3 | Port the registry FSM and isolation broker to `vanguard/packages/`; run the echo plugin through the complete wire lifecycle | RF-34–RF-45 green; declared absence is pre-execution and ineligible; unsigned or forged evidence fails closed | Sprint 3.1 | COMPLETE |
| **3.3** | M-3 | Delete residual `layer0/` source, packaging, CI, and test surfaces atomically after parity | NOVA-4 / RF-38–RF-45 green; no stale import, package entry, workflow path, or duplicate parser remains | Sprint 3.2 | COMPLETE |
| **4.1** | M-4 | Execute one real coding-agent run from start to signed completion | One uninterrupted `run_id`; all nine evidence rows populated; no human repair, stitched trace, cassette substitution, or forged verdict | M-3 | ACTIVE — ENVIRONMENT BLOCKED |
| **5.1** | M-5 | Add Math/Formal Pack #2 and prove substrate generality | Zero diffs under `vanguard/packages/{domain,kernel}/`; contract, trajectory, and exterior-evidence parity with Pack #1 | M-4 | PLANNED |
| **5.2** | M-5 | Produce exact attributable T0 witness memo and finish post-foundation consolidation | RF-52–RF-53 and RF-34–RF-37 green; memo key binds subject, inputs, environment, checker, toolchain, assurance, and policy version | Sprint 5.1 | PLANNED |
| **6.1** | M-6 | Mediate `agent.spawn` as an S0–S12 effect with attenuated child authority and budget | RF-55–RF-59 plus RF-26 green; absent grant denies; depth and selectors never widen; TCB remains within budget | M-5 | PLANNED |
| **7.1** | M-7 | Measure selector independence and WAL contention before enabling concurrency | Measurement ADR records calls, envelopes, bytes, retries, contention, critical path, and cost per signed pass; I-11 remains until ratification | M-6 | PLANNED |
| **7.2** | M-7 | Activate bounded worker pool and alpha↔delta Pareto routing | RF-46–RF-48 green; no duplicate or unknown effect; claims and leases survive cold continuation | Sprint 7.1 | PLANNED |
| **8.1** | M-8 | Express debate, critic/reviser, bounded-tree, and evolutionary topologies through manifests | RF-65 green with zero kernel or episode-engine diff; RF-66 universal-loop challenge adjudicated | M-7 | PLANNED |
| **9.1** | M-9 | Add rebuildable hybrid retrieval, evidence-ranked skills, and macro candidate laboratory | RF-77 and RF-67–RF-68 green; index rebuilds from immutable artifacts; macro selector hull remains least privilege | M-8 | PLANNED |
| **10.1** | M-10 | Add governed Active-Inference belief/policy loop and reversible promotion | RF-69–RF-70 green; prediction precedes observation; exact paired McNemar, A/A floor, effect interval, signed evidence, human pointer, and rollback all pass | M-9 | PLANNED |

---

## Developer Implementation Briefs

These briefs describe the smallest acceptable mechanism. They do not open queued work; a sprint
moves to [`sprint_active.md`](sprint_active.md) only after its dependency gate is objectively green.

### Sprint 3.1 — Canonical composition

- **Problem:** fixed role/path manifests cannot express repeated SPI instances or typed topology,
  and multiple parsers can disagree about authority or identity.
- **Build:** one versioned reader normalizing supported old rows and `/2`; immutable component and
  binding values; resolver and validator; one JCS identity preimage containing nodes, complete edge
  set, refs/digests, interfaces, config, isolation, ceilings, profiles, and entrypoints.
- **Core invariant:** composition produces addresses, never runtime scheduling.
- **Gate:** RF-28–RF-33, RF-46, RF-73–RF-74, RF-76 plus unchanged kernel/episode-engine diffs.

### Sprint 3.2 — Plugin lifecycle and cells

- **Problem:** untrusted plugin code needs attributable lifecycle and bounded calls without another
  event writer or authority path.
- **Build:** registry-owned FSM/events/projection; common typed RPC semantics; direct dispatch only
  for explicitly granted `in_process`; UDS process cell otherwise; timeout, method allowlist,
  selector ceiling, log isolation, process cleanup, fault-to-retire path.
- **Core invariant:** registry controls lifecycle; kernel controls grants; evaluator remains exterior.
- **Gate:** RF-34–RF-44 and normal/fault echo traces reduce to the expected durable state.

### Sprint 3.3 — Convergence proof

- **Problem:** deleting a fork before parity or retaining a compatibility implementation both leave
  ambiguous authority.
- **Build:** migrate every caller/import/test/package/workflow/navigation reference, then remove the
  fork atomically. Historical references remain only as history, never instructions.
- **Gate:** RF-45/NOVA-4, no duplicate parser/writer/reducer/dialect, full CI and architecture gates.

### Sprint 4.1 — Honest foundation run

- **Problem:** hermetic components do not prove the substrate can complete one real task honestly.
- **Build:** preregister task/oracle/environment; start one run through canonical composition; invoke
  a real model; dispatch all effects through S0–S12; evaluate externally; persist WAL and trajectory;
  reconstruct in a fresh process. Export a cassette only after the real run as regression material.
- **Pseudocode:** `preregister -> compose -> run -> signed evaluate -> close -> cold replay -> audit`.
- **Gate:** all nine evidence rows above share one run/lineage; no manual repair, fake, stitch, host
  fallback, or copied verdict. Failure is evidence, not permission to substitute.

### Sprint 5.1 — Pack #2 generality

- **Problem:** one coding pack can hide domain coupling in the substrate.
- **Build:** Math/Formal pack as a client of existing ports: manifest, prompt/context policy, tools,
  checker registry, fixtures, and exterior evaluator. Add no SPI and change no domain/kernel code.
- **Gate:** zero diff under `vanguard/packages/{domain,kernel}/`; same composition, dispatch, ledger,
  trajectory, recovery, and signed-evidence contracts as Pack #1.

### Sprint 5.2 — Attributable witness and consolidation

- **Problem:** a result without exact subject/input/toolchain/policy binding is not reusable evidence.
- **Build:** content-addressed T0 memo binding subject, inputs, environment, checker, toolchain,
  assurance, policy version, result, signature, and invalidation conditions. Derive eligibility from
  evidence; never accept a promotability flag from input.
- **Gate:** RF-34–RF-37 and RF-52–RF-53; absent, forged, stale, or mismatched evidence is ineligible.

### Sprint 6.1 — Mediated delegation

- **Problem:** engine-owned spawn is implicit authority and cannot conserve parent budget/lineage.
- **Build:** represent target harness as selector `agent://spawn/harness/<D_H>`; submit spawn as an
  ordinary effect; durably append intent before child creation; attenuate selectors, handles,
  budget sublease, depth, and turns; ledger child start/return/failure/cancellation and reconcile.
- **Pseudocode:** `request -> S0..S8a intent -> create child -> child receipts -> S9..S12 settle`.
- **Gate:** RF-55–RF-59 and RF-26; absent grant denies, child is a strict subset, cold continuation
  preserves lineage, no direct agency subprocess, and TCB stays within budget.

### Sprint 7.1 — Measure before concurrency

- **Problem:** concurrency without workload and WAL measurements can duplicate effects or cost more
  than it saves.
- **Build:** measurement-only instrumentation for selector conflicts, calls, envelopes, bytes, WAL
  waits/retries, critical path, cost, and signed-pass outcome. Run sequential baselines and proposed
  worker bounds under fixed identities.
- **Gate:** accepted measurement ADR and reproducible report; I-11 remains active.

### Sprint 7.2 — Bounded concurrency and Pareto profiles

- **Problem:** safe independence and durable work ownership are required before parallel effects.
- **Build:** bounded worker pool over explicit independence groups; WAL-backed claim/lease state;
  idempotency-key duplicate rejection; unknown selector means conflict; alpha–delta profile chooses
  only among feasible actions and cannot alter authority.
- **Pseudocode:** `partition -> durable claim -> dispatch independently -> settle/reconcile -> join`.
- **Gate:** RF-46–RF-48 plus crash/retry/contention tests and measured improvement. Lift I-11 only by
  explicit governance after evidence.

### Sprint 8.1 — Framework builder

- **Problem:** debate, critic/reviser, trees, and evolution must not become kernel modes.
- **Build:** SDK/CLI emits ordinary manifests, profiles, plugin calls, and mediated spawn policies;
  bound topology by depth/turns/budget; keep one universal episode mechanism.
- **Gate:** RF-65 reference topologies run with zero kernel/episode-engine change; RF-66 challenge is
  adjudicated with evidence, not a topology-specific runtime.

### Sprint 9.1 — Retrieval, skills, and macro laboratory

- **Problem:** derived indexes become hidden state, and learned macros can silently widen authority.
- **Build:** rebuildable hybrid index from immutable artifacts; source-digest citations; evidence-
  ranked skills; macro candidates whose selector is the least-privilege hull of constituent effects;
  adversarial replay before promotion.
- **Gate:** RF-77 rebuild equality, held-out retrieval lift, RF-67–RF-68 least-privilege/dispatch
  proof, published scale measurements, and explicit five-SPI review.

### Sprint 10.1 — Governed meta-cognition

- **Problem:** adaptive policy without preregistered predictions and exact comparison becomes
  unauditable self-modification.
- **Build:** ledger prediction before observation; fit beliefs with VFE; rank feasible policies with
  EFE; attribute credit to signed trajectories; propose promotion through governance with immutable
  pointer and rollback target. Keep evaluation exterior.
- **Gate:** RF-69–RF-70; paired exact McNemar, A/A floor, effect interval, Pareto safety, signed
  evidence, human approval pointer, and tested rollback. No automatic irreversible promotion.

### Common gate sequence

```text
targeted falsifier -> affected package suites -> full production suites
-> codegen/schema -> boundaries/TCB/domain/isolation/duplication
-> metadata/links/stale paths/IDs/secrets -> evidence recorded on active board
```
