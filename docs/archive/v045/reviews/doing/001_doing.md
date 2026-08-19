# Vanguard v0.4.5.0 Agentic Coding Harness — Full Development Guide (Pending Work)

Status: implementation guide and acceptance contract  
Date: 2026-08-17  
Owning requirement: `REQ-TRUST-001`  
Tracking board: `docs/scrum/roadmap_backend.md`, S28–S34  
Product target: a Vanguard-native, headless agentic coding CLI capable of explaining repositories, planning work, implementing simple and multi-file tasks, testing, recovering, reviewing, and completing greenfield projects.

**First CLI `[TODO]` (operator path):** `--in-place`; CLI grant (`AutonomousGrant` in `runtime/autonomous_grant.py`); live `patch.apply`; bind `format_skill_index` into the compiler; honest `lab_driver` exit codes; wire `coding_progress` fingerprints as stop signals.

---

## 1. Executive Verdict & Pending Gap

`[TODO]` operator in-place writes + live one verb. `[LATER]` S34 `oracle_green` campaign.

The missing proof is a live run that begins with an empty workspace, produces a structured plan, creates a coherent multi-file project, responds to failing tests, escalates and descends between model tiers, and reaches `oracle_green` under a hard cost ceiling.

The product claim is therefore:

> Vanguard has a credible coding-harness foundation. It becomes a proven autonomous coding CLI only after the S34 greenfield acceptance artifact exists.

---

## 2. Product Outcomes (Pending Capability Classes)

### 2.1 Explain — `[TODO]` real `lab_driver` / binder

Given a large existing repository, the agent can:
- inspect relevant files through Vanguard effects;
- explain architecture, dependency direction, important entrypoints, and risks;
- cite observed files and symbols rather than inventing structure.

### 2.2 Repair — `[TODO]` live Q2 + writes landing on a real checkout

Given a focused failing task, the agent can:
- read the relevant implementation and tests;
- make one bounded edit per turn;
- run focused checks;
- interpret real exit codes and test failures;
- iterate until the exterior verifier passes or a named stop condition fires.

### 2.3 Build — `[TODO]` live multi-file; `[LATER]` coordinator plan DAG as the product

Given an empty directory and a product brief, the agent can:
- create a validated project plan;
- decompose the plan into dependency-ordered steps;
- create multiple coherent files across episodes;
- maintain task state without falsely marking work complete;
- start and behaviorally verify the resulting application.

### 2.4 Deliver complex work — `[LATER]` (not first CLI)

Given a multi-module feature or greenfield system, the agent can:
- use a stronger architect or diagnostic model for difficult reasoning;
- delegate routine implementation turns to free or inexpensive executors;
- detect objective lack of progress;
- replan after repeated failures;
- return to cheaper execution after recovery;
- review the final diff against requirements;
- resume safely from the ledger after interruption;
- terminate only with a truthful result and complete evidence.

---

## 3. Non-negotiable design constraints

1. `HarnessSession` and `EpisodeEngine` remain the only model-to-effect execution path.
2. The coordinator may schedule episodes but may never dispatch model-requested effects itself.
3. One proposal contains at most one effect. `multi_action_proposal` remains a refusal.
4. A model cannot mark a task verified or declare `oracle_green`.
5. The final oracle is exterior, predeclared, and not selected by the model.
6. Every attempt has a distinct `episode_id`; the full coding job has one stable `run_id`.
7. Every model route, approval, paid reservation, proposal, effect, receipt, and terminal reason is attributable.
8. Unknown pricing, missing provider identity, missing usage, and unavailable verification fail closed.
9. BENCHMARK continues to deny privileged writes. Autonomous building uses a narrow, signed, labelled INTERACTIVE run grant.
10. No second agent loop, model-as-judge success path, silent tool-batch splitting, hidden host execution, or parallel session database is introduced.

---

## 4. Target Architecture & Coordinator Binder

`[LATER]` as the product DAG. **First CLI:** `lab_driver` → `HarnessSession` → `EpisodeEngine` is the path.

```text
vg code <workspace> <brief/options>
        |
        v
CodingRunCoordinator                 application workflow only
  |-- RunManifest                    immutable configuration and identities
  |-- BudgetController               reserve before paid call; reconcile after
  |-- RepositoryMapService           bounded file/symbol observation
  |-- CodingPlanStore                validated plan plus ledger-derived status
  |-- ProgressAnalyzer               workspace/test/action fingerprints
  |-- ModelRoutingPolicy             role, health, tier, escalation, descent
  `-- ExteriorVerifier               focused and final declared checks
        |
        v
