# OpenRouter Model Ceiling & Tier Fit Rules

## Fit Evaluation Rule

1. **Ceiling Tier:** A model's assigned ceiling is the highest tier ($1 \dots 5$) where it achieves `passed = true` on $\ge 1$ benchmark scenario belonging to that tier.
2. **Escalation Invariant:** A model is only evaluated on Tier $K+1$ if it successfully passes Tier $K$. Failing lower tier scenarios halts higher tier escalation (`run_escalated_ladder`).
3. **Pass Criteria:**
   - **Tier 1:** Workspace unit tests pass, no manual code patch required, $\le 8$ calls.
   - **Tier 2:** Unit tests pass, $\ge 2$ workspace files touched, $\le 12$ calls.
   - **Tier 3:** Unit tests pass, refactor maintains clean non-leaky invariants.
   - **Tier 4:** Unit tests pass + documentation/README updates present.
   - **Tier 5:** Unit tests pass + new modular architecture created.

## Model Band Assignment Matrix

| Band | Model Identifier | Tier Ceiling | Status |
| :--- | :--- | :--- | :--- |
| **Free** | `cohere/north-mini-code:free` | Tier 1 | Verified ($0) |
| **Free** | `nvidia/nemotron-3.5-lightning:free` | Tier 1 | Verified ($0) |
| **Free** | `nvidia/nemotron-3-super-120b-a12b:free` | Tier 1 | Verified ($0) |
| **Medium** | `openai/gpt-5.6-luna` | Tier 2 | Pending Paid Wave |
| **Medium** | `deepseek/deepseek-v4-flash-0731` | Tier 2 | Verified ($0) |
| **Medium** | `xiaomi/mimo-v2.5` | Tier 2 | Pending Paid Wave |
| **High** | `google/gemini-3.7-flash` | Tier 3 | Pending Paid Wave |
| **High** | `deepseek/deepseek-v4-pro-0813` | Tier 3 | Verified ($0) |
| **High** | `z-ai/glm-5.2` | Tier 3 | Pending Paid Wave |
| **Top** | *(Unspecified)* | Fail-Closed | Top band empty until named by PL |
