# Phase 1 — Build-to-Trust-Spine Engineering Briefing
## Task Complexity, Review Governance & Sprint Execution Guide (S1–S4)

**Audience:** Project Manager (PM), Scrum Master, Tech Lead, and Lead Developers  
**Reference Documents:** `docs/v4/13_C_gts_mvp_program_and_engineering_plan.md`, `docs/development/guidelines_phase_0_briefing.md`, `docs/sprint0/system-architecture-icd.md`  
**Purpose:** Provide the governance overlay for Sprints 1 through 4 — the build phase that ends with the trust-spine demo. Maps every task to its complexity level, execution track, owner and sign-off gate. Phase 0 established the baseline; Phase 1 builds everything that must be proven correct before the first model-connected harness exists.

---

## 1. Pacing & Governance Framework

Identical to Phase 0 — the two-track model carries forward without change.

* 🟢 **FAST TRACK (Levels 0–2):** Autonomous execution. Standard CI + peer review.
* 🔴 **GATE & REVIEW TRACK (Levels 3–5):** Explicit Tech Lead / Project Lead sign-off before merging.

### Complexity Scale (unchanged)

| Level | Profile | Governance / Pacing |
| :---: | :--- | :--- |
| **0** | Junior Dev / PM Assistant | 🟢 Fast Track (Async review) |
| **1** | Developer | 🟢 Fast Track (Peer review) |
| **2** | Mid Developer | 🟢 Fast Track (CI automated gate) |
| **3** | Senior Developer | 🔴 Gate Track (Sr Dev + TL sign-off) |
| **4** | Lead Architect / Sr Dev | 🔴 Gate Track (Tech Lead approval) |
| **5** | Tech Lead / Principal | 🔴 Gate Track (Joint TL + PL sign-off) |

---

## 2. Two-Clock Discipline for PM & Scrum

Every artifact built in Phase 1 belongs to exactly one clock. PM must track which clock governs each piece of work.

| Clock | What it governs | Lifecycle | Phase 1 examples |
| :--- | :--- | :--- | :--- |
| **Fast Clock (Enforcement / Permanent)** | Capability checks, sandbox isolation, event recording, kernel dispatch, attenuation algebra, ledger integrity | Never expires. Changes require an ADR | `kernel/` (T2), `domain/` reducers (T3), port contracts, architecture tests |
| **Slow Clock (Compensation / Temporary)** | Scaffolding compensating for model flaws; disposable code built to learn | Must declare `compensatesFor` and carries an expiration trigger | `spike/` (T0a), `slice/` (T0b) — **both deleted outright at S4 exit** |

**PM action:** Every sprint review must confirm no slow-clock artifact has been promoted to a fast-clock dependency. The argument to keep `spike/` or `slice/` is the signal to delete it faster.

---

## 3. Sprint 1 · Contracts, Wire Schema & Disposable API Spike (Weeks 3–4)

### Sprint 1a — Wire schema v0.1 + provider spike

| Status | Task ID | Task Summary | Complexity (0–5) | Track | Owner | When to Review / Action |
| :---: | :--- | :--- | :---: | :---: | :--- | :--- |
| **DONE** | **T0a.1–T0a.3** | Disposable Provider API Spike in `spike/` | **1** | 🟢 FAST | Dev 3 | Merged to main via sprint1/integration |
| **DONE** | **T1.1–T1.3** | Canonicalisation, primitives and selector algebra | **4** | 🔴 GATE | Dev 1 | Merged to main — 60 tests passing, dual TS+Python readers |
| **DONE** | **T1.4–T1.6** | EffectDescriptor, CapabilityGrant and Receipt | **4** | 🔴 GATE | Dev 2 | Merged to main — contracts.ts + JSON schemas |

### Sprint 1b — Envelope, artifact, claim, recording, process + CLI foundation

| Status | Task ID | Task Summary | Complexity (0–5) | Track | Owner | When to Review / Action |
| :---: | :--- | :--- | :---: | :---: | :--- | :--- |
| **DONE** | **T1.7–T1.11** | Envelope, Artifact, Claim, Correction and Recording | **3** | 🔴 GATE | Dev 2 | Merged to main — EventEnvelope, Artifact, EvidenceClaim |
| **DONE** | **T6.4** | CLI/TUI foundation — `vg run`, `vg trace`, `vg why` | **2** | 🟢 FAST | Dev 4 | Merged to main via sprint1/dev4-tui (mock runtime) |

