---
id: draft.audit.aether-sota-agentic-coding-development-plan-2026-09-06
class: report
authority: non-canonical
canonical_for: []
status: historical-reference
owner: repository-governance
version: "1.1.0"
last_verified: 2026-09-06
subject_head: "dfb0bb64fc82398b9a05f1e3457f4f45babfcbca"
subject_branch: main
report_revision_head: "2a5fb1ff78b5f7987db547b1ff86b297aad175c1"
evidence_boundary: audited-source-plus-reproduced-local-gates
---

# AETHER SOTA Agentic Coding Architecture and Development Plan Audit

> [!IMPORTANT]
> **Document Status: HISTORICAL REPORT — RECOMENDATIONS REALIZED (2026-09-11 | HEAD: `1e257e76`)**
> - **Audited Subject:** `dfb0bb64` (2026-09-06)
> - **Current Implementation Truth:**
>   - **DONE:** The "next moves" described in §Abstract (restoring product truth boundary, repairing boundary violations, closing gates) are fully delivered. `MS-BASELINE` and `MS-CONTEXT` are closed.
>   - **ACTIVE RUNWAY:** `MS-CONTROL` (T-26/T-27).
>   - **PROPOSAL SCOPE:** Topics in this document touching multi-agent swarms, complex delegation, and CAS belong to the post-control horizon (FH-1).
> - **Authority:** Non-canonical auxiliary report (`authority: non-canonical`).

## Abstract

This auxiliary report evaluates AETHER/Vanguard's architecture, execution runway, coding-agent product, capability system, verification program, and performance claims against modern agentic-software practice. It then gives a dependency-ordered path from mechanism-rich prototype to empirically qualified coding-agent framework.

The conclusion is two-sided. AETHER's small capability-aware kernel, mediated effects, monotonic budget attenuation, event-derived state, durable continuation, exterior evaluation, and exact-subject evidence form a strong architecture. These choices agree with classical security engineering, ports-and-adapters, event sourcing, TDD, provenance standards, and current frontier-agent engineering guidance.

At the audited commit, however, delivered SOTA performance is unproved: five boundary violations were reproducible, four related Python product tests and three TypeScript CLI test files failed, the documentation metadata gate failed, command help invoked execution, LDA health surfaces disagreed, no accepted live L0 or L2 control disposition existed, and the tools-side autofix proficiency bypassed the production trust spine it was described as exemplifying.

The next move is to restore the public product's truth boundary and repository gates, then obtain exact-subject live evidence before adding repository intelligence, capability composition, or multi-agent treatments. The project already has substantial mechanism; it now needs evidence that binds the shipped path, measured subject, and claimed outcome.

This file is non-canonical. It does not authorize implementation, alter milestone status, or supersede `VISION.md`, `AGENTS.md`, or the five execution-runway files. It records an audit and a proposed implementation plan for investigation.

---

## 1. Audit question, subject, and standard of proof

### 1.1 Questions answered

The investigation asks five questions:

1. Are `technical.md`, `spec.md`, `tasks.md`, `backlog.md`, and `milestones.md` mutually aligned and usable as an execution control plane?
2. Does the as-built framework embody sound architecture for general AI agents, not merely one coding workflow?
3. Was the Coding Max product path at the audited commit truthful, secure, recoverable, and competitive?
4. Is the Skills → Techniques → Proficiencies → Mastery capability model production-grade or still experimental?
5. What should be implemented next, in what dependency order, and with which proof obligations?

### 1.2 Audited subject

The primary subject is Git commit:

```text
dfb0bb64fc82398b9a05f1e3457f4f45babfcbca
branch: main
date inspected: 2026-09-06
```

The worktree was initially clean. Some validation commands subsequently changed `tools/002_LLM_API_MOCK/lam.sqlite` and created BAAC run directories; those outputs were excluded from qualifying evidence. This report was later committed at `2a5fb1ff`. Its findings remain scoped to the audited source commit above and must be re-run before being asserted about a later HEAD.

### 1.3 Epistemic classes

This report uses the following evidence classes:

| Class | Meaning |
|---|---|
| `FACT` | Directly observed in the audited source, Git identity, or command output. |
| `REPRODUCED` | A command was executed during the audit and produced the stated result. |
| `INFERENCE` | A conclusion logically derived from facts but not itself an executed observation. |
| `PROPOSAL` | Recommended future work; not a statement about current code. |
| `EXTERNAL` | A claim supported by the cited paper, standard, official documentation, or publisher record. |
| `UNKNOWN` | Evidence was absent, stale, contradictory, or not executed. |

The authority ordering follows repository law:

$$
\text{Vision and normative law}
\succ
\text{canonical architecture}
\succ
\text{current source}
\succ
\text{tests as falsifiers}
\succ
\text{generated indexes and historical reports}.
$$

Generated knowledge is useful for routing but cannot override current source. A green unit test establishes only the predicate actually asserted by that test. It cannot silently establish product utility, benchmark validity, sandbox isolation, or rollback correctness.

### 1.4 Reproduced command evidence

The following results were directly reproduced:

| Command or surface | Result |
|---|---|
| `git rev-parse HEAD` | `dfb0bb64fc82398b9a05f1e3457f4f45babfcbca` |
| `check_tcb_budget.py` | PASS; 1,386 logical kernel LOC, ceiling 1,438 |
| `check_boundaries.py` | FAIL; five violations |
| Wave-2 focused Python set | PASS; 31/31 |
| Coding Max facade + RF-90 set | FAIL; 4/14 |
| Domain blindness | PASS |
| Isolation policy | PASS |
| Markdown links | PASS |
| Stale-path checker | PASS |
| Duplication checker | PASS |
| Execution-truth checker | PASS |
| Event coverage | PASS |
| Falsifier-ID checker | PASS |
| `npm run typecheck` | PASS across all workspaces |
| `npm --workspace @vanguard/cli test` | FAIL; `transport`, `wave2`, and `wave4` test files |
| Documentation metadata checker | FAIL; twelve violations under `docs/research/`; this did not by itself prove drift in the five execution files |
| `node vanguard/clients/cli/dist/src/main.js code --help` | emitted `[complete] instrument_error, 0 turns, unknown`; this tested the built CLI entry point, not an installed `aether` wrapper |
| Capability catalog | 10 registered entries, 4 executable runners |
| Capability prompt prefix | 2,180/4,096 characters |
| LDA `doctor` | reports healthy and current workspace HEAD |
| LDA `identity` | reports index bound to `622131da`, therefore stale versus `dfb0bb64` |

