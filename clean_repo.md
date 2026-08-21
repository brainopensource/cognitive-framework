# Repository Cleanup and Simplification Brief

**Purpose:** make AETHER easy to navigate and develop without deleting architectural law,
forensic evidence, or migration history.

**Rule:** deletion follows migration and a green falsifier. A file that still contains the only
copy of a requirement, decision, test obligation, or evidence pointer is not stale.

> **Mandatory operator-confirmation gate for humans and AI agents:** this document is a cleanup
> proposal, not standing permission to delete. Before removing or permanently relocating any ADR,
> annex, specification, sprint record, review, evidence artifact, or other governance document,
> the executor MUST inventory the exact paths, prove that unique content and incoming references
> have been migrated, identify the recovery commit, and ask the operator who issued the current
> message/prompt for explicit approval of those exact targets. Silence, a general request to
> "clean the repository," or this document alone is not approval. Without confirmation, the
> executor may report candidates and prepare a non-destructive plan, but must not delete or move
> them.

## Target repository shape

```text
README.md                         navigation and verified as-built map
AGENTS.md                         contributor/agent operating rules
docs/SPEC.md + docs/04_annex/     normative law
docs/05_adr/                      append-only decisions and INDEX
docs/03_sprints/sprint_active.md  one active execution board
docs/02_roadmap/milestones.md     outcome-level M-0 through M-10 ladder
docs/06_references/               retained research; advisory only
docs/07_reviews/archive/          non-authoritative proposals and review provenance
vanguard/packages/                canonical production code
packs/                            domain capabilities
test/ + tools/                    executable requirements and enforcement
```

## 1. Safe cleanup now

| Target | Action | Preconditions / reason |
|---|---|---|
| `DELETE.md` | **Deleted in the approved cleanup batch.** | It was an empty stale artifact, not law or evidence. |
| `docs/03_sprints/done/wave2B_review.md` | **Archived in the approved cleanup batch.** | Wave 2B is complete. |
| Proposal reports `002`, `004`, `005`, `006`, `007`, `008` | **Archived under `docs/07_reviews/archive/proposals/`; only moved-link targets were rebased.** | ADRs 0077–0085 contain the accepted decisions; the reports retain non-authoritative provenance. |
| `001_alfa_review_full_decision.md` | **Archived beside the proposals.** | It is ratification provenance, not implementation authority. |
| `CLAUDE.md` | Reduce to a short pointer to `AGENTS.md`, or remove if no supported tool requires it. | Two independent contributor rulebooks drift. `AGENTS.md` is canonical. |
| Broken Markdown links | Repair in living documents and make the widened link checker mandatory. | Current repo-wide failures are concentrated in `SYSTEM_OVERVIEW.md`, two research documents, and the CLI README. Do not hide them with exclusions. |

Do not delete `docs/06_references/`. Add a directory banner stating that research is retained,
non-normative input and cannot be cited by implementation tickets.

## 2. Cleanup at the M-2 exit

| Target | Action | Gate |
|---|---|---|
| `wave2C_todo.md` | Move to `docs/03_sprints/done/` or the review archive, then remove the root copy. | RF-23 and RF-25 green; every durable requirement migrated to SPEC, accepted ADRs, the `002` register, and `sprint_active.md`. |
| Completed M-2 board detail | Compress to results, evidence digests, and links; move task narration to the completed plan. | Tech Lead signs the M-2 re-gate. |
| Duplicate trajectory/falsifier prose | Keep the normative statement in SPEC/ADR and the executable statement in the test; remove repeated implementation essays from the live board. | Named tests and links exist. |

## 3. Atomic cleanup at M-3

| Target | Action | Mandatory gate |
|---|---|---|
| `layer0/` | Delete the complete temporary fork. | Runtime registry/compose replacement green; NOVA-4 negative suite green. |
| `test/layer0/` | Delete or migrate each test to its packages-path owner. | No unique invariant is lost. |
| `pyproject.toml` `layer0*` packaging entry | Remove in the same change as `layer0/`. | Package/build checks prove no Layer-0 artifact ships. |
| Layer-0 CI jobs, imports, path helpers, docs links | Remove atomically. | Boundary, duplication, stale-path, packaging, and full relevant suites green. |
| Hard-coded component consumer tables | Delete only after the Named Component Graph compiler replaces them. | RF-28–RF-45 and graph compatibility fixtures green. |

Never partially delete Layer-0. Source, packaging, tests, CI, and living navigation move together.

## 4. Documentation collapse after M-4, executed at M-5

Keep the Clean Triad and archive the rest:

