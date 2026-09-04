---
id: electroweak-sota-development-plan
class: agent-execution-runbook
authority: execution-runway-foundation
status: draft
owner: engineering-architecture-council
version: "0.9.3"
date: "2026-09-04"
supersedes: ["development-plan-guidelines-0209 v1.0.0"]
companion: [".draft/ELECTROWEAK_SYNTHESIS_FINAL_v093.md", ".draft/todo/ELECTROWEAK_SYNTHESIS_SOTA_CODING_HARNESS_ENGINEERING_ROADMAP.md"]
verification_basis: "working tree at feat/strongforce_beta_release_v093, HEAD 537bdb66"
---

# ELECTROWEAK SYNTHESIS DEVELOPMENT PLAN & AGENT RUNBOOK — v0.9.3

This is the canonical, self-contained implementation runbook designed for autonomous coding agents. It prioritizes core backend implementation, targeted falsifiers, runtime correctness, and strict adherence to the **Electroweak Synthesis of Record (`ELECTROWEAK_SYNTHESIS_FINAL_v093.md`)**.

Your objective is to execute the remaining core backend packages for Vanguard / AETHER, transforming the Coding Max product path into an industrial-grade, fail-closed coding harness.

---

## 1. Non-Negotiable Operating Rules

1. **Do not run any Git command**:
   Forbidden examples include `git status`, `git diff`, `git commit`, `git checkout`, `git add`, `git branch`. Use direct filesystem inspection, linters, and python test runners.
2. **Do not create new Markdown files under `docs/` or `docs/plans/`**:
   All architectural updates must strictly edit existing canonical files in the documentation runway (`docs/execution/{tasks,milestones,backlog,spec}.md`).
3. **Preserve Hexagonal Boundary Lattice**:
   `domain ← ports ← kernel ← agency ← runtime → adapters` (with `apps/` as a client of runtime). Adapters must NEVER import `kernel` or `agency`.
4. **Enforce Kernel TCB Budget ($\le 1438$ logical LOC)**:
   The production kernel currently stands at **1,386 LOC** across 9 files (52 lines of headroom). All new features (AST checks, SQLite queries, git operations, dialect parsers) must reside strictly in `adapters/`, `domain/`, `agency/`, or `runtime/`. Headroom is not a budget to spend.
5. **One Canonical Production Runtime**:
   The supported product path is strictly:
   $$\text{CodingMaxFacade} \to \text{ApplicationService} \to \text{HarnessSession} \to \text{EpisodeEngine} \to \text{Kernel mediated effects} \to \text{adapters}$$
   Do not make `ForgeEngine`, `ChimeraEngine`, or outer directors alternative production runtimes.
6. **Two-Axis Settlement Law**:
   Never conflate the run-termination axis (`RunTermination` in `agency/`) with the evaluation outcome axis (`TaskDisposition` in `domain/evidence/disposition.py`). An agent that solves a task and exhausts turns saying so settles honestly as `terminal=abandoned` AND `disposition=passed`.
7. **Empirical Gate & Hard Veto**:
   **False-completion rate = 0** is an unbendable veto. No pass rate, token efficiency, or speed advantage can override an unverified or misreported pass.

---

## 2. Authoritative Reading Order

Before editing any production code, verify context against:
1. `AGENTS.md` (Operational rules and anti-sprawl invariants)
2. `dev_context_logs/context_summary.md` (Current gate headroom and test status)
3. `.draft/ELECTROWEAK_SYNTHESIS_FINAL_v093.md` (Authoritative Synthesis of Record)
4. `.draft/todo/SOTA_CODING_HARNESS_ENGINEERING_ROADMAP.md` (Architectural Blueprint)
5. `docs/execution/spec.md` (The Law & delta contracts)
6. `docs/execution/tasks.md` (Tasks T-69 through T-97)
7. `docs/execution/milestones.md` (Target outcomes and release gates)
8. `docs/execution/backlog.md` (Package inventory)

Reverse-route documentation obligations for modified files using:
```bash
python3 tools/docs_rag_v0.py --file <path>
uv run lda callers "<SymbolName>"
```

---

## 3. Primary Implementation Targets & Path Canonicalization

Every path below is verified against working tree HEAD `537bdb66`:

* **Domain**:
  * `vanguard/packages/domain/evidence/disposition.py` (**NEW** — Two-Axis Settlement, T-72)
  * `vanguard/packages/domain/evidence/__init__.py` (Export surface)
  * `vanguard/packages/domain/models/profile.py` (Explicit `ToolCallStyle.NATIVE` profiles, T-69)
  * `vanguard/packages/domain/task_state.py` (`SemanticTaskState`, `StepState`, `TaskStep` — T-09, 396 LOC, reuse existing!)
