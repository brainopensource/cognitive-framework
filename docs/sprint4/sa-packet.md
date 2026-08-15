# Senior A — no-model trust spine

Tickets: `S4-SA-001`, `S4-GATE-001` · Contract: `REQ-TRUST-001` / `TEST-TRUST-001`

Complete the episode engine far enough for a **scripted** trajectory with no model: denial, attenuation, budget exhaustion, atomicity, kill recovery, secret non-disclosure. Fake evaluator principal only (OS isolation is S5).

`TEST-TRUST-001` must pass with `OPENROUTER_API_KEY` unset. After S4-SB and S4-DD are mergeable, run `S4-GATE-001`: delete `spike/` and `slice/`; keep `slice-findings.md` content by moving notes under `docs/sprint2/` if needed before deletion.

Must not wire OpenRouter into the default path.
