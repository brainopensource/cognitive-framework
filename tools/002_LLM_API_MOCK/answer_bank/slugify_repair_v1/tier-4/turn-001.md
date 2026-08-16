```python
import re
import unicodedata

def slugify(text: str, allow_unicode: bool = False) -> str:
    """
    Converts to ASCII if allow_unicode is False. Converts spaces or repeated
    dashes to single dashes. Removes characters that aren't alphanumerics,
    underscores, or hyphens. Converts to lowercase. Also strips leading/trailing
    whitespace, dashes, and underscores.
    """
    value = str(text)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")
```
