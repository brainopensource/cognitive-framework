---
id: aether-masterplan-todo
class: execution-masterplan
authority: planning-handoff
status: final-execution-handoff
owner: project-owner-project-lead-tech-lead
version: "1.1.0"
last_verified: 2026-08-25
baseline_commit: f9d7ceb257e8e2c7d6014bd0a29604ffcd89ee0e
project: AETHER v0.7.0 Higgs Update
canonical_authority:
  - VISION.md
  - docs/SPEC.md
  - docs/01_law/
  - accepted ADRs
subordinate_to:
  - VISION.md
  - docs/SPEC.md
  - accepted ADRs
commit_policy: >
  This revision is the final external execution handoff for Phase 0. It is subordinate to the
  constitutional stack and must not coexist in the repository as a second canonical plan. The
  Tech Lead applies its corrections to the canonical documents. If Leadership later wants this
  file versioned, it must replace/consolidate DEVELOPMENT_PLAN.md in one explicit governance
  change; the superseded planning document must no longer remain active.
---

# AETHER — MASTER PLAN / TODO (REV 1 — FINAL CORRECTED HANDOFF)
## From Phase-1 Concept Lock to M-8 Implementation

## 0. Purpose

This document consolidates the complete working decision reached after:

1. the AETHER v0.7.0 Vision / Law Zero lock;
2. the Phase-1 architectural and scientific assessment;
3. ADR-0097 foundation review and concept lock;
4. the Phase-2 implementation package;
5. the independent corrective review of Phase 1 + Phase 2;
6. the repository audit at commit `f9d7ceb257e8e2c7d6014bd0a29604ffcd89ee0e`;
7. the correction of compatibility, provenance, reproducibility, TCB, budget, privacy and activation-gate defects;
8. the decision to execute the program with two independent senior engineering squads.

The objective is not to create another architecture.

The objective is to define **how to move from the accepted theory to production code with minimal central coordination**, while preserving:

- constitutional authority;
- architectural invariants;
- falsifiability;
- scientific evidence quality;
- compatibility;
- independent squad execution;
- large autonomous work packages;
- milestone-level integration gates;
- PR review against specifications rather than line-by-line implementation control.

The operating principle is:

> **Leadership owns WHAT must remain true. Senior engineers own HOW to implement it.**

Leadership should not micro-design classes, algorithms, private helpers, local refactors or internal decomposition unless those choices affect a constitutional boundary, public contract, migration, evidence claim, security property or milestone gate.

## 0.1 Revision-1 disposition

This revision preserves the architecture, roadmap and work-package intent of v1.0.0. It corrects
only operational inconsistencies found during the final Phase-0 audit:

- it removes dependence on unavailable review artifacts;
- it makes the canonical-document correction set explicit;
- it distinguishes independent package development from integrated milestone acceptance;
- it maps all work to exactly two Senior developers plus Leadership gates;
- it freezes shared contracts, fixtures, hotspots and merge order before parallel work starts;
- it resolves strict schema versioning, evidence failure semantics, resource semantics, goal
  privacy and retention vocabulary;
- it makes the activation sequence mechanically unambiguous.

No foundational concept, layer boundary or milestone order is reopened by this revision.

---

# 1. Final program decision

## 1.1 Architecture

**APPROVED AND PRESERVED.**

No evidence requires:

- a foundational rewrite;
- a Kernel/Agency/Runtime reorganization;
- a second runtime;
- a new mandatory metacognition layer;
- a workflow-engine architecture;
- a change to the accepted milestone ordering.

The accepted dependency structure remains:

`domain ← ports ← kernel ← agency ← runtime → adapters`

with packs/clients outside and above the generic substrate.

The accepted milestone order remains:

**M-4 → M-5a → {M-5b ∥ M-6} → M-6.5 → M-7 → M-8**

M-9 and later remain outside the implementation horizon except as stress-test context.

## 1.2 Phase 1

**~95% preserved.**

The Phase-1 thesis is considered correct. The corrective work changes mainly proof semantics, TCB measurement and qualification status, not the architecture.

## 1.3 Phase 2

**~80–85% preserved.**

The Phase-2 direction, workstreams and milestones are retained, but execution must use the
contracts reconciled from C-01…C-12 because the supplied Phase-2 documents contain objective
contract and evidence inconsistencies.

## 1.4 Production implementation

**NO-GO until Phase 0 activation gates clear.**

After Phase 0 is complete, implementation becomes GO without another foundational architecture review.

---

# 2. Complete source and document registry

This section exists so that no engineer has to guess which artifact is source, review, decision, plan, specification or handoff material.

## 2.1 Original Project Source package reviewed as one integrated package

The original Phase 1 + Phase 2 source set contains:

1. `VISION.md`
2. `AETHER_PHASE1_ASSESSMENT.md`
3. `ADR-0097-phase1-foundation-review-and-concept-lock.md`
4. `ARCHITECTURE_DELTA.md`
5. `BACKLOG.md`
6. `MILESTONE_SPECS.md`
7. `SPEC_M4_TRAJECTORY_CAPTURE.md`
8. `SPEC_M5A_EVENT_DERIVED_AGENT.md`
9. `DEVELOPMENT_PLAN.md`
10. `SPEC_M5B_M6.md`
11. `SPRINT_UPCOMING.md`
12. `SPEC_M65_M7_M8.md`
13. `SPRINT_ACTIVE.md`

The audited repository baseline is:

`brainopensource/cognitive-framework@f9d7ceb257e8e2c7d6014bd0a29604ffcd89ee0e`

dated 2026-08-25.

## 2.2 Required Phase-0 handoff package

The executable handoff contains:

1. `VISION.md`
2. `AETHER_PHASE1_ASSESSMENT.md`
3. `ADR-0097-phase1-foundation-review-and-concept-lock.md`
4. `ARCHITECTURE_DELTA.md`
5. `BACKLOG.md`
6. `MILESTONE_SPECS.md`
7. `SPEC_M4_TRAJECTORY_CAPTURE.md`
8. `SPEC_M5A_EVENT_DERIVED_AGENT.md`
9. `DEVELOPMENT_PLAN.md`
10. `SPEC_M5B_M6.md`
11. `SPRINT_UPCOMING.md`
12. `SPEC_M65_M7_M8.md`
13. `SPRINT_ACTIVE.md`
14. `masterplan_todo_rev1.md`

`masterplan_todo_rev1.md` carries the final corrective execution register C-01…C-12 and the
two-Senior operating model. A separately distributed `LEADERSHIP_CORRECTIVE_REVIEW.md`,
`PACKAGE_MANIFEST.md` or ZIP may be retained as audit evidence if available, but none is a
prerequisite for execution and none is an architectural authority.

## 2.3 Canonical repository documents that must be reconciled

The Phase-0 documentation convergence must update the canonical homes that are affected by the ratified decisions, including where applicable:

- `VISION.md`
- `AGENTS.md`
- `README.md`
- `docs/SPEC.md`
- `docs/01_law/EVIDENCE.md`
- `docs/01_law/MEASUREMENT.md`
- `docs/01_law/EXTENSIBILITY.md`
- `docs/01_law/RUNTIME.md`
- other affected law leaves only when explicitly named by the ratified ADR edit set
- `docs/02_decisions/INDEX.md`
- `docs/03_execution/milestones.md`
- `docs/03_execution/sprint_active.md`
- `docs/04_architecture/glossary.md`
- `docs/05_contracts/events.md`
- `docs/05_contracts/trajectories.md`
- affected schemas under `schemas/mhf/`
- affected falsifier and governance references
- `ARCHITECTURE_DELTA.md`
- `BACKLOG.md`
- `MILESTONE_SPECS.md`
- `SPEC_M4_TRAJECTORY_CAPTURE.md`
- `SPEC_M5A_EVENT_DERIVED_AGENT.md`
- `DEVELOPMENT_PLAN.md`
- `SPEC_M5B_M6.md`
- `SPRINT_UPCOMING.md`
- `SPEC_M65_M7_M8.md`
- `SPRINT_ACTIVE.md`

Do not create duplicate canonical definitions.

One concept must have one canonical home.

## 2.4 ADR registry

### Historical / already-established authority

- `ADR-0095` — Vision as Law Zero and roadmap reconciliation.
- `ADR-0069` through `ADR-0095` — historical provenance; immutable. Supersede when necessary, never rewrite history.

### Ratification / correction set

