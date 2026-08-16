```python
import re
import unicodedata

def slugify(text: str, allow_unicode: bool = False) -> str:
    """
    Standard production-grade slugifier.
    """
    value = str(text)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")

def test_slugify():
    assert slugify("Hello World!") == "hello-world"
    assert slugify("  Späce & Punctuation!  ") == "space-punctuation"
    print("All slugify tests passed.")
```
