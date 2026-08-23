---
status: living
id: engineering-testing-falsifiers
class: how-to
authority: descriptive
canonical_for:
  - testing-and-falsifiers-guide
source_of_truth:
  - docs/SPEC.md
  - docs/02_decisions/INDEX.md
derived_from:
  - test/
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: lead-documentation-engineer
version: "0.6.1"
last_verified: 2026-08-21
supersedes: []
superseded_by: null
---

# Testing Strategy & Red Falsifier Discipline

> **Status:** `AS_BUILT`.

---

## 1. Red Falsifier Proof Obligations
Before writing production code for a requirement, an engineer must:
1. Identify the allocated `RF-*` identifier from [`docs/02_decisions/INDEX.md`](../02_decisions/INDEX.md#canonical-rf-falsifier-allocation-register).
2. Write a dedicated falsifier test file under `test/falsifiers/` (e.g. `test_rf23_trajectory_content.py`).
3. Run the test and confirm it fails for the diagnosed defect (**RED CONFIRMED**).
4. Implement the minimal production change.
5. Confirm the test turns green without breaking existing suites (**GREEN**).

---

## 2. Hermetic Execution Rules
- No live network requests during tests.
- Model adapters use cassette replays (`adapters/models/cassette.py`) or fakes.
- API keys (`OPENROUTER_API_KEY`, `OPENAI_API_KEY`) remain unset during automated test runs.
