def get_nth_fibonacci(n: int) -> int:
    """Calculate the Nth Fibonacci number using an iterative approach.

    The Fibonacci sequence is defined as:
        F(0) = 0, F(1) = 1, F(n) = F(n - 1) + F(n - 2) for n >= 2

    This implementation runs in O(n) time and O(1) space.

    Args:
        n: A non-negative integer representing the zero-based index
           in the Fibonacci sequence.

    Returns:
        The Nth Fibonacci number.

    Raises:
        TypeError: If n is not an integer (bool is explicitly rejected).
        ValueError: If n is negative.

    Examples:
        >>> get_nth_fibonacci(0)
        0
        >>> get_nth_fibonacci(1)
        1
        >>> get_nth_fibonacci(10)
        55
    """
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError(f"Expected an int, got {type(n).__name__}")
    if n < 0:
        raise ValueError(f"n must be a non-negative integer, got {n}")

    if n <= 1:
        return n

    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr

    return curr


if __name__ == "__main__":
    result: int = get_nth_fibonacci(50)
    print(f"F(50) = {result}")