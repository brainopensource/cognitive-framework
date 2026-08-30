# AETHER / Vanguard v0.9.2 Backend Architecture & Coding-Harness Review

## 1. Repository & Evidence Baseline

Repository state at review start:

| Item | Result |
|---|---|
| Branch | `feat/beta-release_electroweak-v091` |
| HEAD | `9b3fa8979c25ca41a8203eb94f52a0bd4e6429be` |
| Upstream | `origin/feat/beta-release_electroweak-v091` |
| Initial working tree | Modified: `package.json`, `package-lock.json`, `vanguard/clients/cli/tsconfig.json` |
| Python | 3.12.3 |
| Node | 22.18.0 |
| npm | 10.9.2 |
| uv | 0.5.9 |
| ripgrep | Available |
| pytest | Available |
| `just` | Not installed |
| `sqlite3` CLI | Not installed; Python `sqlite3` used read-only |
| ast-grep | Not installed; `/usr/bin/sg` exists but is not established as ast-grep |
| Griffe / SCIP Python / tree-sitter Python | Not installed |

The working tree changed substantially during the review due to concurrent work. I did not touch production Python or canonical documentation. LDA inspection unexpectedly changed tracked `.lda/index.db*` artifacts; I did not revert them because the working tree was concurrently changing and destructive Git operations were prohibited.

The Tier-1 packet is stale relative to HEAD:

- Packet HEAD: `7d46c7f5528cf23a7b6cfcd6e02ece4d7f32e6a0`
- Reviewed HEAD: `9b3fa8979c25ca41a8203eb94f52a0bd4e6429be`

It remained useful for navigation, but material conclusions below were checked against current source and stored evidence.

Validation actually executed:

- Boundary linter: PASS, 613 source files.
- TCB budget: PASS, 1,384 logical LOC against 1,438.
- Domain blindness: PASS, with a non-fatal warning about absent legacy `layer0/`.
- Isolation policy: PASS.
- Focused tests: 34 run; 32 passed, 2 environment-related errors:
  - local socket creation prohibited by sandbox;
  - `/tmp` benchmark workspace rejected by configured `AETHER_WORKSPACE_ROOT`.
- Deterministic LAM `t1-calculator`: PASS, 4 calls, 2,238 tokens, 7 recorded turns, 517.61 ms, `$0`.
- `just check` and `just verify`: not run because `just` is unavailable.
- Full suite: not run.

The Tier-1 “overall PASS” should not be taken literally: its detailed test log contains path-hygiene failures caused by generated development logs.

## 2. Vision / SPEC / Milestone Alignment

The actual authority order is:

1. [VISION.md](VISION.md)
2. [docs/SPEC.md](docs/SPEC.md)
3. [docs/decisions.md](docs/decisions.md)
4. As-built architecture/reference documentation
5. [docs/execution/active.md](docs/execution/active.md)
6. Milestone contracts
7. Research/reports as non-authorizing evidence

The proposed v0.9.2 work aligns with the constitutional design if:

- the kernel stays domain-blind;
- repository intelligence remains above the substrate;
- all actions continue through S0–S12;
- context, plans, verification and recovery remain event-observable;
- projections and indexes never become authoritative state;
- external evaluation remains distinct from agent completion;
- existing `IndexPort`, context SPI, model port and pack composition seams are extended before creating new authorities.

There is an execution-governance caveat: the active board contains unresolved M-7/M-8 and baseline conflicts. A v0.9.2 technical plan can be prepared, but implementation authorization must be reconciled in the active execution authority.

The requested root `CONTRIBUTING.md` does not exist.

## 3. Actual Backend Architecture

| Subsystem | Classification | Finding |
|---|---|---|
| Domain primitives and wire types | AS_BUILT | Strong value-object, event, artifact, selector and schema foundation. |
| Ports and five SPIs | AS_BUILT contracts / PARTIAL integration | Interfaces exist, but several code-default SPI implementations are not on the canonical execution path. |
| Kernel and capability enforcement | AS_BUILT | S0–S12, attenuation, typed budgets and fail-closed policy are real and tested. |
| Event store and causal ledger | AS_BUILT | SQLite-WAL, append-only envelopes, single emitter and cold folding are real. |
| Artifacts and provenance | AS_BUILT | CAS and context/model capture exist; benchmark reporting fails to preserve trajectory identity. |
| `AgentView` | PARTIAL | Reducer exists, but current event-field mismatches erase useful action and budget semantics. |
| Agency turn loop | AS_BUILT generic loop | Sequential model/tool loop, bounded turns, protocol recovery and delegation entry exist. |
| Planning | PARTIAL | `PlanRevised` and meta-control exist, but there is no production coding plan/replan state machine. |
| Context compilation | PARTIAL | Prefix stability and compaction exist; manifest policy is not passed into the compiler. |
| Repository intelligence | PARTIAL | `IndexPort` and a static repo map exist; ranked/bounded task packets are not integrated. |
| Delegation | PARTIAL | Mediated spawn is real; topology/2 and workflow scheduler remain isolated. |
| Tooling | PARTIAL | Read/search/patch/exec work, but ergonomics and patch correctness are below frontier harness needs. |
| Retry/recovery | PARTIAL | Provider transport retry and proposal-protocol retry exist; effect/transport recovery counters are unused. |
| Verification | MISSING from production completion | A tested verification gate exists but is not wired to episode completion. |
| Memory and learning | AS_BUILT mechanism | Durable scoped memory and governed promotion exist; acceptance evidence remains conflicted. |
| Evaluation/assurance | AS_BUILT substrate / PARTIAL harness use | Exterior evaluation works, but coding completion is not conditioned on local verification. |
| Packs/plugins | PARTIAL | Two overlapping code-default representations exist; production uses agency manifests, while richer pack middleware is mostly dormant. |
| Model adapters | AS_BUILT / PARTIAL adaptation | OpenRouter, Ollama, LAM, cassette and fake are substantial; task-level routing and recovery remain weak. |
| Application services | PARTIAL | Start/resume/status exist, with documented profile mismatch and incomplete cognitive continuation. |
| Benchmark infrastructure | PARTIAL | Sealed oracles and cost controls exist, but the current matrix is not a valid capability baseline. |

