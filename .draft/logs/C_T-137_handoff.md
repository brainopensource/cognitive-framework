# T-137 handoff — Developer C → independent Principal (A)

**row**: T-137 Approval-path discrimination probe
**owner**: C (author; cannot self-accept)
**acceptor requested**: A (non-author)
**subject HEAD**: see `git rev-parse HEAD` at review; packet `.draft/logs/C_T-137_packet.json`
**repair authorized**: no
**USD / provider calls**: 0 / 0

## Lease touched

- `benchmarks/diagnostics/approval_path_probe.py` (new)
- `test/benchmarks/test_approval_path_probe.py` (new)
- `benchmarks/diagnostics/fixtures/dx_approval/{TASK.md,test_oracle.py}` (new)
- Product sources and presets: **read-only**

## Falsifier

```bash
python3 -m unittest test.benchmarks.test_approval_path_probe -v
```

**Ran**: 13 tests, OK.

## Controls

- Positive (session-bound signed, labeled `session_bound_signed_control`): valid descriptor-bound Ed25519 approval landed exactly `approved.py`; candidate digest equals exterior oracle digest.
- Negative: explicit signed denial, boolean `True`, stale expiry binding, foreign key, and missing approver produced **no** workspace mutation.
- Public entrypoint (`execute_product` → `entrypoint.execute`) is unchanged and cannot inject an approver.

## First seam (retained)

`missing_approver_suspension_refused`

Public `interactive=True` (assisted pack → fail-closed threshold) with no approver does not mutate. Ledger path matches DIR-P: suspension then `_resolve(None)` is refusal, never default-allow.

## Disposition

**REPRODUCED as attribution of the cold public-entrypoint seam.** RUN-13 remains open. This is **not** a repair lease. Director decides any later repair boundary.

Session-bound signed landing is an **instrument control**, not a claim that the public CLI wires an operator.

## Unresolved observations

- `interactive=False` (benchmark / policy-allow) still lands writes without an approver — that is the declared standard threshold, not the cold seam.
- Resume of the valid signed cell kept the candidate/oracle digest unchanged (no duplicate tree mutation). Ledger write-effect counts may increase across a second episode on the same store; tree identity is the duplicate criterion.
- T-130 NOT_REPRODUCED on write landing is unchanged; T-137 does not re-open a write-repair site.

## DIR-C7 / DIR-C8

Untouched. No merge authority, no Wilson/30-slot/18-of-30 change.

## Next

T-143 is unblocked by this handoff (acceptance may still be pending).
