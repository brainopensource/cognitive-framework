---
id: ROAD-MILE-01
file: docs/02_roadmap/milestones.md
title: "Vanguard / GTS — Technical Milestone Specification (v0.5.0 → v1.0.0)"
version: 1.0.0
status: NORMATIVE-TRAJECTORY
authority_scope: >
  Evolutionary trajectory of the backend kernel, agency, runtime, adapters, measurement laboratory,
  and (from v1.0.0) Interaction-plane products. Does not replace living sprint boards.
owners: [Project Lead, Tech Lead]
last_reviewed: 2026-08-18
baseline_asbuilt: "v0.4.5-beta (feat/harness-cli-v045)"
---

# Vanguard / GTS Technical Milestones — v0.5.0 → v1.0.0

This document is the **versioned scientific programme** for taking the as-built v0.4.5-beta runtime to a
sovereign v1.0.0 product. It is written against four facts that the 2026-08-18 audit made load-bearing:

1. The **episode loop** (`observe → propose → authorise → effect → receipt`, exterior `evaluate`) is the
   only execution primitive (`A-01`). Application coordinators may *schedule* episodes; they may not
   become a second workflow engine (`REJ-01`).
2. The **attenuation kernel** (`S0`–`S12`) is the keep-set. v0.5.0 is a **composition-and-honesty** cut,
   not a kernel rewrite (`SYSTEM_SPEC_DRIFTS.md` §2.5, §4.1).
3. **`S_t = (G_C, G_E, L, A_t)`** is the persistent object (VG-02). At v0.4.5 only \(L\) is real. Later
   versions instantiate the other three components; they do not invent a second store of truth.
4. Vision tiers (EXEC-01) are **explanatory mapping**, not runtime ontology (`REJ-10`). Code, schemas,
   and CI cite `A-*`, `K-*`, `REQ-*`, and `D-*` identifiers — never “Tier 07 cell.”

**Corpus (read in this order on conflict):** living sprint boards → this file’s *exit criteria* →
`docs/main_v4/` (VG-00…VG-12, GTS-13C) → `SYSTEM_SPEC_THEORY.md` → `SYSTEM_SPEC_DRIFTS.md` →
`SYSTEM_SPEC_ASBUILT.md` (photograph of v0.4.5). Frontend law: `docs/scrum/roadmap_frontend.md` and
`docs/front_v4/` short files. Interaction surfaces are **not** a backend gate before v1.0.0 (`A-09`).

---

## 0. How to use this document

| Kind | Meaning |
|---|---|
| **Invariant** | Holds at every version; a regression is a release blocker. |
| **Gate** | Boolean predicate; the version **does not ship** if false. |
| **Wave** | Ordered work package inside a version; named after DRIFTS §4.4 where applicable. |
| **DEF/REJ** | Honour table: deferred or rejected. Opening one early is a programme error, not a stretch goal. |
| **Proof** | Command, must-fail ID, or measurement protocol that *is* the criterion. |

A milestone is **complete** iff every Gate in its section is true *in production wiring*, not merely as a
library or a fixture (`SYSTEM_SPEC_DRIFTS.md` rubric §3). Library presence without a call site scores 0.

---

## 1. Global objects (frozen through v1.0.0)

### 1.1 Persistent state

\[
S_t = (G_C,\; G_E,\; L,\; A_t)
\]

| Symbol | Type (informal) | v0.4.5 | First honest version |
|---|---|---|---|
| \(G_C\) | Immutable DAG of competence artifacts with content hashes | types / T1.8 wire only | **v0.8.0** |
| \(G_E\) | Directed graph of claims, evaluations, contradictions, invalidations | `Claim` fields; no walker | **v0.8.0** |
| \(L\) | Append-only typed event ledger | SQLite WAL + JSONL; 11 of 34 kinds emitted | **v0.5.0** (closed writer) |
| \(A_t\) | Activation set (which artifacts may enter context as data) | empty / prior-only | **v0.8.0** (policy); **v0.9.0** (evolution pointer) |

**Law (`A-07`).** Every surface is a projection of \(L\). Graphs \(G_C, G_E\) are *derived stores* admitted
only through the claim pipeline (VG-06). They never authorise effects (`MEM-3`, `MEM-4`).

### 1.2 Episode as the execution primitive

\[
E = (\mathit{Task},\; \mathit{EnvSnapshot},\; A_t,\; B,\; \Pi)
\]

where \(B \in \mathbb{Z}_{\ge 0}^4\) is the reservation
\(\{\texttt{usd\_micros},\;\texttt{millis},\;\texttt{tokens},\;\texttt{bytes\_}\}\) (X-14 freeze) and
\(\Pi\) is the frozen harness policy (kinds, packs, approval axis).

**Turn protocol** (VG-03 §2.1), with evaluation *not* in the worker loop (`D-03` keep):

```text
observe → propose → authorise → effect → receipt     # EpisodeEngine
                                          └─► L.append(EpisodeCompleted | …)
L listener (Evidence plane) ─► EvaluationRequested ─► IsolatedEvaluator
```

