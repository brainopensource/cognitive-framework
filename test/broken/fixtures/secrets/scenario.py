#!/usr/bin/env python3
"""MF-SEC-002: Secret in EventEnvelope must be detected and rejected."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vanguard.packages.domain.ledger.events import EventEnvelope
from vanguard.packages.domain.primitives.primitives import uuidv7

SECRET = "sk-live-secret-do-not-leak-12345"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=("reference", "leaked-secret"), required=True)
    args = parser.parse_args()

    if args.variant == "leaked-secret":
        payload = {"kind": "ProposalProduced", "model": "openai/gpt-4o-mini", "raw_auth": f"Bearer {SECRET}"}
    else:
        payload = {"kind": "ProposalProduced", "model": "openai/gpt-4o-mini", "api_key_ref": "OPENROUTER_API_KEY"}

    envelope = EventEnvelope(
        schema_version="vg.4",
        event_id=uuidv7(),
        scope="episode",
        seq="1",
        occurred_at="2026-08-15T22:00:00.000Z",
        recorded_at="2026-08-15T22:00:00.000Z",
        principal="agent-1",
        principal_role="episode",
        run_id="run-1",
        episode_id="episode-1",
        trace_id="run-1",
        span_id="intent-1",
        payload=payload,
        tenant_id="tenant-default",
        owner_id="owner-platform",
        confidentiality="internal",
        retention_class="extended",
        trainability="prohibited",
        redaction_status="none",
    )

    serialized = json.dumps(envelope.to_dict())
    if SECRET in serialized:
        raise AssertionError("secret in envelope")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
