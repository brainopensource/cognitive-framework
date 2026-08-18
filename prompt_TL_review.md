# TASK: Comprehensive Pre-v0.5.0 Architectural & Execution Audit (Theoretical vs. As-Built Analysis)

## CONTEXT & OBJECTIVE
We are preparing for a ground-up codebase refactor/rewrite for v0.5.0. Our project, `vanguard`, is an agentic coding harness framework (similar in scope to Claude Code CLI, OpenCode, Codex). During v0.4.x, execution accelerated and implementation decisions diverged from our initial theoretical blueprints in `docs/main_v4/`.

Before cutting any v0.5.0 code, we must quantify architectural drift, evaluate whether runtime adaptations outclass original designs, and baseline our actual feature completion against our roadmap milestones.

## SCOPE & BOUNDARIES
- **Target Domain**: BACKEND CORE & ENGINE ONLY (`vanguard/packages/`).
- **Out of Scope**: All frontend components, TUI, CLI presentation layers (`vanguard/clients/cli/`), and GUI integrations.
- **Focus**: Core orchestration, harness abstractions, state machines, tool-use execution, protocol bindings, capability attenuation kernel, context compaction, and evaluation backends.

---

## EXECUTION PROTOCOL (3-PHASE AUDIT)

### PHASE 1: THEORETICAL BASELINE SYNTHESIS (`SYSTEM_SPEC_THEORY.md`)
1. Ingest all architectural specs, RFCs, and protocol definitions located in `docs/main_v4/` (specifically `VG-00` through `VG-12` and `GTS-13C`).
2. Extract all core engineering invariants, execution flows, system primitives, capability models, and design patterns.
3. Synthesize these specifications into a single root file: `SYSTEM_SPEC_THEORY.md`.
   - **CONSTRAINT**: Target compression ratio is ~30–40% of original token/word count without loss of technical semantics.
   - **REQUIREMENT**: Structure the document logically so that code symbols, module paths, and function signatures can be anchored to theoretical concepts in future phases.

### PHASE 2: AS-BUILT SYSTEM MAP (`SYSTEM_SPEC_ASBUILT.md`)
1. Analyze the production backend codebase in `vanguard/packages/` alongside the root `README.md`.
2. Map the operational reality: actual component topologies, concrete interfaces, data pipelines, state management, budget tracking, and side-effect handling.
3. Generate `SYSTEM_SPEC_ASBUILT.md` in the workspace root.
   - **CONSTRAINT**: Strictly mirror the structural schema, taxonomy, and section hierarchy established in `SYSTEM_SPEC_THEORY.md` to ensure structural alignment for differential analysis.

### PHASE 3: GAP & DRIFT DIAGNOSTIC REPORT (`SYSTEM_SPEC_DRIFTS.md`)
Synthesize the theoretical baseline (`SYSTEM_SPEC_THEORY.md`) against the production reality (`SYSTEM_SPEC_ASBUILT.md`) into a definitive diagnostic report: `SYSTEM_SPEC_DRIFTS.md`.

Structure the diagnostic report into four mandatory sections:
1. **Architectural & Structural Divergences**:
   - Identify missing, modified, or emergent abstractions, interfaces, and control flows.
   - Categorize each drift: `[DETERIORATION]` (Tech Debt / Compromise), `[OPTIMIZATION]` (Pragmatic/Superior Adaptation), or `[NEUTRAL]` (Refactoring / Renaming).
2. **Qualitative Trade-off & Engineering Evaluation**:
   - Analyze *why* implementation diverged from theory.
   - Detail systemic implications of keeping as-built implementations vs. reverting to original specifications during the v0.5.0 rewrite.
3. **Roadmap & Feature Completion Matrix**:
   - Map implemented components against planned v0.4/v0.5 milestones.
   - Quantify true percentage-to-completion per subsystem (e.g., Tool Execution, Capability Attenuation, Context Compression, Agent Orchestration).
4. **v0.5.0 Refactor Action Plan & Directives**:
   - Define concrete recommendations on what to PRESERVE from `vanguard/packages/`, what to DISCARD, and what theoretical specs from `docs/main_v4/` must be restored.

---

## DELIVERABLES CHECKLIST
- [ ] `SYSTEM_SPEC_THEORY.md` (Root)
- [ ] `SYSTEM_SPEC_ASBUILT.md` (Root)
- [ ] `SYSTEM_SPEC_DRIFTS.md` (Root)
