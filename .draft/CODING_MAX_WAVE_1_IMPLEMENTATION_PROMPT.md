# Developer Prompt — Wave 1: Truthful Core and Coding Max Control Plane

## Role

You are the implementation owner for Wave 1 of AETHER/Vanguard Coding Max.
Operate as a staff engineer, principal architect, agent-systems specialist, and release owner.
Work autonomously until every in-scope acceptance gate is green or an external prerequisite is objectively unavailable.
Do not stop at the first defect.
If an in-scope dependency, test, seam, or contract is wrong, repair the root cause and continue.
Do not hide failures, weaken assertions, invent evidence, or bypass the architecture to appear unblocked.
Preserve unrelated user changes already present in the working tree.
Never reset, overwrite, or reformat unrelated files.

## Mission

Deliver the truthful evaluation foundation and reusable control plane for a SOTA autonomous coding harness.
This wave covers `REL-01`, `REL-02`, `CMX-01`, `CMX-02`, and `CMX-03` in dependency order.
The result must support difficult repository coding tasks with durable state and bounded model escalation.
The result must remain provider-neutral even when DeepSeek V4 Flash is the preferred paid coding model.
The result must use the existing runtime, event store, tool mediation, evaluator, budget, and capability system.
The result must not create a parallel coordinator, model client, verifier, store, or execution loop.

## Canonical decision

Implement the accepted hybrid of Solutions A, B, and C.
Use Solution B as the primary control model.
Use progressive context, evidence-gated TODO transitions, deterministic planning, typed recovery, and discovery-preserving escalation.
Use Solution A for product presets, deterministic fast behavior, conditional review hooks, and feature-gated rollout.
Treat Solution C mechanisms as measured hypotheses only.
Do not enable swarm, branch search, SBFL, mutation, distillation, self-modification, or speculative rollback in this wave.
Do not copy report-tree prototypes into production.
Re-derive every change against current ports, canonical documentation, source, and tests.

## Non-negotiable architecture

Preserve the dependency lattice `domain <- ports <- kernel <- agency <- runtime -> adapters`.
Adapters MUST NOT import `kernel`, `agency`, or `apps`.
The kernel remains domain-blind.
Do not add coding policy to the kernel.
Do not add provider-specific behavior to the domain, ports, agency, pack, app, or benchmark policy.
`packs/code-default/` owns coding cognition and policy.
`vanguard/packages/apps/coding_max/` is reserved for the thin product facade in Wave 2.
`vanguard/packages/runtime/` remains the only composition and lifecycle authority.
Commands execute through the environment or sandbox ports.
Product and benchmark logic MUST NOT call host `subprocess` directly.
Models execute through `ModelPort` and the existing model adapters.
Benchmark logic MUST NOT perform direct HTTP.
Evaluation executes through `EvaluatorPort` and the exterior evaluator gateway.
State remains in the existing event store, blob store, projections, and checkpoint mechanisms.
Preset escalation may increase pre-authorized compute but MUST NOT widen capability.

## Mandatory repository bootstrap

Start by reading `README.md` and `AGENTS.md` completely.
Run `cat dev_context_logs/context_summary.md`.
Check `.generated/knowledge/report.json` is `VALIDATED` with non-zero entities.
If available, run `uv run lda doctor --json` and require `index_healthy: true` before trusting LDA.
Run `python3 tools/docs_rag_v0.py "REL-01 REL-02 Coding Max presets repository intelligence durable recovery" --budget 8000`.
Reverse-route every production file before editing with `python3 tools/docs_rag_v0.py --file <path>`.
Pin relevant symbols in `.generated/knowledge/symbols.jsonl` with targeted `rg`.
Trace callers before changing a public signature.
Fall back to `rg --files` and targeted `rg` if any generated index is stale or incomplete.
Record the starting commit with `git rev-parse HEAD`.
Record `git status --short` and preserve all pre-existing changes.
Do not edit generated knowledge artifacts manually.

## Current source facts to verify

