Sprints 5–6 in GTS-13C are the **beta product slice**: isolate the judge, compile context, then run one frozen harness (`vg-code-default`) as a real coding CLI on OpenRouter + Git. That is Chapter 10 Q1+Q2 only. Q3/Q4, `vg harness bench`, and TableWorld stay S7–S9.

S3–S4 code is already on `sprints3-4/integration` in pieces. The missing product is **wiring**: composition root, live CLI, Git adapter, typed-tool harness, exterior evaluator. `spike/` and `slice/` are still on disk (S4 gate not finished).

---

### What you are aiming at (programme, not a plan)

| Sprint | GTS-13C rows | Done when |
|---|---|---|
| **5** | T5.3–T5.6, T4.9–T4.11 | Evaluator is a separate identity; episode never grades itself; L1–L5 context is prefix-stable; competence estimate is recorded, not consumed |
| **6** | T6.1–T6.8 | First real bug fixed with typed `read/search/patch/test`; `vg run` talks to the runtime; approval binds the descriptor shown; corrections + latency from `docs/sprint2/slice-findings.md` |

Target harness shape: `docs/v4/13_C_gts_mvp_program_and_engineering_plan.md` Chapter 7 (`vg-code-default` vs undeletable `vg-shell-only`).

---

### Authority docs (read before writing S5–S6 specs)

1. **`docs/v4/13_C_gts_mvp_program_and_engineering_plan.md`** — sequencing and rationale only. Part I T4.9–T6.8, Part II S5–S6 rows, Ch.4 spine, Ch.5 packages, **Ch.7 harness YAML**, Ch.10 Q1–Q2, Ch.15 what may enter the contract.
2. **`docs/v4/09_vanguard_decision_register_v040.md`** — §7 ADR-0047..0051, §9 ADR-0054, **§10 ADR-0055..0057** (rebase, four lanes, beta = Q1+Q2). This wins over GTS-13C if they clash.
3. **`docs/sprint0/system-architecture-icd.md`** — six packages, one dispatch path, port table, worker/evaluator/controller identities. CLI lives **outside** `vanguard/packages/`.
4. **`docs/sprint0/active-mvp-contract.json`** — merge gate. S3–S4 rows `REQ-EXEC-*`, `REQ-PORT-002..006`, `REQ-TRUST-001`, `REQ-SEC-001`, `REQ-HARN-001` are assigned; **no S5/S6 rows yet**. `REQ-CLI-001` is the mock CLI only.
5. **`docs/sprint0/verification-threat-evaluation-plan.md`** — `MF-EVL-*`, `MF-GOV-001`, descriptor-substitution, `MF-S4-001`. S5–S6 tests should bind here 1:1 with new `req_id`s.
6. **`docs/v4/03_vanguard_architecture_planes_and_execution_model_v040.md`** — §1 loop, **§6 episode** (no self-eval; VG-03 terminal names beat GTS-13C T4.5), **§7 EnvironmentAdapter + Git**, **§10 L1–L5 context**.
7. **`docs/v4/05_vanguard_kernel_capabilities_and_security_v040.md`** — dispatch already built; read **perimeter / evaluator isolation** for T5.3–T5.6 (S5), not to re-do the kernel.
8. **`docs/v4/06_vanguard_competence_memory_and_evidence_v040.md`** — **§4 evaluator / double probe / inconclusive**. Skip competence lifecycle (O-01, S7+).
9. **`docs/v4/04_vanguard_core_contracts_and_wire_schema_v040.md`** — EffectDescriptor, grants, envelopes, process types. Schemas are DRAFT, not LOCKED.
10. **`docs/v4/10_vanguard_deferred_and_rejected_register_v040.md`** — `DEF-12` (approvals) is **superseded for beta** by ADR-0057; keep promotion/self-update deferred.
11. **`schemas/v4/port-interfaces.md`** — activation rule (interface + fake + suite + real). Text still says EventStore is the only activated port; **the tree has moved on** — treat the file as the rule, not the inventory.
12. **`docs/development/cli_tui_architecture.md`** — hexagonal CLI; `RuntimePort` vs future `RuntimeClient`; **replace `MockRuntime`, do not grow a second backend**.
13. **`docs/sprint2/slice-findings.md`** — model text ≠ patch; approve the exact diff; tests are argv; cwd/root are contract fields. Survives even if `slice/` is deleted.
14. **`spike/provider_notes.md`** — wire quirks for OpenRouter; do not import `spike/`.
15. **`docs/sprint3-4/README.md`** + lane files — what S3–S4 were supposed to land so you can spec S5–S6 against leftovers, not against GTS-13C’s stale S3 = T2/T3 row.

