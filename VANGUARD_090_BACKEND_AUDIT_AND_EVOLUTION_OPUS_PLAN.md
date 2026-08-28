# Vanguard Backend Reality Audit and Evolution Plan — `0.9.0b1` → `0.9.1`

**Document type:** independent code-first audit and two-horizon engineering plan
**Scope:** backend only (`vanguard/packages/**`, `packs/`, `schemas/`, `tools/`, `ci/`, `test/`)
**Branch under audit:** `feat/vanguard-0.9.0b1-beta-evolution`
**Audit date:** 2026-08-28
**Method:** every claim below was re-derived by executing the repository. Documentation was treated
as a claim, not as evidence. No production code or canonical documentation was modified.
**Status of this document:** assessment and plan. It authorises nothing by itself.

---

## How to read this report

The report is organised as two chapters, as requested.

- **Chapter I — Reality Audit** (§1–§11) establishes what is true today. Everything in it is backed
  by a command that was actually run, with its observed output quoted. Where a previous document
  made a claim, that claim is reproduced or falsified explicitly.
- **Chapter II — Two-Horizon Evolution Plan** (§12–§15) turns those findings into an ordered plan:
  Horizon 1 finishes and freezes `0.9.0b1`; Horizon 2 performs an evolutionary refactor into
  `0.9.1`.

Every conclusion carries one of the following dispositions, used consistently throughout:

| Disposition | Meaning |
|---|---|
| `IMPLEMENTED` | Code exists, is reachable from a production path, and executes as claimed. |
| `PARTIAL` | Code exists and works for some consumers but not for the full claimed surface. |
| `DOCUMENTARY` | Asserted in prose only; no executable evidence supports it. |
| `BLOCKED` | Implementation exists but a named external dependency prevents completion. |
| `OBSOLETE` | Present in the tree but no longer reachable or meaningful. |
| `FALSIFIED` | A prior claim that this audit actively disproved. |

A note on epistemic hygiene, because it materially changes the plan: this repository maintains an
unusually sharp separation between *tests passing*, *evidence verifying*, and *a milestone being
accepted*. That separation is a genuine asset and the audit preserves it. But it is also the source
of most of the confusion in the existing documents, which routinely quote one as if it were another.
Section 3 untangles this specifically.

---
---

# CHAPTER I — REALITY AUDIT

---

## 1. Executive verdict

**Vanguard is a real, working, unusually disciplined event-sourced agent substrate that is much
closer to a shippable beta than its own documentation suggests — and its most serious problems are
not architectural. Preserve and simplify. Do not rewrite.**

The audit's five headline conclusions:

### 1.1 The foundation is sound and the architecture is honest

The core theses — events at the centre, append-only causal history, a domain-blind kernel,
capability attenuation, multidimensional budgets, content-addressed artifacts, event-derived
recoverable state — are not aspirational prose. They are implemented, enforced by executable
linters, and covered by 2,152 tests of which 2,141 pass. The kernel is genuinely small (1,373
logical lines across 9 files, under its own 1,438 ceiling) and genuinely domain-blind (verified, not
asserted). The hexagonal boundary linter passes across 414 source files. Event contracts are
codegen-derived and perfectly consistent — 63 kinds in the readable roster, 63 in the wire enum,
zero divergence in either direction.

I looked hard for evidence that the foundation was irrecoverable, because the brief requires proving
that before recommending a rewrite. I did not find it. I found the opposite: the invariants that
would be expensive to retrofit are the ones already in place.

### 1.2 The single most valuable finding is a measured, fixable hot-path defect

Not an architectural flaw — an implementation detail with a large measured cost.

A minimal two-receipt coding episode writes **90 events**, of which **72 (80%) are plugin lifecycle
ceremony** — six state-transition events for each of twelve manifest components, emitted on every
single episode regardless of whether the component is used. Those 72 events cost roughly 73 KB of
the ~99 KB envelope payload.

Compounding this, `LedgerEmitter._write` (`vanguard/packages/runtime/ledger_emitter.py:394`) appends
**every event individually** — `self.store.append([envelope])` — against a SQLite store opened with
`synchronous="FULL"`. Measured append throughput in that configuration is **519 events/second**.
Batched, the same store does 3,949 events/second (7.6×).

The arithmetic closes exactly: 90 events ÷ 519 events/s ≈ **173 ms**, and the measured difference
between an in-memory episode (237 ms) and a file-backed WAL episode (387 ms) is **150 ms**. The
entire durability overhead of the product path is explained by unbatched fsyncs on events that are
80% ceremony.

Two independent, low-risk changes — group-commit at turn boundaries, and collapsing unused-component
lifecycle to a single summary event — should remove the large majority of that 150 ms and the large
majority of the storage amplification, with no change to any invariant. This is the highest
value-per-unit-risk work in the entire plan.

### 1.3 The "universal substrate" claim is not yet demonstrated, and the gap is precisely located

This is the most important *product* finding, and it is more specific than any previous document
states.

The product thesis requires that materially different agent systems be different compositions of the
same primitives. I tested this directly by composing and executing every shipped manifest.

- All **8** manifests on disk compose successfully through `Runtime.compose`.
- `vg-code-default` (the coding harness) executes end-to-end. Proven, and covered by the M-4
  evidence bundle.
- **`vg-code-explain` executes end-to-end.** I ran it: a read-only code-explanation episode through
  the canonical `Runtime.execute_harness`, terminal state `completed`, one `fs.read` receipt, zero
  kernel changes. This is a genuine second reference workflow and it *already works today*. It is
  simply not registered, not tested, and not documented.
- **`vg-table-default` — the only genuinely non-coding domain — cannot execute.** It composes, and
  its verbs `table.read`/`table.patch` correctly resolve to bindings via `TableBindingProvider`. But
  `TableWorldEnvironment` implements **none** of the eight `EnvironmentPort` methods (`profile`,
  `snapshot`, `observe`, `preview`, `apply`, `reconcile`, `compensate`, `dispose`). Execution dies
  at `session.py:614` → `wiring.py:497` with a bare `AttributeError: 'TableWorldEnvironment' object
  has no attribute 'profile'`.

So the honest characterisation of Vanguard today is: **a governed coding-agent runtime with a
credible and largely-built meta-framework contract, one working non-trivial second workflow, and one
clearly-scoped adapter gap standing between it and a demonstrated multi-domain substrate.** That
adapter gap is roughly a day of work on a single file, not a redesign.

### 1.4 The documentation is stratified, and only one layer is trustworthy

`docs/03_execution/sprint_active.md` is **accurate**. I re-derived its entire evidence table
independently with `tools/linters/verify_evidence.py` and it matches bundle-for-bundle, verdict-for-
verdict, including the subtle cases.

`VANGUARD_BACKEND_M1_M9_MASTER_REPORT.md` is **stale and materially wrong**. It reports M-6.5 as
`BLOCKED`, M-7 as `IN_PROGRESS`, and M-8 as `PACKAGE_READY`. All three have since produced bundles
that verify `passed`. It also quotes "566/566 tests passing" for a named subset that today collects
**614**, and quotes a total suite that is green when the suite in fact has **one failing test**.

The single failing test is itself the perfect illustration of the problem: it is
`test/tools/test_check_execution_truth.py`, and it fails because `backlog.md` and `sprint_active.md`
disagree about the state of four work packages. The repository has an automated consistency check
for documentary drift, that check is wired into the suite, and it is currently red. The tree is not
green, and the reason it is not green is documentation.

### 1.5 The beta gap is real but small, and it is concentrated in the product surface, not the engine

Packaging is in better shape than expected: the wheel builds, installs cleanly outside the checkout,
ships its schemas, manifests and packs, and `vanguard doctor` runs correctly from an installed
location against a foreign workspace. That is a genuine and often-underestimated achievement.

What is missing is almost entirely at the CLI/API boundary:

- The CLI exposes only `init`, `doctor`, `run`. There is no `resume`, `status`, `events`, or
  `artifacts` command, even though the underlying recovery, projection and artifact machinery all
  exist and are tested.
- `cmd_run` hardwires `OpenRouterModel` and hard-fails without `OPENROUTER_API_KEY`. There is no
  offline path at the product surface, despite `FakeModel` living in the production adapter package.
  "Offline-after-install verification" is therefore not achievable today by a user.
- Version identity is triplicated, including one hardcoded string literal
  (`service/service.py:379`).
- Five separate `SqliteEventStore(":memory:")` fallbacks exist, one of them in `RuntimeBootstrap`,
  the ADR-0089 *target* entrypoint.

None of these are hard. All of them are visible to the first person who installs the beta.

### 1.6 Verdict

**Preserve the architecture. Simplify the runtime. Finish the product surface. Do not rewrite, and
do not refactor before shipping.**

The ordered recommendation is: fix the documentary drift that is failing the suite; close the small
set of product-surface gaps; register and test the second workflow that already works; fix the
TableWorld adapter to make the multi-domain claim true; freeze `0.9.0b1`. Only then perform the
Horizon 2 consolidation, using the beta measurements as the baseline against which simplification is
judged.

The governance apparatus should be substantially relaxed for ordinary work — but the specific
mechanisms that protect kernel neutrality, causal integrity and budget conservation should be kept
exactly as they are. They are cheap, automated, and they are the reason this codebase is in as good
a condition as it is.

---

## 2. Verified repository baseline

Everything in this section was produced by running the command shown, in the repository root, on
2026-08-28.

### 2.1 Toolchain reality — and a broken developer environment

| Fact | Value | Command |
|---|---|---|
| System interpreter | Python 3.12.3 | `python3 -V` |
| pytest available to system interpreter | 9.1.1 (`~/.local/bin/pytest`) | `python3 -c "import pytest"` |
| **Checked-in `.venv` interpreter** | **has no `pytest` installed** | `.venv/bin/python -m pytest` → `No module named pytest` |

**Finding B-01 — `DOCUMENTARY` / developer-environment defect.** The repository's own `.venv`
cannot run the test suite. Any contributor who follows the obvious path (`.venv/bin/python -m
pytest`) sees `No module named pytest` and concludes the suite is broken. `pyproject.toml` does
declare `[project.optional-dependencies] dev = ["pytest>=7.0.0"]`, so the fix is a documented
`pip install -e '.[dev]'` step, not new packaging. This is trivial but it is the very first thing a
new contributor or a beta evaluator hits.

All measurements in this report therefore use the system interpreter.

### 2.2 Test suite — the tree is not green

```
$ python3 -m pytest -q -p no:randomly
1 failed, 2141 passed, 10 skipped, 1 warning, 39573 subtests passed in 93.75s
```

```
$ python3 -m pytest --collect-only -q
2152 tests collected
```

Collection is fast (4.00 s) and the full run is 93.75 s. The subtest count (39,573) is worth noting:
much of this suite is table-driven vector verification, which is why the effective assertion density
is far higher than the test count suggests.

Per-directory collection:

| Directory | Tests | Directory | Tests |
|---|---:|---|---:|
| `test/runtime/` | 589 | `test/security/` | 55 |
| `test/falsifiers/` | 476 | `test/packs/` | 46 |
| `test/contracts/` | 369 | `test/registry/` | 27 |
| `test/adapters/` | 143 | `test/trust/` | 22 |
| `test/agency/` | 105 | `test/benchmarks/` | 20 |
| `test/kernel/` | 94 | `test/integration/` | 9 |
| `test/tools/` | 94 | `test/governance/` | 5 |
| `test/lab/` | 83 | `test/apps/` | 4 |

`test/broken/` collects nothing by design — it holds negative fixtures for the linters, not tests.

### 2.3 The single failure, in full

```
FAILED test/tools/test_check_execution_truth.py::TestExecutionTruth::
       test_canonical_execution_documents_are_consistent

AssertionError: Lists differ:
['package state drift for WP-A3: backlog=IN_PROGRESS,   board=EVIDENCE_READY',
 'package state drift for WP-A4: backlog=PACKAGE_READY, board=EVIDENCE_READY',
 'package state drift for WP-B2: backlog=BLOCKED,       board=EVIDENCE_READY',
 'package state drift for WP-B4: backlog=PACKAGE_READY, board=EVIDENCE_READY'] != []
```

**Finding B-02 — `IMPLEMENTED` (the checker) / documentary drift (the failure).** This is a
documentation inconsistency, not a code defect. In all four cases `sprint_active.md` is *ahead* of
`backlog.md` — the board records evidence that has since been published and verified, and the
backlog was not updated. The direction matters: the board is the accurate document and the backlog
is lagging, which is the benign direction of drift.

It also means something structurally important: **this repository has an automated defence against
documentary drift, it works, and it is currently firing.** That is a good sign about the mechanism
and a bad sign about the discipline. Repairing this is task `H1-01` and it is the cheapest green-
tree win available.

### 2.4 Architectural invariant linters — all pass

| Linter | Result | Command |
|---|---|---|
| TCB budget | `PASS: 1373 logical lines across 9 files (alarm above 1438)` | `python3 tools/linters/check_tcb_budget.py` |
| Hexagonal boundaries | `PASS: 414 source files checked` | `python3 tools/linters/check_boundaries.py` |
| Domain blindness | `PASS: no coding\|pytest\|ast tokens in domain/, kernel/` | `python3 tools/linters/check_domain_blindness.py` |
| Kernel neutrality (RF-98) | `PASS: kernel is domain-neutral` | `python3 tools/linters/check_kernel_neutrality.py` |

Kernel file-by-file logical LOC, as reported by the budget linter itself:

| File | Logical LOC |
|---|---:|
| `dispatch.py` | 372 |
| `grants.py` | 201 |
| `attenuation.py` | 171 |
| `budget.py` | 139 |
| `model.py` | 137 |
| `provenance.py` | 110 |
| `policy.py` | 106 |
| `classifier.py` | 96 |
| `__init__.py` | 41 |
| **Total** | **1373** (baseline 1307, alarm 1438) |

**Finding B-03 — `IMPLEMENTED`.** The kernel LOC and boundary claims in the master report are
**reproduced exactly** (1373 / 1438, 414 files). This is one of the few numeric claims in the prior
documentation that survives verification unchanged, and it deserves credit.

**Finding B-04 — `OBSOLETE`.** `check_domain_blindness.py` emits
`DOMAIN-BLINDNESS WARN: scan target missing (not an error): layer0/`. `layer0/` was deleted under
ADR-0081 (plugin lifecycle runtime absorption / layer0 deletion). The linter still carries the dead
scan target. Harmless, but it is exactly the kind of residue Horizon 2 should sweep.

The kernel-neutrality receipt also reports which packs it scanned:
`["code-default", "code-explain", "formal-graph-coloring", "formal-sat"]` — useful confirmation that
`code-explain` is a first-class pack in at least one part of the system.

### 2.5 Backend size

Measured with `find … -name '*.py' -not -path '*__pycache__*' | xargs cat | wc -l`:

| Package | Raw LOC | Files | Role |
|---|---:|---:|---|
| `runtime/` | 20,947 | 74 | composition, session, ledger, service, governance |
| `adapters/` | 9,933 | 55 | models, environments, stores, sandbox, evaluators |
| `domain/` | 8,714 | 39 | pure values, JCS, wire, reducer, selectors, evidence |
| `agency/` | 2,604 | 11 | episode engine, manifests, context compilation |
| `kernel/` | 1,747 | 9 | the TCB (1,373 *logical*) |
| `ports/` | 1,509 | 15 | SPI / port protocols |
| **`apps/`** | **0** | **1** | **empty package — dead** |
| **Backend total** | **~45,454** | **204** | |

The clients (`vanguard/clients/{cli,client-core,studio}`) contain no Python; they are TypeScript and
out of scope for this backend-only audit.

**Finding B-05 — `OBSOLETE`.** `vanguard/packages/apps/` contains only an empty `__init__.py`. It is
the residue of the `apps/coding` package retired at M-3. See also Finding D-06 (six matching hollow
test files). Delete in Horizon 2.

**Observation.** `runtime/` at 20,947 LOC is 46% of the backend and larger than `domain` + `kernel` +
`ports` + `agency` combined. That concentration, not the total size, is the structural issue, and
§7 maps it precisely.

### 2.6 Largest modules

| LOC | Module | Assessment |
|---:|---|---|
| 1,401 | `runtime/session.py` | Oversized. The session lifecycle god-module. Horizon 2 extraction target. |
| 1,343 | `runtime/service/service.py` | Oversized. Daemon command dispatch; contains `_cmd_Resume`. |
| 1,057 | `domain/artifacts/manifest.py` | Large but cohesive — the manifest algebra. Justified. |
| 995 | `adapters/models/openrouter.py` | Large adapter; provider quirks. Justified. |
| 955 | `adapters/environment/git.py` | The working `EnvironmentPort` implementation. Justified. |
| 820 | `domain/ledger/reducer.py` | The event reducer; 63 kinds. Justified by fan-out. |
| 771 | `runtime/delegation.py` | Recursion/spawn. Cohesive. |
| 761 | `agency/episode/engine.py` | The turn loop. Cohesive. |
| 710 | `runtime/service/studio_gateway.py` | HTTP gateway. Contains the only `/health` endpoint. |
| 706 | `domain/wire/types_gen.py` | **Generated.** Not hand-maintained; not bloat. |
| 699 | `runtime/root.py` | Three entrypoints (§4.3). Consolidation target. |
| 689 | `runtime/artifacts.py` | CAS. Cohesive. |

Only `session.py` and `service.py` are genuinely oversized in the sense of mixing responsibilities.
The rest are large because their subject matter is large, which is a different thing and must not be
"simplified" by splitting.

### 2.7 Governance and contract surface

| Artifact class | Count | Command |
|---|---:|---|
| ADRs (`docs/02_decisions/NNNN-*.md`) | 36 | `ls docs/02_decisions/[0-9]*.md \| wc -l` |
| Markdown documents under `docs/` | 171 | `find docs -name '*.md' \| wc -l` |
| Executable linters | 24 | `ls tools/linters/*.py \| wc -l` |
| Falsifier test files | 48 | `ls test/falsifiers/*.py \| wc -l` |
| JSON schemas | 465 | `find schemas -name '*.json' \| wc -l` |
| Evidence bundles | 16 (+ acceptances) | `ls docs/03_execution/evidence/` |
| Shipped manifests | 8 on disk / **6 registered** | §6.4 |

171 documents to 204 backend source files is close to a 1:1 documentation-to-code ratio. §10 treats
this as the governance problem it is.

---

## 3. Claims from prior reviews: confirmed, falsified, or unverified

The brief instructs me not to trust the previous analysis. The `director_review_v5/` directory
contains only `test.md`, which is a verbatim copy of this audit's own prompt — **there is no prior
v5 report to reproduce.** The claims tested below are therefore drawn from the two documents that do
make testable assertions: `VANGUARD_BACKEND_M1_M9_MASTER_REPORT.md` (v1.0.0) and the current
`docs/03_execution/sprint_active.md`.

