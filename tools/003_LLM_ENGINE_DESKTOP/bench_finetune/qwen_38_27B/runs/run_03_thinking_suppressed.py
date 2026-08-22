def get_nth_fibonacci(n: int) -> int:
    """Calculate the Nth Fibonacci number using matrix exponentiation.

    Uses the identity:
        [[1, 1],  [n]   [[F(n+1), F(n)],
         [1, 0]]  =     [F(n),   F(n-1)]]

    which allows computation in O(log n) time via fast matrix exponentiation.

    Args:
        n: The index of the Fibonacci number to compute (0-based).
            F(0) = 0, F(1) = 1, F(2) = 1, F(3) = 2, ...

    Returns:
        The Nth Fibonacci number as a non-negative integer.

    Raises:
        ValueError: If n is negative.
        TypeError: If n is not an integer.

    Examples:
        >>> get_nth_fibonacci(0)
        0
        >>> get_nth_fibonacci(1)
        1
        >>> get_nth_fibonacci(10)
        55
    """
    if not isinstance(n, int):
        raise TypeError(f"n must be an integer, got {type(n).__name__}")
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")

    def _mat_mult(A: list[list[int]], B: list[list[int]]) -> list[list[int]]:
        return [
            [A[0][0] * B[0][0] + A[0][1] * B[1][0],
             A[0][0] * B[0][1] + A[0][1] * B[1][1]],
            [A[1][0] * B[0][0] + A[1][1] * B[1][0],
             A[1][0] * B[0][1] + A[1][1] * B[1][1]],
        ]

    def _mat_pow(M: list[list[int]], power: int) -> list[list[int]]:
        result: list[list[int]] = [[1, 0], [0, 1]]
        base: list[list[int]] = [M[0][:], M[1][:]]
        while power > 0:
            if power & 1:
                result = _mat_mult(result, base)
            base = _mat_mult(base, base)
            power >>= 1
        return result

    if n <= 1:
        return n

    base_matrix: list[list[int]] = [[1, 1], [1, 0]]
    result_matrix: list[list[int]] = _mat_pow(base_matrix, n)
    return result_matrix[0][1]


if __name__ == '__main__':
    result: int = get_nth_fibonacci(50)
    print(f"get_nth_fibonacci(50) = {result}")