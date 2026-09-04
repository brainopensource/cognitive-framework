---
id: arch.meta.conductor
canonical_id: arch.meta.conductor
class: architecture
authority: descriptive
truth_plane: PROPOSED
status: proposed
implementation_status: NOT_STARTED
owner: consolidation-agent
canonical_for:
  - meta-cognitive higher-order orchestration
  - swarm goal algebra (individual vs collective objectives)
  - the pilot framework above AETHER
purpose: >
  Specify CONDUCTOR — a thin meta-framework that pilots AETHER rather than extending it.
  Covers the meta-cognitive control loop, the goal algebra that lets swarm members hold
  individual objectives under a shared global objective, and the topology selection
  problem. Reconciles HYDRA's proposal with what the substrate actually implements.
audience: [architect, release-owner, contributor]
last_verified: "2026-09-02"
relationships:
  - report.draft-synthesis-evidence-audit
  - arch.context.long-horizon-engine
  - arch.outer-loop.orchestrator
  - repo-root-vision
---

# CONDUCTOR — The Piloting Meta-Framework

## 0. Why a second framework rather than a bigger first one

AETHER's identity (`VISION.md`, Law Zero) is *domain-blind bounded execution*: the kernel
must not know what a "coding task" or a "swarm" is. Every capability that needs to *reason
about* execution — "is this plan working?", "should this fan out?", "has this agent won?" —
is therefore structurally homeless inside AETHER. It cannot go in the kernel without
breaking domain blindness (invariant I-7), and putting it in a pack makes it peer to the
things it must supervise.

CONDUCTOR resolves this by being a **separate framework that consumes AETHER as a library**,
never the reverse. The dependency arrow points one way:

```
  CONDUCTOR  (reasons about execution)
      │  spawns, observes, decides
      ▼
   AETHER    (executes, domain-blind)          ← unchanged, unaware of CONDUCTOR
      │
      ▼
   ledger    (facts)  ──────► read back by CONDUCTOR
```

This is also what makes CONDUCTOR testable in isolation: it is a pure function from an event
stream to a decision. No model calls are needed to unit-test its control logic.

## 1. The meta-cognitive loop

AETHER's inner loop is `observe → propose → authorize → effect → receipt → evaluate`.
CONDUCTOR's loop operates on a different object — not *the task*, but *the attempt at the
task*:

```
  measure → diagnose → intervene → re-measure
```

| Stage | Input | Output |
|---|---|---|
| **measure** | ledger events since last checkpoint | `ProgressVector` (§2) |
| **diagnose** | `ProgressVector` + history | `Pathology` or `HEALTHY` (§3) |
| **intervene** | `Pathology` | `Intervention` (§4) |
| **re-measure** | — | did the intervention change the vector? |

The fourth stage is what separates this from a rule engine: an intervention that does not
move the vector is itself evidence, and repeated ineffective intervention is its own
pathology (`INTERVENTION_INEFFECTIVE` → escalate).

## 2. `ProgressVector` — what "is it working?" reduces to

All components are computable from the ledger with no LLM call. This matters: the meta layer
must be cheap enough to run every turn, and must not itself hallucinate.

```python
@dataclass(frozen=True)
class ProgressVector:
    verification_delta: float    # tests passing now − passing at checkpoint   [-1..1]
    novelty: float               # 1 − (repeated action signatures / actions)  [0..1]
    scope_fidelity: float        # |touched ∩ declared| / |touched|            [0..1]
    evidence_freshness: int      # turns since last verification receipt
    budget_burn: float           # spent / allocated                           [0..1]
    convergence: float           # 1 − (distinct failure fingerprints / attempts)
```

Two of these already exist in some form and should be reused, not rebuilt:
`chimera/blackboard.py` tracks verifications and patches; `forge/engine.py` has
`FailureFingerprint`, `NoProgressRule`, `RepeatedFailureRule`. CONDUCTOR's contribution is
*normalising them into one comparable vector* so that policies can be written against a
stable shape and A/B-tested.

`scope_fidelity` is the anti-hallucination workhorse and needs no model judgment: an agent
writing to files outside its declared package boundary is out of scope by definition,
readable straight off `fs.write` effect records.

## 3. Pathologies — a closed vocabulary

A closed set is deliberate. An open-ended "the supervisor decides what's wrong" design is
untestable and drifts. Each pathology is a predicate over `ProgressVector` history.