- `ADR-0096` — constitutional refinement that must be ratified in corrected form.
- `ADR-0097-phase1-foundation-review-and-concept-lock.md` — the supplied source is v0.1.0
  `proposed`; Phase 0 must materialize the corrected ratification candidate as v0.2.0 and the
  Director must accept it before it is cited as binding authority.

### New ADRs planned by the execution roadmap

- `ADR-0098` — M-5a substrate change window.
  Owns:
  - `mhf.event/2`;
  - final M-5a semantic kind roster;
  - vocabulary convergence/deprecation;
  - execution contracts;
  - checkpoint contract;
  - dual-read/single-write migration;
  - `M-5-BASE` exit conditions.

- `ADR-0099` — M-7 concurrency disposition.
  Decision based on M7-01 evidence:
  - implement;
  - simplify;
  - or cancel advanced concurrency.

- `ADR-0100` — M-8 skill/promotion lifecycle.
  Owns:
  - composition-level promotion path;
  - regression-aware promotion;
  - rollback;
  - decision whether deprecated lifecycle kinds are reintroduced or represented through typed claims.

## 2.5 Review and architecture-correction artifacts

- `AETHER_PHASE1_ASSESSMENT.md`
  - original architectural/scientific assessment;
  - confirms foundation;
  - identifies constitutional fork, M4-04 incompleteness, event drift, TCB gap and RF-95 NO-GO.

- `ARCHITECTURE_DELTA.md`
  - current-state → target-state delta register;
  - D-01…D-20;
  - must reflect the corrected contracts, not the superseded original assumptions.

- `DEVELOPMENT_PLAN.md`
  - implementation bridge from accepted decisions to modules, contracts, migrations, tasks, tests and gates.

- `BACKLOG.md`
  - work inventory and dependency model.

- `MILESTONE_SPECS.md`
  - canonical delivery order and exit-gate model for M-4 through M-8.

- `SPRINT_ACTIVE.md`
  - sole implementation authorization when actually ACTIVE.

- `SPRINT_UPCOMING.md`
  - next-window preparation only; never current authorization.

- `masterplan_todo_rev1.md`
  - final external execution handoff;
  - owns no constitutional concept;
  - supplies the correction and delegation instructions to be applied to the canonical files.

---

# 3. Authority hierarchy and immutable rules

All implementation and review decisions must obey the following precedence:

1. **VISION / Law Zero**
2. **SPEC and Law**
3. **Accepted ADRs**
4. **Contracts / Protocols / Schemas**
5. **Milestones**
6. **Active Sprint**
7. **Communication / orientation documents**

A lower document cannot invalidate a higher authority.

A stale lower document is a reconciliation problem, not counter-evidence against the Vision.

Historical ADRs remain immutable.

`SPRINT_ACTIVE.md` is the only current implementation authorization board.

The Master Plan never overrides these rules.

---

# 4. Concepts that are now frozen

The following concepts are considered sufficiently reviewed and should not be reopened during normal implementation.

## 4.1 Event

A durable causal fact.

Events own causal truth and provenance identity.

Events do not own large content.

## 4.2 Artifact

Content-addressed immutable larger content.

Examples include prompts, model outputs, context bundles, snapshots, patches, verification artifacts and checkpoint state.

Artifacts do not replace events.

## 4.3 Projection

Derived state computed from the causal record.

A projection is not a second source of truth.

## 4.4 Agent

Conceptually:

**Identity + Policy + Event-Derived Projection + Execution Boundary**

An in-memory object may exist as a convenience, but it must not become authoritative persistent state.

## 4.5 Composition versus trajectory

Composition defines the available space of capabilities and policy/configuration.

Trajectory records what actually happened.

AETHER must not collapse these concepts into a rigid workflow DAG.

## 4.6 Kernel

The Kernel is:

- small;
- domain blind;
- trusted;
- responsible for generic admissibility/authority/resource invariants.

It must never gain:

- coding semantics;
- research semantics;
- topology semantics;
- metacognition semantics;
- plugin behavior;
- agent-specific verbs;
- special cases for `agent.spawn`.

## 4.7 Runtime

Runtime remains the single concrete composition seam.

It owns concrete lifecycle, wiring, recovery, runtime instrumentation, profile resolution, event emission mechanisms, scheduling mechanism and delegation mechanism.

It must not become a second Kernel.

## 4.8 Agency

Agency owns generic observation/proposal/context/episode mechanics.

Agency must not import Runtime, adapters or packs.

## 4.9 Packs

Domain behavior belongs in packs.

Coding is the first laboratory, not the ontology of the framework.

## 4.10 Generality

Generality must be **falsified or supported experimentally**, not asserted from design elegance.

M-5b exists to try to break the generic substrate.

## 4.11 Metacognition

Metacognition is policy/reducer/plugin behavior over ordinary observations and ordinary proposals.

It receives no special Kernel authority.

## 4.12 Self-improvement

The accepted separation is:

**execution → trajectory → analysis → candidate → independent evaluation → promotion / rollback**

Generator, evaluator and promoter remain distinct authorities.

---

# 5. Corrective decisions to ratify and reconcile before implementation

These corrections are final Phase-0 instructions, not independent constitutional authority.
They must be incorporated into the appropriate accepted ADRs, contracts, schemas, specs and
execution boards before production coding. Once reconciled, the canonical repository documents
are the authority used by PR review.

## C-01 — Runtime-owned exact model I/O capture

The real provider-call seam is:

`runtime/session.py::_LayeredOperator.propose`

Prompt/provider input must be captured immediately before the model call after the final bundle is assembled.

Raw structured model output must be captured immediately after the model returns and before downstream interpretation materially changes it.

Agency owns only generic context-provenance protocols.

Do not create an Agency → Runtime dependency.

## C-02 — Evidence capture must distinguish fail versus degrade

Scientific evidence cannot silently disappear.

Rules:

- evidence-ledger append failure is fatal;
- artifact failure is fatal when `capture.required=true`;
- artifact failure may degrade when `capture.required=false` only if `capture_incomplete` is durably recorded;
- a degraded capture run is non-evidentiary;
- a degraded run cannot satisfy RF-95 or promotion evidence.

The Agency protocol must not swallow every sink exception indiscriminately. The corrected
contract distinguishes:

- `EvidenceCaptureRequiredError`: propagates and terminates the evidentiary run;
- optional artifact-capture failure: Runtime first appends `capture_incomplete`, then returns a
  non-evidentiary degradation outcome;
- failure to append either the evidence fact or the degradation fact: fatal.

Agency remains Runtime-blind by depending only on a generic protocol/error contract.

## C-03 — Strict schema versioning

The original assumption that new fields could be added to strict `/1` schemas was incorrect.

Therefore:

- `mhf.trajectory/1` is frozen;
- M-4 introduces `mhf.trajectory/2`;
- readers dual-read `/1` and `/2`;
- production writers single-write `/2`.

The same rule applies to execution profiles:

- `mhf.execution-profile/1` is frozen;
- `/2` introduces corrected retention / evidence-capture semantics;
- historical `/1` identity is never rewritten.

Compatibility means new readers can read old data.

Compatibility does **not** mean old strict validators must accept a new schema.

## C-04 — RF-100 must separate prerequisite from proof

WAL presence is not proof of full cold reconstruction.

Pins are not proof of semantic replay.

The corrected representation separates capability from verification:

- `state_reconstruction.capability ∈ {none, from_checkpoint, full_cold}`;
- `state_reconstruction.verification ∈ {unverified, verified}`;
- `semantic_replay.capability ∈ {unpinned, pinned}`;
- `semantic_replay.verification ∈ {unverified, verified}`.

Any `verified` value requires an immutable executed receipt bound to the run, reducer/schema pins,
input history/checkpoint digest and reconstructed output/state digest. WAL presence may establish
`full_cold` capability but leaves verification `unverified`; pins may establish `pinned`
capability but leave semantic replay `unverified`. Other reproducibility dimensions retain their
ratified domains and must likewise avoid `verified_*` language without executed receipts.

## C-05 — Correct resource semantics

The additive conserved budget dimensions are exactly:

- `usd_micros`
- `millis`
- `tokens`
- `bytes`

`depth` and `turns` are structural ceilings.

Remove `charged_millis` from the target contract.

RF-57 must test four-dimensional additive conservation plus independent depth/turn enforcement.

## C-06 — Goal content stays out of the ledger

`GoalDeclared` stores goal identity/reference, not raw goal text.

Use:

- `goalDigest`
- optional `goalArtifact`

