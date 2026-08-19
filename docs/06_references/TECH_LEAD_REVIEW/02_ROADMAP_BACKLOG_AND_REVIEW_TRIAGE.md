# 02 — ROADMAP, BACKLOG & REVIEW TRIAGE: Realignment to MHF v1 (M0–M6)

**Authority:** `CRITICAL_GAP_ANALYSIS_AND_AUDIT.md` + `NEXT_GEN_META_HARNESS_SPECIFICATION.md` (SPEC).
**Replaces:** `docs/02_roadmap/backlog.md` (1,184 ln, TSK-* corpus), `docs/02_roadmap/milestones.md` (734 ln, v0.5.0→v1.0.0 ladder), and triages `docs/reviews/{doing,todo}/`.
**Standing rule:** an item enters v0.5.0 only if it lands in **Layer 0**, the **plugin runtime**, or the **Phase-1 Coding Pack**. Everything else is a Phase-2/3 plugin (with a named target) or dead.

---

## 1. Governing decision: the v0.4.x board is superseded, not migrated

`sprint_active.md` (the v0.6.0 "Molecular Lattice" board) prescribes closing the open G-050 rows on the v0.4.x codebase *before* extraction ("do not extract `coding_*` until Wave 0 makes the ledger tell the truth"). Under the MHF plan this sequencing is **inverted and the per-row patches are cancelled**:

- **Why:** M1 rebuilds the emission layer wholesale under E-COV=100% and `replay-parity`. Patching `EVENT_KINDS` enforcement, heartbeats, and grant/budget kinds into the v0.4.x writer (TSK-LED-001/004/005) and then porting the writer is double implementation of the weakest kind — each open TSK row is a strict subset of an M1 acceptance criterion. `replay-parity` is a stronger gate than the union of the five open rows.
- **The v0.6.0 board's own risk** ("a thinner runtime on a lying session") is answered differently: nothing thins the runtime until the *new* ledger is proven honest (M1 exits before M3 extraction begins), which is the same principle at a stronger fixpoint.
- **Exception:** work that is codebase-independent or already landed closes in place. **Closed and carried:** TSK-CORE-001/002/003/004 (spans, child_return, operator span, child `AuthorizationDenied` — all `[DONE]` on the board; the semantics port with the kernel), TSK-LED-002/003 (`EpisodeStarted`, `ApprovalResolved` — `[DONE]`; re-proven under E-COV), TSK-CTX-001/002, TSK-HAR-001/002/004, TSK-CLI-001, TSK-DOC-001/002. **Closes in M0 regardless of codebase:** SEC-01 (git-history secret purge — rides the M0 `git filter-repo` pass with the artifact purge).

Frontend wave (**TSK-FE-008/009/030–037/J1–J4**) — **KILLED wholesale** per scope mandate; `vanguard-gui/`, `vanguard-ide/`, and Ink-chrome work leave the repo in M0. The daemon keeps emitting the generated client contract (SPEC A-4); clients live elsewhere.

---

## 2. Review triage

### 2.1 `reviews/todo/001_features.md` — Competitor Feature Harvest

| Item | Verdict | Target & rationale |
|---|---|---|
| **Aider tree-sitter repo map** | **ACCEPTED — Phase 1 (M3)** | `mhf.context.repo-map` plugin (SPEC §4.2). Audit names this the highest-leverage product-axis buy-back (context-rot counter, D-37). |
| **Claude Code subagent context isolation (`Task`) + compact-on-overflow** | **DEFERRED — Phase 2** | Isolation-by-spawn: scheduler `ChildSpawned` (M1) carries the mechanism; the *policy* (when to spawn a sub-context, compact-on-overflow strategy) is `mhf.planner.meta-reflector` + `IContextManager.compact(pressure)` config — SPEC §5.1. |
| **mini-SWE-agent: 100-line paginated viewer, lint-on-edit receipts, empty-exec acks** | **ACCEPTED — Phase 1 (M3)** | Pure receipt-shaping inside `mhf.toolkit.fs` / `mhf.toolkit.terminal`. Cheap, high yield for small models, zero core surface. |
| **OpenCode: `AGENTS.md` context injection, provider-agnostic CLI, permission UX** | **ACCEPTED (partial) — Phase 1** | `AGENTS.md` discovery already exists (`manifests/discovery.py`) — ports into pack loader (M3). Provider-agnosticism is the `IModelProvider` SPI itself (M2). Permission **UX** is frontend → killed; the backend truth (`ApprovalRequested/Resolved` events) is M1. |
| **Pi lean pack (<1k-token prompt, 4 primitives)** | **ACCEPTED — Phase 1 (M4)** | `code-pi-shaped` harness manifest — **pure data, zero code**, and the cheapest generality witness for the harness compiler (SPEC A-5). Joins the M4 parity set. |
| **Reasonix skills-in-frozen-prefix + cache-miss attribution** | **ACCEPTED — landed/Phase 1** | `format_skill_index` in L3 already `[DONE]` (TSK-CTX-002); prefix-attribution telemetry exists in `tools/telemetry/` and wires in M1 (with M-18). |

