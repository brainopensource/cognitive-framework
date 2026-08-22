---
status: living
id: contract-manifests
class: contract-reference
authority: descriptive
canonical_for:
  - manifest-schema-contract
source_of_truth:
  - docs/SPEC.md#7-harness-manifests-and-component-graphs
  - docs/05_adr/0077-named-component-graph-manifest.md
derived_from:
  - schemas/mhf/manifest.schema.json
  - vanguard/packages/domain/wire/contracts.py
applies_to:
  - v0.6.1
implementation_status: RATIFIED_NOT_IMPLEMENTED
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-21
supersedes: []
superseded_by: null
---

# Named Component Graph Manifest (`mhf.manifest/2`)

> **Schema:** `schemas/mhf/manifest.schema.json`  
> **Status:** `RATIFIED_NOT_IMPLEMENTED` (Governed by ADR-0077; target milestone: **M-3**).

---

## Structure

```json
{
  "specversion": "mhf.manifest/2",
  "name": "code-default-graph",
  "version": "1.0.0",
  "description": "Standard coding agent with AST patch, terminal, and git plugins",
  "capabilities": {
    "ceiling": {
      "fs": ["/workspace/**"],
      "generic": ["proc://exec/allow/git,pytest,ruff,python3"]
    }
  },
  "nodes": [
    {
      "id": "fs_tool",
      "plugin": "vg-plugin-fs",
      "version": "^1.0.0",
      "bindings": {
        "workspace": "/workspace"
      }
    },
    {
      "id": "terminal_tool",
      "plugin": "vg-plugin-terminal",
      "version": "^1.0.0"
    }
  ],
  "routes": {
    "default_model": "openrouter:anthropic/claude-3.5-sonnet",
    "fast_model": "openrouter:openai/gpt-4o-mini"
  }
}
```
