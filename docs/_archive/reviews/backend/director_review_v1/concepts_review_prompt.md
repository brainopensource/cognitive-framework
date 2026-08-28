# Concepts Review Directive: Autonomous Meta-Framework & Substrate Audit

## ROLE
Act as the **Engineering Director**, **Chief Architect**, **Principal Staff Engineer**, **PhD-level AI Agent Systems Researcher**, **Senior Software Architect**, and **SOTA Framework Engineer** responsible for evaluating and redefining the future of **AETHER / Vanguard**.

---

## TODO
Clone and verify the latest `main` branch of:  
`https://github.com/brainopensource/cognitive-framework`

Read and audit the complete implementation, architecture, tests, schemas, workflows, active roadmap, accepted decisions, specifications, packs, plugins, runtime, kernel, evaluator, sandbox, persistence, and supporting documentation.

Produce a fresh, independent, evidence-based architectural and strategic review named:  
`Full_harness_rewrite.md`

The purpose of this review is to determine whether the current prototype can evolve into a true meta-framework for constructing autonomous general-task solvers, agentic algorithms, specialized harnesses, recursive agents, and future meta-cognitive systems.

Do not assume that the current architecture, roadmap, abstractions, milestones, ADRs, plugin model, runtime, or trusted boundaries are optimal merely because they already exist.

The review may recommend preserving, correcting, simplifying, generalizing, reordering, replacing, or rebuilding major parts of the system — including starting from a cleaner architectural baseline — whenever the evidence shows that the current design would create long-term limitations for modularity, composability, performance, extensibility, reliability, generality, or scientific self-improvement.

The current roadmap is evidence of previous intent, not an obligation. Treat the existing project as a prototype whose architecture must be validated against the long-term objective of becoming a modular meta-framework capable of supporting coding agents similar to Codex CLI and Claude Code, while also supporting non-coding autonomous task solvers and higher-order agentic algorithms.

Use previous reviews and research as historical reference material only.

Determine the final recommendation independently from the actual `main` branch, its implementation, its tests, and its authoritative documentation.

---

## GUIDELINES

### 1. Source of truth and review discipline
Treat the verified `main` branch, its implementation, tests, schemas, CI, linters, and canonical documentation as the primary source of truth.

Read and reconcile:
- `README.md`
- `AGENTS.md`
- `docs/SPEC.md`
- `docs/01_law/`
- `docs/02_decisions/`
- `docs/03_execution/sprint_active.md`
- `docs/03_execution/milestones.md`
- `docs/04_architecture/`
- `schemas/`
- `vanguard/packages/`
- `packs/`
- `containers/`
- `test/`
- `tools/`
- CI workflows and package configuration.

Read archived reviews, proposals, research, and `001_alfa_review*` documents as historical evidence only. They may inform questions and comparisons, but they must never override current normative law, accepted decisions, the active execution board, or the actual code.

Reconcile every significant claim and classify it as:
- implemented and verified;
- implemented but insufficiently tested;
- documented but not implemented;
- implemented but undocumented;
- contradicted across code and documentation;
- historical or superseded;
- proposed but not authorized;
- blocked by environment;
- or genuinely missing.

Use precise paths, modules, classes, tests, schemas, falsifiers, and commands as evidence. Do not infer architecture from names alone.

---

### 2. Zero-base architectural mandate
The project is still a prototype. The current roadmap, milestones, ADRs, module boundaries, manifest shape, runtime model, plugin architecture, and trusted-core structure represent accumulated intent, not unquestionable truth.

The review is explicitly authorized to recommend:
- preserving the current architecture;
- focused corrections;
- simplification;
- consolidation;
- reordering milestones;
- replacing a subsystem;
- invalidating a planned milestone;
- redefining the v0.6.2 scope;
- rebuilding a component from first principles;
- or performing a broader architectural reset.

Do not preserve an abstraction merely because it has already received effort, documentation, tests, terminology, or an ADR.

Do not recommend a rewrite merely because the project is ambitious, because another framework is fashionable, or because a different language appears more modern.

A material rewrite is justified only when evidence shows that the current boundary, abstraction, or execution model would create a durable limitation in generality, composability, performance, security, maintainability, reproducibility, or future self-improvement.

For every proposed reversal or rebuild, identify:
- the exact assumption that failed;
- evidence from code, tests, benchmarks, or research;
- why a local refactor is insufficient;
- the minimum replacement boundary;
- migration cost versus clean-slate cost;
- what must be preserved;
- what must be deleted or retired;
- the acceptance gates proving the replacement is superior.

The roadmap is a hypothesis to evaluate, not the answer.

---

### 3. Product and research vision
AETHER / Vanguard must not become merely a strong coding-agent harness.

