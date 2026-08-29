# ROLE
  Act as a Staff Engineer, Principal Systems Architect, Tech Lead, CTO/CIO, Engineering Director, Scrum Master, PhD AI Systems Specialist, Senior Backend Developer, and Agentic Coding
  Harness Specialist.

  # TODO

  Create a report with your full plan in two big detailed chapters called VANGUARD_090_BACKEND_AUDIT_AND_EVOLUTION_{CUSTOM_NAME}_PLAN.md . It should be minimum 1000 lines.

  # GUIDELINES
  # Vanguard Backend Reality Audit and Evolution Plan — 0.9.0b1 → 0.9.1

  Act as a Principal Systems Architect, Staff Backend Engineer, AI Research Lead and technical product owner.

  Perform a rigorous, code-first investigation of the current Vanguard repository and determine:

  1. what is genuinely implemented and working today;
  2. what remains necessary to deliver a useful backend beta;
  3. what complexity is essential versus accidental;
  4. what should be completed before refactoring;
  5. how Vanguard should then be simplified into a robust, lightweight and extensible universal agentic framework.

  This is an assessment and planning task. Do not modify production code or canonical documentation yet.

  ## Sources to inspect

  Read the latest repository state, focusing exclusively on the Vanguard backend, including:

  * `vanguard/`
  * `README.md`
  * `VISION.md`
  * `docs/SPEC.md`
  * `docs/03_execution/milestones.md`
  * `docs/03_execution/sprint_active.md`
  * `docs/03_execution/sprint_upcoming.md`
  * current backlog and roadmap
  * current ADRs and contracts
  * existing schemas, tests, benchmarks, evidence bundles and verification tools
  * `AETHER_PHASE1_ASSESSMENT.md`
  * `ADR-0097-phase1-foundation-review-and-concept-lock.md`
  * `ARCHITECTURE_DELTA.md`
  * `BACKLOG.md`
  * `MILESTONE_SPECS.md`
  * `SPEC_M4_TRAJECTORY_CAPTURE.md`
  * `SPEC_M5A_EVENT_DERIVED_AGENT.md`
  * `DEVELOPMENT_PLAN.md`
  * `SPEC_M5B_M6.md`
  * `SPEC_M65_M7_M8.md`
  * `SPRINT_ACTIVE.md`
  * `SPRINT_UPCOMING.md`
  * `masterplan_todo_rev1.md`
  * Other important documents like docs/_archive/reviews/backend/director_review_v4, docs/_archive/reviews/backend/director_review_v3, VANGUARD_BACKEND_M1_M9_MASTER_REPORT.md, VANGUARD_BACKEND_M1_M9_MASTER_REPORT.md and TODO_PROMPT.md

  Resolve actual paths from the repository rather than assuming these filenames are located together. Treat current code, tests and executable verification as implementation evidence;
  treat documentation as claims that must be checked against code.

  ## Do not assume the previous review is correct

  Independently reproduce or falsify all previous claims, including:

  * test counts and failures;
  * kernel LOC and architectural-boundary results;
  * M‑4 through M‑8 implementation and evidence status;
  * missing `CONVERGENCE-BASE-v1`;
  * validity of M‑5b evidence;
  * readiness of M‑6, M‑6.5, M‑7 and M‑8;
  * completeness of recursive execution, topology, memory, rollback and evaluation;
  * packaging and M‑9 readiness;
  * runtime duplication and bloat.

  For every important conclusion, cite concrete evidence:

  * file and symbol;
  * test or verification command;
  * observed result;
  * whether the claim is implemented, partially implemented, documentary only, blocked or obsolete.

  Distinguish clearly between:

  1. implementation truth;
  2. automated verification truth;
  3. milestone/document status;
  4. release-integrity requirements;
  5. organizational or scientific-review requirements.

  Do not allow a missing human reviewer, countersignature, board status or governance ceremony to be presented as a technical blocker to a locally functional beta. Human independence may
  remain necessary for a formal scientific claim or signed release attestation, but technical qualification should rely primarily on reproducible automated evidence.

  ## Product thesis to preserve

  Vanguard is not intended merely to import Lex, LIM or other monolithic engines. It should natively express systems such as:

  * Lex-like coding harnesses;
  * Claude Code/Codex-style coding agents;
  * codebase explainers and reviewers;
  * bug-fixing agents;
  * research and citation agents;
  * RAG workflows;
  * planner/executor/critic systems;
  * multi-agent and nested-subagent topologies.

  The intended abstraction is:

  ```text
  Agent =
    Model
    + Tools
    + Context Strategy
    + Policy
    + Workflow
    + Memory
    + Evaluators
    + Limits
  ```

  These systems must be different compositions of Vanguard primitives, plugins, packs and workflows—not separate production engines hidden behind adapters.

  Preserve, unless code evidence demonstrates a fundamental defect:

  * events at the heart of execution;
  * append-only causal history;
  * content-addressed artifacts;
  * event-derived recoverable state;
  * capabilities and multidimensional budgets;
  * domain-blind kernel;
  * agents and subagents represented by scopes and lineages;
  * replaceable orchestration;
  * plugins and packs outside the kernel;
  * benchmarkable trajectories;
  * transport-neutral logical contracts;
  * deterministic replay where semantically possible;
  * crash recovery and continuation.

  ## Important corrections to the previous proposal

  ### 1. Capture profiles must not impose unnecessary information loss

  Do not define `fast`, `standard` and `research` as separate engines or rigid feature tiers. They should be presets over orthogonal configuration axes.

  Cheap, valuable information that already crosses the runtime should normally be capturable in every production profile:

  * final prompt sent to the model;
  * compiled context;
  * model output;
  * tool requests and results;
  * patches and diffs;
  * causal events;
  * model/configuration identity;
  * tokens, cost and latency;
  * workflow boundaries;
  * recovery state;
  * essential artifacts and digests;
  * lightweight Pareto metrics.

  Large content should live in the artifact store with references in the ledger. Inspect whether current code already supports this efficiently and identify the actual overhead.

  A better configuration model may resemble:

  ```yaml
  capture:
    prompts: full
    context: full
    outputs: full
    tools: full
    patches: full
    environment: digest

  telemetry:
    pareto: basic
    traces: sampled

  recovery:
    events: durable
    checkpoints: boundaries

  evaluation:
    evaluators: []
    repetitions: 1
    mutation_testing: false

  control:
    allow_reject: false
    allow_retry: true
    allow_redirect: false
    allow_fork: false

  retention:
    artifacts: configurable
  ```

  Determine the correct schema from the existing architecture rather than copying this mechanically.

  What should remain optional is additional computation or retention cost:

  * mutation testing;
  * repeated executions;
  * A/B and ablation studies;
  * external evaluators;
  * adversarial validation;
  * environment replication;
  * signed evidence;
  * extended statistical analysis;
  * training exports;
  * long-term retention.

  ### 2. Research should be a composition, not another engine

  Research behavior should be implemented by plugins, evaluators, policies and workflow interceptors around the same runtime.

  Define or verify universal lifecycle boundaries such as:

  ```text
  before_operation
  after_operation
  on_event
  before_commit
  after_result
  on_failure
  ```

  Separate observer plugins from control-authorized plugins. Control decisions should use an explicit vocabulary such as:

  ```text
  ACCEPT | REJECT | RETRY | REDIRECT | FORK | STOP
  ```

  Logging must never gain implicit control authority.

  ### 3. Hashing and integrity

  A hash can be derived later only if the original bytes were retained unchanged. For strong identity and causal integrity, evaluate a path equivalent to:

  ```text
  capture bytes → persist artifact → compute digest → emit causal reference
  ```

  Determine whether hashing, persistence or artifact capture can be asynchronous without violating settlement, recovery or integrity.

  ### 4. Workflow capability must not be rejected prematurely

  Do not assume that Vanguard needs a large general-purpose workflow engine, but also do not prohibit a simple universal workflow model before inspecting the code.

  Determine whether existing operations, events, dependencies, `agent.spawn`, topology lowering and settlement predicates already form a sufficient minimal workflow language.

  The same foundation should be capable of expressing:

  * direct tool loop;
  * ReAct-style loop;
  * staged coding workflow;
  * planner/executor/reviewer;
  * critic/reviser;
  * research fan-out;
  * fork/read/merge;
  * bounded retries;
  * nested subagents.

  Avoid introducing a second orchestration engine.

  ### 5. Milestone evidence must not replace product proof

  A mechanically accepted milestone does not prove that Vanguard is usable as a product. Conversely, documentary drift does not necessarily mean the implementation is missing.

  The beta must demonstrate a real vertical slice:

  ```text
  install → configure → run → inspect → interrupt → resume → verify result
  ```

  At least two useful Vanguard-native compositions should run through the same production runtime:

  1. `Lex-Minimal` or equivalent coding workflow;
  2. `Codebase-Explainer` or another materially different workflow.

  A multi-role composition should also prove nested/multi-agent execution without kernel changes.

  ## Required investigation

  ### A. Repository and dependency map

  Map the backend packages, imports and production execution path:

  ```text
  client/API
  → composition
  → runtime
  → agency/policy
  → kernel authorization
  → adapters/effects
  → events/artifacts
  → projections/recovery
  ```

  Identify:

  * duplicate bootstrap paths;
  * duplicate model factories;
  * duplicate manifest/pack loaders;
  * duplicate event representations;
  * overlapping Agency/Runtime responsibilities;
  * oversized modules such as session lifecycle components;
  * metadata-only registries;
  * obsolete compatibility paths;
  * validations repeated across layers;
  * abstractions with zero or one real consumer;
  * dead schemas, event kinds and adapters;
  * documentation mechanisms coupled to runtime behavior.

  Do not remove anything merely because it looks complex. Explain its consumers, invariant protected, runtime cost and replacement path.

  ### B. Milestone truth matrix

  For every milestone M‑1 through M‑9, report:

  | Milestone | Code implemented | Tests passing | Evidence valid | Product-visible capability | Actual blocker | Required action |
  | --------- | ---------------: | ------------: | -------------: | -------------------------: | -------------- | --------------- |

  Determine whether M‑5a/M‑5b gaps are:

  * missing implementation;
  * missing release identity;
  * failed experiment;
  * stale documentation;
  * invalid evidence;
  * external governance requirement.

  Determine whether M‑6→M‑8 can legitimately remain accepted if earlier release/evidence predicates are incomplete, separating technical functionality from formal milestone lineage.

  ### C. Beta product gap

  Identify the minimum backend work required for `0.9.0b1`, including:

  * one authoritative version source;
  * reproducible package build;
  * clean installation outside the checkout;
  * explicit durable state directory;
  * no hidden `PYTHONPATH` dependency;
  * no silent in-memory fallback;
  * packaged schemas, migrations and manifests;
  * unified runtime composition;
  * commands/API for run, resume, status, events and artifacts;
  * health versus readiness;
  * redacted typed diagnostics;
  * plugin discovery and activation lifecycle;
  * kill-and-resume verification;
  * offline-after-install verification using fake/local/cassette adapters;
  * coding and non-coding reference workflows.

  Classify every item as already complete, partially complete or missing.

  ### D. Performance and storage baseline

  Measure rather than speculate:

  * no-op/minimal-turn framework overhead excluding model latency;
  * authorization dispatch latency;
  * event append throughput;
  * synchronous versus batched persistence;
  * warm runtime memory;
  * cold replay and checkpoint-plus-suffix recovery;
  * prompt/context/artifact capture overhead;
  * storage amplification;
  * latency added by hashing and durability;
  * performance of one agent versus multiple concurrent agents;
  * ledger contention and ordering costs.

  Compare a Vanguard-native minimal coding loop with the simplest dedicated baseline available, while avoiding unfair comparisons caused by different models, tools or task logic.

  ### E. Governance audit

  Classify governance mechanisms into:

  * architectural invariant protection;
  * release integrity;
  * scientific experiment rigor;
  * ordinary product development;
  * obsolete bureaucracy.

  ADRs and formal acceptance should remain mandatory only for changes to foundational invariants or public contracts, such as:

  * kernel neutrality;
  * causal integrity;
  * authority and budget conservation;
  * compatibility;
  * replay semantics;
  * transport equivalence;
  * effect settlement and fail-closed execution.

  Adding an ordinary tool, workflow, pack, evaluator, context strategy or reference agent should not require constitutional ratification.

  Propose how to reduce execution boards and documentary duplication while retaining traceability.

  ## Two-horizon plan required

  ### Horizon 1 — Finish and ship `0.9.0b1`

  Produce the shortest technically correct plan to:

  1. establish independently verified repository truth;
  2. repair only genuine milestone/evidence inconsistencies;
  3. complete missing beta product work;
  4. deliver the two reference workflows;
  5. validate installation, execution, interruption, recovery and inspection;
  6. benchmark current overhead;
  7. freeze an exact beta artifact.

  Do not introduce speculative SOTA capabilities during this horizon.

  Do not require external human ceremony to run or technically qualify the beta. List separate optional steps for formal scientific or signed-release acceptance.

  ### Horizon 2 — Vanguard `0.9.1`

  After beta measurement, plan an evolutionary refactoring—not a rewrite—to:

  * consolidate runtime/bootstrap responsibilities;
  * unify factories and loading paths;
  * converge event contracts;
  * reduce duplicate validation;
  * extract oversized modules without semantic changes;
  * remove dead abstractions and metadata-only ceremony;
  * implement orthogonal capture/operation/evaluation/retention configuration;
  * preserve complete cheap capture;
  * make expensive research operations optional;
  * simplify the public mental model to:

  ```text
  Observe → Decide → Authorize → Execute → Record
  ```

  The existing kernel may retain its deeper internal authorization stages.

  Define how new Vanguard-native agents can be created mostly through configuration, stable SPIs and reusable plugins without kernel changes.

  ## Required deliverable structure

  Produce one detailed report with:

  1. Executive verdict.
  2. Verified repository baseline.
  3. Claims from the previous review: confirmed, falsified or unverified.
  4. Backend architecture and production-path map.
  5. Milestone M‑1→M‑9 truth matrix.
  6. Beta product gap analysis.
  7. Bloat and duplication map.
  8. Retain / consolidate / optionalize / remove / defer matrix.
  9. Capture, telemetry, recovery, evaluation and retention model.
  10. Universal event/plugin/workflow/transport contracts.
  11. Performance and storage measurements.
  12. Exact `0.9.0b1` completion plan.
  13. Exact `0.9.1` refactoring plan.
  14. Risks, rollback points and acceptance criteria.
  15. Final recommendation: preserve, simplify, archive or rewrite—with evidence.

  For every planned task include:

  * task ID;
  * concrete outcome;
  * affected backend modules;
  * dependencies;
  * tests;
  * measurable acceptance criteria;
  * whether it changes behavior or only structure;
  * estimated risk;
  * explicit non-goals.

  End with a small ordered action list stating exactly what the developers should do next.

  ## Constraints

  * Backend only.
  * Do not edit code or documentation in this phase.
  * Do not trust documentation over executable evidence.
  * Do not trust the previous analysis without reproducing it.
  * Do not propose a rewrite without proving the existing foundation is irrecoverable.
  * Do not preserve complexity merely because it already exists.
  * Do not import Lex/LIM as alternative production engines.
  * Do not add another kernel, ledger, agent engine or orchestration authority.
  * Do not sacrifice valuable cheap observability for artificial profile simplicity.
  * Do not confuse scientific rigor with mandatory runtime overhead.
  * Do not make SWE-Bench competitiveness a beta-release blocker.
  * Do require at least one useful coding workflow and one distinct non-coding workflow.
  * Preserve events, budgets, artifacts, recovery, plugins and multi-agent execution as first-class architectural capabilities.

  The final report must make it possible to decide—using verified code evidence—what to finish immediately, what to postpone, what to simplify after beta and whether Vanguard can
  genuinely become a lightweight universal substrate for constructing Lex-like, Claude Code-like, research and code-analysis systems.


  # Notes
  ## Additional Product-Relevance Checks

  Without presuming that any new mechanism is necessary, determine:

  1. Whether bidirectional PTY streaming is required for the `0.9.0b1` coding workflow.
  2. Whether duplicate event publication, serialization, bootstrap or governance work exists in the production hot path.
  3. Whether operational isolation, capture, durability, evaluation and retention are already orthogonal configurations, while preserving cheap essential capture.
  4. Whether current sandbox, context-strategy and plugin contracts can accept future implementations without breaking existing consumers. Do not add speculative extension seams unless a
  concrete near-term consumer proves they are necessary.
  5. Whether prefix stability and replaceable compaction already exist and are sufficient.
  6. Which ideas—CoW snapshot/fork, Tree-Sitter preflight, improved compaction, taint policies, SBFL, differential testing, mutation testing, MCTS and CEGIS—deserve later experiments
  based on measurable product value.

  Classify each as:

  | Proposal | Existing capability | Verified gap | Required for beta | Post-beta experiment | Reject |

  Do not design or schedule these mechanisms merely because they appeared in prior prototypes; first establish repository truth, beta necessity and measurable acceptance criteria.

  # Requirements
  Dont run git commands, focus on the rest as I will manage our existing branch 'feat/vanguard-0.9.0b1-beta-evolution'