# Lane FE-A · Wave 2 — product surface

**Status:** FE-A6–A10 / FE-2-3…FE-2-7 `[DONE]` in-tree (Wave 1 close). Active Wave 2 TUI sprint is **`lane_tui_wave2.md` (FE-2-8)**. FE-2-9 remains Wave 3.

**Write scope:** `vanguard/clients/cli/**`  
**DoD default:** `cd vanguard/clients/cli && npm run typecheck && npm test`

---

## FE-A6 — `vg --demo`

**Delta:** extend `adapters/replay.ts`; CLI flag `--demo` + scenario ids; chrome `source: mock`; catalog under `fixtures/sessions/`.

- [ ] Does not open UDS by default
- [ ] Label visible with `NO_COLOR`

**DoD:** typecheck + tests; demo labelled mock.

**Depends:** FE-A4.

---

## FE-A7 — Daemon lifecycle honesty

**Blocked on Joint J1** for real spawn (`python3 -m vanguard.packages.runtime.service.server` has no `__main__`).

**Delta until J1:** `manageDaemon` (or equivalent) returns `not_available` with actionable text (how to start the daemon when Joint documents it). Fix `getDaemonStatus` hardcoded `version: "0.4.0"` — do not invent health.

- [ ] No fake `running` without a successful connect
- [ ] No silent mock status

**DoD:** tests assert `not_available` / connect-only behavior.

---

## FE-A8 — Approval and why truth

**Delta:** populate `argsDigest` / `descriptorDigest` / `expiresAt` from the real `ApprovalChallenge`. Stop fabricating `explainArtifact` evidence — surface `not_available`.

**Depends:** FE-A3; end-to-end real digests need Joint **J4**.

**DoD:** tests; empty placeholder signatures are not `ok: true` success.

---

## FE-A9 — Distro channels 1–2

**Delta:** `install.sh` + npm-global polish; usage text documents all flags (`--demo`, `--socket-path`, `--manifest`, …).

**Depends:** FE-A6.

**DoD:** `vg --help` lists flags; install documented in CLI README.

---

## FE-A10 — Fixture catalog and soak

**Delta:** complete catalog in `cli_tui_architecture.md` §4.2; soak harness in `vanguard/clients/cli/test/` (not `tools/ci/`).

**Depends:** FE-A6.

**DoD:** named fixtures exist; soak test is deterministic (fake clock / replay).

---

## FE-2-8 — Claude-class chrome

**Delta:** implement `docs/scrum/development_guides/tui_product_surface.md` layout: status bar (`source`, seq, budget), virtualized transcript, prompt bar, `ctrl+c` → `requestCancel`. No new verbs.

**DoD:** `ui.test.ts` + typecheck; `NO_COLOR` still honest.

---

## FE-2-9 — Resume chrome

**Delta:** TUI/headless path that calls `requestResume` with durable run id. If daemon returns `not_available`, show that text — no fake resume.

**DoD:** tests with replay/scenario or live `not_available`.

