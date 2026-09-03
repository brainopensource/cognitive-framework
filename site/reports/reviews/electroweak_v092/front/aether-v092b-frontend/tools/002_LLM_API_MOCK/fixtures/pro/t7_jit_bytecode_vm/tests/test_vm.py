import unittest
from vm import BytecodeVM

class TestBytecodeVM(unittest.TestCase):
    def test_arithmetic_evaluation(self):
        vm = BytecodeVM()
        # (10 + 20) * 3 - 5 = 85
        code = [
            ("PUSH", 10),
            ("PUSH", 20),
            ("ADD",),
            ("PUSH", 3),
            ("MUL",),
            ("PUSH", 5),
            ("SUB",)
        ]
        res = vm.execute(code)
        self.assertEqual(res, 85)

    def test_environment_variable_storage_and_branching(self):
        vm = BytecodeVM()
        # x = 5; if x - 5 == 0 goto 6; return 999; return 42;
        code = [
            ("PUSH", 5),
            ("STORE", "x"),
            ("LOAD", "x"),
            ("PUSH", 5),
            ("SUB",),
            ("JMP_IF_ZERO", 7),
            ("PUSH", 999),
            ("PUSH", 42)
        ]
        res = vm.execute(code)
        self.assertEqual(res, 42)

if __name__ == "__main__":
    unittest.main()
