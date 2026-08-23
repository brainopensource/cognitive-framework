---
status: living
id: engineering-documentation-governance
class: how-to
authority: descriptive
canonical_for:
  - documentation-governance-guide
source_of_truth:
  - AGENTS.md#7-strict-documentation-anti-sprawl-invariant
derived_from:
  - tools/linters/check_doc_metadata.py
  - tools/linters/check_markdown_links.py
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: lead-documentation-engineer
version: "0.6.1"
last_verified: 2026-08-23
supersedes: []
superseded_by: null
---

# Documentation Governance & Anti-Sprawl Rules

> **Status:** `AS_BUILT`.

---

## 1. The Clean Triad Rules
1. **Law (What)** $\to$ Edit [`docs/SPEC.md`](../SPEC.md) and [`docs/04_annex/`](../04_annex/).
2. **Decisions (Why)** $\to$ Append a new ADR in [`docs/05_adr/`](../05_adr/).
3. **Execution (How & Now)** $\to$ Edit [`docs/03_sprints/sprint_active.md`](../03_sprints/sprint_active.md).

Future milestone sequencing and inactive backlog live in
[`docs/02_roadmap/milestones.md`](../02_roadmap/milestones.md); they do not authorize work.

## 2. Language and Placement

- Living and canonical documentation is written in English.
- Frozen research, proposals, diagrams, and tooling notes preserve their original language and are
  not translated in place.
- Update an existing canonical or modular owner before considering a new Markdown file.
- Architecture pages explain boundaries and flows; contract pages point to exact schemas; protocol
  pages point to executable ports; engineering pages describe repeatable contributor procedures.
- Derived pages link to canonical law and code instead of copying event catalogs, SPI definitions,
  schemas, or budget matrices.

---

## 3. Automated Quality Verification

Every living document must pass automated linting before PR merge:

```bash
# Validate standardized YAML metadata & canonical ownership
python3 tools/linters/check_doc_metadata.py

# Verify local markdown links
python3 tools/linters/check_markdown_links.py

# Verify RF falsifier IDs and citations
python3 tools/linters/check_falsifier_ids.py

# Scan for stale path tokens
python3 tools/linters/check_stale_paths.py
```
