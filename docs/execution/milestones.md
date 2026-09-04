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
version: "0.9.3"
last_verified: 2026-09-04
lock_head: "3daa487c0be8"
derived_from:
  - .draft/DEVELOPMENT_FINAL_PLAN.md
  - .draft/DEVELOPMENT_FINAL_PLAN_B.md
  - .draft/DEVELOPMENT_FINAL_PLAN_v2.md
  - .draft/PHASE-0_DEVELOPMENT_FINAL_PLAN.md
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

## 1. Scope

Stable release outcomes only. Work tree: [`tasks.md`](tasks.md). Packages: [`backlog.md`](backlog.md). Deltas: [`spec.md`](spec.md). Handbook: [`technical.md`](technical.md).

No sprint calendar. MS-* is `OPEN` until receipts exist. Package version **0.9.3** is not M-9.

Dual mission: (1) Coding Max on one `EpisodeEngine` path; (2) same substrate for other agents. CLI is a client of `ApplicationService`.

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
| **MS-TRUTH** | No `completed` without bound verification; no invented counts; one gate; **both settlement axes recorded, neither derived from the other**; greenfield vacuity rejection; anti-premature exit | T-42/T-38/T-23 landed; T-08 landed `8637db55`. Open: **T-04** (remove `ADMISSION_GATE_EXEMPT`, live at `session.py:134`, under RF-25 successor baseline), **T-05**, **T-07** (typed verification subject), **T-18 REOPENED** (`TestTamperShield` has zero production callers → wire into `session._admit_completion`), **T-72** (two-axis settlement contract), **T-81** (greenfield vacuity rejection), **T-82** (dialect fenced-action recovery & anti-premature finish). Gated on **HAR-01** preconditions T-69–T-71 and on **INS-01**/**BRG-01** (**T-84**, **T-85**, **T-87**, **T-88**): a settlement claim recorded by an instrument that reuses a fixed run id, publishes an empty receipt, or may have addressed a different model than the one launched is not evidence. **Falsifier:** a run with zero patches or tampered tests cannot earn `passed`; greenfield passing on `pass`/`NotImplementedError` is rejected via **T-81**; unsolicited `finish` proposals with 0 mutations or unparsed note actions are rejected via **T-82**; **a run may legitimately record `terminal_status=abandoned` with `disposition=passed`, and the ledger replays it without contradiction** — the disposition axis is never derived from the termination axis, nor the reverse (`ICD §3`, `VG-03 §6.2`). | `OPEN` | No-session slice `63b77116`; session parser + `ParsedTestOutput.runner` `8637db55`. **T-18 reopened 2026-09-04: mechanism present at `runtime/governance/tamper_shield.py`, unreferenced outside its own test.** |
| **MS-RESUME** | Fresh process restores episode_id, σ, L1–L3 prefix; σ not in L3 | T-09–T-13, T-43–T-44 green on commit `8637db55` | `CLOSED` | `uv run python3 -m unittest test.contracts.test_semantic_task_state test.runtime.test_task_state_fold test.runtime.test_resume_identity` — 16 tests OK (2026-09-03). σ not in L3; episode_id preserved; 40-turn fold parity. |
| **MS-SEE** | Epoch-bound packets; omissions explicit; one `ContextCompiler`; cache-stable prefix; CTRF distillation; Trailing Goal Echo; port-backed intelligence | T-14–T-16, T-36, T-37, T-45 MECHANISM. Adds: `LdaRepoIndex` backs the **unchanged** `IndexPort` over `.lda/index.db` (**80,618** relations); `repo.*` tools return bounded observations into **L5 only**; provider cache breakpoints at the L3 boundary with `cache_read_tokens` recorded; test tool receipts parsed into CTRF (passing runs omitted, failure traces capped $\le 1500$ chars); `ContextCompiler` emits Trailing Goal Echo at tail of L5 (**T-77**). **T-46 is narrowed, not erased:** optional PPR ranking may be A/B-tested inside an agent-issued query in pack policy, never in `IndexPort`, the adapter, or L1–L3. **Falsifier:** `repo.get_callers` leaves the L1–L3 digest bit-identical across 10 turns; turn ≥ 2 cache-hit rate > 85%; compiler includes trailing goal echo; no ranking logic exists in `adapters/stores/lda_index.py`. | `OPEN` (gated on **IDX-01**) | `587db91a`, `33dc7c33`, `2a4cdaad`, `179f5616`, `81b7b572`, `c7995195`. One `ContextCompiler`; omissions are a ledger; no-index fallback documented. |
| **MS-CHANGE** | Multi-file change closure; 2PC in adapters; exact edit primitive; reverse-caller admission; **zero kernel AST** | T-17 `DONE`; T-19/T-20 MECHANISM; **T-18 REOPENED**; **T-83** (greenfield prompt modernization & caller admission). T-47 amended by **T-78** (exact `str_replace`, unique preimage, trimmed-EOL only — **no fuzzy cascade**). **TLS-04 closes as mechanism-present**: `ast.parse` preflight already lives in `adapters/environment/transaction.py` and aborts before durable flush. Read-before-edit remains prompt guidance plus an A/B-able strict profile, not a universal dispatch ladder. **Falsifier:** a syntax error in file N of M leaves all M byte-identical (`tree_hash_before == tree_hash_after`); public API signature changes reject completion if dependent call sites remain uninspected (**T-83b**); greenfield prompts contain zero *"Do not read or search first"* bans (**T-83a**); strict-policy and control runs differ only by the declared read-before-edit policy; `grep -c "import ast" vanguard/packages/kernel/*.py` is **0**; `check_tcb_budget.py` reports **1386 unchanged**. | `OPEN` | `5c9870f0`, `094fa899`, `db935138`. Dialect tickets do not close this gate. |
| **MS-CONTROL** | One `EpisodeEngine` coding path; **one preset catalog**; true budget enforcement; Forge/Chimera excluded from product scores | T-23 `DONE` (≠ qualification). Open: T-26/T-27, T-51/T-52, **T-79**. `apps/coding_max/facade.py` must select from **`packs/code-default/presets.json`** (`aether.code-preset/1`: fast `$0.05`/8t/16k, balanced `$0.15`/20t/40k, max `$0.40`/40t/96k) rather than routing to three byte-identical alias manifests that share `vg-code-default/budget-policy.json` — a policy carrying **no cost and no turn dimension**. Qualify `vg-code-balanced` on the frozen multi-class canary (n ≥ 30, Wilson LB ≥ 0.40), executed **through `entrypoint.py`** (**T-89**, C-18 — a bespoke runner qualifies a different subject than the product ships) and reported under the §9 evidence standard, where **false-completion rate = 0** is a hard veto that no pass rate can override. **Falsifier:** the three presets emit **distinct** `EpisodeStarted.budgetCeiling` values matching `presets.json` exactly; `vg-code-fast` halts at turn 8 with `BUDGET_EXHAUSTED`; `max_turns` is not a Python default in the facade; canary runs execute on the exact frozen candidate SHA. **T-80 is a post-control treatment and does not gate this baseline. No specialist or director lift claim is authorized before this gate closes.** | `OPEN` (gated on **CMX-01**/T-79, T-26/T-27) | Two disjoint preset catalogs confirmed 2026-09-04; the product path reads the undifferentiated one. |
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
