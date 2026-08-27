"""Standalone `vanguard` backend CLI.

Owning contract: WP-C1, `I-5`, ADR-0089 (execution assurance profiles).

The CLI is a *client* of the runtime: it resolves a workspace, obtains operator
key material, and calls the one public execution path
(`Runtime.execute_profiled`). It holds no authority of its own and mints no
identity as a side effect of running work.

Three rules shape this file:

- **Key material is per installation and explicit.** `run` never creates a key;
  `init` does. See `keys.py`.
- **Approval means a human said yes.** Non-interactive execution has no reviewer
  and therefore fails closed unless an explicit scoped grant exists.
- **State creation is explicit.** `.vanguard/` appears because `init` was run,
  not because someone typed `vanguard` in the wrong directory.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from .keys import (
    KeyMaterialError,
    KeyMaterialUnavailable,
    default_key_path,
    interactive_approver,
    load_operator_signer,
)

try:
    from vanguard import __version__
except ImportError:  # pragma: no cover - source checkout without metadata
    __version__ = "0.0.0+unknown"

__all__ = ["main"]

#: Typed exit codes. A single non-zero code cannot distinguish "your task
#: failed" from "this capability is unavailable", and callers -- CI especially
#: -- need that difference to react correctly.
EXIT_OK = 0
EXIT_TASK_FAILED = 1
EXIT_USAGE = 2
EXIT_UNAVAILABLE = 3
EXIT_DENIED = 4

#: Workspace markers, most specific first. `.git` alone is not enough: a
#: monorepo subdirectory has one too.
_ROOT_MARKERS = ("pyproject.toml", "package.json", "Cargo.toml", "go.mod", ".git")

#: Environment keys the CLI is willing to carry from a workspace `.env`. An
#: unfiltered `.env` load is an arbitrary-environment-write primitive, so the
#: values go into a scoped mapping handed to the adapter rather than into the
#: process environment.
_ENV_ALLOWLIST = frozenset({
    "OPENROUTER_API_KEY",
    "OPENROUTER_BASE_URL",
    "DEEPSEEK_API_KEY",
    "VANGUARD_MODEL",
})

_STATE_DIR = ".vanguard"


# -- workspace ---------------------------------------------------------------


def find_workspace_root(start: Path) -> Path:
    """Nearest enclosing directory carrying a repository marker, else `start`."""
    start = start.resolve()
    for candidate in (start, *start.parents):
        for marker in _ROOT_MARKERS:
            if (candidate / marker).exists():
                return candidate
    return start


def _state_dir(workspace: Path) -> Path:
    return workspace / _STATE_DIR


def _require_initialised(workspace: Path) -> Path:
    state = _state_dir(workspace)
    if not state.is_dir():
        raise KeyMaterialUnavailable(
            f"{workspace} is not initialised; run `vanguard init` first"
        )
    return state


def default_manifest_path() -> Path:
    """Locate the bundled default manifest through package resources.

    Path arithmetic from `__file__` resolves only inside a source checkout; an
    installed distribution puts this module somewhere else entirely, so the
    console script would break exactly where it is supposed to work.
    """
    from importlib.resources import files

    resource = files("vanguard.packages.agency").joinpath(
        "manifests", "vg-code-default", "manifest.json"
    )
    return Path(str(resource))


def load_scoped_env(workspace: Path, root: Path | None = None) -> dict[str, str]:
    """Read allowlisted keys from `.env` files into a scoped mapping.

    Never writes `os.environ`. Precedence: real environment, then workspace
    `.env`, then repository-root `.env`.
    """
    scoped: dict[str, str] = {}
    for source in [p for p in (root, workspace) if p is not None]:
        env_file = source / ".env"
        if not env_file.is_file():
            continue
        for line in env_file.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            if key in _ENV_ALLOWLIST:
                scoped[key] = value.strip().strip("'").strip('"')
    for key in _ENV_ALLOWLIST:
        live = os.environ.get(key)
        if live:
            scoped[key] = live
    return scoped


# -- subcommands -------------------------------------------------------------


def cmd_init(args: argparse.Namespace) -> int:
    workspace = find_workspace_root(Path(args.workspace).resolve())
    state = _state_dir(workspace)
    state.mkdir(parents=True, exist_ok=True)
    (state / "blobs").mkdir(parents=True, exist_ok=True)

    key_path = default_key_path()
    created = not key_path.exists()
    try:
        signer = load_operator_signer(allow_create=True)
    except KeyMaterialError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_DENIED

    print(f"workspace   : {workspace}")
    print(f"state       : {state}")
    print(f"operator key: {key_path} ({'created' if created else 'existing'})")
    print(f"public key  : {signer.public_bytes.hex()}")
    return EXIT_OK


def cmd_doctor(args: argparse.Namespace) -> int:
    """Report truthful capability state. Never repairs anything silently."""
    workspace = find_workspace_root(Path(args.workspace).resolve())
    state = _state_dir(workspace)
    rows: list[tuple[str, str, str]] = []

    rows.append(("version", "ok", __version__))
    rows.append(("python", "ok", sys.version.split()[0]))
    rows.append((
        "workspace", "ok" if workspace.is_dir() else "missing", str(workspace)))
    rows.append((
        "state", "ok" if state.is_dir() else "uninitialised",
        f"{state} (run `vanguard init`)" if not state.is_dir() else str(state)))

    key_path = default_key_path()
    try:
        signer = load_operator_signer(allow_create=False)
        rows.append(("operator key", "ok", f"{key_path} {signer.public_bytes.hex()[:16]}…"))
    except KeyMaterialError as exc:
        rows.append(("operator key", "unavailable", str(exc)))

    manifest = default_manifest_path()
    rows.append((
        "default manifest", "ok" if manifest.is_file() else "missing", str(manifest)))

    scoped = load_scoped_env(workspace, _repo_root_of(workspace))
    rows.append((
        "model credentials",
        "ok" if scoped.get("OPENROUTER_API_KEY") else "absent",
        "OPENROUTER_API_KEY present" if scoped.get("OPENROUTER_API_KEY")
        else "no provider key; live execution unavailable"))

    rows.append((
        "approval", "ok" if sys.stdin.isatty() else "non-interactive",
        "TTY attached" if sys.stdin.isatty()
        else "no TTY; approvals deny without an explicit scoped grant"))

    width = max(len(name) for name, _, _ in rows)
    degraded = False
    for name, status, detail in rows:
        if status not in ("ok",):
            degraded = True
        print(f"{name.ljust(width)}  {status.upper():<14} {detail}")
    return EXIT_OK if not degraded else EXIT_UNAVAILABLE


def cmd_run(args: argparse.Namespace) -> int:
    from .compose import TaskContext
    from .root import Runtime
    from ..adapters.models.openrouter import OpenRouterModel
    from ..adapters.stores.blob_store import FileBlobStore

    workspace = find_workspace_root(Path(args.workspace).resolve())
    if not workspace.is_dir():
        print(f"error: workspace {workspace} is not a directory", file=sys.stderr)
        return EXIT_USAGE

    try:
        state = _require_initialised(workspace)
        signer = load_operator_signer(allow_create=False)
    except KeyMaterialUnavailable as exc:
        print(f"unavailable: {exc}", file=sys.stderr)
        return EXIT_UNAVAILABLE
    except KeyMaterialError as exc:
        print(f"denied: {exc}", file=sys.stderr)
        return EXIT_DENIED

    manifest_path = Path(args.manifest) if args.manifest else default_manifest_path()
    if not manifest_path.is_file():
        print(f"unavailable: manifest not found at {manifest_path}", file=sys.stderr)
        return EXIT_UNAVAILABLE

    scoped = load_scoped_env(workspace, _repo_root_of(workspace))
    api_key = scoped.get("OPENROUTER_API_KEY", "")
    if not api_key:
        print(
            "unavailable: no OPENROUTER_API_KEY in environment or allowlisted .env; "
            "live execution requires a provider key",
            file=sys.stderr,
        )
        return EXIT_UNAVAILABLE

    reviewer = args.reviewer or os.environ.get("USER") or "operator"
    approver = interactive_approver(signer, reviewer=reviewer)

    task_ctx = TaskContext(
        brief=args.task,
        repo_path=workspace,
        run_id=args.run_id or "run-cli-standalone",
        episode_id=args.episode_id or "ep-cli-standalone",
        project_id=args.project_id or workspace.name,
        max_turns=args.max_turns,
    )

    print(f"task     : {args.task}")
    print(f"workspace: {workspace}")
    print(f"model    : {args.model}")
    print(f"profile  : {args.profile}")
    print(f"turns    : {args.max_turns}")
    print("-" * 40)

    try:
        result = Runtime.execute_profiled(
            manifest_path,
            task_ctx,
            profile_id=args.profile,
            model=OpenRouterModel(
                model=args.model, stream=False,
                environ={"OPENROUTER_API_KEY": api_key},
            ),
            store_path=str(state / "events.sqlite3"),
            blobs=FileBlobStore(state / "blobs"),
            interactive=True,
            approver=approver,
            approval_key=signer.public_bytes,
        )
    except KeyMaterialUnavailable as exc:
        # An approval was required and no reviewer was reachable. This is a
        # capability failure, not a task failure.
        print(f"\nunavailable: {exc}", file=sys.stderr)
        return EXIT_UNAVAILABLE
    except Exception as exc:  # noqa: BLE001 - surfaced verbatim below
        print(f"error during execution: {exc}", file=sys.stderr)
        if args.traceback:
            import traceback

            traceback.print_exc()
        return EXIT_TASK_FAILED

    _report_result(result)
    if (workspace / ".git").exists():
        # N-06 confines subprocess to the sandbox adapter, and git-backed diff
        # already belongs to EnvironmentPort (`adapters/environment/git.py`).
        # The CLI is a client of the runtime, so it points at the command
        # rather than shelling out around the port. The previous
        # `os.popen(f"git -C {workspace} diff")` also interpolated a
        # user-supplied path into a shell.
        print(f"\nreview changes with: git -C {workspace} diff")

    terminal = str(getattr(result.terminal, "value", result.terminal)).lower()
    return EXIT_OK if terminal in ("succeeded", "success", "completed") else EXIT_TASK_FAILED


def _report_result(result: Any) -> None:
    terminal = str(getattr(result.terminal, "value", result.terminal))
    print(f"\noutcome: {terminal}")
    if getattr(result, "detail", None):
        print(f"detail : {result.detail}")
    telemetry = getattr(result, "telemetry", None)
    if not telemetry:
        return
    print(f"turns  : {telemetry.turns}")
    if telemetry.prompt_tokens is not None and telemetry.completion_tokens is not None:
        print(
            f"tokens : {telemetry.prompt_tokens} prompt + "
            f"{telemetry.completion_tokens} completion = {telemetry.total_tokens} total"
        )
    if telemetry.usd_micros is not None:
        print(f"cost   : ${telemetry.usd_micros / 1_000_000:.4f}")


def _repo_root_of(workspace: Path) -> Path | None:
    for candidate in (workspace, *workspace.parents):
        if (candidate / "pyproject.toml").is_file():
            return candidate
    return None


# -- entrypoint --------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vanguard", description="AETHER standalone backend CLI"
    )
    parser.add_argument("--version", action="version", version=f"vanguard {__version__}")
    sub = parser.add_subparsers(dest="command")

    init = sub.add_parser("init", help="create workspace state and operator key material")
    init.add_argument("-w", "--workspace", default=".")
    init.set_defaults(handler=cmd_init)

    doctor = sub.add_parser("doctor", help="report truthful capability state")
    doctor.add_argument("-w", "--workspace", default=".")
    doctor.set_defaults(handler=cmd_doctor)

    run = sub.add_parser("run", help="execute a task through the canonical runtime")
    run.add_argument("task", help="task brief")
    run.add_argument("-w", "--workspace", default=".")
    run.add_argument("-m", "--model", default=None, help="model identifier")
    run.add_argument("--manifest", default=None, help="manifest path override")
    run.add_argument("--profile", default="product", help="execution profile")
    run.add_argument("--max-turns", type=int, default=20)
    run.add_argument("--reviewer", default=None, help="approval reviewer identity")
    run.add_argument("--run-id", default=None)
    run.add_argument("--episode-id", default=None)
    run.add_argument("--project-id", default=None)
    run.add_argument("--traceback", action="store_true")
    run.set_defaults(handler=cmd_run)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return EXIT_USAGE

    if getattr(args, "model", None) is None and handler is cmd_run:
        from ..adapters.models.config import get_default_model

        args.model = get_default_model()

    try:
        return handler(args)
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        return EXIT_TASK_FAILED


if __name__ == "__main__":
    sys.exit(main())
