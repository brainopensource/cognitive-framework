#!/usr/bin/env python3
"""
Empirical Sweet Spot Validation Runner for LED Engine.
Location: tools/003_LLM_ENGINE_DESKTOP/matrix_execution/validate_sweet_spot.py
Usage:
    python3 validate_sweet_spot.py [MODEL_NAME]
Example:
    python3 validate_sweet_spot.py qwen2.5:1.5b
    python3 validate_sweet_spot.py qwen2.5-coder:14b
"""

import ast
import json
import os
from pathlib import Path
import sys
import time
import urllib.request

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_FILE = BASE_DIR / "docs" / "prompts" / "fibo_challenge_finetune.md"
PRESETS_DIR = BASE_DIR / "presets"
OLLAMA_API_URL = "http://localhost:11434/api/generate"

DEFAULT_MODEL = "qwen2.5:1.5b"
MODEL_NAME = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODEL
sanitized_model = MODEL_NAME.replace(":", "_").replace("-", "_").replace(".", "")
PRESET_JSON = PRESETS_DIR / f"{sanitized_model}_turbo.json"

if not PRESET_JSON.exists():
    print(f"Error: Preset file not found at {PRESET_JSON}")
    print("Please run `train_surrogate.py` first to generate the sweet spot preset.")
    sys.exit(1)


def evaluate_python_code(code_str: str) -> tuple[int, str]:
    """Evaluates code quality (0-100) via AST parsing and validation rules."""
    score = 0
    feedback = []

    clean_code = code_str
    if "```python" in clean_code:
        clean_code = clean_code.split("```python")[1].split("```")[0].strip()
    elif "```" in clean_code:
        clean_code = clean_code.split("```")[1].split("```")[0].strip()

    try:
        parsed = ast.parse(clean_code)
        score += 30
        feedback.append("Syntax: OK")
    except SyntaxError as e:
        feedback.append(f"Syntax: Error ({e.msg})")
        return max(score, 10), " | ".join(feedback)

    has_target_func = False
    has_type_hints = False
    for node in ast.walk(parsed):
        if isinstance(node, ast.FunctionDef) and node.name == "get_nth_fibonacci":
            has_target_func = True
            if node.returns is not None:
                has_type_hints = True

    if has_target_func:
        score += 25
        feedback.append("Func: Present")
    else:
        feedback.append("Func: Missing")

    if has_type_hints:
        score += 15
        feedback.append("Types: Yes")
    else:
        feedback.append("Types: No")

    if "ValueError" in code_str:
        score += 15
        feedback.append("Validation: OK")
    else:
        feedback.append("Validation: No ValueError")

    if not code_str.startswith("```") and "Sure!" not in code_str and "<think>" not in code_str:
        score += 15
        feedback.append("Purity: Pure Code")
    else:
        feedback.append("Purity: Has Markdown/Talk")

    return score, " | ".join(feedback)


def main():
    print("=" * 70)
    print("🎯 EMPIRICAL SWEET SPOT VALIDATION RUNNER")
    print(f"Target Model : {MODEL_NAME}")
    print(f"Preset File  : {PRESET_JSON}")
    print("=" * 70)

    with open(PRESET_JSON, "r", encoding="utf-8") as f:
        preset = json.load(f)

    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        prompt = f.read().strip()

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": preset.get("options", {})
    }
    if preset.get("system_prompt"):
        payload["system"] = preset["system_prompt"]

    print("\n[*] Executing Live Validation Inference on Ollama...")
    print(f"    Options: {payload['options']}")
    
    req = urllib.request.Request(
        OLLAMA_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    start_wall = time.perf_counter()
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
    end_wall = time.perf_counter()

    actual_wall_sec = end_wall - start_wall
    eval_count = res.get("eval_count", 0)
    eval_dur_sec = res.get("eval_duration", 1) / 1e9
    actual_tps = eval_count / eval_dur_sec if eval_dur_sec > 0 else 0
    raw_response = res.get("response", "")

    # Evaluate Code
    score, feedback = evaluate_python_code(raw_response)

    pred_latency = preset.get("predicted_latency_sec", 0.0)
    pred_tps = preset.get("predicted_tps", 0.0)

    delta_latency = abs(actual_wall_sec - pred_latency) / actual_wall_sec * 100 if actual_wall_sec > 0 else 0
    delta_tps = abs(actual_tps - pred_tps) / actual_tps * 100 if actual_tps > 0 else 0

    print("\n" + "=" * 70)
    print("📊 EMPIRICAL VALIDATION RESULTS vs. MACHINE LEARNING PREDICTION")
    print("=" * 70)
    print(f"| Métrica                 | ML Predito | Real Medido | Erro Delta (Δ%) |")
    print(f"| :---------------------- | :--------: | :---------: | :-------------: |")
    print(f"| **Latência de Relógio** | **{pred_latency:.2f} s** | **{actual_wall_sec:.2f} s** | **{delta_latency:.1f}%** |")
    print(f"| **Velocidade (TPS)**    | **{pred_tps:.2f} t/s** | **{actual_tps:.2f} t/s** | **{delta_tps:.1f}%** |")
    print(f"| **Nota de Código (AST)**| $\ge 85/100$ | **{score}/100** | {'✅ PASSOU' if score >= 85 else '❌ FALHOU'} |")
    print("=" * 70)
    print(f"Detalhes da AST: {feedback}")
    print("\n✅ Validação concluída com sucesso!")


if __name__ == "__main__":
    main()