**Single-effect law** (keep): a proposal with \(|\mathit{actions}| \neq 1\) is
`instrument_error:multi_action_proposal`. Parallelism is a later *independence-group* construct (`A-06`,
`CC-*`), not batched tool calls.

### 1.3 Dispatch (the only effect path)

All privileged and recorded effects traverse `Kernel.dispatch` (`AT-01`, `D-01`). Sink class (ADR-0051):

\[
\mathrm{sink}(a) \in \{\texttt{pure},\;\texttt{observation},\;\texttt{privileged}\}
\]

\[
\mathrm{requires\_grant}(a) \iff \mathrm{sink}(a)=\texttt{privileged}
\]

**All three classes still execute S1–S5 and S7–S12.** Observations are not a kernel bypass (`D-04`).
Amend VG-02 `A-03` in v0.5.0 spec wave; do not revert to universal grants.

**Security claim S1** (VG-05) remains the top-level theorem. v0.5.0 makes clauses (d) and (e) *true in
composition* (provenance wiring). Clauses (f) and (g) become testable at v0.8.0 / v0.9.0 when activation
and evolution exist.

### 1.4 Authority predicate (clause S1(e))

Let \(\Sigma_t\) be the monotone accumulation of justifying spans. A privileged effect \(e\) is legal iff
every widening is justified by a span whose trust class is not derived solely from untrusted content
(`K-31`, `K-33`).

**v0.4.5 defect (`D-05`, `D-06`):** `_admit_turn_result` returns `None`; `spawn()` does not call
`Accumulation.child_return`. Until those call sites exist, **S1(e) is unclaimed**.

### 1.5 Policy-kernel size tripwire

\[
|\mathrm{kernel}|_{\mathrm{LOC}} \le 1438
\quad\text{(alarm; ADR-0054 to grow)}
\]

As-built: **1333 / 1438** across nine files. No version may grow this without an ADR. Cognition, coding
workflows, indexers, GUIs, and model kits **live outside** `vanguard/packages/kernel/`.

Declare in the TCB list (`K-02`, `D-48`): OS, bwrap, SQLite, evaluator image, Ed25519/`cryptography` on
the approval path. Concealing a dependency does not remove it.

### 1.6 Planes and identities

| Plane | OS identity (Phase 0 topology) | First complete version |
|---|---|---|
| Interaction | Client processes; no adapter handles (`A-09`) | v1.0.0 product; wire from v0.5 |
| Cognition | Controller / episode engine | v0.5 (loop honesty); operators-as-data v0.9 |
| Control | Same process, audited module boundary + governance | v0.5 (ledger approvals) |
| Workload | Sandboxed worker (rootless bwrap) | v0.5 live writes; v0.6 extra environments |
| Evidence | **UID 10002** evaluator daemon — **K-40 inverted, keep** (`D-32`) | v0.5 trigger via \(L\) |
| Evolution | Separate promotion identity; pointer moves, not file writes | **v0.9.0** (0% as-built) |

### 1.7 Vision-tier mapping (quarantined)

| Vision tier | Engineering object | Honest from |
|---|---|---|
| 0–2 | Bits, clocks, SHA-256, RFC 8785 JCS, JSON Schema 2020-12 | already |
| 3 | Identity, ledger \(L\), integer budgets | v0.5 closed writer |
| 4–5 | Verb table + `Kernel.dispatch` + grants + sandbox | keep; freeze ADR-0051 |
| 6 | Manifests, L1–L5 compactors, `ProposalTranslator` | v0.5–v0.6 |
| 7 | `HarnessSession` / workspace metabolism | v0.5 live cell |
| 8 | Immune = kernel; sensory = evaluator; circulatory = \(L\) | v0.5 |
| 9 | Integrated agent (one `vg` identity, modes INTERACTIVE/BENCHMARK) | v0.6–v0.7 |
| 10 | Role swarms / hats | v0.9 (not a second loop) |
| 11 | \(G_C, G_E\), attestation | v0.8 |
| 12 | Non-coding biomes | v0.6 H0 + v0.8 transfer (`C-10`) |
| 13 | Closed-loop distillation under SA-1…SA-6 | v0.9–v1.0; **never autonomous R0/R1** (`NC-10`, `M-24`) |

---

## 2. Invariants (all versions)

These are non-negotiable. A later milestone that violates one is invalid even if its local gates pass.

| ID | Invariant | Proof sketch |
|---|---|---|
| I-01 | `A-01`: no runtime DAG/workflow engine | `check_boundaries.py` + absence of a node registry that *dispatches* |
| I-02 | `AT-01`: one `Kernel.dispatch` path | architecture test; no second privileged adapter table |
| I-03 | `A-05` / CL-1: evaluator unreachable from agency | import ban + unreadability probe (`IsolatedEvaluator`) |
| I-04 | BENCHMARK / `interactive=False` is fail-closed on privileged writes | no YOLO; AutonomousGrant is INTERACTIVE-only |
| I-05 | One effect per turn | translator + `multi_action_proposal` |
| I-06 | Clients do not hold adapter handles (`A-09`) | FE scopes; no MCP-as-authority (`ADR-0066`) |
| I-07 | Measurement apparatus stays in `lab/` + `tools/telemetry/` (`D-40`) | package lattice |
| I-08 | `REQ-*` is the PR requirement namespace (`D-45`) | `check_pr_requirements.py` |
| I-09 | Playbooks, if present, **constrain never dispatch** (`N-20`) | no `CodingRunCoordinator` in kernel; rigidity is data |
| I-10 | Self-mod: Evolution moves **activation pointers**, never live TCB files (`SA-*`) | no updater in v0.5–v0.8 (`DEF-07`) |

