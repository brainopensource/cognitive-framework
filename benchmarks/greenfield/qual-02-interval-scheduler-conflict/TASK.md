# Task: QUAL-02 Interval Scheduler Conflict Detection

## Brief
`src/intervals.py` provides `merge_intervals`, used by `src/scheduler.py`'s
`Scheduler.has_conflict` to detect overlapping bookings. `test_scheduler.py`
currently fails. Find and fix the bug(s) so that all tests pass. The bug may
span both files.
Verify using `["python3", "-m", "unittest", "test_scheduler.py"]`.
