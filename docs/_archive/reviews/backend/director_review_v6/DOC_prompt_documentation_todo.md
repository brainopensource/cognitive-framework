# AETHER Documentation Greenfield Reconstruction

Act as a combined **Principal Software Architect, Staff Engineer, Senior Technical Auditor/Reviewer, Tech Lead, and PhD-level Senior Documentation Architect**.

Your task is to **reconstruct the canonical AETHER documentation essentially from scratch from the current repository**, using the existing documentation only as secondary evidence and as a final knowledge-loss safety net.

This is a **greenfield documentation reconstruction over an existing codebase**, not a document migration project.

Repository:

`Aether-D-System`

Authoritative branch:

`main`

Before doing anything else:

1. verify the branch;
2. record the exact commit SHA;
3. treat that commit as the immutable implementation baseline for this documentation reconstruction.

Three governing bootstrap documents exist under:

`docs/_archive/reviews/backend/director_review_v6/`

* `DOCUMENTATION_ARCHITECTURE_SPEC.md`
* `migration_process.md`
* `OSS_docs_tools.md`

Read these first to understand the required documentation architecture, metadata/indexing model, validation approach, and candidate OSS tooling.

However, apply the **greenfield/code-first rules below whenever the older migration-oriented wording would imply reconstructing documentation document-by-document**.

---

# 1. Primary objective

Produce a new, concise, canonical, machine-readable and human-readable documentation system describing:

1. **what AETHER actually implements today**;
2. **what AETHER intentionally plans to become**, clearly separated from current implementation;
3. **how developers use, modify, extend, test and reason about the system**.

Do not optimize for preservation of existing Markdown.

Do not reproduce the historical documentation taxonomy.

Do not mechanically summarize, merge, rewrite, or migrate every old document.

Instead:

```text
CURRENT REPOSITORY
        ↓
IMPLEMENTATION EVIDENCE
        ↓
ARCHITECTURE RECONSTRUCTION
        ↓
CANONICAL KNOWLEDGE MODEL
        ↓
NEW DOCUMENTATION
        ↓
LEGACY KNOWLEDGE AUDIT
        ↓
VALIDATED FINAL DOCUMENTATION
```

---

# 2. Two independent truth planes

Do not use one ambiguous authority hierarchy for both current implementation and future intent.

## 2.1 AS_BUILT truth

For statements describing what the system actually does now, use implementation evidence.

Primary evidence includes:

```text
production code
executable tests
schemas
contracts represented in code
configuration definitions
CLI/API behavior
runtime composition
package/module boundaries
public interfaces
benchmarks where relevant
```

The codebase is the primary evidence for implemented behavior.

Tests provide behavioral evidence but must not override clearly contradictory production behavior without investigation.

Existing descriptive documentation does not override implementation evidence.

If documentation says a capability exists but the code does not implement it:

```text
NOT IMPLEMENTED
```

or, when appropriate:

```text
PARTIAL
PLANNED
UNRESOLVED
```

Do not document it as implemented.

## 2.2 TARGET truth

Future intent is a separate knowledge plane.

Use:

```text
VISION.md
current normative target requirements
current accepted architectural decisions
active milestones
active roadmap/backlog where still intentional
relevant theory/research
```

to determine what AETHER intends to become.

Target documentation must never silently become AS_BUILT documentation.

Explicitly distinguish:

```text
IMPLEMENTED
PARTIAL
PLANNED
EXPERIMENTAL
```

## 2.3 Legacy documentation

Everything else under the previous documentation system is:

```text
SECONDARY EVIDENCE
```

Legacy documents may contain useful rationale, terminology, requirements or architectural knowledge, but they must not automatically override either:

```text
AS_BUILT implementation truth
```

or:

```text
current TARGET intent
```

---

# 3. Do not begin by reading the legacy documentation corpus

The first architecture reconstruction must be performed primarily from the repository itself.