The full `just verify` gate was not claimed successful because constituent gates had already failed. The TypeScript result above identifies failing files, not root causes; those require targeted diagnosis.

---

## 2. Theoretical foundation

### 2.1 Hexagonal architecture: semantic inside, technology outside

Alistair Cockburn's original Ports and Adapters article defines the architectural goal as allowing an application to be driven by users, programs, batch processes, and automated tests while remaining independent of UI and database technologies. The key is not the six-sided drawing; it is the separation between semantic application behavior and replaceable driving or driven adapters. See [Cockburn, “Hexagonal Architecture,” HaT Technical Report 2005.02](https://alistair.cockburn.us/hexagonal-architecture).

For AETHER, let the dependency graph be $G=(V,E)$ and assign each module a layer rank $r(v)$. A permitted dependency must satisfy a repository-specific partial order:

$$
(u,v)\in E \Rightarrow r(v) \le r(u)
$$

with additional asymmetric rules for adapters and application clients. The practical invariant is:

```text
domain ← ports ← kernel ← agency ← runtime → adapters
                                     ↑
                                  apps/clients
```

An application is a driver of runtime. Therefore:

$$
E_{runtime\rightarrow apps}=\varnothing.
$$

The audited import from `runtime/cli.py` to `apps/coding_max/facade.py` is not merely a style defect. It reverses the driver relationship and makes the runtime aware of one product client. Similarly, a benchmark that imports a private runtime helper does not measure the public port; it measures an implementation detail.

Cockburn also warns that architectural promises decay without a detection mechanism. AETHER's boundary linter is therefore not ancillary tooling; it is the executable form of the architecture. A boundary exception added only to legalize current code would destroy the falsifier and preserve the defect.

### 2.2 SOLID and Clean Architecture: apply principles to change reasons

SOLID is best used here as a diagnostic vocabulary rather than a demand for more interfaces:

- **Single Responsibility:** `EpisodeEngine` decides turn progression; it should not grade task success. `ApplicationService` coordinates application operations; it should not implement provider HTTP. A CLI parses and renders operator intent; it should not become runtime authority.
- **Open/Closed:** new model providers and repository indexes should enter through ports and adapters, without editing kernel dispatch semantics.
- **Liskov Substitution:** fake, cassette, local, and hosted model adapters must preserve the same typed success and failure contract. A fake returning `finish` cannot receive privileged completion semantics unavailable to a real adapter.
- **Interface Segregation:** read-only investigation should not receive write or shell authority. Repository-intelligence observations should not expose index database handles.
- **Dependency Inversion:** high-level execution policy depends on `ModelPort`, `IndexPort`, `EvaluatorPort`, and store ports rather than concrete infrastructure.

The practical warning is that “clean architecture” does not mean adding one abstraction per class. Excess indirection can obscure the model input, tool calls, and state transitions. Anthropic's production guidance makes the same point for agent frameworks: begin with simple composable patterns and add complexity only when it demonstrates value. See [Anthropic, “Building effective agents”](https://www.anthropic.com/engineering/building-effective-agents).

The relevant optimization target is thus not interface count but change amplification:

$$
A_c = \frac{|\text{files changed}| + \lambda|\text{public contracts changed}|}
{|\text{independent behavior changes}|}.
$$

A good port lowers future $A_c$. A wrapper that only renames an existing function increases $A_c$ and consumes context without reducing coupling.

### 2.3 Test-driven development and scientific falsification

Kent Beck's TDD method gives a disciplined micro-cycle: express a behavioral expectation, observe it fail for the right reason, implement the smallest causal change, then refactor under a green suite. The publisher record is [Beck, *Test-Driven Development: By Example*, Addison-Wesley](https://www.pearson.com/en-gb/subject-catalog/p/test-driven-development-by-example/P200000009421/9780321146533).

For an agentic system, conventional TDD must be extended because the system is stochastic, stateful, tool-using, and capable of mutating its evaluator. A sound coding-agent falsifier binds at least:

$$
V = H(
\text{task},
\text{source revision},
\text{workspace preimage},
\text{patch postimage},
\text{test argv},
\text{oracle},
\text{environment},
\text{run identity}
).
$$

The verification receipt is valid only if all referenced identities still resolve and the relevant test actually executed. “Green” without the command, workspace, task, and postimage is anecdote rather than proof.

There are four distinct layers of testing:

1. **Mechanism unit tests:** Does a parser, budget function, reducer, or policy behave locally?
2. **Contract tests:** Can adapters substitute behind a port, including typed failure semantics?
3. **Product-path tests:** Does the shipped CLI/API traverse the same composition and produce truthful outputs?
4. **Empirical agent evaluations:** Can a model+harness+environment solve frozen tasks under measured cost and uncertainty?

The existing capability test that manually writes and restores a temporary file establishes only that Python file writes are reversible in that fixture. It does not test the actual autofix runner, subprocess tree cleanup, index rollback, multi-file rollback, external side effects, or crash recovery. Calling that “autofix rollback verified” commits a level-of-evidence error.

### 2.4 Event sourcing and state reconstruction