---

## 4. Sprint 2 · Kernel, Ledger, Artifact Graph & Disposable Slice (Weeks 5–6)

### Sprint 2a — Core infrastructure

| Status | Task ID | Task Summary | Complexity (0–5) | Track | Owner | When to Review / Action |
| :---: | :--- | :--- | :---: | :---: | :--- | :--- |
| **TODO** | **T0b.1–T0b.4** | Disposable E2E Slice: `prompt → model → patch → approval → apply → test → result` against a real repo | **2** | 🟢 FAST | Sr Dev + Dev | `slice/` unimportable by CI; output is `slice-findings.md`, not code. **Deletion checked at S4** |
| **TODO** | **T7.1–T7.3** | Artifact graph + `HarnessManifest`: every mutable component is a typed file; one edit = one commit | **4** ⚠ | 🔴 GATE | Tech Lead + Sr Dev | `kind` extension without core change; freeze-at-composition test. Requires T1.8 (S1b) |
| **TODO** | **T3.1–T3.5** | Event store, pure reducer `(State, Event) → State`, replay produces identical state digest | **3** | 🔴 GATE | Dev (Alpha) + Sr Dev | Reduction associativity property test; projection rebuild from zero. Requires T1.7 (S1b) |
| **TODO** | **T2.1–T2.5** | Kernel capabilities, attenuation algebra, budgets as lease trees | **4** ⚠ | 🔴 GATE | Sr Dev (Beta) + Tech Lead | Attenuation monotonicity; budget conservation; must-fail: verb-only attenuation reads evaluator bundle. Requires T1.3–T1.5 (S1a) |

### Sprint 2b — Conformance + permanent baseline

| Status | Task ID | Task Summary | Complexity (0–5) | Track | Owner | When to Review / Action |
| :---: | :--- | :--- | :---: | :---: | :--- | :--- |
| **TODO** | **T1.13–T1.15** | Writer/reader profiles, second-language conformance, migration rehearsal | **2** | 🟢 FAST | Dev + Sr Dev | Cross-reader conformance on golden vectors; old readers survive minor bump |
| **TODO** | **T7.4** | `vg-shell-only` permanent baseline manifest registered; flagged undeletable | **1** | 🟢 FAST | Dev | Builds and runs against fake environment. Requires T7.1–T7.3 + T3.1 |

---

## 5. Sprint 3 · Full Dispatch, Mediation & Ledger Recovery (Weeks 7–8)

| Status | Task ID | Task Summary | Complexity (0–5) | Track | Owner | When to Review / Action |
| :---: | :--- | :--- | :---: | :---: | :--- | :--- |
| **TODO** | **T2.6–T2.10** | Kernel dispatch + sink-class mediation: no `privileged` effect without a grant; all effects recorded | **4** ⚠ | 🔴 GATE | Sr Dev + Tech Lead | Fault injection on every dispatch path. Must-fails: `pure` effect skipping ledger (MF-KRN-009); crash between dispatch and emit leaving no intent record (MF-KRN-010). Requires T2.1–T2.5, T3.1 |
| **TODO** | **T3.6–T3.8** | Ledger recovery + cassettes: external recovery scanner, `undeterminable` stays, cassette replay byte-identical | **3** | 🔴 GATE | Dev + Sr Dev | `kill -9` test; recovery controller writes terminal record, never the dying process. Requires T3.1–T3.5 |

**Sprint 3 exit criteria:** The trust boundary is enforced end-to-end. Every dispatch path has fault-injection coverage. The ledger survives crash-recovery without data loss or state corruption.

---

## 6. Sprint 4 · Episode Engine, Trust-Spine Demo & S4 Exit Gate (Weeks 9–10)

> ⚠ **This is the hardest sprint in the programme.** Three concurrent streams of Level 4–5 work. The trust-spine demo (T4.1–T4.7) is rated `XL ⚠` and requires decomposition before starting. Tech Lead + Project Lead must sign off on the decomposition plan before any code is written.

