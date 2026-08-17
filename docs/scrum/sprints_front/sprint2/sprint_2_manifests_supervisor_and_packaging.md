# Sprint 2: Manifest DNA Engine, Daemon Supervisor & Single-Command Distribution

**Status:** `VOID` — manifests are backend/BETA; CLI packaging is FE-2-7. Do not implement this kit.


**Sprint ID:** `SPRINT-FE-02`  
**Phase / Wave:** `Wave 2 — Autonomous Supervisor & Zero-Config Packaging`  
**Foundation Docs:** [`docs/front_v4/005_vanguard_harnesses_manifests_and_dna_workflows.md`](file:///home/rocha/Coding/Aether-D-System/docs/front_v4/005_vanguard_harnesses_manifests_and_dna_workflows.md), [`docs/front_v4/008_vanguard_build_packaging_and_distribution.md`](file:///home/rocha/Coding/Aether-D-System/docs/front_v4/008_vanguard_build_packaging_and_distribution.md), [`docs/front_v4/011_vanguard_mock_prototype_and_demo_spec.md`](file:///home/rocha/Coding/Aether-D-System/docs/front_v4/011_vanguard_mock_prototype_and_demo_spec.md)  
**Primary Goal:** Build the invisible daemon lifecycle supervisor, manifest discovery/selection UI, offline deterministic demo mode (`vg --demo`), and single-command global distribution scripts.

---

## Sprint Goals & Deliverables

1. **Zero-Config Daemon Supervisor:** Automatically detect, bootstrap, and launch the Python backend daemon process when `vg` runs, redirecting logs cleanly.
2. **Manifest DNA Selector:** Enable dynamic discovery and switching between `vg-code-default`, `vg-code-swe-mini`, and `vg-shell-only`.
3. **Deterministic Mock Demo Mode:** Implement `ReplayAdapter` reading pre-recorded session fixtures so anyone can test the full TUI with zero API keys (`vg --demo`).
4. **Distribution Pipeline:** Provide `npm publish` workflow for `@vanguard/cli` and the universal `curl | sh` installer script (`install.sh`).

---

## Detailed Task Breakdown

### TASK-FE-201: Transparent Daemon Lifecycle Supervisor
* **Subtasks:**
  * Implement `DaemonSupervisor` in `vanguard/clients/cli/src/runtime/supervisor.ts`.
  * Check socket health via lightweight `Ping` RPC.
  * If socket is unavailable, locate or bootstrap isolated virtual environment in `~/.vanguard/runtime/`.
  * Spawn detached Python daemon process: `python3 -m vanguard.packages.runtime.service.server`.
  * Implement graceful socket wait loop (poll socket every 50ms up to 2000ms max timeout).
  * Write daemon PID to `~/.vanguard/run/daemon.pid` and handle cleanup on `/shutdown`.
* **Target Files:** `vanguard/clients/cli/src/runtime/supervisor.ts`, `vanguard/clients/cli/src/runtime/paths.ts`
* **Est. LOC:** ~290 LOC | **Complexity:** 70/100 | **Seniority:** Senior Dev (4★)

### TASK-FE-202: Manifest Discovery & Schema Explorer UI
* **Subtasks:**
  * Implement RPC call to fetch registered manifests from daemon (`ListManifests`).
  * Build interactive Manifest Selector card component in TUI (`/manifest` command).
  * Display capability grant badges (e.g. `fs.read: AUTO`, `proc.exec: SIGN`).
  * Implement budget configuration prompt (max turns, context token ceiling).
* **Target Files:** `vanguard/clients/cli/src/application/ManifestExplorer.ts`, `vanguard/clients/cli/src/ui/ManifestCard.tsx`
* **Est. LOC:** ~240 LOC | **Complexity:** 45/100 | **Seniority:** Normal Dev (3★)

### TASK-FE-203: Deterministic Mock Replay Demo Engine (`vg --demo`)
* **Subtasks:**
  * Enhance [`adapters/replay.ts`](file:///home/rocha/Coding/Aether-D-System/vanguard/clients/cli/src/adapters/replay.ts) to stream events with configurable simulated token delays (10ms–50ms).
  * Package rich synthetic session fixtures:
    * `fixtures/sessions/bugfix_swe_mini.jsonl`
    * `fixtures/sessions/approval_destructive_cmd.jsonl`
    * `fixtures/sessions/subagent_swarm.jsonl`
  * Add CLI flag `--demo` to boot directly into interactive demo without requiring local daemon or API keys.
* **Target Files:** `vanguard/clients/cli/src/adapters/replay.ts`, `vanguard/clients/cli/fixtures/sessions/*.jsonl`
* **Est. LOC:** ~310 LOC | **Complexity:** 40/100 | **Seniority:** Junior / Normal Dev (2★)

### TASK-FE-204: Global Package & Shell Installer Distribution
* **Subtasks:**
  * Configure `package.json` with binary entrypoint `"bin": { "vg": "dist/src/main.js" }`.
  * Write automated build script `npm run build` targeting pure ES modules.
  * Create `install.sh` for zero-dependency one-line installation (`curl -fsSL https://vanguard.ai/install.sh | sh`).
  * Write cross-platform path registration logic for `~/.bashrc`, `~/.zshrc`, and Windows PowerShell profile.
* **Target Files:** `vanguard/clients/cli/package.json`, `tools/distribution/install.sh`
* **Est. LOC:** ~180 LOC | **Complexity:** 50/100 | **Seniority:** DevOps / Senior Dev (3★)
