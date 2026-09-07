---
id: draft.audit.aether-sota-agentic-coding-development-plan-2026-09-06
class: report
authority: non-canonical
canonical_for: []
status: historical-reference
owner: repository-governance
version: "1.0.0"
last_verified: 2026-09-06
subject_head: "dfb0bb64fc82398b9a05f1e3457f4f45babfcbca"
subject_branch: main
evidence_boundary: current-source-plus-reproduced-local-gates
---

# AETHER SOTA Agentic Coding Architecture and Development Plan Audit

## Abstract

This auxiliary report evaluates whether AETHER/Vanguard's architecture, execution runway, coding-agent product, capability system, verification program, and performance claims are aligned with the state of the art in agentic software engineering. It also gives a concrete implementation order for moving from a sophisticated mechanism-rich prototype to an empirically qualified coding-agent framework.

The central conclusion is deliberately two-sided. AETHER's production substrate contains unusually strong ideas: a small capability-aware kernel, complete mediation of effects, monotonic budget attenuation, event-derived state, durable continuation, explicit context layers, exterior evaluation, exact-subject evidence, and a refusal to equate mechanism presence with accepted capability. Those choices agree with classical security engineering, ports-and-adapters architecture, event sourcing, test-driven development, supply-chain provenance, and current guidance from organizations building frontier coding agents.

However, the current repository cannot yet support a claim that the coding agent or universal capability layer is state of the art in delivered performance. At the audited commit, five dependency-boundary violations are reproducible; four related Python product tests fail; three TypeScript CLI test files fail; the documentation metadata gate fails; `aether code --help` invokes execution and returns an `instrument_error`; the LDA health commands disagree about index freshness; no accepted live L0 or L2 control disposition exists; and the tools-side autofix proficiency bypasses the production transaction, capability, sandbox, ledger, and admission mechanisms it is documented as exemplifying.

The correct next move is therefore not more orchestration, more roles, or more speculative intelligence. It is to close the public product's truth boundary, restore all gates, produce exact-subject live evidence, and then add repository intelligence and capability composition behind stable ports. In Popperian terms, the project has many hypotheses and increasingly good falsifiers; its remaining work is to expose the central product claims to those falsifiers without changing the measured subject.

This file is non-canonical. It does not authorize implementation, alter milestone status, or supersede `VISION.md`, `AGENTS.md`, or the five execution-runway files. It records an audit and a proposed implementation plan for investigation.

---

## 1. Audit question, subject, and standard of proof

### 1.1 Questions answered

The investigation asks five questions:

1. Are `technical.md`, `spec.md`, `tasks.md`, `backlog.md`, and `milestones.md` mutually aligned and usable as an execution control plane?
2. Does the as-built framework embody sound architecture for general AI agents, not merely one coding workflow?
3. Is the Coding Max product path currently truthful, secure, recoverable, and competitive?
4. Is the Skills → Techniques → Proficiencies → Mastery capability model production-grade or still experimental?
5. What should be implemented next, in what dependency order, and with which proof obligations?

### 1.2 Audited subject

The primary subject is Git commit:

```text
dfb0bb64fc82398b9a05f1e3457f4f45babfcbca
branch: main
date inspected: 2026-09-06
```

The worktree was initially clean. Some validation commands subsequently produced changes in `tools/002_LLM_API_MOCK/lam.sqlite` and untracked BAAC run directories. Those outputs were preserved and were not used as qualifying evidence. This distinction matters: a source commit, a dirty workspace, and a generated run artifact are different subjects.

### 1.3 Epistemic classes

This report uses the following evidence classes:

| Class | Meaning |
|---|---|
| `FACT` | Directly observed in current source, Git identity, or command output. |
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
| Documentation metadata checker | FAIL; twelve research-document violations |
| `aether code --help` equivalent | exits after emitting `[complete] instrument_error, 0 turns, unknown` |
| Capability catalog | 10 registered entries, 4 executable runners |
| Capability prompt prefix | 2,180/4,096 characters |
| LDA `doctor` | reports healthy and current workspace HEAD |
| LDA `identity` | reports index bound to `622131da`, therefore stale versus `dfb0bb64` |

The full `just verify` gate was not and could not be claimed successful because earlier constituent gates already failed. This is an important negative result, not a procedural inconvenience.

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

The current import from `runtime/cli.py` to `apps/coding_max/facade.py` is not merely a style defect. It reverses the driver relationship and makes the runtime aware of one product client. Similarly, a benchmark that imports a private runtime helper does not measure the public port; it measures an implementation detail.

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