Martin Fowler defines event sourcing as storing changes to application state as a sequence of events, allowing state reconstruction and alternative projections. See [Fowler, “Event Sourcing”](https://www.martinfowler.com/eaaDev/EventSourcing.html).

AETHER's natural state equation is:

$$
S_n = \operatorname{fold}(S_0, e_1,e_2,\ldots,e_n).
$$

This architecture is particularly suitable for agents because a run is not reliably represented by the current process. Model calls time out, workers crash, approvals suspend execution, and contexts compact. If every authoritative transition is durable, a successor process can reconstruct the run without inventing state.

Event sourcing also imposes obligations:

- event schemas require versioning;
- event order or causal dependencies must be explicit;
- reducers must tolerate recognized historical versions;
- secrets and uncontrolled model payloads must not leak into durable logs;
- external effects need idempotency keys or two-phase settlement;
- replay must not reissue already-settled effects;
- snapshots are accelerators, not alternate truth.

These obligations explain why AETHER's single-writer ledger, durable effect identity, cold continuation, and two-axis settlement are more valuable than a generic “memory” vector store.

### 2.5 Security: reference monitors, capabilities, and fail-safe defaults

Saltzer and Schroeder's classical principles include economy of mechanism, fail-safe defaults, complete mediation, separation of privilege, and least privilege. See [“The Protection of Information in Computer Systems,” *Proceedings of the IEEE* 63(9), 1975](https://www.ojp.gov/ncjrs/virtual-library/abstracts/protection-information-computer-systems).

A model instruction is not a security boundary. If the model can invoke a tool, containment must be enforced by the runtime and operating environment. Define the effective authority at turn $t$ as:

$$
C_t = C_{manifest}\cap C_{profile}\cap C_{parent}\cap C_{approval}\cap C_{budget}\cap C_{environment}.
$$

For a child agent $j$ spawned by parent $i$, monotonic attenuation requires:

$$
C_j \subseteq C_i,
\qquad
B_j \preceq B_i,
\qquad
d_j=d_i+1 \le d_{max}.
$$

No prompt, role label, model choice, or “mastery” policy may widen these sets. This is the core reason AETHER's kernel/agency separation is sound.

The Model Context Protocol likewise cautions that tools can represent arbitrary code execution and that clients must not blindly trust tool annotations. See the [MCP tools specification](https://modelcontextprotocol.io/specification/2025-11-25/server/tools). A production capability catalog therefore needs declared effects and enforced grants, not merely Markdown descriptions.

### 2.6 Canonicalization, signatures, and provenance

RFC 8785 explains why cryptographic hashing and signing require an invariant JSON representation. AETHER's JCS use is well founded: semantically equal JSON must produce the same bytes before hashing. See [RFC 8785, JSON Canonicalization Scheme](https://www.rfc-editor.org/rfc/rfc8785.html).

For artifact $a$ with canonical encoding $JCS(a)$:

$$
d_a = H(JCS(a)),
\qquad
\sigma_a = \operatorname{Ed25519.Sign}(sk,d_a).
$$

Verification checks both the digest and authorized signer:

$$
\operatorname{Accept}(a) \Rightarrow
H(JCS(a))=d_a
\land
\operatorname{Verify}(pk,d_a,\sigma_a)
\land
pk\in K_{authorized}.
$$

Ed25519's standard definition is [RFC 8032](https://www.rfc-editor.org/info/rfc8032/). A valid signature proves that a key signed bytes; it does not prove that the task passed, that the signer was independent, or that the underlying environment was trustworthy. Those are separate predicates.

The SLSA provenance model similarly distinguishes subject, builder identity, build definition, external parameters, and resolved dependencies. See [SLSA Build Provenance](https://github.com/slsa-framework/slsa/blob/main/spec/build-provenance.md). AETHER's exact-subject benchmark records should adopt the same intellectual discipline: record who/what executed, over which source and inputs, producing which outputs, under which environment and policy.

### 2.7 Statistical evaluation: point estimates are not capability

If an agent solves $x$ of $n$ independent frozen trials, the naïve pass-rate estimate is:

$$
\hat p=\frac{x}{n}.
$$

For small $n$, the Wald interval is unreliable. A two-sided Wilson score interval with normal quantile $z$ is:

$$
\frac{
\hat p + \frac{z^2}{2n}
\pm
z\sqrt{\frac{\hat p(1-\hat p)}{n}+\frac{z^2}{4n^2}}
}{1+\frac{z^2}{n}}.
$$

The use of Wilson bounds is supported by the [NIST/SEMATECH Engineering Statistics Handbook](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm). A lower-bound release gate is more conservative than a point-estimate gate:

$$
\operatorname{qualify}\iff LB_{Wilson}(x,n,0.95)\ge \tau.
$$

However, repository tasks often share code, fixtures, or failure modes, so independence must not be assumed automatically. Wilson is appropriate for a clearly defined binomial pass@1 gate; clustered tasks or repeated attempts require task-level bootstrap, hierarchical analysis, or another dependence-aware design. No interval can repair invalid membership, duplicated fixtures, missing trials, subject drift, or synthetic labels.

Paired harness comparisons should run both conditions on the same task identities and seeds where possible. For sufficient discordant counts, McNemar's continuity-corrected statistic is:

$$
\chi^2 = \frac{(|b-c|-1)^2}{b+c},
$$

where $b$ counts control-only successes and $c$ treatment-only successes. With few discordant pairs, use the exact binomial test. Missing and `not_run` outcomes require a preregistered policy; silently dropping asymmetric provider failures biases the comparison.

### 2.8 Modern agent-harness theory

Current primary guidance converges on several principles:

- Use the simplest agentic structure that solves the task; add multi-agent complexity only when evaluation shows benefit. [Anthropic, “Building effective agents”](https://www.anthropic.com/engineering/building-effective-agents).
- Treat context as a finite attention budget; prefer compact high-signal information, just-in-time retrieval, compaction, structured notes, and carefully chosen subagents. [Anthropic, “Effective context engineering for AI agents”](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).
- Design tools for model usability: distinct purposes, unambiguous schemas, meaningful token-efficient responses, and evaluation-driven descriptions. [Anthropic, “Writing effective tools for AI agents”](https://www.anthropic.com/engineering/writing-tools-for-agents).
- Long-running work needs durable handoffs and incremental clean-state progress across context windows. [Anthropic, “Effective harnesses for long-running agents”](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).
- Repository structure, tests, validation, feedback, observability, and recovery are part of the agent harness, not incidental infrastructure. [OpenAI, “Harness engineering: leveraging Codex in an agent-first world”](https://openai.com/index/harness-engineering/).
- Higher-risk actions should stop at explicit control points while productive low-risk work remains frictionless inside bounded environments. [OpenAI, “Running Codex safely at OpenAI”](https://openai.com/index/running-codex-safely/).
- Agent evaluation requires tasks, trials, graders, and complete trajectories; no single grader catches every failure. [Anthropic, “Demystifying evals for AI agents”](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents).

O'Reilly's recent catalog frames the same production problem around tools, modular capability design, memory, orchestration, reliability, speed/accuracy trade-offs, scalability, cost, and real-world evaluation. See Michael Albada, [*Building Applications with AI Agents*](https://www.oreilly.com/library/view/building-applications-with/9781098176495/), and Addy Osmani, [*Agentic Engineering*](https://www.oreilly.com/library/view/agentic-engineering/0642572392291/). These are useful practitioner syntheses, but repository decisions should continue to prioritize executable local evidence and primary standards over fashion.

---

## 3. Integrated system model and acceptance invariants

The useful mathematics can be reduced to three contracts. First, a model proposes an operation, but only the mediated runtime may change the environment:

$$
u_t \xrightarrow{classify} \hat u_t
\xrightarrow{authorize(C_t)} \tilde u_t
\xrightarrow{reserve(B_t)} \bar u_t
\xrightarrow{effect} (S_{t+1},r_t).
$$

For every child and later turn, authority and budget are monotone:

$$
C_{child}\subseteq C_{parent}, \qquad B_{t+1}\preceq B_t.
$$

Second, runtime terminal state $T_r$ and externally graded disposition $D_r$ are independent:

$$
T_r\in\{completed,abstained,abandoned,budget\_exhausted,cancelled,instrument\_error\},
$$

$$
D_r\in\{passed,failed,undeterminable,not\_run\}.
$$

A `finish` proposal does not prove task success, and a provider or evaluator outage is not task failure. Publishing success therefore requires a passing exterior verdict bound to the postimage:

$$
publishSuccess(r)\Rightarrow D_r=passed\land V_r.valid\land V_r.subject=H(S_{post}).
$$

Third, optimization is multi-objective. Accepted success must be considered with false completion, cost, latency, tokens, risk, and human intervention. False completion and subject ambiguity are hard vetoes, not quantities to trade for throughput. These contracts capture the report's remaining equations without creating a second architectural specification.

---

## 4. As-built architecture assessment

### 4.1 Strong and SOTA-aligned elements

#### Small trusted kernel

At the audited commit, the kernel budget passed at 1,386 logical lines against a ceiling of 1,438. The architectural value is economy of mechanism: the code that classifies and authorizes effects remains small enough for concentrated review. TCB headroom is a safety margin, not an invitation to move coding intelligence into the kernel.

#### One execution authority

The canonical path centers on `EpisodeEngine` and kernel dispatch rather than adding independent loops for coding, research, swarms, and skills. Reusing one effect authority improves comparability, security review, and replay semantics.

#### Event-derived continuation

Durable identifiers, ledger reducers, SQLite-WAL storage, cold continuation, and no duplicate effect replay are structurally appropriate for long-running agents. They are stronger than storing only a chat transcript or serializing an opaque agent object.

#### Capability and budget attenuation

The separation of requested child scope from parent authority is a sound basis for recursive agency. Typed money, time, token, byte, turn, and depth constraints enable policy enforcement and later cost analysis.

#### Exterior evaluation and evidence discipline

The project correctly rejects several common benchmark errors: dry-run success, PASS without patch identity, provider outage counted as task failure, dirty-subject qualification, zero-test success, and conflation of terminal state with task disposition.

#### Progressive context direction

Stable L1–L3 identity, dynamic L4/L5 context, explicit omission records, result distillation, and repository epochs align with modern context-engineering practice. Keeping ranking policy out of `IndexPort` also preserves the distinction between observation and decision.

### 4.2 Current correctness defects

#### Boundary violations

The five reproduced violations are:

1. `benchmarks/ladder/evidence.py` imports domain digest directly.
2. The same file imports domain task disposition directly.
3. `benchmarks/ladder/l0_triad/runner.py` imports domain digest directly.
4. `benchmarks/product_path.py` imports runtime `entrypoint` and private `_manifest` directly.
5. `runtime/cli.py` imports `apps.coding_max.facade`.

These are related: public clients and benchmarks lack an adequate public product/evidence surface, so they reach inward. The repair should define or export the missing public abstractions, not bless inward imports.

#### False completion projection

At the audited commit, `ApplicationService` and `entrypoint` mapped both `completed` and `abstained` terminal states to the string `completed`. That projection erased the difference the admission system was built to preserve. A patchless fake `finish` could consequently surface as completed even when the strict completion gate refused it.

The repair principle is:

$$
\operatorname{project}(abstained)=abstained,
\qquad
\operatorname{project}(completed)=completed,
$$

and neither projection is a task disposition. Tests expecting a generic successful smoke result must provide an admissible fake trajectory or assert the typed refusal.

#### CLI help is an effectful request

`code --help` is not recognized as a terminal parser action. It flows through default prompt construction and executes the product, returning an error-shaped completion. This violates psychological acceptability, ordinary CLI contracts, and measurement hygiene.

#### LDA truth disagreement

`lda doctor` and `lda identity` disagree about whether the fact graph matches current HEAD. Any system with two health commands that answer the same safety question differently is fail-open if callers choose the favorable answer. A single freshness predicate must back both surfaces.

### 4.3 Documentation architecture assessment

The five-file partition is sensible:

- `spec.md`: normative delta law;
- `tasks.md`: flat executable work tree;
- `milestones.md`: stable outcomes and gates;
- `backlog.md`: package inventory;
- `technical.md`: implementation handbook.

At the audited commit, operational alignment was only partial.

#### Stale checkpoint identity

`tasks.md` and `milestones.md` described a dirty pre-merge tree. Their `lock_head` values differed from each other and from the audited HEAD. A living work board cannot be high-confidence while its opening state declaration names a different subject.

#### Competing critical paths

README/backlog emphasize `REL-01R → REL-02R → M-8`, while tasks/milestones emphasize the MS-CONTROL sequence. Both contain legitimate work, but a contributor cannot infer which one owns the next commit. The execution plane needs one critical-path statement and explicit dependency edges between shared integrity tasks, M-8 evidence repair, and Coding Max control qualification.

#### Status contradiction

CMX-05 was labeled `DONE (hermetic)` while its facade falsifiers failed. “Done at historical subject” may be true, but the row did not say that. A current board should use `REGRESSED` or `REVIEWING` until its present subject is green.

#### Technical handbook entropy

At 5,767 lines, with repeated section numbers, duplicate lock appendices, and multiple historical planning snapshots, `technical.md` violates its own context-economy goals. The problem is not merely aesthetics. If an agent must spend thousands of tokens distinguishing live recipes from preserved history, the documentation introduces instruction interference.

Recommended reduction rule:

$$
\text{keep in handbook}
\iff
\text{future contributor needs it to implement an open task}.
$$

Historical evidence should remain in existing authorized historical sections or Git history, not be repeated throughout the active recipe surface.

#### Backend reference drift

The audited backend references described Ollama, an `ollama.py` adapter, and `OLLAMA_HOST`; omitted the code CLI grammar; and showed a fictitious `packs/code/manifest.json` Python import layout. These references were especially dangerous because they looked like exact operational documentation.

#### Authority error in the older audit

The pre-existing audit under `.draft/audit/` calls `.draft/todo/` the true authoritative synthesis. Repository law says the opposite: drafts are non-authorizing inputs. A useful design insight can be adopted into canonical law, but the draft never becomes authoritative merely because later code resembles it.

---

## 5. Capability-layer audit

### 5.1 The ontology is useful

The progression

$$
Skill \rightarrow Technique \rightarrow Proficiency \rightarrow Mastery
$$

is a useful classification if interpreted operationally:

- a **skill** is a bounded primitive with a typed contract;
- a **technique** is a fixed composition of primitives;
- a **proficiency** is a bounded feedback controller driven by verification;
- **mastery** is policy selection among validated controllers.

This helps distinguish “can run a test” from “can iteratively repair a defect.” It also discourages putting every behavior into one monolithic agent prompt.

### 5.2 Catalog defects

The catalog reports ten entries despite documentation claiming eight. Bridge skills duplicate names used by techniques (`spec-driven-codegen`, `tdd-falsifier`) and conceptually duplicate `autofix-loop`/`autofix-swe-loop`. Name collision makes selection ambiguous and complicates telemetry aggregation.

A production identity should be namespaced and versioned:

```text
aether.skill/test-runner@1
aether.technique/spec-driven-codegen@1
aether.proficiency/autofix-swe@1
```

Each resolved capability should also have a content digest:

$$
capability\_id = H(
manifest,
runner,
schemas,
dependencies,
policy
).
$$

### 5.3 Discovery is metadata, not execution safety

`runtime/agent_plugins.py` is mostly declarative discovery and prefix construction, which respects the prohibition on subprocess imports. That is good. But discovering the first Python runner in a directory and parsing permissive frontmatter does not establish that the runner is safe, compatible, or authorized.

A capability manifest needs at least:

- stable ID and version;
- input and output schemas;
- declared effects and resource selectors;
- required ports;
- network and filesystem policy;
- deterministic timeout and cancellation semantics;
- dependency and environment identity;
- rollback class;
- emitted evidence types;
- compatibility range;
- validation and benchmark receipts.

### 5.4 Autofix is outside the production trust spine

The audited autofix runner directly opened and rewrote the target file. It backed up one file in memory, called local scripts via subprocess, ignored the exit status of LDA reindexing, and restored only that file after failure. The falsifier layer contained a `shell=True` fallback, and model and binary paths were hard-coded to one developer machine.

This creates several unproven conditions:

- generated code could be empty or truncated before replacement;
- imports or tests may generate additional workspace files;
- a test may mutate databases or external resources;
- a killed child process may survive;
- LDA may remain indexed to the failed candidate after rollback;
- multi-file changes are not transactionally restored;
- a passing narrow test may conceal broader regressions;
- an already-running local server is trusted based on health alone in some paths;
- no kernel grant binds the actual mutation.

The documented “fail-closed rollback guarantee” is therefore not established. The correct status is `EXPERIMENTAL TOOLING PROTOTYPE`.

### 5.5 Required convergence

There are two legitimate strategies:

**Strategy A — production integration:** represent proficiency execution as an ordinary runtime composition. It requests `fs.read`, transactional patch effects, test effects, index observations, and finish through declared capabilities. Every turn is ledgered and governed.

**Strategy B — explicit development utility:** keep it under `tools/`/`.agents/`, label it non-production, remove claims of hermetic execution and production rollback, and test it as a local convenience utility.

Strategy A provides architectural reuse but is more work. Strategy B is honest and may be sufficient until Coding Max control closes. The system should not maintain a third state in which a tool is operationally privileged but marketed as an example of the governed runtime.

### 5.6 Progressive disclosure instead of a global catalog dump

The audited prefix fit the 4,096-character ceiling, but the scaling model is linear:

$$
L_{prefix}=\sum_{i=1}^{N}(L_{name_i}+L_{description_i}+L_{format}).
$$

Eventually descriptions will be truncated or compete with task context. A SOTA design uses two levels:

1. a compact index of stable IDs, one-line affordances, risk classes, and retrieval keys;
2. on-demand loading of the selected capability's full contract and examples.

Selection should be evaluated like tool selection: task-to-capability accuracy, unnecessary-load rate, token cost, and outcome lift.

---

## 6. Performance and SOTA qualification

### 6.1 What “high performance” must mean

Performance has at least five dimensions:

1. **Capability:** accepted task success under independent grading.
2. **Efficiency:** tokens, calls, dollars, GPU time, latency, and tool steps per accepted task.
3. **Reliability:** false completion, no-op, malformed call, crash, timeout, and resume-divergence rates.
4. **Security:** denied unauthorized effects, sandbox containment, secret non-disclosure, and tamper resistance.
5. **Maintainability:** change amplification, regression rate, observability, and reproducibility.

The existing one-defect, three-test, small-local-model demonstration is an existence proof that feedback can outperform one-shot generation on that fixture. It is not evidence of general coding proficiency, production rollback, or SOTA performance.

### 6.2 Required metric vector

For every live attempt $i$, record:

$$
m_i=(
y_i,
f_i,
t_i,
c_i,
l_i,
a_i,
q_i,
r_i,
o_i
),
$$

where:

- $y_i$: exterior success;
- $f_i$: false-completion indicator;
- $t_i$: total and phase-specific tokens;
- $c_i$: cost or local compute proxy;
- $l_i$: latency and time to first valid action;
- $a_i$: valid/malformed tool-call counts;
- $q_i$: verification and test-quality observations;
- $r_i$: recovery and strategy-change counts;
- $o_i$: missingness/failure-origin classification.

Aggregate reports must preserve denominators. `not_run` is not a failure, but excluding it without reporting availability creates operationally misleading results.

### 6.3 Benchmark portfolio

No single public benchmark certifies a general coding-agent framework. SWE-bench evaluates real repository issues through containerized tests; the official repository documents its reproducible evaluation harness: [SWE-bench](https://github.com/SWE-bench/SWE-bench). Static sets also face contamination and saturation, motivating temporally fresh evaluation such as [SWE-bench Live](https://openreview.net/pdf/34014365ce60e4ac9afc5fc205d7bdd70b1a796a).

AETHER should use a portfolio:

- hermetic protocol/adversarial fixtures for fail-closed behavior;
- internal frozen multi-class coding tasks;
- long-horizon resume and campaign fixtures;
- fresh or private held-out tasks for contamination resistance;
- official external evaluation for comparable public claims;
- non-coding reference-agent suites for substrate generality.

### 6.4 Trial design

Agent outputs vary. Define the estimand before running: product pass@1, repeated-attempt reliability, or best-of-$k$ are different claims. Record task, seed where controllable, sampling, model version, provider fingerprint, and retry policy. Repeated attempts on one task increase precision about that task; they do not replace breadth across independent repositories and defect classes.

Treatments must vary one declared dimension where causal attribution is claimed:

$$
\Delta U = U(\pi_{treatment})-U(\pi_{control}),
$$

with task identity and evaluation held constant. Changing model, prompt, tool schemas, budget, and retrieval together may improve a product, but it does not identify which mechanism caused the improvement.

### 6.5 Stop conditions

The following hard vetoes are correct:

- any false completion;
- missing source/task/oracle identity;
- mixed live and replay rows in one empirical denominator;
- unclean qualifying subject;
- zero actual model calls labeled as live agent performance;
- evaluation performed on a different materialized task;
- missing patch identity for coding success;
- treatment not bound to a preregistered hypothesis when making causal claims.

NIST's AI RMF emphasizes incorporating trustworthiness into design, development, use, and evaluation, and its GenAI profile organizes work around govern, map, measure, and manage. See the [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) and [NIST AI 600-1](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf). AETHER's gate model is compatible with that lifecycle, provided status artifacts remain current and independently verifiable.

---

## 7. Recommended implementation program

The program below is intentionally shorter than the earlier phase list. Each work package has one outcome, concrete changes, and a gate; the gates also serve as the required falsifier architecture.

### WP-0 — rebaseline the execution plane

Before editing production code, run the canonical gates on current HEAD and record the exact subject. Then synchronize the five execution files so they name one critical path and current statuses. Historical drafts remain evidence inputs, never authority. Explicitly map `REL-01R`/`REL-02R` to task owners, and mark any historically completed item as regressed when its current falsifier fails.

**Gate:** one clean subject is named consistently; every active item resolves an owner, `requires:` edges, and a named falsifier. This is a documentation/control-plane correction, not task acceptance.

### WP-1 — restore the public truth boundary

Repair the five related boundary violations and the terminal projection together:

1. Move Coding Max CLI orchestration out of `runtime.cli`, or make it call only generic public application operations. Runtime must not import `apps`.
2. Export one stable product execution and manifest-identity surface used by CLI, API, and benchmarks; remove benchmark access to `entrypoint._manifest` and other private symbols.
3. Expose value-only evidence receipts through an allowed public package, or keep benchmark vocabulary local and translate from public receipts. Do not duplicate digest algorithms.
4. Preserve terminal state and exterior disposition as separate public fields. Remove `abstained → completed` coercion; a patchless `finish` must remain refused.
5. Make RF-90 fake tapes perform an admissible sequence, or assert the typed non-success result. Never weaken completion law merely to satisfy a smoke test.

**Gate:** the boundary checker passes without new exceptions; the four reproduced Python failures are green; no adapter imports kernel/agency; no benchmark imports a private runtime name; and the following matrix holds:

| Terminal | Disposition | Public success claim |
|---|---|---|
| completed | passed | allowed |
| completed | failed | forbidden |
| abstained/abandoned | passed | report both axes; do not rewrite terminal |
| instrument_error | not_run | no capability score |

### WP-2 — repair the operator surface and all static gates

Parse global and command-local help before prompt construction or runtime composition. `--help` and `-h` must exit zero without model calls, ledger frames, or workspace effects; unknown, ambiguous, or value-missing flags must fail before execution. Reproduce and diagnose the `transport`, `wave2`, and `wave4` test-file failures rather than inferring their causes from file-level output.

In the same gate-restoration package, update existing canonical references: remove active Ollama guidance in favor of llama.cpp/llama-server, replace the fictitious manifest example, document the real code-command grammar and public execution surface, and repair metadata violations in place. Deduplicate only the active recipes in `technical.md`; Git history is the archive. Unify LDA `doctor` and `identity` behind one freshness predicate, then regenerate knowledge artifacts after source and canonical documentation are correct.

**Gate:** built CLI help is effect-free; TypeScript and relevant Python suites pass; every `just verify` recipe constituent exits zero on the same clean commit; LDA surfaces identify that commit. The reported `-m` collision was not independently reproduced in this audit, so it must not be treated as a defect until a failing parser test demonstrates it.

### WP-3 — obtain live instrument and release evidence

Run the frozen L0 triad through the same public entrypoint as the shipped code command. Each attempt must bind task, source, workspace preimage, model/provider, policy, oracle, patch, postimage, terminal, disposition, cost, and missingness. The exterior evaluator must remain outside agent authority. L0 demonstrates instrument viability only; three microtasks do not establish general capability.

Then execute `REL-01R`, audit successor membership, freeze `REL-02R`, preregister the held-out comparison, and run control/treatment on the same runtime subject. A valid negative or undeterminable result closes an experiment record without accepting its lift predicate.

**Gate:** every passing row resolves its patch, oracle, and postimage digests; live and replay rows never share a denominator; provider outage maps to `not_run`; dirty or mismatched subjects cannot qualify; all aggregates expose numerator, denominator, and missingness.

### WP-4 — qualify the single-agent Coding Max control

Complete T-51 corpus freeze and T-52 statistical/cost protocol, freeze T-26 on a clean exact SHA, then run T-27 with `vg-code-balanced` as the single-worker control. Preserve model, server, prompt, manifest, tool schema, policy, retry, and task identities. Apply the specified $n\ge30$, Wilson lower-bound $\ge0.40$, and zero-false-completion gate only if its binomial estimand and independence assumptions are defensible; otherwise retain the policy threshold but use a preregistered dependence-aware interval.

**Gate:** accepted control evidence exists on an exact clean subject, false completion is zero, missingness is explicit, and the statistical method matches the sampling unit. The threshold is an internal release predicate, not proof of human equivalence or industry SOTA.

### WP-5 — converge intelligence and capability execution

After control acceptance, add repository ergonomics in dependency order:

```text
T-75 LdaRepoIndex
  → T-76 repo.* observations in L5
  → T-77 cache breakpoints / CTRF / goal echo
  → T-78 exact unique-preimage str_replace
  → T-83b caller-aware completion admission
```

Index values must be immutable; stale state fails deterministically; fallback is observable; ranking remains outside `IndexPort`; full outputs are digest-addressable; and editing reuses the existing two-phase transaction path. Transaction tests must cover duplicate/missing preimages, failure on file $k$ of $n$, cancellation, syntax failure, byte-for-byte multi-file restoration, and restored index epoch.

For capabilities, choose either governed production integration or an explicit experimental-tool label. Production capabilities need namespaced/versioned/content-addressed identity; schemas; declared effects, budgets, dependencies, and rollback class; on-demand instruction loading; kernel-mediated execution; process-tree cancellation; and receipts. Remove direct privileged writes, hard-coded developer paths, and `shell=True` fallback. Test the actual proficiency—including crash and multi-file rollback—not a hand-written approximation.

**Gate:** selection resolves one stable identity; undeclared effects are denied; child authority cannot widen; timeout kills the process tree; failure restores every declared mutable resource; unavailable infrastructure produces typed `not_run`/instrument failure; and capability selection shows measured outcome lift net of token, latency, and risk cost.

### WP-6 — admit treatments only by evidence

Only after WP-4 should the default product consider anti-thrashing policies, cascades, specialist roles, branch search, campaign directors, governed memory, or skill promotion. Hold task/evaluator identity constant and vary one declared mechanism when making causal claims. Adopt a treatment only when preregistered evidence supports positive net utility, false completion remains zero, and security risk does not increase. This is the point at which “mastery” becomes a measured policy-selection layer rather than aspirational taxonomy.

---

## 8. Risk register

| Risk | Mechanism | Consequence | Mitigation | Release veto? |
|---|---|---|---|---|
| False completion | Terminal projection erases abstention | Invalid product and benchmark claims | Two-axis public results; adversarial gate suite | Yes |
| Boundary erosion | Private imports legalized by exceptions | Product-specific runtime, untestable clients | Public ports; AST boundary lint | Yes |
| Stale index | Conflicting health predicates | Wrong symbols/tests/context | One freshness function; exact HEAD binding | Yes for qualification |
| Capability bypass | Tools write outside kernel/2PC | Data loss and unaudited effects | Runtime integration or experimental label | Yes for production claim |
| Test illusion | Test mocks the property rather than system | False confidence | Integration/property/crash tests | Yes for claimed guarantee |
| Documentation entropy | Repeated historical plans | Agent instruction drift | One active recipe per task | No, but blocks reliable development |
| Benchmark contamination | static/public task leakage | Inflated score | fresh/private held-out tasks | Yes for SOTA claim |
| Missingness bias | outages removed from denominator | Misleading availability | explicit not-run rate | Yes for operational claim |
| Multi-agent cost explosion | duplicate work and context | worse utility despite pass lift | single-agent control and ablation | Yes for default enablement |
| Self-evaluation | agent controls its grader | reward hacking | exterior oracle and separated authority | Yes |
| Signature overclaim | valid key treated as valid result | cryptographic theater | signed predicate + subject verification | Yes |
| TCB growth | coding policy enters kernel | unreviewable trust core | strict ceiling and domain blindness | Yes |

---

## 9. Corrections to prior advice and conclusion

Four corrections are non-negotiable. Do not widen boundary allowlists merely to legalize current imports. Do not mark T-79/T-89/T-92–T-95 accepted from focused mechanism tests. Do not treat `.draft/todo` or any audit as execution authority. Do not call the capability layer production-grade until its real runners satisfy mediated-effects, cancellation, and multi-resource rollback falsifiers. Likewise, an `instrument_error` should never be reclassified simply to make an expected-success test green.

The architecture is SOTA-aligned in important trust, provenance, continuation, and evaluation dimensions, but Coding Max SOTA performance and production-grade universal capabilities remain unproved. The runway's conceptual order is sound—single-agent control before treatments—but its operational truth was inconsistent at the audited commit. The decisive implementation sequence is WP-0 through WP-4: rebaseline, restore the public truth boundary, recover gates, obtain live evidence, and qualify the single-agent control. WP-5 and WP-6 follow only after that evidence exists.

The smallest correct next code package is WP-1. It resolves the common cause behind the boundary and false-completion defects without expanding the kernel. After WP-2 is gate-green on one clean subject, execute live L0 and release evidence; do not add cognitive architecture until the shipped path can prove what it did, why it stopped, whether the task passed, what it cost, and which exact source and evaluator support the claim.

---

## 10. References

### Classical software and systems architecture

1. Alistair Cockburn. [“Hexagonal Architecture,” HaT Technical Report 2005.02](https://alistair.cockburn.us/hexagonal-architecture), 2005.
2. Martin Fowler. [“Event Sourcing”](https://www.martinfowler.com/eaaDev/EventSourcing.html), 2005.
3. Kent Beck. [*Test-Driven Development: By Example*](https://www.pearson.com/en-gb/subject-catalog/p/test-driven-development-by-example/P200000009421/9780321146533), Addison-Wesley, 2002/2022 edition listing.
4. Jerome H. Saltzer and Michael D. Schroeder. [“The Protection of Information in Computer Systems”](https://www.ojp.gov/ncjrs/virtual-library/abstracts/protection-information-computer-systems), *Proceedings of the IEEE* 63(9), 1975.

### Standards and provenance

5. A. Rundgren, B. Jordan, and S. Erdtman. [RFC 8785: JSON Canonicalization Scheme](https://www.rfc-editor.org/rfc/rfc8785.html), 2020.
6. S. Josefsson and I. Liusvaara. [RFC 8032: Edwards-Curve Digital Signature Algorithm](https://www.rfc-editor.org/info/rfc8032/), 2017.
7. SLSA Framework. [Build Provenance specification](https://github.com/slsa-framework/slsa/blob/main/spec/build-provenance.md).
8. Model Context Protocol. [Tools specification](https://modelcontextprotocol.io/specification/2025-11-25/server/tools).
9. NIST. [AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework).
10. NIST. [Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile, NIST AI 600-1](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf), 2024.

### Agent architecture and harness engineering

11. Anthropic. [“Building effective agents”](https://www.anthropic.com/engineering/building-effective-agents), 2024.
12. Anthropic. [“Effective context engineering for AI agents”](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), 2025.
13. Anthropic. [“Writing effective tools for AI agents—using AI agents”](https://www.anthropic.com/engineering/writing-tools-for-agents), 2025.
14. Anthropic. [“Effective harnesses for long-running agents”](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), 2025.
15. Anthropic. [“Demystifying evals for AI agents”](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), 2026.
16. OpenAI. [“Harness engineering: leveraging Codex in an agent-first world”](https://openai.com/index/harness-engineering/), 2026.
17. OpenAI. [“Running Codex safely at OpenAI”](https://openai.com/index/running-codex-safely/), 2026.
18. OpenAI Agents SDK. [Tracing documentation](https://openai.github.io/openai-agents-python/tracing/).
19. Michael Albada. [*Building Applications with AI Agents*](https://www.oreilly.com/library/view/building-applications-with/9781098176495/), O'Reilly Media, 2025.
20. Addy Osmani. [*Agentic Engineering*](https://www.oreilly.com/library/view/agentic-engineering/0642572392291/), O'Reilly Media catalog record.

### Evaluation and statistics

21. NIST/SEMATECH. [“Confidence intervals”](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm), Engineering Statistics Handbook.
22. Carlos E. Jimenez et al. [*SWE-bench: Can Language Models Resolve Real-World GitHub Issues?*](https://arxiv.org/abs/2310.06770), 2023.
23. SWE-bench maintainers. [Official SWE-bench repository and containerized evaluation harness](https://github.com/SWE-bench/SWE-bench).
24. Microsoft Research et al. [*SWE-bench Goes Live!*](https://openreview.net/pdf/34014365ce60e4ac9afc5fc205d7bdd70b1a796a), 2025.

---

## Appendix A — Claim-to-evidence ledger

| Claim | Evidence | Confidence |
|---|---|---|
| Audited TCB is within budget | Executed `check_tcb_budget.py`: 1,386/1,438 | High |
| Audited tree has five boundary violations | Executed boundary checker; exact paths recorded | High |
| Wave-2 mechanisms have 31 focused green tests | Executed six named test modules | High, mechanism only |
| Product completion surface regresses | Executed facade/RF-90 tests: four failures | High |
| CLI help executes the product | Direct invocation emitted instrument error completion | High |
| TypeScript types are coherent | Full monorepo typecheck passed | High |
| CLI runtime behavior is green | Contradicted by three failing test files | High negative evidence |
| LDA index was trustworthy for audited source | Doctor/identity disagreed; treated as stale | Low/invalid |
| Capability prefix fits limit | CLI emitted 2,180/4,096 chars | High |
| Capability catalog has eight entries | Contradicted; CLI reports ten | High negative evidence |
| Autofix rollback is production verified | Test does not call real runner; claim rejected | High |
| Coding Max is SOTA | No accepted live control or official benchmark | Unsupported |
| Core architecture follows ports/adapters | Source layout plus boundary law; five audited violations | High at intent, partial at audited conformance |
