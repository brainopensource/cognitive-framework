---
id: arch.outer-loop.orchestrator
canonical_id: arch.outer-loop.orchestrator
class: architecture
authority: descriptive
truth_plane: PROPOSED
status: proposed
implementation_status: NOT_STARTED
owner: consolidation-agent
canonical_for:
  - long-horizon multi-package agentic delivery
  - director / manager layer above the kernel
  - context-window management strategy for large roadmaps
purpose: >
  Propose a layer above the existing AETHER kernel + composition substrate that turns
  "one episode does one task well" into "many episodes deliver a whole roadmap reliably",
  without changing the kernel's S0-S12 dispatch contract.
audience: [architect, contributor, release-owner]
last_verified: "2026-09-02"
relationships:
  - repo-root-vision
  - arch.system.overview
  - arch.composition.extensibility
  - arch.trust.kernel
  - execution.milestones
supersedes: []
superseded_by: null
note: >
  This document does not modify VISION.md, SPEC.md, or any ADR. It proposes a new
  higher layer (layer 7 in the precedence ladder terms: "orchestration", sitting
  *above* Communication, driven by Execution) and must be ratified through the
  repo's normal ADR process before any code lands.
---

# Outer-Loop Orchestrator — "The Director Layer"

## 0. Problem statement (restated precisely)

AETHER's kernel + `HarnessSession` + `EpisodeEngine` is an **inner loop**: one episode, one
principal, one context window, one budget, bounded by `admission_required()` / `AdmissionGate`
at the end. It is good at *one task done well*. The gap is everything above a single episode:

- A roadmap with dozens of packages (`SOTA-01..11`, Lane A/B in `docs/execution/active.md`)
  does not fit one context window, and today nothing owns *sequencing across* episodes except
  a human editing `active.md` by hand.
- Long sessions drift: without an external observer, an agent can satisfy its own admission
  gate locally while diverging from the roadmap globally (plan adherence decays over many
  turns — this is a *cross-episode* failure mode, not something `AdmissionGate` can see,
  because `AdmissionGate` only ever sees one episode's evidence).
- Context is a scarce, moving resource across a *program*, not just across a *turn*. AETHER
  already has turn-level pruning (`truncation_detector`, `protocol_decoders` in
  `EpisodeEngine`); there is no program-level equivalent — no compaction of *finished*
  episodes into reusable, budgeted memory that later episodes can cite instead of re-deriving.
- There is no autonomous-with-override control surface: today it's fully manual (edit
  `active.md`) or fully autonomous-per-episode (kernel budgets). Nothing sits in between and
  lets an operator watch a stream of events and intervene only when it matters.

## 1. Non-negotiable constraint

**The kernel does not change.** `observe → propose → authorize → effect → receipt → evaluate`
stays the atomic unit. Everything below is a *consumer* of the kernel's ledger and a
*producer* of new `TaskContext`/`HarnessSession` instances — exactly the way a human operator
uses the system today, just automated and observable. This is why the design is additive:
it is a new Domain Pack + a new hexagonal Adapter tier (per `arch.composition.extensibility`
§1), not a kernel change.

```
 ┌─────────────────────────────────────────────────────────────────────┐
 │  OUTER LOOP  (this proposal — new)                                  │
 │  Director → Planner → Dispatcher → {N × HarnessSession} → Verifier  │
 │  → Compactor → Ledger-of-ledgers → (approve | revise | escalate)    │
 └───────────────────────────┬───────────────────────────────────────┘
                              │ each spawned episode is an ordinary
                              │ inner-loop run — kernel unchanged
                              ▼
 ┌─────────────────────────────────────────────────────────────────────┐
 │  INNER LOOP (existing, unchanged)                                   │
 │  HarnessSession → EpisodeEngine → Kernel S0-S12 → SQLite-WAL ledger │
 └─────────────────────────────────────────────────────────────────────┘
```

## 2. Three orchestration strategies, compared

The mandate asks explicitly for more than one approach so they can be measured
head-to-head. All three share the same **primitives** (§4) and the same **event contract**
(§5); they differ only in the *policy* that decides "what episode runs next and when do we
stop." This is the actual variable under scientific control — swap the policy, hold
primitives/event-schema/benchmark fixed.

