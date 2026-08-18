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