If an agent solves $x$ of $n$ independent frozen tasks, the naïve pass-rate estimate is:

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

However, statistical calculation cannot repair invalid task membership, duplicated fixtures, missing trials, subject drift, or synthetic success labels. Measurement validity precedes estimation.

Paired harness comparisons should run both conditions on the same task identities and seeds where possible. McNemar's statistic operates on discordant paired outcomes:

$$
\chi^2 = \frac{(|b-c|-1)^2}{b+c},
$$

where $b$ counts control-only successes and $c$ treatment-only successes. Missing and `not_run` outcomes require explicit policy; silently dropping asymmetric provider failures biases the comparison.

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

## 3. Formal model of AETHER as an agentic computation substrate

### 3.1 Agent-environment loop

Model the harness as a constrained partially observable controlled process:

$$
\mathcal{A}=
\langle
S,O,U,T,Z,R,C,B,E,V
\rangle,
$$

where:

- $S$ is environment and durable task state;
- $O$ is the observation space;
- $U$ is the set of model-proposed operations;
- $T(S,u)$ is the mediated transition function;
- $Z(S)$ produces bounded context observations;
- $R$ is a utility or research reward, not runtime authority;
- $C$ is the active capability set;
- $B$ is the multidimensional budget;
- $E$ is the append-only causal event stream;
- $V$ is exterior verification.

The model proposes $u_t$, but the environment transition occurs only after classification, authorization, budget reservation, execution, and settlement:

$$
u_t
\xrightarrow{classify}
\hat u_t
\xrightarrow{authorize(C_t)}
\tilde u_t
\xrightarrow{reserve(B_t)}
\bar u_t
\xrightarrow{effect}
(S_{t+1},r_t).
$$

This is more precise than saying an agent “has tools.” It distinguishes requested behavior from authorized and observed effects.

### 3.2 Two-axis settlement theorem

Let terminal state $T_r$ answer why runtime stopped, and task disposition $D_r$ answer whether an exterior acceptance predicate holds:

$$
T_r\in\{completed,abstained,abandoned,budget\_exhausted,cancelled,instrument\_error\}
$$

$$
D_r\in\{passed,failed,undeterminable,not\_run\}.
$$

In general there is no total function $f$ such that $D_r=f(T_r)$. Counterexamples prove independence:

- A correct patch may pass exterior tests even if the model fails to emit the protocol's final `finish` action.
- A model may emit `finish` without reading, mutating, or testing anything.
- A provider failure yields `not_run`, not task failure.
- An evaluator outage yields `undeterminable`, not model failure.

Therefore:

$$
\operatorname{publishSuccess}(r)
\Rightarrow
D_r=passed
\land
V_r.valid
\land
V_r.subject=H(S_{post}).
$$

Runtime terminal `completed` is neither necessary nor sufficient for exterior success.

### 3.3 Context as constrained submodular selection

Let candidate context items be $X=\{x_1,\ldots,x_m\}$, each with token cost $c_i$, relevance $q_i$, redundancy $\rho_{ij}$, and provenance confidence $p_i$. Context construction can be expressed as:

$$
\max_{Y\subseteq X}
\left[
\sum_{i\in Y}p_iq_i
-\lambda\sum_{i,j\in Y}\rho_{ij}
\right]
\quad
\text{s.t.}
\sum_{i\in Y}c_i\le B_C.
$$

This explains why dumping a 5,767-line handbook into every prompt is not state of the art even if the handbook is accurate. High-signal routing, stable prefix layers, just-in-time observation, explicit omissions, and digest-addressable full artifacts are better.

### 3.4 Performance objective

A coding harness is a multi-objective system. One useful score is:

$$
U(\pi)=
w_p P_{accepted}
-w_f P_{false\ completion}
-w_c\mathbb{E}[cost]
-w_l\mathbb{E}[latency]
-w_t\mathbb{E}[tokens]
-w_r\mathbb{E}[risk]
-w_h\mathbb{E}[human\ intervention].
$$

Subject to hard constraints:

$$
P_{false\ completion}=0,
\quad C_{child}\subseteq C_{parent},
\quad B_{t+1}\preceq B_t,
\quad \text{dirty qualifying subject}=false.
$$

This makes clear why raw tokens per second or one successful micro-fix cannot establish SOTA status. A faster harness that corrupts files or reports false completion has lower utility.

---

## 4. As-built architecture assessment

### 4.1 Strong and SOTA-aligned elements

#### Small trusted kernel

