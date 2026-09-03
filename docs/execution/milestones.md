---
id: execution.milestones
canonical_id: execution.milestones
class: execution
authority: execution
truth_plane: TARGET
status: living
implementation_status: PARTIAL
owner: repository-governance
canonical_for:
  - milestone outcomes and gates
purpose: Present stable TARGET milestone outcomes, dependencies, and acceptance predicates without claiming current completion. No sprint calendar.
audience:
  - contributor
  - release-owner
version: 0.9.3
last_verified: 2026-09-03
lock_head: "66aa7a3c0c31"
derived_from:
  - .draft/DEVELOPMENT_FINAL_PLAN.md
  - .draft/DEVELOPMENT_FINAL_PLAN_B.md
  - .draft/DEVELOPMENT_FINAL_PLAN_v2.md
  - .draft/PHASE-0_DEVELOPMENT_FINAL_PLAN.md
normative_authority:
  - docs/SPEC.md#milestone-compatibility
  - docs/decisions.md
relationships:
  - execution.tasks
  - execution.backlog
  - execution.feature_spec
  - execution.technical
  - spec.core
reviewer: repository-governance
confidence: high
---

# TARGET Milestone Gates

## 1. Scope & Authority

This page defines stable release outcomes and gate predicates. It does not track day-to-day work packages (owned by [`backlog.md`](backlog.md)) or the flat task tree (owned by [`tasks.md`](tasks.md)). Mechanism presence does not infer milestone closure; closure requires producer-verifiable empirical receipts evaluated under the milestone acceptance boundary.

Day-to-day work is the flat `T-*` tree. There is no sprint calendar and no WIP lane on this page. Status of **MS-*** rows is `OPEN` until receipts exist.

Living package version is **0.9.3** (`pyproject.toml`). That is not M-9 or M-10 acceptance. The M-9/M-10 labels below remain gate IDs.

| Milestone | TARGET Outcome | Acceptance Boundary | Status |
|---|---|---|---|
| **M-0–M-3C** | Trust foundation & canonical composition | Historical completion anchors preserved; successor changes require explicit ADR and falsifier. | `DONE` (Verified & Frozen) |
| **M-4** | Real-model coding proof with durable causal evidence | Immutable RF-95 bundle plus valid acceptance; RF-85 remains optional assurance. | `DONE` (Base Tagged) |
| **M-5a** | Event-derived `AgentView` & accepted successor baseline | Replay evidence and verified `CONVERGENCE-BASE-v1` predicates. | `DONE` (Base Reconciled) |
| **M-5b** | Independent domain-generality witness | RF-86/RF-98 against uncontaminated successor baseline. | `MECHANISM AS_BUILT` (Awaiting Handoff) |
| **M-6** | Mediated recursive delegation | Depth-three cold reconstruction, attenuation, budget conservation, recovery, signed evidence. | `MECHANISM AS_BUILT` (59 tests green) |
| **M-6.5** | Measured adaptive strategy | Valid paired-study disposition; controller remains off unless profile-specific evidence authorizes it. | `MECHANISM AS_BUILT` (Controller Off) |
| **M-7** | Declarative multi-role topology through one runtime | Three real-effect topologies, persisted artifact flow, and explicit scheduler disposition. | `MECHANISM AS_BUILT` (40 tests, 6 skips) |
| **M-8** | Durable memory & governed learning MVP | Authorization, recovery, retention, held-out lift $\ge 0.05$, separated promotion authority, executed rollback receipts. | `BLOCKED` (Empirical runner repair & held-out lift remain open) |
| **M-9** | Installable operational beta `0.9.0b1` | Qualified M-1–M-8 evidence, unified product surfaces, health, two workflows, restart/resume, offline-after-install. | `UNAUTHORIZED` (Blocked on M-8) |
| **M-10** | Final `0.9.0` release | Migration, backup/restore, fault/security/performance qualification, reproducible artifacts, soak, exact-subject signed envelope. | `UNAUTHORIZED` (Blocked on M-9) |

---

## 2. Gate Semantics & Release Invariants

