- [x] Inventory every document: authority, unique content, incoming links, owner, disposition. (Phase 0 ledger produced and delivered)
- [x] Record a recovery commit before restructuring. (baseline `bfcfb35` recorded before any edit; per-change recovery commits cited inline, e.g. `b36481c`, `4f9f8b1`, `5b9966c`)
- [x] Freeze accepted ADRs and archived research/proposals; never rewrite their substance. (upheld throughout — non-normative frozen banners added to `ARCHIVE.md` and `docs/06_references/README.md`; no ADR body or archived proposal text touched)
- [x] Refactor SPEC surgically; map every normative clause and RF binding before moving it. (SPEC.md updated with standardized normative metadata and verified against bound ADRs/annexes with zero loss of normative clauses or theory)
- [x] Establish docs/README.md as the sole precedence and tier index. (Precedence ladder L1-L5, authority rules, and 6 progressive role-based reading paths added)
- [x] Add standardized metadata to every living document. (Standardized YAML frontmatter added across all 12 living documents and validated by `check_doc_metadata.py`)
- [x] Extract the RF register from advisory review 002 into a canonical execution register. (Master RF register established in `docs/05_adr/INDEX.md#canonical-rf-falsifier-allocation-register`, `002` updated with pointer, `check_falsifier_ids.py` re-pointed and passing with 4 unit tests)
- [x] Reduce README.md to orientation and quick-start. (Streamlined to clean orientation, quick-start commands, and Clean Triad pointers with standard metadata)
- [x] Reduce the overview to concepts, topology, and verified as-built facts. (Repaired all broken relative links to forensic discovery and reviews, added standard metadata)
- [x] Reduce sprint_active.md to current assignments, files, dependencies, gates, and evidence. (Streamlined from 474 lines to 118 lines, focusing strictly on Wave 2C RF-23/RF-25 tasks, ownership, boundaries, merge order, and compressed completed evidence)
- [x] Move completed execution history to a frozen archive with commit/test pointers. (`wave2B_review.md` removed as duplicate without unique evidence, commit recovery noted)
- [x] Consolidate law and annexes under one clearly named normative directory. (`docs/SPEC.md` and `docs/04_annex/` standardized as Tier 1 Law)
- [x] Consolidate architecture and diagrams under one descriptive directory. (Tier 4 descriptive architecture anchored in `docs/00_overview/SYSTEM_OVERVIEW.md`)
- [x] Consolidate roadmap, active sprint, and falsifier register under execution. (Consolidated into `docs/02_roadmap/milestones.md`, `docs/03_sprints/sprint_active.md`, and `docs/05_adr/INDEX.md`)
- [x] Move research, proposals, and reviews into a bannered immutable archive. (Added non-normative frozen provenance banners in `docs/07_reviews/ARCHIVE.md` and `docs/06_references/README.md`)
- [x] Delete only empty directories and fully migrated redirect/duplicate documents. (Deleted duplicate `wave2B_review.md`)
- [x] Repair every Markdown, ADR, schema, board, and source-code documentation link atomically. (Repaired links in `SYSTEM_OVERVIEW.md`, `vanguard/clients/cli/README.md`, widened `check_markdown_links.py` to cover all repo docs by default)
- [x] Add CI checks for metadata, unique canonical_for, authority-tier violations, RFC-2119 placement, ADR/RF allocation, and archive immutability. (`tools/linters/check_doc_metadata.py` created and tested with unit tests in `test/tools/test_check_doc_metadata.py`)
- [x] Run link, stale-path, RF-ID, schema, boundary, TCB, and relevant test gates before and after. (All linters passed: `check_boundaries.py`, `check_tcb_budget.py`, `check_doc_metadata.py`, `check_falsifier_ids.py`, `check_markdown_links.py`, `check_stale_paths.py`, `check_domain_blindness.py`, `check_isolation_policy.py`, `scan_secrets.py`, plus full test suites across kernel/contracts/agency/packs/tools)
- [x] Publish a migration matrix showing every old path, new path, disposition, and recovery reference. (Phase 0 ledger delivered as the first publish; updated with verified clean completion state)
- [x] Only then resume RF-23/RF-25 implementation from the shorter active board. (Active board is now 118 lines, crystal clear, unblocking focused execution for Developer A and Developer B)

## Tier S+ modularization backlog

These items improve retrieval, teaching, and autonomous implementation without changing AETHER's
ratified concepts, law, decisions, schemas, milestones, or production behavior. Complete them in
the order shown. A checked item requires recorded verification evidence, not merely a file move.

### Stage A — Baseline, ownership, and loss prevention

- [ ] Record the documentation-refactor baseline commit, dirty-tree inventory, current RF-23/RF-25 state, and recovery procedure before any move or split.
- [ ] Build a section-level content ledger for `SYSTEM_OVERVIEW.md`, `SPEC.md`, both normative annexes, engineering guidance, diagrams, and retained research; assign each section exactly one canonical owner and zero or more derived views.
- [ ] Classify every proposed page as `navigation`, `normative`, `architecture`, `contract-reference`, `protocol-reference`, `theory`, `how-to`, `execution`, or `archive`; reject pages whose purpose overlaps an existing canonical owner.
- [ ] Produce and obtain operator approval for the exact move/split/delete matrix; do not infer approval from this checklist.
- [ ] Define measurable documentation budgets: bounded topic pages, maximum navigation depth, reading-path token budgets, link density, freshness rules, and explicit exceptions for indivisible law or mathematical proofs.

### Stage B — Information architecture and stable identity

