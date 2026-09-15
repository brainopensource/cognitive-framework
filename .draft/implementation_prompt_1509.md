# Implementation Dispatch — Backend Remediation W0–W6

Source plan: `.draft/final_development_plan1509.md`
Governance context: `.draft/todo/leadership_improvements_exec_plane_1409.md`

---

## PROMPT — paste this to each developer, with their packet ID

> You are implementing one bounded work packet from
> `.draft/final_development_plan1509.md` against the repository at
> `/home/rock-dev/Coding/cognitive-framework`.
>
> **Your packet is: `<W-ID>`.** Read only that packet's section below, plus the
> plan stage it cites. Do not start work outside your declared file lease.
>
> **Standing rules, non-negotiable:**
> 1. **Never weaken an execution gate to make a test pass.** Narrow a noisy
>    check, prove it still reds against the original defect, never delete it.
>    If a gate is genuinely wrong, stop and escalate — do not adjust it.
> 2. **Falsifier first.** Write the failing test before the fix. Record the red
>    output. A packet whose test was written after the fix is not accepted.
> 3. **Stay in your lease.** The file lists below are exhaustive. If your change
>    requires a file outside it, stop and report the collision rather than
>    reaching for it — several files are held by other streams.
> 4. **No provider or paid calls.** Zero. Use `lam-engine` cassettes or
>    `llama-cpp` locally if you need model behaviour.
> 5. **Line numbers in the plan are review-time locators, not identity.** Resolve
>    the named symbol first (`lda_symbol` / `lda_references`); if it moved, use
>    the symbol and note the drift in your handoff.
> 6. Do not edit `docs/execution/main/tasks.md` — it is Senior-owned and is the
>    single serialization point. Report status; the Senior records it.
>
> **Definition of done:** your packet's falsifiers red before and green after;
> `just check` green; the collections your packet names green; a handoff note
> stating exact SHA, what you changed, what you deliberately did not change, and
> which falsifier would fail if your change were wrong.
>
> Work the packet. Report when the falsifiers are red, again when green.

---

## Wave structure

```
WAVE A (start now — no ruling, no lease conflict, fully parallel)
  W0  test-runner instrument repair          Lane 1
  W2a candidate-identity falsifiers only     Lane 2
  W3a transaction latent defects             Lane 3
  W6a purity + claim reconciliation (docs)   Lane 3 (after W3a) or 4th dev

WAVE B (needs WAVE A + a ruling or a lease release)
  W1  red-fixture repair            after W0        — no ruling
  W2b candidate-identity fix        after W2a + C6 ruling
  W5  provider/accounting           after W0 + C4 ruling + session.py lease
  W4  completion convergence        after W1,W2b + C1 ruling + session.py lease

WAVE C (needs an explicit leadership ruling that it is pulled forward)
  W3b crash-safe journal/publication/fault injection  = MS-CAS, post-control
```

**Critical path:** W0 → W1 → W4. Everything else branches off it.

---

## Blocking decisions — these are not developer work

Route these to the Senior/Director before Wave B starts. Each one blocks a
named packet, so an unruled row stalls that lane and nothing else.

| Ref | Decision needed | Blocks | Note for the ruling |
|---|---|---|---|
| **C1** | `admission_required` capability-derived, or `vg-code-default` exempt? | **W4** entirely | Source already implements capability-derived at `session.py:280-293` (`"patch.apply" in harness.verbs`); the named allowlists were deleted. Ruling for statement A ratifies as-built. |
| **C6** | `WorkspaceEpoch` — 4, 7, or 8 components? | **W2b** | W2b defines a candidate identity; shipping it before C6 mints a fourth epoch shape. |
| **C4** | Budget dimensions — FH-D04 four-named, or §23.2 abstract vector? | **W5** | `kernel/budget.py:48` already excludes `depth`/`turns` from `ADDITIVE_DIMENSIONS`, matching FH-D04 against F-10. Ruling for FH-D04 ratifies as-built. |
| **OD-11** | `just verify-full` recipe placement | **W1 tail** | `justfile` is inside C's T-132 lease. W1 can complete without it; the recipe lands through C. |
| **MS-CAS** | Is crash-atomicity a MS-CONTROL prerequisite or a post-control branch? | **W3b** | `milestones.md` MS-CAS is `OPEN [PROPOSAL]` gated behind MS-CONTROL, selected by control-failure attribution. W3b is that row's acceptance text almost verbatim. |
| **OD-7** | Who accepts these packets? | every packet's close | Non-author acceptance required; pool is three and already conflicted. |

