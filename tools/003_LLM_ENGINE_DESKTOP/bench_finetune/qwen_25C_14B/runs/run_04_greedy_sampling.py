```python
from typing import Dict

def get_nth_fibonacci(n: int) -> int:
    """
    Calculate the Nth Fibonacci number using matrix exponentiation for O(log n) time complexity.

    Args:
        n (int): The position in the Fibonacci sequence (0-based index).

    Returns:
        int: The Nth Fibonacci number.

    Raises:
        ValueError: If n is negative.
    """
    if n < 0:
        raise ValueError("Input cannot be negative")

    def matrix_multiply(A: Dict, B: Dict) -> Dict:
        return {
            'a': A['a'] * B['a'] + A['b'] * B['c'],
            'b': A['a'] * B['b'] + A['b'] * B['d'],
            'c': A['c'] * B['a'] + A['d'] * B['c'],
            'd': A['c'] * B['b'] + A['d'] * B['d']
        }

    def matrix_power(matrix: Dict, n: int) -> Dict:
        result = {'a': 1, 'b': 0, 'c': 0, 'd': 1}
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

    F = {'a': 1, 'b': 1, 'c': 1, 'd': 0}
    result = matrix_power(F, n - 1)
    return result['a']

if __name__ == '__main__':
    print(get_nth_fibonacci(50))
```