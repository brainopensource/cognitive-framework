# 010 — Phase-4+ considerations (Proposed)

Status: `Proposed`  
Date: 2026-08-17  
One page. Not a delivery kit.

## In scope later

- Language servers in the GUI editor slot (harvest P3 “LSP-as-IDE”).
- Extra installers (MSI, notarized macOS, AppImage) for `vanguard-gui`.
- Named Pipe / TCP **after** the daemon owns them (J5).
- RAG / knowledge graphs / playbooks — backend-first; GUI only views ledger.

## Out of FE scope (do not invent in the client)

- SIEM / DLP in TUI or GUI. Egress is daemon / kernel / sandbox.
- Client-side SSO as a substitute for operator Ed25519 (ADR-0062).
- VS Code extension marketplace / `.vsix` (VOID).
- Code-OSS fork as the IDE strategy.

## Now

FE-1 client-core, FE-2 TUI, FE-3 GUI scaffold. File J1–J5 instead of workarounds.
