# Pre-v0.5.0 Execution Prompts: Milestones, Backlog, and Active Sprints

This document contains three sequential, state-of-the-art prompts for executing the project planning phase. Run these prompts in strict sequential order.

---

# PROMPT 1: Technical PhD-Level Milestones Definition (Macro Roadmap v0.5.0 → v1.0.0)

```markdown
# ROLE
You are the Project Lead, the Tech Lead, and a Senior Software Architect.

# CONTEXT & INGESTION
Read and analyze the following canonical sources thoroughly before writing:
1. `SYSTEM_SPEC_THEORY.md` (The theoretical specifications and architectural axioms).
2. `SYSTEM_SPEC_ASBUILT.md` (The forensic reality map of the live codebase).
3. `SYSTEM_SPEC_DRIFTS.md` (The gap and drift diagnostic report).
4. `docs/01_specs/` (The canonical backend and frontend specification corpus).
5. `docs/00_executive/vision.md` (The 14-tier cosmological and biological hierarchy).

# GOAL
Deliver a comprehensive, PhD-level technical milestones specification in `docs/02_roadmap/milestones.md` defining the strategic evolutionary trajectory of the Vanguard / GTS framework from version `v0.5.0` to `v1.0.0`.

# REQUIREMENTS
1. **PhD-Level SOTA Technical Depth**:
   - Provide formal architectural definitions, mathematical formulations, and state machine transitions for each macro milestone.
   - Ground every milestone in rigorous computer science (formal capability attenuation, cryptographic provenance, context economics, and distributed systems).
2. **Sequential Milestone Breakdown**:
   - **v0.5.0 (Empirical Baseline)**: Greenfield autonomous coding harness, live model integration, strict `--in-place` writes, and signed `AutonomousGrant` boundaries.
   - **v0.6.0 (Decoupled Micro-Kernel Substrate)**: Hexagonal plugin decoupling, abstract environment ports, and modular context/routing policies.
   - **v0.7.0 (Comparative Benchmarking & Model Kits)**: Tree-sitter polyglot AST indexers, prompt caching, empirical topology bake-offs, and multi-tier model ensembles.
   - **v0.8.0 (Cognitive Layer & Memory Graphs)**: Competence & Evidence Graphs ($G_C, G_E$), episodic memory, and autonomous scaffolding self-optimization.
   - **v0.9.0 (Meta-Cognitive Architecture)**: Evolutionary workflow polymers, dual-process System 1/System 2 reasoning, and epistemic uncertainty modeling.
   - **v1.0.0 (Unified Sovereign Product)**: Production TUI CLI, Standalone Tauri GUI IDE (`vanguard-gui`), and emergent self-assembling interfaces.
3. **Formal Verification & Exit Criteria**:
   - For every milestone, specify non-negotiable exit criteria, verifiable behavioral proofs (e.g. un-mocked `oracle_green` benchmarks), TCB budget constraints, and security invariants.
4. **Target File**:
   - Write the complete result directly to `/home/rocha/Coding/Aether-D-System/docs/02_roadmap/milestones.md`. Do not delete or mutate any existing source files.
```

---

# PROMPT 2: Single-Source-of-Truth Technical Backlog

