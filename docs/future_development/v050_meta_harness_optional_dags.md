# Vanguard Code Quality & Architecture Deep-Dive Evaluation

After reading the architecture docs, the full S28–S34 development guide, the roadmap, and the actual code in `vanguard/packages/`, here is a comprehensive evaluation.

---

## 1. After S28–S34: Will We Have Well-Designed Code?

**No — the S28–S34 plan will produce well-tested but architecturally compromised code.** The plan is internally consistent and the tests will pass, but it doubles down on the architectural contradiction I identified earlier. Here's why:

### The Contradiction Is Being Codified, Not Resolved

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

### 2.1 Dead / Redundant Code

| File | Issue |
|---|---|
| `runtime/repair.py` | `drive_until_green` is a simpler repair loop. `coding_coordinator.py` implements a more complex one. Both exist. Which one is authoritative? |
| `runtime/tier_escalation.py` | `TierLadder`, `TierAttempt`, `EscalationOutcome`, `run_with_escalation` — a complete tier-escalation system. `coding_coordinator.py` has its own `_route()` method. `coding_progress.py` has `ProgressAnalyzer.decide_escalation()`. **Three escalation mechanisms exist.** |
| `runtime/model_selection.py` | `select_model()` with `_probe_http()`, `_ollama_tags()`, `_resolve_tag()`, `_free_band()`. `tier_escalation.py` has `RoleAwareRouter.choose()`. `coding_coordinator.py` has `_route()`. **Three model selection mechanisms.** |
| `runtime/lab_driver.py` | Has its own `_verify()`, `_verdict_is_green()`, `_environment_for()`. `coding_verification.py` has `StepVerifier` and `FinalVerifier`. **Two verification paths.** |
| `runtime/coding_entrypoint.py` | Has `_fake_backend()` with `greenfield_adaptive`, `budget_exhausted`, `unavailable`, `non_green` — fake backends for CLI testing. Also has `_scripted_adaptive_plan()` and `_coordinator_dry_plan()`. This is test infrastructure living in production code. |

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

**The `EpisodeRunner` type alias is `Callable[[ModelRole, str, str, str], Any]`.** Four positional string arguments with no type safety. The coordinator calls `self._run_episode(role, model, episode_id, brief)` — if the argument order changes, nothing catches it.

**`CodingRunCoordinator` takes `planner: PlanFactory` as a callback but also calls `self._run(ModelRole.ARCHITECT, ...)` before calling the planner.** The architect episode runs, then the planner callback is called on the same brief. This means the model is invoked twice for planning — once through the episode engine and once through the callback. The callback's result (`self._planner(self.config.brief)`) is what's actually used. The architect episode's output is discarded.

**`coding_entrypoint.py` has `_fake_backend()` which is 100+ lines of test doubles in a production module.** It's imported at module level and selected by a string `kind` parameter. This is test infrastructure that should be in `test/`.

**`session_log.py` has a stray comment block at line 58-59:**
```python
│that differs between domains is a file. So the manifest supplies the system
│    def flush() -> None:
```
This appears to be a copy-paste artifact from `root.py`'s docstring that got embedded in the middle of `session_log.py`.

### 2.4 Missing Abstractions

**No harness can define its own execution strategy.** The `CodingRunCoordinator` hardcodes `DISCOVER → PLAN → EXECUTE → VERIFY → DIAGNOSE → REPLAN → REVIEW → FINAL_VERIFY`. A harness manifest has no field for "execution strategy" or "workflow type."

**The playbook system (§11) is designed but not implemented.** The architecture doc describes `advisory`, `guided`, and `strict` rigidity levels with tool masking, context injection, and gate evaluation. None of this exists in code. The coordinator implements a single hardcoded workflow that roughly corresponds to `strict` mode.

**No operator registry exists.** The architecture says operators are "versioned, addressable, content-hashed entries in the competence graph." The code has no competence graph, no operator registry, and no mechanism for the system to improve its own operators.

### 2.5 Performance / Workflow Issues

**Single effect per turn is a constraint, not a feature.** The translator refuses `multi_action_proposal`. This is documented and intentional, but it means the agent cannot read a file and edit it in the same turn. Claude Code and Cline can. This is a significant latency penalty for multi-step tasks.

**No parallel execution.** The architecture doc §8 describes structured concurrency with independence groups, but the code has no implementation. `EpisodeEngine` is strictly sequential.

**No prompt caching.** The architecture doc §10.2 describes cache boundaries and prefix stability as "the largest single cost lever." The context compiler (`agency/context/compiler.py`) exists but there's no evidence of actual prompt caching integration with providers.

**No streaming.** The model adapter interface is request-response. There's no mechanism for streaming tool calls or real-time output to the user.

### 2.6 Unused / Underused Capabilities

**`EpisodeEngine.spawn()` exists and works** (with the S8-B-01 fix for attenuated children). But the coding coordinator never uses it. Sub-agent delegation is designed, implemented, tested, and unreachable from any harness.

**Structured consolidation** (`agency/context/compaction.py` with `StructuredRecord` and `deadEnds`) is implemented. The coding coordinator doesn't use it — it has its own simpler compaction via `context_policy`.

**`CompetencePriorRecorder`** exists in `agency/context/` and is wired in `_LayeredOperator`. But there's no competence graph to record into, so priors are recorded but never used for operator selection.

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

**The specific refactoring needed (v0.5 or v0.6):**

1. **Extract the coordinator's state machine into a playbook interpreter.** The playbook system (§11) already has the right abstraction. The coordinator should read a playbook that says "at rigidity `guided`, enforce phases in order but let the agent loop freely within each phase." The current hardcoded phases become a `strict` playbook.

2. **Move `coding_plan.py` to `domain/` or `agency/`.** Plans are a general concept, not coding-specific. A TableWorld task also needs a plan.

3. **Consolidate the three model selection mechanisms** into one `ModelRouter` that serves both the lab driver and the coordinator.

4. **Consolidate the two verification mechanisms** into one `ExteriorVerifier` that serves both focused step checks and final oracle checks.

5. **Move test infrastructure out of production code.** `coding_entrypoint.py`'s `_fake_backend()` belongs in `test/`.

6. **Make execution strategy a harness configuration field.** A harness manifest should be able to declare `"execution_strategy": "agentic_loop"` vs `"execution_strategy": "plan_guided"` vs `"execution_strategy": "playbook_strict"`.

---

## 5. Bottom Line

**The framework foundation (kernel, engine, ports, domain, manifests) is well-designed and will age well.** The code in `kernel/`, `agency/episode/`, `domain/`, and `ports/` is clean, well-documented, and correctly implements the architecture.

**The application layer built on top (runtime/coding_*) is accumulating technical debt.** The S28–S34 plan will produce working, tested code, but it will embed a static DAG workflow that contradicts the architecture's own design principles. This debt is manageable — the playbook system provides a clear migration path — but it should be addressed in v0.5 before more `coding_*.py` files are added.

**The architecture is well-designed to grow as a framework for building multiple harnesses.** The manifest system, port/adapters pattern, and frozen kernel are exactly right. The current problem is that the first harness built on the framework (coding) is leaking its assumptions into the framework layer. Fixing that is a matter of moving the coordinator's workflow logic into a playbook and making execution strategy a harness configuration — not a framework rewrite.