Do not recursively read `_archive/` or all historical Markdown before establishing the current implementation model.

First inspect:

* source code;
* workspace/package manifests;
* tests;
* schemas;
* configuration;
* CLI;
* APIs;
* public types/interfaces;
* runtime composition;
* adapters;
* benchmarks where relevant.

Only after a first complete architecture model and candidate documentation exist should legacy documentation be systematically audited.

This separation is deliberate.

It prevents historical documentation from anchoring the reconstruction.

---

# 4. Build a deterministic repository inventory first

Before writing architectural prose, inspect and map the repository.

Use deterministic tooling wherever possible.

Generate lightweight machine-readable inventory artifacts such as:

```text
.generated/knowledge/
├── files.jsonl
├── packages.jsonl
├── symbols.jsonl
├── tests.jsonl
├── schemas.jsonl
├── configuration.jsonl
└── commands.jsonl
```

The exact filenames may change if a better representation emerges.

Extract, where practical:

* packages/modules;
* source languages;
* exported/public symbols;
* entry points;
* interfaces/protocols;
* event definitions;
* configuration definitions;
* CLI commands;
* schemas;
* tests;
* important dependencies;
* module relationships;
* code paths;
* Git metadata;
* approximate document/token sizes.

Do not ask an LLM to manually perform work that can be extracted deterministically.

---

# 5. Use OSS tooling pragmatically

Use the OSS stack defined in `OSS_docs_tools.md` where it materially improves the reconstruction.

Preferred baseline:

```text
Git
rg
filesystem tools
Markdown parser
YAML frontmatter
JSON Schema
jq / yq
ast-grep
SCIP where useful
markdownlint-cli2
Vale
Lychee
Mermaid
pre-commit
MkDocs Material
```

Use:

```text
Pandoc
Docling
```

only when non-Markdown legacy formats actually require conversion.

Do not install or integrate a tool merely because it appears in the research plan.

Evaluate tools against the real repository.

Record:

```text
useful
partially useful
not useful
unnecessary
too expensive
```

where relevant.

Do not block documentation delivery on:

```text
Glean
Kythe
Neo4j
GraphRAG
Joern
vector databases
custom Atlas implementation
custom search infrastructure
custom parser infrastructure
```

These remain future Atlas experiments unless an immediate concrete need emerges.

---

# 6. Reconstruct the architecture bottom-up

Build an evidence-backed model of the actual system.

Identify where applicable:

* repository/workspace topology;
* packages/modules;
* Kernel;
* authority;
* capabilities;
* budgets/resources;
* Agency;
* turn semantics;
* runtime;
* execution lifecycle;
* orchestration;
* events;
* ledger;
* reducers;
* projections;
* artifacts;
* persistence;
* replay;
* recovery;
* checkpoints;
* agents;
* manifests;
* scope;
* lineage;
* spawning;
* workflows;
* topology;
* scheduling;
* concurrency;
* context;
* memory;
* plugins;
* packs;
* tools;
* models;
* model routing;
* evaluators;
* telemetry;
* adapters;
* clients;
* commands;
* transports;
* configuration;
* public contracts.

Do not force these concepts into the documentation if they do not actually exist in the repository.

The list is an investigation checklist, not a predetermined architecture.

---

# 7. For each discovered subsystem determine

At minimum:

```text
Purpose
Responsibilities
Non-responsibilities
Boundaries
Dependencies
Inputs
Outputs
State
Lifecycle
Execution flow
Invariants
Failure semantics
Extension points
Code locations
Tests
Schemas/contracts
Configuration
Current implementation status
```

Every non-obvious implementation claim should be traceable to repository evidence.

Do not invent missing behavior.

---

# 8. Derive the documentation structure from the governing architecture specification

Use:

`docs/_archive/reviews/backend/director_review_v6/DOCUMENTATION_ARCHITECTURE_SPEC.md`

as the canonical documentation information architecture.

The stable top-level organization is:

```text
docs/
├── README.md
├── SPEC.md
├── architecture/
├── reference/
├── guides/
├── decisions/
├── execution/
└── theory/
```

Use the deeper proposed structure as the starting target.

Minor leaf-level modifications are allowed only when inspection of the actual repository demonstrates that the change improves semantic ownership or retrieval.

Do not recreate root-level subsystem silos.

For example:

```text
architecture/runtime/kernel.md
```

answers:

> How does the Kernel work?

while:

```text
reference/contracts/...
```

answers:

> What exactly is the contract?

and:

```text
guides/...
```

answers:

> How do I work with or modify it?

and:

```text
decisions/ADR-...
```

answers:

> Why was this non-obvious choice made?

---

# 9. Enforce canonical ownership

Apply strictly:

> One durable fact → one canonical owner → every other document links to it.

Therefore:

* architecture pages explain structure and behavior;
* reference pages own exact interfaces/contracts/events/configuration;
* guides own procedures;
* ADRs own non-obvious rationale;
* execution owns only current project state;
* theory owns conceptual/research material;
* schemas/code own executable definitions where appropriate.

Do not duplicate exact information across categories.

---

# 10. Produce compact independently retrievable documents

Do not replace old monoliths with new monoliths.

A document should represent one coherent knowledge unit.

Optimize for:

```text
human comprehension
+
AI retrieval precision
+
low irrelevant context
```

Do not split documents based solely on arbitrary line or token limits.

Split when independent concepts would frequently need to be retrieved independently.

Architecture pages should generally use:

```text
# Title

## Purpose
## Responsibilities
## Non-responsibilities
## Boundaries
## Inputs and outputs
## Execution flow
## State and lifecycle
## Invariants
## Failure semantics
## Extension points
## Code map
## Tests and evidence
## Related documentation
```

Use the templates from the bootstrap specification for reference pages, guides, ADRs and theory.

---

# 11. Add machine-readable metadata

Every active canonical Markdown document must have validated frontmatter.

Use the governing schema from the bootstrap documents.

At minimum:

```yaml
---
id:
type:
status:
title:
summary:
authority:
last_verified:
---
```

Use additional semantic metadata only where useful:

```yaml
area:
relates_to:
code:
tests:
schemas:
decisions:
```

IDs must be:

* globally unique;
* semantic;
* stable across file moves;
* independent of paths where practical.

Avoid manually encoding repository topology that can be generated automatically.

---

# 12. Generate machine indexes automatically

Generate a machine-readable knowledge layer rather than maintaining one manually.

Target approximately:

```text
.generated/knowledge/
├── catalog.jsonl
├── headings.jsonl
├── relations.jsonl
├── code-map.jsonl
├── symbols.jsonl
├── unresolved.jsonl
└── context-bundles/
```

This is generated output.

Markdown remains the canonical human-authored knowledge representation.

An AI agent should be able to inspect the catalog rather than recursively reading all documentation.

---

# 13. Connect documentation to code

Use stable code/test/schema references.

Prefer:

```text
package
module
stable symbol
schema
test suite
```

over fragile line-number references.

Use:

```text
rg
ast-grep
SCIP
```

where useful to discover or validate relationships.

Do not manually encode full import, call or reference graphs into frontmatter.

Generated tooling may represent those relationships separately.

---

# 14. Actually create the new documentation

This task is **not complete after analysis or planning**.

Do not stop after producing:

* an architecture report;
* an inventory;
* a migration proposal;
* a TODO list.

Create the new candidate documentation files.

During reconstruction, write into a separate candidate tree so the existing documentation remains intact until validation.

For example:

```text
candidate-docs/
```

mirroring the intended final:

```text
docs/
```

Also create the required lightweight tooling/configuration where useful under:

```text
tools/docs_alpha/
.generated/knowledge/
```

Do not modify production application behavior as part of this task.

---

# 15. Recommended execution phases

