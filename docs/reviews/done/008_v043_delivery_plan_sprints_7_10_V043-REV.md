# 008 — The Corrected v0.4.3 Delivery Plan: Sprints 7–10

**Status:** NON-NORMATIVE programme proposal. Supersedes
`docs/reviews/done/2026-08-16-phase-3-sprints-7-10-blueprint.md` on adoption.
Owns sequencing and rationale only; contracts remain with the v4 set, merge gating with the
Active MVP Contract (`ADR-0046`, `GTS-13C` document map).
**Date:** 2026-08-16 · **Branch/HEAD:** `sprints7-8/integration` @ `0238b1a`
**Authority cited:** `GTS-13C` Ch. 10 (the four gate questions), Ch. 15, `ADR-0057`, `ADR-0058`.

---

> **AMENDMENT (2026-08-16).** This plan's themes and gates stand. Two changes from `009`:
> (a) sprints are now carried under **Waves W6–W9**, continuing the Sprint 6B wave numbering
> (`todo_list.md` W0–W5) rather than restarting — see `011`;
> (b) the packet decomposition from `vanguard_LAM_manifests_plan_sprint-7-to-9.md` (Packets 0–14,
> each with an explicit *"may start when"* and stop condition) is **adopted** in preference to this
> document's flatter lane lists. `011` is the executable form; this document remains the rationale.
> Nine findings from `009 §3.1` that appear in no report here are added to `011`, including
> **`SEC-01` secret history, which is not closed** (`007 §6` correction).

## 1. What changes, and why

The existing Phase-3 blueprint plans a **demo**. `GTS-13C` Ch. 10 gates an **instrument**.
`ADR-0057` already ruled that Beta = Q1+Q2 at S6 and that **S7–S9 keep Q3+Q4**. The blueprint
contains neither Q3 nor Q4 (`001 §3.13`).

This plan restores them, and reorders the work by one principle:

> **Subtract before you add. Measure before you claim. Recurse before you generalise.**

Three consequences, stated plainly so they can be argued with:

1. **Sprint 7 is a consolidation sprint, not a feature sprint.** Roughly 1,500 lines are deleted
   and three architecture rules are added. Nothing new ships. This is the correct use of the
   "we've spent 0.1% of budget" window.
2. **Sprint 10 does not tag a release on a green test suite.** `GTS-13C` Ch. 10 is explicit:
   *"Tickets merged, CI green, and a demo that worked once do not close it."* The gate is four
   questions with named evidence.
3. **The competence graph, operator registry and playbook engine are not in this plan.** Their
   triggers (`O-01`, `O-03`) have not fired and cannot fire until an A/A floor exists (`004 §2`).
   Building them now is the premature formalisation `VG-02 §8` warns against.

---

## 2. Scope ruling: what v0.4.3 is and is not

| | |
|---|---|
| **v0.4.3 IS** | One framework, one honest instrument, one harness (`vg-code-default`) plus the permanent control (`vg-shell-only`), recursion real, manifests load-bearing, one A/A floor number, one non-coding environment |
| **v0.4.3 IS NOT** | A competence graph · an operator registry · playbooks · an offline optimiser · MCP · A2A · a GUI · multi-tenant · training on the corpus |
| **v0.4.3 CLAIMS** | Q1 fully · Q2 with evidence · Q3 with a floor and one paired comparison · Q4 with a line-count measurement |
| **v0.4.3 DOES NOT CLAIM** | That the harness improves outcomes (that needs the floor first, then a powered comparison) · that competence accumulates (`C-06` is not in scope) |

---

## 3. Sprint 7 — **Subtraction & Boundary Restoration** (2 weeks)

**Theme:** make the tree's behaviour match the tree's description.
**Exit test:** every effect in every executable path in the repository traverses `Kernel.dispatch`,
proven by an architecture test that fails against a broken counterpart.

| Lane | Items | From |
|---|---|---|
| **A · Enforcement** | Three boundary rules: lattice completeness · `benchmarkings/` import restriction · `subprocess` confined to `adapters/sandbox/`. Each with a `test/broken/` counterpart | `007 §8`, `003` A1–A3 |
| **A · Deletion** | `runtime/loops/` · `coordination.py` · four bypassing benchmark runners · `_WitnessKernel` · `workflow_visualizer.html` | `007` X1–X4 |
| **A · Honesty** | Remove hardcoded `bwrap` path, approval threshold, reservation, `... or 100`; justify or remove the two bare excepts | `007` X5 |
| **B · Manifest repair** | Fix 3 alias failures · one canonical alias shape · **fail-closed alias validation at composition** · **"an unread component is a composition error"** · metamorphic policy-digest test | `005` H1–H4 |
| **B · Measurement guard** | `benchmarkings/guard.py` refusal conditions + broken counterparts · retraction sweep · promote `zero_hint_v1` to the sole benchmark entrypoint | `002` M1–M4 |
| **Joint · Governance** | `ADR-0063` (ratify Python, reverse `ADR-0001`) · amend `VG-02 §9` · record corrections in `VG-09 §4` · adopt the review WIP limit | `006` S1–S2, `007` X10 |

