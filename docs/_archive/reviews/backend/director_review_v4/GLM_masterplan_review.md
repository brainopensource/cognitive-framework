---
id: glm-masterplan-backend-review
class: review
authority: non-authorizing
canonical_for: []
status: advisory
owner: staff-engineering-review
version: "1.0.0"
last_verified: 2026-08-28
audited_branch: feat_higgs_M4_M8
audited_head: 6e7d172
scope: backend-only (vanguard/packages, packs/, benchmarks/, tools/, test/)
subordinate_to:
  - VISION.md
  - docs/SPEC.md
  - docs/01_law/
  - accepted ADRs
  - docs/03_execution/sprint_active.md
---

# GLM Masterplan Review — Backend Architecture for Agentic Task Execution

> **One phrase:** the substrate (kernel, ledger, identity, evidence) is the right foundation and must not
> be touched; the fastest route to a SOTA agentic-coding framework is to (1) converge the duplicated
> agentic intelligence that currently lives outside the lattice (`tools/006_LLM_INT_MACHINE`) into
> packs/plugins/policies, (2) industrialize the coding harness around a staged localize→plan→edit→verify→repair
> loop with fail-to-pass/pass-to-pass oracles, and (3) turn `mhf.trajectory/2` + `D_H/D_R/D_X` identity into
> a first-class **capability-ablation matrix** so every harness feature and combination is measured, tracked,
> and promoted only on held-out lift — all without one new line of kernel semantics.

**Audience:** Project Owner, Tech Lead, Lane A/B. **Surface:** Python backend only. The TypeScript
CLI/Studio (`vanguard/clients/`) is explicitly out of scope.

## Table of contents

