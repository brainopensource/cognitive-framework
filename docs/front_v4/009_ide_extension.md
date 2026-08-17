# 009 — Vanguard IDE — extension-first, fork deferred (Proposed)

Status: `Proposed`  
Date: 2026-08-16  
Directory name: **`vanguard-ide/`** (repository root, sibling to `vanguard/`).

## Decision (D3)

Ship a **standard VS Code extension** (`engines.vscode`, TypeScript, esbuild). Contributes: sidebar webview view, commands, CodeLens. Talks to the daemon with the same vg.4 frames as the CLI (vendored contract).

A Code-OSS / VSCodium **fork is not in scope**. Sprint estimates of a ~380 LOC fork are not a plan.

## Reversal path (Phase-4+)

If productization later requires a branded standalone editor, reopen a fork program (upstream tracking, signing, per-OS CI). Until then, keep research in the appendix; do not staff it.

## Appendix — fork research (not current work)

Debloat and `product.json` customization are relevant **only** if the reversal fires. Do not claim a specific upstream `product.json` layout as current fact; verify against the Code-OSS version you would pin at that time. Do not treat `vanguard-ide/` as a fork tree today — it is the extension package.
