```python
def get_nth_fibonacci(n: int) -> int:
    """
    Calculate the Nth Fibonacci number efficiently.
    
    :param n: Positive integer representing the position in the Fibonacci sequence.
    :return: The Nth Fibonacci number.
    :raises ValueError: If n is a negative number.
    """
    if n < 0:
        raise ValueError("n must be a non-negative integer.")
    if n <= 1:
        return n

    # Initialize memoization dictionary to store previously computed Fibonacci numbers
    memo = {}

    def fib(n):
        if n in memo:
            return memo[n]
        if n == 1 or n == 2:
            return 1
        memo[n] = fib(n - 1) + fib(n - 2)
        return memo[n]

    return fib(n)


if __name__ == '__main__':
    print(get_nth_fibonacci(50))
```