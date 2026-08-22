def _multiply_matrices(a: tuple[tuple[int, int], tuple[int, int]], b: tuple[tuple[int, int], tuple[int, int]]) -> tuple[tuple[int, int], tuple[int, int]]:
    """Multiply two 2x2 matrices represented as nested tuples."""
    return (
        (a[0][0] * b[0][0] + a[0][1] * b[1][0], a[0][0] * b[0][1] + a[0][1] * b[1][1]),
        (a[1][0] * b[0][0] + a[1][1] * b[1][0], a[1][0] * b[0][1] + a[1][1] * b[1][1]),
    )


def _matrix_power(
    base: tuple[tuple[int, int], tuple[int, int]],
    exponent: int,
) -> tuple[tuple[int, int], tuple[int, int]]:
    """Compute base^exponent via binary (repeated-squaring) exponentiation in O(log exponent)."""
    result: tuple[tuple[int, int], tuple[int, int]] = ((1, 0), (0, 1))
    while exponent:
        if exponent & 1:
            result = _multiply_matrices(result, base)
        base = _multiply_matrices(base, base)
        exponent >>= 1
    return result


def get_nth_fibonacci(n: int) -> int:
    """
    Compute the Nth Fibonacci number using O(log n) matrix exponentiation.

    The Fibonacci sequence is defined as:
        F(0) = 0, F(1) = 1, F(k) = F(k-1) + F(k-2) for k >= 2.

    This implementation leverages the identity:
        [[1, 1], [1, 0]]^n = [[F(n+1), F(n)], [F(n), F(n-1)]]
    and extracts F(n) from the [0][1] entry of the powered matrix.

    Args:
        n: A non-negative integer index into the Fibonacci sequence.

    Returns:
        The Nth Fibonacci number as a Python int.

    Raises:
        TypeError: If n is not an integer.
        ValueError: If n is negative.

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
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError(f"n must be an integer, got {type(n).__name__}")
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")

    base: tuple[tuple[int, int], tuple[int, int]] = ((1, 1), (1, 0))
    powered = _matrix_power(base, n)
    return powered[0][1]


if __name__ == "__main__":
    result = get_nth_fibonacci(50)
    print(f"F(50) = {result}")