Two further items for the Senior, not blockers: the four `docs/execution/main`
blob pins are stale (brief §1.3), so regenerate them **last**, on the final
subject — and three of five `main/` files are already over their CI-only doc
budgets, so W6a must not add lines to them.

---

## W0 — Test-runner instrument repair `WAVE A · no blockers`

**Plan:** Stage 0.1 + 0.2. **Why first:** every other packet's evidence is
measured with this instrument, and it currently misreports.

**Lease:**
- `.agents/skills/test-runner/scripts/run_test.py`
- `.agents/techniques/tdd-falsifier/scripts/run_falsifier.py`
- new fixture dir under `test/tools/` (or the collection the repo uses for tool tests)

**Do:**
1. Replace the summary regex at `run_test.py:71`. It requires `failures=` before
   `errors=` and tolerates no third key, so `FAILED (failures=5, errors=27,
   skipped=17)` fails to match entirely and line 72 falls back to
   `len(failures)` with `errors_count=0`. Parse an order-independent
   `name=count` bag; capture `Ran N tests`; take the **last** summary block
   (stdout and stderr are concatenated at line 52); set `"counts_parsed": false`
   when the fallback is used. **A parse miss must never read as zero.**
2. Fix failure-block association at `:58-68` — split on separator lines first,
   handle the Python 3.11+ header form, stop requiring a `Traceback` header.
3. Fix the timeout kill at `:30-46`: `start_new_session=True`, then
   `os.killpg` SIGTERM → SIGKILL, and bound the post-kill `communicate()`.
   Copy the shape from `adapters/sandbox/rootless.py:122,138`.
4. Fix the inline fallback at `run_falsifier.py:24-36` — it hardcodes
   `timed_out=False` and passes no timeout at all.

**Falsifiers:** every key ordering and combination incl. `skipped`; `OK
(skipped=n)`; errors-only; subTest; expected-failure; empty collection; output
containing the literal `FAILED (`. Timeout: spawn a sleeping grandchild, assert
return at deadline, exit 124, **no descendant survives** (`pgrep -g`).

**Watch:** this defect is a *planted benchmark bug* at
`benchmarks/benchmark_20_suite/08_evaluator_oracle_timeout/src/sandbox_runner.py:17`.
Do not "fix" the benchmark fixture — it is supposed to be broken. Mirror
`test/security/test_sandbox_isolation.py:84` instead.

---

## W2a — Candidate-identity falsifiers `WAVE A · no blockers`

**Plan:** Stage 1.1. Authoring falsifiers needs no ruling; **do not fix
anything in this packet.**

**Lease:** new test files only. No source edits.

**Do:** write three tests that red today against
`GitEnvironment.snapshot` (`git.py:247-278`), which digests
`{"head": ..., "status": ...}` at `:270` — and `git status --porcelain` emits
status codes and paths, not content.

- **A — collision:** write X to `a.py`, snapshot; write Y to the same `a.py`,
  snapshot; assert digests differ.
- **B — degradation:** with a non-zero `rev-parse`, `:259`/`:264` degrade to
  `"unknown"`/`""` and produce a valid-looking constant digest. Assert
  `snapshot()` returns a failed `Result`.
- **C — cross-worktree:** two worktrees at the same HEAD, different dirty
  content, must produce distinct digests.

**Deliver:** the three reds, with output. Then stop. W2b is a separate packet
gated on the C6 ruling.

---

## W3a — Transaction latent defects `WAVE A · no blockers`

**Plan:** Stage 2 preamble only — the three defects found by inspection. This is
pre-control, small, and lease-disjoint. **Do not start the journal, the
publication reference, or the fault-injection matrix** — that is W3b and needs a
leadership ruling.

**Lease:** `vanguard/packages/adapters/environment/transaction.py` and its tests.

**Do:**
1. `_commit` catches only `OSError` (`:159`). A `UnicodeEncodeError` from
   `tmp.write_text` (`:144`) escapes with **no `_restore`**, leaving a partially
   published set. Catch broadly, restore, then fail or re-raise.
2. `_restore` (`:166-176`) rebuilds `self._root / rel_path` raw instead of
   reusing the resolved `dest`, re-running path resolution during recovery.
3. The publish loop indexes `staged` by a parallel `stage_index` counter
   (`:146-154`) whose skip condition must stay byte-identical to the stage
   loop's. Carry the staged path in the tuple instead.

