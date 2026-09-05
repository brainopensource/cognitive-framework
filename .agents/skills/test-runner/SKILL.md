---
name: test-runner
description: >-
  Atomic test execution and hermetic verification skill.
  Executes isolated, timeout-bounded test suites, capturing exit codes, durations,
  stdout, stderr, and structured test failure/error diagnostics.
version: "1.0.0"
authority: operational
---

# Test Runner — Atomic Hermetic Verification Skill

The **test-runner** skill provides bounded, isolated, and structured test execution for automated agent workflows. It ensures that running test suites cannot hang the agent process (fail-closed timeout protection) and extracts machine-readable test diagnostics from stdout/stderr.

---

## 1. Capabilities

- **Subprocess Isolation:** Runs tests in an isolated shell environment without polluting the host agent's state.
- **Fail-Closed Timeout Protection:** Guards against infinite loops or hanging I/O by hard-killing stuck test processes after a configurable timeout.
- **Diagnostic Parsing:** Parses standard test frameworks (Python `unittest`, `pytest`) to extract failing test case names, assertion messages, and tracebacks.
- **Machine-Readable Telemetry:** Emits structured JSON containing execution duration, exit code, failure counts, and detailed error summaries.

---

## 2. CLI Usage

The skill provides the executable runner at `.agents/skills/test-runner/scripts/run_test.py`:

```bash
# Run a specific unit test suite
python3 .agents/skills/test-runner/scripts/run_test.py "python3 -m unittest test.kernel.test_dispatch -v"

# Run with custom timeout (seconds) and JSON output
python3 .agents/skills/test-runner/scripts/run_test.py \
  --test-cmd "python3 -m unittest discover -s test/kernel -t ." \
  --timeout 10.0 \
  --json
```

---

## 3. Output Schema (JSON)

```json
{
  "command": "python3 -m unittest test.kernel.test_dispatch -v",
  "success": true,
  "exit_code": 0,
  "duration_seconds": 0.143,
  "timed_out": false,
  "failures_count": 0,
  "errors_count": 0,
  "failures": [],
  "stdout": "",
  "stderr": "Ran 29 tests in 0.006s\n\nOK\n",
  "summary": "OK"
}
```

When a failure occurs:
```json
{
  "command": "...",
  "success": false,
  "exit_code": 1,
  "duration_seconds": 0.05,
  "timed_out": false,
  "failures_count": 1,
  "errors_count": 0,
  "failures": [
    {
      "kind": "FAIL",
      "test": "test_module.TestCase.test_failing_assertion",
      "traceback": "Traceback (most recent call last):\n  File '...': AssertionError: 1 != 2"
    }
  ],
  "summary": "FAILED (failures=1, errors=0)"
}
```

---

## 4. Python API

Other agent tools or scripts can import the execution primitive directly:

```python
from pathlib import Path
import sys

# Import run_isolated_test
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "skills" / "test-runner" / "scripts"))
from run_test import run_isolated_test

result = run_isolated_test("python3 -m unittest test.kernel.test_dispatch -v", timeout=5.0)
if not result["success"]:
    print(f"Test failed: {result['summary']}")
```