### Strategy A — `SequentialDirector` (closest to current practice, made explicit)

Mirrors what `docs/execution/active.md`'s Lane A/B WIP=1 board already does by hand: a strict
dependency-ordered queue, one package in flight per lane, gate = kernel's own
`AdmissionGate` receipt. This is the *control* condition for benchmarking — it formalizes
today's manual process, it does not out-perform it.

```
loop:
  pkg = plan.next_ready_package(lane)         # topological order from backlog.md deps
  ctx = compactor.build_context(pkg, budget)   # §6
  episode = dispatcher.spawn(pkg, ctx)
  receipt = episode.run_to_completion()
  if receipt.admitted:
     ledger.record(PACKAGE_DONE, pkg, receipt)
     plan.mark_done(pkg)
  else:
     retry_or_escalate(pkg, receipt)           # §7
```

### Strategy B — `DirectorObserver` ("PhD manager", the mandate's explicit request)

A supervisory role, decoupled and hierarchically above the ledger, that does **not** author
code itself. It only ever reads the event stream and takes one of five actions per package
boundary: `APPROVE`, `REQUEST_REVISION`, `REQUEST_NEW_TASK`, `ESCALATE_TO_HUMAN`,
`CLOSE_PROJECT`. This is the layer the mandate describes as "um gestor ... que observa os
eventos mas também aprova, solicita melhorias, correções ou novas interações ou encerra o
projeto." Concretely it is itself an ephemeral agent (same substrate, different
`Principal`/scope — "agents, planners, critics ... are different organizations over the same
substrate", per `README.md`), running a much smaller, cheaper, higher-context-budget episode
whose only tool surface is `read_ledger`, `read_diff`, `read_verifier_report`, and
`emit_directive`.

```
DirectorObserver.on_package_boundary(receipt):
    evidence = ledger.since(last_checkpoint)      # events, not raw transcripts (§6)
    verdict  = director_model.evaluate(
                  plan_intent   = plan.package(receipt.pkg).acceptance_predicate,
                  receipt       = receipt,
                  diff_summary  = evidence.diff_summary,
                  drift_signal  = evidence.plan_adherence_score,   # §7
                  budget_state  = budget.remaining,
               )
    match verdict.action:
      APPROVE            -> plan.mark_done(receipt.pkg); dispatcher.advance()
      REQUEST_REVISION    -> dispatcher.spawn_revision(receipt.pkg, verdict.notes)
      REQUEST_NEW_TASK     -> plan.insert(verdict.new_package, after=receipt.pkg)
      ESCALATE_TO_HUMAN    -> pause(); notify(verdict.reason); await_human_directive()
      CLOSE_PROJECT       -> dispatcher.drain(); ledger.record(PROJECT_CLOSED, verdict.reason)
```

Key property: the Director's own context window is bounded *by construction* because it
never reads raw agent transcripts — only compacted evidence (§6). This is what lets it
supervise arbitrarily many packages without itself suffering the mobile-context-window
problem the mandate describes.

### Strategy C — `EvolutionaryOuterLoop` ("Deep-Alfa"/AlphaEvolve-style, the mandate's explicit request)

For packages where the acceptance predicate is a **measurable score**, not just "tests pass"
(the mandate names this as a distinct case worth trying) — e.g. `benchmarks/benchmark_20_suite`
items, or any package with an evaluator in `benchmarks/frontier_v090/evaluators.py` — run a
population instead of a sequence: spawn `k` independent `HarnessSession`s from the same
`TaskContext` with sampling diversity, score each with the package's own evaluator, keep the
best `n`, mutate (re-prompt with the diff between best-so-far and next-best as guidance),
repeat until score plateaus or budget exhausted.

```
EvolutionaryOuterLoop.run(pkg, budget):
    population = [dispatcher.spawn(pkg, ctx, seed=i) for i in range(k)]
    scored     = [(episode, evaluator.score(episode.result)) for episode in population]
    generation = 0
    while budget.remaining() > 0 and generation < max_generations:
        scored.sort(key=score, reverse=True)
        elite = scored[:n]
        if plateaued(elite, window=2):
            break
        population = [
            dispatcher.spawn(pkg, ctx_with_guidance(elite), seed=k*generation+i)
            for i in range(k)
        ]
        scored = [(e, evaluator.score(e.result)) for e in population]
        generation += 1
    return best(scored)
```

