# Reference: vg-code-default (Product-Default Pack)

## Public Sources
- [OpenCode](https://opencode.ai/): Provider-agnostic client, `AGENTS.md` discovery into context, tool alias patterns.
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/sdk): Tool naming conventions (`Read`, `Grep`, `Edit`, `Bash`), compact-on-overflow intuition.
- [mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent): 100-line paginated file viewer, succinct grep matching, lint receipts.
- [Aider](https://aider.chat/2023/10/22/repomap.html): Tree-sitter repository map index as an observation source (`IndexPort`).
- [Pi coding agent](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent): Four minimal primitives, concise system prompt.

## What Was NOT Copied
- No external agent runtime scheduler or proprietary `while True` loops.
- No vendored source code or competitor libraries.
- No in-process memory mutation of frozen system prefix layers (L1–L3).

## Honesty Label
This pack defines the canonical Vanguard product-default configuration:
- Claude aliases: `Read`/`Grep`/`Edit`/`Bash`
- OpenCode `AGENTS.md` discovery
- Aider-style `IndexPort` repository map observation
- Pi-length inspect-then-edit prompt with `.vanguard/todo.md` goal tracking
- Thickened ACI schemas with skill artifacts (`skills/`)
Authority remains strictly mediated by the kernel.
