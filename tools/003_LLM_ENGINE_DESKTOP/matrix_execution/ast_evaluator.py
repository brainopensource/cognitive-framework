#!/usr/bin/env python3
"""
Canonical Python AST Evaluator (SPEC-LED-2026-V1 Section 4.2)
0-100 Quality Metric for LLM-Generated Python Code.
"""

import ast
import json
import sys
from typing import Tuple, Dict, Any


def evaluate_python_code(code_str: str) -> Dict[str, Any]:
    """
    Evaluates Python code on a 0-100 scale according to SPEC-LED-2026-V1:
    - S_syntax:    30 pts (ast.parse succeeds)
    - S_signature: 25 pts (FunctionDef name == 'get_nth_fibonacci')
    - S_types:     15 pts (Function return annotation exists)
    - S_error:     15 pts (ValueError handling exists in AST)
    - S_purity:    15 pts (No conversational preamble / think tags)
    """
    syntax_score = 0
    signature_score = 0
    types_score = 0
    error_score = 0
    purity_score = 0
    feedback = []

    # Clean markdown fences if present
    clean_code = code_str.strip()
    is_fenced = False
    if "```python" in clean_code:
        clean_code = clean_code.split("```python")[1].split("```")[0].strip()
        is_fenced = True
    elif "```" in clean_code:
        clean_code = clean_code.split("```")[1].split("```")[0].strip()
        is_fenced = True

    # 1. Syntax Check (30 pts)
    parsed = None
    try:
        parsed = ast.parse(clean_code)
        syntax_score = 30
        feedback.append("Syntax: OK")
    except SyntaxError as e:
        feedback.append(f"Syntax: Error ({e.msg})")
        return {
            "total_score": 0,
            "syntax_score": 0,
            "signature_score": 0,
            "types_score": 0,
            "error_score": 0,
            "purity_score": 0,
            "feedback": " | ".join(feedback),
            "is_valid": False,
        }

    # 2. Signature Check (25 pts) & 3. Type Annotation Check (15 pts)
    has_target_func = False
    has_return_type = False
    has_value_error = False

    for node in ast.walk(parsed):
        if isinstance(node, ast.FunctionDef) and node.name == "get_nth_fibonacci":
            has_target_func = True
            if node.returns is not None:
                has_return_type = True

        # 4. Error Check (15 pts): check for Raise ValueError or reference in AST
        if isinstance(node, ast.Raise):
            if isinstance(node.exc, ast.Call):
                if isinstance(node.exc.func, ast.Name) and node.exc.func.id == "ValueError":
                    has_value_error = True
            elif isinstance(node.exc, ast.Name) and node.exc.id == "ValueError":
                has_value_error = True

    if has_target_func:
        signature_score = 25
        feedback.append("Func: get_nth_fibonacci Present")
    else:
        feedback.append("Func: Missing get_nth_fibonacci")

    if has_return_type:
        types_score = 15
        feedback.append("Types: Return Annotated")
    else:
        feedback.append("Types: Missing Annotation")

    if has_value_error or "ValueError" in clean_code:
        error_score = 15
        feedback.append("Error Guard: ValueError Present")
    else:
        feedback.append("Error Guard: Missing ValueError")

    # 5. Purity Check (15 pts): Check if raw code was output without conversation/think tags
    raw_lower = code_str.lower()
    has_preamble = any(phrase in raw_lower for phrase in ["sure!", "here is", "certainly", "below is", "<think>"])
    if not has_preamble and not is_fenced and (clean_code.startswith("def ") or clean_code.startswith('"""') or clean_code.startswith("#") or clean_code.startswith("from ") or clean_code.startswith("import ")):
        purity_score = 15
        feedback.append("Purity: Pure Code")
    elif not has_preamble and is_fenced:
        purity_score = 10
        feedback.append("Purity: Markdown Fenced")
    else:
        purity_score = 0
        feedback.append("Purity: Conversational Filler / Think Tags")

    total_score = syntax_score + signature_score + types_score + error_score + purity_score

    return {
        "total_score": total_score,
        "syntax_score": syntax_score,
        "signature_score": signature_score,
        "types_score": types_score,
        "error_score": error_score,
        "purity_score": purity_score,
        "feedback": " | ".join(feedback),
        "is_valid": total_score >= 70,
    }


def main():
    if "--stdin" in sys.argv:
        code_input = sys.stdin.read()
    elif len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            code_input = f.read()
    else:
        # Default test
        code_input = '''def get_nth_fibonacci(n: int) -> int:
    """Returns the nth Fibonacci number."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
'''

    result = evaluate_python_code(code_input)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
