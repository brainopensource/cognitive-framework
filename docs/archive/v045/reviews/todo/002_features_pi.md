# Pi Coding Agent Architecture Reference & Innovative Mechanisms

> **Status**: Reference Document for Minimalist Agent Design & Future Ideas
> **Source**: `earendil-works/pi-coding-agent` (Mario Zechner & Armin Ronacher)

---

## 1. Context Window Economics (Ultra-Lean Cold Start)

- **System Prompt Footprint**: `< 1,000 tokens` base system prompt tax (vs 7k–10k in Claude Code).
- **Cold-Start Payload**: `~2.5k tokens` total (leaving >98% of context window for user code, AST, and logs).
- **Core Tool Surface**: Strict 4-primitive tool set (`read`, `write`, `edit`, `bash`). Specialized tools are injected dynamically via modular extensions rather than bloating the system prompt.

---

## 2. Non-Destructive DAG Session State & In-Place Branching

- **JSONL Tree Structure**: Every turn records explicit `id` and `parentId` in a tree structure rather than linear destructive compaction.
- **Tree Branching**: Allows `/fork` and `/clone` to branch exploratory refactorings without destroying root history.
- **Differential Context Folding (`Ctrl+O`)**: Dynamic folding filters large bash outputs or test logs from the model's active window while preserving complete trace history.

---

## 3. Decoupled Asynchronous Steering Queue

- **`Enter` (Steering Vector)**: Delivers immediate steering instruction to the agent immediately after current tool finishes, stopping runaway trajectories mid-flight.
- **`Alt+Enter` (Follow-up Queue)**: Delivers follow-up tasks asynchronously after the full sequence completes.

---

## 4. Four-Protocol Wire Normalization (`pi-ai`)

Maps 300+ models into 4 fundamental wire transports:
1. `OpenAI Completions` (`/v1/chat/completions`)
2. `OpenAI Responses` (`/v1/responses`)
3. `Anthropic Messages` (`/v1/messages`)
4. `Google Generative AI` (`/v1beta/models/{model}:generateContent`)