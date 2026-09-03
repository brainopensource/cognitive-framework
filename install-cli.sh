#!/usr/bin/env bash
set -euo pipefail

# Resolve repository root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${SCRIPT_DIR}"

echo "==> Building AETHER CLI packages in ${REPO_ROOT}..."

# Build required packages in workspace order
npm --prefix "${REPO_ROOT}" run build:contracts
npm --prefix "${REPO_ROOT}" run build:projections
npm --prefix "${REPO_ROOT}" run build:client
npm --prefix "${REPO_ROOT}" run build:tui-core
npm --prefix "${REPO_ROOT}" run build:tui
npm --prefix "${REPO_ROOT}" run build:client-core
npm --prefix "${REPO_ROOT}" run build:cli

TARGET_BIN="${REPO_ROOT}/vanguard/clients/cli/dist/src/main.js"
chmod +x "${TARGET_BIN}"

# Target install directory (~/.local/bin is standard on Linux and user-local)
INSTALL_DIR="${HOME}/.local/bin"
mkdir -p "${INSTALL_DIR}"

echo "==> Installing launcher wrappers in ${INSTALL_DIR}..."

cat <<INNER_EOF > "${INSTALL_DIR}/aether"
#!/usr/bin/env bash
export AETHER_REPO_ROOT="${REPO_ROOT}"
export VANGUARD_ROOT="${REPO_ROOT}"
exec node "${TARGET_BIN}" "\$@"
INNER_EOF
chmod +x "${INSTALL_DIR}/aether"

cat <<INNER_EOF > "${INSTALL_DIR}/vg"
#!/usr/bin/env bash
export AETHER_REPO_ROOT="${REPO_ROOT}"
export VANGUARD_ROOT="${REPO_ROOT}"
exec node "${TARGET_BIN}" "\$@"
INNER_EOF
chmod +x "${INSTALL_DIR}/vg"

# Also register npm link so global npm bin knows it
echo "==> Linking via npm..."
(cd "${REPO_ROOT}/vanguard/clients/cli" && npm link) || true

echo ""
echo "============================================================"
echo "  AETHER CLI successfully installed!"
echo "============================================================"
echo "Commands installed to ${INSTALL_DIR}:"
echo "  - aether"
echo "  - vg"
echo ""
echo "You can now open any folder and simply run:"
echo "  $ cd /path/to/any/project"
echo "  $ aether"
echo "  or"
echo "  $ vg"
echo "============================================================"
