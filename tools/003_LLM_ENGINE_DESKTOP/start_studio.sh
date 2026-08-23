#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "⚡ Launching LED Studio (Press Ctrl+C to stop)..."
cargo run --bin led-studio -- --port 8080