```markdown
# ROLE
You are the Project Lead, the Tech Lead, and a Senior Software Architect.

# CONTEXT & INGESTION
Read and analyze the following sources before writing:
1. `docs/02_roadmap/milestones.md` (The milestones defined in Prompt 1).
2. `SYSTEM_SPEC_DRIFTS.md` (The drift diagnostic report, specifically all `[DETERIORATION]` and `[OPTIMIZATION]` items).
3. `SYSTEM_SPEC_ASBUILT.md` (The operational codebase reality).
4. `docs/01_specs/backend/` and `docs/01_specs/frontend/`.

# GOAL
Deliver an authoritative, machine-readable single-source-of-truth task pool in `docs/02_roadmap/backlog.md` that maps all actionable engineering tasks for `v0.5.0` in granular detail, plus high-level research epics for `v0.6.0+`, marking each task with an explicit `[TODO]` or `[DONE]` status.

# REQUIREMENTS
1. **Granular v0.5.0 Task Extraction & Categorization**:
   - Extract every actionable remediation from `SYSTEM_SPEC_DRIFTS.md` (e.g. D-02 evaluation trigger, D-05 justifying spans, D-06 child provenance, D-10 reground policy, D-14 event kinds).
   - Incorporate all active development guide items (e.g. `--in-place` writes, `AutonomousGrant` CLI wiring, `format_skill_index` compiler binding, `_fake_backend` relocation).
   - Incorporate frontend pending tasks from `FE-01` (`FE-2-8`, `FE-2-9`, `FE-3-1` through `FE-3-7`).
2. **Rigorous Task Specification Format**:
   - Assign each task a permanent, unique identifier (e.g. `TSK-CORE-001`, `TSK-CLI-002`, `TSK-EVAL-003`).
   - For every task, define: Title, Owning Subsystem / Path, Milestone Anchor (v0.5.0 .. v1.0.0), Requirement Anchor (`[REQ-xxx]`), Status (`[TODO] ❌` or `[DONE] ✅`), Clear Description, and Exact Verification Command / Test Proof.
3. **No Unbacked Claims**:
   - Mark a task `[DONE] ✅` only if empirical code and passing unit tests already exist in `vanguard/packages/` or `vanguard/clients/`. Otherwise, mark it `[TODO] ❌`.
4. **Target File**:
   - Write the complete backlog directly to `/home/rocha/Coding/Aether-D-System/docs/02_roadmap/backlog.md`.
```

---

# PROMPT 3: Active Sprint Execution Board (v0.5.0 Milestone ONLY)

```markdown
# ROLE
You are the Project Lead, the Tech Lead, and a Senior Software Architect.

# CONTEXT & INGESTION
Read and analyze the following sources before writing:
1. `docs/02_roadmap/milestones.md` (The technical milestones).
2. `docs/02_roadmap/backlog.md` (The prioritized task pool).
3. `SYSTEM_SPEC_THEORY.md` and `SYSTEM_SPEC_ASBUILT.md`.
4. `AGENTS.md` (Repository guidelines, package lattice, test rules, and PR requirements).

# GOAL
Deliver the active sprint execution plan in `docs/03_sprints/sprint_active.md` **focusing strictly on the active v0.5.0 Milestone** (following true Agile / Iterative Research methodology). Break down v0.5.0 into concrete, parallel developer lanes with actionable daily tasks, subtasks, file ownership boundaries, and automated verification commands.

# REQUIREMENTS
1. **Strict v0.5.0 Scope (True Agile Execution)**:
   - Do NOT plan future sprints for v0.6.0+ (those are research horizons that will evolve based on v0.5.0 empirical findings). Focus 100% of the sprint board on delivering the **v0.5.0 Empirical Baseline**.
2. **Multi-Lane Parallel Architecture**:
   - Break down the active sprint into 3 isolated, concurrent developer lanes with zero file-collision overlap:
     - **Lane 1 (ALFA — Architecture & Orchestration)**: Episode engine cleanup, playbook interpreter, and session lifecycle.
     - **Lane 2 (BETA — Security, Progress & Verification)**: `AutonomousGrant` wiring, progress fingerprints, event ledger completeness, and evaluator daemon triggers.
     - **Lane 3 (GAMMA — Product CLI & Live Proof)**: `--in-place` operator writing, CLI streaming bridge, and live greenfield acceptance campaign.
3. **Granular Task & Subtask Structure**:
   - Link every sprint item directly to its corresponding `TSK-xxx` ID in `docs/02_roadmap/backlog.md`.
   - Specify: Target production write scope (files permitted to create/edit), Invariants to uphold, Step-by-step implementation sequence, and Definition of Done.
4. **Automated Verification Harness**:
   - Provide exact shell commands for unit tests, active contract tests (`tools/run_active_contract_tests.py`), boundary checks (`tools/check_boundaries.py`), and TCB budget checks (`tools/check_tcb_budget.py`).
5. **Target File**:
   - Write the complete active sprint board directly to `/home/rocha/Coding/Aether-D-System/docs/03_sprints/sprint_active.md`.
```
