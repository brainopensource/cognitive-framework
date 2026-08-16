```python
import re

def slugify(text: str) -> str:
    """URL-safe slug generator with boundary trimming."""
    cleaned = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", cleaned).strip("-")
```