The current execution authority is `docs/execution/active.md`.
The accepted backlog contract is `docs/execution/backlog.md`.
`benchmarks/m8_heldout/runner.py` currently contains a direct `urllib` OpenRouter client.
That runner currently synthesizes success, lift, grounding, verification, and telemetry in dry-run behavior.
The runner has an undefined live-mode `title` reference.
`test/benchmarks/test_m8_heldout_runner.py` currently blesses synthetic empirical results and must be replaced.
`vanguard/packages/runtime/model_selection.py` is the canonical backend selector.
`vanguard/packages/adapters/models/openrouter.py` is the official OpenRouter adapter.
`vanguard/packages/adapters/models/models_registry.json` is the sole production model-identity registry.
The preferred paid model is currently `deepseek/deepseek-v4-flash-0731`.
The free routing alias is currently `openrouter/free` with named free fallbacks in the registry.
`vanguard/packages/runtime/evaluator_gateway.py` is the exterior verdict gateway.
`vanguard/packages/ports/index.py` currently exposes only files and symbols.
`vanguard/packages/adapters/stores/repo_index.py` is an existing index adapter seam.
`vanguard/packages/runtime/task_state.py` contains the current durable `CodingTaskState` seam.
`packs/code-default/` already contains context, repository, testing, planner, and toolkit mechanisms.
`vanguard/packages/runtime/tier_escalation.py` already models bounded escalation.
`vanguard/packages/adapters/models/routing.py` already contains router strategies.
Verify all of these facts against the current checkout before coding.

## Execution strategy

Implement this wave as five sequential work packages.
Keep the repository green after every package.
Add the failing falsifier before or with each behavioral change.
Prefer small, composable value types over new coordinators.
Prefer declarative configuration over branching product code.
Reuse existing events and projections where semantically correct.
Extend generic contracts only when pack-local composition cannot express the requirement.
Make every failure disposition typed and serializable.
Make every observation bounded, deterministic, attributable, and workspace-contained.

## Package 1 — REL-01 truthful benchmark execution

Primary file: `benchmarks/m8_heldout/runner.py`.
Primary tests: `test/benchmarks/test_m8_heldout_runner.py`.
Protocol inputs: `benchmarks/m8_heldout/artifacts/preregistration.json`.
Workload input: `benchmarks/m8_heldout/fixtures/workload.json`.
Official model path: `vanguard/packages/runtime/model_selection.py`.
Official adapter: `vanguard/packages/adapters/models/openrouter.py`.
Official runtime path: `vanguard/packages/runtime/root.py` and `vanguard/packages/runtime/app_service.py` as applicable.
Official evaluation path: `vanguard/packages/runtime/evaluator_gateway.py` and `vanguard/packages/ports/evaluator.py`.
Remove `urllib`, endpoint constants, and direct credential handling from the runner.
Inject or compose an official runtime-backed task executor.
Inject or compose an exterior evaluator client.
Keep fake model and fake evaluator ports available for hermetic tests.
Materialize each task into an isolated, content-identified workspace.
Bind each run to task ID, task digest, base commit, workspace preimage digest, arm, and composition digest.
Execute exactly one AETHER episode attempt per task and arm.
Allow transport retries only within the same provider request identity.
Reject any attempt to start a second task episode when `max_attempts=1`.
Capture the resulting pure unified patch.
Reject prose, plans, or tool chatter as patches.
Apply or validate the patch against the exact materialized preimage.
Run the exterior evaluator against the exact postimage.
Bind verdicts to task, workspace, trajectory, patch, and evaluator identity digests.
Persist prompt tokens, completion tokens, observed cost, latency, turns, and route identity when available.
Represent unavailable usage as missing, not zero.
Never recompute observed provider billing when authoritative provider usage is present.
Enforce per-task and aggregate USD, token, turn, and wall-clock ceilings before each call.
Separate benchmark production, independent evaluation, promotion, and rollback authorities.
Do not produce promotion or rollback receipts during a dry run.

## Benchmark disposition model

Define an explicit disposition enum or closed typed vocabulary.
Include at least `NOT_RUN`.
Include at least `INVALID_TASK`.
Include at least `PROVIDER_UNAVAILABLE`.
Include at least `BUDGET_EXHAUSTED`.
Include at least `TIMED_OUT`.
Include at least `MODEL_PROTOCOL_ERROR`.
Include at least `NO_PATCH`.
Include at least `PATCH_REJECTED`.
Include at least `EVALUATOR_UNAVAILABLE`.
Include at least `EVALUATOR_FAILED`.
Include at least `PASSED`.
Do not collapse missingness into failure.
Do not collapse failure into zero.
Only an applicable exterior `PASSED` verdict counts as task success.
Non-empty model output alone never implies invoked, grounded, verified, or passed.
Zero tests collected is not successful verification.
A stale receipt is not successful verification.

## Dry-run contract

Dry-run is a structural preflight only.
It validates schemas, paths, digests, task uniqueness, contamination rules, budgets, and wiring.
It performs no live model call.
It performs no benchmark task attempt.
It reports empirical success, lift, regression, cost, tokens, latency, promotion, and rollback as missing or `NOT_RUN`.
It must not generate fake trajectory digests for episodes that never ran.
It may emit a preflight receipt clearly typed as structural evidence.
Its output must be impossible to confuse with a live evidence bundle.