The artifact may be dereferenced only with digest verification.

## C-07 — Retention vocabulary is normalized

Execution retention vocabulary:

- `digests_only`
- `standard`
- `full`

Blob garbage collection / legal-hold semantics are a separate M-8 concern.

Content-capture/privacy policy remains separate from retention.

## C-08 — RF-97 computes the real TCB automatically

The TCB is not equivalent to the `kernel/` directory.

RF-97 must:

- start from production kernel modules;
- parse imports;
- recursively follow in-repository executable dependencies;
- calculate transitive trust closure;
- measure the actual closure;
- fail on unexpected trust-surface growth.

Current known domain modules are regression assertions, not a hard-coded discovery mechanism.

## C-09 — UDS qualification remains unresolved until qualified CI says otherwise

The two RF-43 UDS lifecycle tests are not green merely because the local audit environment could not run them.

They must run in a qualified Linux environment with AF_UNIX support.

A failure creates a blocking defect.

Do not weaken production semantics to accommodate a restricted audit environment.

## C-10 — Metadata and authorization are normalized

Planning/spec documents must carry explicit:

- id;
- class;
- authority;
- status;
- owner;
- version;
- last_verified.

`SPRINT_ACTIVE.md` is non-authorizing until the activation receipts exist.

## C-11 — Two-Senior ownership and acceptance semantics

There are exactly two production developers:

- Senior Dev A — Runtime / execution / causal infrastructure;
- Senior Dev B — contracts / projections / verification / experiments.

`GOV`, `RT`, `AG`, `DM`, `SC`, `TL`, `PK`, `TS` and `LB` remain responsibility classes, not
additional people. The Tech Lead assigns every such responsibility to A, B or Leadership before
activating a work package.

Parallel development means both Seniors can work from the same baseline using frozen contracts,
fixtures and stubs without consuming the other's branch. It does not mean that a consumer's final
integrated acceptance can precede its producer. Therefore:

- `PACKAGE_READY` means the package passes its isolated contract suite;
- `MERGED` means its declared merge order has completed;
- `GATE_ACCEPTED` means the integrated milestone suite and falsifiers pass.

Only `GATE_ACCEPTED` closes a milestone.

## C-12 — Capture authorization and privacy

Retention specifies how long authorized content is kept; it does not authorize capture.
Before raw prompt, model output, context bundle, snapshot, patch or report bytes are persisted,
Runtime must resolve the applicable content-capture policy and secret/sensitivity handling.

- unauthorized raw capture falls back to an allowed digest-only fact or fails closed when
  `capture.required=true`;
- secrets and prohibited sensitive fields are redacted or rejected before blob persistence;
- the applied capture-policy identity/version is recorded in provenance;
- privacy degradation cannot be represented as complete scientific evidence.

---

# 6. Operating model: maximum Senior autonomy, minimum leadership work

## 6.1 Leadership responsibility

Leadership defines only:

- target outcome;
- architectural boundary;
- public contract;
- required migration;
- required falsifier;
- required evidence;
- Definition of Done;
- forbidden changes;
- integration gate.

Leadership should not normally prescribe:

- private class decomposition;
- helper function layout;
- local algorithms;
- internal data structures;
- refactor sequence;
- test helper implementation;
- naming of private symbols;
- commit decomposition;
- local performance optimizations.

## 6.2 Senior developer responsibility

Each Senior is explicitly authorized to:

- design the internal implementation;
- add private modules/helpers;
- refactor code inside the allowed ownership surface;
- improve local abstractions;
- add tests beyond the minimum;
- optimize implementation;
- select algorithms;
- remove local duplication;
- create internal adapters/facades where consistent with layer law;
- propose spec improvements when evidence shows a defect.

They must not silently change architecture.

## 6.3 Escalation triggers

A Senior must return a decision to Tech Lead before merging if the implementation requires any of the following:

1. Kernel semantic change.
2. New upward dependency or violation of the dependency lattice.
3. New concrete composition seam outside Runtime.
4. New public wire schema not already authorized.
5. In-place mutation of a frozen schema.
6. New event kind outside an accepted kind package.
7. Change to writer ownership / authority semantics beyond the accepted contract.
8. Weakening fail-closed behavior.
9. Weakening a falsifier or acceptance gate.
10. Historical ADR edit.
11. New canonical architecture document.
12. Change to the M-4→M-8 dependency order.
13. New domain concept inside Kernel/Agency generic substrate.
14. Evidence claim stronger than what executed evidence proves.
15. Cross-squad branch dependency that was not part of the milestone integration plan.

Everything else is primarily the Senior's implementation decision.

---

# 7. Two-squad organization

## 7.1 Squad A — Senior Dev A

Permanent charter:

**Execution / Runtime / Causal Infrastructure**

Typical ownership:

- runtime execution;
- artifact production;
- event emission mechanisms;
- runtime model I/O instrumentation;
- migrations on runtime write paths;
- delegation;
- topology lowering;
- runtime scheduler mechanism;
- memory/retrieval infrastructure.

## 7.2 Squad B — Senior Dev B

Permanent charter:

**Contracts / Projection / Verification / Generality / Learning**

Typical ownership:

- schemas and contract verification;
- projections;
- reproducibility/falsifiers;
- TCB tooling;
- generality pack;
- scientific evaluation;
- confidence/progress measurement;
- concurrency evidence;
- skill evaluation/promotion/rollback.

## 7.3 Independence rule

The two Seniors work from the **same approved baseline**.

They do not consume each other's unmerged branches.

The allowed synchronization point is:

**milestone integration gate**

not day-to-day implementation.

A required shared interface is frozen in the specification before the work package is opened.

The two packages may be implemented against:

- frozen schemas;
- protocols;
- fixtures;
- golden vectors;
- mocks/fakes;
- interface stubs.

A Senior should not be blocked waiting for the other Senior's private implementation.

Independence is enforced at development time, not misrepresented as absence of architectural
dependencies. When one package produces behavior that the other verifies, the verifier develops
against the frozen Contract Kit and golden fixtures, reaches `PACKAGE_READY`, and completes its
integrated checks after the producer merges in the declared order.

No milestone is opened until its ownership matrix names:

- every shared public contract;
- every shared file/hotspot;
- the sole owner of each hotspot;
- allowed fixture/stub boundaries;
- merge order;
- package-local and integrated acceptance commands.

---

# 8. Work-in-progress rules

Each Senior has:

**WIP = 1 large work package**

A large work package may contain multiple original backlog IDs, but it has one coherent outcome and one PR/PR-series boundary.

Do not give a Senior five disconnected cards.

The Senior may internally break the package into commits/sub-PRs, but the Project Board tracks the large block.

Board states:

- `BLOCKED`
- `READY`
- `IN_PROGRESS`
- `PR_OPEN`
- `REVIEW`
- `PACKAGE_READY`
- `MERGED`
- `GATE_ACCEPTED`

---

# 9. Leadership Phase 0 — Constitutional Convergence

This is deliberately small and must happen before the two production squads begin.

## PH0-00 — Adopt this handoff and prevent parallel planning authority

Owner:

**Project Owner + Tech Lead**

Decision:

- use `masterplan_todo_rev1.md` as the final external correction/execution handoff;
- keep it outside the repository during convergence;
- apply its decisions to existing canonical documents;
- do not commit `masterplan_TODO.md` and this revision as two active plans;
- if later versioned, consolidate it into/replacement of `DEVELOPMENT_PLAN.md` through one
  explicit governance change.

Exit:

- one active planning hierarchy and no parallel authority.

## PH0-01 — Ratification package

Owner:

**Project Owner + Engineering Director / Tech Lead**

Actions:

- materialize and ratify corrected `ADR-0096 v0.4.0`;
- revise the supplied `ADR-0097 v0.1.0 proposed` into the corrected `v0.2.0` candidate and ratify it;
- preserve ADR-0069…0095 as immutable historical provenance;
- update `docs/02_decisions/INDEX.md`;
- record the correct RF-96…RF-100 allocations.

Exit:

- accepted ADR states;
- no unresolved authority fork.

## PH0-02 — Atomic canonical documentation reconciliation

Owner:

**Tech Lead / Project Lead**

Apply the ratified deltas to the existing canonical homes.

Mandatory review targets include:

