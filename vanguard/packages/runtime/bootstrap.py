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
from .workspace import get_workspace_path

__all__ = ["RuntimeDependencies", "RuntimeBootstrap"]


def _resolve_model_adapter(model: Any, profile_id: str) -> Any:
    """Turn a caller `model` into a `ModelPort`.

    Product clients send a catalog id such as `openrouter/free` on the
    StartRun wire. That is a string, not an adapter. Using it as a port
    makes `propose` explode (`str` has no such method) and the TUI looks
    like it did nothing. Offline `local`/`ci` still get FakeModel when
    no model is named.
    """
    import os

    from .model_selection import MODEL_PORTS, select_model

    if model is not None and not isinstance(model, str):
        return model

    name = str(model).strip() if isinstance(model, str) else ""
    if not name:
        model_port = os.environ.get("VANGUARD_MODEL_PORT")
        if model_port:
            return select_model(model_port).model
        if profile_id in {"local", "ci"}:
            return select_model("fake").model
        return select_model("openrouter").model

    lowered = name.lower()
    if lowered in MODEL_PORTS:
        return select_model(lowered).model
    return select_model("openrouter", model_name=name).model


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
        store_path: Path | None = None,
        state_dir: Path | str | None = None,
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
        if store is not None:
            selected_store = store
        elif profile.requested.persistence_mode == "sqlite-wal":
            from .state_contract import ensure_state_directory, resolve_state_directory
            if store_path is not None:
                db_path = Path(store_path).resolve()
                ensure_state_directory(db_path.parent, durability_mode="sqlite-wal")
            else:
                resolved_state = resolve_state_directory(repo, state_dir=state_dir)
                ensure_state_directory(resolved_state, durability_mode="sqlite-wal")
                db_path = resolved_state / "events.sqlite3"
            selected_store = SqliteEventStore(db_path)
        else:
            selected_store = SqliteEventStore(":memory:")
        cleanup: Callable[[], None] = lambda: None

        if profile.requested.process_backend == "host":
            environment: Any = GitEnvironmentAdapter(
                repo, environment_id=f"workspace-{profile.requested.id}:{repo}")
        else:
            bwrap = _bwrap_path()
            sealed_dir = Path(tempfile.mkdtemp(prefix="vg-sealed-worker-", dir=get_workspace_path("sandboxes")))
            sealed_bundle = sealed_dir / "bundle"
            sealed_bundle.write_bytes(
                b"sealed evaluator mount is intentionally unavailable to worker\n")
            worker = WorkerProtocol(
                RootlessSandboxRunner(repo, evaluator_bundle=sealed_bundle, runtime=bwrap))
            environment = SandboxedEnvironmentAdapter(
                worker, repo, environment_id=f"workspace:{repo}",
                direct_filesystem=True)

            def cleanup() -> None:
                shutil.rmtree(sealed_dir, ignore_errors=True)

            if profile.requested.assurance_level == "hermetic":
                qualified = environment.qualify()
                if not qualified.ok:
                    cleanup()
                    raise RuntimeError(
                        f"hermetic containment qualification failed: {qualified.error.kind}: "
                        f"{qualified.error.message}")

        selected_model = _resolve_model_adapter(model, profile.requested.id)
        if selected_model is None:
            raise RuntimeError(f"no model adapter could be selected or resolved for profile {profile_id!r}")

        return RuntimeDependencies(
            model=selected_model,
            store=selected_store,
            environment=environment,
            profile=profile,
            clock=clock or SystemClock(),
            cleanup=cleanup,
        )
