# 007 — Codebase Cleanup, Deduplication & Documentation Consolidation

**Status:** NON-NORMATIVE. Where this file and a v4 owner disagree, the owner wins (`PR-3`).
**Date:** 2026-08-16 · **Branch/HEAD:** `sprints7-8/integration` @ `0238b1a`
**Owns:** the concrete delete / merge / relocate list for code and documentation, and the
process fix that stops review documents accumulating faster than remediation.
**Authority cited:** `VG-00` (registry, precedence, retirement protocol), `VG-01` handbook,
`VG-03 §4` layer contracts, `GTS-13C` Ch. 14, `T10.1`, `T10.4`.

---

## 1. The shape of the problem

| Corpus | Lines | Assessment |
|---|---|---|
| Normative v4 set (`docs/main_v4/`, 16 files) | 4,928 | **Excellent. Keep. Amend two statements** |
| Runtime (`vanguard/packages/`) | 15,569 | Sound core, three parallel loops, one god function |
| Tests (`test/`) | 12,199 | Strong doctrine; three red; one suite correctly refusing |
| **Review + plan documents** (`docs/reviews/done/` + `docs/reviews/done/`) | **5,494** | **Larger than the specification it reviews. Ten NO-GO verdicts, none closed** |
| Agile artifacts (`docs/scrum/sprints/`) | ~1,300 | Sprint-local; retire on sprint close |
| `todo_list.md` | ~25,000 chars | A second, unregistered programme plan at repo root |

**The signal:** 5,494 lines of review against 4,928 lines of specification, with zero closures.
`GTS-13C` Ch. 14 lists "specification capture" as a standing risk with the early signal *"new
normative rules outpace tests."* The realised variant is worse and unlisted: **review output
outpaces remediation.** A team that reviews instead of deciding produces exactly this artifact
profile, and every additional review lowers the marginal value of the next one.

This document (and its siblings 001–008) is itself part of that risk. §5 is the protocol that
prevents it from becoming the eleventh unactioned audit.

---

## 2. Code: delete

Ordered by value. Every item is a **deletion**, and every deletion is safe because the tests that
cover it either cover a bypass path or are deleted with it.

| # | Path | LOC | Reason | Replacement |
|---|---|---|---|---|
| D1 | `vanguard/packages/runtime/loops/` | 144 | Second agent loop; bypasses kernel, sandbox and exterior judge; self-grades; `NameError` on the default path (`001 §3.1`) | Compaction → `ContextCompiler` strategy; retry → the loop itself; tier escalation → `routing_policy` |
| D2 | `test/runtime/test_meta_loop.py` | ~50 | Tests D1; passes only because it injects `test_runner`, masking the `NameError` | — |
| D3 | `vanguard/packages/runtime/coordination.py` | 171 | Second budget and coordination ledger outside the event store (`003 §4`) | Depth as a projection over ledger events in `runtime/ledger/projections.py` |
| D4 | `benchmarkings/swe_pro_tiers/runner.py` | ~350 | Reimplements the episode loop incl. a regex tool-call parser; imports adapters directly | `zero_hint_v1/run_live_agent.py` (uses `Runtime.execute_harness`) |
| D5 | `benchmarkings/swe_pro_tiers/run_matrix_evaluation.py` | ~300 | Same, plus `MANIFEST_DIR` declared and unused while claiming to evaluate manifests (`002 §2.2`) | `vg harness bench` over the honest instrument (`005` H10) |
| D6 | `benchmarkings/run_agentic_live_challenge.py` | ~250 | Same bypass | as D4 |
| D7 | `benchmarkings/run_live_proof.py` | ~200 | Same bypass; imports a loose `ladder` module | as D4 |
| D8 | `workflow_visualizer.html` | 48 KB | Orphan of the rejected runtime-graph design (`ADR-0003`). `VG-03 §2.3` keeps graphs as a **post-hoc** rendering — that belongs in the inspector, over ledger events | Trajectory rendering in the inspector, from the ledger |
| D9 | `vanguard/packages/runtime/root.py:429-445` `_WitnessKernel` | 17 | Exists only because `DispatchResult` does not carry the pending request through a suspension | Session holds the pending request (`003 §5.2`) |

