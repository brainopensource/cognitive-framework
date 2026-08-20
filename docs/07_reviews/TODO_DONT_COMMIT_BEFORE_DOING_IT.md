[SYSTEM DIRECTIVE: AGENT EXECUTION PROMPT]

[META-DIRECTIVE]
Execute the following operational directive with zero conversational filler, no narrative prose, and no meta-commentary. Output must adhere strictly to the schema, constraints, and execution flow specified below.

---

[SYSTEM CONTEXT & OPERATIONAL ROLE]
ROLE: Principal Staff Engineer & Technical Authority (Aether-D-System / Vanguard Runtime)
CONTEXT: Wave 6 Execution Kickoff (Sprint A: Architecture Alignment, Conceptual Consolidation, Documentation Normalization, Refactor Planning)
TASK: Establish ground truth via code analysis, resolve architectural tensions, and produce four canonical deliverables in repository-compliant Markdown.

---

[EVIDENTIARY HIERARCHY & CONSTRAINT ENGINE]
1. EXECUTION TRUTH (Priority 1): File system, line numbers, test outputs, AST analysis, CI execution logs (`layer0/`, `vanguard/packages/`, `packs/`, `test/`, `tools/`, `.github/workflows/`).
2. NORMATIVE SPECS (Priority 2): `docs/SPEC.md`, `docs/05_adr/*`, `schemas/*`.
3. REVIEW DOCUMENTS (Priority 3): `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/*` (Treat as non-normative claims requiring empirical verification).

Strict Rule: Lower-index priorities MUST NOT override higher-index priorities. Unverified claims in Priority 3 must be discarded if contradicted by Priority 1 or 2.

---

[MANDATORY EXECUTION PROTOCOL]

PHASE 0: GROUND TRUTH DETERMINATION
1. Execute full local suite: `npm test`, `pytest`, cargo test, CI workflows (`.github/workflows/*`).
2. Map actual source files (`layer0/`, `vanguard/packages/`, `packs/`, `test/`, `tools/`).
3. Cross-examine claims in `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/` against code state.

PHASE 1: HARD ARCHITECTURAL DECISION MATRIX
Resolve the following 8 core tensions explicitly using empirical evidence. Record (A) Decision, (B) Empirical Grounding (File/Line/Command), (C) Rejected Alternative, (D) Rationale:
- Tension 1: Production vs. Legacy Lattice Target
- Tension 2: Language & Runtime Strategy (FFI, WASM, Native Node/Rust/Python boundary thresholds)
- Tension 3: Decision Authority vs. State Authority Boundaries
- Tension 4: Plugin/Extension Invariant Substrate
- Tension 5: Irrecoverable Field Hardening (Identity, Causality, Attribution)
- Tension 6: CI Measurement Delta (Current vs. Required Synthetic-Proof Gates)
- Tension 7: Freeze Scope vs. Fiction Scope
- Tension 8: Construction vs. Reconstruction Sequencing

PHASE 2: ARTIFACT GENERATION
Generate the following four artifacts strictly following repository conventions (`AGENTS.md`, `CLAUDE.md`):

1. `TODO_DOCS_CONCEPTS.md`
   - File-by-file action inventory under `docs/`, `schemas/`, `specs/` (Action: UPDATE | DELETE | MERGE | ARCHIVE).
   - Verification command per item.
   - Domain Terminology Canonical Lexicon & Frozen State Machine Models.
   - Discarded Review Propositions Log.

2. `ROADMAP_WAVE6.md`
   - Sequenced phases (Core Convergence -> SPI Stabilization -> Production Certification).
   - Hard exit gates per phase (Deterministically testable in CI).
   - Dependency graph ordered by non-reconstructible data integrity constraints.

3. `BACKLOG.md`
   - Prioritized Epics and Tasks mapped to: `domain`, `ports`, `kernel`, `agency`, `runtime`, `adapters`, `cli`.
   - Acceptance criteria, dependencies, t-shirt size estimates.
   - Deprecation/Removal ledger for duplicate implementations and unapproved forks.

4. `SPRINT_0_PLAN.md`
   - Sprint 0 Scope (Remediation, Concept Freezing, Boundary Verification, Refactor Staging).
   - Sprint 1 Preview (Direct handoff for core refactoring).
   - Standard Sprint Board format matching `docs/03_sprints/`.

---

[QUALITY CONTROL & CI GATE ANTI-PASS CONSTRAINT]
For every proposed CI Gate in deliverables:
1. Provide the exact shell/execution command.
2. Provide the "Laziests Passing Code" (LPC) snippet that attempts to trick the gate.
3. Validate that the gate FAILS against the LPC snippet. If it passes, redesign the gate.

---

[EXECUTION BEGINS NOW]