from typing import List, Dict, Any

class SSAOptimizer:
    @staticmethod
    def eliminate_dead_code(instructions: List[tuple]) -> List[tuple]:
        # Remove unused assignments
        used_vars = set()
        for op, *args in instructions:
            if op in ("USE", "RETURN", "BRANCH"):
                used_vars.update(args)
            elif op == "ASSIGN_EXPR":
                # args[0] = target, args[1:] = inputs
                used_vars.update(args[1:])

        optimized = []
        for instr in instructions:
            op, *args = instr
            if op == "ASSIGN_CONST":
                target = args[0]
                if target in used_vars:
                    optimized.append(instr)
            else:
                optimized.append(instr)
        return optimized