**Total: ~1,530 LOC removed, and Q1 ("is the boundary real?") is restored by D1 + D4–D7 alone.**

### 2.1 Retraction, not deletion, for the evidence

Result JSON produced by D4–D7 moves to `benchmarkings/_retracted/` with a `RETRACTION.md`
(`002 §2.2`). Non-degenerate rows move to `benchmarkings/_external_model_probes/` relabelled as
model probes. `VG-02 §11.9` values negative and corrected results; a silent deletion destroys the
audit trail that makes the correction credible.

---

## 3. Code: deduplicate

### 3.1 Three unified-diff engines (~1,400 LOC)

| File | LOC | Method |
|---|---|---|
| `adapters/environment/fake.py` | 642 | `_parse_and_simulate_patch` (line 194) |
| `adapters/environment/git.py` | 762 | `_parse_and_validate_patch` (line 287) |
| `adapters/environment/sandboxed.py` | 261 | delegates to the worker, which has its own |

`VG-03 §7.4`: *"The environment's own diff is the definition of what changed. No second patch
path."* `FT-08` names the second patch path as a failure class. Three parsers with independent
edge-case handling will diverge on hunk-context mismatch, new-file creation, CRLF and rename
detection — and the divergence will present as a fake-vs-real test discrepancy that someone
"fixes" by patching whichever side is red.

**Fix:** one `domain/patch/unified_diff.py` — pure, no I/O, property-tested (parse∘render =
identity; apply∘revert = identity). All three adapters call it. `T10.2` wants a fake and a real
*implementation of a port*; it does not want two implementations of a parser.
**Estimated: −500 LOC, +150 LOC, one property test suite.**

### 3.2 Adapter surface duplication

`fake.py` (642) and `git.py` (762) implement the same nine-method `EnvironmentAdapter` protocol
with substantially parallel structure (`_check_disposed`, profile/snapshot/observe/preview/
apply/reconcile/compensate/dispose). After §3.1 the residue is mostly genuine — a fake and a real
implementation *should* differ. But `_check_disposed`, path resolution and the `Result` plumbing
are mechanical and belong in a shared `adapters/environment/_base.py`.
**Estimated: −200 LOC.**

### 3.3 Kernel construction duplication in `root.py`

Three `Kernel(...)` constructions with identical collaborator lists (`root.py:742`, `:769`, and
the base). Collapses to one under `HarnessSession` (`003 §5.2`).

### 3.4 Evaluator adapter proliferation

`adapters/evaluators/` holds `daemon.py`, `client.py`, `isolated.py`, `fake.py`, `unavailable.py`,
`signing.py` (756 LOC) plus six oracle suites. `unavailable.py` and the deliberate absence of a
`FakeEvaluator` binding are **correct and should stay** — absence must be inconclusive, not a
pass. But `isolated.py` (298) and `client.py` (131) overlap; per
`docs/reviews/done/mvp_beta_delivery_audit_2026-08-16.md` §1.4, `IsolatedEvaluator` is currently
instantiated inside the runtime with an empty oracle and `image_digest="unverified"`. Resolve to
**one** client that talks to the daemon, with attestation required and `inconclusive` when it is
absent.

---

## 4. Code: relocate and fix

