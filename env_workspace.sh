#!/usr/bin/env bash
# Workspace environment configuration for Vanguard / AETHER
if [ -z "$AETHER_WORKSPACE_ROOT" ]; then
    _SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    export AETHER_WORKSPACE_ROOT="${_SCRIPT_DIR}/.vanguard/workspace"
fi
export TMPDIR="$AETHER_WORKSPACE_ROOT/tmp"
export TMP="$AETHER_WORKSPACE_ROOT/tmp"
export TEMP="$AETHER_WORKSPACE_ROOT/tmp"
export XDG_CACHE_HOME="$AETHER_WORKSPACE_ROOT/cache"
export XDG_STATE_HOME="$AETHER_WORKSPACE_ROOT/state"
export PYTHONPYCACHEPREFIX="$AETHER_WORKSPACE_ROOT/cache/python"
export npm_config_cache="$AETHER_WORKSPACE_ROOT/cache/npm"