- `VISION.md`
- `docs/SPEC.md`
- `docs/01_law/EVIDENCE.md`
- `docs/01_law/MEASUREMENT.md`
- `docs/01_law/EXTENSIBILITY.md`
- `docs/03_execution/milestones.md`
- `docs/03_execution/sprint_active.md`
- `docs/04_architecture/glossary.md`
- `docs/05_contracts/events.md`
- `docs/05_contracts/trajectories.md`
- `AGENTS.md`
- `README.md`
- `ARCHITECTURE_DELTA.md`
- `BACKLOG.md`
- `MILESTONE_SPECS.md`
- `SPEC_M4_TRAJECTORY_CAPTURE.md`
- `SPEC_M5A_EVENT_DERIVED_AGENT.md`
- `DEVELOPMENT_PLAN.md`
- `SPEC_M5B_M6.md`
- `SPRINT_UPCOMING.md`
- `SPEC_M65_M7_M8.md`
- `SPRINT_ACTIVE.md`

The reconciliation must remove every superseded execution assumption, including:

- mutation of strict `mhf.trajectory/1` or `mhf.execution-profile/1`;
- blanket swallowing of required evidence-capture failures;
- `charged_millis` as a resource dimension;
- raw goal content as ledger truth;
- mixed `digests-only` / `digests_only` vocabulary;
- staffing that implies `dev-C` or separate LB/TS/tooling people;
- `M-4 ACTIVE` before activation receipts exist;
- any milestone ordering that serializes M-5b before M-6.

Rules:

- no archive edits;
- no duplicate architecture definitions;
- no new review documents committed merely for narrative;
- link/governance/secret/document topology checks green.

## PH0-03 — Freeze the M-4 Contract Kit and ownership matrix

Owner:

**Tech Lead, reviewed by Dev A and Dev B**

The Contract Kit is a small pre-implementation artifact set, not application logic. It freezes:

- `mhf.execution-profile/2` and `mhf.trajectory/2` schemas;
- dual-read/single-write rules;
- provenance/artifact records used across the A/B boundary;
- typed evidence failure/degradation behavior from C-02;
- RF-100 state domains and receipt requirements;
- `digests_only | standard | full` retention vocabulary;
- content-capture/privacy policy from C-12;
- golden vectors, fixtures, stubs and package-local acceptance commands;
- M-4 ownership/hotspot matrix and merge order.

M-4 ownership freeze:

| Surface | Sole owner |
|---|---|
| `runtime/profiles.py`, `runtime/reproducibility.py`, `runtime/trajectory.py`, trajectory reader, profile/trajectory schemas | Dev B |
| `runtime/session.py`, `runtime/artifacts.py`, `runtime/provenance.py`, `runtime/wiring.py`, `runtime/root.py`, `runtime/ledger_emitter.py`, Agency provenance/compiler integration | Dev A |
| Canonical documents, activation board, RF-95 execution and milestone close | Tech Lead |

Any unavoidable overlap is resolved before activation by adding an interface seam, not by granting
both developers ownership of the same file.

Exit:

- both Seniors confirm they can develop from the same baseline without consuming the other's branch.

## PH0-04 — CV-003 Qualified Linux UDS lifecycle re-gate

Owner:

**Tech Lead / CI owner**

Required:

- RF-38…45 lifecycle qualification;
- explicitly run:
  - `test_echo_plugin_wire_lifecycle`
  - `test_child_crash_containment`
- Linux CI with AF_UNIX support;
- zero failure/error for the qualification set.

If green:

- record receipt.

If red:

- create blocking defect;
- authorize only the minimum lifecycle defect repair required by CV-003;
- rerun until green.

This exception is blocker repair, not feature/refactor authorization.

## PH0-05 — Activate the canonical sprint

Only after PH0-00 through PH0-04:

- promote canonical `SPRINT_ACTIVE.md` to actual ACTIVE authorization;
- open the two M-4 senior packages.

**Production coding starts here.**

---

# 10. Master execution board

## Phase 0

- [ ] PH0-00 Adopt rev1 as external handoff; prevent parallel planning authority
- [ ] PH0-01 Ratify corrected ADR-0096 + ADR-0097
- [ ] PH0-02 Reconcile canonical documentation atomically
- [ ] PH0-03 Freeze M-4 Contract Kit, ownership and merge order
- [ ] PH0-04 Clear qualified UDS lifecycle qualification
- [ ] PH0-05 Activate canonical S-P2-01

## M-4

### Squad A

- [ ] **A-M4 — Evidence Runtime & Causal Capture**

### Squad B

- [ ] **B-M4 — Scientific Contracts, Reproducibility & Verification**

### Leadership gate

- [ ] **G-M4 — Integration + RF-95**

## M-5a

### Squad A

- [ ] **A-M5A — Event Substrate Migration**

### Squad B

- [ ] **B-M5A — Event-Derived Projection & Substrate Falsifiers**

### Leadership gate

- [ ] **G-M5A — ADR-0098 exit + M-5-BASE**

## M-5b / M-6 parallel

### Squad A

- [ ] **A-M6 — Mediated Recursive Delegation**

### Squad B

- [ ] **B-M5B — Formal-Domain Generality Falsifier**

### Leadership gate

- [ ] **G-M5B-M6 — Parallel baseline acceptance**

## M-6.5

### Squad A

- [ ] **A-M65 — Meta-Control Runtime**

### Squad B

- [ ] **B-M65 — Confidence, Progress & Paired Evaluation**

### Leadership gate

- [ ] **G-M65 — Measured-value decision**

## M-7

### Squad A

- [ ] **A-M7 — Topology-as-Data & Scheduler Mechanism**

### Squad B

- [ ] **B-M7 — Concurrency Evidence & Topology Falsification**

### Leadership gate

- [ ] **G-M7 — ADR-0099 decision**

## M-8

### Squad A

- [ ] **A-M8 — Memory, Retrieval & Experience Infrastructure**

### Squad B

- [ ] **B-M8 — Skills, Evaluation, Promotion & Rollback**

### Leadership gate

- [ ] **G-M8 — Held-out lift + rollback + neutrality**

---

# 11. M-4 — Product proof and scientific trajectory capture

## 11.1 Milestone purpose

M-4 must produce:

1. one useful durable real-model coding run;
2. complete causal/scientific capture required for later experimentation;
3. correct versioned contracts;
4. proof-honest reproducibility semantics;
5. an accepted RF-95 evidence bundle.

No event-envelope or M-5a semantic-kind change belongs here.

---

## 11.2 A-M4 — Evidence Runtime & Causal Capture

Owner:

**Senior Dev A**

Original backlog coverage:

- M4-101
- M4-102
- M4-103
- runtime-side portions required to complete those contracts

Large-block objective:

> Build the complete production evidence-capture path from runtime execution to durable artifacts and provenance without changing the event envelope or Kernel semantics.

Required outcomes:

### Artifact production

Implement production `ArtifactWriter` behavior using existing blob-store ports/adapters.

Must support artifact roles including the M-4 evidence set such as:

- prompt;
- model output;
- context bundle;
- compaction input/output;
- snapshots/patches/reports where used.

Preserve:

- content-addressed identity;
- blob-first/event-second durability logic;
- no caller-supplied digest authority;
- no large content inline in events.

### Context / compaction provenance

Agency exposes only the generic provenance protocol.

Runtime owns the concrete evidence sink.

Preserve:

- no Agency → Runtime import;
- exact policy identity/digests;
- evidence failure semantics from C-02.

### Exact provider-call capture

Bind runtime capture to:

`runtime/session.py::_LayeredOperator.propose`

Capture:

- finalized model/provider input immediately before invocation;
- raw structured model output immediately after invocation;
- associated artifact identity/provenance.

Raw bytes are persisted only after the C-12 capture/privacy policy authorizes them. Retention is
not capture authorization.

### Cache provenance

Capture response-cache/cassette interaction when applicable.

Live no-cache execution may emit no cache claim.

### Dev A authority

Dev A may freely determine:

- internal runtime classes;
- helper modules;
- buffering strategy;
- dedup implementation;
- local abstractions;
- exact instrumentation helper API;
- test fixtures;
- local refactors.

Dev A may not:

- alter Kernel semantics;
- add new event kinds;
- modify frozen event-envelope schema;
- make Agency import Runtime;
- weaken evidence failure policy;
- change the approved public artifact/provenance contract without escalation.

### A-M4 package readiness

A-M4 reaches `PACKAGE_READY` when:

- artifact path is durable and tested;
- context/compaction claims are produced correctly;
- exact model input/output capture exists at the real runtime seam;
- cache provenance is correct;
- scientific capture failure semantics are enforced;
- legacy no-capture behavior remains valid where required;
- no envelope/kind diff exists;
- full package-specific tests are green.

