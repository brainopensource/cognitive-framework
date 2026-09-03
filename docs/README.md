---
id: nav.home
canonical_id: nav.home
class: navigation
authority: descriptive
truth_plane: BOTH
status: living
implementation_status: IMPLEMENTED
owner: documentation-governance
canonical_for:
  - documentation authority explanation
  - machine context navigation and routing rules
  - task to documentation routing
purpose: Canonical root entry point and machine/human documentation router for AETHER.
audience:
  - newcomer
  - operator
  - developer
  - contributor
  - agent
version: 0.9.1a1
last_verified: 2026-08-30
normative_authority:
  - VISION.md
  - docs/SPEC.md
  - docs/decisions.md
  - docs/execution/tasks.md
relationships:
  - arch.system.overview
  - arch.system.boundaries
  - arch.system.data-flow
  - spec.core
  - decision.index
  - execution.tasks
reviewer: documentation-specialist
confidence: high
---

# AETHER Documentation Master Index & Context Router

## 1. Documentation Authority Hierarchy & Rules

AETHER documentation strictly separates constitutional vision, normative law, architecture, reference, and non-canonical research:

| Authority Tier | Document / Directory | Role & Authority Model |
|---|---|---|
| **0. Constitutional** | [`VISION.md`](../VISION.md) | Foundational vision, identity, ontology, and high-level direction. |
| **1. Operational Law** | [`AGENTS.md`](../AGENTS.md) | Operational guidelines and mandatory execution rules for AI agents and human contributors. |
| **2. Human Entry Point** | [`README.md`](../README.md) | High-level repository entry point, setup guide, and validation summary table. |
| **3. Normative Spec** | [`docs/SPEC.md`](SPEC.md) | RFC 2119 normative requirements and architectural refusals. |
| **4. Decisions Index** | [`docs/decisions.md`](decisions.md) | Compact index of accepted Architecture Decision Records (ADRs). |
| **5. Architecture & Reference** | [`docs/architecture/`](architecture/overview.md), [`docs/backend/`](backend/architecture/runtime-execution.md), [`docs/frontend/`](frontend/README.md) | System workflows, subsystem architectures, wire contracts, and API references. |
| **6. Execution Runway** | [`docs/execution/tasks.md`](execution/tasks.md), [`docs/execution/spec.md`](execution/spec.md), [`docs/execution/technical.md`](execution/technical.md), [`docs/execution/milestones.md`](execution/milestones.md), [`docs/execution/backlog.md`](execution/backlog.md) | The 5 operational runway documents: flat task tree, delta spec, handbook, TARGET gates, and capability inventory. |
| **7. Product PRDs** | [`docs/product/`](product/frontend/PRD_FRONTEND_PLATFORM.md) | Client application PRDs and product requirements. |
| **8. Non-Canonical** | [`docs/theory/`](theory/agent-substrate.md), [`docs/research/`](research/), [`docs/reports/`](reports/) | Non-canonical theoretical essays, historical harness research, and post-mortem audit reports (`authority: non-canonical`). |

> [!IMPORTANT]
> **Authority Rule**: Lower-tier documents or non-canonical research/reports (`authority: non-canonical`) must **never** be used to reject a higher-tier requirement or override canonical architecture.

---

## 2. Machine & AI Context Loading Strategy

To optimize LLM context usage (e.g. 16K and 32K context windows) and prevent prompt bloat:

```text
               ┌─────────────────────────────────────────┐
               │             1. Read docs/README.md      │
               └────────────────────┬────────────────────┘
                                    │
               ┌────────────────────▼────────────────────┐
               │   2. Match Task Category in Routing Table│
               └────────────────────┬────────────────────┘
                                    │
               ┌────────────────────▼────────────────────┐
               │  3. Consult .generated/knowledge/ Index │
               │     (ownership, links, code-map, symbols│
               └────────────────────┬────────────────────┘
                                    │
               ┌────────────────────▼────────────────────┐
               │  4. Load ONLY Canonical Owner Document  │
               └─────────────────────────────────────────┘
```

1. **Do NOT load the whole docs corpus by default.** The canonical documentation corpus is designed for targeted retrieval.
2. **First step for any task**: Read [`docs/README.md`](README.md) or query the machine knowledge layer via `python3 tools/docs_rag_v0.py "YOUR QUERY"`.
3. **Inspect Machine Knowledge**: Use `.generated/knowledge/ownership.jsonl`, `code-map.jsonl`, and `symbols.jsonl` to locate exact file paths and line ranges.
4. **Load Canonical Owner First**: Read only the canonical owner Markdown file for the target subsystem.
5. **Non-canonical Research/Reports**: Load files under `docs/research/` or `docs/reports/` **only** when explicitly instructed.

---

## 3. Task-to-Documentation Routing Table

