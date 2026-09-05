# Part I — Evidence Audit

Every claim in this document is reproducible from the tree at `5243866b`. Commands are given so
each finding can be independently falsified. Where a number disagrees with a number in
`dev_context_logs/context_summary.md`, the discrepancy is noted — the summary was generated on a
different HEAD (`7d46c7f5`, branch `feat/beta-release_electroweak-v091`) and is stale.

---

## 1. Outcome evidence

### 1.1 Repository-wide terminal-state census

Every JSON under `benchmarks/` was parsed and every row bearing a `status`, `terminal`,
`terminal_state`, `passed`, or `oracle_passed` field was tallied.

```
PASS               234        FAIL               101
NO_PATCH           123        DATASET_INVALID     32
PLANNED            115        COMPLETED           18
DRY_RUN_COMPLETE    27        abandoned           15
FAILED_ORACLE        3        ERROR                2
NOT_RUN              2
```

Three observations dominate everything else in this review:

1. **`NO_PATCH` (123) is the single largest failure class**, larger than `FAIL` itself. The agent
   is not producing wrong code. It is producing *no code*.
2. **`PLANNED` (115) and `DRY_RUN_COMPLETE` (27) are 142 rows that never executed.** They are
   preregistrations and dry runs sitting in the same directory tree, with the same schema shape, as
   executed results.
3. A large share of the 234 `PASS` rows come from `benchmarks/baac/runs/baac-*-lam-*`, i.e. runs
   against the **LAM mock model** (`tools/002_LLM_API_MOCK/`, 8,580 LOC), not against a real
   provider. A LAM pass is a harness-plumbing proof, not a capability measurement.

### 1.2 The headline benchmark file is a cassette replay

```bash
python3 -c "import json;d=json.load(open('benchmarks/agentic_matrix_benchmark_results.json'));
print([(r['harness'],r['score'],r['turns'],r['total_tokens'],r['model']) for r in d['coding_harness_benchmarks']])"
```

```
('vg-code-lex',           1.0, 1, 205, 'cassette/golden-deterministic')
('vg-code-default',       1.0, 1, 205, 'cassette/golden-deterministic')
('vg-code-claude-shaped', 1.0, 1, 205, 'cassette/golden-deterministic')
```

Three harnesses, three perfect scores, one turn each, 205 tokens each, all replaying a pre-recorded
golden answer. This file's `framework` field reads `"Vanguard / AETHER Substrate 0.9.0b1"` and its
rows carry `oracle_passed: true` and `score: 1.0` in the same schema shape as live runs. It is
correctly labelled in the `model` field and nowhere else. **Anyone skimming this file will read
"the coding harness scores 1.0" and be wrong.** This is the same class of hazard as peer finding F1,
in a different file.

### 1.3 `frontier_v090` — the 27-task live run

```bash
python3 -c "import json,collections
d=json.load(open('benchmarks/frontier_v090/artifacts/live_27_deepseek_v4_flash_report.json'))
rows=d if isinstance(d,list) else next(v for v in d.values() if isinstance(v,list))
print(collections.Counter(r['terminal'] for r in rows))
print(collections.Counter(r['terminal_reason'] for r in rows))
print(rows[0]['usage'])"
```

```
Counter({'NO_PATCH': 27})
Counter({'completed_without_source_patch': 27})
{'prompt_tokens': 13668, 'completion_tokens': 386, 'cached_tokens': None,
 'cost_usd': None, 'cost_provenance': 'unknown'}
```

Twenty-seven consecutive tasks. `before_digest == after_digest` on every row. 13,668 prompt tokens
consumed to emit 386 completion tokens and then declare completion having changed nothing.

Companion runs:

| Artifact | Result |
|---|---|
| `live_27_free_minimax_report.json` | `NO_PATCH` 25, `COMPLETED` 2 |
| `live_27_clean_report.json` / `_v2` | `DATASET_INVALID` 16, `NO_PATCH` 7, `COMPLETED` 4 |
| `live_hard2_deepseek_v4_pro_report.json` | `NO_PATCH` 2/2 |
| `live_27_attempts.json` | `PASS` 16, `abandoned` 11 |

Note the last row against the first: **16 attempts scored `PASS` in `live_27_attempts.json` while
the corresponding report rows are `NO_PATCH`.** Two files in the same directory disagree about the
same run. This is not a rounding difference; it is two different definitions of success living in
one artifact directory with no schema field distinguishing them.

`cost_provenance: 'unknown'` and `cost_usd: null` on all 27 rows means the run has **no cost
accounting**, despite `openrouter.py` implementing full cached/uncached price arithmetic
(`_price_for`, lines 175–210). The instrument was built and not connected.

