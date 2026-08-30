# AETHER Documentation Control Plane and Atlas OSS Evolution
## From a Clean Documentation Baseline to an Automated Repository Knowledge Control Plane

**Status:** Technical strategy and implementation report  
**Project:** AETHER — Electroweak documentation line  
**Date:** 2026-08-30  
**Scope:** Documentation infrastructure, repository knowledge extraction, OSS orchestration, and future Atlas architecture  

---

# Executive Summary

AETHER has already completed the hardest prerequisite for a durable documentation system: the documentation surface has been reconstructed, compressed, separated by domain, assigned canonical ownership, and validated against the repository. The next problem is therefore **not another documentation migration**. The next problem is to install a permanent control plane that makes regression into documentation sprawl difficult, mechanically detectable, and increasingly automatable.

This report unifies two complementary plans:

1. **“Sim. Pra ganhar produtividade agora…” = plano operacional P0, para instalar já.**
2. **“Sim. E eu simplificaria…” = direção arquitetural do futuro Atlas, depois que houver evidência real do P0.**

The two plans should not be implemented simultaneously as one large platform. They define two different horizons:

- **P0 / operational now:** use mature OSS tools to make the current Markdown documentation structured, validated, searchable, reproducible, and easy for humans and agents to consume.
- **Atlas / architectural future:** convert the practical evidence collected by P0 into a thin repository-knowledge control plane that orchestrates OSS parsers, indexers, search engines, code-intelligence protocols, migration engines, and agentic reasoning through a stable intermediate representation.

The central architectural thesis is:

> **Atlas should not become a parser, code indexer, search engine, graph database, codemod engine, documentation generator, or agent harness. Atlas should become the control plane that composes those capabilities and normalizes their evidence into one project model.**

This allows AETHER to obtain immediate productivity while also creating a real-world laboratory for Atlas. The same tools used to maintain AETHER documentation become candidates for Atlas adapters. Their measured strengths, limitations, output quality, false-positive rates, incremental behavior, and operational costs become empirical design inputs rather than speculative architecture.

The resulting strategy is intentionally evolutionary:

```text
Clean AETHER docs
        ↓
Docs-as-code control plane
        ↓
Generated machine knowledge
        ↓
Docs ↔ code evidence
        ↓
Proto-Atlas commands
        ↓
Stable PKIR
        ↓
Atlas control plane
        ↓
Optional large-scale/deep-analysis backends
```

The practical objective is therefore not to “build Atlas now.” It is to make the current documentation system **Atlas-compatible by construction** while obtaining immediate engineering value.

---

# 1. Current AETHER Documentation Baseline

The current documentation structure is already substantially better than the legacy corpus because it distinguishes global system truth from backend, frontend, product, execution, theory, and research domains.

The current intended structure is:

```text
docs/
├── README.md
├── SPEC.md
├── decisions.md
│
├── architecture/
│   ├── overview.md
│   ├── boundaries.md
│   └── data-flow.md
│
├── backend/
│   ├── architecture/
│   ├── reference/
│   └── guides/
│
├── frontend/
│   ├── README.md
│   ├── architecture/
│   ├── reference/
│   └── guides/
│
├── product/
│   └── frontend/
│       ├── FRONTEND_PRD_PLACEMENT_MANIFEST.md
│       ├── PRD_AETHER_CLI.md
│       ├── PRD_AETHER_DESKTOP.md
│       ├── PRD_AETHER_LAB.md
│       ├── PRD_AETHER_TUI.md
│       └── PRD_FRONTEND_PLATFORM.md
│
├── execution/
│   ├── active.md
│   └── milestones.md
│
├── theory/
│   └── agent-substrate.md
│
└── research/
    └── README.md
```

This structure establishes useful ownership boundaries:

- `SPEC.md` owns compact normative requirements.
- `architecture/` owns global end-to-end architecture.
- `backend/architecture/` owns backend/substrate structure and behavior.
- `backend/reference/` owns exact contracts, events, schemas, manifests, ports, and commands.
- `backend/guides/` owns operational procedures.
- `frontend/` is intentionally sparse until the frontend stabilizes.
- `product/frontend/` owns product requirements independently of implementation churn.
- `execution/` owns current work and milestone sequencing.
- `decisions.md` should own only irreducible rationale that is not already encoded elsewhere.
- `theory/` owns durable conceptual models.
- `research/` owns exploratory, non-authoritative evidence and reports.

This baseline should **not** be replaced by another taxonomy during the OSS setup. The OSS stack must adapt to this structure.

---

# 2. The Core Documentation Philosophy

The most important design decision is to keep the human-authoritative documentation layer small and to derive machine views from it.

The durable model is:

```text
Markdown + Git
     =
human-authored durable source

Generated indexes
     =
machine-reconstructible views

MkDocs / Obsidian
     =
human interfaces

Agents / context compiler
     =
machine consumers

Atlas
     =
future orchestration and semantic control plane
```

No view should silently become a second source of truth.

## 2.1 One fact, one canonical owner

A durable fact should have one primary owner.

Examples:

```text
Normative guarantee       → SPEC.md
Runtime architecture      → backend/architecture/runtime-execution.md
Event wire shape          → backend/reference/events.md
Current implementation    → code + AS_BUILT documentation
Current work              → execution/active.md
Release gate              → execution/milestones.md
Product requirement       → product/
Architectural rationale   → decisions.md
Exploratory hypothesis    → research/
```

Other documents link to the owner instead of copying the content.

This is the strongest anti-bloat rule in the entire system.

## 2.2 Generated knowledge is disposable

Everything under a machine-generated knowledge directory must be reproducible.

Examples:

```text
.generated/knowledge/catalog.jsonl
.generated/knowledge/links.jsonl
.generated/knowledge/symbols.jsonl
.generated/knowledge/code-map.jsonl
.generated/knowledge/claims.jsonl
```

These files are useful for agents and tools, but they are not edited manually.

If the generated directory is deleted, a command should regenerate it from repository sources.

## 2.3 Git owns chronology

Documentation metadata should not duplicate information already encoded by Git.

Avoid maintaining fields whose primary purpose is to repeat:

- author;
- commit;
- modification timestamp;
- review history;
- branch history;
- previous file paths;
- migration provenance that only matters to the reconstruction process.

Those facts are naturally available from version control.

## 2.4 Research never promotes itself

Research may contain hypotheses, reports, benchmarks, external references, and speculative architectures. It is intentionally allowed to be less constrained.

But the transition:

```text
research
   ↓
canonical architecture / SPEC
```

must be explicit.

An LLM, import process, document converter, or external source must never automatically promote exploratory content into canonical truth.

---

# 3. Documentation as a Compilable System

