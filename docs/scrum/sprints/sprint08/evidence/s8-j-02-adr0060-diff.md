# S8-J-02 — ADR-0060 verification diff

**Date:** 2026-08-17 · **Range:** `b82c887..70802a9` (Sprint 8 open → audit)
**Scope:** `vanguard/packages/agency/episode/` — the only package Phase 3 permits Sprint 8 to edit
**Verdict: ADR-0060 HELD. No domain vocabulary entered the engine.**

Run **before** further engine edits land, as instructed. If Lane B chooses to wire `spawn`
(§3 of the audit), this check must be re-run against that change — this verdict covers the
tree at `70802a9` only.

## 1. Surface of change

```
git diff --stat b82c887..HEAD -- vanguard/packages/agency/episode/
 vanguard/packages/agency/episode/engine.py | 5 +++++
 1 file changed, 5 insertions(+)
```

**Five lines, one file, zero deletions.** Every one is the same identifier:

| Line | Added |
|---|---|
| `engine.py:110` | `parent_lease: str | None = None,` — constructor parameter |
| `engine.py:122` | `self._parent_lease = parent_lease` |
| `engine.py:288` | `parent_lease=self._parent_lease,` — into `EffectRequest` |
| `engine.py:309` | `parent_lease: str | None = None,` — `spawn` parameter |
| `engine.py:372` | `parent_lease=parent_lease or self._parent_lease,` — into the child engine |

`lease` is **kernel budget vocabulary** (`kernel/budget.py`, `Governor.reserve`), not domain
vocabulary. The engine still issues no grant, opens no lease and resolves no denial — it names a
lease id and hands it to the kernel. That is the correct side of the boundary.

## 2. Domain-noun scan of the whole package

```
grep -rniE "\b(file|repo|repository|patch|diff|commit|lint|code|test|source|branch|directory|folder|python|bash|shell)\b" \
  vanguard/packages/agency/episode/*.py
```

**Two hits, both benign, both prose:**

- `engine.py:142` — *"trust is set by its **source class** at construction"* → provenance vocabulary (`SinkClass`), not a domain noun.
- `engine.py:146` — *"became unreachable **dead code**"* → ordinary English in a comment.

**Zero domain nouns in identifiers, types, parameters or literals.** The scan is deliberately
wider than `ADR-0060`'s named four (`file`, `repo`, `patch`, `test`) and still comes back clean.

## 3. Corroborating invariants

| Invariant | Result |
|---|---|
| TCB budget | 1,315 / 1,438 — **unchanged** across all of Sprint 8. Recursion did not grow the kernel. |
| `check_boundaries.py` | PASS — `agency/` still imports no adapter and no evaluator |
| Suite | 604 tests, 0 failures, 14 node-absent errors |

## 4. Why it held so easily — and the caveat

The engine barely changed because `spawn` itself predates Sprint 8: it was already on the tree at
the Sprint 7 close. Sprint 8 added only the `parent_lease` thread.

**So this clean result is not yet evidence that adding recursion preserves `ADR-0060`** — it is
evidence that *threading a lease* does. The real test arrives if Lane B wires `spawn` to a
`ProposalKind`, because a spawn **proposal** is where domain vocabulary would most plausibly leak
in (a brief, a workspace, a task description). Re-run this diff on that change before accepting it.

`ADR-0060`'s reversal condition is not triggered.
