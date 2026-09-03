#!/usr/bin/env bash
set -euo pipefail
# Install aether and vg into ~/.local/bin, pointing at this checkout.
ROOT="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$ROOT/../../.." && pwd)"
if ! command -v node >/dev/null; then
  echo "aether install: Node.js >= 20 is required" >&2
  exit 1
fi
cd "$REPO"
npm --workspace @vanguard/cli run build
BIN="${HOME}/.local/bin"
mkdir -p "$BIN"
for name in aether vg; do
  printf '%s\n' '#!/usr/bin/env bash' "export AETHER_HOME=\"$REPO\"" 'exec node "$AETHER_HOME/vanguard/clients/cli/dist/src/main.js" "$@"' > "$BIN/$name"
  chmod +x "$BIN/$name"
done
echo "Installed $BIN/aether and $BIN/vg"
echo "Launch: aether"
echo "Live daemon socket: --socket-path, AETHER_RUNTIME_SOCK, or /tmp/vanguard-runtime.sock"
if [[ ":$PATH:" != *":$BIN:"* ]]; then
  echo "Warning: $BIN is not in PATH. Add: export PATH=\"\$HOME/.local/bin:\$PATH\""
fi
