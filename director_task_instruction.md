# Director Charter — Causal Decisions for the Coding Harness

**To:** CTO / Principal Engineer  
**From:** CEO  
**Date:** 2026-09-12  
**Subject:** `63881e68caab8a33a4da588718db33fe0fb88706`  
**Authority:** `AGENTS.md`, `docs/execution/spec.md` RUN-01..RUN-06, and the five execution files

> This is a temporary chat directive, not a repository artifact. Keep it
> untracked and do not commit it. The Senior Developer owns documentation
> maintenance and will transfer your approved decisions into the canonical
> execution files.

## 1. Assignment

Use one focused leadership session to answer the questions that require
architectural judgment. Do not perform the exhaustive audit, write detailed task
rows, implement product fixes, or run the complete verification matrix yourself.

Your outcome is a compact, decisive handoff from which senior developers can
implement without returning for routine decisions.

We are building a coding agent that can demonstrate, through the real product
path:

- atomic multi-file changes;
- greenfield construction;
- large-context repository navigation;
- durable long-session compaction and fresh-process resumption;
- bounded planning and replanning;
- truthful exterior-oracle completion;
- policy-bound local and hosted model escalation.

Mechanism presence is not success. No SOTA claim is permitted without retained,
comparative evidence against named baselines.

## 2. Verified starting state

Verify these facts briefly; do not repeat the Senior Developer's full audit:

- HEAD at assignment: `63881e68caab8a33a4da588718db33fe0fb88706`.
- `test.benchmarks.test_control_corpus` currently runs 8 tests and ends with
  1 error plus 1 failure rooted in `oracle digest mismatch`.
- The execution board has been truth-synced: T-51 is REOPENED/BLOCKED and T-26b
  review waits for T-51 reacceptance.
- Two T-51 oracle files changed after their accepted digest binding.
- T-26b implementation is landed but not independently accepted.
- `control_preregistration.json` remains UNFROZEN.
- T-26 and T-27 remain BLOCKED.
- The committed autofix cascade is local-only and is not the control subject.
- The control subject is single-worker `vg-code-balanced`, preset `balanced`,
  through `vanguard.packages.runtime.entrypoint.execute`.

If any fact is wrong, record the correction and decide from current evidence.

### 2.1 Measured foundation state — run for you on `63881e68`

Executed 2026-09-12 on a clean checkout of the assignment subject, so you need
not re-run them. Re-run anything you intend to rely on.

| Gate | Command | Result |
|---|---|---|
| Full pipeline | `just verify` | **PASS** — 102 + 310 + 535 tests, 7 skipped, typecheck + docs green |
| Static gates | `just check` | **PASS** — isolation, path hygiene, doc metadata, links, markdownlint (133 files, 0 issues) |
| Execution board | `check_execution_truth.py` | **PASS** — one supported state model |
| Links | `check_markdown_links.py` | **PASS** |
| Whitespace | `git diff --check` | **PASS** |
| LDA index | `lda identity --json` | **FRESH** at `63881e68`, 11,430 symbols |
| Doc drift | `lda drift --json` | **0 stale paths**; 391 undocumented symbols, 306 documents without code evidence (pre-existing, non-blocking) |
| Control slice | `test_metric_veto` + `test_control_accounting` + `test_preregistration` + `test_evidence_row_schema` + `test_product_path_subject` + `test_ladder_runner` | **67 passed** |
| Corpus gate | `test.benchmarks.test_control_corpus` | **RED — 8 tests, 1 failure, 1 error**, `oracle digest mismatch` |

**Verdict: the foundation is clean.** No stale index, no broken links, no
outdated references, no flaky suites observed. Exactly one gate is red, it is
the known T-51 blocker, and its cause is understood. You are not walking into a
repair job — you are walking into one decision.

### 2.2 One structural finding you should rule on

`just check` and `just verify` discover only `test/kernel`, `test/agency` and
`test/contracts` (`justfile:80-82`). Measured discovery across the tree:

```
test/runtime      823        test/packs         92
test/contracts    535  *     test/security      55
test/falsifiers   524        test/apps          38
test/agency       310  *     test/lab           32
test/tools        200        test/registry      28
test/adapters     198        test/middleware    23
test/benchmarks   163        test/trust         22
test/kernel       102  *     others            <10 each
                                    * = in the gate
```