* **Agency**:
  * `vanguard/packages/agency/episode/engine.py` (Anti-thrashing oscillation breaker, T-80)
  * `vanguard/packages/agency/episode/state.py` (`RunTermination` axis kept isolated)
  * `vanguard/packages/agency/context/compiler.py` (L3 breakpoints & Trailing Goal Echo, T-77)
  * `vanguard/packages/agency/context/compaction.py` (CTRF test distillation)
  * `vanguard/packages/agency/manifests/vg-code-{default,fast,balanced,max}/` (Declare `finish-tool.json`, T-71)
* **Runtime**:
  * `vanguard/packages/runtime/entrypoint.py` (UUID run identities, T-84; receipt telemetry passthrough, T-85)
  * `vanguard/packages/runtime/session.py` (Exempt set removal :134, T-04; approval policy :656, T-70; wire `tamper_shield` :1655, T-18; caller admission in Wave 3, T-83b)
  * `vanguard/packages/runtime/ledger_emitter.py` (`VerdictRecorded` settlement payload, T-72)
  * `vanguard/packages/runtime/governance/tamper_shield.py` (Wire into session, T-18)
* **Adapters & Packs**:
  * `packs/code-default/` (Located at **repo root**; purge `ollama`, resolve `$FRONTIER` in `harness.yaml`, T-91)
  * `packs/code-default/presets.json` (Unified preset catalog, T-79)
  * `packs/code-default/system-prompt.txt` (Deconflict greenfield prompt heuristics, T-83a)
  * `vanguard/packages/adapters/models/openrouter.py` (Pass live `aliases.json`, T-86)
  * `vanguard/packages/adapters/models/dialect.py` (Recover fenced JSON action notes, T-82; raw CAS digest, T-90)
  * `vanguard/packages/adapters/stores/lda_index.py` (**NEW** — `LdaRepoIndex` adapter over `.lda/index.db`, T-75)
  * `vanguard/packages/adapters/environment/transaction.py` (2PC atomic rollback & exact `str_replace`, T-78)
  * `tools/llama_cpp/cli.py` & `mcp_server.py` (Fail-closed bridge lifecycle, T-87, T-88)

---

## 4. Phased Implementation Runway (Waves 1 to 5)

Implement work in strict dependency order. Lane A (build) and Lane B (audit/test) must touch disjoint file sets.

### WAVE 1 — SETTLEMENT & SIGNAL TRUTH (P0, Route R)
**Goal**: Make the agent capable of calling native tools, executing 2PC edits, and terminating gracefully—then hold it to truth on both axes. All items are **Route R (Repair)** of verified defects.

1. **Native Tool Profiles (T-69)**:
   Add explicit `ToolCallStyle.NATIVE` in `domain/models/profile.py` only for verified models. Unverified models must preserve the safe fallback chain (`NATIVE → JSON_SCHEMA → FENCED_JSON → TEXT_GRAMMAR`).
2. **Approval Threshold Passthrough (T-70)**:
   Modify `runtime/session.py:656` to read `components.approval_policy` from the manifest instead of the hardcoded `"low"`.
3. **Declare Finish Tool (T-71)**:
   Create flat `vg-code-default/finish-tool.json` at manifest root and register under `components.tools` across `vg-code-{default,fast,balanced,max}`.
4. **Two-Axis Settlement Contract (T-72)**:
   Create `domain/evidence/disposition.py` defining `TaskDisposition` (`passed`, `failed`, `undeterminable`, `not_run`) and `SettlementReceipt`. Record onto `VerdictRecorded` without adding new ledger event kinds. Falsifier: `SettlementReceipt(disposition=PASSED, executed_test_count=0)` raises `DispositionError`.
5. **Remove Admission Gate Exemption (T-04)**:
   Purge `ADMISSION_GATE_EXEMPT = frozenset({"vg-code-default", "vg-code-lex"})` from `runtime/session.py:134`. Every mutating composition must be admission-gated automatically.
6. **Wire TestTamperShield (T-18 REOPENED)**:
   Wire `runtime/governance/tamper_shield.py` into `session._admit_completion`. Reject completion fail-closed if test files were mutated or deleted during the run.
7. **Greenfield Vacuity Rejection (T-81)**:
   Add vacuity check in `packs/code-default/oracles/gate.py`. A test suite passing on empty stubs (containing only `pass` or `raise NotImplementedError`) is rejected fail-closed (`VACUOUS_ORACLE_REJECTED`).
8. **Fenced-Action Dialect Recovery (T-82)**:
   In `adapters/models/dialect.py`, unpack markdown-fenced JSON action blocks within `note` payloads into candidate tool proposals. Strictly reject unsolicited `finish` proposals when notes contain unparsed tool invocations or when zero mutations have occurred.
