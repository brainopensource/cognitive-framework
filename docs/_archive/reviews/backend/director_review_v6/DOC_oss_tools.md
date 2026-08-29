# AETHER Documentation Reconstruction — Evidence-Driven OSS Toolbox

## Purpose

Define the smallest defensible tool stack for documentation reconstruction of
`brainopensource/cognitive-framework` on `main`, preferring existing repository capabilities and
adopting new dependencies only after measured need.

This catalog does not prescribe phase order, product architecture, canonical taxonomy, or cutover.
It does not authorize dependency installation, production-code changes, active-tree changes, or
blocking CI.

## Bootstrap precedence

1. `docs/_archive/reviews/backend/director_review_v6/DOC_prompt_documentation_todo.md`
2. `docs/_archive/reviews/backend/director_review_v6/DOC_ARCHITECTURE_SPEC.md`
3. `docs/_archive/reviews/backend/director_review_v6/DOC_process_management_todo.md`
4. `docs/_archive/reviews/backend/director_review_v6/DOC_migration_process.md`
5. `docs/_archive/reviews/backend/director_review_v6/DOC_oss_tools.md`

If an older migration-oriented instruction conflicts with the greenfield/code-first phase order,
`DOC_prompt_documentation_todo.md` wins.

None of these bootstrap documents overrides AETHER product truth; they govern how that truth is
reconstructed and represented.

Canonical terms throughout this package are: documentation reconstruction, AS_BUILT, TARGET,
candidate-docs/, legacy loss audit, canonical owner, canonical ID, implementation evidence,
normative authority, generated machine layer, independent audit, governance ratification, cutover,
and rollback.

## Classification vocabulary

- `REQUIRED` — needed for the minimum viable alpha and already available in the repository or base
  development environment.
- `CONDITIONAL` — adopt only when an observed input or validation gap meets stated criteria.
- `EXPERIMENTAL` — bounded measurement; never blocks reconstruction or becomes authority.
- `REJECTED_FOR_ALPHA` — not justified for the initial reconstruction; reconsider only with new
  evidence and governance approval where applicable.

“Required” means required for reconstruction execution, not permission to add a new dependency.

## Existing repository capabilities inspected

The current repository already supplies:

- Git for exact revision, diff, provenance, and recovery;
- Python 3.10+ and standard-library filesystem, JSON, AST, and `unittest` facilities;
- `rg`/filesystem enumeration for fast deterministic discovery;
- `jsonschema` as a declared Python dependency;
- Node/npm scripts for TypeScript typechecking and tests;
- `tools/linters/check_doc_metadata.py` for living-document metadata patterns;
- `tools/linters/check_doc_budgets.py` for bounded living documents;
- `tools/linters/check_markdown_links.py` for local links and fragments;
- `tools/linters/check_stale_paths.py` for stale documentation paths;
- `tools/linters/check_falsifier_ids.py` for identifier allocation;
- `tools/linters/check_boundaries.py`, `check_domain_blindness.py`, and
  `check_isolation_policy.py` for implementation-boundary evidence;
- `tools/linters/check_tcb_budget.py` and `check_duplication.py --enforce`;
- `tools/linters/scan_secrets.py`;
- Python tests under `test/`, schemas under `schemas/`, package metadata in `pyproject.toml`, npm
  workspaces in `package.json`, and CI in `.github/workflows/ci.yml`;
- release and qualification scripts under `ci/` and runners/code generation under `tools/`.

Current documentation linters may intentionally exclude `candidate-docs/` or `_archive/`. Use their
logic as evidence and invoke candidate-scoped wrappers only under `tools/docs_alpha/`; do not modify
or promote active checks during reconstruction.

## Adoption decision record

Before adopting a new tool, record:

- problem solved and affected phase;
- representative corpus/input;
- baseline method and baseline result;
- setup cost and installation footprint;
- ongoing maintenance cost;
- deterministic-output behavior;
- hermetic CI suitability and external-network needs;
- cross-platform impact;
- measured time and token reduction;
- accuracy/coverage improvement and new errors;
- overlap with existing tooling;
- security/licensing considerations;
- classification and keep/remove decision.

A tool is retained only when its measurable benefit exceeds setup, maintenance, determinism, and
overlap costs. Record which tools were actually used and the benefit they produced in
`.generated/knowledge/generation-manifest.json` or its approved equivalent.

## Minimum viable alpha stack