## 4. Vanguard Framework Assessment

Framework strengths:

- Small domain-blind kernel with preserved headroom.
- Clear separation of declared composition from observed trajectory.
- Typed provider errors rather than conflating provider failure with task failure.
- Durable intent before effects.
- Single runtime authority through `HarnessSession`.
- Fresh-process state reconstruction and settled-effect suppression.
- Prefix-stable context compiler and observable compaction identities.
- Optional memory, index, delegation and meta-control seams.
- Strong provider adapter implementation, including timeout handling, streaming, provider retries and cost telemetry.

Framework weaknesses:

1. Projection contracts are not aligned with emitted event fields.

   `ProposalProduced` emits `action`, while `AgentView` reads `verb`. The inspected SQLite run therefore reduced every proposal to `verb="unknown"`. Effect events similarly reduced to generic `"effect"`, and budget consumption remained empty.

2. Several declared evolution seams are mechanisms without production callers.

   `IPlanner`, `IContextManager`, repository middleware, deterministic test parsing and verification are implemented and tested independently, but do not drive the canonical loop.

3. Generic retry state is incomplete.

   `ProtocolRecoveryState.transport_retries` and `effect_retries` have mutation methods but no production consumers. Provider adapters retry transport internally; the episode engine immediately terminates on a failed `ModelPort` result.

4. Resume reconstructs safety and accounting better than cognition.

   It preserves ledger state, turn bounds and effect idempotency. It does not reconstruct prior model/tool dialogue into `PromptAssembler`; `AppService.resume()` replaces the task brief with `Resume run <id>`. This is reliable restart, but not full semantic continuation of the agent’s working context.

5. Context policy is not actually bound.

   [session.py](vanguard/packages/runtime/session.py) constructs `ContextCompiler` without the manifest’s context policy. The default happens to resemble the default pack, but alternate pack settings are not authoritative.

## 5. Coding Harness Assessment

The concrete coding path is:

```text
TaskContext
→ manifest composition
→ static workspace discovery/repo map
→ ContextCompiler
→ model proposal
→ phase-based tool restriction
→ kernel dispatch
→ tool receipt in L5
→ repeat or accept model finish
→ exterior evaluation after termination
```

Major gaps by phase:

| Phase | Assessment |
|---|---|
| Task ingestion | Basic brief and workspace binding work; no structured task constraints or expected verification plan. |
| Discovery | Static file/symbol map works, but no task-ranked packet or targeted dependency/test selection. |
| Search/read | Basic tools only; no line ranges, glob/list, symbol lookup tool, batched read, or duplicate-read suppression. |
| Planning | Model prompt behavior, not durable harness state. |
| Tool selection | Phase gating exists but advances on attempted verbs, not successful outcomes. |
| Patching | Whole-file/old-new/simple-diff support; unified-diff implementation is unsafe for complex hunks. |
| Test execution | Works and returns exit details through the environment adapter. |
| Test interpretation | Parser exists but is not integrated. |
| Retry/recovery | Model sees raw receipts; no classified recovery policy per failure type. |
| Compaction | Generic eviction works, but structured consolidation is heuristic and not grounded in durable task state. |
| Termination | Model `finish` can complete without a successful test. |
| Evidence | Runtime captures rich artifacts when configured; benchmark rows discard trajectory digests. |

The highest-leverage coding-harness defect is not lack of agents or concurrency. It is the missing closed loop:

```text
patch → execute relevant verification → parse result → admit/reject completion → replan
```

## 6. LDA / Repository Intelligence / Context Strategy

LDA at the reviewed HEAD reported:

- Status: `HEALTHY`
- Documents: 0
- Files: 0
- Symbols: 0
- Relations: 0
- Queries for `AgentView` and coding-harness topics: empty results

Therefore LDA was not useful for this review beyond demonstrating an indexing/configuration failure. Generated knowledge was more useful, but also contained stale mappings, such as `EpisodeEngine` mapped to the nonexistent historical `agency/turns.py`.

The recommended repository-intelligence design should not add LDA to Vanguard:

```text
Task
→ code-pack IContextManager
→ optional repository intelligence provider
→ IndexPort / LDA adapter / SCIP adapter
→ ranked canonical docs + symbols + dependencies + tests
→ bounded ContextBundle
→ existing ContextCompiler
```

Use the existing `IContextManager` and `IndexPort` seams:

- Keep provider-specific querying in the code pack or adapter.
- Return value-only bounded context.
- Record provider identity, index snapshot digest, query digest, selected references and token count.
- Never let the provider propose actions or carry authority.
- Preserve a deterministic `FileRepoIndex` fallback.
- Treat LDA/SCIP indexes as reconstructible projections.