### 3.1 Claims from `VANGUARD_BACKEND_M1_M9_MASTER_REPORT.md`

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| C-01 | "`566/566 tests passing` (`test/kernel`, `test/contracts`, `test/agency`, `test/packs`)" | **FALSIFIED** | That exact subset collects **614** tests today, not 566. The number is stale. |
| C-02 | Implied green tree | **FALSIFIED** | Full suite: **1 failed**, 2141 passed, 10 skipped. See §2.3. |
| C-03 | "TCB LOC: 1373 / 1438" | **CONFIRMED** | `check_tcb_budget.py` → `1373` logical lines, threshold `1438`. Exact match. |
| C-04 | "`414 source files clean`" (boundary linter) | **CONFIRMED** | `check_boundaries.py` → `BOUNDARY PASS: 414 source files checked`. Exact match. |
| C-05 | "Domain-Blindness Invariant (I-7): zero domain/ast/pytest tokens" | **CONFIRMED** | `check_domain_blindness.py` → `PASS`. (With a stale `layer0/` scan target; see B-04.) |
| C-06 | M-4 status `IN_PROGRESS` | **FALSIFIED** | `M-4-rf95-candidate-07.json` verifies `passed`. M-4's technical predicate is met. |
| C-07 | M-5a status `PACKAGE_READY` | **CONFIRMED (as blocked)** | No M-5a bundle exists. `CONVERGENCE-BASE-v1` is genuinely absent. See §3.3. |
| C-08 | M-5b status `PACKAGE_READY` | **FALSIFIED** | `M-5b-graph-coloring.json` verifies **`failed`**. It is worse than "package ready". |
| C-09 | M-6 status `PACKAGE_READY` | **FALSIFIED (understated)** | `M-6-canonical-recursion-order10.json` verifies `passed`. M-6 is done. |
| C-10 | M-6.5 status `BLOCKED` | **FALSIFIED** | `M-6.5-…-order13.json` verifies `passed`. The study completed. |
| C-11 | M-7 status `IN_PROGRESS (WP-A3)` | **FALSIFIED** | `M-7-topology-order12.json` verifies `passed`. |
| C-12 | M-8 status `PACKAGE_READY (WP-A4)` | **FALSIFIED (understated)** | `M-8-durable-memory-order12.json` verifies `passed`. |
| C-13 | "Validate full candidate build passing `./ci/release_qualify.sh` with zero test regressions" | **FALSIFIED (misdescribes the tool)** | `release_qualify.sh` runs **no tests and no linters**. See §3.4. |
| C-14 | M-6 needs "Complete `ChildRuntimePort` … enforcing componentwise child budget reservation (`depth >= 3`)" | **FALSIFIED (already done)** | `test/falsifiers/test_rf101_rf112_canonical_recursion.py` passes; the M-6 bundle records 57 falsifiers at depth 3 with kill-tree. |
| C-15 | M-9 needs "Single-host packaging in `pyproject.toml` exposing `vanguard` API and `vg` CLI" | **PARTIAL** | Packaging works; the console script is named **`vanguard`**, not `vg`. See §6.2. |

**Net assessment of the master report: 4 of 15 testable claims confirmed, 10 falsified, 1 partial.**
Critically, the falsifications run in *both* directions — the report is pessimistic about M-6/M-6.5/
M-7/M-8 (all four are actually accepted) and optimistic about the test suite and M-5b. It is not
biased; it is simply stale, and it was written against a snapshot that has since moved.

**Recommendation:** `VANGUARD_BACKEND_M1_M9_MASTER_REPORT.md` should be moved to
`docs/_archive/reviews/backend/` and explicitly marked non-authorising. Leaving a document with a
`1.0.0` version stamp and a "Complete Implementation, Remediation & Qualification Guide" subtitle at
the repository root, when 10 of its 15 checkable claims are wrong, is an active hazard — it is the
first document a new engineer or evaluator will read.

### 3.2 Claims from `docs/03_execution/sprint_active.md`

I re-derived the board's entire evidence table independently:

```
$ python3 tools/linters/verify_evidence.py --json
EVIDENCE VERIFIER: 6/16 bundles verify as passed
```

| Bundle | Claimed | **Independently verified** | Board says | Match? |
|---|---|---|---|---|
| `M-4-rf95-candidate-03` | undeterminable | `failed` | preserved history | ✅ |
| `M-4-rf95-candidate-05` | passed | `failed` | `failed` (raw-hex sig, wrong reviewer key) | ✅ |
| **`M-4-rf95-candidate-07`** | passed | **`passed`** | `passed` | ✅ |
| `M-4-rf95-order9` | undeterminable | `failed` | preserved history | ✅ |
| **`M-5b-graph-coloring`** | undeterminable | **`failed`** | `failed` | ✅ |
| **`M-6-canonical-recursion-order10`** | passed | **`passed`** | `passed` | ✅ |
| `M-6-canonical-recursion-order9` | passed | `failed` | superseded | ✅ |
| `M-6-canonical-recursion` | undeterminable | `failed` | superseded | ✅ |
| `M-6.5-…-order11` | passed | `failed` | superseded | ✅ |
| `M-6.5-…-order12` | passed | `passed` | superseded by order13 | ✅ |
| **`M-6.5-…-order13`** | passed | **`passed`** | `passed` | ✅ |
| `M-6.5-attributable-paired-study` | passed | `undeterminable` | superseded | ✅ |
| `M-7-topology-order11` | passed | `failed` | superseded | ✅ |
| **`M-7-topology-order12`** | passed | **`passed`** | `passed` | ✅ |
| `M-8-durable-memory-order11` | passed | `failed` | superseded | ✅ |
| **`M-8-durable-memory-order12`** | passed | **`passed`** | `passed` | ✅ |

**Finding C-16 — `CONFIRMED`, unanimously.** Every single row of `sprint_active.md`'s evidence table
matches independent re-derivation, including the awkward ones (a bundle whose own claimed outcome
verifies *worse* than claimed; bundles that are `failed` but deliberately preserved as history).

This is a genuinely impressive result and it should change how the team allocates trust:
**`sprint_active.md` is the authoritative status document and it has earned that status.** The
verifier is not a rubber stamp — it fails 10 of 16 bundles, including several the producers
originally claimed as `passed`. A verification tool that only ever agrees with its inputs proves
nothing; this one disagrees, specifically, and for stated reasons.

### 3.3 The `CONVERGENCE-BASE-v1` claim

**Verdict: CONFIRMED — genuinely absent, and genuinely external.**

`sprint_active.md` states that `CONVERGENCE-BASE-v1` is absent and that
`prepare_convergence_baseline.py` produces only a candidate declaring `CANDIDATE_NOT_A_BASELINE`
with `commit_sha`, `tag_object_sha` and `tree_digest` unresolved. There is no M-5a bundle in
`docs/03_execution/evidence/`, which corroborates this.

The important interpretive question the brief asks is *what kind* of gap this is. The answer:

- It is **not** missing implementation. The baseline builder exists and runs.
- It is **not** a failed experiment.
- It **is** a **missing release identity** — specifically, an annotated, remotely-resolvable Git tag
  that only a release owner with push rights can create.

