---
id: arch.composition.extensibility
canonical_id: arch.composition.extensibility
class: architecture
authority: descriptive
truth_plane: AS_BUILT
status: living
implementation_status: IMPLEMENTED
owner: composition-extensibility
canonical_for:
  - composition boundary
  - plugin lifecycle
  - pack responsibility
  - extension taxonomy
purpose: Detail the extension model, composition compiler, activation lifecycle, and hexagonal boundary constraints.
audience:
  - developer
  - architect
  - contributor
analysis_subject_sha: d639ec4bda5ea7d8836a182393498a31fc43ea1a
version: 0.9.2a2
last_verified: 2026-08-31
evidence:
  - E-B-012
  - E-B-017
  - E-B-021
  - E-B-050
  - E-B-053
  - E-B-054
relationships:
  - arch.system.overview
  - ref.manifests
  - ref.ports
  - guide.add-pack-tool
  - guide.add-adapter-provider
reviewer: documentation-specialist
confidence: high
---

# Composition & Extensibility Architecture

## Purpose
This document is the canonical architecture owner for the Vanguard extension taxonomy, declarative composition compilation (`compose.py`), plugin dynamic discovery and activation lifecycles, and hexagonal boundary constraints.

## Scope
- The two-tier extension model: Domain Packs (`packs/`) versus Hexagonal Adapters (`adapters/`).
- The composition compiler and `FrozenComposition` immutable representation.
- Component activation lifecycle and security verification (`activation.py`).
- Hexagonal boundary enforcement rules (`domain <- ports <- kernel <- agency <- runtime -> adapters`).

## Non-responsibilities
- Exact JSON Schema fields for manifests (owned by [`ref.manifests`](../reference/manifests.md)).
- Step-by-step authoring tutorials (owned by [`guide.add-pack-tool`](../guides/add-pack-or-tool.md) and [`guide.add-adapter-provider`](../guides/add-adapter-or-provider.md)).
- Kernel capability and budget mediation (owned by [`arch.trust.kernel`](kernel.md)).

## AS_BUILT Status
- `IMPLEMENTED` — Pure hexagonal dependency inversion and manifest composition compilation are fully operational in `vanguard.packages.runtime.compose` and `vanguard.packages.runtime.activation`.

---

## 1. Extension Taxonomy & Two-Tier Model

Vanguard partitions all extensions into two strictly separated categories:

```text
┌─────────────────────────────────────────────────────────────┐
│                 TIER 1: DOMAIN PACKS (packs/)               │
│   Task cognition, custom tools, prompt policies, gates.    │
│   Implements the 5 SPIs (IPlanner, IContext, IToolkit...).  │
└─────────────────────────────────────────────────────────────┘
                               ▲
                               │ Composed by Runtime
┌──────────────────────────────┴──────────────────────────────┐
│             TIER 2: INFRASTRUCTURE ADAPTERS (adapters/)     │
│   Model providers, Bubblewrap sandbox, SQLite WAL stores,   │
│   Evaluator daemons. Implements ports behind SPI contracts.  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. The Composition Compiler (`compose.py`)

Agent configurations are parsed and compiled into an immutable `FrozenComposition` before execution:

1. **Manifest Loading**: `ManifestLoader` reads `manifest.json` (`mhf.manifest/2`), resolving component class paths and tool definitions.
2. **SPI Binding**: The compiler validates that declared classes implement the required SPI protocols (`IPlanner`, `IContextManager`, `IToolkit`, `IMemoryEngine`, `IEvaluationGate`).
3. **Digest Computation**: The compiler computes `composition_digest = SHA256(JCS(manifest_dict))`. Any modification to tools, prompts, or components alters this digest, preventing undetected configuration drift.
4. **Output**: Produces a `FrozenComposition` object containing instantiated components and immutable metadata.

---

## 3. Component Activation Lifecycle (`activation.py`)

Component activation proceeds through explicit lifecycle stages managed by the runtime registry:

1. **Discovery**: Scanning registered pack directories and entry points.
2. **Resolution**: Dynamic import and symbol resolution.
3. **Verification**: Contract validation asserting that components do not violate boundary rules or import forbidden layers.
4. **Activation**: Binding components to active `HarnessSession` and emitting `PluginActivated`.
5. **Quiescence**: Safe cleanup upon episode termination.

---

## 4. Hexagonal Boundary Constraints (`INV-B-001`)

The architecture enforces strict unidirectional dependency boundaries:

$$	ext{domain} \leftarrow 	ext{ports} \leftarrow 	ext{kernel} \leftarrow 	ext{agency} \leftarrow 	ext{runtime} ightarrow 	ext{adapters}$$

### Enforced Rules
- **Domain**: Pure Python standard library only. Zero imports of higher layers or external dependencies.
- **Ports**: Interface protocols only. Zero concrete adapter or runtime imports.
- **Kernel**: Imports only `domain` and `ports`. Domain-blind; $\le 1438$ logical LOC budget.
- **Agency**: Turn cognition. Imports `domain`, `ports`, `kernel`. No evaluator imports.
- **Runtime**: Orchestration and lifecycle. Composes all layers into sessions.
- **Adapters**: Concrete implementations. Must import only `domain` and `ports`. Adapters **must never** import `kernel` or `agency`.

## 5. Product applications: thin app, thick composition

`apps/` is a client slot, not a home for another orchestration substrate. A
first-party product application may validate a request, select a manifest and
preset, invoke the shared runtime application service, and shape a result for a
transport. It MUST NOT own a second turn loop, event writer, tool broker,
provider client, checkpoint store, evaluator, or authorization path.

Domain cognition belongs to the selected pack/composition:

| Concern | Canonical owner |
|---|---|
| Request/result ergonomics and preset selection | `apps/<product>/` |
| Task planner, context policy, domain failure interpretation, completion policy | `packs/<domain>/` and manifest-selected components |
| Generic model, index, sandbox, environment, memory and store contracts | `ports/` |
| Concrete infrastructure | `adapters/`; adapters never import `apps/` or pack policy |
| Composition, lifecycle, ledger, checkpoints and child runtime | `runtime/` |
| Authorization, budgets and effect mediation | domain-blind `kernel/` |

Repository-intelligence features such as symbol lookup, dependency edges, test
mapping, history priors, or optional external indexes must enter through a
generic port and normalized values. An adapter may implement the port; a code
pack may decide how to rank the observations; an app may select the policy.
Reversing that dependency—for example, an adapter importing
`apps.coding_max`—is a boundary violation even when the prototype is stored
outside the production tree.

The same rule applies to verification. A code pack defines which checks are
applicable and interprets their receipts. Execution occurs through the mediated
environment/sandbox path, and independent evaluation remains exterior. Direct
host `subprocess` or provider HTTP inside product or pack orchestration is not a
shortcut around those contracts.

Design reports and executable prototypes under `docs/reports/` are
non-authorizing inputs. Their paths are never production owners, and their
green demonstrations do not establish composition, boundary, or release
acceptance against the current source subject.

---

## Implementation Evidence

- **Composition Compiler**: `vanguard/packages/runtime/compose.py` (`compose_harness`, `FrozenComposition`).
- **Activation Management**: `vanguard/packages/runtime/activation.py`.
- **Registry Services**: `vanguard/packages/runtime/registry/`.
- **Boundary Linter**: `tools/linters/check_boundaries.py` (passes across all source files).
- **Composition Tests**: `test/contracts/test_a1_canonical_composition.py`, `test/contracts/test_manifest_v2_graph.py`.
