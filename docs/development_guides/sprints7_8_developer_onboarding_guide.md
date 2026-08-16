# Developer Onboarding & Architecture Guide: Sprints 7 & 8 (Phase 3)

**Target Audience:** All Software Engineers & AI Specialists on Aether Vanguard  
**Scope:** Architecture Principles, Orders of Abstraction, Testing Workflows with LAM/LAR, Coding Standards & Guardrails  

---

## 1. The Core Vision: Decoupled & Modular Architecture

Aether Vanguard is designed with a **strict, decoupled 3-tier architecture**:

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. DOMAIN (vanguard/packages/domain/)                                  │
│    Pure data structures, immutable contracts, zero I/O, zero deps.    │
├────────────────────────────────────────────────────────────────────────┤
│ 2. KERNEL (vanguard/packages/kernel/)                                  │
│    Capability broker, budget attenuation, resource grants, audit log.  │
│    ⚠️ FROZEN: Modifying kernel code during competitor packs is FORBIDDEN.│
├────────────────────────────────────────────────────────────────────────┤
│ 3. ADAPTERS & MANIFESTS (agency/manifests/ & adapters/)                │
│    Pure data JSON/YAML packs, environment sandboxes, model routers.    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Orders of Abstraction: Emergent Depth vs. Class Bloat

### The Scientific Principle (`GTS-13C §3.6`)
In nature, biology did not create `class Cell(Polymer)` or `class Organism(Cell)`. Nature created a single recursive replicator under selection.

In Vanguard, we do **NOT** create heavy OOP inheritance trees. We implement **one single recursive coordinator** (`EpisodeCoordinator`).

```
┌────────────────────────────────────────────────────────────────────────┐
│ Coordination Depths (Emergent Labels in SQLite Trace Store):           │
│                                                                        │
│ Depth 0 = ATOM       -> Individual frozen tool (view_file, edit_file)  │
│ Depth 1 = MOLECULE   -> Single scenario / single file fix              │
│ Depth 2 = POLYMER    -> Multi-file refactor / escalation ladder        │
│ Depth 3 = CELL       -> Autonomous agent loop with stack trace repair  │
│ Depth 4+ = BODY      -> Multi-agent recursive sub-task swarms          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Primitives & The Frozen Atom Set

Within the coding environment, capability grows by **composition**, not by adding dozens of ad-hoc tools. A large tool catalog burns prompt tokens and degrades model accuracy.

The **Frozen Atom Set** is:
1. `view_file` (or `fs.read`): Read file contents within workspace.
2. `edit_file` (or `patch.apply`): Apply surgical contiguous text replacement.
3. `run_command` (or `proc.exec`): Execute deterministic bash command / pytest in isolation.
4. `list_dir` (or `fs.list`): List directory tree.
5. `grep_file` (or `fs.search`): Search regular expression patterns across files.

---

## 4. The Developer Testing Workflow: LAM & LAR

To achieve maximum development velocity without burning financial budget or waiting on slow cloud APIs:

```
┌────────────────────────────────────────────────────────────────────────┐
│ STEP 1: Fast Inner-Loop Testing (LAM Offline Replay)                    │
│ Command: python3 tools/002_LLM_API_MOCK/simulate.py                    │
│ Speed: < 35ms per scenario | Cost: $0.00 | Flakiness: Zero             │
├────────────────────────────────────────────────────────────────────────┤
│ STEP 2: Local GPU Validation (Local Ollama)                            │
│ Command: python3 tools/002_LLM_API_MOCK/ladder.py --backend ollama     │
│ Models: llama3.2:3b, deepseek-r1:14b, qwen3.6:27b                      │
├────────────────────────────────────────────────────────────────────────┤
│ STEP 3: Wave-Based CI Verification Gate                                │
│ Command: python3 -m unittest discover -s test -t .                     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Coding Standards & Guardrails

1. **Pure Data Manifests:** All competitor shapes (`claude-shaped`, `opencode-shaped`) MUST be written as pure JSON/YAML in `vanguard/packages/agency/manifests/`. Never write `if model == 'claude':` in Python code.
2. **Deterministic Error Handling:** All tool errors must return structured JSON error payloads, never raw uncaught Python exceptions.
3. **Budget Attenuation Invariant:** When an episode spawns a child episode, the child budget is subtracted from the parent budget. Total budget can never increase during execution.
4. **Wave-Based Testing:** Avoid testing after every 3 lines of code. Build feature blocks and test at Mid-Sprint and End-Sprint waves.
