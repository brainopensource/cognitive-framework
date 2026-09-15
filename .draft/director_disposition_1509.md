# Director Disposition — Wave B Unblock

**Subject:** `d614e5ce`. **Ledger:** `.draft/todo/ruling_ledger_1509.md`.
Answers the four items the dispatch put to the Director.

---

## 1. C1 / C4 / C6 — RULED, by ratification

All three ratify what the source already implements. Verified in source, not
asserted:

- **C1 RULED for capability-derived.** `runtime/session.py:admission_required`
  returns `"patch.apply" in verbs`, and its docstring records that both
  `ADMISSION_GATED_HARNESSES` and `ADMISSION_GATE_EXEMPT` are gone, naming the
  failure mode: "two name sets and a predicate could disagree and the names
  silently won." `spec.md:1120` and `:2216` already agree. **`spec.md:1953` is
  the single stale statement.** → **W4 unblocked on the ruling.**
- **C4 RULED for FH-D04.** `kernel/budget.py:ADDITIVE_DIMENSIONS` is exactly
  `{usd_micros, millis, tokens, bytes}`, with a comment naming sibling-summing
  of `depth`/`turns` as defect `F-10`. → **W5 unblocked.**
- **C6 RULED: three identities, separately bound.** Not a field-count dispute.
  → **W2b unblocked**, and W2a's falsifiers already red against the collapsed
  form.

## 2. OD-11 — RULED as sequenced, not as placement

`check_doc_budgets` + `check_stale_paths` attach to `docs-check` (inherited by
`check` and `verify`) **only after** the three execution documents are under
ceiling. Wiring the gate while nine files fail would red every in-loop gate on
files nobody is authorized to touch. Ceilings are never raised to obtain green.

**Amendment to the dispatch:** W1's tail proposed a `just verify-full` recipe.
That is the same surface and the same lease. It lands through C under T-132,
after the ceiling work — not with W1.

## 3. MS-CAS / W3b — NOT pulled forward

The directive's explicit non-actions forbid a CAS journal. W3b stays blocked.

Resolving the apparent tension with the authorized *Isolated child workspace
lifecycle* packet, whose falsifiers include crash-during-mutation: **falsifier
authoring is authorized; journal implementation is not.** Evidence targets may
be written and red; no CAS algorithm, wire schema or journal format is approved.

W3a has landed the three latent defects, so pre-control risk is bounded without
the journal. Two residuals are recorded rather than fixed, both W3b-adjacent:
a parent directory created during staging survives rollback, and crash-atomicity
across the publish loop remains absent by design.

## 4. Lease and acceptance — TWO GAPS, RECORDED NOT SIGNED

- **`session.py` T-140 release date: unknown.** C retains the lease until
  explicit release. No date is supplied, and the directive forbids manufacturing
  one. **W4 and W5(4.3) remain blocked on the lease, not on a ruling.**
- **No independent acceptor exists for this session's work.** W0's repair, W2a
  and W3a were authored or materially supplied by one actor. Under OD-7's
  binding condition these are **LANDED / acceptance pending**, never accepted.
  Leadership owns the appointment of a qualified uninvolved acceptor; the Senior
  records the gap instead of inventing a signature.

## 5. Corrections to the directive itself

1. Subject is `d614e5ce`, not `1a2cb2b6`.
2. The C1 exemption is at **`spec.md:1953`**; `:1885` is a `TransformSpec` block.
3. **Step 2's data-flow rewrite is a no-op.** `docs/architecture/data-flow.md:87`
   already carries the full 14-stage sequence with `S8a` and "Durable intent
   always precedes the physical effect." No edit was made; manufacturing one
   would be a false receipt.
4. **Step 2 collides with OD-11.** It instructs the Senior to edit `spec.md`
   while T-132 scopes that file to C. The C1 correction serializes through C, or
   T-132 is explicitly narrowed. Not edited here.

## 6. Dispatch state

| Packet | State |
|---|---|
| W0 | green — LANDED / acceptance pending |
| W2a | red falsifiers delivered, committed `d614e5ce` |
| W3a | green — LANDED / acceptance pending |
| W1 | **ready** (W0 done); recipe tail defers to C |
| W2b | **ready** (C6 ruled) |
| W5 (4.1, 4.2) | **ready** (C4 ruled); 4.3 lease-blocked |
| W4 | ruling satisfied; **lease-blocked** on T-140 |
| W3b | **not authorized** |
| W6a | ready, unassigned |