| Status | Task ID | Task Summary | Complexity (0–5) | Track | Owner | When to Review / Action |
| :---: | :--- | :--- | :---: | :---: | :--- | :--- |
| **TODO** | **T4.1–T4.7** | Episode engine + recursion — **trust-spine demo: a scripted trajectory runs with no model at all** | **5** ⚠ XL | 🔴 GATE | Tech Lead + Sr Dev + 2 Dev | Denial, attenuation, budget exhaustion, atomicity, recovery, evaluator isolation, secret non-disclosure — all green. Requires T2 + T3 complete |
| **TODO** | **T4.8** | Process engine: interrupted approval process resumes from ledger without replaying episode | **4** ⚠ | 🔴 GATE | Sr Dev + Dev | Restart-resume property test; states readable by a non-engineer. Requires T3.6, T1.12 |
| **TODO** | **T5.1–T5.2** | Worker perimeter: rootless, own OS identity, mount namespace, containment report | **4** ⚠ | 🔴 GATE | Sr Dev + Dev | Mount, egress, syscall probes; unverified perimeter blocks publication; red team reaches nothing. Requires T2.6 |
| **TODO** | **DELETE `spike/` + `slice/`** | Both directories removed from the repository | **1** | 🟢 FAST | Sr Dev | Checked gate item; absence verified in CI. **Non-negotiable** |

---

## 7. S4 Exit Gate — Joint TL + PL Sign-Off

The S4 exit is the single hardest gate in the programme. **No work beyond S4 begins until all items below are signed off jointly by the Tech Lead and the Project Lead.**

### Gate Checklist

| # | Gate Item | Evidence Required | Sign-off |
| :---: | :--- | :--- | :--- |
| **G4-01** | Trust-spine demo passes with no model | Scripted trajectory completes: denial, attenuation, budget exhaustion, atomicity, recovery, evaluator isolation, secret non-disclosure — all green | Tech Lead |
| **G4-02** | Process engine resumes from ledger | Property test: interrupted process resumes to same state without replaying agent reasoning | Sr Dev + Tech Lead |
| **G4-03** | Worker perimeter enforced at OS level | Containment report: mount, egress, syscall probes pass; unverified perimeter blocks publication | Sr Dev + Tech Lead |
| **G4-04** | `spike/` and `slice/` deleted | Both directories absent from the repository; CI absence check passes | Sr Dev |
| **G4-05** | All effects recorded; `privileged` mediated | Must-fail tests MF-KRN-008, MF-KRN-009, MF-KRN-010 pass against broken counterparts | Tech Lead |
| **G4-06** | Active MVP Contract coverage | `merged_scope_evidence_coverage = 100%` for all S1–S4 components | Scrum + Tech Lead |
| **G4-07** | No slow-clock artifact survives | No `compensatesFor` artifact has been promoted to a fast-clock dependency | Tech Lead |
| **G4-08** | Formal go/no-go for S5 | Written decision based on Tech Lead recommendation | **Project Lead** |

### What happens if S4 fails

* Unfinished work moves to explicitly owned S5 tickets with blocking status preserved.
* No gate is weakened because its implementation rolled over.
* Code whose required control is unfinished remains unmerged.
* The Project Lead issues a conditional-go or no-go with documented risks.

---

## 8. XL ⚠ Items — Mandatory Decomposition

Two items in this phase are rated `XL ⚠` (multi-sprint scope, high design risk). They **must be decomposed into sub-tasks with individual acceptance criteria before any code is written.** The decomposition itself requires Tech Lead + Project Lead approval.

| Task ID | Sprint | Description | Why XL ⚠ | Decomposition Owner |
| :--- | :---: | :--- | :--- | :--- |
| **T4.1–T4.7** | S4 | Episode engine + recursion + trust-spine demo | Touches kernel, ledger, agency and runtime simultaneously; every invariant from T2 and T3 must hold under adversarial conditions with no model in the loop | Tech Lead |
| **T7.5–T7.7** | S7 (Phase 2) | `vg harness` + reconstruction suite | Three competitor-shaped harnesses as manifests; any reconstruction requiring a core change falsifies the configurability claim | Sr Dev |

T7.5–T7.7 is listed for awareness; it belongs to Phase 2 and does not block S4 exit.

