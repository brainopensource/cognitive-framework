```python
def slugify(text):
    # Retry without regex
    return text.strip().replace(" ", "-")
```
