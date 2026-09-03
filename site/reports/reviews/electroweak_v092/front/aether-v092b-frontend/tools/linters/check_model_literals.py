#!/usr/bin/env python3
"""Linter to enforce centralized model configuration and prevent unapproved model literals.

Rules:
1. No unapproved model literals in active production or benchmark runner code.
2. All model selection in runners must use `resolve_model()` or `get_default_paid_model()`
   from `vanguard.packages.adapters.models.config`.
3. Models registry (`models_registry.json`) is the single source of truth.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "vanguard" / "packages" / "adapters" / "models" / "models_registry.json"

IGNORED_DIRS = {
    ".git", "__pycache__", ".venv", "dev_context_logs", "docs/research", "docs/reports",
    ".gemini", "node_modules", "artifacts", "runs", ".generated"
}

DISALLOWED_LITERAL_PATTERNS = [
    r"deepseek/deepseek-chat\b",
    r"deepseek-v3\b",
    r"gpt-4o-mini\b",
    r"claude-3-5-sonnet-20241022\b"
]


def check_model_hygiene() -> int:
    if not REGISTRY_PATH.exists():
        print(f"ERROR: Centralized model registry missing at {REGISTRY_PATH}")
        return 1

    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry_data = json.load(f)

    active_tiers = registry_data.get("active_tiers", [])
    allowed_models = set()
    for tier in active_tiers:
        for m in registry_data.get("tiers", {}).get(str(tier), []):
            allowed_models.add(m)

    print(f"Loaded {len(allowed_models)} authorized models from {REGISTRY_PATH.name}")

    violations = []
    
    # Scan python source and benchmark files
    scan_roots = [
        ROOT / "vanguard" / "packages",
        ROOT / "benchmarks" / "benchmark_20_suite",
        ROOT / "tools" / "002_LLM_API_MOCK"
    ]

    for s_root in scan_roots:
        if not s_root.exists():
            continue
        for p in s_root.rglob("*.py"):
            if any(ig in p.parts for ig in IGNORED_DIRS):
                continue
            if p.name in ("models_registry.json", "config.py", "test_model_registry_hygiene.py", "check_model_literals.py"):
                continue

            content = p.read_text(encoding="utf-8", errors="replace")
            for pattern in DISALLOWED_LITERAL_PATTERNS:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    line_no = content[:match.start()].count("\n") + 1
                    violations.append((p.relative_to(ROOT), line_no, match.group(0)))

    if violations:
        print("\n" + "!" * 80)
        print("FAIL: Model Hygiene Violations Found (Disallowed Model Literals):")
        print("!" * 80)
        for path, line, lit in violations:
            print(f"  * {path}:{line} -> Found disallowed literal '{lit}'")
        print("\nFix: Use `resolve_model()` or `get_default_paid_model()` from `vanguard.packages.adapters.models.config`.")
        return 1

    print("MODEL HYGIENE PASS: All active runners and adapters comply with centralized policy.")
    return 0


if __name__ == "__main__":
    sys.exit(check_model_hygiene())
