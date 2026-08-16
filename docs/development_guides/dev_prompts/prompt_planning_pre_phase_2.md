# Leadership Architecture & Evaluation Prompt: Pre-Phase 2 (Sprints 5 & 6) Readiness Review

**Target Document:** `docs/development/dev_prompts/prompt_planning_pre_phase_2.md`  
**Audience:** Project Lead Senior, Principal Tech Lead, Chief Software Architect, and Staff AI Systems Engineers  
**Classification:** Strategic Engineering Governance & Architectural Audit Directive (PhD-Level Specification)  
**Execution Context:** Transition from Phase 1 (Trust Spine Foundation, Sprints 0–4, Tag `v0.4.0-sprint4`) to Phase 2 (Lightweight Beta MVP Coding Harness, Sprints 5 & 6) on `sprint5-6/integration`.

---

## 1. Directive & Persona

Act as a **World Top 3% Senior Software Architect, Principal Tech Lead, and PhD in Computer Science / Machine Learning Systems & Formal Verification**, with deep specialization in:
* SOTA Agentic Coding Harnesses & Execution Runtimes (2026 frontier architectures, 12-layer FUAA framework, prefix-cache KV economics, Tree-sitter localization, ACI design);
* Capability Security & Microkernel Design (resource-scoped grants, monotonic attenuation algebra, lease-tree budget conservation, rootless namespace isolation);
* Event-Sourced Durability & Distributed Recovery (intent-before-effect logging, pure associative state reducers, crash reconciliation scanners, counterfactual cassette replay);
* Rigorous Empirical Measurement & Metacognition (exterior evaluator double-probes, pre-registered A/A noise floors, McNemar paired hypothesis testing, Brier score calibration, Lakatos research program partitions).

### Core Mission
Conduct an exhaustive, forensic cross-examination of the **Vanguard v4.0.0 specification corpus**, the **landed codebase (Sprints 0–4)**, the **recent senior architectural reviews**, and the **SOTA 2026 agentic coding landscape**. 

Produce an actionable, definitive **Pre-Phase 2 Architectural Readiness Report** that determines:
1. Exact mathematical, formal, and operational discrepancies between the specification and landed code;
2. Whether to formalize a specification patch upgrade to **Specification v0.4.1 (v4B)**;
3. Exactly **what to do now** (Sprint 5 & 6 deliverables), **what to do later** (Phase 3 Sprints 7–9+), **what to reject permanently** (architectural anti-patterns), **why**, **how**, and **when**;
4. Concrete four-lane parallel developer work packets for Sprints 5 & 6 with zero blocking dependencies on Day 1.

> **CRITICAL RULE:** This prompt is an architectural diagnostic, governance, and planning directive. Do **NOT** execute speculative feature code during this review. Produce explicit diagnostic evidence, formal decisions, and merge-gated contract rows first.

---

## 2. Mandatory Investigation & Reading Corpus

Before issuing any verdict, the reviewer must inspect, cross-check, and execute non-destructive verifications across the entire repository surface:

### A. Authoritative Specifications (The Keel)
1. **[`docs/v4/09_vanguard_decision_register_v040.md`](file:///home/rocha/Coding/Aether-D-System/docs/v4/09_vanguard_decision_register_v040.md):** The append-only source of truth for all ADRs (ADR-0001 through ADR-0058).
2. **[`docs/v4/00` through `07`](file:///home/rocha/Coding/Aether-D-System/docs/v4/):** Document registry, engineering handbook, charter claims/non-claims, execution planes, wire schemas, kernel capability rules, competence evidence models, and measurement doctrine.
3. **[`docs/v4/13_C_gts_mvp_program_and_engineering_plan.md`](file:///home/rocha/Coding/Aether-D-System/docs/v4/13_C_gts_mvp_program_and_engineering_plan.md):** Living program plan (GTS-13C) — sequencing, rationale, and harness composition.
4. **[`docs/sprint0/active-mvp-contract.json`](file:///home/rocha/Coding/Aether-D-System/docs/sprint0/active-mvp-contract.json):** The **sole merge gate** governing requirement-to-test mapping.
5. **[`docs/sprint0/system-architecture-icd.md`](file:///home/rocha/Coding/Aether-D-System/docs/sprint0/system-architecture-icd.md):** The 6-package dependency lattice and port activation signatures.
6. **[`docs/sprint0/verification-threat-evaluation-plan.md`](file:///home/rocha/Coding/Aether-D-System/docs/sprint0/verification-threat-evaluation-plan.md):** Must-fail catalogue (`MF-*`) and adversarial threat models.

### B. Recent Senior Reviews & SOTA Analysis
1. **[`docs/review/todo/phases_review.md`](file:///home/rocha/Coding/Aether-D-System/docs/review/todo/phases_review.md):** Master multi-phase review, landed inventory, gap audit (GAP-01 through GAP-06), and four-lane developer allocation.
2. **[`docs/review/todo/vanguard_harness_cli_architectural_review_phase_2.md`](file:///home/rocha/Coding/Aether-D-System/docs/review/todo/vanguard_harness_cli_architectural_review_phase_2.md):** Deep comparative review of 17+ coding harnesses in 2026, 8-surface taxonomy, and 7 specific findings against v4.0.
3. **[`docs/review/todo/vanguard_harness_cli_architectural_review_phase_2_REV2.md`](file:///home/rocha/Coding/Aether-D-System/docs/review/todo/vanguard_harness_cli_architectural_review_phase_2_REV2.md):** The 12-layer Functional Universal Agent Architecture (FUAA) and experimental protocol standards.

### C. Landed Codebase & Boundary Tools (Active Tree on `sprint5-6/integration`)
1. `vanguard/packages/domain/` (primitives, wire contracts, canonicalization, selectors, reducer).
2. `vanguard/packages/kernel/` (single dispatch S0–S12, attenuation algebra, budget lease trees, provenance).
3. `vanguard/packages/runtime/` (`ledger/` recovery scanner, stores, projections; `governance/` process engine).
4. `vanguard/packages/agency/` (`episode/` engine and state, `manifests/` registry).
5. `vanguard/packages/ports/` & `adapters/` (`model/` OpenRouter & cassette, `environment/` Git worktree, `sandbox/` rootless namespace, `evaluator/` fake).
6. `vanguard/clients/cli/` (hexagonal Ink/React TUI & headless runtime client).
7. `test/` (contracts, trust spine `test_spine.py`, security, broken counterparts).
8. `tools/` (`check_boundaries.py`, `check_active_mvp_contract.py`, `check_sprint0_governance.py`, `check_tcb_budget.py`, `audit_v4.py`, `run_broken_tests.py`).

---

## 3. Core Evaluation Vectors & Questions to Answer

The evaluation report must provide deep technical answers with concrete file/line evidence across the following six investigative chapters:

### Chapter 1: Specification Invariant Audit & v0.4.1 (v4B) Patch Necessity
Forensically evaluate the mathematical and operational validity of the v4.0 corpus and formulate the exact patch text for **Specification v0.4.1 (v4B)**:
* **The `M-18` Timestamp Impossibility:** Analyze why including physical `timestamp` in the instrument tuple makes experimental comparison mathematically impossible under strict equality ($t_1 \ne t_2$). Provide the formal 4-subset tuple partition formula:
  $$\text{Tuple} = \langle \mathcal{K}_{\text{compat}}, \mathcal{D}_{\text{treatment}}, \mathcal{S}_{\text{strat}}, \mathcal{M}_{\text{meta}} \rangle$$
* **Dispatcher Dual Ingress Topology:** Reconcile the conflict between universal dispatcher mediation (`VG-05 §2.1`) and evaluator exteriority (`VG-03 §3/§6.1`). Define the two explicit ingress channels: `Principal::Episode` (agent proposals) vs `Principal::EvidencePlane` (exterior evaluation triggers on terminal events).
* **Failure Path `F-25` Durability Guarantee:** Eliminate the "log-only" emission failure path by routing outcome commits through transactional outboxes and crash-recovery reconciliation to `undeterminable`.
* **Approvals & Suspension Alignment (`DEF-12`):** Formally align `VG-05` and `VG-10` with ADR-0057 for human-in-the-loop privileged `fs.patch` approvals in beta.
* **Backlog & Identifier Integrity:** Cleanse stale references (e.g. `DEF-02` citing `MF-31`) and establish clean test ID mappings.

### Chapter 2: Landed Codebase Verification & Trust Spine Health
Audit the actual landed code against the strict requirements of Phase 1:
* **Lattice Boundary Enforcement:** Verify that `tools/check_boundaries.py` enforces:
  $$\text{domain} \longleftarrow \text{ports} \longleftarrow \text{kernel} \longleftarrow \text{agency} \longleftarrow \text{runtime} \longrightarrow \text{adapters}$$
  and that `vanguard/clients/cli/` has zero direct imports of backend core packages.
* **Single Dispatch S0–S12 Pipeline:** Verify in `vanguard/packages/kernel/dispatch.py` that pre-execution intent records are persisted to disk *before* sandboxed effect execution, and that sink-class mediation ([ADR-0054](file:///home/rocha/Coding/Aether-D-System/docs/v4/09_vanguard_decision_register_v040.md#L157)) correctly treats `pure`, `observation`, and `privileged` sinks.
* **Monotonic Attenuation & Budget Conservation:** Verify that capability grants narrow monotonically and that budget lease trees debit overruns against parent capacity.
* **Model-Free Trust Spine Isolation:** Verify that `test/trust/test_spine.py` executes in complete process isolation with `OPENROUTER_API_KEY` unset, proving that no real LLM has captured the kernel verification path.
* **TCB Budget Baseline:** Confirm that logical lines of code in `vanguard/packages/kernel/` remain strictly below the 1,438 LOC alarm threshold.

### Chapter 3: SOTA Agentic Coding Harness Synthesis (The 2026 Frontier)
Cross-examine Vanguard's architecture against the 12-layer Functional Universal Agent Architecture (FUAA) established in the senior reviews:
* **Layer 1 (Ingestion & Identity):** Immutable `HarnessManifest` and content-addressed artifact graphs.
* **Layer 2 & 3 (Localization & Context Assembly):** Tree-sitter repo-mapping (`ObservationSource`) and L1–L5 prefix-stable prompt compilation.
* **Layer 4 (Cache Economics):** KV prompt-cache optimization ($L1 \to L3$ frozen across turns) yielding $>80\%$ token cost reductions.
* **Layer 5 (Planning & Control):** Finite recursive loop (`EpisodeEngine`) without hardcoded class hierarchies or cognitive identifier bloat.
* **Layer 6 (Tools & Protocols):** Typed default tools (`read`, `search`, `patch`, `test`) with explicit JSON Schemas; shell restricted to privileged fallback.
* **Layer 7 & 8 (Authority & Containment):** Resource-scoped capability grants vs OS-level rootless namespace container sandboxing.
* **Layer 9 (Editing & Diff Integrity):** Worktree-isolated patch previews (including newly created files) and exact unified diff validation (`git apply --check`).
* **Layer 10 (Trajectory & Recovery):** Transactional append-only event ledger and independent recovery scanner.
* **Layer 11 & 12 (Evidence & Measurement):** Exterior evaluator daemon with bit-for-bit double probes, `inconclusive` fail-closed handling, and paired A/A experimental protocols.

### Chapter 4: Phase 2 (Sprints 5 & 6) Technical Architecture & Detailed Scope
Specify the exact architecture and component interactions to deliver the **Lightweight Beta MVP**:
* **Sprint 5 (The Judge & Context Substrate — T5.3–T5.6, T4.9–T4.11):**
  - OS-isolated evaluator daemon (`UID 10002`) vs worker sandbox (`UID 10001`).
  - Immutability Probe (Probe 1) and Non-Pollution Probe (Probe 2) protocol implementation.
  - Prefix-stable Context Compiler (`agency/context/compiler.py`) with token budgeting and provenance tagging.
  - Pre-action competence prior logging $P(\text{success} \mid \text{task})$.
* **Sprint 6 (Beta Product Assembly & Dogfood Gate — T6.1–T6.8):**
  - Runtime Composition Root (`runtime/root.py`) assembling `Kernel`, `EpisodeEngine`, `ProcessEngine`, `OpenRouterModelAdapter`, `GitEnvironmentAdapter`, and `RootlessSandbox`.
  - Descriptor-Bound Human Approvals: unified diff rendered in TUI, human signs `argsDigest`, tampered diffs fail closed (`MF-GOV-001`).
  - Hexagonal CLI / React Ink TUI with live `EventEnvelope` streaming, `vg why` artifact explanation, and single-keystroke `CorrectionRecord` capture (`[d]efect`, `[s]tyle`, `[t]est`, `[s]ecurity`, `[a]rchitecture`).
  - The Beta Dogfood Milestone Gate: End-to-end fix of a real single-file bug in an external repository using typed tools and OpenRouter.

### Chapter 5: Defect & Gap Matrix (P0 through P3)
Catalog all known technical debts, architectural drifts, and gaps with clear severity, impact, root cause, and remediation status (updating [GAP-01 through GAP-06](file:///home/rocha/Coding/Aether-D-System/docs/review/todo/phases_review.md#detailed-audit-breakdown)).

### Chapter 6: Governance, Quality Doctrine & The Four-Lane Developer Allocation
Structure the human resource and CI merge gates following the non-negotiable **Four-Lane Law** ([ADR-0056](file:///home/rocha/Coding/Aether-D-System/docs/v4/09_vanguard_decision_register_v040.md#L164)):
* **Lane SA (Senior A - GATE, Complexity 4–5):** Context Compiler (S5) $\to$ Runtime Composition Root & Dogfood Verification (S6).
* **Lane SB (Senior B - GATE, Complexity 4):** Exterior Evaluator OS Process Isolation & Double Probes (S5) $\to$ Descriptor-Bound Approval Flow (S6).
* **Lane DC (Developer C - FAST/GATE, Complexity 2–3):** OpenRouter ModelPort Enhancements (S5) $\to$ Latency Telemetry & Benchmarking Suite (S6).
* **Lane DD (Developer D - FAST, Complexity 2–3):** CLI Client Interface Realignment (S5) $\to$ Ink TUI Approval Screens & Single-Key Correction UX (S6).

---

## 4. Required Report Structure

The generated evaluation report must be formatted according to this exact structural schema:

1. **Executive Verdict & Decision Summary** (Max 1 page — clear YES/NO recommendations on v0.4.1 upgrade and readiness).
2. **Landed State vs. Specification Matrix** (Requirement $\to$ Component $\to$ Test ID $\to$ Evidence $\to$ Status).
3. **Formal Specification v0.4.1 (v4B) Patches** (Exact text and mathematical formulations for `M-18`, dual ingress, `F-25`, and `DEF-12`).
4. **SOTA Harness Cross-Analysis (FUAA 12 Layers)** (Detailed comparison vs Claude Code, Aider, OpenHands, Goose, Reasonix, mini-SWE-agent).
5. **Phase 2 (Sprints 5 & 6) Technical Blueprint & Architecture Flow** (Mermaid sequence diagrams and component interfaces).
6. **Detailed Defect & Gap Catalog (P0–P3)** (Concrete file paths, root causes, and verified solutions).
7. **What To Do vs. What NOT To Do Matrix** (Strict rules for engineering and product leadership).
8. **Four-Lane Developer Work Packets (S5 & S6)** (Files owned, ports consumed, first failing tests, must-fail checks, merge sign-offs).
9. **Objective Go / No-Go Gate Criteria** (Pre-merge checklists for Sprint 5 and Sprint 6 exits).
10. **Concluding Program Roadmap & Sequencing.**

---

## 5. Non-Negotiable Architectural Invariants

* **No Cognitive Nouns in Code:** CI linter strictly forbids `plan`, `reflect`, `debug`, `architect` as class or function identifiers in `vanguard/packages/agency/`.
* **Zero Model Authority in Governance:** The compliance and approval state machine (`ProcessEngine`) must execute and resume purely from ledger state without calling an LLM.
* **Exteriority of the Judge:** An episode must never evaluate its own outcome. Evaluation is triggered strictly by observing terminal ledger events across an OS security boundary.
* **100% Contract Test Gate:** No pull request merges to `main` without citing an active `req_id` and passing all bound contract, property, and must-fail tests.
* **Disposables Stay Absent:** `spike/` and `slice/` remain permanently deleted; absence verified by `MF-S4-001`.
* **Zero In-Process Module Leakage:** All contract and trust spine tests execute in subprocess-isolated environments.

---

*This prompt owns the leadership evaluation protocol for authorizing Phase 2 and cutting Specification v0.4.1. It preserves all mathematical invariants, enforces capability security, and guarantees a decoupled, high-performance, SOTA delivery.*
