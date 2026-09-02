Below is a self-contained implementation prompt designed for a capable coding agent. It prioritizes core backend implementation, targeted falsifiers, and runtime
  correctness. It explicitly forbids Git commands and avoids exhaustive documentation or unrelated testing.

  You are implementing the remaining core backend fixes for Vanguard / AETHER, a Python-first autonomous coding harness designed for long-running software-engineering tasks.

  Your objective is to make the existing Coding Max product path capable of:

  - complex bug fixes;
  - multi-file features and refactors;
  - greenfield projects;
  - migrations;
  - large-repository investigation;
  - read-only review and explanation;
  - long sessions with compaction and fresh-process continuation;
  - truthful verification and fail-closed completion.

  This is a convergence and completion task. Do not create a second architecture, second runtime, second event loop, or second tool-execution path.

  ===============================================================================
  1. NON-NEGOTIABLE OPERATING RULES
  ===============================================================================

  1. Do not run any Git command.

  Forbidden examples include:

  - git status
  - git diff
  - git log
  - git show
  - git checkout
  - git restore
  - git reset
  - git add
  - git commit
  - git stash
  - git clean
  - git branch

  Use filesystem inspection, repository-intelligence tools, linters, and tests
  without invoking Git.

  2. Do not create new Markdown reports, plans, ADRs, summaries, or scratch files.

  3. Focus on production code and focused tests.

  Only update existing canonical documentation if a durable public contract,
  architecture, configuration, or user-visible behavior changes. Do not perform
  broad documentation cleanup.

  4. Do not run exhaustive test suites during normal iteration.

  Run:

  - the closest unit tests;
  - the directly affected contract tests;
  - new falsifiers for the behavior being changed;
  - architecture and TCB checks when relevant.

  Do not repeatedly run the full repository suite. Run broader verification only
  after the implementation is coherent and the focused tests pass.

  5. Preserve existing unrelated changes.

  The workspace may already contain frontend and generated-file modifications.
  Do not overwrite, revert, reformat, or “clean up” unrelated files.

  6. Use apply_patch for source edits.

  7. Remain within the existing hexagonal dependency lattice:

      domain <- ports <- kernel <- agency <- runtime -> adapters
                                        |
                                        -> apps as a runtime client

  More precisely:

  - domain: pure value objects, wire contracts, canonicalization and reducers;
  - ports: generic protocols with no concrete backend dependencies;
  - kernel: capability, budget and dispatch authority;
  - agency: episode execution, context compilation and recursive behavior;
  - runtime: composition, lifecycle, persistence and orchestration;
  - adapters: concrete model, sandbox, evaluator, store and index providers;
  - apps/facades: thin clients of runtime/application services.

  Adapters must not import kernel or agency.

  Coding-specific concepts must not enter the domain-blind kernel.

  8. Maintain the kernel TCB budget.

  The production kernel must remain at or below 1438 logical lines. Avoid modifying
  the kernel unless the required invariant genuinely belongs to trusted dispatch
  authority.

  9. All effects remain mediated.

  Models, commands, patches, tests, child agents, evaluators, memory and index
  access must use the existing ports and runtime capability/budget path. Application
  or pack code must not directly execute host subprocesses or provider HTTP calls.

  10. Keep one canonical runtime and ledger.

  The supported Coding Max path must remain:

      CodingMaxFacade / CLI / API
          -> ApplicationService
          -> runtime composition
          -> HarnessSession
          -> EpisodeEngine
          -> Kernel-mediated effects
          -> adapters

  Do not make ForgeEngine, ChimeraEngine or a new coordinator into an alternative
  production runtime.

  ===============================================================================
  2. AUTHORITATIVE READING ORDER
  ===============================================================================

  Before editing, read these files in order:

  1. README.md
  2. AGENTS.md
  3. dev_context_logs/context_summary.md
  4. docs/execution/active.md
  5. docs/execution/milestones.md
  6. docs/execution/backlog.md
  7. docs/SPEC.md
  8. docs/decisions.md
  9. docs/backend/architecture/agency.md
  10. docs/backend/architecture/runtime-execution.md
  11. docs/backend/reference/ports.md
  12. the run/resume product guide and runtime workflow documentation

  Use the repository navigation protocol:

      python3 tools/docs_rag_v0.py \
        "coding max runtime completion resume context verification" \
        --budget 8000

  For every production file you intend to modify, reverse-route its documentation
  obligations:

      python3 tools/docs_rag_v0.py --file <path>

  Use LDA if healthy:

      .venv/bin/lda doctor --json
      .venv/bin/lda context \
        "coding max runtime completion resume context verification" \
        --budget 8000 --json

  An index is only a routing aid. Current canonical documents, source, tests and
  runtime evidence override generated indexes.

  ===============================================================================
  3. PRIMARY IMPLEMENTATION TARGETS
  ===============================================================================

  Inspect these areas before choosing exact edit locations:

  Runtime:

  - vanguard/packages/runtime/session.py
  - vanguard/packages/runtime/app_service.py
  - vanguard/packages/runtime/compose.py
  - vanguard/packages/runtime/wiring.py
  - vanguard/packages/runtime/task_state.py
  - vanguard/packages/runtime/prompt_assembler.py
  - vanguard/packages/runtime/checkpoints.py
  - vanguard/packages/runtime/trajectory.py
  - vanguard/packages/runtime/evidence_capture.py
  - vanguard/packages/runtime/evaluator_gateway.py
  - vanguard/packages/runtime/ledger_emitter.py

  Agency:

  - vanguard/packages/agency/episode/engine.py
  - vanguard/packages/agency/episode/state.py
  - vanguard/packages/agency/episode/admission_gate.py
  - vanguard/packages/agency/context/compiler.py
  - vanguard/packages/agency/context/compaction.py
  - vanguard/packages/agency/context/layers.py
  - vanguard/packages/agency/context/context_packet.py
  - vanguard/packages/agency/manifests/

  Ports and adapters:

  - vanguard/packages/ports/index.py
  - vanguard/packages/ports/spi.py
  - vanguard/packages/ports/model.py
  - vanguard/packages/ports/environment.py
  - vanguard/packages/ports/event_store.py
  - vanguard/packages/adapters/stores/repo_index.py
  - relevant model and sandbox adapters

  Coding product and packs:

  - the CodingMaxFacade implementation;
  - packs/code-default/
  - public Coding Max manifests:
    - vg-code-fast
    - vg-code-balanced
    - vg-code-max
  - experimental manifests and implementations:
    - vg-code-max-v3luna
    - vg-code-chimera
    - vg-1-forge-v2
    - ForgeEngine
    - ChimeraEngine

  Benchmarks and focused falsifiers:

  - benchmarks/m8_heldout/runner.py
  - current Coding Max benchmark runners
  - test/runtime/
  - test/agency/
  - test/contracts/
  - test/falsifiers/

  ===============================================================================
  4. IMPLEMENTATION STRATEGY
  ===============================================================================

  Implement the work in the following dependency order.

  Do not begin repository-scale qualification before the core runtime contracts are
  correct.

  -------------------------------------------------------------------------------
  PHASE A — CANONICAL CODING MAX CONVERGENCE
  -------------------------------------------------------------------------------

  Goal:

  Make fast, balanced and max data-selected configurations of the same canonical
  runtime rather than divergent product implementations.

  A1. Select one public preset lineage.

  The public facade currently selects:

  - vg-code-fast
  - vg-code-balanced
  - vg-code-max

  Later experimental success uses manifests such as:

  - vg-code-max-v3luna
  - vg-code-chimera
  - vg-1-forge-v2

  Reconcile useful configuration and behavior into the public fast, balanced and
  max manifests.

  Do not redirect the public product to a separate ForgeEngine or ChimeraEngine.

  A2. Preserve a thin facade.

  CodingMaxFacade may:

  - validate product-level input;
  - select fast, balanced or max;
  - construct application-service requests;
  - normalize application-service results.

  It must not:

  - implement a turn loop;
  - dispatch tools;
  - call model providers;
  - apply patches;
  - execute tests;
  - own a separate ledger;
  - decide completion independently;
  - implement its own resume semantics.

  A3. Consolidate completion activation.

  The runtime already has capability-derived logic similar to:

      admission_required(harness)

  Use one generic decision derived from compiled capabilities or declared
  components.

  Remove semantic dependence on preset-name sets such as:

      ADMISSION_GATED_HARNESSES = {...}

  Do not maintain separate lists in HarnessSession and ApplicationService.

  The invariant must be:

      any composition capable of mutating a workspace or claiming coding
      completion is admission-gated automatically

  A new write-capable manifest must fail closed even if its name has never appeared
  in source code.

  A4. Bind completion policy declaratively.

  ICompletionPolicy must be selected through the composition contract, declared
  component, pack binding or capability contract.

  Do not select richer coding completion behavior using a hard-coded manifest-name
  allowlist.

  A5. Reconcile Forge and Chimera.

  Inspect ForgeEngine and ChimeraEngine for useful mechanisms such as:

  - prompt structure;
  - recovery behavior;
  - patch parsing;
  - context prioritization;
  - retry classification;
  - verification feedback.

  Port only useful, testable mechanisms into:

  - EpisodeEngine;
  - ContextCompiler;
  - PromptAssembler;
  - completion policy;
  - runtime adapters;
  - declarative manifests.

  Keep ForgeEngine and ChimeraEngine outside the supported product path. Do not
  delete experimental code merely to satisfy this task unless removal is necessary
  to prevent production dispatch through it.

  Acceptance:

  - fast, balanced and max reach the same ApplicationService, HarnessSession and
    EpisodeEngine implementation;
  - capability-derived admission applies to every write-capable composition;
  - the completion policy is not selected by product name;
  - no supported app or experimental engine directly performs effects;
  - all tool names and selectors resolve through one compiled composition contract.

  -------------------------------------------------------------------------------
  PHASE B — TRUTHFUL TASK-AWARE COMPLETION
  -------------------------------------------------------------------------------

  Goal:

  Completion must be based on fresh, applicable, postimage-bound evidence. It must
  never be inferred from model prose, command success alone, or fabricated counts.

  B1. Remove fabricated test counts.

  Locate runtime logic equivalent to:

      executed_test_count = 1

  for a successful test-like command.

  Replace it with typed observation derived from the actual mediated command
  result.

  Never convert exit code zero into “one test executed.”

  B2. Introduce or complete a typed verification receipt.

  Use the appropriate domain/runtime boundary. Do not place coding-specific parsing
  inside the kernel.

  A verification receipt should carry, as applicable:

  - command or verifier identity;
  - command digest;
  - framework/parser identity;
  - exit code;
  - collected count;
  - executed count;
  - passed count;
  - failed count;
  - skipped count;
  - parser confidence or explicit unknown fields;
  - stdout/stderr or result digest;
  - task identity/digest;
  - repository preimage or relevant baseline digest;
  - current postimage digest;
  - changed-file digest or change-surface digest;
  - event/trajectory identity;
  - observation timestamp or monotonic occurrence identity.

  Unknown values must remain explicitly unknown. Do not invent zero or one.

  B3. Parse verification evidence conservatively.

  Support only formats already used by repository workflows. Keep parsing in a
  focused runtime, pack or adapter module.

  Examples may include:

  - unittest;
  - pytest;
  - project-defined verifier output;
  - structured evaluator results.

  Parser rules must be deterministic and covered by small focused tests.

  If a task requires behavioral verification and the output cannot establish that
  tests were collected and executed, fail closed.

  B4. Bind verification to the current postimage.

  A verification receipt becomes stale when:

  - a patch is applied after verification;
  - a relevant file changes;
  - the task identity changes;
  - the change-surface digest changes;
  - the workspace postimage no longer matches;
  - the verification plan changes materially.

  Completion must not reuse stale evidence.

  B5. Add task-aware completion modes.

  Use an explicit task kind or completion-policy decision for:

  1. Bugfix

  Required:

  - a reproducer when feasible;
  - implicated source inspection;
  - patch application;
  - fresh affected regression verification;
  - postimage binding.

  2. Feature or refactor

  Required:

  - declared change surface;
  - public interface and caller checks;
  - configuration/serialization compatibility where applicable;
  - fresh targeted verification.

  3. Migration

  Required:

  - forward behavior;
  - backward compatibility or an explicit breaking-change contract;
  - schema/data transition checks where applicable;
  - rollback or recovery reasoning;
  - consumer verification.

  4. Greenfield

  Required:

  - recorded empty/scaffold baseline;
  - requested files actually created;
  - syntax/build/type verification;
  - at least one behavioral smoke or contract test.

  5. Repository without tests

  Required:

  - create or invoke the smallest applicable executable acceptance harness;
  - do not accept syntax-only success for behavioral work;
  - preserve explicit evidence when only partial verification is possible.

  6. Read-only review or explanation

  Required:

  - no fabricated patch;
  - no mutation requirement;
  - resolved source/symbol/test evidence for material conclusions;
  - explicit checklist coverage of the user’s request.

  B6. Detect incomplete change surfaces.

  Before admitting completion, compare:

  - files proposed or implicated;
  - files read;
  - files modified;
  - callers and dependencies;
  - associated tests;
  - files verified after the final edit.

  Fail closed on material omissions such as:

  - changed public API without caller inspection;
  - configuration schema changed without loader/serializer inspection;
  - implementation changed without affected tests;
  - multi-file request where only one required file was handled;
  - generated or migration surfaces silently omitted.

  B7. Make rejection recoverable.

  When completion is rejected:

  - emit a typed reason;
  - show the reason to the model;
  - preserve the evidence already gathered;
  - propose the smallest next admissible action;
  - consume bounded retry/no-progress budget.

  Repeated completion attempts with unchanged evidence must become typed
  no-progress. They must not create an infinite loop.

  Acceptance:

  - zero collected tests never admit behavioral completion;
  - a successful but unparsable command does not invent verification;
  - a post-verification edit invalidates the previous receipt;
  - new write-capable manifests cannot bypass admission;
  - each supported task kind has explicit completion behavior;
  - read-only tasks can finish without a patch;
  - completion rejection produces actionable model-visible feedback.

  -------------------------------------------------------------------------------
  PHASE C — DURABLE LONG-SESSION CONTINUATION
  -------------------------------------------------------------------------------

  Goal:

  A resumed task must continue the original bounded run. Resume must not behave like
  a new one-turn benchmark invocation.

  C1. Repair ApplicationService.resume().

  The current behavior effectively derives a new maximum turn count from prior
  proposal count plus one and runs non-interactively.

  Replace this with restoration of the original run contract.

  Persist and restore:

  - task identity and request;
  - harness/composition identity;
  - profile;
  - model route policy;
  - completion-policy identity;
  - approval mode and approval authority;
  - original total turn ceiling;
  - turns already spent;
  - additive budget ceiling and consumption;
  - structural ceilings;
  - current phase;
  - task-state digest;
  - context/compaction state;
  - next admissible action;
  - repository/index snapshot identity;
  - latest verification and its freshness;
  - settled effect identities.

  Resume must calculate remaining capacity from the original ceiling. It must not
  grant a fresh budget or collapse the run to one additional turn.

  C2. Preserve approval semantics.

  A run that required interactive or signed approval before suspension must retain
  that requirement after resume.

  Do not silently force:

      interactive = False

  for ordinary product resume.

  Benchmark and automated modes may use explicit non-interactive policies, but that
  must be part of the original composition identity and authorization contract.

  C3. Produce durable semantic task events.

  CodingTaskState already models richer state. Ensure production emits durable
  events for material state transitions, including:

  - task classified;
  - plan created or revised;
  - TODO created, started, blocked, completed or reopened;
  - repository discovery;
  - implicated symbol/file;
  - hypothesis;
  - dead end;
  - change surface;
  - verification plan;
  - verification result;
  - completion rejection;
  - recovery action;
  - route or strategy change;
  - next action;
  - budget observation;
  - context compaction;
  - checkpoint;
  - suspension;
  - resume.

  Do not persist arbitrary hidden model reasoning. Persist operational state and
  evidence needed for deterministic continuation.

  C4. Reconcile effects before model re-entry.

  On restart:

  1. reconstruct ledger state;
  2. validate event ordering and digests;
  3. identify in-flight effects;
  4. reconcile their durable adapter/result state;
  5. mark settled effects;
  6. restore task and context state;
  7. determine the next admissible action;
  8. only then call the model.

  Never replay a settled:

  - patch;
  - command;
  - verification;
  - child spawn;
  - evaluator request;
  - approval;
  - provider call whose result was durably accepted.

  C5. Improve checkpoint and compaction triggers.

  Trigger checkpoints at meaningful boundaries such as:

  - context pressure;
  - approved patch application;
  - verification completion;
  - phase transition;
  - planned suspension;
  - bounded interval after durable progress.

  A checkpoint is an acceleration artifact. The ledger remains authoritative.

  Compaction must retain:

  - user goal;
  - constraints;
  - task kind;
  - current plan;
  - open TODOs;
  - discoveries;
  - modified files;
  - latest failure;
  - latest fresh verification;
  - dead ends;
  - settled effects;
  - next action;
  - remaining budgets.

  C6. Validate long-session parity.

  Create focused scripted tests demonstrating:

  - at least 40 logical turns;
  - at least three fresh-process restarts;
  - one interruption after patch approval;
  - one interruption after verification;
  - no duplicate settled effects;
  - same final postimage as uninterrupted execution;
  - equivalent final evidence under declared nondeterminism;
  - budget use never exceeds original ceilings.

  Acceptance:

  - resume preserves the original run identity;
  - resume provides more than one turn when budget remains;
  - approval behavior remains correct;
  - no settled effect is duplicated;
  - long-session state survives compaction and cold restart.

  -------------------------------------------------------------------------------
  PHASE D — PROGRESSIVE REPOSITORY CONTEXT
  -------------------------------------------------------------------------------

  Goal:

  Give the agent useful large-repository context without placing a flat repository
  dump in a frozen prompt prefix.

  D1. Put ContextPacket on the product path.

  Construct a real ContextPacket through the generic IndexPort.

  It should include:

  - task identity and query;
  - repository/index snapshot identity;
  - provider and version;
  - selected files;
  - selected symbols;
  - callers and dependencies;
  - related tests;
  - token estimate;
  - omitted candidates or omission summary;
  - repository epoch;
  - packet digest.

  D2. Use IndexPort.repo_map().

  Do not inject an unbounded flat file/symbol list into the stable environment
  prefix.

  The prefix should contain only stable, compact information:

  - task;
  - immutable rules;
  - tool contract;
  - concise repository orientation;
  - current composition constraints.

  Dynamic repository knowledge belongs in an evictable/refreshed context layer.

  D3. Implement progressive retrieval.

  Use stages resembling:

  1. Orientation

  - project structure;
  - language/build systems;
  - canonical documents;
  - likely subsystem.

  2. Investigation

  - implicated symbols;
  - primary files;
  - definitions and references;
  - closest falsifiers.

  3. Change closure

  - callers;
  - imports;
  - implementations of modified protocols;
  - configuration and serialization consumers;
  - associated tests.

  4. Post-edit refresh

  - changed symbols;
  - changed repository epoch;
  - newly affected callers/tests.

  5. Verification context

  - latest command;
  - latest result;
  - remaining failures;
  - stale evidence;
  - next verification action.

  D4. Reserve context for execution and recovery.

  Do not spend the complete model context window on initial retrieval.

  Reserve enough capacity for:

  - at least one edit;
  - verification output;
  - failure analysis;
  - one recovery cycle;
  - final completion evidence.

  Use conservative configurable budgets rather than hard-coding assumptions about
  one provider’s maximum context.

  D5. Ensure epoch and path safety.

  Reject or refresh index facts when:

  - repository epoch changed;
  - a path no longer resolves;
  - the index is empty;
  - index health is false;
  - snapshot identity does not match;
  - symbol locations are stale.

  D6. Deterministic fallback.

  When no healthy index is available, fall back to bounded source navigation:

  - repository file enumeration;
  - targeted text search;
  - nearest canonical owner;
  - direct source and test inspection.

  LDA is optional and must remain behind IndexPort. The production harness must not
  depend on LDA-specific types or commands.

  D7. Use topology for change closure, not authority.

  Call/dependency/test relationships help choose what to inspect and verify. They
  must not override current source or executable results.

  Acceptance:

  - public max configuration declares an index provider or explicit fallback;
  - ContextPacket is constructed in production;
  - initial context is bounded;
  - omissions and snapshot identity are visible;
  - post-edit retrieval refreshes against a new epoch;
  - stale or unavailable indexes fall back deterministically;
  - affected callers/tests contribute to completion admission.

  -------------------------------------------------------------------------------
  PHASE E — EMPIRICAL RUNNER INTEGRITY
  -------------------------------------------------------------------------------

  Goal:

  Make the held-out runner exercise a real bounded Coding Max attempt and produce
  an exact evidence bundle. Do not perform expensive live qualification unless
  explicitly authorized.

  E1. Repair RuntimeTaskExecutor.

  The runner must:

  - select a write-capable, admission-gated canonical composition;
  - execute one bounded multi-turn agent attempt;
  - distinguish an agent attempt from its internal turns;
  - retrieve the actual patch from a durable runtime artifact;
  - retain run, event and trajectory identity;
  - invoke an exterior evaluator;
  - record explicit missingness for unavailable usage/cost fields.

  Do not use:

  - vg-code-default with one non-interactive turn;
  - model prose as a patch;
  - an empty patch as success;
  - the model’s own test claim as an exterior verdict.

  E2. Bind identities.

  Each result row or evidence bundle must identify:

  - repository subject/base revision;
  - task ID;
  - task content digest;
  - workspace preimage;
  - workspace postimage;
  - patch digest;
  - composition and manifest digest;
  - model route;
  - attempt number;
  - turn count;
  - event range or root digest;
  - trajectory digest;
  - verification receipt digest;
  - exterior evaluator identity;
  - exterior verdict digest;
  - usage, cost and latency or explicit missingness.

  E3. Preserve single-attempt semantics.

  A bounded multi-turn episode is one attempt.

  Do not count each model turn as an independent benchmark attempt.

  Retries that create a new attempt must be explicit, separately identified and
  excluded when the protocol requires a single attempt.

  E4. Replace the invalid canary with a successor.

  Do not rewrite historical frozen artifacts.

  Create or modify the supported successor manifest so that every row’s:

  - title;
  - payload;
  - task statement;
  - workspace;
  - oracle;
  - split;
  - base revision;
  - digest

  refers to the same unique subject.

  Reject:

  - duplicate tasks;
  - repeated workspaces under unrelated titles;
  - contaminated fixtures;
  - mutable baselines;
  - missing or self-inconsistent digests.

  E5. Add focused negative falsifiers.

  Cover:

  - no patch;
  - prose-only answer;
  - patch does not apply;
  - missing trajectory;
  - mismatched subject;
  - duplicate task;
  - zero tests;
  - stale verification;
  - unavailable evaluator;
  - timeout;
  - budget exhaustion;
  - second agent attempt;
  - postimage mismatch.

  E6. Do not make unsupported claims.

  Hermetic or cassette validation may establish structural correctness.

  It does not establish:

  - official SWE-bench performance;
  - SOTA performance;
  - real-provider quality;
  - M-8 empirical lift;
  - release readiness.

  Leave live provider records as NOT_RUN unless execution is explicitly authorized.

  ===============================================================================
  5. CONTRACTS TO PRESERVE
  ===============================================================================

  Capability contract:

  - capabilities attenuate monotonically;
  - a child never gains authority absent from its parent;
  - budgets cannot increase during delegation or resume;
  - write/test/evaluator effects remain kernel-mediated.

  Budget contract:

  - additive budgets restore as ceiling minus durable consumption;
  - structural ceilings are never treated as additive balances;
  - resume cannot mint new turns, tokens, calls, writes, tests or children;
  - rejected completion consumes bounded progress/retry capacity.

  Completion contract:

      completion =
          task_requirements_satisfied
          AND patch_or_read_only_contract_satisfied
          AND change_surface_closed
          AND verification_is_applicable
          AND verification_is_fresh
          AND verification_matches_current_postimage
          AND no_required_evidence_is_unknown
          AND budgets_and_authority_are_valid

  Do not reduce this to a boolean command result.

  Context contract:

  - stable prefix is compact and immutable;
  - dynamic repository information is refreshable and evictable;
  - every index packet has snapshot identity and omissions;
  - compaction preserves operational state;
  - source and tests remain authoritative.

  Resume contract:

      resume(original_run_id) -> continuation of original bounded execution

  It must not mean:

      resume -> create a loosely related one-turn run

  Evidence contract:

  - every material artifact is content-addressed;
  - identities link task, patch, postimage, verification, trajectory and verdict;
  - missing data remains typed missingness;
  - external evaluation remains separate from local completion admission.

  Product-boundary contract:

  - apps and facades request work;
  - runtime owns composition and lifecycle;
  - agency owns the recursive turn protocol;
  - kernel owns authority and effect admission;
  - adapters perform concrete external operations;
  - packs supply domain-specific policy without bypassing runtime.

  ===============================================================================
  6. MODULE-DESIGN GUIDANCE
  ===============================================================================

  Prefer small focused components over enlarging session.py indefinitely.

  Reasonable module responsibilities include:

  - verification_observer.py
    Parse mediated command outcomes into typed verification observations.

  - completion_evidence.py
    Determine freshness, postimage binding and evidence applicability.

  - resume_contract.py
    Represent persisted continuation identity and remaining budgets.

  - task_events.py
    Emit and fold operational coding-task state transitions.

  - repository_context.py
    Build ContextPacket and progressive context stages through IndexPort.

  - change_surface.py
    Track implicated, inspected, modified and verified files/interfaces.

  Use existing modules when they already own these concepts. Do not create modules
  merely to match these suggested names.

  New protocols belong in ports only when multiple implementations or a true
  hexagonal boundary require them.

  New pure value objects belong in domain only when they are coding-neutral and use
  stdlib-only dependencies.

  Coding-specific verification policy should live in runtime or the code pack, not
  kernel or generic domain.

  Avoid:

  - global mutable state;
  - hidden singleton coordinators;
  - direct adapter construction outside composition;
  - name-based policy routing;
  - broad dictionaries where a stable typed record already exists;
  - storing non-serializable runtime objects in durable state;
  - swallowing parser or reconstruction failures;
  - “best effort” completion that silently bypasses missing evidence.

  ===============================================================================
  7. TARGETED TEST STRATEGY
  ===============================================================================

  Testing is required, but keep it proportional.

  For each change:

  1. Add or update the closest unit test.
  2. Add one negative test for the primary fail-closed invariant.
  3. Add one runtime-boundary or contract test proving the mechanism is integrated.
  4. Run only that focused selection during iteration.

  Priority falsifiers:

  - a newly named write-capable manifest is admission-gated;
  - zero collected tests are rejected;
  - successful unparsable output does not invent a count;
  - a post-verification patch invalidates verification;
  - read-only explanation can complete without mutation;
  - resume retains more than one remaining turn;
  - resume preserves approval semantics;
  - settled patch and test effects are not duplicated;
  - ContextPacket is used in production;
  - stale repository epoch triggers refresh/fallback;
  - incomplete multi-file change surface is rejected;
  - the empirical runner cannot pass without patch plus exterior verdict.

  Useful commands include:

      .venv/bin/python -m unittest <specific.module> -v

      .venv/bin/python -m unittest \
        test.runtime.test_<target> \
        test.agency.test_<target> \
        test.contracts.test_<target> -v

  Architecture checks when touching production boundaries:

      python3 tools/linters/check_boundaries.py
      python3 tools/linters/check_domain_blindness.py
      python3 tools/linters/check_isolation_policy.py

  When touching kernel:

      python3 tools/linters/check_tcb_budget.py
      python3 -m unittest discover -s test/kernel -t .

  Do not suppress failures with shell constructs such as “|| true”.

  Do not run live provider benchmarks without explicit authorization.

  Known repository-wide failures may currently include:

  - path-hygiene failures in retained benchmark artifacts;
  - one cold-index MCP fallback contract failure;
  - two UDS subprocess lifecycle timeouts;
  - one frontend client-core Wave-5 test failure;
  - two unresolved R13 references in historical Chimera review documents.

  Do not misrepresent these as introduced by your work. Also do not use them to
  ignore failures caused by your implementation.

  ===============================================================================
  8. IMPLEMENTATION CHECKPOINTS
  ===============================================================================

  Checkpoint 1 — canonical path

  Demonstrate:

  - fast/balanced/max use ApplicationService and HarnessSession;
  - no manifest-name admission allowlist remains;
  - write capability automatically enables completion admission;
  - no production Forge/Chimera loop is invoked.

  Checkpoint 2 — truthful completion

  Demonstrate:

  - actual verification counts or explicit unknown values;
  - zero-test rejection;
  - stale-receipt rejection;
  - postimage binding;
  - task-aware completion modes;
  - actionable rejection feedback.

  Checkpoint 3 — long-session continuation

  Demonstrate:

  - original ceiling and consumed budget restoration;
  - normal approval behavior after resume;
  - semantic task-state reconstruction;
  - no settled effect replay;
  - scripted 40+ turn run with repeated cold restarts.

  Checkpoint 4 — progressive context

  Demonstrate:

  - production ContextPacket creation;
  - bounded repo_map use;
  - staged retrieval;
  - snapshot/epoch refresh;
  - deterministic no-index fallback;
  - affected-test/change-surface integration.

  Checkpoint 5 — runner integrity

  Demonstrate:

  - one bounded agent attempt;
  - durable patch artifact;
  - event and trajectory identity;
  - exterior verdict;
  - exact subject binding;
  - negative falsifiers;
  - no live/SOTA claim.

  ===============================================================================
  9. DEFINITION OF DONE
  ===============================================================================

  The core implementation is complete only when all of the following are true:

  - One canonical production runtime serves all Coding Max presets.
  - Forge and Chimera are not parallel supported execution authorities.
  - Admission and completion policy are capability/component-derived.
  - Verification counts are observed, never fabricated.
  - Zero tests, stale evidence and incomplete change surfaces fail closed.
  - Bugfix, feature, migration, greenfield, no-tests and read-only tasks have
    explicit completion contracts.
  - Resume preserves the original run, approval mode, budgets and policies.
  - A 40+ turn task survives at least three cold restarts.
  - No settled effect is duplicated.
  - Operational task state survives compaction and restart.
  - ContextPacket and IndexPort are used on the product path.
  - Repository context is progressive, bounded, snapshot-bound and omission-aware.
  - Index failure has a deterministic source-search fallback.
  - The empirical runner returns an actual durable patch and exterior verdict.
  - Benchmark evidence binds task, subject, patch, postimage, trajectory,
    verification and evaluator identities.
  - Focused unit, contract and falsifier tests pass.
  - Boundary and TCB invariants remain satisfied.
  - No Git command was executed.
  - No unsupported SOTA, SWE-bench, M-8 or release claim was introduced.

  ===============================================================================
  10. HANDOFF FORMAT
  ===============================================================================

  When finished, report:

  1. Core behavior implemented.
  2. Production files changed.
  3. Focused tests added or updated.
  4. Commands actually executed.
  5. Exact pass/fail/skip results.
  6. Remaining known blockers.
  7. Any durable contract that required updating an existing canonical document.
  8. Explicit confirmation that no Git command was run.
  9. Explicit confirmation that no live provider or official benchmark claim was
     made.

  Do not claim the backend, milestone, sprint or release complete unless every
  applicable definition-of-done predicate has executable evidence.

  The canonical sprint details and acceptance conditions referenced by this prompt are in docs/execution/active.md:176, with stable gates in docs/execution/milestones.md:81
  and package dependencies in docs/execution/backlog.md:159.
