# Part V — Execution Roadmap

Six sprints. Every item names its file, its acceptance evidence, and its falsifier. Nothing in
Sprints 1–4 touches `kernel/`.

**The governing rule for the whole plan:** *no item is complete until a falsifier proves the control
can fail, and no capability claim is made without a suite row.* This is the repository's own
discipline (`README.md` §10: "A gate that cannot fail is not a gate"), applied to the plan itself.

---

## Sprint 0 — Freeze and admit (2 days, do first)

Nothing else is trustworthy until the evidence surface stops lying by shape. This is D7 and it is
the cheapest item in the review.

| # | Item | Acceptance |
|---|---|---|
| 0.1 | Add `n`, `suite_size`, `suite_digest`, `provenance`, `model_real`, `cost_provenance` to the results schema | schema committed; JSON Schema under `schemas/` |
| 0.2 | Runner refuses to write `pass_rate_pct` when `n < suite_size` | falsifier: writer raises on an n=1 rate |
| 0.3 | Any aggregate containing `model_real: false` emits `undeterminable`, never a number | falsifier: LAM row poisons the aggregate |
| 0.4 | Relabel `agentic_matrix_benchmark_results.json` rows `provenance: "cassette"` | file no longer readable as capability |
| 0.5 | Move ~50 n=1 `report_*.json` to `benchmarks/_archive/logs/`; document that they are logs | `benchmarks/` aggregate is meaningful |
| 0.6 | `.gitignore` `dist/`, `node_modules/`, `.venv`; delete `write a function/` | tree is clean |
| 0.7 | **State the current honest number in one line in the README** | e.g. "measured coding pass rate: undetermined; last valid multi-task run 10/10 easy (`report_easy_v3`, n=10, deepseek-v4-flash)" |

**Sprint 0 falsifier:** attempt to commit a `pass_rate_pct` computed over one task. CI must reject.

0.7 matters more than it looks. The README currently presents an 11-row capability table where most
rows read "Works." A single honest number at the top is worth more than the table, and it makes
every subsequent sprint's improvement visible.

---

## Sprint 1 — Capability (2 weeks) ◀ **the sprint that moves the number**

### 1a. Edit primitive (highest single ROI in the review)

| # | Item | File | Acceptance / falsifier |
|---|---|---|---|
| 1.1 | `str_replace(path, old, new)`, unique-match-or-fail | `adapters/tools/edit.py` | 0 matches → rejection; >1 → rejection naming the count; 1 → applied |
| 1.2 | `multi_edit(path, edits[])`, atomic | same | falsifier: hunk 3 of 4 fails ⇒ **no** write occurs |
| 1.3 | Parse-preflight before commit for parseable languages | `adapters/tools/edit.py` | falsifier: syntactically broken result is rejected, file unchanged |
| 1.4 | Register in `SinkRegistry` as `privileged`; selector-scoped | `kernel/classifier.py` registration site (no kernel logic change) | boundary + domain-blindness linters green |
| 1.5 | Prompt: `str_replace` is the default, with one worked example | `packs/*/system-prompt.txt` | — |
| 1.6 | Retain unified diff as accepted input; delete `resilient_patcher.py` | `agency/forge/` | suite pass rate does not regress |

**Expected effect:** most of `NO_PATCH` 123 and `malformed` 81.

### 1b. Orientation

| # | Item | Acceptance |
|---|---|---|
| 1.7 | `glob(pattern)` | observation sink; gitignore-aware |
| 1.8 | `list(path, depth)` | observation sink; bounded output |
| 1.9 | `grep` backed by ripgrep; `--glob`, context lines, **hits capped per file** with explicit elision | falsifier: 500-hit pattern returns bounded output |
| 1.10 | `read(path, offset, limit)` | large file readable in windows |
| 1.11 | Delete "There is no directory-listing tool" and the other apology lines | prompt shrinks measurably |

### 1c. Execution

| # | Item | Acceptance / falsifier |
|---|---|---|
| 1.12 | `bash(cmd, timeout)` — real shell inside bubblewrap | privileged, descriptor-bound, selector-scoped to workspace |
| 1.13 | Argv allowlist demoted to an opt-in `hermetic` profile | falsifier: `hermetic` profile denies `curl`; `local` permits `ls` |
| 1.14 | `bash_bg` + `poll` + `kill` | a dev server can be started, polled, killed within one episode |
| 1.15 | Falsifier: escape attempts (`../`, `/etc/passwd`, symlink, `$HOME`) all denied | **required before merge** |

