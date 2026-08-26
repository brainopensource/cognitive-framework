---
id: active-sprint-board
class: execution
authority: execution
canonical_for:
  - active-sprint-tasks
  - current-milestone-gates
status: living
owner: tech-lead
version: "0.8.4"
last_verified: 2026-08-26
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# Active Sprint — M-4 Closure, M-5a Baseline and Parallel M-5b/M-6

Authority: [`VISION.md`](../../VISION.md) → [`SPEC.md`](../SPEC.md) + [`01_law/`](../01_law/) →
accepted ADRs through [`ADR-0097`](../02_decisions/0097-phase0-ratification-and-two-lane-activation.md)
→ [`milestones.md`](milestones.md) → this board. Leadership review files are inputs, not a second
execution authority.

## 1. Current state

M-4 implementation and integrated static gates are green. RF-95 is being executed by the Senior lane with
the preregistered real-provider candidate; its evidence is not accepted until the verifier and
fresh-process checks complete. Independent review remains a separate human receipt.

M-5a implementation is complete and gate-green ahead of promotion. M-5b and M-6 may prepare in
parallel because their current work uses frozen interfaces and disjoint surfaces. Neither may claim
promotion evidence until `M-5A-BASE-v2` resolves.

Latest accepted integrated evidence remains **1,575 Python passed / 8 skipped / 0 failed; TypeScript
68/68**. The current development tree rerun is **1,781 Python passed / 8 skipped / 0 failed**, of which the
Dev B package suites are **175**. TypeScript
typecheck and **68/68** CLI tests pass after restoring the locked npm dependencies. This does not
replace the accepted evidence bundle or close any promotion gate. Note that the canonical runner is
`python3 -m unittest discover -s test -t .`; a `pytest` invocation additionally collects
non-suite fixture trees such as `test/runtime/fixtures/greenfield_api/` and reports spurious
failures, so earlier "18 failures / 26 errors" figures measured the collector, not the tree. Static gates pass: TCB
**1,372/1,438**, boundaries, secrets, domain blindness, isolation, duplication, links, stale paths,
and RF-98 structural neutrality; RF-98 historical comparison is unavailable because
`M-5A-BASE-v2` does not resolve.

A-M65 is package-ready but deliberately unmeasured: Runtime now binds an optional controller,
consults it only between durable turns through event-derived projections and guarded confidence,
lowers `delegate` to the mediated `agent.spawn` proposal, records attributed strategy/plan changes,
and preserves the controller-off path. No improvement or default-enable claim is authorized before
the B-M65 paired study and integrated gate.

A-M7 is package-ready and deliberately sequential: `mhf.topology/1` now has a strict generated
wire contract, rejects authority and unrunnable graphs before lowering, binds an optional frozen
composition, and lowers causal role operations plus only explicit `may_delegate_to` edges. The
reference scheduler exposes only operations whose predecessors are settled; the disjoint-read seam
is analysis-only. No concurrent executor, scheduler activation, Kernel change, or I-11 lift is
present.

B-M5B, B-M65, B-M7 and B-M8 are `PACKAGE_READY`; none is `GATE_ACCEPTED`. Three results are
negative or blocked and are recorded as such rather than deferred:

- **B-M5B is materially executed.** One formal-SAT task runs end to end through
  `Runtime.execute_harness` on the unchanged substrate — plugin lifecycle, context policy, kernel
  dispatch, operator-approved `patch.apply`, budget lease, `mhf.trajectory/2` — and the resulting
  witness is graded by the real `EvaluatorDaemon` over a Unix socket under its own Ed25519 key. The
  negative vector runs identically and is signed as `fail`. Evidence is bundled by
  `runtime/formal_evidence.py`, which recomputes every pinned digest and folds the run's terminal
  axis from its own ledger, so a passing witness over an abandoned run is not promotable. RF-86 and
  the RF-98 historical half remain blocked on `M-5A-BASE-v2`; the SAT result is not a generality
  claim until they run.
- **B-M65 is integrated and cannot yet conclude.** The paired study runs on the canonical path with
  the A-M65 hook. The only fully attributable offline provider is deterministic, so the A/A noise
  floor is degenerate at 100% and `MEASUREMENT.md M-07` refuses it; on a task that never stalls the
  controller also issues no directive, so the arms are the same configuration. **A measured M-6.5
  improvement requires a stochastic attributable provider and deliberately-blocked tasks.** This is
  a negative result about the instrument, not about the controller.
- **B-M7 has found a capture gap.** Run against the canonical coding path, M7-01 pairs the three
  real settled effects but reports useful independence `0.0` for one reason only: `EffectStarted`
  writes `descriptorDigest`/`sinkClass`/`grantId`/`leaseId` but **no resolved resource selector and
  no timing**, so no pair can be shown disjoint and contention is unmeasured. That zero is
  *unmeasurable*, not *measured*, and MUST NOT be handed to the ADR-0099 cancel/implement decision
  as if it were the latter. `test_m701_recorded_workload.py` fails if the gap closes silently.

