# Vanguard / AETHER Executive Architecture and Delivery Report

**Date:** 2026-08-24  
**Decision posture:** CEO, Principal Architect, Staff Engineer, AI Research Lead, Senior Developer,
and Tech Lead  
**Repository state assessed:** `main` merge `366c71b`; successor branch
`feat/m7-effect-log-measurement`

## Executive summary

Vanguard already contains the difficult part of a credible general-task agent framework: a small
trusted substrate, typed capability mediation, deterministic event reduction, durable effect intent,
isolated evaluation, explicit composition, domain packs, and architectural enforcement. The correct
next move is not to add a large catalog of agent features. It is to prove that this substrate can run
two materially different task domains without changing its semantics.

The first two products should be:

1. **`coding-default`** — an autonomous coding CLI that can inspect repositories, form plans, edit,
   execute tests, request approvals, recover from interruption, and produce independently evaluated
   evidence.
2. **`research-default`** — an evidence-oriented research agent that can discover sources, acquire
   and normalize documents, extract claims, track citations, identify disagreement, synthesize a
   report, and submit it to an exterior evaluator.

Both products must use the same canonical composition, dispatch, ledger, persistence, replay,
budget, capability, and evaluation paths. Their differences belong in domain packs, plugins,
adapters, prompts, policies, selectors, and evaluators. If the second domain requires changing the
kernel, runtime semantics, or episode engine, the generality claim has failed and the abstraction
must be corrected before expansion.

The immediate execution order remains:

```text
M-4 real foundation run
  -> M-5 independent second-domain proof
  -> M-6 mediated delegation
  -> measured M-7 concurrency decision
  -> M-8 declarative topologies
  -> M-9+ retrieval, durable skills, macros, and governed adaptation
```

M7-01 effect-log measurement may proceed in parallel because it observes sequential behavior and
does not lift invariant I-11. It must not become a pretext for implementing concurrency early.

## Work already completed

The following work was completed during the release-candidate stabilization:

- PR #21 was incorporated into `feat_W4-W6_Higgs_core`, after which the final integration branch
  was reviewed and completed.
- PR #20 was merged into `main` at merge commit `366c71b481459e78c6c9e044697573d15939fad8`.
- The successor branch `feat/m7-effect-log-measurement` was created from that merged mainline and
  published to the remote.
- `LedgerState.digest()` was corrected so non-empty delegated child state contributes to canonical
  identity.
- Historical non-delegating state identity was preserved: an empty child map remains absent from
  the canonical representation, so old non-delegating digests do not change.
- Child insertion order was proven irrelevant to the digest.
- ADR-0091 records the delegation state-digest extension and its compatibility boundary.
- ADR-0092 records that the archived `aether_m456` review bundle is non-authoritative reference
  material and must never be wired into production as a parallel runtime.
- ADR-0092 also rejects the proposed context-store optimization because the claimed 11x resident
  duplication was falsified; the measured reference was 59,000 logical bytes, 7,375 resident bytes,
  and 1.00x against the comparison arm.
- M-6 remains correctly classified as locked and incomplete. ADR-0090 closes only the event-roster
  decision. `agent.spawn`, `SpawnAdapter`, RF-55–RF-59, payload schema convergence, and the kill-tree
  recovery drill remain unfinished.
- RF-86 was made fail-closed when `M-5-BASE` is missing.
- GitHub checkout uses full history so the remote baseline tag is actually available to RF-86.
- The authorized child-digest correction was committed before advancing `M-5-BASE`.
- `M-5-BASE` now points at the final corrected frozen substrate ancestry.
- CI now installs the project's declared Python dependencies.
- CI installs and explicitly qualifies rootless Bubblewrap on Ubuntu runners.
- Ubuntu 24.04's AppArmor restriction on unprivileged user namespaces is handled explicitly on the
  ephemeral runner, and a Bubblewrap startup smoke probe fails early with the real cause.
- Three Ollama absent-tag tests were made hermetic by injecting an installed-tag inventory. Their
  assertions were retained; only the accidental live-daemon dependency was removed.
- Both GitHub push and pull-request CI contexts passed at the final release candidate.
- RF-86 passed all frozen paths: `domain`, `kernel`, `ports`, `runtime`, and `agency/episode`.
- Kernel TCB remained 1,366 logical lines against the 1,438-line ceiling.
- Architecture boundaries, domain blindness, event coverage, RF allocation, documentation links,
  stale paths, duplication detection, secret scanning, package tests, trust tests, security tests,
  replay, registry lifecycle, and runtime tests passed remotely.
- No RF-85 evidence was claimed, no M-4 row was fabricated, and no assertion was weakened or
  xfailed.

