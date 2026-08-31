# Vanguard SOTA Coding Harness Review and Implementation Plan
## Executive verdict
Vanguard has a strong high-assurance agent-framework substrate, but it is not yet a proven SOTA autonomous coding harness.
The current system contains serious foundations: a compact trusted kernel, mediated effects, capability attenuation, typed budgets, event-backed state, model adapters, repository-index contracts, context layers, recovery concepts, benchmark falsifiers, and LAM replay infrastructure.
The missing proof is end-to-end integration.
The system does not yet demonstrate reliable success on large-context, long-plan, multi-file, difficult software-engineering tasks.
The honest current label is:
> Promising high-assurance agent framework with an incomplete Coding Max vertical slice.
The system should not yet be marketed as:
> A SOTA autonomous coding agent.
## Scope of this report
- Backend and runtime only.
- CLI-facing backend contracts.
- Coding Max architecture.
- Wave 1 and Wave 2 acceptance.
- LAM and benchmark reproducibility.
- OpenRouter free-model observations.
- Large-context and multifile capability requirements.
- No frontend implementation.
- No production-code changes as part of this review.
## Evidence reviewed
- `.draft/CODING_MAX_WAVE_1_IMPLEMENTATION_PROMPT.md`.
- `.draft/CODING_MAX_WAVE_2_IMPLEMENTATION_PROMPT.md`.
- `.agents/skills/lda-navigator/SKILL.md`.
- `docs/execution/active.md`.
- `docs/execution/milestones.md`.
- `docs/execution/backlog.md`.
- `test/falsifiers/test_wave_1_audit_falsifiers.py`.
- `benchmarks/m8_heldout/runner.py`.
- `benchmarks/gemini_multifile_benchmark/runner.py`.
- `vanguard/packages/runtime/task_state.py`.
- `vanguard/packages/runtime/session.py`.
- `vanguard/packages/runtime/app_service.py`.
- `packs/code-default/load.py`.
- LAM store, server, replay, and benchmark tooling.
## Repository intelligence status
LDA health check passed.
```text
index_healthy: true
documents: 377
entities: 18125
files: 2762
relations: 16531
symbols: 15084
```
The generated indexes contain revision drift relative to some execution documents.
The indexes are therefore routing aids, not authority.
The execution board, current source, tests, and receipts remain authoritative.
## Current execution status
The current execution board reports:
- `implementation_status: UNRESOLVED`.
- `FIN-A1: BLOCKED`.
- `REL-01/H0: IN_PROGRESS`.
- M-8: blocked.
- M-9: unauthorized.
- M-10: unauthorized.
- Coding Max expansion: staged behind evidence-integrity work.
The board explicitly states that passing focused tests demonstrates mechanism presence only.
The board explicitly rejects SOTA, release, and SWE-bench claims without reproducible evidence.
## What has been achieved
### Trusted execution
The kernel provides:
- Typed effects.
- Capability grants.
- Monotonic attenuation.
- Budget enforcement.
- Fail-closed policy.
- Provenance support.
- Domain blindness.
- A small trusted computing base.
The TCB check reported:
```text
1386 logical lines
1438 logical-line threshold
52 logical lines remaining
```
This is a strong security and maintainability property.
It does not prove coding-task quality.
### Architecture boundaries
The boundary checker reported:
```text
BOUNDARY PASS: 637 source files checked
```
The intended dependency direction remains:
```text
domain ← ports ← kernel ← agency ← runtime → adapters
```
This makes it possible to improve coding policy without expanding the trusted kernel.
### Durable coding state
`CodingTaskState` represents:
- Objective.
- Constraints.
- Plan.
- Strategy steps.
- Hypotheses.
- Inspected files.
- Modified files.
- Verification plan.
- Latest verification.
- Failure class.
- Next action.
- Settled effects.
- Remaining budgets.
- Task class.
- Completion requirements.
- Discoveries.
- Dead ends.
- Implicated files.
- Change surface.
- TODO items.
- Route decisions.
The state supports canonical serialization and deterministic digests.
TODO completion can require a receipt digest.
Verification TODOs can require a fresh verification receipt.
The model is a good projection seam.
The problem is that production resume does not yet reconstruct and use it correctly.
### Repository intelligence
`IndexPort` now includes concepts for:
- Files.
- Symbols.
- Dependencies.
- Test associations.
- Repository maps.
The adapter includes bounded observations, deterministic results, provenance, and path containment.
These are the correct ingredients for large-repository work.
The pack-level repository map still duplicates indexing logic and should be removed from the policy layer.
### Preset overlays
Pack-local data-defined overlays exist for:
- `fast`.
- `balanced`.
- `max`.
The loader validates schema, budget values, and plugin slots.
The overlays compile through the same composition path.
The production manifest registry does not yet prove that all three stable Coding Max identities are available end to end.
### Benchmark integrity
The M-8 runner contains typed dispositions such as:
- `NOT_RUN`.
- `INVALID_TASK`.
- `PROVIDER_UNAVAILABLE`.
- `BUDGET_EXHAUSTED`.
- `TIMED_OUT`.
- `MODEL_PROTOCOL_ERROR`.
- `NO_PATCH`.
- `PATCH_REJECTED`.
- `EVALUATOR_UNAVAILABLE`.
- `EVALUATOR_FAILED`.
- `PASSED`.
Focused tests verify that prose alone cannot count as a patch or pass.
Focused tests verify that zero tests cannot count as successful verification.
Focused tests verify budget refusal, tamper detection, malformed-task rejection, and single-attempt behavior.
This is a substantial improvement over synthetic success metrics.
### LAM
The repository LAM corpus contained:
```text
256 scenarios
658 traces
9 episodes
667 mock calls
```
LAM supports OpenAI-compatible replay, Ollama-compatible replay, exact cassette playback, SQLite metadata, model traces, mock calls, and evidence labels.
LAM is useful for deterministic parser, routing, and trajectory regression.
LAM replay is not a substitute for fresh external evaluation.
## Validation evidence
The reviewed test groups covered 754 tests:
```text
Wave 1, benchmark, and LAM focused tests: 30
Pack tests: 69
Agency tests: 128
Contract tests: 430
Kernel tests: 97
Total: 754
```
Final disposition after local socket tests were rerun with permission:
```text
754 passed
0 functional failures
6 skips in the contract suite
```
Architecture checks:
```text
Boundary checker: PASS
TCB checker: PASS
TCB usage: 1386 / 1438 logical lines
```
Framework-only no-op benchmark:
```text
repeats: 20
minimum: 36.688 ms
median: 37.025 ms
p95: 187.373 ms
maximum: 187.373 ms
```
The benchmark uses a fake model.
It measures runtime overhead, not coding quality.
It excludes provider latency, repository exploration, patch synthesis, and test execution.
## OpenRouter free-model observations
Three bounded calls were made.
Total cost was `$0.00`.
The calls remained below the requested 50-call and `$0.10` limits.
### Automatic free route
Challenge:
```text
Distributed Sharded Consistent Hash Ring with Dynamic Rebalancing
```
Model:
```text
openrouter/free
```
Result:
```text
HTTP status: successful model response
Oracle result: failed
Prompt tokens: 829
Completion tokens: 1000
Total tokens: 1829
Cost: $0.00
Wall time: 12.596 seconds
```
### Cohere North Mini Code
Challenge:
```text
Distributed Sharded Consistent Hash Ring with Dynamic Rebalancing
```
Model:
```text
cohere/north-mini-code:free
```
Result:
```text
HTTP status: successful model response
Oracle result: failed
Prompt tokens: 802
Completion tokens: 1000
Total tokens: 1802
Cost: $0.00
Wall time: 13.914 seconds
```
### GPT OSS free route
Challenge:
```text
Distributed Two-Phase Commit Coordinator with Crash-Safe WAL Replay
```
Model:
```text
openai/gpt-oss-20b:free
```
Result:
```text
HTTP status: 404 Not Found
Oracle result: not executed
Prompt tokens: 0
Completion tokens: 0
Cost: $0.00
Wall time: 0.074 seconds
```
The model catalog must be treated as dynamic.
A configured model name must not be assumed available.
### Interpretation
The executed calls produced:
```text
Executed successful provider calls: 2
Oracle passes: 0
Unavailable model routes: 1
```
The sample is too small to rank models.
It is sufficient to reject the claim that hard multifile coding capability is already demonstrated.
Both successful responses reached the 1000-token completion ceiling.
This may indicate insufficient output budget, inefficient whole-file output, weak reasoning, parser loss, or incomplete implementation.
The current runner does not retain enough evidence to distinguish these causes.
## Major defects
### P0: completion admission is not wired
The audit falsifier confirms that `HarnessSession` does not pass `completion_admitter=` into `EpisodeEngine`.
The policy exists.
The production execution path does not consistently enforce it.
Consequences:
- A model may finish without a fresh verification receipt.
- A stale receipt may be accepted if the path is not connected.
- Post-modification verification freshness may not be enforced.
- Model prose can remain too close to the completion authority boundary.
Fix:
```python
def build_episode_engine(session, task):
    admitter = CompletionAdmitter(
        verification_store=session.verification_store,
        artifact_store=session.artifact_store,
        clock=session.clock,
    )
    return EpisodeEngine(
        model=session.model,
        kernel=session.kernel,
        recorder=session.recorder,
        completion_admitter=admitter,
    )
```
Required invariant:
```text
Write-capable terminal success requires a task-bound,
workspace-bound, fresh verification receipt.
```
### P0: semantic resume is not integrated
The audit falsifier confirms that `ApplicationService.resume` reconstructs a generic resume brief rather than restoring `CodingTaskState`.
Consequences:
- Objective can be lost.
- Constraints can be lost.
- Next action can be lost.
- Dead ends can be repeated.
- Settled effects can be repeated.
- Provider calls can be duplicated.
- Long plans become expensive and fragile.
Fix:
```python
def resume(run_id):
    events = event_store.read_stream(run_id)
    checkpoint = checkpoint_store.latest_valid(run_id)
    state = reconstruct_coding_state(
        checkpoint,
        events.after(checkpoint.sequence),
    )
    task = TaskContext(
        run_id=run_id,
        brief=state.objective,
        constraints=state.constraints,
        remaining_budget=state.remaining_budgets,
    )
    return runtime.continue_from(
        task=task,
        coding_state=state,
        next_action=state.next_action,
        settled_effects=state.settled_effects,
    )
```
The continuation must work in a fresh process.
### P0: official benchmark path is incomplete
The standalone multifile benchmark directly calls OpenRouter with `urllib`.
It bypasses the official model adapter and runtime.
It asks the model to emit complete files in Markdown blocks.
It parses those blocks manually.
It invokes a host subprocess oracle.
This is useful as a baseline.
It is not evidence for Coding Max.
Required target path:
```text
frozen task
    → exact workspace
    → official Vanguard runtime
    → one episode attempt
    → mediated tools
    → exact trajectory
    → pure unified patch
    → exterior evaluator
    → signed evidence bundle
```
### P0: LAM trajectories are incomplete for the multifile runner
The multifile runner records aggregate metadata.
It does not persist the request and response blobs.
It does not persist a trajectory blob path.
It does not persist the generated model output.
It does not persist the parsed file candidates.
It does not persist before/after snapshots.
It does not persist a unified patch digest.
It does not persist the evaluator identity digest.
Therefore, those records cannot support exact replay.
Required record:
```python
RecordedExchange(
    request_digest,
    request_blob_digest,
    response_digest,
    response_blob_digest,
    provider,
    model,
    route_id,
    prompt_tokens,
    completion_tokens,
    observed_cost,
    latency_ms,
    evidence_label,
)
```
Required trajectory:
```python
CodingTrajectory(
    task_digest,
    workspace_preimage_digest,
    composition_digest,
    episode_id,
    exchanges,
    tool_receipts,
    patch_digest,
    evaluator_verdict_digest,
    terminal_disposition,
)
```
### P1: production preset identities are incomplete
Local overlays exist.
Production registry qualification does not prove all of:
```text
vg-code-fast
vg-code-balanced
vg-code-max
```
Each preset needs a stable manifest identity and composition digest.
### P1: repository intelligence is duplicated
The pack-level repository map still performs scanning and truncation independently.
This can produce inconsistent facts, bounds, and provenance.
All repository observations should flow through `IndexPort` or a generic mediated fallback.
### P1: multi-file closure is not proven
The presence of dependency and test association types does not prove that every affected file and test is selected.
The harness needs transitive change-surface analysis, bounded but disclosed retrieval, and explicit verification coverage.
### P1: Coding Max facade is not accepted
The required run, status, resume, evidence, and cost contract is not yet proven to be shared by CLI and API.
The app layer must remain thin.
It must not own execution, persistence, provider HTTP, or evaluator authority.
## SOTA implementation architecture
The target system should be organized as:
```text
CLI / API
    → thin Coding Max facade
        → shared ApplicationService
            → runtime composition
                → code-default policy
                    → EpisodeEngine
                        → Kernel
                            → mediated adapters
```
The coding agent needs separate control, data, persistence, and evidence planes.
### Control plane
The control plane decides what should happen next.
It must not grant authority.
It should operate on typed observations and durable state.
### Data plane
The data plane performs:
```text
understand
→ explore
→ localize
→ plan
→ edit
→ verify
→ recover
→ complete
```
### Persistence plane
The persistence plane stores events and content-addressed artifacts.
`CodingTaskState` is a projection.
Events remain the durable source.
### Evidence plane
The evidence plane binds:
- Task.
- Workspace.
- Composition.
- Model route.
- Trajectory.
- Patch.
- Tests.
- Evaluator.
- Terminal disposition.
## Agent design for hard tasks
The primary worker should be a stateful evidence-seeking agent.
It should not be a single giant prompt.
It should not dump the repository into context.
It should not treat model confidence as verification.
### Primary worker loop
```python
while not state.terminal:
    observation = collect_next_observation(state)
    state = state.record(observation)
    if state.needs_localization:
        evidence = index_port.query(state.unresolved_question)
        state = state.record(evidence)
        continue
    if state.needs_plan:
        plan = planner.create_plan(state)
        state = state.record(plan)
        continue
    if state.needs_edit:
        proposal = model.propose_patch(
            context=compile_progressive_context(state),
            protocol=patch_protocol,
        )
        result = patch_gateway.apply(proposal)
        state = state.record(result)
        continue
    if state.needs_verification:
        verdict = verifier.run(select_verification(state))
        state = state.record(verdict)
        continue
    if state.needs_recovery:
        recovery = recovery_policy.classify(state)
        state = state.record(recovery)
        continue
    completion_admitter.require_fresh_evidence(state)
    state = state.complete()
```
### Planner
The planner should produce explicit hypotheses, not vague prose.
Each plan item should include:
- Objective.
- Preconditions.
- Candidate files.
- Expected behavior.
- Verification command.
- Completion evidence.
- Risk.
- Rollback strategy.
Example:
```python
PlanStep(
    id="P3",
    objective="preserve WAL ordering during crash replay",
    candidate_files=("wal.py", "coordinator.py", "recovery.py"),
    preconditions=("replay parser accepts version 2 records",),
    verification=("python -m pytest tests/test_recovery.py -q",),
    evidence_required=("fresh-test-receipt",),
    risk="duplicate commit after restart",
)
```
### Localizer
The localizer should search in stages:
```text
task terms
→ symbols
→ callers
→ dependencies
→ tests
→ configuration
→ generated artifacts
```
It should maintain competing hypotheses.
It should record rejected hypotheses as dead ends.
It should never silently discard a context miss.
### Editor
The editor should use structured patch operations.
Preferred protocol:
```json
{
  "files": [
    {
      "path": "src/example.py",
      "operations": [
        {
          "kind": "replace_range",
          "start": 41,
          "end": 49,
          "content": "..."
        }
      ]
    }
  ]
}
```
The gateway should reject:
- Absolute paths.
- Traversal.
- Symlink escape.
- Test modifications unless explicitly permitted.
- Unrecognized files.
- Ambiguous ranges.
- Patches without a preimage digest.
### Verifier
The verifier must run through the mediated environment path.
Verification should be layered:
```text
syntax
→ focused test
→ affected tests
→ package tests
→ repository suite
```
The next layer should be selected from evidence and risk.
### Recovery controller
Recovery should not be “try again.”
It should classify the failure.
```python
if failure.is_protocol_error:
    return repair_protocol_and_retry_same_step()
if failure.is_context_miss:
    return retrieve_targeted_evidence()
if failure.is_patch_conflict:
    return refresh_preimage_and_rebase_patch()
if failure.is_test_failure:
    return localize_failure_and_revise_plan()
if failure.is_provider_unavailable:
    return typed_incomplete_provider_state()
if failure.is_budget_exhausted:
    return typed_incomplete_budget_state()
```
## Large-context strategy
Large context should be treated as retrieval and evidence management.
More tokens do not automatically produce better reasoning.
The context compiler should preserve:
- Objective.
- Constraints.
- Current plan.
- Unresolved questions.
- High-confidence discoveries.
- Rejected hypotheses.
- Modified files.
- Latest diagnostics.
- Relevant symbols.
- Relevant tests.
- Required invariants.
It should discard:
- Redundant narration.
- Repeated tool output.
- Duplicate source excerpts.
- Stale diagnostics.
- Low-confidence irrelevant files.
Retrieval ranking should consider:
- Symbol relevance.
- Dependency distance.
- Test association.
- Change risk.
- Public API status.
- Provenance quality.
- Recency.
- Unresolved-question coverage.
Context packets should be independently digestible.
Every observation should carry source identity and truncation facts.
## Multifile correctness
The harness should calculate a change surface before completion.
```python
changed = set(patch.modified_files)
impacted = transitive_dependents(
    changed,
    dependency_graph,
    max_depth=policy.max_dependency_depth,
)
tests = union(index.tests(file) for file in changed | impacted)
for file in changed | impacted:
    require_considered(file)
verification = select_tests(
    targeted=index.tests_for(changed),
    affected=tests,
    broad=policy.broad_suite,
)
```
Completion should fail closed when the change surface is unknown.
Greenfield tasks need a declared scaffold, baseline, and behavioral evaluator.
Syntax success alone is not completion.
## CLI and API contract
The thin facade should expose:
```python
class CodingMaxService:
    def run(request): ...
    def status(run_id): ...
    def resume(run_id): ...
    def evidence(run_id): ...
    def cost(run_id): ...
```
CLI and API must share this service.
They must return the same:
- Run ID.
- Composition digest.
- Status.
- Plan state.
- TODO state.
- Verification identity.
- Evidence references.
- Cost summary.
- Terminal disposition.
The application facade must not own a second runtime, store, evaluator, or provider client.
## Agent portfolio
The first supported agent should be Coding Max.
After its contract stabilizes, add:
- Code Reviewer.
- Research agent.
- Tutor or repository explainer.
All must use the same public runtime/application contract.
Specialists should be sequential and verifier-subordinate by default.
Enable them only after measured ablations show positive value.
## Benchmark protocol for World-tier competitiveness
The benchmark must use a frozen task set.
Each task must contain:
- Task ID.
- Task digest.
- Base workspace digest.
- Base revision.
- Public task statement.
- Hidden evaluator.
- Allowed tools.
- Required tests.
- Attempt limit.
- Token ceiling.
- Cost ceiling.
- Wall-clock ceiling.
- Missingness policy.
- Contamination policy.
Recommended task families:
- Single-file behavioral bugs.
- Cross-module bugs.
- Multi-file features.
- API migrations.
- Database migrations.
- Concurrency defects.
- Async lifecycle defects.
- Fault-tolerance defects.
- Noisy repositories with decoy code.
- Large-context localization.
- Greenfield libraries.
- Greenfield services.
- Resume-after-crash tasks.
- Patch-conflict tasks.
- Provider failure tasks.
Recommended arms:
```text
B0: model-only one-shot
B1: model plus simple tool loop
B2: Vanguard fast
B3: Vanguard balanced
B4: Vanguard max
B5: Vanguard balanced plus sequential reviewer
```
Hold constant:
- Model.
- Task set.
- Evaluator.
- Attempt count.
- Temperature.
- Context ceiling.
- Cost ceiling.
Report:
- Pass rate.
- Patch applicability.
- Test pass rate.
- Cost per task.
- Cost per successful task.
- Tokens per task.
- Turns per task.
- Wall time.
- Context misses.
- Tool errors.
- Recovery count.
- Resume parity.
- Invalid completion count.
## Harness-lift measurement
Define:
```text
Y_i = external evaluator pass for task i
C_i = observed USD cost
T_i = observed tokens
L_i = observed latency
```
Primary metric:
```text
lift = pass_rate(treatment) - pass_rate(control)
```
Efficiency metrics:
```text
success_per_dollar = successful_tasks / total_cost
success_per_token = successful_tasks / total_tokens
```
Use paired tasks and bootstrap confidence intervals.
Keep development, calibration, audit, and held-out sets separate.
Do not tune prompts, routing, or thresholds on the held-out set.
Do not report replay results as live results.
Do not report model-only results as harness results.
## LAM replay protocol
The live run should write:
```text
task.json
workspace-preimage.tar.zst
trajectory.json
requests/
responses/
tool-receipts.jsonl
patch.diff
workspace-postimage.tar.zst
evaluator-result.json
evidence-bundle.json
```
Every artifact should be content-addressed.
LAM should import the exact trajectory and cassette.
Replay should verify:
```text
same request digest
same response bytes
same parser result
same patch digest
same evaluator result
same terminal disposition
```
Secrets must never enter prompts, trajectories, patches, logs, or evidence artifacts.
## Recommended execution order
### Step 1: Finish REL-01/H0
- Remove direct provider HTTP from the official benchmark path.
- Use the official model adapter.
- Use the official runtime.
- Use the exterior evaluator.
- Materialize exact workspaces.
- Emit pure unified patches.
- Bind artifacts by digest.
- Preserve typed missingness.
- Keep dry-run structural only.
### Step 2: Make LAM exact
- Store exact request blobs.
- Store exact response blobs.
- Store tool results.
- Store patch and workspace digests.
- Store evaluator result digests.
- Add deterministic replay tests.
### Step 3: Wire completion admission
- Pass the admitter through the production session.
- Reject stale receipts.
- Reject zero-test completion.
- Reject post-verification modifications.
- Require task and workspace identity matches.
### Step 4: Integrate semantic resume
- Rebuild state from events and checkpoints.
- Restore objective and constraints.
- Restore next action.
- Restore dead ends and discoveries.
- Restore remaining budgets.
- Deduplicate settled effects.
- Test fresh-process recovery.
### Step 5: Register presets
- Add stable manifest identities.
- Record composition digests.
- Test CLI/API preset parity.
- Verify bounded capability differences.
### Step 6: Unify repository intelligence
- Route pack queries through `IndexPort`.
- Remove duplicated scanners.
- Add semantic truncation.
- Add provenance and freshness checks.
- Add deterministic fallback.
### Step 7: Complete CMX-04 and CMX-05
- Prove change-surface closure.
- Prove affected-test selection.
- Prove greenfield baselines.
- Prove CLI/API agreement.
- Prove evidence and cost projections.
### Step 8: Qualify CMX-06 and CMX-07
- Freeze the task set.
- Run controlled ablations.
- Measure reviewer value.
- Measure large-context retrieval.
- Measure resume parity.
- Report missingness honestly.
### Step 9: Compare against world-tier baselines
- Use recognized external benchmarks where licensing and infrastructure permit.
- Use independently reproducible internal benchmarks.
- Report exact model and route identities.
- Report all costs and retries.
- Publish task-level evidence.
- Separate system lift from model lift.
## Stop-ship conditions
Stop claiming completion if any of the following remain:
- Direct provider HTTP in product or benchmark logic.
- Missing trajectory linkage.
- Missing patch linkage.
- Missing evaluator linkage.
- Synthetic success metrics.
- Zero-test completion.
- Stale verification receipt.
- Duplicate settled effects after resume.
- Capability expansion during preset escalation.
- Adapter imports of app or agency policy.
- Host subprocesses outside the mediated environment.
- Unbounded repository context.
- Missing model/provider identity.
- Unreported provider usage.
- SOTA claim without reproducible external evidence.
## Final assessment
Vanguard has a credible foundation for a high-assurance agentic coding system.
It is ahead of a simple prompt-and-tools prototype in security, provenance, budgets, architecture, and falsifier discipline.
It is not yet competitive evidence for World-tier coding scores.
The main risk is not lack of clever mechanisms.
The main risk is disconnected mechanisms and insufficient end-to-end measurement.
The fastest route to a superior system is:
```text
integrate
→ make evidence exact
→ make resume semantic
→ make multifile closure explicit
→ qualify the real runtime
→ measure harness lift
→ add specialists only when ablations justify them
```
The system should first become reliably measurable.
Then it can become reliably better.
Only after that should it make a SOTA claim.