The static full repo map should be replaced or bounded for large repositories. It currently occupies the stable prefix and can make the non-compactable L1–L4 floor exceed the context ceiling.

## 7. LAM + Local Challenge Development Loop

Available corpus:

- Canonical local SWE-style challenge objects: 29
  - Tier distribution: 3/4/4/6/5/4/3 across tiers 1–7
  - 12 bugfix, 15 feature, 2 greenfield
  - Each includes public source and a sealed Python oracle
- Greenfield/dogfood directories:
  - 3 dogfood tasks
  - 1 declared greenfield API task
  - 1 additional historical greenfield webapp directory
- LAM scenarios: 254
  - Tier 0: 1
  - Tiers 1–10: 25, 35, 36, 40, 30, 18, 15, 12, 23, 19

LAM supports:

- `lam-replay`
- `cassette-exact`
- `ollama-live`
- OpenAI-compatible and Ollama-compatible HTTP surfaces
- deterministic turn advancement from observed tool results
- request/response hashes and SQLite trace storage

Recommended fast loop:

1. Unit/contract tests for policy and reducer changes.
2. Failure-specific LAM scenarios:
   - premature finish/no patch;
   - malformed tool call;
   - truncated patch;
   - failing test then correction;
   - incomplete multi-file patch;
   - duplicate read;
   - provider retry exhaustion.
3. Run a stratified fixed subset of local sealed-oracle challenges.
4. Compare control/treatment trajectories in SQLite.
5. Only then run a small real-model canary.

LAM is useful for regression and counterfactual control logic, not for estimating general coding ability or SWE-bench performance.

## 8. SQLite / Historical Trajectory Findings

Read-only databases inspected:

### Vanguard event database

One retained frontier workspace database contained:

- 244 events
- 2 episodes
- 14 proposals
- 12 completed effects
- 1 failed effect
- 6 approval requests
- 28 artifact records
- 28 evidence claims

Observed episode behavior:

- Episode 1: 7 proposal turns; two reads, two patches, three command attempts; first test command ran zero tests; later checks passed; episode still ended `abandoned`.
- Episode 2: two reads, two searches, one successful command, then finish; episode completed.
- Model usage was recorded in `ProposalProduced.diagnostics`.
- `AgentView` reconstructed proposals as `unknown`, effects as generic `effect`, no budget consumption, and zero context epochs.

Only one durable benchmark event database was discovered, so duplicate-read rates, retry distributions and aggregate trajectory metrics cannot be estimated responsibly.

### LAM database

Current read-only snapshot:

- 254 scenarios
- 598–631 trace/call rows depending on concurrent snapshot timing
- 95 OpenRouter traces across 42 scenario IDs
- 76/95 marked passed
- 503 LAM replay traces marked passed

The OpenRouter history is heterogeneous:

- multiple harness names and revisions;
- repeated scenarios;
- synthetic/fabricated challenge families;
- no evidence that these are official SWE-bench evaluator results;
- some “SWE Verified” names are harness labels rather than benchmark qualification.

Consequently, the 80% aggregate is historical local-corpus behavior, not a current Vanguard baseline and not an SWE score.

## 9. Current Benchmark Baseline

The strongest checked live report was `live_27_clean_report_v2.json`:

- 27 rows attempted.
- 16 `DATASET_INVALID` because the untouched baseline already passed.
- 11 remaining rows:
  - 4 `COMPLETED`
  - 7 `NO_PATCH`
- Nominal valid-row rate: 4/11 = 36.4%.
- Coding + bugfix rows only: 4/7 = 57.1%.
- All 11 valid rows were variations over one unique Easy LRU task.
- All 11 had `trajectory_digest = null`.
- Median prompt tokens: 49,361.
- Total prompt tokens: 519,724.
- Cost was not preserved.

This is evidence of four successful repairs, but not a defensible benchmark baseline.

A separate 27-row DeepSeek report recorded 27/27 `NO_PATCH`. Another MiniMax report recorded 2/27 completion. Those reports also lacked trajectory digests.

The older `live_27_attempts.json` is explicitly contaminated by legacy oracle exposure and recorded:

- 24 abandoned
- 3 instrument errors
- zero events emitted
- fixed/default telemetry fields in places

It is not valid comparative evidence.

Current real baseline: partially established only as individual historical observations. No SWE-bench Verified or Pro baseline is established.

## 10. Observed Failure Modes

Confirmed from real run artifacts or source/data inconsistencies:

1. `NO_PATCH` / premature completion.
2. Model completion without verification admission.
3. Abandonment despite later successful commands.
4. Running a command that executes zero tests.
5. Very large prompt usage on a tiny task.
6. Missing trajectory digest in benchmark results.
7. Benchmark loss of the runtime terminal/reason.
8. Invalid benchmark fixtures: 16/27 rows.
9. Read-only Tutor/Research presets evaluated using a patch-required oracle.
10. Projection loss: proposal verbs become `unknown`.
11. Budget projection remains empty despite budget events.
12. Manifest context policy not wired.
13. Dormant repository and testing middleware.
14. Duplicate pack/composition representations.
15. Resume changes the brief and does not rebuild dialogue.
16. LDA reports healthy with an empty index.
17. Generated symbol mappings contain stale paths.