**Falsifiers:** one per defect. For (1), inject a mutation whose content raises
on encode and assert the tree is fully restored.

**Must still pass unchanged:** `test/runtime/test_atomic_multi_file_transaction.py`
(T-17) and `test/adapters/test_str_replace_exact.py`.

---

## W6a — Purity and claim reconciliation `WAVE A · doc-budget caution`

**Plan:** Stage 5.

**Lease:** `tools/linters/check_boundaries.py`, `check_domain_blindness.py`,
`vanguard/packages/domain/workspace.py`, and the claim text.
**Not** `docs/execution/main/*` — three of five are over their CI-only ceilings
and raising one is a governance decision (`check_doc_budgets.py:37-38`).

**Do:** reconcile the stated contract with the enforced one. `check_boundaries.py`
declares `"domain": set()`, yet `domain/workspace.py` does real I/O
(`read_text` `:34`, `mkdir` `:75`/`:95`) and passes only because stdlib specs
resolve to `target_area = None`. Either document the exception with the
allowlist as single source of truth, or route it through a port. Same for
`SUBPROCESS_ALLOWLIST` (`:84-101`) vs. the "confined to adapters/sandbox"
statement. Correct the "mathematically verified" and sub-50ms-retrieval claims
to what is demonstrated.

---

## W1 — Red-fixture repair `WAVE B · after W0`

**Plan:** Stage 0.3. Needs W0 first — you cannot classify failures with an
instrument that miscounts them.