Dev A develops against the frozen profile/trajectory protocols and fixtures in the M-4 Contract
Kit; A does not need Dev B's branch to reach `PACKAGE_READY`.

---

## 11.3 B-M4 — Scientific Contracts, Reproducibility & Verification

Owner:

**Senior Dev B**

Original backlog coverage:

- M4-104
- M4-105
- M4-106
- M4-107
- M4-108 as analysis-only lane where practical
- contract/falsifier tooling associated with M-4

Large-block objective:

> Build the versioned scientific contracts and verification machinery that define what a complete AETHER run means and prevent evidence claims from exceeding actual proof.

Required outcomes:

### Execution profile v2

Freeze:

`mhf.execution-profile/1`

Introduce:

`mhf.execution-profile/2`

Include corrected:

- retention;
- capture-required / evidence semantics;
- identity/preimage behavior.

Readers:

- dual-read `/1` and `/2`.

New production writers:

- single-write `/2`.

Historical identity must remain untouched.

### RF-100

Implement proof-honest reproducibility assessment.

Distinguish:

- prerequisites;
- actual executed verification.

Strong values require run-bound receipts.

### Trajectory v2

Freeze:

`mhf.trajectory/1`

Introduce:

`mhf.trajectory/2`

Carry the new:

- artifact index;
- provenance sections;
- reproducibility section.

Readers dual-read.

New writers single-write `/2`.

### Bench baseline

Freeze append/fold baseline required before M-5a.

### M7-01 early analysis lane

May begin analysis over available ledgers.

Must not implement concurrency.

### Dev B authority

Dev B may freely choose:

- schema helper design;
- reader architecture;
- verification receipt representation within the accepted contract;
- test/fuzz/golden-vector structure;
- benchmark implementation;
- internal reproducibility engine decomposition.

Dev B may not:

- mutate strict `/1` schemas in place;
- label prerequisite-only states as verified;
- alter the event envelope;
- change Kernel budget semantics;
- weaken RF-100.

### B-M4 package readiness

B-M4 reaches `PACKAGE_READY` when:

- profile `/2` migration is correct;
- trajectory `/2` migration is correct;
- old data still reads;
- new writers do not emit `/1`;
- RF-100 states match actual evidence;
- golden vectors pass;
- benchmark artifact is frozen;
- falsifier tests are green.

Dev B verifies artifact/provenance inputs with Contract-Kit golden fixtures; integrated RF-100
and trajectory acceptance occurs after A is merged.

---

# 12. G-M4 — Integration and RF-95

Owner:

**Tech Lead + independent reviewer**

This is not a developer feature package.

## 12.1 Integration review

Open both packages from the same activated baseline. When both are `PACKAGE_READY`, merge in this
order:

1. **B-M4 first**, because it owns the shared profile/trajectory contracts and readers;
2. **A-M4 second**, rebased on `main`, because it wires the production capture path to those
   contracts;
3. run the combined integration suite and promote both to `GATE_ACCEPTED` only together.

The M-4 ownership matrix forbids both branches from editing the same hotspot. A semantic conflict
returns to the Tech Lead; it is not resolved by cross-branch cherry-picking.

Review the combined system against:

- corrected `SPEC_M4_TRAJECTORY_CAPTURE.md`;
- `BACKLOG.md`;
- `MILESTONE_SPECS.md`;
- `DEVELOPMENT_PLAN.md`;
- architectural invariants.

No micro-review of private implementation style is required unless it creates correctness or maintainability risk.

## 12.2 RF-95 prerequisites

RF-95 remains NO-GO until:

- CV-003 receipt exists;
- A-M4 and B-M4 are merged in the declared order;
- both packages pass integrated acceptance;
- combined CI green;
- frozen live task/verifier exists;
- product execution uses the corrected profile `/2`;
- `retention=standard`;
- `capture.required=true`.

## 12.3 RF-95 evidence

Required evidence includes:

- real live-provider run;
- exactly one candidate;
- terminal `mhf.trajectory/2`;
- artifact index;
- model I/O capture;
- context/compaction/cache provenance;
- verifier receipt;
- workspace diff/result;
- WAL;
- fresh-process reconstruction receipt;
- proof-honest reproducibility vector;
- independent review.

Failure:

- preserve evidence;
- do not manually repair trajectory;
- M-4 stays open;
- create defect.

Success:

**M-4 CLOSED**

Then prepare/accept ADR-0098.

---

# 13. M-5a — Single substrate change window

Entry:

- M-4 CLOSED;
- RF-95 accepted;
- ADR-0098 accepted;
- M-4 benchmark frozen.

Purpose:

- move to event-derived agent semantics;
- version the event envelope;
- unify event vocabulary;
- add execution contracts;
- create AgentView;
- add checkpointed reconstruction;
- strengthen TCB measurement;
- create one post-window baseline.

Before opening A-M5A/B-M5A, ADR-0098 must freeze an M-5a Contract Kit containing the complete
event `/2` field table, final kind roster, payload schemas, writer-role matrix, execution-contract
shapes, checkpoint contract, golden fixtures and the ownership matrix below:

| Surface | Sole owner |
|---|---|
| event envelope, generated wire types, event parsing/vocabulary, semantic payload schemas/vectors, emitter ownership and `/2` writer cutover | Dev A |
| execution contracts, ledger/AgentView reducer semantics, checkpoints, RF-96/97/99/100 tooling | Dev B |
| ADR-0098, canonical docs, pin record and `M-5-BASE` tag | Tech Lead |

M-5a supports parallel package development but has ordered integration; it is not described as
two dependency-free implementations.

---

## 13.1 A-M5A — Event Substrate Migration

Owner:

**Senior Dev A**

Large-block objective:

> Execute the wire/runtime side of the one authorized substrate migration without changing Kernel semantics.

Coverage:

- `mhf.event/2`;
- dual-read/single-write event migration;
- writer authority fields;
- emitter cutover;
- vocabulary convergence;
- removal of `_V4_ONLY_KINDS`;
- deprecated-kind write rejection / historical-read support;
- semantic event-kind payload schemas, vectors and writer ownership;
- codegen/schema/vector integration;
- runtime write-path migration.

Constraints:

- Kernel semantic diff must remain zero;
- old ledgers are never rewritten;
- mixed-version chains must remain readable;
- schema is sole live event-kind authority after convergence;
- deprecated historical kinds remain readable;
- new event kinds only as authorized by ADR-0098.

Dev A owns internal migration mechanics.

Dev A does not own reducer/AgentView semantics, checkpoint implementation or RF-97 implementation.

Package readiness:

- mixed-version golden chain green;
- emitter writes only `/2`;
- vocabulary generated from schema;
- deprecated kinds rejected on write;
- old history reads;
- semantic kinds have accepted writer ownership/schemas/vectors;
- Kernel unchanged.

A-M5A is independent of B-M5A and must reach `PACKAGE_READY` without importing or cherry-picking
Dev B's branch.

---

## 13.2 B-M5A — Event-Derived Projection & Substrate Falsifiers

Owner:

**Senior Dev B**

Large-block objective:

> Build the event-derived execution model, projection/reconstruction layer and falsifiers proving that the migrated substrate is recoverable, bounded and honestly measured.

Coverage:

### Execution contracts

Implement the approved domain contracts for:

- `ExecutionScope`
- `LineageRef`
- `OperationRecord`

Correct resource model:

- additive `{usd_micros, millis, tokens, bytes}`;
- structural `depth`;
- structural `turns`.

Reject old/invalid budget semantics.

### AgentView

Build deterministic event-derived projection containing the accepted semantic continuation state.

Raw goal text must not become ledger truth.

Use:

- `goalDigest`;
- optional artifact reference.

### Checkpoints

Implement checkpointed projection reconstruction with:

- digest verification;
- version/pin verification;
- fail-to-cold-fold behavior;
- no new authority semantics.

### RF-96

Fresh-process reconstruction must prove that no process-local object is required.

### RF-97

Implement automatic transitive trusted import closure and multidimensional trust-surface metrics.

### RF-99

Verify authority provenance and role consistency for event `/2`.

### RF-100 current

A later current-state assessment may upgrade evidence only when executed verification receipts exist.

Dev B may freely design projection/checkpoint internals within the frozen contracts.

Package readiness:

- RF-96 green;
- RF-97 green with synthetic indirect-import tests;
- RF-99 green;
- RF-100 current does not overclaim;
- checkpoint/cold-fold parity green;
- corrupted checkpoint degrades safely;
- budget contract rejects `charged_millis` and structural dimensions inside additive costs.

B-M5A develops against ADR-0098 schemas and golden event fixtures. Its isolated reducer,
checkpoint and tooling suite may reach `PACKAGE_READY` in parallel; full mixed-chain and RF-99
acceptance occurs after A-M5A merges.

---

# 14. G-M5A — M-5-BASE

Owner:

**Tech Lead + Project Lead**

Merge order:

1. **A-M5A first** — establishes the event `/2` production substrate and generated types;
2. **B-M5A second** — rebases and validates projection/reconstruction against the real substrate;
3. only the combined green suite promotes both packages to `GATE_ACCEPTED`.

Run:

- full suite;
- migration tests;
- mixed replay;
- benchmark regression check;
- Kernel semantic diff;
- schema/codegen checks;
- falsifiers.

Then:

- update contracts/docs;
- record reducer/schema pins;
- mark ADR-0098 implemented;
- create exactly one tag:

**`M-5-BASE`**

This tag becomes the experimental control baseline for M-5b and M-6.

Do not continue changing substrate semantics casually after this tag.

---

# 15. M-5b and M-6 — true two-squad parallelism

These milestones deliberately diverge.

Neither Senior should wait for the other.

Both start from the same `M-5-BASE`.

---

## 15.1 A-M6 — Mediated Recursive Delegation

Owner:

**Senior Dev A**

Large-block objective:

> Turn `agent.spawn` into an ordinary capability-mediated effect that creates nested execution lineages without teaching the Kernel about agents or topology.

Coverage:

- `SpawnAdapter`;
- product path through Kernel dispatch;
- child execution scope attenuation;
- `ChildSpawned`;
- `ChildReturned`;
- delegation result contract;
- budget reservation/release;
- four-dimensional additive conservation;
- depth/turn structural enforcement;
- kill-tree;
- restart recovery;
- idempotent subtree settlement;
- product-path restriction of direct engine spawn.

Must preserve:

- Kernel verb blindness;
- capability attenuation;
- no topology inside Kernel;
- no conversation dump as delegation return;
- fresh-process recovery.

Acceptance:

RF-55…RF-59 green plus a nested-lineage demonstration bundle.

---

## 15.2 B-M5B — Formal-Domain Generality Falsifier

Owner:

**Senior Dev B**

Large-block objective:

> Try to falsify AETHER generality by implementing a materially non-coding domain without semantic changes to the generic substrate.

Leadership chooses OD-3 before opening the block:

- SAT/SMT witness;
- Lean/proof-checking;
- or another deterministic witness domain satisfying the same falsification objective.

Expected implementation surface:

- `packs/formal-<oracle>/`;
- domain prompts/policies;
- solver toolkit;
- domain context/projections;
- exterior deterministic evaluator;
- fixed task set;
- signed verdicts.

Critical rule:

**No semantic diff in domain/ports/kernel/agency/runtime substrate versus M-5-BASE.**

If B discovers that the formal domain truly requires a substrate change:

- do not silently modify it;
- raise counter-evidence;
- Tech Lead adjudicates under the falsification path.

Acceptance:

- full formal run;
- deterministic witness;
- RF-52/53;
- RF-86 zero-semantic-diff;
- RF-98 neutrality report;
- complete trajectory and reconstruction.

A failed generality hypothesis is a valid scientific result and must not be hidden by architecture patching.

---

# 16. G-M5B-M6 — Parallel acceptance

Leadership reviews both independently.

M-5b does not need M-6.

M-6 does not need M-5b.

Both share only `M-5-BASE`.

After both are accepted, the project has:

- empirically challenged generality;
- mediated recursive execution.

This unlocks M-6.5.

---

# 17. M-6.5 — Adaptive strategy / meta-control

Purpose:

Introduce higher-order control as ordinary policy/plugin behavior and measure whether it helps.

Leadership closes OD-4 before implementation:

**Confidence / Uncertainty Measurement Protocol**

No single confidence signal becomes constitutional truth.

Before both packages open, OD-4 freezes a Contract Kit with signal vocabulary, calibration rules,
`StrategyDirective`/`MetaController` interfaces, paired-run fixtures and ownership: Dev A owns the
runtime/plugin hook; Dev B owns confidence/progress contracts and evaluation tooling. Both may
reach `PACKAGE_READY` independently using fakes; final measured acceptance is integrated.

---

## 17.1 A-M65 — Meta-Control Runtime

Owner:

**Senior Dev A**

Large-block objective:

> Add a generic meta-controller integration path that can propose ordinary strategy changes without receiving special authority.

Coverage:

- MetaController SPI/plugin integration;
- between-turn consultation;
- StrategyDirective lowering;
- normal proposal path;
- `StrategyChanged` attribution;
- delegate directive integration when M-6 is available;
- no direct store/model/kernel bypass.

Possible directives include the accepted semantic family:

- revise plan;
- request context;
- change verification;
- abandon hypothesis;
- delegate;
- conclude.

Internal controller algorithm remains open.

Acceptance:

- controller acts only through normal authority;
- observable attribution exists;
- Kernel unchanged;
- disabled mode preserves baseline behavior.

---

## 17.2 B-M65 — Confidence, Progress & Paired Evaluation

Owner:

**Senior Dev B**

Large-block objective:

> Build the measurement system that decides whether the meta-controller actually improves performance.

Coverage:

- confidence protocol contract/schema;
- ProgressProjection;
- confidence signal ingestion;
- calibration representation;
- paired-run harness;
- fixed task set;
- N-seed/statistical evaluation per measurement law;
- success/cost/latency/repetition/recovery metrics;
- report artifact.

Acceptance:

- observable strategy-change evidence;
- paired comparison;
- no regression-budget breach for the claimed improvement.

If benefit is not established:

- controller remains disabled-by-default;
- negative result is recorded;
- milestone is scientifically successful if the hypothesis was honestly tested.

Leadership merges A-M65 before the final B-M65 study run, executes the paired experiment, and
marks both `GATE_ACCEPTED` only after the evidence report is accepted. A negative result closes
the experiment with the controller disabled by default.

---

# 18. M-7 — Topology and evidence-justified concurrency

Purpose:

Represent structure as data and keep time/scheduling policy replaceable.

Advanced concurrency is not automatically approved.

Before implementation, Leadership freezes topology/scheduler interfaces and uses the current
M7-01 report to bound the allowed scope. Dev A owns topology lowering and runtime mechanism; Dev B
owns analysis, falsifiers and RF-98. Dev B may reach `PACKAGE_READY` with recorded workloads and
topology fixtures, but the three-topology integrated proof runs after A merges.

---

## 18.1 A-M7 — Topology-as-Data & Scheduler Mechanism

Owner:

**Senior Dev A**

Large-block objective:

> Implement topology representation/lowering and a clean runtime scheduling mechanism without prematurely introducing an advanced concurrent engine.

Coverage:

- `mhf.topology/1`;
- topology artifacts;
- role/lineage templates;
- topology lowering;
- allowed delegation structure through ordinary attenuation;
- scheduler mechanism / policy separation;
- readiness model;
- sequential baseline;
- simple obviously-safe parallel read path only where already allowed by the corrected law.

Must not:

- create a second runtime;
- turn topology into authority;
- embed topology rules in Kernel;
- assume advanced concurrency is valuable.

Acceptance:

- multiple topologies lower through one runtime;
- no Kernel semantic change;
- no separate workflow engine.

---

## 18.2 B-M7 — Concurrency Evidence & Topology Falsification

Owner:

**Senior Dev B**

Large-block objective:

> Measure whether concurrency is worth its complexity and prove multiple topologies run without foundational semantic forks.

Coverage:

- M7-01 independence analysis;
- effect/resource/sink independence metrics;
- serialization-vs-dependency analysis;
- contention;
- cache behavior where relevant;
- three-topology falsifier;
- RF-98 rerun;
- evidence package for ADR-0099.

B does not implement advanced concurrency merely because the analysis exists.

---

## 18.3 G-M7 — ADR-0099

Leadership decides from evidence:

Integration order is A-M7 runtime/topology first, B-M7 integrated falsification second, followed
by ADR-0099. No advanced concurrent engine may enter A-M7 unless an earlier evidence-backed
ADR-0099 explicitly authorized that bounded scope.