1.15 is not optional. Widening `proc.exec` to a shell is the only change in this plan that expands
the attack surface, and it must land with its perimeter test in the same commit.

### 1d. Termination and throughput

| # | Item | Acceptance |
|---|---|---|
| 1.16 | `AdmissionGate` is the sole termination control: `workspace_digest` changed ∧ `VerificationReceipt.passed` | falsifier: "completed" with `before == after` is refused, feedback returned |
| 1.17 | **Delete `derive_phase` and the phase allowlists** | test asserting `proc.exec` is reachable at turn 1 |
| 1.18 | `finish(summary)` present in **every** preset | audit: 0 presets lack it |
| 1.19 | Parallel dispatch of disjoint observation effects | falsifier: 2 writes to one path serialise; 5 reads run concurrently |
| 1.20 | Delete "Exactly ONE tool call per turn" | turns-per-task drops on the suite |

**Sprint 1 gate.** `NO_PATCH` rate on 10 brownfield tasks < 20%, and turn distribution has mass
above 1. If either fails, do not proceed — diagnose. (This is the peer audit's F2 question, now
answerable.)

---

## Sprint 2 — Retrieval and economy (1.5 weeks)

### 2a. Wire the index (D2)

| # | Item | File | Acceptance |
|---|---|---|---|
| 2.1 | `LdaRepoIndex(IndexPort)` over `.lda/index.db` | `adapters/stores/lda_index.py` | port unchanged; `FileRepoIndex` retained as fallback |
| 2.2 | `RepositoryMap` carries `source_revision`, `tree_hash`, `index_digest`, `truncated` | same | falsifier: stale index ⇒ explicit degraded mode, **never a silent map** (T-45) |
| 2.3 | Expose `symbol`, `refs`, `defs`, `callers`, `imports`, `covering_tests` as verbs | `adapters/tools/index.py` | observation sinks |
| 2.4 | Incremental re-index of changed paths + reverse-dependency closure | | falsifier: post-write compile never sees a pre-write map (T-16) |
| 2.5 | Wire `ast_grep_adapter.py` as `ast_patch` | `adapters/tools/ast.py` | rename-symbol across 3 files in one call |
| 2.6 | Epoch-bind the index digest into `WorkspaceEpoch` | `runtime/session.py` | stale packet cannot complete (extends `587db91a`) |

**Falsifier for 2.3:** a localisation task solvable in ≤4 tool calls via `covering_tests → symbol →
refs`, which requires >15 calls with grep alone. Add it to the suite.

### 2b. Claim the cache (D3) — **in this order**

| # | Item | Acceptance |
|---|---|---|
| 2.7 | **Prefix-stability regression test first** — rendered `PREFIX_LAYERS` digest byte-identical across all turns | test fails today if `_schemas_with_aliases` drifts |
| 2.8 | Audit and fix `_schemas_with_aliases` determinism (`compose.py:506,524`) | 2.7 green |
| 2.9 | Extend `ContextBundle` to carry breakpoint positions across `ModelPort` | domain change; ports updated |
| 2.10 | Emit `cache_control` in `openrouter.py` | `cached_tokens > 0` on turn 2+ |
| 2.11 | Report `tokens_prefix` / `tokens_cached` / `tokens_volatile` separately | cache regressions visible in ordinary output |
| 2.12 | Fix cost provenance — no more `cost_usd: null` on live rows | `cost_provenance: "metered"` |

2.7 before 2.10 is not stylistic. A breakpoint on a drifting prefix costs the write and never hits.

### 2c. Distillation (P1)

| # | Item | Acceptance |
|---|---|---|
| 2.13 | `ResultDistiller` port; applied at the effect→`Block` boundary | before `CompactionStrategy` ever runs |
| 2.14 | Pytest distiller reusing `forge/engine.py:parse_test_output` | 1,200 → ~180 tokens; failing test ids and assertion preserved |
| 2.15 | `read` skeletoniser (signatures + docstring heads + line numbers) | 3,000 → ~400 |
| 2.16 | `grep` and `git diff` distillers | capped, deduped |
| 2.17 | `expand(digest)` verb — **never destroy, always address** | falsifier: full traceback retrievable after distillation |
| 2.18 | `distillation-policy.json` per pack; conservative default for unknown verbs | A/B-able |

