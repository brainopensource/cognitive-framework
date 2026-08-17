# Sprint 8 — Close Attempt · **NOT CLOSED**

**Branch:** `sprints7-8/integration` @ `b04d525` · **Date:** 2026-08-17
**Verdict: Sprint 8 remains OPEN. Lane A cleared. Lane B sent back.**

This file is the close receipt for Sprint 8. It records a **refused** close, and becomes the
close receipt when the Lane B row below is green. Written in the shape of the Sprint 7 receipt.

---

## 1. Suite and gates

| Check | Result |
|---|---|
| Full suite | **615 tests · 0 failures · 14 errors · 2 skipped** (was 604) |
| All 14 errors | `ReaderUnavailable: node is required` — the admitted class; **zero** others |
| `check_boundaries.py` | PASS, 167 source files |
| `check_tcb_budget.py` | PASS, **1,315 / 1,438 — unchanged across all of Sprint 8** |
| `scan_secrets.py` | PASS |
| Remaining 9 CI gates | PASS |

## 2. `S8-A-02` — **VERIFIED DONE**

Lane A delivered this properly. Every element of the DoD I set is met, and the tests assert the
property rather than the implementation.

| DoD item | Result |
|---|---|
| `grep -c max_segments root.py` → 0 | **0.** No occurrences anywhere in `root.py` |
| Segment loop gone | `test_no_fresh_episode_is_built_per_segment` — green |
| Resume from ledger alone | `test_the_digest_is_identical_with_every_live_object_discarded` — green, and named after stop condition 2 |
| No live object crosses | `test_the_session_exposes_no_dialogue_carried_across_re_entry` — green |
| Turns read from ledger | `test_turns_consumed_are_read_from_the_ledger_not_from_the_operator` — green |
| **64-case gone** | `test_the_bound_is_not_the_product_of_two_numbers` — green |
| `max_turns` hard across approval | `test_turns_never_exceed_max_turns_in_total`, `test_a_smaller_cap_yields_strictly_fewer_turns` — green |

`python3 -m unittest test.runtime.test_resume_from_ledger` → **10 tests, OK.**

The 8×8=64 defect is closed. **`S8-A-02` → `[DONE]`.**

## 3. `S8-B-01` — **SENT BACK.** Reachable, but fails open on authority

Lane B chose **(a) wire it**, and the reachability half is genuinely done:

- `ProposalKind.SPAWN` exists (`state.py:70`), `parse_proposal` handles it (`state.py:122`)
- The episode loop dispatches it (`engine.py:198`)
- `test_model_proposal_triggers_spawn_in_episode_loop` proves a **model proposal** — not a direct
  Python call — starts a child episode. That was the bar, and it is cleared.

**But the child is not attenuated on that path, and the failure is silent.**

```python
raw_scope   = proposal.args.get("scope")
child_scope = raw_scope if isinstance(raw_scope, Scope) else self._scope
```

`proposal.args` is parsed from **model output**. `parse_proposal` copies `args` as a plain dict and
**`Scope` is never constructed from args anywhere in `agency/episode/`.** A model emits JSON, so
`raw_scope` is a `dict` or `None` — **never** a `Scope` instance. The `isinstance` test is therefore
false for every real proposal, and `child_scope` falls back to `self._scope`: **the parent's own,
full, unattenuated scope.**

`attenuate(parent, parent)` then passes, because the subset relation is reflexive.

### Observed, not inferred

A probe in which the model **explicitly asks to narrow** the child to `fs.read`:

```
model asked to narrow to: {"actions": ["fs.read"]}
child_scope IS parent:  True
parent actions:  ['fs.read', 'fs.search', 'patch.apply', 'proc.exec']
child  actions:  ['fs.read', 'fs.search', 'patch.apply', 'proc.exec']
ATTENUATED?      False
```

The child inherited `patch.apply` and `proc.exec`. **The model's narrowing request was silently
discarded.**

### Why this is a send-back and not a nit

