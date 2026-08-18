# Vanguard v0.4.5.0 Agentic Coding Harness — Full Development Guide

Status: implementation guide and acceptance contract  
Date: 2026-08-17  
Owning requirement: `REQ-TRUST-001`  
Tracking board: `docs/scrum/roadmap_backend.md`, S28–S34  
Product target: a Vanguard-native, headless agentic coding CLI capable of explaining repositories, planning work, implementing simple and multi-file tasks, testing, recovering, reviewing, and completing greenfield projects.

## 1. Executive verdict

Vanguard already has the trustworthy substrate of a coding agent:

- a real multi-turn `HarnessSession` rather than a fabricated runner;
- one effect per turn through the existing translator and `EpisodeEngine`;
- `fs.read`, `fs.search`, `patch.apply`, and sandboxed `proc.exec` effects;
- separate BENCHMARK and INTERACTIVE policy behavior;
- isolated per-run workspaces and ledger-derived JSONL receipts;
- real process exit status (`ok` for exit 0, failed/adapter error for non-zero);
- an exterior verifier that runs the task's declared command independently of the model;
- OpenRouter free, medium, and high model bands;
- preliminary repository-map and tier-routing components.

This is not yet evidence of an OpenCode-, Claude Code-, Codex-, Grok Build-, Hermes-, OpenClaw-, or Pi-shaped autonomous coding product. The missing proof is a live run that begins with an empty workspace, produces a structured plan, creates a coherent multi-file project, responds to failing tests, escalates and descends between model tiers, and reaches `oracle_green` under a hard cost ceiling.

The product claim is therefore:

> Vanguard has a credible coding-harness foundation. It becomes a proven autonomous coding CLI only after the S34 greenfield acceptance artifact exists.

## 2. Product outcomes

The completed CLI must support four increasing capability classes through the same runtime path.

### 2.1 Explain

Given a large existing repository, the agent can:

- discover repository instructions such as `AGENTS.md`;
- receive a bounded file and symbol map;
- inspect relevant files through Vanguard effects;
- explain architecture, dependency direction, important entrypoints, and risks;
- cite observed files and symbols rather than inventing structure.

### 2.2 Repair

Given a focused failing task, the agent can:

- read the relevant implementation and tests;
- make one bounded edit per turn;
- run focused checks;
- interpret real exit codes and test failures;
- iterate until the exterior verifier passes or a named stop condition fires.

### 2.3 Build

Given an empty directory and a product brief, the agent can:

- create a validated project plan;
- decompose the plan into dependency-ordered steps;
- create multiple coherent files across episodes;
- maintain task state without falsely marking work complete;
- start and behaviorally verify the resulting application.

### 2.4 Deliver complex work

Given a multi-module feature or greenfield system, the agent can:

- use a stronger architect or diagnostic model for difficult reasoning;
- delegate routine implementation turns to free or inexpensive executors;
- detect objective lack of progress;
- replan after repeated failures;
- return to cheaper execution after recovery;
- review the final diff against requirements;
- resume safely from the ledger after interruption;
- terminate only with a truthful result and complete evidence.

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

## 4. Target architecture

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

The coordinator is a finite-state workflow, not an alternative effect loop:

```text
DISCOVER -> PLAN -> EXECUTE -> VERIFY
                         ^       |
                         |       +-- passed step -> next step
                         |       +-- blocked -> DIAGNOSE -> REPLAN
                         |                            |
                         `---------- descend --------'

all steps verified -> REVIEW -> FINAL_VERIFY -> COMPLETE
                                      |
                                      `-- failed -> recover or named stop
```

## 5. Core domain and application types

Create `vanguard/packages/runtime/coding_coordinator.py` without moving effect semantics out of the existing engine.

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


@dataclass(slots=True)
class CodingRunState:
    phase: CodingPhase
    plan: CodingPlan | None
    active_step_id: str | None
    episode_count: int
    total_turns: int
    replans: int
    paid_calls: int
    current_model: str
    current_tier: str
    last_workspace_digest: str | None
    last_test_fingerprint: str | None
    consecutive_no_progress: int
    repeated_test_failures: int
    malformed_responses: int
    terminal_reason: str | None
