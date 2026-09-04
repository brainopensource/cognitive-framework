---
id: guide.outer-loop.coding-patterns
canonical_id: guide.outer-loop.coding-patterns
class: guide
authority: descriptive
status: proposed
implementation_status: NOT_STARTED
owner: consolidation-agent
canonical_for:
  - outer-loop implementation file layout
  - pack authoring pattern for orchestration ports
purpose: Implementation-level pseudocode and workflow patterns for building the packages in docs/execution/proposed-backlog-outer-loop.md
audience: [contributor, developer]
last_verified: "2026-09-02"
relationships:
  - arch.outer-loop.orchestrator
  - execution.proposed-backlog.outer-loop
  - guide.add-pack-or-tool
  - guide.add-adapter-or-provider
---

# Outer-Loop Coding Patterns & Workflows

Follow `guide.add-pack-or-tool.md`'s existing authoring convention for every package below —
this doc only adds the orchestration-specific shapes on top of that convention, it does not
replace it.

## 1. File layout (proposed)

```
vanguard/packages/domain/ports/orchestration.py        # ORCH-01..11 ports (Protocols)
vanguard/packages/domain/orchestration/
    events.py            # OrchestrationEvent variants, ORCH-01
    plan.py               # ExecutionPlan, Package, LaneId, ORCH-02
packs/orchestration/
    event_bus/            manifest.json, adapter.py     # ORCH-01
    planner/               manifest.json, adapter.py     # ORCH-02
    dispatcher/            manifest.json, adapter.py     # ORCH-03
    policy_sequential/     manifest.json, adapter.py     # ORCH-04  (Strategy A)
    policy_director/       manifest.json, adapter.py     # ORCH-09  (Strategy B)
    policy_evolutionary/   manifest.json, adapter.py     # ORCH-10  (Strategy C)
    compactor_v1/          manifest.json, adapter.py     # ORCH-05
    compactor_lda/         manifest.json, adapter.py     # ORCH-06
    verifier_exterior/     manifest.json, adapter.py     # ORCH-07
    approval_gate/         manifest.json, adapter.py     # ORCH-08
    drift_utils/           manifest.json, adapter.py     # ORCH-11
vanguard/clients/cli/commands/orchestrate.py             # `vg orchestrate run <plan.yaml>`
benchmarks/benchmark_20_suite/runner.py                  # + orchestration_policy param, ORCH-M1
```

Every `packs/orchestration/*` directory is an ordinary Domain Pack per the two-tier extension
model — it gets a `manifest.json`, goes through `compose.py`, and is activated/verified by
`activation.py` exactly like any existing pack. This is what makes each box swappable: to try
a different `Compactor`, you write a new pack and change one manifest reference, not a code
path.

## 2. `OrchestrationEvent` (ORCH-01) — pseudocode

```python
@dataclass(frozen=True)
class OrchestrationEvent:
    kind: str                    # "orch.package.dispatched", etc. — see architecture doc §5
    ts: float
    plan_id: str
    pkg_id: str | None
    payload: dict[str, Any]      # kind-specific, schema-validated at append time

class SqliteEventBus:
    """Projection adapter — appends to the SAME ledger table the kernel already writes,
    filtered by event-kind prefix 'orch.'. Mirrors AgentView's replay-from-ledger pattern."""

    def append(self, event: OrchestrationEvent) -> None:
        validate_against_schema(event)          # fail closed — malformed events never land
        self._ledger.append_fact(namespace="orch", record=asdict(event))

    def since(self, checkpoint: LedgerCursor) -> Iterable[OrchestrationEvent]:
        for row in self._ledger.read_facts(namespace="orch", after=checkpoint):
            yield OrchestrationEvent(**row)

    def subscribe(self, predicate):
        # poll or WAL-hook based tail, same mechanism the runtime already uses for
        # its own event bus — reuse, do not reinvent a pub/sub layer.
        for event in self._ledger.tail(namespace="orch"):
            if predicate(event):
                yield event
```

## 3. `ExecutionPlan` builder (ORCH-02) — pseudocode

```python
def build_plan(backlog: BacklogSnapshot) -> ExecutionPlan:
    graph = DAG()
    for pkg in backlog.packages:
        graph.add_node(pkg.id, lane=pkg.lane, predicate=pkg.acceptance_predicate)
        for dep in pkg.depends_on:
            graph.add_edge(dep, pkg.id)
    if graph.has_cycle():
        raise PlanError("backlog dependency cycle", cycle=graph.find_cycle())
    return ExecutionPlan(graph=graph, lanes=backlog.lanes, wip_limit=backlog.wip_per_lane)

def next_ready(plan: ExecutionPlan, lane: LaneId) -> Package | None:
    in_flight = plan.count_in_flight(lane)
    if in_flight >= plan.wip_limit[lane]:
        return None
    candidates = [p for p in plan.graph.nodes_with_lane(lane)
                  if plan.graph.all_deps_done(p) and not plan.is_done(p)]
    return plan.pick_highest_priority(candidates)   # ties broken by declared backlog order
```

## 4. `SequentialDirector` main loop (ORCH-04) — reference implementation shape

