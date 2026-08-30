#!/usr/bin/env python3
"""
Dual-LLM Collaborative Coding & Self-Correction Harness.
- Model 1 (Tester): Generates comprehensive unittest test cases for a problem specification.
- Model 2 (Coder): Generates the code implementation and self-corrects iteratively based on test execution feedback.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.request
from typing import Tuple

CODER_MODEL = "qwen2.5-coder:7b-instruct-q5_K_M"
TESTER_MODEL = "granite4.1:8b"
OLLAMA_API = "http://localhost:11434/api/chat"


def call_llm(model: str, messages: list, num_ctx: int = 4096, temperature: float = 0.1) -> str:
    payload = {
        "model": model,
        "messages": messages,
        "options": {"num_ctx": num_ctx, "temperature": temperature},
        "stream": False,
    }
    req = urllib.request.Request(
        OLLAMA_API,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["message"]["content"]


def extract_python_code(text: str) -> str:
    blocks = re.findall(r"```python\s*(.*?)\s*```", text, re.DOTALL)
    if blocks:
        return blocks[-1].strip()
    return text.replace("```python", "").replace("```", "").strip()


def run_tests_unittest(solution_code: str, test_code: str) -> Tuple[bool, str]:
    with tempfile.TemporaryDirectory() as tmpdir:
        sol_path = os.path.join(tmpdir, "solution.py")
        test_path = os.path.join(tmpdir, "test_solution.py")

        with open(sol_path, "w", encoding="utf-8") as f:
            f.write(solution_code)

        # Make sure unittest runner is present
        full_test = test_code
        if "from solution import" not in full_test and "import solution" not in full_test:
            full_test = "from solution import *\n" + full_test
        if "unittest.main()" not in full_test:
            full_test += "\n\nif __name__ == '__main__':\n    unittest.main()\n"

        with open(test_path, "w", encoding="utf-8") as f:
            f.write(full_test)

        proc = subprocess.run(
            [sys.executable, "-m", "unittest", "test_solution.py", "-v"],
            capture_output=True,
            text=True,
            cwd=tmpdir,
            timeout=10,
        )

        passed = proc.returncode == 0
        output = proc.stdout + "\n" + proc.stderr
        return passed, output.strip()


def run_dual_agent_workflow(task_description: str, max_rounds: int = 4):
    print("=" * 70)
    print(f"🤖 DUAL-LLM COLLABORATIVE CODER (Local on GPU)")
    print(f"• Tester Agent : {TESTER_MODEL}")
    print(f"• Coder Agent  : {CODER_MODEL}")
    print(f"• Tarefa       : {task_description}")
    print("=" * 70)

    # 1. Tester Agent generates the test suite
    print(f"\n[1/3] 🧪 Tester Agent ({TESTER_MODEL}) está gerando a suíte de testes...")
    t0 = time.time()
    tester_prompt = f"""You are a QA / Senior Test Engineer.
Write a comprehensive unittest test file (`test_solution.py`) for the following task:

Task:
{task_description}

Requirements:
- Use `import unittest` and `class TestSolution(unittest.TestCase)`.
- Import functions from `solution`.
- Include standard cases, edge cases (empty input, punctuation, whitespaces, case sensitivity).
- Provide ONLY Python code enclosed in a ```python block.
"""
    tester_msgs = [
        {"role": "system", "content": "You are a test engineer. Output only Python unittest code."},
        {"role": "user", "content": tester_prompt},
    ]
    raw_tests = call_llm(TESTER_MODEL, tester_msgs)
    test_code = extract_python_code(raw_tests)
    print(f"✓ Testes gerados em {time.time() - t0:.2f}s!")
    print("\n--- SUÍTE DE TESTES GERADA PELO TESTER ---")
    print(test_code)

    # 2. Coder Agent generates initial implementation
    print(f"\n[2/3] 💻 Coder Agent ({CODER_MODEL}) está gerando a implementação inicial...")
    coder_msgs = [
        {
            "role": "system",
            "content": "You are an expert Python engineer. Provide only complete, correct Python code inside a ```python block.",
        },
        {
            "role": "user",
            "content": f"Implement the following task in `solution.py`:\n{task_description}\n\nHere are the unit tests your code will be tested against:\n```python\n{test_code}\n```",
        },
    ]
    t0 = time.time()
    raw_coder = call_llm(CODER_MODEL, coder_msgs)
    sol_code = extract_python_code(raw_coder)
    print(f"✓ Código inicial gerado em {time.time() - t0:.2f}s!")

    # 3. Iterative Feedback Loop
    print(f"\n[3/3] 🔄 Executando testes e iniciando loop de feedback (Max {max_rounds} rodadas)...")
    for round_num in range(1, max_rounds + 1):
        print(f"\n--- RODADA {round_num}/{max_rounds} ---")
        passed, output = run_tests_unittest(sol_code, test_code)

        if passed:
            print("🎉 SUCESSO! Todos os testes do Tester Agent passaram no Coder Agent!")
            print("\n=== CÓDIGO FINAL APROVADO ===")
            print(sol_code)
            print("\n=== RELATÓRIO DO UNITTEST ===")
            print(output)
            return True

        print(f"❌ Falha nos testes!")
        print(output)

        if round_num < max_rounds:
            print(f"\n📨 Enviando feedback de erro dos testes para o Coder ({CODER_MODEL}) consertar...")
            coder_msgs.append({"role": "assistant", "content": f"```python\n{sol_code}\n```"})
            coder_msgs.append(
                {
                    "role": "user",
                    "content": f"Your implementation failed the tests with this error output:\n```text\n{output}\n```\nPlease fix the bug and return the complete corrected `solution.py` in a ```python block.",
                }
            )
            t0 = time.time()
            raw_coder = call_llm(CODER_MODEL, coder_msgs)
            sol_code = extract_python_code(raw_coder)
            print(f"✓ Nova versão corrigida gerada em {time.time() - t0:.2f}s!")

    print("\n⚠️ Limite de rodadas atingido sem aprovação total.")
    return False


if __name__ == "__main__":
    task = "Write a function `def is_anagram(s1: str, s2: str) -> bool` that checks if two strings are anagrams of each other (ignoring case, spaces, and punctuation)."
    run_dual_agent_workflow(task, max_rounds=3)
