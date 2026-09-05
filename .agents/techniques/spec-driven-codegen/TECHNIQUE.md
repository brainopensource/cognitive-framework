---
name: spec-driven-codegen
description: >-
  Technique: Synergistic composition of lda-navigator and llama-cpp.
  Compiles token-budgeted architectural context, symbols, and test falsifiers from the
  LDA fact graph, injecting them into local LLM inference for grounded code synthesis.
version: "1.0.0"
authority: operational
composed_skills:
  - lda-navigator
  - llama-cpp
---

# Spec-Driven Code Generation (Technique 1)

**Spec-Driven Code Generation** is a composite agent technique combining:
1. **Symbolic Fact Grounding** via [`lda-navigator`](file:///home/rock-dev/Coding/cognitive-framework/.agents/skills/lda-navigator/SKILL.md)
2. **Local Neural Code Synthesis** via [`llama-cpp`](file:///home/rock-dev/Coding/cognitive-framework/.agents/skills/llama-cpp/SKILL.md)

---

## 1. Ontological Placement

$$\text{Skill (Atomic: LDA, llama.cpp)} \longrightarrow \mathbf{\text{Technique (Spec-Driven CodeGen)}} \longrightarrow \text{Proficiency (SWE Loop)}$$

While raw LLMs hallucinate non-existent imports or miss exact project conventions, and symbolic search tools cannot synthesize code, this Technique coordinates both in a single unidirectional pipeline:
1. **Resolve & Slice:** LDA extracts the exact AST slice, primary symbols, and falsifiers within a strict token budget.
2. **Context Synthesis:** Injects ground-truth symbols and interfaces into a concise prompt.
3. **Local Inference:** Queries native `llama-server` (e.g. Qwen2.5-Coder at >160 tok/s) to produce a surgical patch without external network calls or cloud costs.

---

## 2. CLI Invocation

The technique script lives at `.agents/techniques/spec-driven-codegen/scripts/generate_grounded_patch.py`:

```bash
# Generate grounded patch with automatic llama-server lifecycle
python3 .agents/techniques/spec-driven-codegen/scripts/generate_grounded_patch.py \
  --task "Fix list index bounds error in chunker" \
  --target-file "vanguard/packages/agency/compactor.py" \
  --budget 2500 \
  --json
```

If test feedback is available from a prior run, it can be passed for guided refinement:

```bash
python3 .agents/techniques/spec-driven-codegen/scripts/generate_grounded_patch.py \
  --task "Fix off-by-one error" \
  --target-file "vanguard/packages/agency/compactor.py" \
  --error-feedback "IndexError: list index out of range at line 42"
```

---

## 3. Output Schema

```json
{
  "task": "Fix list index bounds error in chunker",
  "target_file": "vanguard/packages/agency/compactor.py",
  "symbols_count": 4,
  "tests_count": 2,
  "retrieval_latency": 0.35,
  "llm_latency": 1.12,
  "completion_tokens": 184,
  "tokens_per_second": 164.2,
  "generated_code": "def chunk_text(...): ...",
  "raw_output": "```python\ndef chunk_text(...):\n...```"
}
```
