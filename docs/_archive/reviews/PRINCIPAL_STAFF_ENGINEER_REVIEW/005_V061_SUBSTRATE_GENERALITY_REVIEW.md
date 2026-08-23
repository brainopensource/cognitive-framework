# 004 — Substrate Generality Review (independent)

**Classification:** Engineering Director / Principal Staff Engineering Review Board.
**Subject:** Can the v0.6 foundation become a general agentic substrate, or is it a strong
coding-agent harness with a kernel attached?
**Evidence base:** `SPEC.md`; ADRs `0069`–`0076`; `001` GAMMA; `002` register; `003` Director
review; `000_CANONICAL_EXECUTION_PATH.md`; wave plans 1–4; `sprint_active.md`; `backlog.md`;
`milestones.md`.
**Status:** Advisory. Does not amend SPEC or any ADR. Two recommendations request a scope
decision at M-3; neither reopens `0069`–`0076`.

---

## 0. Verdict first

**You are building the substrate, not merely a coding harness. The primitives are right. The
composition surface is not yet, and it is the layer your users will actually touch.**

The trust spine (authority, state, evidence), the recursion primitive (`spawn`), and the identity
trinity (`D_H`/`D_R`/`D_X`) are sufficient to express tree search, debate, critic loops,
evolutionary search, hierarchical decomposition and multi-agent coordination **without a new
engine**. That is the hard part and it is done correctly.

What blocks the vision is narrower than the vision's ambition suggests:

1. `harness.yaml` is a **fixed-slot template** (one planner, one context, one memory, one
   evaluation, N toolkits), not a composition algebra. Most of the algorithms you named need
   *N planners and N evaluators with declared wiring*.
2. **Planners cannot spawn.** `spawn` is engine-owned, so any algorithm whose shape *is* a
   spawn topology has nowhere to live except inside the engine.

Both are fixable at Wave 3 with contained changes. Both become expensive after Wave 4, because
`D_H` is computed over the manifest shape and every pack is written against it.

Ship-blocking risk is not architectural. It is **scope-weighting**: Wave 3 — where the framework
claim is actually proven — is currently one sprint carrying the least-proven code in the tree.

---

## 1. What AETHER is today

A mature Python runtime (`vanguard/packages/`) whose valuable parts are unusually hard to
replicate:

- **S0–S12 effect kernel** with descriptor-bound grants, attenuation, leases, and write-ahead
  durable intent (S8a) before dispatch. 95 tests. This is a real reference monitor, not a
  permissions dict.
- **One canonicalisation** (JCS, RFC 8785) as the sole digest/signing byte source.
- **One selector algebra**, total and fail-closed, as the sole inclusion relation.
- **SQLite WAL + FULL sync ledger** with per-Project hash chains, and — since M-1 — a *cold*
  replay job that reconstructs grants, budgets, approvals and episode FSM from disk in a fresh
  process. That is the version of I-4 most projects claim and almost none implement.
- **Exterior signed judge** (UID 10002, Ed25519, nonce-bound verdicts, gateway-only writes).
- **Rootless bwrap sandbox** (UID 10001) for `proc.exec` / `patch.apply`.
- **Recursive episode engine** with attenuated `spawn()`.

Programme state: M-0 and M-1 green; M-2 in flight (2.2-A triaged, 2.2-B/C authorized); M-3 and
M-4 queued. `layer0/` is shrinking on schedule and dies at 3.1.

Two honest observations about *today* that the internal documents state but do not weigh:

- **There is no plugin lifecycle in `vanguard/packages/` at all.** Registry and compose-with-slots
  exist only in the fork that is being deleted. The extensibility thesis is entirely unproven on
  the canonical path.
- **The governance corpus is currently larger than the substrate work it governs** — roughly 3.4k
  lines of normative and planning prose across seven authority tiers, plus a file (`000`) whose
  job is to tell a developer which of the other files wins. That was a rational response to the
  dual-runtime failure. It is not free, and its cost is now rising.

---

## 2. Structurally strong — keep as-is