### 1.4 `benchmark_20_suite` — confirming peer findings F1 and F2

```bash
python3 -c "import json,collections
d=json.load(open('benchmarks/benchmark_20_suite/benchmark_20_results.json'))
print(d['pass_rate_pct'], len(d['results']), collections.Counter(x['turns'] for x in d['results']))
f=json.load(open('benchmarks/benchmark_20_suite/benchmark_20_results_vg_1_forge.json'))
print(f['pass_rate_pct'], len(f['results']))"
```

```
9.5   21   Counter({1: 21})
100.0  1
```

Both peer findings hold at current HEAD, unfixed:

- **F1 confirmed.** `pass_rate_pct: 100.0` over `n=1` sits beside `pass_rate_pct: 9.5` over `n=21`
  in the same directory, same schema, filenames differing only by suffix. There is still no `n`,
  no `suite_digest`, and no guard in the writer.
- **F2 confirmed.** All 21 runs terminated at turn 1. A one-turn agent on a brownfield repair task
  is a loop that never iterated. The 9.5% figure measures a defect in the harness, not the
  capability of the harness.

`benchmark_20_results_vg_code_max.json` shows the same distribution (19 FAIL / 2 PASS, all
`turns: 1`).

**The open question the peer audit raised remains open and is still the cheapest high-value
experiment in the repository:** run `vg-code-max` on the 20-task suite and check whether the turn
distribution has mass above 1. Nothing built on the 9.5% number is trustworthy until it does.

### 1.5 The artifact-naming signature

`benchmarks/artifacts/ladder/` contains, among ~50 report files:

```
report_v3a_… report_v3b_… report_v3c_… report_v3d_… report_v3e_…
report_v3f_… report_v3g_… report_v3h_… report_v3i_… report_v3j_…
report_..._fix3, _fix4, _fix5
report_..._final, _final2, _final3
report_..._frontierfix, _policyfix, _sotaalign, _snapshotfix, _aliasfix
```

Almost all are `n=1`. This is the fingerprint of *interactive debugging frozen into permanent
evidence*. Each file is a single-task run performed to check whether a code change helped, then
committed. That is a log, not a measurement. It is also actively harmful: it makes the evidence
directory unsearchable and it makes any future aggregate over `benchmarks/` — like the one in §1.1
— dominated by noise.

`report_easy_v3_easy_deepseek_…json` is the only multi-row ladder artifact (10 rows, 10 PASS,
4–7 turns, $0.001–0.003 each). It is the strongest genuine capability evidence in the repository
and it is buried among forty single-row files with near-identical names.

---

## 2. Structural evidence

### 2.1 Mass distribution

```bash
for d in vanguard/packages/*/; do
  echo "$(find $d -name '*.py' | xargs wc -l | tail -1 | awk '{print $1}') $(find $d -name '*.py' | wc -l) $d"
done | sort -rn
```

| Package | LOC | Files | Role |
|---|---:|---:|---|
| `runtime/` | 25,821 | 91 | compose, session, wiring, ledger, governance |
| `adapters/` | 11,703 | 59 | models, sandbox, stores, evaluators |
| `domain/` | 10,139 | 54 | values, wire, JCS, reducers |
| `agency/` | 9,388 | 39 | **three** loops, context, patchers |
| `kernel/` | 1,769 | 9 | S0–S12, attenuation, budget (TCB closure 1,386 / ceiling 1,438) |
| `ports/` | 1,582 | 15 | interfaces |
| `apps/` | **79** | 3 | **the product** |

Alongside: `test/` 58,714 LOC across 370 files; `docs/` 58,910 lines across 99 markdown files.

The ratio production : tests : docs is approximately **1 : 1 : 1**. For a system whose flagship
application is 79 lines and whose flagship benchmark returns `NO_PATCH` 27/27, this is a
misallocation of effort by roughly an order of magnitude.

`runtime/session.py` alone is 1,899 LOC — larger than the entire kernel plus ports. `runtime/` is
14× the kernel. The layer with no correctness ceiling has absorbed the mass that the layer with a
ceiling was designed to repel. That is what a LOC ceiling on one package and no ceiling anywhere
else produces: the complexity does not disappear, it relocates.

### 2.2 The agent-facing surface

From `packs/code-default/harness.yaml` and the 32 manifests under
`vanguard/packages/agency/manifests/`, the complete tool vocabulary available to a coding episode:

| Verb | Capability | Constraint |
|---|---|---|
| `fs.read` | read **one named file** | fails on a directory, including `.` |
| `fs.search` | grep | Python `re`, whole-workspace or path-scoped |
| `patch.apply` | write | unified diff with `@@` headers, or whole-file `content` |
| `proc.exec` | execute | `argv` array only; `argv[0] ∈ {git, pytest, ruff, python3}`; **no shell** |
| `finish` | terminate | present in some presets only (`v3luna` has it; `vg-code-max` does not) |

