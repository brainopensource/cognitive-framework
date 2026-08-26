---
id: active-sprint-board
class: execution
authority: execution
canonical_for:
  - active-sprint-tasks
  - current-milestone-gates
status: living
owner: tech-lead
version: "0.8.0"
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

M-4 implementation and integrated gates are green. RF-95 is being executed by the Senior lane with
the preregistered real-provider candidate; its evidence is not accepted until the verifier and
fresh-process checks complete. Independent review remains a separate human receipt.

M-5a implementation is complete and gate-green ahead of promotion. M-5b and M-6 may prepare in
parallel because their current work uses frozen interfaces and disjoint surfaces. Neither may claim
promotion evidence until `M-5A-BASE-v2` resolves.

Latest integrated evidence: **1,575 Python passed / 8 skipped / 0 failed; TypeScript 68/68; codegen,
boundaries, TCB 1366/1438, RF-97 transitive closure, secrets, domain blindness, isolation,
duplication, links, stale paths and RF allocation green; Kernel semantic diff zero.**

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
| M-5b | Full formal run and signed verdict bundle | Dev B | IN PROGRESS | SAT/CNF pack is executable; material run waits for reviewed v2 baseline |
| M-6 | SpawnAdapter, conservation, join, recovery, RF-55…59 | Dev A | DONE | 28 falsifiers; conjunctive allocation in ADR index |
| M-6 | Manifest ingress and product-only spawn path | Dev B (active lane) | DONE | Kernel remains verb-blind; agent.spawn admitted in /2 manifests |
| M-6 | Nested-lineage demonstration bundle | Dev B (active lane) | DONE | test_rf55_rf59_delegation_e2e.py; cold-reconstructible child tree |
| M-7 | M7-01 independence analyzer | Tech Lead | DONE — analysis-only | deterministic report producer; no scheduler activation |
| M-7 | Topology/scheduler implementation and ADR-0099 | Dev A + Leadership | TODO | after M-6 and evidence review |
| M-8 | ADR-0100 category/lifecycle decision | Leadership | TODO | required before public M-8 APIs |
| M-8 | Memory and skills implementation/evaluation | Dev A + Dev B | TODO | capability, provenance, held-out lift, rollback |
| M-6.5 | ConfidenceRecord, ProgressView, exterior MetaController contract | Dev A | IN PROGRESS | pure projection/contract slice; no runtime authority |

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

## 4. Immediate sequence

1. Senior completes the single RF-95 candidate and preserves all evidence, pass or fail.
2. Director waiver permits development continuation; obtain G-M4-05 and a passing RF-95 before
   evidence release, promotion, or immutable baseline tagging.
3. Accept ADR-0098, run the append/fold benchmark, explain and freeze the new digests, rerun gates.
4. Create and push `M-5A-BASE-v2` on the reviewed M-5a substrate commit.
5. Dev B executes the material SAT run; Dev A completes M-6 product activation and demonstration.
6. Run RF-86/RF-98 and independent cross-lane review; close M-5b/M-6 separately on evidence.
7. Use `lab/m701_independence.py` on fixed recorded workloads; attach its digest-stable report to
   the ADR-0099 decision. Keep I-11 sequential until that decision.
8. Freeze ADR-0100 and the five-category M-8 contract kit before enabling memory or promotion APIs.
9. Complete the M-6.5 runtime consultation seam and paired evaluation before opening M-7 scheduler
   implementation.

The RF-95 failure also fixed two substrate/adapter defects: determinate adapter errors now emit
`EffectFailed` after `EffectStarted`, and model-authored bare `@@` hunks are context-anchored by
the environment adapters. These repairs are covered by focused tests; they do not make the failed
candidate pass and do not authorize a retry.

## 5. Prohibited scope

- No manual RF-95 trajectory repair, retries, fake/cassette substitution or post-output task choice.
- No movement of historical `M-5-BASE`; no movement/recreation of `M-5A-BASE-v2` after creation.
- No SAT, spawn, topology, memory or strategy semantics in Kernel or the generic episode loop.
- No new event kind without a successor accepted decision, schema, writer, reducer and falsifier.
- No M-7 concurrency before M7-01 measurement and explicit Director lift of I-11.
