---
id: draft.coding-agents-benchmark-architecture-future-guide-2026-08-31
class: draft
authority: non-canonical
status: working
subject_head: 4f58736e407ebb0f55f4e8130a250bac7bf219f6
date: 2026-08-31
---

# Vanguard Coding Agents: implementation, benchmarks, architecture and future guide

> Working dossier, not execution authority. Current authorization remains in
> `docs/execution/active.md`; normative behavior remains in `docs/SPEC.md` and
> canonical architecture documents. Results here describe the inspected dirty
> worktree at the subject HEAD above, including concurrent Dev A/Dev B work.

## 1. Executive summary

This work converted the latest Coding Max path from a harness that could patch
files yet frequently terminate as `abandoned` into one that completed a clean
easy/medium/hard ladder. The decisive result was obtained with
`vg-code-max-v3` and `deepseek/deepseek-v4-flash-0731`:

| Challenge | Difficulty | Terminal | External oracle | Calls | Cost |
|---|---|---|---|---:|---:|
| `sota_easy_config_precedence` | easy | `completed` | PASS | 9 | $0.001589 |
| `sota_medium_public_interface` | medium/multifile | `completed` | PASS | 10 | $0.002840 |
| `sota_hard_large_catalog_collision` | hard/242 KB context | `completed` | PASS | 8 | $0.001828 |
| **Observed total** | | **3/3 clean** | **3/3** | **27** | **$0.006257** |

Five independent benchmark definitions were created and verified red at both
public-test and hidden-oracle baseline. Only three were run live. Therefore the
honest scores are:

- executed score: **3/3 (100%)**;
- planned-suite observed score: **3/5 (60%)**;
- two unexecuted cases are not failures and are not passes;
- no official SWE-bench, SWE-bench Verified or SWE-bench Pro claim is made.

The investigation also disproved the earlier hypothesis that cheap flash models
were inherently unable to use the harness. The dominant failures were in prompt
transport, approval re-entry, phase memory, completion signaling, verification
identity and workspace digest semantics.

## 2. Source-of-truth and evidence hierarchy

Use evidence in this order:

1. current source and executable tests;
2. immutable run JSON, cassettes, SQLite events and external-oracle output;
3. the consolidated scorecard;
4. historical reports and draft notes;
5. narrative claims only when corroborated by the above.

Primary evidence:

- `benchmarks/artifacts/ladder/sota5_scorecard_20260831.json`;
- final `sota5_*snapshotfix*`, `sota5_medium_*`, and `sota5_hard_large_*`
  run/cassette artifacts under `benchmarks/artifacts/ladder/`;
- `benchmarks/sota_context/challenges.py`;
- `test/benchmarks/test_sota_context_challenges.py`;
- `test/runtime/test_approval_reentry_feedback.py`;
- `test/adapters/test_git_snapshot_identity.py`;
- `.draft/VG_CODE_MAX_V3_ROOT_CAUSE_FINDINGS.md`.

The LDA index was checked healthy at the subject HEAD: 2,814 files, 20,566
symbols, 22,580 relations, 514 documents, zero sampled stale symbol paths. The
generated knowledge catalog was rebuilt successfully with 120 entries, 244 link
relationships, 12 code mappings and 626 exported symbols.

## 3. Agent and preset inventory

### 3.1 Coding Max facade

`vanguard/packages/apps/coding_max/facade.py` is the desired thin application
boundary. It owns request ergonomics and `fast`, `balanced`, `max` preset
selection, then delegates `run`, `status`, `resume`, `evidence` and `cost` to
`ApplicationService`. It contains no raw provider HTTP and no subprocess loop.

This is the preferred public architecture:

```text
CLI / API / Python caller
        |
        v
CodingMaxFacade                 apps: ergonomics only
        |
        v
ApplicationService             runtime: lifecycle, persistence, resume
        |
        v
Runtime + EpisodeEngine        composition and turn execution
        |
        v
Kernel S0-S12                  authority, budgets, attenuation, receipts
        |
        +----> ModelPort -----> adapter (OpenRouter/Fake/Cassette/LAM)
        +----> Environment ---> mediated filesystem/process implementation
        +----> EventStore ----> SQLite WAL
        +----> Evaluator -----> verification evidence
```

