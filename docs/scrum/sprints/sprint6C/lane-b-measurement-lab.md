# Lane B (Dev B) Specification: Measurement Laboratory & Control Bench

**Target Branch:** `sprints7-8/integration`  
**Assigned Developer:** Dev B (Lane B Lead)  
**Parent Directive:** [`docs/agile/sprint7_8/sprint7_8_directive_and_playbook.md`](file:///home/rocha/Coding/Aether-D-System/docs/agile/sprint7_8/sprint7_8_directive_and_playbook.md)  
**Target Code Area:** `vanguard/packages/runtime/` & `lab/`  

---

## 1. Objective & Technical Invariants

Implement the unified, ultra-thin **`EpisodeCoordinator`** and the **Measurement Laboratory CLI (`lab/`)** to perform paired statistical comparisons across harness packs and record emergent recursion depth in SQLite.

### Invariants
1. **No OOP Class Bloat:** Never create `class Cell` or `class Organism`. One single recursive `EpisodeCoordinator` handles all levels of coordination.
2. **Emergent Depth Telemetry:** Recursion depth is tracked as an integer in `lam.sqlite` (`0 = Atom`, `1 = Molecule`, `2 = Polymer`, `3 = Cell`, `4+ = Body/Organism`).
3. **Rigorous Paired Statistics:** All harness comparisons must use paired McNemar test calculations to evaluate statistical significance ($p < 0.05$).

---

## 2. Directory Structure for Lane B

```
Aether-D-System/
├── lab/                             # Order 5 Measurement Laboratory
│   ├── bench.py                     # Paired McNemar benchmark runner
│   └── diff.py                      # Multi-harness trajectory comparison tool
└── vanguard/packages/
    ├── agency/manifests/
    │   └── vg-shell-only/           # Undeletable baseline control arm
    │       ├── manifest.json        # Single proc.exec capability
    │       └── aliases.json         # Raw command line passthrough
    └── runtime/
        └── coordination.py          # Unified EpisodeCoordinator & depth logger
```

---

## 3. Tasks Breakdown for Dev B

### Task B.1 (Sprint 7): Unified EpisodeCoordinator (`runtime/coordination.py`)
- Implement `EpisodeCoordinator` supporting recursive sub-episode spawning.
- Enforce budget attenuation: child episode budget cannot exceed parent remaining budget.
- Automatically log episode depth, task ID, parent ID, and token usage into `lam.sqlite`.

### Task B.2 (Sprint 8): Undeletable Control Baseline (`vg-shell-only`)
- Create the minimalist control harness pack with single `proc.exec` capability.
- Serves as the negative control arm for all benchmark trials (measuring what raw bash commands achieve vs. structured multi-atom tools).

### Task B.3 (Sprint 8): Measurement Laboratory Tools (`lab/bench.py` & `lab/diff.py`)
- **`lab/bench.py`:**
  - CLI: `python3 lab/bench.py --pack-a vg-code-default --pack-b vg-code-claude-shaped --db lam.sqlite`
  - Calculates pass rate differential, token efficiency, and paired McNemar contingency matrix ($b, c, \chi^2, p\text{-value}$).
- **`lab/diff.py`:**
  - CLI: `python3 lab/diff.py --trace-a <id> --trace-b <id>`
  - Generates side-by-side terminal visual diff of tool execution cascades and token consumption.

---

## 4. Acceptance Criteria & Quality Gate

- [ ] `EpisodeCoordinator` correctly propagates budgets and logs depth to `lam.sqlite`.
- [ ] `vg-shell-only` baseline control runs cleanly across all 36 gold scenarios.
- [ ] `lab/bench.py` outputs valid McNemar $p$-values and contingency matrices.
- [ ] Unit tests pass: `python3 -m unittest test/runtime/test_coordination.py test/lab/test_bench.py`.
