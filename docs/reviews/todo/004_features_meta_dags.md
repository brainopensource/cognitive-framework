# Vanguard Code Quality & Architecture Deep-Dive Evaluation

**Audit 2026-08-17 (first headless coding CLI):** `[DONE]` observed in tree. `[TODO]` still open. `[LATER]` v0.5 / not the first CLI. First delivery stays on the free episode loop (`lab_driver` → `HarnessSession`). Optional DAGs belong in a playbook after that loop actually writes in-place.

After reading the architecture docs, the full S28–S34 development guide, the roadmap, and the actual code in `vanguard/packages/`, here is a comprehensive evaluation.

---

## 1. After S28–S34: Will We Have Well-Designed Code?

**No — the S28–S34 plan will produce well-tested but architecturally compromised code.** The plan is internally consistent and the tests will pass, but it doubles down on the architectural contradiction I identified earlier. Here's why:

### The Contradiction Is Being Codified, Not Resolved — `[DONE]` as diagnosis; first CLI does **not** ship this DAG

The S28–S34 development guide explicitly mandates:

```
CodingRunCoordinator → HarnessSession.run() → EpisodeEngine → Kernel.dispatch
```

This looks correct on the surface — the coordinator "schedules episodes but dispatches no model-requested effect." But the coordinator's state machine (`DISCOVER → PLAN → EXECUTE → VERIFY → DIAGNOSE → REPLAN → ...`) is a **static DAG workflow** that constrains the episode engine to execute pre-planned steps. The agent is not free to decide what to do each turn — it receives "exactly one ready plan step" and "one-effect-per-turn conditioning."

The architecture doc §2 explicitly rejected this model:
> "All agentic behaviour lived inside one method, inside one node, inside one step"
> "The agent was a leaf of the workflow rather than its substrate"

The S28–S34 plan makes the agent a leaf of the coordinator's workflow. The coordinator decides the phase, selects the step, and routes the model. The agent executes.

### The DAG Question

You said:
> "DAGs should be only optional cases, after we gathered the metadata of lots of battle tested processes and stored them, so we can try solutions mixing free flexible loops where the LLM decides the order, but also try some small proteins / polymers that are dags"

This is exactly what the architecture doc's playbook system (§11) was designed for. The rigidity dial (`advisory` → `guided` → `strict`) lets a playbook be a graph at `strict` — recovered as a parameter, not as architecture. But the S28–S34 plan hardcodes the DAG in the coordinator. A harness that wants "pure agentic loop, no pre-planning" cannot express it. A harness that wants "plan-guided with agentic freedom within phases" cannot express it.

**The fix is not to delete the coordinator — it's to make the coordinator a playbook interpreter, not a hardcoded state machine.** The coordinator should read a playbook that says "at rigidity `guided`, enforce phases in order but let the agent loop freely within each phase." The current coordinator hardcodes `PLAN → EXECUTE → VERIFY` as the only possible workflow.

---

## 2. Real Code Quality Issues Found

### 2.1 Dead / Redundant Code — `[TODO]` tidy (not first CLI)

| File | Issue |
|---|---|
| `runtime/repair.py` | `[TODO]` `drive_until_green` is the **first-CLI** loop. `coding_coordinator.py` is a more complex DAG. Authoritative for this cut: `lab_driver` + `drive_until_green`. |
| `runtime/tier_escalation.py` | `[TODO]` tidy later. Three escalation mechanisms exist (`tier_escalation`, coordinator `_route()`, `coding_progress`). First CLI: do not add a fourth. |
| `runtime/model_selection.py` | `[DONE]` `select_model()` is what `lab_driver` uses. `[TODO]` consolidate RoleAwareRouter / coordinator `_route()` — `[LATER]` v0.5. |
| `runtime/lab_driver.py` | `[DONE]` `_verify()` / declared `verify.sh` is the first-CLI oracle. `[TODO]` do not merge coordinator verifiers into this cut. |
| `runtime/coding_entrypoint.py` | `[DONE]` as CLI bridge; `[TODO]` `_fake_backend()` still in production — `--live` refused until `HarnessSession` binder. |