The immediate goal should be to treat documentation less like a folder of prose and more like a compilable artifact.

A document enters the active documentation surface only if it passes structural constraints.

A useful conceptual pipeline is:

```text
Markdown source
      │
      ├── metadata validation
      ├── syntax/style validation
      ├── terminology validation
      ├── link validation
      ├── ownership validation
      ├── duplicate-ID validation
      ├── stale-path validation
      └── site compilation
              │
              ▼
          VALID DOC
```

This does not require Atlas. Mature OSS already solves most of it.

---

# 4. Recommended Repository-Level Documentation Infrastructure

Tooling should remain outside `docs/`.

Recommended repository structure:

```text
Aether-D-System/
├── docs/
│   └── ...
│
├── .docs/
│   ├── document.schema.json
│   ├── taxonomy.yml
│   ├── terminology.yml
│   ├── authority.yml
│   └── vale/
│
├── tools/
│   └── docs/
│       ├── validate.py
│       ├── catalog.py
│       ├── extract_links.py
│       ├── code_map.py
│       ├── ingest.py
│       └── report.py
│
├── .generated/
│   └── knowledge/
│       ├── catalog.jsonl
│       ├── links.jsonl
│       ├── symbols.jsonl
│       ├── code-map.jsonl
│       └── report.json
│
├── mkdocs.yml
├── justfile
├── .vale.ini
├── .markdownlint-cli2.yaml
├── .lychee.toml
└── .pre-commit-config.yaml
```

The separation is deliberate:

| Surface | Role |
|---|---|
| `docs/` | durable human-authored project knowledge |
| `.docs/` | documentation policy and schemas |
| `tools/docs/` | minimal orchestration glue |
| `.generated/knowledge/` | derived machine-readable repository knowledge |
| root config files | interfaces to mature OSS tools |

This provides a clean path into Atlas because the future Atlas can consume `.generated/knowledge/` without imposing itself on authoring.

---

# 5. Minimal Frontmatter Contract

The reconstruction process used richer metadata because it needed to represent review state, authority reconciliation, analysis SHA, confidence, and migration provenance. That metadata is useful during reconstruction but should not automatically become the permanent authoring burden.

A smaller steady-state schema is preferable:

```yaml
---
id: backend.arch.kernel
kind: architecture
authority: descriptive
truth: as-built
status: active
owner: backend
summary: Domain-blind effect mediation and authority boundary.
related:
  - backend.ref.events
  - spec.core
---
```

Recommended required fields:

```text
id
kind
authority
truth
status
owner
summary
```

Recommended optional fields:

```text
related
tags
supersedes
```

Everything else should require justification.

## 5.1 Why minimal metadata matters

Metadata is useful only when its machine value exceeds its maintenance cost.

Too little metadata produces:

```text
hard-to-query prose
ambiguous authority
weak retrieval
```

Too much metadata produces:

```text
schema bureaucracy
stale fields
LLM context inflation
human avoidance
```

The P0 experiment should explicitly measure this trade-off.

The future Atlas can infer additional data from Git, content, code indexes, and generated relationships rather than requiring humans to type it.

---

# 6. P0: OSS Stack to Install Now

The first attached plan is the operational plan. Its purpose is immediate productivity and evidence generation.

The recommended P0 stack is:

| Capability | Technology | Stage |
|---|---|---|
| Documentation site/navigation/search | MkDocs + Material for MkDocs | P0 |
| Command orchestration | `just` | P0 |
| Metadata format | YAML frontmatter | P0 |
| Metadata contract | JSON Schema | P0 |
| Schema validation | Python `jsonschema` | P0 |
| Markdown linting | markdownlint-cli2 | P0 |
| Terminology/style ontology | Vale | P0 |
| Link integrity | Lychee | P0 |
| Git hooks | pre-commit | P0 |
| Diagrams as code | Mermaid | P0 |
| Metadata shell queries | `yq` / `jq` | P0 |
| Python API extraction | mkdocstrings + Griffe | P0/P0.5 |
| TypeScript API extraction | TypeDoc | after frontend stabilization |
| Legacy markup conversion | Pandoc | on demand |
| Complex document ingestion | Docling | on demand |
| Structural code analysis | ast-grep | P1 experiment |
| Symbol graph | SCIP | P1 experiment |

The key principle is not merely “use these tools.” It is:

> **Use mature OSS as deterministic workers and write only enough proprietary glue to coordinate them.**

---

# 7. MkDocs + Material for MkDocs

## 7.1 Role

MkDocs provides the human documentation build surface. Material for MkDocs adds a mature navigation, search, metadata/tag, and presentation layer while keeping Markdown as source.

The official Material documentation supports tags in page frontmatter and metadata inheritance through `.meta.yml`, which is valuable because it allows folder-level policy without repeating metadata in every document.

## 7.2 Why it fits AETHER

AETHER needs:

- hierarchical navigation;
- fast discovery;
- local documentation rendering;
- searchable Markdown;
- support for metadata;
- diagram rendering;
- deterministic CI builds;
- minimal authoring friction.

MkDocs is a view over `docs/`; it does not need to own the source model.

## 7.3 Usage

Suggested commands:

```bash
just docs-serve
just docs-build
```

`docs-build` should run in strict mode.

MkDocs should consume the existing structure, not force a new one.

## 7.4 What MkDocs is not

MkDocs is not:

- the knowledge model;
- the authority engine;
- the code index;
- the graph database;
- Atlas.

It is the human-readable documentation compiler.

---

# 8. `just`: One Developer Interface over Many OSS Tools

A recurring failure mode of OSS-heavy stacks is exposing every tool directly to every contributor.

Do not require developers to remember:

```text
markdownlint-cli2 ...
vale ...
lychee ...
python tools/docs/validate.py ...
mkdocs ...
scip ...
ast-grep ...
```

Expose one interface.

Example:

```text
just docs-check
just docs-build
just docs-serve
just docs-map
just docs-query QUERY
just docs-ingest FILE
just docs-full
```

The `just` project is explicitly a project-specific command runner rather than a general build system. This makes it appropriate as the thin human-facing orchestration layer.

Conceptually:

```text
Developer
    │
    ▼
   just
    │
    ├── OSS tool A
    ├── OSS tool B
    ├── OSS tool C
    └── tiny AETHER scripts
```

This is already a prototype of the future Atlas philosophy:

> one stable interface over heterogeneous workers.

---

# 9. JSON Schema + `jsonschema`

The Markdown frontmatter becomes useful only if it is validated.

Create:

```text
.docs/document.schema.json
```

The schema should enforce:

- stable IDs;
- allowed `kind`;
- allowed authority classes;
- allowed truth planes;
- allowed lifecycle states;
- expected types for relations;
- optional fields only where justified.