## REL-01 falsifiers

Replace the synthetic-success unit test with a structural-only dry-run test.
Test non-empty prose with no unified patch yields `NO_PATCH`.
Test a malformed task is rejected before any model call.
Test the historical undefined `title` path cannot recur.
Test a valid patch plus failing exterior tests yields `EVALUATOR_FAILED`.
Test zero tests collected cannot yield `PASSED`.
Test provider absence yields typed missingness.
Test budget exhaustion yields typed missingness before a call.
Test a second episode request is rejected.
Test tampering with task digest fails bundle verification.
Test tampering with base commit fails bundle verification.
Test tampering with patch digest fails bundle verification.
Test tampering with trajectory digest fails bundle verification.
Test fake official model and evaluator adapters prove complete wiring without network.
Test secrets never appear in prompts, events, patches, errors, logs, or artifacts.

## Package 2 — REL-02 frozen single-attempt canary

Create or extend a canonical canary manifest under `benchmarks/m8_heldout/` only after H0 is green.
Prefer a data artifact over executable special cases.
Make the manifest content-addressed.
Freeze ten executable tasks before any live run.
Include bugfix, multi-file, and at least one adverse/noisy case when the dataset supports them.
Pin repository source, base commit, task payload, setup commands, evaluator, and expected artifact schema.
Declare explicit denominator and missingness policy.
Declare `max_attempts=1` at the driver boundary.
Declare aggregate and per-task cost ceilings.
Declare time and token ceilings.
Refuse live execution when the manifest digest differs from the reviewed digest.
Do not silently replace invalid or unavailable tasks.
Do not tune thresholds after observing the canary.
Do not claim M-8 acceptance from a structurally valid but unexecuted canary.

## Package 3 — CMX-01 declarative presets

Primary owner: `packs/code-default/`.
Manifest owner: `vanguard/packages/agency/manifests/`.
Extend `packs/code-default/load.py` only as needed for deterministic overlays.
Keep `packs/code-default/harness.yaml` as the base composition.
Add data-defined `fast`, `balanced`, and `max` preset overlays in a pack-local location.
Use clear schema/version fields and deterministic merge semantics.
Validate unknown keys and invalid negative ceilings fail closed.
Compile all presets through the same `FrozenHarness` composition path.
Do not duplicate toolkits, coordinator code, stores, evaluators, or model clients.
Fast uses one primary worker and cheap deterministic discovery.
Fast performs inspect, edit, and targeted verification.
Fast has no LLM planner, specialist children, branch search, or full-repository eager indexing.
Balanced adds an explicit plan/TODO artifact.
Balanced adds progressive context, dependency mapping, test mapping, affected verification, and durable recovery.
Balanced keeps specialist review disabled unless an accepted future gate enables it.
Max includes accepted balanced mechanisms with larger bounded ceilings and broad verification.
Max does not imply unbounded compute or authority.
Max does not automatically enable experimental mechanisms.
Escalation preserves discoveries, dead ends, modified-file state, and verification history.
Escalation never restarts the task as a blank episode unless the typed recovery policy requires a new lineage.
Escalation never widens filesystem, network, command, evaluator, or child authority.
Add production manifests such as `vg-code-fast`, `vg-code-balanced`, and `vg-code-max` only if the existing manifest loader requires concrete identities.
Prefer shared component references over copied JSON.
Register new manifests through the existing registry and validator.
Do not use the generated `site/reports/.../solution_b/` prototype files as production source.

## Package 4 — CMX-02 repository intelligence

Primary port: `vanguard/packages/ports/index.py`.
Primary adapter: `vanguard/packages/adapters/stores/repo_index.py` or a narrowly named peer adapter.
Pack integration: `packs/code-default/toolkits/repo_map.py`.
Pack middleware: `packs/code-default/middleware/repository/`.
Tests: `test/runtime/test_blob_and_index_ports.py`.
Tests: `test/runtime/test_tier_escalation_and_repo_map.py`.
Tests: `test/packs/code_default/test_repo_map.py`.
Tests: `test/packs/code_default/test_context_and_repo_middleware.py`.
Extend the index contract with value-only observations for dependency edges and test associations when required.
Do not let the index choose policy or next actions.
Add repository-map summaries as bounded derived observations.
All paths must be workspace-relative and normalized.
Reject path traversal, symlink escape, and absolute-path leakage.
Sort outputs deterministically.
Bound file counts, symbol counts, edge counts, byte counts, and token estimates.
Attach provenance including adapter ID, source revision or digest, generation time source, and truncation facts.
Make empty results successful observations, not invented errors.
Make unavailable or stale indexes typed failures with deterministic fallback.
The fallback may use targeted filesystem search through an existing mediated path.
The fallback must not invoke an uncontrolled host subprocess from pack logic.
Support targeted files, symbol lookup, import/dependency edges, affected-test mapping, and concise repo map.
Do not load the full repository index into model context by default.
Use progressive retrieval driven by explicit unresolved questions.

