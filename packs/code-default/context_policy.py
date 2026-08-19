"""Context compaction + repo-map budgets from harness.yaml (H-2)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import sys
from pathlib import Path as _Path

_PACK = _Path(__file__).resolve().parent
if str(_PACK) not in sys.path:
    sys.path.insert(0, str(_PACK))

from load import load_harness  # noqa: E402

__all__ = ["context_policy_from_harness"]


def context_policy_from_harness(harness: Mapping[str, Any] | None = None, *, pack_root: Path | None = None) -> dict[str, Any]:
    data = dict(harness or load_harness(pack_root / "harness.yaml" if pack_root else None))
    plugins = data.get("plugins") if isinstance(data.get("plugins"), dict) else {}
    context = plugins.get("context") if isinstance(plugins, dict) else {}
    config = context.get("config") if isinstance(context, dict) else {}
    if not isinstance(config, dict):
        config = {}
    return {
        "token_budget": int(config.get("token_budget") or 4000),
        "compaction": str(config.get("compaction") or "recency-window"),
        "prefix_freeze": bool(config.get("prefix_freeze", True)),
        "system_prompt": str(data.get("system_prompt") or "./system-prompt.txt"),
    }