**Sprint 2 gate.** Same 10 tasks: tokens/task down ≥50%, `cached_tokens` non-zero, pass rate not
regressed.

---

## Sprint 3 — The instrument (1 week) ◀ **makes everything after this decidable**

| # | Item | Acceptance |
|---|---|---|
| 3.1 | Freeze the suite: 44 tasks, content-addressed, committed, `suite_digest` pinned | composition per Part 3 §14.2, including 6 adversarial/trap tasks |
| 3.2 | One runner, `benchmarks/results.jsonl`, append-only, Sprint-0 schema | one file; a new `*_report.json` fails lint |
| 3.3 | `bench compare A B` — paired McNemar via existing `statistics.py` / `paired_evaluation.py` | p-value + per-task deltas |
| 3.4 | `bench report` — rate table by class, with `undeterminable` where warranted | — |
| 3.5 | **Capability-ceiling run**: frozen suite, best available model, generous output budget, no phase gate | this is the harness's real quality; the cheap-model number is its *economy* |
| 3.6 | **Run all 32 manifests once. Delete the losers.** | ≤3 presets survive; deletion justified by a `results.jsonl` query |
| 3.7 | Collapse to one engine and one patcher | `agency/` ≤ 3,000 LOC; suite does not regress |
| 3.8 | Manifest `extends`/`overrides` + `shared/tools/` | a preset's diff is its hypothesis |

3.5 and 3.6 are the two items that retire D5 permanently. 3.6 in particular is the moment the sprawl
becomes cheap to delete, because the data does the deleting.

**Sprint 3 gate.** `bench compare` produces a p-value on real paired data. Publish the number
whatever it is.

---

## Sprint 4 — Long-horizon reliability (1.5 weeks)

| # | Item | Acceptance |
|---|---|---|
| 4.1 | Working-set header pinned in `L4`, regenerated per turn (~80 tok) | goal · changed · verified · **rejected** · next · budget |
| 4.2 | `falsified` projection from the ledger — `patch.apply` + non-zero receipt + `FailureFingerprint` | derived, **never model-self-reported** |
| 4.3 | Summarise-on-compact replacing elide-to-receipt | same token cost, carries the finding, stays addressable |
| 4.4 | Emit `ContextCompacted` with input/output digests + compactor identity | `schemas/mhf/context_compacted.schema.json` already exists; `VISION.md` Ch. 17 satisfied |
| 4.5 | Rolling handoff at ~70% budget; brief copied **verbatim**; `changed`/`verified` from the ledger | falsifier: a 60-turn task completes across ≥2 windows in one lineage |
| 4.6 | Load repo `AGENTS.md`/`CLAUDE.md` into `L3` | project conventions become stated constraints |
| 4.7 | Sub-agent for context isolation: `spawn` with a narrow tool set, value-only return | falsifier: child burns >20k tokens, parent context grows <1k |
| 4.8 | `todo_write` pinned in `L4` | greenfield multi-file decomposition before action |
| 4.9 | Tool-result cache keyed `(verb, args_digest, workspace_epoch)` | re-read of unchanged file costs no round trip |

**Sprint 4 gate.** The 5 long-horizon tasks and 6 greenfield multi-file tasks pass at a materially
higher rate than at the Sprint 3 baseline, with a paired comparison to prove it.

---

## Sprint 5 — Supervision (1 week)

| # | Item | Acceptance |
|---|---|---|
| 5.1 | `ProgressVector` as a pure ledger reducer | `domain/ledger/progress.py`; **zero model calls**; unit-testable on recorded ledgers |
| 5.2 | Supervisor process tailing the ledger, appending `orch.intent.*` | falsifier: kill the supervisor mid-run ⇒ episodes complete unaffected |
| 5.3 | **One** pathology: `THRASHING` (`novelty < 0.3` over 3 turns) → one injected nudge | paired A/B on the frozen suite; publish either direction |
| 5.4 | `scope_fidelity` hard stop — write outside declared boundary | falsifier: out-of-scope write halts the episode |
| 5.5 | Budget kill-switch from the supervisor | falsifier: run terminates, partial work preserved |