The kernel budget is enforced and currently passes at 1,386 logical lines against a ceiling of 1,438. The architectural value is economy of mechanism: the code that classifies and authorizes effects remains small enough for concentrated review. TCB headroom is a safety margin, not an invitation to move coding intelligence into the kernel.

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

`ApplicationService` and `entrypoint` currently map both `completed` and `abstained` terminal states to the string `completed`. That projection erases the difference the admission system was built to preserve. A patchless fake `finish` can consequently surface as completed even when the strict completion gate refused it.

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

But current operational alignment is only partial.

#### Stale checkpoint identity

`tasks.md` and `milestones.md` describe a dirty pre-merge tree. Their `lock_head` values differ from each other and from current HEAD. A living work board cannot be high-confidence while its opening state declaration names a different subject.

#### Competing critical paths

README/backlog emphasize `REL-01R → REL-02R → M-8`, while tasks/milestones emphasize the MS-CONTROL sequence. Both contain legitimate work, but a contributor cannot infer which one owns the next commit. The execution plane needs one critical-path statement and explicit dependency edges between shared integrity tasks, M-8 evidence repair, and Coding Max control qualification.

#### Status contradiction

CMX-05 is labeled `DONE (hermetic)` while its current facade tests fail. “Done at historical subject” may be true, but the row does not say that. Current status should be `REGRESSED` or `REVIEWING` until the present subject is green.

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

The backend references still describe Ollama, an `ollama.py` adapter, and `OLLAMA_HOST`; omit the current code CLI grammar; and show a fictitious `packs/code/manifest.json` Python import layout. These references are especially dangerous because they look like exact operational documentation.

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

The current autofix runner directly opens and rewrites the target file. It backs up one file in memory, calls local scripts via subprocess, ignores the exit status of LDA reindexing, and restores only that one file after failure. The falsifier layer contains a `shell=True` fallback. Model and binary paths are hard-coded to one developer machine.

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

The current prefix fits the 4,096-character ceiling, but the scaling model is linear:

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

Agent outputs vary. A task is not a trial, and a single trial is not a stable estimate. For each task/model/preset cell, either run multiple trials or explicitly define pass@1 as the product contract. Random seeds, sampling, model version, provider fingerprint, and retry policy must be fixed or recorded.

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

### Phase 0 — establish one current truth surface

**Objective:** make the next code change refer to one current source subject and one critical path.

Actions:

1. Preserve historical artifacts, but update the current checkpoint in `tasks.md` to `dfb0bb64` plus the actual dirty-state caveat at execution time.
2. Remove mutable implementation-session prose from the stable milestone table or label it as a historical snapshot.
3. Add explicit task mappings for `REL-01R` and `REL-02R`, or state that existing T-IDs implement them.
4. Downgrade CMX-05 from `DONE (hermetic)` while its current falsifiers fail.
5. State one critical path shared by M-8 and MS-CONTROL.
6. Keep `.draft/todo` non-authorizing; promote adopted decisions into canonical files.

Exit predicate:

$$
\exists!\;P_{critical}
\land
\forall w\in WorkItems,\;owner(w),requires(w),falsifier(w)\text{ resolve}.
$$

### Phase 1 — repair the five boundaries

**Objective:** make public clients use public ports while preserving one runtime authority.

#### Runtime CLI to app inversion

Preferred repair: move Coding Max CLI-specific orchestration to the application/client layer, or have `runtime.cli` invoke only generic `ApplicationService` operations with resolved public manifest/preset inputs. It must not import the app facade.

Falsifiers:

- AST/import scan proves no `runtime → apps` edge;
- CLI/API results serialize from the same result value objects;
- runtime contains no Coding Max provider logic;
- invalid preset fails before any durable effect.

#### Benchmark to private runtime imports

Export a public product execution function and manifest identity query through the repository-authorized public runtime surface. Remove `_manifest` consumption from benchmarks. The public call must be the same call used by the CLI.

Falsifiers:

- benchmark imports only allowed public packages;
- runner and CLI bind identical manifest digest and preset identity;
- a test monkeypatching the public function observes both paths;
- private symbol names are absent from benchmark imports.

#### Benchmark digest and disposition imports

Three options should be evaluated:

1. expose value-only evidence types through an allowed public port package;
2. place benchmark-only row vocabulary entirely in `benchmarks`, translating from product receipts;
3. export a public receipt schema from runtime root.

The preferred design is a value-only public evidence contract with no domain object handles. Avoid duplicating digest algorithms; use a stable public digest operation or receive digests from runtime receipts.

