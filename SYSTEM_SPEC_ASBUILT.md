# Vanguard / GTS — System Specification As-Built

Forensic map of the **production Python backend** at `vanguard/packages/` (`domain/`, `ports/`, `kernel/`,
`agency/`, `runtime/`, `adapters/`) as it exists on branch `feat/harness-cli-v045` at HEAD `6f2f8b2` (three docs-tidy commits after
`d2aef8e feat(S-special): Version 0.4.5`; `vanguard/packages/` is unchanged from that version tag).
Corroborating evidence: root `README.md`, `test/`,
`tools/check_boundaries.py`, `tools/check_tcb_budget.py`, `tools/rule_test_map.py`, `test/broken/manifest.json`,
`docs/scrum/roadmap_backend.md`.

**Out of scope by instruction:** `vanguard/clients/cli/` (TypeScript/Ink), `vanguard-gui/`, all TUI/CLI
presentation code. `lab/`, `tools/telemetry/` and `benchmarkings/` are outside `vanguard/packages/` but are
reported where the theory document names them explicitly (notably §6).

Section numbering and headings mirror `SYSTEM_SPEC_THEORY.md` exactly so the two can be diffed
section-by-section. This document records **what the code does**, not whether that is correct.

## Table of Contents

0. [Document Registry, Precedence & Identifier Namespaces (VG-00)](#0-document-registry-precedence--identifier-namespaces-vg-00)
1. [System Identity, Claims & Non-Claims (VG-02)](#1-system-identity-claims--non-claims-vg-02)
2. [Turn Lifecycle, Planes & Execution Model (VG-03)](#2-turn-lifecycle-planes--execution-model-vg-03)
3. [Core Contracts & Wire Schema (VG-04)](#3-core-contracts--wire-schema-vg-04)
4. [Policy Kernel, Capability Attenuation & Security Model (VG-05)](#4-policy-kernel-capability-attenuation--security-model-vg-05)
5. [Competence, Memory & Evidence Model (VG-06)](#5-competence-memory--evidence-model-vg-06)
6. [Loop Engineering, Measurement & Self-Improvement (VG-07)](#6-loop-engineering-measurement--self-improvement-vg-07)
7. [Architectural Decision Record Summary (VG-09)](#7-architectural-decision-record-summary-vg-09)
8. [Deferred & Rejected Design Space (VG-10)](#8-deferred--rejected-design-space-vg-10)
9. [Build Plan, Programme Spine & Roadmap Milestones (VG-08, GTS-13C)](#9-build-plan-programme-spine--roadmap-milestones-vg-08-gts-13c)
10. [Engineering Handbook Principles (VG-01)](#10-engineering-handbook-principles-vg-01)
11. [Convergence Evidence & Vision Annex (VG-11, VG-12)](#11-convergence-evidence--vision-annex-vg-11-vg-12)
12. [Appendix — Internal Contradictions & Ambiguities in the Corpus](#12-appendix--internal-contradictions--ambiguities-in-the-corpus)

**Measured baselines used throughout:**

| Measurement | Value | Source |
|---|---|---|
| Python source files under `vanguard/packages/` | 125 | `find vanguard/packages -name '*.py'` |
| Physical LOC by package | `domain` 3,622 · `ports` 738 · `kernel` 1,684 · `agency` 2,157 · `runtime` 7,761 · `adapters` 6,211 | `wc -l` |
| Boundary lint | **PASS**, 244 source files checked | `python3 tools/check_boundaries.py` |
| Kernel TCB budget | **PASS**, 1,333 logical LOC / 1,438 alarm (baseline 1,307 + 131) | `python3 tools/check_tcb_budget.py` |
| Full unittest suite | **1,007 tests · 2 failures · 2 errors · 3 skipped** in 30.8 s | `python3 -m unittest discover -s test -t .` |
| Must-fail harness | **38 broken counterparts observed failing** (PASS) | `python3 tools/run_broken_tests.py` |
| Rule-to-test map | `rules=203 tested=28 untestable=42 gaps=133` | `python3 tools/rule_test_map.py` |
| Active MVP Contract | `closure-in-progress`; baseline assignment 100 % (16/16); merged-scope evidence 100 % (14/14) | `python3 tools/run_active_contract_tests.py` |

---

## 0. Document Registry, Precedence & Identifier Namespaces (VG-00)

### 0.1 Precedence rules (`PR-1` … `PR-5`)

No code artefact implements or enforces `PR-1`…`PR-5`. These are document-governance rules with no runtime
counterpart, and none is expected in `vanguard/packages/`.

The closest mechanised counterparts live in `tools/`, not in the backend:
`tools/audit_v4.py`, `tools/check_markdown_links.py`, `tools/check_stale_paths.py`,
`tools/check_sprint0_governance.py`. `tools/check_stale_paths.py` has a must-fail counterpart
(`MF-GOV-PATH-001` in `test/broken/manifest.json`, fixture `test/broken/fixtures/stale_paths/`).

**Observed drift:** the root `README.md` is itself stale against the tree it documents — it cites
`vanguard/packages/runtime/coordination.py`, `vanguard/packages/adapters/stores/sqlite_event.py` and
`vanguard/packages/adapters/stores/fs_blob.py`, none of which exist. The real files are
`adapters/stores/event_store.py` (`SqliteEventStore` at line 121) and `adapters/stores/blob_store.py`.
`README.md:58` also names `runtime/coordination.py` as a live component; `runtime/session_log.py:1-8`
records that `runtime/coordination.py` was **deleted** in `S7-A-05`.

### 0.2 The document set and status classes

Not a code concern. `docs/main_v4/` exists and contains the VG-00…VG-12 + GTS-13C corpus; `README.md:395-417`
carries an "Alignment Matrix" asserting **"Fully Aligned"** for `00`, `01`, `02`, `03`, `05`, `09` and `13C`
(VG-04, VG-06, VG-07, VG-08, VG-10, VG-11, VG-12 rows are absent from that table).

### 0.3 Word budget ledger

`tools/wordcount_v4.sh` **is present** and is the spec's `CI-5` counter (shebang + "authoritative v4 word
count" header). CI invokes it (`.github/workflows/ci.yml`). `tools/` holds 25 top-level `*.py` files
(including `__init__.py` and `repo_paths.py`) plus this shell script and subdirectories. No backend module
in `vanguard/packages/` references word budgets — enforcement is a docs/CI concern, not a runtime one.

### 0.4 Identifier namespaces (global, permanent, never reassigned)

The backend uses spec identifiers as **docstring/comment anchors only** — there is no identifier registry
type, no enum, and no validation of ID well-formedness anywhere in `vanguard/packages/`.

Identifier families actually appearing in `vanguard/packages/**/*.py`:

| Family | Present in code? | Evidence |
|---|---|---|
| `K-nn` | Yes, as comments/docstrings: `K-04`…`K-08`, `K-13`…`K-21`, `K-23`…`K-33`, `K-42`, `K-44`, `K-46`…`K-49` | `grep -roh 'K-[0-9]\{2\}' vanguard/packages` |
| `F-nn` | Yes, and **as a live enum**: `FailurePath` in `vanguard/packages/kernel/model.py:121-154` carries `F-01`…`F-25` **plus `F-21a`** as its string values | `kernel/model.py:121-154` |
| `CT-nn` | Comments only (`CT-03`, `CT-06`…`CT-09`, `CT-16`, `CT-33`, `CT-40`…`CT-43`, `CT-51`, `CT-52`, `CT-53`) | scattered |
| `ADR-nnnn` | Comments only: `ADR-0039`, `0047`, `0048`, `0054`, `0057`, `0058`, `0060`, `0062`, `0067` | `grep -rn 'ADR-00'` |
| `AT-nn` | Comments only: `AT-01`, `AT-09` | `kernel/dispatch.py:37,98`; `kernel/__init__.py:5` |
| `TK-nn` | **Zero occurrences** in `vanguard/packages/` | — |
| `MF-nn` | `MF-KRN-001`…`011` referenced in kernel docstrings; **`MF-01`…`MF-37` appear nowhere in code or tests** | see §9.6 |
| `REQ-*` | **Emergent, undocumented in theory** as a *code-visible* namespace — 23 distinct IDs (below) | `grep -roh 'REQ-[A-Z]*-[0-9]*'` |

**Emergent, undocumented in theory:** the `REQ-*` requirement namespace is the identifier family the code
actually keys on. Observed IDs: `REQ-APP-001`, `REQ-BENCH-001`, `REQ-CLI-002`, `REQ-CTX-001`, `REQ-DOG-001`,
`REQ-EVAL-001`, `REQ-EXEC-001`, `REQ-EXEC-002`, `REQ-HARN-001`, `REQ-PORT-002`…`REQ-PORT-006`,
`REQ-SCHEMA-001`…`005`, `REQ-SCHEMA-007`, `REQ-SEC-001`, `REQ-SLICE-001`, `REQ-TRUST-001`. The theory doc
mentions the Active MVP Contract's `req_id` shape (§9.25, example `REQ-KRN-014`) but never enumerates these.
Also emergent: sprint-packet IDs used as primary anchors in docstrings — `S6B-MD-00n`, `S7-A-0n`, `S8-A-0n`,
`S8-B-01`, `S8-J-07`, `S9-C-0n`, `S10-A-0n`, `S10-B-0n`, `S10-C-02`, `W11-A`, `W12-A`, `W13-A`, `W14-A`,
`W15-A`, `W16-A`, `DEC-6B-0nn`, `GOV-01`, `SEC-01`.

### 0.5 Rule-family census (VG-00 §6)

`tools/rule_test_map.py` exists and runs. Live output:

```
rules=203 tested=28 untestable=42 gaps=133
```

This reproduces the spec's Phase 0 baseline **exactly** (203 / 28 / 42 / 133). The 28 "tested" rules are:
`CC-6, CC-7, CT-42, CT-44, CT-48, CT-51, CT-52, CT-53, D-3, INV-1, INV-2, K-04, K-06, K-07, K-18, K-19, K-20,
K-22, K-23, K-26, K-32, K-33, K-35, K-36, K-42, K-47, V-05, V-08`.

**Material finding on how the number is produced:** `rule_test_map.py` derives coverage by scanning
`docs/main_v4/` for `MF-nn` mentions next to rule IDs (`rules_guarded()`), **not** by checking that a test with
that ID exists. Every one of the 28 maps to an `MF-01`…`MF-37` identifier, and none of those identifiers
exists in `test/` or `test/broken/manifest.json`. The 28 is therefore a *specification cross-reference count*,
not an implementation coverage count. See §9.6.

### 0.6 CI rules and acceptance verification

`CI-1`…`CI-9` are implemented outside `vanguard/packages/`:

| Spec gate | Implementation | Status |
|---|---|---|
| `CI-1`…`CI-4`, `CI-7` | `tools/audit_v4.py` | present |
| `CI-5` | `tools/wordcount_v4.sh` | **present**; invoked from `.github/workflows/ci.yml` |
| `CI-6` | `.github/workflows/ci.yml` schema job over `schemas/v4/*.schema.json` | present; 38 schema artefacts in `schemas/v4/` |
| `CI-8` | grep in CI | present |
| `CI-9` | `tools/rule_test_map.py` | present; **RED by construction**, exits 0 and reports `gaps=133` (it does not fail the build) |

`CV-1`…`CV-13` are addressed by `tools/cv_checks.py`. Additional gates with no spec `CI-n` number:
`tools/check_active_mvp_contract.py`, `tools/check_backend_artifacts.py`, `tools/check_baseline_manifest.py`,
`tools/check_core_changes.py`, `tools/check_pr_requirements.py`, `tools/check_receipt.py`,
`tools/check_schema_archaeology.py`, `tools/scan_secrets.py`, `tools/run_dogfood_r9.py`.

**Emergent, undocumented in theory:** `tools/check_boundaries.py` closes the package set — any file or
directory directly under `vanguard/packages/` that is not one of `{domain, ports, kernel, agency, runtime,
adapters}` is a hard build failure (`check_boundaries.py:203-224`). The spec's `LT-*` contracts constrain
import direction but never make the package roster itself closed.

---

## 1. System Identity, Claims & Non-Claims (VG-02)

### 1.1 Mission and operational thesis

The "evidence-directed competence runtime" framing is present in prose (`README.md:1-20`) but only partly in
code. What exists end-to-end today is: episodes over one typed environment family (git/filesystem/sandbox)
plus a second toy environment (TableWorld), effects authorised through scoped capabilities
(`kernel/dispatch.py`), and an out-of-process evaluator (`adapters/evaluators/daemon.py`).

What does **not** exist as code: the competence-artifact accumulation loop, the activation set, and the
release pipeline. There is no promotion engine, no distillation module, no operator registry (see §5, §6).

The instrument/one-variable-experiment thesis is implemented as the harness-manifest mechanism
(`agency/manifests/`, `domain/artifacts/manifest.py`) plus the offline lab (`lab/bench.py`,
`tools/telemetry/`).

### 1.2 The persistent object

`S_t = (G_C, G_E, L, A_t)` has **no single code counterpart**. Component-by-component:

| Spec term | As-built | Location |
|---|---|---|
| `L` — the ledger | **Implemented.** `EventEnvelope` + append-only stores + pure reducer | `domain/ledger/events.py:106`, `adapters/stores/event_store.py:30,121`, `domain/ledger/reducer.py:53` |
| `G_E` — evidence graph | **Partial.** `Claim` is a parsed value type with `contradicts`/`derivedFrom` fields; there is no graph store, no traversal, no contradiction search | `domain/evidence/claim.py:159` |
| `G_C` — competence artifact graph | **Partial.** `ArtifactGraph` / `KindRegistry` / `ArtifactFile` exist as *harness composition* structures (which manifest components a harness freezes), not as a competence store | `domain/artifacts/graph.py:29,39,65,85` |
| `A_t` — activation set | **Not implemented as a type.** `ActivationChanged` is a valid event kind and is reduced (`domain/ledger/reducer.py:320`) and projected (`runtime/ledger/projections.py:300-329` `ArtifactRegistryProjection`), but **nothing in `vanguard/packages/` ever emits it** |

The four-part R/O/M/P projection (`kind: "R"|"O"|"M"|"P"`) does **not** appear in code. The live `kind`
registry is a 17-row extensible list in `agency/manifests/kinds.json` (`system_prompt`, `tool_schema`,
`tool_impl`, `middleware`, `skill`, `context_policy`, `retrieval_policy`, `compaction_policy`,
`routing_policy`, `budget_policy`, `subagent_config`, `playbook`, `process_definition`, `runtime_image`,
`operator`, `approval_policy`, `competence_claim`) — i.e. the `T7.1` registry, not the VG-04 quadrants.

The "Coding Cell is the first client, not the ontology" claim is contradicted at the module level: `runtime/`
contains eight modules whose names encode the coding domain — `coding_budget.py`, `coding_coordinator.py`,
`coding_entrypoint.py`, `coding_plan.py`, `coding_progress.py`, `coding_verification.py`,
`mock_coding_tape.py`, plus `domain/ledger/coding_session.py`. See §1.9.

### 1.3 Unit of execution

`Episode E = (Task, EnvironmentSnapshot, ActivationSet, Budget, PolicySet)` versus the code's
`agency/episode/state.py:180 Episode`:

```
Episode(episode_id, run_id, principal, brief, depth, turns, terminal, detail)
```

- `Task` → `brief: str` on `Episode`; a richer `TaskContext` lives one layer up in `runtime/root.py:189`.
- `EnvironmentSnapshot` → **absent from `Episode`**; snapshots are an `EnvironmentAdapter` concern
  (`ports/environment.py:46 EnvironmentSnapshot`, `adapters/environment/git.py:144 snapshot()`).
- `ActivationSet` → **absent entirely.**
- `Budget` / `PolicySet` → held by `EpisodeEngine.__init__` (`agency/episode/engine.py:153`) and the kernel's
  `Governor`/`StandardPolicy`, not by the episode value.

There is no `TaskSpec`, `PlanArtifact` or `Proposal` wire type in `domain/wire/contracts.py`. The runtime's
plan is `runtime/coding_plan.py` — an application value explicitly documented as "not a model assertion".

### 1.4 Non-claims (`NC-01` … `NC-12`)

Non-claims constrain documentation, not code. Two have code-visible expressions:

- `NC-08` (budget exact at commit, not instantaneous) — implemented literally.
  `kernel/budget.py:132-153 Governor.commit` computes `settlement[dimension] = reserved - spent` with the
  in-source comment `NOT max(reserved - spent, 0)`; overruns are retained negative.
- `NC-12` (a shell classifier is not a security boundary) — `kernel/classifier.py:48 SinkRegistry` is a
  prefix-matching parser (`PRIVILEGED_PREFIXES`, `OBSERVATION_PREFIXES`, lines 56-57) and the docstring at
  `adapters/sandbox/rootless.py:1-7` places containment in the bubblewrap perimeter.

`NC-02`, `NC-03`, `NC-04`, `NC-05`, `NC-06`, `NC-07`, `NC-09`, `NC-10`, `NC-11` have no code counterpart and
need none.

**Code-level tension with `NC-01`/product language:** `README.md:26-60` presents a nine-level "Biological
Hierarchy of Emergent Competence" (LEVEL 0 sub-atomic … LEVEL 9 "ENTITY / AGI SWARM", "Emergent Machine AGI").
`REJ-10` rejects biological analogies as specification content and `L-14` marks them non-normative; the README
is the project's primary external artefact and carries them as its second section. No code module implements
or references the nine levels.

### 1.5 Falsifiable claims (`C-01` … `C-12`)

| # | Code-visible state |
|---|---|
| `C-01` | **Partially testable in-tree.** Three reconstruction manifests exist as pure data — `agency/manifests/vg-code-claude-shaped/`, `vg-code-opencode-shaped/`, `vg-code-swe-mini/`, registered in `agency/manifests/registry.json` with `"role":"reconstruction"`. Asserted by `test/agency/test_reconstructions.py` and `test/integration/test_reconstruction_packs.py` |
| `C-02` | Registry-entry-plus-config is real for tools/policies (`agency/manifests/kinds.json`, `runtime/root.py` binding table). Memory, retrieval index and web search: `IndexPort` exists (`ports/index.py:42`) with two impls (`adapters/stores/repo_index.py`); memory and web search do not exist |
| `C-03` | Two implementations exist per port (`T10.2`) for model, environment, sandbox, evaluator, event store, blob store, index. No language swap has occurred |
| `C-04` | **No parallel execution exists.** No task groups, no independence groups, no branch identifiers in the engine. `agency/episode/engine.py` is strictly sequential |
| `C-05` | Not measurable in-tree; no operator-isolation arm exists |
| `C-06` | No distilled competence artifact exists |
| `C-07` | **Live and green:** `tools/check_tcb_budget.py` reports 1,333 / 1,438 |
| `C-08` | `kernel/dispatch.py` is the single path; `test/kernel/test_dispatch.py:70-127` asserts no adapter executes without passing S2/S5/S8 |
| `C-09` | Not measurable; no artifact to carry across a model change |
| `C-10` | TableWorld exists (`adapters/environment/tableworld.py`, 138 lines) but is a bespoke in-memory table type, **not** an `EnvironmentAdapter` implementation — it exposes `handle_read`/`handle_patch`/`get_table_state`, not `profile/snapshot/observe/preview/apply/reconcile/compensate/dispose`. It is not bound in `runtime/root.py`'s binding table |
| `C-11` | **Implemented.** `Occurrence.UNDETERMINABLE` (`kernel/model.py:102-107`), `FailurePath.UNDETERMINABLE = "F-22"` (`model.py:151`), preserved in `kernel/dispatch.py` (`F-22` path); recovery controller at `runtime/ledger/recovery.py:124 RecoveryScanner` |
| `C-12` | `INV-2` is enforced at parse for claims and artifacts (`domain/evidence/claim.py:235-270`, `domain/wire/contracts.py:113-124`). No automatic checker *runs* the conditions; `InvalidationCheckRecord` has a schema (`schemas/v4/invalidation-check-record.schema.json`) but no producer in `vanguard/packages/` |

### 1.6 Design axioms (`A-01` … `A-12`)

| # | As-built |
|---|---|
| `A-01` | Held for agentic control flow: no workflow engine, no topology language, no graph validator, no node registry. **But** a declared durable state machine exists — `runtime/governance/definitions.py:33 ProcessDefinition`, `:67 ProcessInstance`, `runtime/governance/engine.py:17 ProcessEngine` — with `states`, `transitions`, nondeterminism rejection at parse (`domain/wire/contracts.py:294-319`). This is `ADR-0050`/`L-10`, not `A-01` |
| `A-02` | **Not implemented.** There is no operator registry and no addressable, versioned, content-hashed operator entry. The only "operator" in the tree is `runtime/root.py:483 _LayeredOperator`, a private provider wrapper. `agency/manifests/kinds.json` reserves the `operator` kind but no manifest declares one |
| `A-03` | Implemented in the `ADR-0051` sink-class form, not the universal form: `kernel/classifier.py:92 SinkRegistry.requires_grant` returns true only for `SinkClass.PRIVILEGED`; `kernel/dispatch.py:207-208` issues a grant only then |
| `A-04` | Type-level enforcement is **partial**. `kernel/model.py:74 Span` carries `trust` and `source_class`, and `agency/context/layers.py:105 Block` carries a provenance mapping. But the context compiler accepts raw `str` (`Fragment(source, label, text)` at `layers.py:89`) — provenance is attached by the constructing call site, not made impossible to omit by the type |
| `A-05` | Enforced statically. `tools/check_boundaries.py:64-69` bans any import of `adapters/evaluators/**` from `agency`, `runtime` or `governance`, with a single named exception, `vanguard/packages/runtime/root.py`. Must-fail counterpart `MF-S0-005` |
| `A-06` | No parallelism exists, so order preservation is trivially held and independence groups are absent |
| `A-07` | Substantially held. `LedgerBridge` (`runtime/root.py:413`) writes every kernel event to one `EventStorePort`; `runtime/session_log.py:1-8` documents the deletion of a second account (`runtime/coordination.py`); `runtime/ledger/projections.py` treats projections as rebuildable caches (`rebuild_projection`, line 330) |
| `A-08` | Held: `runtime/root.py:1-20` documents that the manifest supplies prompts, tools, verbs, sink classes, risk, budgets and evaluators, and `root.py` supplies a verb→adapter binding table only |
| `A-09` | Not verifiable in backend scope (clients excluded). `tools/check_boundaries.py:36` restricts `client` to `{domain, runtime}` |
| `A-10` | Held mechanically: `tools/run_broken_tests.py` requires every registered must-fail case's broken counterpart to fail **and to fail for the declared reason** (`run_broken_tests.py:59-63`); 38 cases pass |
| `A-11` | Held: `domain/artifacts/manifest.py:143 compose()` freezes a `FrozenHarness` per episode; unknown names fail at composition (`runtime/root.py:179 CompositionError`) |
| `A-12` | Held: `RunTermination.INSTRUMENT_ERROR` (`agency/episode/state.py:44`) is separate from any verdict; `ports/evaluator.py:42 Verdict` is produced only by the exterior evaluator |

### 1.7 Cross-cutting norms (`N-01` … `N-21`)

| # | As-built |
|---|---|
| `N-01` | Held structurally: model proposes (`agency/episode/engine.py:227`), kernel authorises (`kernel/dispatch.py:177`), adapter executes (`:296`), evaluator evidences (`runtime/root.py:935 _evaluate`) |
| `N-02` | Reflected in comments; the enforcing artefact is `adapters/sandbox/rootless.py` probes |
| `N-03` | **Partially held.** `kernel/grants.py:62 Grant` carries `principal`, `scope` (actions+resources+constraints), `expires_at`, `purpose_digest`. It has no `action`/`purpose` *string*; purpose is a digest only, and `issue()` refuses an empty `purpose_digest` (`grants.py:164-166`) |
| `N-04` | Held: `kernel/attenuation.py:131 attenuate()` returns `AttenuationDenied` recording `requested` and `grantable`; never intersects |
| `N-05` | Held: `Constraints.narrower_than` (`attenuation.py:64-83`) checks nine dimensions and names the first that widens |
| `N-06` | Enforced statically: `tools/check_boundaries.py:41-58` confines `subprocess`/`os.popen`/`pty` imports to `vanguard/packages/adapters/sandbox/` with **three named exceptions** — `adapters/evaluators/isolated.py`, `adapters/environment/git.py`, `adapters/models/env_loader.py` |
| `N-07` | Partially: evaluator has UID 10002 (`adapters/evaluators/daemon.py:35`), worker UID 10001 (`containers/worker.Dockerfile`). Control plane and cognition share one process |
| `N-08` | Held by omission — nothing in the tree writes to the live runtime |
| `N-09` | **Not held as five/six axes.** `kernel/model.py:40 Trust` is a single ordered 5-value enum (`OPERATOR`, `SYSTEM`, `AGENT_DERIVED`, `UNTRUSTED_DERIVED`, `UNTRUSTED_EXTERNAL`) — one axis, not five. The wire schema carries a separate `provenance` object (`domain/wire/contracts.py:103-111`) |
| `N-10` | Only the evaluator produces a `Verdict`; there is no ranker at all, so the norm is untested |
| `N-11` | `ports/evaluator.py:42 Verdict` carries protocol/evaluator identity |
| `N-12` | No promotion path exists |
| `N-13` | Enforced at parse: `domain/evidence/claim.py` requires non-empty `invalidationConditions` |
| `N-14` | Not implemented (no competence graph) |
| `N-15` | Held: `runtime/ledger/recovery.py:1-11` states the terminal record is always written by the external scanner; `test/trust/test_spine.py:180` asserts it |
| `N-16` | Held: `kernel/dispatch.py:315-323` releases in `finally`; `test/kernel/test_dispatch.py:110` covers every post-reservation failure path |
| `N-17` | Held (see `A-11`) |
| `N-18` | No frontier machinery exists |
| `N-19` | `trainability` is an envelope field with three values (`domain/ledger/events.py:48`); no corpus opt-in code exists |
| `N-20` | Vacuously held — no playbook implementation exists |
| `N-21` | **Held.** `agency/context/compiler.py:135-171` renders the brief into L4 inside the cached prefix; `agency/context/compaction.py` strategies operate on `dialogue` (L5) blocks only |

### 1.8 Irreversible locks (`L-1` … `L-6`)

| # | As-built |
|---|---|
| `L-1` | Schemas exist as 38 artefacts in `schemas/v4/` (writer + generated `.reader.` pairs) and a Python reader profile at `domain/wire/contracts.py`. `schemas/v4/MANIFEST.md` holds status; the theory records all 14 at `DRAFT` |
| `L-2` | Held and measured: `kernel/` is exactly nine files (`__init__`, `attenuation`, `budget`, `classifier`, `dispatch`, `grants`, `model`, `policy`, `provenance`) — the exact roster GTS-13C §5.3 names, plus `model.py` and `__init__.py` |
| `L-3` | **Violated in the sense that operators do not exist at all** — neither as data nor as control flow. No regression, but no realisation |
| `L-4` | No improvement relation is implemented |
| `L-5` | Held: `EvaluatorPort` (`ports/evaluator.py:52`), separate daemon, boundary rule, `MF-S0-005` |
| `L-6` | Held: subprocess + NDJSON seams at `adapters/sandbox/worker.py`, `adapters/evaluators/daemon.py` (Unix domain socket + NDJSON), `adapters/stores/ledger_jsonl.py`, `runtime/service/server.py` |

### 1.9 Strategic frame and generality constraint

The 80/20 dual-track is **not** the in-tree ratio. Coding-specific code totals **2,088** physical LOC
across `coding_budget.py` (243), `coding_coordinator.py` (271), `coding_entrypoint.py` (514),
`coding_plan.py` (223), `coding_progress.py` (365), `coding_verification.py` (243), plus
`mock_coding_tape.py` (126) and `domain/ledger/coding_session.py` (103). The non-coding environment
(`adapters/environment/tableworld.py`) is 138 LOC.

The generality constraint is **mechanised** by `tools/check_core_changes.py` (tested by
`test/tools/test_check_core_changes.py`), which is the `ADR-0060` invariant: adding a domain must change zero
lines in `kernel/` or `agency/episode/`. `agency/episode/engine.py:334-335` carries an explicit comment that
its scope check names no verb, "so `ADR-0060` holds and adding a domain is still zero lines in this file."

However, coding-shaped concepts do reach `domain/`: `domain/ledger/coding_session.py:42
project_coding_session` is a domain-layer projection named for one environment.

### 1.10 Approved stack — decision level

| Area | Spec decision | As-built |
|---|---|---|
| Control plane | Python (`ADR-0063`) | **Matches.** 125 stdlib-first Python modules |
| Interaction client | TypeScript strict on Node | Present at `vanguard/clients/cli/` (out of scope here) |
| Wire contracts | JSON Schema 2020-12 normative | 38 artefacts in `schemas/v4/`; Python reader profile in `domain/wire/contracts.py`; a parallel TS source lives at `vanguard/packages/domain/contracts.ts` (README cites the pair at `:222` under a stale `domain/wire/` path) |
| Validation | TS validator as implementation | Second-language *reader* exists in the CLI workspace |
| Canonicalisation | RFC 8785 / JCS | **Implemented in-tree:** `domain/canonicalisation/jcs.py` (226 lines), `digest.py` (24 lines) |
| Durable store | Embedded transactional, WAL, single writer | **Implemented:** `adapters/stores/event_store.py:121 SqliteEventStore`, `PRAGMA journal_mode = WAL` (line 139), `synchronous="FULL"` default (line 124), monotonic-`seq` enforcement per run (lines 182-196) |
| Blob store | Content-addressed FS with encryption hook | `adapters/stores/blob_store.py` (89 lines) — two impls. **No encryption hook keyed by classification** (`CT-19` unmet) |
| Sandbox | Hardened rootless container | `adapters/sandbox/rootless.py:46 RootlessSandboxRunner`, `/usr/bin/bwrap` with `--unshare-all --unshare-user --die-with-parent` (lines 94-96) |
| Evaluator | Separate process/identity/digest | `adapters/evaluators/daemon.py:35 expected_uid=10002`, SO_PEERCRED peer check (line 65) |
| Laboratory | Python, offline, reads exports | `lab/bench.py`, `build.py`, `diff.py`, `run.py`; `lab/` is forbidden from importing anything (`check_boundaries.py:225-233`) |
| Systems seams | Subprocess + NDJSON over stdio | Matches |

**Emergent, undocumented in theory:** the backend has a hard third-party dependency — `cryptography`
(`runtime/governance/approvals.py:24-25` imports `cryptography.hazmat.primitives.asymmetric.ed25519`). The
project is described as "stdlib-only Python core"; this is the single exception and it sits inside the
governance path.

### 1.11 Risk register (`RSK-01` … `RSK-15`)

No code artefact enumerates or tracks `RSK-*`. Mitigations with code:
`RSK-01` → boundary rule + `MF-S0-005`; `RSK-04` → `tools/run_broken_tests.py`, `tools/telemetry/statistics.py`
refusals; `RSK-07` → `FailurePath.DENIED_SCOPE_ESCALATION` marked alertable (`kernel/model.py:150-155`);
`RSK-08` → no self-update path exists; `RSK-11` → `tools/check_tcb_budget.py`;
`RSK-12` → invalidation conditions at parse only, no automatic checker.
`RSK-02`, `RSK-03`, `RSK-05`, `RSK-06`, `RSK-09`, `RSK-10`, `RSK-13`, `RSK-14`, `RSK-15`: no code counterpart.

### 1.12 Honest limits

Directly corroborated in code and roadmap rather than contradicted. `docs/scrum/roadmap_backend.md:56` records
`PO acceptance — [DONE] ✅ (honest) … live tool-call, Q2, spend, Claude daily-driver still TODO`, and
`docs/scrum/sprints/wave20/evidence/s20-g-03-release-claims.md` is cited as "no coding win, no GUI, no lift".

---

## 2. Turn Lifecycle, Planes & Execution Model (VG-03)

### 2.1 The execution protocol

`observe → propose → authorise → effect → receipt` is implemented as one loop in
`agency/episode/engine.py:185-395`. `evaluate` is **not** in that loop — it is invoked one layer up by
`runtime/root.py:935 HarnessSession._evaluate()` after `EpisodeEngine.run()` returns.

| Step | Spec owner | As-built symbol |
|---|---|---|
| observe | Environment adapter | `EpisodeEngine._view()` (`engine.py:398`) returns a dict of episode state; a real environment observation is an `fs.read` effect through the kernel |
| propose | Cognitive operator | `self._model.propose(view, tools, sampling)` (`engine.py:227`), wrapped by `runtime/root.py:483 _LayeredOperator.propose` which compiles L1–L5 first |
| authorise | Broker | `Kernel.dispatch` → `StandardPolicy.authorize` (`kernel/policy.py:72`) |
| effect | Environment adapter in the perimeter | `adapter.execute(request)` at `kernel/dispatch.py:296`, bridged by `runtime/root.py:321 _EnvironmentEffect` |
| receipt | Environment adapter | `AdapterOutcome` (`kernel/model.py:111`) in-kernel; `ports/environment.py:116 EffectReceipt` at the port |
| evaluate | Evaluator, separate identity | `adapters/evaluators/isolated.py:31 IsolatedEvaluator`, reached via `adapters/evaluators/client.py` over the daemon socket |

**Name divergence:** the spec's "broker" has no module, class or port of that name. The implementation calls
it `Kernel` (`kernel/dispatch.py:97`) and `StandardPolicy` (`kernel/policy.py:56`). This matches spec ambiguity
`Y-20`.

**Name divergence:** the spec's "policy kernel" / "the dispatcher"; the README and code comments call it the
**"Attenuation Kernel"** (`README.md:38,55,235`) — the term flagged by `Y-03` as having no spec anchor. There
is no `AttenuationKernel` class; `kernel/attenuation.py` holds `attenuate()`, `Scope`, `Constraints`.

### 2.2 The inversion: agent loop over workflow DAG

Held. There is no graph validator, node registry, topology parser or DAG type anywhere in
`vanguard/packages/`. `agency/episode/engine.py` is a `while not episode.is_terminal` loop (line 211).

Of the six graph-node equivalences: `retrieve` is an effect (`fs.read`/`fs.search` verbs in
`agency/manifests/vg-code-default/manifest.json`); `architect` has no counterpart (no operator mechanism);
`generate`+`apply` is `patch.apply` bound to `adapters/environment/git.py:603 apply()`; `evaluate` is exterior;
`repair` does not exist in the engine but **does** exist one layer up as `runtime/repair.py:58
drive_until_green` (see §2.6 emergent); fan-out+join does not exist.

`DEF-01` (authoring canvas) and `REJ-01` (runtime graph) are both honoured — neither exists.

### 2.3 The six planes

Only two planes are enforced by OS identity; the rest are module boundaries.

| Plane | As-built |
|---|---|
| **Interaction** | `runtime/service/server.py` (Unix domain socket, 178 lines) + `runtime/service/service.py:74 RuntimeService`. The TS CLI is the client (out of scope) |
| **Cognition** | `agency/` — `episode/`, `context/`, `manifests/`. Co-located in the controller process |
| **Control** | `kernel/` + `runtime/governance/`. Co-located with Cognition |
| **Workload** | `adapters/sandbox/rootless.py` + `adapters/sandbox/worker.py`; UID 10001 per `containers/worker.Dockerfile` |
| **Evidence** | `adapters/evaluators/daemon.py`, UID 10002, SO_PEERCRED, image digest at handshake |
| **Evolution** | **No runtime component**, matching the Phase 0 expectation. `CandidateBuilt`, `CandidateAttested`, `CanaryPromoted`, `RollbackTriggered` are declared event kinds (`domain/ledger/events.py:94-97`) with **zero emitters** |

**Divergence — the evaluation trigger.** The spec assigns the Evidence plane ownership of the trigger: it
observes episode termination in the ledger and emits `EvaluationRequested`; "no episode can request its own
evaluation." As built, `runtime/root.py:935 HarnessSession._evaluate()` is called by the *runtime* immediately
after `EpisodeEngine.run()` returns, and it calls `bound.evaluate(RunRef(...), EvaluationProtocol(...))` directly. There
is **no ledger observer**, and `EvaluationRequested` — a declared event kind at `domain/ledger/events.py:80` —
is **never emitted anywhere in `vanguard/packages/`**. What the daemon does enforce is that the *verdict* is
produced under a separate identity and that the caller cannot forge it (`adapters/evaluators/signing.py`,
Ed25519 verdict signing; `runtime/root.py:1300-1313` requires `VANGUARD_EVALUATOR_VERDICT_PUBLIC_KEY`).

**Divergence — plane consequence 1.** The event store is co-located with Cognition and Control, as the spec's
Phase 0 concession allows.

### 2.4 Intra-process layer topology (`LT-1` … `LT-8`)

`tools/check_boundaries.py:23-37` encodes the lattice. Live run: **PASS, 244 source files checked.**

| # | Spec contract | Encoded rule | Held? |
|---|---|---|---|
| `LT-1` | `domain/` imports nothing | `"domain": set()` | Yes |
| `LT-2` | `ports/` imports only `domain/` | `"ports": {"domain"}` | Yes |
| `LT-3` | `kernel/` ← domain, ports; never adapters/agency | `"kernel": {"domain","ports"}` | Yes |
| `LT-4` | `agency/` ← domain, ports, kernel; never adapters/lab | `"agency": {"domain","ports","kernel"}` | Yes |
| `LT-5` | `adapters/` ← domain, ports; **never each other** | `"adapters": {"domain","ports"}` — sibling-family imports are separately rejected (fixture `test/broken/fixtures/adapter_sibling/`) | Yes |
| `LT-6` | `runtime/` may import everything | `{"domain","ports","kernel","agency","adapters","governance"}` | Yes |
| `LT-7` | `clients/` ← domain + daemon client | `"client": {"domain","runtime"}` | Yes (client code out of scope) |
| `LT-8` | Nothing imports `lab/`; `lab/` is offline | `check_boundaries.py:225-233` — `lab/` must import **nothing**, stricter than the spec | Yes; `MF-S0-*` fixture `lab_import/` |

**Emergent, undocumented in theory — a seventh area.** `governance` is a first-class row in the boundary table
(`check_boundaries.py:34-36`) with its own narrower allowance `{domain, ports, kernel}` — deliberately
excluding `agency` and `adapters`. It physically lives at `vanguard/packages/runtime/governance/` and is
special-cased out of `runtime` by `area_for()` (`check_boundaries.py:96-98`). VG-03 §4 names no such layer;
this is `T10.1`/GTS-13C §5.4 made real. Must-fail counterpart `MF-S0-004` ("governance may not depend on model
APIs").

**Emergent, undocumented in theory — an eighth area.** `benchmarkings/` is a scanned root
(`check_boundaries.py:76-83`) with its own allowlist row and its own must-fail case (`MF-S7-C-001`,
"benchmarkings may import only runtime…").

**Emergent, undocumented in theory — three additional static rules** beyond the `LT-*` set:
1. **Closed package set** — anything under `vanguard/packages/` other than the six named packages is a build
   failure (`check_boundaries.py:203-224`), directory *or* module.
2. **Subprocess containment (`N-06` as a lint)** — `subprocess`, `os.popen`, `pty`, `child_process` may only be
   imported under `adapters/sandbox/`, with three named exceptions (`check_boundaries.py:41-58`).
3. **Evaluator unreachability as an import rule** — `agency`, `runtime`, `governance` may not import
   `adapters/evaluators/**` except at `runtime/root.py` (`check_boundaries.py:60-69`).

Plus a source-cycle detector (`find_cycles`, `check_boundaries.py:178-201`) and an S4-exit mode
(`--s4-exit`) proving `spike/` and `slice/` are absent (`MF-S4-001`). Neither `spike/` nor `slice/` exists in
the tree.

### 2.5 Composition — the four extension forms

Of the four forms, **two exist as ports and two do not exist at all.**

| Form | As-built |
|---|---|
| `ObservationSource` | **No such port, class or protocol.** The nearest artefacts are `IndexPort` (`ports/index.py:42`) and `agency/manifests/discovery.py:37 WorkspaceDiscovery`, which scans `AGENTS.md`, `CLAUDE.md`, `PROJECT.md`, `.github/copilot-instructions.md` into L3/L4 fragments |
| `CognitiveOperator` | **No such port, class or protocol.** No operator registry, no operator invocation as a tool, no operator briefs |
| `EffectAdapter` | Exists as a kernel-side `Protocol` (`ports/kernel.py:46 EffectAdapter`, `name`/`healthy()`/`execute()`) and as the richer `ports/environment.py:140 EnvironmentAdapter` |
| `Evaluator` | Exists: `ports/evaluator.py:52 EvaluatorPort` |

**Recursive composition is implemented, but not by operator invocation.** `agency/episode/engine.py:490
EpisodeEngine.spawn()` runs an attenuated **child episode** under `S8-B-01`/`ADR-0060`. The child receives a
`Scope` parsed from the proposal (`engine.py:96 _parse_child_scope`), fails closed on a missing or
unparseable scope (`engine.py:263-286`), and returns a value-only `SpawnResult` (`state.py:50`). Depth is
bounded through `Constraints.max_depth` (default 8, `attenuation.py:56`) and `attenuate()` sets
`depth = parent.depth + 1` (`attenuation.py:167`).

The seven per-concern rules (return value, workspace, failure, budget, depth, events, provenance) are
partially realised: return value is a value (`SpawnResult.payload`), failure is typed, depth is a budget
dimension, budget is a child lease via `parent_lease`. **Child events carrying a parent identifier** are
handled by `agency/episode/engine.py:618 _CausationEventAdapter`. **Provenance of the returned text as
untrusted-derived** has a kernel implementation (`kernel/provenance.py:92 Accumulation.child_return`) that is
**not called from `spawn()`** — see §4.7.

Registry freezing is real: `domain/artifacts/manifest.py:143 compose()` → `FrozenHarness` (line 72).

### 2.6 The episode engine

#### 2.6.1 The loop

`agency/episode/engine.py:185-395 EpisodeEngine.run()`. Named-collaborator mapping:

| Spec collaborator | As-built |
|---|---|
| `stateAssembler.materialize` | `EpisodeEngine._view()` (`engine.py:398`) — returns a plain mapping; the real assembly is `ContextCompiler.compile()` (`agency/context/compiler.py:135`) invoked by `_LayeredOperator.propose` |
| `operatorPolicy.select` | **No counterpart.** There is exactly one model, bound at composition |
| `operatorRunner.invoke` | **No counterpart.** `self._model.propose(...)` is called directly |
| `eventStore.append(ProposalProduced)` | `EpisodeEngine._emit_proposal` (`engine.py:441-465`) |
| `broker.authorize` | `self._kernel.dispatch(...)` (`engine.py:358`) — authorisation is *inside* dispatch, not a separate call |
| `effectExecutor.execute` | Inside `Kernel._guarded` (`kernel/dispatch.py:296`) |
| `regroundPolicy.shouldRun` | `agency/context/regrounding.py:19 RegroundPolicy.should_reground` **exists but is never called** — the only references outside the module are in `test/agency/test_regrounding.py`. The engine loop contains no re-grounding branch |
| `environment.observe` | `ports/environment.py:151 observe()`, reached through `runtime/root.py:321 _EnvironmentEffect` |
| `reduce` | Two separate reducers: `Episode.with_turn`/`terminated` (`agency/episode/state.py:217,220`) for the in-memory episode, and `domain/ledger/reducer.py:53 reduce_event` for the ledger |

Emission split is implemented as specified: the loop emits `ProposalProduced`; the kernel emits everything
else; intent is durably appended at S8a before S9 (`kernel/dispatch.py:278-294`) and the outcome at S12
(`:330-368`).

No evaluator is invoked in the loop — asserted by `test/trust/test_spine.py:303
test_the_episode_holds_no_evaluator_authority`.

#### 2.6.2 Terminal states — two separate axes

**Held exactly.** `agency/episode/state.py:31 RunTermination` carries all eight spec values and only those:
`completed`, `abstained`, `escalated`, `cancelled`, `budget_exhausted`, `instrument_error`, `runtime_error`,
`abandoned`. The GTS-13C `T4.5` collapsed vocabulary (`resolved/denied/recovered`) does **not** appear —
`ADR-0057` resolved in VG-03's favour and the code follows VG-03.

The evaluation axis (`satisfied`/`unsatisfied`/`partially_satisfied`/`inconclusive`/`invalid_evaluation`) has
**no enum**. `ports/evaluator.py:42 Verdict` carries free-form fields; `adapters/evaluators/isolated.py`
produces "inconclusive" as a string. `runtime/outcome_labels.py` (65 lines) is a separate emergent label set.

Provider failure → `RunTermination.INSTRUMENT_ERROR` at `engine.py:231-244` (three paths: adapter raise,
`result.ok` false, malformed proposal).

#### 2.6.3 Two distinct retries

Transport retry lives in the model adapters (`adapters/models/openrouter.py`, 896 lines, with
`adapters/models/routing.py` preflight and `runtime/provider_health.py` cooldown/rotation). Cognitive retry is
implicit — the loop simply continues after a failed dispatch (`engine.py:388-394`), since
`_TERMINAL_FOR_FAILURE` (`engine.py:66-74`) lists only seven failure paths as run-ending; everything else is
reduced and the loop continues.

#### 2.6.4 No-progress detection

**Implemented, with a one-field divergence.** `agency/episode/state.py:164 Turn` carries
`(index, state_digest, proposal_descriptor, receipt_digest, progress_signal)` and
`Turn.signature()` (`state.py:174`) returns the 4-tuple
`(state_digest, proposal_descriptor, receipt_digest, progress_signal)` — matching the spec tuple exactly.
`Episode.repeats(turn, limit)` (`state.py:226`) fires termination as `ABANDONED`.

The **expected-no-change flag and deadline** exemption for deliberate polling has **no counterpart**.

#### 2.6.5 Inner-loop invariants

| Invariant | As-built |
|---|---|
| Every turn bounded by a lease, not a constant | Held: `Governor.reserve` per dispatch (`kernel/budget.py:108`); `Reservation` built from the proposal (`engine.py:482`) |
| A denial names the offending call | Held: `AttenuationDenied(dimension, requested, grantable)` (`attenuation.py:112`); `BudgetDenied(dimension, requested, remaining, reason)` (`budget.py:32`) |
| Results labelled at construction | **Partially.** `Span` carries `source_class`; but the production composition never constructs a result span (see §4.7) |
| Widening is a classifier output | Held: `kernel/dispatch.py:166` calls `self._classifier.widens_capability(request)`; `MF-KRN-001` fails against a constant |
| Leases release on every path | Held: `finally` at `kernel/dispatch.py:315` |
| Depth is a budget dimension | Held: `Constraints.max_depth`; `StandardClassifier.widens_capability` returns true when `request.depth > held.max_depth` (`classifier.py:115-119`) |

**Emergent, undocumented in theory:** a **turn ceiling** independent of the budget vector.
`EpisodeEngine._max_turns` terminates the run as `ABANDONED` (`engine.py:216-221`), and `runtime/root.py:836-846`
carries a comment that the bound must survive the approval boundary or "an agreeable reviewer bought the run
another eight turns per approval."

**Emergent, undocumented in theory:** an `agency`-level scope check that is *not* the kernel's.
`engine.py:319-355` refuses a proposal whose action is outside `self._scope.actions` **when the episode is
attenuated**, producing a turn with `progress_signal="scope_escalation_denied"` and no kernel dispatch. The
source comment explains it is scoped to children on purpose. This is a second refusal site outside
`Kernel.dispatch`; it emits no `AuthorizationDenied` event (it records only an in-memory `Turn`).

### 2.7 Environments and the adapter protocol

`ports/environment.py:140 EnvironmentAdapter` is a `Protocol` with **all eight** spec methods:
`profile`, `snapshot`, `observe`, `preview`, `apply`, `reconcile`, `compensate`, `dispose`
(lines 143-171). Divergence: every method returns `Result[T]` (`ports/event_store.py:37`) rather than a bare
value, and `grant` is typed `Optional[Any] = None` rather than a required `CapabilityGrant`. The grant is
therefore **not enforced at the port signature** — this is the code's resolution of contradiction `X-02`,
landing on the GTS-13C side.

Implementations:

| Adapter | File | Lines | Full protocol? |
|---|---|---|---|
| Git | `adapters/environment/git.py:50 GitEnvironment` | 847 | Yes — all eight |
| Fake | `adapters/environment/fake.py` | 642 | Yes |
| Sandboxed | `adapters/environment/sandboxed.py` | 265 | Yes; routes everything through the injected worker |
| TableWorld | `adapters/environment/tableworld.py:53 TableWorldEnvironment` | 138 | **No** — exposes `handle_read`/`handle_patch`/`get_table_state` only |

**The frozen atom set.** The spec freezes `read`, `write`, `edit`, `glob`, `grep`, `shell`. The code's live
verb set in `agency/manifests/vg-code-default/manifest.json` is `fs.read`, `fs.search`, `patch.apply`,
`proc.exec` — four verbs, different names. `vg-shell-only/manifest.json` declares `proc.exec` alone.
`kernel/classifier.py:56-57` hard-codes namespace prefixes `fs.write`, `fs.delete`, `net.`, `exec.`, `proc.`,
`secret.` (privileged) and `fs.read`, `fs.stat`, `fs.list`, `git.read` (observation).

Per-tool rules: read/write sets are **schema-supported but unenforced** — `domain/wire/contracts.py:139-142`
accepts optional `readSet`/`writeSet` on an `EffectDescriptor`, and nothing consumes them (no independence
analysis exists). "No tool receives a filesystem handle" is held — `_EnvironmentEffect` (`runtime/root.py:321`)
passes only serialisable requests. "A tool may never write into pinned evaluator paths" is enforced at the
import graph rather than at the broker; there is **no `AT-12`-style selector reachability check** anywhere.

**Irreversible effects.** `preview` exists (`git.py:508`), idempotency keys exist
(`EffectRequest.idempotency_key`, `kernel/model.py:96`; used at `dispatch.py:218` to decide single-use), risk
tiers exist (`RISK_ORDER = ("low","medium","high","critical")`, `attenuation.py:41`), approval exists
(`runtime/governance/approvals.py`), receipts are verifiable, reconciliation exists
(`domain/ledger/reconciliation.py:36 EffectReconciler`, `git.py:753 reconcile`), and compensation exists
(`git.py:800 compensate`). The requirement to emit **plain text stating no rollback exists** has no counterpart.

### 2.8 Concurrency (`CC-1` … `CC-7`)

**No concurrency machinery exists in `vanguard/packages/`.** There are no task groups, no independence groups,
no branch identifiers on episodes, no cancellation scopes reaching process groups, and no per-branch workspaces.

| # | As-built |
|---|---|
| `CC-1` | Trivially held — execution is sequential |
| `CC-2` | No barriers exist because no parallelism exists |
| `CC-3` | **No `IndependenceGroup` type.** `ADR-0065`'s `D-02` ("depth-1 until independence groups exist") is the operative constraint; the code went to depth-8 via `spawn` but still has no independence groups |
| `CC-4` | No parallel reads |
| `CC-5` | Child leases exist (`parent_lease`); cancellation scopes do not. Cancellation is a single `is_cancelled` callable polled once per turn (`engine.py:212-216`) |
| `CC-6` | `ConflictDetected` is a declared event kind (`events.py:74`) and is **reduced** (`reducer.py:378`, `projections.py:283`) but **never emitted** |
| `CC-7` | No batching exists |

`BranchId` appears in `domain/primitives/primitives.py` `_ID_KINDS` but `EventEnvelope` has no `branch_id`
field in the Python dataclass (`domain/ledger/events.py:106`); the wire reader does not require one.

### 2.9 Abnormal termination and recovery

**Implemented, and among the better-covered subsystems.**

| Element | As-built |
|---|---|
| Run lease | `Lease` (`kernel/budget.py:58`) is per-effect, not per-episode. The episode-level lease is the `run lease` concept in `runtime/ledger/recovery.py` |
| Heartbeat | `Heartbeat` event kind (`events.py:96`), consumed by `recovery.py` |
| Recovery scanner | `runtime/ledger/recovery.py:124 RecoveryScanner`; `_parse_iso_to_millis` (line 110) for expiry |
| Recovery controller | Same module; module docstring (lines 1-11): "The terminal record (RunRecovered or RunAborted) is ALWAYS written by the external recovery controller, NEVER by the corpse" |
| Effect reconciliation | `domain/ledger/reconciliation.py:36 EffectReconciler` keyed on idempotency key |
| Preserved uncertainty | `Occurrence.UNDETERMINABLE`; `kernel/dispatch.py:300-306` maps an adapter exception to `UNDETERMINABLE`, never to failure |

Also present: `replay_ledger_state` (`recovery.py:57`) and `LedgerReplayState` (line 44).
Tested by `test/trust/test_spine.py:180-218` and `test/runtime/test_resume_from_ledger.py`.

### 2.10 Context engineering

#### 2.10.1 The layer model

**Implemented exactly.** `agency/context/layers.py:36 Layer` is a `str, Enum` with values
`L1`…`L5` named `SYSTEM`, `TOOLS`, `ENVIRONMENT`, `TASK`, `DIALOGUE` (lines 39-43), each with the spec's
stability comment inline. `Block` (line 105) carries `provenance` (line 123) and `identity` (line 134);
`CompiledContext` (line 146) exposes `prefix_digest` (line 168), `digest` (line 175), `messages` (line 182)
and `bundle` (line 203) — one message per non-empty layer.

#### 2.10.2 Cache boundaries

**Implemented.** `ContextCompiler.__init__` takes `breakpoint_ceiling: int = 4`
(`agency/context/compiler.py:86`). `_breakpoints()` (line 173) refuses to spend a breakpoint on an empty
layer. Exceeding the ceiling raises **at assembly**: `CacheBreakpointCeilingExceeded`
(`compiler.py:68`, raised at lines 153-156). Breakpoint positions are restricted to L1/L3/L4 by
`layers.py:56-58`, whose comment records that L2 is inside the prefix and L5 is absent on purpose.
`ContextBudgetExceeded` (`compiler.py:63`) fires when L1–L3 plus the brief exceed the token ceiling
(lines 159-162).

Prefix stability as a **CI metric over a fixed replay** exists outside the backend:
`tools/telemetry/cache_replay.py` and `tools/telemetry/prefix_attribution.py`, tested by
`test/lab/test_cache_replay.py` and `test/lab/test_prefix_attribution.py`. Must-fail counterparts
`MF-CTX-001` ("compiled context bypassed") and `MF-CTX-002` ("tool observation absent on turn 2").

#### 2.10.3 Compaction strategies (pluggable and comparable)

`agency/context/compaction.py` implements **three of five** strategies behind a `CompactionStrategy` Protocol
(line 30):

| Spec strategy | As-built |
|---|---|
| `recency_window` | `RecencyWindowStrategy` (line 90) — **the registry default** (`resolve_compaction_strategy`, lines 237-255, falls back to `recency-window` on every unknown/absent policy) |
| `result_eviction` | `ResultEvictionStrategy` (line 48), with `_receipt_for` (line 15) keeping the fact and dropping the body |
| `model_summarize` | **Absent** |
| `structured_consolidate` | `StructuredConsolidateStrategy` (line 173) + `StructuredRecord` (line 149) |
| `operator_isolation` | **Absent** (no operators exist) |

The spec names `structured_consolidate` "the recommended default"; the code's default is `recency_window`.
`DEF-11` deferred everything past a recency window in Phase 0; three strategies now exist.

#### 2.10.4 Structured consolidation

`agency/context/compaction.py:149 StructuredRecord` with `to_summary_text()` (line 158). The spec's five
fields are `decisions`, `invariants`, `open`, `artifacts`, `deadEnds`. The implementation extracts structured
information from dialogue blocks (lines 196-219) and emits a single block labelled `structured_record` from
source `structured_consolidate`. Consolidation-loss measurement (replace transcript, re-run, compare) has no
in-tree runner.

#### 2.10.5 Long-horizon invariants

- Compaction drops the load-bearing detail → `StructuredConsolidateStrategy` exists but is not the default.
- Error compounds silently → **`RegroundPolicy` exists and is not wired in.** `agency/context/regrounding.py`
  (43 lines) defines `should_reground(turn_number)` and `create_effect_request(...)`; grep across
  `vanguard/` finds no caller. Its `create_effect_request` builds a `ports.environment.EffectRequest` with a
  hard-coded `"path": "STATUS.md"` (line 40) — a literal, not a policy input.
- Goal drift → held; the brief sits in L4 and compaction touches L5 only.

### 2.11 Playbooks: methodology as data

**Not implemented.** There is no playbook loader, no rigidity dial, no tool masking, no phase gate, and no
`Playbook` type in `vanguard/packages/`. The single occurrence of the word is a reserved registry row:
`domain/artifacts/graph.py:19` lists `"playbook"` among `BUILTIN_KINDS`, and
`agency/manifests/kinds.json` carries `{"kind":"playbook", ...}`. No manifest declares a playbook component.

`docs/scrum/roadmap_backend.md:43` corroborates: *"O-03 spawn live but playbooks still deferred."*

#### 2.11.1 The rigidity dial

No counterpart. `advisory`/`guided`/`strict` appear nowhere in the backend.

#### 2.11.2 Three levers, and no fourth

No counterpart for tool masking or gate evaluation. **Context injection as an L5 note** exists as a general
mechanism (`_LayeredOperator.note`, `runtime/root.py:504`), used for tool results rather than phase intent.

The nearest analogue to a *policy that constrains without dispatching* is
`agency/manifests/vg-code-default/approval-policy.json` plus
`runtime/governance/approvals.py:470 DescriptorBoundApprovalPolicy`, which wraps the S5 decision without ever
dispatching (module docstring, lines 5-7).

#### 2.11.3 Earned, not authored

No distillation, promotion or demotion path exists.

### 2.12 Process topology, seams and performance

**Three processes at Phase 0** is realised: controller (Python, one process), worker (bubblewrap child, UID
10001), evaluator (daemon, UID 10002). Verified at the container level by `containers/worker.Dockerfile` and
`containers/evaluator.Dockerfile` plus `containers/manifest.json`, checked by
`tools/check_backend_artifacts.py --release`.

| Seam | As-built |
|---|---|
| Daemon ↔ clients | `runtime/service/server.py` — Unix domain socket, NDJSON frames; `RuntimeService.execute_command` (`service.py:94`) dispatches `StartRun`, `GetRun`, `ResolveApproval`, `Cancel`, `RecordCorrection`, `Checkpoint`, `Resume`, `ExplainArtifact`, plus `stream_events` (line 345) |
| Daemon ↔ systems components | subprocess + NDJSON: `adapters/sandbox/worker.py` (242 lines), `adapters/evaluators/daemon.py` / `client.py` |
| Daemon ↔ laboratory | Versioned exported artefacts: `adapters/stores/ledger_jsonl.py`, `tools/export_coding_session.py`, `lam.sqlite` traces read by `lab/bench.py` |

**Emergent, undocumented in theory — the transactional inbox/outbox.**
`runtime/service/inbox.py:14 ServiceInboxStore` is a SQLite-WAL store with two tables, `command_inbox`
(idempotency-keyed, line 30) and `event_outbox` (per-run monotonic `seq`, line 46). `record_command`
(line 69) returns `(is_new, prior_receipt)` so a replayed command returns its earlier receipt rather than
re-executing. This is `ADR-0062`'s mechanism and it has no VG-03/VG-04 counterpart — it is a **second
sequence-allocating store** alongside `EventStorePort`.

Performance levers: prompt caching is implemented (§2.10.2); parallel reads are not; model tier routing is
implemented as `runtime/tier_escalation.py:130 TierLadder` + `runtime/model_selection.py`; operator isolation
does not exist; result eviction exists. Latency instrumentation (`T6.8`) lives in `tools/telemetry/runner.py`
and `runtime/telemetry.py`.

### 2.13 The transparency surface

No inspector exists in the backend (the CLI is out of scope). What the backend provides as the data behind one:

| Spec surface | As-built |
|---|---|
| Layered prompt with per-block source and breakpoint positions | `CompiledContext.bundle()` (`layers.py:203`) carries layers, blocks, breakpoints, digests |
| Provenance colouring | `Block.provenance` (`layers.py:123`) |
| Per turn: request, reply, effects, cost, latency, cache-hit | `runtime/session_log.py` (220 lines) + `domain/ledger/coding_session.py:42 project_coding_session` + `runtime/scoring.py` (128 lines) |
| Decisions: which policy rule granted/denied, where the budget bit | `AuthorizationDenied` payload carries `requested`/`grantable`/`untrustedSpans` (`dispatch.py:197-200`); `BudgetReleased` carries `dimension`/`requested`/`remaining` (`dispatch.py:231-233`) |
| Parallel branches | No counterpart |
| Memory | No counterpart |
| Replay | `adapters/models/cassette.py` (190 lines) + `runtime/determinism.py` (injected clock and RNG so event ids are reproducible, lines 1-9) |

`AT-03` (client holds no adapter handle) is enforced by the `"client": {"domain","runtime"}` row only.

### 2.14 Failure taxonomy (`FT-01` … `FT-17`)

`FT-*` identifiers appear **nowhere** in `vanguard/packages/`. Mechanism-by-mechanism:

| # | Mechanism present? | Evidence |
|---|---|---|
| `FT-01` | Yes | `RunTermination.INSTRUMENT_ERROR`; `runtime/root.py:922 _instrument_error()` returns `"model_not_invoked"` when no turn reached the ledger |
| `FT-02` | Yes | `Episode.repeats` (`state.py:226`) |
| `FT-03` | Yes | `BudgetDenied` names the dimension |
| `FT-04` | Yes | `finally` release; `F-24` raises `KernelAlarm` (`dispatch.py:93`) |
| `FT-05` | Yes | `GrantIssuer.verify` compares `descriptor_digest` and `expires_at` (`grants.py:188-219`) |
| `FT-06` | Partial | `authority_violation` exists; the production span set is not fed (see §4.7) |
| `FT-07` | Yes (static) | boundary rule + `MF-S0-005`; `IsolatedEvaluator._probe_immutability` / `_probe_non_pollution` |
| `FT-08` | Yes | `git.py` diff is the only patch path |
| `FT-09` | Vacuous | no ranker exists |
| `FT-10` | Partial | `MF-CTX-001` catches a bypassed compiler; `MF-TEL-001` catches synthetic timing |
| `FT-11` | Yes | brief exempt from compaction |
| `FT-12` | Partial | `StructuredConsolidateStrategy` exists, not default |
| `FT-13` | Yes | assembly-time breakpoint check |
| `FT-14` | No | no concurrency |
| `FT-15` | Yes | `F-22` / `Occurrence.UNDETERMINABLE` |
| `FT-16` | No | `ConflictDetected` never emitted |
| `FT-17` | Yes | `ALERTABLE` frozenset (`kernel/model.py:150-155`) includes `DENIED_SCOPE_ESCALATION`; the event carries `alertable=True` |

**Emergent, undocumented in theory — a named-cause taxonomy.** `runtime/outcome_labels.py` (65 lines) plus
`runtime/repair.py:28 StopReason` and `runtime/provider_health.py` define a parallel failure vocabulary the
theory does not model: `inconclusive:workspace_missing`, `inconclusive:precondition_satisfied`,
`inconclusive:no_intervention`, `inconclusive:model_not_invoked`, `inconclusive:instrument_error`,
`inconclusive:no_verdict` (the six guarded by `MF-S7-C-02-001`…`006` in `test/broken/manifest.json`).

---

## 3. Core Contracts & Wire Schema (VG-04)

`schemas/v4/` holds **38 artefacts**: 15 writer schemas with 15 generated `.reader.` counterparts, plus
`MANIFEST.md`, `README.md`, `port-interfaces.md`, `model_proposal.schema.json`,
`runtime-service.schema.json`, `worker_protocol.schema.json`, `approval-decision.schema.json` and a
`vectors/` directory. The in-tree Python reader profile is `domain/wire/contracts.py` (362 lines).

### 3.1 Source of truth and wire conventions (`CT-01` … `CT-13`)

`domain/wire/contracts.py:355 parse_wire(kind, value)` is the reader entry point, dispatching through
`_PARSERS` (line 340) over ten kinds: `EffectDescriptor`, `CapabilityGrant`, `Receipt`, `EventEnvelope`,
`Artifact`, `EvidenceClaim`, `CorrectionRecord`, `Recording`, `ProcessDefinition`, `ProcessInstance`.

| # | As-built |
|---|---|
| `CT-01` | Schemas exist and are validated in CI. **The Python types are hand-written, not generated** — `contracts.py` is a hand-authored validator, and `domain/ledger/events.py:106 EventEnvelope` is a hand-written dataclass |
| `CT-02` | **Not held for Python.** `tools/reader_profile.py` generates the reader `.json` profiles from writer schemas; it does not generate Python types |
| `CT-03` | Held at the reader: `parse_wire` validates and returns `deepcopy` (line 363); `kernel/dispatch.py:410 _validate` is the S1 parse. `tools/check_boundaries.py` has no cast lint (`AT-10` unimplemented) |
| `CT-04` | Held by construction — JSON only |
| `CT-05` | Enforced per-field: `_parse_effect` filters `None` (`grants.py:56-59` for descriptors); optional fields are `if field in source` throughout |
| `CT-06` | Held: `Constraints.budget_usd_micros: int` (`attenuation.py:53`); `runtime/coding_budget.py:1-5` states integer microdollars, 1 USD = 1,000,000 |
| `CT-07` | Held: `Reservation.millis: int` (`budget.py:47`); `runtime/telemetry.py:1-9` — "Every quantity … is an integer or absent. No float is ever the truth" |
| `CT-08` | Held: `_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")` (`primitives.py:72`), with leap-year validation (`_check_timestamp`, line 86) |
| `CT-09` | Held: `_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")` (`primitives.py:73`) |
| `CT-10` | Held: every enum in the tree is a `str, Enum` or a literal tuple |
| `CT-11` | Held: `parse_wire` returns a lossless `deepcopy` including unknown fields (`contracts.py:363`); writer strictness lives in `schemas/v4/*.schema.json` (`additionalProperties: false`) |
| `CT-12` | Held by `_array`/`_object` helpers (`contracts.py:32,26`) |
| `CT-13` | Not explicitly checked; no lone-surrogate guard exists |

Canonicalisation: `domain/canonicalisation/jcs.py` (226 lines) implements RFC 8785 with a
`CanonicalisationError`; `digest.py:? digest_of` wraps it. `utf16_sort_key` is used for member ordering
(referenced at `selectors/resource_selector.py:288`). Golden vectors live in `schemas/v4/vectors/`, exercised
by `test/contracts/t1_dev1_canonicalisation.py`.

Large integers: `_INT_STRING = re.compile(r"^(0|[1-9][0-9]*)$")` (`primitives.py:74`) with
`int_string_to_int` / `int_string_from_int` (`primitives.py:228,235`). Matches the spec's `IntString` regex
exactly.

Naming: wire fields are `camelCase`; Python symbols are `snake_case`; event kinds are past-tense verb phrases
throughout `EVENT_KINDS` (`events.py:53-101`) — held.

### 3.2 Primitives and branded identifiers (`CT-14` … `CT-16`)

`domain/primitives/primitives.py` (257 lines). `Primitive` (line 56) is a frozen wrapper;
`parse(kind, value)` (line 194) dispatches through `_CHECKERS` (line 163). `_ID_KINDS` (line 157) enumerates
the branded identifier kinds; convenience parsers exist for `Digest`, `Timestamp`, `PrincipalId`, `EpisodeId`
(lines 209-227).

| # | As-built |
|---|---|
| `CT-14` | Held: `_UUIDV7` regex (`primitives.py:75-78`) and a generator `uuidv7(timestamp_ms)` (line 249). `seq` carries causal order as an `IntString` on the envelope (`events.py`, `contracts.py:212`) |
| `CT-15` | **Inverted at the descriptor.** `grants.py:56-58 descriptor_of` explicitly *excludes* `toolCallId`, `callId`, `requestId` — correct for `D-3`. There is no code path that stores or echoes a provider-assigned `ToolCallId` verbatim, so the "never regenerated" half has no counterpart |
| `CT-16` | Held: `EventEnvelope` requires `principal`, `tenantId`, `ownerId` from the first version (`contracts.py:205-211`); `dispatch.py:417` rejects a missing principal as `"principal is required (CT-16)"` |

**Emergent, undocumented in theory:** `principalRole` is a **required** envelope field with a six-value enum
`{user, operator, episode, process, evaluator, release}` (`events.py:50 VALID_PRINCIPAL_ROLES`;
`contracts.py:216`). This is `T2.1`'s principal model promoted onto the wire; VG-04 §12.1 has no such field.

### 3.3 Content addressing and blobs (`CT-17` … `CT-20`)

`ports/blob_store.py:25 BlobStorePort` — `put(bytes) -> Result[str]`, `get(digest) -> Result[bytes]`,
`has(digest) -> bool`. Two implementations in `adapters/stores/blob_store.py` (89 lines): in-memory and
on-disk content-addressed.

| # | As-built |
|---|---|
| `CT-17` | Held — addressed by digest of bytes |
| `CT-18` | **Not implemented.** There is no atomic event+blob commit and no staging/reconciliation between the two stores; they are independent ports |
| `CT-19` | **Not implemented.** `BlobStorePort` has no classification parameter and no encryption hook. Classification lives only on the event envelope (`confidentiality`) |
| `CT-20` | Held by construction |

### 3.4 Provenance — six orthogonal axes (`CT-21` … `CT-23`)

**Major shape divergence.** The spec's six orthogonal axes (`origin`, `instructionAuthority`, `integrity`,
`confidentiality`, `epistemic`, `influence`) are split across three unrelated places, and no single type
carries six axes.

| Spec axis | As-built |
|---|---|
| `origin` | Wire `provenance` object (`contracts.py:103-111 _provenance`) and `Span.source_class` (`kernel/model.py:80`) |
| `instructionAuthority` | `kernel/model.py:40 Trust` — a **single ordered five-value enum** (`OPERATOR` 0, `SYSTEM` 1, `AGENT_DERIVED` 2, `UNTRUSTED_DERIVED` 3, `UNTRUSTED_EXTERNAL` 4, ranks at lines 66-72). Its docstring states it "is not a general lattice … this is the instruction-authority axis alone" |
| `integrity` | No enforcing type |
| `confidentiality` | Envelope field only: `VALID_CONFIDENTIALITIES = {public, internal, confidential, restricted}` (`events.py:46`) |
| `epistemic` | **No counterpart.** The six-value lattice (`observed`, `derived`, `hypothesised`, `corroborated`, `contradicted`, `retracted`) appears nowhere |
| `influence` | **No counterpart** |

`T2.9`'s four-axis rename (`origin`, `integrity`, `sensitivity`, `trust`) is also not literally present;
`Trust` is the only enum. This resolves contradiction `X-05` toward a **fifth** shape: one ordered trust enum
plus separate envelope classification fields.

| # | As-built |
|---|---|
| `CT-21` | **Not held by type signature.** `agency/context/layers.py:89 Fragment(source, label, text)` accepts a raw `str`; `blocks_of(layer, fragments)` (line 229) turns them into `Block`s. Provenance is attached by the constructing call site |
| `CT-22` | Held in `kernel/`: `Span` is constructed with its trust; `Accumulation.extend` will only lower a label on re-entry (`provenance.py:60-68`). Not held in the production wiring (§4.7) |
| `CT-23` | **Not enforced.** `runtime/root.py:1210 _operator_span()` returns a literal `Span("brief-1", Trust.OPERATOR, "operator_brief")` at a call site; there is no per-source-class label registry |

### 3.5 Context blocks and epistemic state

`agency/context/layers.py:105 Block` is the unit of assembly and carries `source`, `label`, `text`, `layer`,
`evictable`, with `provenance` (line 123) and `identity` (line 134) properties, `byte_length` (line 115) and
`token_estimate` (line 119). It does **not** carry an epistemic state — the axis does not exist in code.

### 3.6 Capabilities and effect descriptors

#### 3.6.1 Why a verb set is insufficient

Held: `Scope` (`kernel/attenuation.py:95`) carries `actions` **and** `resources` **and** `constraints`, and
`attenuate()` checks all three plus depth.

#### 3.6.2 The grant

`domain/selectors/resource_selector.py:49` declares the **VG-04 selector kind set exactly**:

```python
SELECTOR_KINDS = ("fs", "network", "secret", "git", "table", "browser", "generic")
```

The GTS-13C `T1.3` kinds (`path`, `glob`, `command`, `host`, `record`) are **not** in the parser — resolving
contradiction `X-06` in VG-04's favour at the domain layer. However, the shipped manifests use both worlds:
`vg-code-default/manifest.json` declares `{"kind":"fs","root":"/workspace","paths":["/workspace"]}` (VG-04
shape) for `fs.read`/`fs.search`/`patch.apply`, and `{"kind":"generic","uriPattern":"proc://exec/allow/git,pytest,ruff,python3"}`
for `proc.exec` — an allowlist encoded inside a `generic` URI string rather than a `command` selector.

Two distinct `CapabilityGrant` shapes exist:

**In-kernel** — `kernel/grants.py:62 Grant`:
```
grant_id, principal, descriptor_digest, scope: Scope, expires_at, purpose_digest,
single_use=True, parent_grant_id=None, authenticator=None, approval_ref=None
```

**On the wire** — `domain/wire/contracts.py:147 _parse_grant`, required fields:
`grantId, principal, descriptorDigest, actions, selector, constraints, expiry, maxUses, purposeDigest`;
optional `parentGrantId`, `approvalRef`, `authenticator`; `constraints` requires `budgetLeaseId` and
optionally carries `maxBytes`, `maxEffects`, `environmentSnapshot`, `networkPolicy` (`deny|allowlist`),
`requirePreview`, `requireApprovalAboveRisk`.

The wire shape is a **merge** of VG-04 and `T1.5`: it keeps `actions` (plural, VG-04) and `purposeDigest`
(VG-04, required by `N-03`) while using a **singular** `selector` (`T1.5`) rather than `resources[]`. This is
a third resolution of `X-07`. `discloseToModel: false` is a literal on the `secret` selector
(`resource_selector.py:288`) but it is a normal Python bool, not a type-level literal.

`CT-51` is enforced at construction: `GrantIssuer.issue` raises `MissingDescriptorBinding` on an empty
`descriptor_digest` (`grants.py:158-162`) **and** on an empty `purpose_digest` (lines 163-166).
`descriptorDigest` is computed at S3 (`dispatch.py:159`) and verified at S8 (`dispatch.py:267-276` →
`grants.py:207-212`). `MF-KRN-003` fails against a grant that omits or bypasses the binding.

#### 3.6.3 Attenuation rules (`CT-24` … `CT-28`)

| # | As-built |
|---|---|
| `CT-24` | Held: `AttenuationDenied(dimension, requested, grantable)` (`attenuation.py:112-119`) |
| `CT-25` | Held with an explicit source comment at `attenuation.py:150` — "the grantable subset is *reported*, never substituted" |
| `CT-26` | Held: `HmacAuthenticator` (`grants.py:93`); `issue(cross_process=True)` refuses without one (`grants.py:178-182`); `verify` fails `F-17 GRANT_FORGED` (`grants.py:196-201`) |
| `CT-27` | Held: `dispatch.py:218` — `single_use=request.idempotency_key is None` |
| `CT-28` | Held negatively: there is no fixed TTL constant. `expires_at` comes from `granted_scope.constraints.expires_at` (`dispatch.py:215`) |

#### 3.6.4 Selector inclusion (`CT-52`)

**Implemented per-kind and fully.** `domain/selectors/resource_selector.py` (450 lines):
`parse_selector` (line 258), `canonicalise_selector` (line 373), `_includes_parsed` (line 383),
`decide(parent, child) -> Decision` (line 431), `includes(parent, child) -> bool` (line 448).

| Kind | Implementation |
|---|---|
| `fs` | Same root + normalised prefix match: `_normalise_path` (line 96), `_normalise_root` (line 119), `_path_under` (line 328), `_prune_paths` (line 336) |
| `network` | `_normalise_host` (line 129) with IDNA/lowercasing, `_host_covers` (line 341) implementing the wildcard rule, `_normalise_port` (line 154), `_prune_hosts` (line 362) |
| `secret` | Literal ref subset; `discloseToModel` forced `False` at parse (line 288) |
| `git` | `_expand_ref` (line 197) full-ref expansion |
| `table` | `_parse_range` (line 207), `_range_contains` (line 230), `_render_range` (line 226), `_prune_ranges` (line 367) — interval containment |
| `browser` | `_normalise_origin` (line 166), exact scheme/host/port equality |
| `generic` | Literal `uriPattern` equality |

`decide()` is total and denies undefined and cross-kind pairs — the `K-48` fail-closed requirement. Consumed
by `kernel/attenuation.py:140-155`, `kernel/classifier.py:121-122`, and `kernel/attenuation.py:199
resource_subset`. Property-tested in `test/contracts/t1_dev1_selectors.py`.

#### 3.6.5 Execution capabilities

`ports/sandbox.py:38 ContainmentReport` and `:57 SandboxReceipt` carry the perimeter facts.
`adapters/sandbox/rootless.py:199 execute()` builds the report from real probes (line 211) and sets
`visibility_mark` to `"probe-verified-rootless"` or `"unverified-rootless-perimeter"` (line 233).
Environment-variable **keys not values** and the redacted-output requirement are handled in
`adapters/sandbox/worker.py`. The spec's full receipt field list (image digest, normalised argv, working
directory, mounts, network policy, resource limits, exit/cancellation/timeout, containment runtime) is
substantially present via `ContainmentReport` fields `syscall_profile`, `startup_probes`, `visibility_mark`
plus runtime/version (line 187 `_runtime_version`).

#### 3.6.6 The effect descriptor and normalisation (`D-1` … `D-6`)

`kernel/grants.py:46 descriptor_of(action, args)`:

```python
normalised = {k: v for k, v in args.items()
              if v is not None and k not in ("toolCallId", "callId", "requestId")}
return digest_of({"action": action, "args": normalised})
```

| # | As-built |
|---|---|
| `D-1` | Held — `digest_of` canonicalises via JCS |
| `D-2` | **Not in `descriptor_of`.** Path normalisation happens in `domain/selectors/resource_selector.py:96 _normalise_path` (selectors) and `adapters/models/invocation.py:268 _workspace_relative` (proposal translation), not on the descriptor's args |
| `D-3` | **Held explicitly** — the three call-identifier keys are dropped. Guarded by `MF-28` in the spec map (no in-tree test of that ID; the behaviour is covered by `test/kernel/test_dispatch.py`) |
| `D-4` | Held — no trimming or case-folding |
| `D-5` | Held — `v is not None` filter |
| `D-6` | Held via JCS number canonicalisation (`jcs.py`) |

The wire `EffectDescriptor` (`contracts.py:126`) is a **different, richer shape** than the kernel's descriptor
digest: `{verb, sinkClass, selector, args, argsDigest, idempotencyKey, riskTier, provenance}` plus optional
`workingDirectory`, `readSet`, `writeSet`. The reader recomputes `digest_of(args)` and rejects a mismatched
`argsDigest` (lines 134-136). Note the field is `verb`, not `name`/`action`; the kernel's `EffectRequest` uses
`action` (`kernel/model.py:87`) and `ports/environment.py:90 EffectRequest` uses **both** `verb` and `action`.

### 3.7 Budgets, reservations and leases (`CT-29` … `CT-32`)

`kernel/budget.py:44 Reservation` has **four** dimensions: `usd_micros`, `millis`, `tokens`, `bytes_`.

Neither spec vector matches: VG-04 §6 names cost, tokens, wall-clock, turns, depth, concurrency;
GTS-13C names `{tokens, wallClock, cost, effects, evaluations, depth}`. As built, **`turns` and `depth` are
enforced outside the `Reservation`** (turn ceiling in `EpisodeEngine._max_turns`; depth in
`Constraints.max_depth`), and `concurrency`, `effects` and `evaluations` are absent. There is **no
`EvaluationBudget`** — `CT-32` has no counterpart.

| # | As-built |
|---|---|
| `CT-29` | Partial: `Lease.lease_id` exists and `parent_lease` is carried on `EffectRequest`, but the emitted `EffectCompleted` payload carries `settlement`, not the lease id (`dispatch.py:361-366`). The wire `Receipt` (`contracts.py:176`) has no lease field at all — matching spec ambiguity `Y-04` |
| `CT-30` | Held: `BudgetDenied(dimension, requested, remaining, reason)` |
| `CT-31` | Held: `Governor.commit` retains negative settlement (`budget.py:145-149`) |
| `CT-32` | **Not implemented** |

`Governor.ledger()` (`budget.py:96`) exposes `{ceiling, spent, held, remaining}` per dimension, and
`test/kernel/test_dispatch.py:321 test_ceiling_is_conserved_across_many_effects` asserts conservation.

**Emergent, undocumented in theory:** `runtime/coding_budget.py` (243 lines) is a **second budget
controller** — a hard pre-call worst-case reservation in integer microdollars for paid model calls, sitting
above the kernel `Governor` and outside the dispatch sequence. Its docstring states it "Never represents
unknown pricing or missing usage as zero."

### 3.8 Tools

A tool declares name, required capability, argument schema, read set and write set. As built, a tool is a
JSON artefact in a manifest pack — e.g. `agency/manifests/vg-code-default/read-tool.json`,
`search-tool.json`, `patch-tool.json`, `test-tool.json`, and `vg-shell-only/shell-tool.json`. The manifest's
`capabilities[]` rows carry `{verb, sink, selector, risk}` (`vg-code-default/manifest.json`).

`readSet`/`writeSet` are **schema-optional and unconsumed** (§2.7). There is **no commutativity flag**
anywhere — `AT-05` and `REJ-05` are held by absence.

**Emergent, undocumented in theory:** `adapters/models/invocation.py:33 ProposalTranslator` (384 lines total)
maps a provider tool-call into a canonical `EffectRequest`. It is **schema-and-selector driven, not a verb
table** (`docs/scrum/roadmap_backend.md:30`, `S10-A-01`, commit `854e8e8`): `_selector_from_schema`
(line 319), `_bind_resource` (line 337), `_is_canonical_verb` (line 289), `_workspace_relative` (line 268),
`validate_proposal_schema` (line 217), `_within_depth` (line 258). Each manifest pack carries an
`aliases.json` mapping provider-facing tool names onto canonical verbs. This whole layer — provider tool name
→ alias → canonical verb → selector-bound resource — has no VG-04 counterpart.

### 3.9 The model interface (`CT-33` … `CT-34`)

`ports/model.py:30 ModelPort` — `propose(ContextBundle, ToolSchemas, Sampling) -> Result[Proposal]`, matching
GTS-13C §5.2's `ModelPort` name and signature rather than VG-04's `ModelProvider`.

| # | As-built |
|---|---|
| `CT-33` | Held at the port: every adapter returns `Result` (`ports/event_store.py:37`), and `Result.fail(kind, message, retryable)` (line 49) carries the error kind. Belt-and-braces at the caller: `engine.py:228-234` catches a raising provider and still terminates as `INSTRUMENT_ERROR` |
| `CT-34` | Held — adapters raise only on programmer error |

Adapters: `openrouter.py` (896), `ollama.py` (137), `lam.py` (120, deterministic mock), `fake.py` (38),
`cassette.py` (190, record/replay), plus `routing.py` (154) and `env_loader.py` (121).
`runtime/model_selection.py:1-9` records the *skip-closed vs skip-as-pass* distinction: a backend that is not
there produces a named `instrument_error`, never a skipped test reporting success.

### 3.10 Task, plan, proposal, effect request

| Spec type | As-built |
|---|---|
| `TaskSpec` | **No wire type.** `runtime/root.py:189 TaskContext` is the application value; `EpisodeStarted` payloads carry a `taskSpec` mapping by convention only |
| `PlanArtifact` | **No wire type.** `runtime/coding_plan.py` (223 lines) holds a runtime-owned, validated plan; its docstring: "a model can propose an `implemented` step, but only an exterior verifier may move it to `verified`" |
| `Proposal` | Two: `ports/model.py Proposal` (the port's return) and `agency/episode/state.py:86 Proposal` with `ProposalKind` (line 63) `{effect, finish, abstain, escalate, spawn}` and `parse_proposal` (line 107) |
| `EffectRequest` | **Three distinct types with the same name** — `kernel/model.py:87` (action/resource/args/principal/run_id/depth/justifying_spans/parent_lease/declared_sink_class/idempotency_key), `ports/environment.py:90` (verb/action/args…), and the wire `EffectDescriptor` |

`ProposalKind.SPAWN` and `ESCALATE` are additions over the spec's `finish`/`abstain`.
`TERMINAL_FOR_KIND` (`state.py`) maps non-effect kinds directly to terminals.

Step-level attribution — "which operator produced which proposal" — is **not recorded**: the
`ProposalProduced` payload (`engine.py:448-459`) carries the descriptor and action but no operator identity,
because no operator identity exists.

"An operator receives no effect capabilities by default" is realised at the episode level:
`EpisodeEngine.spawn` fails closed when the child scope is missing or unparseable (`engine.py:263-286`) rather
than inheriting the parent's grant.

### 3.11 The competence and evidence graph

#### 3.11.1 Why a graph

**Not implemented as a competence graph.** `domain/artifacts/graph.py:85 ArtifactGraph` is a *harness
composition* graph — `ArtifactKind` (line 29), `KindRegistry` (line 39), `ArtifactFile` (line 65),
`LogicalEdit` (line 142), `Commit` (line 156), `Workspace` (line 165). It answers "which files compose this
harness pack", not "which competence artifacts contradict which".

There is no contradiction search, no partial supersession, no per-domain activation, no quarantine, and no
lineage-preserving forgetting anywhere in `vanguard/packages/`.

The four quadrants (`R`/`O`/`M`/`P`) do not appear. The live kind set is `BUILTIN_KINDS`
(`domain/artifacts/graph.py:19`) / `agency/manifests/kinds.json` — 17 rows.

#### 3.11.2 The contracts

**`CompetenceArtifact` does not exist.** The wire `Artifact` (`contracts.py:231 _parse_artifact`) is the
`T1.8` shape, not the VG-04 shape:

```
required: artifactId, kind, class, hypothesis, evidenceRefs,
          invalidationConditions, riskDelta, contentDigest
class ∈ {enforcement, compensation};  compensatesFor required iff compensation (lines 236-240)
contentDigest must bind the immutable content (lines 245-250)
```

Absent VG-04 fields: `artifactVersion`, `body: BlobRef`, `interfaceSchema`, `createdBy`, `createdFrom`,
`dependencies`, `supersedes`, `createdAt`. Present non-VG-04 fields: `class`, `compensatesFor`, `hypothesis`,
`riskDelta` (this is `L-12`).

**`EvidenceClaim` exists in two forms.** Wire: `contracts.py:252 _parse_claim` requires
`id, subject, predicate, value, protocol, evaluator{evaluatorId,class,imageDigest}, environmentProfile,
substrateProfile, taskDistribution, uncertainty, validity{domains[]}, invalidationConditions`.
Domain: `domain/evidence/claim.py:159 Claim` with `InvalidationCondition` (line 85), `Evaluator` (line 108),
`Uncertainty` (line 122), `Validity` (line 145), parsed by `parse_claim` (line 322).
Domain `Claim` **does** carry optional graph/hedge fields: `evidence_refs`, `derived_from`, `contradicts`,
`expires_at` (lines 174-177) plus `support_count`, `last_corroborated_at`, `protection_class` (lines 179-182).
`to_wire` emits the first four only when non-empty (`claim.py:219-225`). Wire `_parse_claim` does **not
require** them (`contracts.py:254`) — they are optional / unknown-field-preserved, not absent from the domain type.

`ADR-0068` hedge fields (`supportCount`, `lastCorroboratedAt`, `protectionClass`) are carried by the writer
schema (`schemas/v4/evidence-claim.schema.json`, golden vector `hedge-fields.json` per
`docs/scrum/roadmap_backend.md:36`) and pass through the reader as unknown-field preservation. They are
recorded and never consumed — held.

**Typed edges** (`derived_from`, `requires`, `supersedes`, `contradicts`, `evaluated_by`, `valid_under`) and
**states** (`candidate`, `active`, `quarantined`, `deprecated`, `retired`) have **no counterpart**.

#### 3.11.3 Invalidation conditions (`INV-1`, `INV-2`)

`InvalidationCondition` (`domain/evidence/claim.py:85`) carries `condition`, `checkKind`, optional `checkRef`.
Both invariants are enforced **at parse**:

- `INV-1`: `_invalidation(value, path)` (`contracts.py:113`) calls `_array(..., nonempty=True)`; an empty
  array raises `WireError("minItems", ...)`. Same in `claim.py:235 _parse_conditions`.
- `INV-2`: `contracts.py:120-124` — `checkKind == "automatic"` requires `checkRef`, validated as an
  `EvaluatorId`.

`InvalidationCheckRecord` has a writer + reader schema (`schemas/v4/invalidation-check-record*.json`) — the
`CT-53` separation of mutable check state from the content-addressed artifact — but **no producer and no
consumer in `vanguard/packages/`**. Nothing ever runs an invalidation check.

#### 3.11.4 Lifecycle rules (`CT-35` … `CT-39`, `CT-53`)

| # | As-built |
|---|---|
| `CT-35` | Held at the type: `Artifact` has no status field, and `contentDigest` must bind the content (`contracts.py:245-250`) |
| `CT-36` | `ArtifactRegistryProjection` (`runtime/ledger/projections.py:300`) tracks activation from events; retirement is a projection state, lineage is the ledger. But no `ActivationChanged` is ever emitted |
| `CT-37` | No quarantine state exists |
| `CT-38` | No expiry mechanism exists |
| `CT-39` | Vacuous — no versioning exists |
| `CT-53` | **Held and tested at the type.** `_parse_artifact` recomputes `digest_of(content)` over a fixed key set that excludes any mutable field (`contracts.py:247-250`), and check state lives in a separate schema |

### 3.12 The instrument tuple (shape)

**Not in `vanguard/packages/`.** Implemented at `tools/telemetry/tuple.py` (248 lines) with
`tools/telemetry/coding_instrument.py` (69 lines). Tested by `test/lab/test_tuple.py` and
`test/benchmarks/test_instrument_tuple.py`. See §6.5.4.

The closest backend artefact is `ports/sandbox.py:38 ContainmentReport`, which `K-45` requires to be part of
the tuple; there is no code path that composes a containment report *into* an instrument tuple.

### 3.13 The event stream

#### 3.13.1 The envelope

`domain/ledger/events.py:106 EventEnvelope` (dataclass) and `contracts.py:206 _parse_event` (reader).
Required wire fields: `schemaVersion` (const `"vg.4"`, line 211), `eventId` (UUIDv7), `scope`, `traceId`,
`spanId`, `seq` (IntString), `occurredAt`, `recordedAt`, `principal`, **`principalRole`**, `tenantId`,
`ownerId`, `confidentiality`, `retentionClass`, `trainability`, `redactionStatus`, `payload`.

The `scope` discriminator is implemented with **full conditional enforcement in both directions**
(`contracts.py:219-226`):
- `episode|recovery` require `runId`; `episode` requires `episodeId`;
- `governance|evolution` may **not** carry `runId`; anything but `episode` may not carry `episodeId`.

This is `MF-35`'s property ("an evolution event forced to carry a synthetic run identifier") enforced at parse.

Differences from VG-04 §12.1: `principalRole` is added (see §3.2); `branchId` and `parentEventId` are absent;
`encryptionKeyRef` and `environmentSnapshot` are not required and not present in the dataclass.
`processId` (the `T1.7` field) is **not** an envelope field — process association is by
`payload.processId` (`runtime/governance/engine.py:19-22`), which is a convention, not a contract.
This resolves `X-08` toward VG-04 with one addition and two omissions.

The four projections the spec requires a single stream to serve are partly realised:
`adapters/stores/ledger_jsonl.py:41 redact_envelope` with `RedactionPolicy` (line 32) produces the redacted
operational trace, preserving `traceId`/`spanId` correlation. Encrypted raw audit, content-free metrics and
the training projection have no code.

#### 3.13.2 The minimum event set

`EVENT_KINDS` (`domain/ledger/events.py:53-98`) contains **34** kinds — the same 34 named in THEORY §3.13.2
(the earlier "33" count was a miscount of that table). The frozenset is not closed against extras: see
`EffectRejected` / `KernelAlarm` below.

**The emitted set is far smaller.** Counting emitters in `vanguard/packages/` (excluding
`events.py`'s declaration and the reducer/projection *consumers*):

| Group | Emitted in production code? |
|---|---|
| `EpisodeStarted` | **No emitter** in `vanguard/packages/`. Declared, reduced (`reducer.py:93`), projected (`projections.py:76`). CLI fixtures invent the kind; the backend never writes it |
| `EpisodeCompleted` | Yes — `engine.py:427 _emit_terminal` |
| `EpisodeStateChanged` | **No emitter** (reduced at `reducer.py:104`, projected at `projections.py:79`) |
| `ObservationRequested`, `ObservationProduced` | **No emitter** |
| `OperatorSelected`, `OperatorInvoked` | **No emitter** (no operators exist) |
| `ProposalProduced` | Yes — `engine.py:448` |
| `AuthorizationRequested` | **No emitter** |
| `CapabilityGranted` | **No emitter** — the kernel issues a grant at S6 but emits no event for it |
| `AuthorizationDenied` | Yes — `dispatch.py:196` |
| `CapabilityRevoked` | **No emitter.** `GrantIssuer.revoke` (`grants.py:225`) returns the revoked ids "so the caller can emit one `CapabilityRevoked` per grant"; **no caller exists** |
| `BudgetReserved`, `BudgetCommitted` | **No emitter** |
| `BudgetReleased` | Yes — `dispatch.py:230` (denial path only) |
| `EffectPreviewed` | **No emitter** |
| `EffectStarted` | Yes — S8a intent, `dispatch.py:281` |
| `EffectCompleted` | Yes — `dispatch.py:355` |
| `EffectReconciled` | Yes — `dispatch.py:351` (`F-22` path); also `domain/ledger/reconciliation.py:74-77` |
| `ConflictDetected` | **No emitter** |
| `EvaluationRequested` | **No emitter** |
| `EvidenceClaimProduced` | **No emitter** |
| `ArtifactCreated`, `ActivationChanged` | **No emitter** |
| `CompetencePriorRecorded` | Yes — `agency/context/compiler.py:253-254` |
| `ApprovalRequested` | Yes — `dispatch.py:189` |
| `ApprovalResolved` | **No emitter.** `ApprovalFlow` (`approvals.py:296`) creates challenges and verifies decisions; `RuntimeService._cmd_ResolveApproval` (`service.py:222`) puts an `ApprovalDecision` on an in-process queue. Governance `ProcessEngine` **consumes** the kind (`engine.py:59`) but nothing in `vanguard/packages/` writes it |
| `Heartbeat` | **No emitter.** Consumed by `recovery.py:158`. CLI fixtures invent it. No HMAC/MAC (T-08 unmet) |
| `RunRecovered`, `RunAborted` | Yes — `runtime/ledger/recovery.py:175-208` |
| `CandidateBuilt`, `CandidateAttested`, `CanaryPromoted`, `RollbackTriggered` | **No emitter** — the Evolution plane has no runtime component |

Net: **11** `EVENT_KINDS` members are produced in `vanguard/packages/`; **23** are declared-only.

`AuthorizationDenied` carries reason, `requested`, `grantable` and `untrustedSpans`, and is flagged
`alertable` for members of `ALERTABLE` (`dispatch.py:196-202`) — held.
`CompetencePriorRecorded` is recorded before turn 1 reaches the provider (`root.py:513-519`) — held.

**Emergent, undocumented in theory — two event kinds the kernel emits that are not in `EVENT_KINDS`:**
`"EffectRejected"` (`dispatch.py:171, 345, 368`) and `"KernelAlarm"` (`dispatch.py:320, 342`). These reach the
store as `payload.kind` strings; `_parse_event` only requires `payload.kind` to be a *string*
(`contracts.py:229-230`), so nothing rejects them. `EVENT_KINDS` is imported by `domain/__init__.py` and used
only by `test/contracts/t3_ledger.py:22` — **the frozenset is not enforced anywhere in production code.**

#### 3.13.3 Storage (`CT-40` … `CT-43`)

| # | As-built |
|---|---|
| `CT-40` | Held: `adapters/stores/event_store.py:121 SqliteEventStore`, `PRAGMA journal_mode = WAL` (line 139), `synchronous` defaults to `"FULL"` (line 124), single-writer monotonic `seq` per run enforced in the transaction (lines 182-196) |
| `CT-41` | Partial: blobs are addressed by digest outside the DB (`adapters/stores/blob_store.py`). **No versioned migration mechanism exists** — no migrations directory, no schema-version column beyond the envelope field |
| `CT-42` | Held: `adapters/stores/ledger_jsonl.py` is export/import only; the primary store is SQLite. `MF-23` guards the inverse in the spec map (no in-tree test of that ID) |
| `CT-43` | Held: `ports/event_store.py:64 EventStorePort` with `read(range_query)` (line 71) and `digest()` (line 75); readers go through the port |

`InMemoryEventStore` (line 30) is the second implementation for `T10.2`.

#### 3.13.4 Recovery events

`Heartbeat`, `RunRecovered` and `RunAborted` are declared and reduced. **Only** `RunRecovered` /
`RunAborted` are produced, by `runtime/ledger/recovery.py:175-208 RecoveryScanner`. `Heartbeat` has **no
producer** in `vanguard/packages/` (consumed at `recovery.py:158`). `EffectReconciled` carries
`{"occurrence": "undeterminable"}` on the `F-22` path (`dispatch.py:351`) — the preserved-uncertainty
state, held. Heartbeats are **not** authenticated (T-08 unmet; HMAC exists for grants only).

### 3.14 Port interfaces (VG-04 §13)

**The port roster diverges substantially from both spec rosters.** Live inventory of
`vanguard/packages/ports/` (9 modules, 738 LOC), all `typing.Protocol`, several `runtime_checkable`:

| Module | Symbol | VG-04 name | GTS-13C name |
|---|---|---|---|
| `model.py:30` | `ModelPort` | `ModelProvider` ✗ | `ModelPort` ✓ |
| `environment.py:140` | `EnvironmentAdapter` | `EnvironmentAdapter` ✓ | `EnvironmentPort` ✗ |
| `evaluator.py:52` | `EvaluatorPort` | `EvaluatorPort` ✓ | `EvaluatorPort` ✓ |
| `event_store.py:64` | `EventStorePort` | `EventStore` ✗ | `EventStorePort` ✓ |
| `blob_store.py:25` | `BlobStorePort` | `BlobStore` ✗ | `BlobStorePort` ✓ |
| `index.py:42` | `IndexPort` | absent | `IndexPort` ✓ |
| `determinism.py:35,22` | `ClockPort`, `RandomPort` | absent | `ClockPort`, `RandomPort` ✓ |
| `sandbox.py:68` | `SandboxRunner` | `SandboxRunner` ✓ | absent |
| `kernel.py:38,46,64,71` | `Clock`, `EffectAdapter`, `EventSink`, `Ledger` | absent | absent |

**Absent from code entirely:** `OperatorRunner`, `ObservationSource`, `PolicyEngine`, `Governor` (as a port).
`Governor` exists only as a **concrete class inside the kernel** (`kernel/budget.py:71`), and policy is a
concrete `StandardPolicy` (`kernel/policy.py:56`) injected as `policy: Any` into `Kernel.__init__`
(`dispatch.py:104`) — a duck-typed seam with no declared interface.

**Emergent, undocumented in theory — `ports/kernel.py`.** Four kernel-facing protocols the spec does not
name: `Clock` (`now() -> str`), `EffectAdapter` (`name`, `healthy()`, `execute(request)`), `EventSink`
(`emit(event)`), `Ledger` (`append_intent(event)`). The split between `EventSink.emit` (never raises, `F-25`)
and `Ledger.append_intent` (must raise, `F-21a`) is load-bearing and is documented at
`runtime/root.py:413-423 LedgerBridge`.

**`SandboxRunner` returns a structured report, not a boolean** — held. `ports/sandbox.py:38 ContainmentReport`
plus `ProbeResult` (line 28), `SandboxReceipt` (line 57), `SandboxResult` (line 63), and a free function
`publication_decision(report) -> Result[None]` (line 75) that returns `Result.fail("denied", "unverified
containment report blocks publication")` when `not report.verified`. That is `K-44` as executable code.

### 3.15 Configuration schemas

Held. `domain/artifacts/manifest.py:105 parse_manifest` rejects unknown/ill-typed rows at authoring time
(`ManifestError`, line 11); `compose(manifest, graph, episode_id)` (line 143) resolves names against the
`ArtifactGraph` and freezes; `runtime/root.py:179 CompositionError` fails the composition, not the first use.
`agency/manifests/loader.py` (259 lines) loads packs; `discovery.py` (106 lines) handles between-run
workspace discovery.

Manifest schemas: `schemas/v4/harness-manifest.schema.json` + reader. Six packs ship:
`vg-code-default`, `vg-shell-only`, `vg-code-claude-shaped`, `vg-code-opencode-shaped`, `vg-code-swe-mini`,
`vg-table-default` — note `vg-table-default` exists on disk but is **not** in
`agency/manifests/registry.json`, which lists five.

### 3.16 Cross-language contract

Two implementations exist: Python (`domain/wire/contracts.py`) and TypeScript (`vanguard/packages/domain/contracts.ts`;
README cites a stale `domain/wire/` pair at `:222`; the TS tree is otherwise out of scope). Vectors are data in `schemas/v4/vectors/`,
exercised by `test/contracts/` (121 test methods) including `t1_wire_contracts.py`, `test_t1.py`,
`schema_subset.py` and a `readers/` subpackage.

Inter-process frame requirements (max size, request id, version negotiation, cancellation frame,
backpressure, separate diagnostics channel, content references, authenticated channel): partially realised in
`schemas/v4/runtime-service.schema.json` and `worker_protocol.schema.json`. Grants crossing a process boundary
are authenticated (`HmacAuthenticator`); approvals crossing one are Ed25519-signed
(`runtime/governance/approvals.py`); the evaluator channel uses SO_PEERCRED + image digest + Ed25519 verdict
signing. Backpressure and an explicit cancellation frame have no implementation.

### 3.17 Versioning and compatibility (`CT-44` … `CT-50`)

| # | As-built |
|---|---|
| `CT-44` | Held for **fields** — `parse_wire` deep-copies unknown fields. Held for **event kinds** only accidentally: `payload.kind` is any string, so an unknown kind is preserved because nothing validates it |
| `CT-45` | Held informally; no exhaustive matching on extensible enums (reducers use `if/elif` chains with implicit fall-through, e.g. `reducer.py:53-460`) |
| `CT-46` | **No migration mechanism exists** — no migrations package, no migration registry |
| `CT-47` | **No migration rehearsal in CI** |
| `CT-48` | Partial: `schemaVersion` is a hard const `"vg.4"` (`contracts.py:211-213`); an unknown version is rejected rather than accepted silently. Corpora do not record their derivation version |
| `CT-49` | Held by construction — `EVENT_KINDS` is append-only in practice |
| `CT-50` | No deprecation mechanism exists |

### 3.18 Conformance

| Kind | As-built |
|---|---|
| Vector conformance | `schemas/v4/vectors/`, `test/contracts/t1_dev1_canonicalisation.py`, `test/contracts/readers/` |
| Property tests | `test/contracts/t1_dev1_selectors.py` (selector inclusion reflexive/transitive), `test/test_ledger_properties.py`, `test/kernel/test_attenuation.py` |
| Round-trip tests | `test/contracts/t1_wire_contracts.py`, `test/contracts/test_t1.py` |
| Must-fail tests | 38 cases, `tools/run_broken_tests.py` (see §9.6) |

`test/contracts/` holds 121 test methods across 16 modules.

### 3.19 What locks here

The three locks are realised as: the corpus format (`domain/wire/contracts.py` + `schemas/v4/`), the wire
interface definition (`schemas/v4/*.schema.json`), and the seams (subprocess/NDJSON, UDS).

`schemas/v4/MANIFEST.md` exists and carries schema status. The operational rule ("a schema marked `DRAFT` may
not be used to record anything intended to survive") has **no code enforcer** — nothing reads `MANIFEST.md`
status at runtime, and the live SQLite ledger records against DRAFT schemas.

---

## 4. Policy Kernel, Capability Attenuation & Security Model (VG-05)

The kernel is nine files under `vanguard/packages/kernel/`: `__init__.py`, `attenuation.py`, `budget.py`,
`classifier.py`, `dispatch.py`, `grants.py`, `model.py`, `policy.py`, `provenance.py`. Logical TCB size is
**1,333** / alarm **1,438** (`tools/kernel-tcb-budget.json`: baseline 1,307 + 131). `tools/check_tcb_budget.py`
and must-fail `MF-KRN-011` enforce the tripwire.

### 4.1 Audit stance

`K-01` is a comment doctrine, not a single gate. Four assurance kinds as built:

1. **Architecture tests** — `tools/check_boundaries.py` plus kernel unit tests (`AT-08`/`AT-09` live; `AT-10`–`AT-12` do not).
2. **Must-fail tests** — 11 `MF-KRN-*` cases plus related `MF-S0-*` / `MF-SEC-*` (see §9.6). Spec IDs `MF-01`…`MF-37` are not the live harness IDs.
3. **Fault injection** — `test/kernel/test_dispatch.py` covers ordering and fail-closed exits; not every `F-nn` is injected there (F-14…F-17 live in `test/kernel/test_attenuation.py`).
4. **Adversarial audit of the verifier before a training run** — **no code**; no training run exists.

### 4.2 The trusted computing base

The *policy-kernel* ceiling is measured. The larger TCB (OS, bwrap, sqlite, `cryptography`, evaluator image,
identity) is **not** enumerated as a versioned declaration in `vanguard/packages/`. `K-02` is therefore held
for the kernel LOC tripwire and unmet as a dependency declaration.

#### 4.2.1 Mutability classes (`R0` … `R4`)

**No code counterpart.** There is no `R0`/`R1` table, no dispatcher pre-check rejecting those targets
(`K-03` **Absent**), and no closed adapter table keyed on mutability class. The closed adapter table that
does exist is `Kernel._adapters` (`dispatch.py:113`) populated at composition (`runtime/root.py` binding
table) — unknown actions fail at S2 (`F-02`), which is a weaker property than `K-03`.

### 4.3 The security claim `S1`

| Clause | As-built |
|---|---|
| (a) effect outside granted actions and resources | Held for privileged sinks via S5 + `attenuate()` + sealed membership (`policy.py:95-106`). Observation/pure sinks skip the grant (`classifier.py:92 requires_grant` only for `PRIVILEGED`) |
| (b) child outside parent | Held at `attenuate()`; child episodes get a parsed child `Scope` (`engine.py:263-286`) |
| (c) modify the verifier | Import-graph only (`AT-02` / `MF-S0-005`). No `AT-12` selector reachability check. Worker probe asserts evaluator path unreadability (`rootless.py` mount probe) |
| (d) exceed limits without debit | Held: `Governor.commit` retains negative settlement (`budget.py:145-149`) |
| (e) untrusted content authorises widening | Library held (`authority_violation`, `provenance.py:130-143`). **Production wiring is weak** — see §4.7 |
| (f) promote a claim without independent evidence | Vacuous — no promotion path exists |
| (g) reach runtime/config/keys/update | Vacuous for update (no updater). Keys live in env (`VANGUARD_EVALUATOR_VERDICT_PUBLIC_KEY`, approval keys). No capability resolver that names those paths |

There is **no** `Principal::EvidencePlane` ingress into `Kernel.dispatch`. Evaluators never import `Kernel`
or `EffectRequest`. Dual-ingress (`ADR-0061`) is spec-only; production effects enter only via
`EpisodeEngine` → `Kernel.dispatch`.

### 4.4 The dispatch sequence `S0` … `S12`

Implemented in `kernel/dispatch.py` (`Kernel.dispatch` `:127`, `_guarded` `:238`). Docstring at `:1-37`
matches the spec diagram.

| Stage | As-built |
|---|---|
| S0 ENTER | `EffectRequest` constructed by `EpisodeEngine._to_effect_request` (`engine.py:467-480`), not inside `dispatch` |
| S1 PARSE | `_validate` (`dispatch.py:139-142`, `:410-428`) |
| S2 RESOLVE | adapter lookup + `healthy()` (`:144-156`) — before any lease (`K-04`) |
| S3 DESCRIBE | `descriptor_of` (`:158-162`) |
| S4 CLASSIFY | `_classifier.widens_capability` (`:164-174`); exception → `F-05` fail-closed |
| S5 AUTHORIZE | `_policy.authorize` (`:176-202`) |
| S6 GRANT | `_issuer.issue` **only if** `requires_grant` (`:206-222`); observation/pure skip |
| S7 RESERVE | `_governor.reserve` (`:224-233`) |
| S8 VERIFY | inside `_guarded` (`:267-276`) |
| S8a INTENT | `_ledger.append_intent` (`:278-293`) before S9 (`K-47`) |
| S9 DISPATCH | `adapter.execute` (`:295-307`) |
| S10 COMMIT | `_governor.commit` (`:309-314`) |
| S11 RELEASE | `finally` (`:315-322`) |
| S12 EMIT | `_finish` after `finally` (`:324-328`, `:330-361`) |

Approval suspension (`F-08`) exits **before S6/S7** (`:187-193`) — `K-13`/`K-14` held.

#### 4.4.1 Ordering rules

| # | As-built |
|---|---|
| `K-04` | **Held** — S2 before S7 |
| `K-05` | **Held** — S8 inside `_guarded` after S7 |
| `K-06` | **Held** — S11 `finally` before S12 |
| `K-07` | **Held** — negative settlement retained |
| `K-08` | **Held** — classifier call, never a constant (`MF-KRN-001`) |
| `K-47` | **Held** — S8a before S9 |

#### 4.4.2 Failure paths (`F-01` … `F-25`)

`FailurePath` at `kernel/model.py:121-154` is the live table (26 members counting `OK` and `F-21a`).
`ALERTABLE` (`model.py:157-163`) is `{F-10, F-17, F-24, F-21a}`.

| ID | As-built |
|---|---|
| `F-01`…`F-05` | **Held** — returned from `dispatch` before the lease |
| `F-06` | **Partial** — fallback when `decision.failure` is unset (`dispatch.py:195`). `StandardPolicy` never sets `DENIED_REJECT` |
| `F-07` | **Held** — benchmark mode (`policy.py:126-127`) |
| `F-08` | **Held** — interactive approval (`policy.py:128-129`, `dispatch.py:191-193`) |
| `F-09` | **Held** in library — `authority_violation` (`provenance.py:130-143`, `policy.py:117-118`). Production span set is usually just the operator brief (see §4.7) |
| `F-10` | **Held** — attenuate deny + sealed-scope membership (`policy.py:88-106`) |
| `F-11` | **Held** — `MissingDescriptorBinding` / `ValueError` at issue (`dispatch.py:222`) |
| `F-12` / `F-13` | **Held** — `BudgetDenied` (`budget.py:115,119` → `dispatch.py:228-229`) |
| `F-14`…`F-17` | **Held** — `GrantIssuer.verify` (`grants.py:188-218`) |
| `F-18`…`F-21` | **Held** — `_failure_for` maps adapter status (`dispatch.py:403-406`) |
| `F-21a` | **Held** — intent append fail (`dispatch.py:291-292`); also emits `KernelAlarm` (`:341-343`) |
| `F-22` | **Held** — adapter exception → `UNDETERMINABLE` (`:300-306`) |
| `F-23` | **Held** — commit except (`:313-314`) |
| `F-24` | **Partial** — `raise KernelAlarm` (`:319-322`); never returned as `DispatchResult.LEASE_LEAK` |
| `F-25` | **Partial** — `_publish` swallows emit failure (`:380-386`); enum value is never returned |

**Divergence from spec text "F-24 is the only kernel alarm":** `KernelAlarm` is also emitted on `F-21a`
(`dispatch.py:341-343`) without raising. Class docstring at `:93-94` still says F-24 only.

`AT-09` exhaustiveness is asserted by `test/kernel/test_dispatch.py`.

#### 4.4.3 Idempotence and replay (`K-09` … `K-12`)

| # | As-built |
|---|---|
| `K-09` | **Partial** — S1–S8 are functions of request + kernel state; not proven as a replay property test |
| `K-10` | **Held** for grants — `single_use` when `idempotency_key is None` (`dispatch.py:218`) |
| `K-11` | **Partial** — resume reconstructs from the ledger (`test/runtime/test_resume_from_ledger.py`); grants are not reused across resume as a documented API |
| `K-12` | **Absent** as a recorded-replay bypass of S9. Cassette replay is a *model* adapter (`adapters/models/cassette.py`), not a kernel replay of effects |

#### 4.4.4 Suspension (`K-13` … `K-17`)

`SuspensionToken` (`dispatch.py:65-73`) binds `descriptor_digest` (`K-15`). No lease is opened (`K-13`).
Re-entry is at S1 (`K-14` comments at `:187-188`). Expiry is a token field (`K-16`); benchmark mode is `F-07`
(`K-17`). Interactive resume after `F-08` is an in-process queue (`RuntimeService._cmd_ResolveApproval`),
not a ledger `ApprovalResolved` event (see §3.13.2).

### 4.5 Grants — kernel obligations (`K-18` … `K-22`)

`Grant` (`grants.py:62-74`): `grant_id`, `principal`, `descriptor_digest`, `scope`, `expires_at`,
`purpose_digest`, `single_use`, `parent_grant_id`, `authenticator`, `approval_ref`.

| # | As-built |
|---|---|
| `K-18` | **Held** — empty `descriptor_digest` / `purpose_digest` refused (`grants.py:158-166`); S8 recomputes |
| `K-19` | **Held** — `single_use=request.idempotency_key is None` |
| `K-20` | **Held** — `HmacAuthenticator`; `issue(cross_process=True)` refuses without one (`grants.py:178-182`) |
| `K-21` | **Partial** — `expires_at` comes from constraints, no fixed TTL; **no renew API** |
| `K-22` | **Absent** as kernel code — subprocess containment is the sandbox, not a grant comment |

`K-49` revoke is transitive (`grants.py:225-241`) but **never called** and never emits `CapabilityRevoked`.

### 4.6 Attenuation (`K-23` … `K-27`, `K-48`, `K-49`)

`attenuate()` (`attenuation.py:131`) returns `AttenuationDenied` or a narrowed `Scope`. `Scope.sealed`
(`attenuation.py:98-107`, set at `:172`) implements `ADR-0067`: `StandardPolicy` denies
`request.action ∉ requested_scope.actions` **only when sealed** (`policy.py:95-106`) as `F-10`.

| # | As-built |
|---|---|
| `K-23` | **Held** |
| `K-48` | **Held** — `decide()` total, denies undefined and cross-kind (`resource_selector.py:431`) |
| `K-24` | **Held** — `depth = parent.depth + 1`; classifier widens when `depth > max_depth` |
| `K-25` / `K-26` | **Held** — denial records requested vs grantable; no silent intersection |
| `K-27` | **Held** — `F-10` is `ALERTABLE` |
| `K-49` | **Partial** — revoke exists; no event, no caller |

### 4.7 Provenance and the authority predicate (clause S1(e))

Library: `kernel/provenance.py`. `Accumulation.extend` only lowers labels (`:60-73`). `advance_turn` (`:75-90`)
is the K-33 union. `child_return` (`:92-99`) labels returned text `UNTRUSTED_DERIVED`.
`authority_violation` (`:130-143`) is F-09 when widening ∧ any untrusted span.

**Production wiring does not feed the library.**

- `_operator_span()` (`runtime/root.py:1210-1213`) returns a literal `Span("brief-1", Trust.OPERATOR, "operator_brief")`.
- `EpisodeEngine` only accumulates a span if `receipt_labeller` returns one (`engine.py:366-369`).
- Production `_admit_turn_result` (`root.py:1228-1245`) notes the tool result into L5 and **`return None`** —
  tool results never become justifying spans.
- `spawn()` (`engine.py:490-615`) never calls `Accumulation.child_return`; the child `run()` is given **no spans**.

So `K-28`–`K-31` hold as types and unit tests (`test/kernel/test_provenance.py`). `K-32` holds
(`StandardClassifier.widens_capability`, `classifier.py:109-124`, `MF-KRN-001`). `K-33` holds in the library
and **fails in production composition**. `K-31` (labels per source class, never at a call site) is also
weakened by the literal `_operator_span`.

#### 4.7.1 The two operands

Classifier operand: **Held**. Span-accumulation operand: **not wired**. `MF-KRN-002` fails a reset in a
broken fixture; the production engine never accumulates tool-result spans, so a reset is indistinguishable
from the live path.

#### 4.7.2 What provenance does not do

Matches the spec's negative claims. Intent binding (purpose digest + approval) exists for privileged
effects; the production predicate rarely sees untrusted spans to refuse.

### 4.8 The workload perimeter (`K-34` … `K-46`)

`adapters/sandbox/rootless.py:46 RootlessSandboxRunner`. bwrap argv (`:91-111`): `--unshare-all`,
`--unshare-user`, `--die-with-parent`, `--new-session`, `--clearenv`, `--ro-bind /usr`, `--proc`, `--dev`,
`--tmpfs /tmp`, `--bind` workspace. **No `--seccomp`**, no rlimits, no `--uid`.

Startup probes (`:162-185`): mount (evaluator path unreadability), egress (UDP 1.1.1.1:53), syscall
(`unshare --mount`). `ContainmentReport` (`ports/sandbox.py:38-53`) is the report type.
`publication_decision` (`sandbox.py:75-83`) implements `K-44`.

| # | As-built |
|---|---|
| `K-34` | **Partial** — namespaces via unshare; runner does not set UID (image docs claim worker 10001) |
| `K-35` | **Held** — writable `/workspace` and `/tmp` only |
| `K-36` | **Held** as deny-by-default (net unshared). No allowlist-egress path |
| `K-37` | **Partial** — limits reported on the report, not applied in bwrap argv |
| `K-38` | **Held** on timeout — `os.killpg` (`rootless.py:138`) |
| `K-39` | **Absent** — syscall probe only, no seccomp filter |
| `K-40` | **Inverted** — evaluator is a **separate** daemon (UID 10002), not inside the worker perimeter. The mount probe asserts the evaluator bundle is *unreadable* from the worker |
| `K-41` | **Absent** — stock `/usr/bin/bwrap`, not a statically linked supervisor |
| `K-42` | **Held** — probes |
| `K-43` | **Held** — `verified=False` / `visibility_mark="unverified-rootless-perimeter"` |
| `K-44` | **Held** — `publication_decision` |
| `K-45` | **Absent** — report is not composed into the instrument tuple |
| `K-46` | **Held** — `adapters/sandbox/fake.py` marks itself unverified |

### 4.9 Self-modification (clause S1(g)) — `SA-1` … `SA-6`

**All six Absent** as code. No candidate workspace, no digest-identified install, no rollback predecessor,
no autonomous promotion of `R0`/`R1`. Held vacuously in the sense that no self-update path exists (`RSK-08`).
`rule_test_map.py` marks the family untestable.

### 4.10 Architecture tests (`AT-01` … `AT-12`)

| # | As-built |
|---|---|
| `AT-01` | **Partial** — comments on `Kernel` / `__init__.py`; lattice prevents agency from importing adapters; composition root is `runtime/root.py`. Not a dedicated "only root imports adapters" scanner |
| `AT-02` | **Held** — evaluator import ban + `MF-S0-005` / `MF-S7-A-03-001` |
| `AT-03` | **Held** — `"client": {"domain","runtime"}` |
| `AT-04` | **Partial** — `Span.source_class` exists; no exhaustive source-class registry |
| `AT-05` | **Held** by absence — no commutativity flag |
| `AT-06` | **Held** — kernel imports only domain/ports |
| `AT-07` | **Partial** — `check_tcb_budget.py`, `check_core_changes.py`; not a review rule per TCB path |
| `AT-08` | **Held** — TCB budget + `MF-KRN-011` |
| `AT-09` | **Held** — `test_dispatch.py` exhaustiveness |
| `AT-10` | **Absent** — no cast lint |
| `AT-11` | **Absent** — no startup UID/topology assertion in tests |
| `AT-12` | **Absent** — no capability→verifier-path check |

### 4.11 Threat model

No code artefact enumerates `A1`–`A7` or `T-01`–`T-08`. Control coverage:

| Attack | As-built residual |
|---|---|
| `T-01` injection → escalation | Predicate library exists; production spans do not accumulate tool results. Perimeter is the load-bearing control |
| `T-02` verifier compromise | Unreachability is an import rule + separate UID. No `AT-12` |
| `T-03` tool escape | Classifier is not load-bearing (`K-39` absent) |
| `T-04` budget evasion | In-flight overrun before commit, as specified |
| `T-05`/`T-06` memory/corpus | No memory write path, no corpus |
| `T-07` release pipeline | No release pipeline |
| `T-08` recovery-path forgery | Recovery is exterior (`recovery.py`). **Heartbeats are not authenticated** |

### 4.12 Audit checklist (one-day reviewer)

Answered from code, not as a passing audit:

1. Model-output → effect path is `EpisodeEngine` → `Kernel.dispatch` only. Dual EvidencePlane ingress does not exist.
2. Widening is a classifier call; `MF-KRN-001` exists. Production spans do not accumulate.
3. `MF-KRN-002` exists; production `receipt_labeller` returns `None`.
4. `AT-12` does not exist — cannot name a selector check that refuses verifier paths.
5. Over-broad request → `AttenuationDenied` / `F-10` alertable. Sealed-scope membership is the extra gate.
6. Containment is probed; unverified blocks publication via `publication_decision`.
7. Terminal record: `RecoveryScanner` writes `RunRecovered`/`RunAborted`. `F-22` preserves undeterminable.
8. Cross-process grants: HMAC. Heartbeats: none.
9. Planes: worker/evaluator UIDs in Dockerfiles; no AT-11 runtime assert. Cognition+Control share one process.
10. Live must-fail IDs are `MF-KRN-*` / `MF-S0-*` / …, not `MF-01`…`MF-37`. Until `CI-9` is a failing gate, VG-05's own caveat applies: rules are asserted, not proven by the spec's ID map.

---

## 5. Competence, Memory & Evidence Model (VG-06)

### 5.1 The governing asymmetry

`MEM-1` has no pipeline to violate. A `Verdict` (`ports/evaluator.py:42`) is produced by the exterior
evaluator and is **not** used to admit a semantic claim. `runtime/root.py:788-791` states the ledger is the
only memory.

### 5.2 The four stores

| Store | As-built |
|---|---|
| Working | Episode context: `ContextCompiler` + `_LayeredOperator.note` (L5) |
| Episodic | `EventStorePort` / SQLite ledger + JSONL export |
| Semantic claims | `domain/evidence/claim.py Claim` as a value type; injected list for `vg why` (`service.py:83-88,331-336`). No store, no write gate, no retrieval |
| Competence | Harness `ArtifactGraph` (`domain/artifacts/graph.py:85`) — composition, not competence. `CompetencePriorRecorded` is the only competence-named event that is emitted |

### 5.3 The claim pipeline

**Absent.** No extractor, contradiction search, corroboration, quarantine, activation, or demotion engine.
`EvidenceClaimProduced` is never emitted. `Claim.contradicts` / `derived_from` / `evidence_refs` are fields
that nothing walks. Hedge fields are recorded and never consumed (`claim.py:22-25, 179-182`).

`MEM-2`…`MEM-7`: parse-time field presence on `Claim` covers `MEM-2` shape; `MEM-3`–`MEM-7` have no
implementation. `MEM-7` trainability is an envelope enum only.

### 5.4 Verification

#### 5.4.1 Evaluator classes

`ports/evaluator.py` / `IsolatedEvaluator` implement a mechanically-reproducible class (command + probes).
No ranker, no learned proxy, no human-adjudicated class as code. `V-01`…`V-04` are held by absence of a
ranker that admits.

#### 5.4.2 Verifier unreachability

Layer 1 (import): **Held** (`AT-02`). Layer 2 (`K-03` dispatch-time R0/R1 reject): **Absent**. Layer 3
(read-only mount of evaluator inputs): **Held** as a worker probe that the evaluator path is unreadable,
not as a shared mount.

#### 5.4.3 The double probe

**Held** inside `IsolatedEvaluator`: `_probe_immutability` (`isolated.py:146`) and `_probe_non_pollution`
(`:197`). Verdict evidence carries `immutability` / `nonPollution` (`:273-286`). A probe failure yields
inconclusive, not a pass (`:72-91`).

#### 5.4.4 Inconclusive as a first-class state (`V-05` … `V-09`)

**Held** as `runtime/outcome_labels.py` plus six must-fail cases `MF-S7-C-02-001`…`006`
(`inconclusive:precondition_satisfied`, `no_intervention`, `model_not_invoked`, `instrument_error`,
`no_verdict`, containment publication block). Provider failure → `RunTermination.INSTRUMENT_ERROR`, not a
task failure. `V-06`/`V-07` (denominator hygiene, per-arm instrument-error rate) live in
`tools/telemetry/statistics.py` / `aa_runner.py`, not in `vanguard/packages/`.

### 5.5 Promotion, activation and demotion

**Absent** as engines. `ArtifactRegistryProjection` (`projections.py:300`) would consume `ActivationChanged`;
nothing emits it. `vg why` (`_cmd_ExplainArtifact`) reports absence rather than smoothing
(`roadmap_backend.md` S10-A-04; `service.py:331-336`).

#### 5.5.1 Three stages, in order

No hard-constraint gate, no frontier, no per-context activation policy. `runtime/repair.py` retries a
harness; it does not rank competence artifacts.

#### 5.5.2 Promotion criteria — all must hold for domain D

No promotion criteria evaluator. Ablation, holdout-for-derivation, and reversible activation are unimplemented.

#### 5.5.3 Demotion and anti-ossification (`V-10` … `V-13`)

`V-10` invalidation conditions are required at parse and **never run**. `V-11`–`V-13` have no counterpart.

### 5.6 The outer loop

**Absent** as distillation/bandit. The closest outer loop is `runtime/repair.py:58 drive_until_green` plus
`runtime/tier_escalation.py` (salvage of deleted `MetaLoopEngine` — docstring `:4-10`: no second dispatch
path, no grading of own escalation). That is repair, not competence promotion.

### 5.7 Substrate invariance

Substrate fields exist on `Claim` (`substrate_profile`) and on the instrument tuple in `tools/telemetry/tuple.py`.
No migration protocol, no portability classification, no substrate-debt metric in `vanguard/packages/`.

### 5.8 Honest limits

Corroborated: no `EvaluationBudget`; ablation is not implemented; TableWorld is not a second domain through
the engine (see `C-10`).

---

## 6. Loop Engineering, Measurement & Self-Improvement (VG-07)

VG-07's in-tree apparatus is **outside** `vanguard/packages/`: `tools/telemetry/` and `lab/{build,run,diff,bench}.py`,
bound by `S8-J-07`. `check_boundaries.py` forbids `lab/` from importing anything.

### 6.1 The three closure conditions

| # | As-built |
|---|---|
| `CL-1` | **Held architecturally** — evaluator import ban + separate daemon. Production evaluation is still *triggered* by the runtime (`root.py:935`), not by a ledger observer |
| `CL-2` | **Partial** — `tools/telemetry/splits.py` implements HOLDOUT/SEALED burn. No promotion path to violate or satisfy it in packages |
| `CL-3` | **Partial** — `tools/telemetry/aa_runner.py` refuses degenerate 0%/100% A/A; `statistics.py` refuses p-values at n<20 (`M-28` comment) |

### 6.2 Levels of loop engineering — vocabulary, never a roadmap

`M-01` is held as practice: no ticket in `vanguard/packages/` is named "L6". As-built loop depth: L1 tool loop
(`EpisodeEngine`) + partial L2 (compaction yes, re-grounding unwired) + spawn as a narrow L3. L4/L5 absent.
`runtime/loops/` **does not exist**; `MetaLoopEngine` was deleted (`tier_escalation.py:4-10`).

### 6.3 Long-horizon instrumentation

Consolidation-loss runner: **absent**. Re-grounding: `RegroundPolicy` exists, **never called**. Retrieval
value: `IndexPort` is observation-only (ALFA S10-A-03: tests assert no `propose`/`rank`/`select`/`dispatch`).

### 6.4 Distillation and promotion pipeline

**Absent** in packages. Evolution event kinds have zero emitters (see §3.13.2). `tools/telemetry/gap_freeze.py`
is a promotion-freeze helper for the lab, not a runtime promoter.

### 6.5 The measurement doctrine (`M-02` … `M-20`)

Most `M-*` IDs do not appear in `vanguard/packages/`. Coded outside packages:

| ID / spirit | Where |
|---|---|
| `M-18` incomparable lift refused | `tools/telemetry/tuple.py:1-34, 189-220` |
| `M-19` split burn | `tools/telemetry/splits.py` |
| `M-07` spirit (degenerate A/A) | `tools/telemetry/aa_runner.py:7-8` |
| `M-28` small-n p-value refuse | `tools/telemetry/statistics.py:9,57` |
| Integer quantities | `runtime/telemetry.py:1-9` |
| Arm scoring from ledger | `runtime/scoring.py` (`W15-A`) |

`K_compat` refusal on the tuple is the live `M-18` gate. `lab/bench.py` is paired McNemar over `lam.sqlite`.

### 6.6 Optimisation and what it cannot do

No optimiser in packages. Repair (`runtime/repair.py`) retries the same harness; it does not rewrite the
kernel or the evaluator.

### 6.7 The release pipeline (`M-21` … `M-24`)

**Absent.** `CandidateBuilt` / `CandidateAttested` / `CanaryPromoted` / `RollbackTriggered` never emitted.
No canary, no signed promotion, no tested rollback of a successor.

### 6.8 The transfer experiment (impoverished-ontology, Phase 2)

**Absent** as a runner. TableWorld exists as a toy environment not bound through `EnvironmentAdapter` / the
episode engine — it cannot currently witness `H0`.

### 6.9 The experiment registry (`M-25` … `M-28`)

**No runtime registry.** `M-28` appears as a comment in `statistics.py`. Preregistration helper:
`tools/telemetry/preregistration.py`.

### 6.10 Preparation for search, process rewards and reflection

**Absent** (`DEF-06` honoured). Contracts declare the event kinds; no engines.

---

## 7. Architectural Decision Record Summary (VG-09)

ADRs are documentation. Code cites a **subset** as docstring anchors. Grep of `ADR-00` in `vanguard/packages/`:
`0039`, `0047`, `0048`, `0054`, `0057`, `0058`, `0060`, `0062`, `0067`. `0068` behaviour (hedge fields) is
implemented without the ID. `0050` appears in schema `$comment`s. `tools/` cites **zero** ADR IDs.

### 7.1 Foundational decisions

| ADR | As-built |
|---|---|
| `0000` | Docs only |
| `0001` | **Reversed by `ADR-0063`** — control plane is Python (125 modules) |
| `0002` | **Held** — subprocess + NDJSON seams |
| `0003` | **Held** — no runtime workflow graph; `ProcessEngine` is governance, not agent topology |
| `0004` | **Partial** — evaluator unreachable by import; no `AT-12` |
| `0005` | **Held** — `compose()` freezes `FrozenHarness` |
| `0006` | **Held** — index is Python regex (`adapters/stores/repo_index.py`); tree-sitter not in TCB |
| `0007` | **Not held** — no parallel execution (`C-04`) |

### 7.2 Adjudications between the two pre-v4 lineages

| ADR | As-built |
|---|---|
| `0008` | Schemas exist; Python reader is hand-written, not generated |
| `0009` | **Held** — `domain/canonicalisation/jcs.py` |
| `0010` | **Held** — SQLite WAL + JSONL export |
| `0011` | **Held** — `Scope` has actions + resources + constraints |
| `0012` | **Held** — `K-26` |
| `0013` | **Held** — controller, worker, evaluator (updater absent) |
| `0014` | Python + TypeScript readers exist (`domain/contracts.ts`) |
| `0015` | Vacuous — no promotion |
| `0016` | **Not held** — no operator-as-data |
| `0017` | **Not held** — `ArtifactGraph` is harness composition |
| `0018` | **Held** at parse (`INV-1`) |
| `0019` | Vacuous — no self-mod path |
| `0020` | Docs only |

### 7.3 Corrections — each bound to the test that now catches it

Live must-fail IDs are `MF-KRN-*`, not `MF-01`…`MF-37`. Approximate mapping:

| ADR | Spec catch | Live catch |
|---|---|---|
| `0027` | `MF-01` / `K-32` | `MF-KRN-001` constant-classifier |
| `0028` | `MF-02` / `K-33` | `MF-KRN-002` span-reset (library; prod spans not accumulated) |
| `0039` | `MF-31` / `CT-51` | `MF-KRN-003` unbound-grant |
| `0023` | `AT-08` | `MF-KRN-011` TCB ALARM |
| `0044` | `MF-36` / `K-47` | `MF-KRN-010` late-intent |
| `0021`/`0022` | `MF-11`/`MF-13` | sandbox probes + `MF-S7-C-02-006` publication block |
| `0031` | `MF-17` / `V-05` | `MF-S7-C-02-004` `inconclusive:instrument_error` |

### 7.4 Deferrals with a scheduled reversal

`0035` five-process split: not started. `0036` third language: absent. `0037` memory-write tests: absent.
`0038` schema LOCKED: still DRAFT (`schemas/v4/MANIFEST.md`).

### 7.5 Sprint 0 governance baseline (`ADR-0045` … `ADR-0053`)

| ADR | As-built |
|---|---|
| `0045` | Docs |
| `0046` | Docs — GTS-13C still the programme plan |
| `0047` | **Held** — `spike/`/`slice/` absent; `--s4-exit` + `MF-S4-001` |
| `0048` | Trust-spine tests exist (`test/trust/test_spine.py`) with fake/LAM models |
| `0049` | **Held** — `vg-code-default` verbs `fs.read`/`fs.search`/`patch.apply`/`proc.exec`; `vg-shell-only` ships |
| `0050` | **Held** — `ProcessDefinition`/`ProcessInstance`/`ProcessEngine` |
| `0051` | **Held** — sink-class mediation; privileged only for grants |
| `0052` | Active MVP Contract tools exist (`tools/check_active_mvp_contract.py`, `run_active_contract_tests.py`) |
| `0053` | Docs |

### 7.6 Kernel, sprint-structure and phase-authorisation decisions

Cited in code:

| ADR | Where |
|---|---|
| `0054` | TCB baseline; `engine.py:530` |
| `0057` | Privileged-apply approval; `runtime/root.py:1` |
| `0058` | `runtime/root.py:1323` |
| `0060` | Zero core lines for a new domain; `engine.py:334-335`, `invocation.py`, `root.py` |
| `0062` | Inbox/outbox + approvals; `service.py:3`, `inbox.py`, `recovery.py:3` |
| `0063` | Python control plane (implicit) |
| `0066` | MCP is not an authority path (commented; zero MCP adapter code) |
| `0067` | `Scope.sealed`; `attenuation.py:99`, `policy.py:95` |
| `0068` | Claim hedge fields without the ID in source |

`0061` (dual dispatch ingress) is **not** realised for EvidencePlane (see §4.3). `0064`/`0065` are docs.

### 7.7 What belongs in the register

No code enforcer that a decision must be an ADR. `tools/check_pr_requirements.py` requires a `REQ-*` cite,
not an ADR cite.

---

## 8. Deferred & Rejected Design Space (VG-10)

### 8.1 Deferred (`DEF-01` … `DEF-12`)

| # | As-built |
|---|---|
| `DEF-01` | **Honoured** — no authoring canvas in packages (GUI is out of scope) |
| `DEF-02` | **Honoured** — no semantic-memory pipeline |
| `DEF-03` | **Partially superseded** — `EpisodeEngine.spawn` is live (`engine.py:490`). Not general subagents / playbooks |
| `DEF-04` | **Partial** — `IndexPort` exists (observation-only). Browser / web search **absent** |
| `DEF-05` | **Honoured** — no systems-language index |
| `DEF-06` | **Honoured** for engines; event kinds declared |
| `DEF-07` | **Honoured** — no updater |
| `DEF-08` | **Honoured** — no public-benchmark gate |
| `DEF-09` | **Honoured** — no training path |
| `DEF-10` | **Honoured** |
| `DEF-11` | **Superseded in part** — three compaction strategies exist; default is still recency-window |
| `DEF-12` | **Superseded for privileged approval** (`ADR-0057`, `approvals.py`). General session-suspend is an in-process queue, not a ledger `ApprovalResolved` |

### 8.2 Rejected (`REJ-01` … `REJ-12`) — never classify these as "missing"

| # | As-built |
|---|---|
| `REJ-01` | **Held** — no runtime workflow graph |
| `REJ-02` | **Held** — no L6+ tickets in packages |
| `REJ-03` | **Held** |
| `REJ-04` | **Held** |
| `REJ-05` | **Held** |
| `REJ-06` | **Held** — `Trust` is one axis, not a unified lattice |
| `REJ-07` | **Held** — classifier is a parser; perimeter is bwrap |
| `REJ-08` | **Held** — enforcement at `Kernel.dispatch` |
| `REJ-09` | **Held** in packages |
| `REJ-10` | **Contradicted by `README.md`** — nine-level "Biological Hierarchy" is the README's second section. No code module implements it |
| `REJ-11` | **Held** — no scalar promotion |
| `REJ-12` | **Held** |

Additionally: `MetaLoopEngine` / `runtime/loops/` **rejected and deleted** (`DECISION-0005`; salvage in
`tier_escalation.py`). MCP as authority path **rejected** (`ADR-0066`); zero MCP adapter code.

### 8.3 How an entry moves

No mechanised register. Roadmap rows in `docs/scrum/roadmap_backend.md` are the living board.

---

## 9. Build Plan, Programme Spine & Roadmap Milestones (VG-08, GTS-13C)

Living board: `docs/scrum/roadmap_backend.md` (updated 2026-08-17, product **v0.4.5-beta**). `TK-*` IDs
have **zero** occurrences in `vanguard/packages/`.

### 9.1 Phase 0 scope (VG-08)

**In, as-built:** schemas + Python/TS readers; episode engine; budgets/leases; grants; SQLite event store +
JSONL export; blob store; fake + real model adapters; Git environment; separately-identified evaluator;
rootless worker with probes; crash recovery scanner; CI boundary/property/conformance/must-fail.

**In the spec, weak or missing in code:** TableWorld as an `EnvironmentAdapter` (it is not); operators;
`vg run` is a client (out of scope) over `RuntimeService`; measurement/A/A floor was spec-out of Phase 0
but `tools/telemetry/` now exists (`Y-15`).

**Out, still out:** canvas/GUI (present as `vanguard-gui/` but out of this document's scope); browser;
semantic memory; automatic promotion; general subagents; training; autonomous updater.

### 9.2 Phase 0 hypotheses

| # | As-built |
|---|---|
| `H0` | **Not witnessed.** TableWorld is not routed through the episode engine. `check_core_changes.py` mechanises the "zero kernel/engine lines" half |
| `H1` | **Partial** — privileged effects yes; observation/pure skip grants |
| `H2` | **Partial** — probes + namespaces; no seccomp (`K-39`); no AT-11 |
| `H3` | **Held** — `F-22` / `RecoveryScanner` |
| `H4` | Open — PO acceptance records live tool-call / Q2 / spend / Claude daily-driver still TODO (`roadmap_backend.md`) |
| `H5` | **Held** — reducer + replay tests |

### 9.3 Three increments

- **A Trust Spine** — present (`test/trust/test_spine.py`, fake/LAM).
- **B Coding Cell** — present as coding runtime modules + `vg-code-default`; live coding win not claimed.
- **C Generality Witness** — **not met.** TableWorld is a side type; `vg-table-default` is unregistered.

### 9.4 Phase 0 tickets (`TK-00` … `TK-12`)

No `TK-*` symbols in packages. Substance mapping: `TK-00` boundaries CI; `TK-01` schemas + JCS + vectors;
`TK-02` grants/selectors; `TK-03` `Governor`; `TK-04` event store/reducer; `TK-05` `RecoveryScanner`;
`TK-06` `Kernel.dispatch`; `TK-07` redaction/export (partial); `TK-08` rootless probes; `TK-09` isolated
evaluator; `TK-10` episode + providers; `TK-11` git environment; `TK-12` TableWorld **incomplete**.

### 9.5 CI gates (VG-08 §4)

`.github/workflows/ci.yml` (`vanguard-v4-gates`) runs `sprint0-gates` and `docs-gates`. Present:
`check_boundaries.py`, `check_tcb_budget.py`, `run_broken_tests.py`, `run_active_contract_tests.py`,
schema validation, `scan_secrets.py`, `check_stale_paths.py`, `audit_v4.py`, `wordcount_v4.sh`,
`rule_test_map.py` (exits 0 with `gaps=133`). **Absent as named gates:** cast lint (`AT-10`), fault-injection
of every `F-nn` as a CI job (unit tests cover a subset).

### 9.6 The must-fail suite (`MF-01` … `MF-37`)

**`MF-01`…`MF-37` appear nowhere in code or tests.** The live harness is `test/broken/manifest.json` (38
cases). `tools/run_broken_tests.py` requires the control to exit 0 and the broken counterpart to exit
non-zero **with the declared `expected_failure` substring**.

Live IDs:

`MF-S7-C-02-001`…`006`, `MF-S7-C-001`, `MF-S0-001`…`009`, `MF-S7-A-01-001`, `MF-S7-A-02-001`,
`MF-S7-A-03-001`, `MF-KRN-001`…`011`, `MF-S4-001`, `MF-GOV-001`, `MF-CTX-001`, `MF-CTX-002`,
`MF-SEC-002`, `MF-TEL-001`, `MF-GOV-PATH-001`, `MF-SEC-SCAN-001`.

Kernel family vs spec table (closest analogue, not a bijection):

| Live | Broken variant / intent | Spec analogue |
|---|---|---|
| `MF-KRN-001` | `constant-classifier` | `MF-01` / `K-32` |
| `MF-KRN-002` | `span-reset` | `MF-02` / `K-33` |
| `MF-KRN-003` | unbound grant | `MF-31` / `CT-51` |
| `MF-KRN-004` | widening attenuation | `MF-04` / `K-23` |
| `MF-KRN-005` | permissive grant | `MF-05` / `K-26` |
| `MF-KRN-006` | leaked lease | `MF-06` / `K-06` |
| `MF-KRN-007` | clamped overrun | `MF-07` / `K-07` |
| `MF-KRN-008` | permissive sink | `MF-KRN-008` (no MF-01–37 twin) |
| `MF-KRN-009` | unrecorded effect | skip-record (`SinkClass` docstring) |
| `MF-KRN-010` | late intent | `MF-36` / `K-47` |
| `MF-KRN-011` | TCB ALARM | `AT-08` |

This is why `rule_test_map.py`'s `tested=28` is a **spec cross-reference count** of `MF-nn` mentions next to
rule IDs in `docs/main_v4/`, not a count of `test/broken/` cases.

### 9.7 The rule-to-test map and its untestable classes

Live output `rules=203 tested=28 untestable=42 gaps=133`. `CI-9` **does not fail the build**. Compensating
assurance for architectural prohibitions is `check_boundaries.py` (stronger than a runtime test). Statistical
refusal tests exist in `tools/telemetry/`. `SA-5` is vacuously held (no autonomous path).

### 9.8 Phase 0 exit criterion

**Not closed.** `CI-9` is red by construction. TableWorld does not witness `H0`. Dogfood 60% / fourteen-day
window is not mechanised. Roadmap PO acceptance is marked done *honestly* with live tool-call still TODO.

### 9.9 GTS-13C — programme artifact ownership

Docs. Code ownership follows the package lattice, not the 13C artifact table.

### 9.10 GTS-13C — the task spine (`T0` … `T11`)

Present in spirit: T1 contracts, T2 kernel, T4 episode, T6 coding harness, T7 manifests, T10 two-impls +
governance area. T8 measurement lives in `tools/telemetry/`. T3 operators **absent**. T5 playbooks **absent**.
T9 evolution **absent**. T11 enterprise **absent**.

### 9.11 `T1` — contract deliverables

38 schema artefacts; hand-written Python reader; TS reader at `domain/contracts.ts`; vectors under
`schemas/v4/vectors/`; `test/contracts/` 121 methods.

### 9.12 `T2` — kernel deliverables

Nine kernel files; `FailurePath`; grants; attenuation; governor; provenance library. Dual-ingress EvidencePlane
**not** delivered. `principalRole` six-value enum **is** delivered.

### 9.13 `T4` — the execution spine

`EpisodeEngine` + `RunTermination` eight values (`ADR-0057`). Spawn live. Playbooks not.

### 9.14 `T6` — the coding harness

~2,088 LOC coding-named modules + `vg-code-default`. Live coding win not claimed.

### 9.15 `T7` — artifact graph and harness manifests

`kinds.json` 17 rows; six packs on disk, five registered; `compose()` freeze; `vg-table-default` orphan.

### 9.16 `T10` — engineering discipline

`check_boundaries.py` (incl. governance special-case and closed package set), `check_tcb_budget.py`,
`check_core_changes.py` (`M11`/`ADR-0060`), two impls per several ports.

### 9.17 GTS-13C spine — one primitive, two coordinators, five nouns

One primitive: the episode loop. Coordinators: `EpisodeEngine` and `ProcessEngine` (governance). Nouns in
code: grants, events, manifests, receipts, verdicts. Operators and playbooks are reserved kinds only.

### 9.18 GTS-13C locked concepts (`L-01` … `L-18`) and open concepts (`O-01` … `O-11`)

Locks with code: schemas, kernel roster, evaluator exteriority, NDJSON seams, sink-class mediation,
integer money. Open: spawn is done (`O-03` on the roadmap); playbooks still deferred; competence graph not
started (roadmap explicit).

### 9.19 Where every capability lives (the falsification test for the abstraction)

Adding a domain is supposed to be zero lines in `kernel/` and `agency/episode/` (`ADR-0060`,
`check_core_changes.py`). Coding still leaked `domain/ledger/coding_session.py` into domain.

### 9.20 Sprint schedule (GTS-13C Part II)

Superseded as a schedule by `docs/scrum/roadmap_backend.md` waves/sprints (S6B–S34 rows). Not restated here.

### 9.21 Test doctrine — six families (GTS-13C Ch. 8)

Present: unit, property (`test/kernel/test_attenuation.py`, selector properties), vectors, must-fail,
cassettes (`adapters/models/cassette.py`). Fault injection of the full `F-nn` table is incomplete. Live
canary is out of packages.

### 9.22 Margins — carried and alarmed

TCB alarm +131 is the only mechanised margin. Cost/latency margins are not CI gates.

### 9.23 The MVP gate — four questions (GTS-13C Ch. 10)

Roadmap / `ADR-0064` record Q1–Q4 as not met or honest-partial. Q3 has a dated why-not (`S9-J-04`).
This document does not re-score them.

### 9.24 How the MVP grows itself — four stages

Stage 1 (ledger accumulates) is **partial** — 11 of 34 kinds emitted. Stages 2–4 (attribution, proposal,
structure) are **absent**.

### 9.25 The Active MVP Contract (GTS-13C Ch. 15)

**Implemented as tools, not as a kernel type.** `tools/check_active_mvp_contract.py` /
`tools/run_active_contract_tests.py`. Header measurement: `closure-in-progress`; baseline 16/16; merged-scope
14/14. `req_id` family in packages is the `REQ-*` list in §0.4 (not `REQ-KRN-014` as the theory example).
`check_pr_requirements.py` is the PR cite gate.

### 9.26 Standing programme risks (GTS-13C Ch. 14)

Code-visible: specification capture (`CI-9` red, 133 gaps); TCB tripwire live; disposable `spike/`/`slice/`
deleted; mediation drift tested by `MF-KRN-008`; process/episode split held (`ProcessEngine` vs
`EpisodeEngine`). Unmechanised: dogfood rate, Conway drift, contract inflation.

---

## 10. Engineering Handbook Principles (VG-01)

VG-01 is practice. Enforcement is tools, not a runtime module.

### 10.1 Mental models (`M1` … `M11`)

| # | As-built |
|---|---|
| `M1` | **Held** for the agent loop; `ProcessEngine` is the carved exception (`X-03`) |
| `M2` | **Partial** — EffectAdapter + Evaluator exist; ObservationSource and CognitiveOperator do not |
| `M3` | **Held** as split: `Kernel.dispatch` vs `RootlessSandboxRunner` |
| `M4` | **Library held, production weak** (§4.7) |
| `M5` | **Held** as import unreachability |
| `M6` | **Held** — `run_broken_tests.py` |
| `M7` | **Not held** — no competence graph |
| `M8` | Docs/CI (`audit_v4.py`); not packages |
| `M9` | Practice |
| `M10` | **Held** — no plugin runtime in kernel; index is a port |
| `M11` | **Held as a lint** (`check_core_changes.py`); contradicted by `coding_session.py` in domain |

### 10.2 SOLID, concretely

Kernel files are one-job modules (`model.py` docstring). Ports are narrow. Substitutability: `ModelPort`
returns `Result` (`CT-33`); `EvaluatorPort` inconclusive-not-pass; `SandboxRunner` reports; `EnvironmentAdapter`
returns `Result[T]`. DI enforced by `check_boundaries.py`.

### 10.3 The shape of a change

Not mechanised beyond PR requirement cites and boundary/TCB gates.

### 10.4 Testing taxonomy — seven kinds

Six of seven exist (see §9.21). Live canary is not a packages test.

### 10.5 Practices and working agreements

`AGENTS.md` / `CLAUDE.md` at repo root. Discovery scans those names into L3/L4 (`agency/manifests/discovery.py`).

### 10.6 Review checklist

No code.

### 10.7 ADR format

Docs. Code cites IDs in comments only.

### 10.8 Repository layout (VG-01 §8)

Live layout is VG-03/T10.1: `vanguard/packages/{domain,ports,kernel,agency,runtime,adapters}` plus
`runtime/governance/` as a boundary **area**, `vanguard/clients/`, `lab/`, `benchmarkings/`. Not
`policy-kernel/` or `controller/`. Closed package set is CI-enforced.

### 10.9 Glossary

No glossary type in code. Wire names are `camelCase`; Python is `snake_case`.

### 10.10 The ten rules

Not enumerated in packages. Closest mechanical set is `check_boundaries.py` + `check_tcb_budget.py` +
`run_broken_tests.py` + `scan_secrets.py`.

---

## 11. Convergence Evidence & Vision Annex (VG-11, VG-12)

### 11.1 Independent design convergence (VG-11) — EVIDENCE, secondary

No code. Eight convergent conclusions vs as-built: (1) loop not graph — held; (2) single authorisation point
— held for `Kernel.dispatch`, with sink-class skip for non-privileged; (3) evaluator unreachable — import
held, trigger is runtime-side; (4) measurement apparatus — outside packages; (5) instrument ≠ task failure —
held (`INSTRUMENT_ERROR`, inconclusive labels); (6) trajectory as substrate — ledger partial (11/34 kinds);
(7) freeze at composition — held; (8) must-fail — 38 live cases, wrong ID family.

### 11.2 Vision annex (VG-12) — NON-NORMATIVE

No ticket in packages cites VG-12. `README.md` nevertheless carries the biological hierarchy that `REJ-10`
and VG-12 exist to quarantine. Competence-prior recording (`CompetencePriorRecorded`) is the one
metacognition-shaped mechanism that shipped.

---

## 12. Appendix — Internal Contradictions & Ambiguities in the Corpus

These are spec-vs-spec conflicts. This section records **which side the code took**.

### 12.1 Load-bearing contradictions

| # | Code resolution |
|---|---|
| **X-01** | **Sink-class mediation** (`ADR-0051`): grants only for `PRIVILEGED`. All three classes still traverse `Kernel.dispatch` and are recorded |
| **X-02** | **Optional grant** — `EnvironmentAdapter.observe(..., grant: Optional[Any] = None)` |
| **X-03** | **Both exist** — episode loop + `ProcessEngine` / `governance/` as a first-class boundary area |
| **X-04** | **VG-03 axes** (`ADR-0057`) — `RunTermination` eight values; verdict is a separate `Verdict` |
| **X-05** | **Fifth shape** — one ordered `Trust` enum + envelope `confidentiality`; no `epistemic`/`influence` types |
| **X-06** | **VG-04 kinds** in `SELECTOR_KINDS`; manifests encode command allowlists as `generic` URI strings, not GTS `command` |
| **X-07** | **Merge** — kernel `Grant` has actions + resources + `purpose_digest`; wire grant has plural `actions` and singular `selector` |
| **X-08** | **VG-04 envelope** + required `principalRole`; no `branchId`/`processId` on the envelope |
| **X-09** | **GTS-leaning ports** plus extras: `ModelPort`, `EnvironmentAdapter`, `EvaluatorPort`, `EventStorePort`, `BlobStorePort`, `IndexPort`, `ClockPort`, `RandomPort`, `SandboxRunner`, and `ports/kernel.py` (`Clock`, `EffectAdapter`, `EventSink`, `Ledger`). No `OperatorRunner`/`ObservationSource`/`PolicyEngine` port |
| **X-10** | **VG-03 + T10.1** layout with `governance/` special-cased |
| **X-11** | `tools/telemetry/splits.py` uses HOLDOUT/SEALED (three-split spirit) |
| **X-12** | Lab uses McNemar (`lab/bench.py`); telemetry refuses small-n p-values rather than a full T8.3 stack |
| **X-13** | Wire `principalRole` is T2.1's six. Kernel ingress is Episode-only. Phase 0 identities: controller + worker 10001 + evaluator 10002 |
| **X-14** | `Reservation` is `{usd_micros, millis, tokens, bytes_}`; turns/depth enforced outside it |
| **X-15** | Privileged approval shipped; `ApprovalResolved` as a ledger event did not |

### 12.2 Ambiguities and undefined terms

| # | As-built |
|---|---|
| **Y-01** | Resolved in code as `Trust` five-value enum (`kernel/model.py:40-52`) |
| **Y-02** | Resolved as 1,307 + 131 = 1,438 in `kernel-tcb-budget.json`; live 1,333 |
| **Y-03** | README/comments say "Attenuation Kernel"; class is `Kernel` |
| **Y-04** | Port `EffectReceipt` + kernel `AdapterOutcome`; wire `Receipt` has no lease id |
| **Y-05** | Only verifier admits a `Verdict`; no activation-policy admit path |
| **Y-06** | `RISK_ORDER = ("low","medium","high","critical")` (`attenuation.py:41`) |
| **Y-07** | Live verbs `fs.read`, `fs.search`, `patch.apply`, `proc.exec` plus classifier prefixes |
| **Y-08** | VG-07 cites `tools/telemetry/` — those files exist |
| **Y-09** | Docs |
| **Y-10** | **Confirmed** — live `MF-KRN-*`/`MF-S0-*`/… vs spec `MF-01`…`MF-37` |
| **Y-11`–`Y-18` | Docs/governance; not packages |
| **Y-19** | `FailurePath` includes `F-21a` as its own member; `AT-09` tests the enum, not `F-01..F-25` as a range |
| **Y-20** | No `Broker` type; `Kernel` + `StandardPolicy` |

### 12.3 Known-open governance gates (spec-recorded, not implementation observations)

As of this tree: `CI-9` still reports `gaps=133` and exits 0; schemas remain DRAFT; `SEC-01` has
`tools/scan_secrets.py` + `MF-SEC-SCAN-001`; Active MVP Contract tools exist and report closure-in-progress;
VG-05 caveat still applies — a rule whose only test ID is an `MF-01`…`MF-37` string in `docs/main_v4/` is
not an established control in `test/broken/`.