Do not write a large custom validator if JSON Schema already expresses the rule.

Custom Python should only implement repository-specific invariants that generic schema validation cannot express, such as:

```text
canonical ID must be globally unique
related ID must resolve
authority combinations must be legal
frontend docs may be deferred
a generated page must not be manually edited
```

---

# 10. markdownlint-cli2

Markdown is flexible enough to become structurally inconsistent unless linted.

markdownlint-cli2 is appropriate for:

- heading structure;
- list formatting;
- spacing conventions;
- duplicate headings;
- malformed Markdown patterns;
- deterministic CI enforcement.

It also documents direct pre-commit integration.

Use it for **structure**, not conceptual correctness.

Do not overload markdownlint with AETHER-specific ontology rules; Vale and custom metadata checks are better layers for that.

---

# 11. Vale: Terminology and Ontology Drift Detection

Vale is unusually important for AETHER because the project has experienced conceptual vocabulary drift across multiple architectural eras.

Vale is markup-aware: it parses prose rather than blindly linting syntax tokens.

AETHER-specific Vale rules can detect terminology such as:

```text
deprecated term:
Agent Instance

preferred:
AgentView
```

or:

```text
deprecated:
event log

preferred where semantically appropriate:
causal ledger
```

or warn about historical branding inside active normative documentation.

This converts some semantic drift from a review problem into a deterministic lint problem.

## 11.1 Appropriate Vale rules

Good candidates:

- obsolete architectural terminology;
- forbidden metaphors in normative docs;
- inconsistent capitalization of canonical entities;
- incorrect authority language;
- vague words in normative documents;
- stale project branding;
- repeated weak phrases that hide implementation status.

## 11.2 What Vale should not do

Vale should not try to prove:

- whether an architectural claim matches code;
- whether a decision is still authoritative;
- whether a benchmark is scientifically valid.

Those require stronger evidence.

---

# 12. Lychee: Link Integrity

Lychee is a fast asynchronous link checker implemented in Rust and supports Markdown, HTML, websites, CLI use, library use, GitHub Actions, and pre-commit integration.

For AETHER it should verify:

```text
doc → doc
doc → anchor
doc → external source
generated site → external source
```

Internal path checks can remain in the existing repository-specific checker if that checker understands canonical IDs and AETHER-specific routing better.

A useful split is:

```text
fast local checks
    → internal path/anchor validator

slower network checks
    → Lychee
```

External URLs should normally be checked in CI rather than on every local commit to avoid latency and rate-limit problems.

---

# 13. pre-commit: Fast Local Regression Barrier

pre-commit exists to manage multi-language Git hooks and is explicitly designed to run standard linters before review.

Do not put the entire documentation pipeline into every commit.

Recommended local hook set:

```text
frontmatter schema
canonical ID uniqueness
markdownlint
Vale
internal links
stale paths
```

Avoid by default:

```text
full external URL crawl
SCIP indexing
deep code analysis
Docling conversion
full repository semantic reconciliation
```

Those belong in CI or explicit commands.

The goal is a sub-second or low-second feedback loop whenever possible.

If pre-commit becomes irritating, developers will bypass it, destroying its value.

---

# 14. Mermaid: Architecture as Versioned Text

New diagrams should default to Mermaid when the representation is expressible there.

Benefits:

```text
Git-diffable
AI-editable
text-searchable
copyable
regenerable
embeddable in Markdown
```

This avoids a proliferation of:

```text
architecture_final.png
architecture_final_v2.png
architecture_final_REAL.png
```

Mermaid should be preferred for:

- sequences;
- state machines;
- component relationships;
- flows;
- topology illustrations;
- lifecycle diagrams.

Use graphical design tools only when Mermaid cannot represent the information adequately.

---

# 15. `yq` and `jq`: Proto-Query Interface

These tools are useful because the P0 metadata model is YAML/JSON.

Before writing a sophisticated Atlas query language, simple questions can already be answered deterministically.

Examples:

```text
all active backend architecture documents
all TARGET documents
all docs owned by frontend
all relationships targeting spec.core
all research documents with status experimental
```

The important architectural lesson is that **structured metadata permits useful queries without a database**.

This helps measure whether the future PKIR needs a richer query engine or whether simpler representations remain sufficient.

---

# 16. Generated API Documentation: Griffe, mkdocstrings, and TypeDoc

A major source of documentation bloat is manually copying information that is already authoritative in code.

## 16.1 Python

Griffe extracts the structural API model of Python programs and can serialize API information. mkdocstrings' Python handler uses Griffe to collect and render Python documentation.

Use these for:

- exported APIs;
- signatures;
- parameters;
- docstrings;
- public classes;
- protocols;
- package reference.

Do not manually maintain large API tables in Markdown when the data can be generated.

## 16.2 TypeScript

TypeDoc converts TypeScript source comments into HTML documentation or a JSON model.

When the frontend architecture stabilizes, TypeDoc can provide:

```text
TS exports
components
interfaces
types
client APIs
```

Its JSON model is especially interesting for Atlas because generated API information can feed the machine knowledge layer without scraping rendered HTML.

## 16.3 Separation

Human documentation explains:

```text
why
architecture
usage
semantics
constraints
```

Generated API documentation describes:

```text
exact callable surface
types
signatures
exports
```

This reduces duplicate ownership.

---

# 17. Pandoc: Universal Legacy Markup Adapter

Pandoc should be treated as an ingestion adapter, not as part of the daily authoring loop.

The official Pandoc manual describes it as a library and CLI for converting between numerous markup and word-processing formats.

Use it for sources such as:

```text
RST
HTML
DOCX
LaTeX
Org
other Markdown dialects
```

Pipeline:

```text
Legacy document
       ↓
     Pandoc
       ↓
normalized staging Markdown
       ↓
AI/human reconciliation
       ↓
canonical AETHER document
```

Important rule:

> **Conversion does not grant authority.**

Pandoc solves syntax conversion, not semantic reconciliation.

---

# 18. Docling: Complex Document Ingestion

Docling is appropriate when source documents contain complex layout or are not primarily markup.

Its current documentation lists support for formats including PDF, DOCX, XLSX, PPTX, HTML, Markdown, LaTeX, images, and other formats, and it exports to Markdown and a structured JSON representation called `DoclingDocument`.

That makes it conceptually important for future Atlas:

```text
PDF / Office / complex source
        ↓
      Docling
        ↓
 DoclingDocument
        ↓
 Atlas adapter
        ↓
 normalized evidence
```

Do not build OCR, layout analysis, PDF table extraction, or Office ingestion inside Atlas unless a future requirement proves an OSS gap.

---

# 19. P0.5: Generated Knowledge Layer