| Asset | Why it survives several generations |
|---|---|
| **Three planes** (decision / state / evidence) | The only clean answer to "who is allowed to say what happened." Most frameworks let the orchestrator be its own historian; you cannot recover attribution afterwards. |
| **Exterior, unreachable judge** | The separability thesis is a genuine moat. It is what makes a later training signal un-gameable *by construction* rather than by policy. Nobody else has this. |
| **`Agent = Principal + HarnessInstance`; `spawn` as the only delegation primitive; swarm as policy** | The single most important decision in the tree for the general-substrate goal. Refusing `MetaAgent`/`SwarmEngine`/`Orchestrator` as types is what keeps algorithm variety from becoming engine variety. |
| **Identity trinity `D_H`/`D_R`/`D_X`**, with prompt/ceiling/policy/routes inside `D_H` | Locks the *denominators* of every future experiment before any experiment exists. Collapsing these is the mistake that permanently forecloses self-improvement, and you did not make it. |
| **Typed budget algebra** — additive `{usd, tokens, bytes, millis}` vs structural `{depth, turns}`; siblings not summed | Correct mathematics. The 2.2-A note that a duck-typed `as_map()` could have *silently* restored sibling-depth summing is the best piece of engineering reasoning in the corpus. |
| **One algebra, one canonicalisation, one writer** (ADR-0076) | Semantic drift is the failure mode that actually killed the previous architecture. Naming the canonical artifact rather than "harmonising" two is right. |
| **Wire-first plugin boundary**, Protocol as client, `in_process` as a *privilege that still speaks the wire* | This is what makes a flat, polyglot, swappable future reachable at all. Do not soften it for ergonomics. |
| **Falsifier discipline** ("a concept without a bound falsifier is not locked") | Culture, not architecture, and worth more than most of the architecture. The F-08 adjudication — declaring a falsifier *stale* rather than bending the kernel to it — is evidence the process discriminates rather than ritualises. |
| **Sequential scheduler (I-11) with a measurement gate** | Correct. Concurrency before selector soundness would have been the classic unforced error. |
| **Model/sandbox as first-party ports, not the sixth SPI** | Correct for now. Routing *policy* is already composition data inside `D_H`, so the experiment surface is preserved without paying wire cost on the hottest path. |

---

## 3. Structurally weak, limiting, or under-weighted

### W1 — The composition model is a template, not an algebra *(highest leverage; act at Wave 3)*

`harness.yaml` binds fixed keys: `planner:`, `context:`, `memory:`, `evaluation:`, `toolkits: []`,
`model_routes: []`. That is a **five-hole agent shape**. It expresses "a ReAct coding agent with
swappable parts" perfectly, and it cannot express:

- a critic loop (needs *two* planner-class components with declared roles);
- debate (N proposers + an aggregator);
- tree search (an expansion policy + a scoring policy + a selection policy);
- evolutionary search (a population operator + a fitness binding);
- a research agent with two evaluation gates (one cheap/inline, one exterior/terminal).

None of these needs a new engine — they are all spawn topologies plus policy. But there is
**nowhere in the manifest to name them**, so today they can only be smuggled inside a single
monolithic planner plugin. That is exactly the "inherit from a large predefined agent
architecture" outcome the vision rejects, arriving through the config file rather than through a
base class.

The external comparison is instructive rather than imitable. <cite index="7-1">DeepSeek Harness organises configuration as a profile: an ordered stack of plugin bundles with profile-specific configuration layered on top</cite> — a flat list, not a fixed record. <cite index="5-1">Its stated design has "no privileged core to patch."</cite> **Do not copy the second property.** The privileged core is your entire differentiation; a flat plugin graph with no authority boundary is exactly the system whose evidence you cannot trust. **Do copy the first.** Flatness at the *composition surface* is orthogonal to rigidity at the *authority boundary*, and you can have both — that is the differentiated position no one currently occupies.

**Recommended shape (design at 3.1-B, do not implement before it):** the manifest becomes a
**named component graph** — a map of component instances, each declaring its SPI kind, ref,
config and capability ceiling, plus an explicit binding section describing wiring. Named slots
survive as a *pack convention* (`code-default` declares one planner named `main`), not as a schema
constraint. `D_H` covers the graph, unchanged in principle. The current pack migrates mechanically.

Cost now: one schema revision and a compose-v2 that resolves a map instead of six keys — work
3.1-B is already doing. Cost after M-4: schema migration, `D_H` migration, every pack rewritten,
every trajectory in the corpus attributed to a superseded shape.

### W2 — Planners cannot spawn, so recursive algorithms have no home *(design now, decide at M-3, implement post-M-4)*

`spawn(parent, harness, capabilities, budget)` is engine-owned. `IPlanner` gets
`plan/observe/reflect`. Therefore any algorithm whose structure *is* recursion — tree search,
hierarchical decomposition, delegation strategies, the §5.1 outer loop — must either live in the
engine (rejected: new engine per algorithm) or be faked inside a planner that cannot actually
create children.

