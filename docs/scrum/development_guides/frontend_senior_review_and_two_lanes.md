# Frontend lock — two lanes, CLI TUI now, IDE extension next

Status: `RATIFIED — Tech Lead, frontend`  
Decision date: 2026-08-16  
Revision: 1.0  
Authority: top frontend law below `docs/main_v4/`. Does not amend VG-04, ADR-0062, or backend sprint gates.  
Supersedes: the open “senior review / two lanes” prompt (this file is now the decision record).

Backend freeze: `vanguard/packages/**`, `benchmarkings/**`, backend tools/CI, and `docs/main_v4/**` are not frontend write scope. All FE work consumes the existing daemon over the shipped vg.4-frame protocol.

---

## 1. Verdicts

| Prompt claim | Verdict | Meaning |
|---|---|---|
| Keep the Ink CLI / hexagonal client | **Extend** | Lane FE-A deltas against `vanguard/clients/cli/**`. Do not rewrite. |
| `docs/front_v4/003` JSON-RPC / Ping / LedgerEvent / 4 MiB frames | **Replace** | That protocol is not implemented. Consumer note cites VG-04 + ADR-0062 + `server.py`. |
| Standalone Code-OSS “Vanguard IDE” fork now | **Replace** | Standard VS Code extension at `vanguard-ide/`. Fork is Phase-4+ reversal path only. |
| Sequential FE then IDE | **Reshape** | Two parallel lanes from day one. Shared freeze is contract + fixtures, already in-tree. |

---

## 2. Locked decisions (D1–D6)

| # | Decision | Rationale |
|---|---|---|
| D1 | **Wire protocol = vg.4 frames as implemented** in `vanguard/packages/runtime/service/server.py` and `vanguard/clients/cli/src/adapters/live.ts`. | Backend is frozen. A JSON-RPC 2.0 / `Ping` / `LedgerEvent` / 4 MiB-frame spec describes nothing that exists. |
| D2 | **TUI = keep the Ink stack and hexagonal layout** in `vanguard/clients/cli/`. Fix deltas; do not rewrite. | Layering is correct (no vanguard-package imports; boundary test exists). Problems are dead code and missing deltas. |
| D3 | **IDE = standard VS Code extension** at `vanguard-ide/` (webview panel + CodeLens + daemon bridge on the same socket). **No Code-OSS fork now.** | A fork is a multi-person maintenance program. An extension delivers the same operator UX and keeps lane B unblocked. Standalone IDE via a VSCodium-style Code-OSS build is a Phase-4+ productization option (reversal path in `docs/front_v4/009`). |
| D4 | **Two lanes, parallel from day one.** FE-A: `vanguard/clients/cli/**`. FE-B: `vanguard-ide/**`. | Dependency is the frozen client-side wire contract + replay fixtures (`src/contract/`, `fixtures/*.jsonl`, `adapters/replay.ts`). FE-B develops against replay/mock daemon. |
| D5 | **`docs/front_v4/` is Proposed** until per-file ratification is recorded in this document. | The registry was never ratified. 003 contradicted VG-04 / ADR-0062 and the daemon. |
| D6 | **Backend gaps become Joint notes, not FE workarounds.** No client-side invention of RPCs, manifest schemas, or daemon entrypoints. | Do not silently fork the wire. ROADMAP §0.2 rule 2. |

---

## 3. Lane ownership

| Lane | Path | Owner | Must not edit |
|---|---|---|---|
| FE-A | `vanguard/clients/cli/**` | CLI / TUI | `vanguard-ide/**`, `vanguard/packages/**`, `docs/main_v4/**` |
| FE-B | `vanguard-ide/**` | IDE extension | `vanguard/clients/cli/**`, `vanguard/packages/**`, `docs/main_v4/**` |
| Joint | notes only | Tech + Project Lead | FE does not implement J1–J5 |

Shared code (contract types, parse, signer) is **owned by FE-A**. FE-B consumes it by **vendoring** into `vanguard-ide/src/contract/` (build step; no monorepo runtime dependency). FE-B never edits the CLI tree and vice versa.