Once P0 validation is reliable, produce small deterministic machine indexes.

Recommended files:

```text
.generated/knowledge/
├── catalog.jsonl
├── links.jsonl
├── ownership.jsonl
├── headings.jsonl
└── report.json
```

Example catalog row:

```json
{
  "id": "backend.arch.kernel",
  "kind": "architecture",
  "path": "docs/backend/architecture/kernel.md",
  "authority": "descriptive",
  "truth": "as-built"
}
```

Example relationship row:

```json
{
  "source": "backend.arch.kernel",
  "relation": "related_to",
  "target": "backend.ref.events"
}
```

The generated layer starts to resemble a primitive project knowledge representation without committing to Atlas internals.

---

# 20. P1: ast-grep for Structural Code Evidence

ast-grep is a Rust-based structural search, lint, and rewriting engine built around syntax trees. It supports many languages and structured JSON output.

Its first use in AETHER should be **observation**, not automated mutation.

Questions to test:

```text
Where is AgentView defined?
Which production sites construct it?
Where is EffectRequest produced?
Are deprecated classes still instantiated?
Which modules violate a stated boundary?
Where are legacy runtime entry points used?
```

Possible output:

```text
doc claim
   ↓
search rule
   ↓
AST matches
   ↓
code evidence
```

This provides a first deterministic bridge between documentation and code.

## 20.1 Why not direct Tree-sitter first

ast-grep already provides a high-level polyglot structural interface powered by Tree-sitter-like syntax parsing.

Direct Tree-sitter should be added only when:

- source-range fidelity is insufficient;
- custom grammars are required;
- Atlas needs low-level syntax traversal unavailable through higher-level tools;
- latency measurements justify avoiding another abstraction layer.

Use the highest-level mature abstraction that solves the problem.

---

# 21. P1: SCIP for Symbol Intelligence

SCIP is a language-agnostic code intelligence protocol for information such as:

- definition;
- references;
- implementations.

Its official repository provides a protobuf schema, Go and Rust bindings, and indexers across multiple language ecosystems including Python and TypeScript.

This makes SCIP a strong candidate for the stable symbol layer.

Conceptually:

```text
docs/backend/architecture/agency.md
              │
              │ refers_to
              ▼
       symbol:AgentView
          /       \
 definition      references
    │                │
    ▼                ▼
 Python source     callers
```

## 21.1 ast-grep vs SCIP

They solve different problems.

```text
ast-grep
→ syntax patterns
→ structural rules
→ structural rewrites
→ custom repository-specific detection

SCIP
→ symbol identities
→ definitions
→ references
→ implementations
→ language-agnostic navigation
```

Atlas may ultimately consume both.

The P1 experiment should measure overlap rather than assuming both are necessary everywhere.

---

# 22. What to Measure During P0 and P1

The experiments are valuable only if the project records evidence.

For each OSS component measure:

| Dimension | Example metric |
|---|---|
| automation gain | manual minutes avoided |
| precision | false-positive rate |
| recall | relevant facts discovered |
| configuration cost | config LOC / maintenance |
| incremental capability | full rebuild vs changed-file processing |
| structured output | JSON / protobuf / AST availability |
| determinism | repeatable output |
| language coverage | Python / TypeScript / Rust / etc. |
| agent usability | CLI stability / parseability |
| performance | wall-clock / memory |
| operational complexity | install/runtime dependencies |
| Atlas role | core / adapter / optional backend / reject |

A useful experimental register could remain generated or live under research:

```text
docs/research/atlas-oss-evaluation.md
```

Keep it explicitly non-normative.

---

# 23. The Future Atlas: A Thin Repository Knowledge Control Plane

The second attached plan defines the long-term architecture.

Atlas should become:

> **A tool-independent repository knowledge control plane that transforms heterogeneous project evidence into a canonical project model and uses that model to drive search, context compilation, organization, migration, validation, and agent operations.**

It should explicitly avoid rebuilding mature functionality.

---

# 24. Atlas as an Intermediate Representation

The most important proprietary concept is not the parser. It is the normalized model.

A minimal Project Knowledge Intermediate Representation (PKIR) might contain:

```text
Entity
Relation
Claim
Evidence
Locator
Authority
Revision
```

Possible Rust representation:

```rust
struct Entity {}
struct Relation {}
struct Claim {}
struct Evidence {}
struct Locator {}
struct Authority {}
struct Revision {}
```

An entity:

```json
{
  "id": "concept.agent-view",
  "kind": "concept",
  "name": "AgentView",
  "summary": "Event-derived projection of agent state"
}
```

A relation:

```json
{
  "source": "concept.agent-view",
  "relation": "implemented_by",
  "target": "symbol:aether.agency.AgentView",
  "evidence": "scip:..."
}
```

Another relation:

```json
{
  "source": "concept.agent-view",
  "relation": "specified_by",
  "target": "doc:spec.core#agent-state",
  "authority": "normative"
}
```

This is where Atlas becomes technically distinctive.

OSS solves syntax and indexing.

Atlas solves:

```text
identity
semantic normalization
authority
provenance
reconciliation
canonical ownership
knowledge preservation
context compilation
migration planning
```

---

# 25. Fact Providers, Not Giant Integrations

Every external extractor should behave like an adapter.

Conceptual interface:

```rust
trait FactProvider {
    fn detect(&self, repo: &Repository) -> Support;
    fn extract(&self, repo: &Repository) -> Result<FactBatch>;
}
```

Possible providers:

```text
GitProvider
MarkdownProvider
PandocProvider
DoclingProvider
ScipProvider
AstGrepProvider
SchemaProvider
TestProvider
GleanProvider
JoernProvider
```

External data flow:

```text
tool-specific output
        ↓
    provider
        ↓
normalized Atlas facts
        ↓
       PKIR
```

Atlas must not encode SCIP semantics throughout its core.

It must not encode Glean semantics throughout its core.

It must not encode Markdown AST types throughout its reasoning engine.

The adapter boundary protects the control plane.

---

# 26. Migration Providers

The same architecture should apply to changes.

Conceptual interface:

```rust
trait MigrationProvider {
    fn analyze(
        &self,
        request: MigrationRequest
    ) -> Result<MigrationPlan>;

    fn apply(
        &self,
        plan: &MigrationPlan
    ) -> Result<MigrationResult>;

    fn verify(
        &self,
        result: &MigrationResult
    ) -> Result<Verification>;
}
```

Implementations might include:

```text
GitMoveProvider
MarkdownRewriteProvider
AstGrepMigrationProvider
OpenRewriteProvider
PandocMigrationProvider
AgentMigrationProvider
```

This separates:

```text
what Atlas wants changed
```

from:

```text
how a particular language/tool performs that change
```

