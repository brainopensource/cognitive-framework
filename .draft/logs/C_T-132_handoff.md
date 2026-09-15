# C implementation handoff — T-132 Gate discovery

- **packet**: T-132
- **owner**: Developer C
- **eligible peer acceptor**: Developer A (non-author)
- **subject**: dirty tree on HEAD `cf4103de882ad9eca5596f192595a941845c9e7a`
- **falsifier**: `python3 -m unittest test.contracts.test_collection_integrity -v` → 12 tests, OK
- **strict isolated gate**:
  - synthetic 30-HOLDOUT admission: GREEN (`test_synthetic_eligible_holdout_admission_is_green`)
  - actual unaccepted holdout: RED (`just verify-admission-strict` / `HOLDOUT UNACCEPTED`)
  - stale oracle digest: RED (`test.benchmarks.test_control_corpus` → `oracle digest mismatch`)
- **not a corpus acceptance**. No suite was hidden to manufacture PASS.

## Required modules now in `just verify` and both CI workflows

- `test.benchmarks.test_corpus_quarantine`
- `test.benchmarks.test_control_accounting`
- `test.benchmarks.test_metric_veto`
- `test.falsifiers.test_completion_gate_scope`
- `test.benchmarks.test_control_corpus` (stale-oracle red control)

`just check` is unchanged and remains the fast loop (metadata-only quarantine).

## Cost (same subject, 2026-09-15)

| Gate | Wall |
|---|---|
| narrow kernel | 0.59s |
| narrow agency | 2.82s (4 pre-existing cassette errors on this machine) |
| narrow contracts | 0.35s |
| required green control/falsifier modules | <1s |
| `test_control_corpus` stale-oracle | 0.04s RED |
| full `test/falsifiers` discover | 39.48s RED (21 errors, 3 failures) |

Full-tree falsifier discover is too expensive and currently red for unrelated missing signed bundles. Those modules are named exclusions, not deleted.

## Exclusions (explicit)

| Path | Reason |
|---|---|
| `test/e2e` | not an importable unittest package (no `__init__.py`); clean-machine RC probe |
| `test/broken` | linter negative fixtures, not a unittest package |
| `test/falsifiers` full discover | material graph-coloring / M-5b / M-7 / inference-accounting error on this subject; named false-completion module is gated instead |

## Consequence

`just verify` is now RED on this subject: that is the T-132 proof, not a license to drop the control instrument. T-51 / curator / sealed store remain MISSING.