### 2.2 `reviews/todo/002_features_pi.md` — Pi Architecture Reference

| Item | Verdict | Target & rationale |
|---|---|---|
| Ultra-lean cold start (<1k system-prompt tokens) | **ACCEPTED — Phase 1 (M4)** | Manifest data; measured by the lab as a paired arm vs `code-default` (prompt-tax experiment falls out of the harness-digest attribution for free). |
| **Non-destructive DAG session state (`id`/`parentId` JSONL tree, `/fork`, `/clone`)** | **ACCEPTED (mechanism) — Phase 1 (M1)** | The ledger already carries `causation_id`; SPEC §1.3 defines branch-resume ("fold to seq=N + divergent branch id"). M1 makes `branch_id` a first-class envelope field. The `/fork` *command surface* is a client concern → out of scope. |
| Differential context folding (Ctrl+O) | **DEFERRED — Phase 2** | `IContextManager` capability `"folding"`: large receipts held as blob refs, unfolded on demand. Needs the receipt→blob path (M1) first. |
| Decoupled async steering queue (Enter / Alt+Enter) | **REJECTED for v0.5.0** (mechanism noted) | Interactive-client feature; the backend half already exists (`ServiceInboxStore`, idempotent commands, D-17 kept). Revisit when a client repo exists. |
| **Four-protocol wire normalization (OpenAI Completions/Responses, Anthropic Messages, Google GenAI)** | **ACCEPTED — Phase 1 (M2/M3)** | Design constraint on `IModelProvider` adapters: one internal typed message shape, four transport codecs. Replaces per-provider ad-hoc `invocation.py` formatting. |

### 2.3 `reviews/todo/003_features_meta.md` — Capability Gap Matrix

| Item | Verdict | Target & rationale |
|---|---|---|
| Real-time tool-use streaming on ModelPort | **DEFERRED — Phase 2** | SPI capability negotiation: `IModelProvider.capabilities() ⊇ {"streaming"}`; scheduler consumes incrementally. Not needed for Phase-1 acceptance (structured first-failure streaming in the terminal toolkit covers the latency-critical path, SPEC §4.3). |
| LSP integration | **DEFERRED — Phase 2** | `mhf.toolkit.lsp` plugin (subprocess tier, daemon-per-language). Named early because its receipts (diagnostics) feed the repo map. |
| **AST-aware editing** | **ACCEPTED — Phase 1 (M3)** | Already core to the plan: `mhf.toolkit.ast-patch` (SPEC §4.1). |
| Filesystem watching (inotify daemon) | **DEFERRED — Phase 2** | M3's Merkle index is *receipt-driven* (invalidation on effect), which is deterministic and replay-safe; inotify adds nondeterminism for a benefit that only matters with concurrent external editors. Reversal condition: a live co-editing use case. |
| Multimodal/image input | **DEFERRED — Phase 3** | Wire-schema extension + provider capability; no Phase-1 consumer. |
| Interactive diff preview & approval UI (Ink TUI) | **REJECTED** | Frontend purge. Backend truth = approval events + patch blob refs. |
| **Directive: harness strategy sovereignty** (manifest declares execution strategy) | **ACCEPTED — Phase 1 (M2)** | This *is* the `planner:` ref in `harness.yaml` (SPEC §2.3). Closes the request exactly. |
| **Directive: playbook rigidity dial** (`advisory→guided→strict`) | **DEFERRED — Phase 2** (strict tier **REJECTED**) | `advisory` = skill cards (exists) + harvested playbook *data* (SPEC §5.4, matches TSK-EPIC-060-006 "data, no dispatch"); `guided` = a planner-plugin policy. `strict` deterministic DAG execution is rejected — it reintroduces the workflow runtime that handbook-M1 and the loop-over-DAG inversion (VG-03 §2) exist to prevent, and N-20's prohibition is carried into the ADR log. |