```

## 6. Structured planning

Use a machine-validated plan rather than treating a Markdown checklist as authoritative.

```json
{
  "schema": "vg.coding-plan.v1",
  "goal": "Build a task-management web application",
  "assumptions": ["Python 3.10+", "No dependency downloads"],
  "steps": [
    {
      "id": "step-001",
      "title": "Create the HTTP API",
      "status": "pending",
      "dependsOn": [],
      "files": ["server.py"],
      "intent": "Serve static assets and task JSON endpoints",
      "acceptanceChecks": [
        ["python3", "-m", "unittest", "test.test_server"]
      ],
      "risk": "medium"
    }
  ],
  "finalChecks": [
    ["python3", "-m", "unittest", "discover", "-s", "test", "-t", "."]
  ]
}
```

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

If adding a new ledger event kind is outside the frozen contract, the architect writes exactly one `.vanguard/plan.json` through `patch.apply`. The coordinator parses it, validates it, records its digest, and derives later status from receipts. The mutable file is not trusted as the sole history.

## 7. Architect, executor, diagnostic, and reviewer roles

### Architect

Default: `deepseek/deepseek-v4-flash`.

Input:

- user brief;
- bounded repository map and symbols;
- discovered `AGENTS.md` constraints;
- available verbs and command allowlist;
- public acceptance contract;
- budget and plan schema;
- prior failures when replanning.

Output: one validated plan artifact. It does not implement several files or claim passing tests.

### Executor

Default: a healthy free tool-calling model. It receives one ready step, its allowed files, latest focused verification, and the relevant repository slice.

```text
Role: Executor
Current step: step-002, create the browser UI
Allowed files: static/index.html, static/app.js, static/style.css
Latest check: static/app.js is missing
Rule: propose exactly one effect; runtime decides verification
```

### Diagnostic

Default: DeepSeek V4 Flash after objective blocking signals. It receives compact evidence: plan, changed paths, relevant diffs, repeated test fingerprint, latest receipts, and remaining budget. It returns a diagnosis and plan revision, then execution descends to a cheaper model.

### Reviewer

The reviewer checks requirements, diff coverage, unresolved plan items, and suspicious shortcuts. It cannot override the exterior verifier. Start with a cheap capable model; use DeepSeek Flash only when the review is structurally complex.

## 8. Coordinator pseudocode

```python
def run_coding_task(config: CodingRunConfig) -> CodingRunResult:
    state = initialize_state(config)
    ledger = open_run_ledger(config.run_id)
    budget = BudgetController(config, ledger)
    index = build_repo_index(config.workspace)

    state.phase = CodingPhase.PLAN
    state.plan = run_architect_episode(
        config=config,
        state=state,
        index=index,
        budget=budget,
        ledger=ledger,
    )
    validate_plan(state.plan)

    while state.episode_count < config.max_episodes:
        if all_required_steps_verified(state.plan):
            break

        step = select_next_ready_step(state.plan)
        if step is None:
            return stop_from_ledger("plan_deadlock", state, ledger)

        state.phase = CodingPhase.EXECUTE
        model = route_model(ModelRole.EXECUTOR, state, budget)
        before = workspace_digest(config.workspace)

        episode = run_harness_episode(
            run_id=config.run_id,
            episode_id=next_episode_id(state),
            workspace=config.workspace,
            model=model,
            brief=executor_brief(state.plan, step),
            index=index,
        )

        after = workspace_digest(config.workspace)
        signals = analyze_episode(episode, before, after, state)
        update_progress_counters(state, signals)
        index.update(signals.changed_paths)

        state.phase = CodingPhase.VERIFY
        receipt = exterior_verify_step(config.workspace, step)
        apply_verification_result(state.plan, step, receipt)

        if receipt.passed:
            mark_verified(state.plan, step.id, receipt.digest)
            reset_progress_counters(state)
            descend_to_free_executor(state)
            continue

        decision = decide_escalation(state, signals, receipt, budget)

        if decision.action == "continue":
            continue
        if decision.action == "rotate_free":
            state.current_model = decision.model
            continue
        if decision.action == "replan":
            state.phase = CodingPhase.DIAGNOSE
            revision = run_diagnostic_episode(
                state=state,
                evidence=compact_failure_evidence(...),
                model=decision.model,
                budget=budget,
            )
            state.phase = CodingPhase.REPLAN
            state.plan = merge_validated_revision(state.plan, revision)
            state.replans += 1
            descend_to_free_executor(state)
            continue
        if decision.action == "stop":
            return stop_from_ledger(decision.reason, state, ledger)

    state.phase = CodingPhase.REVIEW
    review = run_review_episode(...)
    if review.requires_changes:
        merge_review_tasks(state.plan, review)
        # Return through the same execute/verify state machine within limits.

    state.phase = CodingPhase.FINAL_VERIFY
    final = exterior_final_oracle(config.workspace)
    if final.passed and all_required_steps_verified(state.plan):
        state.phase = CodingPhase.COMPLETE
        return project_result_from_ledger("oracle_green", state, ledger)

    return stop_from_ledger(
        classify_final_failure(state, final), state, ledger
    )
