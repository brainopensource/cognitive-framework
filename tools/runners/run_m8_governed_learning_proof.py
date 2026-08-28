#!/usr/bin/env python3
"""Observe the M-8 memory, promotion and rollback falsifiers in a fresh process.

M-8's predicate is `durable_memory_and_signed_rollback_verified`. That is two
claims, and this report keeps them separable: durable authorized memory on one
side, signed promotion with an *executed* rollback on the other.

The suites span `falsifiers/`, `security/`, `adapters/` and `runtime/` because
M-8's invariants do: authorization before ranking is a security property, CAS
durability is an adapter property, and authority separation is a governance
property. Reporting only the falsifier directory would understate what the
milestone actually rests on.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from falsifier_proof import ROOT, emit, run_suite  # noqa: E402

MODULES = (
    "test.falsifiers.test_m8_skill_lifecycle",
    "test.security.test_m8_memory_falsifiers",
    "test.security.test_m8_memory_fake_parity",
    "test.adapters.test_durable_memory_port",
    "test.runtime.test_governed_learning",
)

MARKERS = {
    "authorities_distinct": "TheThreeAuthoritiesStayDistinct",
    "held_out_is_real": "HeldOutEvidenceMustBeReal",
    "presence_is_not_use": "PresenceIsNotUseAndUseIsNotGrounding",
    "promotion_binds_decision": "PromotionEvidenceBindsWhatWasDecided",
    "rollback_executed": "RollbackIsExecutableNotDocumented",
    "reproducibility_recomputed": "ReproducibilityIsRecomputedAfterPromotion",
    "no_premature_event_kinds": "NoLifecycleEventKindIsIntroducedBeforeADR0100",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = run_suite(
        args.root.resolve(), MODULES,
        schema="aether.m8-falsifier-report/1", markers=MARKERS,
    )
    return emit(report, args.out)


if __name__ == "__main__":
    raise SystemExit(main())
