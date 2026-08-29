# 10. Documentation Folder Proposed Structure

### Documentation Architecture and Target Folder Structure

The Vanguard 0.9.x documentation reset must not merely delete obsolete Markdown; it must replace the current fragmented documentation taxonomy with a small, explicit, predictable information architecture. The current numbered structure (`01_law/`, `02_decisions/`, `03_execution/`, `04_architecture/`, `05_contracts/`, `06_protocols/`, `07_engineering/`, `08_theory/`, `09_diagrams/`, `09_tools/`, `_archive/`) should be treated as legacy organization. Preserve only information that remains technically necessary, migrate it into the new structure below, and then remove the obsolete directories rather than maintaining two parallel documentation systems.

The preferred active structure is:

```text
docs/
├── README.md
├── SPEC.md
│
├── architecture/
│   ├── overview.md
│   ├── system-context.md
│   ├── components.md
│   │
│   ├── runtime/
│   │   ├── execution-model.md
│   │   ├── kernel.md
│   │   ├── agency.md
│   │   ├── orchestration.md
│   │   ├── events-ledger.md
│   │   ├── artifacts.md
│   │   ├── recovery.md
│   │   └── concurrency.md
│   │
│   ├── extensibility/
│   │   ├── agents.md
│   │   ├── plugins.md
│   │   ├── packs.md
│   │   ├── tools.md
│   │   ├── models.md
│   │   ├── evaluators.md
│   │   └── adapters.md
│   │
│   ├── state/
│   │   ├── identity.md
│   │   ├── memory.md
│   │   ├── persistence.md
│   │   └── configuration.md
│   │
│   └── diagrams/
│       ├── system.md
│       ├── runtime.md
│       ├── agent-lifecycle.md
│       └── recovery.md
│
├── reference/
│   ├── contracts/
│   ├── protocols/
│   ├── events.md
│   ├── configuration.md
│   ├── cli.md
│   ├── service-api.md
│   └── schemas.md
│
├── guides/
│   ├── development.md
│   ├── testing.md
│   ├── debugging.md
│   ├── add-agent.md
│   ├── add-plugin.md
│   ├── add-pack.md
│   ├── add-tool.md
│   ├── add-model.md
│   ├── add-adapter.md
│   ├── create-workflow.md
│   ├── benchmarking.md
│   └── release.md
│
├── decisions/
│   ├── README.md
│   └── only-current-and-important-ADRs.md
│
├── execution/
│   ├── milestones.md
│   ├── backlog.md
│   ├── sprint_active.md
│   └── sprint_upcoming.md
│
└── theory/
    ├── README.md
    ├── causal-computation.md
    ├── resource-model.md
    ├── agent-composition.md
    ├── evaluation-and-learning.md
    └── self-improvement.md
```

Each top-level directory has exactly one purpose.

`architecture/` explains **how AETHER is structured and how its major subsystems interact**. This is where the Kernel, Agency layer, Runtime, orchestration, event ledger, artifacts, recovery, concurrency, memory, plugins, packs, tools, models, evaluators, adapters, identities and configuration should be explained. These pages describe responsibilities, boundaries, data flow, lifecycle, state transitions, causal relationships and important implementation constraints. They must not duplicate every class or function.

`reference/` contains **exact technical facts that developers need to look up**. Contracts, protocols, event vocabulary, schemas, CLI semantics, service commands and configuration fields belong here. Reference documentation should be precise and close to the actual code/schema representation. If information answers “what is the exact shape, field, command, event, interface or protocol?”, it belongs here rather than in architecture.

`guides/` contains **task-oriented development instructions**. A developer asking “how do I add a plugin?”, “how do I create an agent?”, “how do I add a tool?”, “how do I test a new adapter?”, or “how do I create a workflow?” should find one short guide instead of reconstructing the procedure from ADRs, architecture documents and old sprint plans.

`decisions/` contains only **small, currently relevant architectural decisions whose rationale is not obvious from code, architecture documentation or contracts**. ADRs must not become a second specification, a project history, a research paper, a milestone report, a design tutorial, or a development diary. The Vanguard 0.9.x reset should aggressively reduce the existing ADR set. If an old ADR still contains an important current decision, extract that decision into a new concise ADR and delete the historical document from the active tree. Git preserves the original reasoning.

`execution/` contains only **current project execution state**: milestones, backlog, active work and immediately upcoming work. It must never become long-term architectural documentation or historical project management. Completed historical execution material belongs in Git history, not in the active context.

`theory/` exists only for **the mathematical, scientific or conceptual material that genuinely helps explain AETHER's design**: causal computation, resource/budget models, agent composition, evaluation, learning, metacognition or self-improvement. Theory must be clearly separated from implemented architecture. A theoretical idea must not appear to be a production feature merely because it has a Markdown file.