## Current authority and decision status

The canonical law and execution documents remain controlling. Archived reports, Higgs material,
Alfa, Fi, and the independent `aether-m4-m8` bundle are research and review inputs. They can suggest
falsifiers, seams, or experiments, but cannot authorize production work.

Current leadership decisions:

- **M-4 is open.** It requires one real, uninterrupted, promotion-eligible coding run with all nine
  evidence rows derived from canonical sources.
- **M-5 is locked until M-4 closes.** Its purpose is to falsify substrate generality with a truly
  independent second domain and zero semantic changes to the frozen substrate.
- **M-6 is locked until M-5 closes.** The event roster is decided, but delegation is not implemented.
- **M7-01 measurement is authorized.** It is observation and analysis only.
- **M-7 implementation is locked.** I-11 remains mandatory until measurement and a successor ADR
  explicitly justify a scheduler.
- **M-8 is locked.** Topologies cannot be evaluated before a sequential baseline exists.
- **M-9+ remains a research horizon.** Retrieval redesign, durable learned skills, macros,
  meta-cognition, and automatic promotion are not current implementation authority.

## Target product architecture

The intended product structure is:

```text
                            Clients
              coding CLI | researcher UI | API | batch
                               |
                        Runtime composition
          profiles | lifecycle | sessions | activation | cleanup
                               |
                    Sequential agency mechanism
                observe -> propose -> authorize -> effect
                               |
                     Trusted kernel dispatch
         grants | attenuation | budgets | policy | provenance
                               |
                    Ports and typed contracts
                               |
       models | tools | MCP | sandbox | evaluator | stores | index
                               |
                     Concrete adapters/plugins

Central truth: append-only event log + content-addressed artifacts
Derived state: reducers + rebuildable projections + measurements
```

### Architectural rules

1. The kernel owns authority semantics, not domain behavior.
2. The runtime owns composition and lifecycle, not coding or research ontology.
3. Domain packs describe tools, prompts, policies, evaluators, and task-specific composition.
4. Plugins implement narrow typed services; they do not create an alternative runtime.
5. MCP is an adapter protocol, never an implicit trust grant.
6. Indexes and caches are rebuildable projections, never canonical truth.
7. The ledger is append-only; corrections are new facts, not mutation of history.
8. Large artifacts live in a blob store. The ledger records identity, provenance, policy, and hashes.
9. Evaluation is exterior to the agent being evaluated.
10. Performance features require measured bottlenecks and falsifiable acceptance criteria.

## Two independent proof domains

### Autonomous coding CLI

The coding client should mature into a product while remaining only a client of the runtime. Its
domain pack should provide:

- repository discovery and scoped file access;
- lexical search, symbol navigation, AST-aware inspection, and diagnostics;
- patch construction and reviewable diff application;
- process execution through sandbox and capability policy;
- task planning and bounded goal tracking;
- test, lint, build, and evaluator adapters;
- human approval for privileged effects;
- session resume, fork, replay, and cold recovery;
- optional MCP connections governed by selectors and explicit grants;
- context compilation, compaction, and evidence rehydration;
- terminal UX for status, receipts, costs, evidence, and approvals.

No code intelligence or CLI feature should become kernel knowledge. LSP, AST, repository maps,
terminal rendering, and patch UX are coding-pack plugins or adapters.

### Evidence-oriented researcher

The research pack must be independent enough to challenge the abstraction. It should provide:

- web, paper, dataset, and repository source acquisition;
- immutable source snapshots or governed references;
- parsing and normalization into typed document artifacts;
- passage and claim extraction with exact source spans;
- citation graph and contradiction tracking;
- temporal metadata and source-quality assessment;
- retrieval over lexical, embedding, and graph projections;
- research plans and bounded query budgets;
- synthesis that distinguishes observation, source statement, and inference;
- exterior verification of citation entailment and report requirements;
- reproducible export of the final report and its complete evidence lineage.

The researcher must not record or expose private hidden chain-of-thought. Scientific observability
means recording observable inputs, outputs, decisions, transformations, tool activity, and evidence,
not demanding inaccessible internal reasoning tokens.

## Event-centered scientific telemetry

Logging should be central, but a single enormous event type would create coupling. Use a small
envelope plus typed payload families.

Every event should carry, where applicable:

- project, run, episode, branch, parent, and principal identity;
- monotonic sequence, schema version, producer, and timestamp source;
- composition, run-plan, model-route, environment, and artifact digests;
- capability descriptor, grant, budget lease, and policy decision;
- causation, correlation, parent event, and idempotency keys;
- input and output artifact references;
- measured wall, model, tool, queue, and evaluator timing;
- token and cost accounting, including known/unknown status;
- cache key identity, hit/miss, source, and validation result;
- selector and resolved-resource information;
- terminal result, uncertainty, error taxonomy, and reconciliation state.