- **Invariant G-1 (Evidence Verifiability)**: Unknown, missing, failed, degraded, or `undeterminable` evidence never satisfies a predicate.
- **Invariant G-2 (Linear Authorization)**: M-9 cannot be authorized before M-8 has an exact producer-verifiable bundle and independent acceptance over its digest. M-10 closes only when `./ci/release_qualify.sh` exits `0` for the exact candidate.
- **Invariant G-3 (Non-Contamination)**: Local test suites, cassettes, and self-authored oracles never constitute an official SWE-bench result. Official claims require the SWE-P5 protocol.

---

---

## 3. Backend-finish TARGET overlay (MS-*)

Vanguard v0.9.x backend finish contributes evidence to existing M-4–M-10 gates. Implementation details live in [`tasks.md`](tasks.md). Typed contracts live in [`spec.md`](spec.md). Engineering handbook: [`technical.md`](technical.md).

These rows recast A §0 / B §1 reliability order as **capability outcomes**, not waves.

| ID | TARGET outcome | Acceptance | Status |
|---|---|---|---|
| **MS-INSTRUMENT** | Exact-subject, schema-valid, dry-run-null empirical instrument | Enumerator digest; no `__pycache__` tasks; `subject_sha` bound; dry-run pass/cost/oracle null (B §8.4/8.5; T-01–T-03, T-24–T-25, T-40–T-41) | `CLOSED` |
| **MS-TRUTH** | No `completed` without bound verification; Forge cannot invent counts; one gating function | AdmissionGate + `VerificationReceipt.passed`; A §9.7; T-04–T-08, T-42, T-38, T-23. T-04 remains `[PROPOSAL]` until RF-25 successor baseline | `OPEN` |
| **MS-RESUME** | Fresh process restores episode_id, σ, prefix L1–L3; σ not in L3 | A §10.7; T-09–T-13, T-43–T-44. `domain/task_state.py` MISSING until T-09 | `OPEN` |
| **MS-SEE** | Epoch-bound packets, omissions explicit, one ContextCompiler | A §11.9; v2 §3 target (not current L3 dump); T-14–T-16, T-36–T-37, T-45–T-46 | `OPEN` |
| **MS-CHANGE** | 2PC multi-file, adapter preflight, tamper, implicated-set, greenfield oracle | A §12.8; v2 §4.2; T-17–T-20, T-47–T-49. AST never in kernel | `OPEN` |
| **MS-CONTROL** | One EpisodeEngine coding path qualified; Forge/Chimera not in product scores | A §13.6; facade fast/balanced/max; T-26–T-27, T-51–T-52 | `OPEN` |
| **MS-META** | Controller off unless paired study valid | A §14.7; T-28 `[PROPOSAL]` | `OPEN` `[PROPOSAL]` |
| **MS-SPECIALIST** | Treatments vs control; exterior merge | A §15.6; T-29–T-30, T-53 `[PROPOSAL]` | `OPEN` `[PROPOSAL]` |
| **MS-CAMPAIGN** | Director as runtime client; CAS handoffs | A §16.8; v2 §7.1; T-31, T-54–T-55, T-34 `[PROPOSAL]` | `OPEN` `[PROPOSAL]` |
| **MS-MEMORY** | Product memory behind grants; held-out lift; rollback | A §17.7; M-8 remaining empirical; T-32, T-56–T-57 `[PROPOSAL]` product wiring | `OPEN` `[PROPOSAL]` |
| **MS-OFFICIAL** | SWE-P5 / DeepSWE wrapper; local ≠ official | A §18.8; G-3; T-33, T-58 | `OPEN` `[PROPOSAL]` / blocked on control |
| **MS-SENIOR** | Senior Developer profile | A §29.1 copied below | `OPEN` |
| **MS-STAFF** | Staff Engineer profile | A §29.2 copied below | `OPEN` |
| **MS-PRINCIPAL** | Principal Architect profile | A §29.3 copied below | `OPEN` |
| **MS-LEAD** | Tech Lead profile | A §29.4 copied below | `OPEN` |
| **MS-HYDRA** | Bifurcation + living horizon | v2 §7.3–7.4; T-55. Product implementer remains EpisodeEngine+pack, not ChimeraEngine | `OPEN` `[PROPOSAL]` |

