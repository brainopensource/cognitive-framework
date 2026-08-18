# S20-G-03 — Proven claims only (v0.4.5-beta)

**Date:** 2026-08-17 · **Owner:** GAMMA · **REQ-TRUST-001**  
**Branch:** `feat_sprint_special` → prepare `main` (this document does not merge).

## You may say

- Effects go through `Kernel.dispatch`; spawn is fail-closed at agency and sealed at the kernel (`ADR-0067`).
- `vg-code-default` is a product pack (IndexPort, skills, aliases, approval modes).
- `lab/run.py` is a stdlib shim; `python3 -m vanguard.packages.runtime.lab_driver` runs a real `HarnessSession`. It computes no outcome of its own.
- Episode memory is the ledger; `tools/export_coding_session.py` projects `vg.coding-session.v1` (no second session DB).
- Coding LAM keeps a **declared** four-task denominator; missing dirs stay in it (ALFA `9192be1`: 4 present / 0 missing).
- MOCK can loop (ALFA: 4 turns → `attempts_exhausted`; tape is not a gold patch). INTERACTIVE vs BENCHMARK proved against `StandardPolicy`.
- Ollama was reachable; live dogfood did **not** `oracle_green`. Several `instrument_error`s were our defects (session `kind`, probe, tool shape), then labelled.

## You may not say

- We passed GTS-13C Ch. 10 Q2 or Q3, or beat OpenCode / Claude Code / Aider.
- The coding CLI is a daily driver, or any task is `oracle_green`.
- A published A/A lift or SWE number (S9-J-03 unsigned).
- The OpenRouter key incident is closed (`S7-J-04`).
- MCP is supported (`ADR-0066` is rules, not an adapter).
- GUI / daemon (`FE-N1`) ships in 0.4.5.

## Merge checklist (PL)

Do not merge until these are green **on the merge commit**:

- `python3 -m unittest discover -s test/runtime -t .`
- `python3 -m unittest discover -s test/agency -t .`
- `python3 -m unittest discover -s test/adapters -t .`
- `python3 -m unittest test.lab.test_coding_instrument`
- `python3 tools/check_boundaries.py`
- `python3 tools/check_tcb_budget.py`
- `python3 tools/scan_secrets.py`
- `lab/run.py` still delegates only (no fabricated `turnCount`)

ALFA reported **351** runtime tests OK @ S22 `557191e`. BETA S22 `9e90c00`. S21-A 337 @ prior close. GAMMA does not re-attest from this session.

**v0.5** (not this tag): concept proposal `docs/scrum/sprints/wave20/evidence/v050-concept-lock-proposal.md`. Do not implement TUI here.
