# C implementation handoff — T-133 Q-01 quarantine correction

- **packet**: T-133
- **owner**: Developer C
- **eligible peer acceptor**: Developer A (non-author)
- **subject**: dirty tree on HEAD `cf4103de882ad9eca5596f192595a941845c9e7a` (implementation uncommitted at handoff)
- **SHA**: not yet committed; bind the landing SHA when C records the packet commit
- **falsifier**: `python3 -m unittest test.tools.test_check_corpus_quarantine test.benchmarks.test_corpus_quarantine -v`
  - 34 tests, 0.771s, OK
- **metadata linter**: `python3 tools/linters/check_corpus_quarantine.py --metadata` → PASS (HOLDOUT remains UNACCEPTED; this is not corpus admission)
- **not done**: T-51 plaintext, old-oracle digest repair, sealed-store acquisition, freeze

## Released to T-132

Gate files were already transferred. This packet does not edit `justfile` or CI workflows.

Handoff artifacts for discovery:

- callable coverage: every inventoried required path now has callable-level guards (see matrix)
- immutable exposure commitments: `benchmarks/ladder/corpus_registry.json` (30 EXPOSED, 0 HOLDOUT, `holdout_admission: UNACCEPTED`)
- red/green receipts: focused falsifier above

## Callable coverage matrix

| Path | Guard | Callables covered |
|---|---|---|
| benchmarks/agentic_harness_matrix_benchmark.py | required | `write_control_report`, `run_single_harness_task` |
| benchmarks/baac/lib/runner.py | required | runner materialize path |
| benchmarks/baac/lib/state.py | required | `materialize_scratch_workspace` |
| benchmarks/benchmark_needle_in_haystack.py | required | `setup_workspace`, `run_needle_benchmark` (explicit ordinary-user) |
| tools/diagnostics/write_landing_probe.py | required | `materialize`, `run_probe` (explicit ordinary-user; diagnostic, not holdout) |
| benchmarks/gemini_multifile_benchmark/runner.py | required | `run_multifile_benchmark` |
| benchmarks/harness_comparison_bench.py | required | `run_single_harness_eval` |
| benchmarks/ladder/l0_triad/runner.py | required | `materialize`, `run_task` (explicit ordinary-user L0) |
| benchmarks/ladder_runner.py | required | `run_one` |
| benchmarks/product_path.py | required | `execute_product` (ordinary-user unless corpus ID in extra) |
| benchmarks/run_20_eval_suite.py | required | `setup_workspace`, `evaluate_challenge` |
| benchmarks/run_3_hard_lda.py | required | `run_hard_challenge` |
| tools/002_LLM_API_MOCK/import_10_pro_corpus.py | required | `import_10_pro` |
| tools/002_LLM_API_MOCK/import_16_corpus.py | required | `import_corpus` |
| tools/002_LLM_API_MOCK/import_pro_corpus.py | required | `import_all_swe_challenges` |
| tools/002_LLM_API_MOCK/import_swe_verified_repo.py | required | `import_swe_verified` |
| tools/002_LLM_API_MOCK/importer.py | required | `import_trajectory` |
| tools/002_LLM_API_MOCK/live_coding.py | required | `load_challenge`, `main` |
| tools/002_LLM_API_MOCK/record.py | required | `trace_to_scenario` |
| tools/002_LLM_API_MOCK/store.py | required | `upsert_scenario` |
| tools/telemetry/coding_lam.py | required | `default_workspace_map` |
| vanguard/packages/runtime/task_sets.py | declarative | id+role declarations preserved through `resolve_task_set` |

Observed-unleased rows were promoted to required after callable guards landed. No directory-wide LAM lease.

## Correction vs Director rejection (63d12d83)

| Rejection | Repair |
|---|---|
| `guard_materialization(task_id=None)` / `guard_capture(task_id=None)` return | refuse `missing identity` unless `scope=ordinary_user` is explicit |
| unknown ID returns | refuse `unknown identity` |
| source bytes not checked | fingerprint/oracle-mount check on supplied source |
| truthy authority + caller FROZEN | bound evaluation authority + frozen commitments must match member |
| 14 unleased loaders | callable-level guards; linter rejects `observed-unleased` and unguarded callables |
| omitted corpus ID as bypass | ordinary user work must set `SCOPE_ORDINARY_USER`; registered IDs cannot use that scope |

Positive controls retained: fresh DEV admit; separately authenticated synthetic evaluation.

## Explicitly missing (do not invent)

- independent corpus curator name: **MISSING**
- sealed-store authority / location: **MISSING**
- T-51 replacement holdout identities: **MISSING** (30 old members remain EXPOSED)
