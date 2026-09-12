# Director Charter II — Architecture, Protocol and Horizon

**To:** CTO / Principal Engineer
**From:** CEO
**Date:** 2026-09-12
**Subject:** current `HEAD` on `feat/aether-framework-electroweak-canonical-agents`
**Authority:** `AGENTS.md`, `docs/execution/main/spec.md` RUN-01..RUN-13, and the five execution files

> Temporary chat directive, not a repository artifact. Keep it untracked and do
> not commit it. The Senior Developer transfers approved decisions into the
> canonical execution files.

## 1. What changed since Charter I

Charter I is discharged. Its decisions are now normative and you may not
relitigate them without new evidence:

- `spec.md` RUN-07..RUN-13 record D1-D6 plus the open causal question.
- `technical.md` records the nine approved architectural boundaries.
- `milestones.md` records the RUN-11 package order and freeze predicates.
- `tasks.md` carries T-130 (hermetic write-landing probe), T-131 (eight
  `BLOCK-T27` defects), T-132 (gate discovery widening), and the T-51 holdout
  exposure finding with its normative audit-before-repair ordering.

One thing Charter I did not deliver: the RUN-13 causal statement. T-130 is the
instrument that produces it, it is hermetic and costs nothing, and it does not
need you. **Do not spend this session on it.** If T-130 has returned by the time
you read this, its packet is evidence for §3 below; if it has not, decide §3
conditionally and name the branch.

## 2. Why this charter is different

Charter I converted a mess into decisions. That was correct and it is done. The
remaining risk is no longer disorder — it is that we execute a well-governed plan
toward a target that is merely *correct* rather than *state of the art*.

This session is for the work only a principal can do: the mathematics, the
protocol design, the architecture that has to be right before it is built, and
the honest assessment of how far the current design can actually go. You are not
being asked to approve or schedule. You are being asked to **design and to
falsify your own design**.

Depth is the deliverable. Where a claim is quantitative, give the equation and
its domain of validity. Where a mechanism is a protocol, give its state machine,
its failure modes and its recovery. Where you are guessing, say so and say what
measurement would settle it. A confident paragraph that cannot be falsified is
worth less to us than an uncertain one that can.

## 3. Assignments

### A1 — The completion problem, formally

Truthful completion is the invariant the whole instrument rests on, and we
currently defend it with a veto and a digest. State the problem properly.

Give the formal conditions under which an exterior oracle's verdict on a
submitted candidate is a sound estimator of task success. Define the adversary:
an agent optimizing for oracle-pass rather than task completion, with full
knowledge of the harness. Characterize the gap between `oracle_passes(c)` and
`task_solved(c)` — false completion, and its neglected dual, false failure, where
a correct candidate is rejected by an oracle that is wrong or by a harness that
loses the write. Our RUN-03 acceptance rule uses a two-sided Wilson lower bound
at 0.40 with zero observed false completions over n = 30; derive what that
actually bounds, including what "zero observed" is worth at n = 30 (give the
upper confidence bound on the unobserved rate). State whether our acceptance
threshold is defensible or merely conventional.

### A2 — Long-horizon context economics

Give the model. Define the state an agent must carry across a 100+ turn episode,
the rate at which it is generated, and the compaction operator that bounds it.
Then state the loss: what compaction provably destroys, and which of RUN-10's six
preserved quantities (objective, constraints, unresolved failures, plan state,
changed-file identity, resource ledger) are sufficient to reconstruct competent
behavior versus merely sufficient to avoid crashing.

Derive the relationship between context budget, turn count and task success. If
the relationship is not derivable, say so and give the experiment that measures
it. Address the failure we actually observe in the field: an agent that is still
technically executing at turn 80 but has stopped making progress. Is
that a context defect, a planning defect or a reward defect, and what
instrumentation distinguishes them? Bounded replanning with terminal exhaustion
(RUN-10) is our current answer; argue whether it is adequate or merely safe.

### A3 — The write path, designed rather than repaired

T-130 will tell us where writes are lost. It will not tell us what the write path
should be. Design it.

Specify the transaction protocol end to end: emission, normalization, admission,
capability grant, staging, atomic commit, digest sealing, oracle handoff. Give
the state machine, the invariant at each transition, and the behavior under
crash, partial write, concurrent mutation and resume. Say precisely what makes a
multi-file change atomic in a filesystem that offers no such guarantee, and what
our `CAS-01` proposal buys that the current transaction adapter does not.

Then the harder half: state which failure modes this design makes *impossible*
versus merely *detectable*, and what it costs. An impossible-by-construction
failure that doubles latency may be the wrong trade; say which you would take.

### A4 — What SOTA actually requires

We intend to build a state-of-the-art coding agent harness. Assess honestly
whether the current architecture can get there, or whether it is a well-governed
local optimum.

Name the specific capabilities that separate a leading harness from a competent
one, and for each, say whether we have it, can reach it from here, or need a
design we do not have. Be concrete about where we are behind. Consider at
minimum: retrieval quality versus context volume; verification strength beyond
test-passing; recovery from a wrong plan rather than a wrong edit; multi-model
routing under a budget; whether learned or accumulated task experience is a real
advantage or a contamination liability we are right to gate hard.

Give a dated, falsifiable claim about what would have to be true for us to
publish a defensible SOTA result, and what our honest current distance from it
is. `MS-SOTA`, `FH-E04` and T-127 already gate the claim; this is not about the
gate, it is about whether the thing behind the gate is achievable.

### A5 — The refactor we are avoiding

Every codebase has one. Identify the structural change that is most expensive to
make now and most expensive to defer, and rule on it.

RUN-10 approved nine boundaries and authorized no public port or schema change.
That was the right call for the control arm. State whether it is the right call
for the next twelve months, and if not, name the delta, its migration path and
the moment at which deferring costs more than doing it. The `FH-1` proposal tree
(CAS-01, delegation, memory, evaluation) is the obvious candidate; say whether
it is one refactor or four independent ones, because we have been treating it as
a package and that may be the error.

### A6 — Horizon

Sequence the next three to six months at the level of capability, not task rows.
What must be true in order, what can be built in parallel, what we should refuse
to build. Include at least one thing we are currently planning that you would
cancel, and defend the cancellation.

## 4. Required output

For A1-A3 and A5, produce genuine technical content: equations with stated
domains, protocol state machines, invariants, failure enumerations. Prose that
restates the assignment is a failed deliverable. For A4 and A6, produce
judgment with reasons and an explicit statement of what would change your mind.

Close with:

1. any decision that changes RUN-07..RUN-13, stated as a named delta with its
   justification — silence means those decisions stand;
2. anything requiring a public port or schema change, which RUN-10 currently
   forbids and only you can unlock;
3. the three assumptions in your own analysis most likely to be wrong, and the
   measurement that would expose each.

## 5. Boundaries

- Read product and benchmark source; do not edit implementation code.
- Do not run development iterations against the T-51 holdout.
- Do not weaken, delete or silently replace a required falsifier.
- Do not add a sixth execution document or commit this directive.
- Do not freeze `control_preregistration.json`; do not run T-27.
- Zero provider calls. RUN-12 stands: `DEFER — zero calls`.
- No SOTA claim from mechanism presence, design quality or diagnostics.
- Do not schedule, decompose into task rows, or assign leases. That is Senior
  work and doing it here wastes the session.

## 6. Definition of done

The Senior Developer can build against A3, the measurement owner can defend A1
under review, and the CEO knows from A4 and A6 what we are actually capable of
and what we have been avoiding. Nothing is implemented, frozen or claimed.