Exit predicate: `check_boundaries.py` passes without new exceptions.

### Phase 2 — restore two-axis completion truth

**Objective:** ensure public outcomes do not fabricate completion.

Actions:

1. Remove `abstained → completed` coercion in `ApplicationService` and `entrypoint`.
2. Audit all result projections for similar `terminal in {completed, abstained}` mappings.
3. Decide the public vocabulary: terminal status and exterior disposition should be separate fields.
4. Make `completed` require the product completion gate, not merely a terminal enum.
5. Rewrite RF-90 fake tapes to perform an admissible action sequence, or assert a non-success terminal.
6. Preserve strict rejection of patchless fake `finish`.

Property-based matrix:

| Terminal | Exterior disposition | Public success? |
|---|---|---|
| completed | passed | yes |
| completed | failed | no |
| completed | undeterminable | no claim |
| abstained | passed | task may be solved, runtime did not complete |
| abandoned | passed | task solved externally; terminal remains abandoned |
| instrument_error | not_run | no capability score |

Exit predicate:

$$
false\_completion=0
$$

over the complete hermetic adversarial suite, with all four currently failing Python tests green.

### Phase 3 — make the CLI a truthful operator surface

**Objective:** commands that inspect or request help must never execute an agent.

Actions:

1. Parse global and command-local `--help`/`-h` before default prompt construction.
2. Return exit code zero and write usage to the appropriate stream.
3. Reject missing values for value flags rather than silently using defaults.
4. Define one meaning for each short flag within a command scope; an unsupported losing spelling errors.
5. Add the named TypeScript test file for help and flag semantics.
6. Diagnose and repair the `transport`, `wave2`, and `wave4` CLI test-file failures.
7. Document the actual `aether code` grammar in the existing backend commands reference.

Exit predicate:

```text
aether --help             -> 0, no runtime frame
aether code --help        -> 0, no runtime frame
aether code -h            -> 0, no runtime frame
ambiguous/unknown option  -> nonzero, explanatory error, no runtime frame
```

### Phase 4 — restore repository gates and documentation truth

**Objective:** reach a clean, reproducible candidate before live measurement.

Actions:

1. Fix documentation metadata failures in place without creating new canonical documents.
2. Remove active Ollama instructions and replace them with llama.cpp/llama-server configuration.
3. Replace the fictitious manifest example with a schema-valid excerpt matching current pack composition.
4. Document the current code command and public product execution surface.
5. Deduplicate the active portion of `technical.md`; retain one recipe per open task.
6. Make LDA doctor and identity share one freshness calculation and one subject revision.
7. Run the exact `just check` and `just verify` recipe bodies.
8. Regenerate knowledge artifacts only after canonical documentation is correct.

Exit predicate: every `just verify` constituent exits zero on a clean tree, and generated indexes identify that same HEAD.

### Phase 5 — live L0 and empirical-runner repair

**Objective:** demonstrate that the public product can act, mutate, verify, finish, and retain evidence.

For each P0 task:

1. materialize a fresh isolated workspace;
2. bind task and oracle digests;
3. run through the same public entrypoint as `aether code`;
4. record model/provider identity and sampling;
5. record every tool proposal, accepted effect, and receipt;
6. retain patch and postimage digests;
7. execute the exterior oracle outside the agent's authority;
8. emit both terminal and disposition axes;
9. preserve failures and missingness;
10. confirm the source subject remained clean.

The L0 claim is limited to instrument viability. Three successes do not establish general coding performance.

### Phase 6 — M-8 successor evidence

**Objective:** close the release-blocking empirical integrity path before product expansion.

Actions:

1. complete `REL-01R` over the repaired live executor;
2. audit every successor task for unique content, workspace, oracle, split, and base revision;
3. freeze `REL-02R` only after those identities resolve;
4. preregister the held-out memory/learning comparison;
5. execute control and treatment through the same runtime subject;
6. report positive, negative, invalid, or undeterminable results honestly;
7. require independent acceptance over the exact bundle digest.

A negative valid result may close the experiment without accepting the lift predicate. This prevents endless tuning from rewriting the question after observing outcomes.

### Phase 7 — single-agent Coding Max control

**Objective:** establish a trustworthy baseline before adding specialists.

Actions:

1. complete T-51 multi-class corpus freeze;
2. complete T-52 statistical and cost protocol;
3. freeze T-26 on a clean exact SHA;
4. run T-27 with `vg-code-balanced` as the single-worker control;
5. require $n\ge30$, Wilson lower bound $\ge0.40$, and false completion zero;
6. preserve model, server, prompt, manifest, tool schema, policy, and task identities.

