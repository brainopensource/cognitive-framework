import unittest
from src.context_allocator import ContextAllocator

class TestContextAllocator(unittest.TestCase):
    def test_preserves_module_docstring_and_top_signatures(self):
        header = "class KernelDispatch:"
        docstring = '    """Trusted Computing Base 13-stage pipeline."""'
        body = [f"    def step_{i}(self): pass" for i in range(50)]

        pruned = ContextAllocator.prune_section(header, docstring, body, max_lines=10)

        # Falsifier Assertion: header and docstring MUST be preserved at top of pruned output
        self.assertIn("class KernelDispatch:", pruned)
        self.assertIn('"""Trusted Computing Base 13-stage pipeline."""', pruned)
        self.assertIn("# ... [pruned] ...", pruned)

if __name__ == "__main__":
    unittest.main()