```

## 9. Repository discovery and large-codebase explanation

The real composition root must bind `IndexPort`; a test that manually supplies an index is insufficient proof.

```python
def build_index_for_workspace(workspace: Path) -> IndexPort:
    return RepositoryIndex.scan(
        workspace,
        exclude={
            ".git", ".vanguard/cache", ".venv", "node_modules",
            "__pycache__", "dist", "build",
        },
        max_files=2_000,
        max_file_bytes=256_000,
    )
```

Bind it in the driver:

```python
ports = SessionPorts(
    model=current_model,
    environment=environment,
    index=build_index_for_workspace(task_path),
    ...,
)
```

Refresh only changed paths after effects. For large repositories, inject a bounded high-level map and allow `fs.search`/`fs.read` to retrieve details. Never dump the entire codebase into the prompt.

An empty workspace is a valid observation:

```text
Workspace repository map:
- files: 0
- symbols: 0
- state: empty greenfield workspace
```

Explanation mode uses the same observation and effect path but grants no write verbs unless requested.

## 10. Objective progress detection

Escalation must be based on observable evidence, not model confidence.

```python
@dataclass(frozen=True, slots=True)
class ProgressSignals:
    real_tool_action: bool
    workspace_changed: bool
    changed_paths: tuple[str, ...]
    test_fingerprint: str | None
    test_improved: bool
    malformed_response: bool
    translator_refusal: str | None
    repeated_action_digest: bool
    repeated_patch_digest: bool
```

Workspace digest:

```python
digest = sha256(canonical_sequence(
    (relative_path, sha256(file_bytes))
    for each included workspace file
))
```

Test fingerprint:

```python
fingerprint = sha256(canonical_json({
    "argv": receipt.argv,
    "exitCode": receipt.exit_code,
    "failedTests": sorted(receipt.failed_test_ids),
    "errorKinds": sorted(receipt.error_kinds),
}))
```

A prose response, a real tool action, a changed workspace, a different failure, an improved test count, and a green test are distinct states. Do not collapse them into a single `completed` flag.

## 11. Escalation, provider rotation, and descent

Recommended model roles:

| Role | Default | Alternatives |
|---|---|---|
| Architect | `deepseek/deepseek-v4-flash` | `xiaomi/mimo-v2.5` |
| Free executor | healthy registered free tool model | rotate within free band |
| Diagnostic/replan | `deepseek/deepseek-v4-flash` | `xiaomi/mimo-v2.5` |
| Frontier recovery | explicit authorization only | `z-ai/glm-5.2`, `deepseek/deepseek-v4-pro`, `minimax/minimax-m3`, `openai/gpt-5.6-luna` |

Policy:

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

Malformed streaming often indicates provider behavior, not weak reasoning. Rotate free providers before buying stronger reasoning. Configuration facts such as a missing key, unknown price, absent workspace, or refused paid tier stop immediately; escalation must not conceal them.

After every successful diagnosis or replan, descend to a free executor. The expensive model supplies architectural information; it does not remain the default implementation model.

Do not silently catch router failures and reuse the original model. Emit a named routing failure with requested model, tier, and cause.

## 12. Provider health

```python
@dataclass(slots=True)
class ProviderHealth:
    successful_calls: int = 0
    malformed_calls: int = 0
    timeouts: int = 0
    tool_call_successes: int = 0
    consecutive_failures: int = 0
    cooldown_until: datetime | None = None
```

Select free executors using observed health, while preserving deterministic tie-breaking for replay and experiments. Do not permanently rank a model from a single run; campaign-level promotion belongs outside the live loop.

## 13. Budget controller

Use integer microdollars. Reserve worst-case cost before every paid call, then reconcile actual provider usage.

```python
def reserve_call(model, max_input_tokens, max_output_tokens):
    price = registry.require_known_price(model)
    reserve = (
        max_input_tokens * price.prompt_micros_per_token
        + max_output_tokens * price.completion_micros_per_token
    )
    if spent + reserved + reserve > hard_limit:
        raise BudgetExhausted()
    ledger.record_budget_reservation(model, reserve)


def reconcile_call(reservation, usage):
    if usage is None:
        ledger.record_usage_unattributed(reservation)
        return
    actual = calculate_integer_cost(reservation.model, usage)
    ledger.commit_budget(reservation, actual)