HarnessSession                       canonical episode path
        |
        v
ModelPort -> Translator -> Kernel -> EnvironmentPort -> Sandbox
        |                                             |
        `---------------- ledger receipts <-----------'
```

---

## 5. Core Domain and Application Types — `[TODO]` binder

Create `HarnessSession` binder in `vanguard/packages/runtime/coding_coordinator.py`.

```python
class CodingPhase(Enum):
    DISCOVER = "discover"
    PLAN = "plan"
    EXECUTE = "execute"
    VERIFY = "verify"
    DIAGNOSE = "diagnose"
    REPLAN = "replan"
    REVIEW = "review"
    FINAL_VERIFY = "final_verify"
    COMPLETE = "complete"
    FAILED = "failed"


class ModelRole(Enum):
    ARCHITECT = "architect"
    EXECUTOR = "executor"
    DIAGNOSTIC = "diagnostic"
    REVIEWER = "reviewer"


@dataclass(frozen=True, slots=True)
class CodingRunConfig:
    run_id: str
    workspace: Path
    brief: str
    planner_model: str
    executor_models: tuple[str, ...]
    recovery_models: tuple[str, ...]
    reviewer_model: str | None
    max_turns_per_episode: int
    max_episodes: int
    max_replans: int
    max_paid_calls: int
    budget_usd_micros: int
    no_progress_limit: int = 3
    repeated_failure_limit: int = 2
    malformed_response_limit: int = 2
```

---

## 6. Structured Planning — `[TODO]` live architect episode; `[LATER]` as the live product brain

Validation invariants:

```python
def validate_plan(plan: CodingPlan) -> None:
    require(plan.schema == "vg.coding-plan.v1")
    require(1 <= len(plan.steps) <= MAX_PLAN_STEPS)
    require(unique(step.id for step in plan.steps))
    require(dependency_graph_is_acyclic(plan.steps))
    require(all_paths_are_workspace_relative(plan))
    require(all_commands_are_allowlisted(plan))
    require(all(step.acceptance_checks for step in plan.steps))
    require(bool(plan.final_checks))
```

Step states are runtime-owned:

```text
pending -> ready -> in_progress -> implemented -> verified
                                |               |
                                +-> blocked     +-> invalidated
```

The model may claim `implemented`; only an exterior check may produce `verified`. A replan may supersede a step but must retain its history and digest.

---

## 7. Architect, Executor, Diagnostic, and Reviewer Roles — `[LATER]` live roles

- **Architect**: Default: `deepseek/deepseek-v4-flash`. Output: one validated plan artifact.
- **Executor**: Default: healthy free tool-calling model. Receives one ready step and allowed files.
- **Diagnostic**: Default: `deepseek/deepseek-v4-flash` after objective blocking signals.
- **Reviewer**: Checks requirements, diff coverage, unresolved plan items.

---

## 8. Coordinator Engine — `[TODO]` HarnessSession binder

```python
def run_coding_task(config: CodingRunConfig) -> CodingRunResult:
    # Requires binding HarnessSession to the episode loop
    ...
```

---

## 9. Repository Discovery & Map — `[TODO]` explicit empty-workspace map text & refresh

```python
# [TODO] Refresh only changed paths after effects.
# [TODO] Explicit empty workspace observation:
# Workspace repository map:
# - files: 0
# - symbols: 0
# - state: empty greenfield workspace
```

---

## 10. Objective Progress Detection — `[TODO]` wire fingerprints into `lab_driver` stop

Wire `test_fingerprint` and `workspace_digest` from `coding_progress.py` directly into `lab_driver` termination triggers.

---

## 11. Escalation, Provider Rotation, and Descent — `[TODO]` on `lab_driver`; `[LATER]` paid DeepSeek until spend + live verb

