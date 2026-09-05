---
name: autofix-loop
description: >-
  Autonomous Closed-Loop SWE Autofix Skill. Combines LDA graph retrieval, local llama.cpp
  inference, isolated test execution, and sub-30ms AST delta synchronization to repair code defects.
version: "1.0.0"
authority: operational
---

# Autofix Loop Skill

The **autofix-loop** skill bridges Antigravity to the **Autofix SWE Loop Proficiency** (`.agents/proficiencies/autofix-swe-loop/`). It enables multi-turn, test-grounded code repair using local models and deterministic graph intelligence.

---

## Quick Reference

To run the automated repair loop:

```bash
python3 .agents/proficiencies/autofix-swe-loop/scripts/autofix_harness.py \
  --task "<defect description>" \
  --target-file "<file path>" \
  --max-turns 3
```

### Composed Components

- **Symbolic Grounding:** [`lda-navigator`](file:///home/rock-dev/Coding/cognitive-framework/.agents/skills/lda-navigator/SKILL.md)
- **Local Model Execution:** [`llama-cpp`](file:///home/rock-dev/Coding/cognitive-framework/.agents/skills/llama-cpp/SKILL.md)
- **Hermetic Test Runner:** [`test-runner`](file:///home/rock-dev/Coding/cognitive-framework/.agents/skills/test-runner/SKILL.md)
- **Architecture Spec:** See [`PROFICIENCY.md`](file:///home/rock-dev/Coding/cognitive-framework/.agents/proficiencies/autofix-swe-loop/PROFICIENCY.md)
