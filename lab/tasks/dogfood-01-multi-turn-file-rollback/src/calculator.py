"""Buggy calculator implementation with division error."""

def add(a: float, b: float) -> float:
    return a + b

def divide(a: float, b: float) -> float:
    # BUG: reversed division
    return b / a