### 3.2 `vg-code-max-v2`

V2 introduced explicit read/search/patch/test tool schemas, repository-map
injection from turn zero, a disciplined inspect-test-patch-verify prompt and
admission gating. It was an important composition improvement but lacked the
explicit finish primitive and inherited several runtime defects later exposed
by live qualification.

### 3.3 `vg-code-max-v3`

V3 is the best empirically supported current experimental composition. Relative
to V2, it adds or depends on:

- explicit `agency.finish` tool;
- complete repository map in environment context;
- concrete tool descriptions and examples on the wire;
- durable episode turn/phase state through approval re-entry;
- capability-derived admission gating;
- clean observation of approved patch and test effects;
- completion verification bound to material workspace identity;
- no-progress recovery based on repeated action/outcome signatures.

Its manifest grants only `fs.read`, `fs.search`, `patch.apply` and `proc.exec`;
`agency.finish` is a control proposal rather than a privileged environmental
effect. The current uncommitted V3 files must still be integrated carefully.

### 3.4 1-Forge

`vanguard/packages/agency/forge/` contains:

- `patcher.py`: atomic multi-file patching with unified diff, block and AST
  replacement strategies, syntax validation and rollback;
- `compiler.py`: bounded context compilation and deterministic JCS-style
  distillation;
- `engine.py`: short reflexive TDD loop, goal contract, admission and stale
  verification rules;
- `facade.py`: `ForgeConfig`, engine construction and task execution.

Forge is useful as a micro-agent experiment, but its facade currently constructs
and runs `ForgeEngine` directly. This differs from the thin Coding Max facade and
creates a second execution-loop architecture. Before calling it a production
preset, decide whether Forge should become a strategy/plugin inside the shared
EpisodeEngine or remain an explicitly experimental agency subsystem.

Evidence is limited: focused Forge tests pass and one live easy pilot passed;
the claimed “25/25 1-Forge” was not substantiated by the inspected artifacts.
The recorded LAM BaaC batch associated with Forge contains 0/3, so it must not
be presented as 25/25.

### 3.5 Experimental variants

`vg-code-max-v2b`, `vg-1-forge-v2` and late V3 manifest edits are present in the
dirty concurrent worktree. They are experimental until they have:

1. a canonical registry entry;
2. boundary and model-literal checks;
3. focused contract tests;
4. red-before benchmark fixtures;
5. clean terminal live evidence;
6. cassette replay parity;
7. a globally green test suite.

Do not create a V4 merely to rename fixes. Promote V3 only after stabilization;
reserve V4 for a materially different architecture with an explicit migration
and comparative benchmark.

## 4. Important primitives and decoupled code

### 4.0 Plugins, skills and adapters used

These terms are not interchangeable:

| Kind | Component | Role in this work |
|---|---|---|
| repository skill | `lda-navigator` / LLM Docs Atlas | healthy-index check, bounded routing, canonical-document discovery and evidence navigation |
| repository skill/tool | `lam-engine` / LLM API Mock | deterministic synthetic completions and exact offline cassette replay |
| harness components/plugins | code-default planner, context manager, toolkit, memory, evaluation and completion policies | composed behavior behind SPI/ports; completion policy owns admission evidence rather than session literals |
| model adapter | OpenRouter | mediated live DeepSeek calls and usage/cost capture |
| model adapter | Cassette/LAM/Fake | network-free replay and hermetic tests |
| environment/evaluator adapters | Git environment, sandbox/evaluator and SQLite store | mediated files/processes, verification and durable events |

No external Codex marketplace plugin was needed. LDA and LAM are repository
skills/tooling; OpenRouter is reached through a Vanguard adapter, never direct
HTTP from the facade or benchmark challenge.

### 4.1 Ports and mediated effects

All external behavior must pass through ports. Model calls use `ModelPort`;
commands/files use the environment and sandbox path; verification uses evaluator
ports; durability uses event/blob stores. Apps remain runtime clients. Adapters
must not import apps, kernel or agency.

### 4.2 Proposal and tool primitives

- `fs.read`: inspect one exact file; bounded directory listing may be used for
  orientation but should not replace repository-map routing.
