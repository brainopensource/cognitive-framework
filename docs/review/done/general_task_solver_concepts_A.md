# General Task Solver Concepts — Version A

- **Status:** Independent technical review and concept proposal
- **Research cut-off:** 2026-08-14
- **Starting application:** Agentic coding harness CLI
- **Long-term direction:** A domain-independent, evidence-directed problem-solving substrate

---

## 1. Executive verdict

Vanguard v4 contains a stronger trust, evidence, and failure-semantics foundation than most coding-agent projects, but it is currently a better research specification than a Phase 0 implementation plan. Its best ideas should be retained: the evaluator and release authority remain outside the self-editable boundary; effects are mediated by resource-scoped capabilities and real workload isolation; runs produce typed, durable evidence; crashes preserve uncertainty instead of inventing success; competence claims can be invalidated and demoted; promotion requires hard safety constraints before multi-objective optimization; and coding is treated as a falsifiable laboratory rather than proof of general intelligence. The main weakness is premature closure: six architectural planes, exactly four extension forms, a frozen tool atom set, universal mediation of every read and model call, a categorical rejection of workflow graphs, fully specified wire schemas, TableWorld, and 203 normative rules with 133 initially uncovered create a large correctness surface before the product has demonstrated useful agent behavior. The recommended decision is therefore **not to discard Vanguard and not to implement it literally**. Preserve the trust-and-evidence spine, reduce the first executable core to an episode coordinator, immutable event envelope, model gateway, capability broker, sandbox runtime, external evaluator, and versioned artifact registry, and keep all other taxonomies provisional. Build a competitive coding harness first; instrument it before enabling learning; introduce bounded offline evolution of prompts, skills, retrieval, and routing before harness-code evolution; promote only against an incumbent through held-out and sealed evidence; and treat any future “general problem solver” or AGI claim as a research hypothesis, not an architectural consequence. Knowledge may emerge from accumulated, falsifiable experience across environments, but neither event sourcing, self-modification, nor a competence graph guarantees intelligence.

## 2. Clean definition and non-claims

### 2.1 Proposed definition

A **General Task Solver substrate** is a system that:

1. converts a user goal and observed environment state into proposed actions;
2. executes authorized actions across replaceable environments under explicit resource, security, and cost limits;
3. records enough identity, causality, state, and outcome evidence to audit and resume a run;
4. estimates its uncertainty and can abstain, ask, branch, or escalate;
5. evaluates outcomes with tests and authorities that the candidate cannot silently rewrite;
6. converts repeated evidence into versioned, scoped competence artifacts; and
7. promotes, demotes, or rolls back those artifacts through a statistically defensible external process.

The coding harness is the first environment because repositories offer unusually good instruments: compilers, type checkers, tests, linters, sanitizers, mutation testing, version control, reproducible containers, human review diffs, and production outcomes.

### 2.2 What this definition does not claim

- It does not claim that a harness architecture is AGI.
- It does not equate autonomy with intelligence, tool count with capability, or longer trajectories with better reasoning.
- It does not assume that self-reflection is learning. A reflection is only a candidate hypothesis until external evidence changes a versioned artifact.
- It does not assume that benchmark improvement transfers to deployment.
- It does not assume that biological labels such as hippocampus, executive function, or global workspace are implementable specifications.
- It does not require one model, one planning style, one memory system, or one orchestration topology to work for all tasks.

This restraint matters. The credible long-term claim is that the framework can become a **scientific instrument for studying cumulative machine competence**. Whether that process reaches broadly general intelligence is an empirical question.

## 3. Review method and epistemic boundaries

This report used three bodies of evidence:

- the complete Vanguard v4 project corpus, including its normative documents, decision and rejection registers, convergence evidence, Phase 0 plan, reader packet, and answer key;
- current official documentation and repositories for production coding-agent systems and interoperability protocols; and
- primary or near-primary research on agent interfaces, evaluation, test-time search, prompt and harness evolution, reward hacking, prompt injection, capability security, metacognition, and complementary learning systems.

Claims are separated into four classes:

- **Observed design:** documented behavior of an existing system.
- **Empirical result:** a result reported by a paper, scoped to its benchmark and experimental conditions.
- **Engineering inference:** a recommendation derived from several observations.
- **Research hypothesis:** something Vanguard should test rather than assume.

Preprints are useful signals, not settled science. Vendor documentation describes intended product behavior, not independent proof of quality. Public benchmarks are vulnerable to contamination, task selection effects, infrastructure errors, and optimization against the scoreboard. These limitations are part of the design, not footnotes to it.

## 4. What the competitive field has actually converged on

The field has largely converged on the same visible primitives. A state-of-the-art CLI therefore cannot win merely by having an agent loop, shell access, repository instructions, skills, MCP, subagents, or a permission prompt.