Dual mission (v2 §1.1): (1) SOTA coding agent (`Coding Max`) on one `EpisodeEngine` path. (2) Harness builder: compose other agents from the same substrate. CLI is a client of `ApplicationService`, not a second brain.

### From A — executive reliability order (not a wave calendar)

## 0. Executive decision

AETHER should not begin by building a larger swarm.

It should first make one coding lineage truthful, resumable, context-efficient, and independently verifiable.

The program order is:

1. repair benchmark and completion truth;
2. establish durable semantic task state;
3. put progressive repository context on the product path;
4. prove multi-file greenfield and brownfield closure;
5. qualify a strong single-agent control;
6. add adaptive strategy as bounded policy;
7. add specialist roles one treatment at a time;
8. add the persistent outer loop only after inner-loop evidence is reliable;
9. promote memory and skills only through held-out causal evidence;
10. optimize models, budgets, and topology against cost-adjusted signed success.

This ordering follows a simple reliability law:

$$
P(\text{campaign success})
=
\prod_{i=1}^{N}P(G_i\mid G_{<i}),
$$

where every weak milestone gate compounds across a long campaign.

If a per-package gate is only $0.95$ reliable, a 20-package campaign has at most
$0.95^{20}\approx0.358$ reliability before modeling other failures.

Long-horizon SOTA therefore comes from reducing compounded epistemic error, not merely increasing turns.

The recommended product target is a backend substrate that can instantiate four competency profiles:

- Senior Developer: bounded feature and bug-fix ownership with evidence-backed completion;
- Staff Engineer: repository-scale change planning, dependency management, and multi-package delivery;
- Principal Architect: architectural constraints, trade-off analysis, migrations, and evolution plans;
- Tech Lead: campaign decomposition, review routing, risk management, and operator escalation.

These are not four new runtimes.

They are four declarative organizations of the same causal substrate.

---

### From B — executive decision and score-band ASPIRATION

## 1. Executive decision

**Recommended ordering.** Make one coding lineage truthful before adding more agents, more context, or more memory.

The program order is:

1. Restore benchmark and navigation identity so no later score can be laundered through a stale SHA, a `__pycache__` task, or a dry-run.
2. Close false-positive completion on the product path (`vg-code-default` exemption, Forge `test_count = 1`, regex test-count inference).
3. Promote semantic task state from a runtime fold dumped into frozen L3 into a domain value that the compiler, admission gate, and resume path all consume.
4. Bind repository intelligence to a workspace epoch so progressive context cannot silently serve a pre-write snapshot.
5. Prove greenfield scaffold-and-oracle and brownfield blast-radius closure on frozen internal tasks.
6. Qualify a **single-agent** Coding Max control with Wilson intervals and explicit missingness.
7. Add metacognition as a bounded, opt-in policy with paired ablations.
8. Add specialist topologies only as named treatments against that control.
9. Add a durable outer-loop campaign director only after inner-loop completion is fail-closed.
10. Promote memory and skills only through held-out lift, separated authorities, and executable rollback.
11. Enter official DeepSWE v1.1 / SWE-bench Pro / SWE-bench Verified programs as a **separate measurement lane**, never as the implementation definition of done.

**Central architectural thesis.** AETHER already has the right substrate: a domain-blind kernel, an event-sourced ledger, one public run path, and pack-owned coding semantics. The product is blocked not by missing swarm machinery but by **untruthful settlement**. An agent that can declare success without a bound verification receipt, resume into a stale prefix, or be scored on an invalid task set cannot become a senior engineer no matter how many specialist roles are bolted on.

The reliability law this plan obeys is:

\[
R_{\text{campaign}} = \prod_{t=1}^{T} \Pr(\text{honest progress}_t \mid \text{honest state}_{t-1})
\]

If any factor is an unmeasured heuristic (invented test counts, keyword task classification, frozen resume dumps, ungated `finish`), the product collapses with horizon \(T\). Multi-agent branching multiplies that product by a merge-error term. Therefore Plan B forbids default multi-agent behavior until a single lineage has a measured \(R\) on frozen tasks.

**What this plan is not.**

