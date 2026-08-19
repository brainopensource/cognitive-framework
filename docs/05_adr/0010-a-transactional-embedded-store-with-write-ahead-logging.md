---
adr: 0010
title: "A transactional embedded store with write-ahead logging; line-delimited JSON is export only"
status: accepted
source_section: "3. Adjudications between the two lineages"
migrated_from: docs/01_specs/backend/09_vanguard_decision_register_v040.md
---

# ADR-0010: A transactional embedded store with write-ahead logging; line-delimited JSON is export only

**Reasoning.** Append-only files fail on atomic multi-record commit, torn writes, concurrent reads and indices — four problems solved at near-zero cost

**Reversal condition.** Storage volume exceeds what an embedded store handles, at which point the export format is unchanged

**Owner · status.** Tech Lead · accepted
