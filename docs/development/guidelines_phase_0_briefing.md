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

| Task ID | Task Description | Output / Artifact | Complexity (0–5) | Track | Primary Owner | Review / Sign-off Gate |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| **B-01** | **Register GTS-13C & Archive Superseded** | Update registry; archive `GTS-13` / `13B` | **0** | 🟢 FAST | PM / Scrum | Tech Lead verification |
| **B-02** | **Create Decision Record** | Author 18 locked architectural decisions (`DR-01`..`DR-18`) with reversal conditions; seal Rev1/Rev2 to lead-only | **5** | 🔴 GATE | Tech Lead + Project Lead | **MANDATORY JOINT SIGN-OFF** |
| **B-03** | **System Architecture & ICD** | Package isolation (`domain ← ports ← kernel ← agency ← runtime → adapters`), sink classification (`pure/observation/privileged`), port signatures | **4** | 🔴 GATE | Tech Lead + Sr Dev | Tech Lead approval |
| **B-04** | **Active MVP Contract Matrix** | Machine-readable matrix (`req_id` $\to$ `component` $\to$ `test_id` $\to$ `evidence`). Enforces Gate A & Gate B | **5** | 🔴 GATE | Tech Lead + Req Owners | **MANDATORY TL SIGN-OFF** |
| **B-05** | **Verification, Threat & Eval Plan** | Threat models, must-fail test catalogue, A/A noise floor protocol, verifier-deployment gap monitor | **3** | 🔴 GATE | Sr Dev | Tech Lead approval |
| **B-06** | **Automate CI & Traceability Gates** | Package boundary linters, PR template checks, Gate A/B calculation scripts | **2** | 🟢 FAST | Sr Dev + Dev | Tech Lead acceptance |
| **B-07** | **Convert GTS-13C into Backlog** | Issue tracker tickets with dependencies, test IDs, and definition of done | **1** | 🟢 FAST | PM + Scrum | Tech Lead dependency check |
| **B-08** | **Assemble Clean Developer Packet** | Distribute Decision Record, GTS-13C, Architecture/ICD, Active Contract, Verification Plan, Backlog | **0** | 🟢 FAST | PM | Tech Lead review |
| **B-09** | **Phase 0 Baseline Review & Tag** | Cross-document consistency review, baseline tagging, formal go/no-go decision | **5** | 🔴 GATE | Project Lead + Tech Lead | **FORMAL GO/NO-GO GATE** |

---

## 3. Sprint 0 through Sprint 2 Task Breakdown & Complexity

### Sprint 0 · Infrastructure, Baseline & Schema Archaeology (Weeks 1–2)

| Task ID | Task Summary | Complexity (0–5) | Track | Owner | When to Review / Action |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **T0.1–T0.4** | Fix 3 bugs by hand; record observation $\to$ proposal $\to$ effect $\to$ receipt in flat file; produce `field-inventory.md` | **3** | 🔴 GATE | Tech Lead + Sr Dev | **Review at exit:** Unused fields marked `speculative` |
| **T0.5–T0.6** | Non-coding task baseline (spreadsheet/log) + timing human baseline | **2** | 🟢 FAST | Dev + PM | Verify generality candidate fields |
| **T10.1–T10.3** | Package layout scaffold; broken imports fail build; `test/broken/` scaffold | **2** | 🟢 FAST | Sr Dev + Dev | CI boundary test must pass |
| **T10.4–T10.9** | Rule-to-test CI mapping; margin alarms setup (TCB LOC, p95 latency) | **2** | 🟢 FAST | Dev | Validate automated reporting |

### Sprint 1 · Contracts, Wire Schema & Disposable API Spike (Weeks 3–4)

| Task ID | Task Summary | Complexity (0–5) | Track | Owner | When to Review / Action |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **T0a.1–T0a.3** | Disposable Provider API Spike in `spike/` (raw API calls, rate limits, token accounting $\to$ `provider-notes.md`) | **1** | 🟢 FAST | Dev | **Check:** Must live in unimportable `spike/` |
| **T1.1–T1.3** | Canonicalisation spec (40 golden triples), opaque primitives, `ResourceSelector` with total inclusion relation | **4** | 🔴 GATE | Tech Lead + Sr Dev | **Review:** Property test on selector inclusion |
| **T1.4–T1.6** | `EffectDescriptor` (with `sinkClass`), `CapabilityGrant`, `Receipt` (with first-class `undeterminable`) | **4** | 🔴 GATE | Tech Lead + Sr Dev | **Review:** Grant without descriptor digest fails parse |
| **T1.7–T1.11** | `EventEnvelope`, `Artifact`, `Claim` (mandatory invalidation conditions), `CorrectionRecord`, `Recording` | **3** | 🔴 GATE | Sr Dev + Dev | **Review:** Empty invalidation array rejected at parse |

### Sprint 2 · Real-Provider Disposable Slice, Kernel & Ledger (Weeks 5–6)

| Task ID | Task Summary | Complexity (0–5) | Track | Owner | When to Review / Action |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **T0b.1–T0b.4** | Disposable E2E Slice (`prompt → model → patch → approval → test`) tagged `delete-or-replace-by-S4` | **2** | 🟢 FAST | Sr Dev + Dev | **Check:** Generates `slice-findings.md`; unimportable by core |
| **T2.1–T2.5** | Kernel capability issuance, attenuation monotonicity, lease-tree budget conservation | **4** | 🔴 GATE | Sr Dev + Tech Lead | **Review:** Must-fail escalation attempts emit alerts |
| **T3.1–T3.5** | Append-only event store, pure state reducer `(State, Event) → State`, projection rebuild from zero | **3** | 🔴 GATE | Dev + Sr Dev | **Review:** State reconstruction identical on replay |
| **T1.12–T1.14** | Reader profiles (forward compatibility) + second-language reader-only conformance | **2** | 🟢 FAST | Dev + Sr Dev | Cross-reader agreement on all golden vectors |

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

1. [ ] **PM / Scrum**: Set up the sprint board mapping `B-01` through `B-09` and Sprint 0 tasks (`T0.1`–`T0.6`, `T10.1`–`T10.9`).
2. [ ] **Tech Lead**: Author `01_decision_record.md`, `02_system_architecture_and_icd.md`, and `03_active_mvp_contract.md`.
3. [ ] **Senior Dev**: Author `04_verification_threat_evaluation_plan.md` and scaffold `tools/ci/` boundary tests.
4. [ ] **Project Lead**: Execute final Phase 0 baseline review (`B-09`) to authorize Sprint 0 development.
