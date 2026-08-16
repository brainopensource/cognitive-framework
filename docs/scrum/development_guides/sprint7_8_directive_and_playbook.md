# Phase 3 (Sprints 7 & 8) Executive Engineering Directive & Developer Playbook

**To:** Scrum Master, Project Lead, Tech Lead, Dev A (Lane A), Dev B (Lane B)  
**From:** CTO & Principal AI Specialist Architect  
**Target Branch:** `sprints7-8/integration`  
**Milestone:** Phase 3 — Manifest Engine, Competitor Reconstructions & Measurement Laboratory (v0.4.1 Baseline)  

---

## 1. Executive Strategy & Operational Governance

### Core Directives

1. **Zero Architecture Drift (`VG-00 PR-3`):**  
   Normative specifications in [`docs/main_v4/`](file:///home/rocha/Coding/Aether-D-System/docs/main_v4/) are binding contracts. Reconstructions must be **pure-data JSON/YAML manifests**. Modifying `vanguard/packages/kernel/` or `agency/episode/` for a competitor pack is strictly forbidden.
2. **Emergent Coordination, Not Class Bloat (`GTS-13C §3.6`):**  
   Do **NOT** create heavy OOP hierarchies like `class Cell(Polymer)` or `class Organism(Cell)`. The hierarchy (Atom $\to$ Molecule $\to$ Polymer $\to$ Cell $\to$ Body) is an **emergent observational finding** logged in [`tools/002_LLM_API_MOCK/lam.sqlite`](file:///home/rocha/Coding/Aether-D-System/tools/002_LLM_API_MOCK/lam.sqlite) via recursion depth.
3. **Model Tier Testing Rule:**
   - **Inner Loop (Dev Velocity):** Use the **LAM Engine** (`tools/002_LLM_API_MOCK`) for instant < 30ms $0 cassette replays across 36 gold scenarios.
   - **Complex Validation:** Use escalated local GPU Ollama models (`llama3.2:3b`, `qwen3.6:27b`).
   - **Cloud OpenRouter API:** Deferred until final gate signoff.
4. **Wave-Based Testing & High Velocity:**  
   Developers focus on building core feature blocks first. Automated test suites execute in two main waves (Mid-Sprint Wave and End-Sprint Wave) to prevent micro-testing stalls.
5. **Backlog Discipline:**  
   Track all major task completions directly in `todo_list.md` with structured `[X]` checkboxes.

---

## 2. Sprint 7 & 8 Architecture & Folder Layout

```
Aether-D-System/
├── docs/agile/sprint7_8/            # Sprint 7-8 backlog, ICD, & gate evidence
│   ├── sprint7_8_directive_and_playbook.md # Executive playbook
│   ├── lane-a-manifests-and-packs.md       # Dev A specification
│   └── lane-b-measurement-lab.md          # Dev B specification
├── docs/development_guides/
│   └── sprints7_8_developer_onboarding_guide.md # Architecture & developer manual
├── lab/                             # Order 5 Measurement Laboratory (Dev B)
│   ├── bench.py                     # Paired McNemar benchmark runner
│   └── diff.py                      # Harness diff & trace comparison tool
└── vanguard/packages/
    ├── agency/
    │   └── manifests/               # Order 4 Pure-Data Manifest Packs (Dev A)
    │       ├── loader.py            # Dynamic manifest and alias loader
    │       ├── discovery.py         # AGENTS.md / CLAUDE.md discovery parser
    │       ├── vg-code-default/
    │       ├── vg-code-claude-shaped/
    │       ├── vg-code-opencode-shaped/
    │       ├── vg-code-swe-mini/
    │       └── vg-shell-only/       # Undeletable baseline control pack (Dev B)
    └── runtime/
        └── coordination.py          # Thin EpisodeCoordinator & depth logger (Dev B)
```

---

## 3. Parallel Developer Work Allocation (Lane A vs. Lane B)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ LANE A (DEV A): MANIFEST ENGINE & RECONSTRUCTION PACKS                                 │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ • Task A.1 (S7): Manifest Loader & Aliases Engine (vanguard/packages/agency/manifests) │
│   - Parse manifest declarations (manifest.json, aliases.json, tool-schemas/).         │
│   - Bind model-declared tool aliases to canonical verbs (e.g. read -> fs.read).        │
│ • Task A.2 (S7): Dynamic Workspace Discovery (AGENTS.md / CLAUDE.md)                   │
│   - Auto-discover local repo instructions via standard fs.read observation in L3/L4.   │
│ • Task A.3 (S8): Reconstruction Manifest Packs                                         │
│   - Build vg-code-claude-shaped, vg-code-opencode-shaped, vg-code-swe-mini.             │
│   - Verify packs require ZERO code changes in kernel/ or agency/episode/.              │
└────────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────────┐
│ LANE B (DEV B): MEASUREMENT LABORATORY & CONTROL BENCH                                 │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ • Task B.1 (S7): Lightweight EpisodeCoordinator & Depth Logger                         │
│   - Implement vanguard/packages/runtime/coordination.py.                              │
│   - Record episode recursion depth (Atoms -> Molecules -> Polymers) in lam.sqlite.   │
│ • Task B.2 (S8): Control Baseline Pack (vg-shell-only)                                 │
│   - Freeze un-deletable control arm with single proc.exec capability.                  │
│ • Task B.3 (S8): Measurement Laboratory CLI (lab harness bench | diff)                 │
│   - Build lab/bench.py and lab/diff.py for paired McNemar statistical testing.        │
│   - Measure verifier-deployment gap with cassette and live Ollama runs.                │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Junior Developer Pitfalls & Prevention Guardrails

| Common Anti-Pattern / Pitfall | Prevention Rule & Technical Constraint |
| :--- | :--- |
| **Hardcoding Competitor Logic in Python** | **Forbidden.** Never write `if model == 'claude':` logic in Python. Map all verbs in data manifests via `aliases.json`. |
| **Creating OOP Inheritance Trees (`class Cell`)** | **Forbidden.** Do NOT write `class Cell(Polymer)`. Use the single `EpisodeCoordinator` and log depth dynamically to `lam.sqlite`. |
| **Modifying Microkernel Code** | **Forbidden.** `vanguard/packages/kernel/` is frozen. Any pack requiring kernel diffs fails CI boundaries (`tools/check_boundaries.py`). |
| **Micro-Testing Stall** | **Forbidden.** Do NOT run unit tests after every 5 lines of code. Build in feature waves; execute test runner at Mid-Sprint and End-Sprint waves. |
| **Over-Creating Duplicate Markdown Files** | **Forbidden.** Update existing backlog files (`todo_list.md`) with `[X]` checkboxes instead of creating temporary duplicate files. |

---

## 5. Wave-Based Sprint Execution Plan

### Wave 1: Mid-Sprint Execution (Target Day 3)
- **Dev A:** Land Manifest Loader (`loader.py`), `aliases.json` translator, and `AGENTS.md` parser (`discovery.py`).
- **Dev B:** Land `EpisodeCoordinator` in `runtime/coordination.py` and `lam.sqlite` depth logger.
- **Mid-Sprint Test Wave:** Run `python3 -m unittest discover -s test -t .` once to verify Wave 1 integration. Update `todo_list.md`.

### Wave 2: End-Sprint Execution & Release Gate (Target Day 6)
- **Dev A:** Land the 3 reconstruction packs (`vg-code-claude-shaped`, `vg-code-opencode-shaped`, `vg-code-swe-mini`).
- **Dev B:** Land `vg-shell-only` baseline control pack and `lab harness bench | diff` laboratory tools.
- **Final Sprint Verification Wave:**
  ```bash
  python3 tools/check_backend_artifacts.py --release
  python3 tools/check_boundaries.py
  python3 tools/check_tcb_budget.py
  python3 tools/scan_secrets.py
  python3 -m unittest discover -s test -t .
  ```