| Pathology | Predicate (sketch) | Canonical intervention |
|---|---|---|
| `THRASHING` | `novelty < 0.3` over 3 turns | inject falsified-paths block; restrict tools |
| `SCOPE_DRIFT` | `scope_fidelity < 0.8` | hard stop; re-brief with boundary |
| `BLIND` | `evidence_freshness > 3` | force verification before further edits |
| `WON_BUT_UNAWARE` | `verification_delta > 0` ∧ passing ∧ no `finish` | restrict to `{finish, read, search}` |
| `STALLED` | `verification_delta == 0` over 5 turns | escalate model band, or fan out |
| `DIVERGENT` | `convergence < 0.3` | bisect: split into narrower sub-tasks |
| `BUDGET_RISK` | `budget_burn > 0.8` ∧ `verification_delta ≤ 0` | terminate, preserve partial |
| `INTERVENTION_INEFFECTIVE` | 2 interventions, vector unchanged | escalate to human/Director |

`WON_BUT_UNAWARE` is listed third-from-nowhere but is empirically the **most frequent**
failure in this repo: 18 of 26 oracle passes ended `abandoned`
(`SONNET_SUPER_AGENT.md` §2). The merged `_completion_allowed_tools` machinery
(`session.py:1366` → `engine.py:392`) is precisely this intervention, already implemented —
CONDUCTOR generalises it from a hardcoded special case into one entry in a table.

## 4. Interventions — ordered by cost

Cheapest first is a hard rule; a supervisor that reaches for model escalation before trying a
pinned note is burning budget to avoid thinking.

```
0. NOTE            inject a non-evictable block           ~50 tok, 0 calls
1. RESTRICT        narrow the offered tool set             0 tok, 0 calls
2. REBRIEF         rebuild L4 with sharpened goal          ~200 tok
3. ROLLBACK        revert to last green workspace digest   0 calls
4. ESCALATE_BAND   route to a stronger model               $$
5. BISECT          split into 2+ narrower sub-tasks        $$
6. FAN_OUT         spawn k parallel attempts               $$$$
7. ESCALATE_HUMAN  pause, request directive                human time
8. TERMINATE       stop, preserve partial + memory          —
```

Levels 0–3 are free or near-free and resolve the majority of observed pathologies. Levels
6–7 are the ones every multi-agent framework reaches for first, and they are the last resort
here.

## 5. Goal algebra — individual objectives under a collective objective

This is the mandate's specific ask: *swarms of agents with individual goals but also a
broader smart goal*. The failure mode of naive multi-agent systems is that local optima
compose into a global mess — each agent satisfies its brief and the system does not work.

Model it explicitly:

```python
@dataclass(frozen=True)
class Objective:
    id: str
    predicate: str              # human-readable acceptance
    falsifier: Falsifier        # executable — the ONLY thing that closes it
    scope: frozenset[str]       # declared interfaces/files this objective may touch
    parent: str | None

@dataclass(frozen=True)
class GoalLattice:
    """Objectives form a tree; satisfaction composes upward under an explicit rule."""
    root: Objective
    children: Mapping[str, tuple[Objective, ...]]
    composition: Literal["conjunctive", "quorum", "pareto"]
```

Three composition rules, each appropriate to a different situation:

- **`conjunctive`** — parent satisfied iff *all* children satisfied. Decomposition of a
  feature into sub-tasks. Default.
- **`quorum`** — parent satisfied iff *m of n* children satisfied. Redundant attempts at one
  hard sub-problem; the swarm case.
- **`pareto`** — parent selects the child maximising a score vector with no single winner
  required. The AlphaEvolve/Deep-Alfa case from the outer-loop doc.

**Three invariants that make this safe, all mechanically checkable:**

1. **Scope partition.** For conjunctive siblings, `scope_i ∩ scope_j = ∅`. Two agents that
   may write the same file will race, and no amount of supervision fixes it after the fact.
   Check at plan time, before spawning anything.
2. **Falsifier independence.** A child's falsifier must not be satisfiable by another child's
   work. Otherwise agent B's changes make agent A "pass" and both stop.
3. **Attenuation.** `child.budget ≤ parent.budget_remaining`, `child.capabilities ⊆
   parent.capabilities`, monotonically. AETHER already enforces capability attenuation for
   delegation (M-6); the lattice reuses it rather than inventing a parallel mechanism.

The global objective is never merely the AND of local ones — it carries its own falsifier
(the integration test). A swarm where every child is green and the root falsifier is red is
the *expected* case that must be representable, and it triggers a root-level
`REBRIEF`/`BISECT` rather than a false success.

