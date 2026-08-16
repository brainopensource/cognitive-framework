# 004 — Cognition, Competence & Self-Improvement: from theory to practice

**Status:** NON-NORMATIVE. Where this file and a v4 owner disagree, the owner wins (`PR-3`).
**Date:** 2026-08-16 · **Branch/HEAD:** `sprints7-8/integration` @ `0238b1a`
**Owns:** the gap between the cognitive theory in `VG-02/03/06/07/12` and the code; the minimum
viable competence machinery; the sequencing that avoids premature formalisation; the scientific
grounding for each mechanism.
**Authority cited:** `VG-02 §1 §5 §11`, `VG-03 §5 §10 §11`, `VG-06`, `VG-07`, `GTS-13C` Ch. 3
(`O-01`…`O-11`), Ch. 11, Ch. 12, `ADR-0015`…`ADR-0018`.

---

## 1. The gap, stated precisely

`VG-02 §1` defines the persistent object of the entire programme:

$$S_t = (G_C,\; G_E,\; L,\; A_t)$$

$G_C$ immutable competence graph · $G_E$ graph of claims, evaluations and invalidations ·
$L$ ledger of episodes, effects and lineage · $A_t$ activation set valid for the current context.

**Implementation status:**

| Term | Code | Assessment |
|---|---|---|
| $L$ | `domain/ledger/` (1,188 LOC) + `adapters/stores/` + `runtime/ledger/` | **Real and good.** Events, reducer, state, reconciliation, projections, recovery |
| $G_C$ | `competence_claim` is a **string in a tuple** at `domain/artifacts/graph.py:18` | **Absent.** No node, edge, lineage, supersession, or forgetting-as-competition |
| $G_E$ | `schemas/v4/evidence-claim.schema.json` only | **Absent in code.** No `Claim` type, no store, no invalidation evaluation, no demotion |
| $A_t$ | zero occurrences outside prose | **Absent.** The loop takes no activation set |

Three of four terms of the project's defining formalism are unimplemented. Everything downstream
of them — operators-as-data (`A-02`, `L-3`), playbooks (`VG-03 §11`), the improvement relation
(`L-4`), promotion/demotion (`VG-06 §5`), the offline optimiser (`GTS-13C` Ch. 11 stage 3) —
therefore does not exist either.

**This is not a criticism of sequencing.** `O-01` explicitly says: design the competence-graph
lifecycle *when one distilled artifact clears the A/A floor* — **"derive the lifecycle from the
survivor, not before it."** That instruction is correct and should be obeyed. The problem is
narrower and more urgent:

> **The A/A floor does not exist either (`002 §4`), so the trigger for `O-01` can never fire.
> The programme is blocked on a measurement it has not built, while building abstractions that
> the measurement was supposed to license.**

That is the real strategic finding of this document. The unblock is measurement, not cognition.

---

## 2. What must be built now, what must wait, and why

`VG-02 §8` carries the standing warning: *"premature formalisation is indistinguishable from
rigor at the moment of the decision. Ask of every plan: how many things must be simultaneously
correct before the first feedback signal?"*

Applying that test honestly:

| Mechanism | Things that must be simultaneously correct before feedback | Verdict |
|---|---|---|
| A/A floor | A/A runner, a manifest, a task class, a refusing scorer | **4 — build now** |
| Recursion + context isolation | spawn, child lease, isolation, one measurement | **4 — build now** |
| `Claim` as a real type with invalidation | schema (exists), type, store, a scheduled evaluator | **4 — build now (thin)** |
| Operator registry as data | operator schema, registry, selection policy, activation set, invocation, budget shape, output contract, an operator worth selecting | **8 — wait** |
| Playbook engine + rigidity dial | operator machinery + phases + gates + masking + distillation + promotion | **12+ — wait** |
| Competence graph $G_C$ | all of the above + lineage + supersession + activation topology + demotion | **15+ — wait for `O-01`** |
| Offline optimiser | all of the above + corpus + attribution + counterfactual re-execution | **20+ — wait** |

**Build now: the floor, recursion, and the thinnest possible $G_E$.** Everything else waits for
its trigger. The discipline of `O-01`…`O-11` is one of the corpus's best features and the plans
in `docs/superpowers/` quietly abandon it.

---