And from `packs/code-default/system-prompt.txt`, verbatim:

> "Exactly ONE tool call per turn. Never batch multiple tool calls or emit parallel actions in one turn."
> "There is no directory-listing tool: fs.read only reads one named file and fails if given a directory (including `.`)."
> "`proc.exec` takes an `argv` array executed directly, never a shell string -- there is no `bash` or `sh` binary available."

Roughly half the system prompt is spent explaining the absence of capabilities. This is the
measurable centre of the problem and it is developed in Part 2 §D1.

### 2.3 The unwired index

```bash
python3 -c "import sqlite3;c=sqlite3.connect('.lda/index.db')
print({n:c.execute(f'select count(*) from \"{n}\"').fetchone()[0]
       for (n,) in c.execute(\"select name from sqlite_master where type='table'\")
       if not n.startswith('fts_search_')})"
```

```
files 3,347 · entities 13,882 · symbols 10,422 · relations 77,610
documents 255 · doc_sections 5,073 · index_runs 1 · fts_search 29,959
```

This is a real, populated, multi-relation code-and-documentation graph with full-text search. It is
built and consumed by `tools/007_LLM_DOCS_ATLAS/` (8,156 LOC) and surfaced to *developers* through
`tools/docs_rag_v0.py` and `AGENTS.md` §"Repository-Intelligence Navigation Protocol".

What the *agent* receives when it calls `IndexPort`:

```python
# vanguard/packages/adapters/stores/repo_index.py:8-10, 363 LOC total
"""The real one is deliberately cheap: a regex definition scan, no parser, no
   language server. tree-sitter can replace the body later without the port
   moving, which is the point of having the port now."""

_DEFINITIONS = (   # the complete symbol vocabulary
    (".py",  "function", r"^\s*(?:async\s+)?def\s+([A-Za-z_]\w*)"),
    (".py",  "class",    r"^\s*class\s+([A-Za-z_]\w*)"),
    (".ts",  "function", r"^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_]\w*)"),
    (".ts",  "class",    r"^\s*(?:export\s+)?class\s+([A-Za-z_]\w*)"),
    (".tsx", "function", r"^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_]\w*)"),
)
```

Five regexes, three file extensions, no call graph, no reference resolution, no cross-file edges.

Further:

```bash
grep -rn "ast_grep_adapter\|scip_adapter" --include="*.py" . | grep -v node_modules
#   → (no results outside the files' own definitions)
grep -rn "tree_sitter\|language_server\|embedding\|faiss" --include="*.py" vanguard/
#   → (one docstring mention; no code)
```

`tools/ast_grep_adapter.py` and `tools/scip_adapter.py` exist and are imported by **nothing**.

### 2.4 Prompt caching: built, then not requested

`agency/context/compiler.py` and `agency/context/layers.py` implement a genuinely correct
cache-stable prefix design: `L1`–`L4` frozen at construction so no call site can move them,
`BREAKPOINT_LAYERS` declaring where a cache boundary may sit, `CacheBreakpointCeilingExceeded`
guarding the count. The docstring's reasoning is exactly right.

```bash
grep -rn "cache_control\|ephemeral" --include="*.py" vanguard/
#   → (no results)
grep -n "cached_tokens" vanguard/packages/adapters/models/openrouter.py
#   → 175, 182, 195, 207, 1138, 1140, 1154, 1157  — all inside cost arithmetic
```

The adapter *reads* `cached_tokens` to compute price and **never emits a single cache breakpoint on
the wire**. The expensive half of prompt caching (a provably stable prefix) is complete; the
free half (marking it) was never done. At 13,668 prompt tokens per turn this is the dominant
recurring cost in every run in §1.3.

Compounding this, the prefix-drift hazard the peer report flagged is still live:

```bash
grep -rn "_schemas_with_aliases" --include="*.py" vanguard/
#   → runtime/compose.py:506, runtime/compose.py:524
```

Tool schemas are still expanded into aliased duplicates at composition. If that expansion is not
byte-stable across turns, `L2` mutates and the prefix invariant is violated — an invariant
currently protected by a docstring and no test.

### 2.5 Three loops in a one-loop architecture

```
agency/episode/engine.py       1,122      agency/forge/engine.py        795
agency/chimera/engine.py         495
agency/forge/patcher.py          603      agency/forge/resilient_patcher.py  504
agency/chimera/patcher.py        147
```

Three episode engines and three patchers, in the package whose architectural mandate is *one*
recursive turn machine. `README.md` §10 states: *"The episode is the program. There is no workflow
engine…"* The code contains three.