**≈947 of ≈3,171 tests (~30%) run in the standard gates.** `test/benchmarks`
— which contains the control instrument — and `test/falsifiers` are both
outside them.

This is why the stale oracle digest survived: `just verify` passed at every
step while `test_control_corpus` was red, because that suite is never
discovered. Every "verify passed" receipt in the recent handoffs is true and
simultaneously silent about the control instrument.

Whether to widen gate discovery is an architectural and cost decision, not a
developer's call. It also bears directly on D1: a measurement instrument that
no gate protects will drift again.

`test/e2e` and `test/broken` are not importable as packages; that appears
deliberate but is unconfirmed.

### 2.3 Working tree at handoff

`docs/execution/tasks.md` (truth-sync) and `.draft/temp_auxiliary_table.md` are
modified; `.generated/knowledge/catalog.jsonl` was regenerated by `just verify`
and must not be hand-edited. `director_task_instruction.md` is untracked and
stays that way.

## 3. The one diagnosis you own

Determine the causal boundary of the write-landing failure. This is the hardest
and highest-leverage question: capable models have consumed turns on multi-file
and greenfield work while changing zero files.

Require evidence through the real product route:

```text
runtime.entrypoint.execute
  -> runtime.root
  -> runtime.session.HarnessSession
  -> agency.episode.EpisodeEngine
  -> model adapter and dialect normalization
  -> tool admission and capability grant
  -> patch transaction and candidate workspace
  -> completion admission (_admit_completion)
  -> exterior oracle
  -> evidence reconciliation and report admission
```

Forge, BaaC, and the autofix proficiency are comparative evidence only. A fix in
one of those paths does not close a product-path defect.

Use retained evidence from one L0 case, one non-control multi-file case, and one
non-control greenfield case. If existing evidence cannot distinguish the seam,
authorize a small diagnostic probe for the Senior Developer. Do not run or tune
against the T-51 holdout.

Classify the cause among, at minimum:

- no canonical tool emitted;
- undeclared or malformed tool call;
- capability or policy denial;
- patch transaction rejection or partial application;
- wrong candidate workspace;
- stale tree observed by the oracle;
- patchless completion admitted;
- resource exhaustion before the first valid action;
- multiple independent failures.

Return one causal statement:

```text
Observed symptom -> failing seam -> governing invariant -> smallest valid
architectural repair boundary -> evidence that will falsify the repair.
```

You decide whether the repair is local to an existing component or requires a
separately admitted public contract change. You do not implement it.

## 4. Decisions only the Director makes

Return a ruling for every item. `UNDECIDED` is not an exit state.

### D1 — Measurement trust

Is the control instrument currently trustworthy enough to freeze after T-51 is
restored, or is a broader corpus rebuild required? The Senior Developer will
statically audit all 30 oracles and apply this default escalation rule:

- three or more toothless/non-deterministic oracles means systemic failure and
  corpus rebuild;
- fewer than three permits named repair or replacement.

You may override the threshold only with a written rationale.

### D2 — T-51 treatment

Choose `REPAIR` or `REPLACE` for the two invalidated members and explicitly
authorize the Senior Developer to rebind the resulting suite digests after the
new oracles are independently proven red on the intended defect and green on a
correct implementation.

### D3 — Fix before measurement

Decide which known product defects must be fixed before T-26/T-27. Classify each:

- `BLOCK-T27`;
- `MEASURED-MISSINGNESS` with a typed non-binary outcome;
- `POST-CONTROL` with a reason it cannot invalidate measurement.

Required rows:

1. valid model writes do not land;
2. multi-file application can be partial or invisible to the oracle;
3. patchless, test-inlined, or extra-file completion can appear green;
4. product episodes consume their full turn ceiling after valid completion;
5. malformed/undeclared tool dialect is not attributed precisely;
6. evidence identity can diverge from the submitted product candidate;
7. resume or compaction can lose task, candidate, plan, or budget identity;
8. model escalation can bypass aggregate budget or provider policy.

### D4 — Target architecture

Approve or reject these architectural boundaries:

- one canonical `EpisodeEngine`; no second agent loop;
- atomic all-or-nothing multi-file transaction with final tree digest;
- exterior oracle evaluates the exact submitted candidate;
- context retrieval is token-bounded and provenance-bound;
- compaction preserves objective, constraints, unresolved failures, plan state,
  changed-file identity, and resource ledger;
- fresh-process resume never duplicates effects or resets ceilings;
- replanning is finite and exhaustion is terminal;
- production model escalation flows through existing `ModelPort`, provider
  factory, credential isolation, and evidence accounting;
- escalation retains one task/slot identity and one aggregate resource budget.

Name any required public schema or port change explicitly. Absence of such a
decision means developers must preserve current public contracts.

### D5 — Delivery order

Approve a priority order for five implementation packages:

1. measurement and oracle integrity;
2. product-path write/change closure;
3. exterior completion and false-completion resistance;
4. large-context, compaction, and resumable-session qualification;
5. budgeted model cascade plus comparative evidence.

State which packages may run in parallel and which require a completed review
first. Default to the order above unless diagnosis establishes a different
dependency.

### D6 — Live model authority

The available diagnostic ceiling is aggregate `$0.10 USD / 150 provider calls`.
Decide how much, if any, may be allocated before freeze. Every allocation must
name:

- exact pinned model ID;
- task class and diagnostic purpose;
- USD, provider-call, token, turn, and wall-clock sub-ceilings;
- evidence/ledger destination;
- stop condition.

`openrouter/free` is exploratory only and cannot produce qualification evidence.
The existence of a credential is not authority. Hosted access must use the
admitted `ModelPort` path. Unknown cost remains unknown.

This charter does not authorize T-27 or freezing the preregistration.

## 5. Required Director handoff

Return one decision table with these columns:

| Decision | Evidence | Ruling | Blocks | Authorized owner | Review gate |
|---|---|---|---|---|---|

Then provide:

1. the write-landing causal statement from §3;
2. D1-D6 with no undecided cells;
3. the ordered implementation packages and permitted parallelism;
4. any public-contract escalation requiring leadership approval;
5. the exact diagnostic spend allocation, or `DEFER — zero calls`;
6. a rough engineering size for each package: `S`, `M`, or `L`;
7. the conditions under which T-26 may become freeze-ready.

Keep the handoff short enough to review in one sitting. The Senior Developer
will translate it into leases, task rows, exact falsifiers, receipts, and the
five canonical execution documents.

## 6. Delegated Senior work — not Director work

The Senior Developer owns:

- static audit and recorded verdict for all 30 control oracles;
- validating, repairing/replacing, digest-binding, and independently reviewing
  the T-51 corpus after D1/D2;
- independent T-26b review after T-51 reacceptance;
- detailed implementation task decomposition, leases, `requires:` edges,
  pseudocode, exact falsifiers, estimates, and stop conditions;
- compression/supersession of stale execution-document history without adding a
  sixth execution file;
- implementation and review assignments;
- all focused gates, `just check`, `just verify`, LDA synchronization/drift,
  link checking, execution-truth checking, and final receipts;
- preparation of the freeze-readiness packet.

The Senior Developer returns to the Director only for a public port/schema
change, preset or threshold change, holdout-policy change, additional paid
authority, or a genuine architectural fork not resolved by D1-D6.

## 7. Boundaries

- Read product and benchmark source; do not edit implementation code.
- Do not run development iterations against T-51.
- Do not weaken, delete, or silently replace a required falsifier.
- Do not add a sixth execution document or commit this directive.
- Do not freeze `control_preregistration.json`.
- Do not run T-27.
- Do not claim SOTA from mechanism presence or engineering diagnostics.
- Stop after the decision handoff; implementation and verification belong to
  the admitted Senior/Principal task owners and independent reviewers.

## 8. Definition of done

The Director assignment is complete when:

- the real write-landing failure has a defensible causal boundary;
- D1-D6 are decided;
- T-51 repair/replacement and digest authority are explicit;
- every known defect is classified;
- target architecture and package order are approved;
- live diagnostic authority is explicit and bounded;
- the Senior Developer can construct the detailed implementation charter without
  another routine leadership meeting.

Nothing is implemented, frozen, or called SOTA by this assignment. It converts
uncertainty into decisions so the engineering lanes can move quickly and safely.
