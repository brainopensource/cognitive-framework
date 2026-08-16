# Sprint 2 — Developer Prompts: Alpha, Beta, Gamma

**Branch:** `sprint2/alpha-beta-gamma`  
**Base:** `main` (Sprint 1 merged, clean)  
**Rule:** All 3 devs commit to the same branch. Prefix every commit message with `[dev-alpha]`, `[dev-beta]`, or `[dev-gamma]`. PRs must cite `REQ-*` row IDs to pass the CI gate.

```bash
git checkout -b sprint2/alpha-beta-gamma main   # first dev only
git checkout sprint2/alpha-beta-gamma           # the other two
```

---

## 🧑‍💻 Dev Alpha — Event Store & State Ledger

**Complexity: Level 3 / 5 — Senior Developer**  
**Why it's hard/risky:** You are building the append-only ledger — the single source of truth for all system state. A bug means corrupted or unreplayable history. Pure state reducers must be provably deterministic: zero I/O, zero clocks, zero randomness. Any deviation breaks the replay guarantee and crash-recovery.

**Your scope:** `vanguard/packages/domain/` (ledger types) + new `vanguard/packages/ledger/` module.

**Read before coding:**
- `docs/v4/04_vanguard_core_contracts_and_wire_schema_v040.md` — §2, §6
- `docs/sprint0/system-architecture-icd.md` — §2, §5
- `docs/v4/01_vanguard_engineering_handbook_v040.md` — Pure reducer invariants
- `docs/sprint0/active-mvp-contract.json` — T3.* rows
- `docs/sprint1/backlog.md` — T3.1–T3.8

**Verify before pushing:**
```bash
python3 -m unittest discover -s test
python3 tools/check_boundaries.py
python3 tools/cv_checks.py
```

---

## 🧑‍💻 Dev Beta — Kernel, Capabilities & Security

**Complexity: Level 4 / 5 — Lead Architect**  
**Why it's hard/risky:** The kernel is the Trusted Computing Base. Every capability grant and sink-class decision flows through here. A mistake means privilege escalation or an agent bypassing approval. The attenuation algebra must be strictly monotone-decreasing. Must-fail tests MF-001, MF-002, MF-003 must prove these controls reject bad inputs.

**Your scope:** `vanguard/packages/kernel/`

**Read before coding:**
- `docs/v4/05_vanguard_kernel_capabilities_and_security_v040.md` — §2, §3, §5
- `docs/sprint0/system-architecture-icd.md` — §2, §3
- `docs/sprint0/verification-threat-evaluation-plan.md` — §2 MF-001, MF-002, MF-003
- `docs/sprint0/active-mvp-contract.json` — T2.* rows
- `docs/v4/01_vanguard_engineering_handbook_v040.md` — §2 Liskov rules

**Verify before pushing:**
```bash
python3 -m unittest discover -s test
python3 tools/check_boundaries.py
python3 tools/run_broken_tests.py
```

---

## 🧑‍💻 Dev Gamma — Ports, Fakes & E2E Disposable Slice

**Complexity: Level 2–3 / 5 — Mid to Senior Developer**  
**Why it's hard/risky:** Ports are the seam between the pure kernel and the real world. Every port needs exactly two implementations from day one: a deterministic Fake (no I/O, no clock) and a Real adapter. A port with only one implementation is a defect per the engineering handbook. The `slice/` must wire a real provider call end-to-end but must never be imported by production code.

**Your scope:** `vanguard/packages/ports/` (8 interfaces + 8 fakes) + `slice/` (disposable, deleted at S4).

**Read before coding:**
- `docs/sprint0/system-architecture-icd.md` — §4.1, §4.2, §4.3
- `docs/v4/01_vanguard_engineering_handbook_v040.md` — §2, §5 two-implementation rule
- `docs/sprint0/verification-threat-evaluation-plan.md` — §2 MF-005, MF-006
- `docs/sprint0/active-mvp-contract.json` — REQ-CI-002, REQ-CI-003
- `docs/v4/13_C_gts_mvp_program_and_engineering_plan.md` — T0b, T10.2

**Verify before pushing:**
```bash
python3 -m unittest discover -s test
python3 tools/check_boundaries.py
python3 tools/run_broken_tests.py
```
