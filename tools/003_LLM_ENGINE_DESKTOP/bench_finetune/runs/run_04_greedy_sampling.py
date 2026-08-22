```python
from __future__ import annotations

from typing import Tuple

Matrix = Tuple[Tuple[int, int], Tuple[int, int]]


def _mat_mult(a: Matrix, b: Matrix) -> Matrix:
    """Multiply two 2×2 matrices."""
    return (
        (a[0][0] * b[0][0] + a[0][1] * b[1][0], a[0][0] * b[0][1] + a[0][1] * b[1][1]),
        (a[1][0] * b[0][0] + a[1][1] * b[1][0], a[1][0] * b[0][1] + a[1][1] * b[1][1]),
    )


def _mat_pow(m: Matrix, power: int) -> Matrix:
    """Raise a 2×2 matrix to a non-negative integer power via binary exponentiation."""
    result: Matrix = ((1, 0), (0, 1))  # identity matrix
    base: Matrix = m
    while power > 0:
        if power & 1:
            result = _mat_mult(result, base)
        base = _mat_mult(base, base)
        power >>= 1
    return result


def get_nth_fibonacci(n: int) -> int:
    """
    Calculate the Nth Fibonacci number using O(log n) matrix exponentiation.

    The Fibonacci sequence is defined as:
        F(0) = 0, F(1) = 1, F(k) = F(k-1) + F(k-2) for k >= 2.

    This implementation leverages the identity:
        [[1, 1], [1, 0]]^n = [[F(n+1), F(n)], [F(n), F(n-1)]]

    and computes the matrix power in O(log n) time via binary exponentiation.

    Args:
        n: A non-negative integer representing the index in the Fibonacci sequence.

    Returns:
        The Nth Fibonacci number as a Python int.

    Raises:
        TypeError: If ``n`` is not an integer.
        ValueError: If ``n`` is negative.

    Examples:
        >>> get_nth_fibonacci(0)
        0
        >>> get_nth_fibonacci(1)
        1
        >>> get_nth_fibonacci(10)
        55
        >>> get_nth_fibonacci(50)
        12586269025
    """
    if not isinstance(n, int):
        raise TypeError(f"Expected an integer, got {type(n).__name__}")
    if n < 0:
        raise ValueError(f"Fibonacci index must be non-negative, got {n}")

    if n == 0:
        return 0
    if n == 1:
        return 1

    base: Matrix = ((1, 1), (1, 0))
    result = _mat_pow(base, n)
    return result[0][1]


if __name__ == "__main__":
    n = 50
    fib_n = get_nth_fibonacci(n)
    print(f"F({n}) = {fib_n}")
```