```

Rules:

- free model price resolves to exactly zero;
- unknown paid pricing is refused;
- absent usage is unknown, never silently zero;
- frontier models require explicit authorization;
- budget exhaustion is distinct from turn or attempt exhaustion;
- initial live campaign ceiling is `$0.05`; the wider authorized envelope is `$0.50` only after review.

## 14. Verification hierarchy

Three verification layers have different authority.

1. **Agent-requested test:** a normal sandboxed `proc.exec`; useful feedback, not final truth.
2. **Step verifier:** the coordinator runs the step's declared focused check outside the episode and may mark that step verified.
3. **Final exterior oracle:** runs the immutable final acceptance contract and is the only path to `oracle_green`.

The final greenfield web-app oracle should check behavior, not a gold source layout:

- the starting workspace was empty and isolated;
- multiple source, UI, test, and documentation files now exist;
- unit tests pass;
- the server starts on an assigned local port;
- `GET /` returns HTML;
- `GET /api/tasks` returns valid JSON;
- `POST /api/tasks` creates observable state;
- browser JavaScript calls the public API;
- no required plan step remains pending or blocked;
- no effect escaped the workspace;
- the original fixture remains unchanged.

## 15. Approvals and autonomy

Strict BENCHMARK cannot build software because it correctly denies `patch.apply` and privileged `proc.exec`. Greenfield building uses INTERACTIVE policy with a signed, bounded run grant:

```json
{
  "workspace": "/tmp/vg-run-123/project",
  "verbs": ["fs.read", "fs.search", "patch.apply", "proc.exec"],
  "commands": [
    ["python3", "-m", "unittest"],
    ["python3", "server.py"]
  ],
  "expiresAfterEpisodes": 12,
  "budgetUsdMicros": 50000
}
```

This is recorded as an autonomous lab departure. It is not a blanket approval, does not grant network access, and cannot widen itself.

## 16. Context management and resume

Prompt context has three layers:

```text
Frozen: policy, tool schema, one-effect rule
Stable: goal, validated plan, instructions, repository map
Rolling: active step, relevant files, recent diffs, latest failure and receipts
```

Compaction must retain the active step, unresolved approval, latest failing-test fingerprint, workspace digest, model route, and remaining budget.

Resume derives state from the ledger:

```python
def resume_run(run_id):
    state = reconstruct_coding_run(ledger.read(run_id))
    verify_workspace_identity(state.workspace_digest, workspace_digest(...))
    restore_plan(state.plan_digest)
    restore_budget(state.budget_state)
    restore_provider_health(state.provider_health)
    reverify_any_step_interrupted_before_receipt()
    continue_from(state.phase, state.active_step_id)
```

A file existing after a crash does not prove its step completed; the focused verifier runs again.

## 17. CLI product surface

The product entrypoint should be the shipped `vg` CLI, backed by the same Python runtime driver rather than a TypeScript agent loop.

```bash
vg code ./empty-app \
  --brief TASK.md \
  --planner deepseek/deepseek-v4-flash \
  --executor-band free \
  --recovery-model deepseek/deepseek-v4-flash \
  --max-turns 40 \
  --max-episodes 12 \
  --max-replans 2 \
  --budget-usd 0.05 \
  --interactive \
  --jsonl-out run.jsonl
