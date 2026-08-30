"""Self-Contained Standalone Production Daemon for RuntimeService.

Spawns and manages the RuntimeServer listening on Unix Domain Socket or Named Pipe,
enforces single-instance ownership via PID lockfile, and handles graceful SIGINT/SIGTERM.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import time
from pathlib import Path
from typing import Any

from ..adapters.stores.event_store import SqliteEventStore
from ..adapters.stores.blob_store import FileBlobStore
from .governance.approvals import ApprovalAuthority, OperatorSigner
from .keys import default_key_path, load_operator_signer
from .service import (
    RuntimeServer,
    RuntimeService,
    ServiceInboxStore,
)

try:
    from vanguard import __version__
except ImportError:
    __version__ = "0.9.1-rc1"


def get_default_paths() -> tuple[Path, Path, Path, Path]:
    """Resolve platform-appropriate defaults for data, state, socket, and PID."""
    home = Path.home()
    if sys.platform == "win32":
        local_app = Path(os.environ.get("LOCALAPPDATA", home / "AppData" / "Local")) / "Aether"
        state_dir = local_app / "state"
        data_dir = local_app / "data"
        socket_path = state_dir / "runtime.sock"
        pid_file = state_dir / "runtime.pid"
    elif sys.platform == "darwin":
        state_dir = home / "Library" / "Application Support" / "Aether" / "state"
        data_dir = home / "Library" / "Application Support" / "Aether" / "data"
        socket_path = state_dir / "runtime.sock"
        pid_file = state_dir / "runtime.pid"
    else:
        xdg_state = Path(os.environ.get("XDG_STATE_HOME", home / ".local" / "state")) / "aether"
        xdg_data = Path(os.environ.get("XDG_DATA_HOME", home / ".local" / "share")) / "aether"
        state_dir = xdg_state
        data_dir = xdg_data
        socket_path = Path("/tmp/vanguard-runtime.sock")
        pid_file = state_dir / "runtime.pid"

    return state_dir, data_dir, socket_path, pid_file


def is_process_alive(pid: int) -> bool:
    """Check if process with PID is currently alive."""
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def main(argv: list[str] | None = None) -> int:
    default_state, default_data, default_sock, default_pid = get_default_paths()

    parser = argparse.ArgumentParser(description="AETHER Managed Runtime Daemon")
    parser.add_argument(
        "--socket-path",
        default=os.environ.get("AETHER_RUNTIME_SOCK", str(default_sock)),
        help="Socket path to bind",
    )
    parser.add_argument(
        "--state-dir",
        default=os.environ.get("AETHER_STATE_DIR", str(default_state)),
        help="State directory for logs and PID",
    )
    parser.add_argument(
        "--data-dir",
        default=os.environ.get("AETHER_DATA_DIR", str(default_data)),
        help="Data directory for SQLite events and blobs",
    )
    parser.add_argument(
        "--pid-file",
        default=os.environ.get("AETHER_PID_FILE", str(default_pid)),
        help="PID lockfile path",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON structured readiness facts to stdout",
    )

    args = parser.parse_args(argv)

    sock_path = Path(args.socket_path).resolve()
    state_dir = Path(args.state_dir).resolve()
    data_dir = Path(args.data_dir).resolve()
    pid_file = Path(args.pid_file).resolve()

    state_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    sock_path.parent.mkdir(parents=True, exist_ok=True)
    pid_file.parent.mkdir(parents=True, exist_ok=True)

    # 1. Check PID lockfile for single managed ownership
    if pid_file.exists():
        try:
            existing_pid = int(pid_file.read_text(encoding="utf-8").strip())
            if is_process_alive(existing_pid):
                info = {
                    "status": "already_running",
                    "pid": existing_pid,
                    "socket": str(sock_path),
                    "version": __version__,
                }
                if args.json:
                    print(json.dumps(info), flush=True)
                else:
                    print(f"AETHER Runtime daemon is already running (PID {existing_pid}) on {sock_path}")
                return 0
            else:
                # Stale PID file, clean up
                pid_file.unlink(missing_ok=True)
        except Exception:
            pid_file.unlink(missing_ok=True)

    # Write current PID
    my_pid = os.getpid()
    pid_file.write_text(str(my_pid), encoding="utf-8")

    # 2. Initialize operator signer and authority
    try:
        signer = load_operator_signer(allow_create=True)
        authority = ApprovalAuthority({signer.key_id: signer.public_bytes})
    except Exception:
        signer = OperatorSigner(key_id="op-default")
        authority = ApprovalAuthority({signer.key_id: signer.public_bytes})

    # 3. Initialize durable stores
    db_path = data_dir / "aether_inbox.db"
    inbox = ServiceInboxStore(db_path)
    service = RuntimeService(inbox, authority=authority)

    # 4. Start RuntimeServer
    server = RuntimeServer(service, sock_path)
    server.start()

    # 5. Signal handling for graceful shutdown
    stop_event = False

    def handle_signal(signum: int, frame: Any) -> None:
        nonlocal stop_event
        stop_event = True

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    if hasattr(signal, "SIGHUP"):
        signal.signal(signal.SIGHUP, handle_signal)

    # Emit readiness message to stdout
    ready_info = {
        "status": "ready",
        "pid": my_pid,
        "socket": str(sock_path),
        "version": __version__,
        "protocol": "vg.4",
        "dataDir": str(data_dir),
        "stateDir": str(state_dir),
    }
    if args.json:
        print(json.dumps(ready_info), flush=True)
    else:
        print(f"AETHER RuntimeService daemon listening at {sock_path} (PID {my_pid})", flush=True)

    try:
        while not stop_event:
            time.sleep(0.2)
    finally:
        server.stop()
        inbox.close()
        pid_file.unlink(missing_ok=True)
        if sock_path.exists():
            try:
                sock_path.unlink()
            except OSError:
                pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