- It is not an authorization to start Waves 6–10.
- It is not a claim that AETHER currently scores 60–90 on DeepSWE or SWE-bench Pro. **FACT:** no official receipt exists for HEAD `ebad36e`.
- It is not a claim that Coding Max, Forge, and Chimera are one product. **FACT:** Forge and Chimera are parallel loops.
- It is not a frontend plan. CLI/TUI control is a later consumer of this backend.

**Score bands (ASPIRATION, not forecast).**

| Band | Internal meaning | External meaning | Premature if claimed today |
|---|---|---|---|
| Qualification | Frozen internal multi-class suite, exact-subject, Wilson lower bound \(\ge 0.40\) on \(n \ge 30\), zero synthetic success | Instrument-valid harness; not an official score | Yes |
| Credible competitive | Same protocol on official DeepSWE v1.1 public tasks, lower bound overlapping the mid-pack (currently roughly 50–63% on mini-swe-agent) | Comparable to `deepseek-v4-flash [max]` 53%±4% and `glm-5.3-flash [max]` 63%±4% on DeepSWE v1.1 as of 2026-09-02 | Yes |
| Frontier parity | Official DeepSWE v1.1 pass@1 whose CI overlaps the 2026-09-02 leaders (gemini-3.8-flash / claude-opus-5 at 74%) **and** Scale SWE-bench Pro public standardized scores in the current 55–62% band | Harness + model jointly competitive | Yes |
| Stretch | DeepSWE \(\ge 80\%\) or Scale Pro public \(\ge 70\%\) under the **same** official scaffold | Would require model generation plus harness; not a Plan B exit | Yes |
| Unsupported | “90/100”, “replaces staff engineers”, “beats all vendor scaffolds” | Professional replacement is not a benchmark outcome | Always |

The user-requested 60–90 band is therefore a **mixture**: 60 is a plausible later qualification/competitive threshold on DeepSWE-class tasks; 90 is a stretch that current public leaderboards do not support as a near-term AETHER claim. SWE-bench Verified is saturating near 95%+ under vendor scaffolds and is the wrong trophy. SWE-bench Pro standardized scores remain far lower than vendor-scaffold scores; mixing those numbers is a methodology error this plan forbids.


### From A — final recommendation

## 36. Final recommendation

The next release program should be judged by whether it creates an agent that can carry truth across time.

That means:

- truth across tool calls;
- truth across context compaction;
- truth across process restarts;
- truth across files and packages;
- truth across agent handoffs;
- truth across evaluation boundaries;
- truth across learning and promotion.

The decisive technical sequence is:

```text
truthful evidence
  -> durable semantic state
  -> progressive context
  -> change-surface closure
  -> qualified single-agent control
  -> measured adaptive strategy
  -> measured specialist topology
  -> durable campaign direction
  -> governed learning
  -> external frontier qualification
```

If AETHER follows this order, its distinctive advantage will not be a fashionable swarm diagram.

Its advantage will be a small trusted substrate beneath agents that can work for hours or days, lose a process, recover their exact obligations, change strategy from evidence, coordinate specialists without sharing mutable hidden state, and stop only on independently bound proof.

That is the path from a capable coding harness to a credible Senior Developer, Staff Engineer, Principal Architect, and Tech Lead substrate.


### From A — competency model

## 4. Competency model: agents as declarative projections

### 4.1 Shared competency dimensions

Every engineering profile should be scored on the same dimensions.

| Dimension | Observable | Required evidence |
|---|---|---|
| Problem framing | explicit goal and constraints | goal digest and ambiguity log |
| Localization | implicated symbols and files | retrieval receipt and inspected set |
| Planning | dependency-aware task graph | versioned plan artifact |
| Implementation | bounded, coherent change | patch receipts and change surface |
| Verification | task-relevant falsification | typed verifier receipt |
| Recovery | progress after failure | strategy-change evidence |
| Architecture | conformance and trade-offs | invariant checks and decision record |
| Communication | concise handoff | evidence-linked summary |
| Leadership | decomposition and review | campaign DAG and exterior verdicts |
| Economics | value per cost | measured cost and latency |

### 4.2 Senior Developer profile

The Senior Developer profile owns one bounded task contract.

It must:

- reproduce before repairing when feasible;
- locate the smallest causal change surface;
- preserve repository conventions;
- add or update falsifiers;
- run targeted validation during iteration;
- run required gates before completion;
- report uncertainty honestly;
- leave a resumable task state.

