# Wave-2 (2.1-A) compatibility shim: the canonical line-delimited JSON-RPC 2.0
# codec lives at vanguard/packages/domain/wire/jsonrpc.py. This re-export keeps
# layer0/registry/ importing unmodified -- and, critically, means a
# `JsonRpcError` raised across the plugin-cell UDS here and one caught by a
# packages adapter are the *same* class -- until layer0/ is deleted entirely.
"""Re-export of the canonical JSON-RPC codec.

See vanguard/packages/domain/wire/jsonrpc.py -- the only place this codec is
implemented (SPEC §2.1, ADR-0069).
"""

from __future__ import annotations

from vanguard.packages.domain.wire.jsonrpc import (
    JsonRpcError,
    dumps_error,
    dumps_request,
    dumps_result,
    loads,
)

__all__ = ["JsonRpcError", "dumps_error", "dumps_request", "dumps_result", "loads"]
