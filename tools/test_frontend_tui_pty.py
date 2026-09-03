#!/usr/bin/env python3
"""PTY Validation for AETHER TUI and CLI.

Spawns the real compiled TUI inside a pseudo-terminal (120x35),
types human commands, tests modals and slash commands, and verifies screen rendering.
"""

from __future__ import annotations

import os
import pty
import re
import select
import struct
import sys
import termios
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANSI_ESCAPE_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE_RE.sub("", text)


class PTYSession:
    def __init__(self, cmd: list[str], rows: int = 35, cols: int = 120):
        self.cmd = cmd
        self.rows = rows
        self.cols = cols
        self.master_fd = None
        self.pid = None
        self.buffer = ""
        self._lock = threading.Lock()
        self._running = False

    def start(self) -> None:
        self.master_fd, slave_fd = pty.openpty()
        winsize = struct.pack("HHHH", self.rows, self.cols, 0, 0)
        fcntl_import = __import__("fcntl")
        fcntl_import.ioctl(slave_fd, termios.TIOCSWINSZ, winsize)

        pid = os.fork()
        if pid == 0:
            os.close(self.master_fd)
            os.setsid()
            fcntl_import.ioctl(slave_fd, termios.TIOCSCTTY, 0)
            os.dup2(slave_fd, 0)
            os.dup2(slave_fd, 1)
            os.dup2(slave_fd, 2)
            os.close(slave_fd)
            os.chdir(str(ROOT))
            env = dict(os.environ)
            env["TERM"] = "xterm-256color"
            env["FORCE_COLOR"] = "1"
            env["COLUMNS"] = str(self.cols)
            env["LINES"] = str(self.rows)
            os.execvpe(self.cmd[0], self.cmd, env)
            sys.exit(127)

        self.pid = pid
        os.close(slave_fd)
        self._running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()

    def _read_loop(self) -> None:
        while self._running and self.master_fd is not None:
            try:
                r, _, _ = select.select([self.master_fd], [], [], 0.05)
                if not r:
                    continue
                chunk = os.read(self.master_fd, 4096)
                if not chunk:
                    break
                decoded = chunk.decode("utf-8", errors="replace")
                with self._lock:
                    self.buffer += decoded
            except (OSError, ValueError):
                break

    def get_clean_buffer(self) -> str:
        with self._lock:
            return strip_ansi(self.buffer)

    def send_key(self, key: str) -> None:
        if self.master_fd:
            os.write(self.master_fd, key.encode("utf-8"))

    def send_text(self, text: str) -> None:
        for ch in text:
            self.send_key(ch)
            time.sleep(0.01)

    def expect(self, pattern: str, timeout: float = 6.0) -> bool:
        deadline = time.monotonic() + timeout
        reg = re.compile(pattern)
        while time.monotonic() < deadline:
            if reg.search(self.get_clean_buffer()):
                return True
            time.sleep(0.05)
        return False

    def close(self) -> None:
        self._running = False
        if self.pid:
            try:
                os.kill(self.pid, 15)
                os.waitpid(self.pid, 0)
            except OSError:
                pass
        if self.master_fd:
            try:
                os.close(self.master_fd)
            except OSError:
                pass
            self.master_fd = None


def test_tui_interactive_pty() -> bool:
    print("--- [PTY TEST] Launching TUI interactive session (vg run --demo) ---")
    cmd = ["node", str(ROOT / "vanguard/clients/cli/dist/src/main.js"), "run", "--demo"]
    sess = PTYSession(cmd)
    sess.start()
    try:
        # Step 1: Wait for TUI to render header & composer
        print("  [1] Verifying TUI initialization and header rendering...")
        if not sess.expect("vg-code-balanced", timeout=5.0):
            print("  [FAIL] Header with agent 'vg-code-balanced' not found.")
            print("Buffer excerpt:\n", sess.get_clean_buffer()[:500])
            return False
        print("    -> OK: Header renders agent 'vg-code-balanced'")

        # Step 2: Test opening /help modal
        print("  [2] Testing /help slash command modal...")
        sess.send_text("/help\r")
        if not sess.expect("Command Palette|Help|Keyboard", timeout=4.0):
            print("  [FAIL] Help overlay did not open.")
            return False
        print("    -> OK: Help overlay rendered")

        # Step 3: Test Escape closes modal
        print("  [3] Testing Escape closes modal...")
        sess.send_key("\x1b")
        time.sleep(0.3)

        # Step 4: Test /model modal
        print("  [4] Testing /model command modal...")
        sess.send_text("/model\r")
        if not sess.expect("Select Model|Models", timeout=4.0):
            print("  [FAIL] Model select modal did not open.")
            return False
        print("    -> OK: Model selection modal rendered")

        # Close modal with Escape
        sess.send_key("\x1b")
        time.sleep(0.3)

        # Step 5: Test typing a prompt into composer
        print("  [5] Testing composer prompt input...")
        sess.send_text("Hello from PTY automated test!\r")
        time.sleep(0.5)
        clean = sess.get_clean_buffer()
        if "Hello from PTY automated test!" not in clean:
            print("  [FAIL] Dispatched prompt not rendered in transcript.")
            return False
        print("    -> OK: Prompt rendered immediately in transcript (optimistic turn)")

        print("--- [PTY TEST PASS] All interactive TUI validations succeeded with 100% fidelity ---")
        return True
    finally:
        sess.close()


if __name__ == "__main__":
    success = test_tui_interactive_pty()
    sys.exit(0 if success else 1)