1. **It inverts the sprint's sentence.** *"A parent episode spawns a child under an attenuated
   grant"* is false on the only reachable path. Attenuation is exercised **only** by tests that pass
   a Python `Scope` directly — the direct-Python-call path that was explicitly not the bar.
2. **It fails open.** Everything else in this codebase fails closed: `models_for_band("top")`
   refuses, an unread manifest component refuses, a degenerate bench refuses, an unresolvable
   causation chain returns `None` rather than fabricating a root. Here, an unparseable scope grants
   **more** authority, not less — and says nothing.
3. **A careful model is punished.** The one that tries to sandbox its child gets full privilege
   anyway, with no signal that its request was dropped.
4. **`S9-B-01` would measure the wrong system.** Recursion cannot be a DNA dimension when every
   spawned child has identical authority to its parent regardless of what the pack or the model says.

### What Lane B must deliver

- [ ] Build a `Scope` from the proposal's `args["scope"]` mapping — the model's narrowing must be
      **honoured**, and the result must still pass `attenuate` against the parent
- [ ] **Fail closed** when `args["scope"]` is absent or unparseable. Refuse the spawn with a typed
      `SpawnResult`, or attenuate to a declared floor. Inheriting the parent's scope by default is
      not an option
- [ ] Test: a model proposal narrowing to `fs.read` produces a child that **cannot** `patch.apply`
- [ ] Test: a model proposal whose requested scope **widens** the parent is denied, via the loop
- [ ] Test: a malformed/absent scope does **not** yield a full-authority child
- [ ] Re-run `S8-J-02` afterwards

**Do not weaken `attenuate`.** The kernel is correct; the defect is the fallback in `engine.py:200`.

## 4. `S8-J-02` — **RE-RUN, ADR-0060 HELD**

The earlier pass (`b82c887..70802a9`) did not cover `7e42230`; that commit landed between the audit
push and the J-02 commit. Re-run over `70802a9..b04d525`:

- Surface: `engine.py` +45, `state.py` +16
- New vocabulary: `SPAWN`, `spawn`, `brief`, `scope`, `child_scope`, `parent_episode_id` — all
  **episode and kernel** vocabulary. `brief` is an existing `Episode` field, not a domain noun
- 13-term domain scan: **2 hits, both the same prose as before** (`source class`, `dead code`)
- TCB **1,315 — unchanged**; `check_boundaries.py` PASS over 167 files

**Zero domain nouns.** `ADR-0060` holds through the spawn wiring; its reversal condition is not
triggered. This verdict must be re-run again after the Lane B fix above.

## 5. Gate — what closes Sprint 8

- [x] `S8-A-02` green; `max_segments` gone; resume from the ledger alone; 64-case dead
- [ ] **`S8-B-01`: attenuation honoured and fail-closed on the model-proposed path**
- [x] `S8-J-02` ADR-0060 re-run on the spawn diff
- [ ] `S8-J-02` re-run once more after the Lane B fix
- [x] Suite 0 failures, errors only node-absent; 12/12 gates; TCB under budget
- [ ] This file re-issued as a clean close

## 6. Carried, not blocking

| Item | Owner | Note |
|---|---|---|
| `S8-J-01` VG-04 `Claim` reader fields | Joint | **Scheduled for after close.** `support_count`, `last_corroborated_at`, `protection_class` stay **withheld from `to_wire()`** until the schema amendment lands. `additionalProperties:false` means emitting them early produces a claim the normative reader rejects. Lane A has correctly not emitted them |
| `S7-J-04` key rotation | **CTO** | Rotate at the OpenRouter console. Exposure measured: tree clean; historical — 1 reachable `.env` blob, 21 `refs/original/**`, 3 remote branches. **Do not rewrite history first.** `s7-j-04-key-rotation.md` |
| `S8-J-03..J-07` | Joint | Open; none blocks lane coding |
| Sprint 9 | Lane C only | `S9-C-01..03` cleared. **No A/A number** — that hold is now released for A-02 but B's row is still open; keep holding until Sprint 8 closes |
| Sprint 10 | — | **Not started. Not authorised.** |
