"""OpenRouter model band registry and loader."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

MODELS_FILE = Path(__file__).resolve().parent / "models.json"


def load_models() -> Dict[str, List[str]]:
    """Load model bands from models.json."""
    if not MODELS_FILE.is_file():
        raise FileNotFoundError(f"models.json missing at {MODELS_FILE}")
    data = json.loads(MODELS_FILE.read_text(encoding="utf-8"))
    for band in ("free", "medium", "high", "top"):
        if band not in data or not isinstance(data[band], list):
            raise ValueError(f"models.json must contain array for band '{band}'")
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
