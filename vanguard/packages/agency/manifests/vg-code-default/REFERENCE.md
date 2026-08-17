# Reference: vg-code-default (Product-Default Pack)

## Public Sources
- [OpenCode](https://opencode.ai/): Provider-agnostic client, `AGENTS.md` discovery into context, tool alias patterns.
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/sdk): Tool naming conventions (`Read`, `Grep`, `Edit`, `Bash`), compact-on-overflow intuition.
- [mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent): 100-line paginated file viewer, succinct grep matching, lint receipts.
- [Pi coding agent](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent): Four minimal primitives, concise system prompt.

## What Was NOT Copied
- No external agent runtime scheduler or proprietary `while True` loops.
- No vendored source code or competitor libraries.
- No in-process memory mutation of frozen system prefix layers (L1–L3).

## Honesty Label
This pack defines the canonical Vanguard product-default configuration (Claude aliases `Read`/`Grep`/`Edit`/`Bash`, OpenCode `AGENTS.md` discovery, Pi-length inspect-then-edit prompt, thickened ACI schemas). Authority remains strictly mediated by the kernel.