---

## 3. v0.5.0 — Empirical Baseline (“S-truth + live coding cell”)

**Vision name:** Empirical Seed.  
**Cosmological band:** Tiers 0–7 made *honest*, not metaphorical.  
**Predecessor:** v0.4.5-beta. Kernel libraries exist; composition lies (`D-05`–`D-15`).  
**Thesis:** A greenfield coding harness is only a product if the ledger, provenance predicate, and grant
token that bound it are true in production.

### 3.1 Formal target

Let \(\mathcal{W}\) be a workspace, \(g\) a signed `AutonomousGrant`, \(M\) a live `ModelPort`.

A **v0.5.0 run** is a sequence of episodes \(\{E_i\}\) such that:

1. \(\forall i:\; E_i\) is reduced by `EpisodeEngine` (not by a hidden effect loop inside the coordinator).
2. Every privileged write \(w\) satisfies \(\mathrm{selector}(w) \subseteq \mathrm{scope}(g)\) and
   \(\mathrm{cmd}(w) \in g.\texttt{commandAllowlist}\) when \(w\) is `proc.exec`.
3. \(\mathrm{digest}(\mathcal{W}_0)\) is bound in \(g\) (workspace digest constraint).
4. `--in-place` means the environment adapter’s `patch.apply` / write sink mutates \(\mathcal{W}\) under
   the sandbox, **not** a fake projection (`live: true`).
5. On `EpisodeCompleted` (terminal axis), an Evidence-plane listener emits `EvaluationRequested`; the
   worker never calls `HarnessSession._evaluate` as the *sole* trigger (`D-02`).

**Coordinator law.** `CodingRunCoordinator` may remain as an *application scheduler* of episodes
(DISCOVER…FINAL_VERIFY as **labels on successive \(E_i\)**). It is **illegal** for it to:

- dispatch effects,
- bypass `Kernel.dispatch`,
- or treat the model as a leaf that cannot choose verbs inside an episode.

v0.5.0 does **not** introduce a playbook interpreter. Distillation of that FSM into a `guided` playbook
is a **v0.9.0** artefact (`D-36`).

### 3.2 State machine — session honesty

```text
[*] → COMPOSE(FrozenHarness)
    → EPISODE_START { emit EpisodeStarted }
    → TURN { propose → Kernel.dispatch → receipt; spans accumulate }
    → (optional) APPROVAL_WAIT { ApprovalRequested; resume iff ApprovalResolved ∈ L }
    → EPISODE_TERMINAL { EpisodeCompleted }
    → EVAL_REQUEST { EvaluationRequested from ledger listener }
    → EVAL_CLAIM { IsolatedEvaluator; signed verdict }
    → [*]
```

**Must emit (closes D-11…D-15, writer set):**  
`EpisodeStarted`, `EpisodeCompleted`, `ProposalProduced`, `AuthorizationDenied`, `CapabilityGranted`
(S6), `BudgetReserved`/`BudgetCommitted` (or kinds removed by ADR), `EffectStarted`/`Completed`/
`Reconciled`, `ApprovalRequested`, **`ApprovalResolved` on \(L\)** (not only an in-process queue),
`EvaluationRequested`, `RunRecovered`/`RunAborted`, `KernelAlarm`/`EffectRejected` **∈ `EVENT_KINDS`**.

Unknown `payload.kind` is **rejected at the writer** (`D-11`).

### 3.3 AutonomousGrant (already in tree)

`runtime/autonomous_grant.py` is an **emergent protocol** (keep). Formal envelope:

\[
g = \mathrm{Sign}_{sk}(\mathit{JCS}(\{\mathit{workspace},\;\mathit{verbs},\;\mathit{cmds},\;
B_{\max},\;T_{\max},\;t_{\mathrm{exp}},\;\mathit{digest}\}))
\]

| Field | Semantics |
|---|---|
| `workspaceRoot` + digest | Exact tree; grant dies on unexpected mutation of the bound digest |
| `allowedVerbs` | Subset of the periodic table (`fs.read`, `fs.search`, `patch.apply`, `proc.exec`, …) |
| `commandAllowlist` | Further attenuation of `proc.exec` |
| `maxTurns` / `maxAttempts` / `maxBudgetMicros` | Hard ceilings; kernel `Governor` still accounts \(B\) |
| INTERACTIVE vs BENCHMARK | Privileged writes require \(g\) or a human approval; BENCHMARK cannot mint \(g\) |

### 3.4 Waves (ordered)

