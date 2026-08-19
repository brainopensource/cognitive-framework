# TASK: Standalone Implementation of Wave 6 (Milestone M5: Meta-Cognition & Skill Synthesis)

### 🎯 ROLE: Senior AI Specialist (PhD)
### 📁 WORKSPACE DIRECTORY: experiments/m5_meta_cognition_phd/
### ⚠️ STRICT DIRECTIVE: ZERO GIT COMMANDS · DO NOT MODIFY EXISTING CORE CODE

---

### 0. Normative Context & Objective
Per `docs/SPEC.md` (§6 & §7), `docs/02_roadmap/milestones.md` (M5), and `docs/04_annex/MEASUREMENT.md`, build a complete, standalone, production-grade implementation of **Wave 6 (Milestone M5: Meta-Cognition & Evolutionary Tuning)** entirely inside your assigned directory: `experiments/m5_meta_cognition_phd/`.

---

### 1. Mandatory Technical Requirements (Per Normative Specs)

#### A. Trajectory Ingestion & Failure Diagnosis
- Ingest immutable execution receipts (`mhf.trajectory/1`) containing event sequences, error traces, tool call counts, and token/USD spend.
- Implement root-cause diagnosis for failure modes (`CONTEXT_OVERFLOW`, `TOOL_SCHEMA_ERROR`, `TEST_ASSERTION_FAIL`, `BUDGET_EXHAUSTION`).

#### B. Declarative Configuration Mutation Engine
- Compute updated `harness.yaml` parameters for subsequent retry episodes (e.g., adjusting context budgets, repair rounds, and model tier escalation: Tier 1 Local → Tier 2 DeepSeek → Tier 3 Frontier).
- Enforce bounded computational limits and prevent degenerate infinite retry loops.

#### C. Skill Procedure Card Synthesizer
- When an episode succeeds (verified by test passes), extract the problem pattern and solution steps into a persistent Markdown skill procedure card (`skills/<slug>.md`).

#### D. Standalone Test Suite
- Provide a complete, self-contained unit test suite verifying log ingestion, parameter mutation, and skill card generation.

---

### 2. Required Files in Your Directory
1. `README.md` — Complete architectural design, mathematical rationale, and usage instructions.
2. `meta_reflector.py` — Complete, fully-typed Python module implementing the outer reflector and skill synthesizer.
3. `test_meta_reflector.py` — Standalone unit test suite (must execute with `python3 -m unittest` and pass 100%).
