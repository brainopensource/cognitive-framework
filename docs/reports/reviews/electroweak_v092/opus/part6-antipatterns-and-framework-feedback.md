# Part VI — Anti-Patterns, and Vanguard as a Framework

Two sections. §1 is what *not* to do — including several things currently proposed in the `.draft`
corpus and the peer reports. §2 assesses Vanguard's standing as a framework for building agents,
which is the project's actual stated ambition and deserves separate judgement from the coding-agent
product.

---

## 1. Anti-patterns

Ordered by how much damage they would do from here.

### N1 — Do not build the outer loop before the inner loop works

**Why it is tempting.** It is the most intellectually interesting layer, the peer corpus specifies
it well, and it addresses a real gap.

**Why it is wrong now.** Sequencing, supervision, and cross-episode memory are *multipliers* on the
inner loop's success probability. `NO_PATCH` 27/27 is the thing being multiplied. A Director that
correctly sequences 20 packages, each executed by a harness that cannot patch a file, delivers
nothing and costs two weeks.

There is also an attribution trap: build both at once and no later measurement can tell you which
change mattered.

**What to do instead.** Sprints 1–3, then the peer plan verbatim. The peer plan is good; it is
early.

### N2 — Do not add capability by prompt

Every line in `system-prompt.txt` describing what the agent *cannot* do is a capability gap wearing
prompt clothing. Roughly 60% of the current prompt is that. The instinct — "the model keeps trying
to `ls`, so tell it there is no `ls`" — inverts the fix. **Add `ls`.**

The same instinct produced "Exactly ONE tool call per turn" (a throughput cap sold as discipline)
and the greenfield/brownfield branch in the prompt (repo-shape detection that belongs in a tool).

### N3 — Do not constrain the action space to compensate for a weak model

`derive_phase` is the canonical instance. It forbids running the test suite before editing —
denying the single most reliable brownfield strategy — in order to stop a weak model from
monologuing.

**The general rule: control outcomes, not paths.** `AdmissionGate` is the right shape; a phase
ladder is prior restraint. Prior restraint has a specific and expensive failure mode: it caps your
best model to protect against your worst, and the cap is invisible in your metrics because you
never measure what the strong model *would* have done.

### N4 — Do not ship eight pathologies at once

The `CONDUCTOR` pathology vocabulary is well designed and the closed-set discipline is right. But
eight detectors × eight interventions shipped together is 64 untested interaction pairs, and if the
suite moves you will not know which pair moved it. If it moves *down*, you will not know which to
revert.

**Ship one. Measure it. Then the second.** `THRASHING` first — most frequent, cheapest to detect,
cheapest to treat.

### N5 — Do not build embeddings or a vector store

Explicit recommendation against the obvious move. Code identity is exact, code relations are typed,
and chunk boundaries destroy the structure that carries the meaning. You have 77,610 typed relations
computed and sitting on disk. Replacing structural retrieval with cosine similarity would be
replacing an asset with a downgrade — and it would fork the memory layer, which the anti-sprawl
rules already forbid.

### N6 — Do not fork LDA; do not build a second index

Adopting the peer report's warning verbatim, because it is correct. `Compactor.retrieve()`,
`IndexPort`, and any future memory retrieval must all resolve to the *same* LDA-backed store. Two
retrieval systems is the exact sprawl `AGENTS.md` prohibits, and it splits the one asset that
compounds.

### N7 — Do not add a fourth graph

Three graphs are legitimate: the **code graph** (projection), the **causal graph** (the ledger,
authoritative), and the **composition graph** (declaration). A fourth — a workflow DAG declaring
the order of work before the work runs — is what `spec.md`'s loop-over-DAG clause forbids.
`derive_phase` is a three-node instance already in the tree. Do not grow it, and do not let a
"topology language" become it.

### N8 — Do not keep forks to preserve optionality

Thirty-two manifests, three engines, three patchers, fifty n=1 reports. Each was kept because it
*might* have been better. None can be checked, so all are kept, so the set only grows.

The counter-intuitive part, worth restating: **deleting the forks is not the fix.** Without the
instrument they regrow within a month, for the same rational reason they appeared. Build
`bench compare` (Sprint 3) and the forks become cheap to delete because the data does it.

### N9 — Do not commit debugging runs as evidence

`report_v3a` through `report_v3j`, `_fix3/4/5`, `_final/final2/final3`. Each is one interactive
debugging run frozen into the evidence tree. The cost is not disk; it is that `benchmarks/` becomes
unsearchable and every aggregate over it is dominated by noise — which is why Part 1 §1.1 required
a script rather than a glance.