- `fs.search`: bounded content search; truncation is evidence, never closure.
- `patch.apply`: source mutation whose changed paths feed admission state.
- `proc.exec`: mediated allowlisted command execution and verification source.
- `agency.finish`: explicit completion proposal; admission still decides whether
  completion is legal.

Keep aliases out of the provider payload where possible. Exposing both `read`
and `fs.read` doubles tools, wastes tokens and can produce unstable choices.

### 4.3 Episode state across approval

Approval suspension is not a new episode. `prior_turns` and
`prior_seen_verbs` must survive re-entry. Approved effects are dispatched once,
recorded once and fed back to the next model context even when they fail.
Reconstruction must never replay a settled patch, evaluator run or provider call.

### 4.4 Completion and verification

A completion is valid only if all applicable evidence remains fresh:

```text
source changed
  + changed files inspected/known
  + public interfaces have closed caller/importer analysis
  + relevant direct and regression tests pass
  + migration compatibility/rollback evidence where applicable
  + verification workspace digest == current material workspace digest
  + no unresolved truncation
  = admissible finish
```

Snapshot sequence numbers identify observations, not workspace contents. The
workspace digest must depend only on material state such as Git HEAD/status;
including a monotonic snapshot counter makes every receipt instantly stale.

### 4.5 Context and repository intelligence

LDA is a routing projection, not architectural authority. Use:

```text
context summary -> LDA health -> bounded context query -> symbols/callers
-> canonical docs -> targeted source/tests -> raw events and benchmark evidence
```

For huge repositories, give the agent a symbol-bearing repository map, then
retrieve exact file slices. Do not put every file into the model context.

### 4.6 LAM and cassettes

LAM provides zero-cost deterministic replay. The correct workflow is:

1. record a live provider interaction once;
2. store canonical request, response, tool proposal, usage and digest;
3. replay with network blocked;
4. iterate runtime/prompt fixes offline;
5. spend live budget only on final confirmation.

The final three V3 cassettes replayed 27 records with network blocked and exact
canonical proposal parity. Their digests are preserved in the scorecard.

## 5. End-to-end workflows

### 5.1 Coding task

```text
brief + preset + budget
  -> compose manifest and ports
  -> classify task and build implicated surface
  -> compile objective/repository map/history/tools
  -> model proposes read/search/patch/test/finish
  -> kernel authorizes and attenuates effect
  -> approved effect executes exactly once
  -> receipt/event/blob persisted
  -> result re-enters episode context
  -> completion policy evaluates current evidence
  -> terminal result exposes IDs, digests, state, route, usage, cost, artifacts
```

### 5.2 Benchmark loop

```text
generate/reset fixture
  -> assert public baseline RED
  -> assert hidden oracle baseline RED
  -> run one isolated agent arm
  -> preserve trajectory, SQLite metadata and cassette
  -> run external hidden oracle
  -> reconcile oracle PASS with admission terminal
  -> classify failure signature
  -> fix framework or agent
  -> replay offline
  -> one live confirmation
```

An oracle pass plus `abandoned` is not a clean pass. Report both external-oracle
rate and admission-completion rate.

### 5.3 Cold resume

```text
fresh process
  -> open SQLite WAL event store
  -> fold monotonic durable events into CodingTaskState
  -> validate task/composition/workspace identities
  -> restore objective, discoveries, dead ends, modified files, verification,
     remaining budget, turn history, phase state and exact next action
  -> skip all settled effect IDs
  -> continue from the first unsettled action
```

Resume must never synthesize a prompt such as `Resume run <id>` and call `run`
from scratch.

## 6. How to use the current tooling

### 6.1 Python facade

```python
from vanguard.packages.apps.coding_max import CodingMaxFacade

agent = CodingMaxFacade(workspace="/path/to/repository")
result = agent.run(
    "Fix the failing cache eviction behavior and verify regressions.",
    preset="max",
    model_port="fake",       # deterministic by default for development
    max_turns=40,
)
print(result.to_dict())
```

Use `status(run_id)`, `resume(run_id)`, `evidence(run_id)` and `cost(run_id)`
through the same facade. Live provider selection must be explicit and must use
the model registry and mediated adapter.

### 6.2 Benchmark ladder

Inspect options:

```bash
python3 benchmarks/ladder_runner.py --help
```

Offline/focused development should use fakes or recorded cassettes. A live run,
only after checking the global budget ledger, has the shape:

```bash
python3 benchmarks/ladder_runner.py \
  --tier sota-easy \
  --manifest vg-code-max-v3 \
  --model deepseek/deepseek-v4-flash-0731 \
  --budget-usd 0.01 \
  --max-calls 20 \
  --tag qualification_name
```

Available tiers are `easy`, `medium`, `hard`, `sota-easy`, `sota-medium` and
`sota-hard`. Tags are mandatory operationally even if not syntactically required;
they prevent artifact overwrite.

### 6.3 BaaC

```bash
python3 -m benchmarks.baac.cli verify
python3 -m benchmarks.baac.cli cycle --mode lam --preset vg-1-forge
python3 -m benchmarks.baac.cli report
```

Treat BaaC result JSON as evidence only after checking baseline falsification,
actual model calls, patch presence, terminal state and path hygiene.

### 6.4 Repository navigation

```bash
uv run lda doctor --json
python3 tools/docs_rag_v0.py "task terms" --budget 8000
python3 tools/docs_rag_v0.py --file path/to/file.py
uv run lda tests path/to/file.py
```

If HEAD freshness or row counts are invalid, fall back to targeted `rg`,
canonical documentation, source and tests.

## 7. Benchmark history and honest interpretation

### 7.1 Legacy 27 rows

The old report produced **4/27 = 14.81% raw**. It was not 27 independent valid
problems: three challenges were repeated in a 3x3x3 matrix. Inspection found 16
`DATASET_INVALID` rows and seven `NO_PATCH` rows. On the valid denominator the
score is **4/11 = 36.36%**, but this remains a weak and distorted corpus.

The legacy driver/preset also allowed non-empirical or ungated behavior. Retire
it as a qualification source; preserve it only as historical failure evidence.

### 7.2 Historical Benchmark 20

One prior narrative/artifact lineage reported 18/20 (90%) at approximately
$0.063. The currently inspected `benchmark_20_deepseek_v4_flash.json`, however,
has been overwritten/changed and now reports 0/20 with zero calls and zero cost.
Therefore 18/20 must be labeled **historical and not reproducible from the
current single file** until immutable, content-addressed evidence is restored.

This illustrates why benchmark artifacts must be append-only and digest-bound.

### 7.3 Legacy V3 easy batch

The easy batch reached 10/10 external-oracle success but 0/10 clean admission
completion because runs terminated `abandoned`. This is useful diagnostic proof,
not a 100% agent score.

### 7.4 New SOTA-context five

All five definitions are baseline-red:

1. `sota_easy_config_precedence` — coercion and configuration precedence;
2. `sota_medium_public_interface` — coordinated model/serializer/service API
   change across files;
3. `sota_medium_idempotent_ledger` — idempotent durable event behavior;
4. `sota_hard_large_catalog_collision` — 242 KB generated file with relevant
   collision near EOF and fix in registry logic;
5. `sota_hard_atomic_quota` — concurrent atomic quota semantics.

Items 1, 2 and 4 passed live and cleanly. Items 3 and 5 remain unexecuted due to
the call ceiling and are the immediate unresolved benchmark work.

### 7.5 Budget accounting

- final three clean runs: 27 calls, $0.006257;
- artifact-backed aggregate observed during the session: 332 calls, $0.067647;
- one additional provider call entered from a credential-contaminated full-suite
  test before interruption;
- minimum observed calls: 333 against the requested 300 cap;
- recorded cost remained below $0.15, but exact total cost is unknown because
  the interrupted call was not represented in the benchmark artifacts.

The call cap was violated because two concurrent runners used per-process budget
guards. A process-local counter cannot enforce a workspace-wide budget.

## 8. Root causes and why they mattered

### D1. Prompt tuple silently took a lossy serialization path

The prompt assembler emitted message tuples while the OpenRouter adapter accepted
only lists. Production discarded structured conversation/tool history; JSON
cassette round-trip converted tuples to lists and masked the bug during replay.

### D2. No legal finish under mandatory tool choice

The phase ladder required a tool every turn, while finish previously meant plain
text with no tool call. Runs were structurally unable to complete. The explicit
`agency.finish` primitive removed the contradiction.

### D3. Approval re-entry erased episode history