Per the brief's explicit instruction, this must not be presented as a technical blocker to a locally
functional beta. It is a *release-integrity* requirement (category 4 in the brief's taxonomy), not
an implementation requirement (category 1). M-5a's *code* — AgentView, authority provenance,
checkpoint verification, unknown-event preservation, cold reconstruction — is implemented and tested.
What is missing is a signature on a tag.

**This distinction drives the entire Horizon 1 plan: `0.9.0b1` is qualified on reproducible automated
evidence, and the tag-dependent formal acceptance is listed separately as optional (§12.6).**

### 3.4 What `ci/release_qualify.sh` actually does

The master report (C-13) describes it as validating "the full candidate build … with zero test
regressions". It does not.

`ci/release_qualify.sh` is 15 lines and execs `tools/release_qualification.py` (212 lines). Its
checks, read from the source:

| Check | Function |
|---|---|
| External Git receipt matches subject | `_check_external_git_receipt` |
| Signed envelope subject matches candidate | `_check_signed_subject` |
| Installable resources present | `_check_installable_resources` |
| Execution profiles resolve | `_check_profiles` |
| Event store constructs | `_check_event_store` |
| Memory store constructs | `_check_memory_store` |

It runs **no tests**, **no linters**, and — by explicit design, stated in its own header comment —
**no Git commands** ("clean subject and baseline/tag identity require an external Git-capable
process"). That design choice is defensible and honest. But it means the release predicate quoted in
`sprint_active.md` (`./ci/release_qualify.sh == 0`) is *necessary and far from sufficient*, and no
current document says so. Task `H1-12` closes this by adding the suite and linters as explicit,
separate release stages rather than by expanding the qualifier's remit.

### 3.5 Claims this audit could not verify

Stated plainly, so they are not mistaken for confirmations:

| Claim | Why unverified |
|---|---|
| Organisational independence of the M-4 producer/reviewer keys | `sprint_active.md` self-discloses that both keys were held by one operator. This is an honest disclosure and is unverifiable from inside the repository — it is a fact about people, not bytes. |
| Live-provider behaviour of `OpenRouterModel` | Requires network and paid credits. `test/runtime/test_composition_root.py::LiveDogfood` skips without a key. Deliberately not exercised. |
| Rootless bubblewrap containment attestation | `bwrap` availability was not probed under this audit's WSL2 environment; the `host-dev` escape hatch was used for the workflow execution tests, which the code correctly bars from `release=True`. |
| Real SWE-Bench performance | Out of scope per the brief; explicitly not a beta blocker. |

I flag the first of these as the one genuine *organisational* gap. It is real, but it is not
technical, and per the brief it must not gate the beta.

---

## 4. Backend architecture and production-path map

### 4.1 The layer lattice, as enforced

The hexagonal ordering is not merely documented — `tools/linters/check_boundaries.py` enforces the
import direction across 414 files and passes. The real dependency direction is:

```
domain  ──►  (nothing; pure values, JCS canonicalisation, wire types, reducer)
ports   ──►  domain
kernel  ──►  domain, ports                     [the TCB: 1,373 logical LOC, domain-blind]
agency  ──►  domain, ports, kernel             [episode engine, manifests, context]
runtime ──►  domain, ports, kernel, agency     [composition, session, ledger, service]
adapters──►  domain, ports                     [models, environments, stores, sandbox]
```

`runtime` wires `adapters` in at composition time through `wiring.py`, which is why `adapters` does
not appear upstream of `runtime` in the import graph. That inversion is the load-bearing design
decision of the whole system and it is correctly implemented.

### 4.2 The production execution path, traced through actual code

Traced by reading `cli.py` → `root.py` → `session.py` → `kernel/dispatch.py` → `wiring.py` →
`ledger_emitter.py`, and confirmed by executing it:

```
  vanguard run  (runtime/cli.py:207 cmd_run)
        │  resolves workspace, operator Ed25519 signer, manifest path, scoped .env
        ▼
  Runtime.execute_profiled          (runtime/root.py:175)          ← ADR-0089 target entrypoint
        │
        ├─► Runtime.compose         (runtime/compose.py:226)
        │      manifest.json → Harness (frozen composition + composition_digest)
        │      components → tool schemas, aliases, policies, skill cards, budget
        │
        ├─► RuntimeBootstrap.build  (runtime/bootstrap.py:60)      ← selects adapters from profile_id
        │      profile → environment adapter (Git | Sandboxed/bwrap)
        │      profile → event store (SQLite-WAL at <repo>/.vanguard/events.sqlite3)
        │      profile → clock
        │
        ▼
  Runtime.run_composed              (runtime/root.py:247)
        │
        ▼
  HarnessSession(...)               (runtime/session.py:614)       ← 1,401 LOC; the turn loop host
        │      _environment_map(ports.environment, harness)  ← wiring.py:497, calls environment.profile()
        │
        │  ── per turn ──────────────────────────────────────────────────────
        │   ContextCompiler.compile          (agency/context/compiler.py:80)
        │   ModelPort.propose                (adapters/models/openrouter.py:533)
        │   AliasTranslator: tool name → canonical verb   ("Read" → "fs.read")
        │   Kernel dispatch S0..S12          (kernel/dispatch.py)  ← authorization
        │        classifier → policy → grants → attenuation → budget → provenance
        │   BindingResolver.resolve(verb)    (runtime/wiring.py:304)
        │   EffectBinding factory → EnvironmentPort.observe / .apply / .reconcile
        │   LedgerEmitter.emit_kind          (runtime/ledger_emitter.py:236)
        │        └─► _write → store.append([envelope])   ← ledger_emitter.py:394  ONE EVENT AT A TIME
        │  ─────────────────────────────────────────────────────────────────
        ▼
  RunResult (terminal, receipts, telemetry, verdict, replay_gaps)
        │
        ├─► projections / recovery  (runtime/ledger/recovery.py, runtime/checkpoints.py)
        └─► artifacts / CAS         (runtime/artifacts.py)
```

The path is coherent and single-threaded through the kernel. There is exactly one authorization
authority and exactly one ledger writer, which is what the architecture claims.

### 4.3 Three entrypoints, one of which is legacy

`runtime/root.py` exposes three class methods on `Runtime`:

| Entrypoint | Line | Adapter selection | Status |
|---|---:|---|---|
| `execute_harness` | `root.py:70` | **Runtime chooses adapters itself** (`sandbox_mode` string, `_bwrap_path()`, `OpenRouterModel()` default) | **Legacy.** Its own docstring says so: *"`execute_harness` remains the legacy entrypoint until every caller has migrated and W3D-12 sunsets it."* |
| `execute_profiled` | `root.py:175` | **`RuntimeBootstrap.build()` chooses, from `profile_id` alone** | **Target** (ADR-0089). Used by the CLI. |
| `run_composed` | `root.py:247` | Caller supplies fully-built `SessionPorts` | **Primitive.** Both of the above delegate to it. |

This is not accidental duplication — it is a *documented, in-progress migration* with a named
sunset ticket. That distinction matters for the plan: `execute_harness` should be finished off, not
"discovered and removed".

Caller census (`grep` across `vanguard`, `test`, `tools`):

| Consumer | References |
|---|---:|
| `vanguard/packages/runtime/root.py` (internal) | 13 |
| `test/falsifiers/*` | ~25 across 8 files |
| `test/runtime/*` | ~10 |
| `vanguard/packages/runtime/{bootstrap,child_runtime,lab_driver,cli,session,compose,entrypoint,service,authority_audit}.py` | 6, 5, 3, 2, 1, 1, 1, 1, 1 |
| `tools/runners/*` | 4 |

**Finding A-01 — `PARTIAL` (migration incomplete).** The CLI already uses `execute_profiled`. The
remaining `execute_harness` consumers are overwhelmingly *tests*, which is the easy case — tests can
be migrated without behavioural risk because they construct their own fakes. `child_runtime.py`
(5 references) is the one production consumer that matters, because it is the recursion path.

**Non-goal for Horizon 1:** do not delete `execute_harness`. It is load-bearing for ~35 tests
including the M-4/M-6/M-7 falsifiers. Migration is Horizon 2 work (`H2-01`).

### 4.4 Bootstrap paths — five, not one

Distinct places that construct a runtime or its adapters:

| # | Location | Purpose | Verdict |
|---|---|---|---|
| 1 | `runtime/root.py:70` `execute_harness` | legacy full path | consolidate (H2) |
| 2 | `runtime/root.py:175` `execute_profiled` | **canonical** | retain |
| 3 | `runtime/bootstrap.py:60` `RuntimeBootstrap.build` | adapter selection from profile | retain (this is the seam) |
| 4 | `runtime/entrypoint.py:50` `execute` | JSON-request coding preview entrypoint | **remove or fold** |
| 5 | `runtime/lab_driver.py:206` | benchmark/lab harness | retain, but must not use `:memory:` silently |
| 6 | `runtime/service/service.py:140` | daemon | retain, but must not use `:memory:` silently |

**Finding A-02 — `OBSOLETE`.** `runtime/entrypoint.py` (153 LOC) is a sixth composition path that
hardcodes domain knowledge. `docs/01_law/EXTENSIBILITY.md:56` already flags it in the repository's
own words:

> `runtime/entrypoint.py` | hardcodes `vg-code-default` / `vg-code-explain` manifest selection and
> raises `unsupported coding command`; defaults `project_id` to `coding-preview` | resolve the
> manifest through pack discovery; the entrypoint must be domain-neutral

It also builds its own models (`OllamaModel` at `:78`, `OpenRouterModel` at `:84`), its own manifest
path (`:28`), and its own in-memory store (`:89`). It is a complete parallel mini-runtime. It has one
internal reference and no test coverage of its `execute()` path. **Recommend deletion in Horizon 2**
(`H2-03`), after confirming no client depends on it.

### 4.5 The silent in-memory fallback — five sites

The brief asks specifically about "no silent in-memory fallback". Verified by grep:

| Site | Code | Guarded? |
|---|---|---|
| `runtime/root.py:103` | `selected_store = store or SqliteEventStore(":memory:")` | Only when `release=True` |
| `runtime/bootstrap.py:88` | `selected_store = SqliteEventStore(":memory:")` | Reached only when `persistence_mode != "sqlite-wal"` |
| `runtime/service/service.py:140` | `self.event_store = SqliteEventStore(":memory:")` | **No** |
| `runtime/entrypoint.py:89` | `preview_store = SqliteEventStore(":memory:") if fake_backend else None` | Gated on `fake_backend` — acceptable |
| `runtime/lab_driver.py:206` | `store = SqliteEventStore(":memory:")` | **No** (lab context — arguably fine) |

**Finding A-03 — `PARTIAL`.** The *product* path is actually safe: all four shipped profiles
(`product`, `local`, `sandboxed`, `hermetic`) declare `persistence_mode: "sqlite-wal"` and
`persistence_durable: True`, so `bootstrap.py:88`'s `:memory:` branch is **unreachable for every
shipped profile**. It exists only for a hypothetical future profile.

The genuine exposures are `root.py:103` (legacy entrypoint, silently non-durable unless the caller
remembers to pass a store) and `service.py:140` (the daemon). A user who runs the daemon and expects
durable history does not get it, and nothing tells them.

**Recommendation (`H1-05`):** make `root.py:103` and `service.py:140` fail closed or emit an
explicit `EphemeralLedgerSelected` warning event. Delete `bootstrap.py:88`'s dead branch in
Horizon 2 rather than in the beta — it is unreachable, so it is not a beta risk.

### 4.6 Duplicate model construction — six sites, no factory

```
runtime/entrypoint.py:78       OllamaModel(...)
runtime/entrypoint.py:84       OpenRouterModel(model=planner_model)
runtime/cli.py:267             OpenRouterModel(model=..., stream=False, environ=...)
runtime/model_selection.py     OpenRouterModel(...) ×5, OllamaModel(...) ×1
runtime/bootstrap.py:129       OpenRouterModel()
runtime/root.py:148            OpenRouterModel()
```

**Finding A-04 — `PARTIAL`.** There is no single model factory. `adapters/models/config.py` provides
a `ModelRegistry` with a deliberate fail-closed design (its docstring: *"raises `ModelRegistryError`
instead of silently substituting hardcoded names"*), and `model_selection.py` (262 LOC) is the
closest thing to a selection policy — but `cli.py`, `root.py`, `bootstrap.py` and `entrypoint.py`
each bypass it and construct adapters directly.

Cost of this today: the CLI cannot run offline (§6.5) *because* `cli.py:267` constructs
`OpenRouterModel` unconditionally rather than asking a factory for "whatever this profile says". A
single `ModelFactory.for_profile(profile, overrides)` seam would fix the offline gap and the
duplication together. That is why `H1-06` (offline path) and `H2-04` (unify factories) are the same
underlying change, split across horizons by risk.

### 4.7 Duplicate manifest/pack resolution

| Site | What it does |
|---|---|
| `agency/manifests/loader.py:235,253,265,273` | The real loader. Normalises directory-or-`manifest.json`, validates, lists available packs. |
| `runtime/compose.py:344` `_manifest_file` | **Second, independent** directory-or-file normalisation. |
| `runtime/cli.py:106` | Third path construction for the default manifest. |
| `runtime/entrypoint.py:28` `_manifest` | Fourth, hardcoded to two manifest names. |

**Finding A-05 — `PARTIAL`.** Four resolution paths, two of which (`loader.py` and `compose.py`)
independently reimplement the same "is this a directory or a `manifest.json`?" normalisation. This is
genuine, removable duplication with no invariant defended by having two copies. Horizon 2 (`H2-05`).

### 4.8 Two pack formats, two locations

| Location | Count | Format | Consumed by |
|---|---:|---|---|
| `vanguard/packages/agency/manifests/` | 8 | `manifest.json` + `aliases.json` + `*-tool.json` (`mhf.manifest/2`) | **Production** (`Runtime.compose`) |
| `packs/` | 4 | `harness.yaml` + `plugin.yaml` + `load.py` + `manifest.json` | **Linters and falsifier tests only** |

Grep confirms `packs/` is referenced from production code **nowhere**. Its consumers are:
`tools/linters/check_kernel_neutrality.py:36`, `check_tcb_budget.py:145`,
`check_isolation_policy.py:60`, and the M-5b/graph-colouring falsifiers
(`test/falsifiers/test_m5b_material_run.py:55`, `test_graph_coloring_material_run.py:37`) plus
`test/runtime/test_anticheat.py:228`.

**Finding A-06 — `PARTIAL` / packaging defect.** `packs/` is legitimate test-and-evidence
infrastructure. The defect is that `pyproject.toml` ships it in the wheel
(`include = ["vanguard*", "schemas*", "packs*"]`), so every beta user installs four evidence packs
they cannot use. Worse, they install as **top-level `packs/` and `schemas/` directories inside
`site-packages`** — verified by installing the wheel:

```
$ python3 -m pip install --target site dist/vanguard_runtime-0.7.3.dev0-py3-none-any.whl
$ ls site
...  packs/  schemas/  vanguard/  cryptography/  jsonschema/  ...
```

Two generically-named top-level directories in `site-packages` is namespace pollution that can
collide with any other distribution. This is a real, if unglamorous, packaging bug. `H1-07`.

### 4.9 Event representations — convergent, contrary to expectation

The brief asks about "duplicate event representations". I tested this directly:

```python
from vanguard.packages.domain.ledger.events import READABLE_KINDS
from vanguard.packages.domain.wire.types_gen import EventKind
len(READABLE_KINDS)                    # 63
len({e.value for e in EventKind})      # 63
set(READABLE_KINDS) - {e.value for e in EventKind}   # set()
{e.value for e in EventKind} - set(READABLE_KINDS)   # set()
```

And the emitter's privilege map is a strict subset:

```python
set(ledger_emitter.PRIVILEGED_KIND_OWNERS) - {e.value for e in EventKind}   # set()  (26 kinds)
```

**Finding A-07 — `FALSIFIED` (the concern does not hold).** There is exactly one event vocabulary.
`domain/wire/types_gen.py` is **generated** from the schemas (hence its 706 LOC — it is not
hand-maintained bloat), `READABLE_KINDS` agrees with it perfectly in both directions, and the
runtime's 26-entry privilege table is a proper subset naming no unknown kind.

This is a strong positive result and it removes a whole workstream. **"Converge event contracts" is
not needed — they are already convergent, and codegen keeps them that way.** Horizon 2 should not
spend effort here.

### 4.10 The SPI surface

`vanguard/packages/ports/spi.py` (125 LOC) declares five `runtime_checkable` Protocols:

| Protocol | Methods | Real implementor |
|---|---|---|
| `IPlanner` | `plan`, `observe`, `reflect` | `adapters/models/planner.py` |
| `IContextManager` | `compile`, `ingest`, `compact`, `reground` | `agency/context/compiler.py` (structurally) |
| `IToolkit` | `verbs`, `execute`, `compensate`, `health` | `adapters/sandbox/toolkit.py` |
| `IMemoryEngine` | `write`, `recall`, `consolidate`, `invalidate`, `capabilities` | `adapters/stores/memory_engine.py` |
| `IEvaluationGate` | `request`, `gate`, `preregister` | `adapters/evaluators/*` |

They are also used *declaratively*: `domain/artifacts/manifest.py:24` defines
`_SPI_KINDS = {"IPlanner","IMemoryEngine","IToolkit","IContextManager","IEvaluationGate"}` and
`:189` maps component roles onto them (`"context" → "IContextManager"`, `"toolkit" → "IToolkit"`),
so plugin manifests declare which SPI they provide and the registry verifies it
(`test/falsifiers/test_rf38_rf45_plugin_lifecycle.py`).

**Finding A-08 — `IMPLEMENTED`.** This is a working extension system, not metadata-only ceremony.
It answers the brief's question 4 (*can current contracts accept future implementations?*)
affirmatively for tools, memory, planners and evaluators.

The one soft spot: `ContextCompiler` is a concrete class that `HarnessSession` instantiates directly
rather than resolving through `IContextManager`. So a *replacement* context strategy is declarable
in a manifest but not actually injectable at runtime without editing `session.py`. Per the brief's
instruction not to add speculative seams, I do **not** recommend building that injection point until
a concrete second context strategy exists. Recorded as a known limitation, not a task.

---

## 5. Milestone M-1 → M-9 truth matrix

The brief asks for a matrix separating five things that this repository's own documents routinely
conflate. I use those five columns literally.

**Legend.** *Code* = implementation exists on a production path. *Tests* = automated suite covers it
and passes. *Evidence* = a signed bundle verifies `passed` under `verify_evidence.py`.
*Product-visible* = a user of the beta can actually observe the capability. *Blocker* = what is
genuinely in the way.

| Milestone | Code implemented | Tests passing | Evidence valid | Product-visible capability | Actual blocker | Required action |
|---|---|---|---|---|---|---|
| **M-1 – M-3** Trust spine, budgets, attenuation, single-writer ledger | ✅ `kernel/dispatch.py` S0–S12, `budget.py` 4-D additive, `attenuation.py` monotonic | ✅ 94 kernel + 369 contract tests | n/a (baseline, pre-dates bundle protocol) | ✅ Every run is authorized and budgeted | **None** | None. Hold the 1,438 LOC ceiling. |
| **M-4** Useful coding proof, file WAL, attributable run | ✅ `Runtime.execute_profiled`, `mhf.trajectory/2`, cold reconstruction | ✅ incl. `test_rf95_product_execution_profile.py` | ✅ **`M-4-rf95-candidate-07` verifies `passed`** | ✅ `vanguard run` performs real repairs | **None technical.** Producer/reviewer keys held by one operator — *organisational*, self-disclosed | Optional: a distinct reviewer re-signs the same digest. **No rerun needed.** Not a beta blocker. |
| **M-5a** Event-derived AgentView + accepted control | ✅ AgentView, authority provenance, checkpoint verification, unknown-event preservation, cold reconstruction | ✅ `test_resume_from_ledger.py` (10 tests) + reducer suite | ❌ **No bundle.** `CONVERGENCE-BASE-v1` absent | ✅ Recovery works; replay works | **Missing release identity** — an annotated, remotely-resolvable Git tag. Release-owner action, external to code | Create and push the tag; run the fail-closed baseline builder. **Category 4 (release integrity), not category 1.** |
| **M-5b** Non-contaminated generality falsifier | ✅ `packs/formal-graph-coloring`, `adapters/evaluators/suites/formal_graph_coloring.py` (286 LOC) | ✅ `test_graph_coloring_material_run.py`, `test_graph_coloring_oracle.py` | ❌ **`M-5b-graph-coloring` verifies `failed`** | ⚠️ Not user-facing | **Invalid evidence** *and* **blocked on M-5a**. The bundle claims `passed` over an `undeterminable` subject; materials record no digest scheme; pinned tree was dirty at capture | Re-emit against the successor baseline once `CONVERGENCE-BASE-v1` exists. The builder now emits `raw-sha256`, so the mechanical defect is already fixed. Preserve the failed bundle. |
| **M-6** Mediated recursive delegation, depth ≥ 3 | ✅ `runtime/delegation.py` (771), `child_runtime.py`, `ports/child_runtime.py` | ✅ `test_rf101_rf112_canonical_recursion.py` (11 refs) | ✅ **`M-6-…-order10` verifies `passed`** — 57 falsifiers, fresh process, depth 3, kill-tree | ⚠️ Works, but no CLI surface exposes subagents | **None** | None. (Master report's "pending deliverables" for M-6 are already delivered — see C-14.) |
| **M-6.5** Adaptive controller paired study | ✅ `runtime/paired_evaluation.py` (323), `meta_controller` port | ✅ `test_m65_integrated_study.py` | ✅ **`M-6.5-…-order13` verifies `passed`** — 32 paired trials, portable refs, `raw-sha256` | ❌ Research artifact, not a product feature | **None** | None. Master report's `BLOCKED` is stale (C-10). |
| **M-7** Multi-role topologies | ✅ `runtime/topology.py` (441), `runtime/scheduler.py` | ✅ `test_m7_topology_execution.py`, `test_m701_recorded_workload.py` | ✅ **`M-7-…-order12` verifies `passed`** — 40 tests, 25 markers, all three topologies as real M-6 children with CAS artifact flow | ⚠️ No CLI/API surface | **None technical.** ADR-0099 read-concurrency disposition is a recorded decision, and §11.6 supplies the missing measurement | None for the beta. Attach §11.6's contention data to ADR-0099. |
| **M-8** Durable memory + governed learning | ✅ `runtime/governance/learning.py` (664), `approvals.py` (618), `adapters/stores/memory_engine.py` (639) | ✅ suite green | ✅ **`M-8-…-order12` verifies `passed`** — 59 tests, 34 markers, authorization-before-ranking, CAS composition registry, verified rollback in fresh process | ❌ No CLI surface | **None** | None. Master report's `PACKAGE_READY` understates it (C-12). |
| **M-9** Operational beta `0.9.0b1` | ⚠️ **PARTIAL** — packaging works, CLI incomplete | ⚠️ suite has 1 documentary failure | ❌ No bundle | ⚠️ Installable and runnable; not inspectable or resumable | **Product-surface gaps** (§6) + the one red test | **This is the whole of Horizon 1** (§12). |

### 5.1 Answering the brief's specific M-5a / M-5b question

The brief asks whether the M-5a/M-5b gaps are missing implementation, missing release identity, a
failed experiment, stale documentation, invalid evidence, or an external governance requirement.

| Milestone | Category | Justification |
|---|---|---|
| **M-5a** | **Missing release identity** (and only that) | Every code predicate — AgentView, provenance, checkpoint verification, unknown-event preservation, cold reconstruction — is implemented and tested. The absent artifact is an annotated Git tag. `prepare_convergence_baseline.py` runs and produces a candidate that correctly refuses to call itself a baseline (`CANDIDATE_NOT_A_BASELINE`, 55 schema pins, 4 reducer pins, 3 protected subtrees, `commit_sha`/`tag_object_sha`/`tree_digest` unresolved). That refusal is the system working, not failing. |
| **M-5b** | **Invalid evidence**, *cascading from* M-5a's missing release identity | Two independent defects: (a) the bundle records an acceptance claiming `passed` over a subject whose own outcome is `undeterminable`, which the verifier correctly rejects; (b) its materials record no digest scheme, so integrity cannot be re-derived. Both are fixed in the current tooling. The *implementation* (deterministic graph-colouring pack + exterior verifier, zero kernel leakage confirmed by RF-98) is sound. |

Neither is a failed experiment, and neither is missing implementation. Both are downstream of one
external Git operation.

### 5.2 Can M-6 → M-8 legitimately remain accepted while M-5a/M-5b are incomplete?

This is the sharpest governance question in the brief, and it deserves a direct answer rather than a
deferral.

**Technically: yes, unambiguously.** Each of M-6, M-6.5, M-7 and M-8 has a bundle that verifies
`passed` on its own terms, over a clean pinned subject, signed by a registered producer and accepted
by a registered reviewer, re-verified in a fresh process. Those are *self-contained* claims about
recursion, controller lift, topology execution and durable memory. None of them depends on the
content of `CONVERGENCE-BASE-v1`. The recursion either reached depth 3 with conserved budgets or it
did not, and the verifier says it did.

**As formal milestone lineage: no.** `sprint_active.md`'s own dependency graph orders
`M5A → M5B` and `M4 → M6 → {M6.5, M7} → M8`, and its stated rule is that acceptance derives from
digest-addressed evidence in dependency order. Under a strict reading, an unbroken accepted lineage
does not exist because M-5a has no bundle at all.

**Resolution.** These are two different predicates and the repository currently has one word for
both. The plan's recommendation (`H1-11`) is to make the distinction explicit in `milestones.md`:

- **`TECHNICALLY_VERIFIED`** — this milestone's own bundle verifies `passed`. Depends on nothing
  upstream. M-4, M-6, M-6.5, M-7, M-8 all hold this today.
- **`LINEAGE_ACCEPTED`** — `TECHNICALLY_VERIFIED` **and** every dependency is `LINEAGE_ACCEPTED`.
  Currently held by M-1…M-4 only, and blocked for everything downstream of M-5a by one Git tag.

Per the brief's explicit instruction, **`0.9.0b1` is qualified on `TECHNICALLY_VERIFIED` plus the
product proof of §6.** `LINEAGE_ACCEPTED` is the gate for a formal scientific claim or a signed
release attestation (M-10), and it is listed among the optional steps in §12.6. This preserves the
rigour of the lineage concept without allowing a missing tag to block a locally functional beta.

### 5.3 What the milestone record does *not* prove

Worth stating plainly, because it is the brief's §5 correction and it is correct:

Five milestones verify `passed`, and a user who installs `0.9.0b1` today still cannot resume a run,
list events, inspect an artifact, or execute anything at all without an OpenRouter API key. The
milestone evidence is real and it measures real properties — but it measures *substrate* properties,
not *product* properties. §6 measures the product ones, and they are the ones that are behind.

---

## 6. Beta product gap analysis

Each item from the brief's checklist, classified `COMPLETE` / `PARTIAL` / `MISSING`, with the
evidence that produced the classification.

| # | Requirement | Status | Evidence |
|---|---|---|---|
| 1 | One authoritative version source | **PARTIAL** | §6.1 — three sources, one hardcoded |
| 2 | Reproducible package build | **COMPLETE** | §6.2 — wheel builds clean |
| 3 | Clean installation outside the checkout | **COMPLETE** | §6.3 — verified by installing and running |
| 4 | Explicit durable state directory | **COMPLETE** | `<repo>/.vanguard/` — `bootstrap.py:85` |
| 5 | No hidden `PYTHONPATH` dependency | **COMPLETE** | §6.3 |
| 6 | No silent in-memory fallback | **PARTIAL** | §4.5 — two live exposures |
| 7 | Packaged schemas, migrations, manifests | **PARTIAL** | §6.2 — they ship, but pollute `site-packages` |
| 8 | Unified runtime composition | **PARTIAL** | §4.3 — 3 entrypoints, migration in progress |
| 9 | Commands/API for run, resume, status, events, artifacts | **MISSING** (4 of 5) | §6.4 |
| 10 | Health vs readiness | **PARTIAL** | §6.6 |
| 11 | Redacted typed diagnostics | **PARTIAL** | §6.7 |
| 12 | Plugin discovery and activation lifecycle | **COMPLETE** | §6.8 — fully implemented (and expensive) |
| 13 | Kill-and-resume verification | **PARTIAL** | §6.9 |
| 14 | Offline-after-install verification | **MISSING** | §6.5 |
| 15 | Coding **and** non-coding reference workflows | **PARTIAL** | §6.10 — the decisive finding |

**Scorecard: 5 complete, 8 partial, 2 missing.** Nothing here requires new architecture.

### 6.1 Version identity — three sources

```
pyproject.toml:7                       version = "0.7.3.dev0"
vanguard/__init__.py:12                __version__ = "0.7.3.dev0"        # importlib fallback
vanguard/packages/runtime/service/service.py:379   "serverVersion": "0.7.3.dev0"   # HARDCODED
docs/03_execution/milestones.md:9      version: "0.7.3.dev0"
```

`vanguard/__init__.py` does the right thing (`importlib.metadata.version("vanguard-runtime")` with a
literal fallback). The defect is `service.py:379`, which embeds the version as a **string literal in
a response payload**. A daemon built from a `0.9.0b1` wheel will report `0.7.3.dev0` to every
client.

Also note: **the declared version is `0.7.3.dev0`, not `0.9.0b1`.** The beta version does not exist
anywhere in the tree yet. `H1-04` sets it once, in `pyproject.toml`, and makes `service.py` read
`vanguard.__version__`.

### 6.2 Package build — works

```
$ python3 -m pip wheel --no-deps -w wheelout .
Successfully built vanguard-runtime
Created wheel: vanguard_runtime-0.7.3.dev0-py3-none-any.whl  size=1,648,127
```

The wheel includes non-Python assets via a deliberately broad `package-data` glob whose comment
explains itself well:

> `.jcs` and `.digest` are the other two thirds of the REQ-SCHEMA-001 canonicalisation triples.
> Without them a wheel ships the inputs and none of the canonical forms or digests to check them
> against.

That reasoning is correct and the packaging honours it. The defect is scope, not intent
(§4.8): `schemas/` and `packs/` install as top-level `site-packages` directories.

### 6.3 Clean installation outside the checkout — works

First, confirming the negative — the source tree genuinely is not importable from elsewhere:

```
$ cd /tmp/scratch && python3 -m vanguard.packages.runtime.cli doctor
ModuleNotFoundError: No module named 'vanguard'
```

Then, installing the wheel to a clean target and running against an unrelated workspace:

```
$ python3 -m pip install --target site wheelout/*.whl
$ cd proj && env -u OPENROUTER_API_KEY PYTHONPATH=../site ../site/bin/vanguard doctor
version            OK             0.7.3.dev0
python             OK             3.12.3
workspace          OK             /tmp/.../proj
state              UNINITIALISED  /tmp/.../proj/.vanguard (run `vanguard init`)
operator key       OK             /home/rocha/.vanguard/keys/operator.ed25519 9b26195e…
default manifest   OK             /tmp/.../site/vanguard/packages/agency/manifests/vg-code-default/manifest.json
model credentials  ABSENT         no provider key; live execution unavailable
approval           NON-INTERACTIVE no TTY; approvals deny without an explicit scoped grant
```

**Finding P-01 — `COMPLETE`, and better than expected.** The installed CLI resolves the **packaged**
manifest (note the `site/vanguard/...` path, not the checkout), correctly detects an uninitialised
foreign workspace, and correctly reports missing credentials. `PYTHONPATH` appears here only because
`pip install --target` is not a real virtualenv; it is an artifact of my test method, not a
dependency of the product. Requirements 3 and 5 are genuinely met.

This deserves emphasis because it is the item most likely to have been broken, and it is not.

`doctor` is also a genuinely good diagnostic: seven checks, honest states (`UNINITIALISED`,
`ABSENT`, `NON-INTERACTIVE`), no false greens. It is the strongest part of the current product
surface.

### 6.4 CLI surface — the largest product gap

```
$ vanguard --help
usage: vanguard [-h] [--version] {init,doctor,run} ...
```

| Command | Status | Underlying machinery |
|---|---|---|
| `init` | ✅ `cli.py:140` | — |
| `doctor` | ✅ `cli.py:161` | — |
| `run` | ✅ `cli.py:207` | `Runtime.execute_profiled` |
| **`resume`** | ❌ **MISSING** | **Exists**: `service.py:695 _cmd_Resume`, `studio_gateway.py:364 _handle_resume`, `governance/engine.py:91 resume`, `ledger/recovery.py RecoveryScanner.scan_and_recover_run` |
| **`status`** | ❌ **MISSING** | **Exists**: `runtime/ledger/projections.py` (339 LOC), ADR-0103 progress projection |
| **`events`** | ❌ **MISSING** | **Exists**: `SqliteEventStore.read(EventRange)`, `runtime/trajectory_reader.py` (266 LOC) |
| **`artifacts`** | ❌ **MISSING** | **Exists**: `runtime/artifacts.py` (689 LOC), CAS with digest addressing |

**Finding P-02 — `MISSING` (surface only).** This is the single most consequential gap, and it is
also the cheapest to close. *All four missing commands are thin read-only projections over machinery
that already exists, is tested, and is reachable.* There is no new capability to build — only
argument parsing and output formatting.

The brief's vertical slice is `install → configure → run → inspect → interrupt → resume → verify`.
Today a user can do `install → configure → run`. `inspect` and `resume` are unreachable from the
product surface despite being fully implemented underneath. `H1-08` and `H1-09`.

### 6.5 Offline-after-install — missing, and it blocks the beta's own self-test

`cli.py:207 cmd_run` constructs the model unconditionally:

```python
result = Runtime.execute_profiled(
    manifest_path, task_ctx, profile_id=args.profile,
    model=OpenRouterModel(model=args.model, stream=False,
                          environ={"OPENROUTER_API_KEY": api_key}),
    ...)
```

and hard-exits before that if no key is present:

```python
if not api_key:
    print("unavailable: no OPENROUTER_API_KEY in environment or allowlisted .env; "
          "live execution requires a provider key", file=sys.stderr)
    return EXIT_UNAVAILABLE
```

**Finding P-03 — `MISSING`.** There is no offline path at the product surface. This matters more
than it first appears:

1. A beta evaluator with no OpenRouter account cannot run *anything*. `doctor` is the entire
   experience.
2. The repository *has* the pieces — `adapters/models/fake.py::FakeModel` is a deterministic scripted
   `ModelPort` in the **production** adapter package, with no ambient I/O, clock or network. It is
   what every falsifier uses.
3. Without it there is no self-test, so requirement 14 cannot be satisfied by construction.

The fix is small: a `--model-adapter {openrouter,ollama,fake}` flag (or a `fake` profile) routed
through the model factory of `H1-06`, plus a bundled cassette. This simultaneously closes §4.6's
duplication for the CLI path.

### 6.6 Health vs readiness

Only one endpoint exists, in the Studio gateway:

```
studio_gateway.py:156   if path not in ("/api/health", "/api/v1/health") and not self._authenticate():
studio_gateway.py:159   if path in ("/api/health", "/api/v1/health"):
```

**Finding P-04 — `PARTIAL`.** There is a liveness endpoint (correctly exempted from auth) and no
readiness endpoint. Readiness for this system is a meaningful and *already-computed* notion — it is
essentially what `doctor` reports (store reachable and durable, manifest resolvable, sandbox
qualifiable, credentials present). `H1-10` exposes `doctor`'s existing check results as
`/api/v1/ready`. Low effort, no new logic.

### 6.7 Redacted typed diagnostics

Positive: the CLI has a typed exit-code vocabulary (`EXIT_USAGE`, `EXIT_UNAVAILABLE`, `EXIT_DENIED`,
`EXIT_TASK_FAILED`, `EXIT_OK`) and distinguishes capability failure from task failure — the
`KeyMaterialUnavailable` handler comments *"An approval was required and no reviewer was reachable.
This is a capability failure, not a task failure."* That is exactly right and rare.

Redaction is a first-class concept: `SessionPorts.capture_policy` carries
"capture/redaction/sensitivity/retention", the events table has `confidentiality`,
`retention_class`, `trainability` and `redaction_status` columns (§11.3), and
`tools/linters/scan_secrets.py` exists.

Negative: `cmd_run`'s catch-all is untyped and unredacted —

```python
except Exception as exc:  # noqa: BLE001 - surfaced verbatim below
    print(f"error during execution: {exc}", file=sys.stderr)
```

**Finding P-05 — `PARTIAL`.** An adapter exception carrying a URL, a path, or a key fragment is
printed verbatim. `H1-13` routes it through the existing redaction policy.

### 6.8 Plugin discovery and activation lifecycle — complete, and the source of §11's cost

`runtime/registry/lifecycle.py` implements a fail-closed state machine per ADR-0081:

```
DISCOVERED → RESOLVED → VERIFIED → ACTIVATED → QUIESCING → RETIRED
     └──────────────── any ────────────────► FAULTED → RETIRED
```

with one ledger event per entered state, `manifest_digest` required at construction, and
`graph_digest` + `ceiling_digest` required at verification.

**Finding P-06 — `COMPLETE`.** Requirement 12 is fully met — arguably over-met. This is precisely
the mechanism generating 72 of 90 events per episode (§11.3). The capability is right; the *default
verbosity* is the problem, and §9 proposes making it a capture axis rather than deleting it.

### 6.9 Kill-and-resume verification

| Asset | Status |
|---|---|
| `runtime/ledger/recovery.py` (444 LOC): `RecoveryScanner.scan_and_recover_run`, `reconcile_open_intents`, `reconcile_open_children`, `settled_effect`, `continue_idempotent_effect` | ✅ Substantial and correct-looking |
| `runtime/checkpoints.py` (539 LOC): `CheckpointManager.capture/load/reconstruct`, `Reconstruction.state_digest` | ✅ |
| `test/runtime/test_resume_from_ledger.py` | ✅ **Real** — 200 LOC, 10 tests, passing |
| `test/runtime/test_coding_resume.py` | ❌ **Hollow** — see D-06 |
| CLI `resume` command | ❌ Missing (§6.4) |
| An actual **kill** (SIGKILL mid-run) then resume test | ❌ Not found |

**Finding P-07 — `PARTIAL`.** Ledger-level resume is implemented and genuinely tested. What is
missing is (a) the product command and (b) a true crash test — the existing tests resume from a
*ledger*, not from a *killed process*. Given that crash recovery is an advertised architectural
capability, a real SIGKILL-and-resume test is the honest way to claim it. `H1-09`.

### 6.10 The two reference workflows — the decisive product finding

I composed every manifest on disk:

```
COMPOSE OK   vg-code-claude-shaped      tools=8   digest=sha256:41cd6…
COMPOSE OK   vg-code-default            tools=13  digest=sha256:8451e…
COMPOSE OK   vg-code-explain            tools=5   digest=sha256:341bc…
COMPOSE OK   vg-code-lex                tools=8   digest=sha256:a8536…
COMPOSE OK   vg-code-opencode-shaped    tools=8   digest=sha256:5ce75…
COMPOSE OK   vg-code-swe-mini           tools=4   digest=sha256:fb394…
COMPOSE OK   vg-shell-only              tools=1   digest=sha256:76242…
COMPOSE OK   vg-table-default           tools=2   digest=sha256:9b479…
```

Eight compose. But composition is not execution, so I executed them.

#### Workflow 1 — `vg-code-default` (coding): ✅ WORKS

Verified by the M-4 evidence bundle (real diff, passing tests, file-backed WAL, complete
`mhf.trajectory/2`, matching cold reconstruction) and reproduced in §11's benchmark: terminal
`completed`, 2 receipts (`fs.read`, `patch.apply`), 90 events.

#### Workflow 2 — `vg-code-explain` (read-only explainer): ✅ **WORKS — proven in this audit**

Verbs: `fs.read`, `fs.search`. I ran it end-to-end through the canonical runtime with a scripted
`ModelPort`:

```
$ python3 -c "... Runtime.execute_harness(manifest_path=vg-code-explain/manifest.json,
                model=Explainer(), sandbox_mode='host-dev', interactive=False) ..."
TERMINAL: completed
DETAIL:   calc.py sums a list with an off-by-one
RECEIPTS: [('fs.read', None)]
```

**Finding P-08 — `IMPLEMENTED` but unregistered.** A materially different workflow — read-only,
different tool set, different system prompt, different composition digest — executes through the
**same** production runtime with **zero kernel changes**. This is exactly the product thesis, and it
already holds today.

What it lacks is only: an entry in `registry.json`, an end-to-end test, and a `REFERENCE.md` (the
other six manifests have one). That is hours of work, not days. `H1-14`.

#### Workflow 3 — `vg-table-default` (non-coding domain): ❌ **BLOCKED**

Verbs: `TableRead`, `TablePatch`, aliased to canonical `table.read` / `table.patch`.

First I confirmed the aliasing and binding layer is correct:

```python
aliases.json:  {"TableRead": "table.read", "TablePatch": "table.patch"}
default_resolver().resolve("table.read")   # EffectBinding(factory=<_DomainProviderBridge…>)
default_resolver().resolve("table.patch")  # EffectBinding(…, carries_diff=True)
default_resolver().resolve("table.diff")   # None   ← correctly not advertised
```

`wiring.default_providers()` lazily loads `TableBindingProvider`, which declares
`supported_verbs = ("table.read", "table.patch")` with an honest comment about deliberately not
advertising `table.diff` "until the environment has a frozen diff contract and implementation".
**The binding layer is correct and the historical D-27 "orphan pack" drift is fixed there.**

Then I attempted execution:

```python
env = TableWorldEnvironment({"accounts": [{"id":"1","balance":100.0}, …]})
ports = SessionPorts(model=FakeModel(tape), environment=env, clock=SystemClock(),
                     store=SqliteEventStore(":memory:"), interactive=False)
Runtime.run_composed(harness, ports, task)
```

```
Traceback (most recent call last):
  File "runtime/root.py", line 350, in run_composed
    session = HarnessSession(
  File "runtime/session.py", line 614, in __init__
    base_env = _environment_map(ports.environment, harness)
  File "runtime/wiring.py", line 497, in _environment_map
    profile = environment.profile()
AttributeError: 'TableWorldEnvironment' object has no attribute 'profile'
```

**Finding P-09 — `PARTIAL`, and this is the gap between "coding runtime" and "universal substrate".**

`ports/environment.py` declares eight methods. `TableWorldEnvironment`
(`adapters/environment/tableworld.py:53`) implements **none** of them:

| `EnvironmentPort` (`ports/environment.py`) | `TableWorldEnvironment` |
|---|---|
| `profile()` :143 | ❌ |
| `snapshot()` :147 | ❌ |
| `observe(req, grant)` :151 | ❌ |
| `preview(req, grant)` :155 | ❌ |
| `apply(req, grant)` :159 | ❌ |
| `reconcile(receipt, grant)` :163 | ❌ |
| `compensate(receipt, grant)` :167 | ❌ |
| `dispose()` :171 | ❌ |
| — | ✅ `handle_read`, `handle_patch`, `get_table_state`, `evaluate_invariants` |

It is a **domain helper object, not an environment adapter** — precisely what
`docs/02_decisions/DRIFT_REGISTER_v045.md:85` recorded as drift D-27 ("Pack is an orphan. TableWorld
is not an `EnvironmentAdapter`"). That entry is **still accurate**, and its recommendation
(*"Register `vg-table-default` or delete the pack; do not leave orphans"*) is still outstanding.

The failure mode also matters: an unguarded `AttributeError`, not a typed
`CompositionError`/`UnsupportedEnvironment`. Any environment adapter that is even slightly incomplete
fails with a bare Python attribute error deep inside session construction. `H1-15` fixes the adapter;
`H1-16` makes `_environment_map` fail closed with a typed, actionable error.

#### Multi-agent / nested composition

`M-7-topology-order12` verifies `passed` with all three topologies (direct;
planner/executor/reviewer; fork/read/merge) running as real M-6 children with CAS artifact flow.
`runtime/topology.py` is a *pure lowering* module — `_reject_authority()` (`:172`) refuses any
topology field that carries authority, with the comment *"topology is routing data"*. That is the
correct separation and it means multi-agent execution genuinely requires no kernel changes.

**Finding P-10 — `IMPLEMENTED`.** Nested/multi-agent execution is proven. It has no product
surface, but the brief asks for proof of the capability, and the capability is proven.

#### Summary

| Workflow | Composes | Executes | Registered | Tested E2E | Verdict |
|---|---|---|---|---|---|
| `vg-code-default` (coding) | ✅ | ✅ | ✅ | ✅ | **Ready** |
| `vg-code-explain` (explainer) | ✅ | ✅ **(proven here)** | ❌ | ❌ | **Nearly ready — register + test** |
| `vg-table-default` (non-coding) | ✅ | ❌ | ❌ | ❌ | **Blocked on one adapter file** |
| Multi-role topologies | ✅ | ✅ | n/a | ✅ | **Ready** |

The brief requires "at least one useful coding workflow and one distinct non-coding workflow". The
strict reading (a genuinely non-coding *domain*) requires `H1-15`. The looser reading (a materially
different workflow) is satisfied *today* by `vg-code-explain`. I recommend doing both, because
`vg-code-explain` is nearly free and `vg-table-default` is what actually substantiates the
"universal substrate" claim in the VISION.

---

## 7. Bloat and duplication map

Per the brief: nothing is listed here merely because it looks complex. Each entry names its
consumers, the invariant it protects (if any), its measured runtime cost, and a replacement path.

### 7.1 Genuinely dead — remove with no replacement

| ID | Item | Size | Consumers | Invariant protected | Cost | Action |
|---|---|---:|---|---|---|---|
| D-01 | `vanguard/packages/apps/` | empty `__init__.py` | **none** | none | none | Delete |
| D-02 | `test/runtime/test_coding_coordinator.py` | shell | none | none | none | Delete |
| D-03 | `test/runtime/test_coding_entrypoint.py` | shell | none | none | none | Delete |
| D-04 | `test/runtime/test_coding_plan.py` | shell | none | none | none | Delete |
| D-05 | `test/runtime/test_coding_progress.py` | shell | none | none | none | Delete |
| D-06 | `test/runtime/test_coding_resume.py` | shell | none | none | **negative** — masks a real coverage gap (§6.9) | Delete |
| D-07 | `test/runtime/test_coding_verification.py` | shell | none | none | none | Delete |
| D-08 | `layer0/` scan target in `check_domain_blindness.py` | 1 line | linter | none | prints a WARN forever | Delete the target |

All six `test_coding_*` files share one body:

```python
"""Retired with apps/coding (M3). Semantics live in packs/code-default/."""
def load_tests(loader, tests, pattern):
    return unittest.TestSuite()
```

**Finding D-06 is the one that matters.** `test_coding_resume.py` is a file whose name asserts that
coding-workflow resume is tested. It tests nothing. It is worse than absent, because a reviewer
grepping for resume coverage finds it and stops looking. This is the concrete harm of leaving
tombstones in the tree.

### 7.2 Duplication with a replacement path

| ID | Item | Consumers | Invariant | Measured cost | Replacement |
|---|---|---|---|---|---|
| U-01 | 3 version sources (§6.1) | packaging, CLI, daemon | none | daemon lies about its version | Single source in `pyproject.toml`; `service.py` reads `vanguard.__version__` |
| U-02 | 6 model construction sites (§4.6) | CLI, bootstrap, root, entrypoint, model_selection | none | **blocks offline CLI** | One `ModelFactory` |
| U-03 | 4 manifest path resolvers (§4.7) | compose, loader, cli, entrypoint | none | none measured | `loader.py` becomes sole normaliser |
| U-04 | 5 `:memory:` fallbacks (§4.5) | root, bootstrap, service, entrypoint, lab_driver | **violates** durable-history expectation | silent data loss in daemon | Fail closed or emit explicit event |
| U-05 | 3 runtime entrypoints (§4.3) | ~35 tests + 6 modules | none | none measured | Finish the documented ADR-0089 migration |
| U-06 | `runtime/entrypoint.py` parallel mini-runtime (§4.4) | 1 internal ref | none | none measured | Delete |
| U-07 | Two pack formats/locations (§4.8) | production vs linters | none | ships 4 unusable packs + namespace pollution | Exclude `packs/` from the wheel |

**Explicitly not duplication** (checked and cleared):

- **Event contracts** — verified convergent, 63/63, codegen-maintained (§4.9). No work needed.
- **`domain/wire/types_gen.py`** (706 LOC) — generated. Not hand-maintained bloat.
- **`packs/formal-*`** — real M-5b evidence infrastructure. Keep in the repo; just don't ship them.

### 7.3 Oversized modules — extract, do not redesign

| ID | Module | LOC | Responsibilities mixed | Risk of extraction |
|---|---|---:|---|---|
| O-01 | `runtime/session.py` | 1,401 | `SessionPorts` DTO, `HarnessSession` construction, environment mapping, turn loop, approval flow, capture policy, terminal resolution | **Medium.** It is the hot path and the M-4/M-6/M-7 evidence runs through it. Extract only mechanically, with digests unchanged. |
| O-02 | `runtime/service/service.py` | 1,343 | daemon transport, command dispatch (`_cmd_Resume` et al.), store lifecycle, version reporting | **Low.** Command handlers split cleanly. |

`session.py` is the correct extraction target and the correct thing to be *careful* about. The
acceptance criterion for `H2-02` is therefore byte-identical composition and trajectory digests
before and after — a structural change that alters no digest is provably semantics-preserving here,
because digests are computed over canonicalised state.

### 7.4 Abstractions with zero or one consumer

Checked each SPI protocol's real usage (§4.10). All five have real implementors and are used
declaratively by the manifest system. **None qualifies as dead ceremony.** I specifically looked for
"metadata-only registries" and did not find one — `registry.json` is under-populated (§6.4), which is
the opposite failure.

The one genuine single-consumer abstraction is `IContextManager`, whose only implementor is reached
by direct instantiation rather than through the protocol. Per the brief's instruction not to add
speculative seams, this is recorded and **not** scheduled.

### 7.5 What must not be removed

Listed because a naive simplification pass would target them:

| Item | Why it stays |
|---|---|
| 24 linters in `tools/linters/` | They are the reason the invariants actually hold. Four of them pass today on 414 files and 1,373 kernel lines. Cheap, automated, load-bearing. |
| `verify_evidence.py`'s strictness | It fails 10 of 16 bundles including several claimed `passed`. A verifier that never disagrees is worthless. |
| Plugin lifecycle state machine | The *capability* is correct (§6.8). Only its default verbosity is wrong (§9). |
| 63-kind event roster | Convergent and codegen-maintained; the fan-out is inherent to the domain. |
| `packs/formal-*` | M-5b evidence substrate. |
| Typed CLI exit codes | Genuinely good design (§6.7). |

---

## 8. Retain / consolidate / optionalize / remove / defer matrix

| Component | Disposition | Horizon | Rationale |
|---|---|---|---|
| `kernel/` (S0–S12, budgets, attenuation, grants) | **RETAIN unchanged** | — | 1,373 LOC, domain-blind, verified. The crown jewel. |
| `domain/` (values, JCS, reducer, wire, selectors) | **RETAIN** | — | Pure, convergent, codegen-backed. |
| `ports/` + `spi.py` | **RETAIN** | — | Working extension system (§4.10). |
| Event roster (63 kinds) | **RETAIN** | — | Verified convergent. No work. |
| `Runtime.execute_profiled` + `RuntimeBootstrap` | **RETAIN — make canonical** | H1 | Already the CLI's path. |
| `Runtime.execute_harness` | **CONSOLIDATE** | H2 | Documented legacy; ~35 test consumers. Finish ADR-0089 migration. |
| `runtime/entrypoint.py` | **REMOVE** | H2 | Parallel mini-runtime; domain-leaking; 1 ref. |
| `vanguard/packages/apps/` | **REMOVE** | H1 | Empty. |
| 6 × `test_coding_*.py` | **REMOVE** | H1 | Hollow; D-06 actively misleads. |
| `layer0/` linter scan target | **REMOVE** | H1 | Dead path. |
| Version sources ×3 | **CONSOLIDATE** | H1 | Daemon misreports version. |
| Model construction ×6 | **CONSOLIDATE** | H1 (CLI) / H2 (rest) | Blocks offline run. |
| Manifest resolvers ×4 | **CONSOLIDATE** | H2 | No invariant defended. |
| `:memory:` fallbacks ×5 | **CONSOLIDATE / fail closed** | H1 (service, root) / H2 (rest) | Silent non-durability. |
| `packs/` in the wheel | **REMOVE from distribution** | H1 | Keep in repo; exclude from `package-data`. |
| `schemas/`,`packs/` as top-level site-packages dirs | **CONSOLIDATE** under `vanguard/` | H1 | Namespace pollution. |
| Plugin lifecycle verbosity | **OPTIONALIZE** (capture axis) | H1 | 80% of events; keep capability. |
| Single-event ledger append | **CONSOLIDATE** (group commit) | H1 | 150 ms/episode, measured. |
| `session.py` (1,401 LOC) | **CONSOLIDATE (extract)** | H2 | Digest-preserving extraction only. |
| `service/service.py` (1,343 LOC) | **CONSOLIDATE (extract)** | H2 | Handlers split cleanly. |
| CLI `resume`/`status`/`events`/`artifacts` | **ADD** | H1 | Thin projections over existing machinery. |
| Offline model path | **ADD** | H1 | Requirement 14 impossible without it. |
| `TableWorldEnvironment` → `EnvironmentPort` | **ADD** | H1 | Substantiates the substrate claim. |
| `vg-code-explain` registration + E2E test | **ADD** | H1 | Already works; nearly free. |
| `vg-table-default` registration | **ADD** | H1 | After H1-15. Ends drift D-27. |
| `readyz` endpoint | **ADD** | H1 | Reuse `doctor` checks. |
| `VANGUARD_BACKEND_M1_M9_MASTER_REPORT.md` | **ARCHIVE** | H1 | 10/15 claims falsified (§3.1). |
| `backlog.md` ↔ `sprint_active.md` drift | **REPAIR** | H1 | Currently failing the suite. |
| Shared-ledger concurrency | **DEFER** (document limit) | H2 | §11.6; fails closed. |
| Bidirectional PTY streaming | **REJECT for beta** | — | §13.4. |
| CoW fork, Tree-Sitter, SBFL, MCTS, CEGIS, mutation testing | **DEFER** | post-beta | §13.4. |
| `IContextManager` runtime injection | **DEFER** | — | No concrete second consumer. |

---

## 9. Capture, telemetry, recovery, evaluation and retention model

The brief's correction #1 is correct and this section derives the schema **from the existing
architecture**, as instructed, rather than transplanting the illustrative YAML.

### 9.1 What already exists — more than expected

| Axis | Existing mechanism | Orthogonal today? |
|---|---|---|
| Capture | `SessionPorts.capture_policy: CapturePolicy \| None`; `blobs: BlobStorePort \| None` | **Partly** — but bundled into `ExecutionProfile` |
| Isolation | `ExecutionProfile.process_backend` (`host` \| `platform-sandbox`) | ✅ |
| Durability | `persistence_mode` (`sqlite-wal`), `persistence_durable` | ✅ |
| Evaluation | `evaluation_mode` (`none` \| `exterior`), `evaluation_absence_reason` | ✅ |
| Retention | `retention` (`standard`), plus per-event `retention_class` column | ✅ |
| Assurance | `assurance_level` (`recorded` \| `hermetic`), `attestation_required` | ✅ |
| Telemetry | `RunResult.telemetry` (turns, prompt/completion tokens, `usd_micros`) | ✅ |
| Recovery | `checkpoints.py` + `ledger/recovery.py` | ✅ |

The `SessionPorts.capture_policy` docstring is notably thoughtful:

> `None` is the legacy no-capture composition and stays legal indefinitely: a session with no
> artifact store emits no artifact facts and makes no evidence claim it cannot support. Binding one
> turns capture on for this session and nothing else about it.

That is exactly the right principle — capture is additive and makes no claim it cannot support.

**Finding CAP-01 — `PARTIAL`.** The axes exist and are already largely orthogonal *at the port
level*. The problem is one level up: `ExecutionProfile` bundles them into four fixed presets
(`product`, `local`, `sandboxed`, `hermetic`), and `profile.digest` — *"the value that MUST change
whenever effective execution does"* — is computed over the whole bundle. So a user cannot vary
capture without changing profile identity.

### 9.2 The one real information-loss defect

Comparing the two presets a beta user would actually pick:

| Field | `product` | `local` |
|---|---|---|
| `capture_required` | **`True`** | **`False`** |
| everything else | identical | identical |

`product` and `local` differ in exactly one field, and it is capture. So the "cheap information"
axis is *already* the thing being traded away by preset choice — precisely the failure mode the brief
warns against. A user choosing `local` for convenience silently loses prompt/context/output capture.

**Recommendation.** Keep the four presets as *names*, but make capture an independently
overridable axis (`RuntimeBootstrap.build` already accepts an `overrides` parameter — the seam
exists), and flip the default so that cheap capture is on everywhere and only *cost* is opt-in.

### 9.3 Cost of "cheap" capture — measured, not assumed

The brief asks for the actual overhead. From §11:

| Capture item | Measured cost |
|---|---|
| Causal events (18 semantic events/episode) | ~26 KB, ~35 ms at current unbatched append |
| Plugin lifecycle (72 events/episode) | ~73 KB, ~139 ms at current unbatched append |
| Exterior verifier (pytest subprocess) | ~43 ms |
| Full episode, in-memory | 237 ms |
| Full episode, durable WAL | 387 ms |

**The genuinely cheap capture — prompts, context, outputs, tools, patches, digests — is not what
costs.** What costs is (a) fsync-per-event and (b) lifecycle ceremony for components that were never
used. Both are fixable without dropping a single field of semantic capture. This directly validates
the brief's thesis: there is no need to trade observability for speed here.

### 9.4 Proposed configuration model

Derived from the fields that already exist; every key below maps to real code.

```yaml
# Presets remain, as names over these axes. Nothing here is a new engine.
isolation:
  process_backend: host | platform-sandbox      # ExecutionProfile.process_backend
  workspace_mode:  in-place | sealed            # ExecutionProfile.workspace_mode

durability:
  events:      durable | ephemeral              # persistence_mode / persistence_durable
  commit:      per-event | per-turn | per-boundary   # NEW — the group-commit knob (H1-02)
  checkpoints: none | boundaries                # checkpoints.CheckpointManager

capture:                                        # ALL default to full; they are cheap
  prompts:   full | digest | off
  context:   full | digest | off
  outputs:   full | digest | off
  tools:     full | digest | off
  patches:   full | digest | off
  environment: digest                           # already a digest
  lifecycle: summary | full | off               # NEW — collapses the 72 events (H1-03)

telemetry:
  pareto: basic | full                          # RunResult.telemetry
  traces: off | sampled | full

evaluation:                                     # expensive: default off
  mode: none | exterior                         # ExecutionProfile.evaluation_mode
  evaluators: []
  repetitions: 1
  mutation_testing: false

control:                                        # §10.2 — who may steer, not who may log
  allow_reject: false
  allow_retry: true
  allow_redirect: false
  allow_fork: false

retention:
  artifacts: standard | extended | ephemeral    # ExecutionProfile.retention + retention_class
  trainability: <per-event column, already present>
```

Two keys are new (`durability.commit`, `capture.lifecycle`) and both correspond directly to the two
measured hot-path defects. Everything else is a rename of a field that exists.

### 9.5 Hashing and integrity (brief's correction #3)

The brief asks whether hashing/persistence/capture can be asynchronous without violating settlement,
recovery or integrity.

Current path, read from `ledger_emitter.py`:

```
construct Event → build envelope (payload cannot influence envelope claims, :299)
  → compute envelope_digest → store.append([envelope])  (:394, synchronous)
  → raise OSError if rejected                            (:396, fail-closed)
```

Artifacts follow `capture bytes → persist to CAS → digest → reference in ledger`, which is already
the ordering the brief endorses.

**Assessment.** Hashing itself is not the cost — SHA-256 over ~1.1 KB envelopes is negligible next to
a 1.9 ms fsync (the reciprocal of 519 events/s). Making hashing async would buy nothing and would
break the causal reference chain.

**However, batching the append is safe**, and this is the important distinction:

- Digest computation stays synchronous and in-order (identity preserved).
- Only the *fsync boundary* moves from per-event to per-turn.
- A crash then loses at most one turn's events — and the recovery machinery already handles a
  truncated suffix: `RecoveryScanner.reconcile_open_intents` and `continue_idempotent_effect` exist
  precisely to reconcile intents with no settled outcome.
- Settlement is unaffected because an effect is settled by its `EffectCompleted` event, and that
  event is in the same batch as the intent that precedes it.

**Recommendation:** group-commit at turn boundaries (`durability.commit: per-turn`), keep per-event
digesting, keep fail-closed on append rejection. Expected gain from §11.4: ~7.6× on append, ~139 ms
of the 150 ms durability penalty. Risk: bounded to one turn of history, already recoverable.

### 9.6 Recovery model

| Capability | Status | Evidence |
|---|---|---|
| Event-derived state | ✅ | `replay_ledger_state`, `domain/ledger/reducer.py` (63 kinds) |
| Checkpoint + suffix replay | ✅ | `CheckpointManager.reconstruct`, `_cold` |
| Cold replay cost | ✅ **1.64 ms / 90 events** (~55,000 events/s) | §11.5 |
| Open-intent reconciliation | ✅ | `recovery.py:236` |
| Open-child reconciliation | ✅ | `recovery.py:319` |
| Idempotent effect continuation | ✅ | `recovery.py:432` |
| Resume from a **killed process** | ❌ | §6.9 — untested |
| Resume from the **CLI** | ❌ | §6.4 |

Replay is cheap enough that checkpointing is an optimisation, not a necessity, at beta scale. That
is a good position to be in.

---

## 10. Universal event / plugin / workflow / transport contracts

### 10.1 Workflow — the existing primitives are already sufficient (brief's correction #4)

The brief asks, correctly, not to reject a workflow model before inspecting the code. Inspecting it:

| Primitive | Location |
|---|---|
| Operations / effects with typed verbs | `wiring.py` `EffectBinding`, `BindingResolver` |
| Causal events with dependencies | 63-kind roster, `reducer.py` |
| `agent.spawn` (mediated, capability-attenuated) | `runtime/delegation.py`, `ports/child_runtime.py` |
| Topology lowering | `runtime/topology.py` — roles, edges, flows, `entryRole` |
| Readiness/scheduling | `runtime/scheduler.py` |
| Settlement predicates | `EffectCompleted`, `reconcile`, `compensate` |
| Budget conservation across depth | `kernel/budget.py`, `kernel/attenuation.py` |

Can these express the nine shapes the brief lists?

| Shape | Expressible today? | How |
|---|---|---|
| Direct tool loop | ✅ | `vg-shell-only`; proven |
| ReAct-style loop | ✅ | `vg-code-default`; proven (M-4) |
| Staged coding workflow | ✅ | manifest + skill cards |
| Planner / executor / reviewer | ✅ | topology; proven (M-7 order12) |
| Critic / reviser | ✅ | same topology primitives |
| Research fan-out | ⚠️ | topology supports it; ADR-0099 disposition is sequential-only lowering |
| Fork / read / merge | ✅ | proven (M-7 order12) |
| Bounded retries | ✅ | budgets + `max_turns` |
| Nested subagents | ✅ | proven at depth 3 (M-6 order10) |

**Finding W-01 — `IMPLEMENTED`.** Eight of nine are proven; the ninth (parallel fan-out) is a
deliberate, recorded scheduling decision, not a missing capability. **Vanguard does not need a
workflow engine, and it must not acquire one.** The existing operations + events + spawn + topology
lowering *are* the workflow language. `topology.py:172 _reject_authority` keeps it declarative
("topology is routing data"), which is what prevents it from becoming a second orchestration
authority.

### 10.2 Plugin lifecycle boundaries and control vocabulary (brief's correction #2)

Existing lifecycle states (`registry/lifecycle.py`): `DISCOVERED → RESOLVED → VERIFIED → ACTIVATED →
QUIESCING → RETIRED`, plus `FAULTED`. These are *component* lifecycle states, not *operation*
interception points.

Mapping to the brief's proposed boundaries:

| Brief's boundary | Existing equivalent | Status |
|---|---|---|
| `before_operation` | Kernel dispatch S0–S12 (authorization) | ✅ but kernel-internal, not a plugin seam |
| `after_operation` | `EffectCompleted` emission | ✅ observable via events |
| `on_event` | Event stream / `observe_dispatch` (`root.py:519`) | ✅ |
| `before_commit` | `LedgerEmitter._write` | ⚠️ no interception seam |
| `after_result` | `on_terminal` callback (`execute_harness`/`run_composed`) | ✅ |
| `on_failure` | `EffectFailure`, `compensate`, `reground` | ✅ |

**Finding W-02 — `PARTIAL`.** Observation boundaries substantially exist. What does **not** exist is
an explicit control vocabulary. `ACCEPT | REJECT | RETRY | REDIRECT | FORK | STOP` appears nowhere;
`GateDecision` (`types_gen.py:89`) is the nearest thing and applies only to evaluation gating.

**Assessment against the brief's own constraint.** The brief says not to add speculative extension
seams without a concrete near-term consumer. There is no near-term consumer for `REDIRECT` or
`FORK`. Therefore:

- **Beta:** do not build a control-plugin framework. Document that plugins are **observers only**,
  and that control authority lives in the kernel and the approval flow. This is already true in
  code, and stating it is free.
- **Post-beta:** if a concrete consumer appears (an adversarial validator, a retry policy), extend
  `GateDecision` rather than inventing a parallel vocabulary.

The brief's rule that *"logging must never gain implicit control authority"* is **already enforced**,
and enforced well: `ledger_emitter.py:58` — *"would be claiming the Kernel's authority for its own
append"* — and `:93` — *"plugins, workers and child episodes propose, they never append."* The
`PRIVILEGED_KIND_OWNERS` table (26 kinds) mechanically prevents a non-kernel writer from emitting a
privileged kind. This is one of the best-implemented invariants in the system.

### 10.3 Transport neutrality

| Transport | Implementation | Shares the logical contract? |
|---|---|---|
| In-process | `Runtime.execute_profiled` | ✅ canonical |
| CLI | `runtime/cli.py` | ✅ thin client over the runtime |
| Daemon (JSON-RPC) | `runtime/service/service.py`, `service/contract.py` (367 LOC) | ✅ |
| HTTP (Studio) | `runtime/service/studio_gateway.py` | ✅ |
| Plugin cell (UDS JSON-RPC) | `adapters/sandbox/toolkit.py` | ✅ |

`ports/spi.py`'s header states the design intent: *"the five Protocols are client conveniences of
the wire"*. **Finding W-03 — `IMPLEMENTED`.** Transport neutrality holds; the wire contract is
primary and the Python protocols are conveniences over it. The one defect is `service.py:379`'s
hardcoded version (§6.1), which is a bug in a payload, not in the contract.

### 10.4 Governance audit

Classifying every governance mechanism per the brief's five categories:

| Mechanism | Category | Keep? |
|---|---|---|
| `check_tcb_budget.py` (kernel LOC ceiling) | Architectural invariant | ✅ Keep. Cheap, automated, load-bearing. |
| `check_boundaries.py` (hexagonal imports) | Architectural invariant | ✅ Keep. |
| `check_domain_blindness.py`, `check_kernel_neutrality.py` | Architectural invariant | ✅ Keep. |
| `check_isolation_policy.py` | Architectural invariant | ✅ Keep. |
| `verify_evidence.py` + Ed25519 trust root | Release integrity + scientific rigor | ✅ Keep. Proven discriminating. |
| `check_evidence_acceptance.py` (supersession) | Release integrity | ✅ Keep. |
| `release_qualification.py` | Release integrity | ✅ Keep, but state its real scope (§3.4). |
| Preregistration (`docs/03_execution/prereg/`) | Scientific rigor | ✅ Keep **for studies only**. |
| Paired study / CRN / McNemar / Holm | Scientific rigor | ✅ Keep for M-6.5-class work; never on the product path. |
| `check_execution_truth.py` (board/backlog consistency) | Ordinary product dev | ⚠️ Keep the check; **remove the duplication it polices** (§10.5). |
| `check_doc_budgets.py`, `check_doc_metadata.py`, `check_markdown_links.py`, `check_stale_paths.py` | Ordinary product dev | ⚠️ Keep, but they are the tax on 171 documents. |
| `check_commit_scope.py`, `check_core_changes.py` | Ordinary product dev | ⚠️ Review. |
| Dual execution boards (`sprint_active` + `backlog` + `sprint_upcoming` + `milestones`) | **Obsolete bureaucracy** | ❌ **Consolidate** (§10.5). |
| ADR requirement for ordinary changes | **Obsolete bureaucracy** | ❌ **Relax** (§10.6). |

### 10.5 Documentary duplication — the mechanism that is currently failing the build

Four documents encode overlapping work-package state:

| Document | Owns | Also duplicates |
|---|---|---|
| `milestones.md` | stable milestone gates | state model, dependency graph |
| `sprint_active.md` | **current state (accurate)** | milestone predicates, evidence verdicts |
| `backlog.md` | stable work-package contracts | **package states (currently wrong ×4)** |
| `sprint_upcoming.md` | later work | — |

`milestones.md` explicitly tries to prevent this — *"This file owns stable gates and must not
duplicate that volatile snapshot"* — and `check_execution_truth.py` enforces board/backlog agreement.
But the duplication was designed in anyway, and it is what is failing the suite today (§2.3).

**Recommendation (`H1-01` + `H2-10`):** package **state** lives in exactly one place —
`sprint_active.md`. `backlog.md` keeps stable *contracts* (entry/completion predicates) and drops its
state column entirely. `check_execution_truth.py` then verifies that every package named in the
board exists in the backlog, which is a real invariant, instead of policing a duplicated column that
must be hand-synchronised. This makes the failing test structurally impossible to fail for this
reason again.

### 10.6 Proposed ADR policy

**ADR required** (constitutional — these are the brief's list, and they are the right list):
kernel neutrality; causal integrity; authority and budget conservation; wire/schema compatibility;
replay semantics; transport equivalence; effect settlement and fail-closed execution; the TCB
ceiling.

**ADR not required** (ordinary engineering — no ratification):
adding a tool, verb binding, pack, manifest, evaluator, context strategy, or reference agent;
adding a CLI command; adapter implementations; test additions; performance work that changes no
contract; documentation.

Applied to this plan: of ~26 Horizon 1 and Horizon 2 tasks, **two** touch constitutional surface —
`H1-02` (group commit, touches durability/settlement semantics) and `H1-03` (lifecycle capture,
touches the event stream's completeness claim). Everything else is ordinary work. That ratio —
2 of 26 — is the concrete argument for relaxing the policy.

---

## 11. Performance and storage measurements

All figures below were produced by executing the **production path** — `Runtime.execute_harness` →
`compose` → `HarnessSession` → kernel dispatch → `GitEnvironmentAdapter` → `LedgerEmitter` — using
the fixtures of `test/runtime/test_composition_root.py` (a real Git repo, a real off-by-one bug, a
real unified diff, a real pytest verifier). The model is a scripted cassette, so **model latency is
excluded by construction** and every millisecond below is framework overhead.

Host: WSL2, Linux 6.18.33.2, Python 3.12.3. Benchmark scripts are in the session scratchpad and are
reproducible.

### 11.1 End-to-end episode overhead

Workload: 2 receipts (`fs.read`, `patch.apply`), 1 exterior verification, terminal `completed`.
n = 7, warm.

| Configuration | Median | Min | Max | σ |
|---|---:|---:|---:|---:|
| In-memory store, **with** pytest verifier | **237 ms** | 233 ms | 243 ms | 3.0 ms |
| In-memory store, **no** verifier | **195 ms** | — | — | — |
| **File-backed SQLite-WAL**, with verifier | **387 ms** | — | — | — |

Derived:

| Component | Cost | Share of 387 ms |
|---|---:|---:|
| Framework core (compose, kernel, session, environment) | ~195 ms | 50% |
| Exterior verifier (pytest subprocess) | ~43 ms | 11% |
| **Durable ledger writes** | **~150 ms** | **39%** |

**Finding PERF-01.** Sub-second framework overhead for a complete governed, authorized,
event-sourced, durable coding episode is a genuinely good result for this class of system. The
variance is also very low (σ = 3 ms on 237 ms), which indicates no hidden nondeterminism in the hot
path. But **39% of the wall clock is the ledger**, and §11.4 shows almost all of that is avoidable.

### 11.2 Storage — 90 events for a two-receipt episode

```
$ sqlite3 .../events.sqlite3 "select count(*) from events"
90
main db file:  4,096 bytes   (WAL mode — data is in the -wal file)
on disk total: 172,032 bytes
row payload:   121,440 bytes
envelope JSON:  98,969 bytes
```

**Amplification: ~86 KB on disk per receipt; ~1.1 KB per event.**

### 11.3 Where the events actually go — the headline finding

| Count | Envelope bytes | Kind | Category |
|---:|---:|---|---|
| 12 | 11,878 | `PluginDiscovered` | ceremony |
| 12 | 11,807 | `PluginResolved` | ceremony |
| 12 | 13,967 | `PluginVerified` | ceremony |
| 12 | 11,843 | `PluginActivated` | ceremony |
| 12 | 11,809 | `PluginQuiesced` | ceremony |
| 12 | 11,773 | `PluginRetired` | ceremony |
| 4 | 4,644 | `EffectStarted` | semantic |
| 3 | 3,011 | `ProposalProduced` | semantic |
| 2 | 1,855 | `BudgetReserved` | semantic |
| 2 | 1,864 | `BudgetCommitted` | semantic |
| 2 | 2,376 | `EffectCompleted` | semantic |
| 1 | 1,224 | `EpisodeStarted` | semantic |
| 1 | 1,146 | `CompetencePriorRecorded` | semantic |
| 1 | 971 | `ApprovalRequested` | semantic |
| 1 | 1,391 | `CapabilityGranted` | semantic |
| 1 | 7,410 | `EpisodeCompleted` | semantic |
| **90** | **98,969** | | |

| Category | Events | Share | Bytes | Share |
|---|---:|---:|---:|---:|
| **Plugin lifecycle ceremony** | **72** | **80.0%** | **73,077** | **73.8%** |
| Semantic execution | 18 | 20.0% | 25,892 | 26.2% |

**Finding PERF-02 — the single most actionable measurement in this audit.**

The 72 ceremony events are exactly 12 × 6: the `vg-code-default` manifest declares **12 components**
(1 `system_prompt`, 4 `tools`, 1 `context_policy`, 1 `routing_policy`, 1 `approval_policy`,
1 `retrieval_policy`, 3 `skill` cards), and `PluginLifecycle` emits one event per entered state for
each of them, on **every episode**, whether or not the component is ever used. In this episode only
2 of the 4 tools were invoked, yet all 12 components paid the full 6-event lifecycle.

The event schema `events` table also carries 19 columns including `confidentiality`,
`retention_class`, `trainability` and `redaction_status` — good governance metadata, but multiplied
across 72 unnecessary rows.

**Recommendation (`H1-03`).** Add `capture.lifecycle: summary | full | off`, defaulting to
`summary`: emit `PluginDiscovered`/`PluginActivated` for components actually resolved into the
active composition, plus **one** `RegistryComposed` summary event carrying the digest of the full
12-component lifecycle. `full` reproduces today's behaviour byte-for-byte for evidence runs. This is
a ~4× reduction in event count and ~3× in bytes, with the capability and the auditability retained
(the summary carries the digest, so nothing becomes unverifiable).

### 11.4 Append throughput — synchronous vs batched

Same 90-event corpus, replayed into fresh stores. Median of 3 runs.

| Store configuration | Median | **Events/sec** | vs baseline |
|---|---:|---:|---:|
| SQLite WAL, `synchronous=FULL`, **one-by-one** ← **what the runtime does** | 173.2 ms | **519** | 1.0× |
| SQLite WAL, `synchronous=FULL`, batched | 22.8 ms | 3,949 | **7.6×** |
| SQLite WAL, `synchronous=NORMAL`, one-by-one | 44.4 ms | 2,028 | 3.9× |
| SQLite WAL, `synchronous=NORMAL`, batched | 17.4 ms | 5,165 | 9.9× |
| In-memory, one-by-one | 0.19 ms | 476,225 | 917× |
| In-memory, batched | 0.03 ms | 2,971,179 | 5,724× |

**Finding PERF-03 — the causal chain closes exactly.**

`LedgerEmitter._write` (`ledger_emitter.py:394`) executes `self.store.append([envelope])` — a
one-element list — for every event. `SqliteEventStore.__init__` defaults to `synchronous="FULL"`.
So the runtime operates in the slowest row of that table: **519 events/second**.

90 events ÷ 519 events/s = **173 ms**, against a **measured 150 ms** difference between the
in-memory and file-backed episodes (§11.1). The residual is batching that already occurs incidentally
within a turn. **The entire durability overhead of the product path is accounted for.**

**Recommendation (`H1-02`).** Group-commit at turn boundaries. Keep `synchronous=FULL` (do not buy
speed with durability). Keep per-event digesting and ordering. Expected: ~139 ms of the ~150 ms
recovered.

**Combined with `H1-03`:** 90 events → ~25 events, and 519 ev/s → ~3,949 ev/s. Projected ledger cost
per episode: ~6 ms, down from ~173 ms. **Projected episode wall clock: ~205 ms, down from 387 ms —
a 47% reduction with no loss of semantic capture and no invariant weakened.**

### 11.5 Cold replay and recovery

| Operation | Median | Rate |
|---|---:|---:|
| Read 90 events from SQLite + `replay_ledger_state` | **1.64 ms** | ~55,000 events/s |

**Finding PERF-04.** Recovery is 100× cheaper than the writes that produced the history. A run with
9,000 events would cold-replay in ~164 ms. **Checkpointing is an optimisation, not a requirement, at
any plausible beta scale.** `checkpoints.py` (539 LOC) is therefore not on the critical path and
should not be a beta concern.

### 11.6 Concurrency — and a real defect

**(a) Independent agents, separate ledgers** (thread pool, 3 episodes per worker):

| Concurrent agents | Episodes | Wall | Median latency | Throughput |
|---:|---:|---:|---:|---:|
| 1 | 3 | 0.83 s | 243 ms | 3.62 ep/s |
| 2 | 6 | 1.14 s | 353 ms | **5.26 ep/s** |
| 4 | 12 | 2.54 s | 775 ms | 4.72 ep/s |

Throughput peaks at 2 workers (1.45×) and **regresses** at 4, while per-episode latency degrades
3.2× from 243 ms to 775 ms. Causes: the GIL, plus a pytest subprocess per verification. This is a
threading-model limit, not a ledger limit — **process-level parallelism is the right answer for
multi-agent scale-out**, and nothing in the architecture prevents it.

**(b) Concurrent agents sharing one project ledger: FAILS**

```
OSError: Non-monotonic sequence in project 'project-default':
  event 01a04a2a-…-916c530776d7 has seq 318 (318) <= prior seq 318
component cleanup failed: … has seq 318 (318) <= prior seq 319
component cleanup failed: … has seq 318 (318) <= prior seq 320
  … (repeating through cleanup)
```

**Finding PERF-05 — `PARTIAL` / real defect.** Sequence numbers are allocated non-atomically
(read-then-write race), so two threads appending to one project ledger collide.

Mitigating assessment — this is much less severe than it looks:

1. **It fails closed.** The monotonicity invariant *detects* the race and refuses the write. No
   corruption, no silent reordering, no torn history. The invariant is doing its job.
2. It is arguably **by design**: the architecture specifies a *single project-ledger writer*, and
   two concurrent sessions on one project ledger violate that precondition.
3. No production path does this today. `RuntimeBootstrap` derives the store path per repository.

The genuine defects are (i) nothing in the API signature, docstring, or type prevents a caller from
doing it; (ii) the failure surfaces as a raw `OSError` mid-run with a noisy cleanup cascade rather
than a typed precondition error; (iii) it is undocumented.

**Recommendation.** Beta (`H1-17`): document the single-writer constraint and convert the collision
to a typed `ConcurrentLedgerWriter` error raised at store acquisition, not mid-episode. Horizon 2
(`H2-08`): if concurrent same-project agents become a requirement, allocate sequences inside the
SQLite transaction. Do **not** do this for the beta — no consumer needs it.

### 11.7 Comparison against a dedicated baseline

The brief asks for a comparison with "the simplest dedicated baseline available", while warning
against unfair comparisons.

**I did not run one, and I recommend against manufacturing one for the beta.** Any honest baseline
would have to hold model, tools and task logic constant while removing the substrate — which means
writing a bespoke minimal agent loop. The result would measure the cost of *governance,
authorization, capture and durability*, which is not overhead to be minimised but the product's
entire value proposition.

The defensible and more useful comparison is **Vanguard against itself**, which §11.1–11.4 supply:

| Configuration | Episode wall clock |
|---|---:|
| Ungoverned floor (in-memory, no verifier) | 195 ms |
| Today's product path (durable WAL + verifier) | 387 ms |
| **Projected after `H1-02` + `H1-03`** | **~205 ms** |

That says the *achievable* cost of full governance and durability over the ungoverned floor is
roughly **10 ms per episode**, and that today's 192 ms gap is implementation slack, not architectural
cost. That is the number the team should hold itself to, and it is far more actionable than a
contrived cross-framework benchmark. `H1-18` records these as regression thresholds.

### 11.8 Measurement summary

| Metric | Measured | Target after H1 |
|---|---:|---:|
| Episode overhead (durable, verified) | 387 ms | ≤ 220 ms |
| Framework core (no durability, no verifier) | 195 ms | unchanged |
| Events per 2-receipt episode | 90 | ≤ 30 |
| Ceremony share of events | 80% | ≤ 25% |
| Ledger bytes per episode | ~172 KB | ≤ 50 KB |
| Append throughput (durable) | 519 ev/s | ≥ 3,500 ev/s |
| Cold replay | 55,000 ev/s | unchanged |
| Concurrent throughput peak | 5.26 ep/s @ 2 workers | unchanged (process-level in H2) |
| Shared-ledger concurrency | crashes (fails closed) | typed error |

---
---
---

# CHAPTER II — TWO-HORIZON EVOLUTION PLAN

Every task below carries: **ID**, concrete outcome, affected modules, dependencies, tests,
measurable acceptance criteria, whether it changes **behaviour** or only **structure**, estimated
risk, and explicit non-goals.

Risk scale: **L** = local, reversible, covered by existing tests. **M** = touches a shared path;
needs new tests. **H** = touches a verified invariant or the hot path; needs evidence re-run.

---

## 12. Exact `0.9.0b1` completion plan (Horizon 1)

**Objective.** Ship an installable, runnable, inspectable, resumable, offline-testable backend beta
with two working reference workflows and a measured performance baseline.

**Explicit non-goals for the entire horizon.** No refactoring of `session.py` or `service.py`. No
deletion of `execute_harness`. No new SOTA capabilities. No SWE-Bench work. No new orchestration
engine. No control-plugin framework. No parallel topology scheduling. No changes to `kernel/`.

### Wave 0 — Restore a green, honest baseline

#### `H1-01` — Eliminate package-state drift
- **Outcome:** `python3 -m pytest` reports 0 failures.
- **Modules:** `docs/03_execution/backlog.md`, `docs/03_execution/sprint_active.md`, `tools/linters/check_execution_truth.py`.
- **Depends on:** none. **This is the first task.**
- **Change:** Remove the *state* column from `backlog.md`; it keeps stable entry/completion
  predicates only. `sprint_active.md` becomes the sole owner of package state (it is already the
  accurate one — §3.2). Repoint `check_execution_truth.py` at the real invariant: every package on
  the board exists in the backlog, and every backlog package has stable predicates.
- **Tests:** `test/tools/test_check_execution_truth.py` (must pass); add a negative fixture where a
  board package is absent from the backlog.
- **Acceptance:** full suite `0 failed`; deleting a backlog package makes the new check fail.
- **Type:** structure (documentation + linter). **Risk: L.**
- **Non-goals:** do not change any package's actual state; do not touch `milestones.md` gates.

#### `H1-02` — Group-commit ledger appends
- **Outcome:** ledger appends batch at turn boundaries; ~139 ms/episode recovered.
- **Modules:** `runtime/ledger_emitter.py` (`_write`, `:394`), `runtime/session.py` (turn boundary),
  `adapters/stores/event_store.py`.
- **Depends on:** `H1-01`.
- **Change:** buffer envelopes within a turn; flush as one `store.append(batch)` at the turn
  boundary and at every terminal/settlement point. Digests still computed per event, in order.
  `synchronous=FULL` retained. Append rejection still raises (fail-closed). New config key
  `durability.commit: per-event | per-turn` (§9.4), defaulting to `per-turn`; `per-event` reproduces
  today's behaviour exactly.
- **Tests:** new `test/runtime/test_group_commit.py` — (a) event order and `seq` identical to
  `per-event` mode; (b) SIGKILL mid-turn loses at most one turn and `RecoveryScanner` reconciles the
  open intents; (c) `envelope_digest` values byte-identical across modes. Re-run
  `test/falsifiers/test_rf101_rf112_canonical_recursion.py` and `test_m7_topology_execution.py`.
- **Acceptance:** append ≥ 3,500 ev/s (from 519); durable episode ≤ 250 ms; **every existing
  falsifier still passes**; M-4/M-6/M-7/M-8 bundles re-verify `passed` after re-run.
- **Type:** **behaviour** (durability granularity). **Risk: H** — touches settlement semantics.
- **Non-goals:** do not weaken `synchronous`; do not make hashing async; do not reorder events.
- **ADR required:** yes (durability/settlement semantics).

#### `H1-03` — Lifecycle capture axis
- **Outcome:** ceremony events drop from 72 to ≤ 6 per episode by default; capability retained.
- **Modules:** `runtime/registry/lifecycle.py`, `runtime/registry/broker.py`, `runtime/profiles.py`.
- **Depends on:** `H1-02`.
- **Change:** add `capture.lifecycle: summary | full | off`, default `summary`. In `summary`, emit
  lifecycle events only for components resolved into the active composition, plus one
  `RegistryComposed` event carrying the digest of the complete 12-component lifecycle record.
  `full` is byte-identical to today and is what evidence runs use.
- **Tests:** new `test/registry/test_lifecycle_capture.py` — (a) `full` reproduces today's 72 events
  exactly; (b) `summary` emits ≤ 6 and its digest matches the `full` record; (c) the fail-closed
  transition table is unchanged in all modes.
- **Acceptance:** ≤ 30 events per 2-receipt episode in `summary`; ≤ 50 KB ledger; `full` mode
  digest-identical to pre-change; `test/falsifiers/test_rf38_rf45_plugin_lifecycle.py` passes.
- **Type:** **behaviour** (event stream completeness under default config). **Risk: H.**
- **Non-goals:** do not change the state machine; do not remove any event kind from the roster.
- **ADR required:** yes (causal-history completeness claim).

#### `H1-04` — One version source
- **Outcome:** `0.9.0b1` declared once; every surface reports it.
- **Modules:** `pyproject.toml:7`, `vanguard/__init__.py:12`, `runtime/service/service.py:379`,
  `docs/03_execution/milestones.md:9`.
- **Depends on:** none. **Change:** set `version = "0.9.0b1"` in `pyproject.toml`; make
  `service.py` emit `vanguard.__version__`; add a test asserting no other module contains a version
  literal.
- **Tests:** new `test/tools/test_version_single_source.py`.
- **Acceptance:** `vanguard --version`, `doctor`, and the daemon's `serverVersion` all report
  `0.9.0b1`; the grep-based test finds no stray literal.
- **Type:** structure. **Risk: L.** **Non-goals:** no release tagging.

#### `H1-05` — No silent in-memory ledger
- **Outcome:** ephemeral storage is never chosen without saying so.
- **Modules:** `runtime/root.py:103`, `runtime/service/service.py:140`.
- **Depends on:** `H1-01`.
- **Change:** `service.py` requires an explicit store path or fails with `EXIT_UNAVAILABLE`.
  `root.py:103` emits an explicit `EphemeralLedgerSelected` warning event when it falls back.
- **Tests:** new `test/runtime/test_no_silent_ephemeral.py`.
- **Acceptance:** starting the daemon with no store path fails with a typed error; every
  `:memory:` selection on a product path is preceded by an observable event.
- **Type:** **behaviour** (daemon startup). **Risk: M.**
- **Non-goals:** do not remove `bootstrap.py:88`'s dead branch (Horizon 2); do not touch
  `lab_driver.py`.

### Wave 1 — Product surface

#### `H1-06` — Model factory + offline adapter selection
- **Outcome:** `vanguard run --model-adapter fake` executes with no network and no API key.
- **Modules:** new `runtime/model_factory.py`; `runtime/cli.py:267`, `runtime/bootstrap.py:129`.
- **Depends on:** `H1-04`.
- **Change:** one `ModelFactory.for_profile(profile, overrides)` returning `OpenRouterModel`,
  `OllamaModel` or `FakeModel`. CLI and bootstrap call it instead of constructing adapters. The
  no-API-key hard exit moves behind the factory so it fires only for adapters that need a key.
- **Tests:** new `test/runtime/test_model_factory.py`; extend `test/tools/` CLI tests for the
  offline path.
- **Acceptance:** with `OPENROUTER_API_KEY` unset and no network, `vanguard run --model-adapter
  fake --task …` completes and writes a durable ledger.
- **Type:** **behaviour** (new CLI option; existing default unchanged). **Risk: M.**
- **Non-goals:** do not migrate `model_selection.py`'s five sites (Horizon 2); do not change routing
  policy.

#### `H1-07` — Distribution hygiene
- **Outcome:** the wheel installs no top-level `packs/` or `schemas/`.
- **Modules:** `pyproject.toml` (`packages.find`, `package-data`).
- **Depends on:** none.
- **Change:** move packaged schemas under `vanguard/schemas/` (or ship as package data of
  `vanguard`); drop `packs*` from the distribution entirely — it is linter/evidence infrastructure
  (§4.8) and no production code reads it. Resolve via `importlib.resources`, not `__file__` walking.
- **Tests:** new `test/tools/test_wheel_layout.py` — build a wheel, assert its top-level names are
  exactly `{vanguard}`.
- **Acceptance:** `pip install` into a clean target creates no top-level `packs`/`schemas`;
  `vanguard doctor` from the installed location still resolves the packaged default manifest.
- **Type:** structure (packaging). **Risk: M** — path resolution must be re-verified.
- **Non-goals:** do not delete `packs/` from the repository.

#### `H1-08` — CLI inspection commands
- **Outcome:** `vanguard status`, `vanguard events`, `vanguard artifacts`.
- **Modules:** `runtime/cli.py`; reads `runtime/ledger/projections.py`,
  `runtime/trajectory_reader.py`, `runtime/artifacts.py`.
- **Depends on:** `H1-04`.
- **Change:** three read-only subcommands over existing machinery. `--json` on each.
  `status` renders the ADR-0103 progress projection; `events` supports `--run`, `--kind`,
  `--since`, `--limit`; `artifacts` lists and `--get <digest>` fetches from CAS.
- **Tests:** new `test/tools/test_cli_inspection.py` against a fixture ledger.
- **Acceptance:** after an offline `run`, each command returns correct data with exit 0; each
  returns `EXIT_UNAVAILABLE` on an uninitialised workspace; `--json` output validates.
- **Type:** **behaviour** (new commands; nothing existing changes). **Risk: L** — read-only.
- **Non-goals:** no mutation; no daemon changes; no new projections.

#### `H1-09` — `vanguard resume` + a real crash test
- **Outcome:** a SIGKILLed run resumes from its ledger and completes.
- **Modules:** `runtime/cli.py`; reuses `ledger/recovery.py::RecoveryScanner`,
  `checkpoints.py::CheckpointManager`, `service.py:695 _cmd_Resume`.
- **Depends on:** `H1-06`, `H1-08`.
- **Change:** `vanguard resume --run <id>` calling the existing recovery path — no new recovery
  logic. Delete the hollow `test/runtime/test_coding_resume.py` (D-06) and replace it with a real
  test.
- **Tests:** new `test/runtime/test_kill_and_resume.py` — start an offline run in a subprocess,
  `SIGKILL` mid-turn, `resume`, assert terminal state and that reconstruction matches an
  uninterrupted run's state digest.
- **Acceptance:** the kill/resume test passes 10 consecutive times (it must not be flaky); resumed
  and uninterrupted state digests are equal; no duplicated effects (idempotent continuation).
- **Type:** **behaviour** (new command). **Risk: M** — first true crash test; may surface latent
  recovery bugs. *That is the point.*
- **Non-goals:** no new recovery semantics; if the test finds a bug, fix the bug, do not weaken the
  test.

#### `H1-10` — Readiness endpoint
- **Outcome:** `/api/v1/ready` distinct from `/api/v1/health`.
- **Modules:** `runtime/service/studio_gateway.py:156`, reusing `cli.py:161 cmd_doctor` checks.
- **Depends on:** `H1-05`.
- **Change:** extract `doctor`'s checks into a reusable function; `health` = process alive;
  `ready` = store reachable *and* durable, manifest resolvable, credentials present. `200`/`503`.
- **Tests:** new `test/runtime/test_health_readiness.py`.
- **Acceptance:** with no store, `health` is 200 and `ready` is 503 with a typed reason.
- **Type:** **behaviour** (new endpoint). **Risk: L.**
- **Non-goals:** no auth changes; no new metrics.

#### `H1-13` — Redact CLI diagnostics
- **Outcome:** no unredacted adapter exception reaches the terminal.
- **Modules:** `runtime/cli.py:283` (the `except Exception` catch-all).
- **Depends on:** `H1-08`. **Change:** route the handler through the existing capture/redaction
  policy; print a typed error and a reference digest; keep `--traceback` for local debugging.
- **Tests:** new `test/tools/test_cli_redaction.py` — an adapter raising with an embedded fake key
  must not print it.
- **Acceptance:** the injected secret is absent from stdout/stderr; `scan_secrets.py` passes over
  captured output.
- **Type:** **behaviour** (error text). **Risk: L.**

### Wave 2 — The two reference workflows

#### `H1-14` — Register and prove `vg-code-explain`
- **Outcome:** a second, materially different workflow is registered, tested and documented.
- **Modules:** `agency/manifests/registry.json`,
  `agency/manifests/vg-code-explain/REFERENCE.md` (new).
- **Depends on:** `H1-06`.
- **Change:** add the `registry.json` entry (`role: "reference-explainer"`); write `REFERENCE.md`
  to match the other six; add an end-to-end test. **The workflow itself needs no code change — it
  already executes (§6.10).**
- **Tests:** new `test/integration/test_reference_workflow_explain.py` — run `vg-code-explain`
  offline through `Runtime.execute_profiled`, assert terminal `completed`, a read receipt, no write
  effect attempted, and a composition digest different from `vg-code-default`.
- **Acceptance:** test passes offline; `registry.json` and the manifests directory agree;
  `test/agency/test_manifest_loader.py` extended and passing.
- **Type:** structure + test. **Risk: L.**
- **Non-goals:** do not change the manifest's tools or prompt.

#### `H1-15` — Make `TableWorldEnvironment` an `EnvironmentPort`
- **Outcome:** the non-coding domain executes end-to-end; the substrate claim becomes true.
- **Modules:** `adapters/environment/tableworld.py`, `agency/manifests/registry.json`.
- **Depends on:** `H1-06`, `H1-16`.
- **Change:** implement the eight `EnvironmentPort` methods (`profile`, `snapshot`, `observe`,
  `preview`, `apply`, `reconcile`, `compensate`, `dispose`) over the existing
  `handle_read`/`handle_patch`/`get_table_state`. `snapshot` returns a table-state digest;
  `compensate` restores the prior record (`TableState` already versions records). Register
  `vg-table-default`.
- **Tests:** new `test/integration/test_reference_workflow_table.py` — a `table.read` +
  `table.patch` episode offline, asserting a real receipt, a real state change, budget conservation,
  and cold reconstruction of terminal state. Extend `test/adapters/test_tableworld.py` for
  compensation.
- **Acceptance:** a non-coding episode reaches terminal `completed` through the **same**
  `Runtime.execute_profiled` with **zero** changes under `kernel/`, `domain/` or `agency/` —
  verified by `check_boundaries.py` and `check_kernel_neutrality.py`; drift **D-27 closed**.
- **Type:** **behaviour** (new capability). **Risk: M** — new adapter, but additive and covered.
- **Non-goals:** do not implement `table.diff` (the provider deliberately does not advertise it); do
  not add table concepts to `kernel/` or `domain/`.

#### `H1-16` — Typed environment-contract failure
- **Outcome:** an incomplete environment adapter fails with an actionable typed error.
- **Modules:** `runtime/wiring.py:495 _environment_map`, `runtime/session.py:614`.
- **Depends on:** `H1-01`.
- **Change:** verify the `EnvironmentPort` surface at session construction and raise
  `CompositionError("environment adapter X does not implement EnvironmentPort: missing profile,
  snapshot, …")` instead of letting an `AttributeError` escape.
- **Tests:** new `test/runtime/test_environment_contract.py` — a deliberately partial adapter yields
  the typed error naming every missing method.
- **Acceptance:** the exact failure reproduced in §6.10 becomes a typed `CompositionError`; the
  message names all eight missing methods.
- **Type:** **behaviour** (error type). **Risk: L.**
- **Non-goals:** do not add runtime duck-typing tolerance; fail closed.

#### `H1-17` — Document and type the single-writer constraint
- **Outcome:** the §11.6 crash becomes a typed precondition error.
- **Modules:** `adapters/stores/event_store.py`, `ports/event_store.py` docstrings.
- **Depends on:** `H1-02`.
- **Change:** detect a second concurrent writer at store acquisition and raise a typed
  `ConcurrentLedgerWriter` error there, rather than an `OSError` mid-episode with a cleanup cascade.
- **Tests:** new `test/adapters/test_single_writer.py` reproducing the two-thread case.
- **Acceptance:** the reproduction raises `ConcurrentLedgerWriter` at acquisition; no partial
  episode is written; no cleanup cascade.
- **Type:** **behaviour** (error type and timing). **Risk: M.**
- **Non-goals:** do **not** implement concurrent same-project writes.

### Wave 3 — Cleanup, measurement, freeze

#### `H1-11` — Split `TECHNICALLY_VERIFIED` from `LINEAGE_ACCEPTED`
- **Outcome:** the milestone vocabulary stops conflating two predicates (§5.2).
- **Modules:** `docs/03_execution/milestones.md`, `docs/03_execution/sprint_active.md`, new ADR.
- **Depends on:** `H1-01`.
- **Acceptance:** M-4/M-6/M-6.5/M-7/M-8 read `TECHNICALLY_VERIFIED`; M-5a reads
  `BLOCKED_ON_RELEASE_IDENTITY`; the beta predicate references `TECHNICALLY_VERIFIED` only.
- **Type:** structure. **Risk: L.** **ADR required:** yes (acceptance semantics).

#### `H1-12` — Honest release qualification
- **Outcome:** `release_qualify.sh` states its scope; suite and linters are explicit stages.
- **Modules:** `ci/release_qualify.sh`, `tools/release_qualification.py`.
- **Depends on:** `H1-01`, `H1-04`.
- **Change:** add `--with-suite` and `--with-linters` stages, and make the report enumerate what it
  did **not** check (Git identity, organisational independence).
- **Acceptance:** `./ci/release_qualify.sh --with-suite --with-linters` exits 0 and its JSON lists
  every stage plus explicit non-checks.
- **Type:** **behaviour** (new stages). **Risk: L.**

#### `H1-19` — Remove dead code
- **Outcome:** eight dead items removed (§7.1, D-01…D-08).
- **Modules:** `vanguard/packages/apps/`, six `test/runtime/test_coding_*.py`,
  `tools/linters/check_domain_blindness.py`.
- **Depends on:** `H1-09` (which replaces `test_coding_resume.py`).
- **Acceptance:** suite count drops by 0 tests (the shells contain none); no import breaks; the
  `layer0/` WARN is gone.
- **Type:** structure. **Risk: L.**

#### `H1-20` — Archive the stale master report
- **Outcome:** no falsified document at the repository root.
- **Modules:** move `VANGUARD_BACKEND_M1_M9_MASTER_REPORT.md` →
  `docs/_archive/reviews/backend/`, with a header noting §3.1's findings.
- **Depends on:** `H1-01`. **Acceptance:** `check_markdown_links.py` and `check_stale_paths.py`
  pass. **Type:** structure. **Risk: L.**

#### `H1-21` — Fix the developer environment
- **Outcome:** the documented setup can run the suite.
- **Modules:** `CONTRIBUTING.md`, `Makefile`, `docs/07_engineering/development.md`.
- **Depends on:** none. **Change:** document `pip install -e '.[dev]'`; add `make test`.
- **Acceptance:** following the documented steps from a clean clone runs the full suite green.
- **Type:** structure. **Risk: L.** (Finding B-01.)

#### `H1-18` — Freeze the performance baseline
- **Outcome:** §11's measurements become enforced regression thresholds.
- **Modules:** new `test/benchmarks/test_overhead_baseline.py`; `benchmarks/`.
- **Depends on:** `H1-02`, `H1-03`.
- **Change:** commit the four benchmark scripts from this audit; assert generous ceilings (episode
  ≤ 300 ms, events ≤ 40, ledger ≤ 80 KB, append ≥ 2,500 ev/s) so the test is not flaky on slow CI
  but still catches a regression of the §11 magnitude.
- **Acceptance:** thresholds hold on three consecutive CI runs; reverting `H1-02` makes the test fail.
- **Type:** test only. **Risk: L.**
- **Non-goals:** no cross-framework benchmark (§11.7).

#### `H1-22` — Beta artifact freeze
- **Outcome:** an exact, reproducible `0.9.0b1` artifact.
- **Depends on:** **all of the above.**
- **Acceptance (the beta gate):**
  1. `python3 -m pytest` → **0 failed**.
  2. All 24 linters pass.
  3. `./ci/release_qualify.sh --with-suite --with-linters` → exit 0.
  4. Wheel builds; installs into a clean environment; no top-level `packs`/`schemas`.
  5. **Offline vertical slice, from the installed wheel, with no network and no API key:**
     `init → doctor → run --model-adapter fake → status → events → artifacts → SIGKILL → resume →
     verify`.
  6. **Two reference workflows** execute offline through the same runtime: `vg-code-default` and
     `vg-code-explain`; plus `vg-table-default` proving the non-coding domain.
  7. **Multi-role** topology executes (M-7 evidence re-verified after `H1-02`/`H1-03`).
  8. §11.8 thresholds met.
  9. M-4/M-6/M-6.5/M-7/M-8 bundles **re-verify `passed`** after the hot-path changes.
- **Type:** release. **Risk: M.**

### 12.6 Optional — formal scientific / signed-release acceptance

Per the brief, these are **separate** and **do not gate** `0.9.0b1`:

| ID | Step | Why it is not a beta blocker |
|---|---|---|
| `OPT-01` | Create and push annotated `CONVERGENCE-BASE-v1`; run the fail-closed baseline builder | Release-owner Git action. Unblocks M-5a lineage only. |
| `OPT-02` | Re-emit M-5b against the successor baseline | Depends on `OPT-01`. Generality *falsifier*, not product function. |
| `OPT-03` | A distinct reviewer identity re-signs the M-4 candidate-07 digest | Organisational independence. **No rerun needed** — same digest. |
| `OPT-04` | Publish an M-9 evidence bundle for the beta artifact | Formal attestation of a beta that already works. |
| `OPT-05` | Attach §11.6 contention data to ADR-0099 | Completes a recorded decision with measurement. |

---

## 13. Exact `0.9.1` refactoring plan (Horizon 2)

**Objective.** Evolutionary consolidation — not a rewrite — measured against the `0.9.0b1` baseline
frozen by `H1-18`.

**Governing rule.** Every Horizon 2 task must leave composition digests, trajectory digests and
event `seq` ordering **unchanged**. Because those digests are computed over canonicalised state, a
structural change that preserves them is *provably* semantics-preserving. That is the acceptance
mechanism for this entire horizon, and it is unusually strong — most codebases cannot make this
guarantee.

**Explicit non-goals for the whole horizon.** No new kernel. No second ledger, agent engine or
orchestration authority. No import of Lex/LIM as production engines. No removal of any architectural
invariant linter. No reduction in semantic capture.

### `H2-01` — Complete the ADR-0089 entrypoint migration
- **Outcome:** `execute_profiled` is the only public composition entrypoint; `execute_harness` is
  removed (its `W3D-12` sunset).
- **Modules:** `runtime/root.py:70`, `runtime/child_runtime.py` (5 refs), ~35 test files.
- **Depends on:** `0.9.0b1` frozen.
- **Change:** migrate `child_runtime.py` first (the only production consumer), then tests, then
  delete. Tests move to `execute_profiled(profile_id="local", …)` or to `run_composed` with
  explicit `SessionPorts`.
- **Tests:** all existing falsifiers must pass unchanged in assertion content.
- **Acceptance:** `grep -r execute_harness vanguard/ test/` returns nothing; **M-4/M-6/M-7/M-8
  bundles re-verify `passed`**; `root.py` drops ~110 LOC.
- **Type:** structure. **Risk: M** — wide blast radius, but each step is mechanical and covered.
- **Non-goals:** do not change `run_composed`'s signature.

### `H2-02` — Extract `session.py` (1,401 LOC)
- **Outcome:** four cohesive modules; no file over ~500 LOC; zero semantic change.
- **Modules:** `runtime/session.py` → `session/ports.py` (`SessionPorts`), `session/lifecycle.py`
  (construction, environment mapping), `session/turn.py` (the loop), `session/terminal.py`
  (resolution, telemetry). `runtime/session.py` re-exports for compatibility.
- **Depends on:** `H2-01`.
- **Tests:** existing `test/runtime/*` unchanged (import surface preserved).
- **Acceptance:** **byte-identical composition and trajectory digests** on the `H1-18` fixture
  before and after; §11.8 thresholds unchanged; no file > 550 LOC.
- **Type:** **structure only**. **Risk: M** — hot path; the digest criterion is the guard.
- **Non-goals:** no behaviour change, no signature change, no performance work.

### `H2-03` — Delete `runtime/entrypoint.py`
- **Outcome:** the sixth composition path and its domain leak are gone (§4.4, and
  `docs/01_law/EXTENSIBILITY.md:56`).
- **Modules:** `runtime/entrypoint.py` (153 LOC), its one internal reference.
- **Depends on:** `H2-01`. **Acceptance:** file removed; no import breaks; no client regression;
  `check_stale_paths.py` passes. **Type:** structure. **Risk: L.**
- **Non-goals:** if a client is found to depend on it, replace it with a thin `execute_profiled`
  wrapper rather than keeping the mini-runtime.

### `H2-04` — Unify model construction
- **Outcome:** one factory; `model_selection.py`'s five sites route through it.
- **Modules:** `runtime/model_factory.py` (from `H1-06`), `runtime/model_selection.py`,
  `runtime/root.py:148`, `runtime/bootstrap.py:129`.
- **Depends on:** `H1-06`, `H2-03`.
- **Acceptance:** exactly one `OpenRouterModel(` construction site in `vanguard/packages/runtime/`;
  routing/fallback behaviour unchanged (`test/runtime/test_w14_model_ports_and_driver.py` passes).
- **Type:** structure. **Risk: M.**

### `H2-05` — Unify manifest resolution
- **Outcome:** `agency/manifests/loader.py` is the sole path normaliser.
- **Modules:** `runtime/compose.py:344` (delete `_manifest_file`), `runtime/cli.py:106`.
- **Depends on:** `H2-03`.
- **Acceptance:** one normalisation implementation; all 8 manifests still compose with **identical
  digests**; `test/agency/test_manifest_loader.py` passes.
- **Type:** structure. **Risk: L.**

### `H2-06` — Extract `service/service.py` (1,343 LOC)
- **Outcome:** command handlers separated from transport and store lifecycle.
- **Modules:** `runtime/service/service.py` → `service/commands/*.py`, `service/transport.py`.
- **Depends on:** `H2-02`. **Acceptance:** wire contract unchanged
  (`test/runtime/test_service_contract*`); no file > 500 LOC. **Type:** structure. **Risk: L.**

### `H2-07` — Remove residual `:memory:` branches
- **Outcome:** `bootstrap.py:88`'s unreachable branch and `lab_driver.py:206` cleaned up.
- **Depends on:** `H1-05`. **Acceptance:** every remaining `:memory:` in `vanguard/packages/` is
  either test-only or explicitly requested. **Type:** structure. **Risk: L.**

### `H2-08` — Transactional sequence allocation *(conditional)*
- **Outcome:** concurrent same-project writers become correct rather than merely safe.
- **Modules:** `adapters/stores/event_store.py`.
- **Depends on:** `H1-17`, **and a concrete consumer requiring it.**
- **Change:** allocate `seq` inside the SQLite transaction.
- **Acceptance:** the §11.6 two-thread reproduction succeeds with strictly monotonic `seq`; no
  throughput regression against `H1-18`.
- **Type:** **behaviour**. **Risk: H** — touches the causal-ordering invariant.
- **Non-goals:** **do not do this speculatively.** Fail-closed (`H1-17`) is sufficient until a
  consumer exists. Listed for completeness, deliberately gated.

### `H2-09` — Orthogonal configuration model
- **Outcome:** §9.4's axes are directly configurable; presets become named bundles over them.
- **Modules:** `runtime/profiles.py`, `runtime/bootstrap.py` (`overrides` already exists).
- **Depends on:** `H1-02`, `H1-03`.
- **Change:** capture, durability, evaluation, retention and control become independently
  overridable. `profile.digest` covers the *effective resolved* configuration, so identity stays
  honest. Default cheap capture **on** everywhere; only cost is opt-in — fixing the `product`/`local`
  information-loss defect (§9.2).
- **Tests:** new `test/runtime/test_profile_axes.py` — every axis varies independently and changes
  the digest.
- **Acceptance:** the four presets resolve to today's exact configurations (digest-identical);
  capture can be raised on `local` without changing isolation.
- **Type:** **behaviour** (defaults change). **Risk: M.** **ADR required:** yes (profile identity).

### `H2-10` — Collapse the execution boards
- **Outcome:** one state document; traceability retained (§10.5).
- **Modules:** `docs/03_execution/*`, `tools/linters/check_execution_truth.py`,
  `check_doc_budgets.py`.
- **Depends on:** `H1-01`, `H1-11`.
- **Acceptance:** package state appears in exactly one file; the drift class of `H1-01` is
  structurally impossible; document count under `docs/03_execution/` reduced without losing any
  stable contract.
- **Type:** structure. **Risk: L.**

### `H2-11` — Relax the ADR policy
- **Outcome:** §10.6's policy is codified.
- **Modules:** new ADR; `CONTRIBUTING.md`; `check_core_changes.py`.
- **Acceptance:** adding a tool/pack/manifest/evaluator/CLI command requires no ADR; changing kernel
  neutrality, causal integrity, budget conservation, replay semantics, transport equivalence or
  settlement still does, mechanically enforced by `check_core_changes.py`.
- **Type:** structure (process). **Risk: L.**

### 13.1 The simplified public mental model

After Horizon 2 the documented model is five stages:

```
Observe → Decide → Authorize → Execute → Record
```

mapping onto what already exists:

| Stage | Implementation |
|---|---|
| **Observe** | `ContextCompiler.compile` + `EnvironmentPort.observe` |
| **Decide** | `ModelPort.propose` (or any `IPlanner`) |
| **Authorize** | Kernel S0–S12 — *retains its internal stages; they are simply not the public model* |
| **Execute** | `BindingResolver` → `EffectBinding` → `EnvironmentPort.apply` |
| **Record** | `LedgerEmitter` → event store → projections/recovery |

The kernel keeps its thirteen internal stages. The public vocabulary shrinks to five. That is a
documentation change enabled by the consolidation, not a code change — and it is the honest
simplification, because it describes what the system actually does.

### 13.2 Creating new agents without kernel changes — the target workflow

After Horizon 2, a new Vanguard-native agent should require **no Python in `kernel/`, `domain/`,
`agency/` or `runtime/`**:

1. **Manifest** (`manifest.json`) — components, capabilities, evaluators, budget policy.
2. **Tool schemas** (`*-tool.json`) — name, canonical verb, JSON schema.
3. **Aliases** (`aliases.json`) — model-facing names → canonical verbs.
4. **Prompt** (`system-prompt.txt`).
5. **Policies** — context / routing / approval / retrieval, as JSON.
6. **Skill cards** (optional).
7. **Registration** — one row in `registry.json`.
8. **New domain only:** one `EnvironmentPort` adapter + one `BindingProvider` in `adapters/`.

Steps 1–7 are pure configuration and already work — `vg-code-explain` is the existence proof
(§6.10). Step 8 is the only code, it lives entirely in `adapters/`, and `H1-15` makes `TableWorld`
the worked example of it. **That is the substrate claim, made concrete and testable.**

### 13.3 Which prior-prototype ideas deserve later work

Per the brief's classification table. Nothing here is scheduled; each needs a measurable
product-value hypothesis first.

| Proposal | Existing capability | Verified gap | Required for beta | Post-beta experiment | Reject |
|---|---|---|---|---|---|
| **Bidirectional PTY streaming** | `proc.exec` via `RootlessSandboxRunner`; no PTY anywhere (grep confirms) | No — M-4 produced a real repair without it | **No** | Only if an interactive-tool workflow is prioritised | — |
| **CoW snapshot / fork** | `fork/read/merge` topology proven (M-7); Git-backed workspace | Workspace-level CoW absent | No | ✅ if parallel topologies are enabled | — |
| **Tree-Sitter preflight** | None | Yes | No | ✅ — cheap, plausible patch-validity gain; measure patch reject rate first | — |
| **Improved compaction** | `ContextCompiler` with breakpoint ceiling (4) + `IContextManager.compact` | Only one strategy, not injectable (§4.10) | No | ✅ once a second strategy exists | — |
| **Taint policies** | Capability attenuation, selectors, `confidentiality`/`trainability` columns | Partial — no dataflow taint | No | ✅ | — |
| **SBFL** | `packs/code-default/oracles` | Yes | No | ✅ — needs a failure corpus first | — |
| **Differential testing** | `paired_evaluation.py`, CRN/McNemar (M-6.5) | Substrate exists | No | ✅ — cheapest next study | — |
| **Mutation testing** | None | Yes | No | ✅ **as an optional evaluator**, never on the product path | — |
| **MCTS** | Topology + budgets could express it | Yes | No | ⚠️ only with a measured baseline to beat | — |
| **CEGIS** | `formal-sat`, `formal-graph-coloring` packs | Yes | No | — | ❌ **Reject** for this product line: no near-term consumer; belongs in the formal packs if anywhere |

Two additional answers the brief asks for directly:

- **Duplicate publication/serialisation/bootstrap/governance in the hot path?** Yes, one, and it is
  measured: 80% of events are plugin ceremony (§11.3), plus fsync-per-event (§11.4). No duplicate
  *serialisation* or duplicate *event publication* was found — each event is constructed and written
  once.
- **Prefix stability and replaceable compaction?** Prefix stability is implemented
  (`agency/context/layers.py`, `discovery.py`'s explicit "without breaking prefix stability", and a
  4-breakpoint cache ceiling). Compaction is *declared* replaceable via `IContextManager.compact`
  but is not injectable at runtime (§4.10). Sufficient for beta; genuinely replaceable only after
  `H2` and only when a second strategy exists.

---

## 14. Risks, rollback points and acceptance criteria

### 14.1 Principal risks

| ID | Risk | Likelihood | Impact | Mitigation | Rollback |
|---|---|---|---|---|---|
| R-01 | `H1-02` group commit breaks settlement or replay | Medium | **High** | Digest-equality tests across modes; re-run all falsifiers; re-verify all bundles | `durability.commit: per-event` restores exact current behaviour — the config key *is* the rollback |
| R-02 | `H1-03` lifecycle summary invalidates evidence bundles | Medium | **High** | `full` mode is byte-identical; evidence runs pin `full` | Set `capture.lifecycle: full` |
| R-03 | `H1-09`'s real crash test exposes latent recovery bugs | **High** | Medium | Expected and desirable — better found now | Fix the bug; never weaken the test |
| R-04 | `H1-07` packaging move breaks resource resolution | Medium | Medium | `importlib.resources`; installed-wheel test | Revert `pyproject.toml`; single commit |
| R-05 | `H1-15` TableWorld adapter leaks domain into shared layers | Low | **High** | `check_kernel_neutrality.py` + `check_domain_blindness.py` + `check_boundaries.py` in CI | Revert one adapter file |
| R-06 | `H2-02` session extraction changes semantics | Medium | **High** | Byte-identical digest criterion | Revert; re-exports keep the import surface stable |
| R-07 | `H2-01` `execute_harness` removal breaks a falsifier | Medium | Medium | Migrate `child_runtime.py` first; one test file per commit | Per-commit revert |
| R-08 | Scope creep into SOTA work during Horizon 1 | **High** | **High** | The non-goals in §12 are explicit and enumerated | Governance, not code |
| R-09 | Version bump to `0.9.0b1` implies unearned stability | Low | Medium | `b1` is a beta marker; `README` states known limits | — |
| R-10 | Multi-agent shared-ledger limit surprises a user | Medium | Medium | `H1-17` typed error + documentation | — |

### 14.2 Rollback points

| Point | After | Rollback granularity |
|---|---|---|
| **RP-0** | `H1-01` | Green tree restored; documentation-only revert |
| **RP-1** | `H1-05` | Wave 0 complete; each task independently revertible |
| **RP-2** | `H1-13` | Product surface complete; all additive |
| **RP-3** | `H1-17` | Workflows complete; adapter-level revert |
| **RP-4** | `H1-22` | **Beta frozen — the Horizon 2 rollback target** |
| **RP-5** | `H2-05` | Consolidation complete; digest-verified |
| **RP-6** | `H2-11` | `0.9.1` |

**RP-4 is the critical one.** Horizon 2 must not begin until the beta artifact is frozen and
tagged, because it is the only baseline against which "the refactor changed nothing" can be proven.

### 14.3 Global acceptance criteria

**Horizon 1 (`0.9.0b1`)** — the nine gates of `H1-22`, plus:

| Criterion | Threshold | Source |
|---|---|---|
| Suite | 0 failed | §2.2 |
| Linters | 24/24 pass | §2.4 |
| Kernel TCB | ≤ 1,438 logical LOC | §2.4 |
| Boundaries | ≥ 414 files clean | §2.4 |
| Episode overhead (durable) | ≤ 220 ms | §11.8 |
| Events per 2-receipt episode | ≤ 30 | §11.8 |
| Ledger per episode | ≤ 50 KB | §11.8 |
| Append throughput | ≥ 3,500 ev/s | §11.8 |
| Offline vertical slice | passes from installed wheel | §12 `H1-22` |
| Reference workflows | 2 executing + 1 non-coding domain | §6.10 |
| Evidence bundles | M-4/M-6/M-6.5/M-7/M-8 still `passed` | §3.2 |

**Horizon 2 (`0.9.1`)**:

| Criterion | Threshold |
|---|---|
| Composition + trajectory digests | **byte-identical** to `0.9.0b1` on the `H1-18` fixture |
| Performance | no regression vs §11.8 |
| Composition entrypoints | 1 public (`execute_profiled`) |
| Model construction sites | 1 |
| Manifest normalisers | 1 |
| Largest runtime module | ≤ 550 LOC |
| Kernel | **unchanged** |
| Evidence bundles | all still `passed` |
| Public mental model | 5 stages, documented |

---

## 15. Final recommendation

### **PRESERVE and SIMPLIFY. Do not archive. Do not rewrite.**

The brief requires proving the foundation irrecoverable before recommending a rewrite. The evidence
runs decisively the other way:

| Evidence for preservation | Measurement |
|---|---|
| Kernel is small and domain-blind | 1,373 logical LOC / 9 files; RF-98 and domain-blindness both `PASS` |
| Hexagonal boundaries hold | 414 files clean |
| Event contracts are convergent | 63 = 63, both directions empty, codegen-maintained |
| The suite is real | 2,152 tests, 39,573 subtests, 1 documentary failure |
| Evidence verification is discriminating | 6/16 bundles pass; it rejects claims its own producers made |
| Five milestones technically verified | M-4, M-6, M-6.5, M-7, M-8 all `passed` under independent re-derivation |
| Recursion, topology, memory, rollback all work | depth 3 + kill-tree; 3 topologies with CAS flow; signed rollback |
| Framework overhead is sub-second | 237 ms in-memory; 387 ms durable |
| Recovery is cheap | 55,000 events/s cold replay |
| Packaging works | wheel builds, installs, runs outside the checkout |
| A second workflow already runs | `vg-code-explain`, proven in this audit |
| Multi-domain binding layer is correct | `table.read`/`table.patch` resolve properly |
| Authority separation is enforced mechanically | `PRIVILEGED_KIND_OWNERS`; "plugins propose, they never append" |

Against that, the problems found are: one stale document, one documentary drift failing the suite,
two hot-path implementation defects with measured costs and clear fixes, four missing CLI commands
over machinery that already exists, one incomplete adapter (eight methods on one file), and a
handful of duplicated construction sites. **Not one of these is architectural.** A rewrite would
discard verified invariants — the expensive part — in order to fix a fsync granularity and an
argument parser.

### What must be true for this recommendation to hold

1. **The beta ships before the refactor.** Horizon 2's entire acceptance mechanism is digest
   equality against a frozen `0.9.0b1`. Refactoring first destroys the ability to prove the refactor
   safe.
2. **The two hot-path fixes land with their config escapes.** `durability.commit: per-event` and
   `capture.lifecycle: full` must reproduce today's behaviour exactly, or the evidence bundles
   become unreproducible and the audit trail breaks.
3. **`H1-15` is not skipped.** Without it, "universal substrate" remains a claim. With it, it is a
   test. It is one file.
4. **The non-goals are enforced.** R-08 (scope creep into SOTA work) is rated the highest-likelihood
   risk in this plan, and it is the one that has plausibly cost this project the most time already —
   the archive contains substantial prototype and research material for MCTS, CEGIS, SBFL and
   frontier-benchmark work, while `vanguard status` does not exist.

### The honest one-paragraph summary

Vanguard is a well-built event-sourced agent substrate whose engine is in better condition than its
documentation, whose product surface is thinner than its engine, and whose main performance problem
is 80% ceremony events written one fsync at a time. It has one working coding workflow, a second
workflow that works but nobody registered, and a third that needs eight methods on one adapter to
make its central architectural claim true. Finish those, add four read-only CLI commands and an
offline model, fix the drifting document that is currently failing its own build, and it is a beta.
Then — and only then — consolidate the three entrypoints, the six model factories and the
1,400-line session module, using the beta's digests to prove nothing changed.

---

## Ordered action list — what to do next

Strictly ordered. Each item is a stopping point.

| # | Action | Task | Why first |
|---|---|---|---|
| 1 | Fix `backlog.md` ↔ `sprint_active.md` drift; get the suite to 0 failures | `H1-01` | Nothing else should be judged against a red tree |
| 2 | Document `pip install -e '.[dev]'`; make `.venv` able to run the suite | `H1-21` | Contributors currently cannot reproduce anything |
| 3 | Archive `VANGUARD_BACKEND_M1_M9_MASTER_REPORT.md` | `H1-20` | 10 of 15 claims falsified; it is actively misleading |
| 4 | Set `0.9.0b1` in one place; fix `service.py:379` | `H1-04` | Everything downstream references the version |
| 5 | Implement group-commit (`durability.commit`) | `H1-02` | Largest measured win: ~139 ms/episode |
| 6 | Implement `capture.lifecycle: summary` | `H1-03` | Removes 80% of events; do it with (5) and re-verify bundles once |
| 7 | Re-run all evidence bundles; confirm 6/16 still `passed` | — | Gate before touching anything else |
| 8 | Add `ModelFactory` + `--model-adapter fake` | `H1-06` | Unblocks every offline test below |
| 9 | Add `status`, `events`, `artifacts` | `H1-08` | Thin projections; makes the beta inspectable |
| 10 | Add `resume` + the real SIGKILL test | `H1-09` | Completes the vertical slice; expect to find bugs |
| 11 | Typed environment-contract error | `H1-16` | Prerequisite for (12) |
| 12 | Implement `TableWorldEnvironment` as `EnvironmentPort`; register it | `H1-15` | Makes the substrate claim true and closes drift D-27 |
| 13 | Register + E2E-test `vg-code-explain` | `H1-14` | Nearly free; second reference workflow |
| 14 | Remaining beta items | `H1-05,07,10,11,12,13,17,19` | Parallelisable |
| 15 | Freeze benchmarks as regression thresholds | `H1-18` | The Horizon 2 baseline |
| 16 | **Freeze `0.9.0b1`** | `H1-22` | **Rollback point RP-4** |
| 17 | *Only then* begin Horizon 2 | `H2-01` … | Digest equality requires a frozen baseline |

**Do not start item 17 before item 16 is complete.**

---

*End of report.*
