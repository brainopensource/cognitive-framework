"""Coding-harness instrument tuple (VG-07). Not TableWorld.

Family is the frozen pack. Arms are labelled ModelPorts. The split is the
pre-registered coding tasks. Contamination identity is the session JSONL digest
when a ledger exists; absence is recorded, not invented.

REQ-TRUST-001: this module does not call a model and does not grade artifacts.
"""

from __future__ import annotations

from typing import Any

CODING_FAMILY = "vg-code-default"

CODING_ARMS = (
    "mock",
    "ollama:deepseek-r1",
    "openrouter-free",
    "deepseek-flash",
)

# Protocol names (S9-J-01). Directories are BETA's to land; missing stays in
# the denominator as inconclusive:workspace_missing (ALFA W13-A invariant).
PREREGISTERED_TASKS = (
    "DOGFOOD-01",
    "DOGFOOD-02",
    "DOGFOOD-03",
    "GREENFIELD-API-HTML",
)

WORKER_HIDDEN_NAMES = frozenset({
    "REFERENCE.md",
    "GOLD.patch",
    "gold.diff",
    "expected.patch",
    "solution.py",
})

FORBIDDEN_LIVE_LABELS_WHEN_MOCK = frozenset({
    "ollama:deepseek-r1",
    "openrouter-free",
    "deepseek-flash",
    "openrouter",
    "ollama",
})


def instrument_tuple(*, arm: str = "mock", session_jsonl_digest: str | None = None) -> dict[str, Any]:
    if arm not in CODING_ARMS:
        raise ValueError(f"unknown coding arm {arm!r}; want one of {CODING_ARMS}")
    return {
        "family": CODING_FAMILY,
        "arm": arm,
        "split": list(PREREGISTERED_TASKS),
        "contaminationLedger": session_jsonl_digest,
        "schema": "vg.coding-instrument.v1",
    }


def is_hidden_from_worker(name: str) -> bool:
    return name in WORKER_HIDDEN_NAMES or name.endswith(".gold.patch")


def mock_must_not_wear_live_label(model_port: str, claimed_arm: str) -> bool:
    """Return True when the pairing is honest."""
    if model_port == "mock":
        return claimed_arm == "mock"
    return claimed_arm != "mock"