| Wave | Outcome | Closes |
|---|---|---|
| **S-truth** | Wire `receipt_labeller` / `_admit_turn_result`; `spawn` → `child_return`; lifecycle events; `EVENT_KINDS` closed | D-05, D-06, D-11–D-15 |
| **S-spec** | Patch VG-02/03/04/05 to ADR-0051, inverted K-40, F-21a alarm, LT+governance, MF ID bijection; `CI-9` fails on gaps | D-04, D-25, D-32, D-44, X-* |
| **S-eval** | Ledger listener owns evaluation trigger; RPC remains transport, not authority | D-02 |
| **S-product** | Live `ModelPort`; `--in-place`; AutonomousGrant on INTERACTIVE; Q2 dogfood DOGFOOD-01..03 + one greenfield | Board TODOs, live:false |
| **S-hygiene** | `_fake_backend` out of `coding_entrypoint.py` → `test/`; `RegroundPolicy` wired **or** deleted; README `REJ-10` | D-10, D-46, D-47 |

**Explicitly not in v0.5.0:** operators-as-data, playbooks, \(G_C/G_E\) engine, independence groups,
seccomp-unless-reviewable, kernel rewrite, TUI/GUI as backend gates, moving `lab/` into packages.

### 3.5 Exit criteria (non-negotiable)

| Gate | Proof |
|---|---|
| **G-050-01** S1(e) in production | Must-fail: tool-result span is `UNTRUSTED_EXTERNAL`; widening from it denied. `MF-KRN-002` equivalent against **composed** `HarnessSession`, not a fixture-only kernel |
| **G-050-02** Child provenance | Spawned child accumulation includes `child_return`; test kills parent mid-child |
| **G-050-03** Ledger beginning | `EpisodeStarted` written from `vanguard/packages/` |
| **G-050-04** Approval replay | `ProcessEngine` can resume from store-only `ApprovalResolved` |
| **G-050-05** Evaluation exteriority | Killing the session process still yields `EvaluationRequested` from a ledger watcher **or** documented compensating control + ADR if topology cannot; worker cannot import evaluator |
| **G-050-06** Live writes | `live: true` greenfield: files exist on disk; tests go RED→GREEN via `proc.exec`; **un-mocked** `oracle_green` on at least one `lab/tasks/greenfield-*` task with a named live model |
| **G-050-07** Grant bound | Attempted write outside `g` denied; BENCHMARK refuses privileged write without human/test approver |
| **G-050-08** TCB | `python3 tools/check_tcb_budget.py` PASS; kernel ≤ 1438; no kernel growth without ADR |
| **G-050-09** Lattice | `python3 tools/check_boundaries.py` PASS |
| **G-050-10** Honesty of tests | `CI-9` retargeted to live `MF-KRN-*`/`MF-S0-*` roster **and fails** on gaps; or map rewritten with bijection |
| **G-050-11** Spec freeze | `A-03` text matches ADR-0051; K-40 text matches separate UID evaluator |
| **G-050-12** One grant shape | Kernel grant and wire grant agree (X-07) **or** explicit translator with golden vectors |

**`oracle_green` definition (this programme):** a task workspace whose tests start failing, the agent is
not shown gold patches, the evaluator image is pinned, and the verdict is signed. MOCK/`live: false`
**does not** satisfy G-050-06. A scripted `_fake_backend` **does not** satisfy G-050-06.

### 3.6 Security invariants added

- F-21a (`INTENT_APPEND_FAILED`) remains a `KernelAlarm` (keep `D-18`).
- Interrupted VERIFY must not invent success (coordinator resume path — distinct from F-21a).
- `publication_decision` still blocks unverified perimeters (`K-44`).

---

## 4. v0.6.0 — Decoupled Micro-Kernel Substrate

**Vision name:** Molecular Lattice.  
**Thesis:** The coding cell is the first *client* of the runtime, not its ontology (VG-02 §1.2). Hexagonal
ports become the only way a domain appears.

### 4.1 Formal target

Let \(\mathcal{P}\) be the closed port set after `compose()` (`K-03`, `D-26`):

\[
\mathcal{P} = \{\texttt{ModelPort},\;\texttt{EnvironmentAdapter},\;\texttt{IndexPort},\;
\texttt{SandboxRunner},\;\texttt{ClockPort},\;\texttt{RandomPort},\;\texttt{EventStore},\;
\texttt{BlobStorePort},\;\dots\}
\]

A **domain pack** \(D\) is a `FrozenHarness` (manifest + genes + aliases). Binding:

\[
\mathrm{Runtime}(\mathcal{P}, D) \quad\text{with}\quad
\mathrm{coding\_*} \not\subset \texttt{vanguard/packages/runtime/}
\]

**H0 (generality):** there exists a registered non-coding environment \(D_{\neg c}\) (TableWorld or
successor) that is a real `EnvironmentAdapter`, appears in `registry.json`, and completes an episode
**without** importing `coding_*` (`C-10` partial; full transfer remains v0.8+).

### 4.2 Refactor theorems