**Sprint 7 exit gate — all must be true:**

- [ ] `507+` tests green, zero failures, zero errors (node available for `SC-7`, or the refusal explicitly waived with a dated ticket)
- [ ] Architecture tests prove: no second loop, no `subprocess` outside the sandbox adapter, no evaluator import in `agency/` or `runtime/`, no package outside `LT-1…LT-8`
- [ ] Each of the three new rules **fails** against its planted broken counterpart
- [ ] Every retained benchmark artifact carries an evidence-class label; every retracted one carries a `RETRACTION.md`
- [ ] A planted degenerate run (`pre_passed=true`, `patch_length=0`) is **refused** by the scorer
- [ ] Composition fails on an alias whose target is not a declared verb
- [ ] Composition fails on a manifest component no consumer reads
- [ ] `ADR-0063` merged; `VG-02 §9` no longer states a false stack

**Net: ~−1,500 LOC. Zero features. Q1 restored.**

> The argument that will be made against this sprint — *"we're deleting a whole sprint's output"*
> — is the signal that the work is necessary. `GTS-13C` Ch. 14: *"Anyone argues to keep it… the
> argument to keep it is the signal to delete it faster."* That rule was written for `spike/` and
> `slice/`; it applies verbatim here.

---

## 4. Sprint 8 — **Recursion, Resume & Load-Bearing Manifests** (2–3 weeks)

**Theme:** make the architecture's central claim real.
**Exit test:** a parent episode spawns a child under an attenuated grant and a child lease; the
child's exploration never enters the parent's context; the whole thing is reconstructible from
the ledger alone.

| Lane | Items | From |
|---|---|---|
| **A · Session** | Decompose `execute_harness` → `compose / HarnessSession / run`. **One `Kernel` per run.** Ports injected | `003` A7 |
| **A · Resume** | Approval suspension becomes suspend-with-continuation inside the engine; re-entry reduces the ledger for that `episodeId`; delete the segment loop. `max_turns` and no-progress detection survive an approval | `003` A9 |
| **A · Determinism** | `RandomPort` + determinism-complete `ClockPort`; `Recording` wired so replay is byte-identical | `004` G3 |
| **B · Recursion** | `EpisodeEngine.spawn`: child scope ⊆ parent (existing attenuation), child lease (existing `Governor`), `depth` as a real budget dimension, child events carry `causationId`, return is text/payload never a handle, workspace destroyed in `finally` | `003 §3.4` |
| **B · Isolation** | `operator_isolation`: child gets a fresh compiler prefix; only the return enters the parent's L5 | `VG-03 §10.3` |
| **B · Policies real** | `CompactionStrategy` protocol + registry (`result_eviction`, `recency_window`); `ModelRouter` protocol + registry; `approval_policy` component. All selected by manifest, frozen at composition | `005` H5–H7 |
| **B · Depth projection** | Depth labels as a ledger projection, replacing the deleted SQLite table | `003 §4` |
| **Joint · Evidence format** | `Claim` as a `domain/` type: non-empty invalidation at parse, ≥1 **automatic** condition (substrate-digest change), `support_count`/`last_corroborated_at` recorded-not-consumed | `004` G1–G2 |

**Sprint 8 exit gate:**

- [ ] Property test: child grant is a strict subset of the parent's on verb, selector, constraints, expiry, uses and budget
- [ ] Property test: budget conserved across a two-level spawn; a child overrun debits the parent
- [ ] Test: a child's intermediate turns are absent from the parent's compiled context; only the return appears
- [ ] Test: an episode suspended for approval and resumed reconstructs an identical `state_digest` **from the ledger alone**, with no live object carried across
- [ ] Test: `max_turns` is a hard bound across an approval boundary
- [ ] Metamorphic test: changing `context_policy` digest changes an observable; changing `routing_policy` digest changes the model selected
- [ ] `Claim` with an empty invalidation array fails at parse; a claim whose substrate digest changed evaluates as stale **without human review** (`C-12`)
- [ ] Cache-hit-rate measured over a fixed replay, recorded as a CI metric (`006` S5)

---

## 5. Sprint 9 — **The Instrument** (2–3 weeks)

**Theme:** produce one number nobody can argue with.
**Exit test:** an A/A noise floor exists per task class against `vg-shell-only`, and the runner
refuses to report when the design is degenerate.