---

# 27. The Role of AI

Atlas should not use an LLM for tasks that deterministic tools solve better.

Avoid LLMs for:

```text
find functions
find definitions
find references
parse Markdown
parse Git history
check links
perform exact text search
apply deterministic rename
enumerate files
calculate hashes
validate schemas
```

Use semantic reasoning for ambiguity:

```text
Do these two documents represent the same concept?

Is this historical claim still current?

Does this rationale conflict with current SPEC?

Which of several conflicting pages should become canonical?

How should these clusters be named?

Does a code change materially require an architecture update?

Which context bundle best answers this task?
```

The target architecture is therefore roughly:

```text
deterministic extraction
        +
bounded semantic reasoning
        +
deterministic verification
```

not:

```text
LLM reads everything and guesses
```

---

# 28. Storage Strategy: SQLite First

Do not introduce a graph database merely because the data is graph-shaped.

Initial PKIR tables could be:

```sql
entity
relation
claim
evidence
locator
revision
authority
```

Many graph operations can be implemented initially using:

- indexes;
- joins;
- recursive CTEs.

Examples:

```text
neighbors(entity)
documents_for(symbol)
tests_for(component)
dependencies(component)
claims_supported_by(code-location)
```

SQLite provides:

- local-first operation;
- a single-file database;
- mature transaction semantics;
- low operational burden;
- excellent suitability for a developer tool.

The database should remain behind a storage interface so it can be replaced later.

---

# 29. Tantivy: Later Full-Text Search Backend

Tantivy is a Rust library for building full-text search engines and uses BM25 relevance.

It becomes relevant when Atlas needs its own fast search over:

```text
documents
headings
claims
symbols
evidence
Git revisions
```

It is not required for P0 because MkDocs/local grep/current repository tools already provide useful search.

Adopt Tantivy only when measurements show Atlas needs:

- lower-latency unified search;
- programmatic search ranking;
- hybrid ranking with authority/graph factors;
- local embedded indexing.

A future Atlas score could combine:

```text
exact ID match
+
symbol match
+
BM25
+
graph proximity
+
authority
+
freshness
+
optional semantic similarity
```

Vector search is not necessary to start.

---

# 30. Glean: Optional Large-Scale Fact Backend

Glean is highly relevant conceptually but should not be a P0 dependency.

Its official model is already close to several Atlas ideas:

```text
facts
predicates
schemas
queries
derived predicates
```

Glean also supports user-defined schemas and can store information beyond its built-in code indexes.

This raises an important possibility:

```text
Atlas PKIR
     │
StorageProvider
   /      \
SQLite    Glean
local     scale
```

Glean may eventually serve as:

- large repository fact storage;
- derived relation engine;
- cross-repository indexing layer;
- scalable code-knowledge backend.

But Atlas should not require a Glean deployment merely to operate on one developer repository.

Use it when scale justifies it.

---

# 31. Joern: Deep Analysis Tier

Joern uses a Code Property Graph (CPG), combining program constructs and relationships in a graph representation.

This is useful for deeper program analyses such as:

```text
data flow
control flow
security analysis
program patterns
```

But it is more expensive and operationally heavier than basic syntax/symbol indexing.

Use a tiered analysis model:

```text
Tier 0  filesystem + Git
Tier 1  Markdown/config/schema
Tier 2  ast-grep
Tier 3  SCIP
Tier 4  Joern
Tier 5  LLM semantic reasoning
```

Every task should use the cheapest tier capable of answering it.

Joern is therefore a future deep-analysis adapter, not a baseline requirement.

---

# 32. OpenRewrite: Semantic Migration Backend

OpenRewrite represents transformations as reusable recipes over its semantic tree model and is designed for automated code migrations and refactoring.

Use it later for:

```text
framework upgrades
API migrations
package moves
dependency migrations
type-aware changes
large semantic refactors
```

Potential routing:

```text
Migration request
      │
      ├── simple file/text change → native/Git
      ├── structural code change → ast-grep
      ├── semantic migration → OpenRewrite
      └── ambiguous transformation → agent-assisted plan
```

Atlas should produce the migration intent and verification contract; the specialized engine performs the transformation.

---

# 33. Cytoscape.js: Visualization, Not Knowledge Storage

Cytoscape.js is valuable for displaying project graphs and running graph algorithms in a frontend.

Potential future UI:

```text
Atlas API
    ↓
graph query
    ↓
JSON nodes/edges
    ↓
Cytoscape.js
```

This could visualize:

- doc ownership;
- code-to-doc relationships;
- module dependencies;
- concepts;
- tests;
- execution flows;
- provenance chains.

Cytoscape.js should not define Atlas's graph model. It is a rendering and interaction client.

---

# 34. Obsidian: Optional Human Workspace

Obsidian can remain useful as a local Markdown browsing and editing environment.

The correct relationship is:

```text
Markdown files
   ↓
Obsidian view

Markdown files
   ↓
MkDocs view

Markdown files
   ↓
Atlas model
```

Do not allow Obsidian-specific features to become mandatory repository semantics.

In particular, prefer portable Markdown links over requiring proprietary wiki-link conventions unless a translation layer is intentionally introduced.

The future “evolution of Obsidian” described by Atlas is not primarily a prettier editor. It is:

```text
human knowledge workspace
+
repository facts
+
code intelligence
+
authority model
+
automated validation
+
agent context
+
migration planning
+
graph/query surface
```

Obsidian can remain one interface over that substrate.

---

# 35. Grok Build as Architectural Inspiration

Grok Build is useful as a reference architecture, not as a foundational dependency.

The project was open-sourced in July 2026. Its published architecture exposes practical patterns including:

- context assembly;
- tool-call dispatch;
- tool registry;
- TUI;
- local-first operation;
- config-driven behavior;
- plugins;
- hooks;
- skills;
- MCP servers;
- subagents;
- headless execution;
- workflows.

The most relevant ideas for Atlas are:

```text
small control plane
config-driven
local-first
extensions behind interfaces
headless automation
one interactive CLI/TUI surface
structured tools
agent orchestration
```

Atlas should borrow these design patterns while remaining deterministic without an LLM.

The documentation control plane must work even when:

```text
no model API is configured
no internet exists
no agent is running
```

AI is an optional semantic worker, not a runtime prerequisite for basic repository integrity.

---

# 36. Super-Atlas: Best-of-Breed Composition

A mature architecture can eventually look like:

```text
                           ATLAS
                 Repository Knowledge Control Plane
                              │
          ┌───────────────────┼────────────────────┐
          │                   │                    │
       INGEST               MODEL                ACTION
          │                   │                    │
          ▼                   ▼                    ▼
       OSS tools             PKIR              OSS tools
```