```python
class SequentialDirector:
    def __init__(self, plan, dispatcher, compactor, verifier, bus, approval_gate, policy):
        ...  # standard hexagonal constructor injection, same style as HarnessSession.__init__

    def run(self) -> OrchestrationRunReport:
        self.bus.append(OrchestrationEvent("orch.plan.built", ..., self.plan.summary()))
        while True:
            pkg = self.plan.next_ready(lane=self.lane)
            if pkg is None:
                if self.plan.all_done():
                    break
                self._await_in_flight()
                continue

            ctx = self.compactor.build_context(pkg, self.budget.remaining_for(pkg))
            episode = self.dispatcher.spawn(pkg, ctx)
            self.bus.append(OrchestrationEvent("orch.package.dispatched", ..., {
                "pkg_id": pkg.id, "episode_id": episode.id, "strategy": "sequential"}))

            receipt = episode.run_to_completion()
            self.bus.append(OrchestrationEvent("orch.package.receipt", ..., receipt.as_dict()))

            verdict = self.verifier.verify(pkg, receipt)
            self.bus.append(OrchestrationEvent("orch.package.verified", ..., verdict.as_dict()))

            if verdict.result == "pass":
                if self.approval_gate.requires_human(verdict, self.policy):
                    ticket = self.approval_gate.request_approval(verdict)
                    decision = self.approval_gate.resolve(ticket)   # blocks or polls per mode
                    if decision.rejected:
                        self._revise(pkg, decision.notes); continue
                self.plan.mark_done(pkg)
                self.compactor.compact_episode(receipt)   # feeds future TaskContext builds
            else:
                self._revise_or_escalate(pkg, receipt, verdict)

        return self._final_report()
```

## 5. `DirectorObserver` prompt/tool contract (ORCH-09)

The Director's own episode is an ordinary `HarnessSession` with a deliberately narrow tool
surface — this keeps it auditable and keeps its own context bounded:

```
tools available to the Director principal:
  read_ledger(since: cursor) -> OrchestrationEvent[]
  read_diff(episode_id) -> unified_diff (bounded to N lines; over-limit -> summary only)
  read_verifier_report(pkg_id) -> VerificationVerdict
  read_plan_predicate(pkg_id) -> str
  emit_directive(action: APPROVE|REQUEST_REVISION|REQUEST_NEW_TASK|ESCALATE|CLOSE, notes: str)

NOT available: fs.write, shell exec, or any tool that mutates the workspace directly.
The Director recommends; only Dispatcher (acting on an approved directive) mutates state.
```

This separation — Director reasons, Dispatcher acts — is the concrete implementation of "não
autoriza a si mesmo": the same authorization/effect split the kernel already enforces at the
episode level (`observe -> propose -> authorize -> effect`), reapplied one level up.

## 6. Compaction pattern (ORCH-05/06)

```python
def compact_episode(receipt: EpisodeReceipt) -> CompactedMemory:
    return CompactedMemory(
        episode_id=receipt.episode_id,
        intent=receipt.task.brief_summary(),
        decisions=extract_decisions(receipt.transcript),      # heuristic + cheap LLM pass
        artifacts=receipt.artifacts_index(),
        interfaces_exposed=receipt.declared_interfaces(),
        pitfalls=extract_pitfalls(receipt.transcript),
        token_count=count_tokens(...),
    )

def build_context(pkg: Package, budget: TokenBudget) -> TaskContext:
    deps = [compactor.retrieve(MemoryQuery(pkg_id=d), budget.slice_for(d))
            for d in pkg.depends_on]
    # ORCH-06: retrieve() delegates to LDA's existing query/ranking pipeline instead of a
    # bespoke vector store — see tools/007_LLM_DOCS_ATLAS for the ranking/allocator API to bind.
    return TaskContext(brief=pkg.brief, dependency_memories=deps, budget=budget)
```

## 7. Testing/measurement workflow (not "exhaustive tests" — targeted ablation, per mandate)

1. Implement `ORCH-01..04` first (M-O2 gate) with the *narrowest* possible surface: no
   `Compactor` sophistication, no `DirectorObserver` yet — get a real 3-package chain running
   end to end on `benchmark_20_suite` before adding any other strategy.
2. Add `ORCH-M1` (runner param) at the same time as `ORCH-04`, not after — this makes every
   subsequent package measurable from day one instead of retrofitted.
3. Only after M-O2 is green: build `ORCH-05/06` (compaction), re-run the same fixed package
   set, diff the token/wall-clock/acceptance columns. This is the first real ablation point
   (one variable: compactor v1 vs v2).
4. Only after that: `ORCH-07/08/09` (Strategy B) as a decorator over the same dispatch — rerun
   again, second ablation point (one variable: policy A vs B, compactor and verifier held
   fixed).
5. `ORCH-10` (Strategy C) last, and only against packages whose acceptance predicate is
   already a numeric evaluator score (do not force it onto boolean-pass/fail packages).

## 8. Anti-patterns to avoid (explicit, since the mandate warns about large-context failure modes)

- **Do not** let the Director read raw multi-turn transcripts — only compacted evidence
  (§6 of the architecture doc). If the Director's own context grows with the number of
  packages processed, the design has failed its own purpose.
- **Do not** give the Director write tools. Authorization and effect stay split, one level up
  from the kernel's own split, for the same reason.
- **Do not** fork LDA for outer-loop retrieval. Extend it; two independent memory/retrieval
  systems is exactly the sprawl `AGENTS.md`'s anti-sprawl rules already warn against.
- **Do not** treat `EvolutionaryOuterLoop` as a default. It is real budget spent on breadth
  over depth; only justified where the backlog's `orchestration_strategy: evolutionary`
  manifest field is explicitly set, and only after `ORCH-M2`'s ablation shows it winning on
  that package class.