The clean generalisation is already latent in the design: **expose spawn as a
capability-mediated kernel verb** (`agent.spawn`), dispatched through S0–S12 like any other
effect. A planner may spawn only if its composition granted the verb; children are attenuated by
the existing machinery; every spawn is a ledgered, budgeted, attributed event. Authority does not
weaken — it *strengthens*, because delegation stops being a privileged engine call and becomes a
mediated effect with a receipt.

This is the change that converts "a strong ReAct harness with a kernel" into "a framework for
agentic algorithms." It is also the one place where the current design most plausibly forces a
new engine later, which is the ADR-0070 reversal condition stated in its own text.

**Do not implement it now.** It touches the TCB and Wave 4 must not absorb a kernel change. Write
the design note at 3.1, test the hypothesis at M-3 by attempting to express one non-ReAct
algorithm against the component graph, and decide immediately after M-4.

### W3 — The turn loop is not pluggable, and that is correct — but say so with a falsifier

`observe → propose → authorize → effect → receipt → evaluate` should stay mechanism. Algorithms
differ in *what they propose and when they spawn*, not in whether effects get authorized. DSH
makes the loop itself a plugin; that is coherent only because it has no authority boundary to
preserve.

State this as a claim with a falsifier, or it will be relitigated every quarter:
**"name an agentic algorithm that cannot be expressed as spawn-topology + planner policy over
this loop."** If someone produces one, that is genuine ADR-0070 reversal evidence. If nobody can
in a year, the loop is proven and the argument ends.

### W4 — Guardrails are structural where they should be declarable *(cheap; act at Wave 3)*

The user-facing worry is justified. Today a composition cannot easily say "no exterior evaluator"
— a research agent or a pure-compute optimisation loop should not need a UID-10002 daemon and a
preregistered oracle to run. The mechanism is mandatory *and* the policy is mandatory, and only
the second needs to be.

**The rule that resolves this without weakening anything: you may turn a guardrail off; you may
never turn off the record that it was off.**

A composition declares `evaluation: none`. Compose accepts it. `D_H` records it. The trajectory
records `oracle: null` and the run is marked **unattributable for promotion**. The distinction the
substrate must enforce is not *guarded vs unguarded* — it is **absent vs forged**. An unsigned
verdict must never be acceptable; an *acknowledged absence* of a verdict is a legitimate
composition.

Same treatment for sandbox tier and approval policy, per composition and per component.

**Never optional, regardless of composition:** writer authority on privileged kinds; envelope
lineage; fail-closed selector inclusion; ledger-as-truth; capability attenuation on spawn; the
signature requirement on any verdict that *is* claimed; JCS as the byte source. Those seven are
the permanent substrate. Everything else is policy.

### W5 — The `K ≪ N` claim is asserted but not yet defended by any test

`002` §5 states many logical agents share a bounded worker pool. Nothing in the tree demonstrates
logical-agent / worker separation: `EpisodeEngine` *is* the scheduler shell, and `HarnessSession`
holds live per-run state. The question that decides whether a future async scheduler is a refactor
or a rewrite is precise:

> **Is an episode's continuation reconstructible from the ledger alone, or does resuming require
> the live Python object?**

F-02 suggests grants, budgets, approvals and FSM survive a cold fold. That is most of the answer.
Add one falsifier at Wave 2 or 3, while it is cheap:
**suspend an episode mid-turn, reconstruct it in a fresh process from the WAL, resume, complete.**
Green means the concurrency future is a scheduling refactor and I-11 can be lifted on measurement
alone. Red means there is hidden in-process coupling, and you want to know that now, not at
Wave 8. This is the highest-value cheap test not currently on the board.

Ledger throughput: single-writer SQLite per Project is the eventual ceiling, and you already
chose the escape hatch correctly — `project_id` as the consistency unit means sharding by project
needs no model change. Nothing to do now.

### W6 — Over-engineering: the governance corpus

Seven authority tiers, ADRs restating the deferred list four times (SPEC §9, ADR-0073, `002` §2,
`milestones.md`), and ADR-0076 existing solely to adjudicate which of two live artifacts is
canonical. The last one is a symptom worth naming: **it is the tax on having let the fork live**,
not a permanent feature of the process.

Prose duplication drifts the same way code duplication drifts, and prose has no linter. Two
concrete costs already visible: the deferred/refusal list must be updated in four places, and the
`000` file exists because the hierarchy is no longer self-evident.