Execute autonomously through these phases.

Do not request approval between phases unless an ambiguity would require changing production semantics.

## Phase A — Baseline

* verify branch;
* record commit;
* inventory repository;
* inspect languages/workspaces/packages;
* identify executable evidence.

## Phase B — Architecture discovery

* reconstruct package/module architecture;
* reconstruct runtime topology;
* identify contracts, events, state and extension seams;
* produce a structured internal architecture map.

## Phase C — Canonical documentation design

* reconcile discovered architecture against `DOCUMENTATION_ARCHITECTURE_SPEC.md`;
* determine exact final files;
* establish IDs and ownership;
* detect where proposed leaf files are unnecessary or missing.

## Phase D — AS_BUILT documentation

Create:

* architecture pages;
* technical reference;
* developer guides;
* navigation/README material.

These must describe the current implementation.

## Phase E — TARGET documentation

Review:

```text
VISION.md
current normative specification
active accepted decisions
active milestones/roadmap
```

Preserve intentional future behavior separately.

Do not contaminate AS_BUILT pages with unimplemented claims.

## Phase F — Legacy knowledge audit

Only now inspect historical/legacy documentation comprehensively enough to determine whether the reconstruction omitted unique valuable knowledge.

Classify legacy findings:

```text
ALREADY_CAPTURED
CURRENT_DECISION
FUTURE_REQUIREMENT
THEORY
OBSOLETE
CONTRADICTED_BY_CODE
UNRESOLVED
```

Absorb only useful unique knowledge.

Do not preserve historical prose by default.

## Phase G — Machine layer

Generate:

* metadata;
* catalog;
* headings index;
* relations;
* reverse code map;
* context bundles where useful.

## Phase H — Quality pipeline

Run:

```text
JSON Schema validation
markdownlint-cli2
Vale
Lychee
path validation
ID validation
duplicate ownership checks
```

Integrate appropriate checks through:

```text
pre-commit
CI
```

## Phase I — Diagrams and publishing

Use Mermaid for high-value diagrams.

Configure MkDocs Material as the initial presentation layer.

MkDocs is a consumer, not the documentation knowledge model.

## Phase J — Independent audit

Review the complete candidate documentation again against the repository baseline.

Fix actionable findings.

---

# 16. Legacy audit must be loss-oriented, not migration-oriented

The question during the legacy pass is not:

> Where should every old document move?

The question is:

> Does this old material contain unique knowledge that the new evidence-backed documentation would otherwise lose?

Examples worth preserving may include:

* still-binding architectural decisions;
* security invariants;
* compatibility requirements;
* rationale that remains important;
* intentionally future requirements;
* research/theory that still informs AETHER.

Examples normally not worth preserving:

* completed sprint reports;
* old reviews;
* superseded implementation plans;
* duplicate explanations;
* historical status narratives;
* outdated architectural descriptions;
* obsolete terminology;
* abandoned proposals.

Git provides historical recovery.

---

# 17. SPEC must be actively reviewed

Do not blindly copy the current `SPEC.md`.

Determine whether each important section is primarily:

```text
CURRENT IMPLEMENTATION
CURRENT NORMATIVE CONTRACT
FUTURE TARGET
MIXED
OBSOLETE
```

Refactor or separate mixed material where necessary.

The resulting documentation must make it impossible for a reader or agent to mistake future intent for current behavior.

---

# 18. VISION has a different role

Do not reconstruct `VISION.md` from implementation.

Vision describes product identity and intended direction.

Review it for current relevance, but preserve deliberate future intent even when the implementation has not reached it.

Explicitly link relevant architecture gaps or milestones to that future direction rather than pretending they are already implemented.

---

# 19. Decisions

Do not preserve the historical ADR corpus mechanically.

Create or retain only decisions that a current Senior Engineer genuinely benefits from knowing and whose rationale is not obvious from:

* code;
* contracts;
* architecture pages.