### 2.2 Coupling Issues

**`runtime/root.py` is 1343 lines and does too many things:**
- Manifest loading and composition
- Harness freezing
- Environment adapter bridging (`_EnvironmentEffect`)
- Ledger bridging (`LedgerBridge`)
- Context compilation (`_LayeredOperator`)
- Session lifecycle (`HarnessSession`)
- Approval flow (`_resolve`, `_SwappablePolicy`)
- Evaluator binding
- Budget parsing
- Workspace discovery
- Index binding

This is the composition root, so some coupling is expected. But `HarnessSession.run()` at 1343 lines is a god method that manages episode execution, approval suspension/resumption, receipt recording, telemetry collection, and evaluation — all in one class.

**`runtime/coding_coordinator.py` depends on `coding_plan.py` but `coding_plan.py` is a general-purpose plan model.** If a non-coding harness wants plans, it shouldn't need to import from a `coding_` prefixed module. The plan model should be in `domain/` or `agency/`.

### 2.3 Protocol / Design Issues

**The `EpisodeRunner` type alias is `Callable[[ModelRole, str, str, str], Any]`.** `[TODO]` type-safety (not first CLI). Four positional string arguments. The coordinator calls `self._run_episode(role, model, episode_id, brief)` — if the argument order changes, nothing catches it.

**The `CodingRunCoordinator` takes `planner: PlanFactory` as a callback but also calls `self._run(ModelRole.ARCHITECT, ...)` before calling the planner.** `[TODO]` the architect episode is discarded; the callback plan is used. Do not ship this as the first CLI.

**`coding_entrypoint.py` has `_fake_backend()` which is 100+ lines of test doubles in a production module.** It's imported at module level and selected by a string `kind` parameter. This is test infrastructure that should be in `test/`.

**`session_log.py` stray comment block:** `[DONE]` (fixed). `terminal_refusal` lives at the dataclass; the copy-paste from `root.py` is gone.

### 2.4 Missing Abstractions

**No harness can define its own execution strategy.** `[LATER]` v0.5. First CLI: the strategy **is** the episode loop. The coordinator DAG must not become the only workflow.

**The playbook system (§11) is designed but not implemented.** `[LATER]` `advisory` → `guided` → `strict`. Do not implement playbooks to ship the first CLI.

**No operator registry exists.** `[LATER]` competence graph / operator registry.

### 2.5 Performance / Workflow Issues

**Single effect per turn is a constraint, not a feature.** `[DONE]` keep it. Translator refuses `multi_action_proposal`. Do not loosen for the first CLI.

**No parallel execution.** `[LATER]`.

**No prompt caching.** `[LATER]`. Compiler prefix exists; provider cache integration does not.

**No streaming.** `[LATER]`. Request-response only.

### 2.6 Unused / Underused Capabilities

**`EpisodeEngine.spawn()` exists and works** `[DONE]` (S8-B-01 + ADR-0067). `[TODO]` coding pack does not expose it. `[LATER]` coordinator using spawn.

**Structured consolidation** `[DONE]` in `agency/context/compaction.py`. `[TODO]` coding coordinator does not use it — first CLI uses pack `context_policy` instead.

**`CompetencePriorRecorder`** `[DONE]` wired in `_LayeredOperator`. `[LATER]` no competence graph to consume priors.

---

## 3. Architecture Quality Verdict

### What's Genuinely Good

1. **The kernel dispatch sequence (S0–S12).** `kernel/dispatch.py` is 428 lines of meticulously ordered, well-documented code. Every step has a documented ordering rule backed by a real defect. The lease-before-emit, classifier-as-call, intent-before-effect properties are correctly implemented.

2. **The episode engine.** `agency/episode/engine.py` is 645 lines of clean loop logic. The spawn mechanism, no-progress detection, attenuation checks, and terminal state handling are well-designed.