## 6. Topology selection — the decision, not the topologies

HYDRA's core insight is right and worth keeping: **the topology should be chosen at runtime
from task complexity, not fixed by the manifest.** A single-file rename does not need a DAG
of specialists; a cross-cutting refactor does.

Where this proposal diverges from HYDRA: HYDRA calibrates a complexity functional `C` via
logistic regression and bifurcates on a threshold. That requires labelled training data the
repo does not have, and it decides *before* any evidence exists — the moment when the system
knows least.

**Start escalatory instead.** Every task begins in the cheapest topology. Topology change is
an `Intervention` (level 5/6), triggered by an observed pathology, not by an a-priori
prediction:

```
SOLO (1 agent, ReAct)
  │  STALLED or DIVERGENT after N turns
  ▼
BISECTED (sequential sub-objectives, conjunctive lattice)
  │  one sub-objective still STALLED
  ▼
FAN_OUT (k parallel attempts on that sub-objective, quorum or pareto)
  │  all k fail
  ▼
ESCALATE_HUMAN
```

This is strictly better than threshold prediction on three counts: it needs no training
data, it is never wrong about cheap tasks (they never escalate), and every escalation is
justified by a recorded event rather than a score. It also produces exactly the labelled
dataset HYDRA's regression would need — so if predictive bifurcation is still wanted later,
this path generates its training set as a side effect. Ship escalatory first, harvest
labels, then evaluate whether prediction beats reaction.

## 7. Autonomy dial

Same code path for both modes the mandate asks for; the difference is a table, not a branch.

```python
@dataclass(frozen=True)
class AutonomyPolicy:
    auto_max_level: int                  # highest Intervention level taken without asking
    always_ask: frozenset[str]           # pathologies that always escalate to human
    observe_only: bool                   # emit interventions as suggestions, never apply

# fully autonomous:  auto_max_level=8, always_ask=∅
# supervised:        auto_max_level=3, always_ask={SCOPE_DRIFT, BUDGET_RISK}
# observation:       observe_only=True   — agent runs, CONDUCTOR narrates, applies nothing
```

`observe_only` is the mode to build **first**. It lets CONDUCTOR run against historical
ledgers and live runs, emitting the interventions it *would* have made, with zero risk. That
gives an offline evaluation of the whole pathology table before any of it is allowed to act —
and against `benchmarks/artifacts/ladder/` cassettes, it costs $0.

## 8. Implementation shape

```
conductor/                        # separate package; imports vanguard, never imported by it
  measure.py       ProgressVector from ledger events        (pure, no model)
  diagnose.py      Pathology predicates                     (pure, table-driven)
  intervene.py     Intervention → concrete AETHER actions
  lattice.py       Objective, GoalLattice, invariant checks (pure)
  topology.py      escalation state machine
  policy.py        AutonomyPolicy
  adapters/
    aether.py      the ONLY module that imports vanguard
```

Four of seven modules are pure functions over data. That is the point: the meta layer is
where correctness matters most and model calls help least.

**Relationship to the outer-loop doc.** `arch.outer-loop.orchestrator` describes *sequencing
packages across episodes* (the program view). CONDUCTOR describes *supervising an attempt*
(the episode view). They compose: the outer loop's `DirectorObserver` is CONDUCTOR running
at package granularity with `auto_max_level` tuned for program-level decisions. Same
vocabulary, two scales — build CONDUCTOR first, because the episode scale is where the
measured failures are.

## 9. Build order

| Step | Item | Cost | Value |
|---|---|---|---|
| 1 | `ProgressVector` from ledger, offline over `benchmarks/artifacts/ladder/` | S | immediate diagnostic on existing runs |
| 2 | Pathology table + `observe_only` mode | S | validates the vocabulary at $0 |
| 3 | Interventions 0–3 (note/restrict/rebrief/rollback) | M | generalises the `WON_BUT_UNAWARE` fix already merged |
| 4 | `GoalLattice` + the three invariant checks | M | prerequisite for any swarm |
| 5 | Escalatory topology, SOLO→BISECTED | M | the real long-horizon win |
| 6 | FAN_OUT / quorum / pareto | L | only after 1–5 measure well |

Steps 1–2 produce a full diagnostic report on every run already recorded, for free, before a
line of control logic is trusted with anything. Given the evidence audit's finding that the
headline benchmark numbers do not mean what they appear to mean, that is also the fastest
route to knowing what is actually wrong.
