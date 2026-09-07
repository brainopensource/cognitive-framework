---
id: draft.audit.wave2_closeout
class: audit
authority: advisory
status: draft
truth_plane: AS_MEASURED
owner: external-review
date: "2026-09-06"
subject_sha: dfb0bb64
revalidated_at: 2a5fb1ff
subject_branch: main
subject_state: clean
audience:
  - architect
  - repository-governance
  - developer
purpose: >
  Independent architectural and empirical audit of the AETHER / Vanguard substrate
  at the Wave 2 close-out boundary, establishing whether the codebase is a sound
  foundation for a state-of-the-art meta-framework for constructing and
  comparatively evaluating coding agents.
method: static measurement + full dynamic test execution + dependency-graph metrics
relationships:
  - execution.milestones
  - execution.tasks
  - execution.feature_spec
  - arch.system.boundaries
---

# An Architectural and Empirical Audit of the AETHER / Vanguard Agent Substrate

**Subject:** `dfb0bb64` (`main`, clean working tree).
Still valid at `2a5fb1ff`: `git diff --stat dfb0bb64..2a5fb1ff` touches only
`.draft/audit/**`, so no measurement below is affected.
**Audit date:** 2026-09-06 · **Revision 2** (§F-B1 mechanism corrected; F-B5 added;
sibling audits reconciled — [Appendix E2](#appendix-e2--reconciliation-with-the-two-sibling-audits))
**Scope:** `vanguard/`, `packs/`, `benchmarks/`, `test/`, `tools/linters/`, `docs/execution/`
**Method:** static dependency-graph measurement, cyclomatic analysis, clone detection, cryptographic configuration-identity proof, and full dynamic execution of the 2,855-test suite.

---

## Table of Contents

1. [Abstract](#1-abstract)
2. [Theoretical Framework and Prior Art](#2-theoretical-framework-and-prior-art)
3. [Measurement Apparatus and Reproducibility](#3-measurement-apparatus-and-reproducibility)
4. [Finding Class A — Governance Integrity Failure](#4-finding-class-a--governance-integrity-failure)
5. [Finding Class B — Semantic Correctness Defects](#5-finding-class-b--semantic-correctness-defects)
6. [Finding Class C — Experimental Design Invalidity](#6-finding-class-c--experimental-design-invalidity)
7. [Finding Class D — Structural / Modularity Defects](#7-finding-class-d--structural--modularity-defects)
8. [Quantitative Architecture Analysis](#8-quantitative-architecture-analysis)
9. [Statistical Validity of the Benchmark Programme](#9-statistical-validity-of-the-benchmark-programme)
10. [Comparative Analysis Against the 2026 Harness Landscape](#10-comparative-analysis-against-the-2026-harness-landscape)
11. [Synthesis: Is This a SOTA Foundation?](#11-synthesis-is-this-a-sota-foundation)
12. [Remediation Programme with Acceptance Predicates](#12-remediation-programme-with-acceptance-predicates)
13. [Appendices](#13-appendices)

---

## 1. Abstract

AETHER is an event-sourced agentic-computation substrate whose stated purpose is not to
optimise a single coding agent but to serve as a *measurement instrument*: a common
runtime on which many harness designs (`vg-code-max`, Chimera, Hydra, Octopus, `vg-luna`,
and re-creations of Claude Code, OpenCode, Pi, Hermes) can be constructed and compared
under a held-constant model, thereby isolating the harness as the independent variable.

This audit evaluates whether the artefact at `dfb0bb64` can discharge that purpose.

**Principal conclusion.** The substrate's *trusted core* is of genuinely high quality and
is, to this auditor's knowledge, more rigorously bounded than any comparable open-source
harness: a 1,386-line reference monitor under an enforced budget, a domain-blindness
linter that passes, a port layer at near-optimal abstraction (Martin distance
$D = 0.04$), and an evidence schema (`benchmarks/ladder/evidence.py`) that encodes
per-run provenance more completely than the published agent benchmarks it intends to
compete with.

**However**, the layers above that core are not currently fit for the measurement purpose,
for four independent reasons, each established by direct evidence rather than inspection:

- **(A)** The Wave 2 work was merged to `main` while its own governing documents declare
  the gate blocking and the tree unmergeable. `main` is red: two of five architecture
  linters exit non-zero, and 66 of 2,855 tests fail or error.
- **(B)** The completion gate works and its verdict is then thrown away: four sites in
  `runtime/` project the terminal state `abstained` — *"the gate refused this"* — onto the
  string `"completed"`, while a fifth projects it to `"abandoned"`. The product surface
  therefore reports success for a run with no patch and no verification receipt,
  violating `TC-E-058` at precisely the boundary the T-27 canary measures through.
  Separately, patch anchoring admits stale anchors (`TC-E-061`), and `code --help`
  executes the product and exits `0` on `instrument_error`.
- **(C)** The three "distinct" presets `vg-code-{fast,balanced,max}` are **cryptographically
  identical** after removing two label fields (SHA-256
  `6f9a4df4dad104d0bbf82c3a52f0423f867bd06a046cff4062cdd1e02760afed`, all three).
  The mutual information between the preset label and the behaviour-affecting harness
  configuration is $0$ bits once budget is conditioned out. Any measured difference
  between arms is therefore *fully confounded* with budget and carries no information
  about harness design.
- **(D)** A 2,107-line top-level `lab/` package was deleted in `67f033d5` (2026-09-03)
  while ten dependent test modules were left in place. Those modules are the falsifiers
  for `MS-META` and the M-7 independence claims, and one of them is a *security*
  assertion. They now raise `ImportError` at collection rather than failing — a silent
  transition from "enforced" to "absent."
- **(E)** Executing the suite **mutates the developer's real repository**: it `git add`s
  unrelated working files and writes to the tracked `lam.sqlite` corpus. The guard written
  to prevent exactly this is a `pytest_configure` hook, and `pytest` is not installed —
  so under the only runnable runner the guard never executes (F-A4). Discovered
  empirically during this audit; reverted.

The remediation is not a rewrite. Every class B, C and D defect sits at a seam where one
concept has two or more implementations — two entrypoints, two preset catalogues, three
engines, six patch appliers, and a terminal-state projection written four times (§8.3).
The corrective programme is predominantly *deletion and unification* (§12).

---

## 2. Theoretical Framework and Prior Art

This audit is not conducted by taste. Each finding is bound to a named, published
criterion, so that the finding is falsifiable and the remediation has an acceptance
predicate.

### 2.1 Structural criteria

| # | Principle | Source | Operationalisation used here |
|---|---|---|---|
| T1 | **Single Responsibility Principle** — a module should have one reason to change | Martin, *Agile Software Development: Principles, Patterns, and Practices* (2002); *Clean Architecture* (2017), ch. 7 | Method count, cyclomatic complexity $CC$, and constructor arity per class (§8.2) |
| T2 | **Dependency Inversion Principle** — high-level policy must not depend on low-level detail | Martin (2002), ch. 11 | Direction of the package import graph (§8.1) |
| T3 | **Acyclic Dependencies Principle (ADP)** — the package dependency graph must be a DAG | Martin (2002), ch. 28 | Cycle detection over measured import edges (§8.1) |
| T4 | **Stable Dependencies / Stable Abstractions Principle** — depend in the direction of stability; stable packages must be abstract | Martin (2002), ch. 28 | $I$, $A$, $D$ metrics, main-sequence distance (§8.1) |
| T5 | **Ports & Adapters (Hexagonal Architecture)** — the application core is isolated behind ports; adapters are replaceable | Cockburn, "Hexagonal Architecture" (2005); Vernon, *Implementing Domain-Driven Design* (2013), ch. 4 | Adherence measured against the repository's own `docs/architecture/boundaries.md` `INV-B-001` and `tools/linters/check_boundaries.py` |
| T6 | **Reference monitor** — complete mediation, tamper-proof, small enough to verify | Anderson, *Computer Security Technology Planning Study* (1972); Saltzer & Schroeder, "The Protection of Information in Computer Systems," *Proc. IEEE* 63(9), 1975 | TCB LOC budget (`check_tcb_budget.py`), domain blindness, $CC$ of `kernel/dispatch.py` |
| T7 | **Don't Repeat Yourself** — every piece of knowledge has a single authoritative representation | Hunt & Thomas, *The Pragmatic Programmer* (1999), §7 | Type-1/Type-2 clone detection at architectural seams (§8.3) |
| T8 | **Clone taxonomy** — Type-1 exact, Type-2 renamed, Type-3 gapped, Type-4 semantic | Roy, Cordy & Koschke, "Comparison and evaluation of code clone detection techniques," *Sci. Comput. Program.* 74(7), 2009 | Applied in §8.3 |
| T9 | **Cyclomatic complexity** $CC = E - N + 2P$; $CC > 10$ warrants refactor, $CC > 50$ is untestable | McCabe, "A Complexity Measure," *IEEE TSE* SE-2(4), 1976 | Measured per function (§8.2) |

### 2.2 Verification and evidence criteria

| # | Principle | Source | Operationalisation |
|---|---|---|---|
| T10 | **Falsifiability** — a claim is scientific only if an observation could refute it | Popper, *Logik der Forschung* (1934) / *The Logic of Scientific Discovery* (1959) | The repository's own "named falsifier" discipline; §4.3 shows where a falsifier ceased to be able to fail |
| T11 | **Test-Driven Development** — the test must fail for the intended reason before the code exists | Beck, *Test-Driven Development: By Example* (2003) | Applied to the T-79 falsifier's discriminating power (§6.2) |
| T12 | **Mutation adequacy** — a test suite's strength is its ability to kill semantic mutants | DeMillo, Lipton & Sayward, "Hints on Test Data Selection," *IEEE Computer* 11(4), 1978; Jia & Harman, *IEEE TSE* 37(5), 2011 | §6.2: the T-79 falsifier survives the mutant "make all three manifests identical" |
| T13 | **Construct validity / confounding** — a measurement is invalid if the manipulated variable co-varies with an unmodelled one | Campbell & Stanley, *Experimental and Quasi-Experimental Designs for Research* (1963); Wohlin et al., *Experimentation in Software Engineering* (2012), ch. 8 | §6.1, §9.1 |
| T14 | **Wilson score interval** for binomial proportions; strictly preferred to Wald at small $n$ | Wilson, *JASA* 22(158), 1927; Brown, Cai & DasGupta, *Statist. Sci.* 16(2), 2001 | §9.2 |
| T15 | **Rule of three** — with $0$ events in $n$ trials, the 95% upper bound on the rate is $\approx 3/n$ | Hanley & Lippman-Hand, *JAMA* 249(13), 1983 | §9.3 |
| T16 | **McNemar's test** for paired binary outcomes — the correct test for two harnesses on the same task set | McNemar, *Psychometrika* 12(2), 1947 | §9.4 |

### 2.3 Agent-systems prior art (2026 state of the art)

| System | Architectural commitment | Relevance to AETHER |
|---|---|---|
| **Claude Code** | Single-threaded loop, flat append-only history, deliberately shallow subagents with a hard depth limit, five-layer compaction pipeline (microcompact → context collapse → auto-compact at ≈98% window) | Identical bet to AETHER's ratified `TC-E-039` (unary sequential turn loop). Validates the design choice. |
| **DeepSeek Harness (`dsh`)**, MIT, 2026-08-13, micro-kernel on Cordis | *Everything is a plugin*: model adapter, tool registry, session log, **and the agent loop itself** are swappable; append-only session log is the substrate for `resume`/`fork`/`search`/`replay` | Closest architectural sibling. AETHER already has the event-sourced log and the micro-kernel; the differentiator is that `dsh` made the **loop** a plugin. AETHER has one `EpisodeEngine` plus two rogue engines (§7.3). |
| **OpenCode** (SST) | Client/server over HTTP+SSE; provider-agnostic via `models.dev` (75+ providers, no hardcoded integrations); genuine **LSP** integration (go-to-definition, references, compiler diagnostics) | AETHER's `IndexPort`/LDA is the structural analogue; LSP-grade semantic retrieval is absent. |
| **Hermes** | Transport adapters normalise Anthropic Messages / chat-completions / Codex Responses / Bedrock; **compression creates lineage rather than rewriting history**; ~20k-token system prompt | The compression-as-lineage property is exactly AETHER's `TC-E-057`. Independent convergence is strong evidence the clause is correct. |
| **Pi** (earendil-works / M. Zechner) | Minimal harness; **2–3k-token system prompt**; four execution modes (interactive, print/JSON, RPC, SDK) | Establishes the opposite pole of the prompt-mass axis (§10.2). |

The critical observation from this landscape is recorded in §10.2: the harness design space
in 2026 has a *measurable, order-of-magnitude* primary axis — system-prompt mass, 2k to
20k tokens — and AETHER's manifest system can already express it, but does not.

---

## 3. Measurement Apparatus and Reproducibility

All measurements below were produced on the audited subject and are reproducible.

### 3.1 Environment

```
subject           dfb0bb64 (main), working tree clean
platform          Linux 7.1.12-200.fc44.x86_64
python            3.12 (.venv)
pytest            NOT INSTALLED  ← see F-A3
just              NOT INSTALLED  ← gate executed via justfile recipe bodies
```

### 3.2 Commands executed

Every command is in **[Appendix E](#appendix-e--reproduction-script)**, kept as a single
runnable script (`.draft/audit/reproduce.sh`) rather than restated here. Package metrics
and cyclomatic complexity were computed by AST traversal; both algorithms are given
inline in §8.1 and §8.2.

### 3.3 Headline measurements

| Measurement | Value |
|---|---|
| Architecture linters passing | **3 / 5** (`check_boundaries` exit 1, `check_path_hygiene` exit 1) |
| Tests executed | 2,855 |
| Failures | **13** |
| Errors | **53** |
| Skipped | 19 |
| Total red | **66** |
| Wall clock | 180.4 s |
| `npm run typecheck` (all TS workspaces) | PASS |
| `npm --workspace @vanguard/cli test` | **PASS 81/81** (all 10 built test files executed) |
| `aether code --help` | executes the product; prints `instrument_error`; **exits 0** |
| `lda identity` / `lda doctor` freshness | agree (`FRESH` / `index_healthy: true`) |
| Kernel logical LOC | 1,386 / 1,438 budget (**PASS**) |
| Domain blindness | **PASS** |
| Isolation policy | **PASS** |

---

## 4. Finding Class A — Governance Integrity Failure

> *Severity: **Critical (process)**. This class does not describe broken code; it
> describes a broken relationship between the code and the documents that are
> supposed to govern it. It is listed first because every other finding in this
> report was already known to the project and was merged anyway.*

### F-A1 — The blocking gate was merged past

`docs/execution/milestones.md:44` states, of the subject under audit:

> "The tree is **not gate-green**: five `check_boundaries.py` violations, plus four
> related-surface failures (`coding_max` facade CMX-04 ×2, RF-90 fakeBackend ×2).
> **No task may be checked and no L0/L2 subject frozen until those are repaired**,
> touched-surface verification passes, and the subject is clean."

The developer log for the same session concludes: *"Kernel was not touched. TCB stays 1386.
… **No commit.**"*

**Measured reality.** The work is committed and merged:

```
dfb0bb64 Merge pull request #31 from brainopensource/feat/strongforce_beta_release_v093
f2ca64bd feat(W2): Docs-execution, vg-code-* max fast and balance, V0.9.3.g
```

`git log --oneline -3 -- benchmarks/ladder/evidence.py benchmarks/product_path.py`
returns `f2ca64bd`. The working tree is clean. The subject is *simultaneously*
clean and red — the exact state the governing document declares must not exist.

**Analysis.** The gate was not weakened; no linter was edited, no assertion relaxed.
It was **bypassed by merge**. This is a strictly worse failure mode than weakening,
because weakening leaves a diff and merging leaves none: the linter still reds, so no
future reader can detect from the code that a decision was made to ignore it. The
governing documents remain textually correct and operationally void.

Both execution documents also carry a stale baseline: `milestones.md:44` and
`tasks.md:37` describe a *dirty tree at `622131da`*, which is two commits behind the
audited HEAD.

### F-A2 — The suite that "passes" is not the suite CI runs

`pyproject.toml` declares `[tool.pytest.ini_options]` with `testpaths = ["test"]`, and the
`justfile` `verify` recipe is the "canonical local/CI qualification gate." **`pytest` is
not installed in `.venv`**:

```
.venv/bin/python -m pytest  →  No module named pytest
```

Every test module in the repository is `unittest`-based (`if __name__ == "__main__":
unittest.main()`), so the suite *is* runnable — but only by a command that is not the
declared gate. The reported per-task falsifier counts ("8/8", "4/4", "6/6", "31/31
named focused falsifiers green") are therefore attestations about a set of ~31
hand-selected tests, executed by an undeclared runner, on a tree whose other 2,824
tests were not consulted.

This is the mechanism by which F-A1 became possible: **a narrow green is reported as
evidence while the wide red is not measured.** The dev log's characterisation of the
remainder as "four related-surface failures (outside the 31)" understates the true
figure by a factor of 16.5.

### F-A3 — Falsifiers that cannot fail

`test/contracts/test_evidence_signing.py:147` reads `lab/m65_study.py` as source text to
assert that no signing key is baked into it:

```python
source = (_ROOT / "lab" / "m65_study.py").read_text(encoding="utf-8")
```

`lab/` does not exist (§7.1). The assertion therefore raises `FileNotFoundError` during
collection. **A security check silently transitioned from `enforced` to `absent`.**

Per Popper (T10), a proposition that can no longer be refuted by any observation has
ceased to be a scientific claim. Nine further modules are in the same state (§7.1).
`MS-META`'s stated gate — *"Controller off unless paired study valid"* — currently has
**no executable falsifier at all**.

### F-A4 — The test suite mutates the developer's real repository

*This finding was discovered empirically during the audit: executing the suite dirtied the
audited subject. It was detected, reverted, and is reported here in full.*

Running `python -m unittest discover -s test -t .` on a clean tree produced:

```
A  .draft/audit/EXHAUSTIVE_ARCHITECTURAL_AUDIT_EXECUTION_VS_CODE.md   ← staged, unrelated user file
A  benchmarks/baac/runs/baac-run-1788732534/sum_pair_result.json      ← staged, generated
A  benchmarks/baac/runs/baac-run-1788732745/sum_pair_result.json      ← staged, generated
MM tools/002_LLM_API_MOCK/lam.sqlite                                  ← tracked corpus modified
?? benchmarks/baac/runs/baac-run-1788744834/                          ← generated
```

Two distinct defects are present.

**(a) `git add` escapes the temporary workspace.** At least ten test modules invoke
`subprocess.run(["git", "add", "."], cwd=…)`:

```
test/adapters/test_aci_gifts.py:63,130      test/contracts/test_environment_port.py:76,323
test/contracts/test_baseline_manifest_verifier.py:77
test/falsifiers/test_d9_trajectory_digest_is_reproducible.py:50   … and others
```

When `cwd` resolves inside the real repository — or when a fixture's temporary directory
is created under the repository root — `git add .` stages **whatever the developer is
currently working on**. In this audit it staged an unrelated 52 KB draft document that
predated the session by three hours. A developer who then ran `git commit` would have
committed a file they never selected.

**(b) The tracked-corpus guard is inert under the only runnable runner.**
`test/conftest.py` exists precisely to prevent this, and says so:

> *"`tools/002_LLM_API_MOCK/lam.sqlite` is a tracked corpus, and the harness ladder opens
> it for writing at import time. A test run that edits a tracked file makes `git status`
> report work nobody did, and that is how a batch of build artifacts was staged by
> accident once already."*

The redirect is implemented in `pytest_configure(config)`. **`pytest_configure` is a
pytest hook; it never executes under `unittest`.** Since `pytest` is not installed
(F-A2), the only runnable runner is `unittest`, and therefore the guard never runs. The
comment records that this exact accident already happened once; the fix chosen was
runner-specific, and the project then lost that runner.

This is the same structural pattern as F-C2: a protective mechanism that is present,
documented, believed to be active, and empirically inert.

**Severity.** This defect can silently corrupt the very thing the project's epistemology
depends on — `subject_sha` and `dirty_flag` are mandatory fields in
`evidence.py`'s `identity` group, and `MS-INSTRUMENT` closes on "dirty tree fail-closed."
A suite that dirties the tree it is measuring can cause a run to be rejected for
contamination it created itself, or — worse — to be *accepted* on a subject SHA that no
longer describes the files that were executed.

**Recommendation A.** Before any Wave 3 work: (i) make `just check` green and make it a
required merge check; (ii) install `pytest` into `.venv` *or* change the declared gate to
`unittest` — the declared runner and the executed runner must be the same object;
(iii) add a meta-test asserting that zero test modules fail at *collection*, so that a
falsifier can never again disappear without turning something red; (iv) move the
`conftest.py` corpus redirect into a runner-agnostic location (module import side effect
or a `unittest` `load_tests` hook) and add a post-suite assertion that
`git status --porcelain` is byte-identical before and after a run.

---

## 5. Finding Class B — Semantic Correctness Defects

> *Severity: **Critical (product)**. These defects cause a coding agent to report
> success for work it did not do.*

### F-B1 — `completed` without evidence at the product boundary

```
FAIL  test.apps.coding_max.test_coding_max_facade
      .test_preset_finish_without_evidence_is_never_completed
      AssertionError: 'completed' == 'completed'

FAIL  test.apps.coding_max.test_coding_max_facade
      .test_facade_is_usable_by_python_callers_with_injected_service
      AssertionError: 'completed' == 'completed'
```

A run in which the model emits a bare `finish` — no patch effect, no verification
receipt — returns `outcome = "completed"` through `CodingMaxFacade`.

**Normative violation.** `spec.md` `TC-E-058`:

> "Model-requested finish **MUST NOT** by itself establish successful completion.
> Where task policy requires verification, completion **MUST** be admitted only by an
> applicable successful verification receipt bound to the current task and current
> post-effect subject."

`MS-TRUTH`'s stated falsifier — *"a run with zero patches or tampered tests cannot earn
`passed`"* — is presently refuted at the product surface.

#### Mechanism: a lossy terminal-state projection, replicated four times

The gate is **not** absent. `RunTermination` (`agency/episode/state.py:31`) distinguishes
`COMPLETED` from `ABSTAINED`, and its docstring states the reason explicitly:

> *"Collapsing this with the evaluation outcome is how instrument failure silently
> becomes task failure, so the evaluation axis is deliberately absent from `agency/`."*

The admission gate correctly refuses the patchless finish and yields `ABSTAINED`. The
defect is that the runtime then **projects that refusal onto the success string**:

```python
runtime/entrypoint.py:166   outcome = "completed" if terminal in {"completed","abstained"} else terminal
runtime/app_service.py:264  outcome = "completed" if terminal in {"completed","abstained"} else terminal
runtime/app_service.py:450  outcome=("completed" if terminal in {"completed","abstained"} else terminal)
runtime/trajectory.py:319   "abstained": "completed",
```

Formally, the projection $\pi$ is non-injective exactly where it must not be:

$$\pi(\texttt{abstained}) = \pi(\texttt{completed}) = \texttt{"completed"}$$

so `abstained` — *"the gate refused to admit this"* — is unrecoverable from the product
result. The correct projection is the identity on both:
$\pi(\texttt{abstained}) = \texttt{abstained}$, $\pi(\texttt{completed}) =
\texttt{completed}$, and **neither is a task disposition** (`TC-E-059`).

**A fifth site disagrees with the other four.** `runtime/child_runtime.py:46` maps the
same state differently:

```python
TERMINAL_OUTCOMES = {"completed": "completed", "abstained": "abandoned", ...}
```

So one terminal state has **two contradictory projections in the same package**:
a parent episode reports an abstention as `completed`, while the identical abstention in
a child episode reports as `abandoned`. Under `TC-E-014` a child's authority may not
exceed its parent's; here the child is *more* truthful than the parent. Any delegation
study that aggregates parent and child outcomes is summing two different scales.

**Correction to an earlier reading.** My first-pass diagnosis — "two entrypoints, two
completion semantics" — was wrong about the causal direction. `entrypoint.execute` does
**not** get this right: it carries the identical defective line at `:166`. The
`INSTRUMENT_ERROR` I observed from `entrypoint` came from a *different* scenario (a
text-only response with no finish tool call at all), not from the patchless-finish case.
The duplication (F-D1) is therefore not the cause of this defect — it is the reason the
defect had to be written **four times**, and the reason a single-site fix will not close
it. This distinction changes the remedy: **R6 must repair the projection first, and unify
the paths second.** Unifying two entrypoints that share the same bad line would preserve
the bug and hide it better.

**Consequence for the programme.** T-27 requires a false-completion rate of *exactly zero*
measured through this boundary. Every abstention the gate correctly refuses is currently
counted as a success, so the measurement is guaranteed to be wrong in the optimistic
direction. No canary may be run until F-B1 is closed.

### F-B2 — Stale patch anchors are admitted

```
FAIL  test.falsifiers.test_d6_patch_context_anchoring
      .test_wrong_line_numbers_still_anchor_on_context
      AssertionError: False is not true : stale patch anchor in src/calc.py at line 1
```

**Normative violation.** `TC-E-061`:

> "A successful patch effect **MUST** bind its input subject, verify the required
> preimage or anchors, apply every declared hunk within the authorized workspace, and
> record the resulting postimage identity. Ambiguous anchors, partial application,
> workspace escape, or a postimage mismatch **MUST** fail closed."

A stale anchor that nonetheless applies is the most damaging possible failure mode for a
coding agent: it produces a *syntactically valid, test-passing* edit in the wrong
location. The run is green; the change is wrong. Unlike a crash, it is not
self-announcing.

Note the structural cause again: the repository contains **six independent patch-apply
implementations** (§8.3). The one on the product path carries the bug; five spares do not.

### F-B3 — Storage amplification is super-linear

```
FAIL  test.benchmarks.test_beta14_performance_baseline
      .test_sqlite_wal_growth_and_write_amplification_multi_turn
      AssertionError: 4.675 not less than or equal to 4.5
                      : Storage growth ratio 4.68x scaled non-linearly
```

This is a *scaling* signal, not a flake. The `max` preset authorises 40 turns
(`presets.json`) versus the 20 of `balanced`. If write amplification $W(t)$ grows
super-linearly in turn count $t$, then a longer-horizon agent — precisely the direction
Octopus/Hydra-class designs go — degrades faster than the turn budget suggests. For a
substrate whose durable event log is its source of truth (`TC-E-003`), storage
amplification is a first-order architectural property, not a performance nicety.

### F-B4 — Remaining failures

| Test | Significance |
|---|---|
| `test_read_patch_test_finish_uses_production_boundaries` | The canonical happy path itself |
| `test_the_direct_form_does_real_work_through_the_canonical_path` | `TC-E-049` topology evidence |
| `test_code_with_fake_backend_executes_cleanly` (RF-90) | Generic entrypoint; `'instrument_error' not found in {'completed','abstained'}` |
| `test_resume_command_executes_without_explicit_brief` (RF-90) | Resume path — `MS-RESUME` is marked `CLOSED` |
| `test_execute_patch_apply` | Sandbox worker patch dispatch |
| `test_every_registered_benchmark_runs_and_returns_timing_fields` ×11 | The benchmark registry does not self-verify |
| `test_repository_living_docs_metadata_passes` | Documentation metadata linter fails on its own repository |
| `test_local_tag_resolves_…`, `test_tag_is_lightweight_not_annotated` | M5A baseline forensics — the contamination-provenance chain |

Note that `test_resume_command_executes_without_explicit_brief` is red while
`MS-RESUME` is recorded as `CLOSED` in `milestones.md:87`. A closed milestone with a
red falsifier is a governance contradiction of the same family as F-A1.

---

### F-B5 — `code --help` executes the product and exits `0` on an error

```
$ node bin/aether code --help
[complete] instrument_error, 0 turns, unknown
$ echo $?
0
```

Two defects compound here.

1. **`--help` is not a terminal parser action.** It falls through to default prompt
   construction and *executes the product*, with `--help` treated as the brief. A help
   request is supposed to be a pure query; here it allocates a run id, composes a
   manifest, and enters the episode loop. Beyond violating the ordinary CLI contract,
   this is a measurement-hygiene defect: help invocations emit run records into the same
   ledger the canary will be scored from.

2. **The exit code is `0` while the terminal state is `instrument_error`.** This is worse
   than the help bug and independent of it. Any CI step, benchmark harness, or shell
   script that branches on `$?` — the ordinary contract — reads success from an
   instrument failure. It is the same lossy-projection pathology as F-B1, expressed in
   the process-exit channel rather than the result string: the error is *representable*
   and is *discarded at the boundary*.

`tasks.md` files this under T-97 (deferred: "TypeScript `aether code --help` / `-m`
collision"). The deferral is defensible for the help text; **it is not defensible for the
exit code**, which is a one-line fix on a surface that every automated caller depends on.

---

## 6. Finding Class C — Experimental Design Invalidity

> *Severity: **Critical (scientific)**. The instrument cannot measure what the project
> exists to measure.*

### F-C1 — The three presets are the same harness (cryptographic proof)

The product arms are `vg-code-fast`, `vg-code-balanced`, `vg-code-max`. Their manifests
differ in exactly two lines:

```
$ diff vg-code-fast/manifest.json vg-code-max/manifest.json
2c2
<   "harness": "vg-code-fast"
---
>   "harness": "vg-code-max"
21c21
<   "budgetPolicy": "vg-code-fast/budget-policy.json"
---
>   "budgetPolicy": "vg-code-max/budget-policy.json"
```

Normalising away those two *label* fields and hashing:

```
fast      6f9a4df4dad104d0bbf82c3a52f0423f867bd06a046cff4062cdd1e02760afed
balanced  6f9a4df4dad104d0bbf82c3a52f0423f867bd06a046cff4062cdd1e02760afed
max       6f9a4df4dad104d0bbf82c3a52f0423f867bd06a046cff4062cdd1e02760afed
```

**All three arms are the same harness.** Identical `system_prompt`, identical `tools`,
identical `context_policy`, `routing_policy`, `approval_policy`, `retrieval_policy`,
`repo_index`, `skill`, identical `capabilities`, identical `evaluators`.

#### Information-theoretic statement

Let $P \in \{\text{fast}, \text{balanced}, \text{max}\}$ be the preset label with uniform
prior, and let $C = (C_{\text{struct}}, C_{\text{budget}})$ be the behaviour-affecting
configuration, where $C_{\text{struct}}$ is the tuple of components, capabilities and
evaluators, and $C_{\text{budget}} = (\text{usd\_micros}, \text{millis}, \text{tokens},
\text{turns})$.

$$H(P) = \log_2 3 = 1.585\ \text{bits}$$

Because $C_{\text{struct}}$ is constant across the support of $P$:

$$I(P; C_{\text{struct}}) = H(C_{\text{struct}}) - H(C_{\text{struct}} \mid P) = 0 - 0 = 0\ \text{bits}$$

whereas

$$I(P; C_{\text{budget}}) = H(P) = 1.585\ \text{bits}$$

Hence for any outcome $Y$ measured across arms, the data-processing inequality gives

$$I(P; Y) \le I(P; C) = I(P; C_{\text{budget}})$$

**Every bit of between-arm variation is attributable to budget alone.** Under Campbell &
Stanley (T13) this is total confounding of the construct "harness design" with the
construct "resource allowance." An A/B result across these arms is a
*strength-of-budget* curve mislabelled as a harness comparison.

This directly contradicts the intent recorded in `MS-CONTROL`, which lists T-79 under
*"One `EpisodeEngine` coding path; **one preset catalog**; true budget enforcement."*
The catalogue was unified; the *arms* were not differentiated.

### F-C2 — The T-79 falsifier is mutation-inadequate

The named falsifier `test/apps/test_preset_budgets.py` is reported 8/8 green. It asserts:

```python
def test_each_preset_declares_a_distinct_budget_policy(self):
    policies = {p: manifest["budgetPolicy"] for p in EXPECTED}
    self.assertEqual(len(set(policies.values())), 3,
        f"T-79: presets route to byte-identical budget policies: {policies}")
```

This asserts that the three `budgetPolicy` **path strings** differ. It cannot distinguish
"three policies" from "three filenames."

Applying mutation-adequacy analysis (T12): consider the mutant
$M$ = *"make all three manifests byte-identical apart from the two label fields."*
$M$ is precisely the state of the subject, and the falsifier **survives** $M$ — it is green
on a tree that exhibits the very defect it is named for. Under Beck's TDD criterion (T11),
this test never failed for the intended reason, because the intended reason was
"the arms are not differentiated" and the test measures "the strings are not equal."

The mutation score of the T-79 falsifier against the class of mutants it purports to
detect is $0$.

**A falsifier that is green on the defect is not evidence; it is a false negative wearing
the costume of a proof.** This is the single most important methodological finding in the
report, because the project's entire epistemology rests on named falsifiers.

### F-C3 — Half the preset catalogue is dead configuration

`packs/code-default/presets.json` declares, per preset:

```json
"fast":     { "budget": {...}, "plugins": { "planner": null,
                                            "context": {"config": {"token_budget": 1000}} } }
"balanced": { "budget": {...}, "plugins": { "planner": {"config": {"max_repair_rounds": 4}},
                                            "context": {"config": {"token_budget": 3000}} } }
"max":      { "budget": {...}, "plugins": { "planner": {"config": {"max_repair_rounds": 8}},
                                            "context": {"config": {"token_budget": 8000}} } }
```

These *are* meaningful harness differentiators — `fast` disables the planner entirely;
`max` gets 8× the context budget and 2× the repair rounds of `balanced`.

**None of it reaches a run.** The `plugins` overlay is consumed only by
`load.compile_preset()`, and:

```
$ grep -rn 'compile_preset' --include=*.py .
test/packs/code_default/test_presets.py:8
test/packs/code_default/test_presets.py:13
```

`compile_preset` and `compile_pack` have **zero non-test callers**. The production path
(`ApplicationService.run(manifest_path=…)`) reads Plane B (the manifests). The facade
extracts exactly one scalar from Plane A:

```python
policy = loader.resolve_preset_policy(chosen)     # facade.py:69
turns  = loader.effective_limit(policy.turns, max_turns)   # facade.py:72
```

So there are two configuration planes, and the one carrying the interesting differentiation
is not connected to the runtime.

### F-C4 — The parity generator has no callers

`load.budget_policy_document()` exists specifically to derive each
`vg-code-*/budget-policy.json` from `presets.json`, and its docstring says so:
*"Manifest budget-policy JSON derived from the catalog (T-79 parity)."*

```
$ grep -rn 'budget_policy_document' --include=*.py .
(no results outside its own definition)
```

Zero callers — including zero tests. The two files are hand-maintained in parallel; the
mechanism written to guarantee they cannot diverge is inert. `test_preset_budgets`
compares the two files at runtime, which catches drift after the fact, but the generator
is dead weight advertising a contract nothing enforces.

---

## 7. Finding Class D — Structural / Modularity Defects

### F-D1 — Two product entrypoints, ~85% clone

`runtime/entrypoint.py` and `apps/coding_max/facade.py` independently implement the same
operation. The pack-loader helper is a **Type-2 clone** (Roy et al., T8) differing by two
lines in thirteen:

```
$ diff <(sed -n '27,39p' apps/coding_max/facade.py) <(sed -n '40,52p' runtime/entrypoint.py)
2d1
<     """Load ``packs/code-default/load.py`` — the catalog compiler."""
5c4,5
<         path = Path(__file__).resolve().parents[4] / "packs" / "code-default" / "load.py"
---
>         import importlib.util
>         path = _root() / "packs" / "code-default" / "load.py"
```

Two consequences follow immediately:

1. **Shared-key collision.** Both register the *same* module key:
   ```python
   spec = importlib.util.spec_from_file_location("code_default_load", path)
   sys.modules[spec.name] = module
   ```
   Whichever loads first wins; the second silently reuses it. But the two resolve `path`
   differently — `parents[4]` versus `_root()` (which honours `$VANGUARD_ROOT`). If the
   environment variable points elsewhere, the two disagree and **the disagreement is
   invisible**: no error, no warning, just a different catalogue than the caller believes.

2. **Divergent semantics.** F-B1 is the empirical proof: the completion gate is enforced
   on one clone and not the other.

**The preset literal `{"fast","balanced","max"} is written five times:**

| Location | Form |
|---|---|
| `apps/coding_max/facade.py:47` | `PRESETS = ("fast", "balanced", "max")` |
| `runtime/entrypoint.py:30` | `if chosen not in {"fast","balanced","max"}` |
| `runtime/entrypoint.py:107` | `if command == "code" and preset not in {"fast","balanced","max"}` |
| `packs/code-default/load.py:44` | `PRESET_NAMES = ("fast","balanced","max")` |
| `benchmarks/product_path.py:16` | `PRODUCT_PRESETS = {...}` |

**Manifest path resolution has two incompatible mechanisms:**

| Mechanism | Sites |
|---|---|
| `importlib.resources.files("vanguard.packages.agency")` | `facade.py:57`, `cli.py:68`, `app_service.py:232`, `app_service.py:467` |
| Raw path arithmetic `_root() / "vanguard/packages/agency/manifests"` | `entrypoint.py:34`, `entrypoint.py:110` |

`pyproject.toml` ships this as an installable distribution
(`[tool.setuptools.packages.find] include = ["vanguard*","schemas*","packs*","tools*"]`).
**The second mechanism breaks in an installed wheel**, where the source tree layout no
longer exists. The audited product entrypoint is therefore not deployment-portable.

**The reintroduced magic number.** `entrypoint.py:110-112`:

```python
if harness_override:
    manifest_path = _root() / "vanguard/packages/agency/manifests" / harness_override / "manifest.json"
    explicit = request.get("maxTurnsPerEpisode")
    max_turns = 40 if explicit in (None, "") else int(explicit)   # ← hardcoded
```

`test_preset_budgets.test_max_turns_is_not_a_python_default_in_the_facade` exists
specifically to forbid a hardcoded `40`:

> *"T-79: the turn ceiling must come from presets.json, not from a Python default that
> silently overrides the catalog"*

The forbidden default is present ten lines below the check, on the code path that
benchmarks use for every non-preset arm. The falsifier inspects
`CodingMaxFacade.run.__signature__` and is structurally incapable of seeing it.

**Private-member coupling.** `entrypoint.py:66` calls
`ApplicationService._pack_completion_policy(...)`; `benchmarks/product_path.py:12` imports
`entrypoint._manifest`. Both cross module boundaries through the leading-underscore
contract.

### F-D2 — Layering violations (measured, `check_boundaries` exit 1)

```
BOUNDARY FAIL benchmarks/ladder/evidence.py:8    → domain.canonicalisation.digest
BOUNDARY FAIL benchmarks/ladder/evidence.py:9    → domain.evidence.disposition
BOUNDARY FAIL benchmarks/ladder/l0_triad/runner.py:11 → domain.canonicalisation.digest
BOUNDARY FAIL benchmarks/product_path.py:12      → runtime.entrypoint
BOUNDARY FAIL runtime/cli.py:183                 → apps.coding_max.facade
```

The fifth is the structurally serious one. `runtime → apps` **inverts** the dependency
direction the entire package layout is built on, and creates a cycle (§8.1). It exists
solely so `cmd_code` can call `facade.run` — which, per F-D1, duplicates
`entrypoint.execute`. Removing the duplication removes the violation for free.

The first three are a *placement* error rather than a design error:
`benchmarks/ladder/evidence.py` is a high-quality artefact (§11.2) that encodes
`TC-E-062`. Evidence-row schema is a **domain** concern. Relocating it to
`domain/evidence/` resolves three of the five violations and improves the design.

### F-D3 — A second and third execution engine

`spec.md` `TC-E-038`: *"The sole production chain **MUST** remain `mhf.manifest/2 →
CanonicalManifest → FrozenComposition → ActivationPlan → RunPlan → EpisodeEngine`."*
`MS-CONTROL`: *"Forge/Chimera excluded from product scores."*

**Forge (~2,300 LOC) is live in the benchmark corpus:**

```
benchmarks/benchmark_20_suite/runner.py:599   engine = ForgeFacade.create_engine(...)
benchmarks/baac/lib/runner.py:211             engine = ForgeFacade.create_engine(...)
```

It is reachable because `runtime/root.py` imports and re-exports it:

```python
# root.py:69-74
from ..agency.forge import (FORGE_PRESET_NAME, ForgeConfig, ForgeFacade,
                            GoalContract, HERBS_PRESET_NAME)
# root.py:764-767  — __all__ re-export
```

**Nothing in `runtime/` uses these symbols.** The composition root is coupled to a
non-product engine purely to act as a re-export conduit into `benchmarks/`.

*Consequence.* B20 and BAAC results were produced by an engine that bypasses
`EpisodeEngine`, the kernel dispatch stages, and the ledger. They are **not commensurable**
with product-path results. T-89 corrects this prospectively for the canary; nothing in the
execution documents marks the historical rows as a different subject. Any table that places
a Forge row beside an `entrypoint.execute` row is comparing two instruments.

**Chimera (~2,000 LOC) is imported only by tests:**

```
test/agency/test_chimera.py:22
test/runtime/test_coding_verification.py:15
```

`chimera/facade.py` has no caller at all. Chimera carries its own `patcher.py`,
`compiler.py`, `blackboard.py` (559 LOC), `retrieval.py`, `verification.py`,
`governor.py`, `symbolic.py`, `skills.py` — a complete parallel stack, dead.

### F-D4 — A deleted package took its falsifiers offline

`67f033d5` (2026-09-03, *"feat(integration): Fix Vanguard to work with TUI CLI Code"*)
deleted the top-level `lab/` package — **2,107 lines across 9 files**:

```
lab/bench.py                            297 ---
lab/build.py                            139 ---
lab/diff.py                              73 ---
lab/evo14_concurrent_readonly_study.py  167 ---
lab/m65_study.py                        812 ---
lab/m65_tasks.py                         77 ---
lab/m701_independence.py                309 ---
lab/run.py                               34 ---
lab/topology_analysis.py                199 ---
                                      2,107 deletions
```

**Ten test modules that depend on it were not deleted.** They now raise at collection:

| Test module | Depends on | Governs |
|---|---|---|
| `test/lab/test_m65_study.py` | `lab.m65_study` | `MS-META` paired study |
| `test/falsifiers/test_m65_integrated_study.py` | `lab.m65_study` | `MS-META`, RF-114/117 |
| `test/falsifiers/test_rf114_rf117_m65_falsifiers.py` | `lab.m65_study`, `lab.m65_tasks` | `MS-META` |
| `test/falsifiers/test_m701_recorded_workload.py` | `lab.m701_independence` | M-7.01 independence |
| `test/falsifiers/test_m7_topology_and_independence.py` | `lab.m701_independence`, `lab.topology_analysis` | `TC-E-049` topology |
| `test/runtime/test_m701_independence.py` | `lab/…` | M-7.01 |
| `test/lab/test_bench.py`, `test_build.py`, `test_diff.py`, `test_coding_instrument.py` | `lab/bench.py` etc. | Lab tooling |
| `test/contracts/test_evidence_signing.py:147` | `lab/m65_study.py` (as text) | **Security: no baked-in signing key** |

Meanwhile `runtime/skill_evaluation.py` (622 LOC), `runtime/paired_evaluation.py`
(337 LOC) and `runtime/lab_driver.py` (593 LOC) remain in the runtime. **The
evidence-producing layer was removed and the evidence-consuming layer was kept.**

`MS-META`'s gate — *"Controller off unless paired study valid"* — has no executable
falsifier. `test/contracts/test_evo05_one_event_representation.py:27` still lists
`ROOT / "lab"` in its `SCAN_ROOTS`, silently scanning nothing.

This is the most serious finding in class D, because it is invisible: the milestone table
still cites these falsifiers by name.

### F-D5 — Namespace collision: a Wave 2 addition shadowed a Wave 0 tool

```
ERROR: test.tools.test_lam_ladder
ImportError: cannot import name 'run_ladder' from 'ladder'
             (/home/…/benchmarks/ladder/__init__.py)
```

`tools/002_LLM_API_MOCK/ladder.py` defines `run_ladder` (line 114).
`test/tools/test_lam_ladder.py` defensively prepends the tool directory to `sys.path`:

```python
tools_dir = Path(__file__).resolve().parents[2] / "tools" / "002_LLM_API_MOCK"
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))
from ladder import run_ladder
```

Wave 2 (T-92) introduced `benchmarks/ladder/` as a package, which now wins resolution.
**A new benchmark package silently broke a pre-existing tool's test by name collision.**

This is a symptom of a repository-wide pattern: **124 `sys.path` mutations** across
`vanguard/`, `packs/`, `benchmarks/` and `tools/`, and six `spec_from_file_location`
dynamic loads in *production* code. Flat top-level module names combined with runtime
path mutation make the import graph a function of execution order. That is not a
property a reproducible measurement instrument can afford — it interacts directly with
`TC-E-030` (production replay parity in a fresh process).

### F-D6 — Confirmed dead code (deletion index)

Consolidated for deletion planning; each row is proved where cited.

| Artefact | LOC | Proved in |
|---|---|---|
| `agency/chimera/**` | ~2,000 | F-D3 |
| `load.compile_preset` / `compile_pack` | — | F-C3 |
| `load.budget_policy_document()` | — | F-C4 |
| `root.py` Forge re-exports | — | F-D3 |
| `packs/code-default/toolkits/composite.py` | — | here: absent from `plugin.yaml`, no importer |
| `adapters/bindings/lex_reproducer.py` | — | here: no importer found |
| `adapters/models/ollama` | — | here: referenced by a test, module absent, forbidden by policy |

### F-D7 — Hygiene

- `check_path_hygiene` exit 1: 23 hardcoded `/home/rock-dev/...` paths in
  `tools/model_benchmarks/experiments/` (21) and `vanguard/clients/tui/test/` (2).
- `test/broken/` contains **linter negative fixtures**, not broken tests. Any agent
  navigating this tree will misread it. Rename to `test/fixtures/linter_negative/`.
- `pyproject.toml` packages `tools*` into the distribution.
- `packs/code-default/load.py` is loaded by *file path* despite `packs*` being an
  installed package — the two mechanisms should not coexist.
- `delete.md` at repository root.

---

## 8. Quantitative Architecture Analysis

### 8.1 Martin package metrics

Computed over the AST import graph, resolving relative imports against filesystem
position. Definitions (Martin, T4):

$$I = \frac{C_e}{C_a + C_e} \qquad A = \frac{N_a}{N_c} \qquad D = |A + I - 1|$$

where $C_a$ = afferent couplings (packages depending on this one), $C_e$ = efferent
couplings, $N_a$ = abstract units (Protocol/ABC classes), $N_c$ = total units.
$D = 0$ is the *main sequence*; $D \to 1$ is either the *zone of pain* (stable+concrete)
or the *zone of uselessness* (unstable+abstract).

| package | files | $C_a$ | $C_e$ | $I$ | $A$ | $D$ | depends on |
|---|---:|---:|---:|---:|---:|---:|---|
| `kernel` | 9 | 4 | 2 | 0.33 | 0.34 | **0.33** | domain, ports |
| `domain` | 54 | 7 | 0 | 0.00 | 0.29 | **0.71** ⚠ | — |
| `ports` | 15 | 6 | 1 | 0.14 | 0.82 | **0.04** ✅ | domain |
| `agency` | 40 | 2 | 3 | 0.60 | 0.19 | 0.21 | domain, kernel, ports |
| `adapters` | 60 | 3 | 2 | 0.40 | 0.12 | 0.48 | domain, ports |
| `runtime` | 92 | 3 | 6 | 0.67 | 0.14 | 0.19 | adapters, agency, **apps**, domain, kernel, ports |
| `apps` | 3 | 1 | 1 | 0.50 | 0.33 | 0.17 | runtime |
| `packs` | 41 | 0 | 5 | 1.00 | 0.15 | 0.15 | adapters, domain, kernel, ports, runtime |
| `benchmarks` | 147 | 0 | 6 | 1.00 | 0.14 | 0.14 | adapters, agency, domain, kernel, ports, runtime |

**Interpretations.**

1. **`ports` at $D = 0.04$ is excellent** — $A = 0.82$, $I = 0.14$: highly abstract and
   highly stable, essentially on the main sequence. The hexagonal port layer (T5) is
   correctly constructed. This is the strongest structural result in the repository.

2. **`domain` at $D = 0.71$ sits in the zone of pain.** It is maximally stable
   ($C_e = 0$, $I = 0$: it depends on nothing, seven packages depend on it) yet only
   29% abstract across 54 files. Per the Stable Abstractions Principle, a package this
   stable must be abstract, because concrete code in a maximally-stable position cannot
   be varied without breaking seven dependents. This is the structural reason domain
   changes are expensive and the reason `benchmarks/ladder/evidence.py` was written
   *outside* domain (F-D2) rather than inside it.

3. **`runtime` is a hub**: 92 files, $C_e = 6$ (it depends on every other package
   including `apps`), $I = 0.67$. Combined with §8.2 this is the concentration point of
   all complexity.

4. **ADP violation — a measured cycle:**

   $$\texttt{runtime} \to \texttt{apps} \to \texttt{runtime}$$

   Edge weights: `runtime → apps` = 1 (`cli.py:183`), `apps → runtime` = 2
   (`facade.py` imports `ApplicationService`, `results`). Per Martin (T3), a cycle in the
   package graph means the two packages are, for release purposes, **one package**.
   `apps` is 103 lines; it is currently welded to a 26,622-line hub.

**Edge weights (import-statement counts), top 12:**

```
runtime    → domain      89
runtime    → adapters    60
adapters   → ports       54
runtime    → ports       47
adapters   → domain      35
agency     → domain      24
benchmarks → runtime     21
packs      → domain      17
runtime    → agency      16
benchmarks → adapters    13
runtime    → kernel      11
benchmarks → domain       8
```

`kernel → domain` (6) and `kernel → ports` (1) are *permitted* — they target
`canonicalisation.digest`, `canonicalisation.jcs` and `selectors.resource_selector`,
which are the innermost pure-computation layer. This is correct hexagonal direction, not
a violation.

### 8.2 Cyclomatic complexity (McCabe, T9)

Measured by AST decision-point counting: $CC = 1 + |\{$`If`, `For`, `While`,
`ExceptHandler`, `With`, `Assert`, `IfExp`, `comprehension`, `Match`$\}| + \sum
(|\texttt{BoolOp.values}| - 1)$.

| File | Lines | File $CC$ | Worst function | $CC$ | Len | Params |
|---|---:|---:|---|---:|---:|---:|
| `runtime/session.py` | 2,234 | 347 | `_observe_completion_dispatch` (L1766) | **36** | 122 | 3 |
| | | | `HarnessSession.run` (L1207) | **33** | 241 | 1 |
| | | | `HarnessSession.__init__` (L681) | **26** | **245** | 6 |
| `runtime/entrypoint.py` | 338 | 106 | `execute` (L90) | **90** ⚠ | 224 | 1 |
| `agency/episode/engine.py` | 1,129 | 165 | `EpisodeEngine.run` (L263) | **86** ⚠ | **533** | 12 |
| | | | `spawn` (L975) | 21 | 125 | 15 |
| | | | `__init__` (L192) | 5 | 61 | **20** |
| `runtime/app_service.py` | 899 | 182 | `resume` (L349) | 33 | 107 | 6 |
| | | | `run` (L136) | 29 | 161 | 13 |
| `runtime/root.py` | 773 | 90 | `run_composed` (L303) | 25 | 130 | 8 |
| | | | `execute_harness` (L109) | 14 | 118 | **21** |
| | | | `execute_profiled` (L229) | 2 | 72 | **22** |
| `runtime/service/service.py` | 1,350 | 167 | `_envelope_from_service_event` | 23 | 37 | 2 |
| **`kernel/dispatch.py`** | **458** | **52** | `dispatch` (L128) | **16** ✅ | 110 | 7 |
| `apps/coding_max/facade.py` | 98 | 6 | `_pack_loader` | 4 | 13 | 0 |

**Interpretations.**

- McCabe's original guidance places $CC > 10$ in "refactor" territory and $CC > 50$ in
  "untestable." **`entrypoint.execute` at $CC = 90$ and `EpisodeEngine.run` at $CC = 86$
  are both roughly double the untestability threshold.** A function with $CC = 90$ has at
  minimum 90 linearly independent paths; exhaustive branch coverage is not a realistic
  proposition, which is consistent with F-B1 (a completion-gate path that was simply never
  exercised on that clone).

- **`kernel/dispatch.py` has a maximum function $CC$ of 16 across 458 lines.** The trusted
  core is measurably the *simplest* code in the repository. The reference-monitor
  criterion of Saltzer & Schroeder (T6) — "small enough to be verified" — is satisfied,
  and the TCB budget linter enforces it (1,386 / 1,438). **This is the strongest single
  result of the audit.**

- **`HarnessSession` violates SRP (T1) decisively.** The class spans L665–L2050 (~1,400
  lines) with ~45 methods. Its `__init__` alone is 245 lines with $CC = 26$. It
  simultaneously owns: context compilation, packet binding, index fallback, workspace
  epoch derivation, σ folding, tamper shielding, completion admission, stub detection,
  meta-controller consultation, checkpointing, reconstruction, telemetry, evaluation
  dispatch, budget attenuation, and effect dispatch. It has at least fifteen reasons to
  change.

- **Parameter counts of 20–22** (`root.execute_harness` = 21, `root.execute_profiled` = 22,
  `EpisodeEngine.__init__` = 20) indicate that the composition root passes a
  configuration *record* as positional/keyword soup rather than as a type.

- **`SessionPorts` has ~20 optional fields**, the majority documented as
  "`None` means legacy" / "`None` preserves today's behavior." Each is a runtime
  behavioural fork with no type-level discrimination, giving a configuration space of
  order $2^{20}$ reachable shapes, of which the suite exercises a vanishing fraction.
  This is where F-B1 and F-B2 live.

### 8.3 Clone analysis (Roy et al., T8)

| Concept | Independent implementations | Locations |
|---|---:|---|
| **Patch application** | **6** | `adapters/environment/{fake,git,sandboxed}.py`, `agency/chimera/patcher.py`, `agency/forge/{patcher,resilient_patcher}.py` (+ `packs/…/ast_patch.py`, `adapters/bindings/lex_surgical_editor.py` as tool-level variants) |
| **Execution engine** | **3** | `agency/episode/engine.py`, `agency/forge/engine.py`, `agency/chimera/engine.py` |
| **Product entrypoint** | **2** | `runtime/entrypoint.py`, `apps/coding_max/facade.py` (Type-2 clone, 11/13 lines identical) |
| **Terminal-state projection** | **5** | `entrypoint.py:166`, `app_service.py:264,450`, `trajectory.py:319` (all → `"completed"`); `child_runtime.py:46` (→ `"abandoned"`) |
| **Preset catalogue** | **2** | `packs/code-default/presets.json`, `agency/manifests/vg-code-*/budget-policy.json` |
| **Manifest resolution** | **2** | `importlib.resources.files(...)` ×4 sites, raw path arithmetic ×2 sites |
| **Preset name literal** | **5** | F-D1 table |

**The governing observation of this audit:**

> Every red test in §5 sits at a seam where one concept has two or more implementations.

| Defect | Seam | Duplicated concept |
|---|---|---|
| F-B1 (`completed` without evidence) | 4 projection sites + 1 contradictory | terminal-state projection |
| F-B2 (stale anchor) | 6 patch appliers | patch application |
| F-C1 (identical arms) | presets.json vs manifests | preset catalogue |
| F-D3 (incommensurable benchmarks) | EpisodeEngine vs Forge | execution engine |
| F-D5 (namespace collision) | `benchmarks/ladder` vs `tools/…/ladder.py` | module name |

This is a textbook demonstration of the cost function behind DRY (T7): the defect rate at
a seam is proportional to the number of implementations that must be kept in agreement,
because agreement is maintained by human attention rather than by the type system.

### 8.4 Size distribution

| Layer | LOC | Share |
|---|---:|---:|
| TypeScript clients (11 packages) | ~29,500 | 27.4% |
| `vanguard/packages/runtime` | 26,622 | 24.7% |
| `benchmarks/` | 15,141 | 14.1% |
| `vanguard/packages/adapters` | 11,950 | 11.1% |
| `vanguard/packages/domain` | 10,363 | 9.6% |
| `vanguard/packages/agency` | 9,437 | 8.8% |
| `vanguard/packages/kernel` | 1,769 (**1,386 logical**) | 1.6% |
| `vanguard/packages/ports` | 1,582 | 1.5% |
| **`vanguard/packages/apps`** | **103** | **0.1%** |

TypeScript client breakdown: `client` 5,218 · `lab` 5,544 · `desktop` 3,273 · `tui` 3,049 ·
`cli` 2,948 · `projections` 2,855 · `client-core` 2,182 · `ui-web` 1,319 · `studio` 1,306 ·
`contracts` 1,220 · `tui-core` 599.

**The ratio 29,500 : 103 is the diagnosis in one number.** There are 286 lines of
TypeScript client for every line of product application layer, and T-97 — making the
TypeScript CLI actually expose `aether code --help` / `-m` — is *deferred*. A desktop
app, a web UI, a studio and a projections layer exist before the product surface can
correctly report whether it fixed a bug.

`benchmarks/` contains ~20 unrelated runners (`benchmark_20_suite`, `m8_heldout`,
`frontier_v090`, `swe_bench`, `baac`, `sota_context`, `gemini_multifile`, `ladder`,
`agentic_harness_matrix`, `needle_in_haystack`, `lda_ab_test`, `isolated_workspace`, …).
Only **four** import the shared `benchmarks/protocols.py`. For a project whose declared
purpose is cross-harness comparison, there is no single mandatory result protocol —
each runner defines its own result shape, which makes cross-runner meta-analysis
impossible by construction.

---

## 9. Statistical Validity of the Benchmark Programme

### 9.1 Confounding (T13)

Per F-C1, the arm variable $P$ carries $0$ bits about $C_{\text{struct}}$. The
`MS-CONTROL` acceptance predicate — qualify `vg-code-balanced` at L2 — is therefore
sound *as a capability floor for one harness*, but the moment `fast` and `max` rows are
placed beside it, the resulting table is a budget-response curve, not a harness
comparison. This must be stated explicitly in any published table until F-C1 is closed.

### 9.2 The Wilson threshold requires 60%, not 40%

`MS-CONTROL` specifies: *"single-worker `vg-code-balanced` on the exact frozen candidate
SHA at L2 ($n \ge 30$, Wilson LB $\ge 0.40$)."*

The Wilson score lower bound (T14) at confidence $1-\alpha$, $z = z_{1-\alpha/2} = 1.96$:

$$\text{LB} = \frac{\hat{p} + \dfrac{z^2}{2n} - z\sqrt{\dfrac{\hat{p}(1-\hat{p})}{n} + \dfrac{z^2}{4n^2}}}{1 + \dfrac{z^2}{n}}$$

Evaluated at $n = 30$:

| $k$ | $\hat{p}$ | Wilson LB | Meets $\ge 0.40$? |
|---:|---:|---:|:--|
| 12 | 0.400 | 0.2459 | no |
| 15 | 0.500 | 0.3315 | no |
| 17 | 0.567 | 0.3920 | no |
| **18** | **0.600** | **0.4232** | **yes** |
| 20 | 0.667 | 0.4878 | yes |

Minimum $k$ such that $\text{LB} \ge 0.40$, by $n$:

| $n$ | min $k$ | min $\hat{p}$ |
|---:|---:|---:|
| 30 | 18 | **0.600** |
| 50 | 27 | 0.540 |
| 100 | 50 | 0.500 |
| 200 | 94 | 0.470 |

**The stated criterion is materially stricter than it reads.** "Wilson LB ≥ 0.40 at
$n \ge 30$" demands an *observed* pass rate of **60%**. A reader — human or agent —
who plans against "we need 40%" will under-provision by 50% relative and discover it
only after the paid run. This should be stated in `milestones.md` as
"$n \ge 30$, $\ge 18/30$ observed" so the operational target is unambiguous.

Note also that increasing $n$ *lowers* the required $\hat{p}$: at $n = 200$ a 47% observed
rate clears the same bar. If the true capability is near 0.5, $n = 30$ is a coin flip on
milestone closure. Budget permitting, $n = 50$ is a materially better design point.

### 9.3 "False completion = 0" is a weak claim at $n = 30$ (T15)

T-27 requires false-completion rate exactly zero. By the rule of three, observing $0$
events in $n$ trials gives a 95% upper confidence bound of $\approx 3/n$:

| $n$ | 95% upper bound on true false-completion rate |
|---:|---:|
| 30 | **0.100** |
| 50 | 0.060 |
| 100 | 0.030 |

**Zero observed false completions in 30 runs is consistent with a true rate as high as
10%.** For a property that `TC-E-058` treats as a safety invariant, that is not a strong
guarantee. Two recommendations follow:

1. Do not describe the result as "false completion rate = 0"; describe it as
   "0/30 observed, 95% CI [0, 0.10]."
2. Treat the *mechanism* (the completion gate, F-B1) as the primary evidence and the
   empirical rate as corroboration. A gate proven correct by construction is worth more
   than 30 samples — which is precisely why F-B1 must be closed before, not after, the
   canary.

### 9.4 The right test for harness comparison is McNemar, not two-proportion (T16)

When two harnesses run the *same* task set, outcomes are paired, and the correct
statistic is McNemar's on the discordant cells:

$$\chi^2 = \frac{(|b - c| - 1)^2}{b + c}, \quad \text{df} = 1$$

where $b$ = tasks harness A solves and B does not, $c$ = the reverse. Concordant pairs
carry no information. Using an unpaired two-proportion test on paired data
systematically *understates* power and will cause real harness effects to be dismissed.

`benchmarks/lab/test_bench.py::McNemarBench` exists — and currently **errors**, because
`lab/bench.py` was deleted (F-D4). The statistically correct comparison machinery was
removed along with the package.

**Design note.** For detecting a moderate paired effect ($b + c \approx 12$ discordant
pairs with a 3:1 split) at $\alpha = 0.05$, power $\approx 0.8$ requires roughly
$n \approx 40$–$60$ tasks depending on the base solve rate. The L1 twelve-task freeze
(T-93) is adequate for a smoke gate but is **underpowered for any comparative claim**.
This should be recorded now so that L1 results are not later over-interpreted.

---

## 10. Comparative Analysis Against the 2026 Harness Landscape

### 10.1 Where AETHER is genuinely ahead

| Property | AETHER | dsh | OpenCode | Hermes | Pi | Claude Code |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| Append-only event log as source of truth | ✅ | ✅ | partial | ✅ | partial | ✅ |
| **Bounded, budget-enforced reference monitor (TCB linter)** | ✅ **1,386 LOC** | ✖ | ✖ | ✖ | ✖ | ✖ |
| **Capability grants distinct from process isolation** (`TC-E-023`) | ✅ | ✖ | ✖ | ✖ | ✖ | partial |
| **Per-run evidence schema with mandatory provenance** (`TC-E-062`) | ✅ | ✖ | ✖ | ✖ | ✖ | ✖ |
| Completion gated on verification receipt (`TC-E-058`) | ⚠ *specified, breached* | ✖ | ✖ | ✖ | ✖ | ✖ |
| Compression as lineage, not rewrite (`TC-E-057`) | ✅ | ✅ | ✖ | ✅ | ✖ | ✅ |
| Swappable **agent loop** | ✖ | ✅ | ✖ | partial | ✅ | ✖ |
| LSP-grade semantic retrieval | ✖ (LDA index) | ✖ | ✅ | ✖ | ✖ | ✖ |
| Provider-agnostic model registry | partial | ✅ | ✅ (75+) | ✅ | ✅ | ✖ |

The first four rows are real, defensible differentiation. **No other harness in this
comparison has a formal trusted-core budget or a mandatory evidence schema.** That is the
thesis worth defending, and it is already built.

### 10.2 The experiment the field is asking for, and AETHER can almost run

The 2026 landscape has converged on an order-of-magnitude spread along one immediately
measurable axis:

$$\text{system-prompt mass}: \quad \text{Pi} \approx 2\text{–}3\text{k tokens} \;\longrightarrow\; \text{Hermes} \approx 20\text{k tokens}$$

That is a factor of ~7–10 in the single largest fixed cost of every turn, and no
published study isolates it with the model held constant.

**AETHER already has the arms.** `vanguard/packages/agency/manifests/` contains
`vg-code-claude-shaped`, `vg-code-opencode-shaped`, `vg-code-swe-mini`,
`vg-code-critic-reviser`, `vg-code-lex`, `vg-code-max-v3luna`, each with its own
`system-prompt.txt`, `routing-policy.json`, `context-policy.json` and `approval-policy.json`.
The manifest system is a *composition-by-reference* design — `vg-code-fast/manifest.json`
references `vg-code-default/system-prompt.txt` rather than copying it — which is exactly
the right shape for factorial variation.

**The mechanism exists and is not used for the product arms.** F-C1 is therefore not a
missing capability; it is an unexercised one. Differentiating `fast`/`balanced`/`max`
along prompt mass, tool-set size, planner presence and context policy is a
configuration exercise, not an engineering project — and it converts the flagship
experiment from "budget response" into a genuine harness comparison.

**Proposed Wave 3 flagship study.** Five arms — Pi-shaped (~2k), `vg-code-fast` (~5k),
`vg-code-balanced` (~8k), Claude-shaped (~12k), Hermes-shaped (~20k) — one model, one
frozen task set, paired McNemar analysis, one mandatory evidence schema. Preregistered
hypothesis: solve rate is non-monotonic in prompt mass, peaking in the middle, with
cost strictly increasing. This is publishable, cheap, and precisely what the substrate
was built for.

---

## 11. Synthesis: Is This a SOTA Foundation?

### 11.1 The honest verdict

**As a trusted substrate: yes, and measurably so.** As a *measurement instrument today:
no.* As a product: not yet.

The distinction matters because the three verdicts have different remedies. The substrate
needs nothing. The instrument needs F-C1 closed. The product needs F-B1 closed.

### 11.2 What is genuinely excellent, and must be preserved

1. **The trusted core.** 1,386 logical LOC across 9 files, enforced ceiling 1,438, max
   function $CC = 16$, domain-blindness linter green. Measurably the simplest and
   best-bounded code in the repository. This satisfies Saltzer & Schroeder's
   verifiability criterion in a way no comparable open-source harness attempts.

2. **The port layer.** $D = 0.04$, $A = 0.82$. Textbook hexagonal architecture (T5).

3. **`benchmarks/ladder/evidence.py`.** The `REQUIRED_GROUPS` schema — *identity, arm,
   execution, change, verification, settlement, economics, provenance* — with
   refuse-incomplete-rows semantics is a more rigorous encoding of run provenance than
   the published agent benchmarks it competes with. It captures `gguf_digest`,
   `quantization`, `sampling_digest`, `tool_schema_digest`, `time_to_first_valid_action_s`,
   `tamper_verdict` and `varied_dimension`. It is in the wrong package (F-D2), but the
   design is correct and should be *promoted*, not merely relocated.

4. **Orthogonal settlement axes.** Recording `terminal_status` and `disposition`
   independently, with neither derived from the other, so that
   `terminal_status=abandoned` + `disposition=passed` is representable without
   contradiction. This is a subtle modelling decision that most harnesses get wrong by
   collapsing them.

5. **The normative vocabulary.** `MECHANISM` vs `CLOSED`; "T-95 does not close
   `MS-CONTROL`"; "T-97 is deferred on the record (filed, not vanished)"; "MECHANISM,
   not empirical close." This governance language is a genuine asset and is *rarer than
   the code*. The failure in F-A1 is not that the vocabulary is wrong — it is that the
   merge did not respect it.

6. **Composition-by-reference manifests.** The right substrate for factorial harness
   variation (§10.2).

### 11.3 The single root cause

§8.3 establishes the pattern empirically; this is its consequence for strategy. The
project's stated ambition — *"not having only one solution and optimising it, but having a
range of solutions we can verify against each other"* — has been implemented as
*duplicated implementations* rather than as *parameterised variation over one
implementation*. These are opposite architectures with opposite cost curves:

$$\text{duplication: } \quad \text{defect surface} \propto k \cdot n \qquad\qquad \text{parameterisation: } \quad \text{defect surface} \propto k + n$$

where $k$ is implementation complexity and $n$ the number of variants. Three engines and
six patch appliers is the $k \cdot n$ regime; one engine with a manifest-declared policy
is the $k + n$ regime. DeepSeek's `dsh` — *everything is a plugin, including the loop* —
is the $k + n$ regime made explicit, and is the correct target architecture for AETHER's
stated goal.

**AETHER does not need more engines. It needs one engine with more knobs, and a
measurement layer that can prove the knobs matter.**

### 11.4 On overengineering

The kernel is *not* overengineered; it is exemplary and should not be touched. The
overengineering is entirely above it: ~29,500 lines of TypeScript client and ~15,000
lines of unshared benchmark runners sitting on top of a 103-line application layer whose
product surface cannot yet correctly report whether it fixed a bug.

The corrective is not "write less code in future." It is **delete the parallel stacks
that already exist** — Chimera (~2,000), Forge's product coupling, four of six patch
appliers, one of two entrypoints — and freeze the client surface until `MS-CONTROL`
closes.

---

## 12. Remediation Programme with Acceptance Predicates

Each item carries a falsifier, in the repository's own idiom. **No item requires new
architecture.** Estimated net change: **−6,000 to −8,000 LOC**.

### Wave 2.5 — Restore gate integrity *(prerequisite to everything)*

| # | Action | Acceptance predicate |
|---|---|---|
| **R1** | Make `just check` green; make it a required merge check | `for l in tools/linters/*.py; do python3 $l \|\| exit 1; done` exits 0 on `main` |
| **R2** | Reconcile declared and executed test runner: install `pytest` into `.venv`, or change the declared gate to `unittest` | The command in the `justfile` `verify` recipe runs and its result is the reported result |
| **R3** | Add a collection-integrity meta-test | A test asserting that zero test modules raise at import; it must fail today (10 modules, F-D4) |
| **R3b** | **Make the suite non-mutating** (F-A4): move the corpus redirect out of `pytest_configure`; confine every `git add` to a workspace provably outside the repo root | `git status --porcelain` is byte-identical before and after a full suite run; a meta-test asserts it |
| **R4** | Resolve `lab/` — restore from `67f033d5^` or delete its 10 dependent test modules **on the record** | Either `test/lab/**` and the four `lab`-dependent falsifiers pass, or `milestones.md` `MS-META` records that its falsifier was withdrawn and why |
| **R5** | Update the stale handoff paragraphs (`tasks.md:37`, `milestones.md:44`) to the true HEAD and true red count | Documented baseline SHA equals `git rev-parse HEAD` |

### Wave 2.5 — Close the correctness defects

| # | Action | Acceptance predicate |
|---|---|---|
| **R6a** | **Repair the projection first** (F-B1): `abstained` must project to `abstained` at all four sites; reconcile the contradictory fifth site in `child_runtime.py` | `grep -c 'in {"completed", "abstained"}' vanguard/packages/runtime/` = 0; one terminal state has exactly one projection package-wide |
| **R6b** | **Then unify the paths.** Make `CodingMaxFacade` a thin argument-shaper over `entrypoint.execute`; delete the facade's independent path | `test_preset_finish_without_evidence_is_never_completed` green; a mutation reintroducing the collapse turns *both* facade and entrypoint tests red |
| **R6c** | **Make `--help` a terminal parser action and return a non-zero exit on non-success terminals** (F-B5) | `aether code --help` prints usage, runs no episode, exits 0; `aether code <failing>` exits non-zero |
| **R7** | **Anchor verification fails closed** per `TC-E-061` | `test_d6_patch_context_anchoring` green; a deliberately stale anchor produces a typed failure, not an applied hunk |
| **R8** | **Collapse patch appliers 6 → 2** (product + a fake for tests) | `grep -rl "def apply.*patch" vanguard/ packs/` returns ≤ 2 production files; F-B2's falsifier still green |
| **R9** | **One entrypoint.** Delete `_pack_loader` from `facade.py`; delete the `harness_override` hardcoded `40`; route `cli.cmd_code` through `entrypoint` | `check_boundaries.py` no longer reports `runtime → apps`; `grep -c '"fast", "balanced", "max"'` across the tree ≤ 2 |
| **R10** | **One manifest resolver** — `importlib.resources` everywhere | An installed wheel resolves `vg-code-balanced/manifest.json`; add an installed-package smoke test |

### Wave 2.5 — Restore experimental validity

| # | Action | Acceptance predicate |
|---|---|---|
| **R11** | **Differentiate the three arms.** Either wire `compile_preset` into production so `presets.json.plugins` binds, or move the differentiation into the manifests | The normalised SHA-256 of the three manifests are **pairwise distinct**; a new falsifier asserts $\lvert\{\text{sha}(m_p)\}\rvert = 3$ over normalised manifests |
| **R12** | **Strengthen the T-79 falsifier** to compare *content*, not path strings | The strengthened test is **red on `dfb0bb64`** and green after R11 (this is the TDD ordering requirement, T11) |
| **R13** | Resolve `budget_policy_document` — generate `budget-policy.json` at build time, or delete it | Zero unused public functions in `load.py`; or a build step whose output is byte-identical to the committed files |
| **R14** | **Excise Forge from `root.py`'s re-exports**; port B20/BAAC onto `execute_product` | `grep -c "Forge" vanguard/packages/runtime/root.py` = 0; every benchmark runner reaches the engine through `entrypoint.execute` |
| **R15** | **Mark pre-T-89 benchmark rows as a distinct subject** | Every published table carries the `harness/configuration identity` field from `evidence.py`'s `arm` group; Forge-produced rows are visibly a different instrument |
| **R16** | **Delete Chimera** (~2,000 LOC, test-only) and `toolkits/composite.py` | Suite green after deletion; `agency/` LOC drops by ~2,000 |
| **R17** | **Restate the Wilson criterion operationally** in `milestones.md` | `MS-CONTROL` reads "$n \ge 30$, $\ge 18/30$ observed (Wilson LB ≥ 0.40)"; false-completion reported as "0/30, 95% CI [0, 0.10]" |

### Wave 2.5 — Structural hygiene

| # | Action | Acceptance predicate |
|---|---|---|
| **R18** | **Move `ladder/evidence.py` → `domain/evidence/`** | 3 of 5 boundary violations resolved by relocation; `domain` $A$ rises |
| **R19** | **Split `HarnessSession`** — extract context-binding, completion-admission, evidence-capture | `session.py` < 800 lines; no function with $CC > 25$; `__init__` < 60 lines |
| **R20** | **Eliminate the `ladder` name collision** and reduce `sys.path` mutation | `test_lam_ladder` green; production `sys.path` mutations = 0 |
| **R21** | **Freeze the TypeScript clients**; land T-97 only | No commits to `desktop`/`studio`/`ui-web`/`lab` until `MS-CONTROL` closes; `aether code --help` works |
| **R22** | **One mandatory benchmark result protocol** | Every runner in `benchmarks/` emits rows validated by `evidence.append_row`; ≥ 18/20 runners import the shared protocol |
| **R23** | Fix `check_path_hygiene` (23 sites); rename `test/broken/`; remove `delete.md`; drop `tools*` from the wheel | All five linters exit 0 |

### Wave 3 — Then, and only then

| # | Action |
|---|---|
| **R24** | Live L0 (T-92); T-51/T-52; freeze T-26 on a clean, green SHA; run T-27 |
| **R25** | The five-arm prompt-mass study of §10.2, paired McNemar, one evidence schema, preregistered |
| **R26** | Evaluate LSP-backed retrieval as an `IndexPort` adapter (the OpenCode differentiator) — A/B against LDA |
| **R27** | Consider `dsh`'s "loop as plugin" for the `EpisodeEngine` seam, once there is exactly one engine to parameterise |

### Ordering constraint

$$\text{R1–R5} \;\prec\; \text{R6–R10} \;\prec\; \text{R11–R17} \;\prec\; \text{R24}$$

R24 (the paid canary) must not be attempted before R6, because F-B1 guarantees the
false-completion measurement is biased optimistic; and must not be attempted before R11,
because F-C1 guarantees the between-arm comparison is confounded.

---

## 13. Appendices

### Appendix A — Complete dynamic test result

```
Ran 2855 tests in 180.449s
FAILED (failures=13, errors=53, skipped=19)
```

*Side effect observed during this run: the suite staged three files and modified the tracked `lam.sqlite` corpus — see F-A4. Reverted after measurement.*

Note that F-B5 (`code --help`) is **not** among these 66. It is not covered by any test in
the suite, which is why an effectful help path and a zero exit code on `instrument_error`
have survived. The TypeScript suite that does cover the CLI passes 81/81 — it asserts flag
documentation and daemon honesty, but never asserts an exit code.

**Failures (13):**

```
test.adapters.test_sandbox_worker              .test_execute_patch_apply
test.apps.coding_max.test_coding_max_facade    .test_facade_is_usable_by_python_callers_with_injected_service
test.apps.coding_max.test_coding_max_facade    .test_preset_finish_without_evidence_is_never_completed
test.benchmarks.test_beta14_performance_baseline.test_sqlite_wal_growth_and_write_amplification_multi_turn
test.falsifiers.test_d6_patch_context_anchoring.test_wrong_line_numbers_still_anchor_on_context
test.falsifiers.test_m5a_baseline_forensics    .test_local_tag_resolves_to_expected_contaminated_commit
test.falsifiers.test_m5a_baseline_forensics    .test_tag_is_lightweight_not_annotated
test.falsifiers.test_m7_topology_execution     .test_the_direct_form_does_real_work_through_the_canonical_path
test.falsifiers.test_rf90_generic_entrypoint   .test_code_with_fake_backend_executes_cleanly
test.falsifiers.test_rf90_generic_entrypoint   .test_resume_command_executes_without_explicit_brief
test.integration.test_lam_runtime_vertical     .test_read_patch_test_finish_uses_production_boundaries
test.test_repo_paths                           .test_audit_and_governance_from_foreign_cwd
test.tools.test_check_doc_metadata             .test_repository_living_docs_metadata_passes
```

**Error root causes (53), classified:**

| Cause | Count | Class |
|---|---:|---|
| `ModuleNotFoundError: No module named 'lab'` + `FileNotFoundError: …/lab/*.py` | ~20 | **F-D4 — deleted package** |
| `test.registry.test_plugin_isolation` (bubblewrap / UDS broker) | 8 | Environmental — isolation surface **unmeasured** |
| `test.tools.test_backend_baselines_smoke` | 12 | Benchmark registry does not self-verify |
| `test.registry.test_attenuation_rpc_gate` | 5 | Environmental (subprocess broker) |
| `ImportError: cannot import name 'run_ladder' from 'ladder'` | 1 | **F-D5 — namespace collision** |
| `ModuleNotFoundError: No module named 'setuptools'` | 2 | Environment |
| `ModuleNotFoundError: …adapters.models.ollama` | 1 | Dead reference; policy-forbidden module |
| Remainder (evidence signing, lab bench/diff, openrouter contract, SPI adapters) | ~4 | Mixed |

The ~13 bubblewrap/broker errors mean the **containment surface is currently
unmeasured**, which is in direct tension with `TC-E-032`: *"isolation claims **MUST** be
measured rather than asserted."* This is legitimately environmental and legitimately
deferrable — but it must be recorded as an *unmeasured* claim, not a satisfied one.

### Appendix B — Linter results verbatim

```
check_boundaries       exit=1
  BOUNDARY FAIL: benchmarks/ladder/evidence.py:8       ('domain.canonicalisation.digest')
  BOUNDARY FAIL: benchmarks/ladder/evidence.py:9       ('domain.evidence.disposition')
  BOUNDARY FAIL: benchmarks/ladder/l0_triad/runner.py:11 ('domain.canonicalisation.digest')
  BOUNDARY FAIL: benchmarks/product_path.py:12         ('runtime.entrypoint')
  BOUNDARY FAIL: vanguard/packages/runtime/cli.py:183  ('apps.coding_max.facade')

check_tcb_budget       exit=0
  {"baseline_logical_loc": 1307, "current_logical_loc": 1386, "threshold": 1438}
  TCB PASS: 1386 logical lines across 9 files

check_domain_blindness exit=0   (WARN: scan target missing — layer0/)
check_isolation_policy exit=0
check_path_hygiene     exit=1   (23 machine-local path violations)
```

### Appendix C — Preset catalogue, both planes

**Plane A — `packs/code-default/presets.json` (`aether.code-preset/1`)**

| preset | usd_micros | millis | tokens | turns | planner | context token_budget |
|---|---:|---:|---:|---:|---|---:|
| fast | 50,000 | 300,000 | 16,000 | 8 | **null** | 1,000 |
| balanced | 150,000 | 900,000 | 40,000 | 20 | `max_repair_rounds: 4` | 3,000 |
| max | 400,000 | 2,400,000 | 96,000 | 40 | `max_repair_rounds: 8` | 8,000 |

*The `planner` and `context` columns never reach a run (F-C3).*

**Plane B — `vg-code-*/budget-policy.json`** (hand-duplicated from Plane A; generator
`budget_policy_document()` has zero callers, F-C4)

```json
fast     {"usdMicros":"50000",  "wallClockMillis":"300000",  "tokens":"16000","turns":"8",
          "effects":"128","evaluations":"16","depth":"1"}
balanced {"usdMicros":"150000", "wallClockMillis":"900000",  "tokens":"40000","turns":"20", …}
max      {"usdMicros":"400000", "wallClockMillis":"2400000", "tokens":"96000","turns":"40", …}
```

**Plane B — `vg-code-*/manifest.json`**: identical across all three except `harness` and
`budgetPolicy` (F-C1).

### Appendix D — Manifest inventory

33 harness manifests exist under `vanguard/packages/agency/manifests/`:

```
vg-1-forge-v2                    vg-code-max-v2b                vg-code-v090-lex-surgical
vg-bugfix-v090-v1-direct         vg-code-max-v3                 vg-code-v090-lim-falsifier
vg-bugfix-v090-v2-reproduce-verify vg-code-max-v3luna           vg-code-v090-opencode-shaped
vg-chimera-v1                    vg-code-opencode-shaped        vg-code-v090-react-control
vg-code-balanced                 vg-code-swe-mini               vg-herbs
vg-code-chimera                  vg-code-v090-claude-shaped     vg-research-minimal
vg-code-claude-shaped            vg-code-default                vg-research-v090-v1-local
vg-code-critic-reviser           vg-code-explain                vg-research-v090-v2-web-corroborated
vg-code-fast                     vg-code-lex                    vg-shell-only
vg-code-max                      vg-code-max-v2                 vg-table-default
                                                                vg-tutor-v090-v1-read-search
                                                                vg-tutor-v090-v2-evidence-graph
```

`vg-code-claude-shaped` and `vg-code-opencode-shaped` each carry their own
`system-prompt.txt`, `routing-policy.json`, `context-policy.json`, `approval-policy.json`
and a `REFERENCE.md`. **The differentiation machinery §10.2 calls for already exists**;
it is simply not wired to the three product arms.

### Appendix E — Reproduction script

```bash
#!/usr/bin/env bash
# .draft/audit/reproduce.sh — regenerate every measurement in this report
set -uo pipefail
cd "$(git rev-parse --show-toplevel)"

echo "== subject =="
git rev-parse HEAD; git status --short

echo "== linters (justfile 'check' recipe body) =="
for l in check_boundaries check_tcb_budget check_domain_blindness \
         check_isolation_policy check_path_hygiene; do
  python3 tools/linters/$l.py; echo "$l exit=$?"
done

echo "== configuration identity proof (F-C1) =="
for p in fast balanced max; do
  printf '%-9s ' "$p"
  sed -E 's/"harness":[^,]*/"H"/; s/"budgetPolicy":[^,]*/"B"/' \
    vanguard/packages/agency/manifests/vg-code-$p/manifest.json | sha256sum
done

echo "== dead production API (F-C3, F-C4) =="
for s in compile_preset compile_pack budget_policy_document; do
  printf '%-24s ' "$s"
  grep -rn "$s" --include=*.py . 2>/dev/null \
    | grep -v __pycache__ | grep -v '\.venv' \
    | grep -v 'packs/code-default/load.py' | wc -l
done

echo "== entrypoint clone (F-D1) =="
diff <(sed -n '27,39p' vanguard/packages/apps/coding_max/facade.py) \
     <(sed -n '40,52p' vanguard/packages/runtime/entrypoint.py)

echo "== deleted lab package (F-D4) =="
ls -d lab 2>&1
git show --stat --oneline 67f033d5 -- lab | head -12

echo "== full dynamic suite =="
.venv/bin/python -m unittest discover -s test -t . 2>&1 | tail -3
```

### Appendix E2 — Reconciliation with the two sibling audits

Two further audits of the same subject sit in this directory. They are **complementary,
not contradictory**: they cover surfaces this report did not (the `.agents/` capability
layer, `docs/backend/` staleness, the TypeScript clients, the `.draft/todo/` synthesis
dossier), while this report contributes the quantitative structure (§8), the cryptographic
preset-identity proof (F-C1), and the statistical corrections (§9).

**Claims imported after independent verification**

| Claim | Source | This audit's verification |
|---|---|---|
| `abstained` and `completed` both project to `"completed"` | `AETHER_SOTA…AUDIT` §4.2 | **Confirmed and extended.** Four sites, plus a contradictory fifth mapping to `"abandoned"` (F-B1). The fifth site is new here. |
| `code --help` is an effectful request | `AETHER_SOTA…AUDIT` §4.2 | **Confirmed and extended.** Also exits `0` on `instrument_error` — the exit-code defect is new here (F-B5). |

**Claims that did NOT reproduce on this subject** *(recorded as negative results, not as
criticism — both are consistent with a transient state at the time of that audit)*

| Claim | Source | Measured here |
|---|---|---|
| `npm --workspace @vanguard/cli test` FAILS on `transport`, `wave2`, `wave4` | `AETHER_SOTA…AUDIT` §1.4 | **Passes 81/81, 0 fail.** All ten source test files are present in `dist/test/` and were executed — this is not a stale-build artefact. |
| `lda doctor` and `lda identity` disagree about index freshness | `AETHER_SOTA…AUDIT` §4.2 | **Both agree.** `identity` reports `freshness_vs_head: FRESH`, `doctor` reports `index_healthy: true`, both bound to HEAD. The index has evidently been rebuilt since; at that time it was pinned to `622131da` against HEAD `dfb0bb64`, which is a *staleness* condition rather than a design defect. |

**A claim this report contests**

`EXHAUSTIVE_ARCHITECTURAL_AUDIT_EXECUTION_VS_CODE.md` Thesis 1 holds that the execution
documents are *"100% truthful"* and that Wave 2 is *"correctly held as unaccepted."*

That was true at `622131da`. It is **false at `dfb0bb64`**: the work was merged to `main`
(F-A1), so the documents' central operative claim — *"No task may be checked and no L0/L2
subject frozen until those are repaired… and the subject is clean"* — now describes a
state the repository has already left. The documents are *honest*; they are no longer
*current*.

The mechanism of the disagreement is itself the finding. Both sibling audits report
"31/31 named falsifiers green" and Wave 1 "all PASS", inheriting those figures from the
developer log rather than from a full suite execution. This report ran the full suite and
found **66 red** (13 failures, 53 errors). The three findings that only a full run could
surface — the deleted `lab/` package (F-D4), the `ladder` namespace collision (F-D5), and
the suite's mutation of the working tree (F-A4) — were invisible to a narrow-set
verification. **This is direct empirical support for F-A2: reporting a curated green while
the wide red goes unmeasured is how all three of these defects survived two prior
audits.**

**Findings unique to this report and unchallenged by either sibling:** F-C1 (the three
arms are cryptographically identical), F-C2 (the T-79 falsifier is mutation-inadequate),
F-D4, F-D5, F-A4, and the §8/§9 quantitative results. The headline verdict and the
remediation ordering in §12 stand.

### Appendix F — References

**Architecture and design**
- Martin, R. C. *Agile Software Development: Principles, Patterns, and Practices.* Prentice Hall, 2002. (SRP, DIP, ADP, SDP, SAP; the $I$/$A$/$D$ metrics)
- Martin, R. C. *Clean Architecture: A Craftsman's Guide to Software Structure and Design.* Prentice Hall, 2017.
- Cockburn, A. "Hexagonal Architecture (Ports and Adapters)." 2005.
- Vernon, V. *Implementing Domain-Driven Design.* Addison-Wesley, 2013, ch. 4.
- Evans, E. *Domain-Driven Design.* Addison-Wesley, 2003.
- Hunt, A. & Thomas, D. *The Pragmatic Programmer.* Addison-Wesley, 1999, §7 (DRY).
- Fowler, M. "Event Sourcing." martinfowler.com, 2005.

**Measurement and quality**
- McCabe, T. J. "A Complexity Measure." *IEEE Trans. Software Eng.* SE-2(4), 1976, 308–320.
- Roy, C. K., Cordy, J. R. & Koschke, R. "Comparison and evaluation of code clone detection techniques and tools." *Sci. Comput. Program.* 74(7), 2009, 470–495.
- DeMillo, R. A., Lipton, R. J. & Sayward, F. G. "Hints on Test Data Selection." *IEEE Computer* 11(4), 1978, 34–41.
- Jia, Y. & Harman, M. "An Analysis and Survey of the Development of Mutation Testing." *IEEE TSE* 37(5), 2011, 649–678.
- Beck, K. *Test-Driven Development: By Example.* Addison-Wesley, 2003.

**Security**
- Anderson, J. P. *Computer Security Technology Planning Study.* ESD-TR-73-51, USAF, 1972. (reference monitor)
- Saltzer, J. H. & Schroeder, M. D. "The Protection of Information in Computer Systems." *Proc. IEEE* 63(9), 1975, 1278–1308.

**Statistics and experimental design**
- Wilson, E. B. "Probable Inference, the Law of Succession, and Statistical Inference." *JASA* 22(158), 1927, 209–212.
- Brown, L. D., Cai, T. T. & DasGupta, A. "Interval Estimation for a Binomial Proportion." *Statistical Science* 16(2), 2001, 101–133.
- Hanley, J. A. & Lippman-Hand, A. "If Nothing Goes Wrong, Is Everything All Right?" *JAMA* 249(13), 1983, 1743–1745. (rule of three)
- McNemar, Q. "Note on the sampling error of the difference between correlated proportions or percentages." *Psychometrika* 12(2), 1947, 153–157.
- Campbell, D. T. & Stanley, J. C. *Experimental and Quasi-Experimental Designs for Research.* Rand McNally, 1963.
- Wohlin, C. et al. *Experimentation in Software Engineering.* Springer, 2012.
- Popper, K. *The Logic of Scientific Discovery.* Hutchinson, 1959.
- Cover, T. M. & Thomas, J. A. *Elements of Information Theory.* 2nd ed., Wiley, 2006. (data-processing inequality, §2.8)

**Agent systems (2026 landscape)**
- "Dive into Claude Code: The Design Space of Today's and Future AI Agent Systems." arXiv:2604.14228. <https://arxiv.org/html/2604.14228v1>
- "Claude Code Agent Harness: Architecture Breakdown." WaveSpeed. <https://wavespeed.ai/blog/posts/claude-code-agent-harness-architecture/>
- "DeepSeek open sources an agent harness where everything is a plugin." The New Stack. <https://thenewstack.io/deepseek-harness-open-source-plugins/>
- "The Open-Sourcing of DeepSeek Harness Opens the Door to Modular, Unbundled AI Agent Infrastructure." InfoQ, 2026-08. <https://www.infoq.com/news/2026/08/deep-seek-harness/>
- "How Coding Agents Actually Work: Inside OpenCode." M. Abboud. <https://cefboud.com/posts/coding-agents-internals-opencode-deepdive/>
- "How Hermes implements an open source agent harness architecture." Arize AI. <https://arize.com/blog/how-hermes-implements-open-source-agent-harness-architecture/>
- "Pi vs Hermes vs Codex vs Claude Code: Which AI Agent Fits?" <https://mcplato.com/en/blog/pi-agent-hermes-codex-claude-code-mcplato/>
- "AI Agent Harness Comparison: DeepSeek Harness vs Pi vs OpenCode vs Hermes vs Claude Code." Tencent Cloud. <https://www.tencentcloud.com/techpedia/147665>

**Repository-internal normative sources**
- `docs/execution/spec.md` — `TC-E-001` … `TC-E-062`, invariants `I-7`, `I-TCB`, `INV-DELTA-1…5`
- `docs/execution/milestones.md` — `MS-INSTRUMENT`, `MS-TRUTH`, `MS-RESUME`, `MS-SEE`, `MS-CHANGE`, `MS-CONTROL`, `MS-META`
- `docs/execution/tasks.md` — T-04, T-26, T-27, T-79, T-89, T-92 … T-97
- `docs/architecture/boundaries.md` — `INV-B-001` hexagonal dependency lattice

---

## Document control

| Field | Value |
|---|---|
| Subject SHA | `dfb0bb64` |
| Subject state | clean |
| Findings | **5** governance · **5** correctness · 4 experimental-design · 7 structural (**21**) |
| Blocking for Wave 3 | F-A1, F-A3, F-A4, F-B1, F-B2, F-C1, F-C2, F-D4 |
| Measurements reproducible via | Appendix E |
| Sibling audits | reconciled in Appendix E2: 2 claims imported after verification, 2 did not reproduce, 1 contested |
| Author | external architectural review |
| Status | **draft — no code or documentation was modified in producing this report.** Executing the suite dirtied the tree (F-A4); the mutation was reverted and `git status` restored to its pre-audit state. |

