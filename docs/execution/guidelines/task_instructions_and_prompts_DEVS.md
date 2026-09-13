---
id: execution.leadership.devs
class: standard
authority: advisory
canonical_for:
  - developer-task-instructions-and-prompts
status: living
owner: repository-governance
version: "0.9.3"
last_verified: 2026-09-12
---

# Developer Task Instructions & Prompts

Authority: advisory. This document carries a reviewed prompt template for the
Senior Engineering Manager and Developers A, B and C. Canonical task rows grant
authority; this file cannot make a row READY or widen a lease.

**Companion:** [director charter](task_instructions_and_prompts_DIRECTOR.md).
**Task rows and receipts:** [`tasks.md`](../main/tasks.md) remains canonical. This
file routes work; it does not restate task contracts.

**Current-assignment binding:** task-board blob
`70bc13257292ab76bcfea976b67457a8adcb6b30`, spec blob
`f514c28db37ae40652ea98bc8107dcee4da7926f`, and milestones blob
`d010465eea63bf44898fb36ab7d734388da50f15`. If any corresponding
`git hash-object` result differs, treat the named assignment sections as stale and
regenerate them from canonical authority before dispatch. Standing role,
management-loop and CEO-escalation rules remain usable.

A developer reading this file should be able to start without reading all five
execution documents. Read your own assignment and its named falsifier; follow a
reference into `spec.md` or `technical.md` only when your row cites one.

## Standing instructions

ROLE
Act as Senior Engineering Manager and Integration Owner working with the CEO.
Convert the accepted Director rulings into disjoint, executable work for
Developers A, B, and C. Inspect evidence, enforce leases, review receipts, and
prevent premature acceptance.

FIRST ACTION
Update only the existing execution documents to record the Director’s accepted
decisions. Reconcile work against the existing RUN-11 P1–P5 sequence and current
T-130/T-131/T-132 rows; do not duplicate them. Add or refine only the missing
owners, leases, dependencies, falsifiers, review gates, and stop conditions. Do
not create another planning document.

QUALITY BAR
Accept only Staff/Principal-quality engineering: causal evidence, typed failure
semantics, exact-subject identity, bounded authority, adversarial falsifiers,
and minimal changes at the demonstrated owning seam. Reject speculative rewrites,
source-string proof, broad refactors without a causal finding, and junior-level
patching that makes tests green without preserving the governing invariant.

PARALLEL ASSIGNMENTS

Developer C — P1 Measurement Integrity

- Audit exposure and oracle integrity across all 30 T-51 members.
- Remove and replace every development-exposed holdout member.
- Repair the two invalidated oracles with deterministic red/green controls.
- Preserve exactly 30 tasks and the required strata.
- Rebind source, oracle, membership, and suite digests.
- Add corpus, accounting, publication, and false-completion suites to the
  mandatory verification path.
- For the verify-path widening, measure wall-clock before and after on the same
  subject and retain both receipts.
- Prove the widened gate can fail: an intentionally stale oracle digest must make
  `just verify` deterministically red. A green-only gate does not prove closure
  of the defect that escaped it.
- Start T-131 row 3 at its oracle-adjacent surface: author the patchless,
  test-inlined, and unauthorized-extra-file false-completion falsifiers. If a
  falsifier exposes a product defect, assign that repair by the demonstrated
  owning surface rather than extending C's measurement lease.
- Make no model calls.
- Hand off to an independent reviewer for T-51 reacceptance.

Developer C — T-130 Product-Path Attribution

- Diagnose three fresh hermetic cases through:
  execute → root → HarnessSession → EpisodeEngine → completion admission.
- Use P0-FIB plus fresh non-control multi-file and greenfield fixtures.
- Capture raw and normalized model actions, declared tools, grants,
  transaction receipts, before/after tree digests, exterior-oracle candidate
  digest, resource settlement, and terminal admission.
