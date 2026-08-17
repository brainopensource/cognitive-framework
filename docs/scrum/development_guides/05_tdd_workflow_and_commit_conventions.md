# 05 — TDD Workflow & Commit Conventions

**Purpose:** the mechanical loop, so nobody has to invent one.

---

## 1. The loop

```
1. Write the failing test.
2. Run it. Confirm it FAILS, and confirm it fails for the RIGHT REASON.
3. Write the minimum implementation.
4. Run it. Confirm it PASSES.
5. Run the gates (guide 04 §7).
6. Commit.
```

**Step 2 is not optional and not a formality.** A test that passes before you implement anything is
testing nothing. A test that fails for the wrong reason (import error, typo) is not yet a test.

---

## 2. Branch and commit

**Branch:** `sprint<NN>/<lane>-<task-id>` — e.g. `sprint07/lane-a-S7-A-04`

**Commit message:**

```
[lane-<a|b|c|j>] <TASK-ID>: <imperative one-line summary>

<why, if not obvious from the summary>
<rule or ADR being satisfied, e.g. "A-05: the loop must not grade itself">

Refs: REQ-XXX-NNN
```

Examples:

```
[lane-a] S7-A-04: delete MetaLoopEngine (ADR-0064, 011 §8)

It executed subprocess.run on the host with no grant and branched on its own
evaluator verdict, inverting A-05. Salvage: compaction -> S8-B-02, retry -> the
loop itself, tier escalation -> S8-B-03.

Refs: REQ-TRUST-001
```

```
[lane-b] S7-B-01: one alias shape, fail-closed at composition (N-17)

to_canonical fell back to identity, so a misconfigured alias failed at turn 3 as
UNKNOWN_ACTION instead of at composition.

Refs: REQ-HARN-001
```

---

## 3. PR requirements

- [ ] Cites **at least one `req_id`** from the Active MVP Contract. A PR citing none is rejected by
      CI, not by a reviewer
- [ ] States which backlog row it closes (`011` id)
- [ ] Shows the failing-test output **before** the fix
- [ ] All gates green, or a stated reason a gate is intentionally red
- [ ] **Zero** diff in `kernel/**`, `agency/episode/**`, `domain/wire/**` — or an
      `ADR-XXXX core change` label with both leads on review (`BR-5`)
- [ ] No new normative rule added to a `docs/main_v4/` file while a contract row is uncovered
      (`T10.7`)

---

## 4. When to write an ADR instead of code

Write one when a competent engineer arriving in six months would be **surprised** and unable to
reconstruct why.

**Always** for: a `kernel/` change · a reversal of a locked decision · a wire-format change
(`L-1` — irreversible) · a new top-level package · a new extension form.

**Never** for: a decision they would reach unaided. A register of everything is a register nobody
reads.

**Format:** decision · context · **the losing alternative, stated fairly enough that its advocate
would recognise it** · reversal condition · evidence/affected components · owner + status.

> Stating the losing alternative fairly is not courtesy. A register recording only winners cannot
> support a reversal, because the reader has no idea what to reconsider.

---

## 5. Definition of done — a row is `[DONE]` when

1. Its DoD command runs and passes.
2. Its test exists, and it **failed** before the implementation.
3. Gates are green.
4. The backlog row in `011` is updated with the evidence.

**Not when the code exists.** Not when it works locally. Not when the PR is open.

---

## 6. When you are stuck

1. Re-read your lane file's **stop conditions**. Most blockers are already named there.
2. If your task hit a stop condition: **write the finding.** That is a deliverable, not a failure —
   several of Phase 3's most valuable outcomes are stop conditions firing.
3. If a guideline does not answer your question, **that is a defect in the guideline.** Raise it;
   the point of these documents is that you should not need a lead.

---

## 7. The one-paragraph reminder

You are working on an instrument whose product is an honest record of whether machine competence
accumulates. The code will be replaced; the record will not. That is why a refusing test beats a
green one, why a declared lab departure beats a clean-looking number, and why deleting 1,500 lines
can be the highest-value sprint in the programme.
