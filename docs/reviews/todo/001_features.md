# Competitor Feature Harvest & Atoms Reference

> **Status**: Reference Note for Post-v0.5.0 Roadmap & Harvest Ideas
> **Scope**: External competitor atoms (OpenCode, Claude Code, mini-SWE-agent, Aider, Codex, Pi) to evaluate for future milestones.

---

## 1. Competitor Harvest Atoms & Source Map

| Product | Feature / Atom to Harvest | Implementation Target in Vanguard Architecture |
|---|---|---|
| **[Aider](https://aider.chat/2023/10/22/repomap.html)** | Tree-sitter polyglot repository map | As an AST-based `IndexPort` adapter in `vanguard/packages/adapters/stores/` |
| **[Claude Code](https://docs.anthropic.com/en/docs/claude-code/sdk)** | Subagent context isolation (`Task`), compact-on-overflow | Declared via manifest pack + recursive `spawn` |
| **[mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent)** | 100-line paginated file viewer, lint-on-edit receipts, empty exec acks | Adapter observation receipts (`fs.read`, `patch.apply`, `proc.exec`) |
| **[OpenCode](https://opencode.ai/)** | Provider-agnostic CLI, `AGENTS.md` context injection, permission UX | Manifest loader + CLI `AutonomousGrant` |
| **[Pi coding agent](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent)** | Lean prompt footprint (<1,000 tokens), 4 core primitives (`read`, `write`, `edit`, `bash`) | Ultra-lean manifest pack (`vg-code-pi-shaped`) |
| **[Reasonix](https://github.com/)** | Skills index in frozen prefix (≤4,000 chars), cache miss attribution | Prompt compiler prefix assembly + telemetry |

---

## 2. Recipe: How to Adopt a Feature without Bloating Core

1. **Pack Gene**: Add to `vanguard/packages/agency/manifests/<id>/` (`system-prompt.txt`, `aliases.json`, `context-policy.json`).
2. **Adapter Behaviour**: Enhance observation receipts in `vanguard/packages/adapters/` (e.g. pagination, linter receipt).
3. **Port & Adapter**: Implement new port in `ports/` and bind in manifest without changing kernel.
4. **Client Presentation**: Surface UX in `vanguard/clients/cli/`.