Not established from available evidence:

- aggregate duplicate-read rate;
- context-compaction frequency across real runs;
- retry efficiency;
- cache-hit rate;
- subagent benefit;
- per-task cost distribution;
- official SWE task success.

## 11. Frontier Capability Gap

The largest gap to strong coding harnesses is disciplined stateful execution, not substrate security.

| Capability | Current gap |
|---|---|
| Repository understanding | Static regex repo map; no task-ranked dependency/test context. |
| Persistent task state | Ledger exists, but coding plan, verification state and hypotheses are not first-class projections. |
| Planning/replanning | Prompt-driven; meta-controller is not a practical coding planner. |
| Tool ergonomics | No range reads, file listing/globbing, symbol lookup, batched observation or structured diagnostics. |
| Patch reliability | Complex unified diff semantics are insufficient. |
| Verification loop | Not enforced before finish. |
| Failure interpretation | Tested parser exists but is not connected. |
| Retry/recovery | Failure classes do not select recovery actions. |
| Context efficiency | Static full map and repeated growing transcripts produce high token use. |
| Model adaptation | Provider-specific wire handling is good; task/preset capability adaptation is weak. |
| Trajectory learning | Rich runtime evidence exists, but benchmark persistence breaks linkage. |
| Benchmark validity | Current matrix cannot support capability claims. |
| Parallelism/subagents | Available mechanisms, but no evidence they are the current bottleneck. |

## 12. v0.9.2 Framework Improvements

### F-092-01 — Repair semantic projection fidelity

- Problem: `AgentView` cannot see actual actions or budget usage.
- Evidence: current SQLite events emit `action`; reducer reads `verb`; reconstructed attempts are `unknown`.
- Hypothesis: aligning reader compatibility with emitted fields restores useful replay, meta-control and analysis without changing event identity.
- Implementation: update compatibility reads in [agent_view.py](vanguard/packages/domain/ledger/agent_view.py), plus contract vectors for current event payloads.
- Expected behavior: replay exposes exact proposal/effect verbs and consumed additive budgets.
- Metric: 100% of proposal/effect events receive non-generic action attribution; budget totals equal ledger reducer totals.
- Fast experiment: fold the retained 244-event DB before/after.
- LAM: replay a read-patch-test-finish trace and compare projection.
- Local challenge: confirm projection matches actual tool sequence.
- Real model: one canary with cold reconstruction.
- Falsification: any valid current event still reduces to `unknown` or inconsistent budget.

### F-092-02 — Make recovery policy operational

- Problem: retry state declares transport/effect dimensions that are unused.
- Evidence: only protocol/truncation retries are consumed; failed model result terminates immediately.
- Hypothesis: bounded, typed recovery at the framework policy seam reduces avoidable instrument failure without hiding provider errors.
- Implementation: consume typed `retryable` model/effect failures in `EpisodeEngine`; emit recovery decisions; keep provider transport retries in adapters.
- Files: `agency/episode/engine.py`, `protocol_recovery.py`, provider/result contracts.
- Metric: recovery success, attempts per recovered failure, extra tokens, terminal error rate.
- Falsification: no reduction in injected transient failures, or increased loops/cost beyond a preregistered limit.

### F-092-03 — Bind manifest context policy

- Problem: declared context policies do not affect the compiler.
- Evidence: `HarnessSession` omits `context_policy=` when constructing `ContextCompiler`.
- Implementation: carry the already composed policy value into `ContextCompiler`; include it in `D_H` and context-selection evidence.
- Metric: configuration conformance and deterministic context digest.
- Falsification: treatment produces identical behavior even when policies deliberately differ.

## 13. v0.9.2 Harness Improvements

### H-092-01 — Verification-admitted completion

- Problem: the model can finish without a successful test.
- Evidence: verification gate exists only in unit tests; live artifacts contain `NO_PATCH`, zero-test execution and abandonment.
- Hypothesis: rejecting finish until a successful applicable verification receipt materially raises patch/test correctness.
- Implementation: generic completion-admission callback in agency/runtime; coding-specific policy in the code pack. Do not put pytest semantics in the kernel.
- Files: `episode/engine.py`, `session.py`, code-pack testing middleware and pack configuration.
- Expected behavior: finish after a patch is accepted only after a zero-exit, non-empty verification run; failure returns compact diagnostics to the model.
- Metrics: verified completion rate, false completion rate, recovery turns, cost.
- LAM: premature-finish and failed-test-then-repair scenarios.
- Local challenges: fixed stratified 10-task set.
- Real model: 3-task canary.
- Falsification: verified pass rate does not improve or turn/cost growth exceeds the registered ceiling.

### H-092-02 — Task-ranked bounded repository context

- Problem: full static repo maps are high-noise and non-adaptive.
- Evidence: median 49k prompt tokens on one Easy task; context ranker and symbol/import utilities are not wired.
- Hypothesis: ranked task packets reduce prompt tokens and exploratory turns without lowering success.
- Implementation: code-pack `IContextManager` consumes `IndexPort` plus an optional repository-intelligence provider. Select canonical docs, named files, symbols, dependencies and relevant tests under a token budget.
- Files: `packs/code-default`, `runtime/prompt_assembler.py`, composition binding; optional LDA/SCIP adapters outside the substrate.
- Metrics: success, prompt tokens, unique/duplicate reads, discovery turns, context precision.
- Falsification: less than 15% median token reduction, no turn reduction, or any material success regression.