Every approval suspension reconstructed a fresh engine. Turn indices reset,
no-progress never accumulated, tool feedback appeared detached and budget bounds
became misleading. Durable prior turns fixed this.

### D4. Approval re-entry erased phase memory

`seen_verbs` was engine-local and cleared. The agent could patch, re-enter the
inspect phase and lose access to the expected next behavior. Phase state now
survives the round trip.

### D5. Approved effects bypassed completion observation

The post-approval dispatch path bypassed the callback that records modified files
and verification evidence. Admission then returned `MISSING_SOURCE_PATCH` even
after a real patch. Approved dispatch is now explicitly observed.

### D6. Failed approved effects disappeared from model context

The next turn did not see why a command or patch failed, encouraging repetition.
Failures are now admitted as tool-result context while remaining failed effects.

### D7. `proc.exec` was not recognized as verification

Completion logic recognized generic test/exec aliases but not the production
verb. A successful real test therefore created no usable verification receipt.

### D8. Snapshot sequence polluted material workspace digest

Including `_snapshot_seq` meant two snapshots of unchanged files had different
digests. Verification was stale immediately after it was created. Sequence now
belongs only to snapshot identity; material digest is based on HEAD/status.

### D9. Tool descriptions were decorative

Descriptions existed in manifests but were omitted from provider tool payloads.
They are now transmitted. This was not the sole root cause but reduced the
quality of cheap-model behavior.

### D10. Livelock detector included growing context state

`Turn.signature` contained a digest that changed every turn, making repetition
mathematically impossible to detect. Action/outcome repetition is now evaluated
independently of normal context growth.

### D11. Runtime implicitly discovered `.env`

Model selection read repository `.env` without explicit caller authority. A full
test suite unexpectedly entered OpenRouter. Runtime dotenv discovery was removed;
entry points that support dotenv must load it deliberately. The unavailable-
provider test also explicitly clears process credentials.

### D12. Artifact overwrite and path leakage

Non-unique filenames allowed runs to replace prior evidence. Several concurrent
BAAC/V3 JSON artifacts also contain `/home/rocha`, causing path-hygiene failure.
Use unique run/tag names, relative/redacted paths and content-addressed immutable
artifacts.

## 9. Logs, failures and current gate state

Observed failure signatures included:

- repeated `fs.read({"path":"."})` or `ls` loops;
- `tool is not declared by manifest: patch` after phase reset;
- `MISSING_SOURCE_PATCH` after a patch actually landed;
- passing external oracle with terminal `abandoned`;
- stale verification immediately after successful `proc.exec`;
- all-zero observation result digests;
- accidental credentialed provider call from a nominally hermetic test;
- Unix-socket evaluator failures when the full suite was run inside a restricted
  sandbox;
- absolute local paths persisted in benchmark artifacts.

Focused validation passed across the new changes, including batches of 43, 21,
35, 42 and 31 tests. Architecture/security gates observed as passing:

- boundaries: 730 source files;
- TCB: 1,386 logical lines, limit 1,438;
- domain blindness;
- isolation policy;
- secret scan;
- duplication enforcement;
- knowledge-base generation and LDA health.

The final full-suite run outside the Unix-socket restriction, with provider
credentials explicitly removed at process start, produced:

```text
Ran 2559 tests in 137.677s
FAILED (failures=2, skipped=14)
```

Remaining failures:

1. path hygiene rejects absolute developer paths in concurrent V3/BAAC artifacts;
2. a trust test still observed `OPENROUTER_API_KEY`, indicating another test or
   loader mutates/reloads credentials after process start.

Therefore the repository must not yet be described as globally green.

## 10. Development rules learned from this investigation

1. Prove every fixture red before invoking a model.
2. Separate external-oracle success from admission completion.
3. Record every paid call and replay before making another paid diagnostic call.
4. Make artifacts immutable, uniquely named and content addressed.
5. Enforce budgets in a shared transactional ledger, not process memory.
6. Test approval re-entry as a continuation, not just isolated dispatches.
7. Bind verification to material workspace identity and patch sequence.
8. Ensure failed tools return actionable feedback to the model.
9. Keep completion explicit but policy-controlled.
10. Run benchmark tests with credentials and network blocked by default.
11. Treat generated repository maps as routing hints, never authority.
12. For large files, test both retrieval success and final patch correctness.
13. Never infer model weakness until the exact production prompt/tool payload has
    been independently replayed or probed.