| Tool/capability | Class | Use | Reason |
|---|---|---|---|
| Git | `REQUIRED` | branch/SHA capture, diff, provenance, rollback reference | Already authoritative for repository state and recovery. |
| `rg`, `find`, shell path utilities | `REQUIRED` | deterministic file/text inventory | Already available, fast, auditable, and sufficient for initial discovery. |
| Python stdlib (`pathlib`, `json`, `ast`, `re`, `unittest`) | `REQUIRED` | inventory, Python symbols/imports, JSONL generation, tests | No new dependency; deterministic bounded scripts. |
| Existing `jsonschema` dependency | `REQUIRED` | candidate metadata/generated-record validation | Already declared in `pyproject.toml`; avoids a custom validator. |
| Existing repository linters | `REQUIRED` | metadata patterns, links, paths, budgets, IDs, secrets, architecture evidence | Matches current repository governance and CI. |
| Existing Python/TypeScript tests and schemas | `REQUIRED` | implementation evidence and traceability | Executable AS_BUILT evidence. |
| Minimal scripts under `tools/docs_alpha/` | `REQUIRED` when a gap exists | candidate-scoped inventory, generation, validation, retrieval harness | Keeps temporary reconstruction engineering isolated. |
| Markdown with validated frontmatter | `REQUIRED` | canonical human-authored representation | Diffable, reviewable, and compatible with existing repository practice. |
| Generated JSONL under `.generated/knowledge/` | `REQUIRED` | catalog, headings, relations, code map, audit/reconciliation | Derived, reproducible, stream-friendly machine layer. |

No additional package is part of the minimum viable alpha.

## Tools for initial deterministic inventory

### Git, `rg`, filesystem utilities, and Python AST — `REQUIRED`

Use Git to pin the subject, `rg --files` and bounded filesystem commands to enumerate it, and Python
AST for Python imports, definitions, and entry points. Use package/schema/test configuration directly
for production roots and public surfaces. Record versions and deterministic sorting.

### ast-grep — `EXPERIMENTAL`

Use only where structural multi-language extraction demonstrably improves precision or maintenance
over `rg` and Python AST. Test on a bounded Python/TypeScript subsystem. Compare correct relations,
false positives, runtime, installation size, and rule-maintenance cost. Do not require it for baseline
inventory.

### SCIP — `EXPERIMENTAL`

Use only on a bounded subset where cross-language symbol definition/reference relationships justify
indexing cost. Compare against existing imports, package boundaries, schemas, tests, and ast-grep.
Reject if it does not materially improve code-to-document routing or traceability.

### Direct Tree-sitter integration — `REJECTED_FOR_ALPHA`

The alpha has no demonstrated need for a custom parser layer beyond language ASTs and a possible
ast-grep experiment. Reconsider only if measured extraction gaps cannot be addressed otherwise.

## Tools useful for semantic reconstruction

### Frontier and ordinary AI models — `CONDITIONAL`

Use models according to the management document: frontier models for architecture, ambiguity,
conflict, and ownership; ordinary capable models for bounded writing from approved packets. Model
output is never implementation evidence or normative authority and must be reviewed against sources.

### Pandoc — `CONDITIONAL`

Use only when a legacy source format actually requires conversion and Pandoc has a suitable reader.
Do not run it over native Markdown merely to normalize style. Record conversion command, source,
losses, warnings, and manual-review burden.

### Docling — `CONDITIONAL`

Use only for complex PDF/Office extraction where layout, reading order, or tables defeat simpler
tools. It is not required for the repository's Markdown-first corpus. Extracted content remains
legacy evidence subject to the late legacy loss audit.

### `jq`/`yq` — `CONDITIONAL`

Use when already available and they materially simplify reproducible JSON/YAML inspection. Python is
the portable default, so absence of these tools must not block reconstruction or lead to a new
mandatory dependency.

## Validation tools

### Existing repository documentation linters — `REQUIRED`

Use the applicable checks under `tools/linters/` first. Candidate-scoped validation must account for
their current globs and exclusions. Reuse logic through bounded wrappers rather than changing active
CI before governance ratification.

### Minimal candidate metadata validator — `REQUIRED`

Implement only if existing checks do not scan `candidate-docs/`. Use the existing `jsonschema`
dependency and the approved schema. Validate IDs, enums, ownership, evidence/authority requirements,
and referential integrity.

### Markdownlint — `CONDITIONAL`

Adopt only if existing rendering or consistency failures create measurable review cost. Start with a
small rule set compatible with current Markdown; avoid bulk cosmetic churn.

### Vale — `CONDITIONAL`

