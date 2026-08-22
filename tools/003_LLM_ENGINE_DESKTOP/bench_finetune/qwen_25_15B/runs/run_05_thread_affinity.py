```python
def get_nth_fibonacci(n: int) -> int:
    """
    Calculate the Nth Fibonacci number efficiently using matrix exponentiation.
    
    Args:
        n (int): The index of the Fibonacci number to calculate.
        
    Returns:
        int: The Nth Fibonacci number.
        
    Raises:
        ValueError: If the input is a negative integer.
    """
    if n < 0:
        raise ValueError("Input must be a non-negative integer")
    if n == 0:
        return 0
    if n == 1 or n == 2:
        return 1

    # Initialize the base cases
    a, b = 0, 1
    for _ in range(3, n + 1):
        a, b = b, a + b

    return b

if __name__ == "__main__":
    print(get_nth_fibonacci(50))  # Output: 12586269025
```