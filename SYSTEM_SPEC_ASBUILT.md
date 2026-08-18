# Vanguard / GTS — System Specification As-Built

Forensic map of the **production Python backend** at `vanguard/packages/` (`domain/`, `ports/`, `kernel/`,
`agency/`, `runtime/`, `adapters/`) as it exists on branch `feat/harness-cli-v045`, commit lineage ending
`d2aef8e feat(S-special): Version 0.4.5`. Corroborating evidence: root `README.md`, `test/`,
`tools/check_boundaries.py`, `tools/check_tcb_budget.py`, `tools/rule_test_map.py`, `test/broken/manifest.json`,
`docs/scrum/roadmap_backend.md`.

**Out of scope by instruction:** `vanguard/clients/cli/` (TypeScript/Ink), `vanguard-gui/`, all TUI/CLI
presentation code. `lab/`, `tools/telemetry/` and `benchmarkings/` are outside `vanguard/packages/` but are
reported where the theory document names them explicitly (notably §6).

Section numbering and headings mirror `SYSTEM_SPEC_THEORY.md` exactly so the two can be diffed
section-by-section. This document records **what the code does**, not whether that is correct.

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
`README.md:236` also names `runtime/coordination.py` as a live component; `runtime/session_log.py:1-8`
records that `runtime/coordination.py` was **deleted** in `S7-A-05`.

### 0.2 The document set and status classes

Not a code concern. `docs/main_v4/` exists and contains the VG-00…VG-12 + GTS-13C corpus; `README.md:395-417`
carries an "Alignment Matrix" asserting **"Fully Aligned"** for `00`, `01`, `02`, `03`, `05`, `09` and `13C`
(VG-04, VG-06, VG-07, VG-08, VG-10, VG-11, VG-12 rows are absent from that table).

### 0.3 Word budget ledger

`tools/wordcount_v4.sh` is **not present** in `tools/` (the directory holds 24 `*.py` plus `__init__.py`,
`repo_paths.py` and subdirectories; no `wordcount_v4.sh`). `BR-1` therefore has no in-repo enforcer under the
name the spec gives it. No backend module references word budgets.

### 0.4 Identifier namespaces (global, permanent, never reassigned)

The backend uses spec identifiers as **docstring/comment anchors only** — there is no identifier registry
type, no enum, and no validation of ID well-formedness anywhere in `vanguard/packages/`.

Identifier families actually appearing in `vanguard/packages/**/*.py`:

| Family | Present in code? | Evidence |
|---|---|---|
| `K-nn` | Yes, as comments/docstrings: `K-04`…`K-08`, `K-13`…`K-21`, `K-23`…`K-33`, `K-42`, `K-44`, `K-46`…`K-49` | `grep -roh 'K-[0-9]\{2\}' vanguard/packages` |
| `F-nn` | Yes, and **as a live enum**: `FailurePath` in `vanguard/packages/kernel/model.py:117-147` carries `F-01`…`F-25` **plus `F-21a`** as its string values | `kernel/model.py:119-147` |
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
| `CI-5` | `tools/wordcount_v4.sh` | **absent** |
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
| `C-11` | **Implemented.** `Occurrence.UNDETERMINABLE` (`kernel/model.py:100-105`), `FailurePath.UNDETERMINABLE = "F-22"`, preserved in `kernel/dispatch.py:353-357`; recovery controller at `runtime/ledger/recovery.py:124 RecoveryScanner` |
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
| `N-01` | Held structurally: model proposes (`agency/episode/engine.py:227`), kernel authorises (`kernel/dispatch.py:177`), adapter executes (`:296`), evaluator evidences (`runtime/root.py:934 _evaluate`) |
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

