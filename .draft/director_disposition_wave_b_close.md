# Senior/Director Disposition — Wave B Close

**Subject:** `88b2793e`, clean working tree.
**Supersedes:** the dispatch state table in `.draft/director_disposition_1509.md`.
**Ledger:** `.draft/todo/ruling_ledger_1509.md` (rulings unchanged).

Everything below was measured on this subject. Nothing is carried from a
report.

---

## 1. STOP THE LINE — W2b regressed the product path

**W4 is no longer blocked only by the T-140 lease. It is blocked by a defect.**

`7a297760` made `GitEnvironment.snapshot` fail closed when HEAD cannot be
resolved. That is correct for falsifier B (enumeration failure). It is wrong for
a repository **with no commits yet**, which is a valid candidate and the exact
case the product advertises:

```
empty repo (no commits) : snapshot().ok = False   <-- regression
after first commit      : snapshot().ok = True
```

`test/runtime/test_s21_named_causes.GreenfieldIsAValidWorkspace` exists
precisely to record that an empty tree is not refused.

The second half is the laundering. `session.py:_workspace_digest` turns a failed
`Result` into `""`. Empty string is non-None and does not start with `sha256:`,
so `_carrier_bindings_or_latch` (`session.py:2356-2372`) correctly refuses it and
`_append_change_surface` raises:

```
RuntimeError: ChangeSurfaceUpdated: unbound identity bindings ['candidateDigest']
RuntimeError: VerificationRecorded: unbound identity bindings ['workspaceDigest']
```

The carrier validator is right and must not be touched. A carrier whose subject
cannot be checked is a different fact, not a weaker one.

**Measured blast radius on `88b2793e`:**

| Collection | Result |
|---|---|
| `test/falsifiers` | 617 ran — 3 failures, **16 errors** |
| `test/agency` | 316 ran — **1 error** (`test_cassette_replay`) |
| `test/adapters` | **22 failures** (`test_openrouter`, `test_llama_cpp` — W5, separate) |
| `test/runtime` | 936 ran — **OK**, 17 skipped |
| `test/kernel`, `test/contracts` | OK |

### Packet W2c — AUTHORIZED, blocking, owner Dev B

1. Distinguish **"no commits yet"** (valid empty candidate: digest the working
   tree, record the absence of a revision explicitly) from **"enumeration
   failed"** (failed `Result`). Falsifier B meant the second only.
2. Stop `_workspace_digest` laundering a failed `Result` into `""`. Propagate a
   typed refusal; never hand the carrier validator a value that cannot be
   checked.
3. Do **not** relax `_carrier_bindings_or_latch`. Do not revert W2b — the
   content-addressed identity is correct and `test_w2a_candidate_identity` is
   5/5 green because of it.
4. Falsifier first: an empty repository must reach `ChangeSurfaceUpdated` with a
   bound `candidateDigest`, and a genuinely unreadable tree must still fail.

**Sequencing:** W2c precedes W4. W5's 22 adapter failures are a separate defect
in the same lane and do not gate W4.

---

## 2. Governance defect — packet receipts are being destroyed

Twice now, a broad commit has swallowed a packet's files:

| Commit | Swallowed | Effect |
|---|---|---|
| `12d79bdc` "LDA improvements" | all of **W0** | W0's evidence is attributed to an unrelated commit |
| `5cd3603a` "consolidate backend remediation work" | all of **W1** (7 test files) | same |

Both packets are verified green, so no work is lost — but neither has a
subject-bound receipt of its own. That is the precise failure
`README.md:108-110` guards against, and it defeats OD-1, which promotes
behaviour *with its original subject*.

**Ruling.** A packet lands in its own commit naming its packet ID. A commit that
mixes packets is not a receipt. The Senior records W0's and W1's evidence against
`12d79bdc` and `5cd3603a` respectively, with an explicit note that the
attribution is incidental rather than intended. Neither is re-committed —
rewriting history to manufacture a cleaner receipt would be the same offence in
the other direction.

---

## 3. Acceptance — the gap is now structural, not incidental

| Packet | State | Author / material supplier |
|---|---|---|
| W0 | green | one actor |
| W2a | green (turned green by W2b) | one actor |
| W3a | green | one actor |
| W1 | green | one actor |
| W2b | **regressed the product path** | Lane 2 |
| W5 | 22 adapter failures | Lane 2 |
| W6a | linters pass; path hygiene still red | Lane 3 |

Four packets are **LANDED / acceptance pending**. Dev C was nominated as the
non-author acceptor, but C cannot be the sole acceptor for a batch that includes
C's own W6a, and OD-7 excludes any material supplier.

**Recorded, not signed:** no qualified uninvolved acceptor is evidenced as
appointed. Leadership owns that appointment. The Senior records the gap rather
than inventing a signature. No packet in this wave is *accepted*.

---

## 4. T-140 / `session.py` lease — still unknown

No release date was supplied. C retains the lease. W4's `session.py` edits stay
blocked. **No date is recorded here**, because the directive forbids a
manufactured one and nothing has changed that.

Note the collision this creates: W2c's fix touches `session.py:_workspace_digest`,
which is inside that same lease. **W2c is therefore lease-blocked exactly as W4
is.** Releasing T-140 now unblocks both; leaving it held stops the critical path
behind a defect that is already breaking 17 tests.

This is the single highest-value action available to leadership.

---

## 5. OD-11 — sequencing holds, first condition not yet met

`just check` still fails path hygiene on `docs/research/coding_harness/aux_cli_multi_profiles.md`
(machine-local `/home/<user>/` paths, 8+ occurrences). Under OD-11 the budget and
stale-path linters attach to `docs-check` only after the execution documents are
under ceiling; that condition is unchanged and this file is a further blocker to
a green in-loop gate. It belongs to W6a's Stage 0.4, through C's lease.

Ceilings are not raised. Lowering remains permitted.

---

## 6. Dispatch state

| Packet | State | Blocked by |
|---|---|---|
| W0, W2a, W3a, W1 | green | acceptance only |
| **W2c** | **AUTHORIZED, blocking** | T-140 lease |
| W2b | landed, regressed | superseded by W2c |
| W5 | 22 failures, own lane | — |
| W6a | partial; path hygiene red | — |
| W4 | not startable | **W2c**, then T-140 |
| W3b | not authorized | MS-CAS ruling stands |

Standing boundaries unchanged: zero paid calls, T-26 UNFROZEN, T-27
unauthorized, MS-CONTROL OPEN, D-6 closed at F1–F7.