### H-092-03 — Durable coding task state

- Problem: planning and re-planning are implicit transcript behavior.
- Evidence: planner SPI is not the canonical loop; PlanRevised is emitted only by optional meta-control.
- Implementation: a pack-level coding reducer containing goal, planned files, verification command, hypotheses, modified files, last failure and next action. Persist meaningful revisions as existing semantic events/artifacts.
- Metric: wasted-loop count, repeated failed action count, recovery rate.
- Falsification: no improvement over prompt-only control.

### H-092-04 — Reliable editing and tool ergonomics

- Problem: current patching and observation tools are too limited.
- Evidence: unified-diff application is simplistic; no range reads, list/glob or symbol lookup.
- Implementation:
  - range-aware reads;
  - bounded file listing/glob;
  - structured symbol lookup through `IndexPort`;
  - exact patch preimage/anchor validation;
  - proper multi-hunk unified-diff application;
  - structured command receipt with exit code, executed test count and bounded diagnostics.
- Metric: patch-application success, malformed-patch retries, tokens/read, test interpretation accuracy.
- Falsification: no reduction in patch/tool failure rate.

## 14. Verification / Recovery / Context Improvements

The intended coding loop should be:

```text
inspect
→ build bounded task state/context
→ patch
→ run targeted test
→ parse structured result
→ if failure: classify + replan
→ run broader verification
→ completion gate
→ exterior oracle
```

Important separations:

- Local verification is a coding-harness completion condition.
- Exterior oracle remains independent evaluation.
- A passing local test does not self-certify release evidence.
- Provider retry does not imply task retry.
- Resume should reconstruct:
  - task brief identity;
  - last durable plan;
  - settled effects;
  - last verification;
  - compact structured state;
  - not necessarily the entire transcript.

## 15. Benchmark-Driven Experiments

| Experiment | Control | Treatment | Primary metric | Falsification |
|---|---|---|---|---|
| E1 Completion gate | Current finish behavior | Verification-admitted finish | sealed-oracle pass rate | No pass gain or excessive turn growth |
| E2 Context packet | Static full repo map | Ranked bounded packet | tokens/task | <15% reduction or success regression |
| E3 Failure interpreter | Raw command output | Parsed compact diagnostics | recovery success | No improvement in failed-test recovery |
| E4 Durable plan | Prompt-only | persisted coding state | repeated actions/turns | No loop reduction |
| E5 Patch engine | Current `_unified` | exact preimage multi-hunk patching | patch application rate | No reliability gain |
| E6 Model policy | fixed preset | provider capability profile | pass/cost frontier | Dominated on both quality and cost |
| E7 Subagent ablation | direct sequential | one bounded reviewer child | pass rate and overhead | <5-point lift or >25% token overhead |

Subagent and concurrency work should remain P3 until the single-agent loop is reliable.

## 16. Prioritized v0.9.2 Backlog

| Priority / ID | Track | Scope and seam | Tests / benchmark | Acceptance | Dependency / risk |
|---|---|---|---|---|---|
| P0 B092-01 | Infrastructure | Repair challenge preflight and matrix semantics in `frontier_v090` | fixture preflight; role-appropriate evaluators | zero invalid rows; each scored class has valid oracle | Dataset rebuild; medium |
| P0 B092-02 | Infrastructure | Persist runtime terminal, detail, trajectory digest, costs and event DB | runner contracts | every live row links to immutable trajectory | artifact retention; low |
| P0 F092-01 | Framework | Align `AgentView` with emitted event fields | reducer vectors + retained DB fold | exact action/budget projection | schema compatibility; low |
| P0 H092-01 | Harness | Wire verification-admitted completion | LAM failure scenarios + local tasks | no post-patch unverified completion | zero-test detection; medium |
| P1 H092-02 | Harness | Integrate bounded repository context through existing context/index seams | A/B local corpus | ≥15% token reduction without success loss | provider quality; medium |
| P1 H092-03 | Harness | Durable plan/failure/verification projection | replay/recovery tests | cold restart preserves next action | event semantics; medium |
| P1 H092-04 | Harness | Robust patch and observation tools | patch corpus + multi-file tasks | ≥95% valid-patch application on corpus | polyglot support; medium |
| P2 F092-02 | Framework | Typed bounded retry policy | injected transient failures | improved recovery with bounded attempts | retry amplification; medium |
| P2 A092-01 | Adapter | Provider capability profiles and route telemetry | cassette/provider contract tests | no schema/tool mismatch per supported provider | provider drift; medium |
| P2 C092-01 | Framework | Semantic resume packet from ledger/artifacts | fresh-process parity tests | original brief/plan/verification restored | retention/missing blobs; high |
| P2 P092-01 | Infrastructure | Remove or reconcile duplicate code-default composition surfaces | composition equivalence test | one canonical runtime source | migration risk; high |
| P3 X092-01 | Harness | Bounded reviewer child ablation | local paired experiment | preregistered ≥5-point lift | cost/latency; high |
| P3 X092-02 | Infrastructure | LDA/SCIP adapter experiment | packet relevance benchmark | beats `FileRepoIndex` control | external tooling; medium |

## 17. Recommended First Implementation Sprint

Smallest high-leverage sequence:

1. Fix benchmark validity and evidence persistence.
2. Fix `AgentView` action/budget projection fidelity.
3. Wire coding verification as a completion gate.
4. Add the bounded repository-context A/B behind existing context/index seams.
5. Run deterministic and local challenge experiments before any new topology work.

Sprint exit criteria:

- zero invalid tasks in the selected development subset;
- every live row has runtime terminal, trajectory digest, provider/model and cost provenance;
- no patched task may terminate completed without admitted verification;
- retained event DB reconstructs exact verbs and budgets;
- context treatment shows measured token/turn benefit or is rejected;
- focused and full validation commands are recorded honestly.

## 18. Roadmap Toward SWE-bench Targets

```text
No defensible current SWE baseline
↓
fixed deterministic policy regressions
↓
29-task local sealed-oracle baseline
↓
3–5 task real-model canary
↓
20–50 task controlled real-model sample
↓
official SWE-bench Verified qualification
↓
official SWE-bench Pro qualification
```

At every stage record:

- unique tasks and attempts;
- pass rate with confidence interval;
- prompt/completion/cached tokens;
- cost and provenance;
- latency;
- turns and tool calls;
- patch-application success;
- local verification execution and pass;
- retries by failure class;
- trajectory and evaluator digests.

Evidence missing before stronger claims:

- official dataset checkout and evaluator provenance;
- contamination controls;
- immutable harness/model/prompt identities;
- representative task count;
- complete per-run trajectories;
- cost and cache telemetry;
- repeated controlled trials;
- official benchmark scoring.

The ~90% Verified and ~60% Pro figures must remain directional targets.

## 19. Risks and Falsification Criteria

Primary risks:

- Adding a new repository abstraction instead of using existing context/index seams.
- Moving coding policy into the domain or kernel.
- Treating local verification as exterior evaluation.
- Increasing turns and costs through unconditional retry.
- Compaction that removes the failure or task constraint needed for recovery.
- Benchmark overfitting to 29 local tasks or recorded LAM scripts.
- Interpreting repeated traces as independent task coverage.
- Preserving both code-default pack systems indefinitely.
- Trusting “HEALTHY” repository intelligence without non-zero indexed entities.
- Optimizing token usage before evidence linkage is repaired.

The program should be stopped or revised if:

- verification gating does not improve sealed-oracle success;
- ranked context fails the token threshold or harms success;
- durable planning does not reduce repeated actions;
- reviewer children fail the preregistered lift/overhead threshold;
- provider-specific policies cannot remain behind adapters/packs;
- any proposal requires coding semantics in the kernel.

## 20. Exact Next Actions

1. Reconcile v0.9.2 authorization with `docs/execution/active.md`.
2. Freeze a clean analysis subject SHA and working tree for implementation.
3. Repair the frontier challenge subset so every untouched fixture fails its intended oracle.
4. Split coding/bugfix scoring from Tutor/Research scoring.
5. Extend benchmark rows with runtime terminal, terminal detail, trajectory digest, cost and event-store location.
6. Add current-event compatibility vectors for `AgentView`.
7. Implement the completion-admission seam and code-specific verification gate.
8. Create LAM regressions for premature finish, zero tests, failed-test correction and incomplete multi-file patches.
9. Establish a fixed stratified local subset from the 29 challenges.
10. Measure the static repo-map control.
11. Bind the manifest context policy and optional context manager.
12. Run ranked-context treatment against the same tasks and tapes.
13. Proceed to a small real-model canary only if local acceptance criteria pass.
14. Do not begin subagent/concurrency optimization until the single-agent verification loop is green.

No production code or canonical documentation was edited during this review.

```text
REPOSITORY UNDERSTOOD: YES
CANONICAL ARCHITECTURE UNDERSTOOD: YES
EVIDENCE SUFFICIENT: PARTIAL
CURRENT REAL BASELINE ESTABLISHED: PARTIAL
FRAMEWORK GAPS IDENTIFIED: YES
HARNESS GAPS IDENTIFIED: YES
LOCAL EXPERIMENT LOOP READY: PARTIAL
LDA USEFUL: NO
LAM USEFUL: PARTIAL
V0.9.2 PLAN READY: YES
```

---

## 21. Session Addendum — Repository Intelligence as an AI Navigation Atlas

> **Status:** temporary, non-canonical working material. Durable rules from this section must be
> routed to their semantic owners in `AGENTS.md`, `README.md`, `docs/SPEC.md`, architecture,
> reference, and execution documents. This draft is evidence and design rationale, never authority.

### 21.1 Why the atlas matters

The combination of `dev_context_logs/`, `.generated/knowledge/`, `.lda/index.db*`, canonical
documentation, source, tests, and event/benchmark stores can reduce repository discovery from a
workspace-wide read to a small, targeted context packet. This is particularly valuable for AI
development because repository exploration consumes the same bounded context needed for planning,
editing, verification, and recovery.

The desired routing path is:

```text
dev_context_logs/context_summary.*             Tier-1 session bootstrap
        ↓
.generated/knowledge/code-map + ownership      subsystem and canonical owner
        ↓
.generated/knowledge/symbols + links           target symbol, relation and source path
        ↓
canonical documentation                        constraints and architectural intent
        ↓
targeted source + tests + schemas               implementation and executable falsifiers
        ↓
SQLite trajectories / benchmark evidence       observed behavior when the task requires it
```

The corresponding authority rule is:

```text
index points
documentation constrains
source implements
tests falsify
ledger/evidence demonstrates
```