Logs go to `.vanguard/` and are gitignored. Measurements go to one `results.jsonl`. Trajectories go
to the ledger and the blob store, content-addressed.

### N10 — Do not let documentation absorb the effort the agent needs

Fifty of two hundred commits are docs. Nine rework board structure. Five commits are labelled `fix`;
one is labelled `test`.

Documentation is tractable and the agent is not, so effort flows to documentation. The
`check_doc_budgets.py` 200-line limit shows someone recognised this and answered it with a linter
while `technical.md` grew to 5,575 lines routing around it. **A linter cannot fix a priority
problem.**

### N11 — Do not treat mechanism presence as capability

The project *states* this rule better than almost anyone ("mechanism presence is not milestone
acceptance") and then the README's capability table says "**Works.**" in eleven rows while the
flagship benchmark returns `NO_PATCH` 27/27.

Both are defensible in isolation: the mechanisms *do* work; the product does not. But a reader
cannot tell, and neither can a coding agent reading the README as context. One honest number at the
top of the README (Sprint 0.7) resolves it.

### N12 — Do not optimise against a cheap model only

Every live artifact in Part 1 was produced on tier-1/tier-2 models with a 1K output cap. This
creates an unresolvable confound between harness defects and model incapacity — and it selects for
prompt hand-holding over capability, because hand-holding is what helps a weak model.

Keep the tiering for economy. But **validate every architectural decision on a frontier model at
least once** (Sprint 3.5). Two numbers, reported separately: the harness's *quality* (best model)
and its *economy* (cheap model).

### N13 — Do not conflate `undeterminable` with failure, or with success

This one is a compliment shaped like a warning. `undeterminable` as a first-class disposition is the
project's best epistemic instrument, and its danger is drift in both directions: used too readily it
becomes a way to avoid negative results; used too rarely and a broken instrument gets scored as a
task failure (which is exactly what the 9.5% number is).

The rule that keeps it honest: **`undeterminable` describes the instrument, never the subject.** If
the harness terminated at turn 1 because `finish` was unreachable, that is `undeterminable`, not
`fail`. If the agent produced a wrong patch, that is `fail`, not `undeterminable`.

---

## 2. Vanguard as a framework for building agents

The project's stated ambition (`VISION.md` Ch. 1) is a *general agentic computation substrate*, of
which the coding agent is the first manifestation. That deserves judgement on its own terms.

### 2.1 What Vanguard does better than the field

Assessed against what agent frameworks generally provide:

| Property | Field norm | Vanguard |
|---|---|---|
| State model | in-memory objects; transcript is the state | **`State = fold(events)`**, cold replay, process-independent continuation |
| Effect mediation | tool functions called directly | **typed effects through a 13-stage dispatch with descriptor-bound grants** |
| Privilege | ambient — the agent has what the process has | **monotonic attenuation**; a child cannot exceed its parent |
| Budgets | token counter, maybe a cost cap | **typed multi-dimensional algebra** (usd, millis, tokens, bytes, turns, depth) with reservation and conservation |
| Auditability | logs | **intent-before-effect, receipt-after, provenance DAG, digest-linked** |
| Verification | the agent grades itself | **exterior evaluator, separate UID, signed verdicts, unimportable from cognition** |
| Reproducibility | "set temperature=0" | **explicit replay/re-execution distinction**, computed multidimensional reproducibility vector |
| Extension | plugins with ambient access | **two-tier packs/adapters over ports, JSON-Schema + JCS narrow waist** |
| Domain neutrality | framework knows about "chat", "tools", "RAG" | **kernel is domain-blind, linter-enforced** |
| Epistemics | benchmark numbers | **`undeterminable`, must-fail falsifiers, invalidated own baseline** |

Every row is a genuine differentiator. Several are unavailable anywhere else at all. **The
substrate is not the problem and should not be rebuilt.**

### 2.2 What Vanguard does worse than the field

| Property | Field norm | Vanguard |
|---|---|---|
| Tool surface | 15–25 verbs, parallel | **5 verbs, one per turn** |
| Edit primitive | exact-match replace | unified diff + 504 LOC of recovery |
| Code retrieval | grep + glob + read | 5 regexes (while owning a 77k-edge graph) |
| Prompt caching | standard | prefix built, breakpoints never sent |
| Time-to-first-agent | minutes | 32 manifests, 12 component files, no inheritance |
| Measured pass rate | published | **undetermined** |
| Docs-to-capability ratio | — | 59k lines : 79-LOC product |

The second table is entirely *inner-loop and instrumentation*. Not one row is an architectural
defect. That is the review's central finding restated: **AETHER is a strong framework carrying a
weak harness.**

### 2.3 The framework's actual gap: authoring cost

For "build any agent on this substrate" to be true, building a *second* agent must be cheap. Today:

- 32 manifests exist because there is no inheritance (Part 3 §13.2).
- Each preset re-specifies twelve component paths, so a one-variable change is a twelve-line diff.
- The tool surface is per-pack rather than shared, so a new agent starts from zero tools.
- `apps/` is 79 LOC, so there is no worked example of an application over the runtime.
- `vg-research-minimal`, `vg-tutor-*`, `vg-table-default` exist as presets with no measured
  outcomes — evidence that non-coding agents were *attempted* and never validated.

**What would make it real:**

1. **`extends` / `overrides` in manifests** (Sprint 3.8). Turns a preset into a delta.
2. **`packs/shared/tools/`.** A new agent inherits `read`, `glob`, `grep`, `bash`, `finish` for free
   and declares only what is special.
3. **One non-coding reference agent, measured.** The 1.0 horizon already names "two non-coding
   reference agents"; the requirement should be *measured on a frozen suite*, not merely present.
   A research agent with `fetch`/`search`/`cite` and a citation-accuracy oracle would falsify or
   confirm the generality claim honestly — which is what `M-5b` is *for*.
4. **A quickstart that actually works.** "New agent in 20 lines" as a tested example under `apps/`.
   Today `CodingMaxFacade` is the only worked example and it is a thin wrapper with no counterpart.

### 2.4 On the generality claim

`VISION.md` Ch. 11 gets the epistemics exactly right: *M-5b does not create generality, it tries to
falsify it.* The `packs/formal-sat/` and `packs/formal-graph-coloring/` packs are the right
instrument — deterministic witnesses, strong oracles, minimal evaluation ambiguity.

One caution about *when*. Testing generality with a coding agent at an undetermined pass rate risks
a misattributed result: if the formal pack fails, you cannot tell whether the abstraction leaked or
the shared inner loop is simply weak. **Falsify generality after Sprint 3**, when the coding agent's
number is known and can serve as the control it was meant to be. `ADR-0102` already establishes that
an invalid control invalidates the experiment; this is the same principle applied one level up.

### 2.5 The strategic identity question

`README.md` opens with: *"AETHER is a general event-sourced agentic computation framework and
experimental substrate."* True, and — for now — the wrong lead.

Nobody adopts a substrate. They adopt a tool that works, and then discover it rests on a substrate.
The order in which value becomes legible is:

```
a coding agent that works
  → "how does it recover from a crash mid-run?"   → the ledger becomes interesting
  → "how do I stop it running arbitrary commands?" → the kernel becomes interesting
  → "how do I prove this configuration is better?" → the trajectory store becomes interesting
  → "can I build a research agent on this?"        → the substrate becomes the product
```

The substrate is the *durable* value and the coding agent is the *legible* value. Right now the
README leads with the durable one and the legible one returns `NO_PATCH` 27/27. **Lead with Coding
Max once it works, and let the substrate be the reason it is trustworthy** — which is the honest
version of the same claim and a far stronger one.

There is a second, quieter identity asset worth naming. The trajectory store plus paired evaluation
plus replay-with-substitution makes AETHER a genuinely credible **laboratory for agentic systems** —
`VISION.md` Ch. 9's claim, which I think is correct and under-sold. Almost no one can run a
controlled ablation on an agent with an *identical* prefix history. That is a research contribution
independent of whether Coding Max ever wins a benchmark. It is also entirely blocked on Sprint 3.

---

## 3. Closing assessment

**What this project has that is rare:** an event-sourced substrate that actually works, a
domain-blind kernel with a real correctness bound, an exterior evaluator that cognition cannot
reach, a 77,610-edge code graph, a correct cache-stable context compiler, paired-evaluation
statistics, and — most unusually — the intellectual honesty to invalidate its own baseline and
publish `undeterminable`.

**What it has that is costly:** five tools, one call per turn, no directory listing, no shell, an
edit primitive the model cannot emit, a 77,610-edge graph pointed at the developer instead of the
agent, cache breakpoints computed and never sent, 32 unfalsifiable presets, three loops in a
one-loop architecture, and 59,000 lines of documentation certifying that nothing has been proven.

**The relationship between those two lists is the whole finding.** The rigor was aimed at governing
the work instead of at the agent's capability surface. That is a correctable allocation error, not
an architectural one — which is the good news, and the reason this review recommends five weeks of
wiring rather than a rewrite.

The instinct that produced ADR-0102 — invalidating your own control because the evidence demanded
it — is the same instinct that will fix this, once it is pointed at the tool surface instead of at
the constitution.

**Build the thing. Let the ledger prove it worked. Then write the law.**