| Move | From | To |
|---|---|---|
| `coding_coordinator.py`, `coding_plan.py`, … | `runtime/` | application package e.g. `vanguard/packages/apps/coding/` **or** a pack-local interpreter that only schedules episodes |
| `domain/ledger/coding_session.py` | `domain/` | app projection (`D-42`) |
| Model routing | `model_selection.py` + `tier_escalation.py` + coordinator `_route` | **one** `ModelRouter` port implementation; coordinator delegates only |
| Context policy | hard-coded STATUS.md / dead `RegroundPolicy` | `context_policy` + live `RegroundPolicy.shouldRun` as observation effects |
| Environments | Git-shaped adapter only | Git + TableWorld (or cut TableWorld from Phase 0 claims — no orphans, `D-27`) |

**Playbooks:** still **DEF** as a *runtime*. Optional: extract the eight-phase coding FSM into a **data**
playbook at rigidity `advisory` only, executed by the same `EpisodeEngine`. If a playbook module *calls*
tools, the version **fails I-09**.

### 4.3 State machine — composition

```text
kinds.json + pack  → validate → FrozenHarness
         → bind ports (fail unknown names)
         → HarnessSession
         → EpisodeEngine  (unchanged)
```

Plugin languages (ADR-0059): Tree-sitter, browsers, etc. attach **across the wire**, never inside
`kernel/`.

### 4.4 Exit criteria

| Gate | Proof |
|---|---|
| **G-060-01** | `runtime/` has **zero** `coding_*.py`. `check_core_changes.py` / M11 holds on `domain/` |
| **G-060-02** | Second environment: registered pack + adapter tests + one measured episode; **or** pack deleted and Increment C struck from Phase 0 |
| **G-060-03** | New environment = new adapter + manifest **without** kernel/agency patch (`C-03` language-swap still later) |
| **G-060-04** | Single `ModelRouter`; duplicate heuristics gone; tests show role → model map is configuration |
| **G-060-05** | `format_skill_index` is called from `ContextCompiler` (or equivalent L-layer), not only exported |
| **G-060-06** | `RegroundPolicy` invoked from the engine **or** module deleted and VG-03 §6.4 deferred explicitly |
| **G-060-07** | TCB still ≤ 1438; boundaries PASS; no `OperatorRunner` fake-as-layers (`D-35`) |
| **G-060-08** | `root.py` split: composition vs session vs evaluator transport as distinct modules (LOC not a vanity metric; **no new god-object**) |

---

## 5. v0.7.0 — Comparative Benchmarking & Model Kits

**Vision name:** Organism Benchmark.  
**Thesis:** Topology, cache, and model ensemble are **empirical objects** under VG-07, not folklore.
Measurement stays outside `vanguard/packages/` (`I-07`).

### 5.1 Formal target

An **instrument tuple** (VG-04 §3.12 / VG-07) for configuration \(\theta\):

\[
I(\theta) = (\mathit{cost},\; \mathit{latency},\; \mathit{turns},\; \mathit{tokens},\;
\mathit{oracle},\; \mathit{split},\; \mathit{seed})
\]

A **model kit** \(K = (M_{\mathrm{plan}}, M_{\mathrm{exec}}, M_{\mathrm{diag}}, M_{\mathrm{review}})\)
is a frozen routing policy. Bake-off:

\[
\theta^\star \in \arg\min_{\theta} \;\mathbb{E}[\mathit{cost}]
\quad\text{s.t.}\quad
\mathbb{P}(\mathit{oracle}=\texttt{green}) \ge \tau
\]

Pareto front reported on \((\mathit{cost}, \mathit{latency}, 1-\mathbb{P}(\mathrm{green}))\). **No
optimizer-in-the-loop** on the evaluation split (`S19-B-02` / LAR). A/A refuse and split-burn rules
remain (`D-40`).

### 5.2 IndexPort body

`IndexPort` is observation-only (S10-A-03). v0.7.0 **replaces the regex body** with Tree-sitter (or
equivalent) **without moving the port** (`ADR-0059`):

\[
\mathrm{Index}: \mathcal{W} \to \mathrm{RepoMap}
\quad
\mathrm{Index} \not\ni \{\texttt{propose},\;\texttt{dispatch},\;\texttt{rank\_for\_effect}\}
\]

Prompt cache: prefix-stable L1–L4; measure cache-hit rate vs compaction loss. Default compaction stays
recency-window until a **consolidation-loss experiment** beats it (`D-37`).

### 5.3 Parallelism

Independence groups (`CC-1`…`CC-7`) may appear as an **experimental** driver behind a flag. Production
default remains sequential until **CC-6 can emit** and `C-04` is measured (`D-38`). Fan-out without
branch-isolated snapshots is a defect.

### 5.4 Exit criteria

