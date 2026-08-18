---
id: FE-10
file: 010_phase4_considerations.md
title: "Vanguard v4.0 — Enterprise Governance & Security Scope"
version: 4.0.0
status: PROPOSED
authority_scope: >
  Long-term enterprise considerations, client governance boundaries,
  and out-of-scope non-claims for frontend clients.
supersedes: none
superseded_by: none
budget_words: 1500
owners: [Tech Lead]
last_reviewed: 2026-08-17
---

# Vanguard v4.0 — Enterprise Governance & Security Scope

> **Who this is for.** Security architects and frontend developers evaluating enterprise features.

---

## 1. Planned Future Scope (Post-v0.5.0)

- Language server integration in the GUI editor slot.
- Native enterprise platform installers (MSI, notarized macOS, AppImage).
- Windows Named Pipe & TCP socket support once daemon implements them (J5).
- Passive DAG playback of knowledge graphs and playbooks.

---

## 2. Explicit Non-Claims for Frontend Clients

- No client-side SIEM/DLP (egress filtering is strictly enforced by daemon/kernel/sandbox).
- No client-side SSO bypass of the operator Ed25519 signature requirement (ADR-0062).
- No VS Code marketplace extension distribution.