This is strictly opt-in per package (`package.manifest.orchestration_strategy: evolutionary`)
and strictly more expensive — the backlog entry (§8) requires it be benchmarked against
Strategy A on the same package before being recommended as default for any lane.

### Choosing between them is a config, not a fork

All three implement the same `OuterLoopPolicy` port (§4). `SequentialDirector` is the
default. `DirectorObserver` wraps *any* policy (A or C) as a supervisory decorator — it does
not replace the dispatch policy, it gates it. `EvolutionaryOuterLoop` is selected per-package.
This composability is deliberate: it is what makes the comparison in §9 an actual controlled
experiment (swap one variable) instead of three unrelated rewrites.

## 3. Layer placement in the existing precedence ladder

| # | Layer (existing) | This proposal adds |
|---|---|---|
| 0 | Vision (constitutional) | — unchanged |
| 1 | Law (`SPEC.md`) | — unchanged |
| 2 | Decisions (ADRs) | new ADR required before implementation (this doc is pre-ADR) |
| 3 | Architecture/product | **this document** + `docs/backend/architecture/outer-loop-ports.md` (proposed, §4) |
| 3.5 (new) | **Orchestration** | Director/Planner/Dispatcher/Compactor — new pack, `packs/orchestration/` |
| 4 | Sequencing (`milestones.md`, `backlog.md`) | proposed additions in `docs/execution/proposed-backlog-outer-loop.md` |
| 5 | Authorization (`active.md`) | orchestrator *writes* proposed board deltas; a human or `DirectorObserver` with `ESCALATE` still ratifies |
| 6 | Communication | this doc + coding-patterns doc |

## 4. Primitives (ports — implement as a new Domain Pack, per two-tier extension model)

Everything below is a `Protocol`/port, matching the existing hexagonal style
(`domain <- ports <- kernel <- agency <- runtime -> adapters`). Concrete implementations are
swappable Domain Packs so each box in the flowchart can be independently A/B'd, per the
mandate's requirement that every box be replaceable and composable.

```python
# vanguard/packages/domain/ports/orchestration.py  (proposed — pseudocode)

class EventBus(Protocol):
    """Read/append view over the SAME SQLite-WAL ledger the kernel already writes to.
    Not a new store — a typed projection, same pattern as AgentView (M-5a)."""
    def append(self, event: OrchestrationEvent) -> None: ...
    def since(self, checkpoint: LedgerCursor) -> Iterable[OrchestrationEvent]: ...
    def subscribe(self, predicate: Callable[[OrchestrationEvent], bool]) -> Iterator[OrchestrationEvent]: ...

class Planner(Protocol):
    """Turns backlog.md-shaped package graph into a dependency-ordered, lane-aware queue."""
    def build_plan(self, backlog: BacklogSnapshot) -> ExecutionPlan: ...
    def next_ready(self, plan: ExecutionPlan, lane: LaneId) -> Package | None: ...
    def insert(self, plan: ExecutionPlan, pkg: Package, after: PackageId) -> ExecutionPlan: ...

class Compactor(Protocol):
    """Program-level context management — the mandate's 'compressão, cache avançado'."""
    def build_context(self, pkg: Package, budget: TokenBudget) -> TaskContext: ...
    def compact_episode(self, receipt: EpisodeReceipt) -> CompactedMemory: ...
    def retrieve(self, query: MemoryQuery, budget: TokenBudget) -> list[CompactedMemory]: ...

class Verifier(Protocol):
    """Independent of the episode's own AdmissionGate — this is EXTERIOR evaluation,
    same principle as VISION.md's 'security, containment, exterior evaluation ... are
    optional assurance profiles', applied at package granularity instead of turn granularity."""
    def verify(self, pkg: Package, receipt: EpisodeReceipt) -> VerificationVerdict: ...

class ApprovalGate(Protocol):
    """The human-in-the-loop / autonomous switch, per package or per directive."""
    def requires_human(self, verdict: VerificationVerdict, policy: ApprovalPolicy) -> bool: ...
    def request_approval(self, verdict: VerificationVerdict) -> ApprovalTicket: ...
    def resolve(self, ticket: ApprovalTicket) -> ApprovalDecision: ...  # blocks in interactive mode,
                                                                        # polls in autonomous mode

class OuterLoopPolicy(Protocol):
    """Strategy A/B/C all implement this. Dispatcher only knows this port."""
    def next_action(self, state: OrchestrationState) -> OuterLoopAction: ...

class Dispatcher(Protocol):
    """Only thing allowed to touch HarnessSession/EpisodeEngine directly."""
    def spawn(self, pkg: Package, ctx: TaskContext, **kw) -> HarnessSession: ...
    def spawn_revision(self, pkg: Package, notes: str) -> HarnessSession: ...
```

