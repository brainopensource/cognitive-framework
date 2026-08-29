 You are implementing the complete benchmark program defined in:

    BENCHMARK_V090_FULL.MD

  Repository:

    /home/rocha/Coding/Aether-D-System

  Your job is to BUILD AND EXECUTE the benchmark program—not merely inspect the repository and report that its implementation is missing.

  Read these files completely before changing anything:

  1. AGENTS.md
  2. README.md
  3. BENCHMARK_V090_FULL.MD
  4. docs/03_execution/sprint_active.md
  5. docs/03_execution/milestones.md
  6. benchmarks/README.md
  7. Relevant manifest, runtime-lab, model-adapter, evaluator, and benchmark code discovered while implementing the program

  Core interpretation

  The following missing paths or components are deliverables, not blockers:

  - benchmarks/frontier_v090/
  - tools/benchmark-drivers/
  - The 27-row orchestrator
  - Preregistration artifacts
  - Benchmark fixtures
  - Challenge definitions
  - Exterior evaluators
  - Budget controller
  - Evidence/report schemas
  - The eleven benchmark presets

  BENCHMARK_V090_FULL.MD explicitly instructs you to create these during Phases 0–4.

  Do not stop merely because they do not exist.

  Mission

  Complete the program in this order:

  1. Inspect the benchmark surfaces and preserve unrelated user files.
  2. Freeze and preregister the experiment.
  3. Validate existing preset surfaces.
  4. Implement all eleven concrete benchmark presets.
  5. Build the external benchmark kit.
  6. Complete a deterministic, unpaid 27-row orchestration dry run.
  7. If the dry run is valid, verify live OpenRouter access safely.
  8. Execute the locked 27-row live experiment if model availability and budget controls permit.
  9. Evaluate every row and produce evidence-backed results.
  10. Report exact outcomes, including failures and framework gaps.

  Non-negotiable safety and repository rules

  - Do not modify these frozen framework paths:

    - vanguard/packages/domain/
    - vanguard/packages/ports/
    - vanguard/packages/kernel/
    - vanguard/packages/agency/episode/
    - vanguard/packages/agency/context/
    - vanguard/packages/runtime/
    - vanguard/packages/adapters/
    - schemas/

  - You may modify or create only benchmark-related solution surfaces permitted by the plan, including:

    - vanguard/packages/agency/manifests/
    - benchmarks/frontier_v090/
    - tools/benchmark-drivers/
    - benchmark tests and fixtures
    - benchmark result artifacts
    - existing canonical documentation when genuinely required

  - Do not create random Markdown plans, reviews, scratch files, or summaries. AGENTS.md prohibits documentation sprawl.
  - Do not create QUICK_WINS_FOR_FRAMEWORK_IMPROVEMENT.MD merely because the benchmark plan mentions it. The repository-wide AGENTS.md anti-sprawl rule takes precedence. Record framework
  gaps in structured benchmark result artifacts and report them to the user unless an existing canonical document is clearly authorized for the update.
  - Never modify frozen framework code to improve a benchmark result.
  - Never invent scores, model responses, tool calls, telemetry, trajectories, or evaluator results.
  - Never treat cassette or fake-model results as empirical model results.
  - Never expose API keys in terminal output, logs, reports, exceptions, or the final response.
  - Never overwrite existing failed-run evidence.
  - Never discard, reset, revert, or overwrite unrelated user changes.
  - Keep provider API keys unset during hermetic tests.
  - Network-dependent/live-provider checks must be explicitly isolated from hermetic tests.

  Branch and delivery rule

  Work only on the branch already provided:

    feat/vanguard-0.9.0b1-beta-evolution

  Do not switch, create, rename, merge, rebase, fetch, pull, or push branches. Focus exclusively on implementing and running the benchmark program. Preserve unrelated user files and
  changes. When the complete benchmark implementation and evidence are ready, the only version-control commands allowed are:

    git add <explicit benchmark files>
    git commit -m "feat(benchmarks): implement Vanguard v0.9 benchmark program"

  Stage only files created or intentionally changed for this benchmark program. Never stage credentials, unrelated evidence, databases, or unrelated user changes. Do not push.

  Filename correction

  The current plan is:

    BENCHMARK_V090_FULL.MD

  The plan may still contain an internal reference to the historical misspelling:

    BENCHAMRKING_V090_FULL.MD

  Use the correctly named file. Do not create a duplicate under the misspelled name.

  Success condition

  The work is not complete merely because some prerequisite is absent.

  At minimum, you must complete Phases 0–4:

  - A digest-addressed preregistration exists.
  - Eleven presets exist and compose, or each failing preset has a precise terminal defect record.
  - Fixtures and exterior evaluators exist.
  - The orchestrator contains exactly 27 preregistered rows.
  - A deterministic cassette/fake dry run processes all 27 rows.
  - Every dry-run row reaches a terminal state.
  - Dry-run outputs are clearly labeled non-empirical.
  - Tests prove no-op rejection, timeout cleanup, budget denial, evidence preservation, and report immutability.

  Only an actual inability to implement this through the permitted solution-layer surfaces may be classified as FRAMEWORK_GAP.

  Phase 0 — discovery, freeze, and preregistration

  1. Inspect the repository for reusable implementations before writing new ones. Search at least:

    - vanguard/packages/agency/manifests/
    - vanguard/packages/runtime/
    - vanguard/packages/adapters/models/
    - vanguard/packages/adapters/evaluators/
    - benchmarks/
    - benchmarks/swe_bench/
    - tools/001_LLM_API_ROUTER/
    - tools/002_LLM_API_MOCK/
    - test/

  2. Find the existing public pack-selecting runtime-lab entrypoint mentioned by the plan.

  3. Do not use a challenge runner that hardcodes `vg-code-default` for comparative execution.

  4. Compute a deterministic SHA-256 digest over every regular file in the frozen paths. Exclude transient caches such as `__pycache__`, `.pyc`, and tool-generated cache directories. Use
  stable relative paths, stable ordering, and byte-level hashes.

  5. Capture:

    - Frozen benchmark-subject digest
    - Frozen framework digest
    - Selected task identifiers and digests
    - Hidden-evaluator digests
    - Eleven manifest/preset identifiers
    - Model request identifier
    - Model parameters
    - Streaming mode
    - Retry policy
    - Timeout policy
    - Per-run budgets
    - Global token and cost ceilings
    - Randomized run order
    - Randomization seed and algorithm
    - Scoring rubrics
    - Report schema version

  6. Store preregistration as machine-readable JSON under the benchmark-specific artifact directory. Serialize canonically and calculate its digest.

  7. Once frozen, the orchestrator must reject unexplained differences between the preregistration and execution inputs.

  8. The plan metadata says `authority: non-authorizing` and `status: proposed`, while its body grants solution-layer implementation authority. Do not use that inconsistency as an excuse
  to stop Phases 0–4. Record the discrepancy in the final report. Do not silently claim milestone acceptance.

  Phase 1 — validate existing preset surfaces

  Locate and validate existing starting materials such as:

  - vg-code-default
  - vg-code-swe-mini
  - vg-code-claude-shaped
  - vg-code-opencode-shaped
  - vg-code-lex
  - vg-code-explain
  - vg-research-minimal
  - vg-code-critic-reviser

  For each candidate:

  - Compose it using the real composition path.
  - Resolve every declared tool.
  - Resolve aliases.
  - Verify required verbs are covered by capabilities.
  - Verify read-only presets cannot mutate files.
  - Parse budgets.
  - Parse context policies.
  - Confirm the preset does not override the locked model.
  - Record success or a precise solution-layer defect.

  Do not declare a framework gap until you prove that the problem cannot be addressed through a manifest, prompt, policy, fixture, external adapter, or benchmark driver permitted by the
  plan.

  Phase 2 — implement eleven concrete presets

  Implement exactly these experimental variants:

  Coding:

  1. C1 — minimal ReAct control
  2. C2 — Claude-shaped evidence loop
  3. C3 — OpenCode-shaped permission-minimal agent
  4. C4 — LEX deterministic surgical agent
  5. C5 — LIM hypothesis-and-falsification agent

  General:

  6. Tutor V1 — basic read/search
  7. Tutor V2 — evidence graph
  8. Research V1 — local research
  9. Research V2 — corroborated/web-capable research
  10. Bugfix V1 — direct repair
  11. Bugfix V2 — reproduce, localize, repair, verify

  Requirements:

  - Implement them as declarative compositions.
  - Reuse existing components where appropriate.
  - Preserve byte-identical shared control components where required by the experiment.
  - Keep the foundation model outside individual preset definitions when possible so the orchestrator can enforce the model lock.
  - Give read-only agents genuinely read-only capabilities.
  - Give coding agents only the minimum write/test capabilities needed.
  - Ensure presets cannot read hidden evaluators.
  - Ensure all eleven presets are selectable through an unchanged public runtime entrypoint.
  - Add focused tests for registration, composition, aliases, permissions, budgets, and model-lock behavior.

  Do not implement vendor-specific behavior inside frozen runtime code.

  Phase 3 — build the external benchmark kit

  Create a cohesive benchmark package under:

    benchmarks/frontier_v090/

  Create command-line driver entrypoints under:

    tools/benchmark-drivers/

  Follow existing repository conventions. Avoid unnecessary third-party dependencies.

  The benchmark kit must include:

  1. Typed run specification.
  2. Exactly 27 preregistered rows.
  3. Deterministic run-order loader.
  4. Global and per-run budget enforcement.
  5. Workspace provisioning.
  6. Immutable source snapshots.
  7. Hidden evaluator isolation.
  8. Runtime invocation through the public pack-selecting path.
  9. Timeout enforcement with descendant-process cleanup.
  10. No-op success rejection.
  11. Model-route verification.
  12. Telemetry capture without invented defaults.
  13. Patch/answer artifact capture.
  14. Exterior evaluation.
  15. Evidence digest calculation.
  16. Cold-reconstruction verification.
  17. Immutable per-run reports.
  18. Aggregate result generation.
  19. Clear dry-run versus live-run labeling.
  20. Resume behavior that never overwrites terminal evidence.

  Challenge matrix

  Coding challenges:

  - One easy challenge
  - One medium challenge
  - One hard challenge
  - Each of the five coding presets runs against all three
  - Total: 15 rows

  General challenges:

  - Tutor easy and hard, run with Tutor V1 and V2
  - Research easy and hard, run with Research V1 and V2
  - Bugfix easy and hard, run with Bugfix V1 and V2
  - Total: 12 rows

  Grand total: exactly 27 rows.

  Challenge validity

  Every challenge must have:

  - A deterministic subject snapshot
  - A stable task digest
  - A failing baseline or equivalent precondition
  - A passing reference state available only to the exterior evaluator
  - Hidden checks inaccessible to the model workspace
  - A validity self-test
  - A documented difficulty classification in machine-readable metadata
  - An evaluator capable of distinguishing no-op, partial, and valid completion

  Prefer existing repository challenges and evaluator machinery where they satisfy the plan. Do not duplicate large challenge collections unnecessarily.

  Reports

  Use the required schema from BENCHMARK_V090_FULL.MD, including:

  - schema
  - run_id
  - preregistration_digest
  - framework_digest
  - manifest_digest
  - task_digest
  - requested model
  - returned model
  - provider
  - terminal status
  - failure taxonomy
  - telemetry
  - patch or answer artifact digest
  - oracle validity and verdict
  - trajectory digest

  Missing provider telemetry must be represented as null with an explicit reason. Never substitute guessed values.

  Terminal classifications must include, as applicable:

  - PASS
  - FAIL
  - INSTRUMENT_ERROR
  - BUDGET_EXHAUSTED
  - PROVIDER_ERROR
  - MODEL_PROTOCOL_ERROR
  - ROUTE_DRIFT
  - ORACLE_ERROR
  - DATASET_DEFECT
  - FRAMEWORK_GAP

  Use the detailed failure taxonomy from the plan for analysis.

  Phase 4 — deterministic unpaid dry run

  **MANDATORY: RUN `MAKE CLEAN-BENCHMARK-CACHE` FROM THE FRESH BENCHMARK WORKSPACE BEFORE EVERY BENCHMARK ROW. NEVER REUSE PYTHON BYTECODE CACHE STATE BETWEEN ROWS. CACHE CLEANUP MUST HAPPEN BEFORE THE SUBJECT SNAPSHOT.**

  Make the benchmark driver invoke `make clean-benchmark-cache` for every newly provisioned workspace and record the command result in each row's evidence. This target removes only
  `__pycache__`, `.pyc`, and `.pyo` artifacts.

  Use deterministic cassette or fake-model infrastructure solely to validate orchestration.

  Do not call these scores empirical.

  Run all 27 rows and prove:

  - Exactly 27 preregistered rows are loaded.
  - Every row reaches a terminal record.
  - Every report binds to the preregistration digest.
  - Every report binds to the unchanged frozen-framework digest.
  - Every run has a fresh workspace.
  - Hidden evaluator materials remain inaccessible.
  - No-op responses cannot pass.
  - Timeout kills descendant processes.
  - Budget denial occurs before an unauthorized call.
  - Missing telemetry remains null with a reason.
  - Reports cannot be silently overwritten.
  - Failed reports are preserved.
  - Resume skips or safely recognizes terminal rows.
  - Cold reconstruction reproduces the material result state.
  - Dry-run artifacts are visibly marked non-empirical.

  Add and run focused tests for these invariants.

  Do not proceed to paid execution if the dry run is structurally invalid.

  Phase 5 — live OpenRouter execution

  Only begin after Phase 4 passes.

  Credential handling:

  - `OPENROUTER_API_KEY` may be unset in the shell.
  - The repository `.env` currently contains a non-empty `OPENROUTER_API_KEY`.
  - Load `.env` without printing, logging, hashing, serializing, or otherwise exposing the secret.
  - Do not add the key to subprocess command lines.
  - Never stage `.env` or include it in benchmark artifacts.
  - Verify only whether the credential is present and usable.

  Locked provider/model:

    Provider: OpenRouter
    Requested model: deepseek/deepseek-v4-flash-0731

  Before spending money:

  1. Verify that the exact requested model is currently available.
  2. Verify the returned model identity can be observed.
  3. Verify pricing and route behavior.
  4. Perform the smallest safe preflight allowed by the budget contract.
  5. Confirm the preflight does not mutate benchmark subjects or consume a preregistered row.

  If the exact model is unavailable:

  - Do not silently substitute another model.
  - Do not use `deepseek/deepseek-chat`.
  - Do not use a fallback route.
  - Record a precise provider/model-availability failure.
  - Preserve all completed Phase 0–4 artifacts.
  - Stop paid execution.

  Budget rules:

  - Maximum total tokens: 1,000,000
  - Maximum paid model spend: USD 0.50
  - Maximum planned measurements: 27
  - Recommended new-call guard: 950,000 tokens and USD 0.48
  - Enforce per-run ceilings before every call.
  - Use actual provider telemetry when supplied.
  - Never infer absent cost or token telemetry.
  - Stop new calls when a ceiling is reached.
  - Preserve all completed and failed rows.

  Execution rules:

  - Execute the preregistered order.
  - Use identical streaming, temperature, output-token, retry, timeout, and translation settings across comparable arms.
  - Preserve every request/response artifact permitted by the security policy.
  - Redact credentials and authorization headers.
  - Never overwrite failed reports.
  - If the returned model differs from the locked model, mark ROUTE_DRIFT and do not score the row.
  - If the provider fails, record PROVIDER_ERROR rather than inventing a model result.

  If network access is sandbox-blocked, request the required network approval through the normal tool mechanism. Do not falsely classify sandboxed network denial as a missing benchmark
  implementation.

  Phase 6 — evaluation

  For every live row:

  - Run the exterior evaluator.
  - Verify evaluator infrastructure before interpreting task failure.
  - Bind the verdict to the source snapshot, task digest, output artifact, and trajectory.
  - Distinguish agent failure from evaluator failure.
  - Grade tutor and research outputs without exposing preset identity to the grader when practicable.
  - Compute all required raw and derived KPIs from the plan.
  - Do not convert missing telemetry into zero.
  - Record uncertainty and small-sample limitations.
  - Do not claim an official SWE-bench leaderboard score from this 27-row experiment.

  Phase 7 — product decision

  After all possible rows are terminal:

  - Rank coding presets by resolution first.
  - Use regression safety as the next criterion.
  - Then compare tokens, cost, latency, and operational failure rate.
  - Compare each general V2 preset against its paired V1.
  - Identify the strongest coding default candidate.
  - Identify one candidate per general product class.
  - Separate preset shortcomings from framework gaps.
  - Make projection caveats explicit.
  - Do not claim milestone acceptance solely from benchmark results.

  Verification commands

  Run the focused benchmark tests first, followed by relevant repository checks.

  At minimum run:

    python3 -m unittest discover -s test/kernel -t .
    python3 -m unittest discover -s test/contracts -t .
    python3 -m unittest discover -s test/agency -t .
    python3 -m unittest discover -s test/packs -t .
    python3 tools/linters/check_boundaries.py
    python3 tools/linters/check_tcb_budget.py
    python3 tools/linters/check_domain_blindness.py
    python3 tools/linters/check_isolation_policy.py
    python3 tools/linters/scan_secrets.py

  Also run:

  - Every new benchmark-specific test
  - The 27-row deterministic dry run
  - Type checking or linting applicable to modified files
  - The full Python suite if practical and if it does not require provider keys

  Before hermetic tests, ensure provider keys are not exported into the test process.

  If a test unexpectedly mutates tracked evidence or databases, report the exact mutation and command. Do not erase user-owned changes.

  Required working behavior

  Do not produce another response like:

    “The benchmark directories and orchestrator are absent, so execution stopped.”

  Instead:

  - Create the missing benchmark directories.
  - Implement the missing orchestrator.
  - Implement the missing presets.
  - Create and validate fixtures.
  - Run all 27 dry-run rows.
  - Continue until reaching an actual external or frozen-framework blocker.

  You may stop before live calls only if:

  - The deterministic dry run is invalid and you have exhausted permitted solution-layer fixes.
  - The exact locked model is unavailable.
  - Provider authentication fails despite safely loading `.env`.
  - Network access is denied after requesting the appropriate permission.
  - The global cost/token guard would be violated.
  - A required capability demonstrably requires changing a frozen framework path.

  Even when one of those occurs, preserve completed artifacts and give a precise evidence-backed terminal classification.

  Progress communication

  While working:

  - Give concise progress updates after each phase.
  - State exact files created or changed.
  - State exact tests run and results.
  - State the frozen framework digest after every batch.
  - Warn immediately if a frozen file changes.
  - Do not ask for clarification when the plan already answers the question.
  - Do not stop after discovery; proceed with implementation.

  Final response format

  Lead with the actual outcome.

  Include:

  1. Whether Phases 0–4 completed.
  2. Whether all eleven presets compose.
  3. Whether the dry-run matrix contains exactly 27 terminal rows.
  4. Whether live execution occurred.
  5. Live row counts by terminal classification.
  6. Exact token and cost totals when provided by the provider.
  7. Framework digest before and after.
  8. Tests and linters run, with pass/fail counts.
  9. Important created or modified files.
  10. Any genuine framework gaps.
  11. Any provider, model, evaluator, or dataset blockers.
  12. Confirmation that unrelated user files and changes were preserved.

  Do not claim completion unless the evidence supports it.
  Do not call dry-run results empirical.
  Do not expose credentials.
  Do not confuse missing deliverables with blockers.

  Begin now by reading the required documents and inspecting the benchmark surfaces. Then implement Phase 0 and continue through the remaining phases without stopping merely because
  benchmark infrastructure must be created.