Parallel proof: FE-B1–B4 are completable against the FE-A-wave-1-start commit (fixture + contract freeze).

---

## 4. Navigator

| Artifact | Role |
|---|---|
| This file | Binding FE law (D1–D6, Joint notes, ratification) |
| `docs/scrum/ROADMAP.MD` | Navigator + FE-A / FE-B board (IDs, depends, DoD commands) |
| `docs/scrum/development_guides/cli_tui_architecture.md` | Binding CLI module tree, adapters, fixtures |
| `docs/front_v4/` | Proposed consumer notes (not VG-04) |
| `docs/scrum/sprints_front/` | Lane-tagged delta kits |

Sprint numbering is `FE-A-n` / `FE-B-n` waves. Do not reuse backend “Sprint 1–4” or `sprint07..10` IDs (ROADMAP §0.3).

---

## 5. Joint notes (backend requests — not FE work)

| ID | Request | FE until Joint lands |
|---|---|---|
| J1 | Daemon self-launch entrypoint (`python3 -m vanguard.packages.runtime.service.server` currently has no `__main__`) | FE-A7 ships `not_available` with actionable text; no fake daemon lifecycle |
| J2 | `Ping` / health verb (supervisor probe is connect-only today) | Status remains connect-or-fail; do not invent a health frame |
| J3 | `ListManifests` verb | Selector ships with user-provided manifest path only; FE must not read `vanguard/packages/` |
| J4 | Populated approval challenge digests | FE-A8 signs only fields present on the challenge; empty placeholders are forbidden |
| J5 | Wire-change wishes (e.g. Windows Named Pipe transport) | File the note; no FE-side transport invention |

---

## 6. `docs/front_v4/` ratification log

Until a row is `Ratified` here, the file header remains `Proposed`.

| File | Disposition (2026-08-16) | Ratified |
|---|---|---|
| `001` backlog | Revised: FE-A / FE-B IDs; Tauri / EPIC-09 / M4 soak removed | No |
| `002` architecture | Revised: INVAR-FE-01..04 kept; tree matches CLI; Named Pipe/TCP proposed | No |
| `003` wire consumer | **Rewritten** as vg.4-frame consumer note | No |
| `004` UI/UX | Revised: VG-04 §12.2 event names | No |
| `005` manifests | Revised: real schema; daemon discovery is J3 | No |
| `006` RuntimeClient guide | **Rewritten** from shipped interface | No |
| `007` testing | Revised: VG-04 vectors + `test/contracts/t1_wire_contracts.py` | No |
| `008` packaging | Revised: channels 1–2 only | No |
| `009` IDE | Revised: extension-first, fork deferred | No |
| `010` enterprise | **Rewritten** as Phase-4+ one-pager | No |
| `011` demo | Revised: real fixtures, `source: mock` | No |
| `012` FE ADRs | Revised: cite ADR-0062; D3 replaces fork-now | No |

---

## 7. Thrown away

- Invented JSON-RPC 2.0 / `Ping` / `LedgerEvent` / 4 MiB client frames as FE law.
- Tauri, AppImage-embedded-Python, and `github.com/vanguard-ai/*` infra claims.
- Code-OSS-fork-now; EPIC-09; M4 1000-run soak as FE work.
- Sequential “finish CLI then start IDE.”
- Client-side invention of daemon verbs or manifest schemas.

Old `sprints_front/sprint1–4` kits (if present) are replaced by `lane_a_wave*.md` / `lane_b_wave*.md`. Mined deltas: reconnect, JCS, key persistence, `--demo`, webview/CodeLens, E2E pyramid.

---

## 8. Verification (docs + boundary)

```text
# no invented JSON-RPC vocabulary in FE docs
grep -r "jsonrpc" docs/front_v4 docs/scrum/sprints_front

# FE must not import core packages
grep -r "vanguard/packages" vanguard/clients/cli/src vanguard-ide/src

# FE must not edit frozen trees
# (reviewer check) vanguard/packages/**  benchmarkings/**  docs/main_v4/**
```
