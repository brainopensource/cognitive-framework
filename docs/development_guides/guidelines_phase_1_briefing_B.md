# Phase 1 — Build-to-Trust-Spine Engineering Briefing
## Task Complexity, Review Governance & Sprint Execution Guide (S1–S4)

**Audience:** Project Manager (PM), Scrum Master, Tech Lead, and Lead Developers  
**Reference Documents:** `docs/v4/13_C_gts_mvp_program_and_engineering_plan.md`, `docs/development/guidelines_phase_0_briefing.md`, `docs/sprint0/system-architecture-icd.md`, `docs/sprint0/active-mvp-contract.json`  
**Purpose:** Provide the governance overlay for Sprints 1 through 4 (the build phase that culminates in the S4 trust-spine demo). Maps task complexity (Levels 0–5), execution tracks (Fast vs. Gate), contract row activations, ownership, and merge gating to guarantee an uncompromised engineering baseline.

---

## 1. Pacing & Governance Framework

All tasks are classified into two execution tracks:

* 🟢 **FAST TRACK (Levels 0–2):** Autonomous, high-speed execution. Standard CI checks and peer review apply.
* 🔴 **GATE & REVIEW TRACK (Levels 3–5):** High design risk, kernel/TCB invariants, capability boundaries, or merge-gating rules. **Requires explicit Tech Lead / Project Lead sign-off before merging.**

### Complexity Scale (0 to 5)

| Level | Profile | Scope & Typical Activities | Governance / Pacing |
| :---: | :--- | :--- | :--- |
| **0** | Junior Dev / PM Assistant | Mechanical docs, checklist tracking, file archival | 🟢 Fast Track (Async review) |
| **1** | Developer | Basic CLI scripts, throwaway provider spikes, JSON schemas | 🟢 Fast Track (Peer review) |
| **2** | Mid Developer | Port fakes, disposable E2E slices, reader profiles | 🟢 Fast Track (CI automated gate) |
| **3** | Senior Developer | Event store reducers, ledger crash recovery, must-fail test fixtures | 🔴 Gate Track (Sr Dev + TL sign-off) |
| **4** | Lead Architect / Sr Dev | Kernel capabilities, attenuation algebra, sink mediation, artifact graph | 🔴 Gate Track (Tech Lead approval) |
| **5** | Tech Lead / Principal | Episode recursion engine, trust-spine demo, boundary laws, S4 exit review | 🔴 Gate Track (Joint TL + PL sign-off) |

---

## 2. Two-Clock Discipline for PM & Scrum

Every engineering artifact belongs to exactly one clock:

| Clock | Scope & Invariants | Lifecycle Rule | Phase 1 Examples |
| :--- | :--- | :--- | :--- |
| **Fast Clock (Enforcement / Permanent)** | Capability checks, sandbox isolation, event recording, kernel dispatch, attenuation algebra, ledger integrity | **Never expires.** Changes require an explicit ADR | `kernel/` (T2), `domain/` reducers (T3), `ports/` contracts, architecture boundary gates |
| **Slow Clock (Compensation / Temporary)** | Scaffolding compensating for model flaws; disposable experimental code built to discover live wire shapes | **Carries expiration trigger.** Must declare `compensatesFor` | `spike/` (T0a), `slice/` (T0b) — **both deleted outright at S4 exit** |

**Governance Invariant:** No slow-clock artifact may ever be promoted to a permanent fast-clock dependency. The argument to keep `spike/` or `slice/` is the signal to delete it faster.

---

## 3. Sprint 1 · Contracts, Wire Schema & Provider Spike (Weeks 3–4) — [MERGED]

| Status | Task ID | Task Summary | Complexity (0–5) | Track | Owner | Contract Row | Acceptance Evidence |
| :---: | :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| **DONE** | **T0a.1–T0a.3** | Provider API Spike in `spike/` | **1** | 🟢 FAST | Dev 3 | Backlog | `provider-notes.md` merged; `spike/` unimportable |
| **DONE** | **T1.1–T1.3** | Canonicalisation, primitives and selector algebra | **4** | 🔴 GATE | Dev 1 | `REQ-SCHEMA-001..003` | 60 tests passing; dual TS+Python readers |
| **DONE** | **T1.4–T1.6** | EffectDescriptor, CapabilityGrant and Receipt | **4** | 🔴 GATE | Dev 2 | `REQ-SCHEMA-004..006` | Contracts and wire schemas validated |
| **DONE** | **T1.7–T1.11** | Envelope, Artifact, Claim, Correction and Recording | **3** | 🔴 GATE | Dev 2 | `REQ-SCHEMA-007..011` | EventEnvelope, Artifact, Claim schemas |
| **DONE** | **T6.4** | CLI/TUI foundation — `vg run`, `vg trace`, `vg why` | **2** | 🟢 FAST | Dev 4 | `REQ-CLI-001` | Mock-backed interactive React/Ink & JSONL streaming |

---

## 4. Sprint 2 · Kernel, Ledger, Artifact Graph & Disposable Slice (Weeks 5–6)

### Parallel Execution Structure (Wave 1 vs Wave 2)

* **Wave 1 — Dev 1 (Technical & Wire Deliverables):** Wire schema correction (T1.4–T1.15), Gamma's live disposable slice & `slice-findings.md` (T0b), and artifact graph with `vg-shell-only` baseline (T7.1–T7.4).
* **Wave 2 — Dev 2 (Governance, Contracts & Verification):** Active contract row activation (`REQ-SLICE-001`, `REQ-CONF-001`, `REQ-GRAPH-001`, `REQ-BASELINE-001`), briefing synchronization, and running full CI boundary/broken gates.

### Sprint 2 Task Breakdown