14. A new preset name does not solve an architectural defect.

## 11. Recommended next development sequence

### P0 — restore trustworthy green state

- redact/regenerate path-leaking benchmark artifacts without destroying raw
  forensic copies outside tracked qualification surfaces;
- find the test or loader that repopulates `OPENROUTER_API_KEY` and make tests
  restore environment state;
- run `just check`, focused suites and `just verify`;
- commit/integrate concurrent V3/V2b/Forge-v2 work in coherent units.

### P0 — global budget ledger

Add an SQLite-backed reservation protocol:

```text
BEGIN IMMEDIATE
read aggregate calls/cost
reject if requested reservation exceeds either ceiling
reserve call and maximum estimated cost
COMMIT
execute provider call
reconcile actual usage/cost idempotently by invocation ID
```

This must span processes and use unique invocation IDs so retries cannot double
charge accounting.

### P1 — finish the five-case qualification

Run `sota_medium_idempotent_ledger` and `sota_hard_atomic_quota` offline against
recorded/mock trajectories first. Only authorize live confirmation under a new
budget after the global ledger exists.

### P1 — artifact schema v2

Every benchmark row should include:

- challenge and baseline digests;
- source HEAD and dirty-tree digest;
- harness/composition/model-registry digests;
- run/episode/invocation IDs;
- public and hidden oracle identities;
- terminal and admission reason;
- changed-file and verification digests;
- provider usage/cost with explicit missingness;
- cassette/trajectory/SQLite/blob references by digest;
- `empirical: true|false` and contamination flags.

### P1 — strengthen true cold resume

Add a fresh-process benchmark that crashes after read, patch and verification in
separate variants. Resume must continue from the exact next unsettled action and
prove zero duplicate patch, provider and evaluator invocation IDs.

### P2 — context scaling benchmark family

Expand beyond a single 242 KB file:

- 1M–10M token repositories with sparse relevant symbols;
- generated decoy modules sharing names and signatures;
- cross-language caller/importer chains;
- API migration requiring source, tests, docs and compatibility shim;
- hidden dependency edges discoverable only through index/call graph;
- truncated search where the answer lies beyond the bound;
- generated code that must not be edited directly;
- monorepo package boundaries and build graph selection.

Measure retrieval recall, first-relevant-file rank, irrelevant tokens, affected
test recall, patch precision, clean completion, cost and wall time separately.

## 12. Suggested agents and compositions

Prefer roles as replaceable strategies behind ports, not autonomous loops that
each reinvent runtime, budgets and persistence.

### Retrieval Cartographer

Combines LDA symbols/callers, lexical search, ownership and build graph into a
bounded implicated-file proposal. Output is structured evidence with truncation.

### Interface Impact Auditor

Given changed public symbols, enumerates callers/importers, compatibility risks
and required regression tests. It cannot patch; it closes or rejects surface
analysis.

### Test Cartographer

Maps changed symbols to direct, regression, contract, property and migration
tests; prioritizes cheapest high-information tests first.

### Failure Triage Specialist

Consumes tool stderr, test output and trajectory state; classifies environment,
dataset, model, harness, patch and verification failures. It proposes the next
diagnostic action without mutating source.

### Patch Synthesizer

Receives a bounded goal contract, implicated files and failing evidence. It may
produce candidate patches but cannot admit completion.

### Adversarial Verifier

Creates hidden tests, mutation tests and counterexamples after a candidate patch.
It should use a different model/strategy or deterministic solver where possible.

### Migration Guardian

Specialist for schemas/APIs/data migrations. Requires forward compatibility,
rollback evidence, idempotency and mixed-version behavior.

### Budget Governor

Deterministic shared service that reserves provider/evaluator budget and chooses
the cheapest eligible route from observed capability data.

### Trajectory Miner

Offline component that clusters failures, identifies reusable successful
subtrajectories, produces LAM cassettes and proposes skill/prompt experiments.
It never self-promotes changes into production.

## 13. Beyond current Chimera: proposed SOTA direction

The existing CHIMERA PRD has the right thesis—heterogeneous computation and
multiple timescale loops—but is too broad to implement safely as one meta-
harness. A stronger next step is **Chimera Evidence Search**, a constrained
portfolio strategy inside the existing runtime rather than a parallel runtime.