The intended long-term system is a modular substrate for constructing, executing, evaluating, comparing, and eventually improving:
- coding agents;
- research agents;
- autonomous general-task solvers;
- formal and mathematical solvers;
- tool-using systems;
- planning agents;
- critic/reviser workflows;
- bounded tree-search systems;
- debate and aggregation systems;
- hierarchical decomposition;
- recursive and delegated agents;
- multi-agent coordination policies;
- deterministic and LLM-hybrid algorithms;
- evolutionary search;
- meta-harnesses;
- governed metacognitive systems;
- and self-improvement experiments.

The coding agent is the first serious laboratory because it provides a difficult, measurable environment for refining loops, planning, tools, context, memory, authority, evaluation, recovery, observability, cost accounting, reproducibility, and safety.

The framework must not become permanently shaped around coding. Coding, mathematics, research, tables, web tasks, and future domains should be expressed through packs, tools, models, environments, or compositions rather than by introducing domain semantics into the trusted foundation.

---

### 4. Central architectural question
Determine whether the current project is becoming:
- the smallest durable substrate from which many generations of agents and agentic algorithms can be constructed; or
- a highly governed coding-agent framework whose apparent generality will collapse when a second or third domain is introduced.

The target architecture should be evaluated as a system of composable agentic building blocks:
> **composition + policies + components + tools + model + environment + execution substrate + evidence.**

Do not assume every mechanism should become a plugin. Determine what must remain trusted infrastructure, what should become a port or adapter, what belongs in a domain pack, what should be a selectable policy, what should be a declarative composition, and what should remain first-party runtime machinery.

---

### 5. Review the project in three horizons

#### A. Project today
Audit the implementation as one coherent machine.

Evaluate:
- the `domain`, `ports`, `kernel`, `agency`, `runtime`, `adapters`, `apps` lattice;
- canonicalization, identity, schemas, wire contracts, and digests;
- event taxonomy, reducer, ledger, receipts, and recovery;
- authority, capabilities, budgets, grants, provenance, and approvals;
- `EpisodeEngine` and universal turn-loop assumptions;
- runtime composition, session ownership, wiring, and registry;
- manifest parsing, graph compilation, profiles, and bindings;
- plugin discovery, lifecycle, isolation, cleanup, and worker protocols;
- model adapters, evaluator, sandbox, stores, and environment adapters;
- packs, tools, containers, and CLI boundaries;
- tests, falsifiers, CI, code generation, and architectural linters;
- duplication, transitional structures, hidden coupling, and ownership ambiguity;
- API stability, developer ergonomics, cognitive complexity, and maintenance cost.

Determine what is genuinely reusable, measured, enforceable, and understandable versus what exists primarily as documentation or test scaffolding.

#### B. Foundation and current release decision
Verify independently the current status of M-0 through M-4.

Pay particular attention to the documented claims that:
- M-0, M-1, M-2, Wave 2C, and M-3 are complete;
- M-3 delivered canonical manifest and component-graph behavior;
- registry lifecycle and plugin isolation are now canonical;
- Layer-0 retirement was actually proven;
- M-4 is active but blocked by a real provider/evaluator environment;
- the nine-row foundation E2E validator cannot be satisfied by mocks, cassettes, stitched traces, host fallback, or manually copied evidence.

Determine whether the M-4 block is:
- merely an unavailable environment;
- a missing operational integration;
- an incomplete product capability;
- a design problem;
- or an incorrectly defined foundation gate.

Then determine the correct v0.6.2 or post-M-3 decision. It may be:
- a narrow corrective release;
- a consolidation release;
- a composition/plugin correction;
- a foundation re-baseline;
- a reordered roadmap;
- or no release until a deeper architectural decision is made.

Do not assume M-4 must be the next step simply because it is documented. Assess whether M-4 is the correct next proof or whether a composition stress test, second-domain probe, or architecture correction must happen first.

For every proposed change, state why it must happen before M-4, what evidence supports it, what it costs, and what risk is created by deferring it.

#### C. Long-term evolution toward v1.0.0
Evaluate whether the current foundation can support the documented sequence:
- **M-4:** real coding-agent foundation E2E;
- **M-5:** second domain through Math and Formal Deductive Verification;
- **M-6:** capability-mediated `agent.spawn`;
- **M-7:** controlled concurrency, worker pools, leases, and Pareto routing;
- **M-8:** framework-builder topologies;
- **M-9:** retrieval, skills, macro laboratory, and scale measurement;
- **M-10:** governed metacognition, trajectory credit, DPO, promotion, and rollback.

The roadmap may be preserved, reordered, split, merged, reduced, or replaced if the evidence justifies it.

