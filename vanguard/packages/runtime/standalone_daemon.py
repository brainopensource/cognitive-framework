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

# Ensure parent directory of 'vanguard' is on sys.path for direct script execution
_current_file = Path(__file__).resolve()
_lib_root = _current_file.parent.parent.parent.parent
if str(_lib_root) not in sys.path:
    sys.path.insert(0, str(_lib_root))

from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.adapters.stores.blob_store import FileBlobStore
from vanguard.packages.runtime.governance.approvals import ApprovalAuthority, OperatorSigner
from vanguard.packages.runtime.keys import default_key_path, load_operator_signer
from vanguard.packages.runtime.service import (
    RuntimeServer,
    RuntimeService,
    ServiceInboxStore,
)

try:
    from vanguard import __version__
except ImportError:
    __version__ = "0.9.0b1"


def get_default_paths() -> tuple[Path, Path, Path, Path]:
    """Resolves standard XDG/platform paths for production runtime."""
    home = Path.home()
    if sys.platform == "win32":
        local_app_data = Path(os.environ.get("LOCALAPPDATA", home / "AppData" / "Local"))
        state_dir = local_app_data / "Aether" / "state"
        data_dir = local_app_data / "Aether" / "data"
        socket_path = state_dir / "runtime.sock"
    elif sys.platform == "darwin":
        state_dir = home / "Library" / "Application Support" / "Aether" / "state"
        data_dir = home / "Library" / "Application Support" / "Aether" / "data"
        socket_path = state_dir / "runtime.sock"
    else:
        # Linux / XDG
        xdg_state = Path(os.environ.get("XDG_STATE_HOME", home / ".local" / "state"))
        xdg_data = Path(os.environ.get("XDG_DATA_HOME", home / ".local" / "share"))
        state_dir = xdg_state / "aether"
        data_dir = xdg_data / "aether"
        sock_env = os.environ.get("AETHER_RUNTIME_SOCK")
        socket_path = Path(sock_env) if sock_env else Path("/tmp/vanguard-runtime.sock")

    pid_file = state_dir / "runtime.pid"
    return socket_path, state_dir, data_dir, pid_file


class StandaloneRuntimeDaemon:
    def __init__(
        self,
        socket_path: Path,
        state_dir: Path,
        data_dir: Path,
        pid_file: Path,
        json_output: bool = False,
    ) -> None:
        self.socket_path = socket_path
        self.state_dir = state_dir
        self.data_dir = data_dir
        self.pid_file = pid_file
        self.json_output = json_output

        self.server: RuntimeServer | None = None
        self._shutdown_requested = False

    def log(self, message: str, **kwargs: Any) -> None:
        if self.json_output:
            out = {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "message": message, **kwargs}
            print(json.dumps(out), flush=True)
        else:
            print(f"[AETHER DAEMON] {message}", flush=True)

    def _acquire_lock(self) -> bool:
        """Enforces single-instance ownership via PID lockfile."""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        if self.pid_file.exists():
            try:
                old_pid = int(self.pid_file.read_text(encoding="utf-8").strip())
                # Check if old pid is alive
                os.kill(old_pid, 0)
                self.log(f"Another runtime instance is already running with PID {old_pid}.", error="already_running")
                return False
            except (ValueError, ProcessLookupError, PermissionError):
                # Stale PID file, safe to clean
                self.pid_file.unlink(missing_ok=True)

        # Write current PID
        self.pid_file.write_text(f"{os.getpid()}\n", encoding="utf-8")
        return True

    def _release_lock(self) -> None:
        if self.pid_file.exists():
            try:
                self.pid_file.unlink(missing_ok=True)
            except OSError:
                pass

    def start(self) -> int:
        if not self._acquire_lock():
            return 1

        from vanguard.packages.adapters.models.env_loader import ensure_openrouter_key_loaded

        key_source = ensure_openrouter_key_loaded(
            (
                os.environ.get("AETHER_HOME") or "",
                os.environ.get("VANGUARD_ROOT") or "",
                os.environ.get("AETHER_REPO_ROOT") or "",
                _lib_root,
            )
        )
        if key_source == "missing":
            self.log("OPENROUTER_API_KEY is not set; live OpenRouter runs will fail closed")
        else:
            self.log("OPENROUTER_API_KEY is present for live model calls")

        # Clean existing dead socket file if present
        if self.socket_path.exists():
            try:
                self.socket_path.unlink(missing_ok=True)
            except OSError:
                pass

        # Setup persistent stores
        events_db_path = self.data_dir / "events.db"
        blobs_dir_path = self.data_dir / "blobs"
        inbox_db_path = self.data_dir / "inbox.db"

        event_store = SqliteEventStore(events_db_path)
        blob_store = FileBlobStore(blobs_dir_path)
        inbox_store = ServiceInboxStore(inbox_db_path)

        signer = load_operator_signer(allow_create=True)
        authority = ApprovalAuthority(public_keys={signer.key_id: signer.public_bytes})

        service = RuntimeService(
            inbox_store=inbox_store,
            event_store=event_store,
            authority=authority,
        )

        self.server = RuntimeServer(
            service=service,
            socket_path=str(self.socket_path),
        )

        # Setup Signal Handlers for graceful shutdown
        def handle_signal(sig: int, frame: Any) -> None:
            if not self._shutdown_requested:
                self._shutdown_requested = True
                self.log(f"Received signal {sig}, initiating graceful shutdown...")
                if self.server:
                    self.server.stop()
                self._release_lock()
                sys.exit(0)

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

        # Ensure directory of socket has 0700 permissions
        self.socket_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(self.socket_path.parent, 0o700)
        except OSError:
            pass

        self.server.start()

        if self.json_output:
            print(
                json.dumps(
                    {
                        "status": "ready",
                        "pid": os.getpid(),
                        "socket": str(self.socket_path),
                        "version": __version__,
                        "protocol": "vg.4",
                        "dataDir": str(self.data_dir),
                        "stateDir": str(self.state_dir),
                    }
                ),
                flush=True,
            )
        else:
            self.log(f"RuntimeService online at {self.socket_path} (PID {os.getpid()}, version {__version__})")

        try:
            while not self._shutdown_requested:
                time.sleep(0.5)
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            if self.server:
                self.server.stop()
            self._release_lock()

        return 0


def main() -> int:
    def_sock, def_state, def_data, def_pid = get_default_paths()

    parser = argparse.ArgumentParser(description="AETHER Standalone Runtime Daemon")
    parser.add_argument("--socket", type=Path, default=def_sock, help="Path to Unix Domain Socket")
    parser.add_argument("--state-dir", type=Path, default=def_state, help="Path to mutable state directory")
    parser.add_argument("--data-dir", type=Path, default=def_data, help="Path to mutable data directory")
    parser.add_argument("--pid-file", type=Path, default=def_pid, help="Path to PID lockfile")
    parser.add_argument("--json", action="store_true", help="Emit structured NDJSON log events")
    args = parser.parse_args()

    daemon = StandaloneRuntimeDaemon(
        socket_path=args.socket,
        state_dir=args.state_dir,
        data_dir=args.data_dir,
        pid_file=args.pid_file,
        json_output=args.json,
    )
    return daemon.start()


if __name__ == "__main__":
    sys.exit(main())
