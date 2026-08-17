# ADR-FE-GUI-001 — Standalone Vanguard GUI shell

Status: accepted · 2026-08-17

We choose **Tauri 2 + React + TypeScript** for the standalone GUI. React provides the slot host and Tauri is the future native shell for filesystem, PTY, git, and window integration. The first FE-3 slice is a browser-runnable shell so replay development needs no daemon or native sidecar.

The GUI consumes `@vanguard/client-core`; it does not embed Ink, invent wire verbs, fork Code-OSS, or become a second agent loop. Monaco, xterm, and xyflow are represented by replaceable slots in this starter and will bind to native adapters in the next wave.