| # | Item | Action |
|---|---|---|
| R1 | `/usr/bin/bwrap` literal (`root.py:659`) | Probe via `shutil.which` behind `SandboxRunner`; composition error names the remedy |
| R2 | `approval_required_above="low"` (`root.py:693`) | `approval_policy` manifest component (`005` H7) |
| R3 | `Reservation(usd_micros=100, millis=1000)` (`root.py:775`) | From `budget_policy` |
| R4 | `tokens_used = ... or 100` (`root.py:793`) | **Delete.** Zero is zero; fabricating telemetry is `RSK-04` at source |
| R5 | `"tools/002_LLM_API_MOCK/lam.sqlite"` (`root.py:712`) | Gone with D3 |
| R6 | Bare `except Exception: pass` at `root.py:722`, `root.py:796` | Either justify with a rule citation (as `engine.py:269` correctly does for `F-25`) or let it raise |
| R7 | `_sandbox_effector` (`root.py:506-513`) | The "compatibility binding" comment marks a name that no longer means what it says. Rename or delete the indirection |
| R8 | `tools/` — 20 scripts at one level, mixing CI checks, LLM routers and dogfood runners | Split `tools/ci/`, `tools/lab/`, `tools/providers/`. `tools/001_LLM_API_ROUTER/outputs/` holds 14 committed response artifacts that belong in a gitignored scratch dir |

---

## 5. Documentation: the consolidation

### 5.1 The registry already specifies the answer