The threshold is an internal qualification criterion, not a claim of human professional equivalence.

### Phase 8 — repository intelligence and change ergonomics

**Objective:** improve localization and editing without creating a second policy engine.

Dependency order:

```text
T-75 LdaRepoIndex
  → T-76 repo.* observations in L5
  → T-77 cache breakpoints, CTRF, goal echo
  → T-78 exact unique-preimage str_replace
  → T-83b caller-aware completion admission
```

Key design constraints:

- index results are immutable values;
- stale index fails deterministically;
- fallback is observable;
- ranking stays request-local and experimental;
- L1–L3 remains stable across dynamic observations;
- full outputs remain digest-addressable;
- edit operations use the existing 2PC transaction manager;
- no fuzzy replacement is introduced without separate evidence.

### Phase 9 — capability convergence

**Objective:** turn the capability taxonomy into a governed system.

Actions:

1. choose production integration or explicit experimental status for each capability;
2. introduce namespaced, versioned, content-addressed manifests;
3. declare effects, budgets, inputs, outputs, dependencies, and rollback class;
4. load full instructions only after selection;
5. route production execution through kernel-mediated ports;
6. replace direct file writes with transactional effects;
7. remove hard-coded developer paths;
8. remove `shell=True` fallbacks;
9. propagate cancellation and validate process-tree death;
10. test the real proficiency, including crash and multi-file rollback;
11. record capability ID and version in run receipts;
12. evaluate task-to-capability selection and outcome lift.

### Phase 10 — treatments, specialists, and campaigns

Only after the single-agent baseline is accepted should the project evaluate:

- anti-thrashing state-hash policies;
- model routing and cascades;
- test investigator, localizer, reviewer, or architect roles;
- branch search and test-time compute;
- durable campaign directors;
- governed memory and skill promotion.

Each added component creates orchestration cost and new failure edges. The admission rule should be:

$$
\operatorname{adopt}(t)
\iff
\Delta U_t>0
\land
\Delta falseCompletion_t=0
\land
\Delta securityRisk_t\le0
\land
CI(\Delta U_t)\text{ supports the decision}.
$$

---

## 8. Required falsifier architecture

### 8.1 Boundary properties

- No runtime module imports `apps`.
- No adapter imports kernel or agency.
- Benchmarks import only public product/evidence surfaces.
- No private-name import appears in benchmark runners.
- Domain and kernel remain free of coding-specific concepts.

### 8.2 Completion properties

- `finish` without mutation and relevant verification cannot become completed.
- zero executed tests cannot yield passed.
- stale verification after write is invalid.
- a test-modifying patch fails tamper policy.
- an unrelated green test cannot satisfy task relevance.
- terminal and disposition survive replay independently.

### 8.3 Transaction properties

- failure at file $k$ of $n$ restores every file byte-for-byte;
- duplicate preimage fails rather than guessing;
- missing preimage returns a typed mismatch;
- syntax failure prevents durable flush;
- cancellation during apply leaves no partial tree;
- index epoch after rollback matches restored workspace.

### 8.4 Capability properties

- selection resolves one stable capability identity;
- undeclared effects are denied;
- child capability sets cannot widen;
- timeout kills the complete subprocess tree;
- failure restores every declared mutable resource;
- unavailable local model returns typed `not_run`/instrument failure;
- full runner integration, not a simulated helper, is exercised.

### 8.5 Evaluation properties

- task set digest is order-independent and membership-complete;
- live and replay labels cannot share a denominator;
- provider outage never becomes task failure;
- dirty source cannot qualify;
- report subject equals executed source subject;
- every PASS resolves patch, oracle, and postimage digests;
- every aggregate exposes numerator, denominator, and missingness.

---

## 9. Risk register

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

## 10. Architecture decision recommendations

### ADR recommendation A — preserve the kernel

Do not move AST parsing, benchmark semantics, repository ranking, role selection, or task-specific completion rules into the kernel. The kernel should continue to classify, authorize, reserve, mediate, and settle generic effects.

### ADR recommendation B — public application boundary

Define one stable public application surface used by Python API, TypeScript CLI, benchmarks, and reference agents. Internal entrypoint helpers must not become de facto ports.

### ADR recommendation C — settlement as two public fields

Expose terminal status and task disposition independently in public results. Never overload `outcome` with both concepts. If backward compatibility requires `outcome`, define it as a projection with explicit loss semantics and do not use it for qualification.

