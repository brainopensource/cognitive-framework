# CV-13 — Comprehension Gate: Reader Packet

**You are the gate.** This is not a review of whether the documents are good. It is a test of whether they are *sufficient*: can an engineer who did not write them reach the right answers using only the documents?

If you cannot answer a question, that is a finding about the documents, **not about you.** Say so plainly. A wrong or absent answer here is worth more to this project than a generous one.

---

## Eligibility

You must not have authored, reviewed or edited any v4 document. If you have read earlier drafts, say so before starting — prior exposure does not disqualify you, but it must be recorded.

## Materials

You may use **only** these thirteen files, plus `schemas/v4/`:

```
docs/v4/00_vanguard_registry_v040.md          … 12_vanguard_vision_annex_v040.md
schemas/v4/*.schema.json  ·  schemas/v4/vectors/  ·  MANIFEST.md  ·  README.md
```

You may **not** use: the pre-v4 documents, the git history, any conversation with an author, or any summary of the above. If you need something outside this set to answer a question, **that is the finding** — record what you needed.

## Conditions

Untimed; two to four hours is typical. Answer in prose. No answer key is provided to you — one exists and is held separately by the Tech Lead, and it is not consulted until you have submitted.

---

## The five questions

**Q1 — Authority.** You need to change how effect descriptors are normalised. Which document is normative for that, how do you know it is the only one, and what would you do if you found a second document stating a conflicting rule?

**Q2 — Closure.** Name the three closure conditions of the improvement loop. For each: state it, say what fails when it is violated, and say whether it is enforced architecturally or by protocol.

**Q3 — Self-modification.** What is the system permitted to do to its own components, and what is it prohibited from doing? Explain *why* the prohibition holds even if the system's tests all pass.

**Q4 — Authorisation.** Why is a permission set over verbs — read, write, execute, network — insufficient? Give a concrete example of an attack it permits.

**Q5 — Evidence.** A test suite passes. What has been established, and what has not? Explain why the distinction changes how a result may be reported.

---

## Scoring

Each question is scored on a three-point scale.

| Score | Meaning |
|---|---|
| **2 — Sufficient** | Answer is correct in substance and the reader can point to where in the set they found it |
| **1 — Partial** | Core idea present but a load-bearing element is missing, or the reader could not locate the source |
| **0 — Insufficient** | Wrong, absent, or reconstructed from outside the set |

**Pass condition: every question scores 2.** Not an average, not a majority.

This is deliberately strict. Each question targets a property whose misunderstanding has already caused a real defect in this project's history, so a partial answer means a future engineer will make the same mistake with the documents open in front of them.

**A score of 0 or 1 is a document defect.** The owning document is corrected, and the gate is re-run with a different reader — never with the same reader after coaching, which would test the coaching rather than the documents.

---

## Submission

Return: your answers; for each, where in the set you found the basis; anything you needed and could not find; and any point where two documents appeared to disagree.

That last item is the most valuable thing you can report. The set is built on the premise that exactly one document is normative per contract, and you are the first reader positioned to falsify it.
