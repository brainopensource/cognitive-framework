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
from ..adapters.stores.lda_index import LdaRepoIndex
from ..adapters.stores.repo_index import FileRepoIndex, workspace_tree_hash
from ..domain.workspace_epoch import WorkspaceEpoch
from ..ports.event_store import PortFailure, Result
from ..ports.index import IndexHealthVerdict, IndexSelection, RepositoryMap
from .determinism import ClockPort, SystemClock
from .profiles import EffectiveExecutionProfile, resolve_profile
from .wiring import _bwrap_path
from .workspace import get_workspace_path

__all__ = [
    "RuntimeDependencies",
    "RuntimeBootstrap",
    "ProductionIndexBinding",
    "select_production_index",
    "PRODUCTION_INDEX_SELECTION_ENABLED",
    "PRODUCTION_INDEX_REJECT_UNUSABLE",
]

PRODUCTION_INDEX_SELECTION_ENABLED = True
PRODUCTION_INDEX_REJECT_UNUSABLE = True


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
    index: Any = None
    index_selection: IndexSelection | None = None
    index_error: PortFailure | None = None


@dataclass(frozen=True, slots=True)
class ProductionIndexBinding:
    """Composition-root index binding for session integration (DIR-I5 / ADR-0107)."""

    port: Any
    selection: IndexSelection


def _epoch_from_map(mapped: RepositoryMap, *, compiled_at_turn: int) -> WorkspaceEpoch:
    return WorkspaceEpoch(
        tree_hash=mapped.tree_hash,
        index_digest=mapped.index_digest,
        source_revision=mapped.source_revision,
        compiled_at_turn=compiled_at_turn,
    )


def _bind_file_index(
    root: Path,
    *,
    verdict: IndexHealthVerdict,
    reason: str,
    compiled_at_turn: int,
) -> Result[ProductionIndexBinding]:
    port = FileRepoIndex()
    indexed = port.index(str(root))
    if not indexed.ok:
        kind = "INDEX_ABSENT" if verdict == "optional_absent" else "INDEX_INVALID"
        message = indexed.error.message if indexed.error else "file index unavailable"
        return Result.fail(kind, message, retryable=False)
    mapped = port.repo_map()
    if not mapped.ok or mapped.value is None:
        message = mapped.error.message if mapped.error else "file index map unbound"
        return Result.fail("INDEX_INVALID", message, retryable=False)
    selection = IndexSelection(
        backend="file",
        source_identity=_epoch_from_map(mapped.value, compiled_at_turn=compiled_at_turn),
        health_verdict=verdict,
        degradation_reason=reason,
        unresolved_coverage=True,
    )
    return Result.success(ProductionIndexBinding(port=port, selection=selection))


def select_production_index(
    repo_path: str | Path,
    *,
    required: bool = False,
    prior: IndexSelection | None = None,
    refresh: bool = False,
    compiled_at_turn: int = 0,
    db_path: str | Path | None = None,
    selection_enabled: bool = PRODUCTION_INDEX_SELECTION_ENABLED,
    reject_unusable: bool = PRODUCTION_INDEX_REJECT_UNUSABLE,
) -> Result[ProductionIndexBinding]:
    """DIR-I5 five-state production index selection.

    Returns a selected `IndexPort` plus an `IndexSelection` value. Failures are
    typed, non-retryable, and never fabricate an empty graph or an epoch.
    """
    root = Path(repo_path).resolve()
    lda_db = Path(db_path).resolve() if db_path is not None else root / ".lda" / "index.db"

    if prior is not None and not refresh:
        current_tree = workspace_tree_hash(root)
        if current_tree is None or current_tree != prior.source_identity.tree_hash:
            return Result.fail(
                "INDEX_SUBJECT_CHANGED",
                "workspace changed after index selection; refresh required",
                retryable=False,
            )

    def required_unbound(message: str) -> Result[ProductionIndexBinding]:
        return Result.fail("INDEX_REQUIRED_UNBOUND", message, retryable=False)

    if not selection_enabled:
        if required:
            return required_unbound("production LDA selection disabled")
        return _bind_file_index(
            root,
            verdict="optional_absent",
            reason="lda_selection_disabled",
            compiled_at_turn=compiled_at_turn,
        )

    lda_present = lda_db.is_file()
    if not lda_present:
        if required:
            return required_unbound(f"required LDA index missing at {lda_db}")
        return _bind_file_index(
            root,
            verdict="optional_absent",
            reason="lda_absent",
            compiled_at_turn=compiled_at_turn,
        )

    lda = LdaRepoIndex(db_path=lda_db)
    indexed = lda.index(str(root), enforce_freshness=reject_unusable)
    if indexed.ok:
        mapped = lda.repo_map()
        if mapped.ok and mapped.value is not None:
            unresolved = bool(lda.unresolved_coverage or mapped.value.truncated)
            selection = IndexSelection(
                backend="lda",
                source_identity=_epoch_from_map(
                    mapped.value, compiled_at_turn=compiled_at_turn
                ),
                health_verdict="healthy_current",
                degradation_reason=None,
                unresolved_coverage=unresolved,
            )
            return Result.success(ProductionIndexBinding(port=lda, selection=selection))
        cause = mapped.error.message if mapped.error else "LDA repo_map unbound"
    else:
        cause = indexed.error.message if indexed.error else "LDA index unusable"

    if required:
        return required_unbound(cause)
    return _bind_file_index(
        root,
        verdict="present_invalid",
        reason=cause,
        compiled_at_turn=compiled_at_turn,
    )


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

        index_result = select_production_index(repo)
        if index_result.ok and index_result.value is not None:
            selected_index = index_result.value.port
            selected_selection = index_result.value.selection
            selected_index_error: PortFailure | None = None
        else:
            selected_index = None
            selected_selection = None
            selected_index_error = index_result.error

        return RuntimeDependencies(
            model=selected_model,
            store=selected_store,
            environment=environment,
            profile=profile,
            clock=clock or SystemClock(),
            cleanup=cleanup,
            index=selected_index,
            index_selection=selected_selection,
            index_error=selected_index_error,
        )
