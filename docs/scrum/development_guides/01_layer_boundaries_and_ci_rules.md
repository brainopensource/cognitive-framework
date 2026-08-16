# 01 — Layer Boundaries & CI Rules

**Purpose:** what may import what, which CI rules enforce it, and how to add a rule correctly.
**Owner of the rules:** `VG-03 §4`. This is a projection.

---

## 1. The lattice

```
clients/     CLI · inspector · API surface        pure consumers
runtime/     composition root · daemon            wiring, frozen at composition
agency/      loop · context · playbooks           cognition
kernel/      dispatch · policy · governor · grants · evaluator boundary
ports/       interfaces only
domain/      pure types, no I/O
adapters/    implements ports; imported ONLY by runtime/
lab/         offline; consumes exported artifacts only
```

| # | Contract |
|---|---|
| `LT-1` | `domain/` imports nothing from the project |
| `LT-2` | `ports/` imports only `domain/` |
| `LT-3` | `kernel/` imports `domain/` and `ports/`. **Never** `adapters/`, **never** `agency/` |
| `LT-4` | `agency/` imports `domain/`, `ports/` and kernel interfaces. **Never** `adapters/`, **never** `lab/` |
| `LT-5` | `adapters/` imports `domain/` and `ports/`. **Never each other** |
| `LT-6` | `runtime/` may import everything. It is the only module that may |
| `LT-7` | `clients/` imports `domain/` and the daemon client. **No adapter handles** |
| `LT-8` | Nothing imports `lab/`. It is offline and consumes exported files |

**Why `LT-4` matters most.** *"A component that can construct its own evaluator is a second
judge."* Evaluator exteriority (`A-05`) becomes a property of the import graph rather than of
anyone's good intentions.

> **A standing caution.** These contracts prove properties of the **import graph**. They do not
> constrain a subprocess spawned under a granted execution capability. Containment is the workload
> perimeter's job, and no static analysis substitutes for it.

---

## 2. The checker — read this before adding a rule

`tools/check_boundaries.py` is **already AST-based** (`ast.parse`, `ast.walk`, `ast.Import`,
`ast.ImportFrom`) and **table-driven**. The comment at line 32 says a missing entry is *"a gap in
this table rather than a property of the architecture."*

**You are adding rows, not building a checker.** If a rule cannot be expressed as a table row, that
is a signal the lattice may be wrong — escalate.

---

## 3. The five Phase 3 rules

| # | Rule | Prevents |
|---|---|---|
| `BR-1` | Any top-level package under `vanguard/packages/` not named in `LT-1..LT-8` is a build failure | A package no contract covers is a package no contract constrains. Would have blocked `runtime/loops/` at its introducing PR |
| `BR-2` | `subprocess` importable **only** from `adapters/sandbox/**` | Host execution outside the perimeter (`N-06`) |
| `BR-3` | No path from `agency/**` or `runtime/**` (except the composition root's explicit binding table) to `adapters/evaluators/**` | A second judge (`A-05`) |
| `BR-4` | `benchmarkings/**` may import `runtime.root` and `ports` **only** | A benchmark that bypasses the kernel becomes unwritable |
| `BR-5` | Reconstruction and domain-addition PRs may not modify `kernel/**`, `agency/episode/**`, `domain/wire/**` without an `ADR-XXXX core change` label and both leads on review | This *is* the `T7.6` / `C-10` configurability experiment |

---

## 4. How to add a rule — the pattern

**Every rule ships with a counterpart that fails. A gate never proven able to fail is not a gate
(`A-10`).**

- [ ] **1. Plant the violation.** Create the thing the rule should catch. Run the checker.
      **It must PASS** — that is the defect, demonstrated.
- [ ] **2. Add the table row.**
- [ ] **3. Rerun.** Non-zero exit, and the message **names the offending file and rule**.
- [ ] **4. Run against the whole tree.** Expect real hits. Triage each: legitimate → explicit,
      commented allowlist entry; illegitimate → **a finding**, report it.
- [ ] **5. Move the planted violation into `test/broken/`** as a permanent counterpart.
- [ ] **6. Verify** `python3 tools/run_broken_tests.py` shows it failing as designed.

**Never** use a wildcard allowlist. A wildcard reintroduces exactly the hole the rule closes.

---

## 5. The other gates

| Gate | Command | Meaning |
|---|---|---|
| Boundaries | `python3 tools/check_boundaries.py` | The lattice holds |
| TCB budget | `python3 tools/check_tcb_budget.py` | Kernel ≤ 1,438 logical LOC. **Growth needs an ADR** (`ADR-0054`) |
| Secrets | `python3 tools/scan_secrets.py --all-refs` | **Always the strict mode.** The lenient default passing is what let `SEC-01` stay open |
| Broken counterparts | `python3 tools/run_broken_tests.py` | Every must-fail test fails against its broken impl |
| Contract | `python3 tools/check_active_mvp_contract.py --release` | Merged-scope evidence 100%. **Expect red while a sprint is open** |
| Contract tests | `python3 tools/run_active_contract_tests.py --candidate` | Non-vacuous: fails on 0 commands executed |
| Baseline manifest | `python3 tools/check_baseline_manifest.py` | Digest integrity; reseal only with an authorising commit |

**Insist on seeing red before green.** A gate you have never watched fail is a gate you do not know
the behaviour of.

---

## 6. Test families (`GTS-13C` Ch. 8)

Coverage is satisfied by **any** of these — demanding must-fail coverage for every rule produces
ceremonial tests.

| Family | Proves | Example |
|---|---|---|
| **Must-fail** | The control can fail | Verb-only attenuation reads the evaluator bundle |
| **Architecture** | A path does **not** exist | No route from `agency` to `adapters/evaluators` |
| **Property** | An algebraic law holds | Attenuation monotone; budget conserved; selector inclusion transitive |
| **Conformance** | Two implementations agree | Golden canonicalisation triples across both readers |
| **Fault injection** | Every failure path recovers | Crash at each dispatch stage |
| **Adversarial** | The threat model is real | Injection, escalation, exfiltration, descriptor substitution |

Plus two statistical families that are **not** unit tests: **A/A** (noise floor) and **paired
comparison** (effect estimation).