## 2. Active board

| Milestone | Task | Owner | Status | Exit/evidence |
|---|---|---|---|---|
| M-4 | A-M4 evidence runtime and causal capture | Dev A | DONE | `PACKAGE_READY` |
| M-4 | B-M4 contracts, trajectory `/2`, RF-100 | Dev B | DONE | `PACKAGE_READY` |
| M-4 | G-M4-03 integrated repository gates | Tech Lead | DONE | 1,575 Python; 68/68 TS; all named gates |
| M-4 | G-M4-04 one preregistered live RF-95 candidate | Senior | AUTHORIZED — attempt 3 | new preregistration required after D7; preserve evidence regardless of outcome |
| M-4 | G-M4-05 independent review receipt | Director | WAIVED — development only | no evidence-release or promotion claim permitted |
| M-4 | G-M4-06 closure | Tech Lead | PROVISIONAL | implementation may continue; RF-95 evidence closure remains open |
| M-5a | Event `/2`, vocabulary and emitter cutover | Dev A | DONE | mixed `/1|/2`, `/2` writes, historical bytes preserved |
| M-5a | CheckpointManager and RF-96/RF-99 | Dev A | DONE | proof-bound cache, cold fallback, fresh process |
| M-5a | AgentView and Operation/Lineage/Scope | Dev B | DONE | deterministic event projection and contracts |
| M-5a | RF-97 transitive TCB closure | Dev B | DONE | AST-discovered 13-file closure; synthetic recursion test |
| M-5a | Reducer semantic pin | Tech Lead | DONE | `REDUCER_VERSION=v1.1.0`; reproducibility uses canonical pin |
| M-5a | Accept ADR-0098 | Tech Lead | TODO | immediately after M-4 closes |
| M-5a | Re-freeze append/fold benchmark | Tech Lead | TODO | after ADR acceptance; record explained digest migration |
| M-5a | Create/push `M-5A-BASE-v2` once | Tech Lead | TODO | reviewed post-M-5a commit; never move `M-5-BASE` |
| M-5b | OD-3 deterministic oracle | Tech Lead | DONE | SAT/CNF complete-assignment witness selected |
| M-5b | `packs/formal-sat` frame and fixed task set | Dev B | DONE | digest-pinned formula, positive witness, negative vector |
| M-5b | Exterior SAT evaluator | Dev B | DONE | deterministic accept/reject; no search or self-grading |
| M-5b | RF-86 baseline cutover | Tech Lead | DONE | defaults to `M-5A-BASE-v2`; missing tag fails closed |
| M-5b | Full formal run and signed verdict bundle | Dev B | PACKAGE_READY | material run through `Runtime.execute_harness`; daemon-signed pass and fail vectors; `runtime/formal_evidence.py` binds pinned digests plus ledger terminal truth |
| M-5b | RF-86 / RF-98 historical rerun | Dev B | BLOCKED | fails closed; `M-5A-BASE-v2` does not resolve |
| M-6 | SpawnAdapter, conservation, join, recovery, RF-55…59 | Dev A | DONE | 28 falsifiers; conjunctive allocation in ADR index |
| M-6 | Manifest ingress and product-only spawn path | Dev B (active lane) | DONE | Kernel remains verb-blind; agent.spawn admitted in /2 manifests |
| M-6 | Nested-lineage demonstration bundle | Dev B (active lane) | DONE | test_rf55_rf59_delegation_e2e.py; cold-reconstructible child tree |
| M-7 | M7-01 independence analyzer | Tech Lead | DONE — analysis-only | deterministic report producer; no scheduler activation |
| M-7 | Topology schema, lowering and scheduler readiness | Dev A | PACKAGE_READY — sequential only | generated `mhf.topology/1`; fail-closed validation; composition-bound causal operations; explicit delegation edges; no activation |
| M-7 | ADR-0099 concurrency decision | Leadership | TODO — evidence blocked | requires resolved-selector/timing capture and an interpretable M7-01 report; I-11 remains in force |
| M-7 | B-M7 independence decomposition and topology falsifiers | Dev B | PACKAGE_READY — evidence blocked | `lab/topology_analysis.py`, 8 fixtures, three-topology shared lowering; M7-01 on the canonical path reports the conservative floor because effect capture omits resolved selectors and timing |
| M-8 | ADR-0100 category/lifecycle decision | Leadership | TODO | required before public M-8 APIs |
| M-8 | Memory and skills implementation/evaluation | Dev A + Dev B | PREPARED — exterior only | capability/provenance/reference lifecycle; no public activation or measured lift |
| M-8 | B-M8 skill generation, evaluation, promotion and rollback | Dev B | PACKAGE_READY — unmeasured | `runtime/skill_evaluation.py`: separated authorities, contamination-checked held-out split, regression budget, presence-only adversarial checks, grounding/verification, Ed25519 promotion evidence, executed injected-regression rollback, `reproducibility_current` recomputation; no lifecycle event kind before ADR-0100 |
| M-6.5 | A-M65 Meta-Control Runtime integration | Dev A | PACKAGE_READY — unmeasured | optional binding; guarded between-turn consultation; directive lowering; `StrategyChanged` attribution; controller-off baseline preserved |
| M-6.5 | B-M65 confidence, progress and paired evaluation | Dev B | PACKAGE_READY — measurement blocked | `guarded_consult` falsifiers (stale confidence, missing references, nondeterminism, budget bypass, authority escalation); ledger metrics incl. wasted loops and signed-pass rate; `lab/m65_study.py` McNemar exact + Holm + A/A floor + `M-18` comparability; integrated run refuses to conclude on a deterministic provider |

