#!/usr/bin/env bash
set -euo pipefail
# Channel 1: curl|sh installer for @vanguard/cli (Node >= 20).
ROOT="$(cd "$(dirname "$0")" && pwd)"
if ! command -v node >/dev/null; then
  echo "vg install: Node.js >= 20 is required" >&2
  exit 1
fi
cd "$ROOT"
npm install
npm run build
npm link
echo "vg is linked. Try: vg --help"
echo "Live daemon socket: --socket-path, VANGUARD_RUNTIME_SOCKET, or /tmp/vanguard-runtime.sock"
echo "Demo (no daemon): vg run --demo --headless"