## 3. The thinnest useful $G_E$ — and why it cannot wait

$G_E$ (claims, evaluations, invalidations) is the one competence structure that must exist
*before* the corpus, not after, because **it is the format the corpus is recorded in**. `L-1`
lists trajectory, event and competence schemas as irreversible: *"Changing it means re-running
everything ever recorded."*

`T4.11` makes the same argument for the competence estimate: *"Nothing consumes it yet;
recording it now costs nothing and retrofitting it later costs a corpus migration."* That
instruction was followed — `CompetencePriorRecorder` exists at `agency/context/compiler.py:243`
and emits `CompetencePriorRecorded` before turn 1, with digests rather than prompt text. Good.

The same argument applies to `Claim` and it was **not** followed. Minimum viable $G_E$:

```python
# domain/evidence/claim.py  — NEW, pure, no I/O
@dataclass(frozen=True, slots=True)
class Claim:
    subject: ArtifactRef            # what is claimed about
    predicate: str                  # scoped: "resolves(task_class=X, manifest=D)"
    value: Any
    protocol: EvaluationProtocolRef # how it was measured
    evaluator: EvaluatorId          # who measured it — never "the system"
    environment_profile: Digest
    substrate_profile: Digest       # model, version, sampling
    uncertainty: Interval           # never a point estimate
    validity: ValidityWindow
    invalidation_conditions: tuple[InvalidationCondition, ...]   # minItems=1, at parse
```

Three properties are load-bearing and each is already specified:

1. **`invalidation_conditions` non-empty, enforced at parse** (`ADR-0018`, `INV-1`, `L-04`).
   `GTS-13C` T1.9 calls this *"the best single decision in the corpus."* The schema already
   enforces it (`schemas/v4/vectors/evidence-claim/invalid/empty-invalidation.json` exists).
   The Python type must too.
2. **At least one condition must be automatic** (`INV-2`, `ADR-0042`, `C-12`). A wholly manual
   set satisfies `INV-1` and still fails `C-12` — staleness discovered only by human review.
   The canonical automatic condition here is *substrate change*: `substrate_profile` digest
   differs ⇒ the claim is stale. That is one line, and it makes `C-09` measurable.
3. **No unscoped claim** (`N-11`, `VG-06`). `predicate` carries its scope in its structure, so
   a claim cannot be silently generalised. `T1.10`'s `CorrectionRecord.scope` makes the same
   point for corrections: *"style and preference corrections are user/team/repo-scoped and may
   never become general competence."*

**Cost:** ~200 LOC of pure `domain/` code plus a store. **Benefit:** every run from that day
forward records evidence in the final format, and the `O-01` trigger becomes evaluable rather
than hypothetical.

---

## 4. Memory and competence accumulation — what the 2026 literature changed

This is where the specification is strong and where the field has moved *toward* us, with one
important correction.

### 4.1 The field validated the shape

