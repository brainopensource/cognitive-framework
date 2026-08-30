---
id: research.coding-harness-llm-response-wrangler
kind: research
status: reference
authority: non-canonical
summary: "Architectural recommendations and research for LLM response wrangling."
topic:
  - coding-harness
---
 # Final architectural recommendation

  Your proposal is feasible, with one refinement:

  Vanguard should not model every processing step as an agent.

  It should model the system as a durable, event-sourced workflow graph containing several kinds of ephemeral execution nodes:

  - deterministic transforms;
  - validators and gates;
  - model inference nodes;
  - tool-effect nodes;
  - agent episodes;
  - joins and selectors;
  - human approval interrupts.

  Agents then become one expensive, nondeterministic node type inside a broader deterministic runtime.

  That gives you the modular composition you want without turning parsing, regex cleanup, test classification, context selection, or deduplication into
  heavyweight agent processes.

  The central rule should be:

  Use code when the transformation is knowable.

  Use a model when fresh judgment is necessary.

  Use an agent episode only when iterative model-tool interaction is necessary.

  Use an independent evaluator when the result must be judged.

  This is the strongest synthesis of Vanguard’s current architecture, RonyGPT’s cascade design, LangGraph’s stateful graph model, Apache Beam’s transform
  model, Temporal’s durable execution semantics, and modern coding-agent research.

  No files were changed, no benchmark was run, and no Git operation was performed during this investigation.

  # 1. Research conclusions

  ## 1.1 LangGraph and LangChain

  The useful LangGraph ideas are:

  - typed graph state;
  - explicit nodes and conditional edges;
  - reducers for merging partial state updates;
  - durable checkpoints;
  - interrupts that can wait indefinitely;
  - replay after process failure;
  - middleware before and after model and tool calls.

  LangChain middleware can modify model requests, validate model responses, handle tool failures, trim or enrich context, change model selection, and route
  execution without rewriting the main agent loop. LangChain agents and middleware, LangGraph reducers, LangGraph interrupts

  Vanguard should adopt these semantics, but should not depend on LangGraph.

  Vanguard already has stronger foundations for:

  - authority attenuation;
  - effect authorization;
  - signed evaluation;
  - content-addressed artifacts;
  - event-sourced replay;
  - provenance;
  - child lineage;
  - budget conservation.

  Adding LangGraph as a runtime dependency would create a second state machine and a second persistence authority.

  Use it as a design reference, not as the execution substrate.

  ## 1.2 Apache Beam

  Beam’s useful abstraction is:

  Input collection
      -> pure or bounded transform
      -> output collection

  Transforms can be chained, branched, joined, filtered, aggregated, and composed into larger transforms. They produce new values instead of mutating their
  inputs. Apache Beam programming model

  That maps cleanly to Vanguard:

  Input artifact
      -> versioned transform
      -> output artifact

  However, Apache Beam itself is not appropriate as a Vanguard dependency.

  Beam is designed for distributed batch and streaming data processing. Vanguard needs:

  - interactive model calls;
  - privileged effects;
  - human interrupts;
  - recursive children;
  - strict capability attenuation;
  - content-addressed evidence;
  - model-specific protocol recovery.

  The correct decision is to borrow Beam’s transform algebra without importing its runner.

  ## 1.3 Temporal and durable execution

  Temporal’s strongest relevant idea is the separation between:

  - deterministic workflow orchestration;
  - fallible activities that perform external work;
  - event history used to replay and recover execution.

  Its event history allows workflows to recover after worker failure, while activities have explicit retry behavior. Temporal event history

  Vanguard already has the right raw materials:

  - SQLite WAL events;
  - deterministic projections;
  - intent-before-effect;
  - idempotency keys;
  - child recovery;
  - artifact digests;
  - reconciliation of incomplete work.

  The missing piece is a general workflow reducer and scheduler above individual episodes.

  The scheduler must remain deterministic.

  Model calls, tools, filesystem changes, subprocesses, web requests, and evaluators must remain activities or effects outside the reducer.

  ## 1.4 OpenAI agent architecture guidance

  Current official OpenAI documentation recommends:

  - Responses API for reasoning and multi-turn tool workflows;
  - typed custom tools;
  - structured outputs instead of prompt-described JSON;
  - preserving response items across turns;
  - intentional context compaction;
  - stable prompt prefixes for caching;
  - bounded programmatic processing for filtering, joining, ranking, deduplication, aggregation, and validation;
  - direct model judgment when intermediate results can change the next decision.

  It also explicitly warns that programmatic tool processing is best for bounded deterministic stages, not every multi-step workflow. Official OpenAI model
  guidance, Responses API reference

  This directly supports your transform-node proposal.

  The OpenAI guidance also says tool-heavy systems should keep detailed tool behavior in tool descriptions, use lean prompts, and choose reasoning effort
  based on measured workload requirements.

  ## 1.5 Coding-agent research

  SWE-agent demonstrates that the agent-computer interface materially affects coding performance. Good repository navigation, compact search results, precise
  editing, and usable test feedback matter as much as prompt wording. SWE-agent paper, SWE-agent ACI notes

  Agentless demonstrates that a simple staged workflow can outperform more complicated autonomous systems:

  localize
  repair
  validate

  Its lesson is not “never use agents.” Its lesson is that deterministic staging and constrained model calls should be the baseline. Agentless paper

  OpenHands uses an event-stream architecture and reports that its newer composable SDK reduced system-attributable failures with low event-sourcing
  overhead. OpenHands SDK paper

  RepoCoder supports iterative retrieval and generation for repository-level code tasks instead of sending the complete repository indiscriminately.
  RepoCoder paper

  Long context alone is not sufficient. Models can underuse relevant information placed in the middle of a large context. Lost in the Middle

  For SWE-Bench Pro and difficult SWE-Bench Verified tasks, Vanguard therefore needs:

  - staged localization;
  - symbol and dependency retrieval;
  - compact evidence bundles;
  - iterative context expansion;
  - artifact-backed working memory;
  - checkpointed conversations;
  - test-driven repair;
  - independent final validation.

  # 2. Current Vanguard audit

  Vanguard already implements most of the difficult safety and durability foundation.

  The relevant existing pieces are:

  - episode loop in vanguard/packages/agency/episode/engine.py;
  - proposal values in vanguard/packages/agency/episode/state.py;
  - model interface in vanguard/packages/ports/model.py;
  - OpenRouter translation in vanguard/packages/adapters/models/openrouter.py;
  - context compilation in vanguard/packages/agency/context/compiler.py;
  - structured compaction in vanguard/packages/agency/context/compaction.py;
  - topology routing in vanguard/packages/runtime/topology.py;
  - topology execution bridge in vanguard/packages/runtime/root.py;
  - child recovery in vanguard/packages/runtime/child_runtime.py;
  - artifact storage in vanguard/packages/runtime/artifacts.py;
  - provenance capture in vanguard/packages/runtime/provenance.py;
  - trajectory comparison in vanguard/packages/runtime/trajectory_reader.py.

  The existing topology implementation is intentionally limited:

  - nodes are agent roles;
  - execution is sequential;
  - edges express role relationships;
  - artifacts move by digest;
  - topology carries no authority;
  - execution becomes ordinary child-agent spawns.

  That is a sound M-7 design, but it is not yet a general workflow engine.

  ## Confirmed architectural gaps

  ### Gap 1: malformed proposals terminate too early

  The episode engine currently treats ProposalMalformed as an instrument error and terminates the episode.

  That is appropriate for an unrecoverable adapter failure, but not for recoverable protocol deviations such as:

  - Markdown patch instead of tool call;
  - incomplete JSON due to truncation;
  - DSML tool markup;
  - valid tool name with malformed arguments;
  - conversational response when a tool is mandatory.

  These should first pass through a bounded recovery policy.

  ### Gap 2: recovery logic lives too close to providers

  The OpenRouter adapter already contains DSML extraction.

  That proves recovery is useful, but provider-specific parsing will become scattered if every dialect adds local heuristics.

  The adapter should decode transport and provider response formats.

  A shared protocol pipeline should classify and normalize the decoded result.

  ### Gap 3: middleware exists as an artifact concept but not as a runtime consumer

  The artifact registry already names middleware as an artifact kind.

  However, the manifest loader’s registered consumers do not expose a general middleware pipeline.

  This is the correct seam to develop.

  ### Gap 4: topology is role-only

  mhf.topology/1 cannot directly express:

  - pure transforms;
  - gates;
  - joins;
  - selectors;
  - deterministic routers;
  - checkpoint nodes;
  - human interrupts.

  Do not overload TopologyRole with these meanings.

  Introduce a versioned generalization after preserving /1 compatibility.

  ### Gap 5: terminal success is too model-directed

  For coding presets, the model should not be able to finish successfully merely by producing conversational text.

  Completion should depend on workflow state:

  patch exists
  and required verification ran
  and verification result is acceptable
  and required files were considered

  The model may propose completion.

  The workflow reducer decides whether completion is admissible.

  ### Gap 6: tool policy is mostly prompt-driven

  The observed NO_PATCH failures show that instructions alone are insufficient.

  Tool policy must be state-dependent and enforced at the request boundary.

  Examples:

  Before inspection:
      allowed = read, search

  After localization:
      allowed = read, search, patch

  After patch:
      allowed = read, search, patch, test

  Before verified completion:
      test evidence required

  ### Gap 7: benchmark attribution is not a first-class projection

  The event log contains enough information to distinguish:

  - provider failure;
  - protocol failure;
  - model behavior failure;
  - harness denial;
  - truncation;
  - invalid dataset baseline;
  - oracle failure;
  - no-progress termination.

  That classification should be a deterministic projection, not prose written after a benchmark.

  # 3. The target architecture

  The recommended architecture has five planes.

  ## Plane 1: immutable artifacts

  Large or semantically important values live in content-addressed storage:

  - task brief;
  - repository map;
  - search results;
  - file slices;
  - model input;
  - raw model output;
  - normalized proposal;
  - patch candidate;
  - applied diff;
  - test output;
  - traceback summary;
  - research evidence;
  - final report.

  Events contain:

  - artifact digest;
  - schema;
  - byte length;
  - producer;
  - causation;
  - transform identity;
  - execution status.

  Events should not carry large inline payloads.

  ## Plane 2: event-sourced workflow state

  The workflow state is derived from events.

  It is never the primary source of truth.

  def reduce(state: WorkflowState, event: Event) -> WorkflowState:
      match event.type:
          case "NodeScheduled":
              return state.schedule(event.node_id)

          case "NodeSettled":
              return state.settle(
                  event.node_id,
                  event.status,
                  event.output_artifacts,
              )

          case "EdgeActivated":
              return state.activate(event.edge_id)

          case "WorkflowSuspended":
              return state.suspend(event.reason)

          case "WorkflowCompleted":
              return state.complete(event.result_digest)

  The reducer must:

  - be deterministic;
  - perform no I/O;
  - call no model;
  - read no clock directly;
  - generate no random identifiers;
  - execute no tools;
  - make no authority decision.

  ## Plane 3: workflow nodes

  Use a small closed set of node kinds.

  NodeKind = Literal[
      "transform",
      "model",
      "episode",
      "effect",
      "gate",
      "router",
      "join",
      "interrupt",
      "evaluator",
  ]

  A transform is deterministic computation.

  A model node is one constrained inference call.

  An episode is an iterative model-tool loop.

  An effect is authorized external work.

  A gate accepts or rejects evidence.

  A router chooses a declared edge.

  A join waits for declared predecessors.

  An interrupt waits for external input or approval.

  An evaluator requests independent judgment.

  ## Plane 4: ephemeral executors

  Nodes are executed by disposable workers.

  A worker receives:

  - workflow digest;
  - node specification digest;
  - input artifact digests;
  - effective capability grant;
  - budget reservation;
  - idempotency key.

  It returns:

  - status;
  - output artifact digests;
  - diagnostics;
  - actual cost;
  - retry classification.

  Workers hold no durable workflow state.

  If a worker dies, another worker reconstructs the state from events and artifacts.

  This matches your idea of agents as ephemeral events across space and time, with one correction:

  The agent itself is not an event.

  The agent invocation is an ephemeral computation.

  Its observable inputs, decisions, effects, outputs, and termination are events and artifacts.

  ## Plane 5: policy and authority

  The workflow graph is routing data.

  It must never grant authority.

  Authority remains derived from:

  - parent scope;
  - capability ceiling;
  - kernel attenuation;
  - approval policy;
  - effect classification;
  - budget reservation.

  A node may request authority.

  The graph cannot manufacture it.

  # 4. The transform primitive

  Do not add a sixth public SPI to vanguard/packages/ports/spi.py.

  The current five SPIs are frozen.

  Instead, introduce a pure artifact-level transform contract.

  Suggested domain module:

  vanguard/packages/domain/transforms/
      __init__.py
      contracts.py
      reducer.py
      schemas.py

  Suggested contract:

  @dataclass(frozen=True, slots=True)
  class TransformSpec:
      transform_id: str
      version: str
      input_schema: str
      output_schema: str
      config_digest: str
      deterministic: bool
      max_input_bytes: int
      max_output_bytes: int


  @dataclass(frozen=True, slots=True)
  class TransformInput:
      artifact_digest: str
      schema_id: str
      labels: Mapping[str, str]


  @dataclass(frozen=True, slots=True)
  class TransformDiagnostic:
      code: str
      severity: Literal["info", "warning", "error"]
      message: str
      location: str | None = None


  @dataclass(frozen=True, slots=True)
  class TransformResult:
      status: Literal[
          "accepted",
          "rejected",
          "unchanged",
          "retryable_error",
          "fatal_error",
      ]
      output_digest: str | None
      output_schema: str | None
      diagnostics: tuple[TransformDiagnostic, ...]
      confidence_ppm: int

  The implementation interface can remain runtime-internal:

  class ArtifactTransform(Protocol):
      spec: TransformSpec

      def apply(
          self,
          payload: bytes,
          config: Mapping[str, object],
      ) -> TransformOutput:
          ...

  Do not pass stores, kernels, model clients, grants, or event emitters into pure transforms.

  The runtime wrapper performs:

  - input artifact retrieval;
  - byte-limit enforcement;
  - transform invocation;
  - output canonicalization;
  - artifact storage;
  - digest calculation;
  - provenance emission.

  # 5. Transform properties

  Every deterministic transform should satisfy:

  ## Determinism

  same transform version
  plus same config digest
  plus same input digest
  equals same output digest

  ## Idempotence where applicable

  Normalization transforms should generally satisfy:

  normalize(normalize(x)) == normalize(x)

  ## Boundedness

  Every transform declares:

  - maximum input bytes;
  - maximum output bytes;
  - time ceiling;
  - memory ceiling;
  - maximum diagnostics.

  ## Provenance

  Every result binds:

  - input digest;
  - output digest;
  - transform ID;
  - transform version;
  - config digest;
  - status;
  - diagnostic codes.

  ## No silent repair

  A transform must not silently change semantic intent.

  For example:

  - whitespace normalization is safe;
  - canonical JSON key ordering is safe;
  - extracting a patch from Markdown is semantic;
  - changing a command is semantic;
  - inventing missing tool arguments is semantic.

  Semantic recovery produces a candidate and a repair directive.

  It does not execute the candidate as an authorized effect.

  # 6. Initial transform library

  Suggested path:

  packs/code-default/middleware/
      protocol/
      context/
      testing/
      repository/
      attribution/

  ## Protocol transforms

  native_tool_call_decoder.py
  dsml_decoder.py
  json_argument_normalizer.py
  markdown_patch_detector.py
  truncation_detector.py
  tool_schema_validator.py
  role_history_validator.py

  Recommended order:

  raw provider response
      -> native decoder
      -> dialect detector
      -> argument normalizer
      -> schema validator
      -> proposal classifier

  Native tool calls always take priority.

  DSML extraction is a compatibility path.

  Markdown patch detection produces:

  {
      "classification": "patch_candidate_in_text",
      "candidate_artifact": "sha256:...",
      "repair_code": "TOOL_CALL_REQUIRED",
  }

  It must not call patch.apply automatically.

  ## Context transforms

  stable_prefix_builder.py
  history_compactor.py
  receipt_summarizer.py
  artifact_reference_expander.py
  tool_result_pruner.py
  duplicate_observation_filter.py

  These should preserve:

  - current goal;
  - active constraints;
  - files already inspected;
  - edits already made;
  - test commands already run;
  - latest failures;
  - unresolved hypotheses;
  - artifact digests;
  - next required action.

  ## Test transforms

  test_command_selector.py
  test_output_parser.py
  traceback_extractor.py
  failure_clusterer.py
  verification_gate.py

  The test output parser should extract:

  {
      "command": ["python3", "-m", "unittest", "..."],
      "exit_code": 1,
      "failed_tests": [...],
      "error_locations": [...],
      "exception_types": [...],
      "short_diagnostics": [...],
      "raw_output_digest": "sha256:...",
  }

  The model receives bounded structured diagnostics plus a reference to raw output.

  ## Repository transforms

  task_file_extractor.py
  symbol_indexer.py
  import_graph_builder.py
  reference_finder.py
  change_surface_estimator.py
  multi_file_completeness.py
  diff_summarizer.py

  Start with lexical and syntax-aware retrieval.

  Do not require a vector database for the first version.

  A strong initial retrieval score is:

