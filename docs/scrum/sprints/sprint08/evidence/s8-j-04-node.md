# S8-J-04 — Node-present suite

**Date:** 2026-08-17 · **Owner:** GAMMA

Readers require **Node ≥ 22.18** (type stripping). Absent node, the suite reports `ReaderUnavailable` (the admitted 14–15 errors).

This machine: user-local `/home/rocha/.local/bin/node` **v22.18.0** (not committed). CI must install the same floor.

DoD (2026-08-17, this machine): `PATH` includes `/home/rocha/.local/bin/node` **v22.18.0**.

```
python3 -m unittest discover -s test -t . -q
Ran 755 tests in 13.557s
FAILED (failures=2, skipped=2)
```

**0 `ReaderUnavailable` errors.** The two failures are `test.adapters.test_sandbox_worker` asserting deleted `proc.test` (`S10-A-02`); not this row.