Skip for this spec: VG-07/T8 (A/A), T7.5–T7.7 reconstructions, T9 TableWorld, VG-12.

---

### Code to study (what exists vs what S5–S6 must still invent)

**Already a framework keel (do not rebuild)**  
- `vanguard/packages/kernel/` especially `dispatch.py` — only privileged path.  
- `vanguard/packages/domain/` — wire, reducer, `artifacts/manifest.py` + `graph.py`.  
- `vanguard/packages/adapters/stores/` — EventStore fake + SQLite.  
- `vanguard/packages/runtime/ledger/` — recovery + projections.  
- `vanguard/packages/ports/event_store.py`, `kernel.py`.

**S3–S4 pieces now on disk (your S5–S6 composition inputs)**  
- `vanguard/packages/agency/episode/engine.py`, `state.py` — depth-1 loop; **no context compiler, no operators-as-data**.  
- `vanguard/packages/runtime/governance/engine.py`, `definitions.py` — process resume; **not wired to CLI approvals**.  
- `vanguard/packages/ports/{model,environment,evaluator,sandbox}.py` — interfaces.  
- `vanguard/packages/adapters/models/{fake,cassette,openrouter}.py` — live LLM exists; trust-spine must not require it.  
- `vanguard/packages/adapters/environment/fake.py` — in-memory Git-shaped fake; **no `git.py` / worktree adapter**.  
- `vanguard/packages/adapters/evaluators/fake.py` — scripted verdicts; **no separate OS identity**.  
- `vanguard/packages/adapters/sandbox/{fake,rootless}.py` — perimeter start; S5 still needs evaluator identity/image.  
- `vanguard/packages/agency/manifests/` — **only** `vg-shell-only` in `registry.json`. No `vg-code-default`.  
- `test/trust/test_spine.py` — no-model gate.  
- `vanguard/clients/cli/` — `src/runtime.ts` (`RuntimePort`), `mock-runtime.ts`, `main.tsx` still constructs the mock. Commands: `run` / `trace` / `why`.

**Empty / thin (this is the S5–S6 hole)**  
- `vanguard/packages/runtime/README.md` — composition root is still a stub; **runtime is the only legal place to inject OpenRouter + Git + sandbox**.  
- No `agency/context/` compiler (T4.9).  
- No operator artifacts as data (T4.10).  
- No typed tool impls as effects (`read/search/patch/test`).  
- CLI `why` does not read the ledger.  
- `schemas/v4/port-interfaces.md` vs actual ports: refresh inventory when you spec, or you will double-activate.

**Lattice reminder:** `vanguard/packages/README.md` + `tools/check_boundaries.py`. Clients: `vanguard/clients/README.md` — CLI must not import kernel/agency/adapters.

---

### Practical leftovers that will show up when you write S5–S6

- **S4 not fully exited:** `spike/` and `slice/` still present (`slice/git-environment.ts` is the anti-pattern for the Git adapter).  
- **Two CLI contracts:** `RuntimePort` in `runtime.ts` vs richer `RuntimeClient` in `cli_tui_architecture.md` (approvals, VG-04 envelopes). Spec which one S6 implements.  
- **Two termination vocabularies:** VG-03 §6.2 vs GTS-13C T4.5 — ADR-0057 already picked VG-03.  
- **`REQ-HARN-001` open:** registering `vg-code-default` is still work; S6 dogfood depends on it.  
- **No contract rows yet** for evaluator isolation, context compiler, Git real adapter, descriptor-bound approval, correction capture, latency. You will add those when you spec, same way S3–S4 did.

Read the authority docs and the modules above, then write S5–S6 against **the tree**, not against GTS-13C Part II’s old S3 kernel rows.