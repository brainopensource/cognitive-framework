# 04 — Testing Doctrine

**Purpose:** what to test, in which family, and the one pattern that matters most.
**Owner:** `GTS-13C` Ch. 8, `VG-01`.

---

## 1. The rule everything else serves

> **`A-10`: A gate that cannot fail is not a gate — and a requirement that cannot be satisfied is
> not a requirement.**

Every fix ships a test **proven to fail against pre-fix code**. Every requirement is checked for
physical satisfiability **before** a test is written for it.

This is not process theatre. The prototype's prompt-injection defence was unreachable dead code —
an accumulator reset each round meant the predicate evaluated over a set that could not contain
untrusted content by construction. **The invariant was documented, tested, and did nothing.**

> *An invariant whose test cannot fail against a broken implementation is a comment.*

---

## 2. The six families

Coverage is satisfied by **any** of them. Demanding must-fail coverage for every rule produces
ceremonial tests.

| Family | Proves | Write it when |
|---|---|---|
| **Must-fail** | The control can fail | You add a control, gate or guard |
| **Architecture** | A path does **not** exist | You add a boundary rule |
| **Property** | An algebraic law holds | You touch attenuation, budget, selectors, reduction |
| **Conformance** | Two implementations agree | You touch the wire format |
| **Fault injection** | Every failure path recovers | You add a dispatch stage or an I/O seam |
| **Adversarial** | The threat model is real | You touch authority, approval or containment |

Plus two statistical families that are **not** unit tests: **A/A** (noise floor) and **paired
comparison** (effect estimation).

---

## 3. The broken-counterpart pattern

`test/broken/` holds deliberately broken implementations. Every must-fail test runs against its
broken counterpart **and must fail**.

```
1. Write the broken implementation first.
2. Run the test against it → MUST FAIL. If it passes, your test is a comment.
3. Write the real implementation.
4. Run the test against it → MUST PASS.
5. Register the counterpart so `tools/run_broken_tests.py` keeps checking it.
```

**Step 2 is the entire value.** Skipping it produces a test that documents an intention.

---

## 4. Property laws you can assert directly

| Law | Where |
|---|---|
| Attenuation is **monotone** — a child grant only narrows; no widening fixpoint | `kernel/attenuation.py` |
| Budget is **conserved** — child leases sum within the parent's remainder; overrun debits negative | `kernel/budget.py` |
| Selector inclusion is **reflexive, transitive, antisymmetric-up-to-equality**, and **denies every undefined pair** | `domain/selectors/` |
| Reduction is **associative over batches** | `domain/ledger/reducer.py` |
| Replay yields an **identical state digest** | `runtime/ledger/` |
| Canonicalisation round-trips; `parse ∘ render = identity` | `domain/canonicalisation/` |
| An interrupted process **resumes to the same state** without re-running any episode | `runtime/governance/` |
| Leases release on **every** path, including creation failure | `kernel/dispatch.py` `finally` |

---

## 5. Instruments that refuse

The best-designed tests in this repository **refuse to run** rather than passing vacuously:

- `test/contracts/readers/__init__.py:40` raises `ReaderUnavailable("node is required: SC-7
  evidence needs both readers, and a run without the TypeScript reader proves nothing about
  cross-language agreement")`. It does **not** skip.
- `EVALUATOR_BINDINGS` has **no** `FakeEvaluator` row, deliberately: *"absence is inconclusive, not
  a pass."*

**Copy this instinct.** A skipped test reads as green on a dashboard. A refusing test reads as what
it is: an unproven claim.

---

## 6. What must never happen in a test

| Anti-pattern | Why |
|---|---|
| A test asserting a stub returns `ok` | Certifies the stub, not the behaviour |
| `assertTrue(True)` after an exception is swallowed | The failure path is untested |
| A must-fail test with no broken counterpart | A comment |
| Marking a row `covered` without a named passing test | The exact failure the contract exists to prevent |
| A test that passes only because it injects the thing under test | E.g. `test_meta_loop.py` injected `test_runner`, masking a `NameError` on the default path |
| A benchmark asserting `oracle_passed` without checking `pre_passed` | Vacuous pass |

---

## 7. Before you open a PR

```bash
python3 -m unittest discover -s test -t . -q     # no new failures
python3 tools/check_boundaries.py                # lattice holds
python3 tools/check_tcb_budget.py                # kernel within budget
python3 tools/run_broken_tests.py                # counterparts still fail
python3 tools/scan_secrets.py --all-refs         # strict mode, always
```

Plus: your new test **fails** against a broken implementation. Show that in the PR body.
