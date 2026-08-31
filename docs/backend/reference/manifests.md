---
id: ref.manifests
canonical_id: ref.manifests
class: reference
authority: descriptive
truth_plane: AS_BUILT
status: living
implementation_status: IMPLEMENTED
owner: packs-manifests
canonical_for:
  - mhf.manifest/2 fields
  - pack file roles
  - plugin lifecycle contract
  - topology/1 reference links
purpose: Own manifest/pack/plugin exact shapes and lifecycle states.
audience:
  - developer
  - contributor
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-08-29
evidence:
  - E-B-012
  - E-B-021
  - E-B-024
  - E-B-034
  - E-B-050
  - E-B-053
  - E-B-054
relationships:
  - arch.composition.extensibility
  - guide.compose-agent
  - guide.add-pack-tool
  - ref.schemas
reviewer: documentation-specialist
confidence: high
---

# Manifests, Packs & Plugin Schema Reference

## Purpose
This document is the canonical reference owner for the `mhf.manifest/2` schema fields, agent pack directory layouts, plugin lifecycle state contracts, and topology extension bindings.

## Scope
- `mhf.manifest/2` manifest file specifications (`manifest.json` / `pack.json`).
- Component bindings, model selectors, tool specifications, and gate configurations.
- Pack directory hierarchy (`packs/<name>/`).
- Plugin lifecycle state machine (`PluginDiscovered` $	o$ `PluginActivated` $	o$ `PluginQuiesced`).
- Topology extension specifications (`mhf.topology/1`).

## Non-responsibilities
- High-level composition architecture and resolution pipeline (owned by [`arch.composition.extensibility`](../architecture/composition-extensibility.md)).
- Step-by-step guides for authoring new agent packs (owned by [`guide.compose-agent`](../guides/compose-an-agent.md) and [`guide.add-pack-tool`](../guides/add-pack-or-tool.md)).

## AS_BUILT Status
- `IMPLEMENTED` — Manifest V2 parsing, pack validation, and plugin lifecycle verification are enforced by `vanguard.packages.runtime.compose` and `schemas/mhf/manifest_v2.schema.json`.

---

## 1. `mhf.manifest/2` Schema Contract

A manifest defines the declarative composition of an agent, its tools, gates, and capabilities:

```json
{
  "api": "mhf.manifest/2",
  "id": "code-default",
  "name": "Default Coding Agent Pack",
  "version": "0.9.1",
  "description": "Standard code editing, search, and validation pack",
  "entrypoint": "agent",
  "components": {
    "planner": "vanguard.packs.code.planner:CodingPlanner",
    "context_manager": "vanguard.packs.code.context:CodeContextManager",
    "toolkit": "vanguard.packs.code.tools:CodeToolkit",
    "memory": "vanguard.packages.adapters.stores.memory_engine:SqliteMemoryEngine"
  },
  "tools": [
    {
      "name": "view_file",
      "description": "View file content from filesystem",
      "schema": { ... },
      "category": "fs_read"
    },
    {
      "name": "replace_file_content",
      "description": "Edit contiguous block of file content",
      "schema": { ... },
      "category": "fs_write",
      "requires_approval": false
    }
  ],
  "gates": [
    {
      "name": "evaluator_gate",
      "type": "exterior_rpc",
      "endpoint": "http://localhost:10002"
    }
  ],
  "topology": {
    "api": "mhf.topology/1",
    "roles": ["primary", "reviewer"]
  }
}
```

### Manifest Fields

| Field | Type | Description |
|---|---|---|
| `api` | `string` | Manifest schema version (`"mhf.manifest/2"`). |
| `id` | `string` | Unique identifier for the agent pack. |
| `name` | `string` | Human-readable name. |
| `version` | `string` | Semantic version string. |
| `description` | `string` | Summary of pack capability. |
| `entrypoint` | `string` | Default agent role entry point. |
| `components` | `object` | Class paths for SPI implementations (`planner`, `context_manager`, `toolkit`, `memory`). |
| `tools` | `array` | Tool definitions with JSON Schemas and categories. |
| `gates` | `array` | Approval and evaluation gate definitions. |
| `topology` | `object` | Optional delegation topology specification. |

---

## 2. Pack Directory Layout

Agent packs live in `packs/<pack_name>/`:

```text
packs/code/
├── manifest.json           # Pack manifest conforming to mhf.manifest/2
├── __init__.py             # Python pack package root
├── planner.py              # IPlanner implementation
├── context.py              # IContextManager implementation
├── tools.py                # IToolkit and tool handlers
├── policies.py             # Domain-specific constraints
└── tests/                  # Hermetic unit tests for pack tools
```

---

## 3. Plugin Lifecycle State Machine

Pack plugins loaded by `vanguard.packages.runtime.registry` transition through strictly tracked lifecycle states:

```text
[ Discovered ] ---> [ Resolved ] ---> [ Verified ] ---> [ Activated ] ---> [ Quiesced ]
```

1. **`PluginDiscovered`**: Plugin manifest found on search path.
2. **`PluginResolved`**: Dependencies and Python module imports successfully resolved.
3. **`PluginVerified`**: Security boundaries and port interface compliance verified.
4. **`PluginActivated`**: Bound into runtime session and ready for turn execution.
5. **`PluginQuiesced`**: Cleanly detached upon episode completion.

---

## 4. Topology Extension (`mhf.topology/1`)

Topology definitions specify delegation roles and child agent routing:
- `mhf.topology/1` declarations are compiled by `vanguard.packages.runtime.compose` and lowered to sequential child turn executions (`arch.orchestration.delegation`).

The production code pack registers three data-selected identities:
`vg-code-fast`, `vg-code-balanced`, and `vg-code-max`. They share the default
tool and policy artifacts while varying only bounded execution ceilings and
are compiled by the same runtime composition root.

---

## Implementation Evidence

- **Manifest Schema**: `schemas/mhf/manifest_v2.schema.json`.
- **Runtime Composition**: `vanguard/packages/runtime/compose.py` (`compose_harness`, `FrozenComposition`).
- **Registry & Plugin Lifecycle**: `vanguard/packages/runtime/registry/`.
- **Contract Tests**: `test/contracts/test_manifest_v2_graph.py`, `test/agency/test_manifest_loader.py`.
