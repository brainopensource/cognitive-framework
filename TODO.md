# Vanguard / AETHER — Master Development Tracker

## [Wave 2C / M-2] Runtime Convergence & Evidence Integrity (COMPLETED - GREEN)
- [x] **2C-R25 (Dev B):** SQLite-WAL Cold Continuation & Lease Reconciliation (`recovery.py`, `session.py`) [GREEN]
- [x] **2C-R23 (Dev A):** Trajectory Economic Un-hollowing & Pre-Crash Join (`trajectory.py`, `session.py`) [GREEN]
- [x] **2C-SEAM / 2C-COMBINED:** Integration of Cold Resume & Full Trajectory Assembly in `session.py` [GREEN]
- [x] **2C-REGATE:** Verify `test_rf25_cold_continuation.py` and `test_rf23_trajectory_content.py` GREEN [PASSED]

## [Wave 3 / M-3] Extensibility & Named Component Graph (ACTIVE / IN PROGRESS)
- [ ] **3.1-A:** Manifest Compiler for Named Component Graph (`mhf.manifest/2` / ADR-0077); parser convergence and RF-28–RF-33 remain
- [x] **3.1-B:** Plugin Lifecycle FSM in `runtime/registry/lifecycle.py` (`DISCOVERED -> RETIRED` / ADR-0081) [GREEN]
- [x] **3.1-C:** Ledger `PluginDiscovered` and `PluginVerified` Events with single-writer validation (`ledger_emitter.py`, `reducer.py`) [GREEN]
- [x] **3.1-D:** Echo Plugin Lifecycle Walking Skeleton over Unix Domain Sockets (UDS) (`broker.py`, `worker.py`, `test/registry/`) [GREEN]
- [ ] **3.1-E:** Complete NOVA-4 and the missing Named Component Graph falsifiers
- [ ] **3.1-F:** Finish atomic Layer-0 retirement by removing stale living navigation and proving parser parity

## [Wave 4 / M-4] Foundation E2E Stop Line (QUEUED)
- [x] **4.1-A:** Preregistered Oracle and Coding Pack Fixture Setup (`test_composition_root.py`) [PREPARED]
- [ ] **4.1-B:** Execute Uncheated Single Run Generating 9 Populated Evidence Rows (Stop-line real provider execution)
- [ ] **4.1-C:** Export Cassette for Hermetic CI Regression Suite (Post-M4)

## [Waves 5 → 10] Macro Roadmap Evolution (QUEUED)
- [ ] **M-5:** Pack #2 (Math & Formal Deductive Verification) with 0 diffs in `domain/` and `kernel/`
- [ ] **M-6:** Capability-Mediated `agent.spawn` Dispatch through S0–S12 (ADR-0080)
- [ ] **M-7:** Controlled Pareto Concurrency & Dynamic Routing Matrix (ADR-0083)
- [ ] **M-8:** Declarative Framework Builder Topologies (Debate, Critic, Tree Search / ADR-0082)
- [ ] **M-9:** Hybrid Retrieval, Skill Synthesis, and Macro-Tool Compilation (ADR-0084)
- [ ] **M-10:** Governed Meta-Cognition, Active Inference (VFE/EFE), and Signed DPO Promotion
