---
id: execution.management.state_of_play
class: execution
authority: descriptive
canonical_for:
  - current-orchestration-state
status: living
owner: repository-governance
version: "0.1.0"
last_verified: 2026-09-12
---

# State of play

What is live right now. **Rewritten each session, never appended.** Git history
is the append-only log; this file stays short enough to read in two minutes.

Descriptive only. Nothing here is authority — see [`tasks.md`](../main/tasks.md)
for task truth and [`spec.md`](../main/spec.md) for law.

---

## Live

| Stream | Holding | State |
|---|---|---|
| C | T-130 (probe), T-132 (gate widening), T-51 (corpus) | READY; T-51 must wait for T-130 attribution; C's three rows serialize — see capacity note below |
| A | T-131 row 6 (evidence identity) | READY now, no attribution needed |
| B | T-131 rows 4 and 7 (completion stop, compaction/resume) | READY now, no attribution needed |
| Director | Charter II, awaiting dispatch | Not blocking any developer |

## Found, not yet decided

Observations that are true, have no owner, and would otherwise survive only in a
chat transcript. This section is the reason the file exists.

| Finding | Impact | Owner |
|---|---|---|
| `docs/execution/main/tasks.md` is 1,838 lines against a 1,700 budget; `check_doc_budgets.py` fails but is **not** wired into `just check` | A budget nobody enforces is not a budget; the file was already over before recent additions | unassigned |
| `director_task_instruction.md` is tracked and committed while instructing that it never be | Process artifact leaked into the truth plane | CEO |
| `GUIDELINES.md` at repo root duplicates both `guidelines/` documents verbatim | Two sources for one instruction | CEO |
| Stream C owns benchmarks, tests, linters, `justfile`, presets and execution docs | Caps parallelism regardless of agent count | CEO + Senior |
| 49 of 52 `living` documents unverified since 2026-09-03 or earlier | `living` currently means "not deleted"; agents cannot tell the working set from the archive | unassigned |
| `status:` vocabulary contains both `proposal` (13) and `proposed` (11) | Two spellings of one state invite hedged output | unassigned |
| RUN-13 causal statement is open; T-130 produces the evidence | Do not assume an `entrypoint.py` root cause | Director, after T-130 |

## As-built deltas

Where implementation diverged from the documents, discovered during work.

| Delta | Detail |
|---|---|
| Gate discovery | `just verify` covers ~947 of ~3,171 tests. `NT-B03` already requires full discovery for *acceptance*, so the spec is correct and the routine gate is the gap. T-132 closes it. |
| Execution doc location | The five canonical documents moved to `docs/execution/main/`; `check_execution_truth.py` was repointed and repo-wide links rewritten. |

## Escalations pending

| Item | Waiting on |
|---|---|
| Whether `GUIDELINES.md` is deleted now that it is split | CEO |
| Whether `director_task_instruction.md` is untracked or its own rule dropped | CEO |
| Redrawing stream C's ownership before adding agents | CEO |
| Public-contract fork, if T-130 falsifies RUN-10 | Director, after T-130 |

---

*Last rewritten: 2026-09-12.*