9. **Greenfield Prompt Modernization (T-83a — Zero Dependencies)**:
   Purge *"Write ONE file per turn... Do not read or search first"* from `packs/code-default/system-prompt.txt`. Replace with normative 3-phase greenfield protocol (scaffold stubs $\to$ red test falsifier $\to$ atomic 2PC commit). Note: Caller admission (`T-83b`) is decoupled to Wave 3 following `IndexPort` adapter landing.
10. **Unique Durable Run Identity (T-84)**:
    Replace hardcoded `"run-cli"` in `runtime/entrypoint.py:56` with generated UUID/ULID identities. Explicit `--resume <id>` is the sole continuation route.
11. **Bridge Fail-Closed Lifecycle (T-87, T-88, T-91)**:
    Fix `--flash-attn` flag in `tools/llama_cpp/cli.py`, verify child PID and `/props` model match before declaring `ONLINE`, and return typed errors on empty completions. Purge `ollama` from `packs/code-default/harness.yaml`.

---

### WAVE 2 — FROZEN CONTROL, PRESETS & MEASUREMENT HONESTY (P0, Route R Control)
**Goal**: Establish the qualified, content-addressed control subject before measuring optional treatments.

1. **Unify Preset Catalog (T-79, Route R)**:
   Update `apps/coding_max/facade.py` to load from `packs/code-default/presets.json` (`$0.05`/8t, `$0.15`/20t, `$0.40`/40t) and eliminate the hardcoded `max_turns: int = 40` default.
2. **Product Receipt Telemetry Passthrough (T-85, Route R)**:
   Wire actual `modelRoutes`, token counts, `verifiedStepIds`, and cost provenance from `compose.py` / `app_service.py` into the receipt emitted by `runtime/entrypoint.py:218`.
3. **Execute Benchmarks Through Product Path (T-89, Route R)**:
   Change `benchmarks/agentic_harness_matrix_benchmark.py:98` to execute via `runtime.entrypoint.execute` rather than calling `Runtime.execute_profiled` directly.
4. **Measurement Ladder & Hypothesis Registry (T-92 to T-95, EXP-01, Route R)**:
   Implement Rung L0 smoke triad (`P0-FIB`, `P0-CSV`, `P0-BUG`), Rung L1 twelve-task pre-canary, and the append-only evidence row schema. Enforce **false-completion rate = 0** as a hard gate.
5. **MS-CONTROL Gate Qualification**:
   Qualify `vg-code-balanced` on the frozen canary suite ($N \ge 30$, Wilson LB $\ge 0.40$) executed through the product path.

---

### WAVE 3 — EDIT PRIMITIVE & RETRIEVAL TREATMENTS (P1, Route L Treatments)
**Goal**: Evaluate surgical editing, LDA repository intelligence, and caller admission as modular treatments over the qualified Wave 2 control. All items are **Route L (Lift)** treatments preregistered in `benchmarks/hypotheses.json`.

1. **Exact-Match `str_replace` Primitive (T-78, Route L)**:
   Implement exact string replacement in `adapters/environment/git.py` routed through `adapters/environment/transaction.py`. Preimage must be unique; trimmed-EOL matching only; zero fuzzy cascades.
2. **`LdaRepoIndex` Adapter (T-75, Route L)**:
   Create `adapters/stores/lda_index.py` satisfying `IndexPort` over `.lda/index.db` (80,618 relations). Missing or stale database returns deterministic `Result.fail`.
3. **L5-Only Observation Verbs (T-76, Route L)**:
   Expose `repo.{search_symbols,get_callers,get_dependencies,get_tests}` in `packs/code-default/toolkits/repo_map.py` bound strictly into L5 observations, leaving L1–L3 cache prefix intact.
4. **Cross-File Caller Admission (T-83b, Depends on T-75)**:
   Wire `IndexPort.get_callers` into `runtime/session.py::_admit_completion` and pass reverse call graph to `agency/multi_file_completeness.py`, preventing completion when public API signatures change without inspecting dependent call sites.
5. **Live Manifest Alias Validation (T-86, Route R)**:
   Pass manifest `aliases.json` map into `ProposalTranslator.translate` on the live path (`adapters/models/openrouter.py:1204`). Validate tool name and arguments against declared schemas; reject undeclared tools fail-closed.
6. **Raw-Response CAS Digest Provenance (T-90, Route R)**:
   Store raw unparsed model completions in CAS by SHA-256 digest and emit typed normalization classifier classes into the event stream.

---

### WAVE 4 — CONTEXT ECONOMY & RELIABILITY TREATMENTS (P1, Route L Treatments)
**Goal**: Maximize context token efficiency and prevent livelock loops on long-horizon runs.