| Gate | Proof |
|---|---|
| **G-070-01** | Tree-sitter (or named indexer) behind `IndexPort`; port tests still forbid propose/dispatch |
| **G-070-02** | Prompt-cache metrics in `tools/telemetry/` from ledger, not logs scraped ad hoc |
| **G-070-03** | Published bake-off: ≥3 kits × ≥N tasks, **un-mocked** models, holdout split, M-18 tuple refusal on missing fields |
| **G-070-04** | Pareto figure + machine-readable JSON; no claim of “best model” without \(\tau\) and split ids |
| **G-070-05** | `oracle_green` rate on the frozen lab corpus with CI excluding zero (`C-06` *not* yet — that needs \(G_C\)) |
| **G-070-06** | Spend path: S9-J-03 authorised or kits restricted to free band with fail-closed paid |
| **G-070-07** | TCB unchanged; polyglot indexer not imported by `kernel/` |

---

## 6. v0.8.0 — Cognitive Layer & Memory Graphs

**Vision name:** Cellular Cortex (Tier 11 objects, still no Evolution plane).  
**Thesis:** Instantiate \(G_C\) and \(G_E\) as **derived, gated stores**. Do not give them effect
authority (`MEM-3`, `MEM-4`, S1(f)).

### 6.1 Graphs

**Competence graph** \(G_C = (V_C, E_C)\):

- \(V_C\): content-addressed artifacts (T1.8: `class`, `compensatesFor`, `hypothesis`, `riskDelta`).
- \(E_C\): typed relations (refines, specialises, conflicts-with — freeze in VG-06, do not resurrect dual
  `CompetenceArtifact` shapes).

**Evidence graph** \(G_E = (V_E, E_E)\):

- \(V_E\): `Claim` nodes (origin episode, protocol, evaluator digest, validity domain, hedge fields).
- \(E_E\): supports, contradicts, invalidates, reproduces.

**Contradiction traversal:** a query \(\mathrm{Contra}(c)\) returns a (possibly empty) set of claims
whose validity domains overlap and whose propositions are formally or evaluator-declared incompatible.
**Absence of a graph database product is allowed**; absence of indexing and a walker is **not**.

### 6.2 Claim pipeline (VG-06) as a state machine

```text
episodic(L) → EXTRACT → candidate
            → SCHEMA+PROVENANCE
            → CONTRA_SEARCH(G_E)
            → CORROBORATE | REPRODUCE
            → QUARANTINE
            → ACTIVATE ⊂ A_t   # still data in context, not instruction authority
            → ATTRIBUTE outcomes
            → DEMOTE | EXPIRE
```

**Activation** \(A_t\) is a filter, not a grant issuer. Recall is labelled so it cannot justify
capability widening (`MEM-4` = S1(e) for memory).

### 6.3 Episodic memory vs working memory

| Store | Retention | Enters context as |
|---|---|---|
| Working | episode view, L1–L5 | assembled blocks with provenance |
| Episodic | \(L\) + optional blob projections | receipts, not advice |
| Semantic | \(G_E\) claims | `Trust` class ≠ OPERATOR |
| Competence | \(G_C\) | skills/methods; still non-authoritative |

Cross-session continuity = replay from \(L\) + retrieval from \(G_E/G_C\), **not** a hidden chat dump.

### 6.4 Self-tuning context (not self-mod of TCB)

Budgeted compaction policy may be selected by evidence (`structured_consolidate` vs recency) **only
after** G-070-style measurement. Changing L4 brief exemption is **forbidden** (`N-21`).

### 6.5 Exit criteria

| Gate | Proof |
|---|---|
| **G-080-01** | Relation index + contradiction query with golden graphs; not “dataclass exists” |
| **G-080-02** | Pipeline must-fails: unevidenced claim cannot look like corroborated (`vg why` already started this) |
| **G-080-03** | Ablation: with \(G_C\) vs without, on **holdout** tasks; lift above null floor **or** no promotion (`C-06`) |
| **G-080-04** | Turn/token **learning curve** on a frozen series: median turns strictly decrease **or** report failure honestly |
| **G-080-05** | `CompetencePriorRecorded` / `EvidenceClaimProduced` emitted from production, not tests only |
| **G-080-06** | No `ActivationChanged` from the Evolution plane yet (that is v0.9); v0.8 activation is evidence-policy only |
| **G-080-07** | S1(f) must-fail: claim cannot widen a grant |
| **G-080-08** | TCB still excludes graph engine; walker in agency/adapters |

**Non-goal:** `CandidateBuilt` / `CanaryPromoted` (Evolution). Scaffolding “self-optimization” in v0.8
means **policy selection under evidence**, not rewriting `kernel/`.

---

## 7. v0.9.0 — Meta-Cognitive Architecture

**Vision name:** Tribal Swarm.  
**Thesis:** Cognition becomes **data** (`A-02`): operators, playbooks, hats. Evolution plane exists as a
**gated pointer mover**. Dual-process and uncertainty are explicit types, not prompt poetry.

### 7.1 Operators as addressable objects

A **cognitive operator** \(O\) is content-hashed, versioned, and selected by `operatorPolicy.select`:

\[
O = (\mathit{id},\; \mathit{digest},\; \mathit{brief},\; \mathit{allowed\_verbs},\; \mathit{model\_kit})
\]

`_LayeredOperator` as a private wrapper is **retired**. Extensions: pack gene, registry entry, or
spawned child with sealed scope (`ADR-0067`) — one composition mechanism.

