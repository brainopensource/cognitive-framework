"""Request/result ergonomics for Coding Max.

This module is intentionally a client of ``ApplicationService``. It owns
preset selection and the public operation names, while runtime owns model
selection, effect mediation, persistence, and recovery.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from ...runtime.app_service import ApplicationService
from ...runtime.results import RunResult, StatusResult

__all__ = ["CodingMax", "CodingMaxFacade", "InvalidPreset"]


class InvalidPreset(ValueError):
    """The caller requested a preset outside the frozen Coding Max catalog."""


class CodingMaxFacade:
    PRESETS = ("fast", "balanced", "max")

    def __init__(self, workspace: str | Path | None = None, *, service: ApplicationService | None = None) -> None:
        self.service = service or ApplicationService(workspace=workspace)

    @classmethod
    def _validate_preset(cls, preset: str) -> str:
        if preset not in cls.PRESETS:
            raise InvalidPreset(f"unknown Coding Max preset {preset!r}")
        return preset

    @staticmethod
    def _manifest(preset: str) -> Path:
        from importlib.resources import files
        return Path(str(files("vanguard.packages.agency").joinpath(
            "manifests", f"vg-code-{preset}", "manifest.json")))

    def run(
        self, brief: str, *, preset: str = "balanced", profile_id: str = "local",
        run_id: str | None = None, model: Any = None, model_port: str | None = "fake",
        planner_model: str | None = None,
        state_dir: str | Path | None = None, interactive: bool = True,
        max_turns: int = 40,
    ) -> RunResult:
        chosen = self._validate_preset(preset)
        return self.service.run(
            brief=brief, manifest_path=self._manifest(chosen), profile_id=profile_id,
            run_id=run_id, model=model, model_port=model_port, planner_model=planner_model, state_dir=state_dir,
            interactive=interactive, max_turns=max_turns,
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

    def evidence(self, run_id: str, *, state_dir: str | Path | None = None) -> Mapping[str, Any]:
        return self.service.evidence(run_id, state_dir=state_dir)

    def cost(self, run_id: str, *, state_dir: str | Path | None = None) -> Mapping[str, Any]:
        return self.service.cost(run_id, state_dir=state_dir)


CodingMax = CodingMaxFacade