### 2.4 `reviews/todo/004_features_meta_dags.md` — Emergent DAGs & Decoupling

| Item | Verdict | Target & rationale |
|---|---|---|
| Emergent DAGs philosophy (playbooks from practice, not hardcoded state machines) | **DEFERRED — Phase 2** | Exactly SPEC §5.4 dynamic skill synthesis: harvest → candidate playbook data → §5.2 selection pipeline. No playbook *runtime* ever (see 2.3). |
| **Decoupling directive 1: `runtime/` = composition + session only; `coding_*` out** | **ACCEPTED — Phase 1 (M3)** | Verbatim the M3 extraction (audit D-42, TSK-EPIC-060-001). |
| **Decoupling directive 2: merge 3 model-selection paths into one policy** | **ACCEPTED — Phase 1 (M3)** | Single router: `model_selection.py` + `tier_escalation.py` + coordinator routing collapse into `mhf.planner.drive-until-green` policy + `IModelProvider` routing table (TSK-EPIC-060-002; also RT-01 from `doing/`). |
| Decoupling directive: fakes out of production entrypoints | **CLOSED** | TSK-CLI-001 `[DONE]`; re-enforced structurally in M2 (fakes are plugin-manifest `isolation: in_process` test doubles under `test/`). |

### 2.5 `reviews/doing/` — Active items

| Item | Verdict | Target |
|---|---|---|
| **[SEC-01]** git-history secret blob | **ACCEPTED — M0** | Rides the single `filter-repo` pass (with artifact purge). Acceptance: `scan_secrets.py --all-refs` green. |
| **[M-18]** instrument tuple unwired | **ACCEPTED — M1** | Trajectory record at `EpisodeCompleted` *is* the tuple's landing site (SPEC §7); closes with E-COV. |
| **[C-3]** implement \(G_C/G_E\) graphs (from `000_doing`/`001` directives) | **DEFERRED — Phase 3** | Contradicts `milestones.md` §3.4's own exclusion list and SPEC §9. Target: `mhf.memory.graph` (SPEC §6.1), gated on the activation-bundle rule (I-3). |
| **[H-1]** manifest loader fail-fast on unknown aliases | **ACCEPTED — M2** | `compose()` v2 rejects unknown refs/aliases at composition (SPEC §2.3 already mandates; make it an M2 acceptance test). |
| **[H-2]** wire `context_policy.json` into ContextCompiler | **ACCEPTED — M3** | Becomes `IContextManager` plugin config — the policy that is hashed must be the policy that executes (a mini-AP-5). |
| **[REC-01]** recursive spawning with context isolation | **SPLIT** | Mechanism (depth in `Reservation`, `ChildSpawned/Returned` with provenance) = **M1**; recursion *policy* (when/what to delegate) = **Phase 2** `meta-reflector`. Depth>1 stays off until CC-6-class events can be measured (audit D-38 discipline). |
| **[RT-01]** wire `routing.py` | **ACCEPTED — M3** | Absorbed into the single-router task (2.4). |
| `001_doing.md` v0.4.5 harness guide (S28–S34 rows: structured plan, coordinator, progress fingerprints, provider health, resume, CLI receipts, greenfield proof) | **SUPERSEDED — salvage mapped** | Plan/progress/verification → Pack #1 modules (M3); progress fingerprints → `no-progress detection` in planner (M3); provider health → `IModelProvider.health()` (M2 SPI, M3 impl); `--resume RUN_ID` → M1 replay/branch semantics; greenfield proof → Phase-1 acceptance gate (M3, un-mocked `oracle_green` carried from G-050-06); CLI receipts → killed (frontend). |
| `002_doing_advanced-plugin.md` local-model middleware (MultiActionUnpacker, think-tag stripper, budget middleware, heuristic pre-search) | **ACCEPTED — Phase 1 (M2 design / M3 impl)** | Becomes `mhf.model.local-adapter` — the **first third-party-shaped plugin** and the M2 lifecycle demo payload. Multi-action unpacking = provider-side decomposition into sequential single-effect proposals (preserves one-effect-per-turn at the kernel; the queue lives in the adapter). Think-tag stripping + budget middleware = adapter middleware chain. Heuristic pre-search → merged into repo-map (M3), not duplicated. |

