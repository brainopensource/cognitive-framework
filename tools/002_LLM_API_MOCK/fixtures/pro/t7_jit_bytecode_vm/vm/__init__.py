from typing import List, Dict, Any, Optional

class BytecodeVM:
    def __init__(self):
        self.stack: List[int] = []
        self.ip: int = 0
        self.env: Dict[str, int] = {}

    def execute(self, bytecode: List[tuple]) -> int:
        self.ip = 0
        while self.ip < len(bytecode):
            op, *args = bytecode[self.ip]
            if op == "PUSH":
                self.stack.append(args[0])
            elif op == "ADD":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a + b)
            elif op == "SUB":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a - b)
            elif op == "MUL":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a * b)
            elif op == "STORE":
                self.env[args[0]] = self.stack.pop()
            elif op == "LOAD":
                self.stack.append(self.env[args[0]])
            elif op == "JMP_IF_ZERO":
                val = self.stack.pop()
                if val == 0:
                    self.ip = args[0]
                    continue
            self.ip += 1
        return self.stack[-1] if self.stack else 0
