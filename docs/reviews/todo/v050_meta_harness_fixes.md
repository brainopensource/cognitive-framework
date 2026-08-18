# Vanguard Evaluation: Framework for Building Agentic Coding CLI Tools

**Audit 2026-08-17 (first headless coding CLI):** `[DONE]` exists on the episode/`lab_driver` path. `[TODO]` still required for that cut. `[LATER]` competitor-parity or v0.5 playbooks — not the first CLI. The recommended first delivery is **`HarnessSession` + `vg-code-default` + `lab_driver`**, not making `CodingRunCoordinator` the product.

## Executive Summary

Vanguard has an **exceptionally well-designed architecture** at the specification level, but the current implementation has a **critical architectural contradiction** that prevents it from being a competitive coding harness CLI. The framework is well-positioned to grow modularly, but the current coding harness implementation is architectural debt that must be resolved before it can compete with Claude Code, Cline, or Codex.

---

## 1. Architecture Quality: Strong Foundation

### What's Excellent

**The Six-Plane Decomposition (§3)** is genuinely sophisticated. Separating Interaction, Cognition, Control, Workload, Evidence, and Evolution into distinct OS-level identities with different credential sets is the right security model for an agent that edits code. The fact that Phase 0 collapses some planes into one process but *documents exactly which guarantees weaken* (§12) is unusually honest engineering.

**The Episode Loop** — `observe → propose → authorise → effect → receipt → evaluate` — is the correct abstraction. The architecture doc's §2 critique of static DAG workflows is sharp and correct: "All agentic behaviour lived inside one method, inside one node, inside one step" and "The agent was a leaf of the workflow rather than its substrate."

**The Kernel Dispatch Sequence (S0–S12)** in `kernel/dispatch.py` is meticulously designed. Every ordering rule (K-04 through K-47) is backed by a defect that actually shipped. The lease-before-emit ordering, the classifier-as-call-not-constant, the intent-before-effect durability — these are hard-won lessons encoded as structure.

**The Manifest System** is the right approach to harness-as-configuration. `vg-code-claude-shaped`, `vg-code-default`, `vg-code-opencode-shaped`, `vg-code-swe-mini` are all JSON files that compose tools, prompts, policies, and evaluators. This is exactly how you avoid coupling the framework to any specific harness.

**The Layer Topology** with strict import rules (domain → ports → kernel → agency → runtime → adapters) and tool-enforced boundaries (`check_boundaries.py`) is proper modular architecture.

**The Context Engineering Model (L1–L5)** with cache-aware layer boundaries, structured consolidation, and operator isolation is more sophisticated than what most coding agents implement.

---

## 2. The Critical Architectural Contradiction

### The Problem: Two Competing Execution Models — `[DONE]` as diagnosis; first CLI uses the engine, not the DAG

The architecture document §2 explicitly **rejects** the static DAG workflow model:

> "The episode loop is at least as expressive as the static topology language rejected above, at a small fraction of the machinery."
> "Static topology is a strict subset."

Yet `runtime/coding_coordinator.py` + `runtime/coding_plan.py` implement **exactly the rejected model**:

```python
class CodingPhase(str, Enum):
    DISCOVER = "discover"
    PLAN = "plan"
    EXECUTE = "execute"      # ← static step execution
    VERIFY = "verify"         # ← per-step verification
    DIAGNOSE = "diagnose"
    REPLAN = "replan"
    REVIEW = "review"
    FINAL_VERIFY = "final_verify"
```

The coordinator runs a plan DAG with dependency-ordered steps, per-step verification gates, and a bounded replan loop. `[DONE]` this file exists. `[TODO]` HarnessSession binder. `[LATER]` playbook. **First CLI: ignore this DAG.**

Meanwhile, `agency/episode/engine.py` implements the **correct** loop — the one the architecture says should be the only execution primitive. But the coding coordinator wraps it, constrains it, and prevents it from being the primary agentic surface.

### The Consequence

This means Vanguard currently has:
- A **spec** that says "the episode loop is the only execution primitive" (Axiom A-01)
- An **engine** that implements that loop correctly
- A **coding coordinator** that ignores it and uses a static DAG instead

The coding harnesses (`vg-code-default`, `vg-code-claude-shaped`) are thin prompt/tool configurations. The actual coding behavior — plan→step→execute→verify→replan — is **hardcoded in runtime code**, not defined by the harness. This directly violates Claim C-01: "Every reference harness is expressible as configuration, with no core change."

---

## 3. What's Missing to Compete with Claude Code / Cline / Codex

### Missing Capabilities (Gap Analysis)

First CLI uses the **episode loop** (`lab_driver`), not the coordinator DAG. Keep one-effect-per-turn. Do not chase this table as a backlog.