Subsystems must therefore be documented as a hierarchy inside the appropriate information category rather than becoming independent top-level documentation silos. For example, the Kernel should have an architectural page such as `architecture/runtime/kernel.md`, exact kernel-related contracts should live under `reference/contracts/`, and instructions for modifying or testing kernel-sensitive code should live in `guides/`. The same rule applies to plugins, agents, orchestration, memory and events. This prevents a new `kernel/`, `plugins/`, `agents/`, `events/`, `runtime/`, `memory/`, and `orchestration/` documentation tree from each accumulating its own duplicated architecture, reference material and tutorials.

The documentation should explicitly model the major AETHER building blocks:

```text
AETHER
├── Kernel / Authority / Capabilities / Budgets
├── Agency / Turn Semantics / Context
├── Runtime / Composition / Lifecycle
├── Events / Ledger / Reducers / Projections
├── Artifacts / Content-Addressed Storage
├── Persistence / Replay / Recovery / Checkpoints
├── Agents / Scope / Lineage / Spawn
├── Workflow / Topology / Scheduling / Concurrency
├── Memory / Retrieval / Context
├── Plugins / Packs / Tools
├── Models / Routing
├── Evaluation / Measurement / Telemetry
└── Clients / Commands / Transports
```

These are architectural building blocks, not necessarily folders at the root of `docs/`. They should be documented at the level where understanding them is useful without reproducing the source tree.

The final test for the documentation architecture is simple: a new Senior Engineer or AI coding agent should be able to answer four different questions without reading historical documents:

1. **What is AETHER and how is it architected?** → `SPEC.md` + `architecture/`
2. **What is the exact contract or protocol?** → `reference/`
3. **How do I implement or extend something?** → `guides/`
4. **Why was a non-obvious architectural choice made?** → `decisions/`

If information does not clearly belong to one of those purposes, it should be questioned before being retained. The goal of the reset is not to rename the current documentation tree; it is to eliminate duplicated authority, historical context pollution, and subsystem documentation sprawl, leaving one small and coherent documentation system for the current Vanguard/AETHER product.


# TODO

┌────┬──────────────────────────────────────┬─────────────────────────────┬───────────────────────────┐
│ #  │ FAZER                                │ OSS / IA                    │ OUTPUT                    │
├────┼──────────────────────────────────────┼─────────────────────────────┼───────────────────────────┤
│ 1  │ Congelar estrutura-alvo da Section10 │ Seu plano                   │ target-taxonomy.yml       │
│ 2  │ Inventariar toda documentação        │ Python + Git + rg           │ inventory.jsonl           │
│ 3  │ Extrair Markdown/Office/PDF          │ Pandoc + Docling            │ documentos normalizados   │
│ 4  │ Extrair títulos/headings/links       │ Markdown parser             │ headings/links JSONL      │
│ 5  │ Classificar docs legadas             │ Scripts + IA                │ migration-matrix.jsonl    │
│    │                                      │                             │ KEEP/MERGE/SPLIT/etc.     │
│ 6  │ Mapear cada doc → destino Section10  │ IA + regras determinísticas │ target_path + target_id   │
│ 7  │ Agrupar por assunto                  │ scripts + IA                │ kernel/events/agents/...  │
│ 8  │ Conferir contra código real          │ rg + ast-grep + SCIP        │ evidence/code-map         │
│ 9  │ Reconciliar conflitos                │ Codex/Claude                │ reconciliation.jsonl      │
│ 10 │ Gerar documentos novos compactos     │ IA + templates              │ candidate-docs/           │
│ 11 │ Adicionar frontmatter padronizado    │ YAML + JSON Schema          │ docs estruturadas         │
│ 12 │ Criar links entre docs/código/testes │ scripts + ast-grep/SCIP     │ relations.jsonl           │
│ 13 │ Gerar índice para IA                 │ Python + jq/yq               │ catalog.jsonl             │
│ 14 │ Validar estrutura                    │ markdownlint                 │ Markdown consistente      │
│ 15 │ Validar terminologia                 │ Vale                        │ ontology drift detectada  │
│ 16 │ Validar referências                  │ Lychee                      │ links íntegros            │
│ 17 │ Gerar diagramas                      │ Mermaid                     │ diagrams-as-code          │
│ 18 │ Publicar docs                        │ MkDocs Material             │ portal navegável          │
│ 19 │ Testar retrieval humano + IA         │ Codex/Claude + benchmark    │ métricas                  │
│ 20 │ Substituir docs antigas              │ Git                         │ docs/ final                │
└────┴──────────────────────────────────────┴─────────────────────────────┴───────────────────────────┘