Recommended observable payload families:

- model request prepared, model invocation started/completed/failed;
- context layer selected, transformed, compacted, or rehydrated;
- tool or MCP request proposed, authorized, started, settled, or denied;
- source acquired, normalized, extracted, cited, superseded, or rejected;
- artifact created, transformed, evaluated, or promoted;
- index projection built, queried, invalidated, or rebuilt;
- cache lookup, validation, hit, miss, write, or eviction;
- evaluator request, signed verdict, and verification outcome;
- child lifecycle, budget transfer, and recovery reconciliation after M-6 opens.

Privacy and performance require tiered storage:

```text
ledger envelope       small, immutable, queryable
typed event payload   canonical operational fact
blob object           large prompt/output/source/artifact bytes
projection/index      disposable and rebuildable
metrics warehouse     derived aggregates, never authority
```

Content retention must be policy-controlled. Secrets, credentials, personal data, copyrighted
source bodies, and provider-restricted content must not be copied into permanent logs merely because
it is observable. Store governed references or redacted content and preserve a digest where lawful.

## Indexing, caching, and context strategy

### Indexing

Implement indexing as port-backed projections over canonical artifacts:

- coding: path index, lexical index, symbol graph, imports/references, diagnostics, test ownership;
- research: source catalog, lexical passages, embeddings, citation graph, entity/time indexes;
- common: artifact identity, lineage, provenance, event ranges, and evaluator outcomes.

Every index must support deletion and full deterministic rebuild. A search result must name the
index version, query, selected artifact IDs, ranking metadata, and canonical source digest.

### Caching

Cache keys must bind all behavior-affecting inputs. Useful caches include:

- provider prompt-prefix cache;
- model result cache for explicitly deterministic/cassette-eligible calls;
- parsed document and AST cache;
- repository symbol/index shards;
- tool result cache for pure observations;
- evaluator and oracle cache only where the subject and oracle identities are exact;
- context compilation and tokenization cache.

A cache hit is evidence, not invisibility. Log the key, identity inputs, source artifact, age,
validation, and hit/miss. Privileged effects are never replayed from a generic result cache.

### Context and compression

Context compilation should use progressive disclosure:

1. always-on law and task identity;
2. short plugin and skill descriptions;
3. on-demand tool schemas and skill bodies;
4. ranked source or code excerpts;
5. bounded recent trajectory;
6. structured compaction with preserved decisions, identifiers, failures, and pending intents;
7. rehydration from immutable artifacts when exact detail is needed.

Compression must never silently replace canonical evidence. Store the source range, compactor
identity, instructions, output digest, token counts, and a link to the original artifact.

## Delivery roadmap and TODO register

| Priority | Work item | Concrete outcome | Gate / acceptance |
|---:|---|---|---|
| P0 | Finish M-4 RF-85 | One real uninterrupted coding run producing all nine source-derived evidence rows | No mocks, stitched traces, fallback, or manual repair |
| P0 | Implement M7-01 capture | Sequential effect log over a fixed-seed task set | Resolved selectors, sink, idempotency, timings, cache rate |
| P0 | Define telemetry envelope v1 | Common identities and typed observable transformation records | Backward-compatible schema and event-coverage proof |
| P0 | Establish privacy/retention policy | Clear rules for raw prompts, sources, secrets, PII, and blob retention | Fail-closed redaction and access tests |
| P1 | Open M-5 after M-4 | Formal/research Pack #2 executes without semantic substrate changes | RF-86 plus independent evaluator |
| P1 | Build `research-default` | Source-to-claim-to-citation-to-report workflow | Same runtime, WAL, ledger, replay, and evidence path as coding |
| P1 | Prove two-domain parity | Coding and research traverse one public execution authority | No domain branch in kernel or episode engine |
| P1 | Freeze plugin taxonomy | Model, tool, skill, MCP, session, sandbox, store, evaluator, index, UI seams | No universal god-plugin and no sixth SPI by accident |
| P1 | Add governed MCP adapter | Typed discovery/invocation with grants, selectors, receipts, and timeouts | Server cannot mint authority or write privileged history |
| P2 | Add rebuildable indexes | Coding symbol/AST and research document/citation projections | Cold rebuild equality and deletion tests |
| P2 | Add content-addressed caches | Measured caches for pure or identity-bound operations | Logged hit/miss, validation, invalidation, and stale-denial |
| P2 | Improve context compiler | Demand-loaded skills, tool search, evidence ranking, compaction provenance | Quality/cost/residency benchmark; exact artifact rehydration |
| P2 | Complete M-6 prerequisites | Spawn schema, adapter, RF-55–RF-59, attenuation and kill-tree proof | Only after M-5; no kernel domain semantics |
| P3 | Decide M-7 | Quantify independence, attainable speedup, contention, and recovery cost | Cancel below about 30%; successor ADR otherwise |
| P3 | Implement declarative topologies | Planner/executor/verifier and researcher fan-out as composition data | M-8; zero kernel or episode-engine topology diff |
| P3 | Productize coding CLI | Sessions, diffs, approvals, skills, hooks, MCP, diagnostics, replay | CLI remains a client of runtime authority |
| P3 | Productize researcher | Collections, citation graph, contradiction analysis, reproducible export | Exterior citation and factuality evaluation |
| P4 | Scientific evaluation system | Preregistered paired experiments, A/A floor, confidence intervals, cost/quality curves | No self-promotion from benchmark wins |
| P4 | Advanced retrieval and memory | Hybrid search, evidence-ranked durable skills, governed routing | M-9+ only; rebuildable, attributable, reversible |