| Capability | Claude Code | Cline | Codex | First CLI |
|---|---|---|---|---|
| **True agentic loop** (agent decides what to do each turn) | ✅ | ✅ | ✅ | `[DONE]` engine; `[TODO]` do not ship coordinator DAG as the product |
| **Tool-use streaming** (real-time output) | ✅ | ✅ | ✅ | `[LATER]` |
| **MCP server integration** | ✅ | ✅ | ✅ | `[LATER]` ADR-0066 rules only |
| **Diff preview & approval UI** | ✅ | ✅ | ✅ | `[LATER]` TUI; `[TODO]` labelled CLI grant |
| **Sub-agent delegation** (spawn/parallel) | ✅ | ✅ | ⚠️ | `[DONE]` engine; `[TODO]` pack expose |
| **LSP integration** | ✅ | ❌ | ✅ | `[LATER]` |
| **Session resume** | ✅ | ✅ | ✅ | `[DONE]` ledger; `[TODO]` `lab_driver --resume` |
| **Parallel tool execution** | ✅ | ⚠️ | ✅ | `[LATER]` (one effect/turn is the cut) |
| **Real-time cost tracking** | ✅ | ✅ | ✅ | `[DONE]` telemetry; `[TODO]` operator JSON |
| **Checkpoint/rollback** | ✅ | ✅ | ✅ | `[LATER]` |
| **Multi-file edit transactions** | ✅ | ✅ | ✅ | `[LATER]` keep single `patch.apply` |
| **Prompt caching** | ✅ | ✅ | ✅ | `[LATER]` |
| **Filesystem watching** | ✅ | ✅ | ✅ | `[LATER]` |
| **AST-aware editing** | ✅ | ❌ | ✅ | `[LATER]` |
| **Image/multimodal input** | ✅ | ✅ | ✅ | `[LATER]` |
| **Web search / RAG** | ✅ | ❌ | ✅ | `[LATER]` |
| **Custom tool authoring** | ✅ | ✅ | ✅ | `[DONE]` pack JSON; `[LATER]` dynamic |
| **Multi-model routing** | ✅ | ✅ | ✅ | `[DONE]` modules; `[TODO]` one router on `lab_driver` |

### The Core Gap

The fundamental missing piece isn't any single feature — it's that **the coding harness doesn't use the episode engine as its primary execution surface**. Claude Code, Cline, and Codex all work as:

```
User gives task → Agent explores → Agent decides what to do → Agent does it → Agent observes → Agent decides next step → ...
```

This IS the episode loop. Vanguard has it. But the coding coordinator replaces it with:

```
User gives task → Planner creates plan DAG → Execute step 1 → Verify step 1 → Execute step 2 → Verify step 2 → ... → Final verify
```

The agent is demoted from "entity that decides what to do" to "entity that executes pre-planned steps." This is the exact anti-pattern the architecture doc diagnosed.

---

## 4. Architecture Quality for Growth & Self-Improvement

### What's Well-Designed for Evolution

1. **Harnesses as data, not code.** Adding a new coding style (e.g., "cline-shaped") requires only a new manifest directory with JSON files. The binding table in `root.py` maps verbs to adapters — new verbs are rows, not code changes.

2. **Operators as data.** The architecture's claim that "operators are addressable, versioned, replaceable entries" means the system can improve its own operators without changing the runtime. This is the foundation for self-improvement.

3. **Exterior evaluator.** The Evidence plane is a separate process with its own identity. The agent cannot grade itself. This is the single most important property for a self-improving system — without it, "improvement" is just the agent learning to please itself.

4. **The kernel is frozen and small.** The TCB budget is tracked (`tools/kernel-tcb-budget.json`). The dispatch sequence has exactly one path from proposal to effect. This is correct for a system that will eventually modify its own components.

5. **Context isolation.** Operator spawn creates isolated contexts. A child's exploration never pollutes the parent's window. This is essential for parallel exploration and safe delegation.

6. **The ledger as single source of truth.** Everything is an event. Every surface is a projection. This means replay, audit, and measurement are built on the same substrate.

### What Threatens Modularity

1. **`runtime/coding_coordinator.py` is the capture the architecture warned about.** The doc says: "A coding-first architecture risks permanent capture by coding's logic." The coding coordinator is exactly that — coding-specific workflow logic living in the runtime package, not in a harness.

2. **The `runtime/` package is bloated with application logic.** It contains `coding_coordinator.py`, `coding_plan.py`, `coding_progress.py`, `coding_verification.py`, `coding_budget.py`, `repair.py`, `scoring.py`, `tier_escalation.py`, `model_selection.py`, `outcome_labels.py`, `task_sets.py`, `skill_index.py`. These are application concerns that should live in harnesses or adapters, not in the composition root.

3. **No harness can define its own execution strategy.** A harness that wants "pure agentic loop, no pre-planning" can't express it. A harness that wants "plan-guided with agentic freedom within phases" can't express it. The execution strategy is hardcoded.

4. **The coding coordinator and episode engine are unaware of each other's capabilities.** The engine supports `spawn` (sub-agents), context isolation, structured consolidation, no-progress detection, and budget-governed recursion. The coding coordinator uses none of these.

---

## 5. Verdict

### Is the framework good?

**Yes, at the specification and kernel level.** The architecture is genuinely well-designed. The plane decomposition, the episode loop, the kernel dispatch sequence, the manifest system, the context engineering model, and the evaluator exteriority are all correct decisions. The architecture documents are unusually rigorous and honest about limitations.

### Are the solutions built with it good?

**No, the current coding harness is not competitive.** The `CodingRunCoordinator` implements the rejected static DAG model. It doesn't use the episode engine's capabilities. It's missing streaming, MCP, LSP, parallel execution, sub-agents, diff preview, session resume, and most features that make Claude Code/Cline/Codex usable day-to-day.

### Can it grow without refactoring?

**Partially.** The manifest system, port/adapters, and kernel are well-isolated and can grow. But the `runtime/coding_coordinator.py` pattern is architectural debt that will force refactoring. Every new coding harness capability currently requires changes to runtime code rather than harness configuration. The architecture doc's own Claim C-01 ("every reference harness is expressible as configuration, with no core change") is currently **falsified** by the coding coordinator's existence.

### The Path Forward

**First CLI `[TODO]`:** ship `lab_driver` as the agentic surface (`--in-place`, labelled writes / `AutonomousGrant`, live one `patch.apply`). Do not make `CodingRunCoordinator` the product.

**v0.5 `[LATER]`:** turn the coordinator DAG into a playbook (`advisory` → `guided` → `strict`). At `strict`, a playbook IS a graph, recovered as a parameter rather than as architecture.

After the first CLI writes in-place, streaming / MCP / LSP / parallel / TUI remain harness capabilities — not this cut.