```text
  score = (
      0.30 * lexical_match
      + 0.25 * symbol_match
      + 0.20 * dependency_proximity
      + 0.10 * path_prior
      + 0.10 * test_reference_match
      + 0.05 * recency_need
  )
```

  All terms should be normalized to the interval from zero to one.

  Weights must be configuration artifacts so experiments do not change code.

  ## Attribution transforms

  trajectory_classifier.py
  loop_detector.py
  harness_denial_classifier.py
  dataset_preflight_classifier.py
  protocol_failure_classifier.py

  Output taxonomy:

  llm
  provider
  protocol
  harness
  framework
  dataset
  oracle
  mixed
  unknown

  Unknown must remain a valid result.

  # 7. Protocol recovery state machine

  Replace immediate malformed-proposal termination with bounded recovery.

  Suggested module:

  vanguard/packages/agency/episode/protocol_recovery.py

  Pseudocode:

  def recover(raw, state, policy):
      decoded = protocol_pipeline.apply(raw)

      if decoded.valid_proposal:
          return Accept(decoded.proposal)

      if decoded.truncated and state.truncation_retries < 1:
          return RetryModel(
              reason="OUTPUT_TRUNCATED",
              continuation=True,
          )

      if decoded.has_patch_candidate and state.protocol_retries < 1:
          return RetryModel(
              reason="PATCH_EMITTED_AS_TEXT",
              feedback={
                  "required_tool": "patch.apply",
                  "candidate_digest": decoded.candidate_digest,
              },
          )

      if decoded.has_unknown_tool and state.protocol_retries < 1:
          return RetryModel(
              reason="UNKNOWN_TOOL",
              feedback={
                  "allowed_tools": state.allowed_tools,
              },
          )

      if decoded.invalid_arguments and state.protocol_retries < 1:
          return RetryModel(
              reason="INVALID_TOOL_ARGUMENTS",
              feedback=decoded.schema_errors,
          )

      return FailInstrument(
          reason=decoded.failure_code,
      )

  Keep separate counters for:

  - provider transport retries;
  - protocol repair retries;
  - truncation continuations;
  - effect retries;
  - logical patch revisions.

  Do not use one generic retry count.

  # 8. Tool-choice enforcement

  Add state-dependent tool policy to the model request.

  Suggested modules:

  vanguard/packages/agency/episode/tool_policy.py
  vanguard/packages/adapters/models/openrouter.py
  vanguard/packages/adapters/models/config.py

  Pseudocode:

  def tool_policy(state, preset):
      if preset.mode in {"research", "explain"}:
          return ToolPolicy(mode="auto")

      if state.phase == "inspect":
          return ToolPolicy(
              mode="required",
              allowed=("fs.read", "fs.search"),
          )

      if state.phase == "edit":
          return ToolPolicy(
              mode="required",
              allowed=("fs.read", "fs.search", "patch.apply"),
          )

      if state.phase == "verify":
          return ToolPolicy(
              mode="required",
              allowed=("proc.exec", "fs.read", "patch.apply"),
          )

      if state.verification_passed:
          return ToolPolicy(mode="auto")

      return ToolPolicy(mode="required")

  Provider adapters translate canonical policy into provider syntax.

  Presets declare intent.

  Adapters declare capability.

  The runtime resolves the effective intersection.

  If a provider does not support required tool selection, emit a visible capability downgrade in the run profile.

  Do not pretend the behavior was enforced.

  # 9. Standard role history

  The OpenRouter adapter already reconstructs:

  - assistant messages with tool_calls;
  - tool messages with tool_call_id.

  Preserve this path.

  The next work is verification, not wholesale replacement.

  Add contract tests for:

  assistant tool call
  tool response
  assistant tool call
  tool response
  assistant final

  Verify that:

  - call IDs remain stable;
  - tool response IDs match;
  - arguments remain canonical;
  - no tool result becomes a user message;
  - provider-native response items are preserved where supported;
  - compaction retains action and receipt summaries.

  # 10. Generalized topology

  Preserve mhf.topology/1.

  Introduce mhf.topology/2 only through an explicit ADR and normative contract update.

  Version 2 should add operations without redefining roles.

  Example:

  {
    "api": "mhf.topology/2",
    "topologyId": "swe-hard",
    "version": "1.0.0",
    "nodes": [
      {
        "id": "localize",
        "kind": "model",
        "policyRef": "coding.localizer/1"
      },
      {
        "id": "rank-context",
        "kind": "transform",
        "policyRef": "repo.context-ranker/1"
      },
      {
        "id": "implement",
        "kind": "episode",
        "policyRef": "coding.implementer/1"
      },
      {
        "id": "test",
        "kind": "effect",
        "policyRef": "coding.test-ladder/1"
      },
      {
        "id": "verify",
        "kind": "evaluator",
        "policyRef": "coding.oracle/3"
      }
    ],
    "edges": [
      {"from": "localize", "to": "rank-context"},
      {"from": "rank-context", "to": "implement"},
      {"from": "implement", "to": "test"},
      {"from": "test", "to": "implement", "condition": "repairable_failure"},
      {"from": "test", "to": "verify", "condition": "passed"}
    ]
  }

  Cycles must be bounded by declared counters.

  A cycle without a monotonic stopping measure must fail composition.

  Examples of valid measures:

  - attempts remaining;
  - budget remaining;
  - unresolved failures decreasing;
  - candidate set shrinking;
  - verification stage advancing.

  # 11. Workflow event model

  Prefer reusing existing events where their semantics already match.

  Add only events needed for general workflow projections.

  Candidate events:

  WorkflowStarted
  NodeReady
  NodeScheduled
  NodeStarted
  NodeSettled
  NodeRetryScheduled
  EdgeActivated
  WorkflowSuspended
  WorkflowResumed
  WorkflowCompleted
  WorkflowAbandoned
  TransformApplied
  GateDecided

  Each NodeSettled should contain:

  {
      "workflowId": "...",
      "nodeId": "...",
      "attempt": 1,
      "status": "completed",
      "inputArtifacts": ["sha256:..."],
      "outputArtifacts": ["sha256:..."],
      "actualCost": {...},
      "diagnosticCodes": [...],
  }

  No model prose should be required to reconstruct workflow progress.

  # 12. RonyGPT ideas to adopt

  RonyGPT’s strongest transferable ideas are:

  - deterministic layers run before the LLM;
  - each layer fails independently;
  - weak outputs do not block stronger later outputs;
  - quality is scored by several signals;
  - results are merged conservatively;
  - expensive fallback happens only after deterministic methods are weak;
  - inputs are pruned before model use;
  - untrusted input is explicitly delimited;
  - duplicate records are merged deterministically;
  - confidence and completeness are different concepts.

  Translate this into Vanguard as:

  cheap deterministic inspection
      -> confidence assessment
      -> bounded escalation
      -> model call
      -> independent validation

  Do not copy RonyGPT’s domain-specific speaker heuristics.

  Copy the architecture of:

  - cascading;
  - scoring;
  - bounded fallback;
  - evidence preservation;
  - deterministic arbitration.

  # 13. Coding workflow for easy and medium tasks

  Use a compact staged workflow.

  preflight
  localize
  inspect
  patch
  focused test
  repair if needed
  regression test
  finish

  ## Preflight

  Deterministically verify:

  - task workspace exists;
  - baseline is clean for the challenge;
  - baseline oracle fails when expected;
  - allowed commands are representable as argv;
  - required files exist;
  - test command is available;
  - no stale bytecode or challenge cache is being consumed.

  If preflight fails, classify the row as dataset or harness invalid before model spend.

  ## Localize

  Use search and repository transforms to produce:

  - likely files;
  - likely symbols;
  - relevant tests;
  - dependency neighbors;
  - task-mentioned paths.

  Use one constrained model call only if deterministic localization is ambiguous.

  ## Inspect

  Build a focused context bundle.

  Recommended order:

  task and acceptance criteria
  current hypothesis
  top relevant source slices
  relevant tests
  dependency signatures
  recent tool receipts
  remaining budget and stopping conditions

  Do not dump the repository.

  ## Patch

  Prefer:

  - structured edit operations;
  - unified diff;
  - AST edit where appropriate;
  - whole-file replacement only for small files.

  ## Verify

  Use a test ladder:

  syntax or import check
  focused failing test
  related module tests
  broader regression tests
  exterior oracle

  Only the first necessary steps run inside the repair loop.

  The exterior oracle remains independent.

  # 14. Coding workflow for SWE-Bench Pro and hard Verified tasks

  Hard tasks need a longer durable workflow, not merely larger max_turns.

  Recommended phases:

  task understanding
  repository mapping
  hierarchical localization
  dependency expansion
  hypothesis formation
  reproduction
  change planning
  implementation
  focused validation
  repair loop
  cross-file review
  regression validation
  independent evaluation

  ## Repository mapping

  Generate content-addressed artifacts for:

  - package tree;
  - symbol index;
  - import graph;
  - inheritance relationships;
  - call references;
  - test-to-source references;
  - configuration entry points;
  - migration or schema files.

  ## Hierarchical localization

  Use three levels:

  repository to files
  files to symbols
  symbols to edit spans

  Keep multiple candidates when confidence is low.

  candidate_score = (
      issue_term_match
      + failing_test_reference
      + dependency_proximity
      + symbol_reference_count
      + semantic_model_score
  )

  ## Reproduction

  Before editing, attempt to produce a minimal reproduction or identify the existing failing test.

  If reproduction is impossible, record why:

  - missing dependency;
  - environment mismatch;
  - issue only covered by hidden oracle;
  - insufficient task information;
  - baseline already passes.

  ## Change plan

  The plan becomes an artifact:

  {
      "hypothesis": "...",
      "files_to_modify": [...],
      "files_to_inspect": [...],
      "tests_to_run": [...],
      "invariants": [...],
      "rollback_condition": "...",
  }

  ## Long conversation support

  At each phase boundary, create a checkpoint artifact containing:

  - phase;
  - accepted facts;
  - rejected hypotheses;
  - files read;
  - files changed;
  - tests run;
  - failures;
  - unresolved questions;
  - next action;
  - budget consumed;
  - artifact references.

  Do not summarize away exact test names, file paths, symbol names, digests, or unresolved errors.

  ## Repair loop

  while budget.remaining and attempts < limit:
      patch = implement(plan, context)
      result = run_focused_tests(patch)

      if result.passed:
          break

      diagnosis = classify_failure(result)

      if diagnosis.origin == "patch":
          context = add_structured_feedback(context, diagnosis)
          continue

      if diagnosis.origin in {"harness", "environment", "dataset"}:
          suspend_or_abort(diagnosis)
          break

      if diagnosis.origin == "unknown":
          request_falsifier_or_relocalization()

  ## Cross-file completeness

  Before final verification, compare:

  - files named in the task;
  - files implicated by dependency analysis;
  - files actually inspected;
  - files changed;
  - tests covering changed behavior.

  This emits warnings, not automatic edits.

  # 15. Research agent

  The research agent should be a workflow, not one open-ended chat loop.

  interpret question
  decompose claims
  plan searches
  retrieve sources
  normalize sources
  extract evidence
  deduplicate claims
  identify conflicts
  request targeted follow-up searches
  synthesize
  citation gate
  final answer

  Suggested nodes:

  research.question-parser
  research.query-planner
  research.source-retriever
  research.source-normalizer
  research.claim-extractor
  research.evidence-ranker
  research.conflict-detector
  research.synthesizer
  research.citation-validator

  Use parallelism only for independent searches.

  The synthesis node should receive claim-evidence records, not raw pages when avoidable.

  Example claim record:

  {
      "claim_id": "claim-17",
      "claim": "...",
      "support": [
          {
              "source_digest": "sha256:...",
              "location": "...",
              "quality": 0.92,
              "stance": "supports"
          }
      ],
      "conflicts": [],
      "confidence": 0.86
  }

  The citation gate verifies that every material factual claim has supporting evidence.

  # 16. Code explanation agent

  The code explanation agent should remain read-only.

  Workflow:

  parse question
  identify relevant symbols
  build bounded dependency neighborhood
  read source and tests
  construct execution trace
  check explanation against code
  render at requested depth

  Modes:

  overview
  module explanation
  function trace
  data-flow explanation
  architecture explanation
  bug explanation
  security explanation

  The agent should cite local files and lines.

  It should distinguish:

  - observed code behavior;
  - inferred design intent;
  - documentation claim;
  - uncertainty.

  # 17. Model routing

  Route by node, not only by whole agent preset.

  Example:

  classification and parsing
      deterministic code or small model

  query generation and localization
      efficient reasoning model

  complex implementation
      strongest coding model justified by budget

  test failure summarization
      deterministic parser first

  architectural review
      strong reasoning model

  independent evaluation
      separate route and evidence context

  Model routing inputs should include:

  - task difficulty estimate;
  - context size;
  - number of implicated files;
  - failed attempts;
  - protocol adherence history;
  - remaining budget;
  - latency target;
  - assurance profile.

  Escalation should be monotonic and bounded.

  A model should not be escalated merely because the harness denied a malformed command.

  # 18. Prompt architecture

  Reduce prompt density.

  Use four layers:

  L1 immutable constitutional constraints
  L2 agent or role contract
  L3 tool schemas and workflow phase
  L4 dynamic task context and receipts

  Place stable layers first to improve prompt-cache reuse.

  Move tool-specific instructions into tool descriptions.

  The dynamic prompt should state:

  - current phase;
  - required outcome;
  - allowed actions;
  - evidence already collected;
  - immediate stopping condition;
  - next required decision.

  Avoid repeating every global rule on every turn.

  # 19. Performance strategy

  Highest performance here means task success per unit of cost and latency, not maximum model usage.

  Apply these optimizations:

  ## Cache stable prefixes

  Cache:

  - system contract;
  - role contract;
  - tool definitions;
  - repository conventions.

  Do not invalidate the prefix with dynamic timestamps or run IDs.

  ## Use artifact references

  Do not replay raw outputs when a compact structured artifact is sufficient.

  ## Deduplicate observations

  If the same file slice or search query is requested repeatedly, return:

  already observed
  artifact digest
  previous turn
  change status

  Only reread when the file digest changed.

  ## Use progressive context expansion

  Start with high-confidence evidence.

  Expand only when:

  - hypothesis confidence is low;
  - test feedback implicates another module;
  - reviewer detects missing dependency;
  - model explicitly requests a justified neighbor.

  ## Parallelize independent work

  Good parallelism:

  - independent research queries;
  - independent repository searches;
  - separate candidate localizations;
  - independent reviewers;
  - unrelated test shards.

  Bad parallelism:

  - two agents editing the same files;
  - test execution before patch settlement;
  - reviewer operating on an uncommitted artifact identity;
  - multiple retries for the same non-idempotent effect.

  ## Prefer structured small outputs

  Localization nodes return ranked references.

  Test nodes return structured failures.

  Review nodes return findings.

  Only final synthesis nodes produce prose.

  # 20. Development sequence

  ## Phase 0: freeze the contract

  Edit existing canonical law and create one append-only ADR when implementation begins.

  The ADR should decide:

  - transforms are not a sixth SPI;
  - workflow graphs carry no authority;
  - event log is durable truth;
  - artifacts carry large values;
  - reducers are deterministic;
  - workers are ephemeral;
  - semantic repair cannot silently become an effect;
  - /1 topology remains compatible;
  - /2 adds typed operation nodes.

  ## Phase 1: failure attribution

  Implement first:

  tools/benchmark-drivers/triage.py

  Inputs:

  - report artifacts;
  - SQLite event stores;
  - trajectory records;
  - run configuration.

  Outputs:

  - one classification per run;
  - evidence references;
  - aggregate counts;
  - unknown cases.

  This gives a trustworthy baseline before behavior changes.

  ## Phase 2: protocol pipeline

  Add:

  vanguard/packages/agency/episode/protocol_recovery.py
  vanguard/packages/agency/episode/tool_policy.py
  packs/code-default/middleware/protocol/

  Modify:

  vanguard/packages/agency/episode/engine.py
  vanguard/packages/adapters/models/openrouter.py

  Keep adapter decoding separate from recovery policy.

  ## Phase 3: command and test feedback

  Modify:

  vanguard/packages/runtime/lab_driver.py
  packs/code-default/toolkits/terminal_runner.py

  Add:

  packs/code-default/middleware/testing/test_output_parser.py
  packs/code-default/middleware/testing/verification_gate.py

  Normalize commands into argv before validation.

  Return actionable denials.

  Do not broaden the command allowlist globally.

  Read-only command support should be preset-scoped.

  ## Phase 4: artifact transform runtime

  Add:

  vanguard/packages/domain/transforms/contracts.py
  vanguard/packages/domain/transforms/schemas.py
  vanguard/packages/runtime/transform_runtime.py
  vanguard/packages/runtime/transform_registry.py

  Extend the existing artifact provenance machinery instead of adding a second store.

  ## Phase 5: context and repository intelligence

  Add:

  packs/code-default/middleware/repository/symbol_indexer.py
  packs/code-default/middleware/repository/import_graph.py
  packs/code-default/middleware/repository/context_ranker.py
  packs/code-default/middleware/repository/multi_file_completeness.py

  Modify the existing context compiler to consume ranked artifact references.

  ## Phase 6: workflow topology v2

  Add parsing and lowering after the transform runtime is stable.

  Suggested files:

  vanguard/packages/domain/workflows/contracts.py
  vanguard/packages/domain/workflows/reducer.py
  vanguard/packages/runtime/workflow_scheduler.py
  vanguard/packages/runtime/workflow_recovery.py

  Preserve vanguard/packages/runtime/topology.py as the /1 compatibility implementation or delegate it through a normalized internal representation.

  ## Phase 7: specialized workflow packs

  Create compositions for:

  research-general
  code-explain
  code-fix-standard
  code-swe-hard
  code-review
  bug-reproduce

  Reuse nodes instead of copying agent loops.

  ## Phase 8: verification

  Before live benchmarks, verify with:

  - transform unit tests;
  - property tests for determinism and idempotence;
  - malformed protocol fixtures;
  - replay tests;
  - crash-and-resume tests;
  - duplicate-delivery tests;
  - LLM mock tests;
  - authorization falsifiers;
  - artifact provenance tests;
  - history-schema tests;
  - context-compaction tests;
  - baseline-invalid dataset tests.

  Only after these pass should live canaries resume.

  # 21. Required invariants

  The implementation should enforce these mechanically:

  I1. A workflow graph never grants authority.

  I2. A transform cannot execute an effect.

  I3. Every semantic output preserves a reference to raw input.

  I4. Every effect passes through Kernel.dispatch.

  I5. Every model call has a bounded output and retry policy.

  I6. Every cycle has a monotonic stopping measure.

  I7. Every node invocation has an idempotency key.

  I8. Every large node input and output is content-addressed.

  I9. Reducer replay performs no external I/O.

  I10. Unknown failure attribution never becomes model failure by default.

  I11. Completion gates depend on evidence, not model prose.

  I12. Child authority is no broader than parent authority.

  I13. Evaluators do not share agent-side verdict authority.

  I14. Compaction preserves active constraints and unresolved work.

  I15. Invalid benchmark baselines consume no live model budget.

  # 22. Success metrics

  Track system quality separately from model quality.

  Framework metrics:

  protocol recovery rate
  system-attributable failure rate
  replay success rate
  duplicate-effect prevention rate
  artifact provenance completeness
  unknown-attribution rate

  Agent metrics:

  task success
  first-patch success
  repair-loop success
  files localized correctly
  unnecessary files read
  test feedback utilization
  tool-call validity
  no-progress loops

  Efficiency metrics:

  tokens per successful task
  model calls per successful task
  tool calls per successful task
  cached-token fraction
  time to first useful action
  time to verified completion
  context bytes selected versus available

  Coding-quality metrics:

  oracle pass
  regression pass
  patch size
  unrelated changes
  multi-file completeness
  static analysis findings
  reviewer findings
  reproduction quality

  # 23. Final decision

  Do not build a larger monolithic autonomous agent.

  Do not add Apache Beam, LangGraph, LangChain, or Temporal as a second runtime.

  Do not add a sixth Vanguard SPI merely for middleware.

  Build an artifact-transform algebra and a durable workflow scheduler on top of Vanguard’s existing event, artifact, kernel, topology, and child-lineage
  foundations.

  The final conceptual model should be:

  Workflow specification
      -> deterministic lowering
      -> event-sourced scheduler
      -> ephemeral node executor
      -> content-addressed outputs
      -> deterministic projection
      -> next ready node

  And for agent nodes:

  focused context
      -> model proposal
      -> protocol validation
      -> authorization
      -> effect
      -> receipt
      -> structured feedback
      -> next proposal or evidence-gated completion

  This gives Vanguard a compact but powerful architecture:

  - RonyGPT-style deterministic cascades;
  - Beam-style composable transforms;
  - LangGraph-style typed routing and interrupts;
  - Temporal-style replay and durable activities;
  - SWE-agent-quality interfaces;
  - Agentless-style staged coding workflows;
  - Vanguard-native authority, provenance, recursion, and evaluation.

  That is the direction most likely to improve both free-model reliability and frontier-model performance while keeping agents ephemeral, workflows durable,
  and the architecture genuinely modular.