3. **The manifest system.** Harnesses as JSON files with composed tools, prompts, policies, and evaluators is the right abstraction. Adding a new harness is a directory, not a code change.

4. **The layer topology.** `domain → ports → kernel → agency → runtime → adapters` with tool-enforced boundaries is proper hexagonal architecture.

5. **The ledger.** Everything is an event. Every surface is a projection. This is the right foundation for replay, audit, and measurement.

6. **The exterior evaluator.** The Evidence plane as a separate process with its own identity is the single most important architectural decision for a self-improving system.

### What's Problematic

1. **The `runtime/` package is a dumping ground.** It contains 30+ Python files mixing composition root concerns (`root.py`), application workflows (`coding_coordinator.py`, `repair.py`), domain models (`coding_plan.py`), infrastructure (`determinism.py`, `telemetry.py`), and test infrastructure (`coding_entrypoint.py`'s fake backends). There's no clear separation between "framework" and "application built on the framework."

2. **Three parallel implementations of the same concerns.** Model selection exists in `model_selection.py`, `tier_escalation.py`, and `coding_coordinator.py`. Verification exists in `coding_verification.py` and `lab_driver.py`. Escalation exists in `tier_escalation.py`, `coding_progress.py`, and `coding_coordinator.py`. This is the natural result of three developers (ALFA, BETA, GAMMA) building in parallel without a shared abstraction layer.

3. **The coding coordinator is framework capture.** The architecture doc warned: "A coding-first architecture risks permanent capture by coding's logic." The coding coordinator is exactly that — a coding-specific workflow hardcoded in the runtime package. A non-coding harness (like TableWorld) cannot use it. The architecture's Claim C-10 ("the same core serves a second, non-coding environment with no special cases") is threatened by this pattern.

4. **The DAG is hardcoded, not emergent.** You said DAGs should be "knowledge emergent from practice" — small proteins/polymers made of atoms organized into molecules. The current architecture has no mechanism for this. The coordinator's state machine is a fixed DAG. There's no way to discover, distill, and deploy new workflows from battle-tested processes.

---

## 4. Will It Grow Without Refactoring?

**The kernel, ports, domain, and agency layers will grow cleanly.** They have clear boundaries, frozen contracts, and minimal coupling.

**The runtime layer will require refactoring.** The current pattern of adding new `coding_*.py` files for each concern is unsustainable. At S34, the runtime package will have ~20 files all prefixed `coding_` — a sign that "coding" should be a harness, not a package.

**The specific refactoring needed (v0.5 `[LATER]`, not first CLI):**

1. **Extract the coordinator's state machine into a playbook interpreter.** `[LATER]`
2. **Move `coding_plan.py` to `domain/` or `agency/`.** `[LATER]`
3. **Consolidate the three model selection mechanisms.** `[LATER]`
4. **Consolidate the two verification mechanisms.** `[LATER]` — first CLI keeps `lab_driver` `_verify`.
5. **Move `_fake_backend()` out of production.** `[TODO]` after HarnessSession binder.
6. **Execution strategy as harness field.** `[LATER]` — first CLI is `agentic_loop` only.

---

## 5. Bottom Line

**The framework foundation (kernel, engine, ports, domain, manifests) is well-designed and will age well.** The code in `kernel/`, `agency/episode/`, `domain/`, and `ports/` is clean, well-documented, and correctly implements the architecture.

**The application layer built on top (runtime/coding_*) is accumulating technical debt.** The S28–S34 plan will produce working, tested code, but it will embed a static DAG workflow that contradicts the architecture's own design principles. This debt is manageable — the playbook system provides a clear migration path — but it should be addressed in v0.5 before more `coding_*.py` files are added.

**The architecture is well-designed to grow as a framework for building multiple harnesses.** The manifest system, port/adapters pattern, and frozen kernel are exactly right. The current problem is that the first harness built on the framework (coding) is leaking its assumptions into the framework layer. Fixing that is a matter of moving the coordinator's workflow logic into a playbook and making execution strategy a harness configuration — not a framework rewrite.