**Hats (Tier 10)** are operators + briefs (Architect, Executor, Skeptic, Synthesizer), **not** four
engines. Switching hats is `OperatorSelected` / `OperatorInvoked` on \(L\).

### 7.2 Playbooks (methodology as data)

Rigidity \(\rho \in \{\texttt{advisory},\;\texttt{guided},\;\texttt{strict}\}\) (VG-03 §2.11).

| \(\rho\) | Engine behaviour |
|---|---|
| advisory | L5 injection; agent may ignore |
| guided | phase order; skip requires recorded justification |
| strict | phase gates; equivalent to a graph **as a parameter**, not as the runtime (`REJ-01` still holds) |

Levers: tool masking (attenuation), L5 notes, gate evaluation. **The playbook never dispatches (`N-20`).**
The v0.4.5 `CodingPhase` FSM, if still useful, is **compiled into** a playbook, then deleted from
application Python.

**Earned, not authored:** promotion uses the v0.8 improvement relation; decay demotes (`C-12`).

### 7.3 Dual-process (System 1 / System 2)

Not a second kernel. A **routing policy** over operators:

- **S1 (habitual):** cheap kit, advisory playbook, high prior in \(G_C\).
- **S2 (deliberative):** expensive kit, guided/strict playbook, Skeptic hat, extra observations.

Switching criterion is a **declared function** of epistemic state (below), budget remainder, and
failure fingerprints — logged as `OperatorSelected` reasons. No hidden `MetaLoopEngine` (`D-41` stay
deleted).

### 7.4 Epistemic uncertainty

Extend context blocks (VG-04 §3.5) with a first-class uncertainty record:

\[
u = (\mathit{kind},\; \mathit{hedge},\; \mathit{domain},\; \mathit{invalidation})
\]

using existing hedge fields (`ADR-0068`). **Abstain** remains a legal proposal. Undeterminable external
effects stay undeterminable (`C-11`, F-22 family) — never coerced to success.

### 7.5 Evolution plane

Events that must become real (today: never emitted):

`CandidateBuilt`, `CandidateAttested`, `CanaryPromoted`, `RollbackTriggered`, `ActivationChanged`.

**Promotion relation** (sketch): candidate \(c\) beats incumbent \(a\) on holdout, does not regress
safety, carries INV conditions, and is **human-gated for R0/R1** (`M-24`, `NC-10`). Evolution **updates
\(A_t\) pointers**; it does not write kernel files (`SA-1`…`SA-6`).

### 7.6 Concurrency (production)

If `C-04` was evidenced in v0.7 experiments, enable independence groups in production: branch-isolated
workspaces, CC-6 events, join by evaluator — still one effect per *turn per branch*.

### 7.7 Exit criteria

| Gate | Proof |
|---|---|
| **G-090-01** | Operator registry: replace operator without agency/kernel edit (`A-02`) |
| **G-090-02** | Playbook `strict` recovered as data; no Python phase enum in `runtime/` |
| **G-090-03** | Hats observable on \(L\); Skeptic cannot be skipped on `strict` security playbooks |
| **G-090-04** | S1/S2 switch has a must-fail: budget exhaustion cannot silently drop S2 when policy forbids |
| **G-090-05** | Uncertainty: abstain and undeterminable receipts round-trip on wire + replay |
| **G-090-06** | Evolution canary + rollback drill; `ActivationChanged` only from Evolution identity |
| **G-090-07** | Distillation: at least one playbook or operator beats unguided baseline on holdout (`C-06`) |
| **G-090-08** | High-ambiguity task protocol published (time-bounded, human abort); **no AGI claim** (`NC-01`) |
| **G-090-09** | TCB; Evolution code not in `kernel/`; AT-12 (capability ↛ verifier paths) **or** explicit deferral retired — **AT-12 required at this version** |

---

## 8. v1.0.0 — Unified Sovereign Product

**Vision name:** Living Cosmic Intelligence (product language).  
**Engineering name:** Interaction plane ships; backend remains the same kernel.  
**Thesis:** TUI and Tauri GUI are **pure consumers** of vg.4 NDJSON/UDS (`A-09`). “Self-assembling UI”
means **pack-driven views and skill-driven chrome**, not the model mutating client binaries.

### 8.1 Product topology

```text
                    ┌─ vg (Ink TUI)           FE-2
 Interaction        ├─ vanguard-gui (Tauri 2) FE-3
                    └─ headless / CI          lab_driver
                            │  vg.4 wire only
                    controller + broker
                            │
              worker (bwrap)   evaluator (UID 10002)
```

Frontend law (roadmap_frontend): one `@vanguard/client-core`, two skins, 1 MiB frames, **no third wire**,
**no MCP authority**, VS Code fork remains VOID.

### 8.2 Self-assembly (bounded)

Allowed: Evolution-promoted **manifests** that declare which inspector panes, skill indexes, and
approval cards to show.  
Forbidden: agent writes to `vanguard-gui/` or CLI as a privileged sink; UI code is R2/R3 at best,
signed and canaried like any other candidate.

### 8.3 Production bar