**Triage totals:** 14 ACCEPTED (Phase 1), 9 DEFERRED (each with a named plugin target), 4 REJECTED/KILLED, 3 CLOSED-carried. Every DEFERRED entry lands in `docs/05_adr/DEFERRED_REJECTED.md` with a reversal condition.

---

## 3. `milestones.md` — rewritten

The v0.5.0→v1.0.0 ladder (v0.6 "Molecular Lattice", v0.7 benchmarking, v0.8 memory graphs, v0.9 meta) is replaced. **v0.5.0 = MHF v1 = M0–M6.** Former v0.8/v0.9 content maps to Phase-2/3 plugin milestones (v0.6.x/v0.7.x) and is not re-planned here beyond named targets.

| Milestone | Duration | Outcome | Exit gate (proof command) |
|---|---|---|---|
| **M0 — Excise & Sanitize** | 1 sprint | Docs collapsed per migration matrix; artifacts/secrets purged from history; frontend trees removed; repo ≤ 3 MB | `G-M0`: `scan_secrets.py --all-refs` PASS · repo-size check · docs gates (matrix §2) · CI still green on retained suite |
| **M1 — Layer 0** | 2 sprints | Kernel + events + JCS ported verbatim; full event taxonomy emitted; one generated `EffectRequest`; scheduler v1; six-dim `Reservation`; trajectory record | `G-M1`: **E-COV = 100%** · **`replay-parity`** green (grants, budgets, approvals, lifecycle reconstructed) · mutation score ≥ 80% on kernel+reducers · `pytest test/layer0` green |
| **M2 — Plugin Runtime** | 2 sprints | Registry, lifecycle FSM, isolation broker (`in_process`+`subprocess` w/ rlimits+seccomp), SPI v1, `compose()` v2, walking-skeleton echo plugin, `mhf.model.local-adapter` demo | `G-M2`: echo plugin traverses DISCOVERED→RETIRED with full ledger trail · fault injection → `PluginFaulted` + fallback · hot-swap mid-run with attribution · compose() rejects unknown ref/alias (H-1) · grant-ceiling ∩ enforced |
| **M3 — Coding Pack #1** | 2–3 sprints | `apps/coding` + adapters extracted to plugins; ast-patch, repo-map, terminal (structured first-failure), fs/index toolkits; single router; container tier | `G-M3` (**Phase-1 acceptance**): compiled `code-default` ≥ v0.4.5 baseline on lab dogfood + `zero_hint_v1` under paired McNemar · un-mocked `oracle_green` on ≥1 greenfield task, live model, signed verdict (carries G-050-06 verbatim) · `grep -rE "coding|pytest|ast" layer0/` empty (I-7) |
| **M4 — Harness Parity** | 1 sprint | `code-claude-shaped`, `code-opencode-shaped`, `code-swe-mini`, `code-pi-shaped`, `table-default` recompiled as manifests | `G-M4`: 5 packs compile+run · `git diff --stat layer0/` = 0 across M4 · TableWorld registered (closes D-27/TSK-HAR-007) |
| **M5 — Phase-2 Plugins** | (v0.6.x) | meta-reflector, genome mutation + lab selection, calibrated escalation, skill harvest; **prerequisite: 200-task suite** (statistical-power gate from the audit synthesis) | `G-M5`: one promoted mutation beats baseline, McNemar p<0.05, A/A floor respected, preregistered |
| **M6 — Distillation Loop** | (v0.6.x) | Trajectory→DPO harvest; first fine-tuned tier-1 model behind cassette regression | `G-M6`: fine-tuned local model ≥ free-tier baseline pass rate at lower USD/episode |