**Do not touch this now** — mid-flight documentation surgery during Wave 2 is strictly worse than
the duplication. **Schedule for immediately after M-4:** collapse to **SPEC (law) + ADR log
(decisions) + one living board**, retiring GAMMA and `002` as standing authorities once their
content is absorbed. Target: a senior developer productive from three documents, not seven.

### W7 — Under-engineering: Wave 3 carries the framework claim on one sprint

Wave 1 got seventeen tasks and fifteen falsifiers for the trust spine. Wave 3 gets seven tasks
for: registry FSM + ledgered lifecycle + compose v2 + echo plugin + fault injection + isolation
broker + rlimits + pack migration + the coding-token sweep. And it is building on
`layer0/registry/` and `layer0/compose/`, which have **no packages twin and have never run on the
canonical path**.

The trust spine is the moat. The plugin lifecycle is the *product*. Wave 3 should carry the same
falsifier rigour Wave 1 did — at minimum: unknown-ref fails at compose not runtime; empty ceiling
denies; only the registry may append `Plugin*` kinds; a faulted cell cannot leave the FSM in an
active state; `in_process` requires an explicit policy grant; no code path exists that mutates a
frozen composition.

### W8 — Trajectories validate but do not yet carry enough to learn from

`assemble_trajectory` reports a **zero cost vector** (carried to Wave 4). F-12 asserts *schema
validity*, which a content-free record satisfies. That is precisely the shape of failure I-9 was
written to prevent — a digest over `{ids, n}` was rejected for the same reason.

Cost-aware policy learning, escalation calibration (§5.3), and any router experiment are
undefined without per-turn cost. **Strengthen F-12 now** with content assertions: non-zero cost
vector, populated turns, model fingerprint present, verdict embedded or explicitly null. Cheap,
and it protects the dataset that the entire Phase-2 thesis consumes.

---

## 4. The required answers, condensed

1. **What is AETHER today?** A mature, fail-closed effect machine with an exterior judge and a
   real ledger, mid-convergence from a dual runtime, with the extensibility layer still unbuilt.
2. **Strong?** §2 — planes, judge, spawn, identity trinity, budget algebra, one-algebra
   discipline, wire-first boundary, falsifier culture.
3. **Weak/limiting?** §3 — fixed-slot composition (W1), planner/spawn boundary (W2), structural
   guardrails (W4), unproven `K ≪ N` (W5), governance mass (W6), Wave-3 weighting (W7), hollow
   trajectories (W8).
4. **Is the direction correct?** Yes. Waves 0–2 sequencing is right and the trust-spine-first
   ordering was the correct bet. Wave 3's *content* needs widening; its position does not.
5. **Abstractions that survive generations?** `Principal`/`spawn`; `Project` as consistency unit;
   `EffectRequest`/`Receipt`; the event envelope with lineage; `D_H`/`D_R`/`D_X`; `SignedVerdict`;
   the selector algebra; JCS; the three planes.
6. **Should become more composable?** The manifest (W1). The evaluation/approval/sandbox policies
   (W4). Delegation (W2). *Not* the loop, the kernel, or the judge.
7. **Must stay non-pluggable and trusted?** The seven in W4, plus: the dispatch sequence, the
   registry's exclusive right to plugin lifecycle events, the evaluator gateway's exclusive right
   to `VerdictRecorded`, and trajectory emission itself.
8. **Over-engineering?** Governance corpus (W6). Also: the five-SPI freeze is defended more
   strongly than its evidence supports — it will need a review once the component graph exists,
   and that is fine, but "a sixth SPI requires a design review" should not harden into "there are
   five SPIs forever."
9. **Under-engineering?** Wave 3 (W7), trajectory content (W8), the suspend/resume proof (W5),
   and plugin-lifecycle falsifiers.
10. **Many classes of agentic algorithm without new engines?** *Primitives: yes. Composition
    surface: not yet.* Fix W1 and W2 and the answer becomes yes without qualification.
11. **High-performance orchestration of many logical agents?** Preserved but unproven. W5's test
    decides it. Nothing in the current design forecloses it; `project_id` sharding and sequential-
    with-a-gate were both correct calls.
12. **Enough freedom in plugins/composition?** In the *wire*, yes. In the *manifest*, no — W1.
13. **Guardrails as infrastructure vs product constraint?** Currently drifting toward constraint.
    W4's absent-vs-forged rule corrects it at low cost.
