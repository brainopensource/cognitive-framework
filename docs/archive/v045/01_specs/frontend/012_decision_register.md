---
id: FE-12
file: 012_decision_register.md
title: "Vanguard v4.0 — Frontend Decision Register & Anti-Patterns"
version: 4.0.0
status: LIVING
authority_scope: >
  Frontend architectural decision records (ADRs), locked design choices,
  anti-patterns, and merge review checklists.
supersedes: none
superseded_by: none
budget_words: 2500
owners: [Tech Lead]
last_reviewed: 2026-08-17
---

# Vanguard v4.0 — Frontend Decision Register & Anti-Patterns

> **Who this is for.** Technical leads, reviewers, and frontend engineers verifying PR compliance.

---

## 1. Locked Frontend Architectural Decisions

| Decision | Disposition & Citation |
|---|---|
| **Wire Protocol & Daemon** | Cite **ADR-0062** (vg.4 NDJSON UDS, 1 MiB max frame, no JSON-RPC). |
| **Operator Signatures** | Cite **ADR-0062** (Ed25519, RFC 8785 Canonical JSON). |
| **IDE Architecture** | **Locked by D3**: Standalone GUI IDE app (Phase 2). VS Code extension is VOID. |
| **Frontend Lanes** | **Locked by D4**: FE-1 (Client Core), FE-2 (CLI TUI), FE-3 (GUI IDE). |

---

## 2. Forbidden Frontend Anti-Patterns

- Direct typecasting of daemon JSON without validation (`CT-03`).
- Silent fallback to mock data when in live mode.
- Empty `argsDigest` / `descriptorDigest` presented as a valid cryptographic signature.
- Client-side traversal of `vanguard/packages/` for manifest discovery.
- Adding unbacked command verbs that the daemon does not implement.
- Submoduling competitor runtime loops.

---

## 3. Merge Review Checklist

- [ ] Files are placed under `vanguard/clients/client-core/`, `vanguard/clients/cli/`, or `vanguard-gui/` only.
- [ ] Event kinds strictly $\subseteq$ VG-04 §12.2.
- [ ] No undeclared daemon verbs invented.
- [ ] Offline fixtures labelled `source: mock`.
