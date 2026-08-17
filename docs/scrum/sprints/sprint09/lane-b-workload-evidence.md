# Sprint 9 · Lane B — Workload & Evidence

**Owner:** Senior B · **Backlog:** `011 §6` · **Refinement:** **REFINED AND OPEN (2026-08-16)**
**Commit prefix:** `[lane-b]`

## ▶ YOUR S9 FIRST TASK: `S9-B-01` — **BLOCKED BY `S8-B-01a` AND `S8-B-04`**

Each pack must differ on **≥3** dimensions. Compaction (`S8-B-02`) and routing (`S8-B-03`) are real
and `[DONE]`. **Approval policy is not real until `S8-B-04` lands**, so a pack cannot yet differ on
it — and `S8-B-04` is your own Sprint 8 row. Finish `S8-B-01a`, then `S8-B-04`, then this unblocks.

**DoD command when unblocked:** `python3 -m unittest discover -s test/agency -t .` — green, each pack
composing with **zero** `agency/episode/` edits.

**Authorised to start NOW, in parallel with Sprint 8:** the `REFERENCE.md` per pack — the public docs
read and, explicitly, **what was not copied**. Prose against public sources, no code, and the part
most likely to be rushed if it waits. Include the honesty label: these reconstruct **tool surface +
prompt + policy**, not any vendor's scheduler. Depth-1 serialisation stands (`D-02`, `D-09`).

**`S9-B-02`:** `build`, `run` and `diff` are **NOT blocked** — start them whenever you have room.
**`bench` is BLOCKED BY `S9-C-02`**, because it enforces a pre-registration hash whose format is
Lane C's output.

**You may not** publish any pack comparison or claim the packs differ *meaningfully* until the A/A
floor exists and `S9-J-03` is signed. Three packs that differ is a fact; three packs that differ by a
meaningful amount is a claim.

---

## S9-B-01 — Reconstructions that actually differ

Today `vg-code-claude-shaped`, `vg-code-swe-mini` and `vg-code-default` are **byte-identical**
except `system-prompt.txt` and `aliases.json`. They reference the *same four tool schema files*,
capabilities, policies, budget and evaluator. `T7.6`/`C-01` is therefore **untested** — not
falsified, untested, which is worse because the programme was recording it as tested.

Sprint 8 made compaction, routing and approval real. Now use them.

- [ ] Each pack must differ on **≥3** of: compaction strategy · model routing · approval policy ·
      turn budget · tool surface · search strategy · edit granularity
- [ ] `REFERENCE.md` per pack citing the **public** docs read and stating what was **not** copied
- [ ] Honesty label: these reconstruct **tool surface + prompt + policy**, not Anthropic's
      scheduler. Depth-1 serialisation stands (`D-02`, `D-09`)
- [ ] Test: `Runtime.compose` each with **zero** `agency/episode/` edits
- [ ] Commit

**Stop condition:** any pack needing a kernel branch → stop, write the finding. That *is* the
configurability experiment, and a negative result is cheap and publishable.

## S9-B-02 — `vg harness build | run | diff | bench`

Ship as a `lab/` entrypoint first (`D-10`) — the product CLI promotes it later.

| Command | Done when |
|---|---|
| `build` | Loads pack, composes, prints `composition_digest`, lists verbs, fails if unwired |
| `run` | One task dir against one frozen harness + labelled ModelPort |
| `diff` | Symmetric difference of two frozen graphs — human-readable **and** machine JSON |
| `bench` | Paired arms, same instances, same evaluator, pre-registration hash enforced |

- [ ] If any arm is LAM replay, the pre-reg file **must** say `backend: lam-replay` and the result
      **must not** be used as Q3
- [ ] Commit
