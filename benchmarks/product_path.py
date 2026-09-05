"""Single product execution path for canaries and the L0 public-CLI ladder.

Callers go through ``runtime.entrypoint.execute`` so a benchmark cannot
qualify a different subject than ``vg code`` ships.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from vanguard.packages.runtime.entrypoint import execute, _manifest

__all__ = ["PRODUCT_PRESETS", "execute_product", "manifest_for_preset"]

PRODUCT_PRESETS = {
    "vg-code-fast": "fast",
    "vg-code-balanced": "balanced",
    "vg-code-max": "max",
}


def manifest_for_preset(preset: str) -> Path:
    return _manifest("code", preset)


def execute_product(
    *,
    workspace: Path | str,
    brief: str,
    preset: str = "balanced",
    harness: str | None = None,
    model: Any = None,
    profile_id: str = "product",
    run_id: str | None = None,
    store_path: Path | str | None = None,
    interactive: bool = False,
    allow_paid: bool = False,
    fake_backend: str | None = None,
    max_turns: int | None = None,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Invoke the public product entrypoint in-process."""
    command = "explain" if harness == "vg-code-explain" else "code"
    chosen = PRODUCT_PRESETS.get(harness or "", preset)
    request: dict[str, Any] = {
        "command": command,
        "workspace": str(workspace),
        "brief": brief,
        "preset": chosen,
        "profile": profile_id,
        "interactive": interactive,
        "allowPaid": allow_paid,
    }
    if run_id:
        request["runId"] = run_id
    if store_path is not None:
        request["storePath"] = str(store_path)
    if max_turns is not None:
        request["maxTurnsPerEpisode"] = max_turns
    if fake_backend:
        request["fakeBackend"] = fake_backend
    if model is not None:
        request["injectedModel"] = model
    if harness and harness not in PRODUCT_PRESETS and harness != "vg-code-explain":
        request["harness"] = harness
    if extra:
        request.update(dict(extra))
    return execute(request)
