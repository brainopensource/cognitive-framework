# Sprint 8 — Close Receipt · **CLOSED**

**Branch:** `sprints7-8/integration` · **Date:** 2026-08-17  
**Verdict: Sprint 8 is CLOSED.** Lane A, Lane B, and Lane C verified. All sprint gates pass.

---

## 1. Suite and gates

| Check | Result |
|---|---|
| Full suite | **617 tests · 0 failures · 14 errors · 2 skipped** |
| All 14 errors | `ReaderUnavailable: node is required` — the admitted reader class (`S8-J-04`); **zero** others |
| `check_boundaries.py` | PASS, 167 source files checked |
| `check_tcb_budget.py` | PASS, **1,315 / 1,438 — unchanged across all of Sprint 8** |
| `scan_secrets.py` | PASS |
| Remaining 9 CI gates | PASS |

---

## 2. `S8-A-02` — **VERIFIED DONE**

Lane A delivered ledger-based re-entry and bounded loop execution:

| DoD item | Result |
|---|---|
| `grep -c max_segments root.py` → 0 | **0.** No occurrences anywhere in `root.py` |
| Segment loop gone | `test_no_fresh_episode_is_built_per_segment` — green |
| Resume from ledger alone | `test_the_digest_is_identical_with_every_live_object_discarded` — green |
| No live object crosses | `test_the_session_exposes_no_dialogue_carried_across_re_entry` — green |
| Turns read from ledger | `test_turns_consumed_are_read_from_the_ledger_not_from_the_operator` — green |
| **64-case gone** | `test_the_bound_is_not_the_product_of_two_numbers` — green |
| `max_turns` hard across approval | `test_turns_never_exceed_max_turns_in_total`, `test_a_smaller_cap_yields_strictly_fewer_turns` — green |

`python3 -m unittest test.runtime.test_resume_from_ledger` → **10 tests, OK.**

---

## 3. `S8-B-01` — **VERIFIED DONE.** Model-proposed spawn fails closed on authority

Lane B delivered Option (a) with fail-closed child scope parsing:

- `ProposalKind.SPAWN` parsed from model proposals (`state.py`).
- `_parse_child_scope` in `engine.py` constructs child `Scope` strictly from `args["scope"]`.
- **Fail-closed:** Missing or unparseable `scope` mappings produce a typed failure receipt (`scope_unparseable`) without spawning a child with parent authority.
- **Narrowing enforced:** A model proposal narrowing to `fs.read` spawns a child that cannot execute `patch.apply`.
- **Budget conservation & `F-13`:** Grandchild / child / parent budget conserved across two levels; child overruns debit reality (`K-07`); closed parent leases refuse child reservations (`F-13`).
- **Workspace lifecycle:** Per-branch workspace destroyed in `finally` (`N-16`).
- **Context isolation:** Child intermediate turns remain absent from parent compiled context (`S8-B-05`).

`python3 -m unittest test.agency.test_episode_spawn -v` → **13 tests, OK.**

---

## 4. `S8-J-02` — **RE-RUN, ADR-0060 HELD**

Re-run over final `sprints7-8/integration` state:

- Vocabulary in `agency/episode/`: `SPAWN`, `spawn`, `brief`, `child_scope`, `parent_episode_id`, `parent_lease` — all generic kernel/agency vocabulary.
- Domain noun scan (`file`, `repo`, `patch`, `test`): **0 occurrences in engine code.**
- TCB: **1,315 / 1,438 — unchanged.**
- Boundary check: **PASS over 167 source files.**

`ADR-0060` holds cleanly through full spawn integration.

---

## 5. Gate — Sprint 8 Close Checklist

- [x] `S8-A-02` green: `max_segments` removed, resume from ledger alone, 64-case dead.
- [x] `S8-B-01`: Attenuation honoured and fail-closed on model-proposed path.
- [x] `S8-B-01a`: `parent_lease` threaded through `Governor.reserve`, budget conserved 2 levels deep, `F-13` verified.
- [x] `S8-B-02`..`B-10`: Compaction strategies, model routers, approval policy component, ACI gifts all green.
- [x] `S8-C-01`..`C-04`: Depth projection, cache hit/miss attribution, regex probes verified.
- [x] `S8-J-02`: ADR-0060 re-run passes with zero domain nouns.
- [x] Full suite: 0 failures, 12/12 gates pass, TCB under budget.

**Sprint 8 is formally CLOSED.**

---

## 6. Carried to Post-Merge / Wave 2

| Item | Owner | Note |
|---|---|---|
| `S8-J-01` VG-04 `Claim` wire fields | Joint | Scheduled post-merge once normative reader schema amendment lands. Extra fields remain withheld from `to_wire()`. |
| `S7-J-04` key rotation | **CTO** | Rotate credentials in OpenRouter console. Exposure is historical; no git history rewrite. |
| Sprint 9 | All Lanes | Opened following merge of `sprints7-8/integration` → `main`. |
