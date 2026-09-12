# DX-GREEN: Bounded retry helper (greenfield)

The workspace is empty apart from this brief and its oracle.

Create `retry.py` exposing `retry(fn, attempts: int = 3) -> object`:

- call `fn()` and return its result on the first success;
- on an exception, retry until `attempts` calls have been made;
- re-raise the last exception when every attempt fails;
- raise `ValueError` when `attempts` is less than 1, without calling `fn`.