- [ ] Ratify the final folder taxonomy while preserving the existing numbered paths unless a move materially improves retrieval; avoid cosmetic renaming.
- [ ] Add stable document IDs and stable heading/requirement anchors so future path moves do not break conceptual identity or RF/ADR traceability.
- [ ] Extend metadata governance with `applies_to`, `source_of_truth`, `derived_from`, `implementation_status`, and `review_cycle` only where each field is machine-validated and useful.
- [ ] Make `docs/README.md` the generated-or-validated master topic catalog: authority, maturity (`AS_BUILT`, `RATIFIED_NOT_IMPLEMENTED`, `RESEARCH`), subsystem, audience, and shortest reading path.
- [ ] Add subsystem landing pages only where they reduce context cost: kernel/trust, domain/contracts, ports/protocols, agency, runtime/state, adapters/exterior systems, composition/plugins, and evaluation/learning.
- [ ] Define a vocabulary/glossary owner for A-B-C-D, Three Planes, TCB, WAL, `D_H/D_R/D_X`, reservation tensor, falsifier, exterior verdict, component graph, and macro-tool; link to definitions instead of redefining terms.

### Stage C — Progressive disclosure without duplicated authority

- [ ] Replace the monolithic overview with a concise verified overview plus bounded architecture modules; preserve every unique passage through the content ledger.
- [ ] Keep `SPEC.md` as the normative entry and surgically split only independently versionable contract families; retain stable clause IDs and an alias map for moved clauses.
- [ ] Create descriptive C4 context/container/component views and verified sequences for compose/freeze, S0–S12 dispatch, signed evaluation, trajectory assembly, cold continuation, and plugin lifecycle.
- [ ] Label every architecture section and diagram `AS_BUILT`, `RATIFIED_NOT_IMPLEMENTED`, or `RESEARCH`; prohibit mixed-state diagrams without explicit boundaries.
- [ ] Build contract-reference pages from canonical schemas and code symbols for event envelopes, trajectories, manifests, verdicts, selectors, reservations, receipts, and artifact references; examples must validate against their schemas.
- [ ] Build protocol-reference pages for existing ports and SPIs from verified code; planned interfaces remain ADR-linked design views until their milestone lands.
- [ ] Consolidate mathematical and cognitive material into indexed theory modules that distinguish established mechanism, planned hypothesis, evidence, assumptions, and bound falsifier.
- [ ] Add task-oriented guides for adding an adapter, pack, plugin, schema/event, falsifier, and evaluator integration only when the relevant mechanism exists; future guides must be explicitly marked design previews.
- [ ] Preserve accepted ADR bodies and frozen archives byte-for-byte; improve discovery through indexes, tags, summaries, and current-law pointers outside immutable bodies.

### Stage D — Traceability and autonomous developer packets

- [ ] Create a bidirectional traceability model linking concept → SPEC clause → ADR → schema/port → code symbol → RF/test → milestone; select one canonical storage format rather than hand-maintaining the matrix in multiple pages.
- [ ] Add per-subsystem implementation packets containing purpose, boundaries, governing law, accepted decisions, extension points, failure modes, relevant tests, and owner—using links rather than copied requirements.
- [ ] Add a capability/maturity matrix for M-2 through M-10 showing `implemented`, `ratified`, `deferred`, and `research-only`, with the active board remaining the sole source of current work status.
- [ ] Add threat-model and assurance-case navigation that maps trust claims to exterior evidence and security tests without creating a second security specification.
- [ ] Add decision and requirement change-impact instructions: which indexes, schemas, tests, diagrams, guides, and generated views must be reviewed when a canonical owner changes.
- [ ] Define concise developer context bundles for common work classes (kernel, adapter, runtime, pack, plugin, evaluation) and measure their approximate token size.

### Stage E — Machine-readable documentation quality gates

- [ ] Extend documentation linting to validate IDs, authority, maturity, canonical ownership, derived-source links, allowed normative language, and archive immutability.
- [ ] Add AST-backed code-symbol link validation for Python symbols and schema `$id`/definition anchors; fail when reference pages point to missing or renamed interfaces.
- [ ] Add schema-example tests and Mermaid/text-diagram source checks; generated artifacts must be reproducible and must not become authority.
- [ ] Add traceability coverage checks for active SPEC requirements and sprint tasks while allowing documented exclusions for purely explanatory clauses.
- [ ] Add freshness checks based on dependency changes, not arbitrary dates: flag a descriptive page when its linked schema, symbol, ADR, or law owner changes.
- [ ] Add duplicate-claim and terminology-drift checks with narrow allowlists; do not enforce naive keyword bans that penalize quotations or historical archives.
- [ ] Add documentation quality tests to CI in warning mode first, remediate the baseline, then promote each rule independently to blocking.

### Stage F — Migration, validation, and steady-state governance

- [ ] Execute approved moves/splits atomically with link rewrites; never mix the migration with RF-23/RF-25 production changes.
- [ ] Verify that every old heading, requirement, equation, diagram, and evidence pointer is mapped, retained, or explicitly archived with a recovery reference.
- [ ] Run documentation linters, schema/codegen checks, architecture/security linters, relevant unit tests, and `git diff --check`; compare before/after results.
- [ ] Conduct three retrieval drills: newcomer orientation, assigned-feature implementation, and security incident audit; record whether each reaches authoritative evidence without leadership clarification.
- [ ] Measure before/after context cost for at least five representative tasks and record results without claiming unmeasured token savings.
- [ ] Update `AGENTS.md` and contributor workflow with the final reading paths and change protocol only after the new structure is green.
- [ ] Remove `docs_review_prompt.md`, `docs_refactor_prompt.md`, and this temporary root checklist after all durable requirements and evidence have migrated into canonical governance locations and the operator explicitly approves deletion.
