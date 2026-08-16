# Dev 4 — disposable provider probe, correction, recording and process contracts

Tickets: `S1-D4-001..004` · Contract: `REQ-SCHEMA-010..012`; T0a is backlog-only

Run the provider probe only under `spike/`: direct call, no engine/kernel/grant/ledger dependency, no imports into core, and no code reuse. Preserve findings in `provider-notes.md`; the code is deleted at S4. Do not expose secrets in prompts, output or notes.

Use those notes to finish Recording; keep CorrectionRecord scope explicit; keep Process contracts finite, model-free and resumable from ledger state. Deliver schema candidates and vectors only—no cognitive loop or permanent provider integration.