Skill-library accumulation on frozen weights (the Voyager line) is now mainstream: agents
accumulate reusable procedural knowledge without weight updates via an ever-growing library plus
retrieval. ([Voyager](https://arxiv.org/html/2305.16291),
[Adaptation of Agentic AI: post-training, memory, skills](https://arxiv.org/pdf/2512.16301))

### 4.2 The field discovered the failure mode we predicted — and named it

**Library drift** is now a documented, distinct failure mode of persistent cross-task memory:
accumulated artifacts *degrade* future performance through a retrieval bottleneck. It is
explicitly described as the frozen-weight counterpart to catastrophic forgetting — persistent
skill artifacts replace neural weights as the degradation substrate.
([Library Drift](https://arxiv.org/html/2605.19576v1))

Separately: *"All existing frameworks measure self-evolution solely by forward progress on new
tasks, without asking whether adaptation preserves competence on previously mastered ones."*
Capability degradation is reported as a **consistent, structural** failure across all four
dimensions of self-evolution. ([Do Self-Evolving Agents Forget?](https://arxiv.org/html/2605.09315v1))

`VG-02 RSK-12` predicted exactly this: *"Competence ossification — the library encodes
workarounds for weaknesses that no longer exist."* `RSK-03` predicted memory poisoning.
`ADR-0017` predicted that an array cannot express contradiction, partial supersession or
lineage-preserving forgetting. **The corpus called it. That is a real credit to the design work
and it should be said out loud.**

### 4.3 The correction the literature forces on us

The proposed mitigation in the literature is **evidence-gated memory preservation**: memory
entries accumulate *stability* through repeated self-verified support over time; historically
reliable memories are protected from destructive rewrite or eviction, while low-evidence entries
stay adaptable.

Our design has the *gating* (verifier-gated promotion, `VG-06 §5`) but does **not** currently
have an explicit **stability/protection axis** — an artifact in our design is active or not, and
demotion is driven by staleness and invalidation. The literature's finding is that eviction and
rewrite pressure damage *high-evidence* entries first, because they are the oldest and the most
frequently retrieved-around.

**Recommendation — one field, added now, consumed later:**

> Add `support_count` and `last_corroborated_at` to `Claim`, and a `protection_class` derived
> from them. Nothing consumes them in v0.4.3. Recording them now costs nothing and retrofitting
> them later costs a corpus migration — the identical argument `T4.11` already accepted for the
> competence prior.

This is the cheapest possible hedge against the one failure mode the 2026 literature says is
structural.

### 4.4 What we must *not* import

`VG-02 §11.11` and `L-14`: biological and cosmological analogies are non-normative.
`GTS-13C` Ch. 12 gives the test — *does the import predict something about our system's
behaviour that could turn out false?* Applied:

| Import | Legitimate form | Illegitimate form present in our plans |
|---|---|---|
| CLS / hippocampal consolidation | Fast episodic store + slow consolidated store, offline interleaved replay, forgetting as competition — each makes a falsifiable prediction | "The event store is a hippocampus" |
| Cellular hierarchy | **Depth labels applied by the trace viewer after a run** | **`Atom → Molecule → Cell → Body → Biome` as a class hierarchy to build** — present in `docs/superpowers/plans/2026-08-16-phase-3-sprints-7-10-blueprint.md` §2 and partially built in `runtime/coordination.py` |
| Evolutionary computation | Pareto/QD archives, diversity as insurance, the failure of scalar fitness (`ADR-0015`) | "Evolution guarantees progress" |
| Metacognition | Pre-action prior scored post-hoc; Brier score alertable (**implemented**) | "The system knows itself" |

The `Atom/Molecule/Cell/Body/Biome` hierarchy is the live violation. `GTS-13C §4.3` is
unambiguous: *"Build the classes and you have hand-authored the hierarchy you claimed would
emerge… Nature did not implement `class Cell`; it implemented a replicator under selection and
let scale happen."* Delete the hierarchy from the plans (`008 §2`) and let depth be an integer
that a projection labels.

---

## 5. Context engineering — the largest cost lever, half built

`VG-03 §10` calls context engineering *"the actual quality bottleneck, and the largest cost lever
in the system."* The 2026 numbers agree emphatically: context editing alone delivers **29%**
performance lift; on a 100-turn eval it cut tokens **84%**; subagent context isolation
outperformed a single-agent baseline by **90.2%** on an internal research eval.

### 5.1 What is built and correct

`agency/context/compiler.py` (316 LOC) is high quality:

- L1–L3 frozen **at construction**, so prefix stability is a property of the type rather than of
  every call site — the docstring's reasoning at lines 12-18 is exactly right.
- Breakpoints only on L1/L3/L4; **L5 never carries one** (`VG-03 §10.2`).
- `CacheBreakpointCeilingExceeded` raises **at assembly**, not from later telemetry.
- `ContextBudgetExceeded` when the incompressible floor exceeds the window — refusing rather
  than silently over-sending, with an explicit `M6` citation.
- `result_eviction` leaves a receipt (`_receipt_for`), so the operator cannot re-issue the same
  read forever.
- The brief is compaction-exempt (`VG-03 §10.5`, `N-21`, `FT-11`).

### 5.2 What is missing

| `VG-03 §10.3` strategy | Status |
|---|---|
| `recency_window` | **Declared in every manifest, not implemented** (`005 §3`) |
| `result_eviction` | ✅ implemented, and it is the default |
| `model_summarize` | ❌ |
| `structured_consolidate` — *"lowest measured; the recommended default"* | ❌ |
| `operator_isolation` — *"the primary mechanism"* | ❌ (requires recursion, `003 §3`) |

Two consequences:

1. **Strategies are not pluggable, so the comparison the system exists to run cannot be run.**
   `VG-03 §10.3` says the point of making them pluggable is that *"which compaction strategy is
   better"* is exactly the one-variable question. Today there is one strategy and a decorative
   manifest field naming a different one.
2. **`StructuredRecord` (`VG-03 §10.4`) is unimplemented**, and it is the one with `deadEnds` —
   which `VG-03` singles out because *"an agent re-exploring an approach it already abandoned is
   among the most common and most expensive long-horizon failures."* The 2026 compaction
   literature (progressive compaction ladders, trajectory-grounded compaction validation)
   converges on the same structured approach.
   ([Slipstream](https://arxiv.org/pdf/2605.08580), [CompactionRL](https://arxiv.org/pdf/2607.05378),
   [Self-Compacting Language Model Agents](https://arxiv.org/pdf/2606.23525))

### 5.3 Also missing: periodic re-grounding

`VG-03 §10.5` calls re-grounding *"the highest-value scheduled interrupt in a long run"* and
`VG-03 §6.1` shows it in the loop with a careful note that it is an **observation effect,
authorised like any other** — not a privileged side channel. `regroundPolicy` does not exist in
`engine.py`. This is ~30 lines and it is the cheapest defence against `FT-11` goal drift and
silent error compounding.

### 5.4 Recommendation

| # | Item | Effort |
|---|---|---|
| C1 | `CompactionStrategy` protocol in `ports/`; register `result_eviction` + `recency_window`; select by `context_policy` | 3 d |
| C2 | `structured_consolidate` emitting `StructuredRecord` incl. `deadEnds` | 1 wk |
| C3 | Consolidation quality measurement: replace transcript with record, re-run, compare (`VG-03 §10.4` — *"that is a number, not an opinion"*) | 3 d |
| C4 | `regroundPolicy` as an authorised observation effect | 2 d |
| C5 | `operator_isolation` — falls out of recursion (`003 §3.4`) | — |
| C6 | Prefix-stability as a monitored CI metric over a fixed replay (`VG-03 §10.2`) | 2 d |

C1 and C6 are prerequisites for *any* harness comparison. C2/C3 are the highest-value cognitive
investment available, and unlike the competence graph they need no corpus to be worth building.

---

## 6. Self-improvement: the pipeline, and where to stop

`GTS-13C` Ch. 11 gives four stages. Honest placement today:

| Stage | Requirement | Status |
|---|---|---|
| 1. The ledger accumulates | Episodes, effects, receipts, verdicts, corrections | **Partially.** Ledger real; corrections not captured in a merge path (`T6.7`); a large share of runs bypassed it entirely (`002`) |
| 2. The corpus becomes attributable | Artifact graph populated + counterfactual re-execution | **No.** `Recording` (`T1.11`) has a schema but no `RandomPort`/complete `ClockPort`, so replay is state reconstruction, not counterfactual re-execution |
| 3. Attribution becomes proposal | Offline optimiser clusters failures, proposes Tier-1 edits **with a declared prediction** | **No**, and correctly so |
| 4. Proposal becomes structure | At plateau, propose a representation not given | **No**, and must not be attempted |

**Stage 2 is the true frontier of this programme, and it is blocked on two small ports.**
`RandomPort` and a determinism-complete `ClockPort` are perhaps 150 LOC together. Without them,
"which component caused this?" is unanswerable, and stage 3 — the progressive-vs-degenerating
ratio, which is the actual measure of whether the loop is learning — cannot be computed at all.

That ratio, incidentally, is the concrete operationalisation of the Lakatos import in Ch. 12,
and it is the single most defensible scientific claim the project could make. It is two ports
and an A/A floor away, not a research programme away.

### 6.1 Safety of the self-improvement loop

The 2026 literature on self-evolving systems is blunt about compounding risk: threats amplify
through the evolution loop itself, and evaluation integrity is the primary control surface.
([Safety in Self-Evolving LLM Agent Systems](https://arxiv.org/pdf/2606.23075))

Our design's answers — `ADR-0019` (release pipeline, never in-place), `L-05` (promotion moves a
pointer), `L-06` (rollback tested before the promotion it protects), `O-07` (never autonomous
for kernel or evaluator), `RSK-08` — are correct and ahead of the field. **One is currently
violated:** `meta_loop.py` closes the observe→act→grade→act loop inside a single process with
no boundary (`001 §3.1`, `003 §2.1`). That is the shape the safety literature warns about, and
deleting it restores the property.

---

## 7. Honest limits worth re-stating to stakeholders

`VG-02 §11` is the most valuable page in the corpus and deserves to survive the delivery push
unedited. Three items are especially live right now:

1. **"The flywheel is bounded by the evaluator."** Coding is chosen because verification is
   cheap. The 2026 verifier-gaming results (`002 §4.3`) show even cheap verification is gameable
   at 0–13.9% depending on the model's post-training. Our double probe plus isomorphic
   perturbation is a genuine answer; without them the flywheel optimises the oracle.
2. **"Most measured differences will be noise at achievable sample sizes."** With harness-only
   variance measured at 10–20 points in the field, our A/A floor may well be large enough that
   several planned comparisons are underpowered from the start. **Better to learn that from the
   floor than from a published claim** — and `RSK-06` requires the sample size be derived from
   the floor and recorded in the family declaration.
3. **"C-06 may never clear the floor — a genuinely interesting negative result."** The programme
   should be prepared, socially and contractually, to publish that. `VG-02 §11.9` already
   commits to it. Every plan in `docs/superpowers/` implicitly assumes success; none names the
   negative outcome. That asymmetry is how a research programme becomes a demo programme.

---

## 8. Backlog

| # | Item | Trigger | Effort | Note |
|---|---|---|---|---|
| G1 | `Claim` as a `domain/` type, non-empty invalidation at parse, ≥1 automatic condition | **now** (`L-1` format lock) | 3 d | |
| G2 | `support_count` / `last_corroborated_at` / `protection_class` fields, recorded not consumed | **now** | 0.5 d | §4.3 hedge |
| G3 | `RandomPort` + determinism-complete `ClockPort` | **now** | 2 d | unblocks stage 2 |
| G4 | Counterfactual re-execution from `Recording` | after G3 | 1 wk | unblocks attribution |
| G5 | Compaction strategies pluggable + selected by manifest | **now** | 3 d | `005` |
| G6 | `structured_consolidate` + `deadEnds` + consolidation-quality measurement | **now** | 1.5 wk | highest cognitive ROI |
| G7 | `regroundPolicy` as an authorised observation effect | **now** | 2 d | |
| G8 | Operator registry as data, activation set, operator invocation | **`O-03`** — a real task needs depth the current mechanism cannot reach | — | **do not start** |
| G9 | Competence graph $G_C$, promotion/demotion topology | **`O-01`** — one artifact clears the A/A floor | — | **do not start** |
| G10 | Playbooks + rigidity dial | after G8 | — | **do not start** |
| G11 | Offline optimiser, progressive-vs-degenerating ratio | after G4 + floor | — | **do not start** |

The shape of this table is the recommendation: **five small items now, six large items behind
explicit triggers.** The current plans invert that.

---

## Sources

- [Library Drift: Diagnosing and Fixing a Silent Failure Mode in Self-Evolving LLM Skill Libraries](https://arxiv.org/html/2605.19576v1)
- [Do Self-Evolving Agents Forget? Capability Degradation and Preservation in Lifelong LLM Agent Adaptation](https://arxiv.org/html/2605.09315v1)
- [Voyager: An Open-Ended Embodied Agent with Large Language Models](https://arxiv.org/html/2305.16291)
- [Adaptation of Agentic AI: A Survey of Post-Training, Memory, and Skills](https://arxiv.org/pdf/2512.16301)
- [Safety in Self-Evolving LLM Agent Systems: Threats, Amplification, and Case Studies](https://arxiv.org/pdf/2606.23075)
- [Slipstream: Trajectory-Grounded Compaction Validation for Long-Horizon Agents](https://arxiv.org/pdf/2605.08580)
- [CompactionRL: Reinforcement Learning with Context Compaction for Long-Horizon Agents](https://arxiv.org/pdf/2607.05378)
- [Self-Compacting Language Model Agents](https://arxiv.org/pdf/2606.23525)
- [Context Engineering: Agent Reliability Playbook 2026](https://www.digitalapplied.com/blog/context-engineering-agent-reliability-playbook-2026)