| Task Category | Primary Canonical Owner | Secondary Reference / Evidence | Typical Docs Packet (Est Tokens) |
|---|---|---|---|
| **Kernel / TCB** | [`docs/backend/architecture/kernel.md`](backend/architecture/kernel.md) | [`docs/SPEC.md`](SPEC.md), [`backend/reference/ports.md`](backend/reference/ports.md) | ~3,500 – 5,500 tokens |
| **Runtime Service** | [`docs/backend/architecture/runtime-execution.md`](backend/architecture/runtime-execution.md) | [`backend/reference/runtime-service.md`](backend/reference/runtime-service.md), `symbols.jsonl` | ~3,800 – 6,000 tokens |
| **Events & Ledgers** | [`docs/backend/architecture/causal-state.md`](backend/architecture/causal-state.md) | [`docs/backend/reference/events.md`](backend/reference/events.md), [`backend/reference/schemas.md`](backend/reference/schemas.md) | ~3,500 – 5,200 tokens |
| **Agency & Turns** | [`docs/backend/architecture/agency.md`](backend/architecture/agency.md) | [`backend/architecture/workflows/agent-lifecycle.md`](backend/architecture/workflows/agent-lifecycle.md) | ~3,000 – 5,000 tokens |
| **Delegation / Topology**| [`docs/backend/architecture/delegation-topology.md`](backend/architecture/delegation-topology.md) | [`backend/architecture/workflows/delegation.md`](backend/architecture/workflows/delegation.md) | ~2,500 – 4,500 tokens |
| **Artifacts & Evidence** | [`docs/backend/architecture/assurance-evaluation.md`](backend/architecture/assurance-evaluation.md) | [`backend/reference/artifacts-memory.md`](backend/reference/artifacts-memory.md) | ~3,200 – 5,500 tokens |
| **CLI / TUI / Client** | [`docs/product/frontend/PRD_AETHER_CLI.md`](product/frontend/PRD_AETHER_CLI.md) | [`docs/product/frontend/PRD_AETHER_TUI.md`](product/frontend/PRD_AETHER_TUI.md) | ~4,000 – 6,500 tokens |
| **Frontend Platform** | [`docs/product/frontend/PRD_FRONTEND_PLATFORM.md`](product/frontend/PRD_FRONTEND_PLATFORM.md) | [`docs/product/frontend/PRD_AETHER_DESKTOP.md`](product/frontend/PRD_AETHER_DESKTOP.md) | ~6,000 – 9,000 tokens |
| **Execution tasks**| [`docs/execution/tasks.md`](execution/tasks.md) | [`docs/execution/spec.md`](execution/spec.md), [`docs/execution/technical.md`](execution/technical.md) | ~2,000 – 8,000 tokens |

---

## 4. Machine Knowledge Layer Integration

The repository automatically maintains a deterministic, machine-readable knowledge layer in `.generated/knowledge/` (`just docs-knowledge`). **The authoritative counts are always `.generated/knowledge/report.json`** (`total_documents`, `links_count`, `symbol_index_count`) — never hardcode them here:

- **`catalog.jsonl`**: Complete catalog of all living documentation files, including titles, authority tiers, status, file size, line counts, and estimated tokens.
- **`ownership.jsonl`**: Canonical ownership mappings from subsystem IDs to document paths.
- **`links.jsonl`**: Verified markdown link relationship graph.
- **`code-map.jsonl`**: Mappings from production packages (`vanguard/packages/`) to canonical documentation owners.
- **`symbols.jsonl`**: AST-derived index of all public production classes/protocols (plus curated key symbols), each linked to its canonical doc owner. Regenerated by `tools/generate_knowledge_base.py`.

To perform local deterministic context retrieval for an AI agent without loading full files:
```bash
# Authority-ranked routing for a task, packed inside a token budget
python3 tools/docs_rag_v0.py "YOUR SEARCH QUERY" --budget 8000

# Reverse routing: code path -> canonical owner doc + symbols defined there
python3 tools/docs_rag_v0.py --file vanguard/packages/kernel/budget.py
```

The LDA dashboard (`uv run lda serve`, `127.0.0.1:8765`) visualizes the same knowledge base for humans. Its agent-facing `lda query` / `lda context` commands are **experimental** until `uv run lda doctor --json` reports `"index_healthy": true` (`just lda-index` populates the index); `docs_rag_v0.py` is the canonical agent retrieval surface.

LDA is project-agnostic and profile-driven: this repository selects its AETHER profile (authority vocabulary, non-canonical tiers, workspace exclusions) explicitly via the root `lda.yaml` — never by artifact side-channel. Its architectural invariants, enforced by `test/tools/test_lda_portability.py`, are: (1) **Single Emitter** — LDA never writes `.generated/knowledge/`; (2) **Git-HEAD binding** — context packets record `provenance.source_head_sha` and must be recompiled (or refused) on workspace HEAD mismatch; (3) **Bounded growth** — global symbol rankings are capped at Top-K (`max_global_symbols`, default 500).

---

## 5. Worked Example: Developing a Feature With the Knowledge Base

Task: *"Add a new typed budget class for sandbox wall-clock limits."*

| Step | Command / Artifact | Question Answered | Tokens |
|---|---|---|---|
| 0. Bootstrap | `cat dev_context_logs/context_summary.md` | TCB ≤1438 (currently 1384 → **54 LOC headroom** constrains where the code may live); which suites must stay green; what is already failing | ~800 |
| 1. Route | `python3 tools/docs_rag_v0.py "typed budget wall clock limit" --budget 6000` | Subsystem = Kernel Core; canonical owner = `docs/backend/architecture/kernel.md`; secondary = `docs/backend/reference/ports.md` | ~800 |
| 2. Reverse route | `python3 tools/docs_rag_v0.py --file vanguard/packages/kernel/budget.py` | Documentation debt: `kernel.md` must be updated; existing symbols in the target file | ~200 |
| 3. Pin symbols | `grep "Budget" .generated/knowledge/symbols.jsonl` | Existing algebra to extend (`BudgetDenied`, attenuation classes) and where they live | ~200 |
| 4. Read owners | `docs/backend/architecture/kernel.md` + `docs/SPEC.md` budget clauses | The contract/invariants the change must respect | ~2,500–5,000 |
| 5. Validate | `python3 -m unittest discover -s test/kernel -t .` + `just check` | Executable falsifiers for the change | — |

Total targeted reading: **~5–8K tokens** instead of the 50–150K+ a full-corpus scan costs — and the map told us our documentation obligations *before* the first commit, which is what keeps this knowledge base truthful.