| System | Strong current primitives | Strategic lesson for Vanguard |
|---|---|---|
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) | Repository-aware editing and execution, instruction memory, hooks, subagents with separate context and permissions, sandboxing, and an SDK | Excellent interaction design, model-harness co-design, and extension ergonomics are baseline requirements; instruction files are context, not security policy. |
| [Codex CLI](https://learn.chatgpt.com/docs/codex/cli) | Interactive and headless operation, repository instructions, skills, MCP, review, resumable sessions, subagents, web access, and layered sandbox/approval controls | Sandbox and approval are distinct controls. Cloud setup and agent execution should be separate phases, and parallel agents are a selective tactic rather than a default. |
| [OpenCode](https://opencode.ai/docs/) | Open-source client/server architecture, multi-provider support, primary agents and subagents, skills, plugins, MCP, permissions, LSP integration, and SDK access | Provider neutrality and protocol compatibility reduce adoption friction; broad extensibility without secure defaults also expands the trusted surface. |
| [Grok Build](https://docs.x.ai/build/overview) | TUI, headless and ACP modes, sessions with file snapshots and tool history, skills, plugins, hooks, MCP, and multiple-agent workflows | Session durability, protocol access, and operational visibility are product features, not merely internal plumbing. |
| [Amp](https://ampcode.com/manual) | Durable threads, CLI and SDK surfaces, independent-context subagents, plugins, MCP, and remote execution | Context isolation and resumable remote work are competitive product capabilities; subagents are most useful when work is independently decomposable. |
| [OpenClaw](https://github.com/openclaw/openclaw) | Gateway/session architecture, channels, tools, plugins, skills, and configurable sandboxing | A broad personal-agent surface is powerful but multiplies identity, secret, network, plugin, and prompt-injection risks. Skill visibility is not authorization. |
| [Hermes Agent](https://github.com/NousResearch/hermes-agent) | Model-agnostic agent, memory, skills, session search, and an explicit self-evolution extension | A visible learning loop is attractive, but self-authored memories or skills without held-out promotion evidence are suggestions, not demonstrated improvement. |
| [OpenHands](https://docs.openhands.dev/sdk/arch/events) | Event-sourced agent state, typed tools, immutable configuration, replay-oriented architecture, server/runtime separation | Independent convergence on event-based state is strong support for a durable ledger, but recorded replay must not be confused with reproducing nondeterministic model outputs. |
| [SWE-agent](https://arxiv.org/abs/2405.15793) and [mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent) | Deliberately designed agent-computer interface; a very small implementation can remain competitive | Interface design and model quality often dominate framework complexity. Minimal baselines are mandatory controls against over-engineering. |
| [Aider](https://aider.chat/docs/repomap.html) | Repository maps and role separation between architectural reasoning and editing | Context selection and model-role matching can create more value than adding new agent abstractions. |
| [SWE-ReX](https://swe-rex.com/latest/) | Runtime interface decoupled from sandbox infrastructure | Environment execution should be replaceable without changing cognition or evaluation. |

### 4.1 The real competitive opportunity

The defensible edge is the combination of:

- a fast and pleasant interactive coding product;
- an evidence ledger that can attribute outcomes to exact artifact versions;
- a least-authority execution boundary that remains outside model influence;
- a statistically credible promotion and rollback process;
- an extensible artifact graph that supports bounded self-improvement; and
- a research workbench that can compare models, contexts, tools, policies, and orchestration without silently changing several variables at once.

No incumbent feature list proves that combination works. Vanguard should compete on **verified change throughput**: time, money, and human attention required to produce a correct, safe, maintainable change that is actually accepted.

## 5. Vanguard v4: overall assessment

### 5.1 Strongest contributions

1. **Evaluator exteriority.** A candidate may propose a successor but cannot install itself, change the authoritative evaluator, or widen its own grants. This is the central condition for discussing recursive improvement responsibly.
2. **Evidence-directed competence.** Competence is a scoped, falsifiable claim with provenance, support, counterevidence, validity conditions, and lifecycle—not a flattering entry in a memory file.
3. **Explicit uncertainty.** Task failure, policy denial, evaluator failure, and inconclusive recovery are distinct outcomes. This prevents infrastructure faults from becoming false evidence about intelligence.
4. **Capability-based effects.** Authorization is bound to a concrete effect descriptor rather than to an abstract tool name.
5. **Durable event history.** Transactional persistence, causal identifiers, receipts, and deterministic state reduction make audits and new offline projections possible.
6. **Multi-objective promotion.** Hard constraints precede Pareto selection, avoiding a single scalar reward that can trade security for benchmark points.
7. **Reversal culture.** The ADRs and must-fail tests encode ways the design can be disproved.
8. **No in-episode self-replacement.** Evolution is staged through build, evaluation, canary, promotion, and rollback.
9. **Coding as a laboratory.** The documents correctly resist treating software engineering as the ontology of every future domain.
10. **Honest limits.** The corpus acknowledges evaluator dependence, credit-assignment difficulty, stochastic measurement, and transfer risk.

### 5.2 Central weakness

The corpus tries to protect the future by deciding too much of it before the first useful vertical slice. Its Phase 0 includes a controller, broker, worker perimeter, evaluator identity, transactional event store, schemas, fake and real models, Git, TableWorld, operators, containment reporting, crash recovery, redaction, conformance, property and must-fail tests, plus 203 normative rules. The rule map is admirable governance, but 133 rules initially lacking coverage are also evidence that the specification has outrun implementation. This conflicts with the corpus's own minimalist principle: minimize what must be simultaneously correct before learning from reality.

### 5.3 Recommended top-level decision

**Keep the spine; reopen the ontology.** Treat the current documents as a high-quality design hypothesis library. Freeze only the small set of contracts whose migration cost or safety impact justifies it. Everything else should earn permanence through working increments and comparative experiments.

## 6. Document-by-document disposition

| Vanguard document | What should survive | What should change |
|---|---|---|
| **00 — Registry** | Source precedence, decision provenance, rule identifiers, generated coverage, and explicit status | Stop equating prose freeze with architectural truth. Version contracts semantically and allow migration ADRs without treating section numbering as a system invariant. |
| **01 — Engineering Handbook** | Effect mediation, falsifiability, explicit boundaries, no hidden bypasses | Replace “exactly four” extension kinds and categorical no-DAG language with provisional interfaces and a hybrid orchestration rule. |
| **02 — Charter, Claims, and Non-claims** | Coding-first scope, stated non-claims, measurable hypotheses, reversal conditions | Add product hypotheses: latency, task success, cost, user correction burden, adoption, and compatibility. Generality should remain a research program, not a Phase 0 property. |
| **03 — Architecture Planes and Execution Model** | Observe–propose–authorize–effect–receipt–evaluate protocol; environment adapters; control/workload separation | Keep planes as a conceptual map, not mandatory deployable services. Permit durable state machines for known governance and long-running coordination. Narrow the trusted mediation path to security-relevant effects. |
| **04 — Core Contracts and Wire Schema** | Stable IDs, causality, content hashes, artifact identity, effect descriptors, receipts, versioned schemas | Lock only a minimal envelope first. Keep payloads extensible, retain raw envelopes, and test migrations. Avoid requiring cross-language completeness before the first useful harness. |
| **05 — Kernel, Capabilities, and Security** | Resource-scoped grants, descriptor binding, attenuation, trusted broker, sandbox perimeter, uncertain effect recovery | “Every effect” currently includes reads, model calls, memory, and verification, producing a large choke point and TCB. Pure deterministic computation and non-privileged projections need not traverse the privileged kernel. |
| **06 — Competence, Memory, and Evidence** | Claims with scope and falsification; evidence graphs; staged activation; invalidation and demotion | Implement a simple artifact registry plus episode/evaluation index first. Delay a general competence graph until it beats retrieval baselines on activation quality and maintenance cost. |
| **07 — Loop Engineering and Measurement** | Paired comparisons, preregistration, holdouts, sealed evaluation, canary and rollback, hard constraints, Pareto archive | McNemar is correct only for paired binary outcomes. Add continuous, censored, hierarchical, sequential, and deployment analyses; model variance and practical effect sizes. |
| **08 — Phase 0 Build Plan** | Vertical increments, fake-provider tests, failure injection, trust-boundary tests, no self-improvement in Phase 0 | Split into Phase 0A product/trust slice and 0B evidence laboratory. Move TableWorld, full coverage closure, extensive schemas, and most competence machinery behind demonstrated coding utility. |
| **09 — Decision Register** | Decision ownership, rationale, dependencies, and explicit reversal evidence | Reopen decisions that constrain product-market learning: no graph, no runtime discovery, fixed extension taxonomy, frozen atom set, and hard cross-model transfer. |
| **10 — Deferred and Rejected Register** | Prevent accidental resurrection of known bad ideas; require evidence to reverse a decision | Convert several rejections to scoped choices. Runtime DAGs, discovery, and learned critics are dangerous in specific roles, not universally invalid. |
| **11 — Design Convergence Evidence** | Independent-review trail and explicit challenge process | Convergence among reviewers sharing the same premises is not external validation. Add competing prototypes, red-team reviews, and empirical disconfirmation. |
| **12 — Vision Annex** | Long-range ambition, staged trust, evidence-directed cumulative competence | Separate vision from roadmap. Remove any implication that emergence is guaranteed and define cross-domain milestones that could falsify the trajectory. |
| **Reader packet and answer key** | Valuable comprehension and consistency checks | They test whether a reviewer can reconstruct the design, not whether the design is correct or useful. Add implementation and user-study evidence. |

## 7. Decisions to preserve, revise, defer, and reject

### 7.1 Preserve now

- The evaluator, root policy, grant authority, release signer, and sealed data stay outside the editable artifact graph.
- Work executes in an OS-enforced sandbox with network denied by default and explicit resource limits.
- A capability identifies operation, resource, constraints, origin, expiry, and delegation chain; tool names alone never authorize effects.
- Every security-relevant effect has a proposal, authorization decision, execution receipt, and terminal outcome.
- Events and artifacts are immutable and content-addressed; projections are rebuildable.
- Recovery may report unknown or inconclusive when the outside world cannot be reconciled safely.
- Promotion compares a candidate to an incumbent and is reversible by pointer change.
- Correctness and safety constraints cannot be compensated by lower cost or higher speed.
- Public benchmarks are never the sole promotion authority.

### 7.2 Revise before implementation

**Agent loop versus workflow graph.** A recursive loop is more expressive than a static DAG, but expressiveness does not decide operational suitability. Use a dynamic episode loop for open-ended reasoning and an explicit durable state machine for release governance, human approvals, resumable long-running work, and known compliance paths. A hidden workflow encoded in conditionals is harder to inspect than a small declared graph.

**Exactly four extension forms.** Environment adapters, tools, context sources, and operators are a useful starting taxonomy, not a natural law. Schedulers, evaluators, policies, artifact transformers, optimizers, model providers, storage projections, and human adjudicators should be protocol roles with declared capabilities and trust level. Adding a role requires review but not an ontological crisis.

**Frozen tool atoms and no runtime discovery.** Freeze the exact resolved tool and plugin set **per episode**. Discovery and installation may occur between episodes from signed, allowlisted manifests under operator policy. This preserves reproducibility while supporting MCP, plugins, enterprise integrations, and evolving environments.

**Universal single dispatch.** The trusted broker must mediate privileged side effects and capability sinks. It does not need to own pure transforms, token accounting projections, event queries, or deterministic reducers. Centralizing all computation increases latency, coupling, and the trusted computing base.

**Deterministic replay.** Vanguard can deterministically replay the reducer over recorded events. It generally cannot regenerate identical model completions, remote API behavior, timestamps, or race outcomes. The contract should say **audit replay** and **state reconstruction**, with optional controlled re-execution when the environment is reproducible.

**Cross-model transfer.** Mark artifacts as model-independent, model-family, model-specific, or unknown. Transfer can be a hard gate for artifacts claiming portability and a reporting metric for model-specific optimizations. Otherwise the framework will reject its best co-adapted variants.

**Statistical test selection.** Exact paired McNemar remains one tool for binary outcomes, not the doctrine. Test choice follows endpoint, pairing, censoring, clustering, variance, and stopping rule.

### 7.3 Defer until evidence earns the complexity

- a general competence graph rather than a simpler artifact/evidence registry;
- TableWorld as anything more than a later adapter-conformance test;
- autonomous harness-code rewriting;
- semantic consolidation into generalized knowledge;
- a multi-agent society or fixed supervisor-worker topology;
- cryptographic attestation beyond the threat model and deployment needs;
- cross-domain “problem solver OS” branding;
- online model training or weight updates.

### 7.4 Reject

- self-authored tests as sole promotion evidence;
- an LLM judge as sole authority for correctness or safety;
- candidate access to sealed tasks, evaluator implementation, release credentials, or grant widening;
- scalar reward that permits safety or correctness trade-offs;
- silent memory writes during read-only or advisory turns;
- automatic retention of every reflection;
- benchmark-only optimization;
- a claim that accumulated logs necessarily become knowledge;
- biological analogy used as proof of architecture;
- “AGI” as a Phase exit criterion.

## 8. Recommended minimal foundation

### 8.1 Three trust zones

The six Vanguard planes remain useful for discussing responsibilities, but implementation should begin with three enforceable trust zones:

1. **Trusted control and evidence zone:** policy kernel, capability broker, event append authority, evaluator identity, artifact registry, release pointer, sealed data access.
2. **Mutable cognition zone:** model prompts, context compiler, skills, retrieval, planning and orchestration policy, subagent configuration, learned critics, candidate generators.
3. **Sandboxed workload zone:** repository, shell, language servers, test runners, tools, network proxies, browser or other environment adapters.

~~~mermaid
flowchart TB
    U["User or API"] --> C["Episode coordinator"]
    C --> M["Mutable cognition"]
    M --> P["Effect proposal"]
    P --> B["Capability broker"]
    B --> W["Sandboxed workload"]
    W --> R["Receipt and artifacts"]
    R --> L["Immutable event ledger"]
    L --> E["External evaluation"]
    E --> A["Artifact registry and promotion"]
    A -. "versioned activation" .-> C
~~~

The optimizer reads evidence and proposes candidates, but the promotion service is a distinct authority. A process boundary is required where compromise would alter safety; it is not required merely to make a diagram symmetrical.

### 8.2 Minimal runtime components

| Component | Responsibility | Must remain replaceable? |
|---|---|---|
| **Episode coordinator** | Own the state machine, budgets, leases, stop conditions, checkpoints, and cancellation | Yes; behavior versioned per episode |
| **Model gateway** | Normalize provider calls, identity, capabilities, token/cost data, streaming, retries, and cancellation | Yes; provider-neutral core |
| **Context compiler** | Assemble instructions, repository map, retrieved evidence, active skills, tool schemas, and compression products within a budget | Yes; primary optimization surface |
| **Capability broker** | Authorize concrete privileged effects against immutable policy and grants | Policy and interface stable; implementation small |
| **Sandbox runtime** | Execute tools with filesystem, process, network, CPU, memory, and time containment | Yes; local, container, VM, and remote backends |
| **Event and artifact store** | Append immutable envelopes and store content-addressed blobs; build projections | Storage engine replaceable behind contract |
| **Evaluator and release service** | Run authoritative tests, compare candidate/incumbent, canary, promote, demote, and roll back | Separately identified and inaccessible to candidates |

### 8.3 Minimal stable contracts

Freeze only these concepts at first:

- **RunIdentity:** run, episode, parent, attempt, tenant, project, task, environment snapshot, activated artifact set.
- **EventEnvelope:** event ID, causal parent, monotonic sequence, type, schema version, producer identity, timestamp, payload digest, sensitivity label.
- **ArtifactIdentity:** type, digest, version, dependencies, producer, source evidence, validity scope.
- **CapabilityGrant:** subject, operation, resource selector, constraints, issuance source, expiry, attenuation chain.
- **EffectProposal:** normalized operation, exact resources, arguments digest, expected read/write set, idempotency key, provenance summary.
- **AuthorizationDecision:** policy version, matching grant, allow/deny/ask, reason, approval identity.
- **EffectReceipt:** start and terminal state, environment identity, outputs and errors, artifact digests, reconciliation status.
- **EvaluationResult:** evaluator identity, suite and dataset digest, endpoint vector, uncertainty, validity and leakage metadata.
- **PromotionDecision:** candidate, incumbent, preregistered policy, evidence set, decision, signer, rollout and rollback plan.

The payload schemas should evolve through semantic versioning and migrations. Preserve unknown fields and raw envelopes so that new projections can be computed from old runs.

### 8.4 The mutable artifact graph

Do not hard-code “the seven editable components.” Represent an open, typed dependency graph. Initial artifact types may include:

- system and task prompts;
- repository and user instruction compilers;
- tool descriptions and schemas;
- tool implementations;
- context selection, retrieval, and compaction policies;
- planning and action-selection operators;
- model routing and sampling policy;
- skills and playbooks;
- subagent roles and coordination policy;
- memory extractors and activation rules;
- sandbox images and dependency lockfiles;
- learned critics used for triage; and
- complete harness bundles.

Every run records exact artifact digests. A candidate changes a declared subset, and evaluation attributes evidence to the smallest defensible unit. When interactions matter, use preregistered factorial or ablation experiments rather than pretending that single-component attribution is always possible.

[Agent Harness Engineering](https://arxiv.org/abs/2604.25850) supports the value of exposing editable components and falsifiable contracts rather than treating “the agent” as one opaque treatment. Its reported gains remain benchmark-specific, but the observability principle is sound.

### 8.5 Product compatibility layer

The first coding harness should support the conventions developers already use: repository-local instruction files such as AGENTS.md and CLAUDE.md, SKILL.md-style skills, MCP servers, hooks, headless JSON output, an SDK, CI execution, session resume, Git worktrees, and optional ACP-compatible clients. Compatibility belongs in adapters; it must not leak into the trust kernel.

### 8.6 Initial deployment topology

Begin as a local CLI plus one coordinator daemon, one or more sandboxed worker processes, and a separately identified evaluation/release process. Do not create a microservice per conceptual plane. Split a component only when its trust level, failure isolation, independent scaling, or deployment ownership requires it. Language choice should follow implementation evidence: a memory-safe compiled language is attractive for the broker and process supervisor, while SDKs and experimental cognition components can be polyglot behind versioned protocols. The architecture must not depend on one language runtime.

## 9. Self-improvement architecture

### 9.1 Separate four loops

Self-improving systems become unsafe and scientifically uninterpretable when serving, learning, evaluation, and deployment collapse into one loop.

| Loop | Purpose | May mutate the active harness? |
|---|---|---|
| **Serving loop** | Solve the current task under an immutable run snapshot | No |
| **Episode-learning loop** | Record evidence, candidate memories, corrections, and failure classifications | No; produces quarantined artifacts |
| **Offline optimization loop** | Cluster failures, propose variants, allocate experiments, and maintain a candidate archive | No; creates candidate versions |
| **Release loop** | Evaluate, attest, canary, promote, demote, and roll back | Only through external policy and signed pointer changes |

The active system is never a working directory that rewrites itself. It is a resolved, immutable artifact bundle. An optimizer can construct its successor in an isolated candidate workspace; only the release authority can activate that bundle for future runs.

### 9.2 A safe improvement ladder

| Level | Editable surface | Required evidence | Default status |
|---|---|---|---|
| **L0 — Selection** | Choose among already approved models, skills, tools, and strategies | Online telemetry and prior validity scope | Phase 0 |
| **L1 — Memory** | Add scoped episodic records and candidate semantic claims | Provenance, validation, expiry, conflict checks | Phase 1 |
| **L2 — Context competence** | Prompts, skills, tool descriptions, retrieval, compaction | Paired held-out improvement, hard safety gates | Phase 2 |
| **L3 — Decision competence** | Routing, planning operators, subagent policy, test-time search budget | Multi-seed held-out suite, cost and latency frontier, canary | Phase 2–3 |
| **L4 — Harness implementation** | Tool code, context compiler code, coordinator modules, sandbox images | Static analysis, differential tests, mutation tests, sealed evaluation, attestation, canary and rollback | Phase 3 |
| **L5 — Trust root** | Broker policy, evaluator authority, release signer, sealed-data controls | Human-controlled engineering release only | Never autonomous |

This order follows the evidence, not fashion. [GEPA](https://arxiv.org/abs/2507.19457), [ACE](https://arxiv.org/abs/2510.04618), and [SkillOpt](https://arxiv.org/abs/2605.23904) indicate that structured context, prompts, and skills can be high-leverage improvement surfaces without adding inference-time model calls. [Darwin Gödel Machine](https://arxiv.org/abs/2505.22954), [Meta-Harness](https://arxiv.org/abs/2603.28052), and [Self-Harness](https://arxiv.org/abs/2606.09498) show the promise of broader code-level harness search, but they do not remove the need for independent evaluators, held-out tasks, operational security, or release control.

### 9.3 Candidate generation

The optimizer should be a portfolio rather than a single “reflection” prompt:

- failure-mode clustering over traces, test failures, operator interventions, and production reversions;
- local edits proposed by an LLM under an explicit component contract;
- retrieval of previously successful changes from related but non-identical contexts;
- mutation and crossover over typed artifacts;
- evaluator-guided evolutionary search, as explored by [AlphaEvolve](https://arxiv.org/abs/2506.13131);
- ablations that remove accumulated complexity;
- counterexample-guided repair from deterministic oracles;
- model or role substitution;
- search over context budgets and tool descriptions; and
- human-authored hypotheses.

Every proposal states:

- the artifact subset changed;
- the hypothesized causal mechanism;
- expected wins and possible regressions;
- falsification conditions;
- affected scope;
- required evaluation tier; and
- rollback trigger.

A compact, diverse Pareto archive should retain viable alternatives rather than collapse immediately to one champion. Diversity is valuable only when candidates remain reproducible and their niches are explicit.

### 9.4 Evidence-gated promotion funnel

1. **Construction:** build in an isolated workspace; resolve dependencies; emit a software bill of materials and artifact digest.
2. **Static gates:** schema validation, type checking, policy linting, capability-diff inspection, secret scanning, dependency policy, and forbidden-path checks.
3. **Targeted gates:** tests linked to the change hypothesis, regression tests, property-based and metamorphic checks, mutation score, differential execution against the incumbent, and adversarial tool outputs.
4. **Development evaluation:** fixed paired tasks for rapid iteration. Results are not promotion evidence once repeatedly inspected.
5. **Held-out evaluation:** tasks unavailable to candidate generation, paired by task, environment, seed, and budget.
6. **Sealed audit:** low-leakage suite controlled outside the optimizer, preferably returning only the decision and limited diagnostics. Repeated failures consume a touch budget.
7. **Canary:** bounded real workloads compared with the incumbent, with automatic rollback on correctness, safety, cost, latency, or human-intervention thresholds.
8. **Promotion:** signed activation pointer, never an in-place overwrite.
9. **Post-deployment audit:** compare promotion-time predictions with observed acceptance, corrections, reversions, and incidents.

The importance of independent verification is empirical, not merely philosophical. A study of self-improving code agents found many apparent optimization gains disappeared under stronger evaluation—73.8% in its Kernel-Bench analysis and 46.8% in ALE-Bench—showing the danger of optimizing a proxy rather than the deployed objective ([Reward Hacking in Self-Improving Code Agents](https://openreview.net/forum?id=ikrQWGgxYg)). [SEAL](https://arxiv.org/html/2607.24300v1) explores fixed hidden audits, incumbent comparisons, limited feedback, and rollback in a heuristic-policy setting. That experiment does not prove the mechanism for all coding agents, but it provides a useful adversarial design pattern.

### 9.5 Test-time adaptation is not long-term learning

Parallel attempts, iterative revision, verifier-guided search, and solution merging can improve an individual run, as surveyed in work on [test-time scaling for agents](https://arxiv.org/html/2506.12928v1). They also increase latency and cost and can produce correlated failures. Vanguard should use an expected-value gate:

- estimate uncertainty that another attempt changes the outcome;
- estimate task payoff and failure cost;
- estimate marginal compute, latency, and merge risk;
- branch only when expected value is positive; and
- stop when posterior value falls below budget.

Best-of-N is a runtime search policy. It becomes learned competence only when evidence changes a versioned future policy.

## 10. Measurement and scientific methodology

### 10.1 Primary objective

The north-star metric should be:

> **Cost and elapsed time per verified, accepted change at a bounded safety level.**

“Verified” means the relevant independent oracles passed. “Accepted” means the user or downstream process kept the result. Neither benchmark pass rate nor tokens per answer alone captures value.

### 10.2 Metric vector

Track separate axes instead of one reward:

- **Correctness:** task oracle pass, hidden-test pass, build/type/lint status, defect and regression rate.
- **Security:** denied bypasses, capability violations, secret exposures, sandbox escapes, unsafe approvals, injection success.
- **Quality:** maintainability review, complexity delta, test quality, mutation score, review findings.
- **Efficiency:** tokens, model and tool cost, wall time, CPU, storage, network, number of attempts.
- **Interaction:** time to first useful action, p50/p95 response latency, approval count, clarification burden, cancellations.
- **Autonomy:** human intervention count, correction magnitude, rescue rate, successful resume rate.
- **Deployment value:** merge or acceptance rate, time to merge, revert rate, escaped defect rate, incident rate.
- **Generalization:** live task performance, repository/language/domain transfer, model transfer by portability class.
- **Calibration:** expected versus observed success, selective risk at abstention thresholds, confidence drift.

The dashboard must preserve the vector and the hard constraints. A lower-cost candidate that violates security does not lie on an acceptable Pareto frontier.

### 10.3 Experimental unit and pairing

The experimental unit is the tuple of task, initial environment snapshot, model/provider identity, run artifact bundle, budget, seed or sampling controls, evaluator version, containment profile, and dataset partition. Paired comparisons should share every controllable element except the preregistered treatment.

Vanguard's instrument tuple is a strong idea, but “one changed element if and only if comparable” is too strict for interactions. Use:

- one-factor paired experiments for most changes;
- preregistered factorial designs when components interact;
- ablations to test necessity;
- stratification by repository, language, task class, difficulty, and tool surface; and
- random effects or hierarchical models when repeated tasks, repositories, or models create clusters.

### 10.4 Statistical decision rules

- Use exact McNemar for paired binary outcomes with small discordant counts.
- Use paired bootstrap or permutation intervals for non-normal cost and latency deltas.
- Use survival methods for timeouts and censored long-running tasks.
- Use mixed-effects or hierarchical Bayesian models for repeated repositories, models, and task families.
- Define a minimum practically important effect and perform power analysis before expensive evaluation.
- Use sequential methods with alpha spending or always-valid inference when results are inspected repeatedly; naive repeated peeking inflates false positives, a point illustrated in [Spotify's sequential-testing review](https://engineering.atspotify.com/2023/03/choosing-sequential-testing-framework-comparisons-and-discussions).
- Control the family of hypotheses actually used for a decision; Holm–Bonferroni is reasonable for planned frequentist families but is not a universal replacement for modeling.
- Require both uncertainty bounds and practical effect, not a p-value alone.
- Run A/A experiments to measure infrastructure and model noise.
- Publish negative results and rollbacks in the ledger.

### 10.5 Meta-evaluate the evaluator

The evaluator is not assumed correct because it is external. Track:

- correlation between promotion scores and accepted production outcomes;
- false promotions later rolled back;
- false rejections recovered by human review;
- score sensitivity to evaluator version, environment, and hidden-task rotation;
- leakage indicators and repeated-touch counts;
- mutation-killing ability of tests;
- inter-rater reliability for human or LLM-assisted judgments; and
- blind challenge sets constructed by a separate red team.

If promotion-time performance stops predicting deployment value, freeze automated promotions. The verifier–deployment gap is itself a monitored failure mode.

### 10.6 Human corrections as evidence

The diff between the agent's proposal and the accepted result is dense and valuable, but it is not automatically clean ground truth. Record structured reason codes:

- functional defect;
- missing requirement;
- security or policy correction;
- test inadequacy;
- maintainability;
- architecture preference;
- style or formatting;
- product decision changed;
- environment changed; or
- reviewer disagreement.

Only corrections supported by outcome evidence should become general competence claims. Preference and style signals should remain user-, team-, or repository-scoped.

### 10.7 Data governance and research integrity

Every episode and evaluation item needs ownership, license, consent basis, sensitivity, retention, deletion, and permitted-use metadata. Training, optimization, retrieval, and evaluation are distinct uses and should not be silently conflated. Keep customer repositories out of cross-tenant learning by default; make any contribution explicit and revocable; preserve tenant separation in embeddings, caches, traces, and artifacts; and maintain a deletion path for derived memory where policy requires it. Record benchmark origin and exposure so that a task seen in development cannot later masquerade as sealed evidence. Generated tests need lineage to their source requirements, and licensed skills or code fragments need compatible redistribution terms. A system that cannot explain where an improvement's data came from does not possess auditable knowledge.

## 11. Security model

### 11.1 Threat model

Assume all of the following can be malicious, compromised, or simply wrong:

- issue bodies, README files, source comments, test fixtures, generated logs, web pages, package metadata, and tool output;
- a model completion, including one that appears to quote policy;
- an MCP server or plugin;
- dependencies and build scripts;
- candidate harness code;
- stale memories and poisoned skills;
- an approval request crafted to mislead a human; and
- a remote service returning partial success after a timeout.

The user, deployment administrator, policy kernel, release authority, and evaluator are different principals. Their authority must not be conflated.

### 11.2 Prompt injection: provenance is necessary but insufficient

[AgentDojo](https://arxiv.org/abs/2406.13352) demonstrates that untrusted tool data can redirect an agent toward an attacker's goal. [CaMeL](https://arxiv.org/abs/2503.18813) provides strong evidence for separating control flow derived from trusted intent from untrusted data flow and for capability-constrained effects. Vanguard should adopt the principle while avoiding an overclaim: once mixed text enters an opaque model, block labels do not prove causal isolation.

Use defense in depth:

1. classify origin, integrity, sensitivity, and trust for all external data;
2. keep trusted goal and policy in a separate control representation;
3. bind each privileged proposal to an operator-approved task intent;
4. propagate conservative labels through deterministic transformations;
5. at privileged sinks, validate operation, destination, resource scope, data sensitivity, and goal relevance;
6. prevent untrusted content from granting capabilities or changing policy;
7. isolate secrets from the model unless the exact effect requires them;
8. execute in a sandbox with network and filesystem egress policy;
9. require explicit approval for policy-defined high-impact effects; and
10. continuously red-team with adaptive injections and corrupted tools.

Taint tracking should be **sink-oriented**. It can conservatively say that an output depends on untrusted input; it generally cannot prove which sentence influenced a neural model. When provenance is lost, the system should narrow authority rather than fabricate certainty.

### 11.3 Capability and sandbox rules

Capability security has a mature systems foundation. [Capsicum](https://www.usenix.org/conference/usenixsecurity10/capsicum-practical-capabilities-unix) shows how object capabilities and sandboxing can compartmentalize UNIX applications. For Vanguard:

- grants are unforgeable references or broker-side records, never text asserted by the model;
- delegation can only attenuate operation, resource, duration, budget, and destination;
- approvals authorize the normalized effect descriptor shown to the user, not a later altered command;
- the sandbox enforces filesystem, process, syscall, network, CPU, memory, and wall-clock bounds;
- network access uses destination-aware proxies and egress logs;
- credentials are short-lived, scoped, injected at execution time, and excluded from model-visible history where possible;
- read access and data exfiltration are modeled together; “read-only” is not harmless when network output exists;
- the kernel remains small enough for boundary-focused tests and code review; and
- uncertainty after timeout triggers reconciliation or human escalation, not blind retry of non-idempotent effects.

### 11.4 MCP, plugins, and third-party tools

MCP is an interoperability protocol, not a trust guarantee. The versioned [MCP security guidance](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices) explicitly covers confused-deputy risks and per-client consent. Treat each server as a principal with:

- pinned identity and manifest digest;
- declared capabilities and data destinations;
- transport and authentication policy;
- version and dependency attestation;
- explicit tenant and user binding;
- output provenance labels;
- timeout and retry semantics; and
- sandboxing or process isolation appropriate to its code.

In-process plugins are trusted code and should be rare. Prefer out-of-process adapters with a typed protocol. A skill is context; a tool is executable code; a capability is authority. These are three different things.

### 11.5 Security acceptance tests

The must-fail suite should include:

- descriptor substitution after approval;
- path traversal, symlink, hard-link, mount, and case-normalization attacks;
- shell expansion and argument-boundary attacks;
- network exfiltration through allowed tools;
- malicious MCP results and confused-deputy flows;
- prompt injection in repository files and tool output;
- memory poisoning and stale-skill activation;
- candidate attempts to read sealed tasks or evaluator code;
- capability replay, forgery, expiry, and illegal delegation;
- non-idempotent timeout with ambiguous external state;
- concurrent agents writing overlapping resources;
- redaction bypass through encoding, archives, logs, or diffs; and
- plugin or hook execution outside the declared trust zone.

Security claims should be scoped to a containment profile and adversary model. “Secure” without both is not a useful result.

## 12. Memory, knowledge, and metacognition

### 12.1 Four operational memory classes

| Store | Purpose | Write policy | Typical lifetime |
|---|---|---|---|
| **Working context** | Current goal, observations, active plan, tool results, uncertainty | Episode coordinator; aggressively budgeted | One episode |
| **Episodic evidence** | Immutable runs, events, outcomes, corrections, environment and artifact identities | Append-only evidence path | Long-lived under retention policy |
| **Semantic claims** | Generalized facts or competence claims with scope, support, counterevidence, expiry | Offline consolidation and validation | Until invalidated |
| **Procedural artifacts** | Skills, prompts, operators, routing and tool-use procedures | Versioned candidate and promotion pipeline | Versioned, reversible |

This resembles complementary learning systems only at the level of a useful hypothesis. Neuroscience distinguishes fast acquisition of specific experience from slower integration into structured knowledge; the updated [Complementary Learning Systems review](https://pubmed.ncbi.nlm.nih.gov/27315762/) is relevant inspiration. It does not imply that a SQL event store is a hippocampus or that nightly summarization is cortical consolidation.

### 12.2 Consolidation process

1. Preserve raw episodic evidence with provenance.
2. Detect recurring patterns and contradictions offline.
3. Propose a minimal scoped claim or procedural artifact.
4. Search for counterexamples and near-neighbor failures.
5. Evaluate on held-out episodes or targeted generated tests.
6. Activate with model, environment, repository, and time scope.
7. Monitor prediction quality and invalidate on drift.
8. Keep lineage back to supporting and contradicting episodes.

Memories are selected evidence, not an append-only diary of model opinions. Retrieval quality must be evaluated against simpler baselines, including no memory.

### 12.3 Operational metacognition

Metacognition should mean measurable monitoring and control of object-level problem solving:

- estimate the probability that a plan, tool call, test interpretation, or final result is correct;
- identify uncertainty source: missing information, ambiguous requirement, model disagreement, flaky tool, environment drift, or policy limit;
- choose a control action: inspect, test, branch, ask, abstain, escalate, or stop;
- compare predicted confidence with observed outcome; and
- update calibration by task family and substrate.

Human research distinguishes confidence bias from metacognitive sensitivity—the ability of confidence to discriminate correct from incorrect trials ([How to Measure Metacognition](https://pmc.ncbi.nlm.nih.gov/articles/PMC4097944/)). The engineering analog is to measure Brier score, calibration error, risk-coverage curves, and selective accuracy, not the eloquence of self-critique.

The system should store decision summaries, evidence references, uncertainty, and alternatives sufficient for audit. It should not depend on retaining private chain-of-thought as a privileged truth source.

### 12.4 Competence graph: earn it

A graph becomes justified when it improves at least one of:

- artifact activation precision;
- transfer to new tasks;
- invalidation speed after dependency or model drift;
- conflict detection;
- explanation of why an artifact was selected; or
- experiment allocation.

Until then, a relational artifact registry with typed links and indexed evidence is simpler. Graph terminology should describe queries that exist, not ambition.

## 13. Cross-disciplinary foundations without cargo cults

| Field | Transferable principle | Concrete design consequence | What not to infer |
|---|---|---|---|
| **Philosophy of science** | Knowledge advances through risky predictions, attempted falsification, and revision | Every improvement proposal includes mechanism, prediction, counterexample search, and reversal condition | Passing today's tests makes a claim true forever |
| **Bayesian epistemology** | Beliefs should update with evidence and preserve uncertainty | Scoped confidence, prior evidence, likelihood of outcomes, posterior calibration, explicit unknown | One subjective score is an objective probability |
| **Lakatosian research programs** | Protect a small productive core while changing auxiliary hypotheses | Keep the trust root stable; allow cognition, memory, routing, and evaluation hypotheses to compete | The “hard core” may never be challenged |
| **Neuroscience / CLS** | Rapid episode storage and slower integration solve different problems | Separate immutable episodes from validated semantic and procedural consolidation | Software components map one-to-one to brain regions |
| **Psychology of metacognition** | Confidence has bias and sensitivity; monitoring is distinct from task performance | Measure calibration and selective risk; train ask/abstain/escalate policies | Verbal self-reflection demonstrates self-awareness |
| **Cognitive psychology** | Working resources are limited and interference matters | Budget context; retrieve selectively; isolate subtask contexts; test compaction loss | Larger context is always better memory |
| **Control theory** | A controller needs an estimated state, observable plant, bounded actions, and stability under feedback | Explicit environment snapshots, receipts, uncertainty, stop rules, rate limits, rollback | More frequent feedback always improves stability |
| **Decision theory / economics** | Information and computation have opportunity cost | Expected-value gates for search, subagents, tests, and human questions | Maximum compute means maximum rationality |
| **Evolutionary computation** | Variation, selection, niches, and archives can preserve diverse solutions | Typed mutation, Pareto archive, novelty and coverage, incumbent comparison | Evolution supplies goals or guarantees progress |
| **Machine learning** | Generalization depends on train/eval separation and distribution | DEV, held-out, sealed, live, and deployment partitions; contamination tracking | A benchmark rank is deployment competence |
| **Security engineering** | Least authority, complete mediation, compartmentalization, and defense in depth | Resource capabilities, brokered sinks, sandbox, short-lived secrets, adversarial testing | Prompt instructions are an enforcement boundary |
| **Distributed systems** | Partial failure, retries, ordering, and identity are first-class | Idempotency keys, effect receipts, leases, WAL, reconciliation, explicit unknown outcomes | Exactly-once external effects are generally available |
| **Software architecture** | Stable boundaries should follow reasons to change and trust, not nouns | Small kernel; ports/adapters; semantic versioning; contract tests; projections | More services mean more decoupling |
| **Human-computer interaction** | Trust depends on legibility, control, latency, and recoverability | Fast feedback, concise approvals, inspectable diffs, cancel/resume, undo, provenance explanations | Maximum autonomy is the best experience |

The correct use of multiple sciences is triangulation: derive candidate mechanisms, make them operational, and test them. The incorrect use is naming modules after mental faculties and assuming the desired capability emerges.

## 14. The SOTA coding harness product

### 14.1 Minimum competitive feature set

The first product must be excellent before it is self-improving:

- fast TUI plus headless mode and stable SDK;
- robust repository inspection, search, patching, Git diff, worktree, and review;
- shell, test, type, lint, build, and optional LSP tools;
- provider-neutral model gateway with model-capability probes;
- repository/user instructions, skills, MCP, hooks, and policy adapters;
- streaming progress, cancellation, resume, checkpoints, and crash recovery;
- plan and action visibility without exposing private reasoning;
- explicit permission modes and sandbox status;
- concise, descriptor-bound approvals;
- citations from conclusions to files, commands, tests, and artifacts;
- separate read-only review and mutating execution modes;
- cost, token, latency, test, and intervention telemetry;
- safe parallel attempts in isolated worktrees; and
- deterministic fake-model and fake-tool fixtures for framework tests.

### 14.2 Lean interactive path, asynchronous governance

The CLI loses if every file read waits on a remote governance service. The synchronous path should:

- compile context locally;
- stream model output immediately;
- authorize low-risk effects through cached, exact grants;
- append events in batches without losing crash safety;
- run the smallest relevant checks first; and
- defer heavy evaluation, consolidation, clustering, and promotion to asynchronous workers.

Set explicit product budgets: startup latency, time to first token, time to first tool action, approval round trips, p95 resume time, event-write overhead, and cost per accepted change. Trust should be visible but not theatrical.

### 14.3 Adaptive multi-agent orchestration

Subagents are useful when they isolate context or parallelize independent work. They are harmful when they duplicate search, compete for the same files, or produce an expensive merge problem. The coordinator should estimate:

- task decomposability;
- write-set overlap;
- uncertainty and expected value of diversity;
- model and tool cost;
- latency target;
- merge/verifier capacity; and
- security scope.

Default to parallel read-heavy research and independent worktree branches. Serialize shared-resource mutation unless commutativity or compensation is proven. Compare a multi-agent policy against the strongest single-agent baseline; otherwise topology becomes ceremony.

### 14.4 Context engineering as a first-class subsystem

The context compiler should be separately versioned and evaluated. Inputs include:

- trusted user goal and constraints;
- repository instruction hierarchy;
- compact repository map;
- relevant files and symbols;
- retrieved episodes and active competence artifacts;
- current plan and state summary;
- tool descriptions and capability visibility;
- security provenance;
- remaining budget; and
- compression products with loss indicators.

Measure not only task success but context precision, missing-critical-context rate, irrelevant-token rate, compaction recovery, and sensitivity to ordering. Optional LSP data should earn its token and latency cost; it is not automatically superior to search and repository maps.

## 15. Recommended delivery roadmap

### Phase 0A — Useful and trustworthy vertical slice

**Build:**

- one CLI with interactive and headless modes;
- one real model provider plus a deterministic fake;
- one Git workspace adapter;
- read, search, patch, shell, and test tools;
- basic repository instructions and skills;
- immutable run snapshot and minimal event envelope;
- local transactional event store and content-addressed artifacts;
- sandboxed worker, descriptor-bound approvals, and network-off default;
- resume, cancel, timeout, and unknown-effect handling; and
- an external test evaluator.

**Do not build:** self-improvement, competence graph, TableWorld, general subagents, automatic semantic memory, or a complete universal schema catalog.

**Exit only when:**

- representative repository tasks complete end to end;
- no privileged effect bypass exists in the tested surface;
- interrupted runs resume without inventing outcomes;
- a user can inspect exactly what changed and why;
- event overhead meets the latency budget;
- the product beats a simple baseline on verified-change throughput; and
- at least one independent reviewer can extend a tool through the public contract.

### Phase 0B — Evidence laboratory

Add:

- exact artifact identities and rebuildable projections;
- paired evaluation runner and A/A noise measurement;
- DEV, HOLDOUT, SEALED, live, and deployment partitions;
- mutation, metamorphic, property, and differential oracles;
- human-correction capture with reason codes;
- meta-evaluator dashboard;
- prompt-injection and capability adversarial suite;
- canary and rollback infrastructure; and
- a minimal Pareto archive with no autonomous promotion.

Exit when promotion-time evidence predicts real acceptance better than baseline heuristics and the evaluator catches seeded reward-hacking mutations.

### Phase 1 — Competitive coding product

Add:

- additional model providers and routing;
- MCP and hook adapters;
- optional LSP and repository maps;
- worktrees and adaptive subagents;
- CI, server, and SDK surfaces;
- enterprise policy, tenancy, retention, and secret controls;
- long-horizon checkpointing; and
- targeted compatibility with established instruction and skill formats.

Exit on user-facing metrics: accepted-change rate, latency, cost, intervention, revert rate, and retention—not architecture completion.

### Phase 2 — Bounded competence evolution

Enable offline proposals for:

- prompts and skills;
- tool descriptions;
- retrieval and compaction;
- model routing;
- context budgets; and
- orchestration policy.

All changes pass the external promotion funnel. Start with human approval of every promotion. Automate only low-risk artifact classes after measured false-promotion and rollback rates are acceptable.

### Phase 3 — Harness implementation evolution

Permit isolated candidate edits to selected harness modules. Require:

- declared mutable boundaries;
- stronger static and dynamic analysis;
- capability-diff review;
- seeded sabotage tests;
- model-swap reporting;
- sealed low-leakage audits;
- cryptographic artifact identity;
- staged canaries; and
- automatic rollback.

The trust root and evaluator authority remain human-controlled.

### Phase 4 — Cross-domain general task solving

Introduce one genuinely different environment at a time—such as structured data reconciliation, controlled browser workflows, scientific data analysis, or operations incident response. The purpose is to test which contracts transfer.

TableWorld can be an inexpensive adapter-conformance witness, but success there does not demonstrate general problem solving. A cross-domain milestone requires:

- no core trust-contract change;
- competitive task performance against a domain-specific baseline;
- domain-native evaluators;
- calibrated abstention;
- transfer of at least some artifacts with measured benefit;
- bounded security and data policy; and
- an honest record of domain-specific additions.

Call the system an operating system only if it eventually owns durable scheduling, resource allocation, isolation, lifecycle, identity, and inter-process protocols across applications. Until then, “framework” or “runtime” is more accurate.

## 16. Research program and falsifiable hypotheses

| ID | Hypothesis | Experiment | Reversal or kill criterion |
|---|---|---|---|
| **H1** | Event-sourced runs materially improve diagnosis and recovery | Randomized internal debugging study against conventional logs | No reduction in diagnosis time or recovery accuracy after accounting for implementation cost |
| **H2** | Descriptor-bound capabilities reduce harmful actions without unacceptable friction | Adversarial injection suite plus user approval study | Bypass remains common or approval burden destroys task throughput |
| **H3** | A separately optimized context compiler improves verified changes more efficiently than a larger generic context | Paired tasks across repositories and models | Gains disappear on held-out tasks or cost/latency frontier worsens |
| **H4** | Offline skill/prompt evolution produces cumulative competence | Candidate/incumbent held-out and canary sequence | Improvements fail to persist, transfer, or predict deployment outcomes |
| **H5** | A competence graph improves artifact activation over simple retrieval | A/B activation precision, task outcomes, maintenance cost | No practical gain over relational metadata and retrieval |
| **H6** | EV-gated parallelism dominates always-one and always-N policies | Paired tasks stratified by uncertainty and decomposability | Routing overhead or correlated failures erase frontier gains |
| **H7** | Sealed low-feedback audits reduce reward hacking | Seed proxy-exploiting candidates and compare promotion pipelines | Attack variants pass at unacceptable rates or leakage grows with touches |
| **H8** | Model-scoped and portable artifact classes improve both specialization and transfer reporting | Evaluate artifacts across model families with declared scope | Scope labels do not predict transfer or add useful decisions |
| **H9** | Fast/slow memory separation improves long-term performance without poisoning | Longitudinal conflict, drift, and retrieval study | Memory causes more regressions, privacy risk, or context waste than benefit |
| **H10** | Core contracts transfer beyond coding | Add a non-code environment without changing the minimal event/capability/evaluation envelope | Core changes are repeatedly required or domain-specific framework wins decisively |
| **H11** | Metacognitive calibration reduces costly failures | Compare confidence-aware ask/abstain/branch policy with fixed policy | Calibration fails under shift or intervention cost exceeds avoided failures |
| **H12** | Harness-code evolution can be made operationally safer than manual-only iteration | Shadow candidates, sealed sabotage suite, canary rollback study | False promotions or security regressions exceed agreed risk budget |

Every research cycle should publish the hypothesis, treatment, instrument tuple, dataset partitions, stopping rule, effect threshold, result, counterevidence, and decision. Failed hypotheses are durable knowledge if the experiment is reproducible.

## 17. Principal risks and mitigations

| Risk | Why it matters | Primary mitigation |
|---|---|---|
| **Specification capture** | The team optimizes compliance with Vanguard prose rather than user outcomes | Minimal vertical slice, independent baselines, reopen decisions through evidence |
| **Reward hacking** | Candidate improves the proxy or disables detection | External evaluator, seeded sabotage, mutation tests, sealed audit, canary |
| **Evaluator overfitting** | Repeated feedback leaks the holdout | Partition rotation, touch budgets, live tasks, one-bit sealed decisions |
| **Prompt injection** | Untrusted repository/tool content redirects privileged actions | Trusted intent separation, sink checks, capabilities, sandbox, egress control |
| **TCB growth** | Universal mediation becomes an unauditable monolith | Mediate privileged sinks only; size and dependency budget; boundary tests |
| **False learning** | Reflections and noisy corrections become “knowledge” | Quarantine, counterexample search, held-out validation, scope and expiry |
| **Statistical noise** | Archive fills with sampling artifacts | Pairing, power/MDE, variance models, sequential rules, A/A tests |
| **Benchmark contamination** | Score improves while deployment value does not | Live and internal tasks, contamination metadata, deployment correlation |
| **Latency collapse** | Governance makes the CLI unpleasant | Lean sync path, async evaluation, explicit performance budgets |
| **Multi-agent cost explosion** | Parallelism duplicates work and complicates merges | EV gating, isolated write sets, single-agent baseline |
| **Model lock-in** | Harness co-adapts invisibly to one provider | Provider contract, capability probes, artifact portability classes |
| **Privacy and secret leakage** | Durable logs and tools increase exposure | Data minimization, sensitivity labels, retention, encryption, short-lived credentials |
| **Ontology rigidity** | Early extension taxonomy blocks future domains | Open typed roles, versioned manifests, empirical contract evolution |
| **AGI narrative pressure** | Vision substitutes for measurable progress | Explicit non-claims, cross-domain falsification gates, external review |

## 18. Decisions recommended now

1. Adopt the clean General Task Solver definition in Section 2 as the working concept.
2. Retain Vanguard's evaluator exteriority, capability boundary, immutable evidence, explicit uncertainty, and external release pipeline.
3. Reclassify the v4 corpus from frozen implementation specification to versioned design hypothesis baseline.
4. Split Phase 0 into a useful coding vertical slice and a later evidence laboratory.
5. Lock only minimal identity, event, artifact, capability, receipt, evaluation, and promotion contracts.
6. Use a dynamic agent loop inside an explicit durable episode/release state machine.
7. Freeze exact extensions per run, while allowing signed discovery and installation between runs.
8. Keep the synchronous CLI lean and move consolidation, optimization, and promotion off the serving path.
9. Make verified accepted changes, cost, latency, intervention, safety, and deployment outcomes the primary scorecard.
10. Begin learning with prompts, skills, retrieval, context, and routing; defer harness-code evolution.
11. Keep a contextual Pareto archive and compare every candidate against an incumbent.
12. Treat learned critics as triage or search signals, never sole authorities.
13. Make confidence calibration, abstention, and escalation operational metacognitive capabilities.
14. Use neuroscience, psychology, philosophy, and control theory to generate testable mechanisms, not module names.
15. Require a non-code environment to prove contract transfer, but do not interpret a toy adapter as evidence of AGI.

## 19. Final recommendation

Vanguard should become two things at once, but in the correct order: first, a superb coding-agent product whose work is secure, inspectable, resumable, and measurably useful; second, an experimental platform that can improve versioned competence without allowing candidates to control the evidence that promotes them. Its foundation should be minimal in mechanism and strict at trust boundaries: immutable run identities and events, a small capability broker, replaceable model and environment adapters, sandboxed effects, external evaluators, and reversible artifact activation. Everything resembling cognition—context construction, planning, memory, tools, skills, routing, subagents, and eventually selected harness code—should remain replaceable and experimentally attributable. The scientific path is cumulative but not magical: preserve episodes, propose scoped hypotheses, search for counterexamples, compare against incumbents, quantify uncertainty, deploy cautiously, and invalidate beliefs when reality disagrees. If this process eventually produces robust transfer across domains, calibrated self-monitoring, and increasingly efficient creation of new competence, Vanguard will have earned the right to call itself a general task-solving substrate. Until then, the honest and strategically stronger claim is that it is building the best instrument for discovering whether such cumulative competence is possible.

---

## Appendix A — External research and technical sources

### Production systems and protocols

- Anthropic, [Claude Code overview](https://docs.anthropic.com/en/docs/claude-code/overview), [hooks](https://docs.anthropic.com/en/docs/claude-code/hooks), [subagents](https://docs.anthropic.com/en/docs/claude-code/sub-agents), [memory](https://docs.anthropic.com/en/docs/claude-code/memory), and [security](https://docs.anthropic.com/en/docs/claude-code/security).
- OpenAI, [Codex CLI](https://learn.chatgpt.com/docs/codex/cli), [agent approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security), and [subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents).
- OpenCode, [documentation](https://opencode.ai/docs/), [agents](https://opencode.ai/docs/agents/), [skills](https://opencode.ai/docs/skills/), [plugins](https://opencode.ai/docs/plugins/), and [server/SDK](https://opencode.ai/docs/server/).
- xAI, [Grok Build overview](https://docs.x.ai/build/overview), [CLI reference](https://docs.x.ai/build/cli/reference), [sessions](https://docs.x.ai/build/features/sessions), and [skills/plugins/marketplaces](https://docs.x.ai/build/features/skills-plugins-marketplaces).
- Amp, [Owner's Manual](https://ampcode.com/manual) and [SDK](https://ampcode.com/manual/sdk).
- Nous Research, [Hermes Agent](https://github.com/NousResearch/hermes-agent) and [self-evolution extension](https://github.com/NousResearch/hermes-agent-self-evolution).
- OpenClaw, [repository](https://github.com/openclaw/openclaw), [gateway security](https://docs.openclaw.ai/gateway/security), [sandboxing](https://docs.openclaw.ai/gateway/sandboxing), and [skills](https://docs.openclaw.ai/tools/skills).
- OpenHands, [event architecture](https://docs.openhands.dev/sdk/arch/events) and [software-agent SDK paper](https://arxiv.org/html/2511.03690v2).
- SWE-agent, [Agent-Computer Interfaces Enable Automated Software Engineering](https://arxiv.org/abs/2405.15793).
- Aider, [repository map](https://aider.chat/docs/repomap.html) and [architect/editor mode](https://aider.chat/2024/09/26/architect.html).
- SWE-ReX, [runtime documentation](https://swe-rex.com/latest/).
- Model Context Protocol, [security best practices](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices).

### Self-improvement, search, and evaluation

- Zhang et al., [Darwin Gödel Machine](https://arxiv.org/abs/2505.22954).
- DeepMind, [AlphaEvolve](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/) and [technical paper](https://arxiv.org/abs/2506.13131).
- Agrawal et al., [GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning](https://arxiv.org/abs/2507.19457).
- [Agent Harness Engineering](https://arxiv.org/abs/2604.25850).
- [Self-Harness](https://arxiv.org/abs/2606.09498).
- [Meta-Harness](https://arxiv.org/abs/2603.28052).
- [ACE: Agentic Context Engineering](https://arxiv.org/abs/2510.04618).
- [SkillOpt](https://arxiv.org/abs/2605.23904).
- [Reward Hacking in Self-Improving Code Agents](https://openreview.net/forum?id=ikrQWGgxYg).
- [SEAL: Self-Authored Verification Is Unreliable for Self-Improving Agents](https://arxiv.org/html/2607.24300v1).
- [Test-Time Scaling for Agents](https://arxiv.org/html/2506.12928v1).
- Microsoft, [SWE-bench-Live](https://github.com/microsoft/swe-bench-live).
- [SWE-bench](https://www.swebench.com/).

### Security, cognition, and scientific method

- Debenedetti et al., [AgentDojo](https://arxiv.org/abs/2406.13352).
- Debenedetti et al., [Defeating Prompt Injections by Design](https://arxiv.org/abs/2503.18813).
- Watson et al., [Capsicum: Practical Capabilities for UNIX](https://www.usenix.org/conference/usenixsecurity10/capsicum-practical-capabilities-unix).
- Kumaran, Hassabis, and McClelland, [What Learning Systems Do Intelligent Agents Need? Complementary Learning Systems Theory Updated](https://pubmed.ncbi.nlm.nih.gov/27315762/).
- Fleming and Lau, [How to Measure Metacognition](https://pmc.ncbi.nlm.nih.gov/articles/PMC4097944/).
- Popper, *The Logic of Scientific Discovery*.
- Lakatos, *The Methodology of Scientific Research Programmes*.

## Appendix B — Vanguard v4 sources reviewed

- 00 — Vanguard Registry
- 01 — Vanguard Engineering Handbook
- 02 — Vanguard Charter, Claims, and Non-claims
- 03 — Vanguard Architecture Planes and Execution Model
- 04 — Vanguard Core Contracts and Wire Schema
- 05 — Vanguard Kernel, Capabilities, and Security
- 06 — Vanguard Competence, Memory, and Evidence
- 07 — Vanguard Loop Engineering and Measurement
- 08 — Vanguard Phase 0 Build Plan
- 09 — Vanguard Decision Register
- 10 — Vanguard Deferred and Rejected Register
- 11 — Vanguard Design Convergence Evidence
- 12 — Vanguard Vision Annex
- Reader Packet
- Answer Key
- README