The 80/20 dual-track is **not** the in-tree ratio. Coding-specific code in `runtime/` totals roughly 1,900 LOC
across `coding_budget.py` (243), `coding_coordinator.py` (270), `coding_entrypoint.py` (514),
`coding_plan.py` (223), `coding_progress.py` (365), `coding_verification.py` (243), plus
`mock_coding_tape.py` (126) and `domain/ledger/coding_session.py` (103). The non-coding environment
(`adapters/environment/tableworld.py`) is 138 LOC.

The generality constraint is **mechanised** by `tools/check_core_changes.py` (tested by
`test/tools/test_check_core_changes.py`), which is the `ADR-0060` invariant: adding a domain must change zero
lines in `kernel/` or `agency/episode/`. `agency/episode/engine.py:319-333` carries an explicit comment that
its scope check names no verb, "so `ADR-0060` holds and adding a domain is still zero lines in this file."

However, coding-shaped concepts do reach `domain/`: `domain/ledger/coding_session.py:42
project_coding_session` is a domain-layer projection named for one environment.

### 1.10 Approved stack — decision level

| Area | Spec decision | As-built |
|---|---|---|
| Control plane | Python (`ADR-0063`) | **Matches.** 125 stdlib-first Python modules |
| Interaction client | TypeScript strict on Node | Present at `vanguard/clients/cli/` (out of scope here) |
| Wire contracts | JSON Schema 2020-12 normative | 38 artefacts in `schemas/v4/`; Python reader profile in `domain/wire/contracts.py`; a parallel TS source is referenced by `README.md:212` (`contracts.ts`) |
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
`runtime/root.py:934 HarnessSession._evaluate()` after `EpisodeEngine.run()` returns.

| Step | Spec owner | As-built symbol |
|---|---|---|
| observe | Environment adapter | `EpisodeEngine._view()` (`engine.py:398`) returns a dict of episode state; a real environment observation is an `fs.read` effect through the kernel |
| propose | Cognitive operator | `self._model.propose(view, tools, sampling)` (`engine.py:227`), wrapped by `runtime/root.py:483 _LayeredOperator.propose` which compiles L1–L5 first |
| authorise | Broker | `Kernel.dispatch` → `StandardPolicy.authorize` (`kernel/policy.py:72`) |
| effect | Environment adapter in the perimeter | `adapter.execute(request)` at `kernel/dispatch.py:296`, bridged by `runtime/root.py:321 _EnvironmentEffect` |
| receipt | Environment adapter | `AdapterOutcome` (`kernel/model.py:107`) in-kernel; `ports/environment.py:116 EffectReceipt` at the port |
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
| **Interaction** | `runtime/service/server.py` (Unix domain socket, 177 lines) + `runtime/service/service.py:74 RuntimeService`. The TS CLI is the client (out of scope) |
| **Cognition** | `agency/` — `episode/`, `context/`, `manifests/`. Co-located in the controller process |
| **Control** | `kernel/` + `runtime/governance/`. Co-located with Cognition |
| **Workload** | `adapters/sandbox/rootless.py` + `adapters/sandbox/worker.py`; UID 10001 per `containers/worker.Dockerfile` |
| **Evidence** | `adapters/evaluators/daemon.py`, UID 10002, SO_PEERCRED, image digest at handshake |
| **Evolution** | **No runtime component**, matching the Phase 0 expectation. `CandidateBuilt`, `CandidateAttested`, `CanaryPromoted`, `RollbackTriggered` are declared event kinds (`domain/ledger/events.py:98-102`) with **zero emitters** |

**Divergence — the evaluation trigger.** The spec assigns the Evidence plane ownership of the trigger: it
observes episode termination in the ledger and emits `EvaluationRequested`; "no episode can request its own
evaluation." As built, `runtime/root.py:934 HarnessSession._evaluate()` is called by the *runtime* immediately
after the episode returns, and it calls `bound.evaluate(RunRef(...), EvaluationProtocol(...))` directly. There
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
| `eventStore.append(ProposalProduced)` | `EpisodeEngine._emit_proposal` (`engine.py:441`) |
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