Only after 5.3 shows a signed effect: add `BLIND`, then `WON_BUT_UNAWARE`. **One pathology at a
time, each with its own A/B.** Eight pathologies shipped together is 64 untested interaction pairs
and no attributable result.

---

## Sprint 6 — Outer loop (2 weeks)

Now the peer corpus's plan runs, on an inner loop worth multiplying.

| # | Item | Maps to |
|---|---|---|
| 6.1 | `orch.*` event contract; same ledger, distinct namespace | peer `ORCH-01` / M-O1 |
| 6.2 | `Planner` — dependency DAG from a backlog-shaped input | `ORCH-02` |
| 6.3 | `Dispatcher` consuming `orch.intent.*` (per Part 3 §11.1, a consumer not an owner) | `ORCH-03`, amended |
| 6.4 | `SequentialDirector` — the **control condition** | `ORCH-04` / M-O2 |
| 6.5 | `Compactor` reusing Sprint 4's handoff + LDA retrieval — **extend, never fork** | `ORCH-05/06` / M-O3 |
| 6.6 | Exterior package-granularity `Verifier` | `ORCH-07` |
| 6.7 | `ApprovalPolicy` as data (`interactive`/`autonomous`/`hybrid`) over existing `approvals.py` | `ORCH-08` |
| 6.8 | `DirectorObserver` — compacted evidence only, **no write tools** | `ORCH-09` / M-O4 |
| 6.9 | `find_dead_ends` / `find_bottlenecks` as pure folds | `ORCH-11` |

`ORCH-10` (evolutionary) stays last and opt-in, only on packages with a numeric evaluator — as the
peer report itself specifies.

**Sprint 6 gate.** A 5-package roadmap completes with zero manual board edits, and `bench compare
sequential director` produces a paired result.

---

## Deferred until the instrument exists

| Item | Why deferred |
|---|---|
| Topologies / `M-7` | Part 3 §12.2. Build one only when a measured suite failure is attributable to its absence. Apply `ADR-0092`'s implement/simplify/cancel discipline to `M-7` itself. |
| Skill promotion / learning engine | `skill_evaluation.py` and `governance/learning.py` are built but **unfed**. A promotion decided on n=1 is worse than no promotion. Needs Sprint 3. |
| Embeddings / vector memory | Part 3 §6.1. You have a 77,610-edge graph; a vector store is a downgrade. |
| Web search in the coding pack | Real value, but introduces untrusted content into a carefully-built provenance model. Its own pack, deliberately, later. |
| Official SWE-bench | Correctly already firewalled as a separate preregistered programme. Do not touch before Sprint 3. |
| Documentation rewrite | Sprint 7. Write it **after** the numbers move, so it describes something true. |

---

## Sprint 7 — Documentation, last

Deliberately last, and this ordering is the point.

| # | Item | Target |
|---|---|---|
| 7.1 | `VISION.md` rewritten **in English** | ~1,200 lines; keep Ch. 4, 7, 15, 17, 18 substance; drop the constitutional apparatus |
| 7.2 | `README.md` | ~200 lines; one honest capability number at the top |
| 7.3 | `docs/execution/spec.md` remains the sole normative surface | keep RFC-2119 obligations, invariants, falsifier IDs |
| 7.4 | Delete ~40,000 lines of governance ceremony; keep the `check_*` linters | executable law survives; prose law shrinks |
| 7.5 | Collapse entry points to `just check · verify · bench · run · docs` | one canonical path per action |

---

## Summary

| Sprint | Duration | Delivers | Kernel change |
|---|---|---|---|
| 0 | 2 days | evidence that cannot lie by shape | none |
| 1 | 2 weeks | **the capability surface** | none |
| 2 | 1.5 weeks | retrieval + cache + distillation | none |
| 3 | 1 week | **the instrument**; sprawl deleted by data | none |
| 4 | 1.5 weeks | long-horizon reliability | none |
| 5 | 1 week | decoupled supervision | none |
| 6 | 2 weeks | outer loop / roadmap delivery | none |
| 7 | 3 days | documentation that describes reality | none |

**Critical path to a working coding agent: Sprints 0–3, approximately five weeks.**

Everything in Sprints 0–4 is wiring components that already exist: the ports are defined, the index
is built, the statistics are implemented, the sandbox works, the compiler is correct, the schemas
are written. The work is connection, not invention — which is why five weeks is a realistic number
for a project that has spent months on architecture.