## Leadership conclusion

The competitive advantage should not be “more agent features.” It should be that every feature is
composable, attributable, capability-bounded, reproducible, independently evaluated, and removable
without changing the trusted substrate.

The next engineering branch should implement only M7-01 measurement while the external M-4 lane
qualifies and executes RF-85. After M-4 closes, the highest-value work is the independent research or
formal pack. That is the experiment which turns Vanguard from a coding harness into a demonstrated
meta-framework.

# RESEARCH COMPLEMENT

## Research method and source posture

This complement uses current first-party material. DeepSeek Harness is explicitly a developer
preview whose APIs are expected to evolve, so it is architectural inspiration rather than a stable
dependency. Claude Code is studied as a product and extension architecture, not as normative law for
Vanguard.

Primary sources:

- [DeepSeek Harness developer preview](https://deepseek.com/harness/en/)
- [DeepSeek Harness source repository](https://github.com/deepseek-ai/deepseek-harness)
- [Claude Code extension architecture](https://code.claude.com/docs/en/features-overview)
- [Claude Agent SDK loop and context management](https://code.claude.com/docs/en/agent-sdk/agent-loop)

## DeepSeek Harness findings

DeepSeek Harness presents a Cordis kernel that manages plugin mounting, unmounting, and dependency
relationships while placing agent capabilities in plugins. Its published capability set includes
models, tools, skills, sessions, sandboxes, storage, loops, scheduling, and UI. Composition is
configuration-driven, allowing capabilities to be selected or replaced without editing the harness
source.

It also presents append-only session history as the basis for trajectory inspection, resume, fork,
search, and replay. The recorded surface includes system prompts, model-visible information, tool
calls/results, context injections, and subagent scheduling. This strongly supports Vanguard's
event-centered direction.

DeepSeek exposes several modes:

- **Standard:** full coding-agent capabilities;
- **Code:** model-generated TypeScript composes multiple tool calls;
- **Minimal:** persistent shell plus a string-replacement editor for clean benchmarking;
- **Creator:** runtime inspection and plugin/preset experimentation.

### What Vanguard should adopt

- Capability composition through explicit configuration.
- Replaceable plugin implementations with narrow declared dependencies.
- A minimal benchmark mode that removes optional harness assistance.
- A creator/developer inspection surface for composition, activation, events, and plugin health.
- One event stream supporting inspection, replay, resume, and fork.
- Runtime modes as identity-bearing profiles rather than conditionals scattered through the code.
- Tool-heavy programmatic orchestration as an optional plugin after authority and measurement gates.

### What Vanguard should not copy directly

- **“Everything is a plugin” without a trust boundary.** Authority verification, canonicalization,
  budget algebra, and durable intent must remain in Vanguard's bounded TCB.
- Plugin-owned privileged event writing. Plugins propose; canonical runtime writers append governed
  history.
- Plugin-defined authority semantics or direct grant creation.
- Scheduling or loop replacement before M-7/M-8 gates.
- Raw logging without privacy, retention, and provider-policy controls.
- A second framework kernel alongside the existing runtime.

The better formulation for Vanguard is: **everything that does not define trust semantics should be
replaceable; everything that defines trust semantics must remain small, explicit, and proved.**

## Claude Code findings

Claude Code separates extension concerns instead of representing every concern with one mechanism:

- project instructions provide persistent context;
- skills provide on-demand knowledge and workflows;
- code intelligence provides symbol navigation and diagnostics;
- MCP connects external services and tools;
- subagents isolate context and return summaries;
- dynamic workflows coordinate larger batches of subagents;
- hooks guarantee lifecycle-triggered automation;
- plugins package skills, hooks, subagents, and MCP servers for distribution.

This separation is especially useful. A skill is interpreted by a model; a hook is deterministic
automation. Claude's documentation explicitly recommends enforcement hooks for invariants rather
than relying on prompt instructions. Vanguard should go further: security enforcement belongs in
kernel/runtime policy, while hooks are still mediated effects subject to capabilities and receipts.

Claude Code also uses progressive context loading. Persistent instructions and built-in tool
definitions are recurring context; skill descriptions load cheaply; full skills and MCP schemas are
deferred; subagents receive isolated contexts; hooks run outside the model context unless they return
information. Code intelligence can reduce broad file reads by returning symbol-level facts.

Its long-session design includes automatic compaction, explicit compaction-boundary events,
pre-compaction hooks, session resume/fork, and externally supplied session stores. The documentation
warns that compaction can lose early details, which validates Vanguard's structured compaction and
immutable-artifact rehydration direction.

### What Vanguard should adopt

- A clear taxonomy: instructions, skills, tools/MCP, hooks, subagents, and packaging are distinct.
- Demand-loaded skill bodies and tool schemas.
- Code intelligence as a plugin-backed index rather than repeated whole-file reading.
- Subagent context isolation after M-6, returning compact typed results rather than entire histories.
- Explicit compaction events with source ranges and rehydration links.
- Session resume and fork over one durable event lineage.
- Lifecycle hooks for diagnostics, formatting, notifications, and policy-neutral automation.
- Namespaced plugin contributions and deterministic precedence rules.
- Context-cost telemetry per layer, tool schema, source excerpt, and subagent return.

### What Vanguard should strengthen beyond Claude Code

- Hooks must not run with ambient host authority; they require ordinary capability dispatch.
- MCP tools must be selector-scoped and receipt-producing.
- Compaction summaries must be attributable transformations, never replacement evidence.
- Session continuity must verify event-chain and run-plan identity before resumption.
- Subagent spend and authority must fold into the parent budget and provenance.
- Evaluators remain unreachable from the worker being judged.
- Plugin installation and activation require schema validation, lifecycle evidence, and deterministic
  cleanup.

## Comparative architecture map

| Industry pattern | Vanguard mapping | Decision |
|---|---|---|
| DeepSeek Cordis kernel | Runtime registry and composition lifecycle | Reuse the modular principle; do not replace Vanguard runtime |
| DeepSeek capability plugins | Ports, adapters, packs, binding providers | Adopt narrowly, outside the TCB |
| DeepSeek append-only session log | Canonical event store, ledger reducers, trajectories | Strengthen with durable intent, signatures, and source-derived evidence |
| DeepSeek runtime modes | Identity-bearing execution profiles | Adopt through canonical composition |
| DeepSeek code mode | Programmatic bounded tool orchestration | Defer until M-7 measurement and security design |
| Claude project instructions | Context policy and repository instruction layer | Keep small, persistent, and explicitly sourced |
| Claude skills | Versioned on-demand skill artifacts | Add after generality proof; record versions and invocation |
| Claude hooks | Lifecycle-triggered automation | Mediate through capabilities; hooks are not a security boundary |
| Claude MCP | External service/tool adapters | Add governed MCP port/adapter with selectors and receipts |
| Claude subagents | M-6 mediated child episodes | Implement only through `agent.spawn` and attenuation |
| Claude code intelligence | Coding-pack index plugin | Add rebuildable LSP/symbol/diagnostic projection |
| Claude compaction | Structured context compaction | Preserve transformation lineage and exact rehydration |
| Claude resume/fork | Event-sourced continuation and branch identity | Existing direction; strengthen product UX |

## Research-driven final recommendation

DeepSeek demonstrates the value of broad composability and a unified event stream. Claude Code
demonstrates the value of a precise extension taxonomy, progressive context loading, isolated
subtasks, and lifecycle automation. Vanguard should combine those strengths with its own more
rigorous trust spine:

```text
DeepSeek-style composability
  + Claude-style extension taxonomy and context economy
  + Vanguard capability security, durable intent, replay, and exterior evaluation
  = differentiated general-task meta-framework
```

The proof must remain empirical. First close RF-85. Then run the coding and research/formal packs
through identical substrate semantics. Measure context cost, retrieval quality, tool reliability,
recovery, latency, cache behavior, evaluator agreement, and total cost. Only then authorize
delegation, concurrency, topologies, learned routing, or automatic improvement.
