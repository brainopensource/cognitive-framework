# Task: DOGFOOD-02 Subprocess Timeout Censoring

## Brief
Fix the loop advancement bug in `src/worker.py` so that `test_worker.py` passes quickly without timing out.
Verify with `["python3", "-m", "unittest", "test_worker.py"]`.
