## 1. Verdict on the three documents

| Document | Use it as | Do not use it as |
|---|---|---|
| **v4 `04` (contracts/wire schema)** | **The keel.** This is the one part that is genuinely load-bearing and genuinely expensive to re-cut. Refactor it, but build on it | A finished schema. It was written before a single run existed |
| **v4 `05` (kernel/capabilities)** | **Enforcement, permanent.** `K-01`, resource selectors, attenuation, descriptor binding. Ship close to as-written | Universal mediation of *every* effect — Rev1 is right, that inflates TCB and latency |
| **v4 `07 §5` (measurement)** | The instrument doctrine, with Rev1's statistical corrections folded in | A complete statistical toolkit — McNemar is paired-binary only |
| **v4 `03` (execution model)** | The `observe→propose→authorise→effect→receipt→evaluate` reduction. This is the actual spine and it is correct | The six planes. That is a deployment topology masquerading as an architecture |
| **v4 `06` (competence)** | §3–§4 (claim pipeline, evaluator classes). Real now | §5–§6. A lifecycle for objects that have never existed |
| **v4 `02`, `09`, `10`** | Claims, non-claims, reversal conditions. Cheap, high-value discipline | A constraint on what you may build |
| **v4 `08`** | Delete and rewrite | Anything |
| **Rev1 (A)** | Program plan: competitor analysis, threat model, metric vector, H1–H12 register, correction reason codes | A design document — it names mechanisms without specifying them |
| **Rev2 (B)** | Design rationale: two-clock split, enforcement/compensation, artifact graph, Lakatos partition | A plan — it has no product surface |

**Roughly 60% of v4 survives.** What dies is the *quantity* of normativity, not the *quality* of the thinking.

---

## 2. The spine: five nouns and one recursion

Here is the thing your whole question turns on. You listed twenty capabilities — memory, context, tools, learning, cognition, reflection, methodologies, skills, workflows, harness engineering, loop engineering, evaluation, integrations, communication, sensors, LLMs, scripting, knowledge, indexing, browsing. **If each becomes a subsystem, you have twenty subsystems and one hundred and ninety integration seams, and the abstraction is dead before it exists.**

The alternative is a *universal reduction*: five types, of which one is recursive.

```
Effect      descriptor → authorisation → execution → receipt
            (every touch of the world: read, shell, model call,
             index query, browse, memory write — no exceptions)

Episode     identity + budget lease + context + operator set + terminal state
            ⟵ RECURSIVE. An episode may spawn episodes.

Artifact    content-addressed, typed by an extensible `kind` registry
            (prompt, skill, tool schema, tool impl, context policy,
             routing policy, playbook, competence claim, harness manifest)

Claim       scoped assertion about an artifact or a run,
            with non-empty invalidation conditions

Event       immutable record of all of the above
```

**The recursion is the whole trick.** A tool is an Episode with no model call. An agent is an Episode with one. A team is an Episode that spawns Episodes. A department is an Episode that spawns Episodes that spawn Episodes. Same type, same budget algebra, same capability attenuation, same event stream, at every scale.

This is why the biology analogy is *right about emergence and fatal as a type hierarchy*. Atom/molecule/polymer/cell/organism must **not** be five classes. They are **names for observed scales of one recursive composite** — labels the trace viewer applies after the fact, exactly as v4 `03 §2.3` says about graphs. Build five types and you have hand-authored the hierarchy you claimed would emerge; build one recursive type and the hierarchy is a *finding* in the ledger. Nature did not implement `class Cell`. It implemented a replicator and let scale happen.

---

## 3. Why this leaves room for everything

Your twenty capabilities, each landing in exactly one of three slots. **This table is the falsification test for the abstraction:** anything that fits none of the three means the spine is wrong.

| Capability | Adapter behind a port | Artifact in the graph | Policy parameter |
|---|---|---|---|
| Tools, scripting, file I/O | Environment adapter | Tool schema + description | Risk tier |
| Browsing, research, sensors | Environment adapter | Retrieval policy | Egress scope |
| LLMs as brains + auxiliaries | Model port (n providers) | Routing policy | Budget vector |
| Short/long-term knowledge | Store adapter (4 stores) | Write/consolidation policy | Retention |
| Indexing, search, caching, compression | Index adapter | Context compiler | Token budget |
| Context | — | **Context compiler (versioned, evaluated)** | Layer budgets |
| Cognition, planning, decomposition | — | **Operators** (invoked inside an Episode) | Activation set |
| Reflection | — | Operator whose output is a *candidate Claim* | Rigidity |
| Methodologies, processes, workflows | — | **Playbooks** with a rigidity dial | Selection policy |
| Skills | — | Artifact | Scope |
| Harness engineering | — | *Editing the artifact graph* | Tier 1/2/3 |
| Loop engineering | — | *Editing episode-policy artifacts* | — |
| Learning | Offline optimiser reading the ledger | Writes candidate Artifacts | Promotion gate |
| Evaluating, judging | **Evaluator — outside, unreachable** | Produces Claims | Sealed set |
| Integrations, communication (MCP/ACP/HTTP) | Protocol adapter | Tool schemas | Trust level |

Every one lands. **Not a single item requires a new architectural layer.** That is the decoupling answer: you do not leave "room" by adding extension points, you leave room by having a reduction general enough that new capability arrives as an adapter, an artifact, or a number — and v4's `C-01`/`C-02` are exactly the claims that assert this, which means they are testable on day one rather than aspirational.

