# Remaining Plan — M0 Purge & Scaffolding (TODO Only)

**Status:** STAGED (Awaiting authorization for history rewrite)

| ID | Task | Acceptance / Verification |
|---|---|---|
| **S-M0-A-04** | Verify archive coverage: confirm `docs/archive/v045/` covers all legacy specs before permanent deletion. | `find docs -name '*.md' \| wc -l` trending toward ≤30. |
| **S-M0-A-05** | **History rewrite** (`git filter-repo` pass): purge `SEC-01` secrets in history, `lam.sqlite`, `runs/**`, sprint evidence JSONL, `vanguard-gui/`, `vanguard-ide/`, `benchmark_results.json`. | `python3 tools/scan_secrets.py --all-refs` PASS; repo pack size ≤ 3 MB. |
| **S-M0-A-06** | CI cleanup: drop legacy badges, add lane-ownership enforcement gate. | CI green on rewritten main. |
| **S-M0-B-05** | Migrate test runner: switch from `unittest discover` to `pytest` configuration for retained test suite. | `pytest -q` runs and passes. |
| **S-M0-B-06** | Blob-store evidence relocation tool: move sprint evidence into digest-keyed local store. | Round-trip `fetch(digest)` matches sample artifacts. |


# Remaining Plan — M1/M2 Microkernel & Plugin Runtime (TODO Only)

**Status:** ACTIVE (M1 Complete; M2 Finalizing)

| ID | Sprint | Task | Acceptance / Verification |
|---|---|---|---|
| **S-M2-A-03** | 4 | **AT-12 Verifier Isolation**: implement static reachability proof ensuring no plugin cell holds evaluator UDS path/signing keys (or land ADR with compensating control). | CI isolation proof passes or signed ADR lands. |
| **S-M2-A-04** | 5 | **Hot-Swap Attribution**: verify mid-run routing swap records exact turn seq, recomputes harness digest, and reconstructs both epochs in replay telemetry. | Mid-run swap fixture passes replay-parity with dual harness digests. |


# Remaining Plan — M3: Coding Pack #1 (TODO Only)

**Status:** ACTIVE (Code extraction complete; Acceptance benchmarks pending)

| ID | Task | Acceptance / Verification |
|---|---|---|
| **S-M3-A-06** | **Phase-1 Acceptance Measurement**: run compiled `code-default` pack vs. v0.4.5 baseline on `lab/` dogfood triple + `benchmarkings/zero_hint_v1` under paired McNemar with preregistration. | `python3 lab/bench.py --pack code-default --paired --against v0.4.5-baseline` |
| **S-M3-A-07** | **Live-Model Greenfield Proof**: solve ≥1 greenfield coding task end-to-end using compiled `code-default` against a live model with a signed `oracle_green` verdict. | `python3 tools/run_v0450_greenfield_campaign.py --pack code-default --live` |


# Remaining Plan — M4: Harness Parity (TODO Only)

**Status:** STAGED (Awaiting multi-pack recompilation and parity benchmarks)

### Lane A — Measurement, Latency & Freeze Enforcement

| ID | Task | Acceptance / Verification |
|---|---|---|
| **S-M4-A-01** | **Layer-0 Freeze Gate**: CI job asserting `git diff --stat layer0/` is zero relative to baseline tag for all M4 commits. | `test -z "$(git diff --stat v0.5.1-baseline..HEAD -- layer0/)"` |
| **S-M4-A-02** | **Zero-Hint Parity**: execute `benchmarkings/zero_hint_v1` as a 2×2 paired matrix for compiled packs vs. v0.4.5 baseline under paired McNemar. | `bash benchmarkings/zero_hint_v1/run_matrix_2x2.sh && python3 benchmarkings/zero_hint_v1/summarize_matrix.py` |
| **S-M4-A-03** | **Tier-5 Datalog Parity**: run `benchmarkings/frontier_tier5_datalog_engine` under compiled `code-default` pack with anti-cheat leak lint. | `python3 lab/bench.py --pack-a v0.5.1-baseline --pack-b code-default --db lam.sqlite` |
| **S-M4-A-05** | **Per-Harness Attribution Report**: generate report showing prefix-hit rate, escalation count, USD/episode, and pass rate across all 5 packs. | Pairwise attribution trace diffs generated via `lab/bench.py` / `lab/diff.py`. |
| **S-M4-A-06** | **Parity Gap Disposition**: document every measured deficit below baseline as an ADR row with reversal conditions (zero ad-hoc Layer-0 patches). | ADRs logged and cross-references verified. |

### Lane B — Manifest Recompilation & Multi-Pack Execution

| ID | Task | Acceptance / Verification |
|---|---|---|
| **S-M4-B-01** | Recompile **`code-claude-shaped`** into `packs/code-claude-shaped/harness.yaml` from legacy manifest. | `python3 -m unittest test.packs.test_compile -k claude_shaped` |
| **S-M4-B-02** | Recompile **`code-opencode-shaped`** into `packs/code-opencode-shaped/harness.yaml` from legacy manifest. | `python3 -m unittest test.packs.test_compile -k opencode_shaped` |
| **S-M4-B-03** | Recompile **`code-swe-mini`** into `packs/code-swe-mini/harness.yaml` from legacy manifest. | `python3 -m unittest test.packs.test_compile -k swe_mini` |
| **S-M4-B-04** | Author/recompile fifth shape (**`code-pi-shaped`** or resolve `vg-shell-only`) and align roadmap naming. | `python3 -m unittest test.packs.test_compile -k pi_shaped` |
| **S-M4-B-05** | Register **TableWorld as Pack #2** in `packs/table-default/` from legacy manifest and environment adapter. | `python3 -m unittest test.packs.test_compile -k table_default` |
| **S-M4-B-06** | **5-Pack Runtime Execution**: run 1 full episode for each of the 5 packs through registry with zero hardcoded imports, producing schema-valid `mhf.trajectory/1`. | `python3 -m unittest discover -s test/packs -t .` |
