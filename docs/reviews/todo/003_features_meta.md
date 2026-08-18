# Competitor Capability Gap Analysis & Future Architecture Directives

> **Status**: Future Roadmap & Capability Gap Reference
> **Scope**: Advanced coding harness features (LSP, Streaming, AST, Multi-modal) to plan for v0.6.0+

---

## 1. Competitive Capability Gap Matrix (vs Claude Code / Cline / Codex)

| Advanced Capability | Industry Standard (Claude / Cline / Codex) | Implementation Plan for Post-v0.5.0 |
|---|---|---|
| **Real-Time Tool-Use Streaming** | Live token & tool argument streaming | Async streaming generator on `ModelPort` + SSE client stream |
| **Language Server Protocol (LSP)** | Go-to-definition, find-references, live diagnostics | Add `LspPort` & language server daemon adapter |
| **AST-Aware Editing** | Tree-sitter / structural refactoring | AST patcher adapter to reduce syntax failures on complex edits |
| **Filesystem Watching** | Live `inotify` / `fsnotify` daemon | Real-time workspace change detection |
| **Multimodal / Image Input** | Image attachment inspection for UI testing | Extend wire schema & model adapters for image payloads |
| **Interactive Diff Preview & Approval UI** | Visual patch inspection before write | Ink TUI interactive approval modal |

---

## 2. Long-Term Architectural Directives

1. **Harness Strategy Sovereignty**: Manifests must declare their own execution strategy (e.g. pure free loop vs plan-guided) via configuration rather than hardcoding in `runtime/`.
2. **Playbook Rigidity Dial**: Recover multi-step workflows as playbooks with a rigidity parameter (`advisory` $\rightarrow$ `guided` $\rightarrow$ `strict`) rather than hardcoded runtime DAGs.