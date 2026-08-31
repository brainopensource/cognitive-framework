# Task: Implement Fibonacci Module and CLI

Implement a pure Fibonacci calculator and CLI entrypoint in `src/fib.py`.

## Requirements:
1. Function `fib(n: int) -> int`:
   - Computes the n-th Fibonacci number where `fib(0) = 0`, `fib(1) = 1`, `fib(2) = 1`, `fib(3) = 2`, `fib(10) = 55`.
   - Must raise `ValueError` for any negative integer `n < 0`.
   - Must raise `TypeError` if `n` is not an integer.
2. CLI Behavior:
   - When run as a script (`python3 src/fib.py --n <int>`), it must parse `--n` and print the resulting integer to stdout.
   - For negative integers, the script must exit with non-zero exit code.
