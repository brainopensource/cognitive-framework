# Frontend lock — TUI now, standalone GUI later, three lanes

Status: `RATIFIED — Tech Lead, frontend`  
Decision date: 2026-08-17  
Revision: 2.0  
Authority: top frontend law below `docs/main_v4/`. Does not amend VG-04, ADR-0062, or backend sprint gates.  
Supersedes: `frontend_final_plan.md` (extension-first, `vanguard-ide/**`, FE-B1–B8 — marked spent & VOID).

Backend freeze: `vanguard/packages/**`, `benchmarkings/**`, backend tools/CI, and `docs/main_v4/**` are not frontend write scope. All FE work consumes the existing daemon over the shipped vg.4-frame protocol.

---

## 1. Verdicts

| Prompt claim | Verdict | Meaning |
|---|---|---|
| Keep the Ink CLI / hexagonal client | **Extend** | Lane FE-2 deltas against `vanguard/clients/cli/**`. Do not rewrite. |
| `docs/front_v4/003` JSON-RPC / Ping / LedgerEvent / 4 MiB frames | **Replace** | That protocol is not implemented. Consumer note cites VG-04 + ADR-0062 + `server.py`. |
| Standalone Code-OSS fork or VS Code extension | **Void** | Extension-first (`vanguard-ide/**`, FE-B1–B8) is VOID. Code-OSS fork remains out of scope. Standalone GUI app is Phase 2. |
| Two lanes (CLI vs Extension) | **Reshape** | **Three parallel lanes**: FE-1 (`client-core`), FE-2 (`cli` TUI), FE-3 (`vanguard-gui` shell). |

---

## 2. Locked decisions (D1–D6)

| # | Decision | Rationale |
|---|---|---|
| D1 | **Wire protocol = vg.4 frames as implemented** in `vanguard/packages/runtime/service/server.py` and `vanguard/clients/cli/src/adapters/live.ts`. | Backend is frozen. A JSON-RPC 2.0 / `Ping` / `LedgerEvent` / 4 MiB-frame spec describes nothing that exists. Frame limit is 1 MiB (`MAX_FRAME_BYTES = 1024 * 1024`). No new verbs. |
| D2 | **TUI = keep the Ink stack and hexagonal layout** in `vanguard/clients/cli/`. Fix deltas; do not rewrite in a new framework. | Layering is correct. CLI presentation consumes `@vanguard/client-core`. |
| D3 | **IDE = future standalone GUI app (working name `vanguard-gui/` or `apps/desktop/`). Extension-not-fork is VOID. Code-OSS fork remains out of scope.** | A full Code-OSS fork is an unmaintainable multi-million line sync nightmare. A VS Code extension is constrained by extension APIs and carries IDE bloat. Standalone GUI app consumes `@vanguard/client-core` with slot-based architecture (Monaco, xterm PTY, xyflow event viewer). |
| D4 | **Three parallel FE lanes from day one, disjoint write scopes.** FE-1: `@vanguard/client-core`. FE-2: `vanguard/clients/cli/**`. FE-3: `vanguard-gui/**`. | One client core, two skins (TUI, GUI), plus headless (`vg --headless`). Never a third wire. Ink screens are not embeddable in GUI; GUI embeds terminal PTY running `vg` or directly calls `RuntimeClient`. |
| D5 | **`docs/front_v4/` is Proposed** until per-file ratification is recorded in this document. | The registry was never ratified. 003 contradicted VG-04 / ADR-0062 and the daemon. |
| D6 | **Backend gaps become Joint notes (J1–J5), not FE workarounds.** No client-side invention of RPCs, manifest schemas, or daemon entrypoints. | Do not silently fork the wire. |

---

## 3. Lane ownership & write scopes

| Lane | Role / Scope | Path | Must not edit |
|---|---|---|---|
| **FE-1** | **Core (TUI workstream — finishes CLI brain)**: Move/re-export contract, parse, `RuntimeClient`, live/replay/scenario, signer, run-view reducer, approvals app. | `vanguard/clients/client-core/` (or `vanguard/clients/cli/packages/core/`) | Daemon Python (`vanguard/packages/**`), GUI chrome, pack JSON |
| **FE-2** | **TUI product (finishes Ink CLI)**: Presentation only (`tui/`, `composition/`, `headless/`, `install.sh`). Live/headless `vg run`, honest J1 `not_available`, P0-4 approval prompt (`y/n/c`), `--demo` labelled `source: mock`. | `vanguard/clients/cli/**` | `client-core` internals (except import updates), `vanguard-gui/**`, pack files |
| **FE-3** | **GUI start (future IDE — thin, parallel)**: App shell scaffold (`vanguard-gui/**`), imports `@vanguard/client-core`, replay fixture run panel, placeholder slots (file tree, Monaco stub, xterm PTY stub, xyflow event viewer). | `vanguard-gui/**` (or `apps/desktop/`) | CLI TUI, core wire verbs, competitor IDE submodules |

