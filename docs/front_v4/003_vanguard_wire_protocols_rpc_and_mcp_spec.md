# 003 — Wire protocols, RPC, and frames (Historical Note — Superseded)

Status: `SUPERSEDED by 003_wire_consumer.md`  
Authority: VG-04 §0 / §12 / §15; ADR-0062; `server.py`

**The JSON-RPC 2.0 / 4 MiB frame proposal in early drafts is non-normative and not implemented.**

Wire protocol is strictly **`version: "vg.4"` NDJSON over Unix domain socket** with maximum frame size **1 MiB**. See `003_wire_consumer.md`.