| Current document group | Final disposition |
|---|---|
| `README.md` | Keep as the sole navigation/as-built entry point; update verified counts automatically where possible. |
| `docs/00_overview/SYSTEM_OVERVIEW.md` | Merge unique verified content into `README.md`, then archive or delete it. It currently duplicates navigation and carries many broken/root-relative links. |
| `docs/01_executive/vision.md` | Keep only stable product intent; remove architectural requirements already governed by SPEC/ADRs. |
| `docs/02_roadmap/backlog.md` | Delete if it remains only a pointer; otherwise convert it to a pointer to `sprint_active.md`. Never maintain a second backlog. |
| `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/001`, `003`–`006`, and `VANGUARD_V060_FORENSIC_DISCOVERY.md` | Archive as immutable provenance after all live citations point through ADRs or evidence bundles. |
| `002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md` | Keep through the Foundation Stop; collapse its surviving RF registry into the canonical law/tooling at M-5, then archive it. |
| `DEFERRED_REJECTED.md` and `DRIFT_REGISTER_v045.md` | Archive after unresolved items have an ADR disposition and no active ticket cites them. |
| `docs/08_diagrams/` | Keep only diagrams that match current law and are linked from living navigation; regenerate or remove stale architectural pictures. |

## 5. Protected files—never delete as ordinary cleanup

- `docs/SPEC.md` and `docs/04_annex/`;
- active accepted ADR files and `docs/05_adr/INDEX.md`; fully superseded historical ADR bodies may
  be proposed for removal from the working tree only after their disposition and recovery commit
  are preserved in a compact lineage index and the operator explicitly approves the exact paths;
- signed evidence bundles, canonical schemas, JCS vectors, and migration fixtures;
- completed sprint evidence while referenced by an active gate or ADR;
- tests that uniquely enforce a security, identity, accounting, or compatibility invariant;
- `docs/06_references/`, per Director instruction;
- `AGENTS.md`, unless deliberately replaced by an equivalent canonical contributor contract.

Git history is recovery, not an excuse to erase un-migrated law. Record material removals in the
cleanup commit and preserve the last commit containing the removed corpus.

## 6. Structural simplifications for SOTA development hygiene

1. **One command location.** Documentation must use the real `tools/linters/...` paths, preferably
   exposed through stable `make`, `just`, or package scripts so paths cannot drift again.
2. **One status source.** Only `sprint_active.md` reports active work. Completed plans are immutable
   evidence; proposals and research never carry status.
3. **One requirement identity.** Every ticket cites one accepted ADR/SPEC requirement and one
   named falsifier. RF-72 must lint duplicate/conflicting RF allocations.
4. **Generated inventories.** Generate test counts, TCB LOC, event counts, package lists, and schema
   indexes during CI rather than copying volatile numbers into several documents.
5. **Archive banners.** Every archived proposal/review begins with `NON-NORMATIVE / SUPERSEDED` and
   links to the ADR index; no RFC-2119 language is interpreted from an archive.
6. **No empty placeholder surface.** Keep a reserved package only when a stable boundary requires
   it; otherwise create it when its first gated implementation lands.
7. **Dependency and artifact hygiene.** Remove unused dependencies, generated build output,
   cassettes without provenance, model dumps, local databases, caches, coverage output, and secrets
   from version control; enforce this through `.gitignore`, packaging checks, and secret scanning.
8. **Automatic stale-path enforcement.** Link, package, import, schema-reference, ADR-index, and
   board-plan checks must run in CI before deletions merge.

## 7. Cleanup execution protocol

For each cleanup batch:

1. Inventory incoming links, imports, packaging entries, CI jobs, and unique requirements.
2. Migrate the unique content to its canonical owner.
3. Add or identify the falsifier proving no contract is lost.
4. Move/archive before permanent deletion when provenance has value.
5. Rewrite references atomically—never leave compatibility paths by accident.
6. Run boundary, TCB, stale-path, Markdown-link, packaging, secret, and affected test suites.
7. Present the exact removal/move list, migration evidence, and recovery commit to the operator.
8. Wait for an explicit approving message or prompt naming that scope; do not infer approval.
9. After approval, perform only the confirmed operations and record the authorizing message and
   verification results in the cleanup change.

## Recommended order

```text
now:     cleanup batch complete -> repair remaining living-document links
M-2:     archive wave2C_todo -> compress completed board detail
M-3:     atomically delete layer0 source/tests/package/CI/docs surface
M-5:     collapse living governance to README + Clean Triad; archive old reviews/registers
ongoing: generated inventories + strict link/RF/stale-path/package checks
```

This plan recommends cleanup but performs no deletion. Destructive changes require a dedicated,
reviewable cleanup change with the relevant milestone gate green.
