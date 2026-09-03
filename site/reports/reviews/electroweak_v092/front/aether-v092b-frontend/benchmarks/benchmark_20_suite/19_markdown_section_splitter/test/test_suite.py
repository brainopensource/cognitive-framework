import unittest
from src.splitter import MarkdownSectionSplitter

class TestMarkdownSplitter(unittest.TestCase):
    def test_header_hierarchy_and_code_blocks(self):
        doc = """# Architecture
System overview.

## Kernel
TCB details.

```python
# This is a comment inside code, not a header!
x = 10
```

### Dispatch
13-stage dispatch pipeline.
"""
        chunks = MarkdownSectionSplitter.split(doc)
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0].title, "Architecture")
        self.assertEqual(chunks[1].title, "Kernel")
        self.assertEqual(chunks[1].breadcrumbs, ["Architecture", "Kernel"])
        self.assertIn("# This is a comment inside code", chunks[1].content)
        self.assertEqual(chunks[2].title, "Dispatch")
        self.assertEqual(chunks[2].breadcrumbs, ["Architecture", "Kernel", "Dispatch"])

if __name__ == "__main__":
    unittest.main()
