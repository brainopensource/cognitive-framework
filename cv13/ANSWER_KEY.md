# CV-13 — Answer Key

> **Held by the Tech Lead. Not distributed with the reader packet.** Do not consult it until the reader has submitted. Scoring the reader against a key they have seen tests recall, not sufficiency.

Each answer below cites where in the v4 set a reader is expected to find it. **If the citation does not support the answer, the key is wrong and the document is the defect** — correct the document, not the key.

---

**Q1 — Authority.** `04` is normative for descriptor normalisation (`04 §5.5 [D-1…D-6]`). The reader knows it is the only one because `00 §2` assigns exactly one owning document per contract, and `00 §1 [PR-1]` forbids any other document from restating it. On finding a conflict: `00 §1 [PR-4]` — a disagreement between v4 documents is a defect in owner assignment, fixed by deleting the duplicate, **not** by ranking the documents.

*Score 2 requires all three parts, especially PR-4. A reader who says "the registry decides which wins" has the common wrong model and scores 1.*

---

**Q2 — Closure** (`07 §1`).

- `CL-1` **judge exteriority** — the verifier is unreachable by anything it judges. Violated → reward hacking; the system optimises the measurement. **Architectural** (`05 §7`, `06 §4.2`).
- `CL-2` **evaluation exteriority** — the promotion task set is disjoint from the optimisation set. Violated → training-set scoring; improvements that do not replicate. **Protocol** (`07 §5.7`).
- `CL-3` **noise exteriority** — the observed delta exceeds the A/A floor. Violated → publishing noise; a random seed presented as a design insight. **Protocol** (`07 §5.4`).

*Score 2 requires the architectural/protocol split. Naming three conditions without it scores 1.*

---

**Q3 — Self-modification** (`05 §7 [SA-1…SA-6]`, `07 §7`). Permitted: produce a **candidate artifact** in an ephemeral workspace, sharing no writable mount with the evaluator. Prohibited: touching the live runtime's files, configuration, keys or process; in-place modification of any running component; autonomous promotion of `R0`/`R1`.

**Why passing tests do not license it:** a process that rewrites its own running components cannot verify the result *using the components it just rewrote*. The failure is undetectable from inside, so the strength of the test suite is not the relevant variable — the verifier's position is. Promotion therefore moves an activation pointer (`07 [M-21]`) and never writes over a running component.

*Score 2 requires the "cannot verify itself with what it just rewrote" reasoning. "Because it's risky" scores 0.*

---

**Q4 — Authorisation** (`04 §5.1`, `05 §1.3 [S1(a)]`). A verb-only set is a **verb lattice**: it cannot express *which* resource. Under verb-only attenuation, a child attenuated to "read-only" can read **the evaluator bundle, the policy configuration and the signing keys** — all read-class, all permitted. That is `CL-1` defeated through a permission model, not through a bug. The fix is resource-scoped grants (`04 §5.2`) with a decidable inclusion relation (`04 §5.3.1 [CT-52]`).

*Score 2 requires a concrete resource the "read-only" child should not reach. A generic "too broad" answer scores 1.*

---

**Q5 — Evidence** (`06 §4.1 [V-01]`, `02 [NC-05]`). Established: **conformance to that instrument, under that protocol, in that environment.** Not established: semantic correctness, generalisation beyond the tested distribution, or absence of untested regressions.

It changes reporting because a claim is scoped to its predicate: the correct statement is *"the suite passed under protocol P"*, never *"the change is correct."* A stronger claim overstates the instrument, and once it enters the evidence graph, everything downstream inherits the overstatement.

*Score 2 requires the scoped-claim framing, not merely "tests can be wrong."*

---

## Recording the outcome

| Field | Value |
|---|---|
| Reader | *name, role, prior exposure* |
| Date | |
| Q1…Q5 | *score and note per question* |
| Verdict | **PASS** only if all five score 2 |
| Findings | *anything needed and not found; any apparent contradiction* |

File the completed record at `cv13/RESULT.md`. **A failed gate is a normal outcome and is not a setback** — it is the cheapest defect discovery available at this stage.