| Status | Task ID | Task Summary | Complexity (0–5) | Track | Owner | Contract Row | Review Action & Gate |
| :---: | :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| **IN PROGRESS** | **T0b.1–T0b.4** | Disposable E2E Slice (`prompt → model → patch → approval → apply → test → result`) | **2** | 🟢 FAST | Dev Gamma | `REQ-SLICE-001` | Output `slice-findings.md`; verify `slice/` unimportable; marked for deletion at S4 |
| **IN PROGRESS** | **T7.1–T7.3** | Artifact Graph + `HarnessManifest`: typed files, immutable freeze at composition | **4** ⚠ | 🔴 GATE | Tech Lead + Sr Dev | `REQ-GRAPH-001` | Extensible kind registry without core changes; freeze-at-composition test |
| **IN PROGRESS** | **T1.13–T1.15** | Writer/Reader profiles, dual-language conformance & migration rehearsal | **2** | 🟢 FAST | Dev 1 | `REQ-CONF-001` | 100% agreement on golden vectors; old readers survive minor bump |
| **IN PROGRESS** | **T7.4** | `vg-shell-only` permanent baseline manifest registered and flagged undeletable | **1** | 🟢 FAST | Dev Gamma | `REQ-BASELINE-001` | Runs against fake environment; standing zero-assumption control |
| **DONE** | **T2.1–T2.5** | Kernel capabilities, attenuation algebra, and budget lease trees | **4** ⚠ | 🔴 GATE | Dev Beta | `REQ-KRN-001` | Attenuation monotonicity; budget conservation; alertable denials |
| **DONE** | **T3.1–T3.5** | Event store, pure reducer `(State, Event) → State`, replay digest identity | **3** | 🔴 GATE | Dev Alpha | `REQ-LEDGER-001` | Reduction associativity; state reconstruction; projection rebuild |

---

## 5. Sprint 3 · Full Dispatch, Mediation & Ledger Recovery (Weeks 7–8)

| Status | Task ID | Task Summary | Complexity (0–5) | Track | Owner | Contract Row | Exit Invariant |
| :---: | :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| **PLANNED** | **T2.6–T2.10** | Kernel dispatch + sink-class mediation: no privileged effect without grant; all effects recorded | **4** ⚠ | 🔴 GATE | Dev Beta + TL | `REQ-KRN-002..003` | Fault injection on all dispatch paths; must-fail MF-KRN-008..010 green; TCB LOC alarm active |
| **PLANNED** | **T3.6–T3.8** | Ledger recovery + cassettes: external recovery scanner, immutable uncertainty, cassette replay | **3** | 🔴 GATE | Dev Alpha + Sr Dev | `REQ-LEDGER-002` | `kill -9` recovery test; external terminal record writer; byte-identical cassette playback |

---

## 6. Sprint 4 · Episode Engine, Trust-Spine Demo & Exit Gate (Weeks 9–10)

> ⚠ **Hardest milestone in the programme.** T4.1–T4.7 is rated `XL ⚠` and runs with **zero LLM in the loop**.

| Status | Task ID | Task Summary | Complexity (0–5) | Track | Owner | Exit Invariant |
| :---: | :--- | :--- | :---: | :---: | :--- | :--- |
| **PLANNED** | **T4.1–T4.7** | Episode engine + recursion — **trust-spine demo: scripted trajectory with no model** | **5** ⚠ XL | 🔴 GATE | Tech Lead + Sr Dev + 2 Dev | Denial, attenuation, budget exhaustion, atomicity, recovery, secret non-disclosure all pass |
| **PLANNED** | **T4.8** | Process engine: durable state machine resuming from ledger without replaying episode | **4** ⚠ | 🔴 GATE | Sr Dev + Dev | Restart-resume property test; states readable by non-engineers |
| **PLANNED** | **T5.1–T5.2** | Worker perimeter: rootless OS identity, mount namespace, containment report | **4** ⚠ | 🔴 GATE | Sr Dev + Dev | Mount, egress, syscall probes; unverified containment blocks publication |
| **PLANNED** | **DELETE `spike/` + `slice/`** | Outright deletion of throwaway directories | **1** | 🟢 FAST | Sr Dev | Checked gate item; absence verified by CI boundary checker |

---

## 7. S4 Exit Gate Checklist (Joint TL + PL Sign-Off)

| Gate ID | Verification Item | Acceptance Standard | Approver |
| :---: | :--- | :--- | :--- |
| **G4-01** | Trust-spine demo passes with no model | Scripted trajectory completes with 100% invariant enforcement | Tech Lead |
| **G4-02** | Process engine restart-resume | Interrupted governance resumes without replaying agent reasoning | Sr Dev + Tech Lead |
| **G4-03** | OS-level worker perimeter | Containment report passes mount, egress, syscall probes | Sr Dev + Tech Lead |
| **G4-04** | Disposable code deletion | `spike/` and `slice/` deleted; CI absence check green | Sr Dev |
| **G4-05** | Sink-class mediation | Privileged effects require grant; all effects recorded in ledger | Tech Lead |
| **G4-06** | Active MVP Contract coverage | `merged_scope_evidence_coverage = 100%` across all merged components | Scrum + Tech Lead |
| **G4-07** | Two-clock separation | Zero `compensatesFor` temporary code promoted to permanent fast clock | Tech Lead |
| **G4-08** | Formal Go for Sprint 5 | Written decision authorizing real model integration | **Project Lead** |

---

## 8. Continuous CI Controls & Active MVP Contract Matrix

* **Coverage Metric 1:** `baseline_assignment_coverage = 100%` (34/34 rows assigned to component, owner, test ID).
* **Coverage Metric 2:** `merged_scope_evidence_coverage = 100%` (Every merged component has passing tests or approved justification).
* **PR Gating Rule:** Zero PRs merge if they leave a merged-scope component with an `open` requirement.
