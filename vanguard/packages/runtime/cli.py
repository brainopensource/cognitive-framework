"""Standalone `vanguard` backend CLI (BETA-01, BETA-03, BETA-04, BETA-05).

Owning contract: WP-C1, `I-5`, ADR-0089 (execution assurance profiles).

The CLI is a *client* of the runtime: it resolves a workspace, obtains operator
key material, and calls the public ApplicationService / Runtime paths.
It holds no authority of its own and mints no identity as a side effect of running work.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from .app_service import ApplicationService
from .keys import (
    KeyMaterialError,
    KeyMaterialUnavailable,
    default_key_path,
    interactive_approver,
    load_operator_signer,
)
from .state_contract import inspect_state_directory, resolve_state_directory

try:
    from vanguard import __version__
except ImportError:  # pragma: no cover - source checkout without metadata
    __version__ = "0.9.0b1"

__all__ = ["main"]

#: Typed exit codes.
EXIT_OK = 0
EXIT_TASK_FAILED = 1
EXIT_USAGE = 2
EXIT_UNAVAILABLE = 3
EXIT_DENIED = 4

_ROOT_MARKERS = ("pyproject.toml", "package.json", "Cargo.toml", "go.mod", ".git")
_STATE_DIR = ".vanguard"


def find_workspace_root(start: Path) -> Path:
    """Nearest enclosing directory carrying a repository marker, else `start`."""
    start = start.resolve()
    for candidate in (start, *start.parents):
        for marker in _ROOT_MARKERS:
            if (candidate / marker).exists():
                return candidate
    return start


def _repo_root_of(workspace: Path) -> Path | None:
    for candidate in (workspace, *workspace.parents):
        if (candidate / "pyproject.toml").is_file():
            return candidate
    return None


def default_manifest_path() -> Path:
    """Locate the bundled default manifest through package resources."""
    from importlib.resources import files

    resource = files("vanguard.packages.agency").joinpath(
        "manifests", "vg-code-default", "manifest.json"
    )
    return Path(str(resource))


# -- subcommands -------------------------------------------------------------


def cmd_init(args: argparse.Namespace) -> int:
    workspace = find_workspace_root(Path(args.workspace).resolve())
    state_dir = resolve_state_directory(workspace, state_dir=getattr(args, "state_dir", None))
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "blobs").mkdir(parents=True, exist_ok=True)

    key_path = default_key_path()
    created = not key_path.exists()
    try:
        signer = load_operator_signer(allow_create=True)
    except KeyMaterialError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_DENIED

    print(f"workspace   : {workspace}")
    print(f"state       : {state_dir}")
    print(f"operator key: {key_path} ({'created' if created else 'existing'})")
    print(f"public key  : {signer.public_bytes.hex()}")
    return EXIT_OK


def cmd_doctor(args: argparse.Namespace) -> int:
    """Report truthful capability state. Never repairs anything silently."""
    workspace = find_workspace_root(Path(args.workspace).resolve())
    app = ApplicationService(workspace=workspace)
    report = app.doctor(profile_id=getattr(args, "profile", "product"), state_dir=getattr(args, "state_dir", None))

    rows: list[tuple[str, str, str]] = []
    for check in report.checks:
        rows.append((check.name, check.status, check.detail))

    width = max(len(name) for name, _, _ in rows)
    degraded = report.health != "healthy" or report.readiness != "ready"

    print(f"Vanguard {report.version} — Health: {report.health.upper()}, Readiness: {report.readiness.upper()}\n")
    for name, status, detail in rows:
        print(f"{name.ljust(width)}  {status.upper():<14} {detail}")

    return EXIT_OK if not degraded else EXIT_UNAVAILABLE


def cmd_run(args: argparse.Namespace) -> int:
    workspace = find_workspace_root(Path(args.workspace).resolve())
    if not workspace.is_dir():
        print(f"error: workspace {workspace} is not a directory", file=sys.stderr)
        return EXIT_USAGE

    app = ApplicationService(workspace=workspace)
    try:
        res = app.run(
            brief=args.task,
            manifest_path=args.manifest,
            profile_id=args.profile,
            run_id=args.run_id,
            model_port=args.model_port if hasattr(args, "model_port") else None,
            planner_model=args.model,
            state_dir=getattr(args, "state_dir", None),
            interactive=not getattr(args, "non_interactive", False),
            max_turns=args.max_turns,
        )
    except Exception as exc:
        print(f"error during run: {exc}", file=sys.stderr)
        if getattr(args, "traceback", False):
            import traceback
            traceback.print_exc()
        return EXIT_TASK_FAILED

    print(f"\nrun_id : {res.run_id}")
    print(f"outcome: {res.outcome}")
    print(f"turns  : {res.turns}")
    if res.plan_digest:
        print(f"digest : {res.plan_digest}")
    if res.detail:
        print(f"detail : {res.detail}")

    return EXIT_OK if res.outcome in ("completed", "success", "succeeded") else EXIT_TASK_FAILED


def cmd_resume(args: argparse.Namespace) -> int:
    workspace = find_workspace_root(Path(args.workspace).resolve())
    app = ApplicationService(workspace=workspace)
    try:
        res = app.resume(
            run_id=args.run_id,
            state_dir=getattr(args, "state_dir", None),
            profile_id=getattr(args, "profile", "product"),
        )
    except Exception as exc:
        print(f"error resuming run {args.run_id}: {exc}", file=sys.stderr)
        return EXIT_TASK_FAILED

    print(f"\nrun_id : {res.run_id}")
    print(f"outcome: {res.outcome}")
    print(f"turns  : {res.turns}")
    return EXIT_OK if res.outcome in ("completed", "success", "succeeded") else EXIT_TASK_FAILED


def cmd_status(args: argparse.Namespace) -> int:
    workspace = find_workspace_root(Path(args.workspace).resolve())
    app = ApplicationService(workspace=workspace)
    res = app.status(run_id=args.run_id, state_dir=getattr(args, "state_dir", None))

    print(f"run_id     : {res.run_id}")
    print(f"status     : {res.status}")
    print(f"event_count: {res.event_count}")
    print(f"as_of_seq  : {res.as_of_seq}")
    if res.detail:
        print(f"detail     : {res.detail}")
    return EXIT_OK


def cmd_events(args: argparse.Namespace) -> int:
    workspace = find_workspace_root(Path(args.workspace).resolve())
    app = ApplicationService(workspace=workspace)
    try:
        res = app.events(
            run_id=args.run_id,
            after_seq=getattr(args, "after_seq", 0),
            limit=getattr(args, "limit", None),
            state_dir=getattr(args, "state_dir", None),
        )
    except Exception as exc:
        print(f"error fetching events: {exc}", file=sys.stderr)
        return EXIT_TASK_FAILED

    if getattr(args, "json", False):
        print(json.dumps(res.to_dict(), indent=2))
    else:
        for evt in res.events:
            seq = evt.get("seq", 0)
            payload = evt.get("payload", {})
            kind = payload.get("kind", "Event")
            principal = evt.get("principal", "unknown")
            print(f"[{seq:04d}] {kind:<24} principal={principal}")

    return EXIT_OK


def cmd_artifacts(args: argparse.Namespace) -> int:
    workspace = find_workspace_root(Path(args.workspace).resolve())
    app = ApplicationService(workspace=workspace)
    res = app.artifact(
        digest=args.digest,
        state_dir=getattr(args, "state_dir", None),
    )

    if not res.verified or res.content is None:
        print(f"error: artifact {args.digest} could not be verified: {res.error}", file=sys.stderr)
        return EXIT_TASK_FAILED

    print(f"digest   : {res.digest}")
    print(f"verified : {res.verified}")
    print(f"bytes    : {len(res.content)}")
    if getattr(args, "output", None):
        out_p = Path(args.output).resolve()
        out_p.write_bytes(res.content)
        print(f"saved to : {out_p}")
    else:
        try:
            text = res.content.decode("utf-8")
            print(f"\n--- Content ---\n{text}")
        except UnicodeDecodeError:
            print(f"\n(binary content, {len(res.content)} bytes)")
    return EXIT_OK


# -- entrypoint --------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vanguard", description="AETHER standalone backend CLI"
    )
    parser.add_argument("--version", action="version", version=f"vanguard {__version__}")
    parser.add_argument("--state-dir", default=None, help="custom state directory override")
    sub = parser.add_subparsers(dest="command")

    # init
    init = sub.add_parser("init", help="create workspace state and operator key material")
    init.add_argument("-w", "--workspace", default=".")
    init.set_defaults(handler=cmd_init)

    # doctor
    doctor = sub.add_parser("doctor", help="report truthful capability state")
    doctor.add_argument("-w", "--workspace", default=".")
    doctor.add_argument("--profile", default="product", help="execution profile to qualify")
    doctor.set_defaults(handler=cmd_doctor)

    # run
    run = sub.add_parser("run", help="execute a task through the canonical runtime")
    run.add_argument("task", help="task brief")
    run.add_argument("-w", "--workspace", default=".")
    run.add_argument("-m", "--model", default=None, help="model identifier")
    run.add_argument("--model-port", default=None, help="model provider port (mock, fake, openrouter, etc.)")
    run.add_argument("--manifest", default=None, help="manifest path override")
    run.add_argument("--profile", default="product", help="execution profile")
    run.add_argument("--max-turns", type=int, default=20)
    run.add_argument("--run-id", default=None)
    run.add_argument("--non-interactive", action="store_true", help="disable interactive human review")
    run.add_argument("--traceback", action="store_true")
    run.set_defaults(handler=cmd_run)

    # resume
    resume = sub.add_parser("resume", help="resume an existing run from durable ledger state")
    resume.add_argument("run_id", help="run identifier to resume")
    resume.add_argument("-w", "--workspace", default=".")
    resume.add_argument("--profile", default="product", help="execution profile")
    resume.set_defaults(handler=cmd_resume)

    # status
    status = sub.add_parser("status", help="query execution status and event count for a run")
    status.add_argument("run_id", help="run identifier")
    status.add_argument("-w", "--workspace", default=".")
    status.set_defaults(handler=cmd_status)

    # events
    events = sub.add_parser("events", help="query causally ordered events for a run")
    events.add_argument("run_id", help="run identifier")
    events.add_argument("-w", "--workspace", default=".")
    events.add_argument("--after-seq", type=int, default=0, help="sequence number to read after")
    events.add_argument("--limit", type=int, default=None, help="maximum events to return")
    events.add_argument("--json", action="store_true", help="output as JSON")
    events.set_defaults(handler=cmd_events)

    # artifacts
    artifacts = sub.add_parser("artifacts", help="retrieve and verify content-addressed artifact bytes")
    artifacts.add_argument("digest", help="content digest (sha256:...)")
    artifacts.add_argument("-w", "--workspace", default=".")
    artifacts.add_argument("-o", "--output", default=None, help="output file path")
    artifacts.set_defaults(handler=cmd_artifacts)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return EXIT_USAGE

    try:
        return handler(args)
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        return EXIT_TASK_FAILED


if __name__ == "__main__":
    sys.exit(main())