Each of these is one manifest-declared Domain Pack (`packs/orchestration/{planner,compactor,
verifier,approval,policy,dispatcher}/manifest.json`), independently swappable exactly like
existing Adapters, so "trocar facilmente depois" (the mandate's flexibility requirement) is
structural, not aspirational.

## 5. Event contract (what the Director actually watches)

Reuse the kernel's existing fact-over-ledger philosophy — do not invent a second source of
truth. `OrchestrationEvent` is a typed row appended to the same SQLite-WAL ledger under a
distinct event-kind namespace (`orch.*`), replay-able the same way `AgentView` replays
`agent.*` events (M-5a). Minimum event vocabulary:

```
orch.plan.built            {plan_id, packages[], lanes[]}
orch.package.dispatched    {pkg_id, episode_id, strategy, budget}
orch.package.receipt       {pkg_id, episode_id, admitted: bool, evidence_digest}
orch.package.verified      {pkg_id, verdict: pass|fail|inconclusive, verifier_id}
orch.director.verdict      {pkg_id, action, notes, confidence}
orch.approval.requested    {pkg_id, reason, policy}
orch.approval.resolved     {pkg_id, decision, actor: human|autonomous}
orch.memory.compacted      {episode_id, compacted_digest, tokens_before, tokens_after}
orch.drift.detected        {pkg_id, plan_adherence_score, signal}
orch.project.closed        {reason, final_state}
```

Bottleneck/dead-end detection (mandate: "identificar os gargalos, caminhos mortos") is a pure
function over this event stream, not a new subsystem:

```
def find_dead_ends(events):
    return [pkg for pkg, evs in group_by_package(events)
            if count(evs, kind="orch.package.dispatched") >= RETRY_CEILING
            and last(evs).kind != "orch.package.verified.pass"]

def find_bottlenecks(events):
    durations = {pkg: last(evs).ts - first(evs).ts for pkg, evs in group_by_package(events)}
    return sorted(durations.items(), key=lambda kv: kv[1], reverse=True)[:N]
```

## 6. Context-window strategy (the mandate's core pain point)

Three independent mechanisms, each a swappable `Compactor` implementation, composed:

1. **Rolling episode window** — a package's `TaskContext` is built from the *compacted*
   output of its dependency packages, never their raw transcripts. `compact_episode()`
   distills a finished `EpisodeReceipt` into: `{intent, decisions_made, artifacts_produced,
   interfaces_exposed, known_pitfalls}` — a few hundred tokens, not the multi-turn transcript.
   This is the "janela móvel" the mandate asks for, implemented as summarization-on-write
   rather than truncation-on-read, so information is compacted once and reused many times.

2. **Retrieval-backed long-term memory** — compacted memories are embedded/indexed (this
   repo already has `tools/007_LLM_DOCS_ATLAS` / "LDA" — the LLM Docs Atlas mentioned in
   `README.md`'s roadmap as already having "query, ranking, compiler, storage, allocator,
   indexer, briefing" capabilities). **Reuse LDA as the retrieval backend for
   `Compactor.retrieve()` instead of building a second index** — this is the single biggest
   "don't reinvent, extend" opportunity in the whole proposal, since LDA already solves
   token-bounded routing (`AGENTS.md` §"Repository-Intelligence Navigation Protocol"
   describes exactly this pattern for human/agent doc navigation today).

3. **Budget-aware caching** — `orch.memory.compacted` events record `tokens_before/after`;
   a package's `TaskContext` build is itself budgeted (`TokenBudget` in `Planner`/`Compactor`
   signatures above), so the Director can answer "how much context does finishing the
   roadmap cost" before committing, not just "how much did the last episode cost."

## 7. Drift, hallucination, and plan-adherence handling

Plan adherence is measured, not assumed:

```
plan_adherence_score(pkg, receipt) =
    cosine(embed(pkg.acceptance_predicate), embed(receipt.summary))
    weighted by: interfaces_touched ⊆ pkg.declared_interfaces (hard constraint, not scored)
```

If `interfaces_touched ⊄ declared_interfaces` → automatic `orch.drift.detected`, regardless of
score — this is the concrete mechanism for "evitar hallucinações" at the *scope* level (an
agent editing files outside its package's declared boundary is drift by definition, cheap to
detect from the ledger's own `fs.write` effect records, no LLM judgment required). Score-based
drift (predicate/summary mismatch) is a *softer* signal that feeds `DirectorObserver`'s verdict
but never auto-blocks — only `ESCALATE_TO_HUMAN` or `REQUEST_REVISION`.

## 8. Control surface — interactive vs autonomous, same code path

`ApprovalPolicy` is data, not code branching:

```
ApprovalPolicy:
    mode: "interactive" | "autonomous" | "hybrid"
    escalation_triggers: [DriftAboveThreshold, VerifierInconclusive, BudgetExceeded, ProjectClose]

ApprovalGate.requires_human(verdict, policy):
    if policy.mode == "interactive": return True
    if policy.mode == "autonomous": return False
    return any(t.matches(verdict) for t in policy.escalation_triggers)   # "hybrid"
```

`interactive` = every package boundary is a prompt (mandate: "controlar ... através de
prompts de decisão e aprovação"). `autonomous` = `DirectorObserver` decides everything,
operator only *observes* the event stream (mandate: "apenas observar ele trabalhando").
`hybrid` is the default: autonomous except at the specific triggers the mandate names
(drift, inconclusive verification, budget, project close) — this is what "PhD humano" judgment
reduces to operationally: escalate exactly at the boundaries a senior engineer would actually
want paged for, stay silent otherwise.

## 9. Scientific comparison methodology (mandate: "medir o score... poucas variáveis por vez")

Fixed across all conditions: same package set, same `Compactor`, same `Verifier`, same token
budget ceiling. Varied: exactly one of `{policy: A|B|C, compactor: v1|v2, verifier: kernel-only|
kernel+exterior}`. Use `benchmarks/benchmark_20_suite` (already exists, already has 20 scored
tasks + a `runner.py`) as the fixed measurement harness — do not build a new benchmark
runner; extend `runner.py` to accept an `orchestration_policy` parameter and record
`orch.*` events alongside its existing results JSON. Score reported per condition:

| Metric | Source |
|---|---|
| package acceptance rate | `orch.package.verified` pass ratio |
| tokens per accepted package | `orch.memory.compacted` deltas |
| wall-clock per accepted package | event timestamps |
| drift incidents / package | `orch.drift.detected` count |
| human interventions / package | `orch.approval.requested` where `actor: human` |
| dead-end rate | `find_dead_ends()` |

This gives an ablation table directly comparable to the existing
`benchmarks/ablation/cmx06_protocol.json` pattern already used in this repo — reuse that
artifact shape rather than inventing a new report format.

## 10. What this proposal deliberately does NOT do

- Does not touch `vanguard/packages/kernel/*` or the S0-S12 dispatch contract.
- Does not replace `AdmissionGate` — package-level `Verifier` is exterior and additional,
  episode-level admission is unchanged.
- Does not introduce a second ledger — `orch.*` events live in the same SQLite-WAL store.
- Does not mandate Strategy B or C as default — Strategy A (`SequentialDirector`) remains the
  default until §9's benchmark shows a condition beats it on the fixed harness.

See `docs/execution/proposed-backlog-outer-loop.md` for the package sequence to build this,
and `docs/backend/guides/outer-loop-coding-patterns.md` for implementation-level pseudocode
and file-by-file placement.