**Parallel proof:** FE-3 develops against frozen `client-core` types + replay fixtures (`fixtures/*.jsonl`). FE-2 finishes Ink screens concurrently. Neither waits on the other.

---

## 4. GUI Slot Bind List (Phase 2)

The GUI is a modular slot-based app, **not a VS Code clone or competitor loop rewrite**:
- **Files/Tabs:** Monaco Editor or CodeMirror 6 + virtualized file tree; workspace root from `StartRun.repo`.
- **Terminal:** `@xterm/xterm` + native PTY (optionally running interactive `vg`).
- **Git:** Native `git` CLI runner; ledger remains source of truth.
- **Diff / Approve:** Monaco Diff Editor + existing `OperatorSigner` (RFC 8785 Ed25519) on `ApprovalRequested`.
- **Run / Budget / Trace:** `reduceRunView` + VG-04 envelopes (`BudgetCommitted`, `ObservationProduced`, `OperatorInvoked`).
- **Workflow Canvas:** `@xyflow/react` **ONLY as a passive visualizer of VG-04 event streams** — never a second agent DAG engine.

**Out of v0.4.3 GUI scope:** In-memory vector DB, RAG pipelines, Obsidian graph clones, organic polymer workflows, MCP daemon bridges, playbooks.

---

## 5. Joint notes (backend requests — not FE work)

| ID | Request | FE until Joint lands |
|---|---|---|
| J1 | Daemon self-launch entrypoint (`python3 -m vanguard.packages.runtime.service.server` currently has no `__main__`) | FE-2 / FE-3 ship `not_available` with actionable text; no fake daemon lifecycle |
| J2 | `Ping` / health verb (supervisor probe is connect-only today) | Status remains connect-or-fail; do not invent a health frame |
| J3 | `ListManifests` verb | Selector ships with user-provided manifest path only; FE must not read `vanguard/packages/` |
| J4 | Populated approval challenge digests | Signer signs only fields present on the challenge; empty placeholders are forbidden |
| J5 | Wire-change wishes (e.g. Windows Named Pipe transport) | File the note; no FE-side transport invention |

---

## 6. Ratification log for `docs/front_v4/`

| File | Disposition (2026-08-17) | Ratified |
|---|---|---|
| `001` backlog | Revised: FE-1 / FE-2 / FE-3 IDs; extension epic voided; standalone GUI Phase 2 | No |
| `002` architecture | Revised: INVAR-FE-01..04 kept; trees: `client-core`, `cli`, `vanguard-gui` | No |
| `003` wire consumer | vg.4-frame consumer note (no JSON-RPC, 1 MiB frame limit) | No |
| `004` UI/UX | Revised: VG-04 §12.2 event names; shared token names for TUI and GUI | No |
| `005` manifests | Path-only discovery; daemon discovery is J3 | No |
| `006` RuntimeClient | Re-homed to `@vanguard/client-core` interface | No |
| `007` testing | Pyramid: unit → VG-04 vectors → replay E2E → live E2E; no `.vsix` | No |
| `008` packaging | Channels 1–2 for `vg`; standalone GUI desktop installer Phase 2 | No |
| `009` IDE | **Rewritten**: Vanguard GUI — standalone app, extension void, fork deferred; slots table | No |
| `010` phase 4 | Phase-4+ (RAG, enterprise graphs) one-pager | No |
| `011` demo | Real fixtures (`source: mock`), shared between TUI and GUI | No |
| `012` ADRs | D3 = standalone GUI; extension ADRs voided; D1–D6 locked | No |

---

## 7. Explicitly thrown away

- VS Code extension approach (`vanguard-ide/**`, FE-B1–B8, CodeLens-as-plan) — **VOID**.
- Code-OSS 2M-line full fork as current work.
- Invented JSON-RPC 2.0 / `Ping` / `LedgerEvent` / 4 MiB frames.
- Embedding Ink components inside React/GUI (Ink is terminal-only; reuse is `client-core` + PTY).
- Submoduling competitor loops (OpenCode, Cline, Void, PearAI).

---

## 8. Product surfaces (implementers)

| Skin | Spec | Lane |
|---|---|---|
| Ink TUI (Claude-class operator loop) | `tui_product_surface.md` | FE-2 |
| Standalone GUI (slot IDE) | `gui_ide_slots.md` | FE-3 |
| Shared brain | `@vanguard/client-core` | FE-1 |
| Implementer start | `frontend_implementer_playbook.md` | all |