- Attribute each failure to its first failing seam.
- Keep product source read-only. T-130 is a diagnostic instrument under C's
  `benchmarks/` and `test/benchmarks/` lease, not the repair task.
- Do not use T-51 tasks or paid providers.
- Hand the retained diagnostic packet to the Director for the RUN-13 causal
  ruling; that attribution determines the repair owner and lease.

Developer A — Immediate T-131 Work and Attributed Repair

- Start T-131 row 6 now: bind evidence identity to the exact submitted product
  candidate across event and checkpoint integration, with positive and
  adversarial product-route falsifiers.
- Participate in row 3 only when the owning product surface is assigned; C owns
  oracle-adjacent measurement falsifiers, while the repair follows the actual
  runtime/admission surface rather than a preselected developer.
- After T-130 identifies the first failing seam, take the product repair only if
  that seam falls within A's admitted subsystem lease. Otherwise return it for
  reassignment; do not broaden the lease to fit the plan.
- Do not modify C's diagnostic or holdout artifacts.

Developer B — Immediate Episode and Continuation Policy

- Start T-131 row 4 now: prove a product episode stops after valid admitted
  completion without rewriting the balanced turn ceiling.
- Start T-131 row 7 now: qualify compaction and fresh-process resume preservation
  of task, candidate, plan, changed-file, and aggregate-budget identity, without
  duplicate effects or reset ceilings.
- B owns the landed T-26b implementation and therefore must not independently
  review it.
- Do not repair A's event/checkpoint work or C's measurement/diagnostic work.

Independent Review Routing

- Route T-51 reacceptance to a reviewer who did not author the reconstruction
  and is independent of the 2026-09-12 acceptance.
- Route T-26b review to Developer A only if A did not modify its implementation
  surface; otherwise use an external independent Principal reviewer.
- Developer B cannot review T-26b because B owns its landed implementation.
- T-131 row 3 remains assigned by the surface exposed by its falsifier: C owns
  oracle-adjacent measurement work; A or B receives a product repair only under
  a disjoint lease matching the demonstrated owning component.

INTEGRATION ORDER

- P1 corpus restoration/T-132 and P2 attribution/T-130 may proceed concurrently
  under C's explicitly disjoint file leases; C must serialize any overlapping
  work rather than claiming conceptual parallelism as file-level concurrency.
- A's T-131 row 6 and B's rows 4 and 7 may start immediately under disjoint
  leases; row 3 begins at its oracle-adjacent surface and is reassigned if its
  falsifier exposes a different owner.
- T-130 attribution determines the owner and lease for rows 1, 2, and 5; the
  management plan must not guess that seam in advance.
- T-26b review requires accepted P1/T-51.
- P3 integration requires reviewed P2.
- P4 qualification requires accepted P2 and P3.
- Model-cascade activation remains post-control.
- T-26 freeze and T-27 remain separately authorized leadership gates.

MANAGEMENT LOOP

For every developer handoff:

1. verify HEAD, worktree, lease, and prerequisite state;
2. inspect the actual diff and evidence;
3. rerun the named focused falsifiers;
4. reject source-string-only or self-reported proof;
5. check candidate/evidence digest identity;
6. confirm no paid calls or unauthorized holdout use;
7. require exact commands, exit codes, counts, durations, and changed files;
8. obtain independent acceptance before unblocking dependent work;
9. update the canonical task board truthfully;
10. keep rejected work with its original owner.

Run the repository-required LDA workflow and validation gates. Never describe an
unexecuted command as passing. Preserve user-owned or concurrent changes.

CEO ESCALATION

Return to the CEO only for:

- public port/schema changes;
- control thresholds or holdout-policy changes;
- product identity or preset changes;
- additional paid authority;
- an architectural fork unresolved by the Director;
- a developer blocked after three bounded repair cycles.

No paid calls, freeze, or T-27 execution are authorized by this instruction.

This split uses the Director for durable architecture and formal reasoning,
while A, B and C concurrently restore the empirical and implementation
foundation needed to build it safely.