`resilient_patcher.py` — 504 LOC of unified-diff recovery heuristics — is a monument to a bad
primitive choice, not a feature. See Part 3 §5.

### 2.6 Manifest sprawl by copy

32 presets under `agency/manifests/`. Diffing two of them:

```bash
diff <(python3 -m json.tool .../vg-code-max/manifest.json) \
     <(python3 -m json.tool .../vg-code-max-v3luna/manifest.json)
```

```diff
-  "vg-code-default/read-tool.json"     +  "vg-code-max-v3luna/read-tool.json"
-  "vg-code-default/search-tool.json"   +  "vg-code-max-v3luna/search-tool.json"
-  "vg-code-default/patch-tool.json"    +  "vg-code-max-v3luna/patch-tool.json"
-  "vg-code-default/test-tool.json"     +  "vg-code-max-v3luna/test-tool.json"
                                        +  "vg-code-max-v3luna/finish-tool.json"
```

Identical tools, duplicated into a new directory. The genuine delta between these two presets — a
`finish` tool and a dropped `repo_index` component — is invisible under twelve lines of path churn.

The family tree: `v2`, `v2b`, `v3`, `v3luna`, `chimera`, `forge` (`vg-1-forge-v2`), `herbs`,
`hermes`, `lex`, `claude-shaped`, `opencode-shaped`, `react-control`, `swe-mini`, `critic-reviser`,
`shell-only`, `lim-falsifier`, `surgical`. **Not one of the 32 is known to be better than another**,
because no artifact in the repository runs more than a handful of them against the same frozen task
set with n > 1.

### 2.7 Where the effort went

```bash
git log --oneline -200 --pretty=%s | awk -F'[(:]' '{print $1}' | sort | uniq -c | sort -rn
```

```
101 feat   50 docs   23 refactor   7 chore   5 fix   1 test
```

Five commits out of two hundred are labelled `fix`. One is labelled `test`. Fifty are pure
documentation. Within those fifty:

```
docs(refactor): Improvements to the Sprint Structure          × 5
docs(refactor): Restore development plans                      × 4
```

Nine commits reworking the *shape of the board*. This is the observable signature of effort
flowing to the tractable problem (documentation structure) rather than the hard one (making the
agent patch a file).

### 2.8 What is verifiably healthy

For balance, and because these are worth protecting:

| Asset | Evidence |
|---|---|
| Boundary lattice | `check_boundaries.py` over 597 files, enforced per commit, zero violations |
| TCB ceiling | 1,386 / 1,438 LOC, `check_tcb_budget.py`, headroom +52 |
| Test suite | 634 tests green (97 + 121 + 416, 6 skipped) per `dev_context_logs/04_tests.txt` |
| Event store schema | Single-writer WAL; envelope digest, `retention_class`, `trainability`, `confidentiality`, `redaction_status` as first-class columns — this is a *better* ledger schema than most production systems have |
| Context compiler | Prefix frozen at construction; brief compaction-exempt; correct and well-argued |
| Falsifier discipline | `test/falsifiers/` (56 files), must-fail counterparts for controls |
| Epistemic honesty | `undeterminable` as a first-class disposition; `DATASET_INVALID` rows preserved rather than dropped; ADR-0102 invalidating the project's own baseline |

The last row is the rarest thing in this repository and the reason the rest of this review is worth
writing. A project that invalidates its own control is a project that can be corrected by evidence.

---

## 3. The evidence, summarised as a causal chain

```
tool surface is 5 verbs, 1 call/turn, no shell, no listing, unified-diff edits
      │
      ├──► model cannot orient (no ls, no symbol graph) ──► 13,668 prompt tokens of grep spray
      ├──► model cannot edit reliably (diff line arithmetic) ──► NO_PATCH 123, malformed 81
      ├──► model cannot batch ──► turn count × latency × prompt re-send
      │
      ▼
run terminates "completed" with before_digest == after_digest, 27/27
      │
      ├──► no postcondition gate existed to catch it (AdmissionGate is recent)
      ├──► no cache breakpoints ──► every turn re-sends 13.7k tokens at full price
      ├──► no cost provenance ──► cost_usd: null, so the waste is invisible
      │
      ▼
diagnosis attempted by cloning the manifest and re-running one task
      │
      ├──► 32 presets, 3 engines, 3 patchers, ~50 single-row report files
      ├──► n=1 artifacts adjacent to n=21 artifacts in one schema
      │
      ▼
no comparison is possible, so no fork can be retired, so sprawl compounds
      │
      ▼
effort redirects to the tractable surface: 50/200 commits are documentation
```

Every arrow in that chain is addressable, and none of them requires touching `kernel/`.
