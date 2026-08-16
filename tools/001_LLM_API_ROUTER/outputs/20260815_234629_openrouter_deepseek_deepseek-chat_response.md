```python
def fibonacci_memoized(n, _memo={0: 0, 1: 1}):
    """
    Compute the n-th Fibonacci number using memoization.

    Args:
        n: The index of the Fibonacci number to compute (n >= 0).
        _memo: Internal dictionary for memoization (defaults to {0: 0, 1: 1}).

    Returns:
        The n-th Fibonacci number.

    Raises:
        ValueError: If n is negative.
    """
    if n < 0:
        raise ValueError("n must be >= 0")
    if n not in _memo:
        _memo[n] = fibonacci_memoized(n - 1) + fibonacci_memoized(n - 2)
    return _memo[n]
```