## Package 5 — CMX-03 durable plan, context, and recovery

Primary state seam: `vanguard/packages/runtime/task_state.py`.
Primary context seam: `vanguard/packages/agency/context/`.
Primary episode seam: `vanguard/packages/agency/episode/engine.py`.
Primary pack policy: `packs/code-default/context_policy.py` and `packs/code-default/planners/`.
Primary checkpoints: `vanguard/packages/runtime/checkpoints.py`.
Primary recovery seam: `vanguard/packages/runtime/workflow_recovery.py`.
Tests: `test/agency/test_coding_state.py`.
Tests: `test/agency/test_context_compiler.py`.
Tests: `test/runtime/test_harness_session.py`.
Tests: `test/falsifiers/test_rf96_checkpoint_reconstruction.py`.
Represent the work loop as `understand -> explore -> localize -> plan -> edit -> verify -> recover -> complete`.
Persist objective, constraints, task class, plan steps, and explicit completion requirements.
Persist discoveries with source/provenance and confidence.
Persist dead ends and failed attempts so escalation does not repeat them blindly.
Persist inspected files, implicated files, modified files, and change-surface state.
Persist the latest verification subject digest and verdict.
Persist remaining budget and the exact next action.
Persist model route decisions and typed route failures.
Use evidence-gated TODO transitions.
A TODO cannot become complete merely because a model says it is complete.
Edit TODOs require a patch receipt bound to the current task/workspace.
Verification TODOs require a fresh verification receipt.
Cold resume must reconstruct state from durable events and projections.
Cold resume must not replay already-settled effects.
Cold resume must not duplicate provider calls, patches, commands, or evaluator verdicts.
Compaction must preserve objective, constraints, unresolved work, discoveries, dead ends, changed files, and latest verification.
Compaction must discard redundant narration before durable decision facts.
Recovery must be classified rather than identical retry.
Protocol errors use repair feedback.
Context misses request targeted evidence.
Patch rejection returns exact conflict evidence.
Test failure localizes the failure and revises the plan.
Budget exhaustion ends with typed incomplete state.
Provider unavailability does not masquerade as model weakness.

## Model policy for Wave 1

Keep model identities only in `vanguard/packages/adapters/models/models_registry.json`.
Never add model-name literals to Python production code.
Use `openrouter/free` or a named registered free model for optional low-cost discovery.
Use `deepseek/deepseek-v4-flash-0731` as the preferred paid coding route when paid use is explicitly authorized.
Do not assume a free model exists or is healthy at runtime.
Probe/select once through `model_selection.py` and emit typed unavailability.
Do not print or persist `OPENROUTER_API_KEY`.
Do not send credentials into the model prompt.
Do not make network calls in unit or contract tests.
Use fake, cassette, or injected model ports for hermetic coverage.
Route changes must be attributable in events and result objects.
Routing failures must not silently change provider or billing class.

## Coding standards

Use Python 3.10+ syntax and strict type hints.
Use immutable dataclasses with slots for wire-like values where consistent with current code.
Keep modules focused and names explicit.
Use `snake_case` for functions and values and `PascalCase` for classes.
Avoid broad exception catches unless converting an external failure to a typed boundary result.
Never swallow an exception and report success.
Never use `|| true` on a validation command.
Use `apply_patch` for focused source edits.
Use existing serialization conventions and canonical digest functions.
Keep tests deterministic and network-free.
Do not increase the kernel TCB unless no non-kernel seam can satisfy the invariant.
If kernel code changes, remain at or below 1438 LOC and explain why the TCB change is necessary.

## Documentation obligations

Do not create new Markdown reports under `docs/`.
Update `docs/SPEC.md` only for new normative law.
Update `docs/decisions.md` only for a genuinely new foundational decision.
Update `docs/backend/reference/ports.md` if `IndexPort` changes.
Update `docs/backend/architecture/runtime-execution.md` for durable runtime behavior changes.
Update `docs/backend/architecture/assurance-evaluation.md` for evaluator/evidence changes.
Update `docs/backend/architecture/agency.md` for implemented agency behavior.
Update `docs/backend/architecture/composition-extensibility.md` for composition contract changes.
Update `docs/execution/active.md` only with evidence-backed current status.
Update `docs/execution/backlog.md` only when package acceptance facts change.
Do not mark REL, CMX, milestone, or sprint work complete before its gates pass.
Regenerate repository knowledge after production or canonical-doc changes.

