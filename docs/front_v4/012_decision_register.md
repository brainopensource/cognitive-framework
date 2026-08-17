# 012 — Frontend decision register (Proposed)

Status: `Proposed`  
Date: 2026-08-17  
Product ADRs live in `docs/main_v4/09_vanguard_decision_register_v040.md`. This file only tracks FE-local choices.

## Citations & Locked Decisions

| Decision | Disposition |
|---|---|
| Wire & Daemon | Cite **ADR-0062** (vg.4 NDJSON UDS, 1 MiB limit, no JSON-RPC) |
| Operator Signatures | Cite **ADR-0062** (Ed25519, RFC 8785 Canonical JSON) |
| Editor / IDE | **Locked by D3**: Standalone GUI IDE app (Phase 2). Extension-first is VOID. Code-OSS fork is out of scope. |
| Three Lanes | **Locked by D4**: FE-1 (Client Core), FE-2 (CLI TUI), FE-3 (GUI start). |

## Anti-patterns

- Casting daemon JSON to TypeScript types (`CT-03`).
- Silent mock fallback in live mode.
- Empty `argsDigest` / `descriptorDigest` presented as a successful signature.
- Reading `vanguard/packages/` from the client for “discovery”.
- Adding command names the daemon does not implement.
- Claiming JSON-RPC, `Ping`, or 4 MiB frames as current law.
- Submoduling competitor loops (Cline, Roo, OpenCode, Void).

## Checklist before merging FE work

- [ ] Path is `vanguard/clients/client-core/`, `vanguard/clients/cli/`, or `vanguard-gui/` only
- [ ] Event kinds ⊆ VG-04 §12.2 or explicitly unknown-preserved
- [ ] DoD command from ROADMAP board ran
- [ ] No Joint-scope invention
- [ ] Mock/replay labelled `source: mock`
