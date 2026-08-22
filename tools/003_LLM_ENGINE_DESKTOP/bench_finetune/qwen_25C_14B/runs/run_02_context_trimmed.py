```python
def get_nth_fibonacci(n: int) -> int:
    """
    Calculate the Nth Fibonacci number using matrix exponentiation, which is efficient with a time complexity of O(log n).

    :param n: The position in the Fibonacci sequence (0-indexed).
    :return: The Nth Fibonacci number.
    :raises ValueError: If n is negative.
    """
    if n < 0:
        raise ValueError("Input cannot be negative")

    def matrix_multiply(A, B):
        return [
            [A[0][0] * B[0][0] + A[0][1] * B[1][0], A[0][0] * B[0][1] + A[0][1] * B[1][1]],
            [A[1][0] * B[0][0] + A[1][1] * B[1][0], A[1][0] * B[0][1] + A[1][1] * B[1][1]]
        ]

    def matrix_power(matrix, n):
        result = [[1, 0], [0, 1]]  # Identity matrix
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

    F = [[1, 1], [1, 0]]
    result = matrix_power(F, n - 1)
    return result[0][0]

if __name__ == '__main__':
    print(get_nth_fibonacci(50))  # Output: 12586269025
```