## 3. Decisions in force

- OD-3 selects SAT/CNF. The generator produces a candidate assignment; only the exterior evaluator
  checks it. Oracle, formula and witness vectors are digest-pinned.
- RF-55…RF-59 are conjunctive. The authoritative allocation is the register in
  [`INDEX.md`](../02_decisions/INDEX.md), preserving requirements from ADR-0080 and ADR-0090 while
  using four additive budget dimensions from C-05.
- `REDUCER_VERSION` is `v1.1.0` because the M-5a semantic fold changed. Old checkpoints fail their
  pin and cold-fold; they are never served under new rules.
- RF-86 compares `domain`, `kernel`, `ports`, `runtime`, and `agency/episode` against
  `M-5A-BASE-v2`. It is intentionally red until that reviewed tag exists and is never weakened.
- M-6 implementation was completed in the active Dev B lane; the original masterplan ownership is
  historical. M-5b remains owned by Dev B. Shared-tree work must not overwrite the other lane's
  uncommitted files.
- `runtime/meta_controller.guarded_consult` is the only consultation path that may produce reported
  evidence; bare `consult` remains the minimal value seam. Every M-6.5 falsifier fails closed by
  raising, never by degrading to an unattributable proposal.
- A confidence record MUST declare the `contextEpoch` it was computed at and MUST name a subject in
  the view's reference set. `goal` is always a legitimate subject: `C-06` keeps goal *content* out
  of the ledger, and excluding the token would make goal-level confidence inexpressible.
- M7-01 counts a pair as independent only on a proven-disjoint selector; a missing selector is
  dependent. Shared `observation`/`advisory` sinks are non-exclusive, so disjoint reads remain the
  already-permitted safe-parallel case.

## 4. Immediate sequence

1. Senior completes the single RF-95 candidate and preserves all evidence, pass or fail.
2. Director waiver permits development continuation; obtain G-M4-05 and a passing RF-95 before
   evidence release, promotion, or immutable baseline tagging.
3. Accept ADR-0098, run the append/fold benchmark, explain and freeze the new digests, rerun gates.
4. Create and push `M-5A-BASE-v2` on the reviewed M-5a substrate commit.
5. Dev B has executed the material SAT run with a daemon-signed verdict bundle (both vectors);
   Dev A completes M-6 product activation and demonstration.
6. Run RF-86/RF-98 and independent cross-lane review; close M-5b/M-6 separately on evidence.
7. Extend effect capture with the resolved resource selector and settle timing before
   `lab/m701_independence.py` can produce an ADR-0099 input; until then its report over recorded
   canonical workloads is the conservative floor and is not a cancel decision. Keep I-11 sequential.
8. Freeze ADR-0100 and the five-category M-8 contract kit before enabling memory or promotion APIs.
9. A-M65 and B-M65 are integrated and exercised on the canonical path. Provision a stochastic
   attributable provider and a deliberately-blocked task set so a non-degenerate A/A floor exists;
   only then does `lab/m65_study.py` produce an acceptable verdict. Do not claim improvement before
   that run.

The RF-95 failure also fixed two substrate/adapter defects: determinate adapter errors now emit
`EffectFailed` after `EffectStarted`, and model-authored bare `@@` hunks are context-anchored by
the environment adapters. These repairs are covered by focused tests; they do not make the failed
candidate pass and do not authorize a retry.

## 5. Prohibited scope

- No manual RF-95 trajectory repair, retries, fake/cassette substitution or post-output task choice.
- No movement of historical `M-5-BASE`; no movement/recreation of `M-5A-BASE-v2` after creation.
- No SAT, spawn, topology, memory or strategy semantics in Kernel or the generic episode loop.
- No new event kind without a successor accepted decision, schema, writer, reducer and falsifier.
- No M-7 concurrency before M7-01 measurement and explicit Director lift of I-11. The current
  `0.0` useful-independence report is unmeasurable, not measured, and does not satisfy M7-01.
- No M-6.5 improvement, effect size, or default-enable claim while the A/A floor is degenerate.
- No M-8 promotion outside `Generator != Evaluator != Promoter`; the promotion unit is the
  versioned composition, never a skill in isolation.