Adopt only after a minimal AETHER terminology policy exists and a sample shows valuable defects with
acceptable false positives and maintenance cost. It must not invent product terminology or replace
semantic review.

### Lychee — `CONDITIONAL`

Adopt only when existing local-link validation is insufficient. Internal checks must remain
hermetic. External-network links require controlled retries, allow/deny/ignore policy, caching where
appropriate, and non-blocking treatment until reliability is measured.

### pre-commit — `CONDITIONAL`

Adopt only after commands are stable, deterministic, and fast enough for local use. Initial
reconstruction runs commands explicitly. Enabling hooks or blocking CI requires later governance
ratification.

## Diagrams and publishing

### Mermaid — `CONDITIONAL`

Use only for high-value dependency, sequence, state, or authority relationships that prose cannot
communicate as clearly. Diagram source is derived from or linked to a canonical owner. It never adds
independent facts and must be validated for parse/render success if used.

### MkDocs Material / MkDocs — `CONDITIONAL`

Use only as a presentation consumer after canonical Markdown, navigation, and generated indexes are
valid. Measure whether it improves representative human discovery. It must not own metadata, taxonomy,
or unique content, and it is not a reconstruction or cutover prerequisite.

Other portal/search platforms are `REJECTED_FOR_ALPHA` unless a bounded experiment demonstrates a
specific unmet need.

## Atlas research experiments

Atlas-related tooling remains `EXPERIMENTAL` and non-blocking. Suitable experiments include:

- whether semantic metadata improves correct canonical-owner retrieval;
- whether ast-grep improves TypeScript/Python structural relations over current methods;
- whether SCIP improves cross-language symbol routing enough to justify cost;
- whether alternative chunking/indexing reduces tokens and incorrect-source retrieval.

Each experiment declares hypothesis, baseline, bounded inputs, metrics, cost ceiling, decision rule,
and removal plan. Results are measurements, not product authority or mandatory architecture.

## Canonical representations

- Markdown plus validated frontmatter is the canonical authored representation.
- JSONL indexes are generated, deterministic, reproducible, and manually read-only.
- Generated catalogs, relations, code maps, diagrams, and portals are derived views.
- Git history plus the legacy audit and reconciliation ledgers provide recovery unless governance
  demonstrates a need for retained active records.
- Do not introduce a permanent `_legacy/` active documentation tree by default.

## Tool use by reconstruction phase

| Phase | Default | Optional only after evidence |
|---|---|---|
| Baseline/inventory | Git, `rg`, filesystem tools, Python, repository config | ast-grep, SCIP |
| AS_BUILT discovery | code/tests/schemas/runtime, Python AST, bounded model review | ast-grep, SCIP |
| Candidate writing/TARGET reconciliation | Markdown, approved work packets, capable models | conversion tools for actual non-Markdown inputs |
| Legacy loss audit | `rg`, Python, audit ledgers | Pandoc, Docling |
| Machine layer | Python, `jsonschema`, JSONL | `jq`/`yq` convenience |
| Validation | existing repository linters, candidate wrappers, tests | markdownlint, Vale, Lychee, pre-commit |
| Publishing | none required | MkDocs Material |
| Atlas research | none required | bounded retrieval/AST/symbol experiments |

## Tool evidence log

For every tool actually used, record:

```text
name and version
classification
problem and phase
input scope and recorded SHA
baseline method
commands/configuration
runtime and setup time
output determinism
correct findings and false positives
time/token delta
maintenance/cross-platform/CI impact
keep, remove, or revisit decision
```

An unused proposed tool is recorded as unused, not credited with hypothetical benefit.

## Canonical execution flow

Tooling must support, and never reorder, this flow:

0. Bootstrap documents corrected and committed.
1. Reconstruction branch created.
2. Repository and exact SHA recorded.
3. Deterministic inventory generated.
4. AS_BUILT reconstructed from code/tests/schemas/runtime.
5. Canonical documentation blueprint approved.
6. Candidate AS_BUILT documentation produced.
7. TARGET authority reconciled separately.
8. Legacy loss audit performed.
9. Unique valid knowledge absorbed.
10. Metadata and generated machine indexes produced.
11. Mechanical validation executed.
12. Independent frontier audit completed.
13. Critical findings corrected.
14. Governance change and cutover reviewed.
15. Explicitly authorized cutover performed.
16. Post-cutover validation and rollback check completed.

No tool result authorizes cutover, production-code changes, active documentation deletion, ADR
history rewriting, or blocking CI.