Expanded:

```text
Repository
   │
   ├── Git
   ├── Markdown
   ├── JSON/YAML schemas
   │
   ├── legacy docs ───── Pandoc
   ├── complex docs ──── Docling
   │
   ├── structural code ─ ast-grep
   ├── symbols ───────── SCIP
   ├── deep analysis ─── Joern
   ├── large-scale facts Glean
   │
   └── tests / CI / build evidence
                   │
                   ▼
             Atlas Providers
                   │
                   ▼
                 PKIR
                   │
        ┌──────────┼──────────┐
        │          │          │
      Search     Graph      Evidence
        │          │          │
     Tantivy     SQLite     SQLite
        │          │          │
        └──────────┼──────────┘
                   ▼
              Atlas Engine
                   │
     ┌─────────────┼──────────────┐
     │             │              │
    MAP         CONTEXT        MIGRATE
     │             │              │
 Cytoscape       Agents     ast-grep /
 Mermaid         MCP/API    OpenRewrite
 MkDocs
```

This is a “super Atlas” because it combines specialist engines rather than replacing them.

---

# 37. Atlas Bootstrap Pipeline

A future bootstrap command could operate as:

```text
atlas bootstrap .
        │
        ▼
 Repository Probe
        │
   ┌────┼──────────────┐
   ▼    ▼              ▼
  Git  Docs           Code
   │    │              │
   │ Markdown       ast-grep
   │ Pandoc         SCIP
   │ Docling          │
   └────┬──────────────┘
        ▼
     Raw Facts
        │
        ▼
    PKIR Normalize
        │
        ▼
   Entity Resolution
       / \
      /   \
 deterministic
    merge     ambiguous
                │
                ▼
               LLM
                │
        ┌───────┘
        ▼
  Canonical Project Model
        │
   ┌────┼──────────┐
   ▼    ▼          ▼
 Search Map     Conflicts
   │    │          │
   └────┼──────────┘
        ▼
     Context
        │
        ▼
      Agents
```

The LLM handles ambiguity, not basic extraction.

---

# 38. Context Compilation

One of Atlas's highest-value features should be task-specific context construction.

Instead of giving an agent the whole documentation tree:

```text
Task:
change child budget attenuation
```

Atlas could derive:

```text
SPEC clauses
+
backend architecture pages
+
relevant event/schema reference
+
current execution task
+
symbol definitions
+
callers
+
tests
+
recent relevant Git change
```

The future command:

```bash
atlas context "modify child budget attenuation"
```

could produce a bounded context bundle with provenance explaining why each item was selected.

This is more valuable than a generic vector search because the selection can account for:

- canonical ownership;
- authority;
- code proximity;
- symbol relationships;
- current status;
- freshness;
- test coverage;
- explicit metadata.

---

# 39. Automatic Drift Detection

The generated knowledge layer enables increasingly powerful drift checks.

Examples:

```text
docs mention a canonical symbol
but SCIP no longer resolves it
```

```text
architecture claims one runtime owner
but structural analysis finds a second production caller
```

```text
reference event exists
but no emitter is found
```

```text
guide links to removed command
```

```text
SPEC invariant has no mapped test
```

These should initially be warnings and experiments.

Only promote a detector to a blocking CI gate when its precision is proven.

This avoids creating a noisy control plane that developers learn to ignore.

---

# 40. Documentation Change Workflow

The normal development loop should remain simple.

```text
milestone / active task
        ↓
implementation
        ↓
tests
        ↓
did durable behavior change?
        │
        ├─ no → no doc rewrite required
        │
        └─ yes
             │
             ├─ normative contract? → SPEC
             ├─ architecture? → architecture page
             ├─ API/schema/event? → reference
             ├─ usage? → guide
             ├─ product behavior? → product
             └─ irreducible rationale? → decisions
        ↓
just docs-check
        ↓
PR / merge
```

No status report is generated merely because a change occurred.

---

# 41. Anti-Bloat Constitution

The documentation system should encode the following rules:

1. **One durable fact has one canonical owner.**
2. **Do not create a document to explain that another document changed.**
3. **If information can be generated reliably from code, generate it instead of copying it.**
4. **Research never becomes canonical automatically.**
5. **Generated data is never edited manually.**
6. **Create a new Markdown page only when no existing canonical owner can contain the information cleanly.**
7. **A code change that alters a durable contract updates the canonical documentation in the same change.**
8. **Git owns history; active docs own current truth.**
9. **MkDocs, Obsidian, AI, and Atlas are interfaces or derived views; Markdown + code + Git remain evidence sources.**
10. **Prefer adapters and configuration over new implementations when OSS already solves the capability.**
11. **Do not maintain the same API shape manually in source and Markdown.**
12. **Do not load `research/` into normal agent context unless the task requires it.**
13. **Do not create an ADR for ordinary architecture documentation.**
14. **A decision record exists only when the rationale or reversal criterion cannot be reconstructed from current SPEC, architecture, reference, or code.**
15. **Every new automation must demonstrate lower maintenance cost than the manual process it replaces.**

---

# 42. Technologies Explicitly Not Used Now

The future stack includes many powerful technologies that should deliberately remain outside P0.

## 42.1 Direct Tree-sitter

**Now:** no.

**Why:** ast-grep already provides a convenient polyglot structural interface.

**Later:** use direct Tree-sitter when Atlas needs lower-level parsing, custom language support, source mapping, or extraction behavior unavailable through ast-grep.

---

## 42.2 Glean

**Now:** no.

**Why:** too much operational machinery for a single-repository documentation-control problem.

**Later:** candidate `StorageProvider` / code fact backend for very large repositories or cross-repository Atlas deployments.

---

## 42.3 Joern

**Now:** no.

**Why:** deep Code Property Graph analysis is unnecessary for everyday documentation integrity.

**Later:** on-demand Tier-4 provider for data flow, security analysis, or complex program relationships.

---

## 42.4 OpenRewrite

**Now:** no baseline dependency.

**Why:** current priority is knowledge organization, not large semantic framework migrations.

**Later:** `MigrationProvider` for complex type-aware or framework-level refactoring.

---

## 42.5 Tantivy

**Now:** no.

**Why:** MkDocs, repository search, and generated indexes are sufficient to validate P0 concepts.

**Later:** embedded Atlas full-text/BM25 index when unified low-latency programmatic search becomes useful.

---

## 42.6 Neo4j

**Now:** no.

**Why:** graph-shaped data does not require a graph database. It adds deployment and data-model complexity.

**Later:** only if proven query/workload requirements exceed SQLite/Glean or a specialized backend provides a measurable advantage.

Likely unnecessary.

---

## 42.7 GraphRAG

**Now:** no.