| Gate | Proof |
|---|---|
| **G-100-01** | TUI: resume, `vg why`, approvals, live UDS (frontend Waves 3–5) on **real** daemon |
| **G-100-02** | `vanguard-gui`: files, Monaco/editor, PTY, git, approve — slots in `gui_ide_slots.md` |
| **G-100-03** | Installers + soak; dogfood as daily driver **without** claiming Claude-parity unless measured |
| **G-100-04** | Backend: all G-050…G-090 gates still green on the release tag |
| **G-100-05** | Threat model: NC-03 still honest (malicious operator / kernel exploit **not** claimed) |
| **G-100-06** | S1(g): updater absent **or** SA-1…SA-6 fully evidenced; no silent self-write of R0/R1 |
| **G-100-07** | Second biome beyond coding **or** C-10 explicitly unclaimed in release notes |
| **G-100-08** | Word/schema/secret/boundary/TCB CI all hard-fail; `CI-9` honest |

### 8.4 Non-claims that survive v1.0.0

`NC-01` (AGI), `NC-05` (tests ≠ semantic truth), `NC-06` (remote models non-deterministic), `NC-11`
(transfer until ablation). v1.0.0 is a **sovereign product**, not a completed cosmology.

---

## 9. Cross-version verification matrix

| Concern | v0.5 | v0.6 | v0.7 | v0.8 | v0.9 | v1.0 |
|---|---|---|---|---|---|---|
| Kernel rewrite | forbid | forbid | forbid | forbid | forbid | forbid |
| Provenance wired | **gate** | keep | keep | keep | keep | keep |
| Live `oracle_green` | **≥1 task** | keep | **corpus** | holdout + memory | holdout + hats | product dogfood |
| `coding_*` in `runtime/` | tolerate scheduler | **zero** | zero | zero | playbook data only | zero |
| \(G_C,G_E\) walker | forbid as “done” | forbid | types ok | **gate** | + promotion | keep |
| Operators registry | forbid fake | forbid fake | kits only | optional | **gate** | keep |
| Playbook interpreter | forbid | advisory data optional | — | — | **gate** | keep |
| Independence groups | forbid prod | forbid | experiment | — | prod if C-04 | keep |
| Evolution events | forbid | forbid | forbid | no canary | **gate** | keep |
| TUI/GUI backend gate | no | no | no | no | no | **yes** |
| TCB ≤ 1438 | yes | yes | yes | yes | yes | yes + ADR if grown |
| Evaluator UID 10002 | yes | yes | yes | yes | yes | yes |

---

## 10. Dependency graph (do not skip)

```text
v0.5 S-truth ──┬── S-spec ── S-eval ── S-product ──► v0.5.0 tag
               └── (no G_C, no playbooks)

v0.5.0 ──► v0.6.0 hexagonal waist (H0 environment decision)
                │
                ▼
           v0.7.0 measurement + IndexPort body + kits
                │
                ▼
           v0.8.0 G_C / G_E / A_t (evidence policy)
                │
                ▼
           v0.9.0 operators, playbooks, hats, Evolution pointers
                │
                ▼
           v1.0.0 Interaction skins on an already-true backend
```

**Illegal shortcuts:** shipping GUI on unwired provenance; calling a coordinator a “playbook runtime”
in v0.5; scoring kernel 100% while `_admit_turn_result` returns `None`; treating TableWorld as H0
without an adapter; emitting `CanaryPromoted` from the episode worker.

---

## 11. Identifier map (programme ↔ audit)

| Programme object | Drift / REQ |
|---|---|
| S-truth | D-05, D-06, D-11–D-15 |
| Evaluation listener | D-02, D-03 |
| Sink-class freeze | D-04, X-01, ADR-0051 |
| Live coding cell | roadmap Q2, `REQ-TRUST-001`, `REQ-HAR-001` |
| AutonomousGrant | emergent; K-17 / S32 family |
| Hexagonal move | D-42, M11, ADR-0060, ADR-0059 |
| Graphs | D-23, D-39, VG-06 |
| Operators / playbooks | D-35, D-36, A-02, N-20 |
| Evolution | VG-07 / VG-03 Evolution plane, 0% as-built |
| Frontend | `docs/scrum/roadmap_frontend.md`, `A-09` |

---

## 12. Document control

| Item | Rule |
|---|---|
| Living boards | `docs/scrum/roadmap_backend.md`, `roadmap_frontend.md` remain the *sprint* truth |
| This file | Version *definition* and scientific gates; update only by Tech Lead + Project Lead |
| THEORY | Intent corpus; do not silently rewrite to match code |
| ASBUILT | Photograph; refresh on each tagged version |
| DRIFTS | Decision record for v0.5 keep/wire/amend; supersede rows here when gated |

**Next action after this file:** execute v0.5.0 Wave **S-truth** in composition (`runtime/root.py`,
episode emit sites, `spawn` provenance). Do not open a competence-graph or GUI wave until G-050-01
through G-050-07 are green.

---

*End of ROAD-MILE-01. v0.4.5 built the kernel; v0.5.0 makes it tell the truth and write real files;
v1.0.0 is skins on that truth, not a new cosmology.*