### Option A — Implement

Data justifies advanced scheduling/concurrency.

Open a bounded implementation block.

### Option B — Simplify

Only limited safe concurrency is justified.

Keep the runtime simple.

### Option C — Cancel

Benefit does not justify machinery.

Preserve the sequential/reference model.

No outcome is considered failure if it follows evidence.

---

# 19. M-8 — Memory, retrieval, skills and learning

Purpose:

Close the loop from trajectories to reusable knowledge and measured composition improvement.

Memory remains capability-mediated.

Learning does not mean uncontrolled self-modification.

Before opening M-8, ADR-0100 and the M-8 Contract Kit freeze category ports, retrieval-provenance
records, skill-candidate/promotion boundaries and ownership. Dev A owns memory/retrieval ports and
infrastructure; Dev B owns skill analysis, evaluation, promotion and rollback. Both develop from
the same M-7 baseline with fixtures; integrated promotion uses the real A-M8 ports after A merges.

---

## 19.1 A-M8 — Memory, Retrieval & Experience Infrastructure

Owner:

**Senior Dev A**

Large-block objective:

> Build persistent knowledge/experience/project-memory retrieval infrastructure over the existing event/artifact substrate without introducing a single universal "memory" primitive.

Preserve the five-category conceptual vocabulary:

- session state;
- persistent knowledge;
- experience;
- skills;
- user/project memory.

Session state remains WAL + AgentView.

Likely implementation areas:

- KnowledgePort;
- ExperiencePort;
- ProjectMemoryPort;
- adapters/stores/indexes as needed;
- retrieval;
- capability-mediated access;
- provenance for any retrieved material that reaches model context;
- revocation/auditability where required.

Do not collapse all memory into one blob store or one Kernel primitive.

Acceptance:

- category boundaries are preserved;
- retrieval is provenance-visible;
- access is capability-mediated;
- no Kernel semantic diff.

---

## 19.2 B-M8 — Skills, Evaluation, Promotion & Rollback

Owner:

**Senior Dev B**

Large-block objective:

> Build the external learning/promotion pipeline that converts trajectory evidence into candidate improvements and promotes only composition versions that survive independent evaluation.

Coverage:

- failure/pattern analysis;
- candidate skill/policy generation interface;
- candidate evaluation;
- composition vN+1 creation;
- held-out suites;
- affected-context regression;
- presence-only adversarial tests;
- grounding;
- verification;
- transfer;
- signed promotion evidence;
- promoter authority;
- rollback;
- injected-regression rollback test.

ADR-0100 decides lifecycle representation:

- reintroduce deprecated lifecycle kinds with a full kind package;
- or use typed claims.

Critical invariant:

**Generator ≠ Evaluator ≠ Promoter**

A skill never self-promotes.

The unit of promotion is the versioned composition/library state, not merely a skill in isolation.

Acceptance:

- measured held-out lift for at least one promoted composition;
- decomposed evidence;
- tested rollback restores pre-promotion behavior;
- RF-98 / Kernel neutrality green.

---

# 20. G-M8 — M-8 exit

Leadership accepts M-8 only when:

- memory/retrieval infrastructure is capability-mediated and provenance-visible;
- skill promotion is independently evaluated;
- a real rollback was executed;
- held-out improvement is demonstrated for at least one promoted composition;
- Kernel neutrality remains intact;
- no self-certification path exists.

M-8 closure prepares the project for the later v1.0/M-9 integration horizon.

Merge order is A-M8 first, B-M8 second, then the held-out lift, rollback and neutrality gate.

---

# 21. Branch and integration policy

## 21.1 Baseline rule

Every large package starts from the same approved milestone baseline.

Examples:

M-4:

`main` after Phase 0 activation.

M-5a:

`main` after M-4 closure.

M-5b / M-6:

`M-5-BASE`.

## 21.2 Suggested branch naming

Examples:

- `feat/m4-a-evidence-runtime`
- `feat/m4-b-scientific-contracts`
- `feat/m5a-a-event-substrate`
- `feat/m5a-b-agentview-falsifiers`
- `feat/m6-a-delegation`
- `feat/m5b-b-formal-falsifier`
- `feat/m65-a-meta-runtime`
- `feat/m65-b-paired-evaluation`
- `feat/m7-a-topology-runtime`
- `feat/m7-b-concurrency-evidence`
- `feat/m8-a-memory`
- `feat/m8-b-skill-promotion`

Naming is not constitutional; consistency is the goal.

## 21.3 No cross-branch consumption

Forbidden pattern:

Dev A imports or rebases continuously on Dev B's unfinished feature branch, or vice versa.

Allowed:

- frozen interface fixtures;
- schemas from the baseline/spec;
- integration after independent PR acceptance.

## 21.4 Merge order

| Window | Merge order | Reason |
|---|---|---|
| M-4 | **B → A → integrated gate** | B owns profile/trajectory contract hotspots; A wires production capture to them. |
| M-5a | **A → B → integrated gate** | A establishes event `/2` and generated types; B validates projection/reconstruction on the real substrate. |
| M-5b / M-6 | **Either order** | Disjoint pack/evaluator versus runtime/delegation surfaces; both start from `M-5-BASE`. |
| M-6.5 | **A → B final study → gate** | B's completed experiment evaluates A's runtime controller. |
| M-7 | **A → B integrated falsifier → ADR-0099** | B's final topology proof evaluates A's lowering/runtime mechanism. |
| M-8 | **A → B → integrated gate** | B's promotion pipeline integrates with A's memory/retrieval contracts. |

The second package rebases on `main`, resolves only mechanical integration conflicts and reruns
its package plus integrated acceptance suite.

A semantic conflict means the supposedly frozen interface was not actually frozen and must be escalated.

---

# 22. PR contract

Each large work-package PR must contain:

## 22.1 Authority

References to the exact:

- Vision/Law invariant where relevant;
- accepted ADR;
- milestone;
- spec;
- backlog work package.

## 22.2 Scope

- what changed;
- what intentionally did not change;
- module/layer ownership.

## 22.3 Contract implementation

A concise map:

`spec obligation → implementation path/symbol → test/evidence`

## 22.4 Tests

- unit;
- contract;
- falsifier;
- migration;
- replay/reconstruction where relevant;
- performance regression where relevant.

## 22.5 Compatibility

State explicitly:

- read compatibility;
- write version;
- migration behavior;
- historical data handling.

## 22.6 Architecture declaration

Developer declares whether the PR changed any of:

- Kernel semantics;
- dependency direction;
- public schema;
- event roster;
- Runtime composition seam;
- authority model;
- milestone contract.

Expected answer is usually:

**No**

If yes, the prior escalation decision must be linked.

## 22.7 Evidence

Attach/point to:

- golden vectors;
- receipts;
- benchmark artifact;
- diff report;
- replay transcript;
- CI result;
- evidence bundle as applicable.

---

# 23. Leadership PR review checklist

Leadership review should compare the delivered code to the contract, not redesign the implementation.

## Architecture

- [ ] Dependency lattice preserved.
- [ ] Kernel remains domain blind.
- [ ] Runtime remains sole concrete composition seam.
- [ ] Agency has no upward import.
- [ ] No hidden second source of truth.
- [ ] No new architecture was smuggled into a helper/module.

## Contracts

- [ ] Public schema matches the accepted spec.
- [ ] Frozen schema not mutated in place.
- [ ] Dual-read/single-write migration implemented where required.
- [ ] Event-kind authority is correct.
- [ ] Writer-role authority is correct.

## Evidence

- [ ] Claims do not exceed actual proof.
- [ ] Required provenance is durable.
- [ ] Degraded capture is marked non-evidentiary.
- [ ] Fresh-process verification used where required.
- [ ] No in-memory-only "proof".

## Resources / authority

- [ ] Additive budget dimensions are correct.
- [ ] Depth/turn are structural limits.
- [ ] Capability attenuation preserved.
- [ ] No special authority added for agent/meta/topology behavior.

## Tests

- [ ] Package acceptance tests green.
- [ ] Required RF-* falsifiers green.
- [ ] Migration tests green.
- [ ] Governance tests green.
- [ ] Performance regression inside accepted gate.

## Scope

- [ ] No unrelated refactor creates review noise.
- [ ] No historical ADR rewrite.
- [ ] No documentation sprawl.
- [ ] No silent scope expansion.

## DoD

- [ ] Every required outcome from the large package is met.
- [ ] Any intentionally deferred item is explicitly listed and does not violate the milestone exit gate.