---

### 6. Composition and extensibility
Determine whether the current composition model can express multiple classes of agentic algorithms without creating a new privileged engine for each one.

Evaluate:
- planners;
- context managers;
- memory engines;
- toolkits;
- model routing;
- evaluators;
- approval policies;
- reflection;
- orchestration;
- delegation;
- scheduling;
- retrieval;
- skills;
- macro tools;
- experiments;
- promotion;
- and evidence strategies.

Assess whether the named component graph supports:
- repeated components of the same kind;
- typed bindings;
- explicit interfaces;
- nested compositions;
- profiles;
- capability ceilings;
- lifecycle ownership;
- deterministic freezing;
- graph identity;
- lazy dependencies;
- failure semantics;
- and future polyglot components.

Determine whether composition is actually declarative or whether important behavior remains hidden inside monolithic planners, sessions, or runtime special cases.

---

### 7. Trusted foundation and flexibility
Classify each important mechanism as:
- permanently trusted and non-pluggable;
- trusted first-party infrastructure with replaceable adapters;
- policy-selectable per composition;
- optional but explicitly recorded as absent;
- external service;
- future experimental capability;
- or unsafe to generalize.

Review the placement of:
- capability mediation;
- grants;
- budgets;
- resource selectors;
- evaluator isolation;
- signed verdicts;
- event lineage;
- ledger truth;
- canonicalization;
- provenance;
- approvals;
- sandboxing;
- promotability;
- and identity.

Strong guardrails should remain available as infrastructure without forcing every future agent into unnecessary coding-specific governance. At the same time, absence of a guardrail must never be confused with evidence that the guardrail existed.

---

### 8. Agentic algorithms and meta-harnesses
Use concrete algorithmic cases as expressiveness probes:
- coding harness;
- formal mathematical proof;
- critic/reviser;
- planner/executor/verifier;
- hierarchical decomposition;
- bounded tree search;
- debate and aggregation;
- evolutionary search;
- research workflow;
- deterministic workflow with LLM policy;
- multi-agent coordination;
- and hybrid symbolic/LLM systems.

For each case, determine whether it is:
- expressible in the current system;
- expressible after an already planned milestone;
- expressible only after a new extension contract;
- expressible only by violating current boundaries;
- or evidence that the universal-loop thesis must be revised.

Prefer composition over new ontology where possible, but do not force every algorithm into the same loop if evidence shows a fundamental mismatch.

---

### 9. Runtime, state, performance, and scale
Evaluate whether the architecture preserves a credible path from sequential execution to high-performance orchestration.

Investigate:
- logical-agent versus worker-process separation;
- cold reconstruction from durable state;
- scheduler ownership;
- actor and event-driven compatibility;
- IPC and serialization costs;
- plugin-call overhead;
- registry lifecycle overhead;
- WAL contention and ledger pressure;
- memory footprint;
- model invocation concurrency;
- cancellation and backpressure;
- isolation cost;
- resource accounting;
- observability overhead;
- and failure recovery.

Do not optimize prematurely. Determine which current decisions preserve future optimization freedom and which decisions would make scale unnecessarily expensive.

---

### 10. Polyglot and replaceable process architecture
Evaluate how individual processes could later be replaced by Rust, Go, or TypeScript without rewriting the entire platform.

Potential candidates include:
- sandbox workers;
- evaluator services;
- plugin workers;
- registry brokers;
- event stores;
- retrieval and index services;
- schedulers;
- model gateways;
- benchmark runners;
- telemetry collectors;
- SDKs and CLI clients.

The language must not become the portability boundary. The real boundary must be:
- versioned schemas;
- wire protocols;
- event envelopes;
- canonicalization;
- identity and digest rules;
- error semantics;
- capability and ceiling representation;
- conformance vectors;
- differential replay;
- and lifecycle contracts.

Determine whether a future replacement can produce equivalent results for the same inputs, events, signatures, failures, and recovery scenarios.

Also determine which parts must remain Python reference implementation until semantic equivalence is proven.

---

### 11. Evidence, data, learning, and metacognition
Assess whether the current trajectory and event architecture can support scientifically defensible improvement later.

Evaluate readiness for:
- trajectory analysis;
- cost and routing calibration;
- prompt optimization;
- composition optimization;
- planner selection;
- plugin selection;
- reflection strategies;
- skill extraction;
- retrieval evaluation;
- preference datasets;
- DPO;
- candidate harness archives;
- paired experiments;
- promotion;
- rollback;
- and metacognitive agents.

The standard is not that the system can modify itself. The standard is that every candidate has:
- attributable composition identity;
- execution identity;
- task identity;
- complete trajectory;
- external evidence;
- known cost;
- explicit authority;
- controlled comparison;
- reproducible environment;
- and reversible promotion.

