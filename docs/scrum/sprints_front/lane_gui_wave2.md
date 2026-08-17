# Lane FE-3 · Wave 2 — workbench slots (files, Monaco, PTY)

**Write scope:** `vanguard-gui/**` only  
**Depends:** Wave 1 FE-3-1 scaffold + FE-3-2 replay panel exist. FE-1-1/1-3 types+reducers published.  
**Do not touch:** `vanguard/clients/cli/**` internals · `vanguard/clients/client-core/**` internals (import paths OK) · `vanguard/packages/**`  
**DoD default:** `cd vanguard-gui && npm run typecheck && npm run dev`  
**Unblock first:** Wave 1 `npm run dev` was blocked (`vite` missing; `npm install` failed with `Class extends value undefined is not a constructor or null`). This sprint **must** leave `npm install && npm run dev` green on Linux/WSL with Node ≥ 20.

Copy-paste implementer prompt: [`wave2_implementer_prompts.md`](wave2_implementer_prompts.md) §FE-3.

---

## FE-3-0 — Toolchain (blocker)

Pin `engines.node`, commit a lockfile, document `npm install --workspaces=false` (or install from repo root workspaces). Vite must be a real `devDependency` that installs. Do not “fix” npm by deleting `package-lock` without a replacement lockfile.

**DoD:** clean clone path: `npm install && npm run typecheck && npm run dev` starts Vite.

---

## FE-3-3 — Files + Monaco (real, not CSS stubs)

- Virtualized file tree from a workspace root (Tauri `fs` walk when `src-tauri` exists; until then a **dev-only** Node/Vite plugin or static listing is allowed **only** if labelled `source: mock` / “browser stub”).
- Open file → Monaco model. UTF-8. Dispose models on tab close.
- Do not walk `vanguard/packages/` for discovery (J3).
- Full LSP servers = Phase 4. Monaco tokenization only.

**DoD:** click a file in the tree; editor buffer shows its contents.

---

## FE-3-4 — Terminal PTY

- `@xterm/xterm` + fit addon. Native PTY via Tauri/`portable-pty` on Linux/WSL.
- Default shell. Optional spawn `vg` (Ink TUI **inside** the PTY — never Ink-in-DOM).
- If PTY cannot load in browser-only Vite, render an honest `not_available` slot with the Joint/native reason — **no fake shell prompt that looks live**.

**DoD:** either an interactive shell **or** labelled `not_available`. Never a decorative `$ _` that pretends to be a PTY.

---

## Keep from Wave 1

Replay run panel, `source: mock`, `reduceRunView`, slot registry. Placeholder xyflow/approve/git stay placeholders unless time remains (Wave 3).

**Forbidden:** second agent loop, Ink in DOM, competitor submodules, inventing `Ping`/`ListManifests`.
