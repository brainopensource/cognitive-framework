# Vanguard / AETHER — Master Development Tracker

## [Wave 2C / M-2] Runtime Convergence & Evidence Integrity (COMPLETED - GREEN)
- [x] **2C-R25 (Dev B):** SQLite-WAL Cold Continuation & Lease Reconciliation (`recovery.py`, `session.py`) [GREEN]
- [x] **2C-R23 (Dev A):** Trajectory Economic Un-hollowing & Pre-Crash Join (`trajectory.py`, `session.py`) [GREEN]
- [x] **2C-SEAM / 2C-COMBINED:** Integration of Cold Resume & Full Trajectory Assembly in `session.py` [GREEN]
- [x] **2C-REGATE:** Verify `test_rf25_cold_continuation.py` and `test_rf23_trajectory_content.py` GREEN [PASSED]

## [Wave 3 / M-3] Extensibility & Named Component Graph (COMPLETED - GREEN)
- [x] **3.1-A:** Manifest Compiler for Named Component Graph (`mhf.manifest/2` / ADR-0077); parser convergence and RF-28–RF-33 [GREEN]
- [x] **3.1-B:** Plugin Lifecycle FSM in `runtime/registry/lifecycle.py` (`DISCOVERED -> RETIRED` / ADR-0081) [GREEN]
- [x] **3.1-C:** Ledger `PluginDiscovered` and `PluginVerified` Events with single-writer validation (`ledger_emitter.py`, `reducer.py`) [GREEN]
- [x] **3.1-D:** Echo Plugin Lifecycle Walking Skeleton over Unix Domain Sockets (UDS) (`broker.py`, `worker.py`, `test/registry/`) [GREEN]
- [x] **3.1-E:** Complete NOVA-4 and the missing Named Component Graph falsifiers [GREEN]
- [x] **3.1-F:** Finish atomic Layer-0 retirement by removing stale living navigation and proving parser parity [GREEN]
- [x] **3.1-GATE:** RF-28–RF-33, RF-46, RF-73–RF-74, RF-76; edge-only $D_H$ change; no duplicate parser or runtime scheduling [GREEN]
- [x] **3.2-GATE:** RF-34–RF-44; normal/fault echo lifecycle; UDS permissions, timeout, crash, denial, cleanup, event reduction [GREEN]
- [x] **3.3-GATE:** RF-45/NOVA-4; zero Layer-0 source/package/test/CI/navigation surface; full architecture gates [GREEN]

## [Wave 4 / M-4] Foundation E2E Stop Line (ACTIVE / ENVIRONMENT BLOCKED)
- [x] **4.1-A:** Preregistered Oracle and Coding Pack Fixture Setup (`test_composition_root.py`) [PREPARED]
- [ ] **4.1-B:** Execute Uncheated Single Run Generating 9 Populated Evidence Rows (Stop-line real provider execution) [BLOCKED: no authorized provider/evaluator]
- [ ] **4.1-C:** Export Cassette for Hermetic CI Regression Suite (Post-M4)
- [ ] **4.1-GATE:** One uninterrupted lineage binds real model, S0–S12 effect, sandbox, signed exterior verdict, WAL, cold replay, and rich trajectory [OPEN]

## [Waves 5 → 10] Ordered Sprint Checklist (QUEUED)

- [ ] **5.1 — Pack #2:** Implement Math/Formal as a ports-only pack; zero `domain/` or `kernel/` diff; prove trajectory/recovery/evaluator parity.
- [ ] **5.2 — Witness:** Bind exact subject/input/environment/checker/toolchain/assurance/policy in a signed T0 memo; pass RF-34–RF-37 and RF-52–RF-53.
- [ ] **6.1 — Delegation:** Route `agent.spawn` through S0–S12; durable intent precedes child; attenuate selectors/budget/depth/turns/handles; pass RF-55–RF-59 and RF-26.
- [ ] **7.1 — Measurement:** Measure selector conflicts, calls, bytes, envelopes, WAL waits/retries, critical path, cost, and signed pass; accept ADR while I-11 remains active.
- [ ] **7.2 — Concurrency:** Add bounded workers, WAL claims/leases, duplicate rejection, and authority-neutral Pareto profiles; pass RF-46–RF-48 before lifting I-11.
- [ ] **8.1 — Frameworks:** Express debate, critic/reviser, bounded trees, and evolution with manifests/plugins/spawn; pass RF-65–RF-66 with zero kernel/engine diff.
- [ ] **9.1 — Knowledge/Macros:** Rebuildable cited retrieval, evidence-ranked skills, least-privilege macro hull, adversarial replay; pass RF-77 and RF-67–RF-68.
- [ ] **10.1 — Meta-Cognition:** Prediction-before-observation, VFE/EFE, signed trajectory credit, exact paired promotion, human pointer, rollback; pass RF-69–RF-70.

## Gate Command Set

```bash
python3 -m unittest discover -s test/kernel -t .
python3 -m unittest discover -s test/contracts -t .
python3 -m unittest discover -s test/agency -t .
python3 -m unittest discover -s test/runtime -t .
python3 -m unittest discover -s test/adapters -t .
python3 -m unittest discover -s test/security -t .
python3 -m unittest discover -s test/trust -t .
python3 -m unittest discover -s test/packs -t .
python3 -m unittest discover -s test/falsifiers -t .
PYTHONPATH=tools/common python3 tools/codegen/generate_types.py --check
python3 tools/linters/check_boundaries.py
python3 tools/linters/check_tcb_budget.py
python3 tools/linters/check_domain_blindness.py
python3 tools/linters/check_isolation_policy.py
python3 tools/linters/check_duplication.py --enforce
python3 tools/linters/check_doc_metadata.py
python3 tools/linters/check_markdown_links.py
python3 tools/linters/check_stale_paths.py
python3 tools/linters/check_falsifier_ids.py
python3 tools/linters/scan_secrets.py
```

Only `sprint_active.md` authorizes work. A checked implementation item does not close a sprint until
its named falsifiers, production suites, architecture gates, and evidence row are green.