> **Note the reassignment.** The previous plan's Sprint 9 was "Meta-Harness Loop Engineering &
> Self-Correction" — the loop that grades itself. That work is deleted in Sprint 7 and its three
> useful ideas re-land as data in Sprint 8. Sprint 9 becomes what `ADR-0057` said S7–S9 were for:
> **Q3**.

| Lane | Items | From |
|---|---|---|
| **A · Floor** | A/A runner: identical manifest against itself, N repeats, ≥3 task classes, per-class floor with CI. **Refuses when any arm is degenerate or the floor is zero** | `002` M6 |
| **A · Pre-registration** | Hypotheses, primary metric, alpha, correction, manifest digest, stopping rule — hashed **before any arm runs**, enforced in CI | `002` M5 |
| **A · Statistics** | McNemar exact (paired binary), paired bootstrap (cost/latency), survival methods (timeouts/censoring) | `002` M7 |
| **B · Splits** | `DEV/HOLDOUT/SEALED/LIVE/DEPLOYMENT` + touch ledger + per-instance membership check | `002` M8 |
| **B · Oracle hardening** | Isomorphic-oracle perturbation per task class; seeded-sabotage suite (planted proxy-exploiting candidates must be rejected) | `002` M9–M10 |
| **B · Reconstructions** | Rebuild `claude-shaped` / `opencode-shaped` / `swe-mini` so they **actually differ** on ≥3 of the ten dimensions (`005 §2.3`), now that compaction/routing/approval are real. `vg harness build \| run \| diff \| bench` | `005` H9–H10 |
| **Joint · Dogfood** | Three real bugs in a repository someone knows well, fixed interactively, no hand-patching mid-run. Corrections captured with reason codes (`T6.7`) | `GTS-13C` Ch. 10 Q2 |

**Sprint 9 exit gate:**

- [ ] A per-task-class A/A floor number exists, with N and MDE derived from it and recorded
- [ ] The floor runner **refuses** on a planted degenerate configuration
- [ ] One paired comparison runs end to end and reports an effect with an interval, pre-registered and hashed before the first arm
- [ ] Per-arm instrument-error rate reported; asymmetry flagged
- [ ] A seeded proxy-exploiting candidate is rejected by the pipeline
- [ ] Three real bugs fixed interactively, and the honest answer to *"next time, would you reach for it?"* is recorded — **including if it is no**
- [ ] The three reconstructions produce **different behaviour**, demonstrated, not asserted

> **Expect the floor to be large.** The 2026 field measures 9.5–20 points of harness-only
> variance on fixed models (`002 §1`). If our floor swallows the deltas we intended to claim,
> that is the finding, it arrives early, and it is cheap. `RSK-06` requires we act on it rather
> than raise N until something is significant.

---

## 6. Sprint 10 — **Generality & The Gate** (2 weeks)

**Theme:** falsify the generality claim cheaply, then answer the four questions.
**Exit test:** a non-coding environment runs, and the number of lines changed in `kernel/` and
`agency/episode/` to add it is **measured and published, whatever it is**.

| Lane | Items | From |
|---|---|---|
| **A · Domain de-capture** | Move verb/args/selector binding out of `adapters/models/invocation.py` into the manifest capability row. `invocation.py` holds zero domain knowledge | `003` A11, `005` H8 |
| **A · TableWorld** | Versioned tables; `select/derive/update/validate`; constraints over sums, uniqueness, ranges; **no version control, no shell, no paths as a domain concept**; deterministic evaluator over invariants | `VG-03 §7.3`, `T9.1–T9.3` |
| **A · The core-change detector** | CI counts lines changed in `kernel/` and `agency/episode/` to add a domain. The count is the `C-10` measurement | `T9.3` |
| **B · `vg why`** | `vg why <artifact>`: what evidence activated it, what it predicts, what would demote it | `T6.5` |
| **B · Ports completion** | `BlobStorePort`, `IndexPort` | `004` G3 |
| **B · Structured consolidation** | `structured_consolidate` emitting `StructuredRecord` with `deadEnds`; consolidation-quality measured by transcript-replacement replay | `004` G6 |
| **B · Re-grounding** | `regroundPolicy` as an **authorised observation effect**, not a side channel | `004` G7 |
| **Joint · Gate** | The four-question review, with named evidence per question | `GTS-13C` Ch. 10 |

**Sprint 10 exit gate — the actual MVP gate, verbatim from `GTS-13C` Ch. 10:**

| # | Question | Required evidence |
|---|---|---|
| **Q1** | Is the boundary real? | Red team reaches neither control plane, evaluator, nor secrets. Every must-fail test fails against its broken counterpart. Kill and restart preserve the known/uncertain distinction. No second execution path exists, proven by architecture test |
| **Q2** | Is it useful? | Three real bugs fixed interactively without hand-patching. The recorded answer to *"would you reach for it again?"* |
| **Q3** | Is it measurable? | A/A floor per task class against `vg-shell-only`. One paired comparison. A verifier–deployment gap number (or a written statement of why it is not yet computable, with a date) |
| **Q4** | Is it general? | The non-coding environment was added, and the measured line count changed in `kernel/` + `agency/episode/` is published |

