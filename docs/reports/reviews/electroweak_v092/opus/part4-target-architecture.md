# Part IV — Target Architecture

Two questions, answered separately because they have different answers:

1. **If I wrote this from scratch today, what would I build?** (§1–§5)
2. **Given what exists, what is the delta?** (§6–§8)

The short version: the clean-slate design is *the same architecture* with a radically different
mass distribution. Nothing in AETHER's shape is wrong. The investment is in the wrong layers.

---

## 1. The clean-slate design

### 1.1 Mass budget

```
                          target        actual      delta
domain/    values, wire, JCS, reducers      ~3,000    10,139     −7,100
ports/     interfaces                       ~1,200     1,582      ✓
kernel/    S0–S12, attenuation, budget      ~1,500     1,769      ✓
agency/    ONE loop + context engine        ~2,500     9,388     −6,900  (3 loops → 1)
runtime/   compose, session, ledger, resume ~6,000    25,821    −19,800
adapters/  models, sandbox, INDEX, TOOLS   ~14,000    11,703     +2,300  (different contents)
apps/      CLI/TUI facade                   ~1,500        79     +1,400
                                          ───────   ───────
                                           ~29,700    60,497
```

The claim is not that 30k LOC does what 60k does. It is that **the 30k is in the layers that
determine capability**, and roughly half the current 60k is accreted composition machinery in
`runtime/` and forked cognition in `agency/`.

The two numbers that matter most: `adapters/` grows (tools and the real index live there), and
`apps/` grows twentyfold (the product is currently 79 lines).

### 1.2 What is unchanged from AETHER

I want to be unambiguous about this, because the rest of this document is critical and the
foundation is not:

- **Event-sourced ledger, `State = fold(events)`, process-independent continuation.** This is the
  correct substrate for an agentic system and almost nobody has it. Keep the schema as-is —
  envelope digest, `retention_class`, `trainability`, `confidentiality`, `redaction_status` as
  first-class columns is better than most production event stores.
- **The hexagonal lattice and `check_boundaries.py`.** 597 files, enforced per commit, cheap, real.
- **The domain-blind kernel with a LOC ceiling.** The ceiling is not code golf; it is a bound on the
  size of the correctness argument, and the docstrings say so.
- **Capability-mediated effects with monotonic attenuation and typed budgets.** Correct.
- **Intent-before-effect, receipt-after.** Correct and rare.
- **The evaluator outside everything.** "No cognition or adapter module may import the evaluator
  gate." Correct.
- **Execution profiles resolving into `D_R`, fail-closed.** Correct.
- **The L1–L5 prefix-stable context compiler.** Best code in the repository.
- **Cassette recording for deterministic replay.**
- **The falsifier discipline** — every control has a must-fail counterpart.
- **The epistemic vocabulary** — `undeterminable`, "mechanism presence is not acceptance."

### 1.3 What changes

| Change | From | To |
|---|---|---|
| Tool surface | 5 verbs, 1/turn | ~20 verbs, parallel |
| Edit primitive | unified diff | exact-match `str_replace` + `multi_edit` + `ast_patch` |
| Execution | 4-binary argv allowlist | real `bash` in sandbox; allowlist becomes a profile |
| Index | 5 regexes | LDA graph (77,610 relations) behind unchanged `IndexPort` |
| Cache | prefix stable, unmarked | breakpoints emitted; prefix stability under test |
| Tool results | raw into `L5` | distilled at the effect boundary, digest-addressable |
| Compaction | elide to a receipt | summarise, emit `ContextCompacted` |
| Termination | model self-report | postcondition: digest changed ∧ verification passed |
| Phase control | `derive_phase` ladder | deleted |
| Presets | 32 copied manifests | 1 base + inheriting deltas |
| Loops | 3 engines, 3 patchers | 1 engine, 1 patcher |
| Evaluation | ~50 n=1 reports | 1 frozen suite, 1 `results.jsonl`, 1 compare command |
| Supervision | none | separate process tailing the ledger |

---

## 2. The inner loop

