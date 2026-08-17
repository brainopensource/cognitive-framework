# Reference: vg-code-claude-shaped

## Public Sources Read
- Anthropic Claude Tool Use Documentation & Computer Use / Artifacts specification (public developer guides).
- Anthropic Claude 3.5 Sonnet system prompts and tool calling schemas.

## What Was NOT Copied
- Anthropic's proprietary multi-tenant scheduler, backend prompt optimizers, or server-side tool calling orchestration.
- Any non-public Anthropic internal architecture.

## Honesty Label
This pack reconstructs the **tool surface (view_file, edit_file, bash) + prompt shape + client-side policies (tier-escalation routing, result eviction compaction, low approval friction)** over Vanguard's deterministic runtime. Vanguard depth-1 serial execution stands (`D-02`, `D-09`).
