```python
import math

def get_nth_fibonacci(n: int) -> int:
    """
    Calculate the Nth Fibonacci number using matrix exponentiation for efficiency.
    
    Args:
    n (int): The position in the Fibonacci sequence.
    
    Returns:
    int: The Nth Fibonacci number.
    
    Raises:
    ValueError: If n is negative.
    """
    if n < 0:
        raise ValueError("n must be a non-negative integer")
    
    # Base cases
    if n == 0:
        return 0
    elif n == 1:
        return 1
    
    # Initialize the Fibonacci matrix
    fib_matrix = [[1, 1], [1, 0]]
    
    # Matrix exponentiation for n-1
    for _ in range(2, n + 1):
        fib_matrix = [[fib_matrix[0][0], fib_matrix[0][1]], [fib_matrix[1][0], fib_matrix[1][1]]]
        fib_matrix[0][0] = fib_matrix[0][0] * fib_matrix[0][0] + fib_matrix[0][1] * fib_matrix[1][0]
        fib_matrix[0][1] = fib_matrix[0][0] * fib_matrix[1][0] + fib_matrix[0][1] * fib_matrix[1][1]
        fib_matrix[1][0] = fib_matrix[0][0] * fib_matrix[1][0] + fib_matrix[0][1] * fib_matrix[1][1]
        fib_matrix[1][1] = fib_matrix[0][0] * fib_matrix[1][0] + fib_matrix[0][1] * fib_matrix[1][1]
    
    # Return the (n-1)th Fibonacci number
    return fib_matrix[0][0]

# Example usage
if __name__ == '__main__':
    print(get_nth_fibonacci(50))
```