# P0-BUG: fix the seeded off-by-one in truncate_with_ellipsis

`string_utils.py` truncates too aggressively. Make `test_oracle.py` pass without changing tests.
