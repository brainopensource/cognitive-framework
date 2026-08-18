# SOP: Tool Schema Harvesting & Single-Action Translation (S21-G-03 / S22-B-04)

## Context & Constraint
- Commercial and open-source models trained on OpenCode or Claude Code architectures frequently attempt parallel or batched tool calls (e.g., executing a `Read` and `Edit` simultaneously in a single turn).
- Vanguard's kernel enforce a strict turn discipline: **one proposal $\to$ one classification $\to$ one kernel dispatch $\to$ one observation receipt**. Multiple action proposals fail closed as `instrument_error:multi_action_proposal`.

## Standard Operating Procedure for Pack Authors
1. **Schema Description Injection:** Every tool schema must explicitly state `Single action; do not emit parallel calls.` in its description.
2. **System Prompt Discipline:** The pack system prompt must emphasize the mandatory single-action turn invariant in the primary instructions.
3. **Turn-by-Turn Skill Scaffolding:** Skill cards demonstrating multi-file setups must sequence operations explicitly as Turn 1, Turn 2, and Turn 3, rather than presenting a batch block.
4. **No Imported Loops:** Never import or emulate client-side tool batching engines; preserve strict Vanguard kernel single-action dispatch semantics.
