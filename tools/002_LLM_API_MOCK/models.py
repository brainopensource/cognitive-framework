"""OpenRouter model band registry and loader."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List

# Ensure we can import vanguard if not already in path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from vanguard.packages.adapters.models.config import load_model_registry

def load_models() -> Dict[str, List[str]]:
    """Load model bands from vanguard model registry."""
    registry = load_model_registry()
    data = registry.get("bands", {})
    for band in ("free", "medium", "high", "top"):
        if band not in data or not isinstance(data[band], list):
            raise ValueError(f"models_registry.json must contain array for band '{band}'")
    return data

def models_for_band(band: str) -> List[str]:
    """Return models for a band. Raises RuntimeError if top is requested while empty."""
    band_name = band.lower().strip()
    models = load_models()
    if band_name not in models:
        raise ValueError(f"Unknown band '{band}'. Valid bands: free, medium, high, top")

    if band_name == "top" and not models["top"]:
        raise RuntimeError("Project Lead must name three top OpenRouter model ids in models.json before band=top")

    return models[band_name]
