---
adr: 0066
title: "**MCP is configuration and an adapter after v0.4.3, never authority.** No MCP server, client, or too"
status: accepted
source_section: "12. Phase 3 authorization, language ratification and gate status"
migrated_from: docs/01_specs/backend/09_vanguard_decision_register_v040.md
---

# ADR-0066: **MCP is configuration and an adapter after v0.4.3, never authority.** No MCP server, client, or tool-bridge code lands until this row is accepted (it is accepted here as *rules*, not as an implementation licence). MCP may discover and name tools; it must not issue grants, widen scope, bypass `Kernel.dispatch`, or sit on the evaluator plane. An MCP-shaped tool is a capability row + adapter, same as any other verb. ACP/A2A are client protocols and do not replace VG-04

**Context.** Competitor CLIs treat MCP as the extension model. Importing that as a second authority path would recreate the kernel bypass Sprint 7 deleted

**Alternative considered (and rejected).** Ship an MCP adapter in v0.4.3; or forbid MCP forever

**Evidence / bound test / links.** `docs/reviews/doing/006_…`; S8-J-06; no `vanguard/packages/**/mcp*`

**Reversal condition.** A later ADR names the adapter package, the grant mapping, and a must-fail counterpart that an MCP tool cannot dispatch around the kernel

**Owner · status.** Tech Lead + Project Lead · accepted · 2026-08-17 · accepted
