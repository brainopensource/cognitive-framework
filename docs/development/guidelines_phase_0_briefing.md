# Phase 0 & Baseline Engineering Briefing
## Task Complexity, Review Governance & Sprint Execution Guide

**Audience:** Project Manager (PM), Scrum Master, Tech Lead, and Lead Developers  
**Reference Documents:** `docs/v4/13_C_gts_mvp_program_and_engineering_plan.md`, `docs/development/guidelines_phase_0.md`  
**Purpose:** Provide an operational dashboard mapping task complexity (Levels 0–5), pacing guidelines (when to speed up vs. when to pause for review/gates), and ownership to ensure an uncompromised engineering baseline before and during development.

---

## 1. Pacing & Governance Framework

To balance velocity with safety, all tasks are classified into two execution tracks:

* 🟢 **FAST TRACK (Levels 0–2):** Autonomous, high-speed execution by Developers and Scrum. No architecture approval needed before PR creation; standard automated CI checks and code review apply.
* 🔴 **GATE & REVIEW TRACK (Levels 3–5):** High design risk, invariant contracts, security perimeters, or merge-gating rules. **Requires explicit Tech Lead / Project Lead sign-off before merging.**

### Complexity Scale (0 to 5)

| Level | Profile | Scope & Typical Activities | Governance / Pacing |
| :---: | :--- | :--- | :--- |
| **0** | **Junior Dev / PM Assistant** | Mechanical documentation, moving superseded files, checklist maintenance. | 🟢 Fast Track (Async review) |
| **1** | **Developer** | Basic CLI scripts, JSON/YAML schemas, boilerplate adapters, standard unit tests. | 🟢 Fast Track (Peer review) |
| **2** | **Mid Developer** | CI automation scripts, schema parsers, event serializers, standard port adapters. | 🟢 Fast Track (CI automated gate) |
| **3** | **Senior Developer** | Must-fail test suites, fault-injection runners, OS containment specs, event reducers. | 🔴 Gate Track (Sr Dev + TL sign-off) |
| **4** | **Lead Architect / Sr Dev** | Package isolation rules, Port interface definitions, sink classification, attenuation algebra. | 🔴 Gate Track (Tech Lead approval) |
| **5** | **Tech Lead / Principal** | Authoritative Decision Record, mathematical boundary laws, Active MVP Contract gating. | 🔴 Gate Track (Joint TL + PL sign-off) |

---

## 2. Phase 0 Baseline Preparation Matrix (Before S1 Merge)

These tasks establish the source of truth, merge gates, and developer packet.

| Status | Task ID | Task Description | Output / Artifact | Complexity (0–5) | Track | Primary Owner | Review / Sign-off Gate |
| :---: | :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| **TODO** | **B-01** | **Register GTS-13C & Archive Superseded** | Update registry; archive `GTS-13` / `13B` | **0** | 🟢 FAST | PM / Scrum | Git history/archive cannot yet be verified |
| **DONE** | **B-02** | **Create Decision Record** | ADR-0045..0053 plus approval events and reversal conditions | **5** | 🔴 GATE | Tech Lead + Project Lead | Joint approval recorded |
| **DONE** | **B-03** | **System Architecture & ICD** | Package isolation, sink classification and port signatures | **4** | 🔴 GATE | Tech Lead + Sr Dev | Approved |
| **DONE** | **B-04** | **Active MVP Contract Matrix** | 22 assigned rows; Gate A/B scripts | **5** | 🔴 GATE | Tech Lead + Req Owners | 100% assignment; 100% merged scope |
| **DONE** | **B-05** | **Verification, Threat & Eval Plan** | Threat model, must-fail catalogue and evaluation protocol | **3** | 🔴 GATE | Sr Dev | Approved for S0 scope |
| **TODO** | **B-06** | **Automate CI & Traceability Gates** | Boundaries and Gate A/B work; automated PR-body `req_id` validation remains | **2** | 🟢 FAST | Sr Dev + Dev | Complete PR metadata enforcement |
| **TODO** | **B-07** | **Convert GTS-13C into Backlog** | Markdown backlog exists; issue-tracker import remains | **1** | 🟢 FAST | PM + Scrum | Create real tracker tickets |
| **DONE** | **B-08** | **Assemble Clean Developer Packet** | Sprint 1 index, backlog and Dev 1–4 packets | **0** | 🟢 FAST | PM | Ready, conditional distribution |
| **TODO** | **B-09** | **Phase 0 Baseline Review & Tag** | Conditional decision exists; independent review, branch protection and Git tag remain | **5** | 🔴 GATE | Project Lead + Tech Lead | Full go/no-go still open |

---

## 3. Sprint 0 through Sprint 2 Task Breakdown & Complexity

### Sprint 0 · Infrastructure, Baseline & Schema Archaeology (Weeks 1–2)

