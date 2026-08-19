# Gate R9 — Q2 Dogfood Execution Log

**Execution Timestamp:** `2026-08-19T04:39:45.672858+00:00`  
**Harness:** `Runtime.execute_harness` + LAM + Bubblewrap worker  
**Evaluator:** UID `10002`, sealed oracle mount, signed Unix-socket verdict  

| Task | Turns | Hand Patches | Restarts | Oracle | Signed Verdict | Result | Q2 |
|---|---:|---:|---:|---|---|---|---|
| `bug-001-single-file` | 2 | 0 | 0 | `vanguard/packages/adapters/evaluators/suites/bug-001-single-file/test_oracle.py` | True | **FAIL** | **NO** |
| `bug-002-multi-file` | 2 | 0 | 0 | `vanguard/packages/adapters/evaluators/suites/bug-002-multi-file/test_oracle.py` | True | **FAIL** | **NO** |
| `bug-003-test-reaction` | 2 | 0 | 0 | `vanguard/packages/adapters/evaluators/suites/bug-003-test-reaction/test_oracle.py` | True | **FAIL** | **NO** |

## Evidence

### bug-001-single-file
- Oracle: `vanguard/packages/adapters/evaluators/suites/bug-001-single-file/test_oracle.py`
- Diff digest: `sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Terminal: `abandoned`; verdict: `claims`
- Verdict reason: ``
- Claims: `({'event': 'EvaluationCompleted', 'status': 'failed', 'runId': 'dogfood-bug-001-single-file', 'protocol': 'coding-oracle@3', 'probes': {'immutability': True, 'nonPollution': True}, 'evaluatorUid': 10002, 'imageDigest': 'sha256:a2405085fefdeda18e9485184cc7d999a53816bc8fa46253bb1d13876b40dd6f', 'exitCode': 1},)`
- Detail: turn bound 8 reached

### bug-002-multi-file
- Oracle: `vanguard/packages/adapters/evaluators/suites/bug-002-multi-file/test_oracle.py`
- Diff digest: `sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Terminal: `abandoned`; verdict: `claims`
- Verdict reason: ``
- Claims: `({'event': 'EvaluationCompleted', 'status': 'failed', 'runId': 'dogfood-bug-002-multi-file', 'protocol': 'coding-oracle@3', 'probes': {'immutability': True, 'nonPollution': True}, 'evaluatorUid': 10002, 'imageDigest': 'sha256:a2405085fefdeda18e9485184cc7d999a53816bc8fa46253bb1d13876b40dd6f', 'exitCode': 1},)`
- Detail: turn bound 8 reached

### bug-003-test-reaction
- Oracle: `vanguard/packages/adapters/evaluators/suites/bug-003-test-reaction/test_oracle.py`
- Diff digest: `sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Terminal: `abandoned`; verdict: `claims`
- Verdict reason: ``
- Claims: `({'event': 'EvaluationCompleted', 'status': 'failed', 'runId': 'dogfood-bug-003-test-reaction', 'protocol': 'coding-oracle@3', 'probes': {'immutability': True, 'nonPollution': True}, 'evaluatorUid': 10002, 'imageDigest': 'sha256:a2405085fefdeda18e9485184cc7d999a53816bc8fa46253bb1d13876b40dd6f', 'exitCode': 1},)`
- Detail: turn bound 8 reached
