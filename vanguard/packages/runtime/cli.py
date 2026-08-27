"""
AUTO-GENERATED: Vanguard Standalone CLI
"""

import argparse
import os
import sys
from pathlib import Path

from .compose import TaskContext
from .root import Runtime
from .autonomous_grant import create_autonomous_grant
from .governance.approvals import OperatorSigner
from ..adapters.models.openrouter import OpenRouterModel
from ..adapters.models.config import get_default_model
from ..adapters.stores.blob_store import FileBlobStore
try:
    from vanguard import __version__
except ImportError:
    __version__ = "0.1.0"

def main():
    parser = argparse.ArgumentParser(description="Vanguard CLI")
    parser.add_argument("task", nargs="?", help="The task description / brief (e.g. 'fix bug in file.py')", default=None)
    parser.add_argument("-t", "--task", dest="task_opt", help="The task description / brief", default=None)
    parser.add_argument("-w", "--workspace", default=".", help="Path to the target project workspace")
    parser.add_argument("-m", "--model", default=get_default_model(), help="Model name to execute with")
    parser.add_argument("--max-turns", type=int, default=20, help="Maximum turn ceiling")
    parser.add_argument("--profile", default="product", help="Execution profile")
    parser.add_argument("-v", "--version", action="store_true", help="Print version")
    
    args = parser.parse_args()

    if args.version:
        print(f"Vanguard CLI v{__version__}")
        sys.exit(0)

    task_brief = args.task or args.task_opt
    if not task_brief:
        parser.error("Task description must be provided either as a positional argument or via -t/--task.")

    workspace = Path(args.workspace).resolve()
    
    if not workspace.is_dir():
        print(f"Error: Workspace path '{workspace}' is not a directory.", file=sys.stderr)
        sys.exit(1)
        
    vanguard_dir = workspace / ".vanguard"
    vanguard_dir.mkdir(parents=True, exist_ok=True)
    
    env_file = workspace / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip().strip("'").strip('"')
        
    root_dir = Path(__file__).resolve().parents[3]
    manifest_path = root_dir / "vanguard" / "packages" / "agency" / "manifests" / "vg-code-default" / "manifest.json"

    from ..adapters.models.env_loader import load_api_key

    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        res_ws = load_api_key(workspace)
        if res_ws.ok and res_ws.value:
            api_key = res_ws.value
        else:
            res_root = load_api_key(root_dir)
            if res_root.ok and res_root.value:
                api_key = res_root.value

    if not api_key:
        print("Warning: OPENROUTER_API_KEY not found in environment, workspace .env, or root .env", file=sys.stderr)

    task_ctx = TaskContext(
        brief=task_brief,
        repo_path=workspace,
        run_id="run-cli-standalone",
        episode_id="ep-cli-standalone",
        project_id="vanguard-cli",
        max_turns=args.max_turns
    )
    
    seed_key = b"vanguard-autonomous-operator-seed-key"
    grant = create_autonomous_grant(
        workspace,
        allowed_verbs=("fs.read", "fs.search", "patch.apply", "proc.exec"),
        max_turns=args.max_turns,
        max_attempts=1,
        seed_key=seed_key,
    )
    signer = OperatorSigner(seed_key)
    model = OpenRouterModel(model=args.model, stream=False, environ={"OPENROUTER_API_KEY": api_key})
    
    print(f"Executing task: '{task_brief}'")
    print(f"Workspace: {workspace}")
    print(f"Model: {args.model}")
    print(f"Profile: {args.profile}")
    print(f"Max Turns: {args.max_turns}")
    print("----------------------------------------")

    try:
        result = Runtime.execute_profiled(
            manifest_path, 
            task_ctx,
            profile_id=args.profile,
            model=model,
            store_path=str(vanguard_dir / "events.sqlite3"),
            blobs=FileBlobStore(vanguard_dir / "blobs"),
            interactive=True,
            approver=lambda challenge: signer.approve(challenge, reviewer=grant.reviewer),
            approval_key=signer.public_bytes
        )
        
        terminal = str(getattr(result.terminal, "value", result.terminal))
        print(f"\nExecution finished with outcome: {terminal}")
        if result.detail:
            print(f"Detail: {result.detail}")
        print("Summary:")
        
        telemetry = result.telemetry
        if telemetry:
            print(f"  Turns Taken: {telemetry.turns}")
            if telemetry.prompt_tokens is not None and telemetry.completion_tokens is not None:
                print(f"  Tokens: {telemetry.prompt_tokens} prompt + {telemetry.completion_tokens} completion = {telemetry.total_tokens} total")
            if telemetry.usd_micros is not None:
                cost_usd = telemetry.usd_micros / 1_000_000
                print(f"  Cost: ${cost_usd:.4f}")
        
        print("-" * 40)
        
        if (workspace / ".git").exists():
            diff = os.popen(f"git -C {workspace} diff").read()
            if diff:
                print("\nGenerated Git Diff:")
                print(diff)
            else:
                print("\nNo uncommitted git changes found.")
        else:
            print("\n(No git repository found in workspace to show diff)")

    except Exception as e:
        print(f"Error during execution: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