14. **Will evidence support self-improvement?** The *identity* architecture will — this is the
    project's quiet triumph. The *content* will not until W8 closes.
15. **What prevents SOTA?** (a) shipping the fixed-slot manifest as the composition API;
    (b) Wave 3 declared done on one echo plugin; (c) governance growing faster than capability;
    (d) trajectories that validate but cannot be learned from; (e) foundation-stop discipline
    eroding under product pressure before M-4 evidence exists.
16. **Highest leverage now?** W1 (manifest → component graph, at 3.1-B), then W8 (F-12 content
    assertions), then W5 (suspend/resume falsifier), then W4 (declarable guardrail policy).
17. **Explicitly wait until after M-4?** W2 (`agent.spawn` as a verb — touches the TCB);
    concurrency enablement; second domain pack; model/sandbox behind the wire; any Meta-Harness
    work; the W6 documentation collapse.
18. **After the foundation MVP?** `composition.yaml` = component graph + policies + ceiling +
    budget → `compose` → `FrozenHarness(D_H)` → one substrate. **Pack #2 becomes a gate, not a
    nice-to-have** — I-7 is unproven until a non-coding pack lands with zero diffs under
    `domain/` and `kernel/`. Then: `agent.spawn` decision, measured concurrency, and only then
    the meta-cognitive layer consuming a corpus that was trustworthy from its first row.

---

## 5. Decision register

| # | Item | Call | When |
|---|---|---|---|
| 1 | Three planes, exterior judge, spawn primitive, identity trinity, budget algebra, one-algebra/one-writer/one-canonicalisation, wire-first plugins, sequential scheduler, model port first-party, packages lattice | **Keep as-is** | — |
| 2 | F-12 content assertions (non-zero cost, populated turns, model fingerprint) | **Strengthen now** | Wave 2/3 |
| 3 | Suspend → cold-reconstruct → resume falsifier | **Strengthen now** | Wave 2/3 |
| 4 | Wave-3 falsifier set for plugin lifecycle (six negatives named in W7) | **Strengthen now** | Wave 3 entry |
| 5 | `_PROC_PATTERN` read from compiled ceiling, not restated | **Strengthen now** | 3.1 (already flagged) |
| 6 | Manifest: fixed slots → named component graph; slots become pack convention | **Generalize now** | 3.1-B — Director scope call |
| 7 | Declarable guardrail policy; absent-vs-forged rule; unattributable-for-promotion marking | **Generalize now** | Wave 3 |
| 8 | Loop stays mechanism — publish the claim with its falsifier | **Keep, document** | Wave 3 |
| 9 | `agent.spawn` as capability-mediated kernel verb | **Design now, decide at M-3, implement post-M-4** | — |
| 10 | Pack #2 as the I-7 generality gate | **Revisit after M-4 — as a gate, not a wish** | Post-M-4 |
| 11 | Concurrency enablement | **Revisit after M-4**, gated on #3 plus selector soundness | Post-M-4 |
| 12 | Five-SPI freeze | **Revisit after M-4**, once the component graph exists | Post-M-4 |
| 13 | Documentation collapse to SPEC + ADR log + one board | **Simplify after M-4** | Post-M-4 |
| 14 | Model/sandbox behind the plugin wire (P1-11/12) | **Experiment later**, measurement-gated | Post-M-4 |
| 15 | Third tree, Rust TCB rewrite, swarm engine, workflow DAG, graph DB, evaluator-as-plugin, mid-run hot-swap, "no privileged core" flatness | **Reject** — already correctly refused; this review adds no reason to reopen any of them | — |

---

## 6. The central question, answered

> *Are we building only a strong coding-agent harness, or the minimal, robust, composable
> substrate from which many generations of agents and agentic algorithms can be constructed?*

**The substrate.** The evidence is that the hardest and least reversible decisions — recursion as
one primitive, authority as a reference monitor, state as fold, evidence as an exterior signature,
identity split three ways — were all made in the general form rather than the coding form, at real
cost, before any product pressure required it. That is not what a coding-harness team builds.

But a substrate is only reachable through the surface people compose against, and yours is
currently shaped like the first pack. Two contained changes at Wave 3 — a component graph instead
of five named slots, and guardrails that are declarable but never forgeable — close the gap
between what the substrate can express and what a developer can ask for.

Make those, hold the M-4 stop line, and make Pack #2 a gate rather than an aspiration. Then the
generality claim stops being a thesis and becomes a falsified-and-survived property, which is the
standard this project has already set for itself everywhere else.