If all checks pass:

**MERGE**

If a check fails:

return the PR with the exact violated contract/gate.

Do not replace the developer's internal design merely because Leadership would have coded it differently.

---

# 24. Senior work-package handoff template

Every future large package can be handed to a Senior using this structure:

## Objective

One paragraph describing the milestone outcome.

## Authority

Exact Vision/Law/ADR/spec references.

## Starting baseline

Exact commit/tag.

## Required outcomes

Behavior and public contracts.

## Allowed implementation surface

Packages/modules the Senior owns.

## Must preserve

Architectural invariants.

## Must not do

Explicit forbidden changes.

## Verification

Tests/falsifiers/evidence required.

## Definition of Done

Observable exit conditions.

## Autonomy statement

> You own the internal implementation. You may refactor and introduce private abstractions inside the allowed surface. Do not ask Leadership to choose local implementation details unless a decision crosses one of the escalation triggers.

This should replace microtask-by-microtask instructions.

---

# 25. Scrum / Project-Lead cadence

The project does not need heavy Scrum ceremony.

Recommended control loop:

## Work-package opening

Leadership:

- confirms baseline;
- confirms contract freeze;
- marks one block READY for each Senior.

## During implementation

Senior:

- works autonomously;
- raises only escalation-trigger decisions;
- posts concise blockers/evidence when necessary.

Leadership:

- does not shadow implementation;
- avoids changing specs mid-block;
- resolves escalations quickly.

## PR

Senior delivers completed package.

Leadership reviews PR versus spec.

When its isolated suite is green, the PR becomes `PACKAGE_READY`; this is not yet milestone
acceptance.

## Integration gate

After both packages are `PACKAGE_READY`, Leadership applies the declared merge order, runs the
integrated suite and either returns the exact violated contract or marks both `GATE_ACCEPTED`.

## Milestone gate

Run milestone falsifiers/evidence.

## Next baseline

Tag/record accepted state.

Then open the next two large packages.

---

# 26. Project Owner decisions still outstanding

These are legitimate decisions and should not be delegated accidentally to implementation code.

## OD-1

Final ADR-0098 M-5a semantic kind roster.

Due:

M-5a entry.

## OD-2

Checkpoint policy defaults.

Due:

M5A checkpoint implementation.

Not foundational; Tech Lead may choose/tune based on measurements.

## OD-3

Formal deterministic oracle.

Due:

M-5b entry.

## OD-4

Confidence signal/calibration protocol.

Due:

M-6.5 entry.

## OD-5

ADR-0099 concurrency disposition.

Due:

M-7.

Must be evidence-driven.

## OD-6

M-8 lifecycle event representation.

Due:

ADR-0100.

## OD-7

Multi-tenant isolation-law ownership.

Due:

pre-M-9.

Does not block through M-8.

## OD-8

Blob GC / legal-hold lifecycle semantics.

Due:

M-8 design.

Must remain distinct from execution retention.

---

# 27. What Leadership should not do anymore

After Phase 0:

Do not:

- redesign the layer model every sprint;
- rewrite the Vision because an implementation detail is inconvenient;
- prescribe private methods before the Senior has attempted implementation;
- split every package into dozens of management tasks;
- make either developer consume or continuously rebase on the other's unfinished branch;
- merge speculative M-7/M-8 architecture into M-4;
- approve evidence based only on configuration;
- manually patch failed evidence bundles;
- use a failing falsifier as justification to weaken the falsifier;
- add new Markdown documents when an existing canonical home should be edited.

The project now needs execution discipline more than architectural ideation.

---

# 28. What the two Seniors are explicitly trusted to do

They are not "average implementers executing pseudocode".

They are Senior owners of a bounded subsystem.

They should:

- read the authoritative package;
- inspect current implementation;
- choose robust internal architecture;
- implement end-to-end;
- add missing local tests;
- refactor weak local design;
- document material implementation choices in the PR;
- challenge a faulty spec with evidence;
- keep changes inside the allowed constitutional boundary.

Leadership's job is to judge:

> **Does the delivered system satisfy the contract?**

not:

> **Did the Senior implement it exactly the way Leadership imagined?**

---

# 29. Final execution sequence

The complete sequence is:

## Phase 0

**Adopt rev1 → ratify → reconcile docs → freeze M-4 Contract Kit/ownership → qualify UDS → activate sprint**

Then stop foundational redesign.

## M-4

**A-M4 Evidence Runtime**
in parallel with
**B-M4 Scientific Contracts**

Then:

**integration → RF-95 → M-4 CLOSED**

## M-5a

Accept ADR-0098.

**A-M5A Event Substrate**
in parallel with
**B-M5A Projection/Falsifiers**

Then:

**integration → M-5-BASE**

## Parallel generality/delegation phase

**A-M6 Delegation**
in parallel with
**B-M5B Formal Generality Falsifier**

Then both accepted.

## M-6.5

**A-M65 Meta-Control Runtime**
in parallel with
**B-M65 Confidence/Paired Evaluation**

Then measured-value gate.

## M-7

**A-M7 Topology/Scheduler Mechanism**
in parallel with
**B-M7 Concurrency Evidence/Falsification**

Then ADR-0099.

## M-8

**A-M8 Memory/Retrieval**
in parallel with
**B-M8 Skills/Promotion/Rollback**

Then held-out lift + rollback + neutrality gate.

---

# 30. Definition of program success through M-8

By the end of M-8, AETHER should have demonstrated, rather than merely documented:

1. A useful real coding execution with complete causal/scientific evidence.
2. Event-derived continuation from durable history.
3. Honest cold reconstruction / replay evidence.
4. A measured Trusted Computing Base.
5. A second materially different domain running without substrate semantic change or, if not, explicit counter-evidence.
6. Capability-mediated nested lineages.
7. Meta-control whose value has been experimentally measured.
8. Multiple topologies over one generic runtime.
9. Concurrency only to the extent justified by data.
10. Memory/retrieval with provenance and authority.
11. Skill/composition improvement with independent evaluation.
12. Tested rollback.
13. Kernel neutrality preserved throughout.

That is the point at which the project has moved from an architectural thesis to an experimentally tested agentic-computation substrate.

---

# 31. Immediate TODO — start here

## Leadership

- [ ] Adopt `masterplan_todo_rev1.md` as the final external handoff; do not create a second active repository plan.
- [ ] Use the 13 supplied project documents plus this rev1 as the complete Phase-0 input.
- [ ] Do not use superseded original Phase-2 contract assumptions.
- [ ] Materialize and ratify corrected ADR-0096 v0.4.0.
- [ ] Revise supplied ADR-0097 v0.1.0 into v0.2.0 and ratify it.
- [ ] Apply the exact canonical reconciliation to law, contracts, schemas, specs, backlog, milestones and sprint boards.
- [ ] Update stale `AGENTS.md` orientation without allowing it to override Law Zero.
- [ ] Run governance/document checks.
- [ ] Freeze the M-4 Contract Kit, two-developer ownership matrix, hotspots and B→A merge order.
- [ ] Execute CV-003 in qualified Linux CI.
- [ ] Fix any actual RF-43 defect if reproduced.
- [ ] Record qualification receipt.
- [ ] Activate canonical `SPRINT_ACTIVE.md`.

## Senior Dev A — first production block

- [ ] Start **A-M4 — Evidence Runtime & Causal Capture**.

## Senior Dev B — first production block

- [ ] Start **B-M4 — Scientific Contracts, Reproducibility & Verification**.

## Leadership after both PRs

- [ ] Review each PR against this plan + corrected M-4 spec.
- [ ] Mark each isolated green package `PACKAGE_READY`.
- [ ] Merge B-M4 first, then rebase/merge A-M4.
- [ ] Run combined M-4 integration.
- [ ] Execute RF-95 exactly once when all preconditions are green.
- [ ] Close M-4 only on accepted evidence.
- [ ] Accept ADR-0098.
- [ ] Open A-M5A and B-M5A.

---

# 32. Final policy

From this point forward:

> **Architecture changes require evidence and explicit authority. Implementation details belong to the Senior who owns the work package.**

> **Squads receive large independent outcomes, not micromanaged TODO fragments.**

> **Leadership compares completed PRs against frozen contracts, falsifiers and milestone gates.**

> **The repository—not chat history—is the final implementation truth after ratification.**

This is the operating model for implementing the corrected AETHER plan from the current Phase-1/Phase-2 convergence state through M-8.
