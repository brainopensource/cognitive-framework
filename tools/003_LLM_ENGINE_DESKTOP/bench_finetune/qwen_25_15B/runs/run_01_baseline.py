```python
import math

def get_nth_fibonacci(n: int) -> int:
    """
    Calculates the Nth Fibonacci number. Uses an optimized matrix exponentiation method for O(log n) runtime.
    Raises ValueError if input is negative.
    """
    if n < 0:
        raise ValueError("Input must be a non-negative integer")

    def fibonacci_matrix_power(matrix, power):
        result = [[1, 1], [1, 0]]
        while power:
            if power % 2:
                result = multiply_matrices(result, matrix)
            matrix = multiply_matrices(matrix, matrix)
            power //= 2
        return result

    def multiply_matrices(mat1, mat2):
        row1, col1 = mat1
        row2, col2 = mat2
        row3, col3 = [0, 0], [0, 0]
        row3[0] = row1[0] * row2[0] + row1[1] * row2[1]
        row3[1] = row1[0] * row2[1] + row1[1] * row2[0]
        return [row3], [col3]

    matrix = [[1, 1], [1, 0]]
    return fibonacci_matrix_power(matrix, n)[0][0]

if __name__ == '__main__':
    print(get_nth_fibonacci(50))
```