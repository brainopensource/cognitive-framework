# Backlog — Epic map (M0–M6)

**Rewritten** at the v0.5.0 Foundation Lock, replacing the TSK-* wave-structured backlog. Source:
`docs/TECH_LEAD_REVIEW/02_ROADMAP_BACKLOG_AND_REVIEW_TRIAGE.md` §4. Field schema (owner, status,
`superseded_by:` pointer) is kept from the legacy backlog; waves are replaced by M-epics.

**Governing decision** (roadmap triage §1): the old `sprint_active.md` v0.6.0 board's "close remaining
G-050 rows on the v0.4.x codebase before extraction" sequencing is **inverted and the per-row patches
cancelled**. M1 rebuilds the emission layer wholesale under E-COV=100% and `replay-parity` — patching
`EVENT_KINDS` enforcement, heartbeats, and grant/budget kinds into the old writer and then porting it is
double implementation. `replay-parity` is a strictly stronger gate than the union of the open rows.
**Exception:** work already landed (verified in `docs/SPEC.md` §8.2, not just claimed) closes in place
and ports with the kernel.

| Epic | Absorbs (legacy TSK) | Status |
|---|---|---|
| **EPIC-M0-DOCS** — spec collapse per matrix | `TSK-DOC-001` (done, extended to vision.md), `TSK-DOC-002` (done), `TSK-SPEC-001…011` (spec-amendment rows become ADR-M0-* entries or SPEC text — no separate patches to an archived corpus) | **closed** — `docs/SPEC.md` landed this wave |
| **EPIC-M0-PURGE** — history rewrite: secrets + artifacts + frontend trees | `SEC-01`; `TSK-DOC-003` (`cryptography` in TCB list → ADR) | open — staged in `docs/03_sprints/plans/m0-code-and-purge.md`, **not started** |
| **EPIC-M1-EVENTS** — taxonomy, emitters, E-COV, envelope `branch_id` | `TSK-LED-001…005, 008` (superseded per governing decision above), `TSK-LED-006/007` (keep: WAL store, inbox port verbatim), `TSK-EVAL-001` (evaluation trigger → ledger listener, closes D-02), `M-18` | open |
| **EPIC-M1-KERNEL** — verbatim port + provenance carried + six-dim Reservation + one EffectRequest | `TSK-CORE-001…009` (001–004 done/carried — re-verified `docs/SPEC.md` §8.2 2026-08-18; 005–008 become invariant tests; 009 → metric triple), `TSK-EPIC-060-005` | open |
| **EPIC-M1-CI** — replay-parity, mutation gate, boundaries v2, control-call-site coverage, retargeted rule map | `TSK-TEST-001/002/003` (bijection discipline, `docs/05_adr/ADR-M0-01-control-coverage-discipline.md`) | open |
| **EPIC-M2-REGISTRY** — plugin.yaml schema, resolver, lifecycle FSM, hot-swap | `H-1` | open |
| **EPIC-M2-ISOLATION** — broker: in_process lint, subprocess RPC + rlimits + seccomp | `TSK-SEC-001` (AT-12 or ADR-defer w/ compensating control — decide in M2), `TSK-SEC-002` (seccomp lands here, not deferred), `TSK-SEC-003/004` (probes: keep) | open |
| **EPIC-M2-SPI** — five protocols (`docs/05_adr/ADR-M0-03-five-spis.md`) + `IModelProvider`/`ISandbox`/stores; codegen; 4-protocol wire normalization; walking skeleton (`docs/05_adr/ADR-M0-13-walking-skeleton.md`); `mhf.model.local-adapter` | `002_doing_advanced-plugin.md` (archived, `docs/archive/v045/reviews/doing/`) | open |
| **EPIC-M3-PACK** — coding re-extraction (`apps/coding/` → `packs/`), ast-patch, repo-map, terminal, single router, ctx-policy wiring, live greenfield gate | `TSK-EPIC-060-001/002/003`, `TSK-EPIC-070-001`, `TSK-HAR-001…006` (001/002/004 done-carried; 003 grant library keeps; 005 spend auth keeps; 006 schema-driven translator → absorbed by typed SPI), `TSK-CTX-003/004` (keep: compiler + FrozenHarness port), `H-2`, `RT-01`, S28–S34 salvage | open |
| **EPIC-M4-PARITY** — five packs, TableWorld | `TSK-HAR-007`, `TSK-EPIC-060-004` | open |
| **EPIC-P2/P3** (named, not planned) — meta-reflector, genome+lab, folding, streaming, LSP, playbook-advisory, memory graph, market allocator | `TSK-EPIC-060-006`, `070-002`, `C-3`, `REC-01` (policy half), deferred rows from review triage | deferred |
| **HONOUR TABLE** (standing refusals) | `TSK-CORE-010` (measurement stays outside `vanguard/packages/`), `TSK-CORE-011` (no `MetaLoopEngine`) + `docs/SPEC.md` §9 items | permanent |
| **KILLED** | `TSK-FE-*` (all 14) — frontend backend-gate work, per scope mandate | closed-kill |

Every accepted legacy row is closed with `superseded_by: <new-epic-id>` in this commit — the audit trail
survives even though the old board doesn't.

## Review triage (from `docs/archive/v045/reviews/`)

Full disposition — 14 ACCEPTED (Phase 1), 9 DEFERRED (each with a named plugin target in
`docs/TECH_LEAD_REVIEW/02_ROADMAP_BACKLOG_AND_REVIEW_TRIAGE.md` §2), 4 REJECTED/KILLED, 3 CLOSED-carried
— is preserved verbatim in `docs/TECH_LEAD_REVIEW/02_ROADMAP_BACKLOG_AND_REVIEW_TRIAGE.md` §2 (that
document is stamped `SUPERSEDED-BY-SPEC` but kept as the review packet that produced this backlog).
Every DEFERRED entry lands in `docs/05_adr/DEFERRED_REJECTED.md` with a reversal condition.

`docs/archive/v045/reviews/todo/deepseek_v050_review_and_v060_plan.md` carries mismatched terminology
(different ALFA/BETA lane phrasing, "ArtifactNode/Edge Merkle-DAG", "Semantic Vector Index" not used
elsewhere in this corpus) — low-confidence source, disposition **REJECTED/CLOSED**: nothing in it names
a concrete change not already covered by an epic above.

## Standing rule

An item enters v0.5.0 (M0–M4) only if it lands in Layer 0, the plugin runtime, or the Phase-1 Coding
Pack. Everything else is Phase-2/3 (named target above) or permanently refused (honour table).
