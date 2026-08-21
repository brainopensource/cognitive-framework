# Task: DOGFOOD-02 Subprocess Timeout Censoring

## Brief
Fix the loop advancement bug in `src/worker.py` so that `test_worker.py` completes within lease bounds.
Read timeout observation receipts if execution exceeds lease limits, then apply one Edit to bound the loop.
Verify with `["python3", "-m", "unittest", "test_worker.py"]`.