| Status | Task ID | Task Summary | Complexity (0–5) | Track | Owner | When to Review / Action |
| :---: | :--- | :--- | :---: | :---: | :--- | :--- |
| **TODO** | **T0.1–T0.4** | Four traces and inventory exist; independent blind reconstruction remains | **3** | 🔴 GATE | Tech Lead + Sr Dev | Independent reviewer must sign or add gaps |
| **TODO** | **T0.5–T0.6** | Non-coding trace exists; prospective human timing remains | **2** | 🟢 FAST | Dev + PM | Capture two timed manual reproductions |
| **DONE** | **T10.1–T10.3** | Package scaffold, forbidden imports and eight broken counterparts | **2** | 🟢 FAST | Sr Dev + Dev | CI passes |
| **TODO** | **T10.4–T10.9** | Rule map exists; margin alarms and remaining continuous controls remain | **2** | 🟢 FAST | Dev | Implement automated reporting |

### Sprint 1 · Contracts, Wire Schema & Disposable API Spike (Weeks 3–4)

| Status | Task ID | Task Summary | Complexity (0–5) | Track | Owner | When to Review / Action |
| :---: | :--- | :--- | :---: | :---: | :--- | :--- |
| **TODO** | **T0a.1–T0a.3** | Disposable Provider API Spike in `spike/` | **1** | 🟢 FAST | Dev 4 | Start after full S1 go |
| **TODO** | **T1.1–T1.3** | Canonicalisation, primitives and selector algebra | **4** | 🔴 GATE | Dev 1 + leads | Assigned; not started |
| **TODO** | **T1.4–T1.6** | EffectDescriptor, CapabilityGrant and Receipt | **4** | 🔴 GATE | Dev 2 + leads | Assigned; not started |
| **TODO** | **T1.7–T1.11** | Envelope, Artifact, Claim, Correction and Recording | **3** | 🔴 GATE | Dev 3/4 + Sr Dev | Assigned; not started |

### Sprint 2 · Real-Provider Disposable Slice, Kernel & Ledger (Weeks 5–6)

| Status | Task ID | Task Summary | Complexity (0–5) | Track | Owner | When to Review / Action |
| :---: | :--- | :--- | :---: | :---: | :--- | :--- |
| **TODO** | **T0b.1–T0b.4** | Disposable E2E Slice | **2** | 🟢 FAST | Sr Dev + Dev | Sprint 2 |
| **TODO** | **T2.1–T2.5** | Kernel capabilities, attenuation and budgets | **4** | 🔴 GATE | Sr Dev + Tech Lead | Sprint 2 |
| **TODO** | **T3.1–T3.5** | Event store, reducer and replay | **3** | 🔴 GATE | Dev + Sr Dev | Sprint 2 |
| **TODO** | **T1.12–T1.14** | Reader profiles and second-language conformance | **2** | 🟢 FAST | Dev + Sr Dev | Sprint 2 |

---

## 4. Key Architectural Alignment Reminders for PM & Scrum

1. **Meta-Harness Equivalence**:
   - The Meta-Harness 5-tuple $\mathcal{M}$ is our `HarnessManifest`.
   - Level 4 "Cells" are **Episodes** (coordinating open-ended reasoning).
   - Level 1–2 Tools are **Effects / Adapters** behind ports, not Episodes.
   - Competitor reconstructions (Claude-Code-shaped, OpenCode-shaped) are **falsification tests for `C-01`**. If a reconstruction forces an engine change, that is an invaluable finding, not a bug.
2. **Two-Clock Split**:
   - **Fast Clock (Enforcement / Permanent):** Capability checks, sandbox isolation, event recording. Never expires.
   - **Slow Clock (Compensation / Temporary):** Scaffolding compensating for model flaws (prompts, retrieval hacks). Must declare `compensatesFor` and carries expiration triggers.
3. **Disposable Code Rule (`spike/` & `slice/`)**:
   - Built to learn in S1/S2; **must be deleted outright at S4 exit review**. CI prevents production imports.
4. **Active MVP Contract Gates**:
   - **Gate A (Sprint 0 Baseline):** 100% of rows have `req_id`, component, owner, `test_id`, and evidence defined (`status: open` is allowed).
   - **Gate B (Ongoing PRs):** 100% of merged-scope components must be `covered` or `justified`. Zero unmapped code merges.

---

## 5. Immediate Next Steps for Leadership

1. **TODO — Independent reviewer:** Blindly reconstruct the four T0 traces and sign or add gaps.
2. **TODO — Dev 1 + Dev 2:** Capture prospective hands-on and elapsed timing for two manual reproductions.
3. **TODO — PM / Scrum:** Import the prepared backlog into the real issue tracker.
4. **TODO — Sr Dev:** Add automated PR-body `req_id` validation and remaining margin reporting.
5. **TODO — Project Lead:** Verify branch protection, create the annotated baseline tag and issue the full Sprint 1 go.
6. **DONE — Tech Lead / Sr Dev:** Decision Record, ICD, Active Contract, Verification Plan, package gates and developer packets are prepared.
