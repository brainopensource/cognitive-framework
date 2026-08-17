# Sprint 8 · Joint Track

**Owners:** Tech Lead + Project Lead · **Backlog:** `011 §5` ·
**Refinement:** **REFINED AND OPEN (2026-08-16)** · **Branch:** `sprints7-8/integration`

> **None of the rows below block Developers A, B or C.** Joint work runs alongside the lanes. If a
> Joint row starts blocking a lane, that is a Joint failure — escalate to the CTO, do not idle.

## Carried from Sprint 7 — scheduled here with owners and dates

These are the `011` Joint rows left open at the Sprint 7 close. They are **scheduled, not parked.**

| ID | Item | Owner | Due | Blocks a lane? |
|---|---|---|---|---|
| `S7-J-04` | **Git history rewrite for the leaked key.** Provider-side rotation is the **CTO's action and must happen first**; it is not verifiable from this repo. `scan_secrets.py --all-refs` still reports a reachable `.env` blob and 21 `refs/original`. History rewrite requires **written owner sign-off** on every affected ref (Sprint 7 stop condition 4) | CTO (rotation) → TL (rewrite) | rotation immediately; rewrite on written OK | **No** — explicitly does not block S8/S9 coding |
| `S8-J-04` | **Node-present full suite.** All 14 remaining suite errors are `ReaderUnavailable: node is required`. Install `node` on a runner and confirm **0 errors**. Until then the cross-language reader agreement (`SC-7`) is unproven, not proven-absent | TL | week 1 | No |
| `S8-J-05` | **`docs/reviews/doing/` is over cap** — 12 files against a cap of 8. Move `002`, `006`, `008`, `009` to `docs/reviews/done/` once their findings are represented in `011`, or raise the cap with a reason. Do not leave it silently over | PL | week 1 | No |
| `S8-J-06` | **`ADR-0066` — MCP adapter rules**, pre-recorded before any MCP code exists. Carried from Sprint 7 §6 where it was the one unfiled ADR. Recording it now costs nothing; retrofitting it after an adapter exists costs an argument | TL | week 2 | No |
| `S8-J-07` | **`VG-07` reconciliation** — carried from `011` Joint. Reconcile the `VG-07` rows against what Sprint 7's subtraction actually left on the tree | PL | week 2 | No |
| `S8-J-08` | **Active MVP Contract row reactivation.** The contract was restored **thin** at the Sprint 7 close: 16 rows, 14 covered, from 50. The other 34 Sprints 0–6 rows are in `deferred_activation`. Reactivate a row **only** with its command observed green and a SHA-bound receipt — never by restoring a prior status | TL | week 3 | No |

**Rule adopted at the Sprint 7 close (D2), binding on this sprint:** the baseline manifest seal is
the **last task of the sprint**, never a mid-sprint row. In Sprint 7 Lane B sealed at `6ed94fe` and
Lane A invalidated the seal at `c5ff05f` by rewriting a sealed file. Seal last.

---

## S8-J-01 — `VG-04` wire amendment for `Claim`

Coordinates with `S8-A-05`. This is a **format lock** (`L-1`): *"changing it means re-running
everything ever recorded."*

- [ ] Review the `Claim` type against `VG-06`'s evidence claim; the schema already exists
      (`schemas/v4/evidence-claim.schema.json`) with `invalidationConditions` `minItems: 1`
- [ ] Add `support_count`, `last_corroborated_at`, `protection_class` as **optional reader-profile**
      fields (`T1.13` writer/reader split — a reader rejecting unknown fields breaks forward
      compatibility on its first bump)
- [ ] Golden vectors for the new fields
- [ ] Migration rehearsal (`T1.15`): add the field, bump minor, prove old readers survive
- [ ] Record as an ADR — it is irreversible

> **Why now, when nothing consumes it:** `T4.11` already accepted this argument for the competence
> prior. Recording costs nothing today; retrofitting costs a corpus migration. And the 2026
> library-drift literature says evidence-gated preservation is the structural mitigation — the
> fields are the cheapest possible hedge.

---

## S8-J-02 — Confirm `ADR-0060` held through recursion

Sprint 8 is the only sprint that edits `agency/episode/`. Verify the invariant survived.

- [ ] Diff `agency/episode/` and confirm **zero domain vocabulary** was introduced
- [ ] Confirm `check_tcb_budget.py` still passes — recursion must not grow the kernel
- [ ] If a domain noun did enter, that is a **finding**, and `ADR-0060`'s reversal condition should
      be evaluated honestly rather than the noun quietly renamed

---

## S8-J-03 — Q1/Q2 evidence review

- [ ] Q1: confirm Sprint 7's closure held through a sprint that added code
- [ ] Update `ADR-0064` gate rows **only** where evidence supports it

### The three Q2 dogfood bugs — PRE-REGISTERED BY NAME, 2026-08-16. No runs in Sprint 8.

Named **now**, in Sprint 8, so the tasks cannot be chosen after seeing the harness behave. All three
are real defects in this repository, verified on the tree at `248be91` during the Sprint 7 close.
All three are **un-owned by any Sprint 8 lane row** — chosen that way so no lane fixes them first
and hollows out the exercise.

| ID | Bug | Verified how |
|---|---|---|
| `DOGFOOD-01` | **No baseline re-seal path.** `tools/check_baseline_manifest.py` verifies digests but cannot produce them. The Sprint 7 close (defect D2) had to re-seal with a throwaway script. Fix: a `--seal` flag with the same stale-path guards as the verifier | `grep -c seal tools/check_baseline_manifest.py` → `0`; no seal tool in `tools/` |
| `DOGFOOD-02` | **`spawn` swallows programming errors.** `agency/episode/engine.py:389` catches bare `except Exception` and converts it to a typed `SpawnResult(RUNTIME_ERROR)`. A `TypeError` in the child engine becomes an ordinary child failure and is indistinguishable from a legitimate one. Isolation should not mean concealment | Read at `engine.py:389` |
| `DOGFOOD-03` | **Baseline manifest accepts unknown keys silently.** `check_baseline_manifest.py` validates `schema_version` and `files` and ignores everything else; a `seal_note` key added at the Sprint 7 close was accepted with no validation. A typo'd `git_tag_status` would pass unnoticed — and that field gates `--release` | Observed at the Sprint 7 close: key added, gate still PASS |

**Substitution rule.** If a bug is fixed before Sprint 9 by ordinary work, it is **replaced from the
same list of close-time findings, recorded with a date and a reason** — never silently swapped for
an easier one, and never dropped to leave two. Substitution is a Joint decision, logged here.

**Not Q2 evidence — read this before anyone cites it.** `tools/002_LLM_API_MOCK/scenarios/`
contains `t0-dogfood-bug-001`, `-002` and `-003`. Despite the names, these are **LAM cassette replay
scenarios**, not interactive dogfood runs. Replay is deterministic; it cannot answer *"would you
reach for it again?"* because nobody reached for anything. **They must never be counted toward Q2.**
This is precisely the failure mode `S9-J-04` names: a true sentence read as a stronger one.

(These three scenario ids are also the corpus half of `S8-C-04`'s regex mismatch — `schema.py:20`
requires `^t[1-5]-` and these are `t0-`. Lane C owns that row; it does not make them Q2 evidence.)

## Sign-off checklist

- [ ] All three lane DoDs green
- [ ] `S7-B-03` metamorphic test now green (manifests are load-bearing)
- [ ] TCB under budget; `ADR-0060` verified
- [ ] `Claim` format locked with golden vectors and a migration rehearsal
- [ ] Cache-hit rate is a live CI metric