```

Required surfaces:

```text
vg code PATH
vg code PATH --dry-plan
vg code PATH --headless --json
vg code PATH --resume RUN_ID
vg explain PATH --question "How does dispatch authorization work?"
vg trace RUN_ID
```

Human receipts:

```text
[plan] deepseek/deepseek-v4-flash: 6 validated steps
[step 1/6] Create HTTP API
[write] server.py +112
[test] test.test_server exit 1, 2 failures
[write] server.py +8/-3
[verified] step-001
[escalate] repeated test fingerprint x2
[diagnose] deepseek/deepseek-v4-flash
[resume] cohere/north-mini-code:free
[oracle] full acceptance exit 0
[complete] oracle_green, 27 turns, $0.0134
```

Headless JSON and JSONL contain no terminal escapes. JSONL remains the ledger export; UI receipts are projections.

## 18. Greenfield proof campaign

Start with a dependency-free Python and browser application so the first experiment measures agent behavior rather than package registry availability.

Public brief:

```text
Build a small task-management web application.
- Python standard-library HTTP backend.
- GET /api/tasks returns JSON.
- POST /api/tasks adds a task.
- Browser interface lists and creates tasks.
- Include unit tests and README instructions.
- Use no external dependencies.
```

Arms:

| Arm | Planner | Executor | Recovery |
|---|---|---|---|
| Control | free | same free model | none |
| Planned | DeepSeek Flash | free | none |
| Adaptive | DeepSeek Flash | rotating free pool | DeepSeek Flash |
| Cheap | DeepSeek Flash | cheap model | DeepSeek Flash |

Run three fixed trials per initial arm under an aggregate `$0.05` ceiling. Expand toward 10–20 trials only after reviewing correctness, provider health, and cost.

Primary metric: `oracle_green` rate. Secondary metrics include cost per green, turns per green, time to first valid file, time to first passing focused test, replans, provider failures, translator refusals, repeated failure fingerprints, and workspace escapes.

## 19. Test plan

Coordinator:

- planner precedes executor;
- executor receives exactly one ready step;
- dependencies determine readiness;
- model claims cannot verify steps;
- exterior pass verifies a step;
- resume reconstructs active work;
- final completion requires plan completion and final oracle.

Escalation:

- one failure does not escalate;
- repeated fingerprint escalates;
- repeated action without workspace delta escalates;
- malformed output rotates free providers first;
- diagnostic success descends to free execution;
- missing key and unknown pricing stop without climbing;
- budget exhaustion remains distinct;
- frontier routing requires explicit authorization.

Trust and security:

- model-requested tests cannot set `oracle_green`;
- the model cannot modify the oracle command;
- multi-action proposals remain refused;
- path escape fails closed;
- every paid call has a prior reservation;
- every route and approval is attributable;
- source fixtures remain unchanged;
- no host subprocess path bypasses the sandbox.

Greenfield:

- empty repository map is explicit;
- first write lands only in the isolated workspace;
- files persist across episodes in one run;
- tests demonstrate real red-to-green behavior;
- HTTP behavior passes final verification;
- no required plan items remain unresolved.

## 20. Implementation sequence

### S28 — Finish honest routing and composition

- expose the router through the real CLI;
- remove silent model fallback;
- bind and refresh the repo index in the actual driver;
- consolidate tier policy into one implementation;
- record route identity and reason;
- add outcome-driven routing tests.

### S29 — Structured plan and task state

- implement `vg.coding-plan.v1`;
- validate IDs, DAG, paths, commands, and checks;
- add architect and revision prompts;
- make verification status runtime-owned;
- persist plan and revision digests.

### S30 — Coding coordinator

- add the finite-state coordinator;
- reuse `HarnessSession` for every episode;
- preserve one workspace and run ID across distinct episode IDs;
- support explain, repair, and greenfield modes through the same path;
- reconstruct state from the ledger.

### S31 — Progress, escalation, and descent

- workspace, action, patch, and test fingerprints;
- free-provider health and rotation;
- deterministic escalation triggers;
- DeepSeek diagnostic/replan path;
- post-recovery descent to free execution;
- explicit frontier authorization.

### S32 — Budget, verification, and autonomy

- pre-call budget reservation and post-call reconciliation;
- focused step verification and sealed final oracle;
- signed bounded autonomous run grants;
- honest stop taxonomy and cost/session projection.

### S33 — Product CLI and receipts

- `vg code`, `--dry-plan`, `--resume`, and `vg explain`;
- real-time receipts plus clean JSON/headless output;
- one backend path from TypeScript CLI to Python runtime;
- crash recovery and context compaction.

### S34 — Greenfield proof

- sealed empty-workspace web-app challenge;
- control, planned, adaptive, and cheap arms;
- initial `$0.05` campaign review before expansion;
- archived ledger, plan, routes, diffs, tests, oracle, tokens, and costs;
- no competitor-grade claim before at least one adaptive `oracle_green`.

## 21. Definition of done

The v0.4.5.0 autonomous coding harness is complete only when an archived run proves:

- it started from an empty isolated workspace;
- DeepSeek V4 Flash produced a valid structured plan;
- free models executed multiple plan steps;
- Vanguard effects created a coherent multi-file application;
- focused tests produced real failing and passing exit codes;
- repeated objective failure triggered paid recovery;
- recovery revised the diagnosis or plan;
- execution descended back to a free model;
- runtime verification, not model assertion, completed every required step;
- final behavioral oracle passed;
- JSONL attributes proposals, effects, receipts, routes, approvals, and cost;
- the configured spending limit was never exceeded;
- the original fixture remained unchanged;
- the terminal result was `oracle_green`.

Presence of a tier flag, a completed episode, a generated file tree, or a model-written “done” message is not sufficient evidence.

## 22. Required validation commands

```bash
python3 -m unittest discover -s test/runtime -t .
python3 tools/run_active_contract_tests.py
python3 tools/check_boundaries.py
python3 tools/check_tcb_budget.py
python3 tools/scan_secrets.py
npm test
npm run typecheck
```

Live runs must archive their exact CLI invocation, model identifiers, immutable task manifest, ledger JSONL, projected coding session, workspace diff, exterior verification receipt, provider usage, and integer-microdollar cost.
