# Sprint 7 · Lane A — Control Plane

**Owner:** Senior Developer A · **Backlog:** `011 §4.1`
**Write scope:** `tools/check_boundaries.py` · `tools/repo_paths.py` ·
`vanguard/packages/runtime/**` · `test/runtime/**`
**Do not touch:** `kernel/**` · `agency/episode/**` · `benchmarkings/**` · `docs/main_v4/**`

---

## Invariants for this lane

1. **Zero kernel mutation.** `vanguard/packages/kernel/` is frozen this sprint. If a task appears
   to need a kernel change, stop (§stop conditions).
2. **Deletions are deletions.** No `_deprecated`, no commented-out blocks, no `if False:`. Git is
   the archive.
3. **Every new rule ships with a broken counterpart that fails.** A gate never proven able to fail
   is not a gate (`A-10`).

---

## S7-A-07 — Repair restructure breakage · **START DAY 1**

The `docs/agile` → `docs/scrum` restructure left dangling references. Three tests fail for this
reason alone, and they pollute the baseline everyone else measures against. Fix first.

**Failing now:** `test_repo_root_from_this_file`, `test_three_oracles_are_digest_bound`,
`test_registry_does_not_claim_runs_were_completed`.

- [ ] **Step 1** — reproduce
  `python3 -m unittest test.test_repo_paths -v` → expect FAIL referencing `docs/agile/sprint0`
- [ ] **Step 2** — `tools/repo_paths.py`: replace the `docs/agile` sentinel with `docs/scrum`,
      keeping the dual-layout fallback that already exists for `docs/v4` vs `docs/main_v4`
- [ ] **Step 3** — update the three test fixtures to the live layout
- [ ] **Step 4** — `python3 -m unittest discover -s test -t . -q` → **2 failures / 15 errors**
      (the alias failures + node readers; Lane B closes the rest)
- [ ] **Step 5** — commit `[lane-a] S7-A-07: repair repo_paths after docs/scrum restructure`

**DoD:** the baseline is restored to a known 2F/15E before any deletion lands, so later diffs are
attributable.

---

## S7-A-01 · S7-A-02 · S7-A-03 — The three boundary rules

**Read first:** `tools/check_boundaries.py` is already `ast.parse`/`ast.walk` and table-driven.
Line 32's comment — *"a gap in this table rather than a property of the architecture"* — is the
design intent. **You are adding rows, not a checker.**

### S7-A-01 — Lattice completeness

- [ ] **Step 1** — failing test: create `vanguard/packages/rogue/__init__.py`, run
      `python3 tools/check_boundaries.py` → currently **PASSes**. That is the defect.
- [ ] **Step 2** — add the rule: any top-level package under `vanguard/packages/` not named in
      `VG-03 §4` (`domain`, `ports`, `kernel`, `agency`, `runtime`, `adapters`) is a build failure
- [ ] **Step 3** — rerun → non-zero exit naming the package
- [ ] **Step 4** — delete the rogue package; add the permanent counterpart under `test/broken/`
- [ ] **Step 5** — commit

> This rule alone would have blocked `runtime/loops/` at the PR that introduced it.

### S7-A-02 — `subprocess` confined to the sandbox adapter

- [ ] **Step 1** — failing test: plant `import subprocess` in a temp module under `agency/` →
      checker currently PASSes
- [ ] **Step 2** — rule: `subprocess` importable **only** from `vanguard/packages/adapters/sandbox/**`
- [ ] **Step 3** — run against the tree. **Expect real hits** outside the sandbox (`root.py`
      composition probes, tools). Triage each: legitimate → add to an explicit, commented
      allowlist; illegitimate → it is a finding, report it
- [ ] **Step 4** — broken counterpart
- [ ] **Step 5** — commit

> `N-06`: shell is contained by the sandbox, not mediated by the host language. This rule is the
> static half of that guarantee.

### S7-A-03 — No evaluator import from cognition or runtime

- [ ] **Step 1** — failing test: plant `from ...adapters.evaluators import ...` in `agency/`
- [ ] **Step 2** — rule: no path from `agency/**` or `runtime/**` (except the composition root's
      explicit `EVALUATOR_BINDINGS` table) to `adapters/evaluators/**`