1. **Context Economics & Trailing Goal Echo (T-77, Route L)**:
   Emit provider cache breakpoints at the L3 boundary. Parse test tool outputs into CTRF format (strip passing traces, cap assertion diffs $\le 1500$ chars). Inject Trailing Goal Echo at tail of L5 on turns $\ge 30$.
2. **Anti-Thrashing Workspace Oscillation Breaker (T-80, Route L)**:
   In `agency/episode/engine.py`, if workspace file-tree digest oscillates ($d_t == d_{t-2}$), trip the circuit breaker and return typed `OSCILLATION_CIRCUIT_BREAKER` diagnostic, forcing an alternative hypothesis.

---

### WAVE 5 — OUTER DIRECTOR & TEST-TIME COMPUTE (POST-MS-CONTROL, Route L)
**Goal**: Multi-candidate speculative execution and tournament ranking. Gated strictly on `MS-CONTROL` closed.

1. **Campaign Director as Runtime Client (OCT-03, Route L)**:
   Director holds **zero** mutating tools. Parallel candidate episodes execute in isolated git worktrees.
2. **Recursive Tournament Voting (RTV)**:
   RTV may allocate compute and rank candidate patches, but merge authority belongs exclusively to the bound `ExternalVerifier` test verdict, never model votes.
3. **Comparative Arm Program (ARM-01, T-96, Route L)**:
   Evaluate (manifest × model × preset) triples across the frozen corpus.

---

## 5. Procedural Evidence Standard & Governance

* **Route R (Repair)**: Resolves defects verified in current source at a named file and line. Falsifier is a deterministic regression test.
* **Route L (Lift)**: Optimization treatments (T-75 LDA, T-78 exact replace, T-80 circuit breaker, ARM-01). Must state hypothesis, control digest, and single varied dimension in `benchmarks/hypotheses.json`. Evaluated against the Wave 2 control. A negative lift moves the treatment to `DEFERRED` with configuration retained—never deleted.
* **Opus Preservation Register**: 12 viable Opus idea families (§2.1 of Synthesis of Record) are maintained as testable candidate treatments rather than duplicate engines or forked manifests.

---

## 6. Architectural Invariants to Verify

* **Invariant I-1 (Monotonic Attenuation)**: Child subagents never gain capabilities absent from their parent.
* **Invariant I-6 (Subprocess Isolation)**: All shell and test executions run inside rootless Bubblewrap sandboxes (`adapters/sandbox/`).
* **Invariant I-7 (TCB Domain Blindness)**: Kernel contains zero AST, zero SQLite, and zero pack-specific heuristics. LOC $\le 1438$.
* **Invariant I-8 (Multi-File Closure)**: Modified public API signatures must not complete without inspecting all dependent call sites.
* **Two-Axis Invariant**: `EpisodeCompleted` event payload contains NO disposition field; `VerdictRecorded` payload carries `SettlementReceipt` with independent `terminalStatus` and `disposition`.

---

## 7. Verification Commands & Targeted Falsifiers

Run only focused falsifiers during development loops:

```bash
# Verify TCB Budget & Boundaries
python3 tools/linters/check_tcb_budget.py
python3 tools/linters/check_boundaries.py
python3 tools/linters/check_domain_blindness.py

# Wave 1 Falsifiers
python3 -m unittest test.contracts.test_settlement_disposition -v
python3 -m unittest test.runtime.test_approval_passthrough -v
python3 -m unittest test.contracts.test_manifest_components -v
python3 -m unittest test.adapters.test_dialect_fenced_action_recovery -v
python3 -m unittest test.runtime.test_run_identity -v
python3 -m unittest test.tools.test_llama_bridge_lifecycle -v

# Wave 2 Falsifiers
python3 -m unittest test.apps.test_preset_budgets -v
python3 -m unittest test.runtime.test_receipt_telemetry -v
python3 -m unittest test.benchmarks.test_product_path_subject -v
python3 -m unittest test.benchmarks.test_l0_triad -v
python3 -m unittest test.benchmarks.test_metric_veto -v

# Wave 3 Falsifiers
python3 -m unittest test.adapters.test_str_replace_exact -v
python3 -m unittest test.contracts.test_lda_repo_index -v
python3 -m unittest test.agency.test_l5_only_observations -v
python3 -m unittest test.runtime.test_multi_file_callers_admission -v
python3 -m unittest test.adapters.test_live_alias_validation -v
```

---

## 8. Definition of Done

A wave or task is complete only when:
1. Production code strictly respects the hexagonal lattice and kernel LOC budget ($\le 1438$ lines).
2. Corresponding unit and contract test falsifiers pass hermetically.
3. Relevant task IDs in `docs/execution/tasks.md` and gates in `milestones.md` are marked updated with exact SHA evidence.
4. No Git command was executed.
5. No unsupported SOTA or benchmark claim was made.