**If Q4's count is non-zero, that is a finding, not a failure** — `VG-03 §7.3` says building
TableWorld early exists precisely to falsify generality *"early, cheaply, and therefore
usefully."* Record it, write the ADR, and adjust. A zero count is a strong claim; a small
non-zero count with a published diff is an honest one. Only a *hidden* non-zero count is a
failure.

---

## 7. What is explicitly deferred, with triggers

Per `GTS-13C` Ch. 3. Writing these now would formalise guesses.

| Item | Trigger |
|---|---|
| Competence graph $G_C$, activation topology, promotion/demotion | `O-01` — **one distilled artifact clears the A/A floor.** Derive the lifecycle from the survivor |
| Operator registry as data, activation sets, operator selection policy | `O-03` — a real task needs depth the `spawn` mechanism cannot reach |
| Playbooks + rigidity dial | after the operator registry |
| Offline optimiser, progressive-vs-degenerating ratio | after counterfactual re-execution (Sprint 8 `RandomPort`) **and** the floor |
| MCP adapter | post-v0.4.3, under the three rules of `006 §4.4` (pre-recorded as an ADR in Sprint 7) |
| A2A | an external peer agent exists |
| Parallel branch exploration, independence groups, rankers | after serial recursion and a floor — `C-04` is unmeasurable without one |
| Systems-language components | a measured threshold from `006 §3.1`, crossed on a real repository |
| Training on the corpus | `O-06` — opt-in, licensing, contamination tracking, adversarial verifier audit all exist |

---

## 8. Capacity, risk and the honest schedule

**8–10 weeks** at the current two-senior-lane model (`todo_list.md` §2), assuming the lanes hold.

| Risk | Early signal | Mitigation |
|---|---|---|
| **Sprint 7 is resisted as "deleting a sprint"** | Anyone argues to keep `runtime/loops/` | `GTS-13C` Ch. 14 — the argument is the signal. Escalate to Tech Lead + Project Lead jointly, decide once, record the ADR |
| **The A/A floor is larger than the deltas we hoped to claim** | Floor CI overlaps every planned effect | This is a **result**. Publish it. Reduce claim ambition, not the floor (`RSK-06`) |
| **Q4 line count is non-zero** | TableWorld touches `agency/episode/` | Publish the diff. `C-10` falsified early is the cheapest outcome available |
| **Recursion slips** | `spawn` not merged by end of week 3 of S8 | It reuses existing attenuation and `Governor` — if it is slipping, the cause is `execute_harness` decomposition, not recursion. Reorder |
| **Review accumulation resumes** | An eleventh audit appears | WIP limit of 8 in `docs/reviews/doing/` (`007 §5.2`) |
| **Scope creep from the competence graph** | Any PR mentioning $G_C$, operators or playbooks | `O-01`/`O-03` triggers cited in the PR template; a PR without a fired trigger is rejected by CI, not by a reviewer |

---

## 9. The one-paragraph version, for the CTO and stakeholders

> We built the hard, irreversible half of this system correctly — the capability kernel, the wire
> contracts, the canonicalisation, the ledger, the sandbox boundary — and it is genuinely ahead
> of the field. Under delivery pressure we then built the visible half twice: once properly
> through that kernel, and once quickly around it, and we measured the quick one. The quick path
> grades its own work and executes code outside the sandbox, and several of our published-looking
> results scored tasks that had already passed before the agent acted. The fix is roughly two
> weeks of deletion and eight weeks of the work the specification already called for, and it ends
> with something no competitor has: a harness that ships with its own evidence ledger and one
> honest number for how noisy that ledger is. We are asking to spend Sprint 7 removing code
> rather than adding it, and to stop publishing the affected numbers today.

---

## 10. Traceability

| Sprint | GTS-13C tasks | Gate questions | Reports |
|---|---|---|---|
| S7 | T10.1, T10.3, T10.4, T7.3, T8 (guards) | **Q1** | `002` M1–M4, `003` A1–A6, `005` H1–H4, `007` X1–X5, `006` S1–S2 |
| S8 | T4.4, T4.6, T4.9, T4.10, T3.6, T1.9, T1.11 | **Q1, Q2** | `003` A7–A10, `004` G1–G3, `005` H5–H7 |
| S9 | T8.1–T8.8, T7.5, T7.6, T6.7 | **Q2, Q3** | `002` M5–M11, `005` H9–H10 |
| S10 | T9.1–T9.3, T6.5, T4.9 | **Q3, Q4** | `003` A11–A12, `004` G6–G7, `005` H8 |