Generated indexes and LDA are reconstructible projections. They MUST NOT override canonical
documentation, source, schemas, tests, Git state, or exact-subject evidence.

### 21.2 Atlas health and fallback

The review found a material distinction between operational availability and semantic usefulness:

- LDA reported `HEALTHY` while indexing zero documents, files, symbols and relations.
- Generated symbol data contained at least one stale historical path for `EpisodeEngine`.
- Tier-1 context was generated for a different HEAD than the reviewed source.

A navigation provider should therefore be considered usable only when:

```text
index_usable =
    schema_valid
    AND source_identity_matches
    AND entity_count > 0
    AND required_paths_resolve
    AND freshness_gate_passes
```

Recommended health states:

```text
HEALTHY  usable and source-matched
STALE    structurally valid but generated for another source identity
EMPTY    structurally valid but has no useful indexed entities
INVALID  schema, integrity or path validation failed
```

If the atlas is not usable, navigation degrades deterministically:

```text
LDA/generated index unavailable
→ rg --files
→ targeted rg query
→ canonical owner document
→ source and tests
```

Development must remain possible without LDA. LDA, SCIP, Kythe-style systems, AST indexes, and
future providers are optional accelerators behind provider-neutral seams.

### 21.3 ContextPacket target contract

The optional repository-intelligence result should be a bounded value, not an agent and not an
authority:

```text
ContextPacket {
    task_digest
    repository_snapshot_digest
    provider_id
    provider_version
    index_snapshot_digest
    query_digest
    selected_documents[]
    selected_symbols[]
    selected_files[]
    dependency_edges[]
    related_tests[]
    estimated_tokens
    omissions[]
}
```

`omissions` makes truncation, unavailable indexes, rejected low-confidence relations, and budget
loss visible. Provider identity and snapshot digests make context selection replayable and allow a
control/treatment benchmark to distinguish retrieval changes from model changes.

The target seam remains:

```text
coding pack IContextManager
→ IndexPort / optional provider adapter
→ value-only ContextPacket
→ existing ContextCompiler
```

No coding intelligence belongs in the domain-blind kernel.

### 21.4 Context selection and budgeting

The conceptual selection objective is:

```text
maximize Σ(i ∈ S) [wt·task(i) + ws·symbol(i) + wd·dependency(i)
                    + wa·authority(i) + wv·verification(i) - wn·noise(i)]
subject to Σ(i ∈ S) tokens(i) ≤ Bcontext
```

The weights are experimental configuration, not normative constants. The durable requirements are
boundedness, deterministic identity, visible omissions, provider neutrality, and no authority
transfer.

The context budget is partitioned as:

```text
Btotal = Bstable-prefix + Btask-state + Bworking-context + Brecovery-reserve
```

with:

```text
Bstable-prefix + Btask-state < Btotal
Brecovery-reserve ≥ Bminimum-recovery
```

Compaction must preserve the task objective and constraints, modified files, current plan,
hypothesis, last relevant failure, last fresh verification, settled effects, remaining budgets and
termination criteria. Old raw reads, duplicate observations and superseded diagnostics may be
summarized or evicted.

## 22. Session Addendum — Coding Harness Contracts to Preserve

### 22.1 Durable coding task state

The coding-specific projection should minimally represent:

```text
CodingTaskState {
    task_identity
    repository_snapshot
    goal
    constraints
    current_plan
    hypotheses
    inspected_files
    relevant_symbols
    modified_files
    verification_plan
    last_verification
    classified_failure
    next_action
    settled_effects
    remaining_budgets
}
```

This belongs above the substrate, normally in the coding pack/harness. Event-sourced operational
truth and existing runtime composition remain authoritative; the projection is reconstructible.

Target coding state machine:

```text
INGEST
→ DISCOVER
→ PLAN
→ EDIT
→ VERIFY_TARGETED
→ RECOVER | VERIFY_BROAD
→ COMPLETE | ABANDON
```

Transitions depend on successful receipts and current state, not merely on an attempted tool verb.

### 22.2 Completion admission and verification freshness

```text
CompletionAdmitted =
    ModelRequestedFinish
    AND TaskRequirementsSatisfied
    AND VerificationApplicable
    AND VerificationExecuted
    AND VerificationPassed
    AND VerificationCoversCurrentWorkspaceState
```

For applicable patch tasks:

```text
modified_files ≠ ∅
AND verification.exit_code = 0
AND verification.executed_test_count > 0
AND verification.workspace_digest = current_workspace_digest
```

Any subsequent patch invalidates the prior verification. A command that collects or executes zero
tests does not satisfy the gate. Analysis-only, documentation-only, greenfield, and testless tasks
require explicit policy rather than silently bypassing verification.

Local verification is an operational completion condition. An exterior oracle remains independent
evaluation and cannot be replaced by the agent's own verification receipt.

### 22.3 Patch correctness

```text
PatchSuccess =
    PreimageMatched
    AND AllHunksApplied
    AND WorkspaceContained
    AND PostimageDigestRecorded
```

Ambiguous anchors and partial multi-hunk application fail closed. A patch receipt should identify
every affected file/hunk and invalidate verification for the changed workspace state.

### 22.4 Failure taxonomy and bounded recovery

Initial failure classes:

