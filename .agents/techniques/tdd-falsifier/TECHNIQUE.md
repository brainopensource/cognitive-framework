---
name: tdd-falsifier
description: >-
  Technique: Synergistic composition of lda-navigator and test-runner.
  Queries the LDA graph to identify correlated test suites for touched files and
  executes them via an isolated, timeout-bounded runner to produce structured DiagnosticReports.
version: "1.0.0"
authority: operational
composed_skills:
  - lda-navigator
  - test-runner
---

# TDD Falsifier (Technique 2)

**TDD Falsifier** is a composite agent technique combining:
1. **Targeted Test Discovery** via [`lda-navigator`](file:///home/rock-dev/Coding/cognitive-framework/.agents/skills/lda-navigator/SKILL.md)
2. **Hermetic Timeout-Protected Execution** via [`test-runner`](file:///home/rock-dev/Coding/cognitive-framework/.agents/skills/test-runner/SKILL.md)

---

## 1. Ontological Placement

$$\text{Skill (Atomic: LDA, test-runner)} \longrightarrow \mathbf{\text{Technique (TDD Falsifier)}} \longrightarrow \text{Proficiency (SWE Loop)}$$

Instead of blindly guessing which test suite covers an edited file, or executing long test runs that could hang indefinitely, this Technique:
1. **Discovers Falsifiers:** Queries the SQLite fact graph (`lda tests <target>`) to locate direct test suites mapped to the target.
2. **Prioritizes Repository Suites:** Intelligently ranks unit tests over broad benchmarks and broken fixtures.
3. **Executes with Bounded Timeout:** Runs the test under fail-closed process isolation, killing stuck loops.
4. **Extracts Structured Diagnostics:** Emits a `DiagnosticReport` with status (`PASS`, `FAIL`, `TIMEOUT`), duration, and specific failure traces.

---

## 2. CLI Invocation

The technique script lives at `.agents/techniques/tdd-falsifier/scripts/run_falsifier.py`:

```bash
# Auto-discover and run falsifier for a source file
python3 .agents/techniques/tdd-falsifier/scripts/run_falsifier.py vanguard/packages/kernel/attenuation.py

# Output machine-readable JSON DiagnosticReport
python3 .agents/techniques/tdd-falsifier/scripts/run_falsifier.py \
  vanguard/packages/kernel/attenuation.py \
  --json \
  --timeout 10.0
```

---

## 3. Output Schema (JSON DiagnosticReport)

```json
{
  "status": "PASS",
  "success": true,
  "target": "vanguard/packages/kernel/attenuation.py",
  "test_command": "python3 -m unittest test.kernel.test_attenuation -v",
  "duration_seconds": 0.521,
  "failure_summary": "All tests passed successfully",
  "failures": [],
  "raw_stdout": "",
  "raw_stderr": "Ran 26 tests in 0.375s\n\nOK\n"
}
```

When tests fail:
```json
{
  "status": "FAIL",
  "success": false,
  "target": "vanguard/packages/agency/compactor.py",
  "test_command": "python3 -m unittest test.agency.test_compactor -v",
  "duration_seconds": 0.18,
  "failure_summary": "test_agency.test_compactor.TestCompactor.test_window: IndexError: list index out of range",
  "failures": [
    {
      "kind": "FAIL",
      "test": "test_agency.test_compactor.TestCompactor.test_window",
      "traceback": "Traceback (most recent call last):\n  ...: IndexError: list index out of range"
    }
  ]
}
```