```
┌────────────────────────────────────────────────────────────────────────┐
│ EpisodeEngine — the only loop                                          │
│                                                                        │
│  ┌── compile context ──────────────────────────────────────────────┐   │
│  │  L1 soul + operating manual        ┐                            │   │
│  │  L2 tool schemas                    │ frozen at construction     │   │
│  │  L3 repo map (LDA) + AGENTS.md      │ CACHE BREAKPOINT after L3  │   │
│  │  L4 brief (verbatim, pinned)        │                            │   │
│  │     todos · working set · falsified ┘ regenerated, small          │   │
│  │  L5 distilled dialogue, salience-ordered                         │   │
│  └──────────────────────────────────────────────────────────────────┘  │
│              │                                                          │
│              ▼  propose(context, tools, sampling)  → N tool calls       │
│  ┌── dispatch ──────────────────────────────────────────────────────┐  │
│  │  disjoint observation effects → concurrent                        │  │
│  │  privileged / overlapping     → serial                            │  │
│  │  each: Kernel.dispatch S0–S12 → intent → effect → receipt         │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│              │                                                          │
│              ▼  distill(verb, payload) → text + full_digest             │
│              ▼  append to L5 · update working set · fold ProgressVector │
│              │                                                          │
│  ┌── terminate? ────────────────────────────────────────────────────┐  │
│  │  AdmissionGate: workspace_digest changed ∧ VerificationReceipt   │  │
│  │                 .passed (exit 0 ∧ executed_test_count > 0)       │  │
│  │  else → rejection_feedback into L5, continue                      │  │
│  │  budget 70% → rolling handoff → fresh window, same lineage        │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

Five properties worth naming:

1. **No phase gate.** The model chooses the order; the gate checks the outcome.
2. **The brief is verbatim in `L4` and never compacted** (`VG-03 §10.5` — already correct).
3. **`falsified` is pinned**, so a dead end stays dead.
4. **Handoff, not truncation,** at the budget boundary — the run continues in the same lineage.
5. **Every distillation is addressable** — nothing is destroyed, only deferred.

---

## 3. The outer loop

Per Part 3 §11.1, as a **separate process**, not a layer:

```
┌─────────────────┐   spawn      ┌──────────────────────────────────┐
│   Dispatcher    │ ───────────► │  episode  │  episode  │ episode  │
│  (consumes      │              └──────────────────────────────────┘
│   orch.intent)  │                          │ append
└─────────────────┘                          ▼
         ▲                        ┌─────────────────────────┐
         │ append orch.intent.*   │  SQLite-WAL ledger      │
         │                        │  single writer          │
┌─────────────────┐    tail       └─────────────────────────┘
│   Supervisor    │ ◄─────────────────────────┘
│  fold → ProgressVector → Pathology → intent
│  no write tools · no workspace access · kill it and runs continue
└─────────────────┘
```

The supervisor is a pure fold from an event stream to a decision. It is unit-testable with no model
and no episode, against ledgers you already have on disk. It gets crash recovery for free — the
same `RF-25` property, one level up.

---

## 4. The composition model

```
packs/
  code/
    base/                    soul.txt · manual.txt · policies · tool set
    fast/     extends base   { model_tier: 1, max_turns: 15 }
    balanced/ extends base   { model_tier: 2, max_turns: 40 }
    max/      extends base   { model_tier: 3, max_turns: 100, spawn: true }
  shared/tools/              read · glob · grep · symbol · refs · str_replace · bash · finish …
```

Three presets, one base, shared tool definitions. A preset's diff *is* its hypothesis, so an
ablation is a one-line change and `diff` between two presets is readable. This is the mechanical
fix for Part 1 §2.6.

---

## 5. The evaluation instrument

```
benchmarks/
  suite/                  44 content-addressed tasks + oracles   (suite_digest pinned)
  results.jsonl           append-only, one row per config × task × attempt
  bench.py                run · compare · report
