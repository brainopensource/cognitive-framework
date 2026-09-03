#!/usr/bin/env python3
"""MF-GOV-001: a policy that ignores approval binding must be observable."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from test.kernel import fakes  # noqa: E402
from vanguard.packages.kernel import Decision, FailurePath, Outcome, Scope, StandardPolicy  # noqa: E402
from vanguard.packages.runtime.governance import (  # noqa: E402
    ApprovalAuthorization,
    DescriptorBoundApprovalPolicy,
)


DIFF = """diff --git a/src/a.py b/src/a.py
--- a/src/a.py
+++ b/src/a.py
@@ -1 +1 @@
-return False
+return attacker_value
"""


class BrokenApprovalPolicy(DescriptorBoundApprovalPolicy):
    """The planted defect: any approval-shaped value bypasses binding."""

    def authorize(self, request, *, widens_capability, requested_scope, spans=None):
        base = getattr(self, "_base", getattr(self, "_delegate", None))
        decision = base.authorize(
            request,
            widens_capability=widens_capability,
            requested_scope=requested_scope,
            spans=spans,
        )
        if decision.outcome is Outcome.REQUIRE_APPROVAL:
            return Decision(Outcome.ALLOW, granted_scope=decision.granted_scope)
        return decision


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=("reference", "unbound-approval"), required=True)
    args = parser.parse_args()

    parent = Scope(
        frozenset({"fs.patch"}), (fakes.WORKSPACE,), fakes.constraints()
    )
    requested = Scope(
        frozenset({"fs.patch"}),
        ({"kind": "fs", "root": "/workspace", "paths": ["/workspace/src/a.ts"]},),
        fakes.constraints(),
        depth=1,
    )
    base = StandardPolicy(
        parent_scope=parent,
        approval_required_above="low",
        risk_of={"fs.patch": "critical"},
    )
    invalid = ApprovalAuthorization(
        False, "resumed_args_digest_mismatch", "approval-1", "sha256:" + "0" * 64,
        "sha256:" + "1" * 64,
    )
    policy_type = (
        DescriptorBoundApprovalPolicy
        if args.variant == "reference"
        else BrokenApprovalPolicy
    )
    harness = fakes.build(
        adapter=fakes.FakeAdapter("fs.patch"),
        policy=policy_type(base, invalid),
        held_actions=frozenset({"fs.patch"}),
        scope=parent,
    )
    result = harness.kernel.dispatch(
        fakes.request(action="fs.patch", args={"diff": DIFF}),
        requested_scope=requested,
        reservation=fakes.reservation(),
    )
    if result.failure is not FailurePath.DENIED_REJECT or harness.adapter.calls:
        raise AssertionError("tampered approval reached privileged effect")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
