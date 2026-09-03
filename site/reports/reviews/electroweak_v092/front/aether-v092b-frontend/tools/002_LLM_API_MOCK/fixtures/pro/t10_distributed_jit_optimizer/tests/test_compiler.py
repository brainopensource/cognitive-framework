import unittest
from compiler import SSAOptimizer

class TestJITCompiler(unittest.TestCase):
    def test_dead_code_elimination(self):
        instrs = [
            ("ASSIGN_CONST", "v1", 10),
            ("ASSIGN_CONST", "v2_dead", 999),
            ("ASSIGN_EXPR", "v3", "v1", 5),
            ("RETURN", "v3")
        ]
        res = SSAOptimizer.eliminate_dead_code(instrs)
        targets = [args[0] for op, *args in res if op.startswith("ASSIGN")]
        self.assertNotIn("v2_dead", targets)
        self.assertIn("v1", targets)

if __name__ == "__main__":
    unittest.main()
