```python
def get_nth_fibonacci(n: int) -> int:
    """
    Calculate the Nth Fibonacci number efficiently using matrix exponentiation.

    Args:
        n (int): The position in the Fibonacci sequence (0-indexed).

    Returns:
        int: The Nth Fibonacci number.

    Raises:
        ValueError: If n is a negative integer.
    """
    if n < 0:
        raise ValueError("Input cannot be a negative integer")

    # Base cases
    if n == 0:
        return 0
    elif n == 1:
        return 1

    # Matrix exponentiation method
    def matrix_multiply(A, B):
        return [
            [A[0][0] * B[0][0] + A[0][1] * B[1][0], A[0][0] * B[0][1] + A[0][1] * B[1][1]],
            [A[1][0] * B[0][0] + A[1][1] * B[1][0], A[1][0] * B[0][1] + A[1][1] * B[1][1]]
        ]

    def matrix_power(matrix, power):
        result = [[1, 0], [0, 1]]  # Identity matrix
        base = matrix

        while power > 0:
            if power % 2 == 1:
                result = matrix_multiply(result, base)
            base = matrix_multiply(base, base)
            power //= 2

        return result

    # Transformation matrix
    F = [[1, 1], [1, 0]]
    result = matrix_power(F, n - 1)

    return result[0][0]

if __name__ == '__main__':
    print(get_nth_fibonacci(50))
```