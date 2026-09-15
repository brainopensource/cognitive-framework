"""Request/result ergonomics for Coding Max.

This module is intentionally a client of ``ApplicationService``. It owns
preset selection and the public operation names, while runtime owns model
selection, effect mediation, persistence, and recovery.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ...runtime import pack_catalog
from ...runtime.app_service import ApplicationService
from ...runtime.pack_catalog import InvalidPreset
from ...runtime.results import CostResult, EvidenceResult, RunResult, StatusResult

__all__ = ["CodingMax", "CodingMaxFacade", "InvalidPreset"]


class _CatalogPresets:
    """``PRESETS`` on the class *and* on an instance, read from the catalog.

    T-102. The names are a projection of ``presets.json``, resolved lazily so
    importing the facade does not compile the pack. This class holds no second
    list of its own.
    """

    def __get__(self, instance: object, owner: type | None = None) -> tuple[str, ...]:
        return pack_catalog.preset_names()


class CodingMaxFacade:
    """Request/result ergonomics only. Every decision below is the runtime's."""

    PRESETS = _CatalogPresets()

    def __init__(self, workspace: str | Path | None = None, *, service: ApplicationService | None = None) -> None:
        self.service = service or ApplicationService(workspace=workspace)

    def run(
        self, brief: str, *, preset: str = "balanced", profile_id: str = "local",
        run_id: str | None = None, model: Any = None, model_port: str | None = "fake",
        planner_model: str | None = None,
        state_dir: str | Path | None = None, interactive: bool = True,
        max_turns: int | None = None,
    ) -> RunResult:
        # Declared catalog stays on the composed policy. An explicit
        # ``max_turns`` only attenuates the loop bound. Both the allowlist and
        # the attenuation rule live in ``pack_catalog``; this facade owns
        # neither, so a CLI/API/facade call with the same preset cannot resolve
        # a different manifest or a different ceiling.
        manifest = pack_catalog.preset_manifest_path(preset)
        turns = pack_catalog.turn_ceiling(preset, max_turns)
        return self.service.run(
            brief=brief, manifest_path=manifest, profile_id=profile_id,
            run_id=run_id, model=model, model_port=model_port, planner_model=planner_model, state_dir=state_dir,
            interactive=interactive, max_turns=turns,
        )

    def status(self, run_id: str, *, state_dir: str | Path | None = None) -> StatusResult:
        return self.service.status(run_id, state_dir=state_dir)

    def resume(
        self, run_id: str, *, profile_id: str = "local", model: Any = None,
        model_port: str | None = "fake", state_dir: str | Path | None = None,
    ) -> RunResult:
        return self.service.resume(
            run_id=run_id, profile_id=profile_id, model=model,
            model_port=model_port, state_dir=state_dir,
        )

    def evidence(self, run_id: str, *, state_dir: str | Path | None = None) -> EvidenceResult:
        return self.service.evidence(run_id, state_dir=state_dir)

    def cost(self, run_id: str, *, state_dir: str | Path | None = None) -> CostResult:
        return self.service.cost(run_id, state_dir=state_dir)


CodingMax = CodingMaxFacade