**Preserved from old milestones §2 (invariants, all versions):** dispatch-only effect path (AT-01/A-01), one-effect-per-turn at the kernel, fail-closed evaluation, boundary lattice — restated in SPEC; TCB LOC tripwire replaced by the AP-8 metric triple. **§1.7 vision-tier mapping:** deleted (ADR-M0-10).

---

## 4. `backlog.md` — restructured (TSK → epic map)

Field schema kept (it's fine). Waves replaced by M-epics. Full disposition of the legacy corpus:

| Epic | Absorbs (legacy TSK) | Status |
|---|---|---|
| **EPIC-M0-DOCS** — spec collapse per matrix | TSK-DOC-001 (done, extended to vision.md), TSK-DOC-002 (done), all TSK-SPEC-001…011 (spec-amendment rows become ADR-M0-* entries or SPEC text — no separate patches to a dead corpus) | open |
| **EPIC-M0-PURGE** — history rewrite: secrets + artifacts + frontend trees | SEC-01; TSK-DOC-003 (`cryptography` in TCB list → ADR) | open |
| **EPIC-M1-EVENTS** — taxonomy, emitters, E-COV, envelope `branch_id` | TSK-LED-001…005, 008 (superseded per §1), TSK-LED-006/007 (keep: WAL store, inbox port verbatim), TSK-EVAL-001 (evaluation trigger → ledger listener, closes D-02), M-18 | open |
| **EPIC-M1-KERNEL** — verbatim port + provenance carried + six-dim Reservation + one EffectRequest | TSK-CORE-001…009 (001–004 done/carried; 005–008 become invariant tests; 009 → metric triple), TSK-EPIC-060-005 | open |
| **EPIC-M1-CI** — replay-parity, mutation gate, boundaries v2, control-call-site coverage, retargeted rule map | TSK-TEST-001/002/003 (bijection discipline, ADR-M0-01) | open |
| **EPIC-M2-REGISTRY** — plugin.yaml schema, resolver, lifecycle FSM, hot-swap | H-1 | open |
| **EPIC-M2-ISOLATION** — broker: in_process lint, subprocess RPC + rlimits + seccomp | TSK-SEC-001 (AT-12 or ADR-defer w/ compensating control — decide in M2), TSK-SEC-002 (seccomp lands here, not deferred), TSK-SEC-003/004 (probes: keep) | open |
| **EPIC-M2-SPI** — five protocols + `IModelProvider`/`ISandbox`/stores; codegen; 4-protocol wire normalization; walking skeleton (ADR-M0-13); `mhf.model.local-adapter` | 002_doing plugin design | open |
| **EPIC-M3-PACK** — coding extraction, ast-patch, repo-map, terminal, single router, ctx-policy wiring, live greenfield gate | TSK-EPIC-060-001/002/003, TSK-EPIC-070-001, TSK-HAR-001…006 (001/002/004 done-carried; 003 grant library keeps; 005 spend auth keeps; 006 schema-driven translator → absorbed by typed SPI), TSK-CTX-003/004 (keep: compiler + FrozenHarness port), H-2, RT-01, S28–S34 salvage | open |
| **EPIC-M4-PARITY** — five packs, TableWorld | TSK-HAR-007, TSK-EPIC-060-004 | open |
| **EPIC-P2/P3 (named, not planned)** — meta-reflector, genome+lab, folding, streaming, LSP, playbook-advisory, memory graph, market allocator | TSK-EPIC-060-006, 070-002, C-3, REC-01(policy), deferred rows §2 | deferred |
| **HONOUR TABLE (standing refusals)** | TSK-CORE-010 (measurement stays outside packages — lab remains sibling to `layer0/`), TSK-CORE-011 (no `MetaLoopEngine` — outer loop is a plugin at a scheduler slot, never an engine) + SPEC §9 items | permanent |
| **KILLED** | TSK-FE-* (all 14) | closed-kill |

Every accepted legacy row is closed with `superseded_by: <new-task-id>` in its final backlog commit — the audit trail survives even though the board doesn't.