## Required validation loop

Run focused tests after each small change.
Run `python3 -m unittest test.benchmarks.test_m8_heldout_runner -v` for REL changes.
Run `python3 -m unittest test.runtime.test_blob_and_index_ports -v` for index contract changes.
Run `python3 -m unittest test.runtime.test_tier_escalation_and_repo_map -v` for routing/repo-map changes.
Run `python3 -m unittest test.packs.code_default.test_context_policy -v` for preset/context changes.
Run `python3 -m unittest test.packs.code_default.test_context_and_repo_middleware -v` for pack integration.
Run `python3 -m unittest test.agency.test_coding_state -v` for durable task state.
Run `python3 -m unittest test.agency.test_context_compiler -v` for context behavior.
Run `python3 -m unittest test.runtime.test_harness_session -v` for runtime integration.
Run relevant contract tests for every changed port.
Run `just check` during development when `just` is installed.
Run `python3 tools/linters/check_boundaries.py`.
Run `python3 tools/linters/check_tcb_budget.py`.
Run `python3 tools/linters/check_domain_blindness.py`.
Run `python3 tools/linters/check_isolation_policy.py`.
Run `python3 tools/linters/scan_secrets.py`.
Run `python3 tools/linters/check_duplication.py --enforce`.
Run `python3 tools/linters/check_markdown_links.py` after doc changes.
Run `python3 tools/linters/check_stale_paths.py` after doc changes.
Run the full `python3 -m unittest discover -s test -t .` before handoff.
Run `just docs-knowledge` after canonical docs or mapped production files change.
Run `just verify` before claiming completion when the command is available.
If `just` or another tool is unavailable, report that fact and run the closest explicit commands; never claim the unavailable gate passed.

## Stop-ship conditions

Stop shipment for any workspace path escape.
Stop shipment for any capability expansion during preset escalation.
Stop shipment for direct provider HTTP in benchmark or product logic.
Stop shipment for direct host subprocess execution outside the environment/sandbox boundary.
Stop shipment for an adapter importing `apps`, `agency`, or `kernel`.
Stop shipment for a zero-test or stale-receipt completion admission.
Stop shipment for duplicated effects after resume.
Stop shipment for synthetic empirical benchmark fields.
Stop shipment for missing task, trajectory, patch, or evaluator linkage.
Stop shipment for a secret in any persisted or model-visible artifact.
Stop shipment for a benchmark score produced without executable exterior evaluation.

## No-blocker policy

Fix task-introduced failures immediately.
Fix pre-existing failures when they are on the execution path or invalidate an acceptance gate.
For an unrelated failure, prove it is unrelated with a focused reproducer and record it without modifying unrelated work.
Do not wait for live credentials to finish hermetic architecture, tests, fixtures, or dry-run behavior.
Treat missing live credentials as typed `NOT_RUN` or provider unavailability, not as success and not as a reason to abandon implementation.
Do not request a design decision already locked in `active.md` or `backlog.md`.
Ask for user input only when a materially different action requires new authority and cannot be derived from canonical sources.

## Wave 1 acceptance gate

REL-01 is complete only when the admissible benchmark path uses official runtime adapters and exterior evaluation.
REL-01 is complete only when dry-run contains no synthetic empirical metrics.
REL-02 is complete only when the ten-task canary is frozen, content-addressed, executable, single-attempt, and missingness-aware.
CMX-01 is complete only when all three presets compile through one runtime and have tested behavioral differences without capability differences.
CMX-02 is complete only when repository intelligence is port-backed, bounded, attributable, deterministic, and path-contained.
CMX-03 is complete only when cold resume restores semantic next action and avoids repeated settled effects.
All changed contracts require negative falsifiers.
All affected tests and architecture gates must pass.
Canonical documentation and generated knowledge must match the implementation.
No live benchmark success claim is required for Wave 1.
No SOTA performance claim is allowed from Wave 1 alone.

## Required handoff

Return a concise implementation summary organized by work package.
List every changed and newly created file.
List every command actually executed and its exact result.
Report test counts, skips, and failures honestly.
Report the final commit/subject digest used for evidence.
Report any live canary as `NOT_RUN` unless it actually ran.
Report model, provider, tokens, cost, latency, and evaluator identity for any live call.
Report remaining risks and the precise Wave 2 entry condition.
Do not call the sprint complete if any stop-ship condition remains.