```text
CONTEXT_INSUFFICIENT
CONTEXT_STALE
TOOL_SCHEMA_INVALID
TOOL_EXECUTION_FAILED
PATCH_PREIMAGE_MISMATCH
PATCH_PARTIAL
TEST_COLLECTION_EMPTY
TEST_FAILED
VERIFICATION_STALE
PROVIDER_TRANSIENT
PROVIDER_PERMANENT
BUDGET_EXHAUSTED
NO_PROGRESS
PREMATURE_FINISH
```

For failure class `c`:

```text
retry_count(c) ≤ retry_limit(c)
```

A retry is useful only when it is permitted, budgeted, changes the recovery action or relevant
state, and has positive expected information gain. Repeating the same action and arguments against
the same state is a no-progress loop, not recovery.

### 22.5 Minimum trajectory and benchmark identity

Every qualifying run should retain:

```text
run_id, task_id, task_digest, repository_snapshot,
harness_version, manifest_digest, prompt/preset_digest,
provider/model identity, trajectory_digest, event-store identity,
terminal state/reason, patch digest, verification receipt,
exterior evaluator receipt, tokens, cost, latency, turns,
tool calls, and retry counts by failure class
```

Core measures:

```text
success_rate = unique_valid_tasks_passed / unique_valid_tasks_attempted
verification_rate = completed_tasks_with_fresh_verification / completed_applicable_tasks
retry_efficiency = failed_states_recovered / additional_retry_turns
duplicate_read_rate = redundant_reads / all_reads
cost_per_solved_task = total_experiment_cost / unique_valid_tasks_passed
```

Repeated attempts on the same problem do not increase task coverage. A benchmark row without a
trajectory identity is incomplete evidence.

## 23. v0.9.2 Delivery Waves

The implementation plan is organized as six numbered stages, W-092-0 through W-092-5. Up to five
independent work packages may progress in parallel only when they have disjoint authority and file
ownership. Parallelism does not waive the repository WIP, validation, evidence, or review gates.

### W-092-0 — Canonical contracts and navigation

- Reconcile active execution authorization and milestone relationship.
- Canonicalize navigation, context, verification, patch, recovery and evidence contracts.
- Label all planned behavior as target rather than AS_BUILT.
- Add atlas freshness checks and deterministic fallback guidance.
- Establish exact source identities for the implementation subject.

### W-092-1 — Correctness of subjects, evidence and projections

- Repair invalid benchmark fixtures and role/evaluator mismatches.
- Persist terminal reason, model/provider, token/cost and trajectory identities.
- Repair current-event `AgentView` action/budget projection.
- Add retained-ledger reducer vectors and benchmark preflight tests.

### W-092-2 — Verification-admitted execution

- Introduce the generic completion-admission seam above the kernel.
- Implement coding-specific fresh-verification policy in the coding pack.
- Integrate deterministic test parsing and compact failure feedback.
- Cover premature finish, zero tests, failed-test recovery and post-patch staleness in LAM/tests.

### W-092-3 — Structured context and durable planning

- Bind manifest context policy to the compiler.
- Integrate optional provider-neutral ContextPackets through existing seams.
- Persist/reconstruct coding plan, failure, verification and next-action state.
- Compare static-map control with bounded ranked context using exact paired identities.

### W-092-4 — Tooling, patching, recovery and resume

- Add bounded range reads, listing/glob and symbol lookup.
- Add exact-preimage, atomic, multi-hunk patch behavior.
- Make typed transport/effect/task recovery operational and bounded.
- Restore semantic task/plan/verification state on fresh-process resume.
- Add provider capability profiles behind adapter/pack boundaries.

### W-092-5 — Qualification and release closure

- Run deterministic LAM regressions and the fixed local challenge matrix.
- Run a 3–5 task real-model canary only after local gates pass.
- Decide whether a 20–50 task controlled sample is justified.
- Synchronize canonical documentation to final AS_BUILT behavior.
- Run exact-candidate `just check` and `just verify`.
- Make no SWE-bench claim without official dataset/evaluator qualification.

## 24. Two-Contributor Operating Model

### Dev A — Senior Principal

Dev A owns architectural judgment, normative interpretation, integration boundaries, high-risk
changes, experimental design, falsification criteria, and final exact-subject review. “May do
anything” means freedom to work anywhere inside the authorized v0.9.2 scope; it does not waive the
SPEC, security boundaries, Git safety, tests, evidence requirements, canonical ownership, or
milestone authority.

### Dev B — Standard implementation contributor

Dev B follows the normal repository workflow and supports Dev A with bounded packages: tests,
fixtures, adapters, instrumentation, mechanical implementation, index validation and documentation
corrections. Dev B escalates changes to normative law, trust boundaries, event identities,
composition authority or milestone predicates.

Recommended parallel pairing:

| Wave | Dev A | Dev B |
|---|---|---|
| W-092-0 | Contracts, architecture and ownership | Link/path/index validation and examples |
| W-092-1 | Evidence schema and projection review | Fixtures, persistence and reducer tests |
| W-092-2 | Completion-admission integration | LAM/test-parser scenarios and edge cases |
| W-092-3 | Context/task-state integration | Index fallback, ranking fixtures and telemetry |
| W-092-4 | Recovery/resume/provider integration | Tool and patch corpus implementation |
| W-092-5 | Qualification disposition | Matrix execution and artifact audit |

Files or event families shared between packages must have one active owner. Dev B should prepare a
separate bounded patch or hand findings to Dev A instead of concurrently modifying the same seam.
