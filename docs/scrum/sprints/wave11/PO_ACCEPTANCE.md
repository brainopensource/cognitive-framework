# Wave 11–13 — PO acceptance (coding harness backend)

Not a second board. Status lives on `docs/scrum/roadmap_backend.md`.

## Product

`vg-code-default` compiles into an isolated episode that can **inspect → edit → pytest** on a workspace. Greenfield and bugfix are the same `lab/run.py` / `HarnessSession.run` path. Two modes already exist: `interactive=True` (approvals) and `interactive=False` (BENCHMARK fail-closed).

## Done when

1. `lab/run.py` is not a one-shot stub: `turnCount` comes from the ledger (`ProposalProduced`), stop on allowlisted `proc.exec` green or budget.
2. Privileged verbs suspend for a human in interactive mode and deny without a human in benchmark mode.
3. Session measurement is `python3 tools/export_coding_session.py --jsonl <ledger.jsonl>` (schema `vg.coding-session.v1`). No second session database.
4. Pack may declare `skill` genes; prefix index is `format_skill_index` (≤4000 chars). Bodies are files the model `fs.read`s.
5. Todo is a workspace file the model patches. Not a kernel verb.
6. MOCK dogfood dirs exist. **Q2 stays `[TODO]`** until a human runs live DOGFOOD-01..03 with no mid-run hand-patch.

## Human-only (not ALFA/BETA)

- Rotate OpenRouter key (`S7-J-04`).
- Spend sign-off (`S9-J-03`).
- Live Q2 execution (`S8-J-03`).
