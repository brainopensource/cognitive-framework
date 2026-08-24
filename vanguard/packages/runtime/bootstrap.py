"""`RuntimeBootstrap` — the sole composition-root seam for concrete adapters
(`ADR-0089 §Decision 2`, W3D-03).

Before W-3D, `root.py.execute_harness()` and `lab_driver.py` each construct
`RootlessSandboxRunner`/`GitEnvironmentAdapter`/`OpenRouterModel` inline,
gated by a duplicated `sandbox_mode: str` parameter (see ADR-0089 §Context
point 1). `RuntimeBootstrap.build()` is the one place authorized to turn a
requested `ExecutionProfile` into concrete adapters. `Runtime` stays thin: it
calls the bootstrap and runs what it returns; it does not choose the
provider, the sandbox backend, or the store.

This module is additive. `root.py`'s existing `sandbox_mode`/`release`
parameters are not removed here — W3D-12 sunsets them only after every
caller has migrated to a profile and the developer preview/RF-85
requalification are green (`ADR-0089` rollback-by-slice discipline).
"""

from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping

from ..adapters.environment.git import GitEnvironmentAdapter
from ..adapters.environment.sandboxed import SandboxedEnvironmentAdapter
from ..adapters.sandbox.rootless import RootlessSandboxRunner
from ..adapters.sandbox.worker import WorkerProtocol
from ..adapters.stores.event_store import SqliteEventStore
from .determinism import ClockPort, SystemClock
from .profiles import EffectiveExecutionProfile, resolve_profile
from .wiring import _bwrap_path

__all__ = ["RuntimeDependencies", "RuntimeBootstrap"]


@dataclass(frozen=True)
class RuntimeDependencies:
    """Every concrete adapter one run needs, resolved once, outside the loop.

    `cleanup()` releases anything the bootstrap allocated (e.g. a sealed
    worker temp dir); callers MUST call it after the run, success or not —
    `Runtime.run_composed` does not know about bootstrap-owned resources.
    """

    model: Any
    store: Any
    environment: Any
    profile: EffectiveExecutionProfile
    clock: ClockPort
    cleanup: Callable[[], None] = field(default=lambda: None)


class RuntimeBootstrap:
    """The one place authorized to select concrete adapters from a profile."""

    @staticmethod
    def build(
        *,
        profile_id: str,
        repo_path: Path,
        model: Any = None,
        store: Any = None,
        clock: ClockPort | None = None,
        host_qualifies: bool = True,
        host_facts: Mapping[str, Any] | None = None,
        overrides: Mapping[str, Any] | None = None,
    ) -> RuntimeDependencies:
        """Resolve `profile_id` and construct exactly the adapters it names.

        Raises `SandboxUnavailable` (from `profiles.resolve_profile`) if a
        containment-bearing profile is requested and `host_qualifies` is
        false. There is no fallback branch here — that is the point.
        """
        profile = resolve_profile(
            profile_id, host_qualifies=host_qualifies, host_facts=host_facts, overrides=overrides,
        )
        repo = Path(repo_path).resolve()
        selected_store = store or SqliteEventStore(":memory:")
        cleanup: Callable[[], None] = lambda: None

        if profile.requested.process_backend == "host":
            environment: Any = GitEnvironmentAdapter(
                repo, environment_id=f"workspace-{profile.requested.id}:{repo}")
        else:
            bwrap = _bwrap_path()
            sealed_dir = Path(tempfile.mkdtemp(prefix="vg-sealed-worker-"))
            sealed_bundle = sealed_dir / "bundle"
            sealed_bundle.write_bytes(
                b"sealed evaluator mount is intentionally unavailable to worker\n")
            worker = WorkerProtocol(
                RootlessSandboxRunner(repo, evaluator_bundle=sealed_bundle, runtime=bwrap))
            environment = SandboxedEnvironmentAdapter(
                worker, repo, environment_id=f"workspace:{repo}")

            def cleanup() -> None:
                shutil.rmtree(sealed_dir, ignore_errors=True)

            if profile.requested.assurance_level == "hermetic":
                qualified = environment.qualify()
                if not qualified.ok:
                    cleanup()
                    raise RuntimeError(
                        f"hermetic containment qualification failed: {qualified.error.kind}: "
                        f"{qualified.error.message}")

        selected_model = model
        if selected_model is None:
            from ..adapters.models.openrouter import OpenRouterModel

            selected_model = OpenRouterModel()

        return RuntimeDependencies(
            model=selected_model,
            store=selected_store,
            environment=environment,
            profile=profile,
            clock=clock or SystemClock(),
            cleanup=cleanup,
        )