```python
def decide_escalation(state, signals, verification, budget):
    if verification.passed:
        return DescendToFree()

    if state.malformed_responses == 1:
        return RetrySameModel()
    if state.malformed_responses >= 2:
        return RotateFreeProvider()

    if state.repeated_test_failures >= 2:
        return ReplanWith("deepseek/deepseek-v4-flash")
    if state.consecutive_no_progress >= 3:
        return ReplanWith("deepseek/deepseek-v4-flash")
    if signals.repeated_patch_digest:
        return ReplanWith("deepseek/deepseek-v4-flash")
    if signals.repeated_action_digest and not signals.workspace_changed:
        return ReplanWith("deepseek/deepseek-v4-flash")

    if state.replans >= config.max_replans:
        return Stop("no_progress")
    return Continue()
```

---

## 12. Provider Health — `[TODO]` bind into live execution

Bind `ProviderHealth` tracking into free executor rotation.

---

## 13. Budget Controller — `[TODO]` bind on paid `lab_driver` calls; `[LATER]` paid spend until `S9-J-03`

Enforce integer microdollar reservations and post-call reconciliations before paid model invocations.

---

## 14. Verification Hierarchy — `[TODO]` live `oracle_green`

1. **Agent-requested test:** normal sandboxed `proc.exec`; useful feedback, not final truth.
2. **Step verifier:** coordinator runs step's declared check outside the episode.
3. **Final exterior oracle:** runs immutable final acceptance contract to produce `oracle_green`.

---

## 15. Approvals & Autonomy — `[TODO]` expose on `lab_driver` CLI

Expose signed `AutonomousGrant` on `lab_driver` CLI (prefer this over naked `--approve-writes`).

---

## 16. Context Management & Resume — `[TODO]` `lab_driver --resume RUN_ID` from ledger

Implement `lab_driver --resume RUN_ID` reconstructing run state directly from event ledger.

---

## 17. CLI Product Surface — `[TODO]` first CLI = `lab_driver` in-place + grant + honest exit codes; `[LATER]` TUI receipts

- Support `--in-place` WSL writes.
- Honest `lab_driver` exit codes (exit 0 only on genuine `oracle_green`).
- Clean JSON/JSONL output.

---

## 18. Greenfield Proof Campaign — `[TODO]` live; `[LATER]` claim until adaptive `oracle_green`

Execute live greenfield task under `$0.05` ceiling across control, planned, and adaptive arms.

---

## 19. Test Plan — `[TODO]` live `HarnessSession` campaign

Verify planner-executor sequence, step verification independence, escalation triggers, and path confinement during live harness sessions.

---

## 20. Implementation Sequence (Pending Rows Only)

### S28 — Finish Honest Routing and Composition `[TODO]`
- Expose the router through the real CLI. `[TODO]`
- Remove silent model fallback. `[TODO]`
- Refresh repo index on changed paths in driver. `[TODO]`
- Consolidate tier policy into one implementation. `[LATER]`
- Record route identity and reason. `[TODO]`
- Add outcome-driven routing tests. `[TODO]`

### S29 — Structured Plan and Task State `[TODO]`
- Add architect and revision prompts. `[TODO]`
- Persist plan and revision digests. `[TODO]`
- Live architect episode execution. `[TODO]`

### S30 — Coding Coordinator `[TODO]`
- Reuse `HarnessSession` for every episode (binder for `--live`). `[TODO]`
- Explain mode execution path. `[TODO]`
- Reconstruct state from ledger on resume. `[TODO]`

### S31 — Progress, Escalation, and Descent `[TODO]`
- Wire progress fingerprints into `lab_driver` stop conditions. `[TODO]`

### S32 — Budget, Verification, and Autonomy `[TODO]`
- Expose CLI `AutonomousGrant` on `lab_driver`. `[TODO]`

### S33 — Product CLI and Receipts `[TODO]`
- In-place WSL writes + labelled grant + honest exit codes. `[TODO]`

### S34 — Greenfield Proof `[TODO]`
- Run live sealed empty-workspace web-app challenge to `oracle_green`. `[TODO]`

---

## 21. Definition of Done (`[TODO]` S34 & First CLI Bar)

The v0.4.5.0 autonomous coding harness is complete only when an archived run proves:
- started from an empty isolated workspace;
- produced a valid structured plan;
- Vanguard effects created a coherent multi-file application;
- focused tests produced real failing and passing exit codes;
- repeated objective failure triggered paid recovery;
- execution descended back to a free model;
- runtime verification completed every required step;
- final behavioral oracle passed (`oracle_green`);
- JSONL attributes proposals, effects, receipts, routes, approvals, and cost;
- configured spending limit was never exceeded.
