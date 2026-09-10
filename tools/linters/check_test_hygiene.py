#!/usr/bin/env python3
"""Fail closed when hermetic test commands inherit live provider credentials or unsafe state."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Mapping

_TOOLS = Path(__file__).resolve().parent
_COMMON = _TOOLS.parent / "common"
for _p in (_COMMON, _TOOLS):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

try:
    from repo_paths import repo_root
except ImportError:
    def repo_root() -> Path:
        return Path(__file__).resolve().parents[2]

PROVIDER_KEYS: tuple[str, ...] = (
    "OPENROUTER_API_KEY",
    "DEEPSEEK_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "MISTRAL_API_KEY",
    "GROQ_API_KEY",
    "TOGETHER_API_KEY",
    "COHERE_API_KEY",
    "AZURE_OPENAI_API_KEY",
    "HF_TOKEN",
    "HUGGINGFACE_API_KEY",
    "AWS_SECRET_ACCESS_KEY",
)

_GENERIC_KEY_PATTERN = re.compile(r"^[A-Z0-9_]+_(?:API_KEY|AUTH_TOKEN|SECRET_KEY)$")


def exported_provider_keys(env: Mapping[str, str] | None = None) -> tuple[str, ...]:
    """Return all provider credentials found in the environment."""
    environ = os.environ if env is None else env
    found: list[str] = []
    # Check explicitly declared provider keys first in fixed order
    for key in PROVIDER_KEYS:
        if environ.get(key):
            found.append(key)
    # Check for generic credential naming patterns
    for key, val in environ.items():
        if val and key not in found:
            if _GENERIC_KEY_PATTERN.match(key) and not key.startswith("VANGUARD_TEST_"):
                found.append(key)
    return tuple(found)


def detect_unsafe_inherited_state(
    env: Mapping[str, str] | None = None,
    root: Path | None = None,
) -> list[str]:
    """Detect unsafe inherited paths or flags that could contaminate hermetic execution."""
    environ = os.environ if env is None else env
    try:
        r = (root or repo_root()).resolve()
    except Exception:
        r = Path(__file__).resolve().parents[2]

    violations: list[str] = []

    # 1. LAM_DB_PATH pointing directly to tracked repo corpus
    lam_path_str = environ.get("LAM_DB_PATH")
    if lam_path_str:
        lam_path = Path(lam_path_str).resolve()
        tracked_lam = (r / "tools" / "002_LLM_API_MOCK" / "lam.sqlite").resolve()
        if lam_path == tracked_lam:
            violations.append(f"LAM_DB_PATH points directly to tracked repo corpus: {lam_path}")

    # 2. AETHER_WORKSPACE_ROOT pointing to repository root
    ws_root_str = environ.get("AETHER_WORKSPACE_ROOT")
    if ws_root_str:
        ws_root = Path(ws_root_str).resolve()
        if ws_root == r:
            violations.append(f"AETHER_WORKSPACE_ROOT points directly to repository root: {ws_root}")

    # 3. Writable directory overrides pointing inside tracked code trees
    unsafe_source_dirs = (
        r / "vanguard",
        r / "test",
        r / "docs",
        r / "schemas",
        r / "packs",
    )
    for var in ("TMPDIR", "TMP", "TEMP", "PYTHONPYCACHEPREFIX", "npm_config_cache"):
        val = environ.get(var)
        if val:
            p = Path(val).resolve()
            for sdir in unsafe_source_dirs:
                if p == sdir or sdir in p.parents:
                    violations.append(f"{var} points inside repository source tree: {p}")
                    break

    return violations


def check_test_hygiene(
    env: Mapping[str, str] | None = None,
    root: Path | None = None,
) -> list[str]:
    """Run complete test hygiene check returning all detected violations."""
    violations: list[str] = []
    for key in exported_provider_keys(env):
        violations.append(f"Provider credential {key} is set; hermetic suites require provider keys unset")
    violations.extend(detect_unsafe_inherited_state(env, root))
    return violations


def main() -> int:
    violations = check_test_hygiene()
    if violations:
        for v in violations:
            print(f"TEST HYGIENE FAIL: {v}")
        return 1
    print("TEST HYGIENE PASS: provider keys and inherited state are clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
