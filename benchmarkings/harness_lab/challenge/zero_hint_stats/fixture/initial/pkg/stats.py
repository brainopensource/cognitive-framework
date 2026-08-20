"""Simple statistics helpers."""


def mean(values):
    total = 0
    for value in values:
        total += value
    return total // len(values)


def median(values):
    return values[len(values) // 2]