- [ ] **Step 3** — broken counterpart
- [ ] **Step 4** — commit

> `A-05` + `LT-4`: *"a component that can construct its own evaluator is a second judge."* This
> makes evaluator exteriority a property of the import graph, not of good intentions.

---

## S7-A-04 — DELETE `runtime/loops/`

**Requires:** `S7-A-02`, `S7-A-03` merged — so the rules prevent its return.

- [ ] **Step 1** — `grep -rn "runtime.loops\|MetaLoopEngine" --include=*.py .` → confirm the only
      importers are the package itself and `test/runtime/test_meta_loop.py`
- [ ] **Step 2** — record the salvage mapping in the PR body (compaction → `S8-B-02`; retry → the
      loop itself; tier escalation → `S8-B-03`). **The ideas survive; the code does not.**
- [ ] **Step 3** — `git rm -r vanguard/packages/runtime/loops/ test/runtime/test_meta_loop.py`
- [ ] **Step 4** — full suite; no new failures
- [ ] **Step 5** — commit `[lane-a] S7-A-04: delete MetaLoopEngine (ADR-0064, 011 §8)`

**Why this is not negotiable.** In 144 lines it runs `subprocess.run` on the host with no grant,
**invokes the evaluator inside the loop and branches on the verdict**, emits zero events, and
carries a `NameError` on its default path. It inverts `A-05` — the single property the entire
self-improvement argument rests on.

---

## S7-A-05 — DELETE `runtime/coordination.py`

**Requires:** `S7-A-04`.

- [ ] **Step 1** — failing test: assert episode depth is derivable from ledger events alone
      (`runtime/ledger/projections.py`) → currently impossible
- [ ] **Step 2** — implement the depth projection over `causationId`. Labels
      (`Atom`/`Molecule`/`Polymer`/`Cell`/`Body`) are applied **by the projection**, never as classes
- [ ] **Step 3** — remove the `root.py:712-723` coordinator wiring **and** the fabricated
      `tokens_used = ... or 100` at `:793`. Zero tokens is zero tokens
- [ ] **Step 4** — `git rm vanguard/packages/runtime/coordination.py`; convert
      `test/runtime/test_coordination.py` into a projection test
- [ ] **Step 5** — commit

**Why.** It is a second budget ledger in raw SQLite — no lease, no release, no overrun debit, no
conservation property, no events, no attenuation — defaulting to a path inside `tools/`, wrapped
in a bare `except Exception: pass`. `A-07` says everything is an event and every surface is a
projection of it.

---

## S7-A-06 — Remove hardcoded composition values

- [ ] **Step 1** — failing test: compose on a host where `bwrap` exists somewhere **other than**
      `/usr/bin/bwrap` → currently raises `CompositionError`
- [ ] **Step 2** — replace the literal at `root.py:659` with a `shutil.which("bwrap")` probe behind
      `SandboxRunner`; the composition error must **name the remedy**, not just the absence
- [ ] **Step 3** — `Reservation(usd_micros=100, millis=1000)` at `:775` → read from the frozen
      budget policy
- [ ] **Step 4** — mark `approval_required_above="low"` at `:693` with a `TODO(S8-B-04)` pointing
      at the manifest component that replaces it. Do **not** implement it this sprint
- [ ] **Step 5** — commit

---

## Stop conditions

| Signal | Action |
|---|---|
| Deleting `runtime/loops/` breaks a test that is not `test_meta_loop.py` | **Stop.** Something depends on the bypass path. Report before deleting |
| A boundary rule cannot be expressed in the existing table | **Stop.** The lattice may be wrong. Escalate — do not special-case |
| Any task appears to need a `kernel/` edit | **Stop.** `ADR-0054`; kernel changes need their own ADR |
| `S7-A-02` finds many legitimate `subprocess` uses | Not a stop — but the allowlist must be **explicit and commented**, never a wildcard |

## Definition of done for the lane

```bash
python3 -m unittest discover -s test -t . -q     # no Lane-A-caused failures
python3 tools/check_boundaries.py                # PASS
python3 tools/run_broken_tests.py                # all counterparts fail as designed
python3 tools/check_tcb_budget.py                # PASS
grep -rn "runtime.loops\|EpisodeCoordinator" --include=*.py .   # empty
```
