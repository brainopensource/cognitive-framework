# Prompt — Tech Lead + Project Lead: Sprint 7 field review (final)

**You decide.** This is a go/no-go after A/B/C started Sprint 7 in one shared tree. Frontend is out of scope.

Sprint 7 is **not closed.** Do not treat Lane B’s `[DONE]` on Sprint 8 as S7 exit.

---

## Copy-paste prompt

```text
You are Tech Lead and Project Lead. Review what Seniors A, B, and C actually shipped in Sprint 7 (and B’s early Sprint 8), against the kits and 011. Decide: hold / finish S7 / waive into S8.

## Ask (one page)
1. Honest status vs claims (especially B marking S8-B-* DONE before S7 subtraction closed).
2. Design: any second loop, bypass runner still scored, kernel edit, silent alias, unread-component exemption, spawn without ledger resume?
3. Process: shared dirty tree, stash risk, missing Active MVP Contract / receipts after the docs purge — what you will fix vs what lanes may continue.
4. Verdict: **HOLD S8** until named S7 rows land / **S7 continue in worktrees** / **S8 with waivers** — named.
5. Joint this week vs not blocking (SEC-01, LICENSE, VG-07, ADR-0066, Q1 reverse-or-not, restore contract JSON).

You may override 011. Demand command+output for anything that would close Q1. A lane report is not a receipt.

## Field snapshot (2026-08-16 — verify in git, do not trust this paragraph)

Lane A: S7-A-07 claimed DONE (repo_paths + 3 tests). Stopped before A-01: C has check_boundaries.py open; 2F/15E baseline voided by in-flight C/B; stash briefly captured other lanes’ work. Missing active-mvp-contract.json / dogfood-log / receipts after purge — PR req_id cite is currently unsatisfiable. A-01…A-06 TODO. Do not start S8-A until S7-A exit (loops/coordination still present).

Lane B: S7-B-01…B-05 marked DONE in 011; agency tests reported 83/83. S8-B-01…B-10 marked DONE in 011 (spawn, compaction, router, approval_policy, ACI) — **premature vs plan** (S8 after S7 exit; spawn depends on A’s session/resume still TODO). Treat S8-B as CLAIMED/VERIFY; audit ADR-0060, property tests, no kernel nouns. Do not open S8-A/C on that claim alone.

Lane C: S7-C-01 implemented (benchmarkings import gate + broken counterpart). Left [TODO] until C-03 deletes four runners — correct. Full-repo check_boundaries FAILS on existing bypasses by design. C-02…C-06 TODO. C-07 already DONE from 009.

Joint: J-01…J-03 ADRs filed. J-04 SEC-01, J-05 LICENSE, J-06 VG-07, J-07 WIP protocol, J-08 ADR-0066 still TODO.

Likely starting point: **HOLD full Sprint 8.** Finish S7-A (isolate worktrees) + S7-C-02/03+ in parallel; **audit B’s S8** as a preview PR, not as sprint close.

## Where to look
docs/scrum/ROADMAP.MD (status mirror — 011 wins)
docs/reviews/doing/011_master_backlog_phase3_V043-REV.md §4–5
docs/main_v4/ VG-03, VG-05, VG-09
docs/scrum/sprints/sprint07/README.md + joint-track.md + lane-a/b/c
docs/scrum/sprints/sprint08/README.md + lane-a/b/c (S8 still PLANNED, NOT REFINED)
Code: runtime/loops still there?, grep OpenRouterModel benchmarkings/, loader.py aliases, agency/episode spawn, tools/check_boundaries.py

## Deliverable
- A / B / C: accept | accept-with-fix | reject — one sentence each
- Worktree/branch rule for the rest of S7
- Who restores Active MVP Contract (Joint vs A)
- Q1: do not reverse unless architecture tests + no second path
- Go / no-go S8
```

---

## Appendix — S7 exit (use if it changes the verdict)

unittest 0 failures (node-absent errors only) · check_boundaries PASS + planted counterparts fail · degenerate run refused · alias + unread component fail closed · scan_secrets --all-refs · TCB · net LOC −1530 · no runtime.loops.

S7-B-03 green via S8-B-02 is OK only after you accept that S8-B work; it is not S7 exit by itself.