`VG-00` owns document precedence, status lifecycle, identifier namespaces, **and a retirement
protocol** (Ch. 11). None of the 5,494 lines of review material is registered under `VG-00` Ch. 2,
and every one of them correctly says so in its own header (*"Not in the registry… where this file
and a v4 owner disagree, the owner wins (`PR-3`)"*). **The discipline is right; the retirement
half was never exercised.**

### 5.2 The three-state model for review documents

Adopt directory-as-state, which the repo already half-implements (`done/`, `todo/`, `doing/`):

| State | Directory | Meaning | Exit |
|---|---|---|---|
| `doing` | `docs/reviews/doing/` | Under active remediation. **Cap: 8 documents.** | Every finding has a ticket or a written rejection |
| `done` | `docs/reviews/done/` | Every finding closed, rejected-with-reason, or promoted into a v4 owner | Immutable |
| — | *(no `todo/`)* | **Abolish it.** A review nobody has scheduled is not a todo, it is an opinion | — |

**Rule:** a new review document may not be created while `doing/` holds 8. This is a WIP limit,
and it is the only mechanism that reliably converts reviewing into deciding.

### 5.3 Per-document rulings — SUPERSEDED BY `009 §2`

> **CORRECTION (2026-08-16).** The rulings below were made from document **headers**, not bodies.
> Reading all 13 in full showed they were wrong in both directions: three documents are stronger
> than the corresponding `001`–`008` report, five are ~90% closed by Sprint 6B, and nine findings
> are still live. **`009 §2` is the authoritative ruling.** The table below is retained only to
> show what the header-level triage got wrong, which is itself the argument for `009`.

| Document | Lines | Ruling |
|---|---|---|
| `sota_harness_scientific_benchmarking_programme_2026-08-16.md` | 836 | **Promote.** Its §0 ruling ("we are cheating in several published-looking numbers") is correct and independently confirmed here (`002`). Its labelling regime should become a `VG-07` amendment — i.e. **normative**, not review material |
| `phases_0-2_review_full_rev2.md` | 982 | **Close.** Extract open findings into tickets; the Beta/GA fence in its §7.1 is good and should survive into `008` |
| `phases_0-2_review_full_rev3.md` | 42 | **Merge into rev2's closure**, then delete both. Three revisions of one audit is a version-control failure, not a document set |
| `BETA-MVP-AUDIT-REPORT.md` | 463 | **Close.** Its seven SOTA properties (§0) are a good checklist; promote them into `VG-01` |
| `mvp_beta_delivery_audit_2026-08-16.md` | 358 | **Close.** Same day, same branch, same NO-GO as the above. Duplicate verdict from a second reviewer — merge the deltas, retire both |
| `phases_review.md` | 407 | **Close.** Superseded by `ADR-0058`, which it produced |
| `vanguard_LAM_manifests_plan_sprint-7-to-9.md` | 749 | **Supersede** by `008`. Its §4 "decision lock" content belongs in the Decision Register as ADRs, not in a review file |
| `vanguard_harness_cli_architectural_review_phase_2.md` + `_REV2.md` | 577 | **Merge into one**, keep. Genuinely valuable: the three-evidence-level model (contrato público / inferência arquitetural / não verificável) and the four-unit separation (produto / harness / modelo / protocolo experimental) are exactly the discipline `002` needs. **Promote that framing into `VG-07`.** Note: written in Portuguese while the corpus is English — pick one language for normative material |
| `vanguard_v042_and_v5_from_harness_src.md` | 465 | **Keep in `doing/`** — forward-looking, not yet actionable |

**Net: 5,035 → ~1,000 lines**, with three genuinely valuable frameworks promoted into the
normative corpus where they will actually bind.

### 5.4 `docs/reviews/done/` (615 lines)

| Document | Ruling |
|---|---|
| `2026-08-16-phase-3-sprints-7-10-blueprint.md` (51) | **Supersede by `008`.** It contradicts locked decisions on five points (`001 §3.13`): a class hierarchy the spec forbids, packages outside the layer lattice, a TUI inside the runtime, `agy` vs `vg`, and a Sprint-10 gate of "tests pass + tag git" against a four-question MVP gate. Q3 and Q4 are absent entirely |
| `2026-08-16-lam-benchmark-corpus.md` (459) | **Keep, subordinate to `002`.** LAM is a gym and cassette factory; it must never produce a published capability number |
| `2026-08-16-harness-dna-pack-improvements.md` (105) | **Merge into `005`** |

### 5.5 `todo_list.md` (25 KB at repo root)

A second, unregistered programme plan competing with `GTS-13C`. `ADR-0046` is explicit:
*"GTS-13C is the sole active programme plan."* `GTS-13C` §"Document map" is explicit:
*"A statement appearing in two of them is a defect in ownership, fixed by deleting the copy, not
by ranking them."*

**Ruling:** move to `docs/scrum/sprints/sprint6B/` as a sprint artifact (which is what it is — its header
says "Sprint 6B MVP Beta"), or convert to issue-tracker rows and delete. It must not live at repo
root where it reads as authoritative.

### 5.6 Two normative amendments required

Both are cases where a NORMATIVE document currently states something false:

1. **`VG-02 §9`** — the approved-stack table says *"Control plane: TypeScript (strict) on
   Node.js LTS."* The control plane is Python. Amend, and reference `ADR-0063` (`006 §1`).
2. **`VG-00 §6`** — the normative rules index must gain rows for any rule promoted from §5.3.

`GTS-13C` T10.7 blocks new normative rules while a contract row is uncovered. These are
**corrections of false statements**, not new rules, so they are admissible — but they must be
recorded as corrections in `VG-09 §4`, which is the section that exists for exactly this.

---

## 6. `.gitignore` and hygiene — and a correction to this section

> **CORRECTION (2026-08-16, via `009 §5`).** This section originally read *"This is in good shape."*
> **That was wrong**, and the error is instructive enough to leave visible rather than overwrite.

**What is right.** `node_modules/`, `dist/`, `__pycache__/`, `*.pyc`, `.env` are ignored and
`git ls-files` returns zero tracked matches. `tools/scan_secrets.py` exists and is wired into CI.

**What is wrong.** `git ls-files` reports **HEAD**, not **history**. Running the project's own tool
in the mode the prior audit explicitly named:

```
$ python3 tools/scan_secrets.py            → SECRET SCAN PASS
$ python3 tools/scan_secrets.py --all-refs → SECRET SCAN FAIL: reachable-object: env-named blob .env
$ git for-each-ref | grep -c refs/original → 21
```

**`SEC-01` is not closed.** A reachable `.env` blob and 21 `refs/original` backup refs remain. The
prior audit (`mvp_beta_delivery_audit` P0-08) said exactly this and was carried as stale.

The generalisable defect is worse than the finding: **the scanner was run only in its passing
mode.** `A-10` — a gate that cannot fail is not a gate — extends to a gate whose failing mode is
never invoked. CI must run `--all-refs`, not the lenient default.

**Remediation is a Joint-track Sprint 7 row** (`011`), sequenced deliberately: revoke/rotate at the
provider **first**; then, with repository-owner authorisation, coordinate a history rewrite across
every affected ref, remove backup refs, force-update the remote, invalidate stale clones, and
verify both `--all-refs` and a clean-clone scan. **Never place the secret value in a ticket,
command line, log or receipt.**

Also open: no `LICENSE` file exists while `pyproject.toml` declares Apache-2.0 (`009 §3.1`).

Remaining hygiene: a `make clean` target for untracked working-tree noise, and adding
`tools/001_LLM_API_ROUTER/outputs/` to `.gitignore` (14 committed provider response artifacts).

---

## 7. The consolidated cleanup backlog

| # | Item | Kind | Effort | Net LOC |
|---|---|---|---|---|
| X1 | D1–D3: delete `runtime/loops/`, its test, `coordination.py` | delete | 1 d | −365 |
| X2 | D4–D7: delete the four bypassing benchmark runners | delete | 0.5 d | −1,100 |
| X3 | Retraction sweep + `RETRACTION.md` + relabel (`002` M3) | process | 1 d | — |
| X4 | D8, D9, R7: orphan HTML, `_WitnessKernel`, `_sandbox_effector` | delete | 0.5 d | −70 |
| X5 | R1–R6: hardcoded values, fabricated telemetry, silent excepts | fix | 1 d | ~0 |
| X6 | §3.1 one unified-diff engine, property-tested | dedup | 3 d | −350 |
| X7 | §3.2 shared adapter base | dedup | 1 d | −200 |
| X8 | §3.4 one evaluator client with required attestation | dedup | 2 d | −150 |
| X9 | R8: `tools/` reorganisation + ignore `outputs/` | tidy | 0.5 d | — |
| X10 | §5.2 three-state review protocol + WIP limit of 8 | process | 0.5 d | — |
| X11 | §5.3 close/merge/promote the ten review documents | docs | 2 d | −4,000 docs |
| X12 | §5.4 supersede the Phase-3 blueprint by `008` | docs | 0.5 d | — |
| X13 | §5.5 relocate `todo_list.md` | docs | 0.5 d | — |
| X14 | §5.6 amend `VG-02 §9`; record corrections in `VG-09 §4` | docs | 0.5 d | — |

**Total: ~14 engineer-days. Net effect: −2,235 runtime LOC, −4,000 documentation lines, three
parallel execution paths reduced to one, and three valuable review frameworks promoted from
opinion to binding.**

X1–X5 are **three days** and are the prerequisite for every other workstream in `008`, because
they are what makes the tree's behaviour match the tree's description.

---

## 8. The rule that prevents recurrence

Every item in §2 exists because a package, a directory or a script was created outside the
enforced import lattice. `T10.1` made `spike/` and `slice/` disposable **by construction**
(`ADR-0047`) — and it worked: the S4 gate deleted them and `MF-S4-001` proved their absence.

**The same mechanism, extended, would have prevented all of §2:**

```
# tools/check_boundaries.py — three rules to add
1. A top-level package under vanguard/packages/ not named in VG-03 §4 (LT-1..LT-8)
   is a build failure.                                    -> would have blocked runtime/loops/
2. benchmarkings/ may import vanguard.packages.runtime.root and vanguard.packages.ports
   only.                                                  -> would have blocked D4-D7
3. subprocess is importable only from adapters/sandbox/.  -> would have blocked the host exec
```

Each ships with a `test/broken/` counterpart that must fail (`T10.3`, `A-10`). **Three rules,
one day, and the class of defect that produced 1,500 lines of deletion becomes unwritable.**

That is the actual lesson of this review: the team's architectural judgement is sound and its
enforcement mechanism is excellent — it was simply never pointed at the new code. Point it there.
