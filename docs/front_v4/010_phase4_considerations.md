# 010 — Phase-4+ considerations (Proposed)

Status: `Proposed`  
Date: 2026-08-16  
One page. Not a delivery kit.

## In scope later

- Branded standalone editor (Code-OSS reversal in 009).
- Extra installers (MSI, notarized macOS, AppImage).
- Named Pipe / TCP transports **after** the daemon owns them (J5).
- Optional enterprise packaging (private extension gallery, air-gap npm mirror).

## Out of FE scope (do not invent in the client)

- SIEM connectors in the TUI or webview.
- DLP / egress policy in the client. Egress is daemon / kernel / sandbox — raise a Joint note if the product needs a new event or receipt field.
- Client-side SSO as a substitute for operator Ed25519 (ADR-0062). Identity federation, if ever required, is a backend + org concern.

## Now

Deliver FE-A and FE-B against the frozen daemon. File J1–J5 instead of workarounds.