**Why:** the main problem is authority, identity, provenance, and deterministic repository relationships, not merely semantic retrieval over a graph.

**Later:** potentially as a context/research adapter after PKIR exists, never as the canonical project model.

---

## 42.8 Vector Database

**Now:** no.

**Why:** exact IDs, metadata, symbols, BM25, links, and graph relationships should be exploited first.

**Later:** embeddings can become an optional retrieval signal when semantic recall provides measurable incremental value.

---

## 42.9 Backstage

**Now:** no.

**Why:** Backstage is primarily an internal developer portal/platform experience. AETHER's immediate problem is repository knowledge integrity.

**Later:** an organization-scale Atlas could expose data to Backstage rather than become Backstage.

---

## 42.10 Cytoscape.js

**Now:** not required.

**Why:** no need for graph visualization before the knowledge model is useful.

**Later:** excellent client for an Atlas map UI.

---

## 42.11 Custom Rust Parser / Custom LSP

**Now:** explicitly no.

**Why:** extremely high reinvention cost. SCIP, ast-grep, Tree-sitter, language servers, and existing parsers already solve most syntax/symbol problems.

**Later:** write only missing adapters or project-specific inference.

---

## 42.12 Custom Graph Database

**Now:** no.

**Why:** premature infrastructure.

**Later:** only after measured SQLite/Glean limitations.

---

# 43. Tool Adoption Matrix

| Technology | P0 | P1 | Future Atlas | Role |
|---|---:|---:|---:|---|
| MkDocs Material | Yes | Yes | UI adapter | human docs |
| `just` | Yes | Yes | may become Atlas CLI wrapper | orchestration |
| YAML frontmatter | Yes | Yes | input evidence | metadata |
| JSON Schema | Yes | Yes | schema provider | contract |
| jsonschema | Yes | Yes | adapter/internal | validation |
| markdownlint-cli2 | Yes | Yes | validator | Markdown structure |
| Vale | Yes | Yes | validator | terminology |
| Lychee | Yes | Yes | validator | links |
| pre-commit | Yes | Yes | external | local gates |
| Mermaid | Yes | Yes | rendering adapter | diagrams |
| yq/jq | Yes | Yes | optional | metadata query |
| Griffe | P0.5 | Yes | provider | Python API model |
| mkdocstrings | P0.5 | Yes | view generator | Python docs |
| TypeDoc | later | Yes | provider | TypeScript API model |
| Pandoc | on demand | Yes | ingestion provider | format conversion |
| Docling | on demand | Yes | ingestion provider | complex docs |
| ast-grep | experiment | Yes | provider + migration | AST search/rewrite |
| SCIP | experiment | Yes | provider | symbols |
| SQLite | generated scripts | likely | default store | PKIR |
| Tantivy | No | optional | likely | full-text |
| Glean | No | No | optional scale backend | facts |
| Joern | No | optional | optional deep provider | CPG |
| OpenRewrite | No | optional | migration provider | semantic rewrite |
| Cytoscape.js | No | optional | UI | graph |
| Tree-sitter direct | No | fallback | provider internals | parsing |
| Neo4j | No | No | unlikely | graph DB |
| GraphRAG | No | No | optional consumer | semantic retrieval |
| Vector DB | No | No | optional | embeddings |

---

# 44. P0 Implementation Sequence

The immediate implementation should be deliberately small.

## Step 1 — Freeze the clean docs taxonomy

Do not restructure documentation again while setting up tools.

Use the current global/backend/frontend/product/execution/theory/research structure.

## Step 2 — Create `.docs/`

Add:

```text
.docs/
├── document.schema.json
├── taxonomy.yml
├── terminology.yml
└── vale/
```

## Step 3 — Simplify permanent frontmatter

Define the minimum required metadata set.

Migrate reconstruction-only metadata out of normal authoring where it no longer adds durable value.

## Step 4 — Add `just`

Create the stable commands:

```text
docs-check
docs-build
docs-serve
docs-full
docs-map
```

Do not add dozens of commands before they are needed.

## Step 5 — Install fast validators

Wire:

```text
jsonschema/custom metadata check
markdownlint-cli2
Vale
internal links
stale paths
```

## Step 6 — Install MkDocs

Make the existing tree navigable and searchable.

Do not change document ownership just to satisfy the site generator.

## Step 7 — Install pre-commit

Only fast checks.

## Step 8 — Add CI

Run:

```text
fast checks
MkDocs strict build
external Lychee
generated index reproducibility
canonical ownership checks
```

## Step 9 — Generate catalog + links

Keep scripts tiny.

The output should be JSONL.

## Step 10 — Add API generation

Start with Python Griffe/mkdocstrings.

Add TypeDoc when frontend surfaces stabilize.

This completes P0/P0.5.

---

# 45. P1 Experiment Sequence

P1 exists to discover how much Atlas can reuse.

## Experiment A — ast-grep

Choose 5–10 architectural concepts and measure:

```text
definition discovery
pattern discovery
deprecated implementation detection
boundary checks
false positives
performance
JSON output quality
```

## Experiment B — SCIP

Index Python and TypeScript.

Measure:

```text
definitions
references
implementations
symbol stability
incremental cost
cross-language usefulness
```

## Experiment C — Docs ↔ code map

Build:

```text
code-map.jsonl
```

Example:

```json
{
  "doc": "backend.arch.kernel",
  "relation": "implemented_by",
  "symbol": "scip-python ...Kernel...",
  "evidence": ["..."]
}
```

## Experiment D — Agent context

Use generated data to construct a task-specific context bundle.

Compare:

```text
whole docs context
vs
structured context selection
```

Measure quality, tokens, latency, and missed information.

---

# 46. P1.5: Proto-Atlas

Only after P1 proves value should the project's custom glue become a named subsystem.

Possible commands:

```bash
docs map
docs query
docs show backend.arch.kernel
docs context "change agent.spawn budget semantics"
docs conflicts
docs stale
```

The implementation can still be Python/shell if that is fastest.

Do not rewrite it in Rust merely to declare Atlas has begun.

Atlas begins when a stable abstraction appears, not when a language is chosen.

---

# 47. P2: Atlas Control Plane

At P2, formalize:

```text
PKIR
FactProvider
MigrationProvider
StorageProvider
SearchProvider
ContextCompiler
AuthorityResolver
EvidenceResolver
```

At this point a Rust core becomes attractive if:

- performance matters;
- static schemas are stable;
- a single binary is valuable;
- providers can be cleanly isolated;
- the Python prototype has taught what needs to exist.

A minimal layout might be:

```text
atlas/
├── crates/
│   ├── atlas-pkir/
│   ├── atlas-engine/
│   ├── atlas-adapters/
│   ├── atlas-cli/
│   └── atlas-mcp/
│
├── schemas/
├── rules/
└── prompts/
```