### Core idea

```text
Shared durable blackboard (typed claims + evidence digests)
        |
        +--> deterministic retrieval/graph analysis
        +--> cheap hypothesis workers
        +--> symbolic/static-analysis solvers
        +--> one or more patch candidates in isolated branches
        +--> adversarial verification tournament
        |
        v
Evidence-weighted selector -> existing AdmissionGate -> existing Runtime result
```

### Why this is better than an unconstrained swarm

- one authority path and one durable event model;
- all candidate effects remain kernel-mediated;
- candidates are isolated and content-addressed;
- settled effects are not replayed;
- roles communicate through typed claims, not unbounded chat;
- retrieval, generation and verification budgets are independently measurable;
- failed branches become reusable trajectory evidence;
- the existing facade, ports, resume and admission machinery remain canonical.

### Minimal primitives to add

- `Hypothesis`: claim, confidence calibration, supporting/contradicting evidence;
- `CandidatePatch`: base digest, diff digest, affected surface and provenance;
- `Experiment`: deterministic command/test/fuzzer with expected information gain;
- `BranchOutcome`: candidate-specific receipts, verification and cost;
- `SelectionVerdict`: rubric-bound comparison with dissent/counterexample fields;
- `CapabilityProfile`: empirical success/cost distribution per model and task
  class, never self-reported model confidence.

### Search policy

Use one deterministic baseline candidate first. Branch only when evidence shows
uncertainty or repeated failure. Allocate additional test-time compute according
to expected value of information. Stop when one candidate closes all required
claims or the global budget cannot fund the next discriminating experiment.

### Promotion protocol

1. define benchmark and baseline digests;
2. run current V3 control;
3. run one Chimera component ablation at a time;
4. replay all provider calls through LAM;
5. compare clean completion, retrieval recall, regression escape, cost and time;
6. require improvement on held-out tasks and no trust-boundary regression;
7. promote the strategy/plugin, not a second kernel or app-owned loop.

## 14. Concrete future benchmark program

Create immutable benchmark families rather than isolated demos:

1. **SurfaceClosure-50**: public-interface changes with hidden callers/importers.
2. **LongContext-25**: 1–10M-token repositories, sparse signals and decoys.
3. **Concurrency-30**: races, idempotency, leases, atomic quotas and retries.
4. **Migration-20**: rolling compatibility, rollback and partial failure.
5. **Resume-20**: crash injection at every effect boundary with exactly-once
   assertions.
6. **Security-20**: path/symlink escapes, prompt injection in repository files,
   secret exfiltration attempts and malicious tests.
7. **Polyglot-25**: cross-language protocol/schema and generated-code changes.
8. **Scientific-20**: numerical stability, reproducibility and property oracles.

Every challenge must have a frozen reset manifest, red baseline, public smoke
test, hidden oracle, mutation check and content digest. Report pass@1 only after
clean admission; additionally report oracle-only success to diagnose gates.

## 15. Definition of done for the next qualification

- full suite green with provider credentials unavailable to tests;
- boundaries, TCB, domain blindness, isolation, secrets and duplication green;
- global budget ledger proves ceilings under concurrent runners;
- all five SOTA-context cases executed or explicitly excluded before scoring;
- cassettes replay with network blocked and canonical parity;
- no absolute user paths or secrets in artifacts;
- one fresh-process resume test proves no duplicate settled effects;
- scorecard is immutable, digest-bound and generated from raw evidence;
- V3 control compared against any Forge/Chimera proposal on identical fixtures;
- no V4 naming until a material architecture delta wins the controlled comparison.

## 16. Final recommendations

1. Stabilize and qualify V3 before multiplying presets.
2. Make Forge a composable strategy or clearly label it experimental.
3. Build the global budget ledger before any further paid batch.
4. Finish the two unexecuted SOTA cases.
5. Repair global suite contamination and artifact path hygiene.
6. Adopt immutable benchmark artifact schema v2.
7. Implement Chimera incrementally as evidence-search plugins on the shared
   runtime, with ablations and held-out promotion gates.
8. Optimize for **truthful clean completion per dollar**, not raw oracle pass or
   number of agents.
