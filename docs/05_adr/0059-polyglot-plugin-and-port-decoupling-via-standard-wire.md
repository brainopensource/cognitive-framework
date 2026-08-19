---
adr: 0059
title: "Polyglot plugin and port decoupling via standard wire envelopes (JSON-RPC/IPC/stdio/WebSocket). Heav"
status: accepted
source_section: "11. Sprint 3–4 closure and Phase 2 authorization"
migrated_from: docs/01_specs/backend/09_vanguard_decision_register_v040.md
---

# ADR-0059: Polyglot plugin and port decoupling via standard wire envelopes (JSON-RPC/IPC/stdio/WebSocket). Heavy domain extensions in Rust, Go, TypeScript/Node, or Python must live strictly outside the TCB and connect across port adapters; the core microkernel remains minimal and language-neutral in wire schema

**Context.** Long-term GTS scaling requires specialized high-performance tooling (Tree-sitter in Rust, browser in Node, vector search in Go) without bloating or coupling the Python microkernel

**Alternative considered (and rejected).** Embed polyglot language bindings directly into the kernel

**Evidence / bound test / links.** `docs/sprint0/system-architecture-icd.md`; `vanguard/packages/ports/`

**Reversal condition.** A performance-critical path mathematically requires in-process memory sharing with kernel dispatch

**Owner · status.** Tech Lead · accepted · 2026-08-15 · accepted