---

### 12. Benchmark and generality proof
Define the minimum benchmark lattice required to demonstrate that AETHER is a meta-framework rather than a coding harness with plugins.

At minimum, assess:
- coding;
- a non-coding formal domain;
- recursive delegation;
- multiple composition topologies;
- alternative models;
- alternative evaluation policies;
- recovery and replay;
- and at least one future polyglot component.

Generalization must be measured dimension by dimension. Do not vary domain, topology, model, memory, retrieval, concurrency, and promotion policy simultaneously without controls.

---

### 13. Research
Research contemporary primary sources, official documentation, papers, and engineering systems only after auditing the repository.

Compare architectural ideas from:
- modern coding harnesses;
- lightweight plugin-heavy harnesses;
- durable workflow systems;
- actor and event-driven systems;
- event sourcing;
- capability security;
- sandboxing;
- evaluators;
- trajectory learning;
- self-refinement;
- evolutionary search;
- agentic reinforcement learning;
- metacognitive systems;
- experiment platforms;
- and promotion pipelines.

Use DeepSeek Harness, Codex CLI, Claude Code, and other systems as comparative evidence for composability, execution ergonomics, workflows, and performance.

Do not treat any system as the target architecture. Adopt only concepts that improve AETHER's own long-term substrate while preserving independent authority, evidence, identity, reproducibility, and scientific measurement.

Clearly separate:
- repository facts;
- sourced external facts;
- inference;
- architectural recommendation;
- and speculative future research.

---

## GOAL
Determine whether the project should proceed from the current `main` branch toward v0.6.2 and v1.0.0 through focused corrections, or whether the current prototype requires a deeper architectural reset.

The review must establish the smallest durable and modular substrate capable of supporting autonomous general-task solvers, coding agents, specialized harnesses, recursive agents, alternative agentic algorithms, future meta-harnesses, and governed self-improvement.

The desired result is not maximum abstraction. It is maximum future design freedom obtained from the smallest set of stable, testable, understandable, and high-leverage mechanisms.

---

## DELIVERABLES
Produce a complete report named:  
`Full_harness_rewrite.md`

The report must be written at PhD, Principal Architect, Staff Engineering, AI Systems Research, and SOTA framework-design level.

The report must include:
- Exact repository baseline, commit, branch, timestamp, and evidence scope.
- Executive verdict with confidence level.
- Precise definition of what AETHER is today.
- Current architecture and implementation assessment.
- Strong mechanisms that should remain stable.
- Weaknesses, coupling, debt, contradictions, and unproven claims.
- A keep, strengthen, simplify, generalize, defer, experiment, or reject table for every major subsystem.
- A zero-base assessment of whether the current architecture should survive.
- A concrete v0.6.2 recommendation with explicit scope and non-scope.
- A strict M-4 readiness assessment.
- A revised roadmap from M-4 through v1.0.0.
- A corrected milestone and sprint strategy where necessary.
- Benchmark cases proving composability and domain generality.
- A plugin and component-boundary map.
- A trust, authority, evidence, and flexibility boundary map.
- A runtime, recovery, performance, and scale assessment.
- A polyglot migration strategy for future Rust, Go, or TypeScript processes.
- A data, trajectory, experimentation, and metacognition readiness assessment.
- A future self-improvement and promotion architecture.
- A prioritized action list with exact modules, owners, risks, dependencies, tests, falsifiers, and recommended timing.
- A list of decisions that should remain frozen.
- A list of decisions that should be reopened.
- A list of features that should explicitly be rejected or deferred.
- Explicit answers to:
  - What would prevent AETHER from becoming state of the art?
  - What must change before M-4?
  - What must not change before M-4?
  - Is M-4 the correct next proof?
  - What should wait until a second domain proves generality?
  - What is the minimum meta-framework proof?
  - Which claims require new falsifiers?
  - What should v0.6.2 mean?
  - What should v1.0.0 mean operationally?
  - Should the project proceed, be corrected, or be materially re-founded?

For every major recommendation, provide:
- rationale;
- evidence;
- affected code and documentation;
- migration impact;
- implementation complexity;
- performance consequences;
- security consequences;
- reversibility;
- acceptance criteria;
- falsifier or benchmark;
- and recommended milestone.

Do not begin implementation. Do not modify the repository. Do not create additional documentation files inside the repository.

End the report with one unambiguous decision:
- **“Proceed unchanged,”**
- **“Proceed with focused corrections,”**
- or
- **“Pause for material architectural revision.”**

Follow that decision with the exact next authorized engineering action.