### ADR recommendation D — capabilities are declarations plus enforcement

A Markdown capability card is documentation. A production capability is a content-addressed contract whose effects are enforceable by runtime policy. The catalog must distinguish these categories.

### ADR recommendation E — evidence before orchestration

Keep specialists, swarms, adaptive routing, and campaign directors disabled until a frozen single-worker baseline exists and paired evidence demonstrates net benefit. This matches both local risk economics and current frontier-agent guidance.

---

## 11. Final assessment

### 11.1 Is the architecture good?

Yes. The core substrate is coherent, security-conscious, and more rigorous than many agent frameworks. The combination of complete effect mediation, bounded authority, event-derived state, exact-subject provenance, exterior evaluation, and context economics is a credible foundation for general agents.

### 11.2 Is it SOTA today?

Architecturally SOTA-aligned: **yes, in several dimensions**.

Empirically SOTA as a coding product: **not demonstrated**.

Production-grade universal capabilities: **not yet**.

High performance: **unknown**, because accepted multi-task live evidence is absent and current product gates fail.

### 11.3 Is the execution runway aligned?

The conceptual dependencies are mostly sound, particularly the refusal to enable multi-agent treatments before single-agent control. Operationally, the runway is not fully aligned because identities and statuses are stale, M-8 and MS-CONTROL present competing critical paths, and the handbook contains excessive historical duplication.

### 11.4 Decisive next step

The next implementation package should be one bounded “public truth restoration” change:

1. repair the five boundary violations;
2. preserve abstained/abandoned terminal truth;
3. repair the four Python related-surface failures;
4. fix command-local CLI help and the TypeScript failures;
5. restore all verification gates;
6. synchronize the existing five execution files to the exact subject.

Then run live L0 and the M-8 successor evidence program. Do not add more cognitive architecture until the current product can prove what it did, why it stopped, whether the task passed, what it cost, and which exact source and evaluator produced that conclusion.

---

## 12. References

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
| Current TCB is within budget | Executed `check_tcb_budget.py`: 1,386/1,438 | High |
| Tree has five boundary violations | Executed boundary checker; exact paths recorded | High |
| Wave-2 mechanisms have 31 focused green tests | Executed six named test modules | High, mechanism only |
| Product completion surface regresses | Executed facade/RF-90 tests: four failures | High |
| CLI help executes the product | Direct invocation emitted instrument error completion | High |
| TypeScript types are coherent | Full monorepo typecheck passed | High |
| CLI runtime behavior is green | Contradicted by three failing test files | High negative evidence |
| LDA index is trustworthy for current source | Doctor/identity disagree; treated as stale | Low/invalid |
| Capability prefix fits limit | CLI emitted 2,180/4,096 chars | High |
| Capability catalog has eight entries | Contradicted; CLI reports ten | High negative evidence |
| Autofix rollback is production verified | Test does not call real runner; claim rejected | High |
| Coding Max is SOTA | No accepted live control or official benchmark | Unsupported |
| Core architecture follows ports/adapters | Source layout plus boundary law; five current violations | High at intent, partial at current conformance |

## Appendix B — Definition of done for the next package

The public-truth-restoration package is complete only when all statements below are true on the same clean commit:

- [ ] Boundary checker reports zero violations.
- [ ] No new boundary exceptions were added solely for current files.
- [ ] Coding Max patchless finish never reports completed.
- [ ] Terminal status and exterior disposition remain separate.
- [ ] RF-90 fake tapes have semantically valid expectations.
- [ ] `aether code --help` exits zero without model/runtime execution.
- [ ] Unknown or ambiguous CLI flags fail before execution.
- [ ] All CLI tests pass.
- [ ] All relevant Python tests pass.
- [ ] Documentation metadata passes.
- [ ] Full verification recipe passes.
- [ ] LDA doctor and identity report the same current HEAD.
- [ ] The five execution documents name one current critical path.
- [ ] No live benchmark result is claimed from hermetic mechanics alone.
- [ ] The worktree is clean before the first qualifying run.

## Appendix C — Interpretation warning

This report is intentionally detailed, but detail is not authority. Equations clarify contracts; they do not prove implementation. Citations establish intellectual lineage; they do not make AETHER conformant. Tests provide evidence only for their asserted subjects. A benchmark score measures a model-harness-environment combination under one protocol; it does not establish human-equivalent professional competence. The durable standard remains: canonical law constrains, source implements, executable falsifiers challenge, and exact-subject evidence supports only the claims it actually measures.
