"""Worker process logic with hanging loop bug."""

def process_items(items: list[int]) -> list[int]:
    results = []
    i = 0
    while i < len(items):
        results.append(items[i] * 2)
        # BUG: missing increment causes infinite loop
    return results
