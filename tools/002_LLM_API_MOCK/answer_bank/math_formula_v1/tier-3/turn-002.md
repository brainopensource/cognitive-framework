```python
def calculate_value(A: float, B: float) -> float:
    """
    Computes (A + B) * B and prints the value rounded to 2 decimal places.
    """
    calculated_value = (A + B) * B
    print(f"the value is {calculated_value:.2f}")
    return calculated_value

if __name__ == "__main__":
    calculate_value(5, 3)
```