---

## 9. Dependency Chain — Critical Path

```text
S1a: T1.1–T1.6 (wire schema)
       │
       ├──────────────────────────────────────────────────────┐
       ▼                                                      ▼
S1b: T1.7–T1.12 (envelope, artifact, process def)     T0a (provider spike)
       │                                                      │
       ├───────────────────────┬──────────────────┐           │
       ▼                       ▼                  ▼           ▼
S2a: T3.1–T3.5 (ledger)   T7.1–T7.3 (graph)  T2.1–T2.5   T0b.1–T0b.4
       │                       │              (kernel)     (E2E slice)
       ▼                       ▼                  │
S2b: T7.4 (vg-shell-only)  T1.13–T1.15           │
       │                   (conformance)           │
       └───────────────────────────────────────────┤
                                                   ▼
S3:  T2.6–T2.10 (dispatch + mediation)    T3.6–T3.8 (recovery + cassettes)
       │                                        │
       ├────────────────────────────────────────┘
       ▼
S4:  T4.1–T4.7 (episode engine + trust-spine demo)
       │
       ├── T4.8 (process engine)
       ├── T5.1–T5.2 (worker perimeter)
       └── DELETE spike/ + slice/
```

**The critical path is:** T1 → T3 → T2 → T2.6–T2.10 → T4.1–T4.7. Any delay on the ledger or kernel dispatch directly delays the trust-spine demo.

---

## 10. Continuous Controls (S0 → S4)

These run every sprint and are not sprint-specific. Scrum owns enforcement.

| Task ID | Control | Evidence | Owner |
| :--- | :--- | :--- | :--- |
| **T10.4–T10.9** | Active MVP Contract coverage at 100% (test or justification) | Requirement-to-test map green; every uncovered row carries a justification marker | Scrum + All |
| **T10.4–T10.9** | Margin alarms active | TCB LOC, p95 latency, context tokens, schema extension slack alarmed (not hard-limited) | Dev |
| **Gate B** | Merged-scope evidence coverage = 100% | No PR merges if it would leave a merged component with an `open` requirement | CI automated |

---

## 11. Key Reminders for PM & Scrum (Phase 1 Specific)

1. **Disposable Code Rule:** `spike/` (S1) and `slice/` (S2) are slow-clock artifacts. They exist to learn, not to ship. Track them as liabilities, not assets. The S4 exit review checks their absence — this is a hard gate.
2. **No Model in the Trust-Spine Demo:** T4.1–T4.7 must run with a scripted trajectory and no model at all. If someone says "we need a model to test this," that is a design defect, not a testing limitation.
3. **Broken Counterparts:** Every must-fail test must have a deliberately broken implementation in `test/broken/`. A test that has never been observed failing is not a gate (Handbook M6).
4. **Gate B is Cumulative:** Every merged component's requirements must be `covered` or `justified` at every PR. Coverage is over merged scope, not future scope.
5. **Weekly Three-Question Review:** What merged? What is blocked? Has anything changed our mind about `02`–`07`? The third question is the most important one.

---

## 12. Immediate Next Steps for Leadership (Post-Sprint 1)

1. **TODO — Tech Lead:** Approve T7.1–T7.3 (artifact graph) decomposition plan before S2a coding begins.
2. **TODO — Sr Dev (Beta):** Begin T2.1–T2.5 kernel capabilities; requires T1.3–T1.5 from S1a (available).
3. **TODO — Dev (Alpha):** Begin T3.1–T3.5 event store + reducer; requires T1.7 from S1b (available).
4. **TODO — Sr Dev + Dev (Gamma):** Begin T0b.1–T0b.4 disposable E2E slice; requires T1.7–T1.12 + T0a (both available).
5. **TODO — Dev:** Begin T1.13–T1.15 reader profiles + migration rehearsal at S2b.
6. **TODO — PM:** Schedule dogfood target for mid-S6; begin logging opt-out reasons now.
7. **TODO — Scrum:** Track Active MVP Contract coverage burndown from S2 onward; ensure every PR cites `req_id`.
8. **TODO — Tech Lead + Project Lead:** Plan T4.1–T4.7 decomposition by S3 end — do not wait for S4 to start thinking about it.
