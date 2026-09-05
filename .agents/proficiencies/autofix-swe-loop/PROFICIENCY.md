---
name: autofix-swe-loop
description: >-
  Proficiency: Closed feedback loop SWE engine combining Spec-Driven CodeGen (T1)
  and TDD Falsifier (T2) with sub-30ms AST delta synchronization and fail-closed rollback.
version: "1.0.0"
authority: operational
composed_techniques:
  - spec-driven-codegen
  - tdd-falsifier
composed_skills:
  - lda-navigator
  - llama-cpp
  - test-runner
---

# Autofix SWE Loop (Proficiency Level)

**Autofix SWE Loop** represents the **Proficiency** tier in the agent cognitive ontology:
$$\text{Skill (Atomic)} \longrightarrow \text{Technique (Composition)} \longrightarrow \mathbf{\text{Proficiency (Closed Feedback Loop)}} \longrightarrow \text{Mastery (Meta-Heuristic)}$$

While atomic skills execute single primitives and techniques coordinate unidirectional actions, a **Proficiency** achieves autonomous goal closure through an active state-machine, error traceback ingestion, incremental AST re-indexing, and idempotent fail-closed rollback guarantees.

---

## 1. Control Loop Architecture

```text
               +-------------------------------------------+
               | 0. Baseline TDD Falsifier (Technique 2)   |
               | Proves defect actively fails tests        |
               +---------------------+---------------------+
                                     | (FAIL / ERROR)
                                     v
+------------> +-------------------------------------------+
|              | 1. Spec-Driven CodeGen (Technique 1)      |
|              | Ingests AST slice + error feedback trace  |
|              +---------------------+---------------------+
|                                    | (Generates candidate patch)
|                                    v
|              +-------------------------------------------+
|              | 2. Apply Patch & Incremental AST Delta    |
|              | uv run lda index --delta (<30ms sync)     |
|              +---------------------+---------------------+
|                                    |
|                                    v
|              +-------------------------------------------+
|              | 3. TDD Falsifier Verification             |
|              | Runs test suite under bounded timeout     |
|              +---------------------+---------------------+
|                                    |
|                      +-------------+-------------+
|                      |                           |
|                  (PASS)                      (FAIL)
|                      |                           |
|                      v                           v
|              +---------------+       +-----------------------+
|              |  4a. RESOLVED |       | Turn t < Max Turns?   |
+--------------+ Output diff & |       | Yes: Feed error back  |
               | telemetry     |       | No: Fail-Closed       |
               +---------------+       |     Rollback to base  |
                                       +-----------------------+
```

---

## 2. Invariants & Guarantees

1. **Active Baseline Verification:** The loop first falsifies the defect using Technique 2. If the tests already pass, the loop terminates immediately (`ALREADY_PASSING`) without touching any code.
2. **Deterministic Delta Synchronization:** Between turns, `uv run lda index --delta` re-indexes the AST in `<30ms` so subsequent retrieval queries always reflect the current working tree state.
3. **Multi-Turn Convergence:** When a candidate patch produces a secondary syntax error or fails an assertion, the new traceback is extracted and passed to the next generation turn as iterative feedback.
4. **Fail-Closed Rollback:** If the loop exhausts its turn budget without passing all falsifiers, the original file content is restored byte-for-byte, ensuring no broken intermediate states leak into the repository.

---

## 3. CLI Invocation

The proficiency harness is located at `.agents/proficiencies/autofix-swe-loop/scripts/autofix_harness.py`:

```bash
# Execute autonomous repair loop with max 3 turns
python3 .agents/proficiencies/autofix-swe-loop/scripts/autofix_harness.py \
  --task "Fix list bounds error in memory window compactor" \
  --target-file "vanguard/packages/agency/compactor.py" \
  --max-turns 3 \
  --json
```

---

## 4. Telemetry & Output Schema

```json
{
  "status": "RESOLVED",
  "task": "Fix list bounds error in memory window compactor",
  "target_file": "vanguard/packages/agency/compactor.py",
  "test_command": "python3 -m unittest test.agency.test_compactor -v",
  "total_turns": 2,
  "total_tokens": 348,
  "total_duration_seconds": 3.42,
  "patch_diff": "--- a/vanguard/packages/agency/compactor.py\n+++ b/vanguard/packages/agency/compactor.py\n@@ ... @@\n",
  "history": [
    {
      "turn": 1,
      "duration_seconds": 1.82,
      "lda_delta_seconds": 0.024,
      "tokens": 165,
      "falsifier_status": "FAIL",
      "falsifier_summary": "AssertionError: expected 5 items, got 4"
    },
    {
      "turn": 2,
      "duration_seconds": 1.58,
      "lda_delta_seconds": 0.022,
      "tokens": 183,
      "falsifier_status": "PASS",
      "falsifier_summary": "All tests passed successfully"
    }
  ]
}
```
