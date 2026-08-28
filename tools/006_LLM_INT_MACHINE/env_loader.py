"""Safe environment and API key loader for 006_LLM_INT_MACHINE."""

from __future__ import annotations
import os
from pathlib import Path


def load_openrouter_api_key(search_root: Path | None = None) -> str:
    """Find and load OPENROUTER_API_KEY safely."""
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if key:
        return key
    
    current = search_root or Path(__file__).resolve().parent
    for _ in range(5):
        env_file = current / ".env"
        if env_file.is_file():
            try:
                for line in env_file.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k == "OPENROUTER_API_KEY" and v:
                        os.environ["OPENROUTER_API_KEY"] = v
                        return v
            except Exception:
                pass
        current = current.parent
    
    return ""


def has_openrouter_api_key() -> bool:
    return bool(load_openrouter_api_key())