Its default topology is one worker.

Its optional reviewer is triggered only by risk.

### 4.3 Staff Engineer profile

The Staff Engineer profile owns a multi-package technical outcome.

It must additionally:

- construct a dependency DAG;
- partition interfaces before files;
- manage migrations and compatibility windows;
- coordinate concurrent read-only investigation;
- serialize conflicting writes;
- track cross-package acceptance predicates;
- maintain a decision and risk register;
- produce integration evidence.

Its default topology is director plus sequential package workers.

### 4.4 Principal Architect profile

The Principal Architect profile owns system evolution under constraints.

It must additionally:

- identify constitutional and normative constraints;
- model alternatives and reversal conditions;
- quantify blast radius and migration cost;
- define stable ports rather than premature implementations;
- preserve one source of runtime authority;
- preregister architectural experiments;
- reject complexity without measured lift;
- specify rollback and compatibility semantics.

Its primary artifacts are plans, decision proposals, formal invariants, and executable architecture tests.

### 4.5 Tech Lead profile

The Tech Lead profile owns campaign execution.

It must additionally:

- maintain WIP limits;
- assign bounded work packages;
- monitor evidence and budget events;
- resolve blockers or escalate;
- request revision at package boundaries;
- prevent duplicated ownership;
- close the campaign only when all acceptance predicates resolve;
- preserve human override.

The Tech Lead should not be a privileged bypass.

It is a policy-constrained consumer of the same runtime.

---

### From A — definition of done by capability level

## 29. Definition of done by capability level

### 29.1 Senior Developer done

- at least 60% on frozen mixed internal repository tasks;
- false-positive completion below 1%;
- reliable focused-test selection;
- clean multi-file change closure;
- successful restart parity;
- evidence-linked handoff.

### 29.2 Staff Engineer done

- successful 10-node campaign;
- dependency-aware sequencing;
- cross-package integration checks;
- bounded revision loops;
- no duplicate effects across restart;
- measured cost advantage over naive giant-session control.

### 29.3 Principal Architect done

- successful repository-wide migration tasks;
- explicit alternative and reversal analysis;
- architecture invariant preservation;
- low change amplification on subsequent tasks;
- human reviewer acceptance of decision quality;
- no reliance on hidden benchmark conventions.

### 29.4 Tech Lead done

- maintains WIP and budget constraints;
- routes failures correctly;
- requests operator intervention at defined boundaries;
- completes or honestly terminates campaigns;
- produces reconstructible status from ledger alone;
- never bypasses exterior acceptance.

---

### From B — competency profiles

## 7. Competency profiles

