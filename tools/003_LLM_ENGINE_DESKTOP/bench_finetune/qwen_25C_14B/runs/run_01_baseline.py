```python
from typing import Tuple

def get_nth_fibonacci(n: int) -> int:
    """
    Calculate the Nth Fibonacci number using matrix exponentiation.

    Parameters:
    n (int): The position in the Fibonacci sequence (0-based index).

    Returns:
    int: The Nth Fibonacci number.

    Raises:
    ValueError: If n is a negative integer.
    """
    if n < 0:
        raise ValueError("Input cannot be a negative integer")

    def matrix_multiply(A: Tuple[Tuple[int, int], Tuple[int, int]], B: Tuple[Tuple[int, int], Tuple[int, int]]) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        return (
            (A[0][0] * B[0][0] + A[0][1] * B[1][0], A[0][0] * B[0][1] + A[0][1] * B[1][1]),
            (A[1][0] * B[0][0] + A[1][1] * B[1][0], A[1][0] * B[0][1] + A[1][1] * B[1][1])
        )

    def matrix_power(matrix: Tuple[Tuple[int, int], Tuple[int, int]], n: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        result = ((1, 0), (0, 1))  # Identity matrix
        base = matrix

        while n > 0:
            if n % 2 == 1:
                result = matrix_multiply(result, base)
            base = matrix_multiply(base, base)
            n //= 2

        return result

    if n == 0:
        return 0
    elif n == 1:
        return 1

    F = ((1, 1), (1, 0))
    result = matrix_power(F, n - 1)
    return result[0][0]

if __name__ == '__main__':
    print(get_nth_fibonacci(50))
```

This code defines a function `get_nth_fibonacci` that calculates the Nth Fibonacci number using matrix exponentiation, which operates in O(log n) time complexity. The function includes input validation to raise a `ValueError` for negative inputs and demonstrates the calculation of the 50th Fibonacci number in the `if __name__ == '__main__':` block.