1. [Executive verdict](#1-executive-verdict)
2. [Review method and evidence base](#2-review-method-and-evidence-base)
3. [As-built state of the backend](#3-as-built-state-of-the-backend)
4. [Gap analysis: framework vs. agentic-task requirements](#4-gap-analysis)
5. [SWE-Bench strategy: a measured, modular coding harness](#5-swe-bench-strategy)
6. [Architecture improvements (SOTA techniques, mapped to law)](#6-architecture-improvements)
7. [Refactoring plan: modularity, DRY, decomposition](#7-refactoring-plan)
8. [Workflows and pseudocode](#8-workflows-and-pseudocode)
9. [Development guidelines (additive to AGENTS.md)](#9-development-guidelines)
10. [Milestone alignment and execution order](#10-milestone-alignment)
11. [Risks, invariants to preserve, and anti-goals](#11-risks-and-anti-goals)
12. [Prioritized action register](#12-prioritized-action-register)
13. [Final conclusion](#13-final-conclusion)

## 1. Executive verdict

**Decision: Proceed with focused convergence — no rewrite, no kernel growth.**

AETHER's backend is architecturally ahead of most agentic frameworks: a domain-blind ~1,373-LOC kernel
enforcing S0–S12 capability dispatch, monotonic attenuation, typed four-dimensional budgets, an
event-sourced SQLite-WAL ledger where state is a fold over causal facts, JCS canonicalization with the
`D_H/D_R/D_X` identity separation, exterior signed evaluation, rootless Bubblewrap isolation, dual-read/
single-write schema evolution, and a falsifier culture enforced by linters. This is the expensive,
high-leverage part of a durable agent substrate. It must be frozen.

The decisive weakness is **not** the foundation. It is a three-way divergence:

| Divergence | Evidence | Consequence |
|---|---|---|
| **A second agentic engine exists outside the lattice** | `tools/006_LLM_INT_MACHINE` (`engine.py`) implements its own turn loop with SBFL fault localization, speculative MCTS search, mutation-verified patches, subagent orchestration, hierarchical model routing, and KPI telemetry — none of it mediated by S0–S12, none of it on the ledger | Techniques that should differentiate AETHER's coding harness are unverifiable, unattributable, and un-reusable by any other pack. They cannot be ablated, promoted, or audited |
| **The coding harness is thin relative to SWE-Bench demands** | `packs/code-default` ships a single planner, one `ast_patch` toolkit, a `terminal_runner`, and a heuristic context path; `tools/runners/run_swe_challenge.py` evaluates oracles by `subprocess` outside the evidence envelope | The product path cannot express the staged, budget-aware, verification-driven loops that SOTA coding agents use to score |
| **Runtime is accreting rather than decomposing** | `runtime/` is 20,764 LOC (~47% of the package tree); `session.py` alone is 1,363 LOC; `openrouter.py` is 870 LOC; archived reviews already flagged >1,000-line extractions as required-on-touch | The composition root is becoming the new monolith the lattice was designed to prevent |

The correct response is a **convergence program**, not new architecture:

1. **Converge LIM into the framework** as deterministic, digest-pinned, capability-mediated
   packs/plugins/policies (localizer, speculative search, mutation verifier, router) — each one an
   exterior component behind an existing SPI, each one falsifiable, each one ablatable.
2. **Industrialize the coding harness** with a staged verification loop and SWE-Bench-grade oracles
   (fail-to-pass + pass-to-pass), executed through `Runtime.execute_harness` so every turn is on the
   ledger and every candidate composition carries `D_H`.
3. **Build the capability-ablation matrix** on top of the existing M-6.5 paired-study machinery
   (McNemar exact, Holm–Bonferroni, paired bootstrap CI, `assert_comparable`) generalized from one
   binary treatment axis to a feature matrix over recorded trajectories.
4. **Decompose `runtime/`** with behavior-preserving extraction commits before adding new capability.

**Confidence: 0.87 (high).** Basis: direct code reads of the agency/context/topology/memory surfaces
at HEAD `6e7d172`, LOC accounting, and cross-reference of three archived backend reviews against the
current board. Where a claim is historical rather than re-verified at HEAD, this report says so.

### Bottom-line questions

| Question | Answer |
|---|---|
| Is the foundation worth preserving? | **Yes — freeze it.** Kernel, ledger, identity, evidence planes are correct and falsified |
| Should LIM's techniques be used? | **Yes — but only after conversion** into packs/plugins/policies inside the lattice; the parallel engine itself must be retired |
| Can this framework become a SOTA coding harness? | **Yes**, because the hard parts (attribution, budgets, recovery, evaluation) are already built; what's missing is harness technique, which is additive |
| What is the single biggest leverage item? | The SWE-Bench staged loop + ablation matrix: it converts existing substrate strength into measured, promotable capability |
| Does any proposal require kernel change? | **No.** Every proposal lands as pack, plugin, policy, adapter, or lab exterior. Anything that "needs" kernel change is a finding to escalate |

## 2. Review method and evidence base

Code-first, zero-trust-in-prose. Executed and read at HEAD `6e7d172` on `feat_higgs_M4_M8`.

### 2.1 Mechanical inventory (executed)

```text
LOC by subsystem (python, vanguard/packages/):
  domain    8,714        ports     1,494        kernel    1,747
  agency    2,590        runtime  20,764        adapters  9,662

Largest runtime files:
  session.py 1,363 | delegation.py 725 | artifacts.py 689 | root.py 638
  skill_evaluation.py 622 | checkpoints.py 539 | wiring.py 536 | compose.py 530

agency internals:
  episode/engine.py 757 | episode/state.py 262 | context/compiler.py 337
  context/compaction.py 256 | context/layers.py 246

adapters/models:
  openrouter.py 870 | invocation.py 584 | stochastic.py 259 | cassette.py 190
  ollama.py 175 | routing.py 132 | fake.py 38

Exterior agentic engine (outside lattice):
  tools/006_LLM_INT_MACHINE/{engine, mcts_search, fault_localizer, mutation_verifier,
  subagent_orchestrator, hierarchical_router, context_engine, telemetry_kpi, catalog}

Benchmark surfaces (three, overlapping):
  benchmarks/{swe_bench, greenfield, datalog_engine} + run.py/bench.py/diff.py/build.py
  tools/002_LLM_API_MOCK (synthetic corpus) + tools/005_SWE_VERIFIED_REPO
  tools/runners/run_swe_challenge.py (subprocess-based runner)

Domain packs: code-default, code-explain, formal-sat, formal-graph-coloring
```

### 2.2 Code surfaces read in depth

- `agency/episode/engine.py` — terminal-failure mapping, diagnostics extraction, spawn recursion,
  budget conservation.
- `agency/context/compiler.py` + `compaction.py` + `layers.py` — L1–L5 prefix stability, compaction
  registry, `StructuredConsolidateStrategy`.
- `runtime/topology.py`, `runtime/scheduler.py` — `mhf.topology/1` authority-rejecting validation,
  sequential lowering.
- `runtime/memory.py` — M-8 category contracts, authorization-before-ranking, `InMemoryMemoryPort`.
- `runtime/root.py`, `compose.py`, `delegation.py`, `skill_evaluation.py`, `checkpoints.py` —
  composition chain and evidence plumbing (structure-level read).
- `packs/code-default/` — manifest, plugins (`fs`, `ast-patch`, `repo-map`, `terminal`, `planner`),
  `system-prompt.txt`, task sets.
- `benchmarks/README.md`, `tools/runners/run_swe_challenge.py`, `tools/006_LLM_INT_MACHINE/engine.py`.

### 2.3 Classification vocabulary

- **Implemented:** production path exists and is exercised by focused tests at HEAD.
- **Partial:** useful code exists but a public integration, durability, or verification property is absent.
- **Divergent:** a capability is implemented twice, in two different authority regimes.
- **Missing:** no production implementation.
- **Historical (not re-verified):** claim from archived reviews or the board; current status must be
  re-derived before acting on it.

### 2.4 Honest limitations of this review

- The full Python suite was not re-run to completion inside the review window (discovery exceeds the
  execution budget); red/green status claims cite the board and archived audits and are marked
  **historical (not re-verified)**.
- The depth of `session.py`, `delegation.py`, and `openrouter.py` reads was structural, not line-by-line.
- SWE-Bench (the official benchmark) is not integrated; the repo has its own hermetic SWE suite
  (`benchmarks/swe_bench/`). All SWE-Bench-specific recommendations below are designs for integration,
  not descriptions of existing code.

## 3. As-built state of the backend

### 3.1 Subsystem assessment

| Subsystem | Status | Assessment |
|---|---|---|
| `domain/` (8.7k LOC) | Implemented | Pure stdlib; wire contracts, ledger reducers, JCS, selector algebra, evidence models. Correct to keep frozen |
| `ports/` (1.5k LOC) | Implemented | Hexagonal protocols incl. 5 SPIs. The extension surface for everything in this report |
| `kernel/` (1,373/1,438 logical) | Implemented, frozen | S0–S12, attenuation, budgets, grants, fail-closed policy, provenance DAG. **65 LOC headroom — treat as scarce; do not spend it on harness features** |
| `agency/` (2.6k LOC) | Implemented | `EpisodeEngine` (sequential, budget-enforcing, spawn-recursing), L1–L5 context compiler, three compaction strategies. Sound reference protocol; see §6.2 for compaction weaknesses |
| `runtime/` (20.8k LOC) | Implemented, **accreting** | Composition chain `CanonicalManifest → FrozenComposition → ActivationPlan → RunPlan → EpisodeEngine` works; delegation, checkpoints, skill evaluation, memory contracts, topology lowering all present. Monolith risk in `session.py`/`compose.py` |
| `adapters/` (9.7k LOC) | Implemented | OpenRouter/Ollama/Cassette/Fake/LAM models, evaluator daemon + signed RPC, bwrap sandbox, SQLite WAL stores, stochastic stall instrument. `openrouter.py` needs decomposition |
| `packs/code-default` | Partial as harness | Single planner, one patch toolkit, terminal runner, repo map, evaluation gate. Lacks localization, verification-driven repair, test selection, and multi-role topologies |
| `packs/code-explain` | Exists | The "explain code/docs" domain exists as Pack #2 surface — good generality signal; under-documented relative to code-default |
| `benchmarks/` | Implemented (hermetic) | Three suites: SWE bug-fixing (bwrap + pytest + regression), greenfield synthesis, datalog engine (delegation under budgets). Strong foundation; fragmented execution story |
| `tools/006_LLM_INT_MACHINE` | **Divergent** | Full second agentic engine with SOTA techniques, outside the lattice, unmediated, unlegered. The central convergence target |
| `test/` (17 categories) | Implemented | Kernel/contracts/agency/runtime/security/trust/falsifiers/packs/registry + property tests. Archived audits showed historical reds; current board shows WP states PACKAGE_READY — re-derive before acting |

### 3.2 What is genuinely strong (do not rebuild)

1. **Identity discipline.** `D_H` (composition), `D_R` (runtime/model/evaluator), `D_X` (dataset/protocol)
   are separated and enforced. This is precisely what makes feature-ablation science possible — most
   frameworks cannot even answer "which configuration produced this trajectory."
2. **Prefix-stable context compiler.** L1–L4 frozen at composition, L5 for mid-run additions, breakpoint
   ceilings, brief exempt from compaction. This is KV-cache-aware prompt architecture done correctly.
3. **Budget conservation.** `Σ child actualCost ≤ parent reservation` enforced by one accountant (kernel
   settlement), making overspend unrepresentable rather than merely checked.
4. **Evidence separation.** Generator ≠ evaluator ≠ promoter; unsigned/forged verdicts fail closed;
   `undeterminable` never satisfies a predicate.
5. **Falsifier culture.** Every module ships a named RF-* attack; linters enforce boundaries, TCB,
   blindness, isolation, secrets, duplication.
6. **Recovery.** Fresh-process WAL continuation, `RunRecovered` before trajectory completion,
   at-least-once physical attempts with exactly-once settlement per command identity.

### 3.3 Verified weaknesses and opportunities (at HEAD)

| # | Finding | Location | Severity | Class |
|---|---|---|---|---|
| W-1 | Second agentic engine outside the lattice (SBFL, MCTS, mutation verifier, router, subagent coordinator, KPI telemetry) — unmediated by S0–S12, no ledger events, no `D_H`, no falsifiers | `tools/006_LLM_INT_MACHINE/engine.py` | **HIGH** | Divergent |
| W-2 | `StructuredConsolidateStrategy` detects "dead ends" by substring scan (`"failed" in text`, `"error" in text`, `"decision" in text`) over block text | `agency/context/compaction.py` | MEDIUM | Brittle heuristic |
| W-3 | `resolve_compaction_strategy` silently falls back to `recency-window` on unknown policy kind — contradicts the fail-closed culture applied everywhere else | `agency/context/compaction.py` | MEDIUM | Fail-open |
| W-4 | Memory recall in the reference double is O(n) substring containment with sort-by-record-id "ranking" — acceptable as a hermetic double, but the durable adapter must ship a real deterministic ranker or the M-8 retrieval lift claim is hollow | `runtime/memory.py`, `adapters/stores/` | MEDIUM | Under-powered retrieval |
| W-5 | `session.py` at 1,363 LOC and `openrouter.py` at 870 LOC violate the repo's own "extract >1,000-line files when touched" standard | `runtime/session.py`, `adapters/models/openrouter.py` | MEDIUM | Monolith drift |
| W-6 | Three overlapping benchmark/task surfaces (`benchmarks/`, `tools/002_LLM_API_MOCK`, `tools/005_SWE_VERIFIED_REPO`) with different task contracts and runners; `run_swe_challenge.py` evaluates oracles via raw `subprocess` outside the evidence envelope | repo-wide | MEDIUM | Fragmentation |
| W-7 | Topology lowering produces readiness templates, but role operations do not execute as real M-6 child operations in the public run path (per archived review; mechanism partially landed per board) | `runtime/topology.py`, `runtime/compose.py` | MEDIUM | Historical (partially re-verified) |
| W-8 | No test-selection or dependency-graph awareness in the coding pack: every verification runs the full suite via `terminal_runner` | `packs/code-default/toolkits/terminal_runner.py` | MEDIUM | Performance |
| W-9 | `code-explain` pack exists but the "research/explain docs" workflow has no dedicated trajectory/retrieval story comparable to the coding harness | `packs/code-explain/` | LOW | Product gap |
| W-10 | The M-6.5 paired-study machinery (McNemar exact, Holm, bootstrap CI, comparability gate) is the best experiment instrument in the repo but is scoped to one binary treatment axis | `runtime/paired_evaluation.py`, `lab/` | LOW→HIGH | Under-leveraged |

### 3.4 Historical findings from archived reviews (status to re-derive, not assume)

The three archived backend reviews (v1 forensic, v2B delivery, v3 guidelines) established defects that
the board indicates have since been repaired or packaged: the 17 manifest-loader schema-path errors,
the memory-fake fail-open disjunct (its removal is documented in `runtime/memory.py`'s docstring and
covered by `test/security/test_m8_memory_fake_parity.py`), the `M-5A-BASE-v2` contamination (superseded
by ADR-0102's successor-control protocol), and M-6 evidence (now `passed` on the board via
`M-6-canonical-recursion-order10`). Treat all archived claims as **historical evidence requiring
re-derivation at HEAD**, per the reviews' own rule.

## 4. Gap analysis

This section evaluates the backend against the three target agentic workloads: (a) an agentic coding
harness CLI, (b) research/explain code-and-docs, (c) general task solving through composable packs.

### 4.1 Capability matrix: what SOTA coding agents need vs. what exists

| Capability needed for SWE-Bench-grade coding agents | Substrate support | Harness support | Verdict |
|---|---|---|---|
| Turn loop with tool mediation and budget caps | `EpisodeEngine` + S0–S12 + typed budgets | `packs/code-default` | **Strong** |
| Verifiable, attributable trajectory (`mhf.trajectory/2`) | Ledger + emitter + checkpoints | `runtime/trajectory.py` | **Strong** |
| Recovery from crash mid-task (fresh-process continuation) | WAL + cold fold + `RunRecovered` | product path | **Strong** |
| Fail-to-pass / pass-to-pass test oracles | Exterior evaluator + signed verdicts | `benchmarks/swe_bench` (hermetic only); official SWE-Bench absent | **Partial** |
| Fault localization (which files/tests to attend to) | — | LIM's `fault_localizer.py` only, outside lattice | **Divergent / Missing** |
| Robust patch formats with syntax validation and self-repair | `ast_patch` toolkit | single format; no LLM-proposal-repair loop | **Partial** |
| Test selection / dependency-graph awareness | `code_graph.py` exists in LIM only | full-suite runs only | **Divergent / Missing** |
| Multi-role topologies (planner/executor/reviewer) | `mhf.topology/1` parse/lower + M-6 spawn | single `single-planner` plugin in product path | **Partial** |
| Speculative search over candidate patches (MCTS/tree) | — (I-11 sequential) | LIM `mcts_search.py` only, outside lattice | **Divergent / Missing** |
| Mutation-verified patch acceptance | — | LIM `mutation_verifier.py` only | **Divergent / Missing** |
| Cost-aware model routing per stage | `routing.py` + execution profiles | LIM `hierarchical_router.py` more advanced, outside lattice | **Partial / Divergent** |
| Retrieval of similar past episodes / skills | M-8 memory + skill library + CAS promotion | substring recall in reference; durable adapter landing | **Partial** |
| A/B measurement of harness features | M-6.5 paired study machinery | scoped to one binary axis | **Partial** |
| Sandbox test execution with captured stdout/exit | bwrap UID 10001 + `terminal_runner` | yes | **Strong** |
| Container-per-instance environment parity (SWE-Bench official) | bwrap/OCI images exist | per-instance env setup not productized | **Partial** |

**Reading of the matrix:** the substrate support column is mostly **Strong** — this is unusual and
valuable. The gaps are almost all in the harness layer, and — critically — the missing techniques
already exist in the repository in the wrong authority regime (LIM). The report's central thesis
follows: **converge, don't reinvent.**

### 4.2 Why LIM convergence matters more than it appears

`tools/006_LLM_INT_MACHINE` is simultaneously the repository's best source of harness technique and
its clearest architectural violation:

1. **It is a second engine.** `engine.py` coordinates its own context engine, tool workspace, LLM
   client, and subagent coordinator — precisely the "second runtime" the SPEC refuses. Its techniques
   cannot pass through S0–S12, so its effects are unattributable: no receipt, no budget settlement,
   no recovery, no `D_H`.
2. **It is unlegered.** Its `catalog.py` run receipts are a parallel evidence format. Two evidence
   regimes in one repository is exactly the "dual truth" failure mode the v1 forensic review flagged
   for composition and that M-3C spent a milestone eliminating.
3. **It is unreusable by packs.** A formal-pack or explain-pack composition cannot consume its
   localizer or router, because those are wired to LIM's private interfaces rather than to
   `ports/` SPIs.
4. **But its algorithms are good.** SBFL-based fault localization, speculative MCTS over patch
   candidates, mutation-verified acceptance, and hierarchical cost-aware routing are exactly the
   techniques that separate ~20% SWE-Bench agents from ~40%+ ones. Discarding them would be waste;
   adopting them as-is would be corruption.

**Disposition: adopt the algorithms, retire the engine.** Each LIM capability becomes a deterministic,
digest-pinned, capability-mediated component behind an existing SPI (§6.1 maps each one).

### 4.3 Framework-as-product gaps (for "framework for agentic tools")

For AETHER to serve as the substrate for *other* agentic CLI tools (coding harness, research
assistant, doc explainer), the missing product primitives are:

| Primitive | Today | Needed |
|---|---|---|
| Pack SDK contract | Implicit across `packs/*/load.py` + manifests | One frozen, generated, versioned Pack SDK: `PackDefinition → Manifest → Toolkits → Oracles → Policy`, with golden vectors and a conformance suite every pack must pass (the M-5 parity idea generalized) |
| Task-set contract | `runtime/task_sets.py` digest-pinned resolution exists; three competing surfaces | One canonical task-set schema (`mhf.taskset/N`) with fail-to-pass/pass-to-pass oracle fields, environment pins, and `D_X` binding — used by hermetic suite, SWE-Bench adapter, and synthetic corpus alike |
| Ablation/experiment service | `paired_evaluation.py` + `lab/m65_study.py` (one axis) | Feature-matrix experiments over recorded trajectories with the same comparability gates (§5.4) |
| Retrieval primitive | M-8 memory ports + substring reference | Deterministic BM25-style ranker + optional embedding adapter behind `KnowledgePort`, provenance-preserving, digest-pinned corpora |
| Workflow templates | `mhf.topology/1` + LIM templates outside lattice | Digest-pinned topology templates for the three target workflows (§6.5) shipped as versioned data |
| Local CLI embedding | `runtime/cli.py` (386 LOC) + TS `vg` | The Python runtime CLI must expose: run/resume/status/diff/ablate — the four verbs every agentic tool needs |

## 5. SWE-Bench strategy

Goal: improve SWE-Bench-class resolution rate by running the harness *with* the framework's own
substrate, in a modular and efficient way, while tracking every feature, combination, and event.

### 5.1 Reference architecture: the staged coding loop

SOTA coding agents (SWE-agent, Agentless-style pipelines, repair-with-localization systems) converge
on a staged loop. The AETHER-native version maps every stage onto existing substrate mechanisms:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  Stage 0  INGEST      task digest → D_X; env pin; repo checkout; oracle pin │
│  Stage 1  LOCALIZE    dependency graph + SBFL/F2P-mapping → focus set       │
│  Stage 2  PLAN        planner role: hypothesis + edit plan (L5 notes)       │
│  Stage 3  EDIT        ast_patch / search-replace with syntax pre-validation │
│  Stage 4  VERIFY      test selection → bwrap run → F2P ∪ P2P evaluation     │
│  Stage 5  REPAIR      failure → localized regression feedback → re-edit     │
│           (bounded by repair budget; each attempt is a receipted effect)    │
│  Stage 6  SETTLE      exterior evaluator signs pass/fail; trajectory /2     │
└─────────────────────────────────────────────────────────────────────────────┘
```

Key design points:

- **Every stage is ordinary mediated execution.** Stages are not privileged; the planner is a role,
  the localizer is a deterministic pack toolkit, verification is the exterior oracle, settlement is
  the signed evaluator. The turn loop (I-11) stays unary; stages are *phases within one episode*,
  or — where fan-out is justified (§6.5) — M-6 child spawn, never a second engine.
- **The oracle is two-sided.** SWE-Bench correctness = fail-to-pass tests now pass AND pass-to-pass
  tests still pass. The current `evaluation-gate` plugin must carry both sets, and the exterior
  evaluator must sign the *pair*, not a single boolean.
- **Repair is budgeted.** Each Stage-5 iteration consumes the ordinary typed budget (`tokens`,
  `millis`, `usd_micros`, `bytes`); exhaustion terminates the episode honestly as
  `BUDGET_EXHAUSTED` — which the ledger already models.
- **Localization is deterministic-first.** Deterministic SBFL/coverage data (from Stage-4 runs of the
  baseline suite) seeds Stage 1 before any model call. This is both cheaper and more attributable
  than asking the model to guess files.

### 5.2 Task-set and oracle contract (`mhf.taskset/1`)

Unify the three benchmark surfaces on one schema (Lane B work, generated readers per A-4):

```jsonc
{
  "api": "mhf.taskset/1",
  "taskId": "swe-astropy-12907",
  "dataset": {"name": "swe-bench-verified", "split": "dev", "pin": "sha256:..."},
  "environment": {"image": "sweb.eval.x86_64...", "pin": "sha256:..."},
  "repo": {"commit": "sha256:...", "basePatch": "artifact:..."},
  "oracles": {
    "failToPass":  ["tests/test_regression.py::test_case"],
    "passToPass":  ["tests/test_core.py::test_other"],
    "runner": {"cmd": "python -m pytest -x -q {selected}", "timeoutMs": 900000}
  },
  "hints": {"localization": "artifact:coverage-map/...", "optional": true}
}
```

Rules: the task digest and oracle pin enter `D_X`; the environment pin enters `D_R`; the `hints`
artifact is optional and its absence is never a failure (M-07 discipline: absent ≠ zero).
Hermetic CI runs the identical contract against `Cassette`/`Fake` models; live runs are explicitly
selected. This is what makes the same harness hermetic by default and attributable when live — the
existing hermetic-testing law, applied to benchmarking.

### 5.3 The ablation matrix: tracking features, combinations, and events

The unique asset here is that every run already carries `D_H/D_R/D_X` and a full trajectory. The
proposal: a **capability ledger** — a derived projection (rebuildable, never causal truth) that maps
feature sets to outcomes.

```text
Feature vector F(run) ← execution-profile + composition manifest:
  localization   ∈ {none, sbfl, f2p-map, both}
  patchFormat    ∈ {ast, search-replace, unified-diff}
  verify         ∈ {full-suite, selected, adaptive}
  repairBudget   ∈ {0, 2, 4}
  search         ∈ {greedy, mcts-bounded}
  router         ∈ {static-route, hierarchical}
  memory         ∈ {off, project-recall, skill-index}
```

For each cell `(feature ∈ F) × (task ∈ taskset)` the projection records: resolved, tokens, usd_micros,
turns, repair attempts, outcome (`pass|fail|budget|error`), and the trajectory digest. Analysis
reuses the M-6.5 machinery:

```text
single-feature lift:    McNemar exact over paired runs (feature on/off, same tasks, same seeds)
combination search:     Holm–Bonferroni over the tested family; paired bootstrap CI on resolution rate
comparability gate:     assert_comparable requires arms to differ ONLY on declared feature axes
event-level drill-down: any cell's claim is auditable by replaying its trajectory digest
```

This converts "we think the MCTS helps" into a promotable, signed, held-out claim — feeding the
existing M-8 promotion path (generator ≠ evaluator ≠ promoter) rather than creating a new one.
Nothing here touches the kernel: the matrix is a projection over the ledger plus an exterior
experiment driver in `lab/`.

### 5.4 Efficiency levers (cost/latency, measured not assumed)

| Lever | Mechanism | Expected effect | Guard |
|---|---|---|---|
| Test selection | Dependency-graph + coverage mapping restricts Stage-4 runs to affected tests during repair iterations | Big `millis`/`bytes` savings per repair loop | Final settlement always runs the full oracle; selection is an optimization inside a stage, never the verdict |
| Prefix stability | Already built (L1–L5); enforce skill-index ceiling discipline | Cache-hit retention → token cost cut | `CacheBreakpointCeilingExceeded` remains fatal |
| Early exit | If F2P passes and P2P intact after Stage 3, skip speculative search | Fewer model calls on easy instances | Exterior evaluator still signs; no self-graded exit |
| Bounded search | MCTS with node budget derived from remaining `usd_micros` reservation | Converts unlimited exploration into budgeted search | Search tree is telemetry, never ledger truth; the chosen path re-executes as ordinary effects |
| Model routing | Cheap model for localization/summarization, strong model for edit/repair stages | Cost cut at equal resolution | Routing policy is declared, digest-pinned composition data entering `D_R` |

### 5.5 SWE-Bench integration path (official benchmark)

1. `tools/` gains an **adapter** (not a runtime): converts official SWE-Bench instance JSON to
   `mhf.taskset/1` bundles; container images built once, pinned by digest.
2. Runs go through `Runtime.execute_harness` with `packs/code-default` (or a dedicated
   `packs/swe-agent` derived from it) so every attempt is on the ledger with `D_X` = instance digest.
3. Results export: `tools/export_coding_session.py` extended to emit the official submission format,
   derived from the ledger — never from side-channel logs. If the ledger cannot produce the
   submission artifact, that is a capture gap to fix in capture, not a reason to bypass the ledger.
4. Score tracking: the ablation matrix projection doubles as the score tracker — per-instance,
   per-config, with signed evaluation receipts.

## 6. Architecture improvements

Each improvement is stated with: the SOTA technique, where it lands in the lattice, what law it must
respect, and its falsifier. None requires kernel change.

### 6.1 LIM capability convergence map (adopts algorithms, retires the engine)

| LIM component | Technique | New home in lattice | Authority regime after convergence | Falsifier |
|---|---|---|---|---|
| `fault_localizer.py` (SBFL) | Spectrum-based fault localization from test coverage | `packs/code-default/toolkits/localizer.py` — deterministic toolkit; output = coverage artifact | Ordinary mediated effect; artifact is content-addressed; localization is advisory input to context, never authority | Wrong-localization attack: mutated coverage map detectable by digest; missing map ⇒ `absent`, never "all files" |
| `mcts_search.py` | Speculative MCTS over candidate patches | `packs/code-default/planners/mcts_planner.py` — a *policy/plugin* proposing candidate edit plans; chosen candidate re-executes through the ordinary path | Proposer only (like the M-6.5 controller): no grants, no ledger writes, no bypass; node budget derived from reservation | Budget-bypass / nondeterministic-directive attacks (reuse the 5 `guarded_consult` guards) |
| `mutation_verifier.py` | Mutation testing to validate a patch is not vacuous | `packs/code-default/oracles/mutation_gate.py` — extends the evaluation gate; exterior evaluator still signs | Evaluation-side component inside the pack; signed verdict includes mutation evidence | A patch that deletes tests must fail the gate; forged mutation report fails digest check |
| `hierarchical_router.py` | Cost-aware model routing per stage | `adapters/models/routing.py` extension: profile-declared stage→model map | Declared composition data entering `D_R`; both models' costs settle through the same budget accountant | Undeclared route at runtime ⇒ `D_R` mismatch ⇒ run non-evidentiary |
| `subagent_orchestrator.py` | Fan-out subagents | M-6 `agent.spawn` with topology roles — the only sanctioned delegation | Attenuated child budgets, conserved; kill-tree semantics already built | Conservation property test (Σ child ≤ root) already exists |
| `code_graph.py` | Repo dependency graph | `packs/code-default/toolkits/code_graph.py`; also feeds test selection and repo-map ranking | Deterministic toolkit output, digest-pinned | Rebuild determinism under pinned repo digest |
| `context_engine.py` | Token ceiling engine | Superseded by existing `agency/context/compiler.py` (already superior: prefix stability) | — | — |
| `telemetry_kpi.py`, `catalog.py` | KPI dashboards, run catalog | The ablation-matrix projection (§5.3) + `runtime/telemetry.py` | Projection over ledger; never causal | Projection rebuild determinism |

Retirement rule: after each conversion lands with its falsifier green, the LIM module is marked
deprecated and its import surface is deleted once `check_duplication.py --enforce` confirms no
production consumer remains. LIM may survive as a *lab driver* consuming the framework — never as a
competing execution path.

### 6.2 Context engine hardening (small, high-value fixes)

1. **Fail closed on unknown compaction policy (W-3).** `resolve_compaction_strategy` returning
   `recency-window` on an unrecognized `context_policy` kind is a silent misconfiguration. Change to
   raise a typed `UnknownCompactionPolicyError` at composition time (composition-time validation,
   not a `/1` wire change).
2. **Typed dead-end recording (W-2).** Replace substring dead-end detection in
   `StructuredConsolidateStrategy` with typed receipts: effect outcomes are already on the ledger, so
   the consolidator should consume structured failure records (denial receipts, failed verification
   verdicts) instead of pattern-matching English words in block text:

```python
def consolidate(dialogue, failure_records):
    # failure_records: ledger-derived (kind, descriptor_digest, outcome) for this episode
    dead_ends = tuple(sorted({f.descriptor_digest for f in failure_records
                              if f.outcome in FAILED_OUTCOMES}))
    summary = StructuredRecord(dead_ends=dead_ends,
                               decisions=from_receipts(decision_receipts))
    return render(summary)   # deterministic; digest-pinned; no text scanning
```

3. **Repo-map ranking (W-8 precursor).** `packs/code-default/toolkits/repo_map.py` should rank files
   by a deterministic blend: path proximity to the localized focus set (§6.1) + recency of edits +
   graph centrality from `code_graph`. Ranking is pure and digest-pinned so the L3 environment map
   stays prefix-stable — the ranking input changes only at stage boundaries, never mid-run.
4. **Compaction quality metric.** Add a hermetic benchmark: replay recorded long trajectories, apply
   each strategy, and measure (a) re-exploration rate (does the agent re-attempt a dead end?) and
   (b) answer-fidelity of the summary. Ship numbers with the strategy; do not promote a strategy
   without a paired study (M-6.5 discipline applies to compaction too).

### 6.3 Retrieval upgrade for the M-8 stores

The durable memory adapters must ship a deterministic ranker so "recall" means more than substring:

```text
Ranker contract (deterministic, provenance-preserving):
  score(record, query) = Σ term∈query_terms  idf(term) · tf(record, term)   # BM25-family, pure
  tie-break: record_id ascending  (stable, auditable)
  provenance: RetrievalProvenance(query_digest, policy="bm25/1", selected, dropped, ...)
  optional embedding adapter: behind the same KnowledgePort, pinned model digest entering D_R;
    embeddings are derived data — rebuildable, never causal truth
```

Falsifiers to add: `test_ranking_is_deterministic_under_record_permutation` and
`test_absent_corpus_reports_absent_not_empty` (existing cross-category isolation, revocation
fail-closed, and provenance round-trip tests stay strict).

### 6.4 Verification-stage detail (test selection, oracles, mutation gate)

```text
Test-selection toolkit (deterministic):
  inputs : code_graph artifact, changed-file set (git diff from workspace), historical coverage map
  output : selected_tests ⊆ oracle tests, plus an 'unselected' remainder with justification digest
  rule   : F2P tests are ALWAYS selected; P2P tests selected iff their transitive dependency set
           intersects changed files; unselected P2P still runs at final settlement
  guard  : selection changes what runs mid-loop, never what the signed verdict requires
```

The mutation gate (from LIM) applies only to F2P-successful patches: kill a sample of mutants of the
patch; if a mutant that removes the fix still passes, the patch is vacuous and Stage 5 re-enters
repair. Mutation sampling count is budget-derived and recorded as telemetry.

### 6.5 Workflow templates (versioned topology data, per the SPEC refusal)

Three digest-pinned `mhf.topology/1` templates ship as data, all lowered through the existing M-7
path and executed via M-6 spawn — no engine, no kernel branch:

```text
T1 code-repair        : planner → executor → reviewer(review) with artifact flow patch→oracle
T2 research-explain   : scout(fan-out read-only) → synthesizer(merges_into) → explainer
T3 doc-explain        : reader → summarizer → verifier(review) with citation artifact flows
```

`T2` is the framework answer to "research and explain code/docs": read-only child agents (scopes
attenuated to `fs.read` groups — the `safe_read_only_group` concept already in the scheduler),
merging into one synthesizer that produces a citation-backed explanation artifact whose claims are
digest-linked to source artifacts. This is a genuine SOTA differentiator: research agents whose
every citation is content-addressed and independently re-verifiable.

### 6.6 Patch-format robustness and self-repair (Stage 3 hardening)

The single highest-frequency failure mode in agentic coding is malformed edits. The `ast_patch`
toolkit should grow a proposal-validation/self-repair loop that does **not** spend a model call to
discover a syntax error:

```text
apply_patch(proposal):
  1. parse edit blocks; on parse error → typed BlockParseError with byte offsets
  2. locate anchors (exact → whitespace-normalized → fuzzy within localized file set)
  3. pre-apply AST parse of the RESULT file (ast.parse / tree-sitter equivalent)
  4. on syntax failure: one deterministic autofix attempt (unterminated bracket, bad indent)
  5. on persistent failure: return structured error payload to the episode (an ordinary
     denial-shaped feedback event) so the model's next proposal is repair-informed
```

Each step is pure/pack-level; the *application* of the patch is the ordinary mediated `patch.apply`
effect, so every accepted edit keeps its receipt. Add `patchFormat` to the ablation matrix (§5.3) —
`ast` vs `search-replace` vs `unified-diff` is one of the cheapest high-signal ablations available.

### 6.7 Concurrency posture (respect ADR-0099, extract the wins)

ADR-0099 records `SEQUENTIAL_CONFIRMED`; this review does not reopen it. But two bounded,
evidence-driven wins are admissible under its own terms:

1. **Read-only parallel fan-out in T2** (§6.5): multiple read-only scouts are concurrency *within*
   mediated spawn, each with its own attenuated reservation; results merge deterministically
   (sorted-by-digest). Measured against the sequential baseline in a paired study before becoming
   a default profile.
2. **Test-execution parallelism inside Stage 4**: pytest-level `-n` parallelism is a single mediated
   `proc.exec` effect — wall-clock optimization inside one effect, invisible to causal truth.
   Zero substrate risk; pure `millis` savings.

### 6.8 What NOT to adopt (SOTA-fashion discipline)

| Trendy technique | Verdict | Reason |
|---|---|---|
| Free-form "autonomous multi-agent swarms" | Reject | Violates I-11 + one-runtime refusals; mediated spawn + topologies already cover the justified cases |
| Unbounded tree search / self-play at inference | Defer | Only as budget-bounded proposer policy (§6.1) with a paired study; never as substrate |
| Continuous fine-tuning / RL from harness trajectories | Defer to M-10 research lane | Requires selection-bias controls the M-8 promotion path was built to enforce; see MEASUREMENT.md |
| Vector DB as a new truth plane | Reject as truth; allow as derived index | Caches/indexes remain derived and rebuildable (SPEC axiom); embeddings are data, not authority |
| "MemGPT-style" self-editing memory | Partially adopt | M-8 already separates write authorization from ranking; self-edited memory must still pass `MemoryAccess` authorization at use time — no new semantics needed |

## 7. Refactoring plan

Principle: **behavior-preserving extraction commits** (repo standard) before capability work that
touches the same files. Each extraction is its own commit with byte-identical behavior, verified by
the focused suites.

### 7.1 Decomposition targets

| Target | Current | Extraction plan | Guard |
|---|---|---|---|
| `runtime/session.py` (1,363 LOC) | Session lifecycle + effect admission + diagnostics + capture in one file | Split into `session/lifecycle.py`, `session/effects.py`, `session/capture.py`, `session/recovery.py` with `session/__init__` re-exports | No signature change; `test/runtime` green before/after; no ledger event change |
| `adapters/models/openrouter.py` (870 LOC) | Transport + pricing + retry + translation mixed | Split into `openrouter/transport.py`, `openrouter/pricing.py`, `openrouter/translate.py`; adapter keeps its public surface | Pricing vector source-of-truth unified (archived audit D-item; verify current status first) |
| `runtime/compose.py` (530 LOC) | Composition + task context + topology binding | Extract `composition/normalize.py` if the topology integration (WP-A3) expands it further | Only extract when touched — do not churn a green file speculatively |
| Three benchmark surfaces | `benchmarks/`, `tools/002`, `tools/005` | Freeze `mhf.taskset/1` (§5.2); migrate `benchmarks/` tasks first; deprecate the other two runners once parity receipts exist | Parity: same task digest resolves identically on old and new runner before deprecation |
| LIM modules | Outside lattice | §6.1 conversion map, one module per package | Each conversion lands with falsifier + paired measurement before LIM deprecation |

### 7.2 DRY violations to converge

1. **Two evidence regimes** — LIM `catalog.py` receipts vs `mhf.trajectory/2` + evidence envelopes.
   Converge on the ledger; delete the parallel catalog as a truth source (dashboard consumers read
   the projection).
2. **Two context engines** — LIM `context_engine.py` vs `agency/context/compiler.py`. Keep the
   compiler; port any missing idea (token accounting nuance) as a compaction strategy option.
3. **Two model clients** — LIM `llm_client.py` vs `adapters/models/*`. Keep adapters; routing
   technique moves to `routing.py`.
4. **Compaction registry aliasing** — `COMPACTION_REGISTRY` maps both `result_eviction` and
   `result-eviction` keys. One canonical form (kebab, matching `context-policy.json` usage) plus a
   deprecation warning path; not silent duplication forever.
5. **Pack scaffolding** — `packs/*/load.py`, plugin manifests, and oracles repeat structure. Extract
   a shared pack SDK helper in Lane B's contract set (not a new framework layer — a library used
   *by* packs, below the lattice seams).

### 7.3 Modularity rules going forward

- New agentic capability ⇒ first question: "which existing SPI or pack slot takes this?" Only if
  none does: propose a port addition (Lane B contract, additive, versioned).
- `runtime/` file budget: soft cap 600 LOC/file, hard review trigger at 1,000.
- `kernel/` budget: untouched; the 65 LOC headroom is reserved for authority semantics only.
- Packs may not import `runtime/` internals; they consume ports and declare toolkits/oracles/policies.
- Every new toolkit/oracle/planner ships: deterministic reference path, hermetic fixture, named
  falsifier, and an entry in the ablation-matrix feature list (so it is measurable by construction).

## 8. Workflows and pseudocode

### 8.1 The SWE-Bench episode (end-to-end, in framework vocabulary)

```python
def run_swe_task(task: TaskSetManifest, pack: HarnessPack) -> RunResult:
    # Stage 0 — INGEST (composition-time, before turn 1)
    ctx = TaskContext(
        dataset_pin=task.dataset.pin,          # → D_X
        env_pin=task.environment.pin,          # → D_R
        oracle_pin=digest_of(task.oracles),    # → D_X
    )
    plan = plan_run(pack.manifest, task_context=ctx)

    # Stage 1 — LOCALIZE (deterministic, pre-model where possible)
    coverage = pack.toolkits.localizer.run(    # mediated proc/fs effects; artifact stored
        baseline_tests=task.oracles.failToPass + task.oracles.passToPass)
    focus = pack.toolkits.code_graph.focus_set(changed_hint=None, coverage=coverage)

    # Stages 2–5 — the episode loop (I-11 sequential inside ONE episode)
    outcome = runtime.execute_harness(
        manifest_path=pack.manifest_path,
        task_context=ctx,
        context_hints={"focusSet": focus, "coverageArtifact": coverage.digest},
        repair_budget=RepairBudget(max_attempts=2),   # typed budget reservation per attempt
    )

    # Stage 6 — SETTLE (exterior, signed)
    verdict = evaluator_gateway.submit(           # exterior evaluator, Ed25519-signed
        oracle=task.oracles,
        workspace_diff=extract_diff(outcome),     # content-addressed artifact
        mutation_evidence=pack.oracles.mutation_gate.last_report,
    )
    return RunResult(outcome=outcome, verdict=verdict)  # trajectory /2 completes on ledger
```

### 8.2 The repair loop (inside Stage 5, still ordinary turns)

```text
while repair_attempts < budget and not verified:
    failure_feedback = pack.oracles.evaluation_gate.diff(   # deterministic
        expected = task.oracles, observed = last_run_report)
    emit Note(feedback = summarize(failure_feedback))       # L5 note; prefix untouched
    proposal = model.propose(context_with_dead_ends_marked)
    patch_result = pack.toolkits.ast_patch.apply(proposal)  # §6.6 self-repair inside
    if patch_result.applied:
        selected = pack.toolkits.test_selector.select(changed_files)  # §6.4
        report = terminal_runner.run(selected, sandbox=bwrap)         # mediated effect
        verified = report.f2p_all_pass and report.p2p_no_regress
    else:
        emit Note(feedback = patch_result.error)  # repair-informed next proposal
```

### 8.3 The research/explain workflow (T2 topology, citation-verbatim)

```text
scout_i (read-only child, fs.read-scoped, i ∈ 1..k):
    reads a repo/docs slice; emits Finding artifacts {claim_digest, source_artifact_digest,
    quote_span} — every claim carries its source content digest
synthesizer:
    consumes findings sorted by digest; produces Explanation artifact where each paragraph
    references finding digests (merges_into edges in mhf.topology/1)
explainer:
    renders final artifact; citations are digest URIs, independently dereferenceable
verifier (review relation):
    spot-checks a deterministic sample: re-reads source artifact, confirms quote_span containment
    — unsigned or unverifiable citation ⇒ verdict `undeterminable`, never "pass"
```

This reuses: M-6 spawn (attenuated budgets), M-7 lowering (role graph), M-8 retrieval (project
memory for prior explanations), CAS artifacts (claims are content-addressed), and the exterior
evaluator (verification). No new substrate semantics.

### 8.4 The ablation experiment workflow

```python
def ablate(feature_axis: str, taskset: TaskSetRef, seeds: Sequence[int]) -> AblationReport:
    # arms differ ONLY on the declared axis (M-18 comparability discipline, generalized)
    base_profile = load_profile("swe-base")                       # digest-pinned
    treat_profile = with_feature(base_profile, feature_axis)      # one axis flipped
    runs = []
    for seed in seeds:                                            # common random numbers
        runs.append(paired(
            run_arm(taskset, base_profile,   seed),
            run_arm(taskset, treat_profile, seed)))
    report = paired_study(runs, declared_treatment_dimensions=[feature_axis])
    # inside: assert_comparable → mcnemar_exact → holm_bonferroni → paired_bootstrap_ci
    # report is signed by an evidence producer key and pinned to the trajectory digests
    return report    # feeds the capability ledger; promotion only on held-out lift
```

## 9. Development guidelines

Additive to `AGENTS.md` and the archived v3 guidelines; these are engineering standards for the
harness-convergence program.

### 9.1 Capability-addition checklist (run before writing any agentic feature)

1. Which existing port, SPI, pack slot, or policy takes this? (If none → Lane B contract proposal,
   additive, versioned — never a runtime hack.)
2. Does it touch `domain/`, `kernel/`, `ports/`? If yes: escalation trigger; stop.
3. Is it deterministic under pinned inputs? If it needs randomness: seed from run identity, record
   in `D_R` (the `stochastic.py` stall-instrument pattern is the precedent: derived RNG streams,
   auditable replay).
4. Where does its output go — causal event, artifact, or telemetry? (Exactly one; telemetry is never
   ledger truth; artifacts precede the events that reference them.)
5. What is its falsifier? (No falsifier, no merge — existing rule, restated because it applies to
   every harness plugin too.)
6. What is its ablation axis? (Register the feature in the matrix §5.3 so it is measurable from day one.)
7. Does it fail closed? (Unknown config, missing artifact, unavailable model ⇒ typed failure, never
   a silent default — W-3 is the cautionary example inside this very codebase.)

### 9.2 Harness-specific standards

- **Oracles are two-sided and exterior-signed.** No in-process `.passed` booleans; no self-graded
  exits; `undeterminable` never counts as success.
- **Every model call is attributable.** Provider telemetry (usage, resolved model, cost) must reach a
  durable event — the `_DIAGNOSTIC_FIELDS` mechanism in the engine is the pattern; new adapters must
  extend it, not bypass it.
- **Search/exploration is a proposer, not an executor.** MCTS/tree/debate outputs re-enter the
  ordinary proposal path; the chosen candidate is what the ledger shows.
- **Context prefix is sacred.** Mid-run information lands in L5/notes; stage-boundary recompiles are
  explicit, digest-recorded events; nothing mutates L1–L4 after construction.
- **Budgets encode strategy.** Repair budgets, search node budgets, and fan-out counts are typed
  reservations, not counters in a loop.
- **Benchmark code is still production code.** `tools/` runners must pass secrets/isolation linters;
  no API-key reads at import time; hermetic by default, live by explicit selection.

### 9.3 Measurement standards (extended M-6.5 discipline)

- One treatment axis per experiment; arms byte-identical otherwise; seeds bound via common random
  numbers; A/A floor must be interior (non-degenerate) before any A/B reading.
- Report: McNemar exact + Holm–Bonferroni + paired bootstrap CI + regression budget; attach signed
  report digest and constituent trajectory digests.
- Valid negative results are *results*; they select the declared fallback and close the experiment.
- Score claims without a signed evaluator receipt are not claims.

### 9.4 Documentation discipline

- This report is advisory and non-authorizing; it does not amend law. Adoption of any item goes
  through: backlog entry (stable contract) → sprint board (authorization) → evidence receipt
  (acceptance). No new standing markdown files; decisions land as ADRs; status lives in
  `sprint_active.md`.

## 10. Milestone alignment

Every proposal in this report is placed on the existing ladder. Nothing here reorders gates; items
slot into the current board's lanes and the M-4→M-9 sequence.

| Proposal | Slot | Lane | Depends on | Notes |
|---|---|---|---|---|
| Fix W-3 (fail-closed compaction policy) + W-2 (typed dead ends) | Immediate, any window | B (agency/context) | none | Small, hermetic, falsifiable |
| `session.py` / `openrouter.py` extraction | First touch of those files, or dedicated cleanup package | A | green suite at HEAD | Behavior-preserving commits only |
| `mhf.taskset/1` schema + generated readers | Lane B contract work parallel to WP-B2/B3 | B | A-4 codegen pipeline | Unblocks benchmark unification |
| SWE staged loop in `packs/code-default` (stages 0/3/4/5 hardening) | Lane A harness package after WP-A4 | A | taskset schema; existing toolkits | Hermetic first, live rerun for RF-95 evidence |
| Localizer + code-graph + test-selector conversion from LIM | Pack lane package | A (packs) + B (falsifiers) | taskset schema | One module per package, falsifier per conversion |
| Ablation matrix projection + experiment driver | Lab lane package | B | taskset schema; paired machinery exists | Projection is derived; driver in `lab/` |
| MCTS planner + mutation gate conversion | After the matrix exists (so they are measurable) | A + B | matrix; M-6.5 machinery | MCTS = proposer policy with `guarded_consult`-style guards |
| Hierarchical routing in `routing.py` | Adapter package | A | none | Declared profile data entering `D_R` |
| T2 research-explain topology template | After WP-A3 (topologies through real children) | A + B | M-6 + M-7 receipts | Demonstrates generality beyond code |
| SWE-Bench official adapter (`tools/`) | Exterior lab lane | exterior | taskset schema; staged loop | Never into `vanguard/packages` authority surfaces |
| M-8 retrieval ranker (BM25) | WP-A4/B4 window | A (adapter) + B (falsifiers) | durable stores landing | Provenance policy id `bm25/1` |

Sequencing logic: **contracts first** (taskset), **honesty fixes immediately** (W-2/W-3),
**measurements before techniques** (matrix before MCTS), **conversions before deprecations** (LIM
modules deleted only after their replacements carry falsifiers and parity receipts).

## 11. Risks and anti-goals

### 11.1 Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| LIM convergence drifts into "port the engine wholesale" | Medium | One-module-per-package rule; each conversion independently falsified; LIM engine retirement is a tracked exit criterion, not an afterthought |
| Ablation studies become unfalsifiable dashboard theater | Medium | Reuse the strict M-6.5 gates (comparability, A/A floor, Holm); a cell without a signed report is `undeterminable` on the matrix |
| SWE-Bench integration drags container management into the runtime | Medium | Adapter-only rule: images, pins, and instance conversion live in `tools/`; the runtime sees a taskset bundle and a sandbox adapter |
| Extractions regress behavior silently | Low | Byte-identical diff discipline; focused suites before/after; ledger-event invariance asserted in tests |
| TCB creep via "just one small kernel helper" | Low | Standing prohibition restated; budget linter + review trigger |
| Hermetic CI contaminated by live-provider keys | Known historical (D-3 in archived v2B) | Hygiene preflight linter (already proposed there); re-verify presence at HEAD |

### 11.2 Invariants that must survive every change in this report

```text
1. Kernel stays domain-blind, ≤1438 logical LOC, no new verbs without bound falsifier + TCB proof.
2. One composition seam, one ledger writer, events are the only causal truth.
3. I-11 sequential turn loop stays; delegation is mediated spawn; topologies are data.
4. Two-sided oracles; exterior signed evaluation; undeterminable ≠ pass.
5. D_H/D_R/D_X never collapse; every benchmark run is attributable end-to-end.
6. Hermetic by default; provider keys unset; live paths explicitly selected.
7. Artifacts precede referencing events; projections and caches rebuild from events.
8. No new standing markdown authorities; decisions are ADRs; status is the active board.
```

### 11.3 Anti-goals (explicitly out of scope)

- A TypeScript/Python polyglot substrate expansion before wire conformance (archived v1 verdict stands).
- Distributed scheduling, topology search, continuous-learning services — reserved seams only.
- Replacing the sequential scheduler before ADR-0099's successor process says so.
- Any "agent OS" personalization: this framework's value is attribution and verification, not magic.

## 12. Prioritized action register

Ordered by leverage per unit of risk. Owners are Lane A / Lane B / exterior per board convention.

| # | P | Action | Owner | Effort | Verification |
|---|---|---|---|---|---|
| 1 | P0 | Fix W-3: `UnknownCompactionPolicyError` at composition; W-2: typed dead-end consolidation from ledger receipts | B | S | New falsifiers; hermetic suite; no `/1` wire change |
| 2 | P0 | Freeze `mhf.taskset/1` schema + codegen readers + golden vectors; migrate `benchmarks/` tasks onto it | B | M | Dual-read parity receipts; three surfaces resolve the same task digest identically |
| 3 | P0 | Re-derive suite red/green at HEAD; publish hygiene preflight linter (provider keys unset) | A | S | Full discovery clean; linter red on dirty env |
| 4 | P1 | Extract `session.py` → `session/{lifecycle,effects,capture,recovery}.py` | A | M | Behavior-preserving; focused suites; ledger-event invariance |
| 5 | P1 | Build ablation-matrix projection + `lab/` experiment driver on M-6.5 machinery | B | M | Projection rebuild determinism; signed reports; matrix cells `undeterminable` without receipts |
| 6 | P1 | Convert LIM localizer + code graph + test selector into `packs/code-default` toolkits | A+B | M | Digest-pinned outputs; wrong-localization falsifier; determinism property test |
| 7 | P1 | Harden Stage 3: patch parse/anchor/AST-precheck/self-repair (§6.6); add `patchFormat` axis to matrix | A+B | M | Malformed-edit fixtures; ablation report on hermetic suite |
| 8 | P2 | Staged SWE loop end-to-end in `packs/code-default` with two-sided oracles + budgeted repair | A | L | Hermetic SWE suite green; live rerun eligible for RF-95-class evidence |
| 9 | P2 | Convert MCTS planner (proposer policy, guarded) + mutation gate | A+B | L | Guard falsifiers (reuse 5 `guarded_consult` checks); vacuous-patch attack fails gate |
| 10 | P2 | Hierarchical routing in `adapters/models/routing.py` as declared profile data | A | S | `D_R` mismatch ⇒ non-evidentiary falsifier; cost settlement conservation |
| 11 | P2 | BM25 ranker for durable M-8 stores; `bm25/1` provenance policy | A+B | S | Permutation-determinism + absent-corpus falsifiers |
| 12 | P3 | T2 research-explain topology template + citation-verbatim verifier | A+B | M | Runs via M-6/M-7 path; unverifiable citation ⇒ `undeterminable` |
| 13 | P3 | Official SWE-Bench adapter in `tools/` (instance→taskset conversion, submission export from ledger) | exterior | M | Ledger-derived submission artifact; hermetic smoke on pinned subset |
| 14 | P3 | LIM engine retirement: deprecate module imports as conversions land; `check_duplication --enforce` clean | A | S per step | No production import; lab driver consumes framework only |
| 15 | P3 | Extend Python CLI verbs: run/resume/status/diff/ablate | A | S | Contract tests; no duplicated authority logic in CLI |

### Exit criteria for the program

```text
1. All LIM harness techniques exist as lattice components with falsifiers; LIM engine has no
   production import surface.
2. One taskset contract drives hermetic suite, SWE-Bench adapter, and synthetic corpus.
3. Every harness feature in the matrix has a signed paired report or an explicit "unmeasured" cell —
   never an assumed one.
4. SWE-Bench-class resolution improves on the ablation matrix with held-out lift, attributable to
   named feature axes via trajectory digests.
5. Kernel LOC unchanged; boundaries, TCB, blindness, duplication linters green throughout.
```

## 13. Final conclusion

AETHER's backend does not need a better architecture; it needs its architecture to be used by all of
its own intelligence. The kernel, ledger, identity, and evidence planes are genuinely differentiated
assets that most agentic frameworks lack — attribution, budget truth, recovery, and fail-closed
evaluation are already solved here. The gaps are concentrated and addressable: the coding harness is
missing its verification-driven staged loop, the best harness techniques in the repo live outside the
authority regime that would make them trustworthy and reusable, and the measurement machinery that
already exists (M-6.5's paired studies) has not been pointed at harness features.

The program in this report — converge LIM, industrialize the SWE staged loop, build the ablation
matrix, decompose `runtime/` — is executable within the existing milestone ladder, spends zero kernel
LOC, and turns the project's unusual substrate strengths into a measurable, promotable coding-harness
capability. The first three actions (compaction fail-closed fixes, taskset contract, suite re-derivation)
can start immediately and de-risk everything after them.

When the exit criteria above hold, AETHER will not merely be a substrate with advanced mechanisms — it
will be a framework whose agentic coding harness is itself evidence-grade: every feature measured,
every event attributable, every score signed, and every improvement promoted through the same
generator/evaluator/promoter discipline the project applies to everything else.

*End of report.*