These are **measurable product profiles**, not job-title claims about replacing humans. Benchmark scores do not equal professional replacement ([OpenAI, separating signal from noise](https://openai.com/index/separating-signal-from-noise-coding-evaluations/)).

METR’s 50% time-horizon is a different construct (human-expert duration at 50% success on METR’s suite) and is saturating at long durations; METR warns measurements above 16 hours are unreliable with the current suite ([METR time horizons](https://metr.org/time-horizons/)). Plan B uses METR only as a **qualitative horizon language**, not as a pass criterion.

### 7.1 Senior Developer

| Axis | Requirement |
|---|---|
| Scope | 1–20 files; bugfix/feature within an existing architecture; 15–60 turns |
| Default topology | Single agent, `vg-code-balanced` |
| Abilities | Reproduce, localize with IndexPort, surgical patch, affected tests, truthful `finish` |
| Artifacts | Patch, bound verification receipt, ledger |
| Verification | Bound-local lattice ≥ `bound-local-receipt`; tamper shield on brownfield |
| Completion gate | AdmissionGate + pack completeness; zero-test fail closed |
| Internal criterion | Frozen senior-class suite Wilson LB \(\ge 0.50\) at \(n\ge 30\) **after** Waves 0–5 |
| External | Not claimed; DeepSWE-like tasks are often harder than “senior afternoon bugs” |

### 7.2 Staff Engineer

| Axis | Requirement |
|---|---|
| Scope | Cross-module change; migration; 40–120 turns; resume ≥1 |
| Default topology | Single agent + optional `test_investigator → implementer` **after** ablation |
| Abilities | Blast-radius closure, epoch refresh, dead-end memory, budget-aware escalation |
| Artifacts | Plan DAG in \(\sigma\), implicated set, verification subject list |
| Verification | Affected-test closure + regression set; truncated ⇒ fail |
| Completion gate | All TaskSteps `VERIFIED` (once SemanticTaskState exists) |
| Internal criterion | Staff-class frozen suite LB \(\ge 0.40\) **and** resume parity on ≥5 tasks |
| External | SWE-bench Pro public is the closest published analogue; **do not** quote vendor 80% as this profile |

### 7.3 Principal Architect

| Axis | Requirement |
|---|---|
| Scope | Greenfield multi-package or brownfield architectural change; contracts before code |
| Default topology | `architect-plan` (single writer) then implementer; reviewer has no admit authority |
| Abilities | Extract requirements, write ports/types first, synthetic failing oracle, topological file DAG |
| Artifacts | Architecture notes in \(\sigma.settled\_invariants\), oracle digest, scaffold |
| Verification | Oracle fail-on-stub (FEATURE_SPEC §5) then pass-on-impl; no test mutation |
| Completion gate | Behavioral oracle + smoke + files exist; greenfield completeness policy |
| Internal criterion | Greenfield suite \(n\ge 15\) with oracle-vacuity checks |
| External | DeepSWE’s original tasks are closer than mined SWE-bench; still not “principal architect” |

### 7.4 Tech Lead

| Axis | Requirement |
|---|---|
| Scope | Campaign of multiple tasks; merge policy; operator checkpoints |
| Default topology | Outer-loop director; inner loop still single-writer episodes |
| Abilities | Decompose, sequence, refuse to start Wave-7 treatments without control, report missingness |
| Artifacts | CoordinationPlan, per-node receipts, campaign fold |
| Verification | Each node independently admitted; campaign success ≠ OR of conversational summaries |
| Completion gate | All required nodes signed; rollback of a node does not corrupt others’ CAS artifacts |
| Internal criterion | Campaign fixture of ≥8 nodes, one forced crash, resume of remaining DAG |
| External | Not a public leaderboard |

### 7.5 Mapping to public benches (cautious)

| Profile | Internal suite | Public analogue (not equivalent) |
|---|---|---|
| Senior | B1-class 20 tasks **after membership repair** | SWE-bench Verified is too saturated to certify this |
| Staff | Multi-file brownfield 30+ | SWE-bench Pro public (731), Scale standardized ~55–62% frontier as of 2026-09-03 |
| Principal / long-horizon | Greenfield + original tasks | DeepSWE v1.1 (113 tasks, 91 repos); leaders 74%±1–4% on mini-swe-agent |
| Tech lead | Campaign DAG | None; do not fake one |

---

### From v2 — HYDRA TARGET (not a schedule)

Copied outcome text lives in [`technical.md`](technical.md) (v2 §7). This row does not authorize default multi-agent.


---

## 4. Post-M-10 Horizon: Octopus Outer-Loop Meta-Orchestration (`M-OCT`)

The following outcomes define the post-1.0 architectural horizon for multi-day, multi-agent campaign orchestration. They do not create active sprint milestones or authorize work that M-8/M-9 currently block.

| Wave | Horizon Outcome | Terminal Acceptance Boundary |
|---|---|---|
| **W-OCT-1** | **Content-Addressed Mailbox Protocol** | Roles communicate strictly by publishing and reading content-addressed immutable message digests (`digest_of(payload)`); zero shared memory between roles; replayable multi-agent determinism. |
| **W-OCT-2** | **Declarative CoordinationPlan DAG** | Topology declared as immutable data DAG with strict per-mille budget shares ($\sum \text{budget\_share} \le 1000$); formal merge policies implemented: `CONCAT`, `FIRST_COMPLETE`, `SYNTHESISE`, `UNANIMOUS`. |
| **W-OCT-3** | **Outer-Loop Multi-Day Roadmap Director** | Higher-order director layer executing above `EpisodeEngine`; decomposes complex roadmaps into independent task DAGs across process boundaries without violating kernel S0–S12 contracts. |
| **W-OCT-4** | **Meta-Conductor & Swarm Goal Algebra** | Formal algebraic separation and reconciliation of individual swarm agent objectives under a global parent mission; automated topology selection based on task classification. |

---

## 5. Parallel SWE Benchmark Program (SWE-P0–SWE-P5)

| Program | Outcome | Required Gate | Status |
|---|---|---|---|
| **SWE-P0** | Instrument-valid harness | Isolated materialization, trajectory linkage, evaluator validity, secret boundary. | `DONE` |
| **SWE-P1** | Honest baseline | Preregistered corpus/model/cost policy and explicit missingness reporting. | `APPROVED` |
| **SWE-P2** | Harness experiments | Controlled context/tool/recovery experiments with attributable receipts. | `APPROVED` |
| **SWE-P3** | Model/harness optimization | Predeclared optimization and held-out comparison without contamination. | `BLOCKED` (on P1) |
| **SWE-P4** | Controlled larger run | Budgeted larger sample, independent audit, reproducible subject identity. | `BLOCKED` (on P3) |
| **SWE-P5** | Official evaluation | Official benchmark procedure and receipt; local runs are never official. | `BLOCKED` (on P4) |

---

## Appendix: historical W-092-F* aliases

Old overlay IDs remain resolvable. They are **not** the living work board.

| Historical ID | Maps to | Notes |
|---|---|---|
| **W-092-F0** | MS-INSTRUMENT (partial; LDA health is present-docs/CI) | Historical `DONE` claim stays as history; do not treat as MS-* closure |
| **W-092-F1** | MS-CONTROL path + CMX-09 | Canonical product path |
| **W-092-F2** | MS-TRUTH | Alias `CMX-10A` |
| **W-092-F3** | MS-RESUME | Alias `CMX-10B` |
| **W-092-F4** | MS-SEE / MS-CHANGE | Alias `CMX-11` |
| **W-092-F5** | MS-CONTROL qualification | Blocked on MS-TRUTH…MS-SEE |
| **W-092-F6** | MS-SPECIALIST | `[PROPOSAL]` |

Historical W-092 overlay text (pre-PHASE-0):

## 3. Capability Wave Overlay: Backend Finish (W-092)

Vanguard v0.9.2 is an implementation and qualification overlay contributing evidence to existing M-4–M-10 gates. Active implementation details live in [`tasks.md`](tasks.md) and [`FEATURE_SPEC.md`](FEATURE_SPEC.md).

| Gate | Stable Outcome | Acceptance Predicate | Status |
|---|---|---|---|
| **W-092-F0** | Exact-subject navigation & benchmark truth | LDA/index health is HEAD-bound; runtime-to-patch-to-exterior-verdict evidence resolves; canary subjects content-addressed. | `DONE` (Consolidated & Validated) |
| **W-092-F1** | One canonical Coding Max product path | Fast/balanced/max invoke `ApplicationService -> Runtime -> HarnessSession -> EpisodeEngine`; no parallel production engine or bypass. | `IN_PROGRESS` (Active in `tasks.md`) |
| **W-092-F2** | Truthful task-aware completion | Observed test counts; zero-test/stale/partial evidence fails closed; bugfix/feature/migration/greenfield policies explicit. | `APPROVED` (Spec in `FEATURE_SPEC.md`) |
| **W-092-F3** | Durable long-session continuation | Fresh process restores task/composition/policy/budget identity; never duplicates settled effects across 40+ turns. | `APPROVED` (Spec in `FEATURE_SPEC.md`) |
| **W-092-F4** | Repository-scale progressive context | `ContextPacket` and `IndexPort` supply bounded, snapshot-bound, omission-bearing staged context with deterministic source fallback. | `APPROVED` (Spec in `FEATURE_SPEC.md`) |
| **W-092-F5** | Product qualification | Frozen multi-class tasks produce exact patches, fresh verification, exterior verdicts, event evidence, and resume parity. | `BLOCKED` (Requires F1–F4 completion) |
| **W-092-F6** | Specialist role disposition | Held-out ablations accept or reject reviewer/localizer/planner treatments without weakening verifier authority. | `DEFERRED` (Optional post-baseline) |

---

