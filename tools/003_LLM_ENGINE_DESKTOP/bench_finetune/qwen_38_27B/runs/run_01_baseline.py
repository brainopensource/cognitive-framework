def _mat_mult(A: list[list[int]], B: list[list[int]]) -> list[list[int]]:
    return [
        [A[0][0] * B[0][0] + A[0][1] * B[1][0], A[0][0] * B[0][1] + A[0][1] * B[1][1]],
        [A[1][0] * B[0][0] + A[1][1] * B[1][0], A[1][0] * B[0][1] + A[1][1] * B[1][1]],
    ]


def _mat_pow(M: list[list[int]], p: int) -> list[list[int]]:
    result: list[list[int]] = [[1, 0], [0, 1]]
    while p:
        if p & 1:
            result = _mat_mult(result, M)
        M = _mat_mult(M, M)
        p >>= 1
    return result


def get_nth_fibonacci(n: int) -> int:
    """Return the Nth Fibonacci number (F(0)=0, F(1)=1) using O(log n) matrix exponentiation.

    Args:
        n: A non-negative integer index into the Fibonacci sequence.

    Returns:
        The Nth Fibonacci number as a Python int.

    Raises:
        TypeError: If n is not an integer.
        ValueError: If n is negative.

    Example:
        >>> get_nth_fibonacci(10)
        55
    """
    if not isinstance(n, int):
        raise TypeError(f"Expected int, got {type(n).__name__}")
    if n < 0:
        raise ValueError(f"Fibonacci index must be non-negative, got {n}")

    if n == 0:
        return 0

    base: list[list[int]] = [[1, 1], [1, 0]]
    return _mat_pow(base, n)[0][0]


if __name__ == "__main__":
    print(f"F(50) = {get_nth_fibonacci(50)}")