---

## 4. Where to start typing — the first ninety days, five tracks concurrent

### Week 0–2 · Write the ledger of a run you do *by hand*

Before any schema, fix a real bug in a real repository manually, and **record it as events by hand** — every observation, every proposal, every effect, every receipt, every judgement. Two engineers, three bugs, a text file.

This is the single most valuable two weeks in the programme, and it is what v4 skipped. It forces the schema to be **descriptive of something that happened** rather than aspirational about something imagined. Every field that turns out unfillable dies. Every field you find yourself needing gets added. You will discover that half of `04` is real and half was invented, and you will discover which half in a fortnight rather than in year two.

Then, and only then, write the schemas. One authoritative language, plus a **reader-only** implementation in a second language — that gets you the contract-independence test at a fraction of full cross-language conformance cost.

### Week 2–6 · The walking skeleton, with no model in it

```
packages/
  domain/        pure types + reducers, zero I/O
  ports/         interfaces only — Model, Environment, Store, Index, Evaluator
  kernel/        capability grants, attenuation, budget leases, dispatch
  ledger/        transactional event store, projections, recording
  agency/        the episode engine, context compiler, operator invocation
  adapters/      fake-model, shell, git, filesystem, local-store
  runtime/       composition root
  cli/
lab/             offline; consumes exported artifacts only
```

Run a *scripted* trajectory — a fixed list of proposals with no LLM anywhere. Prove: denial by resource scope, child attenuation, budget lease exhaustion, event atomicity, recovery from `kill -9` with uncertainty preserved, evaluator unreachable, secret non-disclosure.

**No model in the loop, deliberately.** A model's plausibility masks a broken boundary — you will watch it "work" and learn nothing. This is v4's Increment A and it is the correct instinct.

### Week 6–12 · First real bug, and the instrument alongside it

Add one provider, git, patch/search/shell/test, the artifact graph schema, `CorrectionRecord`. Fix the same three bugs the humans fixed in week 0 and diff the trajectories — you now have a paired comparison against a human baseline before you have any benchmark at all.

**Concurrently, not afterwards** (this is where I revise my earlier sequencing): the instrument track builds the A/A floor and paired runner; the generality track prototypes one non-coding environment as a pure contract-falsifier. If the second environment forces an episode-engine change, you have found it in month three for the cost of weeks instead of in year two for the cost of the programme.

---

## 5. The five decoupling rules — enforced in CI, not documented

These are what keep it from becoming coupled. Each is a build gate, not a convention.

1. **Dependency direction is a compile error.** `domain ← ports ← kernel ← agency ← runtime → adapters`. `lab/` imports nothing and is imported by nothing. A cyclic import fails the build.
2. **Two implementations per port from day one.** Fake and real. A contract satisfied by one implementation is an implementation wearing an interface. This is also your entire test strategy.
3. **The loop knows no cognitive vocabulary.** Grep the `agency/` package for "plan", "debug", "reflect", "architect" — if any appear as identifiers rather than as data, cognition has leaked into the engine. Make it a lint rule.
4. **No adapter imports another adapter.** Composition happens only at the root.
5. **No special cases.** A conditional naming one provider, one environment, or one task type is the generality constraint failing quietly, and it always arrives disguised as pragmatism. This is the review item everyone skips and it is the one that decides whether the coding harness is a *first environment* or *the ontology*.

**Performance, since you asked:** orchestration is microseconds against seconds of inference, so the kernel language is irrelevant and the two-clock split is everything. Fast path — local context compile, streaming, cached exact grants, batched appends with crash safety, smallest relevant check first. Slow path — evaluation, consolidation, clustering, promotion, ablation. Carry margins the way you carry KG and power margin: TCB size, p95 first-token, p95 first-effect, context tokens, schema extension slack. Each with an **alarm, not a limit** — a margin nobody watches is a margin already spent.

---

## 6. How the MVP grows itself

The MVP is not a small version of the final system. It is the **first turn of the flywheel that produces the final system**, and the flywheel has exactly four stages:

**Stage 1 — the ledger accumulates.** Every episode, receipt, verdict, and correction delta. No learning yet. You are building a corpus, and the corpus is the asset. This is why the schema is the keel: everything downstream reads it.

**Stage 2 — the corpus becomes attributable.** Once the artifact graph is populated and counterfactual re-execution works, you can ask *which component caused this* and get an answer. Attribution is what turns a log into evidence.

**Stage 3 — attribution becomes proposal.** The offline optimiser clusters failure modes and proposes Tier-1 edits, each with a declared prediction. Predictions verified against next-round outcomes give you the progressive-vs-degenerating ratio — a real measure of whether the loop is learning or accommodating.

**Stage 4 — proposal becomes structure.** When plateau arrives — and plateau is the observable form of *"my representation is inadequate"* — the system proposes a representation it was not given. That is the only interesting question in the programme, and everything before it exists to make it askable.

**Emergence enters at stage 4, not stage 1**, and it enters through the recursion of §2: the hierarchy you want (agents → teams → sectors) is not built, it is *discovered* as the composition depth that survives evaluation on task classes that need it. If depth-3 composition never beats depth-1 on any task class, you have learned something real and expensive about your thesis — and you will have learned it from the ledger rather than from an argument.

**Start Monday with the hand-written ledger.** Not the schema, not the repository, not the document. Three bugs, two engineers, one text file recording what actually happened. Everything else in this programme is downstream of having an honest record of one real run, and you currently have zero.