**Lease:** test files under `test/runtime/` and `test/falsifiers/` only.
**Not** `justfile` (C's T-132 lease) — the `verify-full` recipe routes through C
under OD-11.

**Do:** classify each of the 5 failures / 4 errors in `runtime` and 18 / 4 in
`falsifiers` as fixture defect, prerequisite masking, or environmental — then
repair at the fixture level. For tamper tests hitting `INDEX_UNBOUND` before
their assertion (raised at `session.py:1957+`, terminalised at
`engine.py:753-758`), bind the epoch in setup. **The predicate does not change.**
For every repaired test, prove it still reds against its original defect.

**Report:** the classification table. If any failure is a genuine backend defect
rather than a fixture defect, it becomes its own packet — do not fix it here.

---

## W2b — Candidate identity fix `WAVE B · needs C6 ruling`

**Plan:** Stage 1.2 + 1.3. **Do not start before C6 is ruled.**

**Lease:** `adapters/environment/{git,fake,sandboxed}.py`; read-only on
`session.py` and `admission_gate.py` (verify, do not edit — see W4).

**Do:** canonical content-addressed digest over normalized path, entry type,
mode, and content hash, folded in sorted order with length-prefixed framing.
Symlinks digest the target, never follow. **Enumeration error ⇒ failed
`Result`**, never a degraded digest. Reuse `digest_of` from
`domain/canonicalisation/digest.py:17-25`.

**Do not regress:** `snapshot_id` varies with `_snapshot_seq`, the `digest` does
not — the comment at `git.py:266-269` records why (seq in the digest staled
every verification receipt). And `runtime/evidence_capture.py:50-80` must still
mint exactly two tree hashes, not three.

**Note:** `fake.py:124-136` still folds `seq` into its digest and is therefore
*not* idempotent the way git's is. Align it.

---

## W5 — Provider compatibility and accounting `WAVE B · needs C4 + session.py`

**Plan:** Stage 4. Partially startable: 4.1 and 4.2 touch adapters; 4.3 touches
`session.py:480-509`, held by C until T-140 releases.

**Lease:** `adapters/models/{openrouter,routing}.py`,
`runtime/{trajectory,inference_meter}.py`, `agency/episode/protocol_recovery.py`.
`session.py` **only after lease release**.

**Do:** (4.1) route DSML-in-text through the existing `protocol_recovery` seam so
it triggers bounded recovery then authorized fallback instead of a dead session —
any normalization must still pass tool-schema validation. (4.2) persist
provider-reported cost as a separate authoritative observation, not as a
fallback scavenge at `trajectory.py:140-146`; extend the existing
`measurement_status` vocabulary rather than inventing one. (4.3) preserve the
aggregate reservation across retries and fallback — a two-attempt call must
settle the sum, not the last attempt.

**Note:** `InferenceMeter` is already correct in isolation. The defect is
aggregate, not per-call. Do not "fix" `settle`.

---

## W4 — Completion convergence `WAVE B · needs C1 + session.py · THE DELIVERABLE`

**Plan:** Stage 3. This is the acceptance criterion for the whole effort.

**Lease:** `agency/episode/admission_gate.py`, `agency/multi_file_completeness.py`,
`agency/episode/engine.py`, `packs/code-default/middleware/repository/multi_file_completeness.py`,
and `session.py` **after T-140 release**.

**The framing matters:** the structured feedback the evaluation asks for
**already exists and is being discarded.** This is plumbing, not a new feature.

**Do:**
1. `CallerAdmissionVerdict` (`agency/multi_file_completeness.py:131-142`) carries
   `uninspected_callers`, `stale_receipts`, `omissions`, `diagnostics` and
   `consumes_reasoning_retry` — all dropped by the normalisation at
   `session.py:2688-2693`. The pack policy's `rejections` tuple is collapsed to
   `rejections[0]` at `:2667-2678`, so the model learns one obligation per turn.
   Widen `AdmissionVerdict` to carry `reason_code`, `candidate_digest`,
   `missing_obligations` (the full tuple), `required_evidence`,
   `permitted_recovery_actions` — end to end into `engine.py:759-774` and out via
   `_view()["recoveryFeedback"]`. **Preserve every existing reason code.**
2. Honour `consumes_reasoning_retry`: an environment-caused refusal must not
   count against `_no_progress_limit` or the repeated-action ladder
   (`engine.py:515-600`).
3. Terminate immediately once candidate-bound evidence satisfies the predicate.
   If an obligation cannot be resolved under the active index or authority,
   report that blocker and abstain rather than burning finish attempts.
4. Extract the reason vocabulary shared with `ForgeAdmissionGate`
   (`agency/forge/engine.py:102-195`) so the two gates cannot drift. Forge
   already returns rejection text as a *tool result* rather than a termination —
   that shape is closer to correct.

**Acceptance — this is the whole point:** both diagnostic tasks (two-file
refactor; greenfield retry helper) run through `execute_product`
(`benchmarks/product_path.py:28-71`) and reach `COMPLETED`, not
`budget_exhausted` or `abandoned`. Exterior verification in a fresh copy with
original tests restored still passes, oracle files unchanged. Adversarial
control: a receipt bound to a superseded candidate digest is still rejected.
Turn counts drop materially versus the 14-turn and 6-turn traces.

**Feed back to OD-9:** that adversarial control is a partial false-completion
detector. OD-9 records the veto as a release gate with no detector behind it —
a gate with no detector returns zero because nothing looked.

---

## W3b — Crash-safe candidate lifecycle `WAVE C · needs MS-CAS ruling`

**Plan:** Stage 2.1–2.4. Durable journal with `fsync` of file and directory,
deterministic recovery, indivisible publication via immutable candidate
directories plus an atomic reference swap, fault injection at every boundary,
writer fencing, stale-base refusal.

**Do not start** until leadership rules whether this is a MS-CONTROL prerequisite
or stays a post-control branch. `milestones.md` MS-CAS reads "durable immutable
tree capture, exact edit sets, isolated verification and atomic ledger-head
promotion; disk/process fault injection at every persistence boundary;
concurrent winner/loser and ABA tests" — that is this packet, and it is gated
behind MS-CONTROL and selected by control-failure attribution.

W3a already removes the three latent defects, so the pre-control risk is bounded
without pulling this forward.

---

## Parallelism summary

| Packet | Starts | Blocked by | Lease collision |
|---|---|---|---|
| W0 | now | — | none |
| W2a | now | — | none (new tests) |
| W3a | now | — | none |
| W6a | now | — | avoid `docs/execution/main/*` (over budget) |
| W1 | after W0 | — | `justfile` → C/T-132 |
| W2b | after W2a | **C6** | — |
| W5 | after W0 | **C4**, session.py lease | `session.py` → C/T-140 |
| W4 | after W1+W2b | **C1**, session.py lease | `session.py` → C/T-140 |
| W3b | — | **MS-CAS ruling** | — |

Four packets run concurrently on day one. With three developers: Lane 1 takes
W0 → W1 → W4 (the critical path), Lane 2 takes W2a → W2b → W5, Lane 3 takes
W3a → W6a → review. If a fourth is available, W6a splits off immediately.

The binding constraint is not developer capacity — it is the three rulings and
the `session.py` lease. All three rulings (C1, C4, C6) can be made by ratifying
what the source already implements, which costs nothing and unblocks two lanes.