Do not begin with 20 crates.

---

# 48. P3: Scale and Deep Intelligence

Only measured needs should unlock:

```text
Glean
Joern
Tantivy
OpenRewrite
distributed indexing
cross-repository Atlas
embeddings
advanced graph UI
```

The future architecture remains stable because each appears behind a provider interface.

---

# 49. Acceptance Criteria by Phase

## P0

Pass when:

- all active docs validate against metadata schema;
- no canonical ID collision exists;
- links and anchors pass;
- terminology rules catch known deprecated vocabulary;
- MkDocs builds strictly;
- a contributor can run one command for normal docs validation;
- generated artifacts are reproducible.

## P0.5

Pass when:

- catalog and relationships are generated deterministically;
- public API reference is generated from code where appropriate;
- no generated output is manually owned.

## P1

Pass when:

- docs↔code relationships are demonstrated for real AETHER subsystems;
- ast-grep and SCIP costs/benefits are measured;
- false-positive rates are documented;
- structured outputs can feed agent context.

## P2

Pass when:

- PKIR is tool-independent;
- at least two FactProviders produce interchangeable normalized facts;
- authority/provenance are first-class;
- Atlas can compile a task context without loading the entire repository;
- removing one provider does not break the core model.

---

# 50. Scientific Hypotheses the AETHER Experiment Can Test

The AETHER documentation problem can become a real Atlas research program.

## H1 — Minimal explicit metadata is sufficient

Can ~7 human-authored fields plus generated evidence make a repository reliably machine-readable?

## H2 — Symbol protocols + AST structure solve most docs↔code mapping

Can SCIP + ast-grep resolve enough relationships that Atlas does not need a custom compiler/indexer?

## H3 — Authority-aware retrieval beats semantic retrieval alone

Does a context compiler using:

```text
authority
canonical ownership
symbol proximity
graph relations
freshness
```

produce better task context than embedding similarity alone?

## H4 — Repository organization can remain Markdown-native

Can PKIR be fully reconstructible while Markdown remains the human source?

## H5 — Deterministic machinery can resolve the majority of repository knowledge tasks

What fraction of operations require actual semantic LLM reasoning?

The desired result is likely:

```text
large deterministic majority
+
small semantic ambiguity layer
```

but this must be measured.

---

# 51. Design Principle: Atlas as the LLVM IR of Project Knowledge

A useful analogy is:

```text
C / C++ / Rust / ...
       ↓
      LLVM IR
       ↓
many optimization / target backends
```

Atlas aspires to:

```text
Markdown / Git / SCIP / ast-grep / Docling / schemas / tests / Glean / Joern
                              ↓
                             PKIR
                              ↓
       search / map / context / migration / agents / verification / UI
```

The innovation is the stable intermediate semantics, not the individual parser.

This prevents Atlas from becoming a monolithic reimplementation of the software ecosystem.

---

# 52. Final Recommended Architecture

The immediate stack:

```text
                       AETHER
                         │
                         ▼
                  Markdown + Git
                         │
      ┌──────────────────┼──────────────────┐
      │                  │                  │
 metadata/schema      quality           navigation
      │                  │                  │
 JSON Schema       markdownlint          MkDocs
 jsonschema         Vale
                   Lychee
      │                  │
      └──────────────────┼──────────────────┘
                         │
                    pre-commit / CI
                         │
                         ▼
                 generated knowledge
                         │
       catalog / links / ownership / API
                         │
                         ▼
                ast-grep + SCIP experiments
                         │
                         ▼
                    Proto-Atlas
                         │
                         ▼
                       PKIR
                         │
                         ▼
                Atlas Control Plane
```

The future stack:

```text
                        ATLAS
                         │
        ┌────────────────┼────────────────┐
        │                │                │
      ingest            PKIR            actions
        │                │                │
 Pandoc/Docling      SQLite/Glean      Git
 Markdown/Git        Tantivy           ast-grep
 SCIP/ast-grep       relations         OpenRewrite
 Joern               evidence          agents
        │                │                │
        └────────────────┼────────────────┘
                         │
                     context/map
                         │
               MkDocs / Cytoscape / MCP
```

---

# Conclusion

The correct next step is not another large architecture exercise.

AETHER already has a clean enough documentation taxonomy to begin development. The missing piece is a **permanent, low-friction documentation control plane**.

P0 should immediately deploy mature OSS for:

- navigation;
- metadata validation;
- Markdown quality;
- terminology;
- links;
- diagrams;
- Git hooks;
- API generation;
- deterministic knowledge indexes.

Pandoc and Docling remain ingestion tools rather than daily dependencies.

ast-grep and SCIP become the first controlled experiments connecting documentation to real code.

The evidence from those experiments determines the actual Atlas core.

The future Atlas should remain thin: a control plane over specialist tools, centered on a Project Knowledge Intermediate Representation that owns identity, semantics, authority, provenance, reconciliation, and context compilation.

The ultimate system is therefore not an attempt to replace Obsidian, MkDocs, SCIP, Glean, Joern, Tree-sitter, OpenRewrite, or coding agents.

It is a layer above them:

> **A local-first, tool-independent project knowledge substrate that continuously compiles repository evidence into a canonical model and uses that model to keep documentation, code, decisions, context, migrations, and agents aligned.**

That architecture gives AETHER immediate productivity and gives Atlas a path to become significantly more capable without inheriting the maintenance burden of reinventing every subsystem it orchestrates.

---

# Official Technology References Consulted

The following upstream sources were used to verify capabilities and current project direction as of 2026-08-30:

- Material for MkDocs: https://squidfunk.github.io/mkdocs-material/
- `just`: https://github.com/casey/just
- pre-commit: https://pre-commit.com/
- Vale: https://vale.sh/
- markdownlint-cli2: https://github.com/DavidAnson/markdownlint-cli2
- Lychee: https://github.com/lycheeverse/lychee
- Mermaid: https://mermaid.js.org/
- Pandoc: https://pandoc.org/
- Docling: https://docling-project.github.io/docling/
- ast-grep: https://ast-grep.github.io/
- SCIP: https://github.com/scip-code/scip
- Griffe: https://mkdocstrings.github.io/griffe/
- mkdocstrings: https://mkdocstrings.github.io/
- TypeDoc: https://typedoc.org/
- Tantivy: https://github.com/quickwit-oss/tantivy
- Glean: https://glean.software/
- Joern: https://docs.joern.io/
- OpenRewrite: https://docs.openrewrite.org/
- Grok Build open-source announcement: https://x.ai/news/grok-build-open-source
- Grok Build repository: https://github.com/xai-org/grok-build