```

`bench run <config> --suite <digest>` · `bench compare A B` (paired McNemar) ·
`bench report --since <date>`. One file, one command, one schema. Part 3 §14.

---

## 6. The delta — what to add, what to delete

### 6.1 Add (~4,500 LOC, none in the kernel)

| Component | Home | LOC |
|---|---|---|
| ~15 new tool adapters + schemas | `adapters/tools/` | ~1,200 |
| `LdaRepoIndex(IndexPort)` | `adapters/stores/lda_index.py` | ~400 |
| `ResultDistiller` port + 5 distillers | `ports/`, `adapters/distillers/` | ~500 |
| Cache breakpoints through `ContextBundle` | `domain/`, `agency/`, `adapters/models/` | ~150 |
| Working-set header + `falsified` projection | `agency/context/` | ~250 |
| Rolling handoff | `agency/context/handoff.py` | ~300 |
| Summarise-on-compact + `ContextCompacted` emission | `agency/context/compaction.py` | ~200 |
| Manifest inheritance (`extends`/`overrides`) | `agency/manifests/loader.py` | ~200 |
| Benchmark runner + results schema + compare | `benchmarks/` | ~600 |
| `ProgressVector` reducer | `domain/ledger/progress.py` | ~200 |
| Supervisor process | `apps/supervisor/` | ~300 |
| Parallel dispatch of disjoint effects | `agency/episode/engine.py` | ~200 |

### 6.2 Delete (~12,000 LOC + ~40,000 doc lines)

| Target | Size | Justification |
|---|---|---|
| `agency/forge/` **or** `agency/chimera/` (keep one; fold into `episode/`) | ~4,900 | one loop or the Vision is false |
| `forge/resilient_patcher.py` | 504 | obviated by `str_replace` |
| `episode/tool_policy.py` `derive_phase` ladder | ~80 | prior restraint; D4 |
| 29 of 32 manifests | ~3,000 | delete **by data**, after the suite exists |
| ~50 n=1 `report_*.json` | — | logs committed as measurements |
| `runtime/` composition duplication | ~3,000 | after presets collapse |
| `docs/` governance ceremony | ~40,000 lines | D6 |
| `dist/`, `node_modules/`, `.venv`, `write a function/` from VCS | — | build output and a prompt-named directory are committed |

### 6.3 Net

Roughly **−8,000 LOC of production code, −40,000 lines of docs, +4,500 LOC of capability**, and a
coding agent that can list a directory, find a symbol's callers, edit by exact match, run a shell
command, and issue five reads in one turn.

**Zero lines of `kernel/` change.** Every architectural property the Vision protects survives
intact, which is the strongest available evidence that the architecture was right and the
allocation was wrong.

---

## 7. Why the architecture survives this

Each named property, and why the changes do not touch it:

| Property | Preserved because |
|---|---|
| Domain blindness (I-7) | New verbs are `SinkRegistry` rows; the kernel still names none of them. Deleting `derive_phase` *increases* blindness. |
| TCB ceiling | Nothing added lands in `kernel/`. Headroom is +52 LOC and stays. |
| Loop-over-DAG | Deleting the phase ladder removes the only DAG in the loop. |
| Ledger authority | Distillation is addressable; compaction now *emits* an event where it previously emitted nothing. Provenance improves. |
| Evaluator exteriority | `AdmissionGate` checks a local receipt; the exterior evaluator is untouched and still unimported by cognition. |
| Boundary lattice | Every addition sits in its correct package; `check_boundaries.py` is the acceptance test. |
| Attenuation | `bash` is privileged, descriptor-bound, selector-scoped. More capability under the *same* mediation. |
| Containment | The sandbox becomes the real perimeter instead of a redundant allowlist behind it — the project's own stated doctrine. |
| Honest fallback (T-45) | `LdaRepoIndex` degrades to `FileRepoIndex` with `source_revision`/`index_digest` recorded. Never a silent map. |
| Cache discipline | Strengthened: a docstring invariant becomes a regression test. |
| Falsifiability | Every new control ships with a must-fail counterpart, per existing convention. |

---

## 8. The three properties this buys that few systems have

Worth stating plainly, because they are the reason to do the work rather than start over:

1. **A coding agent whose every action is a typed, authorised, receipted causal fact.** Not a log —
   a replayable record with provenance. Nobody else in this space has this.

2. **Ablation by replay-with-substitution.** Hold a trajectory fixed to turn 11; change one variable;
   re-execute forward. A genuinely controlled experiment on an agent, with an *identical* prefix
   history rather than a similarly-distributed one. This is a research capability, not a feature.

3. **A supervisor that cannot corrupt what it supervises**, because it only reads facts and writes
   proposals — and which survives its own crash by folding the ledger.

All three fall out of the event-sourced design that is already built and already working. They are
currently unreachable only because the agent underneath cannot patch a file.
