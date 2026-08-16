```python
import re

def slugify(text: str) -> str:
    """Converts a string to a lowercase URL-safe slug with hyphens."""
    text = text.lower().strip()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")
```
