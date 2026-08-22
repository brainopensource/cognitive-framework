```python
import math

def get_nth_fibonacci(n: int) -> int:
    """
    Calculate the Nth Fibonacci number using an optimized matrix exponentiation approach.

    Args:
    - n (int): The position in the Fibonacci sequence.

    Returns:
    - int: The Nth Fibonacci number.

    Raises:
    - ValueError: If the input n is negative.

    Examples:
    >>> get_nth_fibonacci(50)
    12586269025
    >>> get_nth_fibonacci(1)
    0
    >>> get_nth_fibonacci(2)
    1
    >>> get_nth_fibonacci(0)
    0
    """
    if n < 0:
        raise ValueError("Input must be a non-negative integer.")
    if n == 0:
        return 0
    if n == 1:
        return 1

    # Initialize the Fibonacci matrix
    fib_matrix = [
        [1, 1],
        [1, 0]
    ]

    # Perform matrix exponentiation
    fib_matrix = mat_pow(fib_matrix, n - 1)

    # Return the bottom-right element
    return fib_matrix[0][0]

def mat_pow(matrix: list[list[int]], power: int) -> list[list[int]]:
    """
    Compute the power of a 2x2 matrix raised to a given power using binary exponentiation.

    Args:
    - matrix (list[list[int]]): The initial 2x2 matrix.
    - power (int): The power to raise the matrix to.

    Returns:
    - list[list[int]]: The matrix raised to the power.
    """
    if power == 0:
        return [[1, 0], [0, 1]]  # Identity matrix

    half_power = mat_pow(matrix, power // 2)
    if power % 2 == 0:
        return mat_multiply(half_power, half_power)
    else:
        return mat_multiply(mat_multiply(half_power, half_power), matrix)

def mat_multiply(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    """
    Multiply two 2x2 matrices.

    Args:
    - a (list[list[int]]): The first 2x2 matrix.
    - b (list[list[int]]): The second 2x2 matrix.

    Returns:
    - list[list[int]]: The product of the two matrices.
    """
    return [
        [a[0][0] * b[0][0] + a[0][1] * b[1][0], a[0][0] * b[0][1] + a[0][1] * b[1][1]],
        [a[1][0] * b[0][0] + a[1][1