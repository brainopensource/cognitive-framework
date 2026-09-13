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
version: "0.9.5"
last_verified: 2026-09-12
lock_head: "bf56eea9"
derived_from:
  - docs/reports/reviews/electroweak_v092/plans/DEVELOPMENT_FINAL_PLAN.md
  - docs/reports/reviews/electroweak_v092/plans/DEVELOPMENT_FINAL_PLAN_B.md
  - docs/reports/reviews/electroweak_v092/plans/DEVELOPMENT_FINAL_PLAN_v2.md
  - docs/reports/reviews/electroweak_v092/plans/PHASE-0_DEVELOPMENT_FINAL_PLAN.md
normative_authority:
  - spec.md#milestone-compatibility
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

## Leadership disposition (2026-09-12)

The next product outcome is **qualified single-controller Coding Max**: an agent
built through the general framework that can read/localize, edit, verify, recover,
resume and report attributable outcomes under a finite budget. MS-CONTROL remains
the immediate empirical gate because adding learning or more workers before a
credible control would make their contribution unmeasurable. This is a product
qualification checkpoint, not M-9 beta acceptance. [RUN-1](spec.md#run-1-leadership-execution-decision-2026-09-12)
ratifies the current planning requirements; `requires:` in tasks owns execution.

**Acceptance provenance.** This session's earlier explicit leadership concurrence
supports the recorded MS-BASELINE/MS-CONTEXT closures on `2989d57d` and the File 1.1
planning decision. The source and focused tests alone would not support those
closures. The later documentation commits show authored plans; no independent
receipt was found in the evidence inspected that accepts their FH-1 algorithms,
atomic leases or any new empirical gate. Those remain proposals. Historical
closures for other subjects are retained as recorded, not re-certified here.
The present leadership delegation authorizes the decisions below; no historical
test count is restated as a new run. Control stays UNFROZEN, with no paid calls
authorized or made by this documentation task and no official score.

| Outcome | Leadership decision | Boundary for completion |
|---|---|---|
| Single-controller qualification | First priority; approve control-gate hardening and corpus/metric preparation now | T-26a/T-51/T-52, current-subject prerequisites, T-26 freeze and independently accepted positive T-27. A negative result completes reporting, not MS-CONTROL. |
| Governed reusable memory and skills | Next framework/product priority after control; refine MEM-01/MEM-02/T-56 first | Durable authorized retrieval, restart, revocation and rollback; separate empirical learning acceptance under M-8. Static skill cards are insufficient. No M-9 bypass. |
| Recoverable workspace and bounded specialist | Conditional follow-on branches; use control failure attribution to choose CAS or one advisory reader | MS-CAS or MS-DELEGATION, then useful treatment evidence where performance is claimed. Read-only delegation does not require CAS. |
| External evaluation | Independent post-control branch; qualify one Verified protocol before expanding to Aider | MS-EVAL protocol evidence and separately authorized MS-OFFICIAL runs. Existing local greenfield checks remain required before this branch. |
| Campaign director | Defer implementation until workspace/delegation are accepted and repeated multi-episode demand is evidenced | MS-CAS + MS-DELEGATION + explicit package admission; combined-tree exterior verification. No MCTS/RTV prerequisite. |
| MCTS, RTV, standing critic swarms, learned routing and professional-equivalence bands | Defer performance experiments; reject vote-based completion and invented universal scores | A dated, budget-matched, preregistered study is required to reconsider a treatment. No speculative algorithm expansion now. |

Capability completeness is demonstrated by composed behavior: discovery and
localization, safe changes, exterior verification, bounded state/recovery, durable
memory/skills and optional bounded delegation. It is not a count of registered
tools. Product claims name only accepted capabilities in the measured composition.

### Resolved — documentation budget (`check_doc_budgets`), 2026-09-12

**Authorization.** Both decisions in this section and the next were authorized by
the CTO on 2026-09-12, delegating the call after the director's review, and are
recorded here by the agent that executed them. They are a delegated decision, not
an independent leadership review of the underlying work, and either may be
reversed without prejudice. The linter change is a **code change** to
`tools/linters/check_doc_budgets.py`; this commit is therefore not
documentation-only.

`check_doc_budgets` is a **blocking CI gate**: it runs in `.github/workflows/ci.yml`
and `.github/workflows/clean-candidate.yml` with no `continue-on-error`. An earlier
draft of this section claimed it gated nothing; that was false and is corrected here.

The 200-line class default was never achievable for these five files, which are
normative registries carrying gate predicates, typed contracts and the task board —
not progressive-reading context. A permanently red gate carries no information, so
the check was **calibrated rather than waived**: `tools/linters/check_doc_budgets.py`
now holds per-file `CEILINGS` for the five, each set just above the size measured
after this consolidation. The reduction achieved is locked in, and regrowth fails
the gate. Lowering a ceiling is always allowed; raising one is a governance decision
that must be justified in the commit that does it. The five files remain measured —
this is an exemption from the class default, never from measurement.

**Still failing, and out of scope here:** `docs/backend/architecture/agency.md` (400),
`runtime-execution.md` (216), `docs/backend/reference/runtime-service.md` (201),
`PRD_AETHER_DESKTOP.md` (209) and `PRD_FRONTEND_PLATFORM.md` (349). All five are
byte-identical at `HEAD` and untouched by this branch, so this gate has been red on
main independently of this work. Their owners must reduce them or calibrate them the
same way before CI can go green.

### Ratified — `technical.md` consolidation, 2026-09-12

The consolidation removed roughly 5,400 of 6,750 lines, far beyond the ~15% stop
threshold that required halting for a decision first. That decision was not obtained
in advance. It is **ratified retrospectively under the authorization recorded above**: what was removed was
duplicated plan-catalog imports, the §12–24 harness-mechanics narrative and stale
inventories, all of which survive in `docs/reports/reviews/electroweak_v092/`; what
was retained is the near-term handbook, the complete FH-1 algorithms and the
fault-injection index. The breach is recorded rather than erased, and the stop rule
remains in force for future passes: a good outcome does not authorize bypassing it.

## 1. Scope

Stable release outcomes only. Work tree: [`tasks.md`](tasks.md). Packages: [`backlog.md`](backlog.md). Deltas: [`spec.md`](spec.md). Handbook: [`technical.md`](technical.md).

No sprint calendar. MS-* is `OPEN` until receipts exist. Package version **0.9.3** is not M-9.

Evidence integrity and the safety obligations of the selected profile are core to
qualification. Additional deployment profiles may be deferred; their required
containment cannot be waived for runs that claim to use them.

The control scope includes truthful disposition, canonical state/recovery,
nonmutating verification, existing patch safety, context compaction and restart.
CAS, specialist treatments, campaigns, governed learning and external benchmark
claims remain conditional post-control work. Calling them post-control does not
place M-8 memory after the M-9 beta that constitutionally depends on it.

**Historical project checkpoint (2026-09-11; accepted integrated subject `2989d57d4d38c01eecdb7a5fbb6f125077f00e59`).** Leadership accepted T-77/T-107/T-110/T-111 and closed MS-BASELINE plus MS-CONTEXT. Full discovery ran 3,121 tests (3,079 passed, 42 skipped, zero failures/errors); `just check`, elevated-IPC `just verify`, the 815-test runtime collection and the 20-test preregistration/frozen-canary slice passed. T-110 exercised 104 turns over four fresh interpreters with semantic parity and no duplicate settled effects. Public presets remain byte-identical; TCB LOC is 1386 (<= 1438); Invariant N-06 passed; `control_preregistration.json` remains `UNFROZEN` (`subject_sha: null`) with zero paid calls. MS-CONTROL remains OPEN; T-26 was recorded READY and UNFROZEN; current freeze is blocked on RUN-1 hardening, while T-27/T-51/T-52 remain open.

### Near-term release predicates (NT-1)

These additive gates do not reopen accepted historical subjects or authorize M-9/M-10 before M-8. They are prerequisites for the next control freeze; status stays OPEN until exact-subject receipts are independently reviewed. Task dependencies and three-stream file ownership live only in [`tasks.md`](tasks.md#near-term-ownership-and-ready-work).

| Gate | Outcome and acceptance predicate | Required task evidence | Status |
|---|---|---|---|
| **MS-BASELINE** | Reproducible, nonmutating full gate with complete collection; truthful terminal/disposition mapping and one facade/product path; existing patch semantics fail closed; no unaccounted dead-stack/falsifier loss. All required linters, full isolated Python suite, TypeScript and complete check/verify recipes pass on one subject; source/index/corpus unchanged. | T-98/T-99/T-101/T-102/T-103/T-108/T-97 plus accepted T-109/T-111 exact-subject receipts. | `CLOSED` on `2989d57d` |
| **MS-CONTEXT** | One canonical state fold/compiler/recovery path; frozen prefix and real serialized token ceiling; explicit cache metrics/missingness; deterministic bounded stall recovery survives restart. At least 100 fixture turns with forced compaction/restart preserve intent, grants, budgets, pending effects, newest result and fresh verification. Dedicated fixture budget does not change product presets. | MS-BASELINE and T-100/T-104/T-105/T-106/T-107/T-77/T-110/T-111 accepted on the integrated subject. Fixture success is not live task or provider-cache performance. | `CLOSED` on `2989d57d` |

#### Near-term gate progression and decision authority

| State | Entrance predicate | Authorized work | Exit predicate | Explicitly still forbidden |
|---|---|---|---|---|
| Baseline candidate | T-97/T-98/T-99/T-101/T-102/T-103/T-108 accepted | T-109 full exact-subject qualification; A/B may fix discovered defects | Independent review accepts zero-failure/error full Python, check/verify, TypeScript and nonmutation receipts | Declaring MS-BASELINE closed from focused tests or partial recipe execution |
| MS-BASELINE closed | T-109 accepted on a clean subject | T-107 runtime binding; T-77 provider-neutral cache/context completion | T-107 and T-77 task receipts accepted and integrated | Control freeze, paid measurement or claims about cache performance |
| Context qualification candidate | T-107 and T-77 integrated | T-110 deterministic 100+ turn compaction/restart falsifier | Uninterrupted/resumed semantic vectors match; no replay, lost state or false completion | Enlarging product presets or treating a fixture as model-quality evidence |
| Context reconciliation | T-109 and T-110 accepted | T-111 final full gate, identity invalidation tests and five-file reconciliation | Independent review accepts compatible final subject and closes MS-CONTEXT | Closing MS-CONTROL or enabling post-control treatments |
| Control candidate | MS-BASELINE and MS-CONTEXT closed | Audit applicable T-79/T-89/T-92-T-95/T-51/T-52 evidence and prepare T-26 | T-26 freezes an eligible exact subject; T-27 later evaluates it | Reusing a freeze after prompt/tool/model/policy/serializer identity changes |

Streams may prepare a larger integrated delivery between these governance transitions.
C may assemble hermetic corpus, metric and preregistration readiness while A runs T-110
and B hardens context/recovery, but preparation does not advance a milestone row.
Leadership reviews the consolidated T-111 subject once; branch-local commits and
focused suites are engineering evidence, not additional milestone gates.

Milestone closure is a governance transition, not a checkbox side effect. The task owner produces evidence; Stream C verifies completeness and subject identity; repository governance accepts or rejects the receipt and changes the milestone row. A failed gate leaves the milestone `OPEN`, preserves the diagnostic artifact and routes the defect to its code owner. A valid negative or undeterminable control result remains publishable evidence but does not satisfy a positive gate.

For MS-BASELINE the authoritative subject is the committed tree exercised by every mandatory command. A later documentation-only receipt commit may cite that subject, but any executable, schema, prompt, corpus, policy, dependency or generated-index change creates a new candidate. For MS-CONTEXT, T-111 additionally proves that all accepted component receipts are compatible with the integrated identity or reruns them on the final subject.

MS-CONTROL additionally requires MS-BASELINE and MS-CONTEXT on its candidate subject. Freeze only after all behavior-affecting integration is complete. A valid negative/undeterminable result is published but does not accept a positive gate. Preserve existing n >= 30 / Wilson lower bound >= 0.40 and zero **observed** false completions; report uncertainty and missingness. No universal cache-hit percentage or benchmark score is inferred from compiler tests.

#### MS-CONTROL admission, stopping and acceptance

The accepted NT-1 subject above is historical evidence, not an alias for HEAD.
The File 1.1 review inspected `5224912f7fb121e0be2b723ffd2a6c605cfa9777`;
successor documentation and generated-catalog commits do not transfer an exact-SHA
freeze. T-26 must establish candidate compatibility under NT-I02 and the subject
rules above. Green prerequisite unit tests demonstrate mechanisms; they do not
close T-51/T-52, supply a live L0 disposition, freeze T-26 or accept T-27.

These are TARGET acceptance requirements subordinate to [EW-9.3–EW-9.4](spec.md#ew-93-wave-2--frozen-control-honest-instrument--presets).
The current [control preregistration](../../../benchmarks/ladder/control_preregistration.json)
remains `UNFROZEN`, with null subject, suite and model identities. Refining this
page neither freezes that artifact nor authorizes measurement.

| Decision boundary | Required evidence / stopping rule |
|---|---|
| Admission | MS-BASELINE/MS-CONTEXT compatibility and applicable T-79/T-89/T-92–T-95/T-51/T-52 receipts on the candidate; required L0/L1 dispositions; one clean SHA and frozen task/oracle membership, model/provider, manifest/preset, prompt/tool/sampling and cost identities. Any unresolved prerequisite keeps T-26 unfrozen. |
| Spending | Zero paid control calls before freeze; T-26 itself makes zero paid calls. Freeze is necessary but does not itself authorize spending. Any required pre-freeze live L0 must use an eligible authorized zero-paid-call route; otherwise admission remains blocked. |
| Arm | Single-worker `vg-code-balanced`, preset `balanced`, through `vanguard.packages.runtime.entrypoint.execute`; preserve the public $0.15 / 900000 ms / 40000 tokens / 20 turns ceiling and record tighter caller attenuation separately. |
| Sample and denominator | At least 30 distinct current `LIVE-LOCAL` / `LIVE-HOSTED` tasks with binary exterior outcomes. Freeze finite membership and task order; one qualifying attempt per task. Retries never increase coverage or replace failed attempts. Preserve every missing, undeterminable and not-run outcome with its reason, outside the binary denominator; no full-suite pass-rate claim from partial coverage. |
| Planned stop | RUN-03: exactly 30 scheduled distinct L2 tasks, one measured attempt per task. Stop at completion of those slots, a resource ceiling or an integrity veto; retain missing slots, never top up to obtain 30 evaluable rows. Freeze all budgets and reconcile the draft artifact at T-26. No outcome-dependent early positive claim. |
| Positive result | At the planned stop, `n_evaluable = 30` — every one of the 30 scheduled tasks produced a binary outcome, per [RUN-03](spec.md#run-1-leadership-execution-decision-2026-09-12) — with the lower endpoint of the two-sided 95% Wilson interval (`z = 1.96`) `>= 0.40`, zero observed false completions and every identity/integrity predicate satisfied. At 30 evaluable tasks, 18 passes meet this statistical threshold; 17 do not. Fewer than 30 binary outcomes is `UNDETERMINABLE`, never a scaled-down positive: slots are never replaced or topped up. This is qualification on the frozen corpus, not a universal reliability claim. |
| Nonpositive result | A valid complete sample below the success threshold is `NEGATIVE`; insufficient evaluable evidence is `UNDETERMINABLE`; unfrozen or identity-invalid measurement is `INVALID`. A false-completion veto prevents acceptance regardless of a numeric disposition. Publish the result, missingness, costs and stop reason; all such outcomes leave MS-CONTROL open. |
| Closure | An independent reviewer accepts the exact-subject evidence digest and repository governance records closure. A helper returning `POSITIVE` is insufficient. Zero observed false completions is a finite-sample observation, not proof of zero population risk. |

**Delivery order into MS-CONTROL (RUN-11, Director 2026-09-12).** Five packages
with rough engineering sizes: P1 measurement and oracle integrity (M, T-51/T-132);
P2 product-path write and change closure (M, T-130 then its repair); P3 exterior
completion and false-completion resistance (M, T-131); P4 large-context,
compaction and resumable-session qualification (L); P5 budgeted model cascade plus
comparative evidence (L). P1 and P2 may run in parallel under disjoint leases. P3
falsifier authoring and P4 read-only qualification may run alongside them. P3
integration requires a reviewed P2; final P4 qualification requires reviewed P2
and P3. T-26b acceptance requires reaccepted P1 and T-51. Measurement corruption
and the absent product trace both precede reliable qualification, which is why
P1 and P2 lead: a number produced before either is closed cannot be trusted even
if it is favourable. MS-CONTROL is freeze-ready only after corpus reacceptance,
independent T-26b acceptance, every RUN-09 blocker closed, exact-subject baseline
and context compatibility, and the required live L0 acceptance under a separate
authority that RUN-12 does not grant.

**Grounding boundary.** Existing mechanisms are
[`live_oracle_pass`, `score_metrics`, `canary_disposition`](../../../benchmarks/ladder/metrics.py),
[`wilson_interval`](../../../benchmarks/statistics.py), and
[`require_frozen`](../../../benchmarks/ladder/control.py). Their focused falsifiers are
[`test_metric_veto.py`](../../../test/benchmarks/test_metric_veto.py) and
[`test_preregistration.py`](../../../test/benchmarks/test_preregistration.py).
These helpers do not by themselves enforce the full membership, unique-attempt,
resource-stop and independent-review requirements above. The production
[`Preregistration`](../../../vanguard/packages/domain/evidence/preregistration.py)
binds task/oracle/evaluator/subject identities for RF-85; it is a distinct contract
from `aether.control-preregistration/1`, not an interchangeable freeze API.

Dual mission: (1) Coding Max on one `EpisodeEngine` path; (2) same substrate for other agents. CLI is a client of `ApplicationService`.

### Post-control horizon release predicates (FH-1)

All rows below are **OPEN [PROPOSAL]**. They define future acceptance, not implementation authorization or a sprint calendar. NT-1 and its control gate remain unchanged. The normative owner is [FH-1](spec.md#fh-1-post-control-backend-horizon-proposal). Existing MS-* rows are extended for these future subjects, not replaced or retrospectively accepted.

Planning inputs are the [measurement and topology review](../../reports/reviews/aether_v093_review/part2_benchmark_mastery_and_topologies.md),
[interface blueprints](../../reports/reviews/aether_v093_review/part3_blueprints_and_interface_contracts.md),
[roadmap and risk review](../../reports/reviews/aether_v093_review/part4_roadmap_and_strategic_synthesis.md),
and [auxiliary execution table](../../../.draft/temp_auxiliary_table.md).
These are non-canonical references: their percentages, phase durations, historical
defect lists and prototype APIs do not establish completion, dependency edges or
implementation authority. Promote only reviewed outcomes here; schemas,
algorithms and atomic task leases belong in the subsequent runway files.

| Gate | Dependencies | Required acceptance evidence | Status |
|---|---|---|---|
| **MS-CAS** | MS-CONTROL; T-112–T-116 | Durable immutable tree capture, exact edit sets, isolated verification and atomic ledger-head promotion; disk/process fault injection at every persistence boundary; concurrent winner/loser and ABA tests; lost reply reconciliation; bounded GC; separate journaled checkout export preserves modes/existence or reports quarantine. No atomic-host-checkout claim. | `OPEN` [PROPOSAL] |
| **MS-DELEGATION** | MS-CONTROL; T-117–T-118 | Canonical child lineage, scope and aggregate budget conservation; restart/revocation/cancellation and unknown-outcome reconciliation; child cannot mutate parent or acceptance records. This qualifies mechanics, not specialist performance. | `OPEN` [PROPOSAL] |
| **MS-SPECIALIST / MS-META extension** | MS-DELEGATION; T-119; MS-CAS additionally for mutating workers | Preregistered paired study against frozen control, cost/latency/missingness included. Enable only treatments satisfying the chosen useful-lift or cost-saving/noninferiority predicate. Valid negative/inconclusive study remains disabled. T-28/T-29/T-30/T-50 retain ownership of their treatment families. | `OPEN` [PROPOSAL] |
| **MS-CAMPAIGN extension** | MS-CAS; MS-DELEGATION; T-120 | Existing runtime client resumes DAG execution after crashes without duplicate effects; parent owns merge; integration checks validate combined tree; blocked dependencies, scope change and exhausted replans have explicit outcomes. A basic campaign does not require a positive specialist study; performance claims do. Full M-OCT remains post-M-10. | `OPEN` [PROPOSAL] |
| **MS-MEMORY extension** | MS-CONTROL; T-121 and existing M-8 predicates | Project authorization/revocation at retrieval and caches; separate generation/evaluation/promotion; versioned lessons, held-out lift, rollback and leakage falsifiers. Memory treatment never trains on the evaluation holdout. This row alone does not accept M-8. | `OPEN` [PROPOSAL] |
| **MS-EVAL** | MS-CONTROL; T-122–T-125 | Qualified immutable candidate/evaluator separation, pinned Verified and Aider adapters, separate greenfield corpus, faithful reference-result replay and failure accounting. No live score required to qualify protocol; no score inferred from fixtures. | `OPEN` [PROPOSAL] |
| **MS-OFFICIAL extension** | MS-EVAL; SWE-P4/SWE-P5; T-126 | Authorized frozen runs, complete upstream outputs/predictions, exact-subject audit and benchmark-specific reporting; missing instances preserved. Optional CAS/topology/memory dependencies apply only if included in the measured arm. Existing DeepSWE T-33 remains a distinct track. | `OPEN` [PROPOSAL] |
| **MS-SOTA** | MS-OFFICIAL; T-127 | Dated eligible comparator, frozen metric/resource envelope, prespecified statistical superiority criterion and reproducible evidence. Passing an official protocol or reporting a score does not close this gate. Negative/inconclusive outcomes remain published with gate OPEN. | `OPEN` [PROPOSAL] |
| **Release handoff** | T-128; applicable accepted gates; existing M-8/M-9/M-10 | Complete preservation recipes on release subject, independently reviewed evidence digest, migration/rollback and operator claims matched to qualified features. M-9 cannot precede M-8; M-10 retains release_qualify exit-zero predicate. | `OPEN` [PROPOSAL] |

Dependency spine: `MS-BASELINE -> MS-CONTEXT -> MS-CONTROL`; thereafter CAS, delegation, memory and evaluation are conditional branches. No requirement to build campaigns or achieve MS-SOTA before evaluating the single controller. A released profile advertises only its accepted branches. Prototype refinements require updated contracts and leaf falsifiers before implementation, with no weakened gate by silent threshold changes.

The prior CAS → delegation → campaign → memory → evaluation review order is
superseded by the priority decision above. It never constituted dependency edges.
Memory/skills refinement follows control first; CAS, advisory delegation and
evaluation remain independent conditional branches, with campaigns deferred.
CAS-01 owns workspace qualification; DEL-01 owns delegation mechanics and advisory
specialists; OCT-03 owns the campaign client; MEM-01 retains M-8 governed-learning
requirements; EVAL-02 qualifies benchmark protocols. Package lifecycles remain
owned by `backlog.md`, and executable leaf ownership remains in `tasks.md`.

The reference designs sharpen the following acceptance boundaries:

- **CAS:** Failed verification preserves the prior authoritative head; concurrent
  promotions have one winner; acknowledged promotion survives restart; lost
  replies reconcile through the original operation identity. Export separately
  detects newer user edits and quarantines conflicts or unrestorable paths.
- **Delegation and specialists:** Qualify one bounded advisory reader first.
  Unknown dispatch outcomes retain their reservation until reconciled; cancellation
  or restart cannot replenish the aggregate allowance. Any later mutating worker
  requires an isolated candidate, and the parent verifies the combined result.
- **Campaign:** The director is a runtime client with zero mutating verbs;
  qualified child episodes perform edits. Dependency readiness and resume must
  preserve settled effects. Model votes and worker-local checks cannot replace
  exterior verification of the integrated candidate.
- **Evaluation:** Report brownfield repair and greenfield completeness separately.
  Pin each benchmark's own attempt/edit/feedback rules and include coordination,
  verification, failed-attempt and recovery costs. Protocol qualification,
  an official measured score and statistical superiority remain distinct gates.

For every empirical post-control branch, freeze finite sample/resource limits,
the comparison, missingness policy and statistical decision before measurement.
Useful-lift and cost-saving/noninferiority alternatives cannot be selected after
viewing results. MS-MEMORY retains held-out lift `>= 0.05` with `p < 0.05`,
independent promotion and executed revocation/rollback evidence; its statistical
protocol belongs in the subsequent specification review. A positive control does
not supply that evidence. Mechanical fault-injection suites qualify CAS,
delegation, campaign recovery and evaluation protocols without manufacturing
performance claims. Negative or inconclusive treatment evidence leaves the
treatment disabled and the corresponding positive gate open.

#### Invariant release vetoes

Any observed false completion, test/oracle contamination, subject mismatch,
unaccounted effect, budget overspend, unauthorized grant widening or duplicate
settled effect prevents acceptance and stops further affected dispatch. Preserve
the evidence and reconcile pending effects before any new candidate is measured.
Mandatory gate failure or missing acceptance evidence likewise vetoes release;
success, cost or latency gains cannot compensate for these failures.

All branches preserve the 1438-LOC kernel ceiling (planned kernel delta: zero),
hexagonal imports, domain blindness, one ledger writer and N-06: no subprocess
execution in runtime; effect execution remains in permitted adapters/tools.
Fault handling must demonstrate the promised recovery or explicit quarantine;
an untested claim of absolute crash/ABA immunity cannot satisfy a milestone.
M-8/M-9/M-10 and G-1–G-3 remain binding regardless of which MS-* branch passes.

## 2. M-0–M-10 and G-1–G-3

This page defines stable release outcomes and gate predicates. It does not track day-to-day work packages (owned by [`backlog.md`](backlog.md)) or the flat task tree (owned by [`tasks.md`](tasks.md)). Mechanism presence does not infer milestone closure; closure requires producer-verifiable empirical receipts evaluated under the milestone acceptance boundary.

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

### Gate semantics & release invariants

- **Invariant G-1 (Evidence Verifiability)**: Unknown, missing, failed, degraded, or `undeterminable` evidence never satisfies a predicate.
- **Invariant G-2 (Linear Authorization)**: M-9 cannot be authorized before M-8 has an exact producer-verifiable bundle and independent acceptance over its digest. M-10 closes only when `./ci/release_qualify.sh` exits `0` for the exact candidate.
- **Invariant G-3 (Non-Contamination)**: Local test suites, cassettes, and self-authored oracles never constitute an official SWE-bench result. Official claims require the SWE-P5 protocol.

## 3. Backend-finish overlay (MS-*)

Reliability order (B §1; A §0 is the same sequence without the official-bench lane):

1. instrument identity → **MS-INSTRUMENT**
2. truthful completion → **MS-TRUTH**
3. durable σ / resume → **MS-RESUME**
4. epoch-bound context → **MS-SEE**
5. multi-file change closure → **MS-CHANGE**
6. one EpisodeEngine control → **MS-CONTROL**
7. meta / specialists / campaign / memory / official → MS-META…MS-OFFICIAL (`[PROPOSAL]` except as receipts appear)

| ID | TARGET | Acceptance | Status | Evidence |
|---|---|---|---|---|
| **MS-INSTRUMENT** | Exact-subject, schema-valid, dry-run-null instrument | membership digest; no `__pycache__` tasks; `subject_sha`; dry-run pass/cost/oracle null; PASS without patch digest refused; dispositions `{passed,failed,undeterminable,not_run}`; dirty tree fail-closed; BAAC `aether.baac.challenge/1` | `CLOSED` | `63b77116` + T-01–T-03 (`65768a6b`). Falsifier: `test.benchmarks.test_instrument_ms` |
| **MS-TRUTH** | No `completed` without bound verification; no invented counts; one gate; **both settlement axes recorded, neither derived from the other**; greenfield vacuity rejection; anti-premature exit | T-42/T-38/T-23/T-72/T-81/T-82 are implemented and their focused falsifiers pass. T-18 is wired through the session and the default manifest declares `repo_index`; T-84/T-85 and BRG-01 T-87/T-88/T-91 are implemented. Still open: T-04's 21-test successor obligation, T-92/L0 and final exact-subject convergence evidence; T-89 is the product-subject bridge into control qualification. **Falsifier:** a run with zero patches or tampered tests cannot earn `passed`; greenfield passing on `pass`/`NotImplementedError` is rejected; a settlement claim recorded by an instrument that reuses a fixed run id or publishes an empty receipt is not evidence; **a run may legitimately record `terminal_status=abandoned` with `disposition=passed`, and the ledger replays it without contradiction** — the disposition axis is never derived from the termination axis, nor the reverse (`ICD §3`, `VG-03 §6.2`). | `MECHANISM` | Focused evidence 2026-09-05: 39 settlement/identity/receipt/approval tests pass through the live `entrypoint` -> `Runtime` -> ledger path; TCB is 1386 and domain-blindness/execution-truth pass. **MECHANISM, not empirical close:** L0 (T-92) has not run, CONVERGENCE-BASE-v1 remains fail-closed against the current subject, T-04's successor obligation is open, and the current branch boundary regression must be repaired before measurement. |
| **MS-RESUME** | Fresh process restores episode_id, σ, L1–L3 prefix; σ not in L3 | T-09–T-13, T-43–T-44 green on commit `8637db55` | `CLOSED` | `uv run python3 -m unittest test.contracts.test_semantic_task_state test.runtime.test_task_state_fold test.runtime.test_resume_identity` — 16 tests OK (2026-09-03). σ not in L3; episode_id preserved; 40-turn fold parity. |
| **MS-SEE** | Epoch-bound packets, explicit omissions, one ContextCompiler and optional port-backed intelligence | Existing T-14–T-16/T-36/T-37/T-45 mechanisms preserved. Core cache/receipt/goal-echo requirements move to MS-CONTEXT via revised T-77; no T-76 dependency for core compilation. Remaining IDX-01 T-75/T-76 keeps unchanged IndexPort, bounded L5 observations and no-index fallback. T-46 remains optional query-local ranking. Falsifiers: current-subject retrieval, unchanged L1–L3 bytes, bounded receipts and no implicit ranking/authority in the adapter. Cache metrics must be observed or null; no blanket 85% threshold. | `OPEN` (remaining IDX-01) | Historical mechanism subjects retained; index row counts are not acceptance predicates. |
| **MS-CHANGE** | Multi-file change closure; 2PC in adapters; exact edit primitive; reverse-caller admission; **zero kernel AST** | T-17 `DONE`; T-18/T-19/T-20 mechanisms are wired; **T-83a** (greenfield prompt modernization, no dependency) and **T-83b** (caller admission, `requires: T-75`) remain separate work. T-47 amended by **T-78** (exact `str_replace`, unique preimage, trimmed-EOL only — **no fuzzy cascade**). **TLS-04 closes as mechanism-present**: `ast.parse` preflight already lives in `adapters/environment/transaction.py` and aborts before durable flush. Read-before-edit remains prompt guidance plus an A/B-able strict profile, not a universal dispatch ladder. **Falsifier:** a syntax error in file N of M leaves all M byte-identical (`tree_hash_before == tree_hash_after`); public API signature changes reject completion if dependent call sites remain uninspected (**T-83b**); greenfield prompts contain zero *"Do not read or search first"* bans (**T-83a**); strict-policy and control runs differ only by the declared read-before-edit policy; `grep -c "import ast" vanguard/packages/kernel/*.py` is **0**; `check_tcb_budget.py` reports **1386 unchanged**. | `OPEN` | `5c9870f0`, `094fa899`, `db935138`, runtime tamper falsifiers 2026-09-05. Dialect tickets do not close this gate. |
| **MS-CONTROL** | One EpisodeEngine product path; one preset catalog; truthful budgets/outcomes and no Forge/Chimera product scores | Requires MS-BASELINE, MS-CONTEXT and existing applicable T-26/T-27/T-51/T-52/T-79/T-89/T-92–T-95/T-97 evidence. Preserve catalog fast $0.05/8t/16k, balanced $0.15/20t/40k, max $0.40/40t/96k and separate caller attenuation. Single-worker vg-code-balanced through entrypoint.execute, exact clean SHA, L2 n >= 30, Wilson LB >= 0.40, zero observed false completions. T-80/T-96 and specialist/director treatments remain post-control; T-106 is core recovery, not such a treatment. | `OPEN` | T-111 hands off accepted local gates; then required live L0, corpus/metric reconciliation, T-26 freeze and T-27 disposition. Historical focused tests are not current acceptance. |
| **MS-META** | Controller off unless paired study valid | T-28 | `OPEN` `[PROPOSAL]` | |
| **MS-SPECIALIST** | Treatments vs control | T-29–T-30, T-53 | `OPEN` `[PROPOSAL]` | |
| **MS-CAMPAIGN** | Outer-loop director as a runtime client; isolated worktrees; CAS mailbox; test-time compute & Recursive Tournament Voting; merge by exterior tests | T-31, T-54, T-34. **`OCT-03` is the canonical row** (draft `DIR-01` is an alias). Director holds **zero** mutating verbs; child episodes run in isolated git worktrees under attenuated budgets; RTV may allocate evaluation and rank speculative candidates; roles exchange only content-addressed digests (OCT-01). Merge is decided solely by the bound `ExternalVerifier` test verdict, **never** LLM quorum or tournament votes. **Hard dependency: `MS-CONTROL` closed.** **Falsifier:** a crash at node K resumes at K+1 with no duplicate effects; a failing child cannot mutate the parent tree; changing an RTV score cannot admit a candidate whose exterior verdict failed. | `OPEN` `[PROPOSAL]` (gated on **MS-CONTROL**) | Staged to Wave 5 per **D-03**: a director dispatching unqualified inner episodes multiplies false completions across an expensive DAG. |
| **MS-MEMORY** | Grants; held-out lift; rollback | T-32, T-56–T-57; M-8 empirical still open | `OPEN` `[PROPOSAL]` | |
| **MS-OFFICIAL** | SWE-P5 / DeepSWE wrapper; local ≠ official | T-33, T-58; G-3 | `OPEN` `[PROPOSAL]` | |
| **MS-SENIOR…LEAD** | Profiles | obligations (A §4) + measurement (B §7) + A §29 done-defs | `OPEN` | Tables below; one copy. |
| **MS-HYDRA** | Bifurcation + living horizon | T-55; implementer = EpisodeEngine+pack | `OPEN` `[PROPOSAL]` | |

**Subject boundary — why `MS-INSTRUMENT` is not reopened.** `MS-INSTRUMENT` is
`CLOSED` over the *benchmark harness* subject (`63b77116` + T-01–T-03, falsifier
`test.benchmarks.test_instrument_ms`), and that closure stands for its subject. The
product CLI path — `runtime/entrypoint.py` — was never that subject, which is why the
run-identity, receipt-telemetry and measured-subject findings do **not** meet the
`REOPENED` predicate (backlog §1) and open **INS-01** in the `INSTRUMENT (product)`
package instead. The consequence is the point: the moment the canary is required to
run through the product path (**T-89**), `MS-INSTRUMENT`'s guarantees stop
transferring and INS-01 becomes a precondition of `MS-CONTROL`, not a nicety.

Score-band ASPIRATION (not a forecast). Backlog points here.

| Band | Internal meaning | External meaning | Premature if claimed today |
|---|---|---|---|
| Qualification | Frozen internal multi-class suite, exact-subject, Wilson lower bound \(\ge 0.40\) on \(n \ge 30\), zero synthetic success | Instrument-valid harness; not an official score | Yes |
| Credible competitive | Same protocol on official DeepSWE v1.1 public tasks, lower bound overlapping the mid-pack (currently roughly 50–63% on mini-swe-agent) | Comparable to `deepseek-v4-flash [max]` 53%±4% and `glm-5.3-flash [max]` 63%±4% on DeepSWE v1.1 as of 2026-09-02 | Yes |
| Frontier parity | Official DeepSWE v1.1 pass@1 whose CI overlaps the 2026-09-02 leaders (gemini-3.8-flash / claude-opus-5 at 74%) **and** Scale SWE-bench Pro public standardized scores in the current 55–62% band | Harness + model jointly competitive | Yes |
| Stretch | DeepSWE \(\ge 80\%\) or Scale Pro public \(\ge 70\%\) under the **same** official scaffold | Would require model generation plus harness; not a Plan B exit | Yes |
| Unsupported | “90/100”, “replaces staff engineers”, “beats all vendor scaffolds” | Professional replacement is not a benchmark outcome | Always |

The user-requested 60–90 band is a **mixture**: 60 is a plausible later qualification/competitive threshold on DeepSWE-class tasks; 90 is a stretch that current public leaderboards do not support as a near-term AETHER claim.

### Competency model (A §4 + A §29 + B §7, once)

Every engineering profile is scored on the same dimensions.

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

These are **measurable product profiles**, not job-title claims about replacing humans. Benchmark scores do not equal professional replacement.

#### Senior Developer (MS-SENIOR)

Owns one bounded task contract: reproduce before repairing when feasible; smallest causal change surface; preserve conventions; add or update falsifiers; targeted validation; required gates before completion; honest uncertainty; resumable task state. Default topology: one worker.

| Axis | Requirement |
|---|---|
| Scope | 1–20 files; bugfix/feature within an existing architecture; 15–60 turns |
| Default topology | Single agent, `vg-code-balanced` |
| Abilities | Reproduce, localize with IndexPort, surgical patch, affected tests, truthful `finish` |
| Artifacts | Patch, bound verification receipt, ledger |
| Verification | Bound-local lattice ≥ `bound-local-receipt`; tamper shield on brownfield |
| Completion gate | AdmissionGate + pack completeness; zero-test fail closed |
| Internal criterion | Frozen senior-class suite Wilson LB \(\ge 0.50\) at \(n\ge 30\) after MS-CONTROL |
| External | Not claimed |

**Done (A §29.1):** at least 60% on frozen mixed internal repository tasks; false-positive completion below 1%; reliable focused-test selection; clean multi-file change closure; successful restart parity; evidence-linked handoff.

#### Staff Engineer (MS-STAFF)

Owns a multi-package technical outcome: dependency DAG; partition interfaces before files; migrations; serialize conflicting writes; cross-package acceptance; decision/risk register; integration evidence.

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

**Done (A §29.2):** successful 10-node campaign; dependency-aware sequencing; cross-package integration checks; bounded revision loops; no duplicate effects across restart; measured cost advantage over naive giant-session control.

#### Principal Architect (MS-PRINCIPAL)

Owns system evolution under constraints: constitutional constraints; alternatives and reversal; blast radius; stable ports; one runtime authority; preregistered experiments; reject complexity without measured lift.

| Axis | Requirement |
|---|---|
| Scope | Greenfield multi-package or brownfield architectural change; contracts before code |
| Default topology | `architect-plan` (single writer) then implementer; reviewer has no admit authority |
| Abilities | Extract requirements, write ports/types first, synthetic failing oracle, topological file DAG |
| Artifacts | Architecture notes in \(\sigma.settled\_invariants\), oracle digest, scaffold |
| Verification | Oracle fail-on-stub then pass-on-impl; no test mutation |
| Completion gate | Behavioral oracle + smoke + files exist; greenfield completeness policy |
| Internal criterion | Greenfield suite \(n\ge 15\) with oracle-vacuity checks |
| External | DeepSWE’s original tasks are closer than mined SWE-bench; still not “principal architect” |

**Done (A §29.3):** successful repository-wide migration tasks; explicit alternative and reversal analysis; architecture invariant preservation; low change amplification on subsequent tasks; human reviewer acceptance of decision quality; no reliance on hidden benchmark conventions.

#### Tech Lead (MS-LEAD)

Owns campaign execution: WIP limits; bounded work packages; evidence and budget events; escalate; prevent duplicated ownership; close only when predicates resolve; human override. Not a privileged bypass.

| Axis | Requirement |
|---|---|
| Scope | Campaign of multiple tasks; merge policy; operator checkpoints |
| Default topology | Outer-loop director; inner loop still single-writer episodes |
| Abilities | Decompose, sequence, refuse specialist treatments without control, report missingness |
| Artifacts | CoordinationPlan, per-node receipts, campaign fold |
| Verification | Each node independently admitted; campaign success ≠ OR of conversational summaries |
| Completion gate | All required nodes signed; rollback of a node does not corrupt others’ CAS artifacts |
| Internal criterion | Campaign fixture of ≥8 nodes, one forced crash, resume of remaining DAG |
| External | Not a public leaderboard |

**Done (A §29.4):** maintains WIP and budget constraints; routes failures correctly; requests operator intervention at defined boundaries; completes or honestly terminates campaigns; produces reconstructible status from ledger alone; never bypasses exterior acceptance.

### Mapping to public benches (cautious)

| Profile | Internal suite | Public analogue (not equivalent) |
|---|---|---|
| Senior | B1-class 20 tasks **after membership repair** | SWE-bench Verified is too saturated to certify this |
| Staff | Multi-file brownfield 30+ | SWE-bench Pro public (731), Scale standardized ~55–62% frontier as of 2026-09-03 |
| Principal / long-horizon | Greenfield + original tasks | DeepSWE v1.1 (113 tasks, 91 repos); leaders 74%±1–4% on mini-swe-agent |
| Tech lead | Campaign DAG | None; do not fake one |

## 4. Post-M-10 Horizon: Octopus Outer-Loop Meta-Orchestration (`M-OCT`)

The following outcomes define the post-1.0 architectural horizon for multi-day, multi-agent campaign orchestration. They do not create a calendar or authorize work that M-8/M-9 currently block.

| ID | Horizon Outcome | Terminal Acceptance Boundary |
|---|---|---|
| **W-OCT-1** / OCT-01 | **Content-Addressed Mailbox Protocol** | Roles communicate strictly by publishing and reading content-addressed immutable message digests (`digest_of(payload)`); zero shared memory between roles; replayable multi-agent determinism. |
| **W-OCT-2** / OCT-02 | **Declarative CoordinationPlan DAG** | Topology declared as immutable data DAG with strict per-mille budget shares ($\sum \text{budget\_share} \le 1000$); formal merge policies implemented: `CONCAT`, `FIRST_COMPLETE`, `SYNTHESISE`, `UNANIMOUS`. |
| **W-OCT-3** / OCT-03 | **Outer-Loop Multi-Day Roadmap Director** | Higher-order director layer executing above `EpisodeEngine`; decomposes complex roadmaps into independent task DAGs across process boundaries without violating kernel S0–S12 contracts. |
| **W-OCT-4** / OCT-04 | **Meta-Conductor & Swarm Goal Algebra** | Formal algebraic separation and reconciliation of individual swarm agent objectives under a global parent mission; automated topology selection based on task classification. |

## 5. Parallel SWE Benchmark Program (SWE-P0–SWE-P5)

| Program | Outcome | Required Gate | Status |
|---|---|---|---|
| **SWE-P0** | Instrument-valid harness | Isolated materialization, trajectory linkage, evaluator validity, secret boundary. | `DONE` |
| **SWE-P1** | Honest baseline | Preregistered corpus/model/cost policy and explicit missingness reporting. | `APPROVED` |
| **SWE-P2** | Harness experiments | Controlled context/tool/recovery experiments with attributable receipts. | `APPROVED` |
| **SWE-P3** | Model/harness optimization | Predeclared optimization and held-out comparison without contamination. | `BLOCKED` (on P1) |
| **SWE-P4** | Controlled larger run | Budgeted larger sample, independent audit, reproducible subject identity. | `BLOCKED` (on P3) |
| **SWE-P5** | Official evaluation | Official benchmark procedure and receipt; local runs are never official. | `BLOCKED` (on P4) |

## Appendix: W-092-F* aliases

Old overlay IDs remain resolvable. They are **not** the living work board.

| Historical ID | Maps to |
|---|---|
| W-092-F0 | MS-INSTRUMENT (LDA health is CI/present-docs, not this gate) |
| W-092-F1 | MS-CONTROL path + CMX-09 |
| W-092-F2 | MS-TRUTH |
| W-092-F3 | MS-RESUME |
| W-092-F4 | MS-SEE / MS-CHANGE |
| W-092-F5 | MS-CONTROL qualification |
| W-092-F6 | MS-SPECIALIST `[PROPOSAL]` |