Current ADRs should be compact.

Git is the project-history archive.

---

# 20. Execution documentation

Keep only operationally useful current state:

```text
milestones
backlog
sprint_active
sprint_upcoming
```

Do not preserve completed execution history in the active documentation tree.

---

# 21. Diagrams

Create only diagrams that materially improve understanding.

Prefer Mermaid.

Useful candidates include:

* system context;
* package/component topology;
* execution lifecycle;
* event/ledger flow;
* agent lifecycle;
* recovery/replay;
* plugin/tool extension flow;
* context/memory flow.

A diagram is a view over canonical knowledge.

It must not become an independent source of architectural truth.

---

# 22. Independent final audit criteria

Before declaring completion, verify:

### Implementation fidelity

* every major implemented subsystem is documented;
* important public contracts are represented;
* non-obvious invariants have evidence;
* code/test/schema references resolve.

### Current vs future

* planned behavior is not described as implemented;
* future requirements remain discoverable;
* obsolete plans are not active.

### Information architecture

* canonical ownership is clear;
* duplicate explanations are minimized;
* pages are independently retrievable;
* navigation is predictable.

### Machine usability

* IDs are unique;
* metadata validates;
* catalog builds;
* relations resolve;
* agents can route through catalog rather than recursive reading.

### Human usability

A new Senior Engineer should be able to answer:

1. What is AETHER?
2. How is it architected?
3. How does execution work?
4. Where are the major boundaries?
5. What are the exact contracts/events/configuration?
6. How do I extend it?
7. How do I test/debug it?
8. What is implemented versus planned?
9. Why do the important non-obvious decisions exist?

without consulting historical reviews.

---

# 23. Final deliverables

The execution should leave at minimum:

```text
candidate-docs/
├── README.md
├── SPEC.md
├── architecture/
├── reference/
├── guides/
├── decisions/
├── execution/
└── theory/

.generated/knowledge/
├── catalog.jsonl
├── headings.jsonl
├── relations.jsonl
├── code-map.jsonl
├── symbols.jsonl
└── unresolved.jsonl

tools/docs_alpha/

mkdocs.yml
documentation validation configuration
pre-commit / CI integration
```

And create:

```text
DOCUMENTATION_REBUILD_REPORT.md
```

containing only the reconstruction/audit record:

1. exact baseline commit;
2. architecture discovered;
3. documentation generated;
4. implementation gaps discovered;
5. legacy knowledge retained;
6. legacy knowledge considered obsolete;
7. unresolved conflicts;
8. OSS tools actually used;
9. measured usefulness/cost of those tools;
10. recommendations relevant to future Atlas.

The report is secondary.

**The canonical documentation files are the primary deliverable.**

---

# 24. Completion behavior

Do not stop merely because the task is large.

Work systematically through the repository and complete as much of the reconstruction as can be supported by evidence.

Do not ask for approval after every subsystem.

Record genuine uncertainty under `unresolved` rather than inventing an answer.

Do not modify production code merely to make the documentation consistent.

Do not rewrite implementation behavior from documentation assumptions.

Do not delete the current documentation tree during reconstruction.

The cutover from `candidate-docs/` to `docs/` happens only after validation.

---

# Core invariant

> **Reconstruct current documentation from current implementation; reconstruct future documentation from current intentional design; use legacy documentation only to recover unique knowledge that neither source contains.**

The target is not a cleaner version of the old documentation.

The target is a **new canonical knowledge system derived from the real AETHER repository**:

```text
CODE / TESTS / SCHEMAS
          ↓
       AS_BUILT
          │
          ├──────────────┐
          │              │
          │        VISION / TARGET
          │              │
          └──────┬───────┘
                 ↓
         CANONICAL KNOWLEDGE
                 ↓
       SMALL STRUCTURED MARKDOWN
                 ↓
       GENERATED MACHINE INDEX
                 ↓
      HUMANS + CODING AGENTS
```
