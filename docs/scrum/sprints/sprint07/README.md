# Sprint 7 (Wave 6) — Subtraction & Boundary Restoration

**Phase:** 3 · **Wave:** W6 · **Target branch:** `sprint07/integration`
**Authorised by:** `ADR-0064`, `DECISION-0005` (`docs/main_v4/09_vanguard_decision_register_v040.md §12`)
**Backlog rows:** `docs/reviews/doing/011_master_backlog_phase3_V043-REV.md §4`
**Timebox:** 2 weeks · 3 lanes + Joint track
**Predecessor:** `docs/scrum/sprints/sprint7_8/` holds the *earlier partial* S7/S8 work
(manifest loader, packs, lab CLI). That work is `[DONE]` except the alias defect carried here.

---

## 1. The sentence this sprint makes true

> **Every effect in every executable path in this repository traverses `Kernel.dispatch`, and an
> architecture test proves it by failing against a planted broken counterpart.**

Nothing else. **This sprint ships no features.** It removes ~1,530 lines and adds five CI rules.

## 2. Why subtraction, and why now

Sprint 6B closed 8 of 9 Beta blockers at the component level. Immediately afterwards, two
kernel-bypassing execution paths were added — `runtime/loops/meta_loop.py` and four
`benchmarkings/` runners — and comparative results were published from runs where the oracle
already passed before the agent acted.

Q1 ("is the boundary real?") was **closer to true at `v0.4.0-sprint4` than it is today.** That is
a regression, and no amount of Sprint 8–10 work repairs it, because every later measurement
inherits the contamination.

> **`GTS-13C` Ch. 14:** *"Disposable becomes architecture — early signal: anyone argues to keep it.
> The argument to keep it is the signal to delete it faster."* That rule was written for `spike/`
> and `slice/`. It applies verbatim to `runtime/loops/`.

## 3. The insight that makes this cheap

`tools/check_boundaries.py` is **already AST-based** (`ast.parse`, `ast.walk`, `ast.Import`,
`ast.ImportFrom`) and **table-driven** — the comment at line 32 literally calls a missing entry
*"a gap in this table rather than a property of the architecture."*

The five new rules are **rows in that table**, not new machinery. The mechanism that made `spike/`
and `slice/` disposable by construction already exists; it was simply never pointed at the new
code. **Point it there.**

## 4. Lanes and write scopes

Scopes are disjoint by construction. A task needing a file outside your scope is a **hand-off**,
not a quick edit.

| Lane | Owner | Write scope |
|---|---|---|
| **A — Control Plane** | Senior A | `tools/check_boundaries.py` · `tools/repo_paths.py` · `vanguard/packages/runtime/**` · `test/runtime/**` |
| **B — Workload & Evidence** | Senior B | `vanguard/packages/agency/manifests/**` · `vanguard/packages/adapters/**` · `test/agency/**` · `test/lab/**` |
| **C — Measurement & Lab** | Senior C | `benchmarkings/**` · `tools/002_LLM_API_MOCK/**` · `lab/**` · `test/broken/**` |
| **Joint** | Tech + Project Lead | `docs/main_v4/**` · `LICENSE` · git history remediation |

**Shared, coordinate before touching:** `vanguard/packages/runtime/root.py` (Lane A owns it this
sprint; Lane B raises a PR comment rather than editing).

## 5. Dependency graph

```
S7-A-01 lattice rule ─┐
S7-A-02 subprocess   ─┼─► S7-A-04 delete runtime/loops/ ─► S7-A-05 delete coordination.py
S7-A-03 evaluator    ─┘
S7-C-01 benchmark gate ─► S7-C-03 delete 4 runners ─► S7-C-04 retraction ─► S7-C-05 promote runner
S7-B-01 alias repair ─► S7-B-02 unread-component ─► S7-B-03 metamorphic (RED, green in S8)
                     └─► S7-B-05 test_bench fix
S7-A-07 restructure repair  (independent — start day 1, unblocks the baseline)
S7-J-04 SEC-01              (independent, Joint, provider-first)
```

**Start day one, in parallel:** `S7-A-07`, `S7-B-01`, `S7-C-01`, `S7-J-04`.

## 6. ADRs to file this sprint

| ADR | Subject | Owner |
|---|---|---|
| `ADR-0063` | Ratify Python control plane, reverse `ADR-0001` | **Filed** |
| `ADR-0064` | Record MVP gate status | **Filed** |
| `ADR-0065` | Adopt D-01…D-15 as binding | **Filed** |
| `ADR-0066` | MCP adapter rules, pre-recorded before any MCP code exists | Joint, this sprint |

## 7. Exit gate

Copy into the sprint review; every box needs a command and its output.

- [ ] `python3 -m unittest discover -s test -t .` → **0 failures**; errors only from node-absent readers
- [ ] `python3 tools/check_boundaries.py` → PASS, and each of the five rules **fails** against its planted counterpart
- [ ] `python3 tools/run_broken_tests.py` → every broken counterpart fails as designed
- [ ] Planted degenerate benchmark run → **refused**, emits `inconclusive`
- [ ] Composition fails on an undeclared alias target **and** on an unread manifest component
- [ ] `python3 tools/scan_secrets.py --all-refs` → **PASS**
- [ ] `python3 tools/check_tcb_budget.py` → PASS
- [ ] `git diff --stat` shows net ≈ **−1,530 LOC**
- [ ] `grep -rn "runtime.loops\|EpisodeCoordinator"` → empty

## 8. Stop conditions

Stop and write a finding — do **not** work around:

1. Deleting `runtime/loops/` breaks a test that is **not** `test_meta_loop.py` → something depends on the bypass path; report before deleting.
2. A boundary rule cannot be expressed in the existing table → the lattice may be wrong; escalate rather than special-casing.
3. Alias repair requires editing `agency/episode/engine.py` → **`ADR-0060` violation**; stop.
4. `SEC-01` history rewrite would touch a ref you cannot identify the owner of → stop; this is not an engineering decision.

## 9. Required reading before the first commit

1. `docs/reviews/doing/001_…§3` — the findings (20 min)
2. `docs/reviews/doing/011_…§4` — your lane's rows (10 min)
3. `docs/scrum/development_guides/00_architecture_decisions_for_implementers.md` (20 min)
4. `docs/scrum/development_guides/01_layer_boundaries_and_ci_rules.md` (10 min)
5. Your lane file in this directory

If you start by writing a feature, you have not read the sprint.
