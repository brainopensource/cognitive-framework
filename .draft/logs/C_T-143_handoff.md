# T-143 handoff — Developer C → independent Principal (A)

**row**: T-143 Greenfield and multi-file oracle completeness
**owner**: C (author; cannot self-accept; cannot be sole acceptor of a batch that includes this row)
**acceptor requested**: A (non-author)
**requires**: T-137 handoff (present; acceptance may still be pending)
**subject HEAD**: `5a3e6e444e0fe995eb8efd321ae9e11e6ded584c` plus uncommitted C delta
**DIR-C7**: workers emit immutable candidate references (`candidateDigest` / `requiredFiles` / `verificationSubjectDigest` on `EvaluationProtocol.parameters`). Evaluator never mints `accepted` or merge authority.

## LDA confirmation (before first `isolated.py` edit)

`lda_plan` named `vanguard/packages/adapters/evaluators/isolated.py` and `test/adapters/test_isolated_evaluator.py`. New falsifier authorized under `test/falsifiers/`. Did not duplicate T-131 `evidence_capture.py`.

## Lease touched

- `vanguard/packages/adapters/evaluators/isolated.py`
- `test/adapters/test_isolated_evaluator.py`
- `test/falsifiers/test_t143_oracle_completeness.py` (new)
- `docs/backend/architecture/assurance-evaluation.md` (canonical owner of exterior evaluation)

## Falsifier (ran)

```bash
python3 -m unittest test.adapters.test_isolated_evaluator test.falsifiers.test_t143_oracle_completeness -v
```

**24 tests, OK.**

Also ran `test.security.test_evaluator_security` — 6 tests OK (outside lease; no regressions).

## Contract

Exterior verification of the exact submitted candidate, before the oracle process:

| Case | Result |
|---|---|
| Valid multi-file + greenfield positive controls | `EvaluationCompleted` / `passed`, `candidateCompleteness=true`, no `accepted` field |
| Empty / `pass` / `NotImplementedError` stubs | `EvaluationIncomplete` / `empty_stub_solution` |
| Vacuous `-c` / `true` command | `vacuous_discovery`; runner not invoked |
| Oracle that ignores required files | `vacuous_discovery` |
| Omitted required file | `omitted_required_file` |
| Unauthorized extra file | `unauthorized_addition` |
| Foreign `candidateDigest` | `candidate_substitution` |
| Stale `verificationSubjectDigest` | `stale_verification` |
| Tampered oracle bytes | existing `EvaluationTampered` still fires first |

Child oracle process gets `PYTHONPATH=<workspace>` so required-behavior tests import the submitted tree (script-path `sys.path[0]` would otherwise hide it).

## Not claimed

- Merge authority, completion admission by product name, MS-CONTROL, T-144, T-51, Wilson/18-of-30.
