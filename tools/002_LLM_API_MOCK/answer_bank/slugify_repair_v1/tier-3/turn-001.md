```python
import re

def slugify(text: str) -> str:
    """URL-safe slug generator replacing spaces and punctuation with hyphens."""
    cleaned = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", cleaned)
```
