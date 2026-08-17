# Prompt — Tech Lead + Project Lead: Sprint 7 exit / proceed to Sprint 8

Broad review briefing. **You decide.** Lane kits and `011` are evidence, not a script. Do not rubber-stamp a green suite if the design is wrong; do not block Sprint 8 for paperwork that does not change Q1.

**Scope of this review:** backend Vanguard work **after Sprint 6 / 6B** — especially Sprint 7 (A/B/C + Joint) — and whether Sprint 8 may start. Frontend is out of scope.

---

## ROLE

```text
You are Tech Lead and Project Lead for Aether Vanguard. Review the work completed (or claimed complete) by Senior A, B, and C after Sprint 6B, focused on Sprint 7. Decide whether we may open Sprint 8.

## Ask
1. What actually landed vs what was supposed to land (honest status, not ROADMAP prose).
2. Is the design sound, or did anyone work around a boundary (second loop, bypass runner, unread policy, silent alias, kernel edit, theatre numbers)?
3. What is missing, wrong, or too dangerous to carry into Sprint 8?
4. Verdict: **proceed to Sprint 8** / **proceed with named waivers** / **hold** — with why.
5. Joint items (SEC-01, LICENSE, VG-07 promo, ADR-0066, Q1 reverse-or-not) — close, defer with owner, or block. You own these; do not dump them on A/B/C.

You may override 011 rows, lane DoDs, and LOC targets if the evidence is better than the plan. If the plan was wrong, say so.

## Where to look (cite; do not restack)
Navigator: docs/scrum/ROADMAP.MD (backend board is a mirror — status lives in 011)
Living backlog: docs/reviews/doing/011_master_backlog_phase3_V043-REV.md §4 (S7) and §5 (S8)
Law: docs/main_v4/ especially VG-03, VG-05, VG-09 (ADR-0063…0065, DECISION-0005/0006)
Sprint 7 kits:
  docs/scrum/sprints/sprint07/README.md
  docs/scrum/sprints/sprint07/joint-track.md
  docs/scrum/sprints/sprint07/lane-a-control-plane.md
  docs/scrum/sprints/sprint07/lane-b-workload-evidence.md
  docs/scrum/sprints/sprint07/lane-c-measurement-lab.md
Sprint 8 (only to judge “safe to start”; it is PLANNED, NOT REFINED):
  docs/scrum/sprints/sprint08/README.md
  docs/scrum/sprints/sprint08/lane-a-control-plane.md
  docs/scrum/sprints/sprint08/lane-b-workload-evidence.md
  docs/scrum/sprints/sprint08/lane-c-measurement-lab.md
Code: vanguard/packages/**, tools/check_boundaries.py, benchmarkings/**, test/broken/**
Predecessor (archive): docs/scrum/sprints/sprint6B/, sprint7_8/ — do not reopen as a third board.

## How to work (keep it short)
- Run or demand receipts (command + output) for anything you would reverse Q1 on. A narrative PR is not enough.
- Sample design, do not re-implement the sprint. Look for: leftover runtime/loops, OpenRouterModel in benchmarkings, identity alias fallback, unread components exempted silently, kernel touched, new features shipped in a subtraction sprint.
- Sprint 8 starts only if S7 did not leave a second execution path or a scorer that still grades theatre. Recursion on a contaminated tree is wasted.
- S7-B-03 remaining RED is expected (greens in S8-B-02). Do not treat that as a hold by itself.
- S8 kits are unrefined — if you proceed, say whether planning refinement is required before A starts execute_harness / B starts spawn.

## Deliverable (for yourselves — one page)
- Per lane A/B/C: accept / accept-with-fix / reject (one sentence each)
- Joint: what you will do this week vs what does not block S8
- Q1: reverse ADR-0064 Q1, or explicitly leave it unreversed
- Go / no-go Sprint 8, and the first S8 constraint (if any)
```

---

## Appendix — published S7 exit checklist (inventory, not the assignment)

Use if useful. Skip boxes that do not change the go/no-go.

From `sprint07/README.md` §7 (need command + output if you rely on them):

- unittest discover → 0 failures; errors only node-absent readers
- check_boundaries.py PASS; each new rule fails its planted counterpart
- run_broken_tests.py counterparts fail as designed
- planted degenerate benchmark → inconclusive / refused
- composition fails undeclared alias **and** unread component
- scan_secrets.py --all-refs PASS
- check_tcb_budget.py PASS
- net LOC ≈ −1,530
- grep runtime.loops / EpisodeCoordinator empty

Joint sign-off (`joint-track.md`): LICENSE; ADR-0066; VG-07 promotion; Q1 evidence pack; SEC-01 rotate-then-rewrite (never paste the secret). A hold on history rewrite is allowed if Q1 code evidence is otherwise clean — say so explicitly.

S8 is recursion/resume/load-bearing manifests. Do not start it to “make progress” if S7 subtraction did not land.
